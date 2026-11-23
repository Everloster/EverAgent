import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/sync-external-skills.sh"


class ExternalSkillSyncTests(unittest.TestCase):
    def run_git(self, repo, *args):
        subprocess.run(
            ["git", "-C", str(repo), *args],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def commit_upstream(self, upstream, message):
        self.run_git(upstream, "add", "skills")
        self.run_git(
            upstream,
            "-c", "user.name=Fixture",
            "-c", "user.email=fixture@example.invalid",
            "commit", "-m", message,
        )

    def test_sync_restores_missing_directory_and_updates_existing_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "public"
            upstream = Path(directory) / "upstream"
            script = root / "scripts/sync-external-skills.sh"
            script.parent.mkdir(parents=True)
            shutil.copy2(SCRIPT, script)
            for skill in ("hypothesis-generation", "scientific-writing"):
                target = upstream / "skills" / skill
                target.mkdir(parents=True)
                (target / "SKILL.md").write_text(f"# {skill}\nnew\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(upstream)], check=True)
            self.commit_upstream(upstream, "initial")

            old = root / "docs/external-skills/scientific-agent-skills/hypothesis-generation"
            old.mkdir(parents=True)
            (old / "SKILL.md").write_text("old\n", encoding="utf-8")
            env = dict(os.environ, EVERAGENT_SKILLS_UPSTREAM=str(upstream))
            result = subprocess.run(
                [str(script)], cwd=root, env=env, encoding="utf-8", errors="replace", capture_output=True, check=False
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            for skill in ("hypothesis-generation", "scientific-writing"):
                target = root / "docs/external-skills/scientific-agent-skills" / skill / "SKILL.md"
                self.assertEqual(target.read_text(encoding="utf-8"), f"# {skill}\nnew\n")
            self.assertFalse(any(".new." in path.name or ".backup." in path.name for path in old.parent.iterdir()))

            repeated = subprocess.run(
                [str(script)], cwd=root, env=env, encoding="utf-8", errors="replace", capture_output=True, check=False
            )
            self.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
            self.assertIn("与上游一致", repeated.stdout)

    def test_missing_upstream_skill_leaves_local_copy_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "public"
            upstream = Path(directory) / "upstream"
            script = root / "scripts/sync-external-skills.sh"
            script.parent.mkdir(parents=True)
            shutil.copy2(SCRIPT, script)
            target = upstream / "skills/hypothesis-generation"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("upstream\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(upstream)], check=True)
            self.commit_upstream(upstream, "missing second skill")

            old = root / "docs/external-skills/scientific-agent-skills/hypothesis-generation"
            old.mkdir(parents=True)
            (old / "SKILL.md").write_text("keep me\n", encoding="utf-8")
            result = subprocess.run(
                [str(script)],
                cwd=root,
                env=dict(os.environ, EVERAGENT_SKILLS_UPSTREAM=str(upstream)),
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("上游缺少 scientific-writing", result.stderr)
            self.assertEqual((old / "SKILL.md").read_text(encoding="utf-8"), "keep me\n")


if __name__ == "__main__":
    unittest.main()
