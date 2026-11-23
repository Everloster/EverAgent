import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "bilibili_inbox.py"
SPEC = importlib.util.spec_from_file_location("bilibili_inbox", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class BilibiliInboxTests(unittest.TestCase):
    def test_parse_duration(self):
        self.assertEqual(MODULE.parse_duration("04:29"), 269)
        self.assertEqual(MODULE.parse_duration("1:02:03"), 3723)
        self.assertEqual(MODULE.parse_duration(""), 0)
        self.assertEqual(MODULE.parse_duration("bad"), 0)

    def test_classify_watch(self):
        self.assertEqual(MODULE.classify_watch(None)[0], "unwatched")
        self.assertEqual(MODULE.classify_watch({"progress": 0, "duration": 100})[0], "opened")
        self.assertEqual(MODULE.classify_watch({"progress": 50, "duration": 100})[0], "partial")
        self.assertEqual(MODULE.classify_watch({"progress": -1, "duration": 100})[0], "finished")
        self.assertEqual(MODULE.classify_watch({"progress": 100, "duration": 100})[0], "finished")

    def test_build_inbox_filters_and_joins(self):
        videos = [
            {
                "dynamic_id": "102",
                "bvid": "BV-new",
                "title": "Long new video",
                "creator_mid": "1",
                "creator_name": "Creator A",
                "published_at": 9_900,
                "published_text": "recent",
                "duration_text": "20:00",
                "url": "https://www.bilibili.com/video/BV-new",
            },
            {
                "dynamic_id": "101",
                "bvid": "BV-seen",
                "title": "Seen video",
                "creator_mid": "2",
                "creator_name": "Creator B",
                "published_at": 9_800,
                "published_text": "recent",
                "duration_text": "30:00",
                "url": "https://www.bilibili.com/video/BV-seen",
            },
            {
                "dynamic_id": "100",
                "bvid": "BV-short",
                "title": "Short video",
                "creator_mid": "1",
                "creator_name": "Creator A",
                "published_at": 9_700,
                "published_text": "recent",
                "duration_text": "02:00",
                "url": "https://www.bilibili.com/video/BV-short",
            },
        ]
        history = [{"bvid": "BV-seen", "progress": 100, "duration": 1800}]
        recommended = [{"mid": "1", "name": "Creator A", "has_update": True}]
        rows = MODULE.build_inbox(
            videos,
            history,
            recommended,
            since_hours=1,
            min_duration_minutes=10,
            unwatched_only=True,
            recommended_only=True,
            limit=10,
            now_ts=10_000,
        )
        self.assertEqual([row["bvid"] for row in rows], ["BV-new"])
        self.assertTrue(rows[0]["official_update"])
        self.assertEqual(rows[0]["watch_state"], "unwatched")

    def test_incomplete_history_is_unknown_not_unwatched(self):
        videos = [
            {
                "bvid": "BV-unknown",
                "title": "Unknown history",
                "creator_mid": "1",
                "creator_name": "Creator",
                "published_at": 9_900,
                "published_text": "recent",
                "duration_text": "20:00",
                "url": "https://www.bilibili.com/video/BV-unknown",
            }
        ]
        common = dict(
            history=[],
            recommended_ups=[],
            since_hours=1,
            min_duration_minutes=10,
            recommended_only=False,
            limit=10,
            now_ts=10_000,
            history_complete=False,
        )
        rows = MODULE.build_inbox(videos, unwatched_only=False, **common)
        self.assertEqual(rows[0]["watch_state"], "unknown")
        self.assertEqual(MODULE.build_inbox(videos, unwatched_only=True, **common), [])

    def test_history_compatibility_wrapper_does_not_mix_view_and_publish_clocks(self):
        class Session:
            def eval(self, expression, timeout):
                self.expression = expression
                return {"items": [{"bvid": "BV1"}], "complete": True, "pages_read": 1}

        session = Session()
        rows = MODULE.fetch_history(session, pages=2, cutoff_ts=123, delay_ms=0)
        self.assertEqual(rows, [{"bvid": "BV1"}])
        self.assertNotIn("oldest<", session.expression)

    def test_markdown_render(self):
        text = MODULE.render_markdown(
            {
                "kind": "inbox",
                "title": "Inbox",
                "generated_at": "now",
                "items": [
                    {
                        "published_text": "today",
                        "creator_name": "A",
                        "title": "Title",
                        "url": "https://example.com",
                        "duration_text": "10:00",
                        "watch_state": "unwatched",
                        "official_update": True,
                    }
                ],
            }
        )
        self.assertIn("[Title](https://example.com)", text)
        self.assertIn("unwatched", text)


if __name__ == "__main__":
    unittest.main()
