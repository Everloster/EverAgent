import importlib.util
import datetime as dt
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


if __name__ == "__main__":
    unittest.main()
