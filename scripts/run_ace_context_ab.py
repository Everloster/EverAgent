#!/usr/bin/env python3
"""Run a controlled ACE startup-routing A/B probe with Pi.

The probe measures the part of agent behavior affected directly by repository
context: route choice, artifact intent, initial file reads, repository skill
selection, and whether the agent pauses for clarification. It intentionally
stops before research or writes. Full artifact quality remains covered by the
real report replays in ``evals/report-quality-replays.json``.

Raw Pi JSONL traces stay in a temporary directory. Only normalized,
repository-relative observations and aggregate metrics are written to disk.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUITE = ROOT / "evals" / "ace-report-tasks.json"
DEFAULT_MODEL = "zai-coding-cn/glm-5.3"
ROUTES = {
    "root",
    "ai-learning",
    "cs-learning",
    "philosophy-learning",
    "psychology-learning",
    "biology-learning",
    "ai-practice",
    "podcast-learning",
    "github-trending-analyzer",
    "web-surfing",
}


def context_fingerprint(snapshot: Path) -> str:
    paths: set[Path] = set()
    for pattern in (
        "AGENTS.md",
        "CLAUDE.md",
        "*/AGENTS.md",
        ".agents/skills/**/SKILL.md",
        "*/skills/**/SKILL.md",
        "evals/ace-report-tasks.json",
    ):
        paths.update(path for path in snapshot.glob(pattern) if path.is_file())
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.relative_to(snapshot).as_posix()):
        relative = path.relative_to(snapshot).as_posix().encode("utf-8")
        digest.update(relative)
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _nearest_rank(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return ordered[index]


def _safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "ref"


def _extract_snapshot(ref: str, target: Path) -> str:
    if ref == "WORKTREE":
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
        diff = subprocess.check_output(
            ["git", "diff", "--binary", "HEAD"], cwd=ROOT
        )
        status = subprocess.check_output(
            ["git", "status", "--porcelain=v1", "-z"], cwd=ROOT
        )
        digest = hashlib.sha256(diff + status).hexdigest()[:12]
        shutil.copytree(
            ROOT,
            target,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"),
        )
        return f"{head}+worktree.{digest}"
    resolved = subprocess.check_output(
        ["git", "rev-parse", ref], cwd=ROOT, text=True
    ).strip()
    archive = subprocess.check_output(
        ["git", "archive", "--format=tar", resolved], cwd=ROOT
    )
    target.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
        bundle.extractall(target, filter="data")
    return resolved


def _probe_prompt(case: dict[str, Any]) -> str:
    routes = ", ".join(sorted(ROUTES))
    return f"""你正在执行 EverAgent ACE 开工路由探针。

用户原始任务：
{case['prompt']}

按当前 checkout 自身的 AGENTS.md、领域协议和 repo skill 做出真实开工决策。只执行研究、测试或写入之前的最小加载阶段：读取你实际需要的项目文件与 SKILL.md，然后停止。

探针约束：
- 不联网，不研究任务正文，不修改文件，不创建产物，不运行测试，不提交或推送。
- 自动注入的根 AGENTS.md/CLAUDE.md 不要重复读取。
- 任何你判断需要按需加载的项目文件或 repo skill，都必须实际调用 read；不要只在答案里声称已加载。
- 如果真实任务应该先澄清，只记录一次最关键问题及暂停决定，不要继续研究。
- initial_project_files 只列本次显式 read 的仓库相对路径；repo_skills_loaded 只列其中的 SKILL.md。
- route 必须是：{routes}。
- artifact_policy 必须是 required、update_existing、forbidden 或 conditional；表示执行原始用户任务时的预期产物动作，忽略探针本身禁止写入的限制。若原始任务必须先等用户补充信息，本轮填 forbidden。

最终只输出一个 JSON object，不要 Markdown，不要解释：
{{
  "route": "...",
  "artifact_policy": "...",
  "paused_before_research": false,
  "clarification_count": 0,
  "clarification_question": "",
  "initial_project_files": [],
  "repo_skills_loaded": []
}}
"""


def _assistant_text(message: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in message.get("content") or []:
        if isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text") or ""))
    return "\n".join(parts).strip()


def _parse_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    candidates = [stripped]
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", stripped, re.S)
    if fenced:
        candidates.append(fenced.group(1))
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        candidates.append(stripped[first : last + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("final assistant message does not contain a JSON object")


def _repo_path(raw: object, snapshot: Path) -> str | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    candidate = Path(raw.strip())
    if candidate.is_absolute():
        try:
            candidate = candidate.resolve().relative_to(snapshot.resolve())
        except ValueError:
            return None
    normalized = Path(os.path.normpath(str(candidate)))
    if normalized.is_absolute() or ".." in normalized.parts:
        return None
    path = normalized.as_posix()
    if path in {".", "AGENTS.md", "CLAUDE.md"}:
        return None
    if not (snapshot / normalized).is_file():
        return None
    return path


def parse_pi_trace(trace: str, snapshot: Path) -> dict[str, Any]:
    reads: list[str] = []
    final_text = ""
    input_tokens = 0
    output_tokens = 0
    tool_failures = 0
    model = ""
    provider = ""

    for raw_line in trace.splitlines():
        if not raw_line.strip():
            continue
        event = json.loads(raw_line)
        if event.get("type") == "tool_execution_start" and event.get("toolName") == "read":
            path = _repo_path((event.get("args") or {}).get("path"), snapshot)
            if path and path not in reads:
                reads.append(path)
        elif event.get("type") == "tool_execution_end" and event.get("isError"):
            tool_failures += 1
        elif event.get("type") == "message_end":
            message = event.get("message") or {}
            if message.get("role") != "assistant":
                continue
            text = _assistant_text(message)
            if text:
                final_text = text
            usage = message.get("usage") or {}
            input_tokens += int(usage.get("input") or 0) + int(usage.get("cacheRead") or 0)
            output_tokens += int(usage.get("output") or 0)
            model = str(message.get("model") or model)
            provider = str(message.get("provider") or provider)

    answer = _parse_json_object(final_text)
    claimed_files = [
        path
        for raw in answer.get("initial_project_files") or []
        if (path := _repo_path(raw, snapshot)) is not None
    ]
    claimed_skills = [
        path
        for raw in answer.get("repo_skills_loaded") or []
        if (path := _repo_path(raw, snapshot)) is not None and path.endswith("/SKILL.md")
    ]
    skills = [path for path in reads if path.endswith("/SKILL.md")]
    return {
        "route": answer.get("route"),
        "artifact_policy": answer.get("artifact_policy"),
        "paused_before_research": answer.get("paused_before_research"),
        "clarification_count": answer.get("clarification_count"),
        "clarification_question": str(answer.get("clarification_question") or ""),
        "initial_project_files": reads,
        "repo_skills_loaded": skills,
        "claimed_initial_project_files": claimed_files,
        "claimed_repo_skills_loaded": claimed_skills,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "tool_failures": tool_failures,
        "model": model,
        "provider": provider,
    }


def score_probe(case: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    allowed_routes = set(case.get("startup_allowed_routes") or [case["expected_route"]])
    route_ok = observation.get("route") in allowed_routes
    expected_artifact = case["artifact_policy"]
    observed_artifact = observation.get("artifact_policy")
    if expected_artifact in {"required", "update_existing"}:
        artifact_ok = observed_artifact in {"required", "update_existing"}
    else:
        artifact_ok = observed_artifact == expected_artifact

    files = set(map(str, observation.get("initial_project_files") or []))
    required_files = set(case.get("expected_initial_files") or [])
    forbidden_files = set(case.get("forbidden_initial_files") or [])
    forbidden_file_hits = sorted(files & forbidden_files)
    context_ok = (
        len(files) <= int(case["max_initial_project_files"])
        and required_files.issubset(files)
        and not forbidden_file_hits
    )

    if case.get("must_pause_before_research"):
        initiative_ok = (
            observation.get("paused_before_research") is True
            and int(observation.get("clarification_count") or 0) == 1
        )
    elif case.get("must_not_pause_before_research"):
        initiative_ok = (
            observation.get("paused_before_research") is False
            and int(observation.get("clarification_count") or 0) == 0
        )
    else:
        initiative_ok = True

    expected_skills = set(
        case.get("startup_expected_skill_paths")
        if "startup_expected_skill_paths" in case
        else case.get("expected_skill_paths") or []
    )
    optional_skills = set(case.get("startup_optional_skill_paths") or [])
    if observation.get("artifact_policy") == "required":
        expected_skills.update(case.get("artifact_expected_skill_paths") or [])
    forbidden_skills = set(case.get("forbidden_skill_paths") or [])
    loaded_skills = set(map(str, observation.get("repo_skills_loaded") or []))
    matched_skills = expected_skills & loaded_skills
    accepted_loaded_skills = expected_skills | optional_skills
    forbidden_skill_hits = sorted(forbidden_skills & loaded_skills)
    skill_recall = len(matched_skills) / len(expected_skills) if expected_skills else 1.0
    skill_precision = (
        len(loaded_skills & accepted_loaded_skills) / len(loaded_skills)
        if loaded_skills
        else (1.0 if not expected_skills else 0.0)
    )
    skills_ok = skill_recall == 1.0 and skill_precision == 1.0 and not forbidden_skill_hits

    score = (
        (20 if route_ok else 0)
        + (10 if artifact_ok else 0)
        + (20 if context_ok else 0)
        + (20 if initiative_ok else 0)
        + (30 if skills_ok else 0)
    )
    return {
        "score": score,
        "checks": {
            "route": route_ok,
            "artifact_policy": artifact_ok,
            "context_budget": context_ok,
            "initiative": initiative_ok,
            "skills": skills_ok,
        },
        "skill_precision": round(skill_precision, 4),
        "skill_recall": round(skill_recall, 4),
        "forbidden_skill_hits": forbidden_skill_hits,
        "forbidden_file_hits": forbidden_file_hits,
    }


def _run_one_attempt(
    *,
    ref_label: str,
    resolved_ref: str,
    snapshot: Path,
    case: dict[str, Any],
    repetition: int,
    model: str,
    thinking: str,
    timeout: int,
    raw_dir: Path,
) -> dict[str, Any]:
    command = [
        "pi",
        "-p",
        "--mode",
        "json",
        "--model",
        model,
        "--thinking",
        thinking,
        "--no-session",
        "--no-mcp",
        "--no-extensions",
        "--tools",
        "read",
        "--approve",
        _probe_prompt(case),
    ]
    started = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            cwd=snapshot,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = round(time.monotonic() - started, 3)
        partial = (
            exc.stdout.decode("utf-8", errors="replace")
            if isinstance(exc.stdout, bytes)
            else str(exc.stdout or "")
        )
        raw_path = raw_dir / f"{_safe_slug(ref_label)}-{case['id']}-r{repetition}.jsonl"
        raw_path.write_text(partial, encoding="utf-8")
        return {
            "context_label": ref_label,
            "context_revision": resolved_ref,
            "case_id": case["id"],
            "repetition": repetition,
            "elapsed_seconds": elapsed,
            "process_exit_code": None,
            "error": f"pi timed out after {timeout}s",
            "score": 0,
            "tool_failures": 1,
        }
    elapsed = round(time.monotonic() - started, 3)
    raw_path = raw_dir / f"{_safe_slug(ref_label)}-{case['id']}-r{repetition}.jsonl"
    raw_path.write_text(proc.stdout, encoding="utf-8")
    result: dict[str, Any] = {
        "context_label": ref_label,
        "context_revision": resolved_ref,
        "case_id": case["id"],
        "repetition": repetition,
        "elapsed_seconds": elapsed,
        "process_exit_code": proc.returncode,
    }
    if proc.returncode != 0:
        result.update(
            {
                "error": (proc.stderr or "pi exited non-zero")[-1000:],
                "score": 0,
                "tool_failures": 1,
            }
        )
        return result
    try:
        observation = parse_pi_trace(proc.stdout, snapshot)
        scored = score_probe(case, observation)
    except (ValueError, json.JSONDecodeError) as exc:
        result.update({"error": str(exc), "score": 0, "tool_failures": 1})
        return result
    result.update(observation)
    result.update(scored)
    return result


def _run_one(
    *,
    ref_label: str,
    resolved_ref: str,
    snapshot: Path,
    case: dict[str, Any],
    repetition: int,
    model: str,
    thinking: str,
    timeout: int,
    raw_dir: Path,
    attempts: int,
) -> dict[str, Any]:
    elapsed_total = 0.0
    last_result: dict[str, Any] = {}
    for attempt in range(1, attempts + 1):
        result = _run_one_attempt(
            ref_label=ref_label,
            resolved_ref=resolved_ref,
            snapshot=snapshot,
            case=case,
            repetition=repetition,
            model=model,
            thinking=thinking,
            timeout=timeout,
            raw_dir=raw_dir,
        )
        elapsed_total += float(result.get("elapsed_seconds") or 0)
        result["attempts_used"] = attempt
        result["elapsed_seconds"] = round(elapsed_total, 3)
        last_result = result
        if not result.get("error"):
            return result
    return last_result


def summarize(label: str, revision: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if not row.get("error")]
    scores = [float(row.get("score") or 0) for row in rows]
    count = len(rows) or 1
    by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_case[str(row["case_id"])].append(row)

    return {
        "label": label,
        "revision": revision,
        "runs": len(rows),
        "successful_runs": len(valid),
        "mean_score": round(sum(scores) / count, 2),
        "minimum_score": round(min(scores), 2) if scores else 0,
        "p10_score": round(_nearest_rank(scores, 0.10), 2),
        "subperfect_runs": sum(score < 100 for score in scores),
        "zero_rate": round(sum(score == 0 for score in scores) / count, 4),
        "route_accuracy": round(
            sum(bool((row.get("checks") or {}).get("route")) for row in rows) / count, 4
        ),
        "artifact_policy_accuracy": round(
            sum(bool((row.get("checks") or {}).get("artifact_policy")) for row in rows) / count,
            4,
        ),
        "initiative_accuracy": round(
            sum(bool((row.get("checks") or {}).get("initiative")) for row in rows) / count,
            4,
        ),
        "context_budget_accuracy": round(
            sum(bool((row.get("checks") or {}).get("context_budget")) for row in rows) / count,
            4,
        ),
        "mean_skill_precision": round(
            sum(float(row.get("skill_precision") or 0) for row in rows) / count, 4
        ),
        "mean_skill_recall": round(
            sum(float(row.get("skill_recall") or 0) for row in rows) / count, 4
        ),
        "mean_initial_project_files": round(
            sum(len(row.get("initial_project_files") or []) for row in rows) / count, 2
        ),
        "mean_input_tokens": round(
            sum(int(row.get("input_tokens") or 0) for row in rows) / count, 2
        ),
        "mean_elapsed_seconds": round(
            sum(float(row.get("elapsed_seconds") or 0) for row in rows) / count, 2
        ),
        "tool_failures": sum(int(row.get("tool_failures") or 0) for row in rows),
        "forbidden_skill_hits": sum(len(row.get("forbidden_skill_hits") or []) for row in rows),
        "forbidden_file_hits": sum(len(row.get("forbidden_file_hits") or []) for row in rows),
        "cases": [
            {
                "id": case_id,
                "mean_score": round(
                    sum(float(item.get("score") or 0) for item in items) / len(items), 2
                ),
                "route_accuracy": round(
                    sum(bool((item.get("checks") or {}).get("route")) for item in items)
                    / len(items),
                    4,
                ),
                "mean_skill_recall": round(
                    sum(float(item.get("skill_recall") or 0) for item in items) / len(items),
                    4,
                ),
                "mean_initial_project_files": round(
                    sum(len(item.get("initial_project_files") or []) for item in items)
                    / len(items),
                    2,
                ),
            }
            for case_id, items in sorted(by_case.items())
        ],
    }


def compare(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    metrics = [
        "mean_score",
        "minimum_score",
        "p10_score",
        "subperfect_runs",
        "zero_rate",
        "route_accuracy",
        "artifact_policy_accuracy",
        "initiative_accuracy",
        "context_budget_accuracy",
        "mean_skill_precision",
        "mean_skill_recall",
        "mean_initial_project_files",
        "mean_input_tokens",
        "mean_elapsed_seconds",
        "tool_failures",
        "forbidden_skill_hits",
        "forbidden_file_hits",
    ]
    deltas = {
        metric: round(float(candidate[metric]) - float(baseline[metric]), 4)
        for metric in metrics
    }
    critical_non_regression = (
        candidate["successful_runs"] >= baseline["successful_runs"]
        and candidate["route_accuracy"] >= baseline["route_accuracy"]
        and candidate["artifact_policy_accuracy"] >= baseline["artifact_policy_accuracy"]
        and candidate["initiative_accuracy"] >= baseline["initiative_accuracy"]
        and candidate["minimum_score"] >= baseline["minimum_score"]
        and candidate["p10_score"] >= baseline["p10_score"]
        and candidate["forbidden_skill_hits"] <= baseline["forbidden_skill_hits"]
        and candidate["forbidden_file_hits"] <= baseline["forbidden_file_hits"]
    )
    efficiency_gain = (
        candidate["mean_input_tokens"] < baseline["mean_input_tokens"]
        or candidate["mean_initial_project_files"] < baseline["mean_initial_project_files"]
        or candidate["mean_elapsed_seconds"] < baseline["mean_elapsed_seconds"]
    )
    return {
        "deltas": deltas,
        "critical_non_regression": critical_non_regression,
        "efficiency_gain": efficiency_gain,
        "accepted": critical_non_regression and efficiency_gain,
    }


def render_markdown(document: dict[str, Any]) -> str:
    baseline = document["summaries"]["baseline"]
    candidate = document["summaries"]["candidate"]
    comparison = document["comparison"]
    metric_rows = [
        ("平均探针分", "mean_score", "higher"),
        ("最低探针分", "minimum_score", "higher"),
        ("P10 探针分", "p10_score", "higher"),
        ("未满分运行数", "subperfect_runs", "lower"),
        ("路由准确率", "route_accuracy", "higher"),
        ("产物策略准确率", "artifact_policy_accuracy", "higher"),
        ("澄清/自主推进准确率", "initiative_accuracy", "higher"),
        ("Context 预算命中率", "context_budget_accuracy", "higher"),
        ("Skill precision", "mean_skill_precision", "higher"),
        ("Skill recall", "mean_skill_recall", "higher"),
        ("平均初始文件数", "mean_initial_project_files", "lower"),
        ("平均输入 tokens", "mean_input_tokens", "lower"),
        ("平均耗时（秒）", "mean_elapsed_seconds", "lower"),
    ]
    lines = [
        "# EverAgent Context 重构 ACE A/B 回放",
        "",
        f"> 日期：{document['generated_on']}｜模型：`{document['model']}`｜Harness：Pi｜推理档位：`{document['thinking']}`",
        "",
        "## 结论",
        "",
        (
            "候选 Context **通过**本轮开工路由回放。"
            if comparison["accepted"]
            else "候选 Context **未通过**本轮开工路由回放的接受条件。"
        ),
        "",
        "本回放覆盖全部 ACE case 的路由、产物意图、最小 Context、Skill 选择和澄清边界；每个版本重复运行"
        f" {document['repetitions']} 次。它不替代完整报告生成，完整产物继续由真实报告回放验证。",
        "",
        "## 汇总",
        "",
        "| 指标 | 重构前 | 重构后 | 变化 |",
        "|---|---:|---:|---:|",
    ]
    for title, key, _direction in metric_rows:
        delta = comparison["deltas"][key]
        lines.append(f"| {title} | {baseline[key]} | {candidate[key]} | {delta:+g} |")

    lines.extend(
        [
            "",
            "## 分任务结果",
            "",
            "| Case | 重构前均分 | 重构后均分 | 重构后 Skill recall | 重构后初始文件数 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    baseline_cases = {item["id"]: item for item in baseline["cases"]}
    for item in candidate["cases"]:
        old = baseline_cases[item["id"]]
        lines.append(
            f"| `{item['id']}` | {old['mean_score']} | {item['mean_score']} | "
            f"{item['mean_skill_recall']} | {item['mean_initial_project_files']} |"
        )

    lines.extend(
        [
            "",
            "## 接受条件",
            "",
            f"- 关键行为不退化：`{str(comparison['critical_non_regression']).lower()}`",
            f"- 至少一个效率指标改善：`{str(comparison['efficiency_gain']).lower()}`",
            f"- 最终判定：`{'pass' if comparison['accepted'] else 'fail'}`",
            "",
            "## 边界",
            "",
            "- 探针只运行开工阶段，原始任务没有联网、写文件、测试或发布。",
            "- 同一 case 与 repetition 的 baseline/candidate 交错提交，并轮换先后顺序，降低时段与队列偏差。",
            "- Pi 的用户级系统提示与全局 Skills 在两组中保持一致；结果只比较 checkout Context 的差异。",
            "- 已恢复的 read 失败保留为观测指标；进程失败、行为分、禁止 Skill/文件与安全边界继续阻断接受。",
            "- 原始 JSONL 含机器级上下文，只保存在临时目录，没有进入公开仓；归档结果仅含仓库相对路径和聚合指标。",
            "- 任务完成质量、证据可靠性和提前停止仍由 report-v2 真实回放及完整行为回放补充。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ACE context startup-routing A/B probes")
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--suite", type=Path, default=DEFAULT_SUITE)
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--jobs", type=int, default=3)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--thinking", default="medium")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args()

    if args.repetitions < 1 or args.jobs < 1 or args.attempts < 1:
        parser.error("--repetitions, --jobs and --attempts must be positive")
    if shutil.which("pi") is None:
        parser.error("pi is not installed")
    suite = json.loads(args.suite.read_text(encoding="utf-8"))
    cases = suite.get("cases") or []
    if not cases:
        parser.error("ACE suite has no cases")
    if args.case_ids:
        requested = set(args.case_ids)
        known = {str(case.get("id")) for case in cases}
        unknown = sorted(requested - known)
        if unknown:
            parser.error("unknown --case values: " + ", ".join(unknown))
        cases = [case for case in cases if case.get("id") in requested]

    with tempfile.TemporaryDirectory(prefix="everagent-ace-ab-") as directory:
        temp = Path(directory)
        snapshots = {
            "baseline": temp / "baseline",
            "candidate": temp / "candidate",
        }
        revisions = {
            "baseline": _extract_snapshot(args.baseline, snapshots["baseline"]),
            "candidate": _extract_snapshot(args.candidate, snapshots["candidate"]),
        }
        fingerprints = {
            label: context_fingerprint(snapshot)
            for label, snapshot in snapshots.items()
        }
        raw_dir = temp / "raw"
        raw_dir.mkdir()
        jobs: list[dict[str, Any]] = []
        for repetition in range(1, args.repetitions + 1):
            for case_index, case in enumerate(cases):
                labels = (
                    ("baseline", "candidate")
                    if (repetition + case_index) % 2
                    else ("candidate", "baseline")
                )
                for label in labels:
                    jobs.append(
                        {
                            "ref_label": label,
                            "resolved_ref": revisions[label],
                            "snapshot": snapshots[label],
                            "case": case,
                            "repetition": repetition,
                            "model": args.model,
                            "thinking": args.thinking,
                            "timeout": args.timeout,
                            "raw_dir": raw_dir,
                            "attempts": args.attempts,
                        }
                    )

        rows: list[dict[str, Any]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as executor:
            futures = [executor.submit(_run_one, **job) for job in jobs]
            for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
                row = future.result()
                rows.append(row)
                print(
                    f"[{index}/{len(futures)}] {row['context_label']} "
                    f"{row['case_id']} r{row['repetition']} score={row.get('score', 0)}",
                    file=sys.stderr,
                    flush=True,
                )

    baseline_rows = [row for row in rows if row["context_label"] == "baseline"]
    candidate_rows = [row for row in rows if row["context_label"] == "candidate"]
    baseline_summary = summarize("baseline", revisions["baseline"], baseline_rows)
    candidate_summary = summarize("candidate", revisions["candidate"], candidate_rows)
    document = {
        "schema_version": 1,
        "generated_on": date.today().isoformat(),
        "suite": str(args.suite.relative_to(ROOT)),
        "model": args.model,
        "harness": "pi",
        "thinking": args.thinking,
        "probe_scope": "startup-routing",
        "execution_order": "paired-interleaved",
        "repetitions": args.repetitions,
        "refs": {
            "baseline": {
                "requested": args.baseline,
                "resolved": revisions["baseline"],
                "context_sha256": fingerprints["baseline"],
            },
            "candidate": {
                "requested": args.candidate,
                "resolved": revisions["candidate"],
                "context_sha256": fingerprints["candidate"],
            },
        },
        "summaries": {
            "baseline": baseline_summary,
            "candidate": candidate_summary,
        },
        "comparison": compare(baseline_summary, candidate_summary),
        "runs": sorted(
            rows,
            key=lambda item: (
                item["context_label"],
                item["case_id"],
                int(item["repetition"]),
            ),
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(render_markdown(document), encoding="utf-8")
    print(json.dumps(document["comparison"], ensure_ascii=False))
    return 0 if document["comparison"]["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
