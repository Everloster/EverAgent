import sys
import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import eval_report_context
import precommit_quality
import audit_reports
import report_catalog


class QualityWiringTests(unittest.TestCase):
    def test_ci_accepts_current_discovery(self):
        text = (ROOT / ".github/workflows/quality.yml").read_text()
        self.assertEqual(eval_report_context.missing_ci_checks(text), [])

    def test_ci_accepts_explicit_legacy_test_modules(self):
        text = "\n".join(("tests.test_report_tooling", "scripts.test_git_commit",
                          "audit_reports.py --all", "reindex.py --check", "eval_report_context.py"))
        self.assertEqual(eval_report_context.missing_ci_checks(text), [])

    def test_ci_rejects_missing_or_narrowed_script_discovery(self):
        text = (ROOT / ".github/workflows/quality.yml").read_text()
        for replacement in ("", "unittest discover -s scripts -p test_git_commit.py"):
            candidate = text.replace("unittest discover -s scripts -p 'test_*.py'", replacement)
            self.assertIn("script tests", eval_report_context.missing_ci_checks(candidate))

    def test_snapshot_receives_deleted_and_unusual_changed_paths(self):
        paths = {"podcast-learning/reports/transcripts/deleted.txt",
                 "podcast-learning/reports/space and\nnewline.md"}
        command = precommit_quality.report_audit_command(paths)
        self.assertEqual(command[:4], [sys.executable, "scripts/audit_reports.py", "--affected", "--summary-only"])
        self.assertEqual(command[4:], [f"--changed-path={path}" for path in sorted(paths)])

    def test_ci_uses_shared_new_report_selection_and_audit_command(self):
        text = (ROOT / ".github/workflows/quality.yml").read_text()
        self.assertIn('new_report_paths(os.environ["AUDIT_BASE"], "HEAD")', text)
        self.assertIn('subprocess.run(report_audit_command(', text)
        self.assertIn("report audit", eval_report_context.missing_ci_checks(
            text.replace("subprocess.run(report_audit_command(", "unused_command(")
        ))

    def test_report_only_change_does_not_run_context_or_full_audit(self):
        paths = {"ai-learning/reports/topic.md", "ai-learning/reports/.quality/topic.review.json",
                 "README.md", "docs/REPORT_INDEX.md"}
        self.assertFalse(precommit_quality.full_report_audit_required(paths))
        self.assertFalse(precommit_quality.context_evaluation_required(paths))
        self.assertTrue(precommit_quality.review_sampling_required(paths))

    def test_sampling_uses_catalog_including_experiments_and_deleted_artifacts(self):
        for path in ("ai-practice/experiments/exp_fixture.md",
                     "ai-practice/experiments/.quality/exp_fixture.review.json",
                     "podcast-learning/reports/.quality/deleted.review.json"):
            self.assertTrue(precommit_quality.review_sampling_required({path}))
        self.assertFalse(precommit_quality.review_sampling_required({"README.md", "docs/REPORT_INDEX.md"}))

    def test_gate_schema_and_context_changes_still_expand_checks(self):
        for path in ("scripts/audit_reports.py", "scripts/report_quality.py", "schemas/report-review-v1.schema.json"):
            self.assertTrue(precommit_quality.full_report_audit_required({path}))
            self.assertIn("--all", precommit_quality.report_audit_command({path}))
        for path in ("AGENTS.md", "ai-learning/skills/paper_analysis/SKILL.md", "docs/REPORT_WORKFLOW.md"):
            self.assertTrue(precommit_quality.context_evaluation_required({path}))


class ReportRenameTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "-q")
        self.git("config", "user.name", "Report fixture")
        self.git("config", "user.email", "fixture@example.org")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.report = self.root / "ai-learning/reports/old.md"
        self.report.parent.mkdir(parents=True)
        self.report.write_text('''---
title: 旧报告
domain: ai-learning
report_type: concept_report
status: completed
updated_on: 2026-01-01
semantic_tags: [test]
quality_schema: report-v1
---
# 旧报告
来源：https://example.org/paper
## 思考与追问
如何验证？
''')
        self.commit()
        for module in (report_catalog, audit_reports):
            patch = mock.patch.object(module, "ROOT", self.root)
            patch.start()
            self.addCleanup(patch.stop)

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.PIPE).decode().strip()

    def commit(self):
        self.git("add", "--all")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "审计测试样本\n\nCo-Authored-By: Aiden")
        return self.git("rev-parse", "HEAD")

    def audit_command(self, added):
        changed = {str(path.relative_to(self.root)) for path in self.root.rglob("*.md")}
        command = precommit_quality.report_audit_command(changed, {str(path.relative_to(self.root)) for path in added})
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = audit_reports.main(command[2:] + ["--json"])
        return code, json.loads(output.getvalue())

    def test_exact_rename_keeps_legacy_contract_in_staging_and_ci(self):
        base = self.git("rev-parse", "HEAD")
        target = self.report.with_name("corrected name.md")
        self.git("config", "diff.renames", "false")
        self.git("mv", str(self.report.relative_to(self.root)), str(target.relative_to(self.root)))
        self.assertEqual(report_catalog.new_report_paths("--cached"), set())
        self.assertEqual(self.audit_command(set())[0], 0)
        self.commit()
        self.assertEqual(report_catalog.new_report_paths(base, "HEAD"), set())
        self.assertEqual(self.audit_command(set())[0], 0)

    def test_copied_report_remains_new_and_must_use_current_contract(self):
        target = self.report.with_name("copy.md")
        target.write_bytes(self.report.read_bytes())
        self.git("add", "--all")
        added = report_catalog.new_report_paths("--cached")
        self.assertEqual(added, {target})
        code, result = self.audit_command(added)
        self.assertEqual(code, 1)
        self.assertTrue(any(item["code"] == "META006" for item in result["issues"]))

    def test_move_into_reports_or_between_domains_is_new(self):
        note = self.root / "docs/note.md"
        note.parent.mkdir()
        note.write_text("# 一份新笔记\n")
        self.commit()
        target = self.report.with_name("from-note.md")
        self.git("mv", "docs/note.md", str(target.relative_to(self.root)))
        other = self.root / "cs-learning/reports/moved.md"
        other.parent.mkdir(parents=True)
        self.git("mv", str(self.report.relative_to(self.root)), str(other.relative_to(self.root)))
        self.assertEqual(report_catalog.new_report_paths("--cached"), {target, other})

    def test_rename_does_not_bypass_existing_contract_errors(self):
        self.report.write_text(self.report.read_text().replace("status: completed", "status: done"))
        self.commit()
        self.git("mv", str(self.report.relative_to(self.root)), "ai-learning/reports/new-name.md")
        self.assertEqual(report_catalog.new_report_paths("--cached"), set())
        code, result = self.audit_command(set())
        self.assertEqual(code, 1)
        self.assertTrue(any(item["code"] == "META005" and item["severity"] == "error" for item in result["issues"]))


if __name__ == "__main__":
    unittest.main()
