"""编辑修订只继承未变的复核；所有身份和材料均为隔离测试样本。"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import report_catalog
import report_quality as quality


class EditorialRevisionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        for module in (report_catalog, quality):
            patch = mock.patch.object(module, "ROOT", self.root)
            patch.start()
            self.addCleanup(patch.stop)
        self.git("init", "-q")
        self.git("config", "user.name", "Editorial fixture")
        self.git("config", "user.email", "fixture@example.org")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.report = self.root / "ai-learning/reports/editing.md"
        self.report.parent.mkdir(parents=True)
        self.report.write_text("""---
title: 编辑样本
domain: ai-learning
report_type: concept_report
status: in_progress
updated_on: 2026-11-01
quality_schema: report-v2
quality_tier: important
semantic_tags: [test]
description: |
  不会自动扩大结论。
---
# 编辑样本

结论一：样本包含32项。
结论二：实验不会改变原文。
结论三：证据仅支持当前范围。

## 适用范围 [原文][source-a]

这是排版示例。
[资料](https://example.org/a)
[source-a]: https://example.org/a
[source-b]: https://example.org/b

~~~python
print(32)
~~~

$$
a = 32
$$

<div>
**原样内容**
</div>
""", encoding="utf-8")
        self.source = self.root / "source.txt"
        self.source.write_text("纯测试来源：32项。", encoding="utf-8")
        self.evidence_path, self.review_path = quality.quality_artifact_paths(self.report)
        relative = str(self.report.relative_to(self.root))
        self.policy = quality.load_policy()
        evidence = {
            "schema_version": 1, "report_path": relative, "quality_tier": "important",
            "created_on": "2026-11-01",
            "generator": {"model": "glm-5.3", "harness": "fixture", "run_id": "fixture-generator",
                          "explicit_model_override": False},
            "task": {"summary": "编辑继承的离线测试", "requirements": [{"id": "R01", "text": "不改变事实"}]},
            "sources": [
                {"id": "S01", "kind": "official", "title": "测试来源", "locator": "https://example.org/a", "accessed_on": "2026-11-01"},
                {"id": "S02", "kind": "local", "title": "测试原文", "locator": "source.txt", "accessed_on": "2026-11-01"},
            ],
            "claims": [
                {"id": f"C0{i}", "claim": anchor, "report_anchor": anchor,
                 "support": "direct", "source_ids": ["S01", "S02"], "evidence": "仅用于隔离回归的模拟证据", "critical": True}
                for i, anchor in enumerate(("样本包含32项", "实验不会改变原文", "证据仅支持当前范围"), 1)
            ],
            "limitations": ["仅为合成测试样本，不代表真实报告审稿"],
        }
        review = {
            "schema_version": 1, "report_path": relative, "quality_tier": "important", "revision_round": 1,
            "reviews": [{
                "role": "primary_review",
                "reviewer": {"model": "glm-5.3", "harness": "fixture", "run_id": "fixture-review",
                             "independent_context": True, "explicit_model_override": False},
                "scores": {key: 95 for key in self.policy["dimensions"]},
                "score_reasons": {key: "隔离测试的模拟通过结论" for key in self.policy["dimensions"]},
                "critical_claim_ids_checked": ["C01", "C02", "C03"], "source_ids_checked": ["S01", "S02"],
                "requirement_ids_checked": ["R01"], "unsupported_claims": [], "missing_requirements": [],
                "hard_failures": [], "notes": "这不是生产审稿记录。",
                "reviewed_snapshot": hashlib.sha256(self.report.read_bytes()).hexdigest(),
            }],
            "decision": {},
        }
        quality._write_json(self.evidence_path, evidence)
        quality._write_json(self.review_path, review)
        result = quality.evaluate_report(self.report)
        self.assertEqual(result["decision"], "pass", result["errors"])
        quality._set_frontmatter_fields(self.report, {"status": "completed"})
        review["decision"] = quality._decision_record(result, self.policy, self.report, self.evidence_path)
        quality._write_json(self.review_path, review)
        self.assertEqual(quality.evaluate_report(self.report)["decision"], "pass")
        self.git("add", "--all")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "编辑继承测试基线\n\nCo-Authored-By: Aiden")
        self.original = self.report.read_text(encoding="utf-8")
        self.old_review = self.review_path.read_bytes()
        self.old_evidence = self.evidence_path.read_bytes()

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.PIPE).decode().strip()

    def formatting_change(self):
        self.report.write_text(
            self.original.replace("这是排版示例。", "**这是排版示例。**  \n\n")
            .replace("## 适用范围", "### 适用范围").replace("2026-11-01", "2026-11-02"),
            encoding="utf-8",
        )

    def heading_change(self):
        self.report.write_text(self.original.replace("编辑样本", "更清晰的编辑样本"), encoding="utf-8")

    def delta(self):
        result = quality.refresh_editorial(self.report, dry_run=True)
        return {
            **{key: result[key] for key in ("base_report_sha256", "report_sha256", "evidence_sha256")},
            "reviewer": {"model": "glm-5.3", "harness": "fixture", "run_id": "fixture-delta",
                         "independent_context": True},
            "assessment": "pass", "notes": "模拟复核：仅换标题表述，没有扩张正文结论。",
        }

    def assert_review_unchanged(self):
        self.assertEqual(self.review_path.read_bytes(), self.old_review)

    def test_formatting_rebinds_without_changing_reviews_scores_or_snapshot(self):
        self.formatting_change()
        result = quality.refresh_editorial(self.report)
        self.assertEqual(result["kind"], "format_only")
        before, after = json.loads(self.old_review), quality._load_json(self.review_path)
        for key in ("reviews", "revision_round"):
            self.assertEqual(after[key], before[key])
        for key in ("score", "policy_id", "policy_sha256", "evaluated_on", "evidence_sha256"):
            self.assertEqual(after["decision"][key], before["decision"][key])
        self.assertEqual(self.evidence_path.read_bytes(), self.old_evidence)
        self.assertEqual(after["decision"]["report_sha256"], hashlib.sha256(self.report.read_bytes()).hexdigest())
        self.assertEqual(quality.evaluate_report(self.report)["decision"], "pass")

    def test_heading_change_requires_only_a_snapshot_bound_delta_review(self):
        self.heading_change()
        dry_run = quality.refresh_editorial(self.report, dry_run=True)
        self.assertEqual(dry_run["kind"], "headings_only")
        self.assertTrue(dry_run["requires_delta_review"])
        self.assertFalse(dry_run["written"])
        self.assert_review_unchanged()
        with self.assertRaisesRegex(ValueError, "差异复核"):
            quality.refresh_editorial(self.report)
        self.assert_review_unchanged()
        delta_path = self.root / "delta.json"
        quality._write_json(delta_path, self.delta())
        self.assertTrue(quality.refresh_editorial(self.report, review_file=delta_path)["written"])
        after = quality._load_json(self.review_path)
        self.assertEqual(after["reviews"], json.loads(self.old_review)["reviews"])
        self.assertEqual(after["editorial_update"]["delta_review"], quality._load_json(delta_path))
        self.assertEqual(quality.evaluate_report(self.report)["decision"], "pass")

    def test_wrong_snapshot_self_review_and_disabled_model_are_rejected(self):
        self.heading_change()
        for mutate in (
            lambda item: item.update(report_sha256="0" * 64),
            lambda item: item.update(base_report_sha256="0" * 64),
            lambda item: item.update(evidence_sha256="0" * 64),
            lambda item: item.update(assessment="fail"),
            lambda item: item.update(notes=""),
            lambda item: item.update(notes=["不是文本"]),
            lambda item: item["reviewer"].update(run_id="fixture-generator"),
            lambda item: item["reviewer"].update(model=123),
            lambda item: item["reviewer"].update(independent_context=False),
            lambda item: item["reviewer"].update(model="minimax-m3"),
        ):
            with self.subTest(mutate=mutate):
                delta = self.delta()
                mutate(delta)
                path = self.root / "delta.json"
                quality._write_json(path, delta)
                with self.assertRaises(ValueError):
                    quality.refresh_editorial(self.report, review_file=path)
                self.assert_review_unchanged()

    def test_facts_code_math_html_metadata_and_citation_changes_are_not_editorial(self):
        for old, new in (
            ("包含32项", "包含64项"), ("实验不会", "实验会"), ("print(32)", "print(64)"),
            ("a = 32", "a = 64"), ("**原样内容**", "原样内容"),
            ("这是排版示例。", "这不是排版示例。"),
            ("不会自动扩大结论。", "会自动扩大结论。"),
            ("[资料](https://example.org/a)", "[资料](https://example.org/b)"),
            ("[原文][source-a]", "[原文][source-b]"),
            ("quality_tier: important", "quality_tier: standard"),
        ):
            with self.subTest(old=old):
                self.report.write_text(self.original.replace(old, new), encoding="utf-8")
                with self.assertRaises(ValueError):
                    quality.refresh_editorial(self.report, dry_run=True)
                self.assert_review_unchanged()

    def test_changed_evidence_scores_and_decision_cannot_be_silently_restored(self):
        self.formatting_change()
        self.evidence_path.write_bytes(self.old_evidence + b"\n")
        with self.assertRaisesRegex(ValueError, "证据或原复核"):
            quality.refresh_editorial(self.report)
        self.assert_review_unchanged()
        self.evidence_path.write_bytes(self.old_evidence)
        for mutate in (
            lambda review: review["reviews"][0]["scores"].update(readability=100),
            lambda review: review["decision"].update(score=100),
        ):
            review = json.loads(self.old_review)
            mutate(review)
            quality._write_json(self.review_path, review)
            before = self.review_path.read_bytes()
            with self.assertRaises(ValueError):
                quality.refresh_editorial(self.report)
            self.assertEqual(self.review_path.read_bytes(), before)

    def test_failed_candidate_validation_never_writes_a_partial_record(self):
        self.formatting_change()
        self.source.unlink()
        with self.assertRaisesRegex(ValueError, "质量错误"):
            quality.refresh_editorial(self.report)
        self.assert_review_unchanged()

    def test_multiline_inline_code_cannot_be_mistaken_for_editable_headings(self):
        text = self.original + "\n" + chr(96) + "code\n# not a heading\n" + chr(96) + "\n"
        with self.assertRaisesRegex(ValueError, "行内代码"):
            quality._editorial_projection(text, headings=True)

    def test_files_changing_during_validation_are_not_overwritten(self):
        self.formatting_change()
        evaluate = quality.evaluate_report
        def concurrent_edit(*args, **kwargs):
            result = evaluate(*args, **kwargs)
            self.report.write_text(self.report.read_text() + "\n另一个写入。\n", encoding="utf-8")
            return result
        with mock.patch.object(quality, "evaluate_report", side_effect=concurrent_edit):
            with self.assertRaisesRegex(ValueError, "期间变化"):
                quality.refresh_editorial(self.report)
        self.assert_review_unchanged()

    def test_editorial_binding_is_checked_and_archived_on_substantive_revision(self):
        self.formatting_change()
        quality.refresh_editorial(self.report)
        after = quality._load_json(self.review_path)
        corrupted = json.loads(json.dumps(after))
        corrupted["editorial_update"]["report_sha256"] = "0" * 64
        quality._write_json(self.review_path, corrupted)
        result = quality.evaluate_report(self.report)
        self.assertIn("QG017", {item["code"] for item in result["errors"]})
        quality._write_json(self.review_path, after)
        quality.start_new_revision(self.report)
        revision = quality._load_json(self.review_path)
        self.assertEqual(revision["history"][-1]["editorial_update"], after["editorial_update"])
        self.assertEqual(revision["reviews"], [])
        self.assertEqual(revision["revision_round"], 2)
        self.assertNotIn("editorial_update", revision)

    def test_invalid_or_unbound_base_cannot_authorize_editorial_updates(self):
        self.formatting_change()
        with self.assertRaises(subprocess.CalledProcessError):
            quality.refresh_editorial(self.report, base="not-a-commit")
        self.assert_review_unchanged()
        review = json.loads(self.old_review)
        review["decision"]["report_sha256"] = "0" * 64
        quality._write_json(self.review_path, review)
        self.report.write_text(self.original, encoding="utf-8")
        self.git("add", "--all")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "未绑定测试基线\n\nCo-Authored-By: Aiden")
        self.formatting_change()
        with self.assertRaisesRegex(ValueError, "基线"):
            quality.refresh_editorial(self.report)

    def test_podcast_source_coverage_still_blocks_missing_or_omitted_core_content(self):
        metadata = report_catalog.parse_frontmatter(self.original)
        metadata.update(domain="podcast-learning", report_depth="deep",
                        source_shownotes_chapters="true", chapters="3")
        evidence = json.loads(self.old_evidence)
        findings, _ = quality.validate_evidence_manifest(self.report, metadata, evidence, self.policy)
        self.assertIn("EVM036", {item.code for item in findings})
        evidence["source_coverage"] = [
            {"id": f"U0{i}", "title": claim["claim"], "importance": "core", "status": "included",
             "source_ids": ["S01"], "report_anchor": claim["report_anchor"]}
            for i, claim in enumerate(evidence["claims"], 1)
        ]
        findings, summary = quality.validate_evidence_manifest(self.report, metadata, evidence, self.policy)
        self.assertEqual(findings, [])
        review = json.loads(self.old_review)
        findings, _ = quality.validate_review_record(self.report, metadata, review, summary, self.policy)
        self.assertIn("REV028", {item.code for item in findings})
        item = review["reviews"][0]
        item["coverage_unit_ids_checked"] = ["U01", "U02", "U03"]
        item["source_content_map"] = [
            {"id": f"M0{i}", "title": unit["title"], "importance": "core", "assessment": "covered",
             "source_ids": ["S01"], "matched_coverage_unit_ids": [unit["id"]], "notes": "模拟来源核对"}
            for i, unit in enumerate(evidence["source_coverage"], 1)
        ]
        findings, _ = quality.validate_review_record(self.report, metadata, review, summary, self.policy)
        self.assertEqual(findings, [])
        evidence["source_coverage"][0].update(status="omitted", omission_reason="模拟遗漏")
        findings, _ = quality.validate_evidence_manifest(self.report, metadata, evidence, self.policy)
        self.assertIn("EVM044", {item.code for item in findings})
        item["source_content_map"][0]["assessment"] = "partial"
        findings, _ = quality.validate_review_record(self.report, metadata, review, summary, self.policy)
        self.assertIn("REV033", {item.code for item in findings})


if __name__ == "__main__":
    unittest.main()
