"""转写传输的公开仓边界与原始回执校验。"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "podcast_artifact_pull", ROOT / "podcast-learning/scripts/podcast_artifact_pull.py"
)
pull = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pull)


class ArtifactPullTests(unittest.TestCase):
    def setUp(self):
        self.private = tempfile.TemporaryDirectory()
        self.addCleanup(self.private.cleanup)
        self.payload = ("[00:01] 一段转写。\n" * 20000).encode()
        self.output = Path(self.private.name) / "episode.transcript.txt"
        self.args = argparse.Namespace(
            remote_path="/private/artifacts/episode.txt", device="test-device",
            sha256=hashlib.sha256(self.payload).hexdigest(), size=len(self.payload),
            request_id="req_transcript_test", timeout=60, output=str(self.output),
        )

    def transfer(self, argv, **kwargs):
        self.assertEqual(argv[:3], ["/bin/eacli", "file", "pull"])
        self.assertEqual(argv[argv.index("--request-id") + 1], self.args.request_id)
        self.output.write_bytes(self.payload)
        return subprocess.CompletedProcess(argv, 0, json.dumps(
            {"ok": True, "result": {"status": "verified", "resumed_bytes": 128}}
        ), "")

    def test_large_artifact_and_idempotent_reuse(self):
        with patch.object(pull.shutil, "which", return_value="/bin/eacli"), \
             patch.object(pull.subprocess, "run", side_effect=self.transfer) as run, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(pull.pull_artifact(self.args), 0)
            self.assertEqual(pull.pull_artifact(self.args), 0)
        self.assertEqual(run.call_count, 1)
        self.assertIn('"duplicate": true', output.getvalue())

    def test_verified_transfer_still_checks_original_receipt_size(self):
        self.args.size += 1
        with patch.object(pull.shutil, "which", return_value="/bin/eacli"), \
             patch.object(pull.subprocess, "run", side_effect=self.transfer):
            with self.assertRaisesRegex(pull.PullError, "original artifact receipt"):
                pull.pull_artifact(self.args)

    def test_destination_cannot_enter_public_repo_through_symlink(self):
        alias = Path(self.private.name) / "repo"
        alias.symlink_to(ROOT, target_is_directory=True)
        self.args.output = str(alias / "should-not-be-created.txt")
        with patch.object(pull.subprocess, "run") as run:
            with self.assertRaisesRegex(pull.PullError, "outside the public repository"):
                pull.pull_artifact(self.args)
        run.assert_not_called()

    def test_existing_different_file_is_preserved(self):
        self.output.write_bytes(b"unrelated private document")
        with patch.object(pull.subprocess, "run") as run:
            with self.assertRaisesRegex(pull.PullError, "differs"):
                pull.pull_artifact(self.args)
        run.assert_not_called()
        self.assertEqual(self.output.read_bytes(), b"unrelated private document")

    def test_partial_receipt_is_not_accepted_as_complete(self):
        receipt = subprocess.CompletedProcess([], 0, json.dumps(
            {"ok": True, "result": {"status": "partial"}}
        ), "")
        with patch.object(pull.shutil, "which", return_value="/bin/eacli"), \
             patch.object(pull.subprocess, "run", return_value=receipt):
            with self.assertRaisesRegex(pull.PullError, "transfer-unverified"):
                pull.pull_artifact(self.args)


if __name__ == "__main__":
    unittest.main()
