import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_readme_links as links


class ReadmeLinksTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def write(self, name, content=""):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def check(self, text):
        self.write("README.md", text)
        return links.check_readme(self.root)

    def test_current_root_readme(self):
        self.assertEqual(links.check_readme(ROOT), [])

    def test_relative_bare_and_percent_encoded_links(self):
        self.write("docs/中文 文档.md", "# 标题 一\n")
        self.assertEqual(self.check('[ok](docs/%E4%B8%AD%E6%96%87%20%E6%96%87%E6%A1%A3.md#标题-一)\n'), [])
        self.assertTrue(self.check("[missing](bare.md)"))

    def test_self_anchor_and_duplicate_headings(self):
        self.assertEqual(self.check("# Heading\n# Heading\n[one](#heading) [two](#heading-1)"), [])
        self.assertTrue(self.check("# Heading\n[bad](#missing)"))

    def test_heading_formatting_unicode_and_setext(self):
        text = "# **中文** 与 `code`\nSetext\n====\n"
        self.assertEqual(self.check(text + "[a](#中文-与-code) [b](#setext)"), [])

    def test_explicit_html_anchors_and_named_anchors(self):
        self.assertEqual(self.check('<a id="custom"></a><a name="legacy"></a>\n[a](#custom) [b](#legacy)'), [])

    def test_html_media_src_srcset_and_poster(self):
        for name in ("small.jpg", "large.webp", "movie.mp4"):
            self.write(name)
        text = '<picture><source srcset="small.jpg 1x, large.webp 2x"><img src="large.webp"></picture>\n'
        text += '<video src="movie.mp4" poster="small.jpg"></video>'
        self.assertEqual(self.check(text), [])
        (self.root / "small.jpg").unlink()
        self.assertTrue(self.check(text))

    def test_srcset_without_whitespace_and_data_url(self):
        self.write("a.webp")
        self.write("b.webp")
        self.assertEqual(self.check('<img srcset="a.webp,b.webp">'), [])
        self.assertEqual(self.check('<img srcset="data:image/png;base64,AAAA 1x, a.webp 2x">'), [])
        self.assertTrue(self.check('<source srcset="a.webp 1x, missing.webp 2x">'))

    def test_media_html_entities(self):
        self.write("a&b.webp")
        self.assertEqual(self.check('<img src="a&amp;b.webp">'), [])

    def test_reference_links_and_missing_explicit_reference(self):
        self.write("target.md", "# Target\n")
        text = "[link][target] [target][] [target]\n\n[target]: target.md#target \"Title\"\n"
        self.assertEqual(self.check(text), [])
        self.assertTrue(self.check("[broken][unknown]"))
        self.assertEqual(self.check("[推测]"), [])

    def test_code_and_comments_do_not_create_links_or_anchors(self):
        text = "# Real\n```md\n# Fake\n[bad](missing.md)\n```\n"
        text += "~~~md\n[bad](missing.md)\n~~~\n"
        text += "`[bad](missing.md)`\n<!-- [bad](missing.md) -->\n"
        text += "    [bad](missing.md)\n"
        self.assertEqual(self.check(text), [])
        self.assertTrue(self.check(text + "[bad](#fake)"))

    def test_external_links_not_fetched(self):
        self.assertEqual(self.check('[a](https://invalid.example/a#no) [b](mailto:a@example.org)\n<img src="//invalid.example/a.png">'), [])

    def test_only_root_readme_links_not_target_report_body(self):
        self.write("report.md", "# Report\n[old broken link](historical.md)\n")
        self.assertEqual(self.check("[report](report.md#report)"), [])

    def test_linked_directory_anchor_uses_its_readme(self):
        self.write("project/README.md", "# Project\n")
        self.assertEqual(self.check("[project](project/#project)"), [])
        self.assertTrue(self.check("[project](project/#missing)"))

    def test_balanced_parentheses_angle_paths_and_titles(self):
        self.write("a(b).md")
        self.write("a space.md")
        self.assertEqual(self.check('[a](a(b).md "Title") [b](<a space.md> "Title")'), [])
        self.assertEqual(self.check(r"[a](a\(b\).md)"), [])

    def test_target_deletion_is_checked_even_without_readme_edits(self):
        target = self.write("target.md", "# Target")
        self.assertEqual(self.check("[target](target.md)"), [])
        target.unlink()
        self.assertTrue(links.check_readme(self.root))

    def test_outside_repository_and_symlink_target_are_not_read(self):
        self.assertTrue(self.check("[outside](../outside.md)"))
        (self.root / "link.md").symlink_to(self.root.parent / "outside.md")
        self.assertTrue(self.check("[outside](link.md#secret)"))
        project = self.root / "project"
        project.mkdir()
        (project / "README.md").symlink_to(self.root.parent / "outside.md")
        self.assertTrue(self.check("[outside](project/#secret)"))


if __name__ == "__main__":
    unittest.main()
