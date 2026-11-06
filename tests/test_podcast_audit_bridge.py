"""播客来源审计、统一入口与私有收据的离线回归。"""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_reports
import report_catalog

transcripts = audit_reports.podcast_audit


class PodcastAuditBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tests")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.reports = self.root / "podcast-learning/reports"
        self.sources = self.reports / "transcripts"
        self.sources.mkdir(parents=True)
        for module in (audit_reports, report_catalog):
            patch = mock.patch.object(module, "ROOT", self.root)
            patch.start()
            self.addCleanup(patch.stop)

    def write_source(self, content=None):
        path = self.sources / "fixture.transcript.txt"
        path.write_text(content or "[00:00:00 -> 00:00:02] 原始内容\n[00:00:02 -> 00:00:04] 第二段\n", encoding="utf-8")
        return path

    def write_report(self, fields="", body=""):
        path = self.reports / "2001-01-01_fixture.md"
        path.write_text(f'''---
title: 测试报告
domain: podcast-learning
report_type: episode_summary
status: completed
updated_on: 2001-01-01
semantic_tags: [test]
{fields}
---
# 测试报告
来源：https://example.org/episode
{body}
''', encoding="utf-8")
        return path

    def findings(self, report, changed=()):
        result = audit_reports.audit([report], strict_all=False, new_paths=set(), changed_paths=set(changed))
        return result["issues"]

    def test_timestamps_and_repeats_do_not_depend_on_duration_field(self):
        source = self.write_source("[00:00:05 -> 00:00:04] 重复\n" + "[00:00:01 -> 00:00:03] 重复\n" * 4)
        report = self.write_report("transcript_path: reports/transcripts/fixture.transcript.txt")
        before = (source.read_bytes(), report.read_bytes())
        legacy = [x for x in self.findings(report) if x["code"] == "POD102"]
        changed = [x for x in self.findings(report, [report]) if x["code"] == "POD102"]
        self.assertEqual(len(legacy), 3)
        self.assertTrue(all(x["severity"] == "warning" for x in legacy))
        self.assertTrue(all(x["severity"] == "error" for x in changed))
        self.assertEqual(before, (source.read_bytes(), report.read_bytes()))

    def test_changed_and_deleted_source_selects_dependent_report(self):
        source = self.write_source()
        report = self.write_report("transcript_path: reports/transcripts/fixture.transcript.txt")
        self.assertEqual(audit_reports._reports_from_paths({source}), [report])
        source.unlink()
        self.assertEqual(audit_reports._reports_from_paths({source}), [report])
        issues = self.findings(report, [source])
        self.assertTrue(any(x["code"] == "POD101" and x["severity"] == "error" for x in issues))

    def test_receipt_change_selects_dependent_report(self):
        report = self.write_report("transcript_audit_path: reports/transcripts/fixture.audit.json")
        receipt = self.sources / "fixture.audit.json"
        self.assertEqual(audit_reports._reports_from_paths({receipt}), [report])

    def test_unreferenced_transcript_is_checked_without_report(self):
        source = self.write_source("[00:00:03 -> 00:00:01] 原始内容\n")
        result = audit_reports.audit([], strict_all=False, new_paths=set(), changed_paths={source}, source_paths={source})
        self.assertEqual(result["reports_scanned"], 0)
        self.assertTrue(any(x["code"] == "POD102" and x["severity"] == "error" for x in result["issues"]))

    def test_duration_uses_segment_end_and_compression_uses_file_bytes(self):
        raw = self.write_source("[00:00:00 -> 00:02:01] " + "字" * 100 + "\n")
        polished = self.sources / "fixture.polished.txt"
        polished.write_text("字" * 50, encoding="utf-8")
        metadata = {
            "transcript_path": "reports/transcripts/fixture.transcript.txt",
            "polished_transcript_path": "reports/transcripts/fixture.polished.txt",
            "duration_seconds": "121", "hanzi_chars_raw": "100", "hanzi_chars_polished": "100",
        }
        findings = transcripts.audit_report(self.root, metadata, "约 raw 的 100%")
        self.assertIn("POD105", {x[0] for x in findings})
        self.assertNotIn("POD104", {x[0] for x in findings})
        self.assertEqual(transcripts.audit(raw)["duration_seconds"], 121)

    def test_invalid_duration_and_zero_hanzi_do_not_crash(self):
        self.write_source("[00:00:00 -> 00:00:01] English\n")
        polished = self.sources / "fixture.polished.txt"
        polished.write_text("English", encoding="utf-8")
        findings = transcripts.audit_report(self.root, {
            "transcript_path": "reports/transcripts/fixture.transcript.txt",
            "polished_transcript_path": "reports/transcripts/fixture.polished.txt",
            "duration_seconds": "not-a-number",
        }, "约 raw 的 30%")
        self.assertEqual({x[0] for x in findings}, {"POD104", "POD106"})

    def test_report_v2_does_not_require_obsolete_domain_template(self):
        report = self.write_report('quality_schema: report-v2', "## Limitations\n范围\n## 思考与追问\n问题")
        with mock.patch.object(audit_reports, "evaluate_report_quality", return_value={"errors": [], "warnings": []}):
            issues = audit_reports.audit_file(report, enforce=False, wikilinks={})
        self.assertFalse([x for x in issues if x.severity == "error"])
        self.assertFalse(any("notable_correction" in x.message or "速览" in x.message for x in issues))

    def test_qualified_wikilink_requires_path_not_just_basename(self):
        target = self.root / "podcast-learning/wiki/concepts/existing.md"
        target.parent.mkdir(parents=True)
        target.write_text("# 概念\n", encoding="utf-8")
        report = self.write_report(body="[[concepts/existing]] [[other/existing]] [[existing]]")
        issues = [x for x in self.findings(report, [report]) if x["code"] == "LINK002"]
        self.assertEqual(len(issues), 1)
        self.assertIn("other/existing", issues[0]["message"])
        self.assertEqual(issues[0]["severity"], "error")

    def test_new_qualified_link_rule_keeps_versioned_history_as_warning(self):
        target = self.root / "podcast-learning/wiki/concepts/existing.md"
        target.parent.mkdir(parents=True)
        target.write_text("# 概念\n", encoding="utf-8")
        report = self.write_report("quality_schema: report-v1", "[[other/existing]] [[missing]]")
        old = {x["message"]: x["severity"] for x in self.findings(report) if x["code"] == "LINK002"}
        self.assertEqual(old["wikilink 无目标：[[other/existing]]"], "warning")
        self.assertEqual(old["wikilink 无目标：[[missing]]"], "error")
        changed = [x for x in self.findings(report, [report]) if x["code"] == "LINK002"]
        self.assertTrue(all(x["severity"] == "error" for x in changed))

    def test_source_paths_cannot_escape_or_follow_symlink(self):
        outside = self.root / "outside.txt"
        outside.write_text("不得读取", encoding="utf-8")
        link = self.sources / "linked.transcript.txt"
        link.symlink_to(outside)
        for value in ("/private/source.txt", "../source.txt", "reports/transcripts/linked.transcript.txt"):
            with self.assertRaises(ValueError):
                transcripts.source_path(self.root, value)

    def private_fixture(self):
        source = self.write_source()
        result = transcripts.audit(source)
        receipt = transcripts.public_receipt(result, "https://example.org/episode")
        receipt_path = self.sources / "fixture.audit.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        metadata = {
            "transcript_visibility": "private", "transcript_path": "null", "polished_transcript_path": "null",
            "source_url": receipt["source_url"], "transcript_source_ref": receipt["source_ref"],
            "transcript_audit_path": "reports/transcripts/fixture.audit.json",
        }
        return source, receipt_path, receipt, metadata

    def test_private_receipt_is_redacted_and_not_claimed_as_source_reverification(self):
        source, receipt_path, receipt, metadata = self.private_fixture()
        serialized = receipt_path.read_text()
        for private in (str(source), "原始内容", "head", "tail\"", "job_id"):
            self.assertNotIn(private, serialized)
        source.unlink()
        findings = transcripts.audit_report(self.root, metadata, "")
        self.assertEqual([x[0] for x in findings], ["POD109"])
        self.assertTrue(findings[0][2])
        self.assertEqual(transcripts.validate_receipt(receipt, source_ref=receipt["source_ref"], source_url=receipt["source_url"]), [])

    def test_missing_source_url_or_receipt_is_not_verification_success(self):
        _, receipt_path, _, metadata = self.private_fixture()
        metadata.pop("source_url")
        self.assertIn("POD107", {x[0] for x in transcripts.audit_report(self.root, metadata, "")})
        receipt_path.unlink()
        self.assertIn("POD107", {x[0] for x in transcripts.audit_report(self.root, metadata, "")})

    def test_receipt_rejects_private_fields_failed_audit_and_ref_mismatch(self):
        _, _, receipt, _ = self.private_fixture()
        for mutate in (
            lambda item: item.update(path="/private/source"),
            lambda item: item["audit"].update(timestamp_errors=1),
            lambda item: item["audit"].update(segments="two"),
            lambda item: item.update(source_ref="sha256:" + "0" * 64),
            lambda item: item.update(source_url="https://example.org/episode?token=secret"),
        ):
            changed = json.loads(json.dumps(receipt))
            mutate(changed)
            self.assertTrue(transcripts.validate_receipt(changed, source_ref=receipt["source_ref"], source_url=receipt["source_url"]))

    def test_receipt_compares_against_source_when_available(self):
        source, _, _, metadata = self.private_fixture()
        metadata.pop("transcript_visibility")
        metadata["transcript_path"] = "reports/transcripts/fixture.transcript.txt"
        source.write_text("[00:00:00 -> 00:00:05] 变化\n", encoding="utf-8")
        self.assertIn("POD108", {x[0] for x in transcripts.audit_report(self.root, metadata, "")})

    def test_public_cli_requires_real_file_and_never_writes_source(self):
        source = self.write_source()
        before = source.read_bytes()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), mock.patch.object(Path, "write_text", side_effect=AssertionError("audit wrote a file")):
            code = transcripts.main([str(source), "--public-receipt", "--source-url", "https://example.org/episode"])
        self.assertEqual(code, 0)
        self.assertEqual(before, source.read_bytes())
        self.assertEqual(json.loads(output.getvalue())["schema_version"], 2)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            transcripts.main([str(source) + ".missing", "--public-receipt", "--source-url", "https://example.org/episode"])
        self.assertEqual(error.exception.code, 1)

    def test_snapshot_changed_path_includes_deleted_sources(self):
        source = self.write_source()
        self.write_report("transcript_path: reports/transcripts/fixture.transcript.txt")
        source.unlink()
        output = io.StringIO()
        with mock.patch.object(audit_reports, "_git_paths", return_value=set()), \
             mock.patch.object(audit_reports, "_git_ref", return_value=""), \
             contextlib.redirect_stdout(output):
            code = audit_reports.main(["--all", "--json", "--changed-path", str(source.relative_to(self.root))])
        self.assertEqual(code, 1)
        result = json.loads(output.getvalue())
        self.assertTrue(any(x["code"] == "POD101" and x["severity"] == "error" for x in result["issues"]))

    def test_changed_and_staged_source_reverse_selection(self):
        source = self.write_source()
        report = self.write_report("transcript_path: reports/transcripts/fixture.transcript.txt")
        def git_paths(command):
            return {source} if "--diff-filter=ACDMRTUXB" in command else set()
        with mock.patch.object(audit_reports, "_git_paths", side_effect=git_paths), \
                mock.patch.object(audit_reports, "new_report_paths", return_value=set()):
            for select in (audit_reports.changed_reports, audit_reports.staged_reports):
                reports, new = select()
                self.assertEqual(reports, [report])
                self.assertEqual(new, set())

    def test_old_report_alias_is_warning_until_selected_as_changed(self):
        report = self.write_report('quality_schema: report-v2\nreport_type: concept_deep_dive', "## Limitations\n## 思考与追问")
        with mock.patch.object(audit_reports, "evaluate_report_quality", return_value={"errors": [], "warnings": []}):
            legacy = [x for x in self.findings(report) if x["code"] == "META010"]
            changed = [x for x in self.findings(report, [report]) if x["code"] == "META010"]
        self.assertEqual(legacy[0]["severity"], "warning")
        self.assertEqual(changed[0]["severity"], "error")

    def test_evidence_only_transcript_reference_still_audits_source(self):
        source = self.write_source("[00:00:03 -> 00:00:01] 原始内容\n")
        report = self.write_report()
        quality = self.reports / ".quality"
        quality.mkdir()
        (quality / f"{report.stem}.evidence.json").write_text(json.dumps({"sources": [{
            "kind": "local", "locator": str(source.relative_to(self.root)),
        }]}), encoding="utf-8")
        self.assertEqual(audit_reports._reports_from_paths({source}), [report])
        for changed in (report, quality / f"{report.stem}.evidence.json"):
            issues = self.findings(report, [changed])
            self.assertTrue(any(x["code"] == "POD102" and x["severity"] == "error" for x in issues))

    def test_deleted_evidence_only_source_fails_but_orphan_deletion_does_not(self):
        source = self.write_source()
        report = self.write_report()
        quality = self.reports / ".quality"
        quality.mkdir()
        (quality / f"{report.stem}.evidence.json").write_text(json.dumps({"sources": [{
            "kind": "local", "locator": str(source.relative_to(self.root)),
        }]}), encoding="utf-8")
        source.unlink()
        old = [x for x in self.findings(report) if x["code"] == "POD101"]
        self.assertEqual(old[0]["severity"], "warning")
        changed = [x for x in self.findings(report, [source]) if x["code"] == "POD101"]
        self.assertEqual(changed[0]["severity"], "error")
        orphan = audit_reports.audit([], strict_all=False, new_paths=set(),
                                     changed_paths={source}, source_paths={source})
        self.assertEqual(orphan["errors"], 0)

    def test_compatibility_entry_rejects_fix(self):
        proc = subprocess.run([sys.executable, str(ROOT / "podcast-learning/scripts/audit_reports.py"), "--fix"], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("只读", proc.stderr)


if __name__ == "__main__":
    unittest.main()
