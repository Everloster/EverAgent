import importlib.util
import datetime as dt
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import radar_common

RADARS = (
    "web-surfing/skills/ai-tech-blog-radar/scripts/radar.py",
    "podcast-learning/skills/ai-tech-podcast-radar/scripts/radar.py",
)


class RadarCommonTests(unittest.TestCase):
    def test_registry_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "registry.json"
            value = {"name": "渠道", "enabled": True}
            radar_common.write_json_atomic(path, value)
            self.assertEqual(radar_common.load_json(path), value)
            radar_common.write_json_atomic(path, {"enabled": False})
            self.assertEqual(radar_common.load_json(path), {"enabled": False})
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_serialization_failure_preserves_original_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "registry.json"
            path.write_text('{"original":true}\n')
            with self.assertRaises(TypeError):
                radar_common.write_json_atomic(path, {"bad": object()})
            self.assertEqual(path.read_text(), '{"original":true}\n')
            self.assertEqual(list(path.parent.iterdir()), [path])

    def test_dotted_values_keep_types_and_plain_strings(self):
        target = {}
        for assignment in ('enabled=true', 'limit=3', 'tags=["ai"]',
                           'discovery.kind=rss', 'query=x=y', 'optional=null'):
            radar_common.set_dotted(target, assignment)
        self.assertEqual(target, {"enabled": True, "limit": 3, "tags": ["ai"],
                                  "discovery": {"kind": "rss"}, "query": "x=y",
                                  "optional": None})

    def test_invalid_assignment_does_not_replace_scalar(self):
        for assignment in ("no-equals", "=value", "...=value", "tier.nested=watch"):
            with self.subTest(assignment=assignment):
                target = {"tier": "core"}
                with self.assertRaises(radar_common.RadarError):
                    radar_common.set_dotted(target, assignment)
                self.assertEqual(target, {"tier": "core"})

    def test_radars_share_helpers_and_keep_domain_semantics(self):
        modules = []
        for index, relative in enumerate(RADARS):
            spec = importlib.util.spec_from_file_location(f"radar_{index}", ROOT / relative)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules.append(module)
            for name in ("RadarError", "load_json", "write_json_atomic", "set_dotted"):
                self.assertIs(getattr(module, name), getattr(radar_common, name))
            self.assertEqual(module.validate_registry(module.load_json(module.DEFAULT_REGISTRY)), [])
        blog, podcast = modules
        self.assertEqual(blog.trim("a" * 500).__len__(), 260)
        self.assertEqual(podcast.trim("a" * 500).__len__(), 420)
        url = "https://example.org/x?uo=1&from=2&utm_source=test"
        self.assertEqual(blog.normalize_url(url), "https://example.org/x?uo=1")
        self.assertEqual(podcast.normalize_url(url), "https://example.org/x?from=2")

    def test_cli_works_from_outside_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            for relative in RADARS:
                with self.subTest(radar=relative):
                    run = subprocess.run(
                        [sys.executable, "-B", str(ROOT / relative), "channels", "validate", "--format", "json"],
                        cwd=directory, capture_output=True, text=True, timeout=30,
                    )
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertTrue(json.loads(run.stdout)["valid"])

    def test_request_ids_follow_eacli_contract_and_isolate_requests(self):
        instant = dt.datetime(2026, 11, 2, 5, tzinfo=dt.timezone.utc)
        for index, relative in enumerate(RADARS):
            with self.subTest(radar=relative):
                spec = importlib.util.spec_from_file_location(f"request_radar_{index}", ROOT / relative)
                radar = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(radar)
                with mock.patch.object(radar, "now_utc", return_value=instant):
                    request = radar.request_id("source-a", "https://example.org/feed")
                    self.assertRegex(request, r"^req_[0-9a-f]{32}$")
                    self.assertEqual(request, radar.request_id("source-a", "https://example.org/feed"))
                    self.assertNotEqual(request, radar.request_id("source-b", "https://example.org/feed"))
                    self.assertNotEqual(request, radar.request_id("source-a", "https://example.org/other"))
                with mock.patch.object(radar, "now_utc", return_value=instant + dt.timedelta(hours=1)):
                    self.assertNotEqual(request, radar.request_id("source-a", "https://example.org/feed"))

    def test_bounded_http_rejects_oversize_plain_and_gzip_responses(self):
        class Response:
            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, size):
                return self.payload[:size]

        for payload, limits in (
            (b"1234", {"max_bytes": 3, "max_decompressed_bytes": 20}),
            (gzip.compress(b"123456"), {"max_bytes": 100, "max_decompressed_bytes": 5}),
        ):
            with self.subTest(limits=limits), mock.patch.object(
                radar_common.urllib.request, "urlopen", return_value=Response(payload)
            ):
                with self.assertRaises(radar_common.RadarError):
                    radar_common.http_get(
                        "https://example.org/feed",
                        timeout=1,
                        user_agent="test",
                        accept="application/xml",
                        **limits,
                    )

    def test_domain_feed_parsers_keep_their_metadata(self):
        modules = []
        for index, relative in enumerate(RADARS):
            spec = importlib.util.spec_from_file_location(f"feed_radar_{index}", ROOT / relative)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            modules.append(module)
        blog, podcast = modules
        xml = """<?xml version="1.0"?><rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"><channel><item>
<title>Agent systems</title><link>https://example.org/post?utm_source=x&amp;from=2</link>
<guid>guide-1</guid><pubDate>Wed, 19 Aug 2026 00:00:00 GMT</pubDate>
<description><![CDATA[<p>Mechanism and benchmark</p>]]></description>
<enclosure url="https://cdn.example.org/a.mp3"/><itunes:duration>1:02:03</itunes:duration>
</item></channel></rss>"""
        source = {
            "id": "source", "vendor": "Example", "homepage": "https://example.org/",
            "feed_url": "https://example.org/feed", "allow_domains": [], "path_prefixes": [],
        }
        since = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
        blog_items = blog.parse_feed_text(xml, source, since)
        podcast_items = podcast.parse_feed_text(xml, source)
        self.assertEqual(blog_items[0]["published_at"], "2026-08-19T00:00:00+00:00")
        self.assertEqual(blog_items[0]["summary"], "Mechanism and benchmark")
        self.assertNotIn("from=2", blog_items[0]["url"])
        self.assertIn("from=2", podcast_items[0]["url"])
        self.assertEqual(podcast_items[0]["duration_seconds"], 3723)
        self.assertEqual(podcast_items[0]["audio_url"], "https://cdn.example.org/a.mp3")

        atom = """<feed xmlns="http://www.w3.org/2005/Atom"><entry>
<title>Namespaced</title><link href="https://example.org/atom"/>
<published>2026-08-20T00:00:00Z</published><summary>Summary</summary>
</entry></feed>"""
        self.assertEqual(blog.parse_feed_text(atom, source, since)[0]["url"], "https://example.org/atom")
        self.assertEqual(podcast.parse_feed_text(atom, source)[0]["published_at"], "2026-08-20T00:00:00+00:00")
        sitemap = """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url>
<loc>https://example.org/post</loc><lastmod>2026-08-20</lastmod></url></urlset>"""
        self.assertEqual(blog.parse_sitemap_text(sitemap)[0][0], "https://example.org/post")

    def test_studied_index_uses_only_declared_sources_and_completed_reports(self):
        spec = importlib.util.spec_from_file_location("studied_radar", ROOT / RADARS[1])
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            podcast_root = Path(directory) / "podcast-learning"
            reports = podcast_root / "reports"
            reports.mkdir(parents=True)
            (reports / "done.md").write_text(
                """---
title: Done episode
status: completed
source_url: https://example.org/episode
related: https://example.org/not-the-episode
---
""",
                encoding="utf-8",
            )
            (reports / "draft.md").write_text(
                "---\ntitle: Draft\nstatus: in_progress\nsource_url: https://example.org/draft\n---\n",
                encoding="utf-8",
            )
            with mock.patch.object(module, "PODCAST_ROOT", podcast_root), mock.patch.object(
                module, "REPORTS_DIR", reports
            ):
                urls, titles = module.load_studied_index()
        self.assertEqual(set(urls), {"https://example.org/episode"})
        self.assertEqual(titles["doneepisode"], "podcast-learning/reports/done.md")


if __name__ == "__main__":
    unittest.main()
