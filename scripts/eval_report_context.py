#!/usr/bin/env python3
"""Prepare and score existing ACE behavioral experiment records.

Static context checks live in the Go ea-quality context command. These authoring
helpers do not execute agents or certify a new behavioral replay.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

try:
    from .report_catalog import ROOT
    from .report_quality import load_policy, normalize_model
except ImportError:  # Direct script execution.
    from report_catalog import ROOT
    from report_quality import load_policy, normalize_model


SUITE_PATH = ROOT / "evals" / "ace-report-tasks.json"


def _load_suite() -> dict:
    return json.loads(SUITE_PATH.read_text(encoding="utf-8"))


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
    parser = argparse.ArgumentParser(description="Prepare and score ACE behavioral experiment records")
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

    parser.error("static checks moved to: go -C packages/everagent-core run ./cmd/ea-quality context")


if __name__ == "__main__":
    raise SystemExit(main())
