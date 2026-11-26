"""A self-authored web project for the product guide; no agent or provider calls."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parents[1]
CARDS = [
    {"id": 31, "title": "Agent 工作区指南", "description": "从分支到工作现场", "tag": "docs"},
    {"id": 12, "title": "Search API contract", "description": "Case-insensitive literal matching", "tag": "api"},
    {"id": 27, "title": "列表筛选界面", "description": "保留搜索条件并重置分页", "tag": "ui"},
    {"id": 8, "title": "Search review checklist", "description": "Verify stable ordering and API errors", "tag": "docs"},
    {"id": 43, "title": "中文搜索样本", "description": "Unicode 搜索与空查询", "tag": "api"},
    {"id": 5, "title": "Preview feedback", "description": "Select an element and describe the expected state", "tag": "ui"},
    {"id": 22, "title": "API integration tests", "description": "Search, tag filters and pagination", "tag": "api"},
    {"id": 17, "title": "变更审查记录", "description": "检查 diff、测试和验收条件", "tag": "docs"},
    {"id": 39, "title": "远程预览说明", "description": "确认浏览器和服务属于哪台机器", "tag": "docs"},
]


def search_cards(query="", tag="", page=1, page_size=4):
    if page < 1 or not 1 <= page_size <= 20:
        raise ValueError("page must be positive and page_size must be between 1 and 20")
    needle = query.strip().casefold()
    matched = [card for card in CARDS if (not tag or card["tag"] == tag) and (
        not needle or needle in (card["title"] + " " + card["description"]).casefold()
    )]
    start = (page - 1) * page_size
    return {"items": matched[start:start + page_size], "total": len(matched), "page": page, "pageSize": page_size}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path in ("/", "/index.html"):
            body = (ROOT / "web/index.html").read_bytes()
            self.respond(200, body, "text/html; charset=utf-8")
        elif url.path == "/api/cards":
            params = parse_qs(url.query)
            try:
                result = search_cards(params.get("q", [""])[0], params.get("tag", [""])[0], int(params.get("page", ["1"])[0]), int(params.get("page_size", ["4"])[0]))
                self.respond(200, json.dumps(result, ensure_ascii=False).encode(), "application/json; charset=utf-8")
            except ValueError as exc:
                self.respond(400, json.dumps({"error": str(exc)}).encode(), "application/json")
        else:
            self.respond(404, b'{"error":"not found"}', "application/json")

    def respond(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=4188)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Card Gallery: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
