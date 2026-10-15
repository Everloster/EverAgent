#!/usr/bin/env python3
"""Model-agnostic evidence and review gate for durable EverAgent reports.

The script does not call an LLM. It creates portable artifacts that any harness
can fill, validates their provenance, computes a conservative rubric score, and
returns the next action: pass, revise, escalate, or needs_review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    from .report_catalog import ROOT, collection_for_path, parse_frontmatter
except ImportError:  # Direct script execution.
    from report_catalog import ROOT, collection_for_path, parse_frontmatter


POLICY_PATH = ROOT / "config" / "report-quality-policy.json"
CURRENT_REPORT_SCHEMA = "report-v2"
SUPPORTED_REPORT_SCHEMAS = {"report-v1", CURRENT_REPORT_SCHEMA}
EVIDENCE_SCHEMA_VERSION = 1
REVIEW_SCHEMA_VERSION = 1
SOURCE_KINDS = {"primary", "official", "secondary", "local", "execution"}
SUPPORT_TYPES = {"direct", "derived", "inference"}
REVIEW_ROLES = {"primary_review", "escalation_review", "flagship_final_review"}
INFERENCE_MARKERS = ("[推测]", "[待验证]")


@dataclass(frozen=True)
class QualityFinding:
    severity: str
    code: str
    message: str


def load_policy(path: Path = POLICY_PATH) -> dict[str, Any]:
    policy = json.loads(path.read_text(encoding="utf-8"))
    weights = policy.get("dimensions", {})
    if sum(weights.values()) != 100:
        raise ValueError("report quality dimension weights must sum to 100")
    if policy.get("current_report_schema") != CURRENT_REPORT_SCHEMA:
        raise ValueError("current_report_schema does not match the validator")
    return policy


def normalize_model(model: str, policy: dict[str, Any]) -> str:
    value = re.sub(r"[\s_]+", "-", str(model or "").strip().lower())
    aliases = {
        re.sub(r"[\s_]+", "-", key.strip().lower()): target
        for key, target in policy["model_policy"].get("aliases", {}).items()
    }
    return aliases.get(value, value)


def report_relative_path(report: Path) -> str:
    return str(report.resolve().relative_to(ROOT))


def quality_artifact_paths(report: Path) -> tuple[Path, Path]:
    directory = report.parent / ".quality"
    return (
        directory / f"{report.stem}.evidence.json",
        directory / f"{report.stem}.review.json",
    )


def report_for_quality_artifact(path: Path) -> Path | None:
    if path.parent.name != ".quality":
        return None
    for suffix in (".evidence.json", ".review.json"):
        if path.name.endswith(suffix):
            report = path.parent.parent / f"{path.name[:-len(suffix)]}.md"
            return report if report.exists() else None
    return None


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _set_frontmatter_fields(report: Path, fields: dict[str, str]) -> None:
    text = report.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("report must have frontmatter before quality artifacts can be initialized")
    try:
        close = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise ValueError("report frontmatter is not closed") from exc

    header = lines[1:close]
    for key, value in fields.items():
        replacement = f'{key}: "{value}"'
        for index, line in enumerate(header):
            if re.match(rf"^{re.escape(key)}\s*:", line):
                header[index] = replacement
                break
        else:
            header.append(replacement)
    report.write_text("\n".join(["---", *header, "---", *lines[close + 1 :]]) + "\n", encoding="utf-8")


def _model_findings(
    model: str,
    *,
    role: str,
    explicit_override: bool,
    policy: dict[str, Any],
    override_reason: str = "",
) -> list[QualityFinding]:
    findings: list[QualityFinding] = []
    canonical = normalize_model(model, policy)
    model_policy = policy["model_policy"]
    disabled = {normalize_model(item, policy) for item in model_policy.get("disabled_models", [])}
    scarce = {normalize_model(item, policy) for item in model_policy.get("scarce_models", [])}
    preferred_roles = set(model_policy.get("scarce_model_preferred_roles", []))

    if explicit_override and not model_policy.get("explicit_user_override_allowed", False):
        findings.append(QualityFinding("error", "MODEL005", "当前策略不允许模型显式覆盖"))
    if explicit_override and not override_reason.strip():
        findings.append(QualityFinding("error", "MODEL006", "显式模型覆盖必须记录原因"))
    if canonical in disabled:
        findings.append(QualityFinding("error", "MODEL001", f"模型 {model} 已禁用于新报告流水线"))
    if canonical in scarce and role not in preferred_roles and not explicit_override:
        findings.append(
            QualityFinding(
                "warning",
                "MODEL002",
                f"稀缺模型 {model} 用于 {role}；默认应保留给升级复核或旗舰终审",
            )
        )
    return findings


def _required_string(obj: dict[str, Any], key: str, prefix: str) -> list[QualityFinding]:
    if not isinstance(obj.get(key), str) or not obj[key].strip():
        return [QualityFinding("error", prefix, f"缺少非空字段 {key}")]
    return []


def validate_evidence_manifest(
    report: Path,
    metadata: dict[str, object],
    manifest: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[list[QualityFinding], dict[str, Any]]:
    findings: list[QualityFinding] = []
    tier = str(metadata.get("quality_tier") or "")
    tier_policy = policy.get("tiers", {}).get(tier)
    relative = report_relative_path(report)

    if manifest.get("schema_version") != EVIDENCE_SCHEMA_VERSION:
        findings.append(QualityFinding("error", "EVM001", "证据账本 schema_version 必须为 1"))
    if manifest.get("report_path") != relative:
        findings.append(QualityFinding("error", "EVM002", "证据账本 report_path 与报告不一致"))
    if manifest.get("quality_tier") != tier:
        findings.append(QualityFinding("error", "EVM003", "证据账本 quality_tier 与 frontmatter 不一致"))

    generator = manifest.get("generator")
    if not isinstance(generator, dict):
        findings.append(QualityFinding("error", "EVM004", "缺少 generator 对象"))
        generator = {}
    for key in ("model", "harness", "run_id"):
        findings.extend(_required_string(generator, key, "EVM005"))
    if not isinstance(generator.get("explicit_model_override"), bool):
        findings.append(QualityFinding("error", "EVM006", "generator.explicit_model_override 必须为布尔值"))
    findings.extend(
        _model_findings(
            str(generator.get("model") or ""),
            role="generator",
            explicit_override=generator.get("explicit_model_override") is True,
            override_reason=str(generator.get("override_reason") or ""),
            policy=policy,
        )
    )

    task = manifest.get("task")
    if not isinstance(task, dict):
        findings.append(QualityFinding("error", "EVM007", "缺少 task 对象"))
        task = {}
    findings.extend(_required_string(task, "summary", "EVM008"))
    requirements = task.get("requirements")
    if not isinstance(requirements, list) or not requirements:
        findings.append(QualityFinding("error", "EVM009", "task.requirements 至少包含一项"))
        requirements = []
    requirement_ids: list[str] = []
    for item in requirements:
        if not isinstance(item, dict) or not item.get("id") or not item.get("text"):
            findings.append(QualityFinding("error", "EVM010", "每项 requirement 必须包含 id 与 text"))
            continue
        requirement_ids.append(str(item["id"]))
    if len(requirement_ids) != len(set(requirement_ids)):
        findings.append(QualityFinding("error", "EVM011", "requirement id 重复"))

    sources = manifest.get("sources")
    if not isinstance(sources, list):
        findings.append(QualityFinding("error", "EVM012", "sources 必须为数组"))
        sources = []
    source_ids: list[str] = []
    primary_sources = 0
    for source in sources:
        if not isinstance(source, dict):
            findings.append(QualityFinding("error", "EVM013", "source 必须为对象"))
            continue
        for key in ("id", "kind", "title", "locator", "accessed_on"):
            findings.extend(_required_string(source, key, "EVM014"))
        source_id = str(source.get("id") or "")
        if source_id:
            source_ids.append(source_id)
        kind = str(source.get("kind") or "")
        if kind not in SOURCE_KINDS:
            findings.append(QualityFinding("error", "EVM015", f"未知 source kind：{kind}"))
        if kind in {"primary", "official", "local", "execution"}:
            primary_sources += 1
        if source.get("accessed_on") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source["accessed_on"])):
            findings.append(QualityFinding("error", "EVM016", f"source {source_id} 的 accessed_on 格式错误"))
    if len(source_ids) != len(set(source_ids)):
        findings.append(QualityFinding("error", "EVM017", "source id 重复"))

    claims = manifest.get("claims")
    if not isinstance(claims, list):
        findings.append(QualityFinding("error", "EVM018", "claims 必须为数组"))
        claims = []
    report_text = report.read_text(encoding="utf-8", errors="replace")
    claim_ids: list[str] = []
    critical_claim_ids: list[str] = []
    critical_source_ids: set[str] = set()
    known_sources = set(source_ids)
    for claim in claims:
        if not isinstance(claim, dict):
            findings.append(QualityFinding("error", "EVM019", "claim 必须为对象"))
            continue
        for key in ("id", "claim", "report_anchor", "support"):
            findings.extend(_required_string(claim, key, "EVM020"))
        claim_id = str(claim.get("id") or "")
        if claim_id:
            claim_ids.append(claim_id)
        anchor = str(claim.get("report_anchor") or "")
        if anchor and anchor not in report_text:
            findings.append(QualityFinding("error", "EVM021", f"claim {claim_id} 的 report_anchor 未出现在报告中"))
        support = str(claim.get("support") or "")
        if support not in SUPPORT_TYPES:
            findings.append(QualityFinding("error", "EVM022", f"claim {claim_id} 的 support 无效"))
        refs = claim.get("source_ids")
        if not isinstance(refs, list):
            findings.append(QualityFinding("error", "EVM023", f"claim {claim_id} 的 source_ids 必须为数组"))
            refs = []
        unknown = sorted(set(map(str, refs)) - known_sources)
        if unknown:
            findings.append(QualityFinding("error", "EVM024", f"claim {claim_id} 引用了未知 source：{', '.join(unknown)}"))
        if support in {"direct", "derived"} and not refs:
            findings.append(QualityFinding("error", "EVM025", f"claim {claim_id} 缺少来源"))
        if support in {"direct", "derived"} and not str(claim.get("evidence") or "").strip():
            findings.append(QualityFinding("error", "EVM026", f"claim {claim_id} 缺少简短 evidence"))
        if support == "inference" and not any(marker in f"{claim.get('claim', '')}{anchor}" for marker in INFERENCE_MARKERS):
            findings.append(QualityFinding("error", "EVM027", f"推断 claim {claim_id} 未标 [推测] 或 [待验证]"))
        if claim.get("critical") is True:
            critical_claim_ids.append(claim_id)
            critical_source_ids.update(map(str, refs))
            if not refs:
                findings.append(QualityFinding("error", "EVM028", f"关键 claim {claim_id} 必须绑定来源"))
        elif not isinstance(claim.get("critical"), bool):
            findings.append(QualityFinding("error", "EVM029", f"claim {claim_id} 的 critical 必须为布尔值"))
    if len(claim_ids) != len(set(claim_ids)):
        findings.append(QualityFinding("error", "EVM030", "claim id 重复"))

    limitations = manifest.get("limitations")
    if not isinstance(limitations, list) or not any(str(item).strip() for item in limitations):
        findings.append(QualityFinding("error", "EVM031", "limitations 至少记录一项边界或未确认事项"))

    if tier_policy:
        if len(sources) < tier_policy["minimum_sources"]:
            findings.append(QualityFinding("error", "EVM032", f"{tier} 至少需要 {tier_policy['minimum_sources']} 个来源"))
        if primary_sources < tier_policy["minimum_primary_sources"]:
            findings.append(QualityFinding("error", "EVM033", f"{tier} 至少需要 {tier_policy['minimum_primary_sources']} 个一手来源"))
        if len(critical_claim_ids) < tier_policy["minimum_critical_claims"]:
            findings.append(QualityFinding("error", "EVM034", f"{tier} 至少需要登记 {tier_policy['minimum_critical_claims']} 个关键 claim"))

    return findings, {
        "requirement_ids": requirement_ids,
        "source_ids": source_ids,
        "claim_ids": claim_ids,
        "critical_claim_ids": critical_claim_ids,
        "critical_source_ids": sorted(critical_source_ids),
        "generator_model": normalize_model(str(generator.get("model") or ""), policy),
        "generator_run_id": str(generator.get("run_id") or ""),
        "generator_explicit_override": generator.get("explicit_model_override") is True,
    }


def _score_review(scores: dict[str, Any], policy: dict[str, Any]) -> float | None:
    weighted = 0.0
    for dimension, weight in policy["dimensions"].items():
        value = scores.get(dimension)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
            return None
        weighted += float(value) * weight / 100
    return round(weighted, 2)


def validate_review_record(
    report: Path,
    metadata: dict[str, object],
    review: dict[str, Any],
    evidence_summary: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[list[QualityFinding], dict[str, Any]]:
    findings: list[QualityFinding] = []
    tier = str(metadata.get("quality_tier") or "")
    tier_policy = policy.get("tiers", {}).get(tier) or {}
    relative = report_relative_path(report)

    if review.get("schema_version") != REVIEW_SCHEMA_VERSION:
        findings.append(QualityFinding("error", "REV001", "复核记录 schema_version 必须为 1"))
    if review.get("report_path") != relative:
        findings.append(QualityFinding("error", "REV002", "复核记录 report_path 与报告不一致"))
    if review.get("quality_tier") != tier:
        findings.append(QualityFinding("error", "REV003", "复核记录 quality_tier 与 frontmatter 不一致"))
    revision_round = review.get("revision_round")
    if not isinstance(revision_round, int) or isinstance(revision_round, bool) or revision_round < 1:
        findings.append(QualityFinding("error", "REV004", "revision_round 必须为正整数"))
        revision_round = 1

    reviews = review.get("reviews")
    if not isinstance(reviews, list):
        findings.append(QualityFinding("error", "REV005", "reviews 必须为数组"))
        reviews = []
    required_reviewers = int(tier_policy.get("reviewers_required", 1))
    if len(reviews) < required_reviewers:
        findings.append(QualityFinding("error", "REV006", f"{tier} 至少需要 {required_reviewers} 个独立复核"))

    required_claims = set(evidence_summary["critical_claim_ids"])
    required_sources = set(evidence_summary["critical_source_ids"])
    required_requirements = set(evidence_summary["requirement_ids"])
    review_scores: list[float] = []
    dimension_values: dict[str, list[float]] = {key: [] for key in policy["dimensions"]}
    reviewer_models: list[str] = []
    reviewer_run_ids: list[str] = []
    scarce_calls = 0
    scarce_calls_without_override = 0
    strong_reviews = 0
    model_policy = policy["model_policy"]
    scarce_models = {normalize_model(item, policy) for item in model_policy.get("scarce_models", [])}
    strong_models = {normalize_model(item, policy) for item in model_policy.get("strong_reviewers", [])}

    for index, item in enumerate(reviews, 1):
        if not isinstance(item, dict):
            findings.append(QualityFinding("error", "REV007", f"review #{index} 必须为对象"))
            continue
        reviewer = item.get("reviewer")
        if not isinstance(reviewer, dict):
            findings.append(QualityFinding("error", "REV008", f"review #{index} 缺少 reviewer"))
            reviewer = {}
        for key in ("model", "harness", "run_id"):
            findings.extend(_required_string(reviewer, key, "REV009"))
        if reviewer.get("independent_context") is not True:
            findings.append(QualityFinding("error", "REV010", f"review #{index} 必须使用独立 context"))
        if not isinstance(reviewer.get("explicit_model_override"), bool):
            findings.append(QualityFinding("error", "REV011", f"review #{index} 的 explicit_model_override 必须为布尔值"))

        role = str(item.get("role") or "")
        if role not in REVIEW_ROLES:
            findings.append(QualityFinding("error", "REV012", f"review #{index} 的 role 无效"))
        model = normalize_model(str(reviewer.get("model") or ""), policy)
        reviewer_models.append(model)
        run_id = str(reviewer.get("run_id") or "")
        reviewer_run_ids.append(run_id)
        findings.extend(
            _model_findings(
                model,
                role=role,
                explicit_override=reviewer.get("explicit_model_override") is True,
                override_reason=str(reviewer.get("override_reason") or ""),
                policy=policy,
            )
        )
        if model in scarce_models:
            scarce_calls += 1
            if reviewer.get("explicit_model_override") is not True:
                scarce_calls_without_override += 1
            if role == "escalation_review" and not str(item.get("escalation_reason") or "").strip():
                findings.append(QualityFinding("error", "MODEL003", f"review #{index} 使用 Kimi K3 升级复核时必须记录原因"))
        if model in strong_models:
            strong_reviews += 1
        if run_id and run_id == evidence_summary["generator_run_id"]:
            findings.append(QualityFinding("error", "REV013", f"review #{index} 与生成阶段使用了同一 run_id"))

        scores = item.get("scores")
        if not isinstance(scores, dict):
            findings.append(QualityFinding("error", "REV014", f"review #{index} 缺少 scores"))
            scores = {}
        score = _score_review(scores, policy)
        if score is None:
            findings.append(QualityFinding("error", "REV015", f"review #{index} 的各维度必须为 0–100 数字"))
        else:
            review_scores.append(score)
            for dimension in policy["dimensions"]:
                dimension_values[dimension].append(float(scores[dimension]))

        score_reasons = item.get("score_reasons")
        if not isinstance(score_reasons, dict):
            findings.append(QualityFinding("error", "REV022", f"review #{index} 缺少 score_reasons"))
        else:
            for dimension in policy["dimensions"]:
                if not isinstance(score_reasons.get(dimension), str) or not score_reasons[dimension].strip():
                    findings.append(QualityFinding("error", "REV023", f"review #{index} 缺少 {dimension} 的评分理由"))

        checks = {
            "critical_claim_ids_checked": required_claims,
            "source_ids_checked": required_sources,
            "requirement_ids_checked": required_requirements,
        }
        for field, required in checks.items():
            actual = item.get(field)
            if not isinstance(actual, list) or not required.issubset(set(map(str, actual))):
                missing = sorted(required - set(map(str, actual or [])))
                findings.append(QualityFinding("error", "REV016", f"review #{index} 的 {field} 缺少：{', '.join(missing)}"))
        for field in ("unsupported_claims", "missing_requirements", "hard_failures"):
            value = item.get(field)
            if not isinstance(value, list):
                findings.append(QualityFinding("error", "REV017", f"review #{index} 的 {field} 必须为数组"))
            elif value:
                findings.append(QualityFinding("error", "REV018", f"review #{index} 仍有 {field}：{'; '.join(map(str, value))}"))
        unsupported = item.get("unsupported_claims") or []
        if isinstance(unsupported, list) and not set(map(str, unsupported)).issubset(set(evidence_summary["claim_ids"])):
            findings.append(QualityFinding("error", "REV024", f"review #{index} 的 unsupported_claims 含未知 claim id"))
        missing_requirements = item.get("missing_requirements") or []
        if isinstance(missing_requirements, list) and not set(map(str, missing_requirements)).issubset(required_requirements):
            findings.append(QualityFinding("error", "REV025", f"review #{index} 的 missing_requirements 含未知 requirement id"))
        hard_failures = item.get("hard_failures") or []
        allowed_hard_failures = set(policy.get("hard_failure_codes", []))
        if isinstance(hard_failures, list) and not set(map(str, hard_failures)).issubset(allowed_hard_failures):
            findings.append(QualityFinding("error", "REV026", f"review #{index} 使用了未知 hard failure code"))
        if not isinstance(item.get("notes"), str) or not item["notes"].strip():
            findings.append(QualityFinding("error", "REV027", f"review #{index} 必须写明审查摘要"))

    if len([item for item in reviewer_run_ids if item]) != len(set(item for item in reviewer_run_ids if item)):
        findings.append(QualityFinding("error", "REV019", "复核 run_id 重复，不能视为独立复核"))
    required_strong = int(tier_policy.get("strong_reviewers_required", 0))
    if strong_reviews < required_strong:
        findings.append(QualityFinding("error", "REV020", f"{tier} 至少需要 {required_strong} 个强模型复核"))
    history = review.get("history") or []
    if not isinstance(history, list):
        findings.append(QualityFinding("error", "REV021", "history 必须为数组"))
        history = []
    for previous_round in history:
        if not isinstance(previous_round, dict):
            continue
        for item in previous_round.get("reviews") or []:
            if not isinstance(item, dict) or not isinstance(item.get("reviewer"), dict):
                continue
            reviewer = item["reviewer"]
            model = normalize_model(str(reviewer.get("model") or ""), policy)
            if model in scarce_models:
                scarce_calls += 1
                if reviewer.get("explicit_model_override") is not True:
                    scarce_calls_without_override += 1
    if evidence_summary["generator_model"] in scarce_models:
        scarce_calls += 1
        if not evidence_summary.get("generator_explicit_override"):
            scarce_calls_without_override += 1
    scarce_limit = int(model_policy.get("scarce_model_max_calls_per_report", 1))
    if scarce_calls_without_override > scarce_limit:
        findings.append(
            QualityFinding(
                "error",
                "MODEL004",
                f"未显式覆盖的稀缺模型调用 {scarce_calls_without_override} 次，超过默认上限 {scarce_limit}",
            )
        )

    aggregate_score = min(review_scores) if review_scores else None
    aggregate_dimensions = {
        dimension: min(values) if values else None
        for dimension, values in dimension_values.items()
    }
    if aggregate_score is not None and aggregate_score < float(tier_policy.get("minimum_total", 0)):
        findings.append(QualityFinding("error", "SCORE001", f"总分 {aggregate_score} 低于 {tier} 门槛 {tier_policy['minimum_total']}"))
    for dimension, minimum in tier_policy.get("minimum_dimension_scores", {}).items():
        value = aggregate_dimensions.get(dimension)
        if value is not None and value < minimum:
            findings.append(QualityFinding("error", "SCORE002", f"{dimension}={value:g} 低于门槛 {minimum}"))

    return findings, {
        "revision_round": revision_round,
        "review_scores": review_scores,
        "score": aggregate_score,
        "dimension_scores": aggregate_dimensions,
        "reviewer_models": reviewer_models,
        "strong_reviews": strong_reviews,
        "scarce_model_calls": scarce_calls,
    }


def evaluate_report(report: Path, policy: dict[str, Any] | None = None) -> dict[str, Any]:
    report = report.resolve()
    policy = policy or load_policy()
    metadata = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace"))
    tier = str(metadata.get("quality_tier") or "")
    findings: list[QualityFinding] = []
    evidence_path, review_path = quality_artifact_paths(report)

    if metadata.get("quality_schema") != CURRENT_REPORT_SCHEMA:
        findings.append(QualityFinding("error", "QG001", f"质量流水线要求 quality_schema: {CURRENT_REPORT_SCHEMA}"))
    if tier not in policy.get("tiers", {}):
        findings.append(QualityFinding("error", "QG002", f"未知或缺失 quality_tier：{tier or '<empty>'}"))

    evidence_summary = {
        "requirement_ids": [],
        "source_ids": [],
        "claim_ids": [],
        "critical_claim_ids": [],
        "critical_source_ids": [],
        "generator_model": "",
        "generator_run_id": "",
        "generator_explicit_override": False,
    }
    if not evidence_path.exists():
        findings.append(QualityFinding("error", "QG003", f"缺少证据账本：{evidence_path.relative_to(ROOT)}"))
    else:
        try:
            manifest = _load_json(evidence_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            findings.append(QualityFinding("error", "QG004", f"证据账本无法读取：{exc}"))
        else:
            evidence_findings, evidence_summary = validate_evidence_manifest(report, metadata, manifest, policy)
            findings.extend(evidence_findings)

    review_summary = {
        "revision_round": 1,
        "review_scores": [],
        "score": None,
        "dimension_scores": {},
        "reviewer_models": [],
        "strong_reviews": 0,
        "scarce_model_calls": 0,
    }
    if not review_path.exists():
        findings.append(QualityFinding("error", "QG005", f"缺少独立复核记录：{review_path.relative_to(ROOT)}"))
    else:
        try:
            review = _load_json(review_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            findings.append(QualityFinding("error", "QG006", f"复核记录无法读取：{exc}"))
        else:
            review_findings, review_summary = validate_review_record(
                report,
                metadata,
                review,
                evidence_summary,
                policy,
            )
            findings.extend(review_findings)

    error_codes = {finding.code for finding in findings if finding.severity == "error"}
    incomplete_codes = {"QG003", "QG004", "QG005", "QG006", "REV005", "REV006", "REV014", "REV015", "REV016", "REV017"}
    quality_failure_codes = {"REV018", "SCORE001", "SCORE002"}
    blocking_codes = error_codes - incomplete_codes - quality_failure_codes
    if not error_codes:
        decision = "pass"
    elif blocking_codes:
        decision = "blocked"
    elif error_codes & quality_failure_codes:
        max_rounds = int(policy.get("tiers", {}).get(tier, {}).get("max_revision_rounds", 1))
        decision = "revise" if review_summary["revision_round"] <= max_rounds else "escalate"
    elif error_codes <= incomplete_codes:
        decision = "needs_review"
    else:
        decision = "blocked"

    return {
        "schema_version": 1,
        "report": report_relative_path(report),
        "quality_schema": metadata.get("quality_schema", ""),
        "quality_tier": tier,
        "evidence_manifest": str(evidence_path.relative_to(ROOT)),
        "review_record": str(review_path.relative_to(ROOT)),
        "score": review_summary["score"],
        "dimension_scores": review_summary["dimension_scores"],
        "decision": decision,
        "recommended_models": policy["model_policy"].get("premium_reviewer_order", []) if decision == "escalate" else [],
        "warnings": [asdict(item) for item in findings if item.severity == "warning"],
        "errors": [asdict(item) for item in findings if item.severity == "error"],
    }


def initialize_quality_artifacts(
    report: Path,
    *,
    tier: str,
    generator_model: str,
    harness: str,
    run_id: str | None = None,
    explicit_model_override: bool = False,
    override_reason: str = "",
    force: bool = False,
) -> tuple[Path, Path, list[QualityFinding]]:
    report = report.resolve()
    if collection_for_path(report) is None:
        raise ValueError("report is not inside a registered report collection")
    policy = load_policy()
    if tier not in policy["tiers"]:
        raise ValueError(f"unknown quality tier: {tier}")
    findings = _model_findings(
        generator_model,
        role="generator",
        explicit_override=explicit_model_override,
        override_reason=override_reason,
        policy=policy,
    )
    if any(item.severity == "error" for item in findings):
        raise ValueError("; ".join(item.message for item in findings))

    evidence_path, review_path = quality_artifact_paths(report)
    if not force and (evidence_path.exists() or review_path.exists()):
        raise FileExistsError("quality artifacts already exist; use --force to replace them")
    _set_frontmatter_fields(
        report,
        {
            "quality_schema": CURRENT_REPORT_SCHEMA,
            "quality_tier": tier,
            "status": "in_progress",
        },
    )
    relative = report_relative_path(report)
    manifest = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "report_path": relative,
        "quality_tier": tier,
        "created_on": dt.date.today().isoformat(),
        "generator": {
            "model": normalize_model(generator_model, policy),
            "harness": harness,
            "run_id": run_id or f"generator-{uuid.uuid4().hex[:12]}",
            "explicit_model_override": explicit_model_override,
            "override_reason": override_reason,
        },
        "task": {"summary": "", "requirements": []},
        "sources": [],
        "claims": [],
        "limitations": [],
    }
    review = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "report_path": relative,
        "quality_tier": tier,
        "revision_round": 1,
        "reviews": [],
        "decision": {},
    }
    _write_json(evidence_path, manifest)
    _write_json(review_path, review)
    return evidence_path, review_path, findings


def append_review_template(
    report: Path,
    *,
    reviewer_model: str,
    harness: str,
    role: str,
    run_id: str | None = None,
    explicit_model_override: bool = False,
    override_reason: str = "",
    escalation_reason: str = "",
) -> tuple[Path, list[QualityFinding]]:
    report = report.resolve()
    policy = load_policy()
    metadata = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace"))
    tier = str(metadata.get("quality_tier") or "")
    if metadata.get("quality_schema") != CURRENT_REPORT_SCHEMA:
        raise ValueError(f"report must use quality_schema: {CURRENT_REPORT_SCHEMA}")
    if tier not in policy["tiers"]:
        raise ValueError("report is missing a valid quality_tier")
    if role not in REVIEW_ROLES:
        raise ValueError(f"unknown review role: {role}")
    findings = _model_findings(
        reviewer_model,
        role=role,
        explicit_override=explicit_model_override,
        override_reason=override_reason,
        policy=policy,
    )
    if any(item.severity == "error" for item in findings):
        raise ValueError("; ".join(item.message for item in findings))

    evidence_path, review_path = quality_artifact_paths(report)
    if not evidence_path.exists():
        raise ValueError("evidence manifest must be completed before creating a review")
    evidence = _load_json(evidence_path)
    evidence_findings, _summary = validate_evidence_manifest(report, metadata, evidence, policy)
    evidence_errors = [item.message for item in evidence_findings if item.severity == "error"]
    if evidence_errors:
        raise ValueError("evidence manifest is incomplete: " + "; ".join(evidence_errors))
    if review_path.exists():
        review = _load_json(review_path)
    else:
        review = {
            "schema_version": REVIEW_SCHEMA_VERSION,
            "report_path": report_relative_path(report),
            "quality_tier": tier,
            "revision_round": 1,
            "reviews": [],
            "decision": {},
        }
    reviews = review.setdefault("reviews", [])
    if not isinstance(reviews, list):
        raise ValueError("review record field 'reviews' must be an array")
    reviews.append(
        {
            "role": role,
            "reviewer": {
                "model": normalize_model(reviewer_model, policy),
                "harness": harness,
                "run_id": run_id or f"review-{uuid.uuid4().hex[:12]}",
                "independent_context": True,
                "explicit_model_override": explicit_model_override,
                "override_reason": override_reason,
            },
            "escalation_reason": escalation_reason,
            "scores": {dimension: None for dimension in policy["dimensions"]},
            "score_reasons": {dimension: "" for dimension in policy["dimensions"]},
            "critical_claim_ids_checked": [],
            "source_ids_checked": [],
            "requirement_ids_checked": [],
            "unsupported_claims": [],
            "missing_requirements": [],
            "hard_failures": [],
            "notes": "",
        }
    )
    _write_json(review_path, review)
    return review_path, findings


def start_new_revision(report: Path) -> Path:
    report = report.resolve()
    _evidence_path, review_path = quality_artifact_paths(report)
    review = _load_json(review_path)
    reviews = review.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        raise ValueError("current revision has no review to archive")
    history = review.setdefault("history", [])
    if not isinstance(history, list):
        raise ValueError("review record field 'history' must be an array")
    history.append(
        {
            "revision_round": review.get("revision_round", 1),
            "reviews": reviews,
            "decision": review.get("decision", {}),
        }
    )
    review["revision_round"] = int(review.get("revision_round", 1)) + 1
    review["reviews"] = []
    review["decision"] = {}
    _write_json(review_path, review)
    _set_frontmatter_fields(report, {"status": "in_progress"})
    return review_path


def reviewer_prompt(report: Path) -> str:
    report = report.resolve()
    evidence_path, review_path = quality_artifact_paths(report)
    policy = load_policy()
    metadata = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace"))
    if metadata.get("quality_schema") != CURRENT_REPORT_SCHEMA:
        raise ValueError(f"report must use quality_schema: {CURRENT_REPORT_SCHEMA}")
    if not evidence_path.exists() or not review_path.exists():
        raise ValueError("quality artifacts are missing; run report_quality.py init first")
    tier = str(metadata.get("quality_tier") or policy["default_quality_tier"])
    evidence = _load_json(evidence_path)
    evidence_findings, _summary = validate_evidence_manifest(report, metadata, evidence, policy)
    evidence_errors = [item.message for item in evidence_findings if item.severity == "error"]
    if evidence_errors:
        raise ValueError("evidence manifest is incomplete: " + "; ".join(evidence_errors))
    dimensions = "、".join(f"{name}（权重 {weight}%）" for name, weight in policy["dimensions"].items())
    score_bands = "；".join(f"{name.replace('_', '–')}：{text}" for name, text in policy.get("score_bands", {}).items())
    hard_failures = "、".join(policy.get("hard_failure_codes", []))
    return f"""你是 EverAgent 报告的独立审稿人。请在全新 context 中完成复核，不参考生成者的推理过程。

报告：{report_relative_path(report)}
证据账本：{evidence_path.relative_to(ROOT)}
复核记录：{review_path.relative_to(ROOT)}
质量等级：{tier}

要求：
1. 实际打开报告、证据账本，以及所有关键 claim 对应的一手来源。
2. 逐项确认关键 claim、来源和用户需求；发现 unsupported claim、遗漏需求或硬错误时如实记录。
3. 按 0–100 分填写：{dimensions}，并为每一维填写 `score_reasons`。评分锚点：{score_bands}。
4. 不直接改报告。先完成复核记录，再由生成者依据问题清单修订。
5. 完成后运行 `python3 scripts/report_quality.py check {report_relative_path(report)}`，不得自行宣称通过。
6. 报告修订后先运行 `python3 scripts/report_quality.py new-revision {report_relative_path(report)}`，再创建新一轮 Reviewer 记录。
7. 硬失败只使用这些代码：{hard_failures}。
"""


def _print_result(result: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    print(
        f"{result['report']}｜tier={result['quality_tier']}｜"
        f"decision={result['decision']}｜score={result['score']}｜"
        f"ERROR {len(result['errors'])}｜WARN {len(result['warnings'])}"
    )
    for item in result["errors"]:
        print(f"  ✗ {item['code']}: {item['message']}")
    for item in result["warnings"]:
        print(f"  ⚠ {item['code']}: {item['message']}")
    if result["recommended_models"]:
        print("  升级复核顺序：" + " → ".join(result["recommended_models"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage and validate EverAgent report quality artifacts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    policy_parser = subparsers.add_parser("policy", help="show model routing and quality thresholds")
    policy_parser.add_argument("--tier", choices=("standard", "important", "flagship"))
    policy_parser.add_argument("--json", action="store_true")

    init_parser = subparsers.add_parser("init", help="initialize report-v2 evidence and review artifacts")
    init_parser.add_argument("report", type=Path)
    init_parser.add_argument("--tier", choices=("standard", "important", "flagship"), default=None)
    init_parser.add_argument("--generator-model", required=True)
    init_parser.add_argument("--harness", required=True)
    init_parser.add_argument("--run-id")
    init_parser.add_argument("--explicit-model-override", action="store_true")
    init_parser.add_argument("--override-reason", default="")
    init_parser.add_argument("--force", action="store_true")

    review_parser = subparsers.add_parser("review-template", help="append an independent reviewer record")
    review_parser.add_argument("report", type=Path)
    review_parser.add_argument("--reviewer-model", required=True)
    review_parser.add_argument("--harness", required=True)
    review_parser.add_argument("--role", choices=sorted(REVIEW_ROLES), default="primary_review")
    review_parser.add_argument("--run-id")
    review_parser.add_argument("--explicit-model-override", action="store_true")
    review_parser.add_argument("--override-reason", default="")
    review_parser.add_argument("--escalation-reason", default="")

    revision_parser = subparsers.add_parser("new-revision", help="archive current reviews and start a new round")
    revision_parser.add_argument("report", type=Path)

    prompt_parser = subparsers.add_parser("review-prompt", help="print the model-independent reviewer prompt")
    prompt_parser.add_argument("report", type=Path)

    check_parser = subparsers.add_parser("check", help="validate evidence, reviews, and score")
    check_parser.add_argument("report", type=Path)
    check_parser.add_argument("--json", action="store_true")
    check_parser.add_argument("--write-decision", action="store_true")
    check_parser.add_argument("--finalize", action="store_true", help="mark an in-progress report completed after a passing check")
    check_parser.add_argument("--final-status", choices=("completed", "archived"), default="completed")

    args = parser.parse_args()
    policy = load_policy()

    if args.command == "policy":
        result = policy if args.tier is None else {
            "schema_version": policy["schema_version"],
            "model_policy": policy["model_policy"],
            "tier": args.tier,
            "quality": policy["tiers"][args.tier],
        }
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "init":
        tier = args.tier or policy["default_quality_tier"]
        try:
            evidence_path, review_path, findings = initialize_quality_artifacts(
                args.report,
                tier=tier,
                generator_model=args.generator_model,
                harness=args.harness,
                run_id=args.run_id,
                explicit_model_override=args.explicit_model_override,
                override_reason=args.override_reason,
                force=args.force,
            )
        except (OSError, ValueError) as exc:
            print(f"[report-quality] {exc}", file=sys.stderr)
            return 1
        print(evidence_path.relative_to(ROOT))
        print(review_path.relative_to(ROOT))
        for item in findings:
            print(f"⚠ {item.code}: {item.message}")
        return 0

    if args.command == "review-template":
        try:
            review_path, findings = append_review_template(
                args.report,
                reviewer_model=args.reviewer_model,
                harness=args.harness,
                role=args.role,
                run_id=args.run_id,
                explicit_model_override=args.explicit_model_override,
                override_reason=args.override_reason,
                escalation_reason=args.escalation_reason,
            )
        except (OSError, ValueError) as exc:
            print(f"[report-quality] {exc}", file=sys.stderr)
            return 1
        print(review_path.relative_to(ROOT))
        for item in findings:
            print(f"⚠ {item.code}: {item.message}")
        return 0

    if args.command == "review-prompt":
        try:
            print(reviewer_prompt(args.report))
        except (OSError, ValueError) as exc:
            print(f"[report-quality] {exc}", file=sys.stderr)
            return 1
        return 0

    if args.command == "new-revision":
        try:
            review_path = start_new_revision(args.report)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"[report-quality] {exc}", file=sys.stderr)
            return 1
        print(review_path.relative_to(ROOT))
        return 0

    try:
        result = evaluate_report(args.report, policy)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[report-quality] {exc}", file=sys.stderr)
        return 1
    if args.write_decision or args.finalize:
        _evidence_path, review_path = quality_artifact_paths(args.report.resolve())
        if review_path.exists():
            review = _load_json(review_path)
            review["decision"] = {
                "status": result["decision"],
                "score": result["score"],
                "evaluated_on": dt.date.today().isoformat(),
                "policy_schema_version": policy["schema_version"],
            }
            _write_json(review_path, review)
    if args.finalize and result["decision"] == "pass":
        _set_frontmatter_fields(args.report.resolve(), {"status": args.final_status})
    _print_result(result, args.json)
    return 0 if result["decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
