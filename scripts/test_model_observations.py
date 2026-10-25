"""Automatic model verification regressions; synthetic metadata only."""
from __future__ import annotations

from datetime import datetime, timezone
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core_bootstrap  # noqa: E402,F401
from everagent_core.identity import declarations, diagnostics, models, observations, processes  # noqa: E402
from everagent_core import git  # noqa: E402

THREAD = "00000000-0000-4000-8000-000000000042"
TURN = "fixture-current-turn"


def stamp(at=None):
    return datetime.fromtimestamp(time.time() if at is None else at, timezone.utc).isoformat()


def owner(name="codex", started=None):
    at = time.time() - 10 if started is None else started
    created = (str(int((at + 11_644_473_600) * 10_000_000)) if os.name == "nt"
               else time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(at)))
    return {"pid": 1234, "name": name, "started": created}


class CodexObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-auto-model-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "sessions/2026/01/01" / ("rollout-fixture-" + THREAD + ".jsonl")
        self.path.parent.mkdir(parents=True)
        (self.root / "config.toml").write_text('model = "misleading-default"\n')
        self.env = patch.dict(os.environ, {"CODEX_THREAD_ID": THREAD, "CODEX_SESSION_ID": THREAD,
                                           "CODEX_HOME": str(self.root)}, clear=True)
        self.env.start(); self.addCleanup(self.env.stop)
        self.chain = patch.object(processes, "process_chain", return_value=[owner()])
        self.chain.start(); self.addCleanup(self.chain.stop)
        self.home = patch.object(declarations, "safe_home", return_value=self.root)
        self.home.start(); self.addCleanup(self.home.stop)
        self.now = time.time()
        self.write()

    def record(self, kind, payload, *, ordinal=True, at=None):
        value = {"timestamp": stamp(self.now if at is None else at)}
        if ordinal:
            value["ordinal"] = 1
        value.update(type=kind, payload=payload)
        return json.dumps(value) + "\n"

    def write(self, model="observed-model", *, index_model=None, native=THREAD, ordinal=True,
              long_turn=False, usage_thread=THREAD, usage_at=None, ended=False):
        text = self.record("session_meta", {"id": native, "cwd": str(self.root)}, ordinal=ordinal)
        text += self.record("event_msg", {"type": "task_started", "turn_id": TURN}, ordinal=ordinal)
        text += self.record("turn_context", {"turn_id": TURN, "model": model}, ordinal=ordinal)
        text += self.record("response_item", {"model": "PRIVATE-DIALOG-SENTINEL"}, ordinal=ordinal)
        if long_turn:
            text += self.record("response_item", {"body": "x" * (observations.MAX_TAIL_BYTES + 1024)}, ordinal=ordinal)
        text += self.record("token_usage_record", {"thread_id": usage_thread, "turn_id": TURN}, ordinal=ordinal,
                            at=self.now if usage_at is None else usage_at)
        if ended:
            text += self.record("event_msg", {"type": "task_complete", "turn_id": TURN,
                                               "last_agent_message": "PRIVATE-DIALOG-SENTINEL"}, ordinal=ordinal)
        self.path.write_text(text)
        with closing(sqlite3.connect(self.root / "state_5.sqlite")) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS threads (id TEXT PRIMARY KEY, rollout_path TEXT, model TEXT, archived INTEGER, updated_at_ms INTEGER)")
            connection.execute("INSERT OR REPLACE INTO threads VALUES (?,?,?,?,?)", (
                THREAD, str(self.path), model if index_model is None else index_model, 0, int(self.now * 1000)))
            connection.commit()

    def test_current_turn_is_automatically_verified_before_default(self):
        value = models.model_evidence("codex")
        self.assertEqual(value["model"], "observed-model")
        self.assertEqual(value["source"], "codex-turn-context")
        self.assertTrue(value["current_model_confirmed"])
        self.assertFalse(value["user_model_declared"])
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", json.dumps(value))
        self.assertNotIn(str(self.root), json.dumps(value))

    def test_diagnose_preserves_automatic_verification_without_declaration(self):
        with patch.object(declarations, "declare_model") as declaration:
            value = diagnostics.diagnose()
        self.assertEqual(value["automatic_probe"]["status"], "observed")
        self.assertEqual(value["identity"]["model"], "observed-model")
        self.assertTrue(value["identity"]["current_model_confirmed"])
        self.assertFalse(value["identity"]["user_model_declared"])
        self.assertTrue(value["commit_allowed"])
        self.assertEqual(value["user_fallback"]["role"], "last-resort")
        declaration.assert_not_called()
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", json.dumps(value))
        self.assertNotIn(str(self.root), json.dumps(value))

    def test_diagnose_failure_does_not_authorize_configured_model(self):
        self.write(index_model="misleading-default")
        with patch.object(declarations, "declare_model") as declaration:
            value = diagnostics.diagnose()
        self.assertEqual(value["status"], "repair-needed")
        self.assertEqual(value["automatic_probe"]["reason_code"], "native-metadata-unavailable-or-invalid")
        self.assertFalse(value["identity"]["current_model_confirmed"])
        self.assertFalse(value["identity"]["user_model_declared"])
        self.assertFalse(value["commit_allowed"])
        self.assertTrue(value["authorized_source_repair_allowed"])
        self.assertFalse(value["diagnostics_are_model_evidence"])
        self.assertEqual(value["repair"]["order"][-1], "request-explicit-user-model-if-unverifiable")
        declaration.assert_not_called()

    def test_diagnose_missing_binding_does_not_scan_history(self):
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "", "CODEX_SESSION_ID": ""}), patch.object(
                observations, "_codex_index") as lookup:
            value = diagnostics.diagnose()
        self.assertEqual(value["automatic_probe"]["reason_code"], "current-caller-scope-unavailable")
        self.assertFalse(value["commit_allowed"])
        lookup.assert_not_called()

    def test_older_envelope_without_ordinal_is_supported(self):
        self.write(ordinal=False)
        self.assertTrue(models.model_evidence("codex")["current_model_confirmed"])

    def test_model_switch_is_rechecked_without_caching(self):
        self.assertEqual(models.model_evidence("codex")["model"], "observed-model")
        self.write("new-model")
        self.assertEqual(models.model_evidence("codex")["model"], "new-model")

    def test_wrong_thread_header_never_confirms(self):
        self.write(native="different-thread")
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def test_index_conflict_never_confirms_a_plausible_default(self):
        self.write(index_model="misleading-default")
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def test_finished_or_stale_session_is_not_current_proof(self):
        self.write(ended=True)
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])
        self.write()
        os.utime(self.path, (self.now - 301, self.now - 301))
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def test_archived_index_is_not_resurrected_from_a_log(self):
        with closing(sqlite3.connect(self.root / "state_5.sqlite")) as connection:
            connection.execute("UPDATE threads SET archived=1 WHERE id=?", (THREAD,))
            connection.commit()
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def test_native_ids_must_agree_before_any_history_lookup(self):
        with patch.dict(os.environ, {"CODEX_SESSION_ID": "different-session"}), patch.object(
                observations, "_codex_index") as lookup:
            self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])
        lookup.assert_not_called()

    def test_missing_native_id_does_not_search_for_a_recent_session(self):
        with patch.dict(os.environ, {"CODEX_THREAD_ID": "", "CODEX_SESSION_ID": ""}), patch.object(
                observations, "_codex_index") as lookup:
            self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])
        lookup.assert_not_called()

    def test_restart_and_nested_same_harness_cannot_borrow_old_context(self):
        with patch.object(processes, "process_chain", return_value=[owner(started=self.now + 5)]):
            self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])
        with patch.object(processes, "process_chain", return_value=[owner(), {**owner(), "pid": 999}]):
            self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def test_long_turn_uses_exact_runtime_index_and_fresh_usage(self):
        self.write(long_turn=True)
        value = models.model_evidence("codex")
        self.assertEqual(value["model"], "observed-model")
        self.assertEqual(value["source"], "codex-thread-state")
        self.assertTrue(value["current_model_confirmed"])
        self.write(long_turn=True, usage_thread="different-thread")
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])
        self.write(long_turn=True, usage_at=self.now - 301)
        self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def test_exact_filename_bootstrap_without_sqlite_index(self):
        (self.root / "state_5.sqlite").unlink()
        self.assertTrue(models.model_evidence("codex")["current_model_confirmed"])

    def test_switching_equivalent_native_readers_does_not_change_signing_identity(self):
        value = {"name": "codex-observed-model", "cli": "codex", "model": "observed-model",
                 "model_source": "codex-turn-context", "model_confidence": "session-bound",
                 "current_model_confirmed": True, "scope_ref": "scope", "observation_ref": "same-observation"}
        self.assertEqual(git.signing_evidence(value), git.signing_evidence({**value, "model_source": "codex-thread-state"}))

    def test_other_turn_or_scope_still_changes_signing_evidence(self):
        value = {"model_source": "codex-turn-context", "current_model_confirmed": True,
                 "scope_ref": "scope", "observation_ref": "current-turn"}
        self.assertNotEqual(git.signing_evidence(value), git.signing_evidence({**value, "observation_ref": "new-turn"}))


class IdentityDiagnosticTests(unittest.TestCase):
    def test_unknown_harness_stops_before_automatic_reader(self):
        unresolved = {"harness_resolved": False, "commit_ready": False}
        with patch.object(diagnostics, "_detect_cli", return_value=(None, "unresolved")), patch.object(
                diagnostics, "inspect_identity", return_value=unresolved), patch.object(
                observations, "collect") as reader, patch.object(declarations, "declare_model") as declaration:
            value = diagnostics.diagnose()
        self.assertEqual(value["automatic_probe"]["reason_code"], "current-harness-unresolved")
        self.assertFalse(value["user_fallback"]["available"])
        self.assertFalse(value["commit_allowed"])
        reader.assert_not_called()
        declaration.assert_not_called()

    def test_unsupported_reader_does_not_probe_another_harness(self):
        probe = {}
        with patch.object(processes, "caller_process") as caller:
            self.assertIsNone(observations.collect("kimi-cli", {"execution_ref": "fixture"}, diagnostics=probe))
        self.assertEqual(probe["status"], "unsupported")
        self.assertEqual(probe["reason_code"], "automatic-reader-not-implemented")
        caller.assert_not_called()

    def test_probe_error_reports_only_exception_type(self):
        probe = {}
        with patch.object(processes, "caller_process", side_effect=OSError("PRIVATE-ERROR-SENTINEL")):
            self.assertIsNone(observations.collect("codex", {"session_ref": "fixture"}, diagnostics=probe))
        self.assertEqual(probe["reason_code"], "automatic-probe-error")
        self.assertEqual(probe["error_type"], "OSError")
        self.assertNotIn("PRIVATE-ERROR-SENTINEL", json.dumps(probe))

    def test_zcode_reports_unsupported_platform_before_reading_metadata(self):
        probe = {}
        with patch.object(processes, "caller_process", return_value=owner("zcode-cli")), patch.object(
                observations.os, "name", "nt"), patch.object(observations, "_zcode_session_token") as source:
            self.assertIsNone(observations.collect("zcode", {"execution_ref": "fixture"}, diagnostics=probe))
        self.assertEqual(probe["reason_code"], "automatic-reader-platform-unsupported")
        self.assertEqual(probe["status"], "unsupported")
        source.assert_not_called()


class ClaudeObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-claude-model-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.now = time.time()
        patches = [patch.object(declarations, "safe_home", return_value=self.root),
                   patch.object(observations.Path, "cwd", return_value=self.root),
                   patch.object(models, "HOME", self.root),
                   patch.object(processes, "process_chain", return_value=[owner("claude")]),
                   patch.object(processes, "current_directory", return_value=self.root),
                   patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": THREAD,
                                           "ANTHROPIC_MODEL": "misleading-default"}, clear=True)]
        for item in patches:
            item.start(); self.addCleanup(item.stop)
        import re
        project = re.sub(r"[^a-zA-Z0-9]", "-", str(self.root))
        self.path = self.root / ".claude/projects" / project / (THREAD + ".jsonl")
        self.path.parent.mkdir(parents=True)
        self.write()

    def record(self, model="observed-claude-model", **changes):
        row = {"type": "assistant", "sessionId": THREAD, "cwd": str(self.root),
               "isSidechain": False, "timestamp": stamp(self.now), "uuid": TURN,
               "message": {"content": [{"type": "text", "text": 'PRIVATE-DIALOG-SENTINEL \\"model\\": \\"wrong-model\\" ] }'}],
                           "model": model}}
        row.update(changes)
        return json.dumps(row) + "\n"

    def write(self, model="observed-claude-model", **changes):
        self.path.write_text(self.record(model, **changes))

    def test_native_assistant_metadata_wins_over_configuration(self):
        value = models.model_evidence("claude-code")
        self.assertEqual(value["model"], "observed-claude-model")
        self.assertEqual(value["source"], "claude-session-runtime")
        self.assertTrue(value["current_model_confirmed"])
        self.assertFalse(value["user_model_declared"])
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", json.dumps(value))
        self.assertNotIn(str(self.root), json.dumps(value))

    def test_tool_cd_uses_only_the_current_harness_project(self):
        checkout = self.root / "other-checkout"
        checkout.mkdir()
        with patch.object(observations.Path, "cwd", return_value=checkout), patch.object(
                processes, "current_directory", return_value=self.root) as locate, patch.object(
                Path, "glob", side_effect=AssertionError("global-project-scan")), patch.object(
                Path, "rglob", side_effect=AssertionError("global-project-scan")):
            value = models.model_evidence("claude-code")
        self.assertEqual(value["model"], "observed-claude-model")
        self.assertTrue(value["current_model_confirmed"])
        self.assertFalse(value["user_model_declared"])
        self.assertEqual(locate.call_args.args[0]["name"], "claude")
        self.assertNotIn(str(self.root), json.dumps(value))

    def test_tool_cd_without_process_binding_does_not_search_other_projects(self):
        checkout = self.root / "other-checkout"
        checkout.mkdir()
        with patch.object(observations.Path, "cwd", return_value=checkout), patch.object(
                processes, "current_directory", return_value=None), patch.object(
                Path, "glob", side_effect=AssertionError("global-project-scan")):
            value = diagnostics.diagnose()
        self.assertFalse(value["commit_allowed"])
        self.assertEqual(value["automatic_probe"]["reason_code"], "native-session-file-unavailable")

    def test_tool_cd_still_requires_the_native_record_project(self):
        checkout = self.root / "other-checkout"
        checkout.mkdir()
        self.write(cwd=str(checkout))
        with patch.object(observations.Path, "cwd", return_value=checkout):
            self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_existing_invalid_session_is_not_replaced_by_process_directory_lookup(self):
        self.path.write_text('{"type":"assistant",}\n')
        with patch.object(processes, "current_directory") as locate:
            value = diagnostics.diagnose()
        self.assertFalse(value["commit_allowed"])
        self.assertEqual(value["automatic_probe"]["reason_code"], "native-metadata-invalid")
        locate.assert_not_called()

    def test_conversation_bodies_are_skipped_without_json_decoding(self):
        original = json.loads
        def metadata_only(text, *args, **kwargs):
            self.assertNotIn("PRIVATE-DIALOG-SENTINEL", text)
            return original(text, *args, **kwargs)
        with patch.object(observations.json, "loads", side_effect=metadata_only):
            self.assertTrue(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_same_observation_survives_gate_and_model_switch_changes_it(self):
        before = models.model_evidence("claude-code")
        self.assertEqual(before["observation_ref"], models.model_evidence("claude-code")["observation_ref"])
        self.write("new-observed-model", uuid="new-turn")
        after = models.model_evidence("claude-code")
        self.assertEqual(after["model"], "new-observed-model")
        self.assertNotEqual(before["observation_ref"], after["observation_ref"])

    def test_foreign_session_checkout_and_sidechain_are_rejected(self):
        for changes in ({"sessionId": "foreign-session"}, {"cwd": str(self.root / "other")},
                        {"isSidechain": True}, {"isSidechain": None}):
            with self.subTest(changes=changes):
                self.write(**changes)
                self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_latest_missing_proof_cannot_fall_back_to_an_older_model(self):
        for changes in ({"message": {}}, {"timestamp": None}, {"uuid": None},
                        {"isSidechain": None}, {"message": {"model": "<synthetic>"}}):
            with self.subTest(changes=changes):
                self.path.write_text(self.record() + self.record(**changes))
                self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_stale_record_file_and_restarted_process_are_rejected(self):
        self.write(timestamp=stamp(self.now - 301))
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])
        self.write()
        os.utime(self.path, (self.now - 301, self.now - 301))
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])
        self.write()
        with patch.object(processes, "process_chain", return_value=[owner("claude", self.now + 5)]):
            self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_nested_harness_and_missing_native_id_never_search_history(self):
        with patch.object(processes, "process_chain", return_value=[owner("claude"), {**owner("claude"), "pid": 999}]):
            self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])
        with patch.dict(os.environ, {"CLAUDE_CODE_SESSION_ID": ""}), patch.object(observations, "_claude") as lookup:
            self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])
        lookup.assert_not_called()

    def test_bounded_incomplete_or_oversized_latest_record_blocks_reuse(self):
        for tail in ('{"type":"assistant",', '{"type":"assistant",}',
                     self.record(message={"model": "new-model", "content": "x" * observations.MAX_RECORD_BYTES})):
            with self.subTest(length=len(tail)):
                self.path.write_text(self.record() + tail)
                self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_duplicate_metadata_and_escaped_body_keys_do_not_override_model(self):
        self.path.write_text(self.record().replace('"model": "observed-claude-model"',
                                                  '"model": "observed-claude-model", "model": "forged"'))
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_partial_tail_retries_same_file_and_observes_the_new_model(self):
        self.path.write_text(self.record() + '{"type":"assistant","message":')
        def finish(_delay):
            self.path.write_text(self.record() + self.record("new-model", uuid="new-turn"))
        with patch.object(observations.time, "sleep", side_effect=finish) as settle:
            value = diagnostics.diagnose()
        self.assertEqual(value["identity"]["model"], "new-model")
        self.assertTrue(value["identity"]["current_model_confirmed"])
        self.assertFalse(value["identity"]["user_model_declared"])
        self.assertEqual(value["automatic_probe"]["retry_count"], 1)
        settle.assert_called_once_with(observations.CLAUDE_READ_SETTLE_SECONDS)
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", json.dumps(value))
        self.assertNotIn(str(self.root), json.dumps(value))

    def test_persistent_partial_tail_is_bounded_and_never_borrows_old_model(self):
        self.path.write_text(self.record() + '{"type":"assistant",')
        with patch.object(observations.time, "sleep") as settle, patch.object(
                observations, "_claude_tail", wraps=observations._claude_tail) as read:
            value = diagnostics.diagnose()
        self.assertFalse(value["identity"]["current_model_confirmed"])
        self.assertFalse(value["commit_allowed"])
        self.assertEqual(value["automatic_probe"]["reason_code"], "native-observation-in-progress")
        self.assertEqual(value["automatic_probe"]["retry_count"], observations.CLAUDE_READ_ATTEMPTS - 1)
        self.assertEqual(read.call_count, observations.CLAUDE_READ_ATTEMPTS)
        self.assertEqual(settle.call_count, observations.CLAUDE_READ_ATTEMPTS - 1)

    def test_complete_malformed_tail_does_not_retry_or_reuse(self):
        invalid = self.record().replace('"model": "observed-claude-model"',
                                       '"model": "observed-claude-model", "model": "forged"')
        for tail in (invalid, invalid.rstrip(), '{"type":"assistant",}\n'):
            with self.subTest(tail=tail), patch.object(observations.time, "sleep") as settle:
                self.path.write_text(self.record() + tail)
                value = diagnostics.diagnose()
                self.assertFalse(value["commit_allowed"])
                self.assertEqual(value["automatic_probe"]["reason_code"], "native-metadata-invalid")
                settle.assert_not_called()

    def test_partial_completion_with_missing_or_foreign_proof_stays_unverified(self):
        for changes in ({"message": {}}, {"sessionId": "foreign"}, {"cwd": str(self.root / "other")},
                        {"isSidechain": None}, {"timestamp": None}):
            with self.subTest(changes=changes):
                self.path.write_text(self.record() + '{"type":"assistant",')
                def finish(_delay):
                    self.path.write_text(self.record() + self.record(**changes))
                with patch.object(observations.time, "sleep", side_effect=finish):
                    value = diagnostics.diagnose()
                self.assertFalse(value["commit_allowed"])
                self.assertEqual(value["automatic_probe"]["reason_code"], "native-assistant-binding-invalid")

    def test_concurrent_snapshot_write_is_retried_before_any_model_is_used(self):
        old = self.record().encode().splitlines()
        new = self.record("new-model", uuid="new-turn").encode().splitlines()
        with patch.object(observations, "_claude_tail", side_effect=[(old, True, False), (new, True, True)]) as read, patch.object(
                observations.time, "sleep") as settle:
            value = diagnostics.diagnose()
        self.assertEqual(value["identity"]["model"], "new-model")
        self.assertEqual(read.call_count, 2)
        settle.assert_called_once()

    def test_fresh_clock_after_settle_handles_concurrent_mtime(self):
        os.utime(self.path, (self.now + 1, self.now + 1))
        probe = {}
        with patch.object(observations.time, "time", return_value=self.now + 2), patch.object(
                observations.time, "sleep") as settle:
            value = observations._claude(THREAD, owner("claude", self.now - 10), self.now, diagnostics=probe)
        self.assertEqual(value["model"], "observed-claude-model")
        self.assertEqual(value["observed_at"], self.now + 2)
        self.assertEqual(probe["retry_count"], 1)
        settle.assert_called_once()

    def test_future_mtime_remains_unverified_after_bounded_retry(self):
        os.utime(self.path, (self.now + 5, self.now + 5))
        probe = {}
        with patch.object(observations.time, "time", return_value=self.now), patch.object(
                observations.time, "sleep") as settle:
            value = observations._claude(THREAD, owner("claude", self.now - 10), self.now, diagnostics=probe)
        self.assertIsNone(value)
        self.assertEqual(probe["reason_code"], "native-observation-in-progress")
        self.assertEqual(settle.call_count, observations.CLAUDE_READ_ATTEMPTS - 1)

    def test_oversized_record_is_not_retried_or_skipped(self):
        self.path.write_text(self.record() + self.record(message={"model": "new-model", "content": "x" * observations.MAX_RECORD_BYTES}))
        with patch.object(observations.time, "sleep") as settle:
            value = diagnostics.diagnose()
        self.assertFalse(value["commit_allowed"])
        self.assertEqual(value["automatic_probe"]["reason_code"], "native-record-oversized")
        settle.assert_not_called()

    def test_partial_utf8_tail_can_settle_without_decoding_conversation_body(self):
        self.path.write_bytes(self.record().encode() + b'{"type":"user","message":{"content":"' + "中".encode()[:1])
        def finish(_delay):
            self.path.write_text(self.record() + json.dumps({"type":"user", "message":{"content":"PRIVATE-DIALOG-SENTINEL"}}) + "\n")
        with patch.object(observations.time, "sleep", side_effect=finish) as settle:
            value = diagnostics.diagnose()
        self.assertTrue(value["commit_allowed"])
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", json.dumps(value))
        settle.assert_called_once()

    def test_claude_snapshot_retains_eof_and_stays_within_the_tail_budget(self):
        self.path.write_bytes(b"x" * (observations.MAX_TAIL_BYTES + 42) + b"\n" + self.record().encode())
        lines, terminated, stable = observations._claude_tail(self.path)
        self.assertEqual(lines, self.record().encode().splitlines())
        self.assertTrue(terminated)
        self.assertTrue(stable)
        self.assertTrue(models.model_evidence("claude-code")["current_model_confirmed"])

    def test_no_persistence_or_symlink_stays_unverified(self):
        original = self.path.read_text()
        self.path.unlink()
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])
        other = self.root / "unrelated.jsonl"
        other.write_text(original)
        self.path.symlink_to(other)
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])


class ProcessDirectoryTests(unittest.TestCase):
    """Native cwd lookup is limited to one creation-bound current ancestor."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="everagent-process-directory-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.owner = owner("claude")
        self.enterContext(patch.object(processes, "process_chain", return_value=[self.owner]))
        self.process = SimpleNamespace(returncode=0, stdout=self.owner["started"] + " /synthetic/claude\n")
        self.directory = SimpleNamespace(returncode=0, stdout=f"p1234\nfcwd\nn{self.root}\n")

    def test_macos_reads_only_that_process_cwd_and_rechecks_creation(self):
        with patch.object(processes.sys, "platform", "darwin"), patch.object(
                processes.subprocess, "run", side_effect=[self.process, self.directory, self.process]) as run:
            self.assertEqual(processes.current_directory(self.owner), self.root)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(run.call_args_list[1].args[0],
                         ["/usr/sbin/lsof", "-a", "-p", "1234", "-d", "cwd", "-Fpfn"])
        self.assertTrue(all(call.kwargs["timeout"] == 1 for call in run.call_args_list))

    def test_linux_reads_only_that_process_cwd_link(self):
        with patch.object(processes.sys, "platform", "linux"), patch.object(
                processes.os, "readlink", return_value=str(self.root)) as readlink, patch.object(
                processes.subprocess, "run", return_value=self.process) as run:
            self.assertEqual(processes.current_directory(self.owner), self.root)
        readlink.assert_called_once_with("/proc/1234/cwd")
        self.assertEqual(run.call_count, 2)

    def test_foreign_process_is_not_queried(self):
        with patch.object(processes.sys, "platform", "darwin"), patch.object(
                processes.subprocess, "run") as run:
            self.assertIsNone(processes.current_directory({**self.owner, "pid": 9999}))
        run.assert_not_called()

    def test_restart_during_lookup_does_not_return_the_old_directory(self):
        restarted = SimpleNamespace(returncode=0, stdout="Mon Jan 1 00:00:00 2024 /synthetic/claude\n")
        with patch.object(processes.sys, "platform", "darwin"), patch.object(
                processes.subprocess, "run", side_effect=[self.process, self.directory, restarted]):
            self.assertIsNone(processes.current_directory(self.owner))

    def test_malformed_foreign_or_ambiguous_macos_records_are_rejected(self):
        for output in (f"p9999\nfcwd\nn{self.root}\n", "p1234\nfcwd\nnrelative\n",
                       f"p1234\nfcwd\nn{self.root}\nn{self.root}\n", f"p1234\nf0\nn{self.root}\n"):
            with self.subTest(output=output), patch.object(processes.sys, "platform", "darwin"), patch.object(
                    processes.subprocess, "run", side_effect=[self.process, SimpleNamespace(returncode=0, stdout=output)]):
                self.assertIsNone(processes.current_directory(self.owner))

    def test_process_or_tool_failure_remains_unavailable(self):
        failures = (OSError("synthetic-unavailable"), subprocess.TimeoutExpired("ps", 1))
        for failure in failures:
            with self.subTest(failure=type(failure).__name__), patch.object(
                    processes.sys, "platform", "darwin"), patch.object(processes.subprocess, "run", side_effect=failure):
                self.assertIsNone(processes.current_directory(self.owner))

    def test_unsupported_platform_does_not_attempt_another_process_probe(self):
        with patch.object(processes.sys, "platform", "win32"), patch.object(processes.subprocess, "run") as run:
            self.assertIsNone(processes.current_directory(self.owner))
        run.assert_not_called()


class MinimaxObservationTests(unittest.TestCase):
    """MiniMax Code Desktop binds its conversation through the runtime turn lease."""

    RUNTIME = 4242
    SESSION = "mvs_fixture_minimax_session"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-minimax-model-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = time.time()
        (self.root / ".minimax").mkdir(parents=True)
        (self.root / ".minimax/config.yaml").write_text("defaultModel: minimax/misleading-default\n")
        self.database = self.root / ".minimax/v2/sqlite/runtime-state.sqlite"
        self.database.parent.mkdir(parents=True)
        created = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(self.now - 60))
        self.chain = [
            {"pid": 1234, "name": "python3", "started": created, "image": "python3"},
            {"pid": 1235, "name": "bash", "started": created, "image": "/bin/bash"},
            {"pid": self.RUNTIME, "name": "MiniMax Code Helper", "started": created,
             "image": "/Applications/MiniMax Code.app/Contents/MacOS/MiniMax Code Helper"},
        ]
        patches = [patch.object(declarations, "safe_home", return_value=self.root),
                   patch.object(models, "HOME", self.root),
                   patch.object(processes, "process_chain", return_value=self.chain),
                   patch.dict(os.environ, {}, clear=True)]
        for item in patches:
            item.start(); self.addCleanup(item.stop)
        self.write()

    def write(self, *, model="minimax/MiniMax-M3.1-Flash", ts=None, turn="fixture-turn",
              lease_pid=None, expires_in=900, usage=True, extra_lease=False, transcript=True):
        session = self.SESSION
        lease_pid = self.RUNTIME if lease_pid is None else lease_pid
        at = self.now if ts is None else ts
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS local_runtime_session_locks ("
                               "session_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, owner_kind TEXT NOT NULL,"
                               " acquired_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL)")
            connection.execute("CREATE TABLE IF NOT EXISTS local_runtime_token_usage ("
                               "id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,"
                               " agent_name TEXT NOT NULL, framework_type TEXT NOT NULL, turn_id TEXT,"
                               " model TEXT, ts INTEGER NOT NULL)")
            connection.execute("DELETE FROM local_runtime_session_locks")
            connection.execute("DELETE FROM local_runtime_token_usage")
            connection.execute("INSERT INTO local_runtime_session_locks VALUES (?,?,?,?,?)", (
                session, "turn-lease:%d:fixture-uuid" % lease_pid, "turn",
                int((self.now - 60) * 1000), int((self.now + expires_in) * 1000)))
            if extra_lease:
                connection.execute("INSERT INTO local_runtime_session_locks VALUES (?,?,?,?,?)", (
                    "mvs_fixture_second_session", "turn-lease:%d:fixture-uuid" % lease_pid, "turn",
                    int((self.now - 60) * 1000), int((self.now + expires_in) * 1000)))
            if usage:
                connection.execute(
                    "INSERT INTO local_runtime_token_usage"
                    " (session_id, agent_name, framework_type, turn_id, model, ts) VALUES (?,?,?,?,?,?)",
                    (session, "mavis", "pi-agent", turn, model, int(at * 1000)))
            connection.commit()
        if transcript:
            path = self.root / ".minimax/v2/sessions/2026/01/01/messages.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"message": {"role": "assistant", "model": "transcript-model",
                                                    "content": "PRIVATE-DIALOG-SENTINEL"}}) + "\n")

    def test_current_turn_is_automatically_verified_before_default(self):
        value = models.model_evidence("minimax-code")
        self.assertEqual(value["model"], "MiniMax-M3.1-Flash")
        self.assertEqual(value["source"], "minimax-session-runtime")
        self.assertTrue(value["current_model_confirmed"])
        self.assertFalse(value["user_model_declared"])
        self.assertEqual(value["configured_model"], "misleading-default")
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", json.dumps(value))

    def test_transcript_is_never_read_as_model_evidence(self):
        self.assertEqual(models.model_evidence("minimax-code")["model"], "MiniMax-M3.1-Flash")

    def test_lease_from_another_process_does_not_verify(self):
        self.write(lease_pid=9999)
        self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])

    def test_expired_lease_does_not_verify(self):
        self.write(expires_in=-30)
        self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])

    def test_two_leased_conversations_stay_ambiguous(self):
        self.write(extra_lease=True)
        self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])

    def test_stale_usage_or_missing_turn_does_not_verify(self):
        self.write(ts=self.now - 301)
        self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])
        self.write(usage=False)
        self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])

    def test_unusable_model_never_falls_back_to_the_config_default(self):
        for model in ("unknown", "", "not a model"):
            with self.subTest(model=model):
                self.write(model=model)
                value = models.model_evidence("minimax-code")
                self.assertFalse(value["current_model_confirmed"])
                self.assertEqual(value["model"], "misleading-default")

    def test_restarted_runtime_does_not_borrow_an_older_turn(self):
        restarted = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(self.now + 5))
        chain = [dict(row, started=restarted) for row in self.chain]
        with patch.object(processes, "process_chain", return_value=chain):
            self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])

    def test_scope_without_execution_shell_does_not_verify(self):
        scope = declarations.caller_scope("minimax-code")
        self.assertIn("execution_ref", scope)
        without = {key: value for key, value in scope.items() if key != "execution_ref"}
        self.assertIsNone(observations.collect("minimax-code", without))

    def test_model_switch_changes_the_signing_evidence(self):
        before = models.model_evidence("minimax-code")
        self.write(model="minimax/New-Model", turn="fixture-turn-2")
        after = models.model_evidence("minimax-code")
        self.assertEqual(after["model"], "New-Model")
        self.assertNotEqual(before["observation_ref"], after["observation_ref"])

    def test_missing_runtime_store_stays_unverified(self):
        self.database.unlink()
        self.assertFalse(models.model_evidence("minimax-code")["current_model_confirmed"])


class KimiDesktopObservationTests(unittest.TestCase):
    """Kimi Desktop binds an active turn through its own running Bash task."""

    APP = 17131
    RUNTIME = 17359
    SHELL = 21969
    SESSION = "conv-fixture-kimi"
    CONVERSATION = "agent:main:main:conversation:fixture"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-kimi-model-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.share = self.root / "share"
        self.workspace = self.root / "workspace"
        self.workspace.mkdir(parents=True)
        self.now = time.time()
        created = lambda at: time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(at))
        self.chain = [
            {"pid": 21970, "name": "python3", "started": created(self.now - 6), "image": "python3"},
            {"pid": self.SHELL, "name": "bash", "started": created(self.now - 5), "image": "/bin/bash"},
            {"pid": self.RUNTIME, "name": "Kimi Helper", "started": created(self.now - 60),
             "image": "/Applications/Kimi.app/Kimi Helper"},
            {"pid": self.APP, "name": "Kimi", "started": created(self.now - 61),
             "image": "/Applications/Kimi.app/Kimi"},
        ]
        self.state = self.share / "daimon/agents/main/runner.state.json"
        self.state.parent.mkdir(parents=True)
        self.database = self.share / "daimon/agents/main/sessions/hosted-logical/conversations.sqlite"
        self.database.parent.mkdir(parents=True)
        self.wire = (self.share / "daimon/runtime/kimi-code/home/sessions/wd_fixture" /
                     self.SESSION / "agents/main/wire.jsonl")
        self.wire.parent.mkdir(parents=True)
        patches = [patch.object(declarations, "safe_home", return_value=self.root),
                   patch.object(models, "HOME", self.root),
                   patch.object(processes, "process_chain", return_value=self.chain),
                   patch.object(observations.Path, "cwd", return_value=self.workspace),
                   patch.dict(os.environ, {"KIMI_SHARE_DIR": str(self.share),
                                           "KIMI_DESKTOP_RUNTIME_NODE": str(self.root / "node"),
                                           "AGENT_MODEL": "misleading-default"}, clear=True)]
        for item in patches:
            item.start(); self.addCleanup(item.stop)
        control = patch.object(observations, "_kimi_background_tasks", side_effect=lambda *_: self.tasks)
        control.start(); self.addCleanup(control.stop)
        self.write()

    def write(self, *, model="observed-kimi-model", request_model=None, usage_at=None, request_at=None,
              usage_scope="turn", turn="5", turn_at=None, task_status="running", task_pid=None,
              task_at=None, task_kind="bash", extra_turn=False, duplicate_task=False,
              lifecycle="running", state_pid=None, workspace=None, records=None,
              request_kind="loop", provider="kimi", model_alias=None, usage=True, request=True,
              long_turn=False, tail=""):
        session = self.SESSION
        turn_at = self.now - 10 if turn_at is None else turn_at
        usage_at = self.now if usage_at is None else usage_at
        request_at = usage_at if request_at is None else request_at
        active = {"operationId": "fixture-operation", "ownerAgentId": "main", "kernelSessionId": session,
                  "conversationKey": self.CONVERSATION, "turnId": turn, "startedAt": stamp(turn_at)}
        turns = [active]
        if extra_turn:
            turns.append({**active, "operationId": "fixture-operation-2", "kernelSessionId": "conv-fixture-other",
                          "conversationKey": self.CONVERSATION + "-other", "turnId": "1"})
        self.state.write_text(json.dumps({
            "schemaVersion": 1, "lifecycleStatus": lifecycle,
            "daemonGeneration": {"pid": self.RUNTIME if state_pid is None else state_pid},
            "control": {"endpoint": {"url": "ws://127.0.0.1:4567/control", "host": "127.0.0.1", "port": 4567,
                                      "pid": self.RUNTIME if state_pid is None else state_pid,
                                      "auth": {"mode": "bearer", "token": "PRIVATE-TOKEN-SENTINEL"}}},
            "activeKernelTurns": turns,
        }))
        task = {"kind": task_kind, "status": task_status,
                "pid": self.SHELL if task_pid is None else task_pid,
                "startedAtMs": int(((self.now - 5) if task_at is None else task_at) * 1000)}
        self.tasks = {session: [task] * (2 if duplicate_task else 1)}
        if extra_turn:
            self.tasks["conv-fixture-other"] = [dict(task)]
        with closing(sqlite3.connect(self.database)) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS conversations ("
                               "agent_id TEXT, conversation_key TEXT, kernel_session_id TEXT,"
                               " kernel_records_path TEXT, workspace_path TEXT)")
            connection.execute("DELETE FROM conversations")
            connection.execute("INSERT INTO conversations VALUES (?,?,?,?,?)", (
                "main", self.CONVERSATION, session, str(self.wire if records is None else records),
                str(self.workspace if workspace is None else workspace)))
            connection.commit()
        rows = [
            {"type": "usage.record", "model": "old-model", "usage": {"output": 1},
             "usageScope": "turn", "time": int((self.now - 20) * 1000)},
            {"type": "llm.request", "kind": "loop", "provider": "kimi", "model": "old-model",
             "modelAlias": "old-model", "time": int((self.now - 20) * 1000)},
            {"type": "tool.result", "result": {"content": "PRIVATE-DIALOG-SENTINEL",
                                                "padding": "x" * (observations.MAX_TAIL_BYTES + 1024) if long_turn else ""}},
        ]
        if usage:
            rows.append({"type": "usage.record", "model": model, "usage": {"output": 1},
                         "usageScope": usage_scope, "time": int(usage_at * 1000)})
        if request:
            rows.append({"type": "llm.request", "kind": request_kind, "provider": provider,
                         "model": model if request_model is None else request_model,
                         "modelAlias": model if model_alias is None else model_alias,
                         "time": int(request_at * 1000)})
        self.wire.write_text("\n".join(json.dumps(row) for row in rows) + "\n" + tail)

    def test_active_turn_is_automatically_verified_before_configuration(self):
        value = models.model_evidence("kimi-desktop")
        self.assertEqual(value["model"], "observed-kimi-model")
        self.assertEqual(value["source"], "kimi-desktop-session-runtime")
        self.assertEqual(value["configured_model"], "misleading-default")
        self.assertTrue(value["current_model_confirmed"])
        self.assertFalse(value["user_model_declared"])
        serialized = json.dumps(value)
        self.assertNotIn("PRIVATE-DIALOG-SENTINEL", serialized)
        self.assertNotIn("PRIVATE-TOKEN-SENTINEL", serialized)
        self.assertNotIn(str(self.root), serialized)

    def test_conversation_bodies_are_never_json_decoded(self):
        original = json.loads
        def metadata_only(text, *args, **kwargs):
            if isinstance(text, str):
                self.assertNotIn("PRIVATE-DIALOG-SENTINEL", text)
            return original(text, *args, **kwargs)
        with patch.object(observations.json, "loads", side_effect=metadata_only):
            self.assertTrue(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_long_turn_uses_only_the_bounded_current_wire_tail(self):
        self.write(long_turn=True)
        self.assertEqual(models.model_evidence("kimi-desktop")["model"], "observed-kimi-model")

    def test_foreign_finished_or_non_bash_tasks_do_not_verify(self):
        for changes in ({"task_pid": 9999}, {"task_status": "completed"},
                        {"task_status": "exited"}, {"task_kind": "exec"}):
            with self.subTest(changes=changes):
                self.write(**changes)
                self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_task_must_match_the_shell_creation_time(self):
        self.write(task_at=self.now - 2)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_parallel_sessions_and_duplicate_bindings_stay_ambiguous(self):
        self.write(extra_turn=True)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])
        self.write(duplicate_task=True)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_two_active_turns_for_one_session_stay_ambiguous(self):
        state = json.loads(self.state.read_text())
        state["activeKernelTurns"].append({**state["activeKernelTurns"][0], "turnId": "6"})
        self.state.write_text(json.dumps(state))
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_wrong_workspace_or_unbound_runtime_does_not_verify(self):
        self.write(workspace=self.root / "other")
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])
        for changes in ({"lifecycle": "stopped"}, {"state_pid": 9999}):
            with self.subTest(changes=changes):
                self.write(**changes)
                self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_wire_outside_the_session_root_or_symlink_does_not_verify(self):
        outside = self.root / "outside.jsonl"
        outside.write_bytes(self.wire.read_bytes())
        self.write(records=outside)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])
        self.write()
        outside.write_bytes(self.wire.read_bytes())
        self.wire.unlink()
        self.wire.symlink_to(outside)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_stale_future_or_previous_turn_usage_does_not_verify(self):
        for at in (self.now - 301, self.now + 5, self.now - 20):
            with self.subTest(at=at):
                self.write(usage_at=at)
                self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])
        self.write()
        os.utime(self.wire, (self.now - 301, self.now - 301))
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_restarted_app_does_not_borrow_an_active_turn_from_the_future(self):
        restarted = [dict(row) for row in self.chain]
        restarted[-1]["started"] = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime(self.now + 5))
        with patch.object(processes, "process_chain", return_value=restarted):
            self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_non_turn_scope_and_unusable_models_never_use_the_default(self):
        self.write(usage_scope="session")
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])
        for model in ("unknown", "", "not a model", None):
            with self.subTest(model=model):
                self.write(model=model)
                value = models.model_evidence("kimi-desktop")
                self.assertFalse(value["current_model_confirmed"])
                self.assertEqual(value["model"], "misleading-default")

    def test_missing_latest_usage_or_request_does_not_borrow_the_old_pair(self):
        self.write(usage=False)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])
        self.write(request=False)
        self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_request_model_kind_provider_and_alias_are_cross_checked(self):
        for changes in ({"request_model": "conflicting-model"}, {"request_kind": "sidechain"},
                        {"provider": "other"}, {"model_alias": "not a model"}):
            with self.subTest(changes=changes):
                self.write(**changes)
                self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_malformed_or_oversized_latest_record_cannot_reuse_old_model(self):
        oversized = json.dumps({"type": "usage.record", "model": "new-model", "usageScope": "turn",
                                "time": int(self.now * 1000), "padding": "x" * observations.MAX_RECORD_BYTES})
        for tail in ('{"type":"usage.record","model":', '{"type":"llm.request","kind":', oversized):
            with self.subTest(length=len(tail)):
                self.write(tail=tail)
                self.assertFalse(models.model_evidence("kimi-desktop")["current_model_confirmed"])

    def test_scope_without_execution_shell_does_not_verify(self):
        scope = declarations.caller_scope("kimi-desktop")
        self.assertIn("execution_ref", scope)
        without = {key: value for key, value in scope.items() if key != "execution_ref"}
        self.assertIsNone(observations.collect("kimi-desktop", without))

    def test_model_switch_changes_the_signing_evidence(self):
        before = models.model_evidence("kimi-desktop")
        self.write(model="new-observed-model")
        after = models.model_evidence("kimi-desktop")
        self.assertEqual(after["model"], "new-observed-model")
        self.assertNotEqual(before["observation_ref"], after["observation_ref"])


class OtherRuntimeObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="everagent-other-model-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        home = patch.object(declarations, "safe_home", return_value=self.root)
        home.start(); self.addCleanup(home.stop)
        hints = patch.object(models, "HOME", self.root)
        hints.start(); self.addCleanup(hints.stop)

    def test_pi_current_shell_context_is_verified_with_native_session(self):
        with patch.dict(os.environ, {"PI_CODING_AGENT": "true", "PI_SESSION_ID": THREAD,
                                    "PI_MODEL": "pi-current-model", "AGENT_MODEL": "outer-model"}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner("pi")]):
            value = models.model_evidence("pi")
        self.assertEqual(value["model"], "pi-current-model")
        self.assertTrue(value["current_model_confirmed"])
        self.assertEqual(value["source"], "pi-session-runtime")

    def test_pi_model_without_native_session_stays_a_hint(self):
        with patch.dict(os.environ, {"PI_CODING_AGENT": "true", "PI_MODEL": "pi-current-model"}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner("pi")]):
            self.assertFalse(models.model_evidence("pi")["current_model_confirmed"])

    def test_inherited_pi_context_does_not_confirm_codex(self):
        with patch.dict(os.environ, {"PI_CODING_AGENT": "true", "PI_SESSION_ID": THREAD,
                                    "PI_MODEL": "pi-current-model", "CODEX_HOME": str(self.root)}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner(), owner("pi")]):
            self.assertFalse(models.model_evidence("codex")["current_model_confirmed"])

    def write_trae(self, current_at=None):
        path = self.root / ".trae/cli/log/traecli-fixture.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(stamp(current_at) + " INFO thread_id=" + THREAD + " config_name=trae-current-model\n" +
                        stamp() + " INFO thread_id=" + THREAD + "-other config_name=wrong-model\n")

    def test_trae_matches_current_thread_instead_of_global_latest(self):
        self.write_trae()
        with patch.dict(os.environ, {"TRAE_THREAD_ID": THREAD}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner("coco")]):
            value = models.model_evidence("trae")
        self.assertEqual(value["model"], "trae-current-model")
        self.assertTrue(value["current_model_confirmed"])

    def test_trae_legacy_thread_alias_is_supported_without_outer_codex(self):
        self.write_trae()
        with patch.dict(os.environ, {"CODEX_THREAD_ID": THREAD}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner("coco")]):
            self.assertTrue(models.model_evidence("trae")["current_model_confirmed"])
        with patch.dict(os.environ, {"CODEX_THREAD_ID": THREAD}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner("coco"), owner()]):
            self.assertFalse(models.model_evidence("trae")["current_model_confirmed"])

    def test_old_thread_line_is_not_refreshed_by_another_thread(self):
        self.write_trae(time.time() - 301)
        with patch.dict(os.environ, {"TRAE_THREAD_ID": THREAD}, clear=True), patch.object(
                processes, "process_chain", return_value=[owner("coco")]):
            self.assertFalse(models.model_evidence("trae")["current_model_confirmed"])


if __name__ == "__main__":
    unittest.main()
