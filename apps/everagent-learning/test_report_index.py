#!/usr/bin/env python3
"""Tests for the learning board's fixed entries and their rendering.

Run from the package root:
    python3 -m unittest test_report_index -v

The suite builds one synthetic public checkout, so it never depends on the
state of the real repository.
"""
from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile
import unittest

PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE_ROOT / "miniapp" / "node"))

import report_index  # noqa: E402
from markdown_render import render_markdown  # noqa: E402
from html.parser import HTMLParser


class MarkdownFootnoteTests(unittest.TestCase):
    def test_notes_have_working_round_trip_links(self) -> None:
        rendered = render_markdown('第一次[^source]，第二次[^source]。\n\n[^source]: [原文](https://example.com/paper)\n    后续说明。')
        self.assertIn('<li id="fn-source">', rendered)
        self.assertIn('href="#fnref-source-1"', rendered)
        self.assertIn('href="#fnref-source-2"', rendered)
        self.assertIn('后续说明。', rendered)
        self.assertNotIn('[^source]', rendered)
        self.assertNotIn('href="#fn-source" target="_blank"', rendered)

    def test_code_examples_and_undefined_notes_remain_literal(self) -> None:
        rendered = render_markdown('```md\n[^demo]: 示例\n```\n\n`[^real]` 与未知[^missing]。\n\n[^real]: 隐藏的未引用注释')
        self.assertIn('[^demo]: 示例', rendered)
        self.assertIn('<code>[^real]</code>', rendered)
        self.assertIn('[^missing]', rendered)
        self.assertNotIn('class="footnotes"', rendered)

    def test_safe_anchors_work_without_enabling_raw_html(self) -> None:
        rendered = render_markdown('<a id="section-one"></a>\n\n[跳转](#section-one)\n\n<a id="bad" onclick="alert(1)"></a>\n<script>alert(1)</script>')
        self.assertIn('<a id="section-one"></a>', rendered)
        self.assertIn('<a href="#section-one">跳转</a>', rendered)
        self.assertNotIn('<a id="bad"', rendered)
        self.assertNotIn('<script>', rendered)

    def test_footnote_content_uses_the_same_safety_and_link_resolver(self) -> None:
        rendered = render_markdown('正文[^a]\n\n[^a]: <script>alert(1)</script> [危险](javascript:alert) [报告](other.md)', link_resolver=lambda url: '/report/other' if url == 'other.md' else url)
        self.assertNotIn('<script>', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertIn('href="/report/other"', rendered)

    def test_every_rendered_fragment_has_a_real_dom_target(self) -> None:
        class Links(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids = []
                self.fragments = []

            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if 'id' in attrs:
                    self.ids.append(attrs['id'])
                if attrs.get('href', '').startswith('#'):
                    self.fragments.append(attrs['href'][1:])

        parsed = Links()
        parsed.feed(render_markdown('<a id="chapter"></a>\n## 章节\n[章节](#chapter) 和资料[^中文]。\n\n[^中文]: 引用说明。'))
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        self.assertTrue(set(parsed.fragments).issubset(set(parsed.ids)))


STUB_CATALOG = '''\
"""Minimal stand-in for the public repository's report catalog."""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


class ReportCollection:
    def __init__(self, id, title, root):
        self.id = id
        self.title = title
        self.root = root


COLLECTIONS = (
    ReportCollection("podcast-learning", "Podcast Learning", "podcast-learning/reports"),
    ReportCollection("web-surfing", "Web Surfing", "web-surfing/reports"),
)


def iter_reports(domain=None):
    for collection in COLLECTIONS:
        base = ROOT / collection.root
        if not base.exists():
            continue
        for path in sorted(base.glob("**/*.md")):
            yield collection, path


def collection_for_path(path):
    resolved = path.resolve()
    for collection in COLLECTIONS:
        base = (ROOT / collection.root).resolve()
        try:
            resolved.relative_to(base)
        except ValueError:
            continue
        return collection
    return None


def report_info(path):
    return {"title": path.stem, "updated_on": "2026-01-01", "tags": [], "metadata": {}}
'''

PODCAST_LIST = """\
# 小宇宙精选播客历史速看表

最近检查：**2026-11-02**

<details open>
<summary><strong>展开 / 收起本周全部更新</strong></summary>

- **11-02** [某期节目](https://example.com/a) · 未做

</details>

<details>
<summary><strong>另一档节目</strong></summary>

- **11-01** [某期节目](https://example.com/b) · 已学习

</details>
"""

BLOG_LIST = """\
# 顶尖技术博客更新

**最近检查：2026-11-02**

<details>
<summary><strong>GitHub AI &amp; ML · 4 篇</strong></summary>

- **11-02** [某篇文章](https://example.com/c) · 未做

</details>
"""

REGULAR_REPORT = """\
---
title: 普通报告
---

正文有 **加粗** 与 <script>alert(1)</script> 原始标签。
"""

STRICT_REPORT = """\
普通报告里有字面量 &amp; 与 <details> 字样。
"""


class FixedEntryTest(unittest.TestCase):
    """The board must offer the two living lists and render them faithfully."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = pathlib.Path(tempfile.mkdtemp(prefix="everagent-learning-test-"))
        (cls.root / "scripts").mkdir(parents=True)
        (cls.root / "scripts" / "report_catalog.py").write_text(
            STUB_CATALOG, encoding="utf-8"
        )
        (cls.root / "podcast-learning" / "reports").mkdir(parents=True)
        (cls.root / "podcast-learning" / "PODCAST_UPDATES.md").write_text(
            PODCAST_LIST, encoding="utf-8"
        )
        (cls.root / "podcast-learning" / "reports" / "regular.md").write_text(
            REGULAR_REPORT, encoding="utf-8"
        )
        (cls.root / "web-surfing" / "reports").mkdir(parents=True)
        (cls.root / "web-surfing" / "TECH_BLOG_UPDATES.md").write_text(
            BLOG_LIST, encoding="utf-8"
        )
        (cls.root / "web-surfing" / "reports" / "plain.md").write_text(
            STRICT_REPORT, encoding="utf-8"
        )
        # A real file outside every collection, so the path is safe but the
        # document is not a report.
        (cls.root / "README.md").write_text("# 公开仓\n", encoding="utf-8")

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_list_exposes_both_fixed_entries(self) -> None:
        payload = report_index.build_list(self.root)
        paths = [item["path"] for item in payload["pins"]]
        self.assertEqual(
            paths,
            [
                "podcast-learning/PODCAST_UPDATES.md",
                "web-surfing/TECH_BLOG_UPDATES.md",
            ],
        )
        titles = {item["id"]: item["title"] for item in payload["pins"]}
        self.assertEqual(titles["podcast-updates"], "小宇宙精选播客")
        self.assertEqual(titles["tech-blog-updates"], "顶尖技术博客")

    def test_fixed_entry_renders_folds(self) -> None:
        payload = report_index.build_detail(
            self.root, "podcast-learning/PODCAST_UPDATES.md"
        )
        report = payload["report"]
        self.assertEqual(report["title"], "小宇宙精选播客")
        self.assertTrue(report["pinned"])
        self.assertEqual(report["html"].count("<details"), 2)
        self.assertEqual(report["html"].count("<summary>"), 2)
        self.assertIn("<details open>", report["html"])
        self.assertNotIn("&lt;details", report["html"])

    def test_fixed_entry_decodes_entities_once(self) -> None:
        payload = report_index.build_detail(
            self.root, "web-surfing/TECH_BLOG_UPDATES.md"
        )
        html = payload["report"]["html"]
        self.assertIn("GitHub AI &amp; ML", html)
        self.assertNotIn("&amp;amp;", html)

    def test_regular_reports_keep_strict_escaping(self) -> None:
        payload = report_index.build_detail(self.root, "podcast-learning/reports/regular.md")
        html = payload["report"]["html"]
        self.assertNotIn("<details", html)
        self.assertNotIn("<script", html)
        self.assertIn("&lt;script&gt;", html)

    def test_regular_report_keeps_literal_entities(self) -> None:
        payload = report_index.build_detail(self.root, "web-surfing/reports/plain.md")
        html = payload["report"]["html"]
        # A regular report is plain text: "&amp;" stays literal and a raw tag
        # stays visible text instead of becoming an element.
        self.assertIn("&amp;amp;", html)
        self.assertIn("&lt;details&gt;", html)
        self.assertNotIn("<details", html)

    def test_unknown_document_is_rejected(self) -> None:
        payload = report_index.build_detail(self.root, "README.md")
        self.assertEqual(payload.get("error"), "unknown_collection")

    def test_unsafe_path_is_rejected(self) -> None:
        payload = report_index.build_detail(self.root, "../../etc/passwd.md")
        self.assertEqual(payload.get("error"), "unsafe_path")


if __name__ == "__main__":
    unittest.main()
