"""Integration tests for the self-authored example, not an agent benchmark."""
import importlib.util
import json
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

spec = importlib.util.spec_from_file_location("demo_server", Path(__file__).resolve().parents[1] / "api/server.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ApiContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = module.ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def get(self, query):
        with urllib.request.urlopen(self.base + "/api/cards?" + query) as response:
            return json.load(response)

    def test_blank_keeps_source_order(self):
        self.assertEqual([item["id"] for item in self.get("")["items"]], [31, 12, 27, 8])

    def test_case_insensitive_title_and_description(self):
        self.assertEqual(self.get("q=SEARCH")["total"], 3)

    def test_chinese(self):
        self.assertEqual(self.get("q=%E4%B8%AD%E6%96%87")["total"], 1)

    def test_tag_and_search(self):
        self.assertEqual([item["id"] for item in self.get("q=search&tag=docs")["items"]], [8])

    def test_literal_not_regex(self):
        self.assertEqual(self.get("q=.*")["total"], 0)

    def test_pagination(self):
        self.assertEqual([item["id"] for item in self.get("page=2")["items"]], [43, 5, 22, 17])

    def test_invalid_page(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.get("page=0")
        with error.exception:
            self.assertEqual(error.exception.code, 400)

    def test_ui_is_served(self):
        with urllib.request.urlopen(self.base + "/") as response:
            self.assertIn(b'id="search"', response.read())

    def test_unknown_path(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(self.base + "/missing")
        with error.exception:
            self.assertEqual(error.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
