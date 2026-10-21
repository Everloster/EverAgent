#!/usr/bin/env python3
"""Static and replay evaluation for EverAgent report context.

Static mode checks context size, duplication, links, skill metadata, and the ACE
task suite. ``--template`` emits a run-record template. ``--score`` evaluates a
completed run record against the suite's observable expectations.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

try:
    from .report_catalog import COLLECTION_BY_ID, ROOT, parse_frontmatter
    from .report_quality import (
        cross_model_sampling_status,
        evaluate_report as evaluate_report_quality,
        load_policy,
        normalize_model,
    )
except ImportError:  # Direct script execution.
    from report_catalog import COLLECTION_BY_ID, ROOT, parse_frontmatter
    from report_quality import (
        cross_model_sampling_status,
        evaluate_report as evaluate_report_quality,
        load_policy,
        normalize_model,
    )


DEFAULT_AGENTS_BUDGET = 32 * 1024
WARN_BUDGET_RATIO = 0.75
SUITE_PATH = ROOT / "evals" / "ace-report-tasks.json"
ANCHORS_PATH = ROOT / "evals" / "report-quality-anchors.json"
QUALITY_REPLAYS_PATH = ROOT / "evals" / "report-quality-replays.json"
INSTRUCTION_POLICY_PATH = ROOT / "config" / "instruction-policy.json"
REPORT_SKILL = ROOT / ".agents" / "skills" / "everagent-report" / "SKILL.md"
CLAUDE_BRIDGE = ROOT / "CLAUDE.md"
ECOMMIT = ROOT / "scripts" / "ecommit.sh"
CI_QUALITY_WORKFLOW = ROOT / ".github" / "workflows" / "quality.yml"
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
    "WebFetch",
    "WebSearch",
    "每次上网前先读",
)


def _behavior_context_sha256(root: Path = ROOT) -> str:
    paths: set[Path] = set()
    for pattern in (
        "AGENTS.md",
        "CLAUDE.md",
        "*/AGENTS.md",
        ".agents/skills/**/SKILL.md",
        "*/skills/**/SKILL.md",
        "evals/ace-report-tasks.json",
    ):
        paths.update(path for path in root.glob(pattern) if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _load_suite() -> dict:
    return json.loads(SUITE_PATH.read_text(encoding="utf-8"))


def _load_instruction_policy() -> dict:
    return json.loads(INSTRUCTION_POLICY_PATH.read_text(encoding="utf-8"))


def _agent_files() -> list[Path]:
    files = [ROOT / "AGENTS.md"]
    files.extend(sorted(path for path in ROOT.glob("*/AGENTS.md") if path.is_file()))
    return files


def _active_context_files(agent_files: list[Path]) -> list[Path]:
    files = set(agent_files)
    files.update(
        {
            REPORT_SKILL,
            ROOT / "METHODOLOGY.md",
            ROOT / "docs" / "REPORT_WORKFLOW.md",
            ROOT / "docs" / "CONTEXT_ENGINEERING.md",
            ROOT / "docs" / "PROTOCOL_COMMON.md",
            ROOT / "docs" / "REPORT_METADATA.md",
            QUALITY_GUIDE,
            CLAUDE_BRIDGE,
            INSTRUCTION_POLICY_PATH,
        }
    )
    for domain in COLLECTION_BY_ID:
        skills = ROOT / domain / "skills"
        if not skills.exists():
            continue
        files.update(skills.rglob("SKILL.md"))
        files.update(skills.rglob("references/*.md"))
    return sorted(path for path in files if path.exists())


def _repo_owned_root_text(text: str) -> str:
    return re.sub(
        r"<!-- BEGIN MANAGED EACLI TOKEN PLAN POLICY -->.*?<!-- END MANAGED EACLI TOKEN PLAN POLICY -->",
        "",
        text,
        flags=re.DOTALL,
    )


def _discoverable_skills() -> list[Path]:
    base = ROOT / ".agents" / "skills"
    return sorted(base.glob("*/SKILL.md")) if base.exists() else []


def _on_demand_playbooks() -> list[Path]:
    paths: list[Path] = []
    for domain in COLLECTION_BY_ID:
        base = ROOT / domain / "skills"
        if base.exists():
            paths.extend(base.rglob("SKILL.md"))
    return sorted(set(paths))


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


def _heading_anchor(heading: str) -> str:
    value = re.sub(r"<[^>]+>", "", heading.strip().lower())
    value = re.sub(r"[`*_~]", "", value)
    value = "".join(char for char in value if char.isalnum() or char in {" ", "-", "_"})
    return re.sub(r"\s+", "-", value)


def _markdown_anchors(path: Path) -> set[str]:
    anchors: set[str] = set()
    counts: dict[str, int] = defaultdict(int)
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*$", line)
        if not match:
            continue
        base = _heading_anchor(match.group(1))
        if not base:
            continue
        count = counts[base]
        counts[base] += 1
        anchors.add(base if count == 0 else f"{base}-{count}")
    return anchors


def _relative_link_errors(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    for target in re.findall(r"\[[^\]]*\]\((\.\.?/[^)]+)\)", text):
        normalized = target.strip().strip("<>")
        clean, separator, fragment = normalized.partition("#")
        if "{" in clean or "}" in clean or "..." in clean:
            continue
        resolved = (path.parent / clean).resolve()
        if clean and not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)} -> {target}")
            continue
        if separator and resolved.suffix.lower() == ".md":
            anchor = unquote(fragment).lower()
            if anchor and anchor not in _markdown_anchors(resolved):
                errors.append(f"{path.relative_to(ROOT)} -> {target}（锚点不存在）")
    return errors


def static_evaluation() -> dict[str, object]:
    files = _agent_files()
    context_files = _active_context_files(files)
    root_agents = ROOT / "AGENTS.md"
    chains: dict[str, dict[str, object]] = {}
    warnings: list[str] = []
    errors: list[str] = []
    ace_context_ab_guarded = False
    ace_context_ab_status = "missing"
    ace_context_ab_candidate_sha256 = ""
    cross_model_sampling_guarded = False
    cross_model_sampling_pending = 0

    try:
        instruction_policy = _load_instruction_policy()
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        instruction_policy = {}
        errors.append(f"指令架构策略无法读取：{exc}")
    budgets = instruction_policy.get("budgets", {})
    if instruction_policy and instruction_policy.get("schema_version") != 1:
        errors.append("指令架构策略 schema_version 必须为 1")
    for owner, relative in instruction_policy.get("owners", {}).items():
        if not (ROOT / str(relative)).is_file():
            errors.append(f"指令 Owner 不存在：{owner} -> {relative}")
    ace_result_relative = instruction_policy.get("owners", {}).get("ace_context_ab_result")
    if ace_result_relative:
        ace_result_path = ROOT / str(ace_result_relative)
        if ace_result_path.is_file():
            try:
                ace_result = json.loads(ace_result_path.read_text(encoding="utf-8"))
                ace_context_ab_candidate_sha256 = str(
                    ((ace_result.get("refs") or {}).get("candidate") or {}).get("context_sha256")
                    or ""
                )
                if ace_result.get("schema_version") != 1:
                    ace_context_ab_status = "invalid-schema"
                    errors.append("ACE Context A/B 结果 schema_version 必须为 1")
                elif (ace_result.get("comparison") or {}).get("accepted") is not True:
                    ace_context_ab_status = "unaccepted"
                    warnings.append("ACE Context A/B 最新结果未通过；仅在宣称 Context 架构改进前重跑")
                elif int(ace_result.get("repetitions") or 0) < 3:
                    ace_context_ab_status = "insufficient-repetitions"
                    warnings.append("ACE Context A/B 每个版本不足三次；仅在架构里程碑验收时要求补齐")
                elif ace_context_ab_candidate_sha256 != _behavior_context_sha256():
                    ace_context_ab_status = "context-changed"
                    warnings.append("ACE Context A/B 上下文指纹已变化；下次 Context 架构里程碑验收时重跑")
                else:
                    case_count = len(_load_suite().get("cases") or [])
                    expected_runs = case_count * int(ace_result["repetitions"])
                    summaries = ace_result.get("summaries") or {}
                    complete = all(
                        int((summaries.get(label) or {}).get("runs") or 0) == expected_runs
                        and int((summaries.get(label) or {}).get("successful_runs") or 0)
                        == expected_runs
                        for label in ("baseline", "candidate")
                    )
                    if not complete:
                        ace_context_ab_status = "incomplete"
                        warnings.append("ACE Context A/B 结果缺少完整成功运行；不能用于宣称架构改进")
                    else:
                        ace_context_ab_status = "current"
                        ace_context_ab_guarded = True
            except (OSError, json.JSONDecodeError) as exc:
                ace_context_ab_status = "unreadable"
                errors.append(f"ACE Context A/B 结果无法读取：{exc}")
    for source in instruction_policy.get("basis", []):
        url = str(source.get("url") or "")
        if not url.startswith("https://developers.openai.com/"):
            errors.append(f"指令策略依据不是 OpenAI 官方开发者文档：{url or '<empty>'}")

    try:
        sampling_status = cross_model_sampling_status()
        cross_model_sampling_pending = int(sampling_status["pending_same_model_reports"])
        if sampling_status["sample_due"]:
            errors.append(
                "跨模型抽样复核已到期："
                + str(sampling_status.get("recommended_report") or "<unknown>")
            )
        else:
            cross_model_sampling_guarded = True
    except (OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        errors.append(f"跨模型抽样状态无法读取：{exc}")

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

    root_text = root_agents.read_text(encoding="utf-8", errors="replace")
    root_repo_owned_bytes = len(_repo_owned_root_text(root_text).encode("utf-8"))
    root_warn = int(budgets.get("root_repo_owned_bytes_warn", 0) or 0)
    root_limit = int(budgets.get("root_repo_owned_bytes_max", 0) or 0)
    if root_warn and root_repo_owned_bytes > root_warn:
        warnings.append(
            f"根 AGENTS 仓库自有内容 {root_repo_owned_bytes} bytes，超过软预算 {root_warn}"
        )
    if root_limit and root_repo_owned_bytes > root_limit:
        errors.append(f"根 AGENTS 仓库自有内容 {root_repo_owned_bytes} bytes，超过 {root_limit}")

    domain_agent_bytes: dict[str, int] = {}
    domain_limit = int(budgets.get("domain_agents_bytes_max", 0) or 0)
    for path in files:
        if path == root_agents:
            continue
        relative = str(path.relative_to(ROOT))
        size = path.stat().st_size
        domain_agent_bytes[relative] = size
        if domain_limit and size > domain_limit:
            errors.append(f"领域 AGENTS 过大：{relative} 为 {size} bytes，超过 {domain_limit}")

    for snippet in instruction_policy.get("root_forbidden_snippets", []):
        if snippet in _repo_owned_root_text(root_text):
            errors.append(f"根 AGENTS 复制了按需 Owner 内容：{snippet}")
    for path in files:
        if path == root_agents:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for snippet in instruction_policy.get("domain_agents_forbidden_snippets", []):
            if snippet in text:
                errors.append(f"领域 AGENTS 复制了公共 Owner 内容：{path.relative_to(ROOT)} -> {snippet}")
    common_context = {
        "AGENTS.md": _repo_owned_root_text(root_text),
        **{
            str(path.relative_to(ROOT)): path.read_text(encoding="utf-8", errors="replace")
            for path in files
            if path != root_agents
        },
    }
    for token in instruction_policy.get("common_context_forbidden_model_tokens", []):
        for relative, text in common_context.items():
            if str(token).lower() in text.lower():
                errors.append(f"模型专属补丁进入公共 AGENTS：{relative} -> {token}")
    for token in instruction_policy.get("model_neutral_forbidden_model_tokens", []):
        for relative in instruction_policy.get("model_neutral_owner_files", []):
            path = ROOT / str(relative)
            if not path.is_file():
                errors.append(f"模型中立 Owner 不存在：{relative}")
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if str(token).lower() in text.lower():
                errors.append(f"模型名进入模型中立 Owner：{relative} -> {token}")

    claude_bytes = CLAUDE_BRIDGE.stat().st_size if CLAUDE_BRIDGE.exists() else 0
    claude_limit = int(budgets.get("claude_bridge_bytes_max", 0) or 0)
    if not CLAUDE_BRIDGE.exists():
        errors.append("缺少 CLAUDE.md bridge")
    else:
        claude_text = CLAUDE_BRIDGE.read_text(encoding="utf-8", errors="replace")
        if claude_text.count("@AGENTS.md") != 1:
            errors.append("CLAUDE.md 必须且只能导入一次 @AGENTS.md")
        if claude_limit and claude_bytes > claude_limit:
            errors.append(f"CLAUDE.md bridge 为 {claude_bytes} bytes，超过 {claude_limit}")
        for snippet in instruction_policy.get("claude_forbidden_snippets", []):
            if snippet in claude_text:
                errors.append(f"CLAUDE.md 重复了公共 Owner 链接：{snippet}")

    commit_wrapper_guarded = False
    if not ECOMMIT.is_file():
        errors.append("缺少 scripts/ecommit.sh")
    else:
        ecommit_text = ECOMMIT.read_text(encoding="utf-8", errors="replace")
        # Entrypoint ownership is static; the commit/index behavior is exercised by
        # scripts.test_git_commit in the staged gate and CI.
        engine_path = ECOMMIT.with_name("git_commit.py")
        engine_text = engine_path.read_text(encoding="utf-8") if engine_path.is_file() else ""
        core_path = ROOT / "packages/everagent-core/src/everagent_core/git.py"
        required_guards = (
            ("wrapper delegates", "git_commit.py" in ecommit_text),
            ("core owner exists", core_path.is_file()),
            ("core delegation", "from everagent_core import git as _core" in engine_text),
            ("public gate binding", "precommit_quality.py" in engine_text),
        )
        missing_guards = [label for label, present in required_guards if not present]
        if missing_guards:
            errors.append("ecommit 缺少 staged snapshot 防护：" + ", ".join(missing_guards))
        else:
            commit_wrapper_guarded = True

    ci_quality_guarded = False
    if not CI_QUALITY_WORKFLOW.is_file():
        errors.append("缺少 .github/workflows/quality.yml")
    else:
        workflow_text = CI_QUALITY_WORKFLOW.read_text(encoding="utf-8", errors="replace")
        required_ci_checks = (
            "tests.test_report_tooling",
            "scripts.test_git_commit",
            "audit_reports.py --all",
            "reindex.py --check",
            "eval_report_context.py",
        )
        missing_ci_checks = [item for item in required_ci_checks if item not in workflow_text]
        if missing_ci_checks:
            errors.append("CI 质量门缺少检查：" + ", ".join(missing_ci_checks))
        else:
            ci_quality_guarded = True

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

    discoverable_skills = _discoverable_skills()
    on_demand_playbooks = _on_demand_playbooks()
    discoverable_description_chars = 0
    skill_count_limit = int(budgets.get("discoverable_skill_count_max", 0) or 0)
    description_limit = int(budgets.get("discoverable_skill_description_chars_max", 0) or 0)
    entrypoint_limit = int(budgets.get("discoverable_skill_entrypoint_bytes_max", 0) or 0)
    playbook_warn = int(budgets.get("on_demand_playbook_entrypoint_bytes_warn", 0) or 0)
    if skill_count_limit and len(discoverable_skills) > skill_count_limit:
        errors.append(f"自动发现 skill 数量 {len(discoverable_skills)}，超过 {skill_count_limit}")
    for path in discoverable_skills:
        skill_text = path.read_text(encoding="utf-8", errors="replace")
        skill = parse_frontmatter(skill_text)
        description = str(skill.get("description") or "")
        discoverable_description_chars += len(description)
        if not skill.get("name") or not description:
            errors.append(f"自动发现 skill 缺少 name/description：{path.relative_to(ROOT)}")
        if description_limit and len(description) > description_limit:
            errors.append(
                f"skill description 过长：{path.relative_to(ROOT)} 为 {len(description)} characters，超过 {description_limit}"
            )
        if entrypoint_limit and path.stat().st_size > entrypoint_limit:
            errors.append(
                f"skill 入口过大：{path.relative_to(ROOT)} 为 {path.stat().st_size} bytes，超过 {entrypoint_limit}"
            )
        if not re.search(r"\b(?:use|when)\b|用于|适用", description, re.IGNORECASE):
            warnings.append(f"skill description 缺少正向触发条件：{path.relative_to(ROOT)}")
        if not re.search(r"\b(?:skip|exclude|except|not)\b|不用于|不适用|跳过", description, re.IGNORECASE):
            warnings.append(f"skill description 缺少非触发边界：{path.relative_to(ROOT)}")
    for path in on_demand_playbooks:
        if playbook_warn and path.stat().st_size > playbook_warn:
            warnings.append(
                f"按需 playbook 入口偏大：{path.relative_to(ROOT)} 为 {path.stat().st_size} bytes"
            )

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
        elif description_limit and len(description) > description_limit:
            errors.append(f"everagent-report description 超过 {description_limit} characters")
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
                "expected_skill_paths",
                "forbidden_skill_paths",
                "completion_signals",
                "expected_completed",
                "expected_stop_reason",
            )
            if field not in case
        ]
        if missing:
            errors.append(f"ACE case {case.get('id', '<unknown>')} 缺字段：{', '.join(missing)}")
        if case.get("expected_route") not in valid_routes:
            errors.append(f"ACE case {case.get('id')} route 未登记：{case.get('expected_route')}")
        expected_skills = set(case.get("expected_skill_paths") or [])
        forbidden_skills = set(case.get("forbidden_skill_paths") or [])
        overlap = expected_skills & forbidden_skills
        if overlap:
            errors.append(f"ACE case {case.get('id')} 的 skill 正负样本冲突：{', '.join(sorted(overlap))}")
        for skill_path in expected_skills | forbidden_skills | set(case.get("artifact_expected_skill_paths") or []):
            if not (ROOT / skill_path).is_file():
                errors.append(f"ACE case {case.get('id')} 引用了不存在的 skill：{skill_path}")
        for context_path in set(case.get("expected_initial_files") or []):
            if not (ROOT / context_path).is_file():
                errors.append(f"ACE case {case.get('id')} 引用了不存在的初始 context：{context_path}")
        if not case.get("completion_signals"):
            errors.append(f"ACE case {case.get('id')} 缺少 completion_signals")
        if case.get("must_pause_before_research") and case.get("must_not_pause_before_research"):
            errors.append(f"ACE case {case.get('id')} 同时要求暂停和禁止暂停")

    try:
        policy = load_policy()
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        policy = {}
        errors.append(f"报告质量策略无法读取：{exc}")
    if policy:
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

    try:
        replay_suite = json.loads(QUALITY_REPLAYS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        replay_suite = {"cases": []}
        errors.append(f"真实报告回放集无法读取：{exc}")
    if not isinstance(replay_suite, dict):
        replay_suite = {"cases": []}
        errors.append("真实报告回放集必须是 JSON object")
    replay_cases = replay_suite.get("cases", [])
    if replay_suite.get("schema_version") != 1:
        errors.append("真实报告回放集 schema_version 必须为 1")
    if not isinstance(replay_cases, list) or not replay_cases:
        errors.append("真实报告回放集必须包含至少一个 case")
        replay_cases = []
    replay_ids: set[str] = set()
    for replay in replay_cases:
        replay_id = str(replay.get("id") or "")
        if not replay_id or replay_id in replay_ids:
            errors.append(f"真实报告回放 id 缺失或重复：{replay_id or '<empty>'}")
        replay_ids.add(replay_id)
        report_path = ROOT / str(replay.get("report_path") or "")
        if not report_path.is_file():
            errors.append(f"真实报告回放目标不存在：{replay.get('report_path')}")
            continue
        try:
            result = evaluate_report_quality(report_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"真实报告回放失败：{replay_id}: {exc}")
            continue
        metadata = parse_frontmatter(report_path.read_text(encoding="utf-8", errors="replace"))
        if result["decision"] != "pass":
            errors.append(f"真实报告回放未通过：{replay_id}: {result['decision']}")
        if metadata.get("quality_tier") != replay.get("quality_tier"):
            errors.append(f"真实报告回放 tier 漂移：{replay_id}")
        if metadata.get("status") != replay.get("status"):
            errors.append(f"真实报告回放 status 漂移：{replay_id}")
        minimum_score = replay.get("minimum_score")
        if not isinstance(minimum_score, (int, float)) or isinstance(minimum_score, bool):
            errors.append(f"真实报告回放 minimum_score 无效：{replay_id}")
        elif not isinstance(result.get("score"), (int, float)) or result["score"] < minimum_score:
            errors.append(f"真实报告回放分数不足：{replay_id}")

    return {
        "schema_version": 1,
        "agents_files": len(files),
        "agents_total_bytes": sum(path.stat().st_size for path in files),
        "root_repo_owned_bytes": root_repo_owned_bytes,
        "root_repo_owned_bytes_warn": root_warn,
        "root_repo_owned_bytes_max": root_limit,
        "domain_agent_bytes": domain_agent_bytes,
        "claude_bridge_bytes": claude_bytes,
        "commit_wrapper_guarded": commit_wrapper_guarded,
        "ci_quality_guarded": ci_quality_guarded,
        "ace_context_ab_guarded": ace_context_ab_guarded,
        "ace_context_ab_status": ace_context_ab_status,
        "ace_context_ab_candidate_sha256": ace_context_ab_candidate_sha256,
        "cross_model_sampling_guarded": cross_model_sampling_guarded,
        "cross_model_sampling_pending": cross_model_sampling_pending,
        "active_context_files": len(context_files),
        "governed_context_files": len(context_files),
        "chains": chains,
        "duplicate_blocks": duplicates,
        "unconditional_reads": unconditional_reads,
        "report_skill_description_chars": len(description),
        "discoverable_skill_count": len(discoverable_skills),
        "discoverable_skill_description_chars": discoverable_description_chars,
        "on_demand_playbook_count": len(on_demand_playbooks),
        "on_demand_playbook_entrypoint_bytes": sum(path.stat().st_size for path in on_demand_playbooks),
        "largest_on_demand_playbook_bytes": max((path.stat().st_size for path in on_demand_playbooks), default=0),
        "ace_cases": len(cases),
        "quality_anchors": len(anchor_ids),
        "quality_replays": len(replay_cases),
        "warnings": warnings,
        "errors": errors,
    }


def run_template() -> dict[str, object]:
    suite = _load_suite()
    return {
        "schema_version": 2,
        "model": "",
        "harness": "",
        "context_revision": "",
        "cases": [
            {
                "id": case["id"],
                "route": None,
                "artifact_created": None,
                "initial_project_files": [],
                "repo_skills_loaded": [],
                "paused_before_research": None,
                "clarification_count": 0,
                "checks_completed": [],
                "completion_signals_met": [],
                "stop_reason": None,
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
    if observed_doc.get("schema_version") != 2:
        raise ValueError("behavioral run schema_version must be 2; regenerate with --template")
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
        score += 20 if checks["route"] else 0

        artifact_policy = exp["artifact_policy"]
        created = obs.get("artifact_created")
        checks["artifact"] = (
            created is True
            if artifact_policy in {"required", "update_existing"}
            else created is False
            if artifact_policy == "forbidden"
            else created in {True, False}
        )
        score += 10 if checks["artifact"] else 0
        if not checks["artifact"]:
            hard_failure = True

        initial_files = obs.get("initial_project_files") or []
        required_initial_files = set(exp.get("expected_initial_files") or [])
        forbidden_files = set(exp.get("forbidden_initial_files") or [])
        unnecessary_context_reads = sorted(forbidden_files & set(map(str, initial_files)))
        checks["context_budget"] = (
            len(initial_files) <= exp["max_initial_project_files"]
            and required_initial_files.issubset(set(map(str, initial_files)))
            and not unnecessary_context_reads
        )
        score += 10 if checks["context_budget"] else 0

        if exp.get("must_pause_before_research"):
            checks["initiative"] = (
                obs.get("paused_before_research") is True
                and int(obs.get("clarification_count") or 0) == 1
            )
        elif exp.get("must_not_pause_before_research"):
            checks["initiative"] = (
                obs.get("paused_before_research") is False
                and int(obs.get("clarification_count") or 0) == 0
            )
        else:
            checks["initiative"] = True
        score += 10 if checks["initiative"] else 0

        expected_skills = set(exp.get("expected_skill_paths") or [])
        if created is True:
            expected_skills.update(exp.get("artifact_expected_skill_paths") or [])
        forbidden_skills = set(exp.get("forbidden_skill_paths") or [])
        loaded_skills = set(map(str, obs.get("repo_skills_loaded") or []))
        matched_skills = expected_skills & loaded_skills
        skill_recall = len(matched_skills) / len(expected_skills) if expected_skills else 1.0
        skill_precision = len(matched_skills) / len(loaded_skills) if loaded_skills else (1.0 if not expected_skills else 0.0)
        forbidden_skill_hits = sorted(forbidden_skills & loaded_skills)
        checks["skills"] = skill_recall == 1.0 and skill_precision == 1.0 and not forbidden_skill_hits
        score += 15 if checks["skills"] else 0

        completed_checks = set(obs.get("checks_completed") or [])
        required_checks = set(exp.get("required_checks") or [])
        if created is True:
            required_checks.update(exp.get("artifact_required_checks") or [])
        checks["checks"] = required_checks.issubset(completed_checks)
        score += 20 if checks["checks"] else 0

        required_completion = set(exp.get("completion_signals") or [])
        observed_completion = set(obs.get("completion_signals_met") or [])
        expected_completed = exp.get("expected_completed") is True
        checks["completion"] = (
            obs.get("completed") is expected_completed
            and required_completion.issubset(observed_completion)
            and obs.get("stop_reason") == exp.get("expected_stop_reason")
        )
        score += 15 if checks["completion"] else 0

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
                "skill_precision": round(skill_precision, 4),
                "skill_recall": round(skill_recall, 4),
                "forbidden_skill_hits": forbidden_skill_hits,
                "unnecessary_context_reads": unnecessary_context_reads,
                "initial_context_files": len(initial_files),
                "clarification_count": int(obs.get("clarification_count") or 0),
                "premature_stop": not checks["completion"],
                "input_tokens": obs.get("input_tokens"),
                "elapsed_seconds": obs.get("elapsed_seconds"),
                "tool_failures": obs.get("tool_failures", 0),
                "checks": checks,
            }
        )

    total = sum(row["score"] for row in rows)
    maximum = sum(row["max_score"] for row in rows)
    return {
        "schema_version": 2,
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
        all_cases = [case for run in runs for case in run["cases"]]
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
                "mean_skill_precision": round(sum(float(case.get("skill_precision") or 0) for case in all_cases) / len(all_cases), 4) if all_cases else 0,
                "mean_skill_recall": round(sum(float(case.get("skill_recall") or 0) for case in all_cases) / len(all_cases), 4) if all_cases else 0,
                "context_overread_rate": round(sum(bool(case.get("unnecessary_context_reads")) for case in all_cases) / len(all_cases), 4) if all_cases else 0,
                "mean_initial_context_files": round(sum(int(case.get("initial_context_files") or 0) for case in all_cases) / len(all_cases), 2) if all_cases else 0,
                "clarification_rate": round(sum(int(case.get("clarification_count") or 0) > 0 for case in all_cases) / len(all_cases), 4) if all_cases else 0,
                "premature_stop_rate": round(sum(case.get("premature_stop") is True for case in all_cases) / len(all_cases), 4) if all_cases else 0,
                "escalation_rate": round(sum(case.get("escalated") is True for case in all_cases) / len(case_scores), 4) if case_scores else 0,
                "scarce_model_calls": sum(int(case.get("scarce_model_calls") or 0) for case in all_cases),
                "input_tokens": sum(int(case.get("input_tokens") or 0) for case in all_cases),
                "elapsed_seconds": round(sum(float(case.get("elapsed_seconds") or 0) for case in all_cases), 2),
                "tool_failures": sum(int(case.get("tool_failures") or 0) for case in all_cases),
            }
        )
    return {"schema_version": 2, "groups": summaries}


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
        try:
            result = score_run(args.score)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"[context-eval] {exc}")
            return 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["score"] == result["max_score"] else 1
    if args.aggregate:
        try:
            result = aggregate_runs(args.aggregate)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            print(f"[context-eval] {exc}")
            return 1
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    result = static_evaluation()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"AGENTS {result['agents_files']} files / {result['agents_total_bytes']} bytes｜"
            f"root-owned {result['root_repo_owned_bytes']} bytes｜"
            f"skills {result['discoverable_skill_count']} / {result['discoverable_skill_description_chars']} chars｜"
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
