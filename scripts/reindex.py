#!/usr/bin/env python3
"""Reindex EverAgent knowledge base.

Counts reports and wiki pages per learning domain and refreshes the
overview table in the root README.md (between the AUTO markers).

Usage:
    python3 scripts/reindex.py            # update README in place
    python3 scripts/reindex.py --check    # print counts, don't write
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# domain dir -> (display name, emoji)
DOMAINS = [
    ("ai-learning", "AI Learning", "🤖"),
    ("cs-learning", "CS Learning", "💻"),
    ("philosophy-learning", "Philosophy Learning", "📚"),
    ("psychology-learning", "Psychology Learning", "🧠"),
    ("biology-learning", "Biology Learning", "🧬"),
    ("ai-practice", "AI Practice", "⚗️"),
    ("podcast-learning", "Podcast Learning", "🎙️"),
]

MARKER_START = "<!-- AUTO-OVERVIEW:START -->"
MARKER_END = "<!-- AUTO-OVERVIEW:END -->"


def count_md(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for p in path.rglob("*.md") if p.is_file())


def domain_stats(domain: str) -> dict[str, int]:
    base = ROOT / domain
    return {
        "reports": count_md(base / "reports"),
        "concepts": count_md(base / "wiki" / "concepts"),
        "entities": count_md(base / "wiki" / "entities"),
        "syntheses": count_md(base / "wiki" / "syntheses"),
    }


def build_table() -> str:
    seen: set[str] = set()
    rows = [
        "| 项目 | 报告 | Wiki(概念/实体/综合) |",
        "|------|------|----------------------|",
    ]
    for domain, name, emoji in DOMAINS:
        if domain in seen:
            continue
        seen.add(domain)
        s = domain_stats(domain)
        wiki = f"{s['concepts']}/{s['entities']}/{s['syntheses']}"
        rows.append(
            f"| {emoji} [{name}](./{domain}/) | {s['reports']} 篇 | {wiki} |"
        )
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reindex knowledge base")
    parser.add_argument("--check", action="store_true", help="print counts only")
    args = parser.parse_args()

    table = build_table()
    if args.check:
        print(table)
        return 0

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    block = f"{MARKER_START}\n{table}\n{MARKER_END}"
    if MARKER_START in text and MARKER_END in text:
        pre = text.split(MARKER_START)[0]
        post = text.split(MARKER_END)[1]
        readme.write_text(pre + block + post, encoding="utf-8")
        print("[reindex] README overview updated.")
    else:
        print("[reindex] markers not found in README; printing table:\n")
        print(block)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
