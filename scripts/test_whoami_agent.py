"""Agent identity evidence and compatibility, without reading real user state."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).with_name("whoami_agent.py")
SPEC = importlib.util.spec_from_file_location("whoami_test", SOURCE)
whoami = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(whoami)


class IdentityTests(unittest.TestCase):
    def test_runtime_model_precedes_default(self):
        with patch.dict(os.environ, {"CODEX_MODEL": "runtime-model"}, clear=True), patch.object(
            whoami, "_toml_get", return_value="default-model"
        ) as read_config:
            value = whoami.model_evidence("codex")
        self.assertEqual(value["model"], "runtime-model")
        self.assertTrue(value["current_model_confirmed"])
        read_config.assert_not_called()

    def test_default_is_a_hint(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            whoami, "_toml_get", return_value="default-model"
        ):
            value = whoami.model_evidence("codex")
        self.assertEqual(value["confidence"], "configured")
        self.assertFalse(value["current_model_confirmed"])

    def test_nearest_cli_wins_over_inherited_environment(self):
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "inherited"}, clear=True), patch.object(
            whoami, "_process_ancestors", return_value=["python3", "pi", "codex"]
        ):
            self.assertEqual(whoami._detect_cli(), ("pi", "process-ancestry"))

    def test_short_names_do_not_match_other_programs(self):
        with patch.object(whoami, "_process_ancestors", return_value=["pip", "spotify"]):
            self.assertFalse(whoami._proc_has("pi"))

    def test_windows_other_processes_do_not_resolve_a_broken_chain(self):
        with patch.object(whoami.os, "name", "nt"), patch.object(whoami, "_ANCESTORS", None), patch.object(
            whoami, "_win_scan", return_value=(["bash.exe"], ["kimi.exe"], False)
        ):
            self.assertFalse(whoami._proc_has("kimi"))

    def test_environment_without_process_match_is_supported(self):
        with patch.dict(os.environ, {"PI_CODING_AGENT": "true"}, clear=True), patch.object(
            whoami, "_process_ancestors", return_value=[]
        ):
            self.assertEqual(whoami._detect_cli(), ("pi", "runtime-environment"))

    def test_codex_home_alone_is_not_cli_evidence(self):
        with patch.dict(os.environ, {"CODEX_HOME": "/example"}, clear=True), patch.object(
            whoami, "_process_ancestors", return_value=[]
        ):
            self.assertEqual(whoami._detect_cli()[0], None)

    def test_explicit_override_rejects_newlines(self):
        with patch.dict(os.environ, {"AGENT_ID": "agent-model\ninjected"}, clear=True):
            self.assertFalse(whoami.inspect_identity()["resolved"])

    def test_nested_toml_model_is_not_a_default(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.toml"
            path.write_text('[profiles.other]\nmodel = "other"\n')
            self.assertIsNone(whoami._toml_get(path, "model"))

    def test_legacy_and_structured_cli_agree(self):
        env = {**os.environ, "AGENT_ID": "test-model", "AGENT_EMAIL": "noreply@example.com"}
        def run(*args):
            return subprocess.run([sys.executable, str(SOURCE), *args], env=env,
                                  capture_output=True, text=True, check=True).stdout.strip()
        value = json.loads(run("--json"))
        self.assertEqual(run("--name"), value["name"])
        self.assertEqual(run("--email"), value["email"])
        self.assertEqual(run("--git-ident"), value["name"] + "\t" + value["email"])


if __name__ == "__main__":
    unittest.main()
