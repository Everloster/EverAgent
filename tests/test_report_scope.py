"""受影响报告检查不带入无关旧账，也不漏掉来源删除。"""

import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_reports
import report_catalog
import report_quality


class AffectedReportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for module in (audit_reports, report_catalog, report_quality):
            patch = mock.patch.object(module, "ROOT", self.root)
            patch.start()
            self.addCleanup(patch.stop)

    def report(self, name="topic.md", *, body="", domain="ai-learning", fields=""):
        path = self.root / domain / "reports" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"""---
title: {name}
domain: {domain}
report_type: {"episode_summary" if domain == "podcast-learning" else "concept_report"}
status: completed
quality_schema: report-v1
updated_on: 2026-01-01
semantic_tags: [test]
{fields}
---
# {name}
来源：https://example.org/paper
{body}
""", encoding="utf-8")
        return path

    def run_audit(self, paths=(), new_paths=()):
        output = io.StringIO()
        arguments = ["--affected", "--json"]
        arguments += ["--changed-path=" + str(path.relative_to(self.root)) for path in paths]
        arguments += ["--new-path=" + str(path.relative_to(self.root)) for path in new_paths]
        with mock.patch.object(audit_reports, "_git_paths", side_effect=AssertionError("读取了隐含 Git 变更")), \
                contextlib.redirect_stdout(output):
            code = audit_reports.main(arguments)
        return code, json.loads(output.getvalue())

    def test_explicit_scope_ignores_unrelated_broken_reports_and_ambient_changes(self):
        wanted = self.report()
        other = self.report("unrelated.md", fields="quality_schema: report-v2")
        evidence = other.parent / ".quality" / (other.stem + ".evidence.json")
        evidence.parent.mkdir()
        evidence.write_text("损坏且不相关的质量记录", encoding="utf-8")
        code, result = self.run_audit([wanted, self.root / "README.md"])
        self.assertEqual(code, 0, result["issues"])
        self.assertEqual(result["reports_scanned"], 1)
        self.assertFalse(any(item["path"].endswith("unrelated.md") for item in result["issues"]))
        self.assertEqual(self.run_audit()[1]["reports_scanned"], 0)

    def test_all_quality_artifact_kinds_select_owner_including_deleted_artifacts(self):
        report = self.report(fields="quality_schema: report-v2")
        for suffix in ("evidence", "review", "transcription-review"):
            with self.subTest(suffix=suffix):
                artifact = report.parent / ".quality" / f"{report.stem}.{suffix}.json"
                self.assertEqual(audit_reports._reports_from_paths({artifact}), [report])
                code, result = self.run_audit([artifact])
                self.assertEqual(code, 1)
                self.assertEqual(result["reports_scanned"], 1)
                self.assertIn("QG003", result["issue_codes"])

    def test_deleted_relative_source_fails_its_reader_not_unrelated_reports(self):
        source = self.root / "docs/source notes.txt"
        source.parent.mkdir(parents=True)
        source.write_text("来源", encoding="utf-8")
        report = self.report(body='[来源](../../docs/source%20notes.txt "一手资料")')
        self.report("other.md", fields="quality_schema: report-v2")
        self.assertEqual(self.run_audit([source])[0], 0)
        source.unlink()
        code, result = self.run_audit([source])
        self.assertEqual(code, 1)
        self.assertEqual(result["reports_scanned"], 1)
        self.assertTrue(any(item["code"] == "LINK001" and item["severity"] == "error" for item in result["issues"]))
        self.assertEqual(audit_reports._reports_from_paths({source}), [report])

    def test_changed_or_deleted_report_used_as_source_selects_its_reader(self):
        source = self.report("source.md")
        reader = self.report("reader.md", body="[详细原文](source.md)")
        self.assertEqual(set(audit_reports._reports_from_paths({source})), {source, reader})
        source.unlink()
        code, result = self.run_audit([source])
        self.assertEqual(code, 1)
        self.assertEqual(result["reports_scanned"], 1)
        self.assertIn("LINK001", result["issue_codes"])

    def test_qualified_wikilink_matches_actual_changed_path_even_after_deletion(self):
        target = self.root / "docs/source.md"
        other = self.root / "other/source.md"
        for path in (target, other):
            path.parent.mkdir(parents=True)
            path.write_text("# 原文\n", encoding="utf-8")
        self.report(body="[[docs/source]]")
        self.assertEqual(self.run_audit([other])[1]["reports_scanned"], 0)
        target.unlink()
        code, result = self.run_audit([target])
        self.assertEqual(code, 1)
        self.assertTrue(any(item["code"] == "LINK002" and item["severity"] == "error" for item in result["issues"]))

    def test_local_evidence_source_changes_select_dependent_owner(self):
        report = self.report(fields="quality_schema: report-v2")
        source = self.root / "source.txt"
        evidence = report.parent / ".quality" / (report.stem + ".evidence.json")
        evidence.parent.mkdir()
        evidence.write_text(json.dumps({"sources": [{"kind": "local", "locator": "source.txt"}]}))
        self.assertEqual(audit_reports._reports_from_paths({source}), [report])
        code, result = self.run_audit([source])
        self.assertEqual(code, 1)
        self.assertIn("EVM035", result["issue_codes"])

    def test_new_path_alone_selects_report_and_does_not_allow_unreviewed_draft(self):
        report = self.report(fields="quality_schema: report-v2\nstatus: in_progress\nquality_tier: important")
        code, result = self.run_audit(new_paths=[report])
        self.assertEqual(code, 1)
        self.assertEqual(result["reports_scanned"], 1)
        self.assertIn("META009", result["issue_codes"])

    def test_natural_learning_and_podcast_headings_are_not_format_passwords(self):
        self.report(body="## 结论\n理解、依据和下一步验证自然写在正文里。")
        report = self.report("episode.md", domain="podcast-learning",
                             fields="report_depth: standard\nreader_contract: standalone",
                             body="## 为什么出现分歧\n推导、例子、适用边界和追问按内容组织。")
        code, result = self.run_audit([report])
        self.assertEqual(code, 0, result["issues"])
        self.assertFalse({"POD001", "POD004", "POD005", "LEARN001"} & result["issue_codes"].keys())


class SamplingCommandTests(unittest.TestCase):
    def test_sampling_check_enforces_the_existing_window_without_running_context(self):
        for due, check, expected in ((True, True, 1), (False, True, 0), (True, False, 0)):
            with self.subTest(due=due, check=check), \
                    mock.patch.object(report_quality, "cross_model_sampling_status", return_value={"sample_due": due}), \
                    mock.patch.object(sys, "argv", ["report_quality.py", "sampling-status", "--json"] + (["--check"] if check else [])), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(report_quality.main(), expected)


if __name__ == "__main__":
    unittest.main()
