"""The Git validator consumes current evidence rather than stale Git configuration."""
import argparse
import importlib.util
import io
import os
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("git_identity_test", Path(__file__).with_name("git_identity.py"))
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)


class GitIdentityTests(unittest.TestCase):
    def test_unresolved_json_does_not_return_a_vendor_email(self):
        result = SimpleNamespace(returncode=0, stdout='{"resolved":false,"email":"noreply@example.com"}')
        with patch.object(identity.subprocess, "run", return_value=result):
            self.assertIsNone(identity._whoami_email())

    def test_stale_git_name_does_not_allow_unknown_current_agent(self):
        with patch.object(identity, "_whoami_identity", return_value={"resolved": False}) as owner, patch.object(
            identity, "read_git_config", side_effect=lambda key: "previous-model" if key.endswith("name") else "noreply@example.com"
        ), patch.object(identity, "read_author_ident", return_value=identity.expected_author()), patch.dict(
            os.environ, {}, clear=True
        ), redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
            result = identity.command_validate(argparse.Namespace(name=None, email=None))
        self.assertEqual(result, 1)
        owner.assert_called_once()

    def test_current_identity_uses_one_query(self):
        with patch.object(identity, "_whoami_identity", return_value={
            "resolved": True, "name": "fixture-model", "email": "noreply@example.com"
            , "model": "fixture-model", "model_source": "user-declared",
            "model_confidence": "declared", "user_model_declared": True,
            "declaration": {"id": "a" * 64}
        }) as owner, patch.object(identity, "read_git_config", side_effect=lambda key: (
            "fixture-model" if key.endswith("name") else "noreply@example.com"
        )), patch.object(identity, "read_author_ident", return_value=identity.expected_author()), patch.dict(
            os.environ, {}, clear=True
        ), redirect_stdout(io.StringIO()):
            self.assertEqual(identity.command_validate(argparse.Namespace(name=None, email=None)), 0)
        owner.assert_called_once()


if __name__ == "__main__":
    unittest.main()
