#!/usr/bin/env python3
"""Reindex EverAgent knowledge base.

Counts reports and wiki pages per learning domain and refreshes the
recent-report and overview tables in the root README.md (between the
AUTO markers).
Also rebuilds docs/REPORT_INDEX.md — the reading entry point that lists
every report by update time, parsed from report frontmatter (see
docs/REPORT_METADATA.md).

Usage:
    python3 scripts/reindex.py            # update README + REPORT_INDEX in place
    python3 scripts/reindex.py --check    # print counts, don't write
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

try:
    from .report_catalog import (
        COLLECTION_BY_ID,
        COLLECTIONS,
        ROOT,
        iter_reports,
        report_info,
    )
except ImportError:  # Direct script execution.
    from report_catalog import (
        COLLECTION_BY_ID,
        COLLECTIONS,
        ROOT,
        iter_reports,
        report_info,
    )

INDEX_PATH = ROOT / "docs" / "REPORT_INDEX.md"
RECENT_TOP = 25
README_RECENT_TOP = 5
MAX_TAGS = 6

OVERVIEW_MARKER_START = "<!-- AUTO-OVERVIEW:START -->"
OVERVIEW_MARKER_END = "<!-- AUTO-OVERVIEW:END -->"
RECENT_MARKER_START = "<!-- AUTO-RECENT:START -->"
RECENT_MARKER_END = "<!-- AUTO-RECENT:END -->"


def count_md(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*.md") if p.is_file())


def domain_stats(domain: str) -> dict[str, int]:
    base = ROOT / domain
    reports = sum(1 for _collection, _path in iter_reports(domain))
    return {
        "reports": reports,
        "concepts": count_md(base / "wiki" / "concepts"),
        "entities": count_md(base / "wiki" / "entities"),
        "syntheses": count_md(base / "wiki" / "syntheses"),
    }


def build_table() -> str:
    rows = [
        "| 项目 | 报告 | Wiki(概念/实体/综合) |",
        "|------|------|----------------------|",
    ]
    for collection in COLLECTIONS:
        if not collection.include_in_overview:
            continue
        s = domain_stats(collection.id)
        wiki = f"{s['concepts']}/{s['entities']}/{s['syntheses']}"
        rows.append(
            f"| {collection.emoji} [{collection.title}](./{collection.id}/) | {s['reports']} 篇 | {wiki} |"
        )
    return "\n".join(rows)


def all_reports_sorted(by_domain: dict[str, list[dict]]) -> list[dict]:
    reports = [report for reports in by_domain.values() for report in reports]
    reports.sort(
        key=lambda report: (report["updated_on"], report["title"]), reverse=True
    )
    return reports


def build_readme_recent(by_domain: dict[str, list[dict]]) -> str:
    rows = [
        "| 日期 | 报告 | 领域 |",
        "|------|------|------|",
    ]
    for report in all_reports_sorted(by_domain)[:README_RECENT_TOP]:
        target = os.path.relpath(report["path"], ROOT)
        collection = COLLECTION_BY_ID.get(report["domain"])
        domain = (
            f"{collection.emoji} {collection.title}" if collection else report["domain"]
        )
        rows.append(
            f"| {report['updated_on']} | [{_md_cell(report['title'])}](./{target}) | {domain} |"
        )
    return "\n".join(rows)


def replace_generated_block(text: str, start: str, end: str, content: str) -> str:
    if start not in text or end not in text:
        return text
    pre, remainder = text.split(start, 1)
    _old, post = remainder.split(end, 1)
    return f"{pre}{start}\n{content}\n{end}{post}"


def indexed_fallback_dates() -> dict[Path, str]:
    """Read stable fallback dates for legacy reports without metadata."""
    if not INDEX_PATH.exists():
        return {}
    dates: dict[Path, str] = {}
    row = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*\[.*\]\(([^)]+)\)\s*\|")
    for line in INDEX_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        match = row.match(line)
        if not match:
            continue
        date, target = match.groups()
        dates[(INDEX_PATH.parent / target).resolve()] = date
    return dates


def collect_reports(fallback_dates: dict[Path, str] | None = None) -> dict[str, list[dict]]:
    """All reports per index domain, sorted by updated_on desc."""
    fallback_dates = fallback_dates or {}
    by_domain: dict[str, list[dict]] = {}
    for collection in COLLECTIONS:
        if not collection.include_in_index:
            continue
        entries = []
        for _item, path in iter_reports(collection.id):
            entries.append(
                report_info(path, fallback_updated_on=fallback_dates.get(path.resolve(), ""))
            )
        entries.sort(key=lambda r: (r["updated_on"], r["title"]), reverse=True)
        by_domain[collection.id] = entries
    return by_domain


def _md_link(path: Path) -> str:
    return os.path.relpath(path, INDEX_PATH.parent)


def _md_cell(text: str) -> str:
    return text.replace("|", "\\|").strip()


def build_index(by_domain: dict[str, list[dict]]) -> str:
    out = [
        "# 📖 报告索引",
        "",
        "> 由 `python3 scripts/reindex.py` 自动生成，请勿手改。",
        "> 数据源：各报告 frontmatter（约定见 [REPORT_METADATA.md](./REPORT_METADATA.md)）。",
        "",
    ]
    all_reports = all_reports_sorted(by_domain)

    out += [
        f"## 最近更新（Top {RECENT_TOP}）",
        "",
        "| 日期 | 报告 | 领域 |",
        "|------|------|------|",
    ]
    for r in all_reports[:RECENT_TOP]:
        out.append(
            f"| {r['updated_on']} | [{_md_cell(r['title'])}]({_md_link(r['path'])}) | {r['domain']} |"
        )
    out.append("")

    for collection in COLLECTIONS:
        if not collection.include_in_index:
            continue
        rs = by_domain[collection.id]
        if not rs:
            continue
        out += [
            f"## {collection.emoji} {collection.title}（{len(rs)} 篇）",
            "",
            "| 日期 | 报告 | 标签 |",
            "|------|------|------|",
        ]
        for r in rs:
            tags = ", ".join(f"`{t}`" for t in r["tags"][:MAX_TAGS]) or "—"
            out.append(
                f"| {r['updated_on']} | [{_md_cell(r['title'])}]({_md_link(r['path'])}) | {tags} |"
            )
        out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Reindex knowledge base")
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify README and REPORT_INDEX are current without writing",
    )
    args = parser.parse_args()

    table = build_table()
    reports_by_domain = collect_reports(indexed_fallback_dates())
    recent = build_readme_recent(reports_by_domain)
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    required_markers = (
        RECENT_MARKER_START,
        RECENT_MARKER_END,
        OVERVIEW_MARKER_START,
        OVERVIEW_MARKER_END,
    )
    markers_present = all(marker in text for marker in required_markers)
    expected_readme = replace_generated_block(
        text, RECENT_MARKER_START, RECENT_MARKER_END, recent
    )
    expected_readme = replace_generated_block(
        expected_readme, OVERVIEW_MARKER_START, OVERVIEW_MARKER_END, table
    )

    expected_index = build_index(reports_by_domain)

    if args.check:
        stale = []
        if not markers_present:
            stale.append("README.md generated markers")
        elif expected_readme != text:
            stale.append("README.md generated blocks")
        current_index = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        if current_index != expected_index:
            stale.append(str(INDEX_PATH.relative_to(ROOT)))
        print(table)
        if stale:
            print("[reindex] stale: " + ", ".join(stale))
            return 1
        print("[reindex] indexes are current.")
        return 0

    if not markers_present:
        print("[reindex] README generated markers are missing.")
        return 1
    if expected_readme != text:
        readme.write_text(expected_readme, encoding="utf-8")
        print("[reindex] README generated blocks updated.")
    else:
        print("[reindex] README generated blocks are current.")

    INDEX_PATH.write_text(expected_index, encoding="utf-8")
    print(f"[reindex] {INDEX_PATH.relative_to(ROOT)} rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
