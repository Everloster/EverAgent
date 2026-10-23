#!/usr/bin/env python3
"""Select bounded context candidates from trusted evaluator records.

This module never executes an agent, grades its answer, or edits a policy.
The caller owns raw evidence verification and the frozen comparison contract.
Unknown measurements remain unknown; an ineligible candidate never wins.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

SHA256 = re.compile(r"[0-9a-f]{64}\Z")
REQUIRED_EVIDENCE = (
    "artifacts_verified", "identity_verified", "all_attempts_accounted",
    "independent_review_passed", "holdout_passed", "user_paths_passed",
)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def _hash(value):
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _complete(row, field):
    count = row.get("observed_cases")
    return (type(count) is int and count > 0 and
            row.get("measurement_counts", {}).get(field) == count and
            _number(row.get("mean_" + field)))


def _dominates(left, right):
    return (left["quality"] >= right["quality"] and left["cost"] <= right["cost"]
            and (left["quality"] > right["quality"] or left["cost"] < right["cost"]))


def pareto_front(rows):
    """Q is maximized, C minimized; no normalization or divide-by-zero."""
    for row in rows:
        if not _number(row.get("quality")) or not _number(row.get("cost")):
            raise ValueError("Pareto objectives must be complete finite measurements")
    return sorted(
        (row for row in rows if not any(_dominates(other, row) for other in rows)),
        key=lambda row: (-row["quality"], row["cost"], row.get("diff_bytes", 0), row["id"]),
    )


def select_candidates(document):
    """Consume comparisons produced outside the candidate's execution boundary."""
    if document.get("schema_version") != 1 or document.get("search_surface") != "context-only":
        raise ValueError("expected a frozen context-only selection record v1")
    seed = document.get("baseline")
    candidates = document.get("candidates")
    if not isinstance(seed, dict) or not isinstance(candidates, list) or not 1 <= len(candidates) <= 3:
        raise ValueError("one baseline and one to three candidates are required")
    ids = [seed.get("id"), *(row.get("id") for row in candidates)]
    if any(not isinstance(value, str) or not value for value in ids) or len(set(ids)) != len(ids):
        raise ValueError("candidate IDs must be unique nonempty strings")
    minimum = document.get("minimum_runs_per_case", 3)
    if type(minimum) is not int or minimum < 3:
        raise ValueError("at least three independent samples per case are required")
    goal = document.get("efficiency_goal_ratio", 0.10)
    if not _number(goal) or not 0 < goal < 1:
        raise ValueError("efficiency goal must be in (0,1)")
    base = seed.get("aggregate", {})
    binding = seed.get("binding", {})
    if (not _hash(binding.get("suite_sha256")) or
            not _hash(binding.get("harness_config_sha256")) or
            not isinstance(binding.get("context_revision"), str) or not binding["context_revision"] or
            not binding.get("model") or binding["model"] in ("unknown", "mixed") or
            str(binding["model"]).startswith("mixed:") or not binding.get("harness")):
        raise ValueError("baseline requires a verified model, harness and real configuration hashes")
    if not _number(base.get("mean_score_ratio")) or not _number(base.get("p10_score_ratio")):
        raise ValueError("baseline quality is missing")
    expected = set(document.get("required_cases", []))
    if not expected or set(base.get("covered_cases", [])) != expected:
        raise ValueError("baseline must cover the complete frozen case set")
    base_ids = set(base.get("run_ids", []))
    def independent(row):
        run_ids = row.get("run_ids", [])
        counts = row.get("case_runs", {})
        return (type(row.get("runs")) is int and row["runs"] > 0 and
                row.get("independent_runs") == row["runs"] == len(run_ids) == len(set(run_ids)) and
                set(counts) == expected and
                all(type(value) is int and value >= minimum for value in counts.values()) and
                len(set(counts.values())) == 1)
    if not independent(base):
        raise ValueError("baseline samples are incomplete or not independent")
    evaluations, eligible = [], []
    all_ids = set(base_ids)
    for candidate in candidates:
        reasons = []
        row = candidate.get("aggregate", {})
        bound = candidate.get("binding", {})
        comparison = candidate.get("comparison", {})
        evidence = candidate.get("evidence", {})
        for key in ("model", "harness", "suite_sha256", "harness_config_sha256"):
            if bound.get(key) != binding[key]:
                reasons.append("binding:" + key)
        if not bound.get("context_revision") or bound.get("context_revision") == binding["context_revision"]:
            reasons.append("candidate-context-revision")
        if comparison.get("ok") is not True or comparison.get("acceptance_ready") is not True:
            reasons.append("existing-comparator-not-ready")
        if set(row.get("covered_cases", [])) != expected or not independent(row):
            reasons.append("incomplete-or-unbalanced-samples")
        run_ids = set(row.get("run_ids", []))
        if all_ids & run_ids:
            reasons.append("reused-run-id")
        all_ids.update(run_ids)
        for key in REQUIRED_EVIDENCE:
            if evidence.get(key) is not True:
                reasons.append("needs-evidence:" + key)
        if evidence.get("critical_failures") != 0 or type(evidence.get("critical_failures")) is not int:
            reasons.append("critical-failures-or-unknown")
        if row.get("safety_violations") != 0 or type(row.get("safety_violations")) is not int:
            reasons.append("safety-violations-or-unknown")
        for key in ("mean_score_ratio", "p10_score_ratio"):
            if not _number(row.get(key)) or row[key] < base[key]:
                reasons.append("quality-regression:" + key)
        for key in ("zero_score_rate", "premature_stop_rate", "context_overread_rate"):
            if not _number(row.get(key)) or not _number(base.get(key)) or row[key] > base[key]:
                reasons.append("behavior-regression:" + key)
        if not _complete(base, "uncached_input_tokens") or not _complete(row, "uncached_input_tokens"):
            reasons.append("incomplete-pareto-cost")
        if not _complete(base, "elapsed_seconds") or not _complete(row, "elapsed_seconds"):
            reasons.append("incomplete-wall-time")
        elif row["mean_elapsed_seconds"] > base["mean_elapsed_seconds"]:
            reasons.append("wall-time-regression")
        diff_bytes = candidate.get("diff_bytes")
        if type(diff_bytes) is not int or diff_bytes <= 0:
            reasons.append("missing-context-diff")
        ratio = None
        if _complete(base, "uncached_input_tokens") and _complete(row, "uncached_input_tokens"):
            before = base["mean_uncached_input_tokens"]
            ratio = (before - row["mean_uncached_input_tokens"]) / before if before else 0.0
        evaluation = {"id": candidate["id"], "eligible": not reasons,
                      "reasons": reasons, "uncached_input_improvement_ratio": ratio,
                      "engineering_goal_met": ratio is not None and ratio >= goal}
        evaluations.append(evaluation)
        if not reasons:
            eligible.append({"id": candidate["id"], "quality": row["mean_score_ratio"],
                             "cost": row["mean_uncached_input_tokens"], "diff_bytes": diff_bytes})
    seed_objective = None
    if _complete(base, "uncached_input_tokens"):
        seed_objective = {"id": seed["id"], "quality": base["mean_score_ratio"],
                          "cost": base["mean_uncached_input_tokens"], "diff_bytes": 0}
    frontier = pareto_front(([seed_objective] if seed_objective else []) + eligible)
    winners = [row for row in frontier if row["id"] != seed["id"] and
               seed_objective is not None and _dominates(row, seed_objective)]
    selected = winners[0]["id"] if winners else seed["id"]
    return {"schema_version": 1, "status": "candidate-ready" if winners else "no-improvement",
            "selected": selected, "baseline_retained": not winners,
            "candidate_evaluations": evaluations, "pareto_front": frontier,
            "record_sha256": hashlib.sha256(json.dumps(document, sort_keys=True,
                                                       ensure_ascii=False).encode()).hexdigest(),
            "production_apply": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path, help="trusted evaluator selection record")
    args = parser.parse_args()
    try:
        result = select_candidates(json.loads(args.record.read_text(encoding="utf-8")))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
