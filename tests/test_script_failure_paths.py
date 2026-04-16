import argparse
import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


class ScriptFailurePathTests(unittest.TestCase):
    @staticmethod
    def _load_modules():
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        import execution_validator  # type: ignore
        import project_lock  # type: ignore
        import task_exec  # type: ignore

        return execution_validator, project_lock, task_exec

    def test_task_exec_begin_rejects_project_mismatch(self) -> None:
        _, _, task_exec = self._load_modules()
        fake_task = SimpleNamespace(id="T123", project="ai-learning")
        args = argparse.Namespace(task_id="T123", project="cs-learning", agent="ByteAgent")
        with patch.object(task_exec, "require_task", return_value=fake_task):
            with self.assertRaises(ValueError):
                task_exec.command_begin(args)

    def test_project_lock_release_detects_agent_mismatch(self) -> None:
        _, project_lock, _ = self._load_modules()
        with tempfile.TemporaryDirectory() as tmp:
            lock_path = Path(tmp) / ".agent-lock"
            lock_path.write_text(
                "agent: NeuronAgent\n"
                "task_id: T001\n"
                "claimed_at: 2026-04-16T00:00:00+00:00\n"
                "git_commit_sha: abc\n",
                encoding="utf-8",
            )
            args = argparse.Namespace(
                project="ai-learning",
                task_id="T001",
                agent="ByteAgent",
                force=False,
            )
            with patch.object(project_lock, "lock_path_for_project", return_value=lock_path):
                with contextlib.redirect_stdout(io.StringIO()):
                    code = project_lock.command_release(args)
        self.assertEqual(code, 1)

    def test_execution_validator_reports_missing_task(self) -> None:
        execution_validator, _, _ = self._load_modules()
        result = execution_validator.validate_input_schema("T_DOES_NOT_EXIST", "ai-learning")
        self.assertFalse(result.passed)
        self.assertTrue(any(issue.field == "task_id" for issue in result.issues))


if __name__ == "__main__":
    unittest.main()
