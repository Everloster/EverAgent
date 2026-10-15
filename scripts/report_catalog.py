#!/usr/bin/env python3
"""Shared report discovery and metadata helpers for EverAgent."""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ReportCollection:
    id: str
    title: str
    emoji: str
    root: str
    patterns: tuple[str, ...] = ("**/*.md",)
    excluded_parts: tuple[str, ...] = ()
    include_in_overview: bool = True
    include_in_index: bool = True


COLLECTIONS: tuple[ReportCollection, ...] = (
    ReportCollection("ai-learning", "AI Learning", "🤖", "ai-learning/reports"),
    ReportCollection("cs-learning", "CS Learning", "💻", "cs-learning/reports"),
    ReportCollection("philosophy-learning", "Philosophy Learning", "📚", "philosophy-learning/reports"),
    ReportCollection("psychology-learning", "Psychology Learning", "🧠", "psychology-learning/reports"),
    ReportCollection("biology-learning", "Biology Learning", "🧬", "biology-learning/reports"),
    ReportCollection(
        "ai-practice",
        "AI Practice",
        "⚗️",
        "ai-practice/experiments",
        patterns=("exp_*.md", "**/评估笔记*.md"),
    ),
    ReportCollection(
        "podcast-learning",
        "Podcast Learning",
        "🎙️",
        "podcast-learning/reports",
        excluded_parts=("transcripts",),
    ),
    ReportCollection("github-trending-analyzer", "GitHub Research", "🔭", "github-trending-analyzer/reports"),
    ReportCollection("web-surfing", "Web Surfing", "🏄", "web-surfing/reports"),
)


COLLECTION_BY_ID = {item.id: item for item in COLLECTIONS}


def _is_excluded(path: Path, collection: ReportCollection) -> bool:
    relative = path.relative_to(ROOT / collection.root)
    return any(part in collection.excluded_parts for part in relative.parts)


def iter_reports(domain: str | None = None) -> Iterable[tuple[ReportCollection, Path]]:
    """Yield canonical report artifacts, excluding transcripts and shownotes."""
    collections = COLLECTIONS if domain is None else (COLLECTION_BY_ID[domain],)
    for collection in collections:
        base = ROOT / collection.root
        if not base.exists():
            continue
        seen: set[Path] = set()
        for pattern in collection.patterns:
            for path in sorted(base.glob(pattern)):
                if path in seen or not path.is_file() or _is_excluded(path, collection):
                    continue
                seen.add(path)
                yield collection, path


def collection_for_path(path: Path) -> ReportCollection | None:
    resolved = path.resolve()
    for collection in COLLECTIONS:
        base = (ROOT / collection.root).resolve()
        try:
            relative = resolved.relative_to(base)
        except ValueError:
            continue
        if any(part in collection.excluded_parts for part in relative.parts):
            return None
        if path.suffix.lower() == ".md":
            return collection
    return None


def parse_frontmatter(text: str) -> dict[str, object]:
    """Parse the small YAML subset used by report frontmatter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    result: dict[str, object] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        match = re.match(r"^(\w+):\s*(.*)$", lines[i])
        if not match:
            i += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value.startswith("[") and value.endswith("]"):
            result[key] = [
                item.strip().strip("\"'")
                for item in value[1:-1].split(",")
                if item.strip()
            ]
        elif value == "":
            items: list[str] = []
            j = i + 1
            while j < len(lines) and lines[j].strip().startswith("- "):
                items.append(lines[j].strip()[2:].strip().strip("\"'"))
                j += 1
            result[key] = items if items else ""
            i = j - 1
        else:
            result[key] = value.strip("\"'")
        i += 1
    return result


def report_info(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="replace")
    metadata = parse_frontmatter(text)
    title = str(metadata.get("title") or "")
    if not title:
        heading = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
        title = heading.group(1).strip() if heading else path.stem

    updated_on = str(metadata.get("updated_on") or metadata.get("created") or "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated_on):
        filename_date = re.search(r"\d{4}-\d{2}-\d{2}", path.stem)
        footer_date = re.search(r"报告生成时间[:：]\s*(\d{4}-\d{2}-\d{2})", text)
        if filename_date:
            updated_on = filename_date.group(0)
        elif footer_date:
            updated_on = footer_date.group(1)
        else:
            updated_on = dt.date.fromtimestamp(path.stat().st_mtime).isoformat()

    tags = metadata.get("semantic_tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]

    collection = collection_for_path(path)
    return {
        "title": title,
        "updated_on": updated_on,
        "tags": tags,
        "metadata": metadata,
        "path": path,
        "domain": collection.id if collection else str(metadata.get("domain") or "unknown"),
    }
