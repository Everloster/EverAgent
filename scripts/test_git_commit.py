"""Commit identity, staged-tree and trailer contracts in isolated Git fixtures."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("commit_test", Path(__file__).with_name("git_commit.py"))
commit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(commit)
IDENTITY = {"name": "fixture-model", "email": "noreply@example.com", "resolved": True,
            "model": "fixture-model", "model_source": "user-declared",
            "model_confidence": "declared", "user_model_declared": True,
            "declaration": {"id": "a" * 64}}


class CommitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="everagent-commit-test-")
        self.root = Path(self.temporary.name).resolve()
        env = {key: value for key, value in os.environ.items()
               if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"}}
        env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.environment = patch.dict(os.environ, env, clear=True)
        self.environment.start()
        self.git("init", "-q")
        (self.root / "file.txt").write_text("staged\n")
        self.git("add", "file.txt")

    def tearDown(self):
        self.environment.stop()
        self.temporary.cleanup()

    def git(self, *arguments, check=True):
        return subprocess.run(["git", *arguments], cwd=self.root, text=True,
                              encoding="utf-8", capture_output=True, check=check).stdout.strip()

    def run_commit(self, *arguments, gate=None, identity=None):
        with patch.object(commit.Path, "cwd", return_value=self.root):
            return commit.commit(list(arguments), gate=gate or (lambda target, env: 0),
                                 identity_reader=lambda: identity or IDENTITY)

    def test_metadata_options_and_attached_values(self):
        self.assertEqual(commit.option_parts(["-mmessage", "--date=now", "-q"]),
                         [("-m", "message"), ("--date", "now"), ("-q", None)])

    def test_content_options_and_author_reset_fail_before_identity_or_gate(self):
        for option in ("--all", "--include", "--only", "--patch", "--fixup=reword:HEAD",
                       "file.txt", "--", "--reset-author", "--unknown"):
            with self.subTest(option=option), self.assertRaises(commit.CommitError):
                commit.option_parts([option])
        with self.assertRaises(commit.CommitError):
            commit.option_parts(["-m"])

    def test_unknown_identity_blocks_commit_and_gate(self):
        calls = []
        self.assertEqual(self.run_commit("-m", "fixture", gate=lambda *args: calls.append(args),
                                         identity={**IDENTITY, "resolved": False}), 1)
        self.assertEqual(calls, [])

    def test_configured_model_blocks_before_the_gate(self):
        calls = []
        value = {**IDENTITY, "user_model_declared": False,
                 "model_confidence": "configured", "model_source": "config-default"}
        self.assertEqual(self.run_commit("-m", "fixture", identity=value,
                         gate=lambda *args: calls.append(args)), 1)
        self.assertEqual(calls, [])

    def test_index_change_blocks_the_commit(self):
        def gate(target, env):
            (target / "file.txt").write_text("changed by gate\n")
            self.git("add", "file.txt")
            return 0
        self.assertEqual(self.run_commit("-m", "fixture", gate=gate), 3)
        self.assertEqual(self.git("log", "-1", check=False), "")

    def test_failed_gate_keeps_head_unborn(self):
        self.assertEqual(self.run_commit("-m", "fixture", gate=lambda *args: 7), 7)
        self.assertEqual(self.git("log", "-1", check=False), "")

    def test_commit_uses_staged_content_owner_author_and_agent_committer(self):
        (self.root / "file.txt").write_text("unstaged\n")
        self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "-m", "fixture"), 0)
        self.assertEqual(self.git("show", "HEAD:file.txt"), "staged")
        name, email = commit.owned_module("git_identity").expected_author()
        self.assertEqual(self.git("show", "-s", "--format=%an <%ae>"), f"{name} <{email}>")
        self.assertEqual(self.git("show", "-s", "--format=%cn <%ce>"), "fixture-model <noreply@example.com>")
        self.assertEqual(self.git("show", "-s", "--format=%B").count(commit.TRAILER), 1)

    def test_existing_trailers_survive_and_aiden_is_deduplicated(self):
        message = "fixture\n\nAgent: fixture\nCo-Authored-By: Other <other@example.com>\n" + commit.TRAILER + "\n" + commit.TRAILER
        self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "-m", message,
                                         "--trailer", commit.TRAILER), 0)
        body = self.git("show", "-s", "--format=%B")
        self.assertEqual(body.count(commit.TRAILER), 1)
        self.assertIn("Co-Authored-By: Other <other@example.com>", body)
        self.assertIn("Agent: fixture", body)

    def test_file_message_and_literal_shell_characters(self):
        path = self.root / "message.txt"
        path.write_text("fixture 中文提交 `literal` $(literal)\n\nTask-Type: maintenance\n", encoding="utf-8")
        self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "-F", str(path)), 0)
        body = self.git("show", "-s", "--format=%B")
        self.assertIn("`literal` $(literal)", body)
        self.assertIn("中文提交", body)
        self.assertEqual(body.count(commit.TRAILER), 1)

    def test_environment_configuration_is_extended_without_persistence(self):
        base = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "example.key", "GIT_CONFIG_VALUE_0": "value"}
        value = commit.identity_environment(IDENTITY, base)
        self.assertEqual(value["GIT_CONFIG_COUNT"], "3")
        self.assertEqual(value["GIT_CONFIG_KEY_0"], "example.key")
        self.assertNotIn("GIT_AUTHOR_NAME", base)

    def test_amend_no_edit_keeps_one_aiden_and_owner_author(self):
        self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "-m", "fixture"), 0)
        self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "--amend", "--no-edit"), 0)
        self.assertEqual(self.git("show", "-s", "--format=%B").count(commit.TRAILER), 1)
        name, email = commit.owned_module("git_identity").expected_author()
        self.assertEqual(self.git("show", "-s", "--format=%an <%ae>"), f"{name} <{email}>")

    def test_reuse_and_reedit_normalize_message_and_retain_other_trailers(self):
        self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "-m", "fixture\n\nAgent: fixture"), 0)
        for flag in ("-C", "-c"):
            with self.subTest(flag=flag), patch.dict(os.environ, {"GIT_EDITOR": ":"}):
                self.assertEqual(self.run_commit("-q", "--no-gpg-sign", "--allow-empty", flag, "HEAD"), 0)
            body = self.git("show", "-s", "--format=%B")
            self.assertIn("Agent: fixture", body)
            self.assertEqual(body.count(commit.TRAILER), 1)

    def test_native_editor_message_is_normalized_before_commit(self):
        message = self.root / "template.txt"
        message.write_text("fixture\n\nAgent: fixture\n" + commit.TRAILER + "\n" + commit.TRAILER + "\n")
        self.git("config", "commit.template", str(message))
        with patch.dict(os.environ, {"GIT_EDITOR": ":"}):
            self.assertEqual(self.run_commit("-q", "--no-gpg-sign"), 0)
        self.assertEqual(self.git("show", "-s", "--format=%B").count(commit.TRAILER), 1)

    def test_identity_switch_or_expiry_after_gate_blocks_commit(self):
        for changed in ({**IDENTITY, "name": "another-model"},
                        {**IDENTITY, "user_model_declared": False},
                        {**IDENTITY, "model": "fixture/model"},
                        {**IDENTITY, "declaration": {"id": "b" * 64}}):
            with self.subTest(changed=changed), patch.object(commit.Path, "cwd", return_value=self.root), patch.object(
                commit._core, "identity_environment", wraps=commit._core.identity_environment
            ), patch.object(commit, "owned_module", wraps=commit.owned_module):
                from unittest.mock import Mock
                reader = Mock(side_effect=[IDENTITY, changed])
                self.assertIn(commit.commit(["-m", "fixture"], gate=lambda *args: 0, identity_reader=reader), (1, 3))
            self.assertEqual(self.git("log", "-1", check=False), "")


if __name__ == "__main__":
    unittest.main()
