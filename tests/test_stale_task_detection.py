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

    def test_find_expired_tasks_uses_expires_at(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        import task_state  # type: ignore

        now = datetime.now(timezone.utc)
        past = (now - timedelta(hours=1)).isoformat(timespec="seconds")
        future = (now + timedelta(hours=1)).isoformat(timespec="seconds")
        expired_task = task_state.TaskEntry(
            id="T-expired",
            project="global",
            type="maintenance",
            target="Expired Task",
            expires_at=past,
        )
        future_task = task_state.TaskEntry(
            id="T-future",
            project="global",
            type="maintenance",
            target="Future Task",
            expires_at=future,
        )
        done_task = task_state.TaskEntry(
            id="T-done",
            project="global",
            type="maintenance",
            target="Done Task",
            status="done",
            expires_at=past,
        )

        with patch.object(task_state, "load_all_tasks", return_value=[expired_task, future_task, done_task]):
            expired = task_state.find_expired_tasks()

        self.assertEqual([task.id for task in expired], ["T-expired"])


if __name__ == "__main__":
    unittest.main()
