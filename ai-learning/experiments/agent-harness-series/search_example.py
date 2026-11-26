"""Self-authored project used by Agent 演义; no agents or network calls."""
import unittest


def search(records, query):
    """Return matching records in input order, using literal casefolded substrings."""
    needle = query.strip().casefold()
    if not needle:
        return []
    return [record for record in records if needle in record["title"].casefold()]


class SearchContract(unittest.TestCase):
    records = [
        {"id": 3, "title": "Claude 与搜索"},
        {"id": 1, "title": "CODEX notes"},
        {"id": 2, "title": "Codex 搜索实现"},
    ]

    def test_case_insensitive(self):
        self.assertEqual([r["id"] for r in search(self.records, "codex")], [1, 2])

    def test_chinese(self):
        self.assertEqual([r["id"] for r in search(self.records, "搜索")], [3, 2])

    def test_input_order(self):
        self.assertEqual([r["id"] for r in search(self.records, "C")], [3, 1, 2])

    def test_blank(self):
        self.assertEqual(search(self.records, "  "), [])

    def test_literal_substring(self):
        self.assertEqual(search(self.records, ".*"), [])


if __name__ == "__main__":
    unittest.main()
