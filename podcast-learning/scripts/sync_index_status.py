#!/usr/bin/env python3
"""已处理状态回填：reports frontmatter → wiki/show-indexes 状态列。

事实源是 `reports/*.md` 的 frontmatter `source_url`（100% 覆盖）；本脚本把
它与 `wiki/show-indexes/{slug}.md` 的单集链接匹配，回填「✅ 已处理（日期 slug）」。

- 链接规范化：去 query（utm 等）+ 去尾斜杠，与 fetch_show_indexes.py 同款
- 幂等：匹配到的行统一写标准状态（重跑不变）；未匹配的行**不动**——
  保留人工维护的状态（如「看过不想做」）或「—」，符合 AGENTS.md
  「状态列由人工/agent 维护，刷新不覆盖」的契约
- cross_episode 系列：source_url 只指向首集时，其余集需人工标（本脚本不猜）
- stdout 摘要：各档回填数 / 无法匹配的报告清单（bilibili 等源不在精选索引内，正常）

用法：python3 scripts/sync_index_status.py [--dry-run]
建议节奏：写完报告后跑一次；催更（fetch_show_indexes.py）前跑一次，
这样催更汇总时「状态 ≠ —」即为已处理。
"""

import argparse
import glob
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
INDEX_DIR = ROOT / "wiki" / "show-indexes"

URL_RE = re.compile(r"https?://[^\s\"'<>)（）」』\u4e00-\u9fff]+")
# 索引行：| 集 | 日期 | 时长 | [标题](链接)… | 状态 |
ROW_RE = re.compile(r"^\|\s*(?:\d+|—)\s*\|\s*\d{4}-\d{2}-\d{2}\s*\|")


def norm(url: str) -> str:
    return url.split("?")[0].rstrip("/")


def load_reports() -> dict[str, tuple[str, str]]:
    """规范化链接 → (报告日期, slug)。frontmatter 内所有 URL 都算（覆盖系列多集）。"""
    by_url: dict[str, tuple[str, str]] = {}
    for path in sorted(glob.glob(str(REPORTS / "*.md"))):
        stem = pathlib.Path(path).stem
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(.+)", stem)
        date, slug = (m.group(1), m.group(2)) if m else ("?", stem)
        text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
        fm = re.match(r"^---\n(.*?)\n---", text, re.S)
        block = fm.group(1) if fm else ""
        for url in URL_RE.findall(block):
            by_url[norm(url)] = (date, slug)
    return by_url


def sync(dry_run: bool) -> int:
    by_url = load_reports()
    print(f"[sync] reports 事实源：{len(by_url)} 个规范化 URL")
    total_filled = 0
    files_changed = 0
    for idx_file in sorted(glob.glob(str(INDEX_DIR / "*.md"))):
        lines = pathlib.Path(idx_file).read_text(encoding="utf-8").splitlines()
        changed = filled = 0
        for i, line in enumerate(lines):
            if not ROW_RE.match(line):
                continue
            m = re.search(r"\]\((https?://[^)]+)\)", line)
            if not m:
                continue
            hit = by_url.get(norm(m.group(1)))
            if not hit:
                continue
            parts = line.split("|")
            if len(parts) < 6:
                continue
            status = f" ✅ 已处理（{hit[0]} {hit[1]}） "
            if parts[-2].strip() != status.strip():
                old = parts[-2].strip()
                if old and old != "—" and "已处理" in old:
                    pass  # 已有等价标记，统一为标准格式（幂等收敛）
                parts[-2] = status
                lines[i] = "|".join(parts)
                changed += 1
                filled += 1
        if changed and not dry_run:
            pathlib.Path(idx_file).write_text("\n".join(lines) + "\n", encoding="utf-8")
        if changed:
            files_changed += 1
            total_filled += filled
            show = pathlib.Path(idx_file).stem
            print(f"  {show}: 回填 {filled} 行")
    print(f"[sync] {'[dry-run] ' if dry_run else ''}共回填 {total_filled} 行 / {files_changed} 档")

    # 反向清单：报告 URL 不在索引里（bilibili/youtube/未收录节目等，属正常）
    idx_urls = set()
    for idx_file in glob.glob(str(INDEX_DIR / "*.md")):
        for line in pathlib.Path(idx_file).read_text(encoding="utf-8").splitlines():
            if ROW_RE.match(line):
                for url in re.findall(r"\]\((https?://[^)]+)\)", line):
                    idx_urls.add(norm(url))
    # 用报告文件粒度报告未命中（而非 URL 粒度，避免 frontmatter 附带链接噪音）
    miss = []
    for path in sorted(glob.glob(str(REPORTS / "*.md"))):
        text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
        fm = re.match(r"^---\n(.*?)\n---", text, re.S)
        block = fm.group(1) if fm else ""
        urls = [norm(u) for u in URL_RE.findall(block)]
        if urls and not any(u in idx_urls for u in urls):
            miss.append(pathlib.Path(path).name)
    if miss:
        print(f"[sync] {len(miss)} 篇报告的 URL 不在精选索引（bilibili 等源，正常）：")
        for name in miss:
            print(f"  - {name}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="只统计不写文件")
    args = ap.parse_args()
    return sync(args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
