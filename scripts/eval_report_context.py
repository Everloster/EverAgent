#!/usr/bin/env python3
"""Static and replay evaluation for EverAgent report context.

Static mode checks context size, duplication, links, skill metadata, and the ACE
task suite. ``--template`` emits a run-record template. ``--score`` evaluates a
completed run record against the suite's observable expectations.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

try:
    from .report_catalog import COLLECTION_BY_ID, ROOT, parse_frontmatter
except ImportError:  # Direct script execution.
    from report_catalog import COLLECTION_BY_ID, ROOT, parse_frontmatter


DEFAULT_AGENTS_BUDGET = 32 * 1024
WARN_BUDGET_RATIO = 0.75
SUITE_PATH = ROOT / "evals" / "ace-report-tasks.json"
REPORT_SKILL = ROOT / ".agents" / "skills" / "everagent-report" / "SKILL.md"
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
    files.update({REPORT_SKILL, ROOT / "docs" / "REPORT_WORKFLOW.md", ROOT / "docs" / "CONTEXT_ENGINEERING.md"})
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
                "required_checks",
            )
            if field not in case
        ]
        if missing:
            errors.append(f"ACE case {case.get('id', '<unknown>')} 缺字段：{', '.join(missing)}")
        if case.get("expected_route") not in valid_routes:
            errors.append(f"ACE case {case.get('id')} route 未登记：{case.get('expected_route')}")

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
    rows: list[dict[str, object]] = []

    for case_id, exp in expected.items():
        obs = observed.get(case_id)
        if obs is None:
            rows.append({"id": case_id, "score": 0, "max_score": 100, "missing": True})
            continue
        score = 0
        checks: dict[str, bool] = {}
        checks["route"] = obs.get("route") == exp["expected_route"]
        score += 25 if checks["route"] else 0

        policy = exp["artifact_policy"]
        created = obs.get("artifact_created")
        checks["artifact"] = (
            created is True
            if policy in {"required", "update_existing"}
            else created is False
            if policy == "forbidden"
            else created in {True, False}
        )
        score += 15 if checks["artifact"] else 0

        initial_files = obs.get("initial_project_files") or []
        checks["context_budget"] = len(initial_files) <= exp["max_initial_project_files"]
        score += 15 if checks["context_budget"] else 0

        checks["initiative"] = not (
            exp.get("must_not_pause_before_research") and obs.get("paused_before_research") is True
        )
        score += 10 if checks["initiative"] else 0

        completed_checks = set(obs.get("checks_completed") or [])
        required_checks = set(exp.get("required_checks") or [])
        checks["checks"] = required_checks.issubset(completed_checks)
        score += 25 if checks["checks"] else 0

        checks["completion"] = obs.get("completed") is True
        score += 10 if checks["completion"] else 0

        if obs.get("safety_violation") is not False:
            score = 0
            checks["safety"] = False
        else:
            checks["safety"] = True

        rows.append({"id": case_id, "score": score, "max_score": 100, "checks": checks})

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


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate EverAgent report context")
    parser.add_argument("--json", action="store_true", help="emit static evaluation as JSON")
    parser.add_argument("--template", action="store_true", help="emit behavioral run template")
    parser.add_argument("--score", type=Path, help="score a completed behavioral run JSON")
    args = parser.parse_args()

    if args.template:
        print(json.dumps(run_template(), ensure_ascii=False, indent=2))
        return 0
    if args.score:
        result = score_run(args.score)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["score"] == result["max_score"] else 1

    result = static_evaluation()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"AGENTS {result['agents_files']} files / {result['agents_total_bytes']} bytes｜"
            f"ACE cases {result['ace_cases']}｜ERROR {len(result['errors'])}｜WARN {len(result['warnings'])}"
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
