"""Automatic model verification regressions; synthetic metadata only."""
from __future__ import annotations

from datetime import datetime, timezone
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core_bootstrap  # noqa: E402,F401
from everagent_core.identity import declarations, models, observations, processes  # noqa: E402
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

    def test_no_persistence_or_symlink_stays_unverified(self):
        original = self.path.read_text()
        self.path.unlink()
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])
        other = self.root / "unrelated.jsonl"
        other.write_text(original)
        self.path.symlink_to(other)
        self.assertFalse(models.model_evidence("claude-code")["current_model_confirmed"])


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
