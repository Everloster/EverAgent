"""Verify complete series Markdown/HTML and image delivery through the learning reader."""
import argparse
import concurrent.futures
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--base", default="http://127.0.0.1:4173")
args = parser.parse_args()
base = args.base.rstrip("/")
root = Path(__file__).resolve().parents[3]


def get(endpoint, **query):
    url = base + endpoint + "?" + urllib.parse.urlencode(query)
    with urllib.request.urlopen(url, timeout=20) as response:
        return response.read(), response.headers.get("content-type", "")


index = json.loads(get("/api/reports", refresh=1)[0])
files = sorted((root / "ai-learning/reports").glob("Agent演义_*.md"))
files += sorted((root / "ai-learning/reports/knowledge_reports").glob("Agent演义_*.md"))
assert len(files) == 23, "Expected 20 main reports and 3 technical appendices"
expected = {str(file.relative_to(root)) for file in files}
assert expected <= {report["path"] for report in index["reports"]}


def verify(file):
    path = str(file.relative_to(root))
    payload = json.loads(get("/api/report", path=path)[0])
    report = payload["report"]
    body = re.sub(r"^---\n.*?\n---\n", "", file.read_text(), count=1, flags=re.S).strip()
    assert body.index("## 概述") < body.index("## 取景框 f(x)"), path
    definitions = set(re.findall(r"^\[\^([^\]]+)\]:", body, re.M))
    references = set(re.findall(r"\[\^([^\]]+)\](?!:)", body))
    assert references <= definitions, f"Undefined sources: {path}: {references - definitions}"
    for target in re.findall(r"\]\(([^\s)]+)\)", body):
        if target.startswith(("http:", "https:", "#")):
            continue
        local = file.parent / urllib.parse.unquote(target.split("#", 1)[0])
        assert local.exists(), f"Broken local link: {path}: {target}"
    assert report["markdown"].strip() == body, f"Incomplete Markdown: {path}"
    assert "概述" in report["html"] and "取景框 f(x)" in report["html"], path
    if re.search(r"^\|[- :|]+\|$", body, re.M):
        assert "<table" in report["html"], f"Missing table: {path}"
    if "```" in body:
        assert "<pre" in report["html"], f"Missing code block: {path}"
    if "![" in body:
        assert "<img" in report["html"], f"Missing figure: {path}"
    return {"path": path, "completeMarkdown": True, "htmlCharacters": len(report["html"])}


details = list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(verify, files))
assets = []
source_svg = []
for file in sorted((root / "ai-learning/reports/paper_assets/agent-yanyi").glob("*")):
    if file.suffix == ".svg":
        assert ET.parse(file).getroot().tag.endswith("svg"), file.name
        source_svg.append(file.name)
        continue
    if file.suffix != ".png":
        continue
    data, mime = get("/api/asset", path=str(file.relative_to(root)))
    assert data == file.read_bytes(), f"Incomplete asset: {file.name}"
    assets.append({"asset": file.name, "mime": mime, "bytes": len(data)})
print(json.dumps({"reports": len(details), "completeMarkdown": True, "readerPngAssets": len(assets), "sourceSvgValid": len(source_svg), "details": details}, ensure_ascii=False, indent=2))
