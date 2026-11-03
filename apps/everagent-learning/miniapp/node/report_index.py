#!/usr/bin/env python3
"""Discover EverAgent learning reports through the public repo's own catalog.

The Mini App must not re-implement report discovery: the public repository
owns the collection list, the exclusion rules and the frontmatter parser in
``scripts/report_catalog.py``. This script only adds a JSON projection and a
single-report detail view on top of that canonical module.

Usage:
    report_index.py <repo-root> list
    report_index.py <repo-root> detail <repo-relative-report-path>
"""

from __future__ import annotations

import json
import base64
import importlib.util
import pathlib
import posixpath
import re
import sys
from urllib.parse import quote, unquote, urlsplit

from markdown_render import render_markdown

MAX_DETAIL_BYTES = 2 * 1024 * 1024
MAX_PINNED_BYTES = MAX_DETAIL_BYTES
PUBLIC_BASE = "https://github.com/Everloster/EverAgent"
ASSET_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
HEADING_LIMIT = 40

# Fixed entries the board always offers next to the report list.
#
# These are living lists the public repository maintains on its own schedule.
# They sit outside every report collection, so the catalog never lists them,
# and they carry no frontmatter, so they need their own identity here.
PINNED_DOCS = (
    {
        "id": "podcast-updates",
        "path": "podcast-learning/PODCAST_UPDATES.md",
        "title": "小宇宙精选播客历史速看表",
        "domain": "podcast-learning",
        "domain_title": "播客学习",
        "note": "近期单集与已有报告",
    },
    {
        "id": "tech-blog-updates",
        "path": "web-surfing/TECH_BLOG_UPDATES.md",
        "title": "顶尖技术博客更新",
        "domain": "web-surfing",
        "domain_title": "Web 冲浪",
        "note": "近期文章与已有报告",
    },
)

PINNED_BY_PATH = {item["path"]: item for item in PINNED_DOCS}


def fail(code: str) -> "None":
    json.dump({"ok": False, "error": code}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return None


def emit(payload: dict) -> None:
    json.dump({"ok": True, **payload}, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")


def load_catalog(root: pathlib.Path):
    source = safe_file(root, "scripts/report_catalog.py")
    if source is None:
        raise FileNotFoundError("catalog")
    name = "everagent_learning_catalog"
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def blob_url(base: str, relative: str) -> str:
    return f"{base}/blob/main/{quote(relative, safe='/')}"


def safe_file(root: pathlib.Path, relative: str) -> pathlib.Path | None:
    """Reject hidden paths, traversal, and symlink/hardlink escapes before reading."""
    if not relative or "\\" in relative or "\x00" in relative or relative.startswith("/"):
        return None
    parts = relative.split("/")
    if any(not part or part in (".", "..") or part.startswith(".") for part in parts):
        return None
    candidate = root / relative
    try:
        if candidate.resolve(strict=True) != candidate or not candidate.is_file():
            return None
        if candidate.stat().st_nlink != 1:
            return None
    except (OSError, ValueError):
        return None
    return candidate


def safe_report_path(root: pathlib.Path, relative: str) -> pathlib.Path | None:
    return safe_file(root, relative) if relative.endswith(".md") else None


def public_url(value: object) -> str:
    """Only absolute Web links without credentials are suitable for the reader."""
    text = str(value or "")
    if any(ord(char) < 32 for char in text) or "\\" in text:
        return ""
    try:
        parsed = urlsplit(text)
        if parsed.scheme in ("http", "https") and parsed.hostname and not parsed.username and not parsed.password:
            return text
    except ValueError:
        pass
    return ""


def project(catalog, collection, path: pathlib.Path, root: pathlib.Path, base: str) -> dict:
    info = catalog.report_info(path)
    metadata = info.get("metadata") if isinstance(info.get("metadata"), dict) else {}
    relative = path.relative_to(root).as_posix()
    tags = metadata.get("semantic_tags") or info.get("tags") or []
    return {
        "id": relative,
        "domain": collection.id,
        "domain_title": collection.title,
        "path": relative,
        "title": str(info.get("title") or path.stem),
        "updated_on": str(info.get("updated_on") or ""),
        "created": str(metadata.get("created") or ""),
        "status": str(metadata.get("status") or ""),
        "quality_tier": str(metadata.get("quality_tier") or ""),
        "report_depth": str(metadata.get("report_depth") or ""),
        "report_type": str(metadata.get("report_type") or ""),
        "source": str(metadata.get("source") or ""),
        "source_url": public_url(metadata.get("source_url")),
        "show": str(metadata.get("show") or ""),
        "episode": str(metadata.get("episode") or ""),
        "tags": [str(tag) for tag in tags][:6],
        "github_url": blob_url(base, relative),
    }


def build_list(root: pathlib.Path) -> dict:
    root = root.resolve()
    catalog = load_catalog(root)
    base = PUBLIC_BASE
    reports = []
    for collection, path in catalog.iter_reports():
        try:
            relative = path.relative_to(root).as_posix()
            if safe_report_path(root, relative) is None:
                continue
            reports.append(project(catalog, collection, path, root, base))
        except (OSError, ValueError):
            continue
    reports.sort(key=lambda row: (row["updated_on"], row["path"]), reverse=True)
    domains = []
    seen = {}
    for collection in catalog.COLLECTIONS:
        count = sum(1 for row in reports if row["domain"] == collection.id)
        seen[collection.id] = collection.title
        domains.append({"id": collection.id, "title": collection.title, "count": count})
    latest = reports[0]["updated_on"] if reports else ""
    pins = []
    for item in PINNED_DOCS:
        if safe_report_path(root, item["path"]) is None:
            continue
        pins.append({
            "id": item["id"],
            "path": item["path"],
            "title": item["title"],
            "domain": item["domain"],
            "domain_title": item["domain_title"],
            "note": item.get("note", ""),
        })
    return {
        "repo_name": "EverAgent",
        "remote_base": base,
        "domains": domains,
        "reports": reports,
        "pins": pins,
        "total": len(reports),
        "latest_on": latest,
    }


def local_target(relative_dir: str, url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
        return ""
    return posixpath.normpath(posixpath.join(relative_dir, unquote(parsed.path)))


def image_resolver(root: pathlib.Path, base: str, relative_dir: str):
    def resolve(url: str) -> str:
        target = local_target(relative_dir, url)
        if safe_file(root, target) and pathlib.Path(target).suffix.lower() in ASSET_TYPES:
            return "/api/asset?path=" + quote(target, safe="")
        return ""
    return resolve


def link_resolver(root: pathlib.Path, relative_dir: str, known: set[str]):
    def resolve(url: str) -> str:
        if url.startswith("#") or urlsplit(url).scheme:
            return url
        target = local_target(relative_dir, url)
        if not target or safe_file(root, target) is None:
            return ""
        fragment = quote(unquote(urlsplit(url).fragment), safe="")
        if target in known:
            return "/dashboard?report=" + quote(target, safe="") + ("#" + fragment if fragment else "")
        # Wiki and other repository documents keep their public GitHub link.
        return blob_url(PUBLIC_BASE, target) + ("#" + fragment if fragment else "")
    return resolve


def build_asset(root: pathlib.Path, relative: str) -> dict:
    root = root.resolve()
    catalog = load_catalog(root)
    prefixes = ["docs/assets/", *(c.root + "/" for c in catalog.COLLECTIONS)]
    path = safe_file(root, relative)
    if path is None or not any(relative.startswith(p) for p in prefixes):
        return {"error": "unsafe_path"}
    if any(part in {"transcripts", "sources", "raw"} for part in pathlib.PurePosixPath(relative).parts):
        return {"error": "unsafe_path"}
    mime = ASSET_TYPES.get(path.suffix.lower())
    if not mime or path.stat().st_size > 6 * 1024 * 1024:
        return {"error": "unsupported_asset"}
    return {"mime": mime, "data": base64.b64encode(path.read_bytes()).decode("ascii")}


def pinned_detail(root: pathlib.Path, relative: str, pinned: dict) -> dict:
    """Build the reader payload for a fixed entry."""
    base = PUBLIC_BASE
    return {
        "id": pinned["id"],
        "domain": pinned["domain"],
        "domain_title": pinned["domain_title"],
        "path": relative,
        "title": pinned["title"],
        "updated_on": "",
        "created": "",
        "status": "",
        "quality_tier": "",
        "report_depth": "",
        "report_type": "",
        "source": "",
        "source_url": "",
        "show": "",
        "episode": "",
        "tags": [],
        "github_url": blob_url(base, relative),
        "pinned": True,
        "pinned_note": pinned.get("note", ""),
    }


def build_detail(root: pathlib.Path, relative: str) -> dict:
    # The catalog yields resolved paths, so the root has to be resolved too or
    # every relative_to() check fails on a non-canonical spelling.
    root = root.resolve()
    catalog = load_catalog(root)
    path = safe_report_path(root, relative)
    if path is None:
        return {"error": "unsafe_path"}
    pinned = PINNED_BY_PATH.get(relative)
    allowed = {p.relative_to(root).as_posix(): c for c, p in catalog.iter_reports()}
    collection = allowed.get(relative)
    if collection is None and pinned is None:
        return {"error": "unknown_collection"}
    limit = MAX_PINNED_BYTES if pinned else MAX_DETAIL_BYTES
    try:
        if path.stat().st_size > limit:
            return {"error": "report_too_large"}
        with path.open("rb") as stream:
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            return {"error": "report_too_large"}
    except OSError:
        return {"error": "unreadable"}
    text = raw.decode("utf-8", errors="replace")
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            body = text[end + 4 :]
    headings = []
    for match in re.finditer(r"^(#{1,3})\s+(.+?)\s*$", body, re.MULTILINE):
        level = len(match.group(1))
        heading = match.group(2).strip()
        if heading and len(headings) < HEADING_LIMIT:
            headings.append({"level": level, "text": heading})
    base = PUBLIC_BASE
    if pinned is not None:
        detail = pinned_detail(root, relative, pinned)
    else:
        info = catalog.report_info(path)
        detail = project(catalog, collection, path, root, base)
    detail["outline"] = headings
    detail["markdown"] = body
    detail["html"] = render_markdown(
        body,
        image_resolver=image_resolver(root, base, posixpath.dirname(relative)),
        link_resolver=link_resolver(root, posixpath.dirname(relative), set(allowed) | set(PINNED_BY_PATH)),
        allow_raw_html=pinned is not None,
    )
    detail["bytes"] = len(raw)
    detail["truncated"] = False
    return {"report": detail, "info_title": detail.get("title", "")}


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        fail("bad_usage")
        return 2
    root = pathlib.Path(argv[1]).expanduser()
    if not root.is_dir():
        fail("repo_missing")
        return 2
    # The catalog derives its own ROOT with Path(__file__).resolve(), so its
    # report paths are always canonical. A symlinked or otherwise
    # non-canonical root would make every relative_to() check raise ValueError
    # and silently drop every report. Canonicalize once, here, so the root and
    # the catalog agree on one spelling of the same directory.
    root = root.resolve()
    try:
        if argv[2] == "list":
            emit(build_list(root))
            return 0
        if argv[2] in {"detail", "asset"} and len(argv) == 4:
            payload = build_detail(root, argv[3]) if argv[2] == "detail" else build_asset(root, argv[3])
            if "error" in payload:
                fail(payload["error"])
                return 1
            emit(payload)
            return 0
    except (OSError, ValueError, ImportError, AttributeError) as exc:
        fail(f"error:{type(exc).__name__}")
        return 1
    fail("bad_usage")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
