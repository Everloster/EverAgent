import unittest
from pathlib import Path


class TaskBoardViewSmokeTests(unittest.TestCase):
    def test_generate_view_smoke(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        sys.path.insert(0, str(scripts_dir))
        import task_board_aggregator  # type: ignore
        import task_state  # type: ignore

        tasks = task_state.load_all_tasks(include_global=True)
        stats = task_board_aggregator.generate_project_stats()
        view = task_board_aggregator.generate_task_board_view(tasks, stats)
        self.assertIn("# Learning Projects Task Board", view)
        self.assertIn("## 任务队列", view)

    def test_catalog_entries_come_from_registry(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        sys.path.insert(0, str(scripts_dir))
        import task_board_aggregator  # type: ignore

        entries = task_board_aggregator.load_catalog_entries()
        self.assertGreaterEqual(len(entries), 1)
        self.assertTrue(any(entry.project == "ai-learning" for entry in entries))


if __name__ == "__main__":
    unittest.main()
