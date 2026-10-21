import importlib.util
import io
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
import precommit_quality  # noqa: E402
import reindex  # noqa: E402
import report_catalog  # noqa: E402
import report_quality  # noqa: E402
import run_ace_context_ab  # noqa: E402


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
            "initial_project_files": list(expected.get("expected_initial_files") or []),
            "repo_skills_loaded": skills,
            "paused_before_research": expected.get("must_pause_before_research") is True,
            "clarification_count": 1 if expected.get("must_pause_before_research") else 0,
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
        reports_dir = ROOT / "ai-learning" / "reports"
        with tempfile.TemporaryDirectory(dir=reports_dir) as directory:
            report = Path(directory) / "legacy-v1.md"
            report.write_text(
                """---
title: "Legacy v1"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-15"
quality_schema: "report-v1"
semantic_tags: ["legacy"]
---

# Legacy v1

来源：https://example.com/source

## 思考与追问

1. 何时按需迁移？
""",
                encoding="utf-8",
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
            evidence_schema, _review_schema = report_quality.load_artifact_schemas()
            malformed_evidence = json.loads(json.dumps(evidence))
            malformed_evidence["task"]["requirements"] = "invalid"
            schema_errors = report_quality._schema_errors(malformed_evidence, evidence_schema)
            unsafe_local_evidence = json.loads(json.dumps(evidence))
            unsafe_local_evidence["sources"][0].update(
                {"kind": "local", "locator": "/etc/passwd"}
            )
            unsafe_findings, _unsafe_summary = report_quality.validate_evidence_manifest(
                report,
                report_catalog.parse_frontmatter(report.read_text(encoding="utf-8")),
                unsafe_local_evidence,
                report_quality.load_policy(),
            )
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
            finalized_result = report_quality.evaluate_report(report)
            repeated_finalize = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "report_quality.py"), "check", str(report), "--finalize"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            stricter_policy = json.loads(json.dumps(report_quality.load_policy()))
            stricter_policy["tiers"]["important"]["minimum_total"] = 99
            pinned_policy_result = report_quality.evaluate_report(report, stricter_policy)
            audit_issues = audit_reports.audit_file(
                report,
                enforce=True,
                wikilinks=audit_reports._wikilink_index(),
            )
            forged_review = json.loads(json.dumps(finalized_review))
            forged_review["decision"]["policy_sha256"] = "0" * 64
            report_quality._write_json(review_path, forged_review)
            forged_policy_result = report_quality.evaluate_report(report)
            report_quality._write_json(review_path, finalized_review)
            report.write_text(report.read_text(encoding="utf-8") + "\n判定后改动。\n", encoding="utf-8")
            tampered_result = report_quality.evaluate_report(report)

        self.assertEqual(result["decision"], "pass")
        self.assertEqual(result["errors"], [])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(finalized_metadata["status"], "completed")
        self.assertEqual(finalized_review["decision"]["status"], "pass")
        self.assertEqual(repeated_finalize.returncode, 1)
        self.assertIn("finalized reports are immutable", repeated_finalize.stderr)
        self.assertEqual(finalized_review["decision"]["policy_id"], report_quality.load_policy()["policy_id"])
        self.assertEqual(len(finalized_review["decision"]["policy_sha256"]), 64)
        self.assertEqual(finalized_result["policy_source"], "archive")
        self.assertEqual(pinned_policy_result["decision"], "pass")
        self.assertEqual(pinned_policy_result["policy_source"], "archive")
        self.assertIn("QG008", {item["code"] for item in forged_policy_result["errors"]})
        self.assertIn("type must be array", "\n".join(schema_errors))
        self.assertIn("EVM035", {item.code for item in unsafe_findings})
        self.assertIn("QG014", {item["code"] for item in tampered_result["errors"]})
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
        self.assertEqual(result["quality_replays"], 5)
        self.assertTrue(result["commit_wrapper_guarded"])
        self.assertTrue(result["ci_quality_guarded"])
        self.assertIn(result["ace_context_ab_status"], {"current", "context-changed"})
        self.assertEqual(result["ace_context_ab_guarded"], result["ace_context_ab_status"] == "current")
        self.assertTrue(result["cross_model_sampling_guarded"])
        self.assertEqual(result["discoverable_skill_count"], 1)
        self.assertLessEqual(result["report_skill_description_chars"], 180)

    def test_ab_context_fingerprint_change_is_pending_not_fresh_evidence(self):
        with mock.patch.object(eval_report_context, "_behavior_context_sha256", return_value="0" * 64):
            result = eval_report_context.static_evaluation()
        self.assertFalse(result["ace_context_ab_guarded"])
        self.assertEqual(result["ace_context_ab_status"], "context-changed")
        self.assertTrue(any("上下文指纹已变化" in warning for warning in result["warnings"]))

    def test_matching_ab_context_fingerprint_allows_complete_evidence(self):
        owner = eval_report_context._load_instruction_policy()["owners"]["ace_context_ab_result"]
        value = json.loads((ROOT / owner).read_text(encoding="utf-8"))
        fingerprint = value["refs"]["candidate"]["context_sha256"]
        with mock.patch.object(eval_report_context, "_behavior_context_sha256", return_value=fingerprint):
            result = eval_report_context.static_evaluation()
        self.assertTrue(result["ace_context_ab_guarded"])
        self.assertEqual(result["ace_context_ab_status"], "current")

    def test_pi_trace_parser_uses_observed_repo_reads(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory)
            paths = [
                "ai-learning/AGENTS.md",
                ".agents/skills/everagent-report/SKILL.md",
                "ai-learning/skills/拆书取景/SKILL.md",
            ]
            for relative in paths:
                target = snapshot / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("fixture", encoding="utf-8")
            final = {
                "route": "ai-learning",
                "artifact_policy": "required",
                "paused_before_research": False,
                "clarification_count": 0,
                "clarification_question": "",
                "initial_project_files": [*paths, "docs/not-read.md"],
                "repo_skills_loaded": paths[1:],
            }
            events = []
            for relative in paths:
                events.append(
                    {
                        "type": "tool_execution_start",
                        "toolName": "read",
                        "args": {"path": relative},
                    }
                )
            events.append(
                {
                    "type": "message_end",
                    "message": {
                        "role": "assistant",
                        "content": [{"type": "text", "text": json.dumps(final)}],
                        "model": "glm-5.3",
                        "provider": "zai-coding-cn",
                        "usage": {"input": 100, "cacheRead": 20, "output": 10},
                    },
                }
            )
            trace = "\n".join(json.dumps(event, ensure_ascii=False) for event in events)
            observed = run_ace_context_ab.parse_pi_trace(trace, snapshot)

        self.assertEqual(observed["initial_project_files"], paths)
        self.assertEqual(observed["repo_skills_loaded"], paths[1:])
        self.assertNotIn("docs/not-read.md", observed["initial_project_files"])
        self.assertEqual(observed["input_tokens"], 120)

    def test_startup_probe_scores_expected_route_and_skills(self):
        suite = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )
        case = next(item for item in suite["cases"] if item["id"] == "a_article_deep_analysis")
        observed = {
            "route": "ai-learning",
            "artifact_policy": "required",
            "paused_before_research": False,
            "clarification_count": 0,
            "initial_project_files": [
                "ai-learning/AGENTS.md",
                ".agents/skills/everagent-report/SKILL.md",
                "ai-learning/skills/拆书取景/SKILL.md",
            ],
            "repo_skills_loaded": [
                ".agents/skills/everagent-report/SKILL.md",
                "ai-learning/skills/拆书取景/SKILL.md",
            ],
        }

        result = run_ace_context_ab.score_probe(case, observed)

        self.assertEqual(result["score"], 100)
        self.assertEqual(result["skill_precision"], 1)
        self.assertEqual(result["skill_recall"], 1)

    def test_context_ab_treats_recovered_tool_failures_as_telemetry(self):
        baseline = {
            "successful_runs": 42,
            "mean_score": 95.0,
            "minimum_score": 70.0,
            "p10_score": 90.0,
            "subperfect_runs": 5,
            "zero_rate": 0.0,
            "route_accuracy": 1.0,
            "artifact_policy_accuracy": 1.0,
            "initiative_accuracy": 1.0,
            "context_budget_accuracy": 0.95,
            "mean_skill_precision": 0.95,
            "mean_skill_recall": 0.95,
            "mean_initial_project_files": 3.0,
            "mean_input_tokens": 50000.0,
            "mean_elapsed_seconds": 40.0,
            "tool_failures": 0,
            "forbidden_skill_hits": 0,
            "forbidden_file_hits": 0,
        }
        candidate = {
            **baseline,
            "mean_score": 98.0,
            "mean_input_tokens": 45000.0,
            "tool_failures": 3,
        }

        accepted = run_ace_context_ab.compare(baseline, candidate)
        self.assertTrue(accepted["accepted"])
        self.assertEqual(accepted["deltas"]["tool_failures"], 3)

        candidate["forbidden_skill_hits"] = 1
        self.assertFalse(run_ace_context_ab.compare(baseline, candidate)["accepted"])
        candidate["forbidden_skill_hits"] = 0
        candidate["successful_runs"] = 41
        self.assertFalse(run_ace_context_ab.compare(baseline, candidate)["accepted"])

    def test_ace_impact_selection_scopes_domain_changes(self):
        cases = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )["cases"]

        podcast = run_ace_context_ab.select_impacted_cases(
            cases, ["podcast-learning/AGENTS.md"]
        )
        self.assertEqual(podcast["case_ids"], ["c_podcast"])
        self.assertFalse(podcast["full_suite"])

        paper_skill = run_ace_context_ab.select_impacted_cases(
            cases, ["ai-learning/skills/paper_analysis/SKILL.md"]
        )
        self.assertEqual(
            paper_skill["case_ids"],
            [
                "a_article_deep_analysis",
                "a_paper_deep_read",
                "a_existing_followup",
                "a_brief_question",
                "a_open_ended_learning_direction",
            ],
        )

        root = run_ace_context_ab.select_impacted_cases(cases, ["AGENTS.md"])
        self.assertTrue(root["full_suite"])
        self.assertEqual(len(root["case_ids"]), len(cases))

        uncovered = run_ace_context_ab.select_impacted_cases(
            cases, ["web-surfing/skills/ai-tech-blog-radar/SKILL.md"]
        )
        self.assertEqual(
            uncovered["uncovered_paths"],
            ["web-surfing/skills/ai-tech-blog-radar/SKILL.md"],
        )

    def test_ace_context_diff_ignores_non_context_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = root / "baseline"
            candidate = root / "candidate"
            for snapshot, agents_text, readme_text in (
                (baseline, "old", "before"),
                (candidate, "new", "after"),
            ):
                agents = snapshot / "podcast-learning" / "AGENTS.md"
                agents.parent.mkdir(parents=True)
                agents.write_text(agents_text, encoding="utf-8")
                (snapshot / "README.md").write_text(readme_text, encoding="utf-8")

            changed = run_ace_context_ab.changed_behavior_context_paths(
                baseline, candidate
            )

        self.assertEqual(changed, ["podcast-learning/AGENTS.md"])

    def test_ecommit_rejects_options_that_change_the_index_after_gate(self):
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts" / "ecommit.sh"), "--all", "--dry-run"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 2)
        self.assertIn("改变待提交内容", proc.stderr)

    def test_precommit_blocks_mutating_an_archived_policy(self):
        archived = "config/report-quality-policies/report-quality-2026-10-15-r1.json"
        with mock.patch.object(
            precommit_quality,
            "git_paths",
            side_effect=[{archived}, set(), {archived}],
        ), mock.patch("sys.stderr", new=io.StringIO()):
            self.assertEqual(precommit_quality.main(), 1)

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

    def test_open_ended_learning_case_requires_one_clarification(self):
        template = eval_report_context.run_template()
        suite = json.loads(
            (ROOT / "evals" / "ace-report-tasks.json").read_text(encoding="utf-8")
        )
        expected = {case["id"]: case for case in suite["cases"]}
        for case in template["cases"]:
            complete_behavioral_case(case, expected[case["id"]])
        target = next(
            case for case in template["cases"]
            if case["id"] == "a_open_ended_learning_direction"
        )
        target["paused_before_research"] = False
        target["clarification_count"] = 0

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            path.write_text(json.dumps(template, ensure_ascii=False), encoding="utf-8")
            result = eval_report_context.score_run(path)

        row = next(
            case for case in result["cases"]
            if case["id"] == "a_open_ended_learning_direction"
        )
        self.assertFalse(row["checks"]["initiative"])
        self.assertEqual(row["score"], 90)

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

    def test_cross_model_sampling_status_preserves_scarce_reviewer(self):
        status = report_quality.cross_model_sampling_status()

        self.assertEqual(status["interval"], 5)
        self.assertEqual(status["pending_same_model_reports"], 3)
        self.assertFalse(status["sample_due"])
        self.assertIn("PuRo-2B", status["recommended_report"])
        self.assertEqual(status["recommended_reviewers"][0], "gpt-5.6-sol")

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
