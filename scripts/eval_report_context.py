#!/usr/bin/env python3
"""Static and replay evaluation for EverAgent report context.

Static mode checks context size, duplication, links, skill metadata, and the ACE
task suite. ``--template`` emits a run-record template. ``--score`` evaluates a
completed run record against the suite's observable expectations.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path

try:
    from .report_catalog import COLLECTION_BY_ID, ROOT, parse_frontmatter
    from .report_quality import load_policy, normalize_model
except ImportError:  # Direct script execution.
    from report_catalog import COLLECTION_BY_ID, ROOT, parse_frontmatter
    from report_quality import load_policy, normalize_model


DEFAULT_AGENTS_BUDGET = 32 * 1024
WARN_BUDGET_RATIO = 0.75
SUITE_PATH = ROOT / "evals" / "ace-report-tasks.json"
ANCHORS_PATH = ROOT / "evals" / "report-quality-anchors.json"
REPORT_SKILL = ROOT / ".agents" / "skills" / "everagent-report" / "SKILL.md"
QUALITY_GUIDE = ROOT / "docs" / "REPORT_QUALITY_GATE.md"
QUALITY_SCHEMAS = (
    ROOT / "schemas" / "report-evidence-v1.schema.json",
    ROOT / "schemas" / "report-review-v1.schema.json",
)
STALE_DIRECTIVES = (
    "贴一个 GitHub repo 链接即可触发",
    "每次研究完顺手做一次事C",
    "每批任务结束，若发现新问题/新解法，把一行改进写进",
    "禁止修改 SKILL.md / 脚本 / README",
)


def _load_suite() -> dict:
    return json.loads(SUITE_PATH.read_text(encoding="utf-8"))


def _agent_files() -> list[Path]:
    files = [ROOT / "AGENTS.md"]
    files.extend(sorted(path for path in ROOT.glob("*/AGENTS.md") if path.is_file()))
    return files


def _active_context_files(agent_files: list[Path]) -> list[Path]:
    files = set(agent_files)
    files.update(
        {
            REPORT_SKILL,
            ROOT / "docs" / "REPORT_WORKFLOW.md",
            ROOT / "docs" / "CONTEXT_ENGINEERING.md",
            QUALITY_GUIDE,
        }
    )
    for domain in COLLECTION_BY_ID:
        skills = ROOT / domain / "skills"
        if not skills.exists():
            continue
        files.update(skills.rglob("SKILL.md"))
        files.update(skills.rglob("references/*.md"))
    return sorted(path for path in files if path.exists())


def _paragraph_duplicates(files: list[Path]) -> list[dict[str, object]]:
    occurrences: dict[str, list[str]] = defaultdict(list)
    original: dict[str, str] = {}
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for block in re.split(r"\n\s*\n", text):
            normalized = re.sub(r"\s+", " ", block).strip()
            if len(normalized) < 120 or normalized.startswith("<!-- BEGIN MANAGED"):
                continue
            occurrences[normalized].append(str(path.relative_to(ROOT)))
            original[normalized] = block.strip()
    return [
        {
            "files": sorted(set(paths)),
            "bytes": len(original[key].encode("utf-8")),
            "preview": original[key][:180],
        }
        for key, paths in occurrences.items()
        if len(set(paths)) > 1
    ]


def _relative_link_errors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for target in re.findall(r"\[[^\]]*\]\((\.\.?/[^)]+)\)", text):
        clean = target.strip().strip("<>").split("#", 1)[0]
        if "{" in clean or "}" in clean or "..." in clean:
            continue
        if clean and not (path.parent / clean).resolve().exists():
            errors.append(f"{path.relative_to(ROOT)} -> {target}")
    return errors


def static_evaluation() -> dict[str, object]:
    files = _agent_files()
    context_files = _active_context_files(files)
    root_agents = ROOT / "AGENTS.md"
    chains: dict[str, dict[str, object]] = {}
    warnings: list[str] = []
    errors: list[str] = []

    for domain in [*COLLECTION_BY_ID, "root"]:
        chain = [root_agents]
        domain_agents = ROOT / domain / "AGENTS.md"
        if domain != "root" and domain_agents.exists():
            chain.append(domain_agents)
        total = sum(path.stat().st_size for path in chain)
        ratio = total / DEFAULT_AGENTS_BUDGET
        chains[domain] = {
            "files": [str(path.relative_to(ROOT)) for path in chain],
            "bytes": total,
            "budget_ratio": round(ratio, 4),
        }
        if ratio >= WARN_BUDGET_RATIO:
            warnings.append(f"{domain} 的 AGENTS 链占默认 32 KiB 的 {ratio:.1%}")
        if ratio > 1:
            errors.append(f"{domain} 的 AGENTS 链超过默认 32 KiB")

    duplicates = _paragraph_duplicates(files)
    if duplicates:
        warnings.append(f"AGENTS 文件存在 {len(duplicates)} 组跨文件重复长段落")

    unconditional_reads: list[str] = []
    for path in files:
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if (
                re.search(r"每次.*(?:先)?读|开始任何工作前.*读|默认通读|必须.*通读", line)
                and not re.search(r"不(?:要|得).*通读|禁止.*通读", line)
            ):
                unconditional_reads.append(f"{path.relative_to(ROOT)}:{number}: {line.strip()}")
    if unconditional_reads:
        warnings.append(f"发现 {len(unconditional_reads)} 条可能导致无条件读取的规则")

    link_errors: list[str] = []
    for path in context_files:
        link_errors.extend(_relative_link_errors(path))
    if link_errors:
        errors.extend(f"无效 context 链接：{item}" for item in link_errors)

    for path in context_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for directive in STALE_DIRECTIVES:
            if directive in text:
                errors.append(f"过时 context 指令：{path.relative_to(ROOT)} -> {directive}")

    if not REPORT_SKILL.exists():
        errors.append("缺少 .agents/skills/everagent-report/SKILL.md")
        skill = {}
        description = ""
    else:
        skill_text = REPORT_SKILL.read_text(encoding="utf-8")
        skill = parse_frontmatter(skill_text)
        description = str(skill.get("description") or "")
        if skill.get("name") != "everagent-report":
            errors.append("everagent-report skill 的 name 不正确")
        if not description:
            errors.append("everagent-report skill 缺少 description")
        elif len(description) > 500:
            warnings.append("everagent-report description 超过 500 characters")
        if "skip" not in description.lower() and "不" not in description:
            warnings.append("everagent-report description 缺少明显的非触发边界")

    try:
        suite = _load_suite()
    except (OSError, json.JSONDecodeError) as exc:
        suite = {"cases": []}
        errors.append(f"ACE 任务集无法读取：{exc}")
    cases = suite.get("cases", [])
    ids = [case.get("id") for case in cases]
    if not cases:
        errors.append("ACE 任务集为空")
    if len(ids) != len(set(ids)):
        errors.append("ACE 任务集存在重复 id")
    valid_routes = set(COLLECTION_BY_ID) | {"root"}
    for case in cases:
        missing = [
            field
            for field in (
                "id",
                "prompt",
                "expected_route",
                "artifact_policy",
                "max_initial_project_files",
                "quality_tier",
                "required_checks",
            )
            if field not in case
        ]
        if missing:
            errors.append(f"ACE case {case.get('id', '<unknown>')} 缺字段：{', '.join(missing)}")
        if case.get("expected_route") not in valid_routes:
            errors.append(f"ACE case {case.get('id')} route 未登记：{case.get('expected_route')}")

    try:
        policy = load_policy()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        policy = {}
        errors.append(f"报告质量策略无法读取：{exc}")
    if policy:
        model_policy = policy["model_policy"]
        if normalize_model(model_policy.get("default_generator", ""), policy) != "glm-5.3":
            errors.append("默认报告生成模型必须为 GLM 5.3")
        scarce = {normalize_model(item, policy) for item in model_policy.get("scarce_models", [])}
        if "kimi-k3" not in scarce:
            errors.append("Kimi K3 必须登记为稀缺模型")
        disabled = {normalize_model(item, policy) for item in model_policy.get("disabled_models", [])}
        if "minimax-m3" not in disabled:
            errors.append("MiniMax M3 必须登记为禁用模型")
        valid_tiers = set(policy.get("tiers", {}))
        for case in cases:
            tier = case.get("quality_tier")
            required_checks = set(case.get("required_checks") or [])
            artifact_checks = set(case.get("artifact_required_checks") or [])
            requires_quality = "quality_gate" in required_checks or "quality_gate" in artifact_checks
            if requires_quality and tier not in valid_tiers:
                errors.append(f"ACE case {case.get('id')} 缺少有效 quality_tier")
            if tier is not None and not requires_quality:
                errors.append(f"ACE case {case.get('id')} 声明 quality_tier 但缺少 quality_gate 检查")

    try:
        anchors = json.loads(ANCHORS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        anchors = {"anchors": []}
        errors.append(f"质量锚点无法读取：{exc}")
    anchor_ids: set[str] = set()
    for anchor in anchors.get("anchors", []):
        anchor_id = str(anchor.get("id") or "")
        if not anchor_id or anchor_id in anchor_ids:
            errors.append(f"质量锚点 id 缺失或重复：{anchor_id or '<empty>'}")
        anchor_ids.add(anchor_id)
        report_path = ROOT / str(anchor.get("report_path") or "")
        if not report_path.is_file():
            errors.append(f"质量锚点报告不存在：{anchor.get('report_path')}")
    for case in cases:
        anchor_id = case.get("reference_anchor")
        if anchor_id and anchor_id not in anchor_ids:
            errors.append(f"ACE case {case.get('id')} 引用了未知质量锚点：{anchor_id}")

    for schema_path in QUALITY_SCHEMAS:
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"质量 schema 无法读取：{schema_path.relative_to(ROOT)}: {exc}")

    return {
        "schema_version": 1,
        "agents_files": len(files),
        "agents_total_bytes": sum(path.stat().st_size for path in files),
        "active_context_files": len(context_files),
        "chains": chains,
        "duplicate_blocks": duplicates,
        "unconditional_reads": unconditional_reads,
        "report_skill_description_chars": len(description),
        "ace_cases": len(cases),
        "quality_anchors": len(anchor_ids),
        "warnings": warnings,
        "errors": errors,
    }


def run_template() -> dict[str, object]:
    suite = _load_suite()
    return {
        "schema_version": 1,
        "model": "",
        "harness": "",
        "context_revision": "",
        "cases": [
            {
                "id": case["id"],
                "route": None,
                "artifact_created": None,
                "initial_project_files": [],
                "paused_before_research": None,
                "checks_completed": [],
                "quality_tier": case.get("quality_tier"),
                "quality_decision": None,
                "report_quality_score": None,
                "generator_model": "",
                "reviewer_models": [],
                "anchor_comparison": None,
                "revision_count": 0,
                "escalated": False,
                "input_tokens": None,
                "elapsed_seconds": None,
                "tool_failures": 0,
                "completed": None,
                "safety_violation": None,
                "notes": "",
            }
            for case in suite["cases"]
        ],
    }


def score_run(path: Path) -> dict[str, object]:
    suite = _load_suite()
    expected = {case["id"]: case for case in suite["cases"]}
    observed_doc = json.loads(path.read_text(encoding="utf-8"))
    observed = {case["id"]: case for case in observed_doc.get("cases", [])}
    policy = load_policy()
    disabled_models = {
        normalize_model(item, policy)
        for item in policy["model_policy"].get("disabled_models", [])
    }
    rows: list[dict[str, object]] = []

    for case_id, exp in expected.items():
        obs = observed.get(case_id)
        if obs is None:
            rows.append({"id": case_id, "score": 0, "max_score": 100, "missing": True})
            continue
        score = 0
        hard_failure = False
        checks: dict[str, bool] = {}
        checks["route"] = obs.get("route") == exp["expected_route"]
        score += 25 if checks["route"] else 0

        artifact_policy = exp["artifact_policy"]
        created = obs.get("artifact_created")
        checks["artifact"] = (
            created is True
            if artifact_policy in {"required", "update_existing"}
            else created is False
            if artifact_policy == "forbidden"
            else created in {True, False}
        )
        score += 15 if checks["artifact"] else 0
        if not checks["artifact"]:
            hard_failure = True

        initial_files = obs.get("initial_project_files") or []
        checks["context_budget"] = len(initial_files) <= exp["max_initial_project_files"]
        score += 15 if checks["context_budget"] else 0

        checks["initiative"] = not (
            exp.get("must_not_pause_before_research") and obs.get("paused_before_research") is True
        )
        score += 10 if checks["initiative"] else 0

        completed_checks = set(obs.get("checks_completed") or [])
        required_checks = set(exp.get("required_checks") or [])
        if created is True:
            required_checks.update(exp.get("artifact_required_checks") or [])
        checks["checks"] = required_checks.issubset(completed_checks)
        score += 25 if checks["checks"] else 0

        checks["completion"] = obs.get("completed") is True
        score += 10 if checks["completion"] else 0

        quality_required = exp.get("quality_tier") is not None and created is True
        if quality_required:
            expected_tier = exp.get("quality_tier")
            checks["quality_tier"] = (
                obs.get("quality_tier") == expected_tier
                if expected_tier
                else obs.get("quality_tier") in policy.get("tiers", {})
            )
            checks["quality_gate"] = obs.get("quality_decision") == "pass"
            quality_score = obs.get("report_quality_score")
            minimum_total = policy["tiers"][obs.get("quality_tier")]["minimum_total"] if checks["quality_tier"] else 101
            checks["quality_score"] = (
                isinstance(quality_score, (int, float))
                and not isinstance(quality_score, bool)
                and quality_score >= minimum_total
            )
            if not checks["quality_tier"] or not checks["quality_gate"] or not checks["quality_score"]:
                hard_failure = True
        else:
            checks["quality_tier"] = True
            checks["quality_gate"] = True
            checks["quality_score"] = True

        models = [obs.get("generator_model"), *(obs.get("reviewer_models") or [])]
        normalized_models = {normalize_model(item, policy) for item in models if item}
        checks["model_policy"] = not bool(normalized_models & disabled_models)
        if not checks["model_policy"]:
            hard_failure = True

        anchor_id = exp.get("reference_anchor")
        checks["anchor"] = not anchor_id or obs.get("anchor_comparison") in {"win", "tie"}
        if not checks["anchor"]:
            hard_failure = True

        if obs.get("safety_violation") is not False:
            hard_failure = True
            checks["safety"] = False
        else:
            checks["safety"] = True

        if hard_failure:
            score = 0

        scarce_models = {
            normalize_model(item, policy)
            for item in policy["model_policy"].get("scarce_models", [])
        }
        scarce_calls = sum(normalize_model(item, policy) in scarce_models for item in models if item)
        rows.append(
            {
                "id": case_id,
                "score": score,
                "max_score": 100,
                "report_quality_score": obs.get("report_quality_score"),
                "revision_count": obs.get("revision_count", 0),
                "escalated": obs.get("escalated") is True,
                "scarce_model_calls": scarce_calls,
                "input_tokens": obs.get("input_tokens"),
                "elapsed_seconds": obs.get("elapsed_seconds"),
                "tool_failures": obs.get("tool_failures", 0),
                "checks": checks,
            }
        )

    total = sum(row["score"] for row in rows)
    maximum = sum(row["max_score"] for row in rows)
    return {
        "schema_version": 1,
        "model": observed_doc.get("model", ""),
        "harness": observed_doc.get("harness", ""),
        "context_revision": observed_doc.get("context_revision", ""),
        "score": total,
        "max_score": maximum,
        "score_ratio": round(total / maximum, 4) if maximum else 0,
        "cases": rows,
    }


def _percentile_nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def aggregate_runs(paths: list[Path]) -> dict[str, object]:
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for path in paths:
        result = score_run(path)
        key = (str(result["model"]), str(result["harness"]), str(result["context_revision"]))
        groups[key].append(result)

    summaries = []
    for (model, harness, context_revision), runs in sorted(groups.items()):
        case_scores = [float(case["score"]) for run in runs for case in run["cases"]]
        quality_scores = [
            float(case["report_quality_score"])
            for run in runs
            for case in run["cases"]
            if isinstance(case.get("report_quality_score"), (int, float))
            and not isinstance(case.get("report_quality_score"), bool)
        ]
        revisions = [int(case.get("revision_count") or 0) for run in runs for case in run["cases"]]
        summaries.append(
            {
                "model": model,
                "harness": harness,
                "context_revision": context_revision,
                "runs": len(runs),
                "cases": len(case_scores),
                "mean_task_score": round(sum(case_scores) / len(case_scores), 2) if case_scores else 0,
                "p10_task_score": _percentile_nearest_rank(case_scores, 0.10),
                "mean_report_quality_score": round(sum(quality_scores) / len(quality_scores), 2) if quality_scores else 0,
                "p10_report_quality_score": _percentile_nearest_rank(quality_scores, 0.10),
                "perfect_case_rate": round(sum(score == 100 for score in case_scores) / len(case_scores), 4) if case_scores else 0,
                "zero_score_rate": round(sum(score == 0 for score in case_scores) / len(case_scores), 4) if case_scores else 0,
                "mean_revision_count": round(sum(revisions) / len(revisions), 2) if revisions else 0,
                "escalation_rate": round(sum(case.get("escalated") is True for run in runs for case in run["cases"]) / len(case_scores), 4) if case_scores else 0,
                "scarce_model_calls": sum(int(case.get("scarce_model_calls") or 0) for run in runs for case in run["cases"]),
                "input_tokens": sum(int(case.get("input_tokens") or 0) for run in runs for case in run["cases"]),
                "elapsed_seconds": round(sum(float(case.get("elapsed_seconds") or 0) for run in runs for case in run["cases"]), 2),
                "tool_failures": sum(int(case.get("tool_failures") or 0) for run in runs for case in run["cases"]),
            }
        )
    return {"schema_version": 1, "groups": summaries}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate EverAgent report context")
    parser.add_argument("--json", action="store_true", help="emit static evaluation as JSON")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--template", action="store_true", help="emit behavioral run template")
    mode.add_argument("--score", type=Path, help="score a completed behavioral run JSON")
    mode.add_argument("--aggregate", type=Path, nargs="+", help="aggregate scored behavioral runs")
    args = parser.parse_args()

    if args.template:
        print(json.dumps(run_template(), ensure_ascii=False, indent=2))
        return 0
    if args.score:
        result = score_run(args.score)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["score"] == result["max_score"] else 1
    if args.aggregate:
        print(json.dumps(aggregate_runs(args.aggregate), ensure_ascii=False, indent=2))
        return 0

    result = static_evaluation()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"AGENTS {result['agents_files']} files / {result['agents_total_bytes']} bytes｜"
            f"ACE cases {result['ace_cases']}｜anchors {result['quality_anchors']}｜"
            f"ERROR {len(result['errors'])}｜WARN {len(result['warnings'])}"
        )
        for route, metrics in result["chains"].items():
            print(f"  {route}: {metrics['bytes']} bytes ({metrics['budget_ratio']:.1%})")
        for warning in result["warnings"]:
            print("  ⚠", warning)
        for error in result["errors"]:
            print("  ✗", error)
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
