import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import eval_report_context
import precommit_quality


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
        self.assertEqual(command[:4], [sys.executable, "scripts/audit_reports.py", "--all", "--summary-only"])
        self.assertEqual(command[4:], [f"--changed-path={path}" for path in sorted(paths)])


if __name__ == "__main__":
    unittest.main()
