import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_podcast_manifest
import report_catalog

import importlib.util

SYNC_PATH = ROOT / "podcast-learning/scripts/sync_index_status.py"
SYNC_SPEC = importlib.util.spec_from_file_location("sync_index_status", SYNC_PATH)
sync_index_status = importlib.util.module_from_spec(SYNC_SPEC)
SYNC_SPEC.loader.exec_module(sync_index_status)


class ReportProjectionTests(unittest.TestCase):
    def test_source_urls_accept_scalar_and_list_without_duplicates(self):
        metadata = report_catalog.parse_frontmatter(
            """---
source_url: "https://example.com/one"
source_urls:
  - "https://example.com/one"
  - "https://example.com/two"
---
"""
        )
        self.assertEqual(
            report_catalog.report_source_urls(metadata),
            ["https://example.com/one", "https://example.com/two"],
        )

    def test_manifest_uses_latest_completed_report_and_ignores_drafts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / "podcast-learning/reports"
            reports.mkdir(parents=True)
            url = "https://www.xiaoyuzhoufm.com/episode/one"
            (reports / "old.md").write_text(
                f"---\ntitle: Old\nstatus: completed\nupdated_on: 2026-01-01\nsource_url: {url}\n---\n",
                encoding="utf-8",
            )
            (reports / "new.md").write_text(
                f"---\ntitle: New\nstatus: archived\nupdated_on: 2026-02-01\nsource_urls: [{url}]\n---\n",
                encoding="utf-8",
            )
            (reports / "draft.md").write_text(
                f"---\ntitle: Draft\nstatus: in_progress\nupdated_on: 2026-03-01\nsource_url: {url}\n---\n",
                encoding="utf-8",
            )
            with mock.patch.object(build_podcast_manifest, "ROOT", root), mock.patch.object(
                build_podcast_manifest, "REPORT_DIR", reports
            ):
                loaded = build_podcast_manifest.load_reports()

        self.assertEqual(loaded[url]["title"], "New")
        self.assertEqual(loaded[url]["path"], "podcast-learning/reports/new.md")

    def test_status_projection_shares_multisource_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            reports = Path(directory)
            (reports / "2026-01-01_show_episode.md").write_text(
                """---
status: done
source_urls:
  - https://example.com/one
  - https://example.com/two
---
""",
                encoding="utf-8",
            )
            (reports / "2026-01-02_show_draft.md").write_text(
                "---\nstatus: in_progress\nsource_url: https://example.com/draft\n---\n",
                encoding="utf-8",
            )
            with mock.patch.object(sync_index_status, "REPORTS", reports):
                loaded = sync_index_status.load_reports()

        self.assertEqual(loaded["https://example.com/one"], ("2026-01-01", "show_episode"))
        self.assertIn("https://example.com/two", loaded)
        self.assertNotIn("https://example.com/draft", loaded)


if __name__ == "__main__":
    unittest.main()
