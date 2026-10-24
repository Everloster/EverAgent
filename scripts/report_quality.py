#!/usr/bin/env python3
"""Model-agnostic evidence and review gate for durable EverAgent reports.

The script does not call an LLM. It creates portable artifacts that any harness
can fill, validates their provenance, computes a conservative rubric score, and
returns the next action: pass, revise, escalate, or needs_review.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import uuid
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

try:
    from .report_catalog import ROOT, collection_for_path, iter_reports, parse_frontmatter
except ImportError:  # Direct script execution.
    from report_catalog import ROOT, collection_for_path, iter_reports, parse_frontmatter


POLICY_PATH = ROOT / "config" / "report-quality-policy.json"
POLICY_ARCHIVE_DIR = ROOT / "config" / "report-quality-policies"
EVIDENCE_SCHEMA_PATH = ROOT / "schemas" / "report-evidence-v1.schema.json"
REVIEW_SCHEMA_PATH = ROOT / "schemas" / "report-review-v1.schema.json"
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
    _validate_policy(policy)
    if path.resolve() == POLICY_PATH.resolve():
        archive = POLICY_ARCHIVE_DIR / f"{policy['policy_id']}.json"
        if not archive.is_file():
            raise ValueError(f"active report policy is not archived: {archive.relative_to(ROOT)}")
        archived = json.loads(archive.read_text(encoding="utf-8"))
        _validate_policy(archived)
        if _canonical_json_bytes(archived) != _canonical_json_bytes(policy):
            raise ValueError("active report policy differs from its immutable archive")
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


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def policy_sha256(policy: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_json_bytes(policy)).hexdigest()


def policy_reference(policy: dict[str, Any]) -> dict[str, str]:
    return {
        "policy_id": str(policy["policy_id"]),
        "policy_sha256": policy_sha256(policy),
    }


def load_policy_revision(policy_id: str) -> dict[str, Any]:
    if re.fullmatch(r"[a-z0-9][a-z0-9._-]*", policy_id) is None:
        raise ValueError("policy_id contains unsafe characters")
    path = POLICY_ARCHIVE_DIR / f"{policy_id}.json"
    policy = _load_json(path)
    _validate_policy(policy)
    if policy.get("policy_id") != policy_id:
        raise ValueError("archived policy id does not match its filename")
    return policy


def _type_matches(value: Any, expected: str | list[str]) -> bool:
    if isinstance(expected, list):
        return any(_type_matches(value, item) for item in expected)
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return expected in checks and checks[expected](value)


def _schema_errors(value: Any, schema: dict[str, Any], location: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by the report artifact contracts."""
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None and not _type_matches(value, expected_type):
        return [f"{location}: type must be {expected_type}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{location}: value must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{location}: value is outside the declared enum")

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{location}.{key}: required field is missing")
        properties = schema.get("properties", {})
        for key, item in value.items():
            child = properties.get(key)
            if isinstance(child, dict):
                errors.extend(_schema_errors(item, child, f"{location}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}.{key}: additional property is not allowed")
    elif isinstance(value, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{location}: requires at least {minimum} items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, item_schema, f"{location}[{index}]"))
    elif isinstance(value, str):
        minimum = schema.get("minLength")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{location}: string is shorter than {minimum}")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            errors.append(f"{location}: string does not match {pattern}")
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        minimum = schema.get("minimum")
        maximum = schema.get("maximum")
        if isinstance(minimum, (int, float)) and value < minimum:
            errors.append(f"{location}: value is below {minimum}")
        if isinstance(maximum, (int, float)) and value > maximum:
            errors.append(f"{location}: value is above {maximum}")
    return errors


@lru_cache(maxsize=1)
def load_artifact_schemas() -> tuple[dict[str, Any], dict[str, Any]]:
    return _load_json(EVIDENCE_SCHEMA_PATH), _load_json(REVIEW_SCHEMA_PATH)


def _nested(schema: dict[str, Any], *keys: str) -> Any:
    value: Any = schema
    for key in keys:
        value = value[key]
    return value


def _validate_policy(policy: dict[str, Any]) -> None:
    errors: list[str] = []
    if policy.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if not str(policy.get("policy_id") or "").strip():
        errors.append("policy_id must be non-empty")
    if policy.get("current_report_schema") != CURRENT_REPORT_SCHEMA:
        errors.append("current_report_schema does not match the validator")
    dimensions = policy.get("dimensions")
    if not isinstance(dimensions, dict) or not dimensions:
        errors.append("dimensions must be a non-empty object")
        dimensions = {}
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in dimensions.values()):
        errors.append("dimension weights must be numeric")
    elif sum(dimensions.values()) != 100:
        errors.append("report quality dimension weights must sum to 100")

    evidence_schema, review_schema = load_artifact_schemas()
    evidence_tiers = set(_nested(evidence_schema, "properties", "quality_tier", "enum"))
    review_tiers = set(_nested(review_schema, "properties", "quality_tier", "enum"))
    policy_tiers = set((policy.get("tiers") or {}).keys())
    if evidence_tiers != review_tiers or policy_tiers != evidence_tiers:
        errors.append("quality tier enums drift between policy and schemas")
    schema_dimensions = set(
        _nested(
            review_schema,
            "properties",
            "reviews",
            "items",
            "properties",
            "scores",
            "properties",
        )
    )
    if set(dimensions) != schema_dimensions:
        errors.append("quality dimensions drift between policy and review schema")
    schema_failures = set(
        _nested(
            review_schema,
            "properties",
            "reviews",
            "items",
            "properties",
            "hard_failures",
            "items",
            "enum",
        )
    )
    if set(policy.get("hard_failure_codes") or []) != schema_failures:
        errors.append("hard failure codes drift between policy and review schema")
    schema_source_kinds = set(
        _nested(evidence_schema, "properties", "sources", "items", "properties", "kind", "enum")
    )
    if schema_source_kinds != SOURCE_KINDS:
        errors.append("source kinds drift between validator and evidence schema")
    schema_support_types = set(
        _nested(evidence_schema, "properties", "claims", "items", "properties", "support", "enum")
    )
    if schema_support_types != SUPPORT_TYPES:
        errors.append("support types drift between validator and evidence schema")
    schema_review_roles = set(
        _nested(review_schema, "properties", "reviews", "items", "properties", "role", "enum")
    )
    if schema_review_roles != REVIEW_ROLES:
        errors.append("review roles drift between validator and review schema")

    model_policy = policy.get("model_policy")
    if not isinstance(model_policy, dict):
        errors.append("model_policy must be an object")
        model_policy = {}
    for key in ("default_generator", "default_reviewer"):
        if not str(model_policy.get(key) or "").strip():
            errors.append(f"model_policy.{key} must be non-empty")
    for key in ("premium_reviewer_order", "strong_reviewers", "scarce_models", "disabled_models"):
        if not isinstance(model_policy.get(key), list):
            errors.append(f"model_policy.{key} must be an array")
    if set(model_policy.get("scarce_models") or []) & set(model_policy.get("disabled_models") or []):
        errors.append("scarce_models and disabled_models must be disjoint")
    if not set(model_policy.get("premium_reviewer_order") or []).issubset(
        set(model_policy.get("strong_reviewers") or [])
    ):
        errors.append("premium_reviewer_order must be a subset of strong_reviewers")

    for tier, rules in (policy.get("tiers") or {}).items():
        if not isinstance(rules, dict):
            errors.append(f"tier {tier} must be an object")
            continue
        if set(rules.get("minimum_dimension_scores") or {}) != set(dimensions):
            errors.append(f"tier {tier} minimum_dimension_scores drift from dimensions")
        for key in (
            "minimum_total",
            "minimum_sources",
            "minimum_primary_sources",
            "minimum_critical_claims",
            "reviewers_required",
            "strong_reviewers_required",
            "max_revision_rounds",
        ):
            if not isinstance(rules.get(key), (int, float)) or isinstance(rules.get(key), bool):
                errors.append(f"tier {tier}.{key} must be numeric")
    if errors:
        raise ValueError("; ".join(errors))


def _artifact_schema_findings(
    value: dict[str, Any],
    schema: dict[str, Any],
    *,
    code: str,
    label: str,
) -> list[QualityFinding]:
    return [
        QualityFinding("error", code, f"{label} 不符合 JSON schema：{error}")
        for error in _schema_errors(value, schema)[:20]
    ]


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _decision_record(
    result: dict[str, Any],
    policy: dict[str, Any],
    report: Path,
    evidence_path: Path,
) -> dict[str, Any]:
    reference = policy_reference(policy)
    decision = {
        "status": result["decision"],
        "score": result["score"],
        "evaluated_on": dt.date.today().isoformat(),
        **reference,
        "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
    }
    if evidence_path.exists():
        decision["evidence_sha256"] = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    return decision


def _policy_for_finalized_report(
    metadata: dict[str, object],
    review: dict[str, Any] | None,
    current_policy: dict[str, Any],
) -> tuple[dict[str, Any], list[QualityFinding]]:
    status = str(metadata.get("status") or "")
    if status in {"in_progress", "planned"}:
        return current_policy, []
    if not isinstance(review, dict):
        return current_policy, []
    decision = review.get("decision")
    if not isinstance(decision, dict) or not decision:
        return current_policy, []
    expected_digest = str(decision.get("policy_sha256") or "")
    expected_id = str(decision.get("policy_id") or "")
    findings: list[QualityFinding] = []
    if not expected_id or not expected_digest:
        findings.append(QualityFinding("error", "QG007", "已完成报告缺少最终判定的策略版本引用"))
    try:
        registered_policy = load_policy_revision(expected_id)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        findings.append(QualityFinding("error", "QG016", f"最终判定引用的策略版本不可用：{exc}"))
    else:
        if expected_digest != policy_sha256(registered_policy):
            findings.append(QualityFinding("error", "QG008", "最终判定的 policy_sha256 与已登记版本不一致"))
    return (registered_policy if not findings else current_policy), findings


def _finalized_binding_findings(
    report: Path,
    metadata: dict[str, object],
    evidence_path: Path,
    review: dict[str, Any] | None,
    score: float | None,
) -> list[QualityFinding]:
    if str(metadata.get("status") or "") in {"in_progress", "planned"}:
        return []
    if not isinstance(review, dict):
        return []
    decision = review.get("decision")
    if not isinstance(decision, dict) or not decision:
        return [QualityFinding("error", "QG011", "已完成报告缺少最终判定记录")]
    findings: list[QualityFinding] = []
    if decision.get("status") != "pass":
        findings.append(QualityFinding("error", "QG012", "已完成报告的最终判定不是 pass"))
    if decision.get("score") != score:
        findings.append(QualityFinding("error", "QG013", "最终判定分数与复核记录不一致"))
    report_digest = hashlib.sha256(report.read_bytes()).hexdigest()
    evidence_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest() if evidence_path.exists() else ""
    if decision.get("report_sha256") != report_digest:
        findings.append(QualityFinding("error", "QG014", "报告内容在最终判定后发生变化"))
    if decision.get("evidence_sha256") != evidence_digest:
        findings.append(QualityFinding("error", "QG015", "证据账本在最终判定后发生变化"))
    return findings


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
    evidence_schema, _review_schema = load_artifact_schemas()
    findings.extend(
        _artifact_schema_findings(
            manifest,
            evidence_schema,
            code="EVM000",
            label="证据账本",
        )
    )
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
        if kind == "local":
            locator = str(source.get("locator") or "")
            locator_path = Path(locator)
            local_candidate = ROOT / locator_path
            local_source = local_candidate.resolve()
            try:
                local_source.relative_to(ROOT.resolve())
                inside_root = not locator_path.is_absolute()
            except ValueError:
                inside_root = False
            if not locator or not inside_root or local_candidate.is_symlink() or not local_source.is_file():
                findings.append(QualityFinding("error", "EVM035", f"本地来源不存在或不是普通文件：{locator or '<empty>'}"))
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

    coverage = manifest.get("source_coverage")
    report_depth = str(metadata.get("report_depth") or "")
    requires_coverage = str(metadata.get("domain") or "") == "podcast-learning" and report_depth in {
        "standard",
        "deep",
    }
    if requires_coverage and (not isinstance(coverage, list) or len(coverage) < 3):
        findings.append(
            QualityFinding(
                "error",
                "EVM036",
                "standard/deep 播客报告至少登记 3 个 source_coverage 单元",
            )
        )
        coverage = []
    elif coverage is None:
        coverage = []
    elif not isinstance(coverage, list):
        findings.append(QualityFinding("error", "EVM037", "source_coverage 必须为数组"))
        coverage = []

    coverage_ids: list[str] = []
    core_coverage = 0
    for item in coverage:
        if not isinstance(item, dict):
            findings.append(QualityFinding("error", "EVM038", "source_coverage 单元必须为对象"))
            continue
        for key in ("id", "title", "importance", "status"):
            findings.extend(_required_string(item, key, "EVM039"))
        coverage_id = str(item.get("id") or "")
        if coverage_id:
            coverage_ids.append(coverage_id)
        importance = str(item.get("importance") or "")
        status = str(item.get("status") or "")
        if importance not in {"core", "supporting"}:
            findings.append(QualityFinding("error", "EVM040", f"coverage {coverage_id} 的 importance 无效"))
        if status not in {"included", "omitted"}:
            findings.append(QualityFinding("error", "EVM041", f"coverage {coverage_id} 的 status 无效"))
        refs = item.get("source_ids")
        if not isinstance(refs, list) or not refs:
            findings.append(QualityFinding("error", "EVM042", f"coverage {coverage_id} 必须绑定来源"))
            refs = []
        unknown = sorted(set(map(str, refs)) - known_sources)
        if unknown:
            findings.append(
                QualityFinding(
                    "error",
                    "EVM043",
                    f"coverage {coverage_id} 引用了未知 source：{', '.join(unknown)}",
                )
            )
        if importance == "core":
            core_coverage += 1
            if status != "included":
                findings.append(
                    QualityFinding("error", "EVM044", f"核心 coverage {coverage_id} 不得省略")
                )
        if status == "included":
            anchor = str(item.get("report_anchor") or "")
            if not anchor or anchor not in report_text:
                findings.append(
                    QualityFinding(
                        "error",
                        "EVM045",
                        f"coverage {coverage_id} 的 report_anchor 未出现在报告中",
                    )
                )
        elif not str(item.get("omission_reason") or "").strip():
            findings.append(
                QualityFinding("error", "EVM046", f"省略 coverage {coverage_id} 必须写 omission_reason")
            )
    if len(coverage_ids) != len(set(coverage_ids)):
        findings.append(QualityFinding("error", "EVM047", "source_coverage id 重复"))
    if requires_coverage and core_coverage < 3:
        findings.append(QualityFinding("error", "EVM048", "standard/deep 播客至少登记 3 个核心内容单元"))
    declared_chapters_match = re.match(r"\d+", str(metadata.get("chapters") or ""))
    if (
        requires_coverage
        and str(metadata.get("source_shownotes_chapters") or "").lower() == "true"
        and declared_chapters_match
        and len(coverage_ids) < int(declared_chapters_match.group(0))
    ):
        findings.append(
            QualityFinding(
                "error",
                "EVM049",
                "source_coverage 少于 frontmatter 声明的 shownotes 章节数；每章都需登记为 included 或 omitted",
            )
        )

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
        "coverage_unit_ids": coverage_ids,
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
    _evidence_schema, review_schema = load_artifact_schemas()
    findings.extend(
        _artifact_schema_findings(
            review,
            review_schema,
            code="REV000",
            label="复核记录",
        )
    )
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
    required_coverage = set(evidence_summary.get("coverage_unit_ids") or [])
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
        requires_source_map = str(metadata.get("domain") or "") == "podcast-learning" and str(
            metadata.get("report_depth") or ""
        ) in {"standard", "deep"}
        if requires_source_map:
            checks["coverage_unit_ids_checked"] = required_coverage
        for field, required in checks.items():
            actual = item.get(field)
            if not isinstance(actual, list) or not required.issubset(set(map(str, actual))):
                missing = sorted(required - set(map(str, actual or [])))
                findings.append(QualityFinding("error", "REV016", f"review #{index} 的 {field} 缺少：{', '.join(missing)}"))

        if requires_source_map:
            source_content_map = item.get("source_content_map")
            declared_chapters_match = re.match(r"\d+", str(metadata.get("chapters") or ""))
            minimum_map_units = max(3, len(required_coverage))
            if (
                str(metadata.get("source_shownotes_chapters") or "").lower() == "true"
                and declared_chapters_match
            ):
                minimum_map_units = max(minimum_map_units, int(declared_chapters_match.group(0)))
            if not isinstance(source_content_map, list) or len(source_content_map) < minimum_map_units:
                findings.append(
                    QualityFinding(
                        "error",
                        "REV028",
                        f"review #{index} 的 source_content_map 至少需要 {minimum_map_units} 个独立来源单元",
                    )
                )
                source_content_map = []

            map_ids: list[str] = []
            mapped_coverage_ids: set[str] = set()
            known_source_ids = set(evidence_summary["source_ids"])
            for map_item in source_content_map:
                if not isinstance(map_item, dict):
                    findings.append(QualityFinding("error", "REV029", f"review #{index} 的 source_content_map 单元必须为对象"))
                    continue
                for field in ("id", "title", "importance", "assessment", "notes"):
                    if not isinstance(map_item.get(field), str) or not str(map_item[field]).strip():
                        findings.append(
                            QualityFinding(
                                "error",
                                "REV029",
                                f"review #{index} 的 source_content_map 单元缺少非空字段 {field}",
                            )
                        )
                map_id = str(map_item.get("id") or "")
                if map_id:
                    map_ids.append(map_id)
                importance = str(map_item.get("importance") or "")
                assessment = str(map_item.get("assessment") or "")
                if importance not in {"core", "supporting"} or assessment not in {
                    "covered",
                    "partial",
                    "missing",
                }:
                    findings.append(
                        QualityFinding(
                            "error",
                            "REV030",
                            f"review #{index} 的 source_content_map {map_id or '<unknown>'} 分类无效",
                        )
                    )
                source_refs = map_item.get("source_ids")
                if not isinstance(source_refs, list) or not source_refs:
                    findings.append(
                        QualityFinding(
                            "error",
                            "REV031",
                            f"review #{index} 的 source_content_map {map_id or '<unknown>'} 必须绑定来源",
                        )
                    )
                    source_refs = []
                unknown_sources = sorted(set(map(str, source_refs)) - known_source_ids)
                if unknown_sources:
                    findings.append(
                        QualityFinding(
                            "error",
                            "REV031",
                            f"review #{index} 的 source_content_map {map_id or '<unknown>'} 引用了未知 source：{', '.join(unknown_sources)}",
                        )
                    )
                coverage_refs = map_item.get("matched_coverage_unit_ids")
                if not isinstance(coverage_refs, list):
                    findings.append(
                        QualityFinding(
                            "error",
                            "REV032",
                            f"review #{index} 的 source_content_map {map_id or '<unknown>'} 缺少 matched_coverage_unit_ids",
                        )
                    )
                    coverage_refs = []
                unknown_coverage = sorted(set(map(str, coverage_refs)) - required_coverage)
                if unknown_coverage:
                    findings.append(
                        QualityFinding(
                            "error",
                            "REV032",
                            f"review #{index} 的 source_content_map {map_id or '<unknown>'} 匹配了未知 coverage：{', '.join(unknown_coverage)}",
                        )
                    )
                mapped_coverage_ids.update(map(str, coverage_refs))
                if importance == "core" and (assessment != "covered" or not coverage_refs):
                    findings.append(
                        QualityFinding(
                            "error",
                            "REV033",
                            f"review #{index} 的核心来源单元 {map_id or '<unknown>'} 未被完整覆盖",
                        )
                    )
            if len(map_ids) != len(set(map_ids)):
                findings.append(QualityFinding("error", "REV034", f"review #{index} 的 source_content_map id 重复"))
            unmapped_coverage = sorted(required_coverage - mapped_coverage_ids)
            if unmapped_coverage:
                findings.append(
                    QualityFinding(
                        "error",
                        "REV035",
                        f"review #{index} 的独立来源地图未映射 coverage：{', '.join(unmapped_coverage)}",
                    )
                )
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
    current_policy = policy or load_policy()
    metadata = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace"))
    tier = str(metadata.get("quality_tier") or "")
    findings: list[QualityFinding] = []
    evidence_path, review_path = quality_artifact_paths(report)
    manifest: dict[str, Any] | None = None
    review: dict[str, Any] | None = None

    if metadata.get("quality_schema") != CURRENT_REPORT_SCHEMA:
        findings.append(QualityFinding("error", "QG001", f"质量流水线要求 quality_schema: {CURRENT_REPORT_SCHEMA}"))

    if evidence_path.exists():
        try:
            manifest = _load_json(evidence_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            findings.append(QualityFinding("error", "QG004", f"证据账本无法读取：{exc}"))
    else:
        findings.append(QualityFinding("error", "QG003", f"缺少证据账本：{evidence_path.relative_to(ROOT)}"))
    if review_path.exists():
        try:
            review = _load_json(review_path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            findings.append(QualityFinding("error", "QG006", f"复核记录无法读取：{exc}"))
    else:
        findings.append(QualityFinding("error", "QG005", f"缺少独立复核记录：{review_path.relative_to(ROOT)}"))

    effective_policy, policy_findings = _policy_for_finalized_report(
        metadata,
        review,
        current_policy,
    )
    findings.extend(policy_findings)
    if tier not in effective_policy.get("tiers", {}):
        findings.append(QualityFinding("error", "QG002", f"未知或缺失 quality_tier：{tier or '<empty>'}"))

    evidence_summary = {
        "requirement_ids": [],
        "source_ids": [],
        "claim_ids": [],
        "critical_claim_ids": [],
        "critical_source_ids": [],
        "coverage_unit_ids": [],
        "generator_model": "",
        "generator_run_id": "",
        "generator_explicit_override": False,
    }
    if manifest is not None:
        evidence_findings, evidence_summary = validate_evidence_manifest(
            report,
            metadata,
            manifest,
            effective_policy,
        )
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
    if review is not None:
        review_findings, review_summary = validate_review_record(
            report,
            metadata,
            review,
            evidence_summary,
            effective_policy,
        )
        findings.extend(review_findings)
    findings.extend(
        _finalized_binding_findings(
            report,
            metadata,
            evidence_path,
            review,
            review_summary["score"],
        )
    )

    error_codes = {finding.code for finding in findings if finding.severity == "error"}
    incomplete_codes = {"QG003", "QG004", "QG005", "QG006", "REV005", "REV006", "REV014", "REV015", "REV016", "REV017"}
    quality_failure_codes = {"REV018", "SCORE001", "SCORE002"}
    blocking_codes = error_codes - incomplete_codes - quality_failure_codes
    if not error_codes:
        decision = "pass"
    elif blocking_codes:
        decision = "blocked"
    elif error_codes & quality_failure_codes:
        max_rounds = int(effective_policy.get("tiers", {}).get(tier, {}).get("max_revision_rounds", 1))
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
        "policy_id": effective_policy.get("policy_id", ""),
        "policy_sha256": policy_sha256(effective_policy),
        "policy_source": "archive" if effective_policy is not current_policy else "current",
        "recommended_models": effective_policy["model_policy"].get("premium_reviewer_order", []) if decision == "escalate" else [],
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
        "source_coverage": [],
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
            "coverage_unit_ids_checked": [],
            "source_content_map": [],
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
    report_digest = hashlib.sha256(report.read_bytes()).hexdigest()
    evidence_digest = hashlib.sha256(evidence_path.read_bytes()).hexdigest()
    dimensions = "、".join(f"{name}（权重 {weight}%）" for name, weight in policy["dimensions"].items())
    score_bands = "；".join(f"{name.replace('_', '–')}：{text}" for name, text in policy.get("score_bands", {}).items())
    hard_failures = "、".join(policy.get("hard_failure_codes", []))
    return f"""你是 EverAgent 报告的独立审稿人。请在全新 context 中完成复核，不参考生成者的推理过程。

报告：{report_relative_path(report)}
证据账本：{evidence_path.relative_to(ROOT)}
复核记录：{review_path.relative_to(ROOT)}
报告 SHA-256：{report_digest}
证据账本 SHA-256：{evidence_digest}
质量等级：{tier}

要求：
1. 开始前在实际审阅目录核对报告与 evidence 的 SHA-256；任一不匹配就停止，在任务回执和 review notes/escalation 中报告 `wrong_target_snapshot`，不得改审另一份同名文件或其它 worktree；它是调度错误，不得写入 `hard_failures`。
2. 先读原始来源，不先接受报告或 evidence 的内容选择；把独立识别出的核心问题、论证、案例和反方逐项写入 `source_content_map`。若有 shownotes 章节，每章至少对应一个地图单元。
3. 再打开报告与证据账本，把每个独立地图单元映射到 `matched_coverage_unit_ids`，填写 `assessment: covered | partial | missing`，并把已实际复核的单元 id 填入 `coverage_unit_ids_checked`。生成者完全省略的核心内容即使没有 claim id，也要作为遗漏需求记录；standard/deep 播客遗漏核心单元时使用 `core_requirement_missing`。
4. 检查报告是否可独立阅读，不能因为 polished 保存了细节就允许报告只剩索引或速览。
5. 播客报告必须运行 `python3 podcast-learning/scripts/audit_transcript.py <transcript> --json` 或核对同等机器收据；头尾抽查不能替代时间戳单调性检查。
6. 按 0–100 分填写：{dimensions}，并为每一维填写 `score_reasons`。评分锚点：{score_bands}。
7. 不直接改报告。先完成复核记录，再由生成者依据问题清单修订。
8. 完成后运行 `python3 scripts/report_quality.py check {report_relative_path(report)}`，不得自行宣称通过。
9. 报告修订后先运行 `python3 scripts/report_quality.py new-revision {report_relative_path(report)}`，再创建新一轮 Reviewer 记录。
10. 硬失败只使用这些代码：{hard_failures}。
"""


def cross_model_sampling_status(policy: dict[str, Any] | None = None) -> dict[str, Any]:
    active = policy or load_policy()
    sampling = active.get("cross_model_sampling") or {}
    enabled = sampling.get("enabled") is True
    interval = int(sampling.get("important_reports_per_sample") or 0)
    eligible_tiers = set(sampling.get("eligible_tiers") or ["important"])
    strong_reviewers = {
        normalize_model(item, active)
        for item in active["model_policy"].get("strong_reviewers", [])
    }
    recorded_on = str(active.get("preference_source", {}).get("recorded_on") or "")
    eligible: list[dict[str, Any]] = []

    if enabled and interval > 0:
        for _collection, report in iter_reports():
            metadata = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace"))
            if metadata.get("quality_schema") != CURRENT_REPORT_SCHEMA:
                continue
            if metadata.get("status") not in {"completed", "archived"}:
                continue
            if metadata.get("quality_tier") not in eligible_tiers:
                continue
            updated_on = str(metadata.get("updated_on") or "")
            if recorded_on and updated_on and updated_on < recorded_on:
                continue
            evidence_path, review_path = quality_artifact_paths(report)
            if not evidence_path.is_file() or not review_path.is_file():
                continue
            try:
                evidence = _load_json(evidence_path)
                review = _load_json(review_path)
            except (OSError, json.JSONDecodeError):
                continue
            generator = normalize_model(
                str((evidence.get("generator") or {}).get("model") or ""), active
            )
            current_reviewer_models = [
                normalize_model(
                    str(((item.get("reviewer") or {}).get("model") or "")), active
                )
                for item in review.get("reviews") or []
                if isinstance(item, dict)
            ]
            history = review.get("history") or []
            previous_reviewer_models: list[str] = []
            if isinstance(history, list) and history:
                previous = history[-1]
                if isinstance(previous, dict):
                    previous_reviewer_models = [
                        normalize_model(
                            str(((item.get("reviewer") or {}).get("model") or "")), active
                        )
                        for item in previous.get("reviews") or []
                        if isinstance(item, dict)
                    ]
            reviewer_models = list(
                dict.fromkeys([*current_reviewer_models, *previous_reviewer_models])
            )
            cross_model = any(
                reviewer in strong_reviewers and reviewer != generator
                for reviewer in reviewer_models
            )
            decision_dates = [
                str((review.get("decision") or {}).get("evaluated_on") or "")
            ]
            if isinstance(history, list):
                decision_dates.extend(
                    str((item.get("decision") or {}).get("evaluated_on") or "")
                    for item in history
                    if isinstance(item, dict)
                )
            sampling_on = (
                str(evidence.get("created_on") or "")
                or min((value for value in decision_dates if value), default="")
                or updated_on
            )
            eligible.append(
                {
                    "report": report_relative_path(report),
                    "updated_on": updated_on,
                    "sampling_on": sampling_on,
                    "generator_model": generator,
                    "reviewer_models": reviewer_models,
                    "cross_model_audited": cross_model,
                }
            )

    eligible.sort(key=lambda item: (item["sampling_on"], item["report"]))
    pending = [item for item in eligible if not item["cross_model_audited"]]
    sampling_windows: list[dict[str, Any]] = []
    uncovered_windows: list[list[dict[str, Any]]] = []
    if interval > 0:
        for start in range(0, len(eligible), interval):
            reports = eligible[start:start + interval]
            complete = len(reports) == interval
            covered = any(item["cross_model_audited"] for item in reports)
            sampling_windows.append(
                {
                    "start": start + 1,
                    "end": start + len(reports),
                    "complete": complete,
                    "covered": covered,
                    "reports": [item["report"] for item in reports],
                }
            )
            if complete and not covered:
                uncovered_windows.append(reports)
    configured_order = list(sampling.get("reviewer_order") or [])
    normalized_order = [normalize_model(item, active) for item in configured_order]
    recommended: dict[str, Any] | None = None
    due_candidates = (
        [item for item in uncovered_windows[0] if not item["cross_model_audited"]]
        if uncovered_windows
        else []
    )
    if due_candidates:
        def reviewer_rank(item: dict[str, Any]) -> tuple[int, str, str]:
            generator = str(item["generator_model"])
            rank = next(
                (index for index, reviewer in enumerate(normalized_order) if reviewer != generator),
                len(normalized_order),
            )
            return rank, str(item["sampling_on"]), str(item["report"])

        recommended = min(due_candidates, key=reviewer_rank)
    recommended_reviewers = (
        [
            configured_order[index]
            for index, reviewer in enumerate(normalized_order)
            if reviewer != recommended["generator_model"]
        ]
        if recommended is not None
        else []
    )
    return {
        "schema_version": 1,
        "policy_id": active["policy_id"],
        "enabled": enabled,
        "interval": interval,
        "eligible_tiers": sorted(eligible_tiers),
        "eligible_reports": len(eligible),
        "cross_model_audited_reports": len(eligible) - len(pending),
        "pending_same_model_reports": len(pending),
        "complete_windows": sum(1 for item in sampling_windows if item["complete"]),
        "covered_windows": sum(
            1 for item in sampling_windows if item["complete"] and item["covered"]
        ),
        "uncovered_windows": len(uncovered_windows),
        "tail_reports": len(eligible) % interval if interval > 0 else 0,
        "sample_due": enabled and bool(uncovered_windows),
        "recommended_report": recommended["report"] if recommended else None,
        "recommended_reviewers": recommended_reviewers,
        "sampling_windows": sampling_windows,
        "reports": eligible,
    }


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
    try:
        policy = load_policy()
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"[report-quality] invalid policy or schema: {exc}", file=sys.stderr)
        return 1
    tier_choices = tuple(sorted(policy["tiers"]))
    parser = argparse.ArgumentParser(description="Manage and validate EverAgent report quality artifacts")
    subparsers = parser.add_subparsers(dest="command", required=True)

    policy_parser = subparsers.add_parser("policy", help="show model routing and quality thresholds")
    policy_parser.add_argument("--tier", choices=tier_choices)
    policy_parser.add_argument("--json", action="store_true")

    sampling_parser = subparsers.add_parser(
        "sampling-status", help="show whether a sampled cross-model audit is due"
    )
    sampling_parser.add_argument("--json", action="store_true")

    init_parser = subparsers.add_parser("init", help="initialize report-v2 evidence and review artifacts")
    init_parser.add_argument("report", type=Path)
    init_parser.add_argument("--tier", choices=tier_choices, default=None)
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
    if args.command == "policy":
        result = ({**policy, "policy_sha256": policy_sha256(policy)} if args.tier is None else {
            "schema_version": policy["schema_version"],
            "policy_id": policy["policy_id"],
            "policy_sha256": policy_sha256(policy),
            "model_policy": policy["model_policy"],
            "tier": args.tier,
            "quality": policy["tiers"][args.tier],
        })
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.command == "sampling-status":
        result = cross_model_sampling_status(policy)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(
                f"policy={result['policy_id']}｜eligible={result['eligible_reports']}｜"
                f"pending={result['pending_same_model_reports']}/{result['interval']}｜"
                f"sample_due={str(result['sample_due']).lower()}"
            )
            if result["recommended_report"]:
                print("  建议抽样：" + str(result["recommended_report"]))
            if result["recommended_reviewers"]:
                print("  Reviewer 顺序：" + " → ".join(result["recommended_reviewers"]))
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
    report_metadata = parse_frontmatter(
        args.report.resolve().read_text(encoding="utf-8", errors="replace")
    )
    if (args.write_decision or args.finalize) and str(report_metadata.get("status") or "") not in {
        "in_progress",
        "planned",
    }:
        print(
            "[report-quality] finalized reports are immutable; run new-revision before writing a new decision",
            file=sys.stderr,
        )
        return 1
    if args.finalize and result["decision"] == "pass":
        _set_frontmatter_fields(args.report.resolve(), {"status": args.final_status})
    if args.write_decision or args.finalize:
        evidence_path, review_path = quality_artifact_paths(args.report.resolve())
        if review_path.exists():
            review = _load_json(review_path)
            review["decision"] = _decision_record(
                result,
                policy,
                args.report.resolve(),
                evidence_path,
            )
            _write_json(review_path, review)
    if args.finalize and result["decision"] == "pass":
        result = evaluate_report(args.report)
    _print_result(result, args.json)
    return 0 if result["decision"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
