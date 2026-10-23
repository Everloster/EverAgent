"""Synthetic public contracts; no private trajectories or device fixtures."""
import copy
import unittest

try:
    from .harness_selection import pareto_front, select_candidates
except ImportError:
    from harness_selection import pareto_front, select_candidates


def record():
    def aggregate(prefix, cost):
        return {"mean_score_ratio": 1.0, "p10_score_ratio": 1.0,
                "runs": 3, "independent_runs": 3, "run_ids": [prefix + str(i) for i in range(3)],
                "observed_cases": 3, "covered_cases": ["synthetic-context"],
                "case_runs": {"synthetic-context": 3}, "safety_violations": 0,
                "zero_score_rate": 0.0, "premature_stop_rate": 0.0, "context_overread_rate": 0.0,
                "measurement_counts": {"uncached_input_tokens": 3, "elapsed_seconds": 3},
                "mean_uncached_input_tokens": cost, "mean_elapsed_seconds": 10}
    binding = {"model": "synthetic-fixed-model", "harness": "synthetic-harness",
               "suite_sha256": "a" * 64, "harness_config_sha256": "b" * 64, "context_revision": "seed"}
    candidate_binding = dict(binding, context_revision="candidate")
    evidence = {key: True for key in ("artifacts_verified", "identity_verified", "all_attempts_accounted",
                                      "independent_review_passed", "holdout_passed", "user_paths_passed")}
    evidence["critical_failures"] = 0
    return {"schema_version": 1, "search_surface": "context-only", "required_cases": ["synthetic-context"],
            "baseline": {"id": "seed", "binding": binding, "aggregate": aggregate("seed", 100)},
            "candidates": [{"id": "c1", "binding": candidate_binding, "aggregate": aggregate("candidate", 80),
                            "comparison": {"ok": True, "acceptance_ready": True},
                            "evidence": evidence, "diff_bytes": 40}]}


class HarnessSelectionTests(unittest.TestCase):
    def test_complete_non_regressing_candidate_can_be_reviewed(self):
        original = record()
        snapshot = copy.deepcopy(original)
        selected = select_candidates(original)
        self.assertEqual(selected["selected"], "c1")
        self.assertFalse(selected["production_apply"])
        self.assertEqual(original, snapshot)

    def test_missing_holdout_keeps_baseline(self):
        doc = record()
        doc["candidates"][0]["evidence"]["holdout_passed"] = False
        selected = select_candidates(doc)
        self.assertEqual(selected["status"], "no-improvement")
        self.assertEqual(selected["selected"], "seed")

    def test_quality_regression_cannot_be_hidden_by_lower_cost(self):
        doc = record()
        doc["candidates"][0]["aggregate"]["p10_score_ratio"] = 0.9
        self.assertEqual(select_candidates(doc)["selected"], "seed")

    def test_changed_real_executor_hash_is_rejected(self):
        doc = record()
        doc["candidates"][0]["binding"]["harness_config_sha256"] = "c" * 64
        self.assertEqual(select_candidates(doc)["selected"], "seed")

    def test_missing_cost_is_not_zero(self):
        doc = record()
        doc["candidates"][0]["aggregate"]["mean_uncached_input_tokens"] = None
        self.assertEqual(select_candidates(doc)["selected"], "seed")

    def test_reused_runs_and_bool_counts_are_rejected(self):
        doc = record()
        doc["candidates"][0]["aggregate"]["run_ids"][0] = "seed0"
        self.assertEqual(select_candidates(doc)["selected"], "seed")
        doc = record()
        doc["candidates"][0]["evidence"]["critical_failures"] = False
        self.assertEqual(select_candidates(doc)["selected"], "seed")

    def test_incomplete_baseline_never_becomes_evidence(self):
        doc = record()
        doc["baseline"]["aggregate"]["case_runs"]["synthetic-context"] = 2
        with self.assertRaises(ValueError):
            select_candidates(doc)

    def test_degenerate_pareto_and_stable_ties(self):
        rows = [{"id": "b", "quality": 1, "cost": 0, "diff_bytes": 20},
                {"id": "a", "quality": 1, "cost": 0, "diff_bytes": 10}]
        self.assertEqual([row["id"] for row in pareto_front(rows)], ["a", "b"])
        with self.assertRaises(ValueError):
            pareto_front([{"id": "missing", "quality": 1, "cost": None}])

    def test_equal_metrics_prefer_no_change(self):
        doc = record()
        doc["candidates"][0]["aggregate"]["mean_uncached_input_tokens"] = 100
        self.assertEqual(select_candidates(doc)["selected"], "seed")

    def test_more_than_three_candidates_are_not_an_open_search(self):
        doc = record()
        doc["candidates"] *= 4
        with self.assertRaises(ValueError):
            select_candidates(doc)


if __name__ == "__main__":
    unittest.main()
