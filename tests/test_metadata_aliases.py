import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import report_catalog


class MetadataAliasTests(unittest.TestCase):
    def test_known_aliases_are_normalized_without_mutating_input(self):
        for field, aliases in report_catalog.METADATA_ALIASES.items():
            for old, canonical in aliases.items():
                with self.subTest(field=field, alias=old):
                    raw = {field: old, "title": "历史资料"}
                    normalized = report_catalog.normalize_metadata(raw)
                    self.assertEqual(normalized[field], canonical)
                    self.assertEqual(raw[field], old)
                    self.assertEqual(len(report_catalog.metadata_alias_issues(raw)), 1)
                    self.assertEqual(report_catalog.metadata_alias_issues(normalized), [])

    def test_unknown_values_and_missing_fields_are_not_invented(self):
        for raw in ({}, {"report_type": "report"}, {"status": None},
                    {"report_type": ["concept_report"]}):
            with self.subTest(raw=raw):
                self.assertEqual(report_catalog.normalize_metadata(raw), raw)
                self.assertEqual(report_catalog.metadata_alias_issues(raw), [])

    def test_parser_preserves_raw_metadata_for_quality_checks(self):
        raw = report_catalog.parse_frontmatter(
            '---\nstatus: "done"\nreport_type: "concept_deep_dive"\n---\n'
        )
        self.assertEqual(raw["status"], "done")
        self.assertEqual(raw["report_type"], "concept_deep_dive")

    def test_report_info_exposes_both_views_without_rewriting_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.md"
            original = ('---\ntitle: "旧报告"\nstatus: "complete"\n'
                        'report_type: "概念深度解析"\n---\n\n正文\n').encode()
            path.write_bytes(original)
            info = report_catalog.report_info(path, fallback_updated_on="2026-06-01")
            self.assertEqual(info["metadata"]["status"], "completed")
            self.assertEqual(info["metadata"]["report_type"], "concept_report")
            self.assertEqual(info["raw_metadata"]["status"], "complete")
            self.assertEqual(info["updated_on"], "2026-06-01")
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
