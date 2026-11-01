"""Public gate contracts use generated synthetic values, never real credentials."""
import contextlib
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_public_context as audit
import precommit_quality


def credential(char="A"):
    return "ghp_" + char * 24


class PublicGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git("init", "-q")
        self.git("config", "user.name", "Public gate fixture")
        self.git("config", "user.email", "fixture@example.org")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.write("README.md", "# Fixture\n")
        self.commit()

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.root, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value, encoding="utf-8")
        return target

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "-qm", "synthetic fixture\n\nCo-Authored-By: Aiden")
        return self.git("rev-parse", "HEAD")

    def staged(self):
        return audit.audit_git(self.root, staged=True)

    def test_python_references_are_not_literal_credentials(self):
        code = '''import os
@KEY@ = os.environ["API_KEY"]
@TOKEN@ = os.getenv("ACCESS_TOKEN")
@PASSWORD@ = config.password
@SECRET@ = existing_secret
client = Client(@KEY@=os.environ.get("API_KEY", None))
settings = {"@KEY@": config.api_key}
标题 = "示例"; @KEY@ = os.getenv("API_KEY", "")
'''.replace("@KEY@", "api_key").replace("@TOKEN@", "access_token").replace("@PASSWORD@", "password").replace("@SECRET@", "secret")
        self.write("env.py", code)
        self.write("guide.md", "# 示例\n```python\n" + code + "```\n")
        self.git("add", "--all")
        self.assertTrue(self.staged()["ok"])

    def test_reference_exemption_keeps_literals_defaults_and_other_token_rules(self):
        value = "synthetic" * 3
        cases = [
            ('api_key = "' + value + '"', "CREDENTIAL_VALUE"),
            ('api_key = ' + 'os.getenv("KEY", "' + value + '")', "CREDENTIAL_VALUE"),
            ('api_key = ' + 'os.environ.get("KEY", default="' + value + '")', "CREDENTIAL_VALUE"),
            ('api_key = ' + credential(), "KNOWN_TOKEN_PREFIX"),
            ('# password=' + value, "CREDENTIAL_VALUE"),
            ('doc = "password=' + value + '"', "CREDENTIAL_VALUE"),
            ('api_key = ' + 'os.environ["password=' + value + '"]', "CREDENTIAL_VALUE"),
        ]
        for code, expected in cases:
            with self.subTest(expected=expected, code_length=len(code)):
                self.assertIn(expected, {item.code for item in audit.scan_text(code, "fixture.py")})
        reference = "os." + "environ"
        for filename, code in (
            ("config.json", json.dumps({"api_key": reference})),
            ("config.yaml", "api_key: " + reference),
            ("fixture.py", 'api_key = "' + reference + '"'),
        ):
            with self.subTest(filename=filename):
                self.assertIn("CREDENTIAL_VALUE", {item.code for item in audit.scan_text(code, filename)})

    def publication(self, source, **overrides):
        record = {
            "schema_version": 1, "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "source_url": "https://example.org/episode", "permission_url": "https://example.org/license",
            "permission_note": "合成测试样本：允许全文公开与改编。", "maintainer_confirmed": True,
        }
        record.update(overrides)
        return self.write(str(source.relative_to(self.root)) + audit.PUBLICATION_SUFFIX,
                          json.dumps(record, ensure_ascii=False))

    def test_new_full_sources_block_even_without_a_report(self):
        for name in ("topic.transcript.txt", "topic.polished.txt", "subtitles.vtt", "subtitles.srt",
                     "podcast-learning/reports/transcripts/full.md"):
            self.write(name, "[00:00:00 -> 00:00:02] 合成测试样本\n")
        self.git("add", "--all")
        result = self.staged()
        self.assertEqual(result["errors"], 5)
        self.assertEqual({item["code"] for item in result["findings"]}, {"FULL_TRANSCRIPT_PUBLICATION"})
        self.assertFalse(audit.audit_git(self.root)["ok"])

    def test_private_receipts_and_reports_do_not_require_publication_records(self):
        self.write("podcast-learning/reports/study.md", "# 学习报告\n来源与原创分析。\n")
        self.write("podcast-learning/reports/transcripts/source.audit.json", '{"schema_version":2}')
        self.git("add", "--all")
        self.assertTrue(self.staged()["ok"])

    def test_publication_permission_is_bound_to_staged_source_and_confirmation(self):
        source = self.write("topic.transcript.txt", "[00:00:00 -> 00:00:02] 合成样本\n")
        for overrides in ({"maintainer_confirmed": False}, {"sha256": "0" * 64},
                          {"permission_note": ""}, {"permission_url": "local-note.md"}):
            self.publication(source, **overrides)
            self.git("add", "--all")
            self.assertFalse(self.staged()["ok"])
        self.publication(source)
        self.assertFalse(self.staged()["ok"], "unstaged permission must not authorize the index")
        self.git("add", "--all")
        self.assertTrue(self.staged()["ok"])
        source.write_text("different worktree source\n")
        self.assertTrue(self.staged()["ok"], "index still contains the approved bytes")
        self.assertFalse(audit.audit_git(self.root)["ok"])

    def test_published_source_changes_and_permission_deletion_need_revalidation(self):
        source = self.write("topic.polished.txt", "合成测试样本。\n")
        permission = self.publication(source)
        self.commit()
        original = source.read_text()
        source.write_text(original + "新增一段。\n")
        self.git("add", source.name)
        self.assertFalse(self.staged()["ok"])
        source.write_text(original)
        self.git("add", source.name)
        self.git("rm", permission.name)
        self.assertFalse(self.staged()["ok"], "removing only permission cannot restore legacy exemption")
        self.git("rm", source.name)
        self.assertTrue(self.staged()["ok"])

    def test_existing_full_sources_are_not_retroactively_relicensed(self):
        source = self.write("legacy.transcript.txt", "历史合成样本。\n")
        self.commit()
        source.write_text("历史合成样本，修正错字。\n")
        self.git("add", source.name)
        self.assertTrue(self.staged()["ok"])
        self.git("mv", source.name, "moved.transcript.txt")
        self.assertFalse(self.staged()["ok"])

    def test_committed_range_requires_same_publication_permission_as_staging(self):
        base = self.git("rev-parse", "HEAD")
        source = self.write("topic.transcript.txt", "合成测试样本。\n")
        self.commit()
        self.assertFalse(audit.audit_git(self.root, base=base, head="HEAD")["ok"])
        self.publication(source)
        self.commit()
        self.assertTrue(audit.audit_git(self.root, base=base, head="HEAD")["ok"])
        self.publication(source, maintainer_confirmed=False)
        self.commit()
        self.assertFalse(audit.audit_git(self.root, base=base, head="HEAD")["ok"])

    def test_index_not_worktree_is_the_publication_boundary(self):
        path = self.write("note with spaces.md", credential())
        self.git("add", "--", path.name)
        path.write_text("safe worktree\n")
        result = self.staged()
        self.assertFalse(result["ok"])
        self.assertEqual(result["findings"][0]["file"], path.name)
        self.git("add", "--", path.name)
        path.write_text(credential())
        self.assertTrue(self.staged()["ok"])

    def test_old_occurrence_does_not_block_unrelated_report_edits(self):
        self.write("old.md", credential() + "\nold text\n")
        self.commit()
        self.write("old.md", "new introduction\n" + credential() + "\nnew text\n")
        self.git("add", "old.md")
        result = self.staged()
        self.assertTrue(result["ok"])
        self.assertEqual(result["existing_occurrences"], 1)
        self.assertEqual(result["files_scanned"], 1)

    def test_changed_value_and_duplicate_occurrence_cannot_use_old_baseline(self):
        self.write("old.md", credential() + "\n")
        self.commit()
        for text in (credential("B"), credential() + " " + credential()):
            with self.subTest(text_length=len(text)):
                self.write("old.md", text)
                self.git("add", "old.md")
                self.assertFalse(self.staged()["ok"])

    def test_renamed_file_is_not_an_exemption(self):
        self.write("old.md", credential())
        self.commit()
        self.git("mv", "old.md", "new name.md")
        self.assertFalse(self.staged()["ok"])

    def test_deleted_content_is_not_scanned(self):
        self.write("old.md", credential())
        self.commit()
        self.git("rm", "old.md")
        self.assertTrue(self.staged()["ok"])
        self.assertEqual(self.staged()["files_selected"], 0)

    def test_tests_and_fixture_paths_have_no_credential_exemption(self):
        for path in ("tests/fixtures/example.txt", "scripts/test_example.py"):
            self.write(path, credential())
        self.git("add", "--all")
        result = self.staged()
        self.assertEqual(result["errors"], 2)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            audit.emit(result)
            audit.emit(result, as_json=True)
        self.assertNotIn(credential(), output.getvalue())
        self.assertNotIn("fingerprint", output.getvalue())
        self.assertNotIn(str(self.root), output.getvalue())

    def test_json_decoded_values_cannot_hide_a_new_token(self):
        value = credential()
        encoded = "".join("\\u%04x" % ord(char) for char in value)
        self.write("payload.json", '{"value":"' + encoded + '"}')
        self.git("add", "payload.json")
        result = self.staged()
        self.assertFalse(result["ok"])
        self.assertTrue(any(item["line"] == 0 for item in result["findings"]))
        self.assertNotIn(value, json.dumps(result))

    def test_json_existing_value_does_not_exempt_changed_value(self):
        self.write("payload.json", json.dumps({"value": credential()}))
        self.commit()
        self.write("payload.json", json.dumps({"value": credential("B")}))
        self.git("add", "payload.json")
        self.assertFalse(self.staged()["ok"])

    def test_invalid_json_is_never_baselined(self):
        self.write("data.json", "{")
        self.commit()
        self.write("data.json", "{\n")
        self.git("add", "data.json")
        self.assertIn("INVALID_JSON", {item["code"] for item in self.staged()["findings"]})

    def test_worktree_mode_includes_untracked_and_staged_changes(self):
        self.write("untracked file.txt", credential())
        self.assertFalse(audit.audit_git(self.root)["ok"])
        self.git("add", "--all")
        self.assertFalse(audit.audit_git(self.root)["ok"])

    def test_committed_ci_range_ignores_worktree_and_checks_entire_range(self):
        base = self.git("rev-parse", "HEAD")
        path = self.write("report.md", credential())
        introduced = self.commit()
        self.write("safe.md", "safe")
        self.commit()
        path.write_text("not committed")
        self.assertFalse(audit.audit_git(self.root, base=base, head="HEAD")["ok"])
        self.assertTrue(audit.audit_git(self.root, base=introduced, head="HEAD")["ok"])
        with self.assertRaises(audit.AuditError):
            audit.audit_git(self.root, base="missing-base", head="HEAD")

    def test_first_commit_has_empty_baseline(self):
        empty = self.root / "empty"
        empty.mkdir()
        subprocess.run(["git", "init", "-q", str(empty)], check=True)
        (empty / "note.md").write_text(credential())
        subprocess.run(["git", "-C", str(empty), "add", "note.md"], check=True)
        self.assertFalse(audit.audit_git(empty, staged=True)["ok"])

    def test_symlinks_are_rejected_without_following_targets(self):
        (self.root / "link.md").symlink_to("README.md")
        self.git("add", "link.md")
        self.assertFalse(self.staged()["ok"])
        self.assertFalse(audit.audit_git(self.root)["ok"])

    def test_private_key_headers_never_exempt_a_replaced_key_body(self):
        header = "-----BEGIN " + "PRIVATE KEY-----\n"
        self.write("note.md", header + "old synthetic body")
        self.commit()
        self.write("note.md", header + "new synthetic body")
        self.git("add", "note.md")
        self.assertFalse(self.staged()["ok"])

    def test_partial_credential_match_never_exempts_changed_suffix(self):
        prefix = "password" + " = " + "A" * 8
        self.write("note.md", prefix + "!old-value")
        self.commit()
        for suffix in ("!new-value", "#new-value", "@new-value"):
            with self.subTest(suffix=suffix):
                self.write("note.md", prefix + suffix)
                self.git("add", "note.md")
                self.assertFalse(self.staged()["ok"])

    def test_existing_heuristics_still_detect_generated_sensitive_examples(self):
        examples = {
            "CREDENTIAL_VALUE": "password" + "=" + "synthetic" * 3,
            "BEARER_TOKEN": "Authorization" + ": Bearer " + "B" * 24,
            "ABSOLUTE_HOME_PATH": "/" + "home" + "/fixture/doc.md",
            "URL_CREDENTIAL": "https://" + "fixture:synthetic@example.org",
        }
        for code, text in examples.items():
            with self.subTest(code=code):
                self.assertIn(code, {item.code for item in audit.scan_text(text, "fixture.md")})

    def test_private_file_extensions_do_not_depend_on_content(self):
        for name in (".env", "key.pem", "id_ed25519"):
            self.write(name, "short")
        self.git("add", "--all")
        self.assertEqual(self.staged()["errors"], 3)

    def test_binary_assets_are_counted_not_claimed_scanned(self):
        (self.root / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00")
        self.write("fake.png", credential())
        (self.root / "unknown.bin").write_bytes(b"\x00\xff")
        self.git("add", "--all")
        result = self.staged()
        self.assertEqual(result["files_skipped_binary"], 1)
        self.assertEqual(result["errors"], 2)
        media = b"\x00\x00\x00\x18ftypisom"
        self.assertTrue(audit.known_binary(media, "docs/assets/public/demo.mp4"))
        self.assertFalse(audit.known_binary(media, "downloads/demo.mp4"))
        self.assertFalse(audit.known_binary(credential().encode(), "docs/assets/public/demo.mp4"))

    def test_oversized_new_text_fails_closed(self):
        self.write("large.txt", "x" * (audit.MAX_BYTES + 1))
        self.git("add", "large.txt")
        self.assertFalse(self.staged()["ok"])

    def test_explicit_scan_keeps_path_and_symlink_guards(self):
        with mock.patch.object(audit, "ROOT", self.root):
            self.assertFalse(audit.scan_file(Path("../outside.txt"))[1])
            link = self.root / "link"
            link.symlink_to(self.root / "README.md")
            self.assertFalse(audit.scan_file(Path("link"))[1])
            self.assertTrue(audit.scan_file(Path("README.md"))[1])

    def test_cli_reports_only_locations_even_with_special_filename(self):
        path = "odd\nfile name.md"
        self.write(path, credential())
        self.git("add", "--", path)
        script = self.root / "scripts" / "audit_public_context.py"
        script.parent.mkdir()
        shutil.copyfile(ROOT / "scripts" / script.name, script)
        result = subprocess.run([sys.executable, str(script), "--staged", "--json"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["findings"][0]["file"], path)
        self.assertNotIn(credential(), result.stdout + result.stderr)

    def test_precommit_public_gate_and_readme_use_correct_snapshots(self):
        self.write("target.md", "# Target\n")
        self.write("README.md", "[target](target.md#target)\n")
        self.commit()
        self.write("README.md", "[missing](missing.md)\n")
        self.git("add", "README.md")
        self.write("README.md", "[target](target.md#target)\n")
        for name in ("audit_public_context.py", "check_readme_links.py"):
            destination = self.root / "scripts" / name
            destination.parent.mkdir(exist_ok=True)
            shutil.copyfile(ROOT / "scripts" / name, destination)
        self.git("add", "scripts")
        calls = []
        actual_run = precommit_quality.run

        def selected_run(label, command, cwd):
            calls.append(label)
            if label in {"incremental public content", "root README links"}:
                return actual_run(label, command, cwd)
            return True

        with mock.patch.object(precommit_quality, "ROOT", self.root), mock.patch.object(
            precommit_quality, "run", side_effect=selected_run
        ), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(precommit_quality.main(), 1)
        self.assertEqual(calls[:2], ["incremental public content", "root README links"])

    def test_precommit_git_failure_is_not_an_empty_change(self):
        with mock.patch.object(precommit_quality, "git_paths", side_effect=RuntimeError), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(precommit_quality.main(), 1)

    def test_ignore_patterns_keep_public_research_visible(self):
        shutil.copyfile(ROOT / ".gitignore", self.root / ".gitignore")
        ignored = ["clip.mp4", "audio.wav", "topic/books/sub/book.pdf", "topic/books/book.epub",
                   "node_modules/pkg/index.js", "nested/node_modules/pkg/index.js", "key.pem",
                   "docs/assets/public/key.pem", "docs/assets/public/.env"]
        visible = ["research/paper.pdf", "reports/data.json", "docs/assets/everagent-intro.webp",
                   "docs/assets/public/clip.mp4", "topic/books/README.md", "id_ed25519.pub"]
        for path, expected in [(path, True) for path in ignored] + [(path, False) for path in visible]:
            with self.subTest(path=path):
                result = subprocess.run(["git", "check-ignore", "--no-index", "-q", path], cwd=self.root)
                self.assertEqual(result.returncode == 0, expected)


if __name__ == "__main__":
    unittest.main()
