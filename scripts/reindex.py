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
import datetime
import os
import re
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

# 报告索引额外覆盖 web-surfing（E 类）；github-trending-analyzer（D 类）
# 自带协议与 README，不纳入。
INDEX_DOMAINS = DOMAINS + [("web-surfing", "Web Surfing", "🏄")]

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
    # ai-practice（B 类）产出形态是 experiments/ 教学笔记（exp_NNN_*.md），
    # 不是 reports/。其余领域的"报告"都在 reports/。
    if domain == "ai-practice":
        exp = base / "experiments"
        reports = (
            sum(1 for p in exp.glob("exp_*.md") if p.is_file())
            if exp.exists()
            else 0
        )
    else:
        reports = count_md(base / "reports")
    return {
        "reports": reports,
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


def parse_report(path: Path) -> dict:
    """Extract title/updated_on/semantic_tags from a report's frontmatter.

    Falls back to the first H1 heading and the file mtime when frontmatter
    or fields are missing (e.g. web-surfing reports).
    """
    info: dict = {"title": "", "updated_on": "", "tags": []}
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:8192]
    except OSError:
        head = ""
    lines = head.splitlines()

    if lines and lines[0].strip() == "---":
        fm: dict = {}
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            m = re.match(r"^(\w+):\s*(.*)$", lines[i])
            if m:
                key, val = m.group(1), m.group(2).strip()
                if val.startswith("[") and val.endswith("]"):
                    fm[key] = [
                        t.strip().strip("\"'")
                        for t in val[1:-1].split(",")
                        if t.strip()
                    ]
                elif val == "":
                    items = []
                    j = i + 1
                    while j < len(lines) and lines[j].strip().startswith("- "):
                        items.append(lines[j].strip()[2:].strip().strip("\"'"))
                        j += 1
                    fm[key] = items if items else ""
                else:
                    fm[key] = val.strip("\"'")
            i += 1
        info["title"] = str(fm.get("title") or "")
        info["updated_on"] = str(fm.get("updated_on") or "")
        tags = fm.get("semantic_tags") or []
        info["tags"] = tags if isinstance(tags, list) else [str(tags)]

    if not info["title"]:
        for line in lines:
            if line.startswith("# "):
                info["title"] = line[2:].strip()
                break
    if not info["title"]:
        info["title"] = path.stem
    # 日期来源优先级：frontmatter updated_on > 文件名内的 YYYY-MM-DD > 文件 mtime。
    # 文件名日期专治 web-surfing 日报（ai-news-daily-2026-08-26），mtime 会随
    # clone/checkout 重置导致索引日期漂移。文件名无完整日期的报告（如
    # kdrama-top10-2024-2026，那是内容年份不是日期）不会误命中，继续回退。
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", info["updated_on"]):
        m = re.search(r"\d{4}-\d{2}-\d{2}", path.stem)
        if m:
            info["updated_on"] = m.group(0)
        else:
            info["updated_on"] = datetime.date.fromtimestamp(
                path.stat().st_mtime
            ).isoformat()
    return info


def collect_reports() -> dict[str, list[dict]]:
    """All reports per index domain, sorted by updated_on desc."""
    by_domain: dict[str, list[dict]] = {}
    for domain, _name, _emoji in INDEX_DOMAINS:
        base = ROOT / domain / "reports"
        entries = []
        if base.exists():
            for p in sorted(base.rglob("*.md")):
                if p.is_file():
                    r = parse_report(p)
                    r["path"] = p
                    r["domain"] = domain
                    entries.append(r)
        entries.sort(key=lambda r: (r["updated_on"], r["title"]), reverse=True)
        by_domain[domain] = entries
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

    for domain, name, emoji in INDEX_DOMAINS:
        rs = by_domain[domain]
        if not rs:
            continue
        out += [
            f"## {emoji} {name}（{len(rs)} 篇）",
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

    INDEX_PATH.write_text(build_index(collect_reports()), encoding="utf-8")
    print(f"[reindex] {INDEX_PATH.relative_to(ROOT)} rebuilt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
