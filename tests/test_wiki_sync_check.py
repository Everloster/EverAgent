"""Contract tests for scripts/wiki_sync_check.py.

These tests exercise the checker against synthetic subproject layouts in
``tmp_path`` so they don't depend on the real repo's state of drift.
"""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


import wiki_sync_check  # noqa: E402


# ---------- Helpers ----------

def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_clean_project(project_dir: Path) -> None:
    """Create a minimally-valid subproject: one paper + one wiki page referencing it."""
    report_stem = "01_foo_2020"
    _write(
        project_dir / "reports" / "paper_analyses" / f"{report_stem}.md",
        '---\ntitle: "Foo 2020"\ndomain: "x-learning"\nreport_type: "paper_analysis"\n'
        'status: "completed"\nupdated_on: "2026-04-17"\n---\nbody\n',
    )
    _write(
        project_dir / "wiki" / "entities" / "foo_person.md",
        '---\nid: entity-foo_person\ntitle: "Foo Person"\ntype: entity/person\n'
        'domain: [x-learning]\ncreated: 2026-04-17\nupdated: 2026-04-17\n'
        f"sources: [{report_stem}]\n---\nbody\n",
    )
    _write(
        project_dir / "wiki" / "index.md",
        "# index\n\n[foo](./entities/foo_person.md)\n",
    )
    _write(project_dir / "wiki" / "log.md", "log\n")


# ---------- Tests ----------

class FrontmatterParsingTests(unittest.TestCase):
    def test_scalar_and_list_fields(self) -> None:
        fm = wiki_sync_check.parse_frontmatter(
            '---\n'
            'title: "Hello"\n'
            "sources: [a, b, c]\n"
            "---\nbody\n"
        )
        self.assertIsNotNone(fm)
        self.assertEqual(fm["title"], "Hello")
        self.assertEqual(fm["sources"], ["a", "b", "c"])

    def test_missing_frontmatter_returns_none(self) -> None:
        self.assertIsNone(wiki_sync_check.parse_frontmatter("# no frontmatter\n"))

    def test_empty_sources_list(self) -> None:
        fm = wiki_sync_check.parse_frontmatter(
            '---\ntitle: "x"\nsources: []\n---\nbody\n'
        )
        assert fm is not None
        self.assertEqual(fm["sources"], [])


class CheckProjectCleanTests(unittest.TestCase):
    def test_clean_project_produces_no_issues(self) -> None:
        with TemporaryDirectory() as tmp:
            proj = Path(tmp) / "x-learning"
            _seed_clean_project(proj)
            issues = wiki_sync_check.check_project("x-learning", proj)
            # Filter out INFO (no-wiki warnings etc.)
            errs = [i for i in issues if i.severity in ("ERROR", "WARN")]
            self.assertEqual(errs, [])


class CheckProjectDriftTests(unittest.TestCase):
    def test_missing_wiki_directory_is_info_not_error(self) -> None:
        with TemporaryDirectory() as tmp:
            proj = Path(tmp) / "x-learning"
            _write(proj / "reports" / "paper_analyses" / "01.md", "---\n---\n")
            issues = wiki_sync_check.check_project("x-learning", proj)
            self.assertEqual(len(issues), 1)
            self.assertEqual(issues[0].severity, "INFO")

    def test_wiki_page_not_in_index_is_error(self) -> None:
        with TemporaryDirectory() as tmp:
            proj = Path(tmp) / "x-learning"
            _seed_clean_project(proj)
            # Add a second wiki page that is NOT referenced in index.md
            _write(
                proj / "wiki" / "concepts" / "orphan.md",
                '---\nid: concept-orphan\ntitle: "orphan"\ntype: concept\n'
                'domain: [x-learning]\nsources: [01_foo_2020]\n---\n',
            )
            issues = wiki_sync_check.check_project("x-learning", proj)
            messages = [i.message for i in issues if i.severity == "ERROR"]
            self.assertTrue(
                any("not linked from wiki/index.md" in m for m in messages),
                f"expected 'not linked' error, got: {messages}",
            )

    def test_index_links_to_missing_page_is_error(self) -> None:
        with TemporaryDirectory() as tmp:
            proj = Path(tmp) / "x-learning"
            _seed_clean_project(proj)
            # Add a broken link in index.md
            index_md = proj / "wiki" / "index.md"
            index_md.write_text(
                index_md.read_text(encoding="utf-8")
                + "\n[broken](./concepts/does_not_exist.md)\n",
                encoding="utf-8",
            )
            issues = wiki_sync_check.check_project("x-learning", proj)
            messages = [i.message for i in issues if i.severity == "ERROR"]
            self.assertTrue(
                any("does not exist" in m for m in messages),
                f"expected 'does not exist' error, got: {messages}",
            )

    def test_paper_without_wiki_reference_is_warn(self) -> None:
        with TemporaryDirectory() as tmp:
            proj = Path(tmp) / "x-learning"
            _seed_clean_project(proj)
            # Add a new paper_analysis that no wiki page references
            _write(
                proj / "reports" / "paper_analyses" / "02_orphan_2021.md",
                '---\ntitle: "Orphan 2021"\ndomain: "x"\n'
                'report_type: "paper_analysis"\nstatus: "completed"\n'
                'updated_on: "2026-04-17"\n---\nbody\n',
            )
            issues = wiki_sync_check.check_project("x-learning", proj)
            warns = [i for i in issues if i.severity == "WARN"]
            self.assertTrue(
                any("02_orphan_2021" in w.message for w in warns),
                f"expected orphan warning, got: {[w.message for w in warns]}",
            )

    def test_wiki_source_with_path_is_tolerated(self) -> None:
        """Cross-reference sources like 'knowledge/epistemology.md' should not warn."""
        with TemporaryDirectory() as tmp:
            proj = Path(tmp) / "x-learning"
            _seed_clean_project(proj)
            _write(
                proj / "wiki" / "entities" / "crossref.md",
                '---\nid: entity-crossref\ntitle: "Cross"\ntype: entity/person\n'
                'domain: [x-learning]\nsources: ["knowledge/external.md"]\n---\n',
            )
            # Register it in the index.md so the orphan-on-disk check passes
            index_md = proj / "wiki" / "index.md"
            index_md.write_text(
                index_md.read_text(encoding="utf-8")
                + "\n[cross](./entities/crossref.md)\n",
                encoding="utf-8",
            )
            issues = wiki_sync_check.check_project("x-learning", proj)
            warns = [
                i for i in issues
                if i.severity == "WARN" and "source 'knowledge" in i.message
            ]
            self.assertEqual(warns, [], "path-like sources should be tolerated")


class ExitCodeTests(unittest.TestCase):
    def test_help_returns_zero(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            wiki_sync_check.main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
