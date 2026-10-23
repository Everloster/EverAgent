"""Portable core contracts. Only fixtures are read; no real session/model declarations."""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core_bootstrap  # noqa: E402,F401
from everagent_core import apps, catalog, devices, session  # noqa: E402
from everagent_core.identity import declarations, models, processes, core  # noqa: E402

SCOPE = {"harness": "codex", "process_ref": "fixture-process", "session_ref": "fixture-session"}


class ModelDeclarationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-model-fixture-")
        self.scope = patch.object(declarations, "caller_scope", return_value=SCOPE)
        self.scope.start()
        self.env = patch.dict(os.environ, {"EVERAGENT_MODEL_DECLARATION": str(Path(self.temp.name) / "receipt.json")}, clear=True)
        self.env.start()
        self.hint = patch.object(models, "configuration_hint", return_value={
            "model": "configured", "source": "config-default", "confidence": "configured"})
        self.hint.start()

    def tearDown(self):
        self.hint.stop()
        self.env.stop()
        self.scope.stop()
        self.temp.cleanup()

    def declare(self, confirmed=True):
        return declarations.declare_model("codex", "user-model", user_confirmed=confirmed,
                                         hint=models.hint_fingerprint("codex"))

    def test_declaration_requires_explicit_user_confirmation(self):
        with self.assertRaises(ValueError):
            self.declare(False)
        self.assertFalse((Path(self.temp.name) / "receipt.json").exists())

    def test_declared_is_distinct_from_runtime_verified(self):
        self.declare()
        value = models.model_evidence("codex")
        self.assertEqual(value["model"], "user-model")
        self.assertTrue(value["user_model_declared"])
        self.assertFalse(value["current_model_confirmed"])

    def test_other_process_or_session_cannot_reuse_the_declaration(self):
        self.declare()
        for key in ("process_ref", "session_ref", "harness"):
            with patch.object(declarations, "caller_scope", return_value={**SCOPE, key: "other"}):
                self.assertFalse(models.model_evidence("codex")["user_model_declared"])

    def test_hint_switch_invalidates_declaration(self):
        self.declare()
        with patch.object(models, "configuration_hint", return_value={
            "model": "changed", "source": "config-default", "confidence": "configured"}):
            self.assertFalse(models.model_evidence("codex")["user_model_declared"])

    def test_expired_or_tampered_record_is_not_accepted(self):
        self.declare()
        path = Path(self.temp.name) / "receipt.json"
        value = json.loads(path.read_text())
        value["model"] = "tampered"
        path.write_text(json.dumps(value))
        self.assertIsNone(declarations.read_declaration("codex", hint=models.hint_fingerprint("codex")))
        self.declare()
        self.assertIsNone(declarations.read_declaration("codex", hint=models.hint_fingerprint("codex"), now=time.time() + 50000))

    def test_native_model_observation_requires_exact_scope_and_freshness(self):
        value = {"harness": "codex", "scope": SCOPE, "source": "codex-turn-context",
                 "observed_at": time.time(), "model": "observed"}
        self.assertTrue(models.model_evidence("codex", observation=value)["current_model_confirmed"])
        for changed in ({"scope": {**SCOPE, "process_ref": "other"}}, {"observed_at": 0}, {"source": "env"}):
            self.assertFalse(models.model_evidence("codex", observation={**value, **changed})["current_model_confirmed"])


class SessionContracts(unittest.TestCase):
    def test_generic_environment_never_confirms_nested_agent_model(self):
        with patch.dict(os.environ, {"AGENT_MODEL": "outer-model"}, clear=True):
            value = models.model_evidence("pi")
        self.assertFalse(value["current_model_confirmed"])

    def test_missing_windows_home_is_truthful_unknown(self):
        with patch.object(models, "HOME", None), patch.dict(os.environ, {}, clear=True), patch.object(
                declarations, "caller_scope", return_value=None):
            self.assertEqual(models.model_evidence("kimi-desktop")["model"], "unknown")

    def test_kimi_desktop_and_cli_are_distinct(self):
        with patch.object(processes, "process_chain", return_value=[{"name": "Kimi"}]), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(core._detect_cli()[0], "kimi-desktop")
        with patch.object(processes, "process_chain", return_value=[{"name": "kimi"}]), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(core._detect_cli()[0], "kimi-cli")
        with patch.object(models, "_toml_get") as config, patch.dict(os.environ, {}, clear=True):
            models.model_evidence("kimi-desktop")
            config.assert_not_called()

    def test_desktop_host_comes_from_caller_image(self):
        for app_id, app in apps.DESKTOP_APPS.items():
            with patch.object(processes, "process_chain", return_value=[
                    {"name": app["name"], "image": "/fixture/" + app["name"] + ".app/Contents/MacOS/" + app["name"]}]):
                self.assertEqual(apps.inspect_host()["id"], app_id)

    def test_windows_kimi_uses_product_path_not_case(self):
        desktop = {"name": "kimi.exe", "image": "C:/Users/fixture/AppData/Local/Programs/Kimi/kimi.exe"}
        cli = {"name": "Kimi.exe", "image": "C:/Users/fixture/.local/bin/Kimi.exe"}
        ambiguous = {"name": "Kimi.exe", "image": "C:/unknown/Kimi.exe"}
        with patch.object(processes.os, "name", "nt"), patch.dict(os.environ, {}, clear=True):
            for row, expected in ((desktop, "kimi-desktop"), (cli, "kimi-cli"), (ambiguous, None)):
                with patch.object(processes, "process_chain", return_value=[row]):
                    self.assertEqual(core._detect_cli()[0], expected)
        self.assertEqual(apps.app_for_process(desktop, windows=True), "kimi-desktop")
        self.assertIsNone(apps.app_for_process(cli, windows=True))

    def test_windows_desktop_product_and_executable_can_omit_spaces(self):
        row = {"name": "MiniMaxCode.exe", "image": "C:/fixture/MiniMaxCode/MiniMaxCode.exe"}
        self.assertEqual(apps.app_for_process(row, windows=True), "minimax-code")
        self.assertIsNone(apps.app_for_process({**row, "image": "C:/unknown/MiniMaxCode.exe"}, windows=True))

    def test_desktop_without_native_session_cannot_share_declaration_across_shells(self):
        rows = [{"pid": 10, "name": "powershell.exe", "started": "shell-start"},
                {"pid": 20, "name": "Kimi", "started": "desktop-start"}]
        with patch.dict(os.environ, {}, clear=True), patch.object(processes, "caller_anchor", return_value="app-anchor"), patch.object(
            processes, "process_chain", return_value=rows
        ):
            scope = declarations.caller_scope("kimi-desktop")
        self.assertIn("execution_ref", scope)
        with patch.dict(os.environ, {}, clear=True), patch.object(processes, "caller_anchor", return_value="app-anchor"), patch.object(
            processes, "process_chain", return_value=[rows[-1]]
        ):
            self.assertIsNone(declarations.caller_scope("kimi-desktop"))

    def test_desktop_cannot_borrow_its_launch_shell_or_terminal(self):
        rows = [{"pid": 20, "name": "Kimi", "started": "desktop-start"},
                {"pid": 30, "name": "zsh", "started": "persistent-launch-shell"}]
        with patch.dict(os.environ, {"ORCA_TERMINAL_HANDLE": "outer-terminal"}, clear=True), patch.object(
            processes, "process_chain", return_value=rows
        ):
            self.assertIsNone(declarations.caller_scope("kimi-desktop"))
        rows.insert(0, {"pid": 10, "name": "powershell.exe", "started": "execution-shell"})
        with patch.dict(os.environ, {"ORCA_TERMINAL_HANDLE": "outer-terminal"}, clear=True), patch.object(
            processes, "process_chain", return_value=rows
        ):
            self.assertIn("execution_ref", declarations.caller_scope("kimi-desktop"))

    def test_nested_harness_cannot_borrow_outer_process_creation_identity(self):
        rows = [{"pid": 10, "name": "codex", "started": None},
                {"pid": 20, "name": "codex", "started": "outer-start"}]
        with patch.object(processes, "process_chain", return_value=rows):
            self.assertIsNone(processes.caller_anchor("codex"))

    def test_inspection_refreshes_a_previous_caller_cache(self):
        stale = [{"pid": 20, "name": "codex", "started": "old-caller"}]
        fresh = [{"pid": 10, "name": "pi", "started": "current-caller"}]
        with patch.object(processes, "_CHAIN", stale), patch.object(
            processes, "process_chain", side_effect=lambda: fresh if processes._CHAIN is None else stale
        ), patch.dict(os.environ, {}, clear=True):
            self.assertEqual(core.inspect_identity()["cli"], "pi")

    def test_cowork_declaration_binds_its_claude_process(self):
        with patch.object(processes, "process_chain", return_value=[
            {"pid": 10, "name": "claude", "started": "current-caller"}
        ]):
            self.assertIsNotNone(processes.caller_anchor("cowork"))

    def test_platform_and_assertion_are_required_for_registry_match(self):
        row = {"id": "fixture", "platform": "windows", "computername": ["fixture"], "hostname_regex": "^fixture$"}
        self.assertIsNone(devices.match_device([row], ("fixture", "fixture", "linux")))
        self.assertIsNone(devices.match_device([row], ("fixture", "fixture", "windows"), expected="another"))

    def test_disconnected_runtime_and_checkout_mismatch_are_visible(self):
        agent = {"resolved": True, "harness_resolved": True, "model": "model",
                 "model_source": "user-declared", "model_confidence": "declared",
                 "user_model_declared": True, "declaration": {"id": "a" * 64}}
        value = session.normalize(device={"known": True}, agent=agent, checkout={"status": "ok"},
                                  runtime={"kind": "orca", "status": "disconnected-or-orphaned",
                                           "verified": False, "workspace_matches_runtime": False},
                                  caller={})
        self.assertEqual(value["status"], "partial")
        self.assertFalse(value["readiness"]["commit"])

    def test_catalog_rejects_duplicate_alias_and_missing_owner(self):
        root = Path(__file__).resolve().parents[1]
        value = catalog.load_catalog(root / "scripts/script-catalog.json")
        self.assertEqual(catalog.validate_catalog(value, roots={"EverAgent": root}), [])
        duplicate = copy.deepcopy(value)
        duplicate["scripts"][1]["aliases"].append({"path": value["scripts"][0]["entrypoint"], "description": "duplicate"})
        self.assertTrue(catalog.validate_catalog(duplicate, roots={"EverAgent": root}))
        missing = copy.deepcopy(value)
        missing["scripts"][0]["owner"]["path"] = "missing.py"
        self.assertTrue(catalog.validate_catalog(missing, roots={"EverAgent": root}))


class ZcodeModelObservationTests(unittest.TestCase):
    """ZCode has no env session key; the conversation tag rides in the shell args."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-zcode-fixture-")
        self.home = Path(self.temp.name)
        now = time.time()
        self.now = now
        # The CLI process starts when the conversation opens, before any request.
        owner_started = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(now - 900))
        self.chain = [
            {"pid": 901, "parent": 902, "name": "python3", "started": owner_started, "image": "python3"},
            {"pid": 902, "parent": 903, "name": "zsh", "started": owner_started, "image": "/bin/zsh"},
            {"pid": 903, "parent": 904, "name": "zcode-cli", "started": owner_started, "image": "/fixture/zcode-cli"},
            {"pid": 904, "parent": 1, "name": "zcode-host-local-1", "started": owner_started, "image": "/fixture/zcode-host"},
        ]
        self.scope = {"harness": "zcode", "process_ref": "fixture", "execution_ref": "fixture-shell"}
        self.args = ("/bin/zsh -c . '/fixture/.zcode/cli/exec/bash-startup/sess_fixture-session/"
                     "embedded-search-startup-fixture.sh'\ntrue\n")
        self.rollout = self.home / ".zcode/cli/rollout/model-io-sess_fixture-session.jsonl"
        self.rollout.parent.mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def _iso(when):
        return datetime.fromtimestamp(when, tz=timezone.utc).isoformat().replace("+00:00", "Z")

    def _record(self, completed_at, model="GLM-5.3", request_id="req-fixture-1", body_bytes=64):
        prefix = ('{"completedAt":"%s","durationMs":1234,"requestId":"%s","attempt":1,'
                  '"model":{"modelId":"%s","providerId":"fixture"}' % (completed_at, request_id, model))
        return (prefix + ',"request":{"body":{"filler":"' + "x" * body_bytes + '"}}}\n').encode()

    def _collect(self, owner_row=None, scope=None):
        patches = [
            patch.dict(os.environ, {}, clear=True),
            patch.object(processes, "process_chain", return_value=self.chain),
            patch.object(processes, "caller_process", return_value=owner_row or self.chain[2]),
            patch.object(declarations, "safe_home", return_value=self.home),
            patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, stdout=self.args)),
        ]
        with patches[0], patches[1], patches[2], patches[3], patches[4]:
            import everagent_core.identity.observations as observations
            return observations.collect("zcode", scope if scope is not None else self.scope)

    def test_observation_binds_execution_shell_and_current_conversation(self):
        self.rollout.write_bytes(self._record(self._iso(self.now - 600), request_id="req-old")
                                 + self._record(self._iso(self.now - 30), request_id="req-new", body_bytes=200000))
        observation = self._collect()
        self.assertIsNotNone(observation)
        self.assertEqual(observation["model"], "GLM-5.3")
        self.assertEqual(observation["source"], "zcode-model-io")
        self.assertEqual(observation["scope"], self.scope)
        with patch.object(declarations, "caller_scope", return_value=self.scope):
            evidence = models.model_evidence("zcode", observation=observation)
        self.assertTrue(evidence["current_model_confirmed"])
        self.assertEqual(evidence["model"], "GLM-5.3")

    def test_hook_wrapper_shells_do_not_hide_the_tagged_execution_shell(self):
        self.rollout.write_bytes(self._record(self._iso(self.now - 30)))
        hook_chain = [
            {"pid": 901, "parent": 905, "name": "python3", "started": self.chain[0]["started"], "image": "python3"},
            # sh runs the pre-commit hook; its command line carries no conversation tag.
            {"pid": 905, "parent": 902, "name": "sh", "started": self.chain[1]["started"], "image": "/bin/sh"},
            {"pid": 902, "parent": 903, "name": "zsh", "started": self.chain[1]["started"], "image": "/bin/zsh"},
            self.chain[2], self.chain[3],
        ]
        by_pid = {902: self.args, 905: "/bin/sh /repo/.git/hooks/pre-commit\n"}
        def fake_run(command, **kwargs):
            pid = int(command[-1])
            return subprocess.CompletedProcess(command, 0, stdout=by_pid.get(pid, ""))
        with patch.dict(os.environ, {}, clear=True), \
                patch.object(processes, "process_chain", return_value=hook_chain), \
                patch.object(processes, "caller_process", return_value=hook_chain[3]), \
                patch.object(declarations, "safe_home", return_value=self.home), \
                patch("subprocess.run", side_effect=fake_run):
            import everagent_core.identity.observations as observations
            observation = observations.collect("zcode", self.scope)
        self.assertIsNotNone(observation)
        self.assertEqual(observation["model"], "GLM-5.3")

    def test_stale_records_or_files_do_not_verify(self):
        self.rollout.write_bytes(self._record(self._iso(self.now - 400)))
        self.assertIsNone(self._collect())
        self.rollout.write_bytes(self._record(self._iso(self.now - 30)))
        os.utime(self.rollout, (self.now - 400, self.now - 400))
        self.assertIsNone(self._collect())

    def test_foreign_conversation_or_missing_shell_tag_does_not_verify(self):
        self.rollout.write_bytes(self._record(self._iso(self.now - 30)))
        with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, stdout="/bin/zsh -c true\n")):
            import everagent_core.identity.observations as observations
            with patch.object(processes, "process_chain", return_value=self.chain), \
                    patch.object(processes, "caller_process", return_value=self.chain[2]), \
                    patch.object(declarations, "safe_home", return_value=self.home), \
                    patch.dict(os.environ, {}, clear=True):
                self.assertIsNone(observations.collect("zcode", self.scope))
        scope_without_shell = {k: v for k, v in self.scope.items() if k != "execution_ref"}
        self.assertIsNone(self._collect(scope=scope_without_shell))

    def test_owner_must_be_the_session_cli_not_the_resident_host(self):
        self.rollout.write_bytes(self._record(self._iso(self.now - 30)))
        self.assertIsNone(self._collect(owner_row=self.chain[3]))

    def test_unusable_newest_request_does_not_borrow_an_older_model(self):
        self.rollout.write_bytes(self._record(self._iso(self.now - 90), request_id="req-old")
                                 + self._record(self._iso(self.now - 30), model="unknown", request_id="req-new"))
        self.assertIsNone(self._collect())


if __name__ == "__main__":
    unittest.main()
