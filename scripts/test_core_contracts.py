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
from everagent_core.identity import config, declarations, models, processes, core  # noqa: E402

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


class ReaderConfigurationAndFactsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="everagent-facts-fixture-")
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name).resolve()
        self.path = self.home / "facts.json"
        self.chain = [{"pid": 8, "name": "zsh", "started": "fixture-shell"}]
        for target in (patch.dict(os.environ, {"EVERAGENT_SESSION_DECLARATION": str(self.path),
                        "EVERAGENT_MODEL_DECLARATION": str(self.home / "legacy.json")}, clear=True),
                       patch.object(processes, "process_chain", return_value=self.chain),
                       patch.object(models, "HOME", self.home),
                       patch.object(declarations, "safe_home", return_value=self.home)):
            target.start()
            self.addCleanup(target.stop)

    def override(self, harnesses):
        path = self.home / "readers.json"
        path.write_text(json.dumps({"schema_version": 1, "harnesses": harnesses}))
        os.environ["EVERAGENT_IDENTITY_CONFIG"] = str(path)

    def test_keywords_paths_and_session_keys_are_repairable_not_model_proof(self):
        self.override({"codex": {"process_names": ["renamed-codex"], "session_keys": ["FIXTURE_SESSION_ID"],
                                 "root": str(self.home / "relocated")}})
        self.chain.append({"pid": 9, "name": "renamed-codex", "started": "fixture-agent"})
        os.environ["FIXTURE_SESSION_ID"] = "current-session"
        self.assertEqual(core._detect_cli(), ("codex", "process-ancestry"))
        self.assertEqual(config.root("codex", self.home), self.home / "relocated")
        self.assertIn("session_ref", declarations.caller_scope("codex"))
        self.assertFalse(core.inspect_identity(observation={})["commit_ready"])

    def test_invalid_configuration_is_diagnosable_not_a_generic_process_match(self):
        for fields in ({"process_names": ["node"]}, {"session_keys": ["API_TOKEN"]},
                       {"model": "made-up"}, {"root": "~/all/*"}):
            with self.subTest(fields=fields):
                self.override({"codex": fields})
                value = core.inspect_identity()
                self.assertEqual(value["cli_source"], "reader-config-invalid")
                self.assertFalse(value["commit_ready"])

    def test_unknown_harness_can_be_user_declared_only_for_this_execution(self):
        fields = {"harness": "new-cli", "model": "user-model", "form": "cli"}
        with self.assertRaises(ValueError):
            declarations.declare_facts(fields, user_confirmed=False)
        receipt = declarations.declare_facts(fields, user_confirmed=True)
        self.assertFalse(receipt["grants_permissions"])
        value = core.inspect_identity(observation={})
        self.assertEqual(value["cli_source"], "user-declared")
        self.assertEqual(value["model"], "user-model")
        self.assertTrue(value["user_model_declared"])
        self.assertFalse(value["current_model_confirmed"])
        normalized = session.normalize(device={"known": True}, agent=value, checkout={"status": "ok"},
                                       runtime={}, caller={})
        self.assertEqual(normalized["interface"]["source"], "user-declared")
        self.chain[0] = {**self.chain[0], "started": "another-shell"}
        self.assertIsNone(declarations.read_facts())

    def test_successive_explicit_facts_preserve_other_still_bound_fields(self):
        declarations.declare_facts({"harness": "new-cli"}, user_confirmed=True)
        declarations.declare_facts({"model": "user-model", "form": "cli"}, user_confirmed=True)
        self.assertEqual(core.inspect_identity(observation={})["name"], "new-cli-user-model")

    def test_automatic_evidence_wins_and_conflicting_declarations_are_refused(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        with self.assertRaises(ValueError):
            declarations.declare_facts({"harness": "pi"}, user_confirmed=True, observed={"harness": "codex"})
        declarations.declare_facts({"model": "user-model"}, user_confirmed=True)
        observation = {"harness": "codex", "scope": declarations.caller_scope("codex"),
                       "source": "codex-turn-context", "observed_at": time.time(), "model": "native-model"}
        value = core.inspect_identity(observation=observation)
        self.assertEqual(value["model"], "native-model")
        self.assertTrue(value["current_model_confirmed"])
        self.assertFalse(value["user_model_declared"])

    def test_facts_expire_on_hint_change_tampering_or_restart(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        declarations.declare_facts({"model": "user-model"}, user_confirmed=True, ttl_seconds=300)
        self.assertIsNone(declarations.read_facts(now=time.time() + 301))
        with patch.dict(os.environ, {"CODEX_MODEL": "different-hint"}):
            self.assertIsNone(declarations.read_facts())
        original = self.path.read_text()
        value = json.loads(original)
        value["fields"]["model"] = "tampered"
        self.path.write_text(json.dumps(value))
        self.assertIsNone(declarations.read_facts())
        self.path.write_text(original)
        self.chain[-1] = {**self.chain[-1], "started": "restarted"}
        self.assertIsNone(declarations.read_facts())

    def test_latest_valid_user_model_receipt_wins_across_compatibility_names(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        declarations.declare_model("codex", "old-model", user_confirmed=True, hint=models.hint_fingerprint("codex"))
        declarations.declare_facts({"model": "new-model"}, user_confirmed=True)
        self.assertEqual(models.model_evidence("codex", observation={})["model"], "new-model")
        declarations.declare_model("codex", "latest-model", user_confirmed=True, hint=models.hint_fingerprint("codex"))
        self.assertEqual(models.model_evidence("codex", observation={})["model"], "latest-model")

    def test_unrelated_fact_updates_do_not_renew_or_resurrect_a_model(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        with patch.object(declarations.time, "time", return_value=1000):
            declarations.declare_facts({"model": "old-model"}, user_confirmed=True, ttl_seconds=4000)
        with patch.object(declarations.time, "time", return_value=1001):
            declarations.declare_model("codex", "new-model", user_confirmed=True,
                                       hint=models.hint_fingerprint("codex"), ttl_seconds=300)
        for now, fields in ((1002, {"form": "cli"}), (1003, {"device": "fixture"})):
            with patch.object(declarations.time, "time", return_value=now):
                receipt = declarations.declare_facts(fields, user_confirmed=True)
                self.assertEqual(receipt["field_times"]["model"], {"declared_at": 1000, "expires_at": 5000})
                self.assertEqual(models.model_evidence("codex", observation={})["model"], "new-model")
        with patch.object(declarations.time, "time", return_value=1302):
            self.assertFalse(models.model_evidence("codex", observation={})["user_model_declared"])
        with patch.object(declarations.time, "time", return_value=6000):
            self.assertNotIn("model", declarations.read_facts()["fields"])

    def test_expired_facts_model_remains_newer_than_legacy_after_another_update(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        with patch.object(declarations.time, "time", return_value=1000):
            declarations.declare_model("codex", "old-model", user_confirmed=True,
                                       hint=models.hint_fingerprint("codex"))
        with patch.object(declarations.time, "time", return_value=1001):
            declarations.declare_facts({"model": "new-model"}, user_confirmed=True, ttl_seconds=300)
        with patch.object(declarations.time, "time", return_value=1400):
            receipt = declarations.declare_facts({"form": "cli"}, user_confirmed=True)
            self.assertNotIn("model", receipt["fields"])
            self.assertFalse(models.model_evidence("codex", observation={})["user_model_declared"])

    def test_configured_desktop_without_session_is_bound_to_each_execution_shell(self):
        self.override({"new-desktop": {"process_names": ["NewDesktopAgent"], "form": "desktop"}})
        self.chain.append({"pid": 9, "name": "NewDesktopAgent", "started": "fixture-app"})
        os.environ["ORCA_TERMINAL_HANDLE"] = "same-terminal"
        for legacy in (False, True):
            with self.subTest(legacy=legacy):
                if legacy:
                    declarations.declare_model("new-desktop", "user-model", user_confirmed=True,
                                               hint=models.hint_fingerprint("new-desktop"))
                else:
                    declarations.declare_facts({"model": "user-model"}, user_confirmed=True)
                self.assertIn("execution_ref", declarations.caller_scope("new-desktop"))
                self.assertTrue(core.inspect_identity(observation={})["commit_ready"])
                self.chain[0] = {**self.chain[0], "started": self.chain[0]["started"] + "-next"}
                self.assertFalse(core.inspect_identity(observation={})["commit_ready"])

    def test_native_conflict_does_not_erase_the_model_supersession_boundary(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        with patch.object(declarations.time, "time", return_value=1000):
            declarations.declare_model("codex", "legacy-old", user_confirmed=True,
                                       hint=models.hint_fingerprint("codex"), ttl_seconds=4000)
        with patch.object(declarations.time, "time", return_value=1001):
            declarations.declare_facts({"model": "newer-correction"}, user_confirmed=True, ttl_seconds=300)
        with patch.object(declarations.time, "time", return_value=1303):
            receipt = declarations.declare_facts({"form": "cli"}, user_confirmed=True,
                                                 observed={"harness": "codex", "model": "native-live"})
            self.assertNotIn("model", receipt["fields"])
        with patch.object(declarations.time, "time", return_value=1304):
            self.assertFalse(models.model_evidence("codex", observation={})["user_model_declared"])
            declarations.declare_facts({"device": "fixture"}, user_confirmed=True)
            self.assertFalse(models.model_evidence("codex", observation={})["user_model_declared"])
        with patch.object(declarations.time, "time", return_value=1305):
            declarations.declare_model("codex", "explicit-new", user_confirmed=True,
                                       hint=models.hint_fingerprint("codex"))
            self.assertEqual(models.model_evidence("codex", observation={})["model"], "explicit-new")

    def test_same_tick_model_declaration_cannot_cross_revocation(self):
        self.chain.append({"pid": 9, "name": "codex", "started": "fixture-agent"})
        with patch.object(declarations.time, "time", return_value=1000):
            declarations.declare_model("codex", "same-tick-old", user_confirmed=True,
                                       hint=models.hint_fingerprint("codex"), ttl_seconds=4000)
            declarations.declare_facts({"model": "same-tick-correction"}, user_confirmed=True)
            declarations.declare_facts({"form": "cli"}, user_confirmed=True,
                                      observed={"harness": "codex", "model": "native-live"})
            self.assertFalse(models.model_evidence("codex", observation={})["user_model_declared"])
        with patch.object(declarations.time, "time", return_value=1001):
            declarations.declare_facts({"model": "later-explicit"}, user_confirmed=True)
            self.assertEqual(models.model_evidence("codex", observation={})["model"], "later-explicit")

    def test_unknown_harness_fallback_invalidates_generic_and_specific_hints(self):
        for harness, key in (("new-cli", "AGENT_MODEL"), ("codex", "CODEX_MODEL"), ("pi", "PI_MODEL")):
            with self.subTest(harness=harness), patch.dict(os.environ, {key: "initial"}):
                declarations.declare_facts({"harness": harness, "model": "user-model"}, user_confirmed=True)
                self.assertTrue(core.inspect_identity(observation={})["commit_ready"])
                os.environ[key] = "changed"
                self.assertIsNone(declarations.read_facts())
                self.assertFalse(core.inspect_identity(observation={})["commit_ready"])


class SessionContracts(unittest.TestCase):
    def test_nested_cli_keeps_its_interface_separate_from_outer_app(self):
        for harness, app, expected in (("codex", "dsh", "cli"), ("pi", "zcode", "cli"),
                                       ("zcode", "zcode", "desktop"), ("dsh", "dsh", "web")):
            with self.subTest(harness=harness, app=app), patch.object(declarations, "read_facts", return_value=None):
                value = session.normalize(device={"known": True},
                    agent={"cli": harness, "harness_resolved": True}, checkout={}, runtime={}, caller={},
                    host_app={"id": app, "verified": True, "source": "caller-process-entry"})
            self.assertEqual(value["interface"]["kind"], expected)
            self.assertEqual(value["host"]["id"], app)
            self.assertEqual(value["interface"]["source"], "caller-process-entry" if harness == app else "harness-rule")

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



class CursorCliBindingTests(unittest.TestCase):
    """cursor-cli declaration binding: sandbox watcher + conversation id only."""

    def test_sand_exit_watch_anchors_cursor_cli_not_generic_node(self):
        watch = {"pid": 52, "name": "sand-exit-watch", "started": "watcher-start"}
        node = {"pid": 1964, "name": "node", "started": "node-start"}
        with patch.object(processes, "process_chain", return_value=[node, watch]):
            self.assertEqual(processes.caller_process("cursor-cli"), watch)
            self.assertIsNotNone(processes.caller_anchor("cursor-cli"))
        with patch.object(processes, "process_chain", return_value=[node]):
            self.assertIsNone(processes.caller_process("cursor-cli"))
            self.assertIsNone(processes.caller_anchor("cursor-cli"))

    def test_cursor_cli_scope_requires_watcher_and_uses_conversation_id(self):
        watch = {"pid": 52, "name": "sand-exit-watch", "started": "watcher-start"}
        with patch.object(processes, "process_chain", return_value=[
            {"pid": 10, "name": "bash", "started": "shell-start"}, watch
        ]), patch.dict(os.environ, {"CURSOR_CONVERSATION_ID": "sand-subagent-fixture-1"}, clear=True):
            scope = declarations.caller_scope("cursor-cli")
        self.assertEqual(scope["harness"], "cursor-cli")
        self.assertIn("process_ref", scope)
        self.assertIn("session_ref", scope)
        self.assertNotIn("execution_ref", scope)
        with patch.object(processes, "process_chain", return_value=[
            {"pid": 10, "name": "bash", "started": "shell-start"}, watch
        ]), patch.dict(os.environ, {}, clear=True):
            # No native conversation id and no terminal_ref: fall back to execution shell.
            scope = declarations.caller_scope("cursor-cli")
        self.assertIn("execution_ref", scope)
        with patch.object(processes, "process_chain", return_value=[
            {"pid": 1964, "name": "node", "started": "node-start"}
        ]), patch.dict(os.environ, {"CURSOR_CONVERSATION_ID": "sand-subagent-fixture-1"}, clear=True):
            self.assertIsNone(declarations.caller_scope("cursor-cli"))

    def test_cursor_cli_declaration_binds_current_conversation_only(self):
        watch = {"pid": 52, "name": "sand-exit-watch", "started": "watcher-start"}
        with tempfile.TemporaryDirectory(prefix="everagent-cursor-cli-") as folder:
            receipt = Path(folder) / "receipt.json"
            env = {"CURSOR_CONVERSATION_ID": "sand-subagent-fixture-a",
                   "EVERAGENT_MODEL_DECLARATION": str(receipt)}
            with patch.object(processes, "process_chain", return_value=[watch]), patch.dict(
                os.environ, env, clear=True
            ), patch.object(models, "configuration_hint", return_value={
                "model": "unknown", "source": "unresolved", "confidence": "unknown"
            }):
                value = declarations.declare_model(
                    "cursor-cli", "grok-bot", user_confirmed=True,
                    hint=models.hint_fingerprint("cursor-cli"))
                self.assertEqual(value["model"], "grok-bot")
                self.assertEqual(value["scope"]["harness"], "cursor-cli")
                self.assertIn("session_ref", value["scope"])
                evidence = models.model_evidence("cursor-cli")
                self.assertTrue(evidence["user_model_declared"])
                self.assertEqual(evidence["model"], "grok-bot")
                self.assertEqual(evidence["confidence"], "declared")
            # A different conversation id must not reuse the receipt.
            with patch.object(processes, "process_chain", return_value=[watch]), patch.dict(
                os.environ, {"CURSOR_CONVERSATION_ID": "sand-subagent-fixture-b",
                             "EVERAGENT_MODEL_DECLARATION": str(receipt)}, clear=True
            ), patch.object(models, "configuration_hint", return_value={
                "model": "unknown", "source": "unresolved", "confidence": "unknown"
            }):
                evidence = models.model_evidence("cursor-cli")
                self.assertFalse(evidence["user_model_declared"])
                self.assertEqual(evidence["model"], "unknown")



if __name__ == "__main__":
    unittest.main()
