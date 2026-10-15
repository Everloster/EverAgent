import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_reports  # noqa: E402
import eval_report_context  # noqa: E402
import reindex  # noqa: E402
import report_catalog  # noqa: E402
import report_quality  # noqa: E402


def load_report_generator():
    path = ROOT / "github-trending-analyzer" / "scripts" / "report_generator.py"
    spec = importlib.util.spec_from_file_location("report_generator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def complete_behavioral_case(case: dict, expected: dict) -> None:
    created = expected["artifact_policy"] in {"required", "update_existing"}
    skills = list(expected.get("expected_skill_paths") or [])
    if created:
        skills.extend(expected.get("artifact_expected_skill_paths") or [])
    checks = list(expected.get("required_checks") or [])
    if created:
        checks.extend(expected.get("artifact_required_checks") or [])
    quality_required = expected.get("quality_tier") is not None and created
    case.update(
        {
            "route": expected["expected_route"],
            "artifact_created": created,
            "initial_project_files": [],
            "repo_skills_loaded": skills,
            "paused_before_research": False,
            "clarification_count": 0,
            "checks_completed": checks,
            "completion_signals_met": expected["completion_signals"],
            "stop_reason": expected["expected_stop_reason"],
            "quality_tier": expected.get("quality_tier"),
            "quality_decision": "pass" if quality_required else None,
            "report_quality_score": 95 if quality_required else None,
            "generator_model": "glm-5.3",
            "reviewer_models": ["glm-5.3"] if quality_required else [],
            "anchor_comparison": "tie" if expected.get("reference_anchor") else None,
            "completed": expected["expected_completed"],
            "safety_violation": False,
        }
    )


class ReportToolingTests(unittest.TestCase):
    def test_catalog_covers_projects_and_excludes_podcast_sources(self):
        reports = list(report_catalog.iter_reports())
        domains = {collection.id for collection, _path in reports}

        self.assertIn("github-trending-analyzer", domains)
        self.assertIn("web-surfing", domains)
        self.assertIn("ai-practice", domains)
        self.assertFalse(any("transcripts" in path.parts for _collection, path in reports))

    def test_report_v1_contract_remains_supported(self):
        report = (
            ROOT
            / "ai-learning"
            / "reports"
            / "knowledge_reports"
            / "GPT6_Astra指令架构_从Prompt堆叠到按需控制_深度解析_20261015.md"
        )
        issues = audit_reports.audit_file(
            report,
            enforce=False,
            wikilinks=audit_reports._wikilink_index(),
        )
        self.assertEqual(
            [issue for issue in issues if issue.severity == "error"],
            [],
        )

    def test_strict_contract_rejects_noncanonical_status_and_missing_tags(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "strict-contract.md"
            report.write_text(
                """---
title: "Strict contract fixture"
domain: "ai-learning"
report_type: "knowledge_report"
status: "done"
updated_on: "2026-10-15"
quality_schema: "report-v1"
---

# Strict contract fixture

来源：https://example.com/source

## 思考与追问

1. 如何继续验证？
""",
                encoding="utf-8",
            )
            issues = audit_reports.audit_file(
                report,
                enforce=True,
                wikilinks=audit_reports._wikilink_index(),
            )

        errors = {issue.code for issue in issues if issue.severity == "error"}
        self.assertIn("META005", errors)
        self.assertIn("META007", errors)

    def test_report_v2_quality_gate_passes_with_evidence_and_independent_review(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "quality-fixture.md"
            report.write_text(
                """---
title: "Quality fixture"
domain: "ai-learning"
report_type: "knowledge_report"
status: "in_progress"
updated_on: "2026-10-15"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["quality"]
---

# Quality fixture

结论一来自官方资料。结论二由两个来源共同支持。结论三说明适用边界。

来源：https://example.com/one

## Limitations

当前只验证固定样本。

## 思考与追问

1. 如何扩大样本？
""",
                encoding="utf-8",
            )
            evidence_path, review_path = report_quality.quality_artifact_paths(report)
            relative = report_quality.report_relative_path(report)
            evidence = {
                "schema_version": 1,
                "report_path": relative,
                "quality_tier": "important",
                "created_on": "2026-10-15",
                "generator": {
                    "model": "glm-5.3",
                    "harness": "codex",
                    "run_id": "generator-1",
                    "explicit_model_override": False,
                },
                "task": {
                    "summary": "验证 report-v2 质量门",
                    "requirements": [{"id": "R01", "text": "报告必须解释质量门"}],
                },
                "sources": [
                    {"id": "S01", "kind": "official", "title": "Source one", "locator": "https://example.com/one", "accessed_on": "2026-10-15"},
                    {"id": "S02", "kind": "primary", "title": "Source two", "locator": "https://example.com/two", "accessed_on": "2026-10-15"},
                ],
                "claims": [
                    {"id": "C01", "claim": "结论一", "report_anchor": "结论一来自官方资料", "support": "direct", "source_ids": ["S01"], "evidence": "官方资料支持结论一", "critical": True},
                    {"id": "C02", "claim": "结论二", "report_anchor": "结论二由两个来源共同支持", "support": "derived", "source_ids": ["S01", "S02"], "evidence": "两项来源交叉支持", "critical": True},
                    {"id": "C03", "claim": "结论三", "report_anchor": "结论三说明适用边界", "support": "direct", "source_ids": ["S02"], "evidence": "原始资料给出边界", "critical": True},
                ],
                "limitations": ["当前只验证固定样本"],
            }
            review = {
                "schema_version": 1,
                "report_path": relative,
                "quality_tier": "important",
                "revision_round": 1,
                "reviews": [
                    {
                        "role": "primary_review",
                        "reviewer": {
                            "model": "glm-5.3",
                            "harness": "claude-code",
                            "run_id": "review-1",
                            "independent_context": True,
                            "explicit_model_override": False,
                        },
                        "scores": {
                            "evidence_fidelity": 94,
                            "request_coverage": 92,
                            "reasoning_quality": 90,
                            "readability": 90,
                            "limitations": 88,
                        },
                        "score_reasons": {
                            "evidence_fidelity": "关键结论均与来源核对",
                            "request_coverage": "覆盖唯一明确需求",
                            "reasoning_quality": "推理链完整",
                            "readability": "结构可独立阅读",
                            "limitations": "边界已明确列出",
                        },
                        "critical_claim_ids_checked": ["C01", "C02", "C03"],
                        "source_ids_checked": ["S01", "S02"],
                        "requirement_ids_checked": ["R01"],
                        "unsupported_claims": [],
                        "missing_requirements": [],
                        "hard_failures": [],
                        "notes": "未发现阻断问题。",
                    }
                ],
                "decision": {},
            }
            report_quality._write_json(evidence_path, evidence)
            report_quality._write_json(review_path, review)
            result = report_quality.evaluate_report(report)
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "report_quality.py"), "check", str(report), "--finalize"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            finalized_metadata = report_catalog.parse_frontmatter(report.read_text(encoding="utf-8"))
            finalized_review = json.loads(review_path.read_text(encoding="utf-8"))
            audit_issues = audit_reports.audit_file(
                report,
                enforce=True,
                wikilinks=audit_reports._wikilink_index(),
            )

        self.assertEqual(result["decision"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(finalized_metadata["status"], "completed")
        self.assertEqual(finalized_review["decision"]["status"], "pass")
        self.assertEqual([item for item in audit_issues if item.severity == "error"], [])

    def test_new_report_v2_draft_is_blocked_before_review(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "draft-report.md"
            report.write_text(
                """---
title: "Draft"
domain: "ai-learning"
report_type: "knowledge_report"
status: "in_progress"
updated_on: "2026-10-15"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["draft"]
---

# Draft
""",
                encoding="utf-8",
            )
            issues = audit_reports.audit_file(
                report,
                enforce=True,
                wikilinks=audit_reports._wikilink_index(),
            )

        errors = [item for item in issues if item.severity == "error"]
        self.assertIn("META009", {item.code for item in errors})

    def test_completed_report_v2_requires_quality_artifacts(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "completed-report.md"
            report.write_text(
                """---
title: "Completed"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-15"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["quality"]
---

# Completed

来源：https://example.com/source

## 思考与追问

1. 如何复核？
""",
                encoding="utf-8",
            )
            issues = audit_reports.audit_file(
                report,
                enforce=True,
                wikilinks=audit_reports._wikilink_index(),
            )

        error_codes = {item.code for item in issues if item.severity == "error"}
        self.assertIn("QG003", error_codes)
        self.assertIn("QG005", error_codes)

    def test_disabled_model_cannot_initialize_report_v2(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "disabled-model.md"
            report.write_text("---\ntitle: x\ndomain: ai-learning\n---\n# x\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                report_quality.initialize_quality_artifacts(
                    report,
                    tier="standard",
                    generator_model="MiniMax-M3",
                    harness="codex",
                )

    def test_initialize_quality_artifacts_sets_v2_metadata(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "initialized-report.md"
            report.write_text(
                "---\ntitle: x\ndomain: ai-learning\nreport_type: knowledge_report\n"
                "status: completed\nupdated_on: 2026-10-15\nsemantic_tags: [quality]\n---\n# x\n",
                encoding="utf-8",
            )
            evidence_path, review_path, findings = report_quality.initialize_quality_artifacts(
                report,
                tier="important",
                generator_model="glm53",
                harness="pi",
                run_id="generator-init",
            )
            metadata = report_catalog.parse_frontmatter(report.read_text(encoding="utf-8"))
            evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

        self.assertEqual(findings, [])
        self.assertEqual(metadata["quality_schema"], "report-v2")
        self.assertEqual(metadata["quality_tier"], "important")
        self.assertEqual(metadata["status"], "in_progress")
        self.assertEqual(evidence["generator"]["model"], "glm-5.3")
        self.assertTrue(review_path.name.endswith(".review.json"))

    def test_model_policy_matches_user_preferences(self):
        policy = report_quality.load_policy()["model_policy"]
        self.assertEqual(policy["default_generator"], "glm-5.3")
        self.assertEqual(policy["default_reviewer"], "glm-5.3")
        self.assertIn("kimi-k3", policy["scarce_models"])
        self.assertIn("minimax-m3", policy["disabled_models"])

    def test_quality_failure_revises_then_escalates(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "routing-report.md"
            report.write_text(
                "---\ntitle: routing\ndomain: ai-learning\nreport_type: knowledge_report\n"
                "status: in_progress\nupdated_on: 2026-10-15\nquality_schema: report-v2\n"
                "quality_tier: important\nsemantic_tags: [quality]\n---\n# routing\n",
                encoding="utf-8",
            )
            evidence_path, review_path = report_quality.quality_artifact_paths(report)
            report_quality._write_json(evidence_path, {})
            report_quality._write_json(review_path, {})
            evidence_summary = {
                "requirement_ids": [],
                "source_ids": [],
                "claim_ids": [],
                "critical_claim_ids": [],
                "critical_source_ids": [],
                "generator_model": "glm-5.3",
                "generator_run_id": "generator-1",
                "generator_explicit_override": False,
            }
            score_failure = [report_quality.QualityFinding("error", "SCORE001", "low score")]

            with mock.patch.object(
                report_quality,
                "validate_evidence_manifest",
                return_value=([], evidence_summary),
            ), mock.patch.object(
                report_quality,
                "validate_review_record",
                side_effect=[
                    (score_failure, {"revision_round": 1, "score": 70, "dimension_scores": {}, "review_scores": [70], "reviewer_models": ["glm-5.3"], "strong_reviews": 0, "scarce_model_calls": 0}),
                    (score_failure, {"revision_round": 2, "score": 70, "dimension_scores": {}, "review_scores": [70], "reviewer_models": ["glm-5.3"], "strong_reviews": 0, "scarce_model_calls": 0}),
                ],
            ):
                first = report_quality.evaluate_report(report)
                second = report_quality.evaluate_report(report)

        self.assertEqual(first["decision"], "revise")
        self.assertEqual(second["decision"], "escalate")
        self.assertEqual(second["recommended_models"], ["gpt-5.6-sol", "kimi-k3"])

    def test_quality_artifact_change_maps_back_to_report(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "mapped-report.md"
            report.write_text("# mapped\n", encoding="utf-8")
            evidence_path, _review_path = report_quality.quality_artifact_paths(report)
            mapped = audit_reports._reports_from_paths({evidence_path})

        self.assertEqual(mapped, [report])

    def test_new_revision_archives_previous_reviews(self):
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "revision-report.md"
            report.write_text(
                "---\ntitle: revision\ndomain: ai-learning\nreport_type: knowledge_report\n"
                "status: completed\nupdated_on: 2026-10-15\nquality_schema: report-v2\n"
                "quality_tier: important\nsemantic_tags: [quality]\n---\n# revision\n",
                encoding="utf-8",
            )
            _evidence_path, review_path = report_quality.quality_artifact_paths(report)
            report_quality._write_json(
                review_path,
                {
                    "schema_version": 1,
                    "report_path": report_quality.report_relative_path(report),
                    "quality_tier": "important",
                    "revision_round": 1,
                    "reviews": [{"reviewer": {"run_id": "review-1"}}],
                    "decision": {"status": "revise"},
                },
            )
            report_quality.start_new_revision(report)
            updated = json.loads(review_path.read_text(encoding="utf-8"))
            metadata = report_catalog.parse_frontmatter(report.read_text(encoding="utf-8"))

        self.assertEqual(updated["revision_round"], 2)
        self.assertEqual(updated["reviews"], [])
        self.assertEqual(updated["history"][0]["revision_round"], 1)
        self.assertEqual(metadata["status"], "in_progress")

    def test_staged_addition_is_treated_as_new(self):
        report = (
            ROOT
            / "ai-learning"
            / "reports"
            / "knowledge_reports"
            / "GPT6_Astra指令架构_从Prompt堆叠到按需控制_深度解析_20261015.md"
        )
        with mock.patch.object(
            audit_reports,
            "_git_paths",
            side_effect=[{report}, {report}, set()],
        ):
            reports, new_paths = audit_reports.changed_reports()

        self.assertEqual(reports, [report])
        self.assertIn(report.resolve(), new_paths)

    def test_git_path_discovery_preserves_unicode_paths(self):
        relative = Path("ai-learning/reports/knowledge_reports/中文报告.md")
        completed = subprocess.CompletedProcess(
            args=["git"],
            returncode=0,
            stdout=f"{relative}\0",
            stderr="",
        )
        with mock.patch.object(audit_reports.subprocess, "run", return_value=completed):
            paths = audit_reports._git_paths(["git", "diff", "--name-only", "-z"])

        self.assertEqual(paths, {ROOT / relative})

    def test_generated_index_covers_github_and_skips_shownotes(self):
        index = reindex.build_index(reindex.collect_reports())

        self.assertIn("## 🔭 GitHub Research", index)
        self.assertIn("research_yetone_magpie.md", index)
        self.assertNotIn(".shownotes.md", index)

    def test_static_context_evaluation_has_no_errors(self):
        result = eval_report_context.static_evaluation()
        self.assertEqual(result["errors"], [])
        self.assertGreaterEqual(result["ace_cases"], 10)
        self.assertEqual(result["discoverable_skill_count"], 1)
        self.assertLessEqual(result["report_skill_description_chars"], 180)

    def test_behavioral_template_can_score_a_complete_run(self):
        template = eval_report_context.run_template()
        suite = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )
        expected = {case["id"]: case for case in suite["cases"]}

        template["model"] = "test-model"
        template["harness"] = "test-harness"
        template["context_revision"] = "test-revision"
        for case in template["cases"]:
            exp = expected[case["id"]]
            complete_behavioral_case(case, exp)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            path.write_text(json.dumps(template, ensure_ascii=False), encoding="utf-8")
            result = eval_report_context.score_run(path)
        self.assertEqual(result["score"], result["max_score"])

    def test_behavioral_score_requires_explicit_safety_result(self):
        template = eval_report_context.run_template()
        suite = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )
        expected = {case["id"]: case for case in suite["cases"]}
        for case in template["cases"]:
            exp = expected[case["id"]]
            complete_behavioral_case(case, exp)
            case["safety_violation"] = None

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            path.write_text(json.dumps(template, ensure_ascii=False), encoding="utf-8")
            result = eval_report_context.score_run(path)

        self.assertEqual(result["score"], 0)

    def test_behavioral_score_detects_skill_false_positive(self):
        template = eval_report_context.run_template()
        suite = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )
        expected = {case["id"]: case for case in suite["cases"]}
        for case in template["cases"]:
            complete_behavioral_case(case, expected[case["id"]])
        target = next(case for case in template["cases"] if case["id"] == "a_brief_question")
        target["repo_skills_loaded"] = [".agents/skills/everagent-report/SKILL.md"]

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            path.write_text(json.dumps(template, ensure_ascii=False), encoding="utf-8")
            result = eval_report_context.score_run(path)

        row = next(case for case in result["cases"] if case["id"] == "a_brief_question")
        self.assertFalse(row["checks"]["skills"])
        self.assertEqual(row["skill_precision"], 0)
        self.assertEqual(row["score"], 85)

    def test_github_report_generator_emits_current_frontmatter(self):
        module = load_report_generator()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "project.md"
            module.generate_project_report(
                {
                    "owner": "acme",
                    "repo": "rocket",
                    "description": "Fast launch toolkit",
                    "stars": 1234,
                    "forks": 56,
                    "language": "Python",
                    "today_stars": 78,
                    "url": "https://github.com/acme/rocket",
                },
                {
                    "summary": "A strong repo",
                    "languages": {"Python": 100},
                    "architecture": "[代码] package layout",
                    "contributors": [],
                    "releases": [],
                },
                output,
            )
            content = output.read_text(encoding="utf-8")
        self.assertIn('quality_schema: "report-v2"', content)
        self.assertIn('quality_tier: "important"', content)
        self.assertIn('status: "in_progress"', content)
        self.assertIn('report_type: "repo_deep_research"', content)

    def test_behavioral_aggregate_reports_p10(self):
        template = eval_report_context.run_template()
        suite = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )
        expected = {case["id"]: case for case in suite["cases"]}
        template.update({"model": "glm-5.3", "harness": "codex", "context_revision": "test"})
        for case in template["cases"]:
            exp = expected[case["id"]]
            complete_behavioral_case(case, exp)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            path.write_text(json.dumps(template, ensure_ascii=False), encoding="utf-8")
            result = eval_report_context.aggregate_runs([path])

        self.assertEqual(result["groups"][0]["p10_task_score"], 100)
        self.assertEqual(result["groups"][0]["p10_report_quality_score"], 95)
        self.assertEqual(result["groups"][0]["mean_skill_precision"], 1)
        self.assertEqual(result["groups"][0]["mean_skill_recall"], 1)
        self.assertEqual(result["groups"][0]["premature_stop_rate"], 0)

    def test_github_summary_avoids_links_for_missing_reports(self):
        module = load_report_generator()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "summary.md"
            module.generate_summary_report(
                "weekly",
                [
                    {
                        "owner": "acme",
                        "repo": "rocket",
                        "description": "Fast launch toolkit",
                        "stars": 1234,
                        "forks": 56,
                        "language": "Python",
                        "today_stars": 78,
                        "url": "https://github.com/acme/rocket",
                    }
                ],
                output,
                missing_repos=["acme/rocket"],
            )
            content = output.read_text(encoding="utf-8")

        self.assertNotIn("./research_acme_rocket.md", content)
        self.assertIn("acme/rocket — 本地深研报告缺失", content)

    def test_reindex_check_is_clean_after_generation(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "reindex.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
