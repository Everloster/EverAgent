import tempfile
import unittest
from pathlib import Path


class TaskStateRoundTripTests(unittest.TestCase):
    def test_parse_and_write_roundtrip(self) -> None:
        # Import from scripts/ without requiring a package install.
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        sys.path.insert(0, str(scripts_dir))
        import task_state  # type: ignore

        content = (
            "- id: T999\n"
            "  project: ai-learning\n"
            "  type: paper_analysis\n"
            "  target: \"Demo (2026)\"\n"
            "  priority: P2\n"
            "  required_capability: task_executor\n"
            "  status: open\n"
            "  claimed_by: null\n"
            "  claimed_at: null\n"
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".project-task-state"
            path.write_text(content, encoding="utf-8")
            tasks = task_state.parse_task_state_file(path, default_project="ai-learning")
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].id, "T999")
            self.assertEqual(tasks[0].status, "open")

            # Write it back and ensure it's still parseable.
            task_state.write_task_state_file(path, tasks)
            tasks2 = task_state.parse_task_state_file(path, default_project="ai-learning")
            self.assertEqual(tasks2[0].id, "T999")


if __name__ == "__main__":
    unittest.main()

