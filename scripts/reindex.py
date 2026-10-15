#!/usr/bin/env python3
"""Reindex EverAgent knowledge base.

Counts reports and wiki pages per learning domain and refreshes the
overview table in the root README.md (between the AUTO markers).
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
    from .report_catalog import COLLECTIONS, ROOT, iter_reports, report_info
except ImportError:  # Direct script execution.
    from report_catalog import COLLECTIONS, ROOT, iter_reports, report_info

INDEX_PATH = ROOT / "docs" / "REPORT_INDEX.md"
RECENT_TOP = 25
MAX_TAGS = 6

MARKER_START = "<!-- AUTO-OVERVIEW:START -->"
MARKER_END = "<!-- AUTO-OVERVIEW:END -->"


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


def collect_reports() -> dict[str, list[dict]]:
    """All reports per index domain, sorted by updated_on desc."""
    by_domain: dict[str, list[dict]] = {}
    for collection in COLLECTIONS:
        if not collection.include_in_index:
            continue
        entries = []
        for _item, path in iter_reports(collection.id):
            entries.append(report_info(path))
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
    all_reports = [r for rs in by_domain.values() for r in rs]
    all_reports.sort(key=lambda r: (r["updated_on"], r["title"]), reverse=True)

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
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = f"{MARKER_START}\n{table}\n{MARKER_END}"
    if MARKER_START in text and MARKER_END in text:
        pre = text.split(MARKER_START)[0]
        post = text.split(MARKER_END)[1]
        expected_readme = pre + block + post
    else:
        expected_readme = text

    expected_index = build_index(collect_reports())

    if args.check:
        stale = []
        if expected_readme != text:
            stale.append("README.md overview")
        current_index = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.exists() else ""
        if current_index != expected_index:
            stale.append(str(INDEX_PATH.relative_to(ROOT)))
        print(table)
        if stale:
            print("[reindex] stale: " + ", ".join(stale))
            return 1
        print("[reindex] indexes are current.")
        return 0

    if MARKER_START in text and MARKER_END in text:
        readme.write_text(expected_readme, encoding="utf-8")
        print("[reindex] README overview updated.")
    else:
        print("[reindex] markers not found in README; printing table:\n")
        print(block)

    INDEX_PATH.write_text(expected_index, encoding="utf-8")
    print(f"[reindex] {INDEX_PATH.relative_to(ROOT)} rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
