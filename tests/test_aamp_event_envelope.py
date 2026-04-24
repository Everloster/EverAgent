import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class AampEventEnvelopeTests(unittest.TestCase):
    def test_task_done_event_roundtrips_aamp_envelope(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        scripts_dir = repo_root / "scripts"
        import sys

        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))

        import ea_events  # type: ignore

        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(ea_events, "EVENTS_DIR", Path(tmp)):
                emitted = ea_events.emit_event(
                    event_type="task_done",
                    actor="NeuronAgent",
                    project="ai-learning",
                    task_id="T999",
                    payload={"target": "Demo"},
                )
                self.assertEqual(emitted.aamp["intent"], "task.result")
                self.assertEqual(emitted.aamp["status"], "completed")
                self.assertTrue(emitted.message_id.startswith("<evt_"))

                loaded = ea_events.load_events(task_id="T999")
                self.assertEqual(len(loaded), 1)
                self.assertEqual(loaded[0].aamp["intent"], "task.result")
                self.assertEqual(loaded[0].aamp["status"], "completed")
                self.assertEqual(loaded[0].message_id, emitted.message_id)


if __name__ == "__main__":
    unittest.main()
