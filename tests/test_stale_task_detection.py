import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


class StaleTaskDetectionTests(unittest.TestCase):
    def test_find_stale_tasks_filters_active_and_expired(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        sys.path.insert(0, str(scripts_dir))
        import task_state  # type: ignore

        now = datetime.now(timezone.utc)
        old = (now - timedelta(hours=80)).isoformat(timespec="seconds")
        fresh = (now - timedelta(hours=2)).isoformat(timespec="seconds")

        stale_task = task_state.TaskEntry(
            id="T-stale",
            project="ai-learning",
            type="paper_analysis",
            target="Old Task",
            status="claimed",
            claimed_at=old,
        )
        fresh_task = task_state.TaskEntry(
            id="T-fresh",
            project="ai-learning",
            type="paper_analysis",
            target="Fresh Task",
            status="in_progress",
            started_at=fresh,
        )
        done_task = task_state.TaskEntry(
            id="T-done",
            project="ai-learning",
            type="paper_analysis",
            target="Done Task",
            status="done",
            done_at=fresh,
        )

        with patch.object(task_state, "load_all_tasks", return_value=[stale_task, fresh_task, done_task]):
            stale = task_state.find_stale_tasks(ttl_hours=72)

        self.assertEqual([task.id for task in stale], ["T-stale"])


if __name__ == "__main__":
    unittest.main()

