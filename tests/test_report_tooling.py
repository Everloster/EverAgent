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


def load_report_generator():
    path = ROOT / "github-trending-analyzer" / "scripts" / "report_generator.py"
    spec = importlib.util.spec_from_file_location("report_generator", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ReportToolingTests(unittest.TestCase):
    def test_catalog_covers_projects_and_excludes_podcast_sources(self):
        reports = list(report_catalog.iter_reports())
        domains = {collection.id for collection, _path in reports}

        self.assertIn("github-trending-analyzer", domains)
        self.assertIn("web-surfing", domains)
        self.assertIn("ai-practice", domains)
        self.assertFalse(any("transcripts" in path.parts for _collection, path in reports))

    def test_current_report_contract_passes_without_errors(self):
        report = (
            ROOT
            / "ai-learning"
            / "reports"
            / "knowledge_reports"
            / "GPT6_Astra指令架构_从Prompt堆叠到按需控制_深度解析_20261015.md"
        )
        issues = audit_reports.audit_file(
            report,
            enforce=True,
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
            case["route"] = exp["expected_route"]
            case["artifact_created"] = exp["artifact_policy"] != "forbidden"
            case["paused_before_research"] = False
            case["checks_completed"] = exp["required_checks"]
            case["completed"] = True
            case["safety_violation"] = False

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
            case["route"] = exp["expected_route"]
            case["artifact_created"] = exp["artifact_policy"] != "forbidden"
            case["paused_before_research"] = False
            case["checks_completed"] = exp["required_checks"]
            case["completed"] = True

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "run.json"
            path.write_text(json.dumps(template, ensure_ascii=False), encoding="utf-8")
            result = eval_report_context.score_run(path)

        self.assertEqual(result["score"], 0)

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
        self.assertIn('quality_schema: "report-v1"', content)
        self.assertIn('report_type: "repo_deep_research"', content)

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
