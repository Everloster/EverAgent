#!/usr/bin/env python3
"""Deterministic teaching lab: review evidence, duplicate findings and stale snapshots.

No model API, CodeRabbit service, network access or third-party dependencies.
Reviewer messages and their root-cause IDs are hand-authored fixtures.
The test contracts are explicit; this program is not a general bug detector.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
import inspect
import json
from pathlib import Path
from typing import Callable


# Application contract: a tenant may only read its own order.
def order_v1(order_id, tenant, orders):
    return orders.get(order_id)


def order_v2(order_id, tenant, orders):
    order = orders.get(order_id)
    return order if order and order["tenant"] == tenant else None


# Application contract: every item fits in a page; an empty list has zero pages.
def pages_v1(total, page_size):
    return total // page_size


def pages_v2(total, page_size):
    return (total + page_size - 1) // page_size


# Application contract: quantity must be a positive integer.
def quantity_v1(value):
    return int(value)


def quantity_v2(value):
    result = int(value)
    if result <= 0:
        raise ValueError("quantity must be positive")
    return result


@dataclass(frozen=True)
class Snapshot:
    label: str
    order: Callable
    pages: Callable
    quantity: Callable

    @property
    def sha256(self):
        # A content snapshot, not a Git commit ID.
        code = "\n".join(inspect.getsource(f) for f in
                         (self.order, self.pages, self.quantity))
        return hashlib.sha256(code.encode()).hexdigest()


@dataclass(frozen=True)
class Finding:
    reviewer: str
    root_cause: str
    claim: str
    snapshot_sha256: str


def probe(snapshot, root_cause):
    """Exercise only the predeclared contract associated with a fixture finding."""
    if root_cause == "tenant-isolation":
        orders = {"order-b": {"tenant": "tenant-b", "amount": 42}}
        observed = snapshot.order("order-b", "tenant-a", orders)
        return {"input": "tenant-a reads tenant-b order", "expected": None,
                "observed": observed, "violation": observed is not None}
    if root_cause == "last-page":
        observed = snapshot.pages(23, 10)
        return {"input": {"total": 23, "page_size": 10}, "expected": 3,
                "observed": observed, "violation": observed != 3}
    if root_cause == "positive-quantity":
        try:
            observed = snapshot.quantity(0)
        except ValueError:
            observed = "ValueError"
        return {"input": 0, "expected": "ValueError", "observed": observed,
                "violation": observed != "ValueError"}
    if root_cause == "empty-page":
        observed = snapshot.pages(0, 10)
        return {"input": {"total": 0, "page_size": 10}, "expected": 0,
                "observed": observed, "violation": observed != 0,
                "contract_note": "The fixture explicitly requires zero pages, not one."}
    raise ValueError(f"No trusted probe registered for {root_cause}")


def verify(finding, snapshot, *, environment_ready=True, exercise_target=True):
    result = {"root_cause": finding.root_cause,
              "reviewed_snapshot": finding.snapshot_sha256,
              "tested_snapshot": snapshot.sha256,
              "application_ready": environment_ready,
              "target_exercised": False}
    if finding.snapshot_sha256 != snapshot.sha256:
        return result | {"status": "stale", "reason": "snapshot_changed"}
    if not environment_ready:
        return result | {"status": "inconclusive", "reason": "setup_failed"}
    if not exercise_target:
        return result | {"status": "inconclusive", "reason": "target_not_exercised"}
    evidence = probe(snapshot, finding.root_cause)
    return result | {"status": "reproduced" if evidence["violation"] else "not_reproduced",
                     "target_exercised": True, "evidence": evidence}


def metrics(selected, gold):
    selected = set(selected)
    tp, fp, fn = len(selected & gold), len(selected - gold), len(gold - selected)
    precision = tp / (tp + fp) if tp + fp else None
    recall = tp / len(gold)
    f1 = 2 * tp / (2 * tp + fp + fn)
    return {"tp": tp, "fp": fp, "fn": fn, "precision": precision,
            "recall": recall, "f1": f1, "issue_ids": sorted(selected)}


def regression_checks(snapshot):
    orders = {"order-b": {"tenant": "tenant-b", "amount": 42}}
    checks = {
        "own_order_readable": snapshot.order("order-b", "tenant-b", orders) == orders["order-b"],
        "unknown_order_absent": snapshot.order("missing", "tenant-b", orders) is None,
        "cross_tenant_denied": snapshot.order("order-b", "tenant-a", orders) is None,
        "page_counts": all(snapshot.pages(n, 10) == expected
                           for n, expected in [(0, 0), (1, 1), (10, 1), (11, 2), (23, 3)]),
        "valid_quantity": all(snapshot.quantity(n) == n for n in (1, 3)),
    }
    for value in (0, -1):
        try:
            snapshot.quantity(value)
        except ValueError:
            checks[f"reject_quantity_{value}"] = True
        else:
            checks[f"reject_quantity_{value}"] = False
    return checks


def run():
    original = Snapshot("original", order_v1, pages_v1, quantity_v1)
    partial = Snapshot("only_reported_bugs_fixed", order_v2, pages_v2, quantity_v1)
    fixed = Snapshot("all_declared_checks_pass", order_v2, pages_v2, quantity_v2)
    gold = {"tenant-isolation", "last-page", "positive-quantity"}
    assert all(probe(original, issue)["violation"] for issue in gold)
    assert not probe(original, "empty-page")["violation"]

    # Three hand-authored reviewer outputs, including one shared false alarm.
    findings = [
        Finding("A", "tenant-isolation", "Cross-tenant order reads are allowed", original.sha256),
        Finding("A", "empty-page", "An empty collection should return one page", original.sha256),
        Finding("B", "tenant-isolation", "The order lookup misses the tenant check", original.sha256),
        Finding("B", "empty-page", "Zero pages for no items is a bug", original.sha256),
        Finding("C", "last-page", "The final partial page is omitted", original.sha256),
        Finding("C", "empty-page", "Empty input should have a page", original.sha256),
    ]
    per_issue = {}
    for finding in findings:
        per_issue.setdefault(finding.root_cause, finding)
    # Count distinct reviewers so one reviewer cannot create extra votes.
    votes = Counter()
    for reviewer in {f.reviewer for f in findings}:
        votes.update({f.root_cause for f in findings if f.reviewer == reviewer})
    majority = {issue for issue, count in votes.items() if count >= 2}
    evidence = [verify(finding, original) for finding in per_issue.values()]
    confirmed = {r["root_cause"] for r in evidence if r["status"] == "reproduced"}
    policies = {"deduplicated_union": metrics(per_issue, gold),
                "two_of_three_vote": metrics(majority, gold),
                "contract_confirmed_candidates": metrics(confirmed, gold)}
    assert policies["deduplicated_union"]["tp"] == 2
    assert policies["two_of_three_vote"]["tp"] == 1
    assert policies["two_of_three_vote"]["fp"] == 1
    assert policies["contract_confirmed_candidates"]["fn"] == 1

    auth = findings[0]
    cases = {
        "setup_failure": verify(auth, original, environment_ready=False),
        "unexercised_target": verify(auth, original, exercise_target=False),
        "old_evidence_new_snapshot": verify(auth, partial),
        "fresh_check_after_fix": verify(Finding("A", auth.root_cause, auth.claim, partial.sha256), partial),
    }
    assert cases["setup_failure"]["status"] == "inconclusive"
    assert cases["unexercised_target"]["status"] == "inconclusive"
    assert cases["old_evidence_new_snapshot"]["status"] == "stale"
    assert cases["fresh_check_after_fix"]["status"] == "not_reproduced"

    regressions = {s.label: regression_checks(s) for s in (original, partial, fixed)}
    assert not all(regressions[partial.label].values())
    assert all(regressions[fixed.label].values())
    return {
        "experiment": "hand-authored review fixtures and executable contract probes",
        "model_calls": 0,
        "snapshot_ids_are": "SHA-256 of local fixture functions, not Git commits",
        "snapshots": {s.label: s.sha256 for s in (original, partial, fixed)},
        "raw_comments": len(findings), "unique_candidates": len(per_issue),
        "known_issues": sorted(gold), "votes": dict(sorted(votes.items())),
        "policies": policies, "candidate_evidence": evidence,
        "verification_cases": cases, "regression_checks": regressions,
        "limits": [
            "Findings and root-cause groups were written by the author, not discovered by an AI.",
            "Contracts cover this fixture only; they are not exhaustive security tests.",
            "Not reproduced alone does not establish that a real-world finding is false.",
            "Inconclusive findings must remain unresolved, not be counted as passed.",
            "The confirmed set misses a known issue absent from every reviewer output.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optionally save the deterministic result JSON")
    args = parser.parse_args()
    result = run()
    result["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
