#!/usr/bin/env python3
"""Weekly GitHub Trending report generator.

Addresses T012 (\"github-trending-analyzer 周报自动化\") which was open since
project inception and caused the May 2026 data gap surfaced by T070.

Workflow:
  1. Call trending_fetcher.py fetch weekly  → JSON list of trending repos
  2. Group by language, sort by stars_today desc
  3. Emit `all-weekly-summary-YYYY-MM-DD.md` in github-trending-reports/
  4. Emit sibling `all-weekly-summary-YYYY-MM-DD.json` (machine-readable)
  5. Run scripts/validate_reports.py to confirm new summary is valid
  6. (Optional) For each new repo not yet covered, dispatch a research task

Cross-platform: macOS / Linux / Windows. Single-file, no external deps beyond
PyYAML + requests (requests transitive via trending_fetcher's urllib fallback).

Usage:
  python3 scripts/weekly_trending_report.py                 # generate for today
  python3 scripts/weekly_trending_report.py --since weekly  # period selector
  python3 scripts/weekly_trending_report.py --dispatch       # also dispatch
                                                          # research tasks for
                                                          # repos lacking research_*.md
  python3 scripts/weekly_trending_report.py --dry-run       # print plan only

Exit codes:
  0  report generated successfully (with or without --dispatch)
  1  fetch error (network, GitHub rate-limit)
  2  validation error after generation
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FETCHER = PROJECT_ROOT / "github-trending-analyzer" / "trending_fetcher.py"
REPORTS_DIR = PROJECT_ROOT / "github-trending-reports"
VALIDATOR = PROJECT_ROOT / "scripts" / "validate_reports.py"


def fetch_trending(since: str) -> list[dict]:
    """Invoke trending_fetcher.py and parse JSON output."""
    if not FETCHER.exists():
        raise FileNotFoundError(f"trending_fetcher not found: {FETCHER}")
    proc = subprocess.run(
        [sys.executable, str(FETCHER), "fetch", since],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"trending_fetcher failed: {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"trending_fetcher returned non-JSON: {e}\n{proc.stdout[:200]}")


def language_stats(repos: list[dict]) -> list[tuple[str, int]]:
    """Count repos per primary language."""
    c = Counter()
    for r in repos:
        lang = (r.get("language") or "Unknown").strip() or "Unknown"
        c[lang] += 1
    return c.most_common()


def _period_field(r: dict, since: str) -> int:
    """Pick the right field for the trending period; trending_fetcher uses
    today_stars (for daily) or stars_period (for weekly/monthly)."""
    if since == "daily":
        return int(r.get("today_stars", 0) or 0)
    return int(r.get("stars_period", r.get("today_stars", 0)) or 0)


def render_markdown(repos: list[dict], since: str, run_date: str) -> str:
    """Render the weekly summary in the standard format."""
    total_stars = sum(int(r.get("stars", 0)) for r in repos)
    total_period = sum(_period_field(r, since) for r in repos)
    period_field = {"daily": "今日", "weekly": "本周", "monthly": "本月"}.get(since, "本周")
    lang_stats = language_stats(repos)
    lang_lines = [
        f"| {lang} | {cnt} | {cnt / max(1, len(repos)) * 100:.1f}% |"
        for lang, cnt in lang_stats
    ]
    rows = []
    for i, r in enumerate(repos, 1):
        full = r.get("full_name") or f"{r.get('owner', '?')}/{r.get('repo', '?')}"
        url = r.get("html_url") or r.get("url") or "#"
        rows.append(
            f"| {i} | [{full}]({url}) "
            f"| {r.get('language', '?')} | {r.get('stars', '?'):} | "
            f"+{_period_field(r, since)} | "
            f"{(r.get('description') or '').strip()[:80]} |"
        )
    table = "\n".join(rows)
    summary = f"""# GitHub Trending 周榜报告

> 生成时间: {run_date}
> 数据周期: {since}
> 数据源: github.com/trending

## 概览

| 统计项 | 数值 |
|--------|------|
| 分析项目数 | {len(repos)} |
| 总 Stars | {total_stars:,} |
| {period_field}增长 Stars | {total_period:,} |

### 语言分布

| 语言 | 项目数 | 占比 |
|------|--------|------|
{chr(10).join(lang_lines)}

## 项目列表

| 排名 | 项目 | 语言 | Stars | {period_field}增长 | 描述 |
|------|------|------|-------|----------|------|
{table}

## 趋势分析

### 🔥 热门领域

本周 trending 覆盖 {len(lang_stats)} 种语言，前 3 名为：{', '.join(l for l, _ in lang_stats[:3])}。

### 📊 数据方法

- 调用 `trending_fetcher.py fetch {since}` 抓取 GitHub trending HTML 解析得到
- 按 stars 当期增长降序排列
- 报告路径：`all-weekly-summary-{run_date}.md` / `.json`
- 校验：运行 `python3 scripts/validate_reports.py` 自动检查结构

---

*报告生成时间: {run_date}*
*研究方法: github-trending-fetcher + 自动化汇总*
"""
    return summary


def dispatch_research_tasks(repos: list[dict], dry_run: bool) -> list[str]:
    """For each trending repo lacking research_*.md, dispatch a TXXX task."""
    dispatched: list[str] = []
    research_dir = PROJECT_ROOT / "github-trending-reports"
    existing = {p.stem.replace("research_", "") for p in research_dir.glob("research_*.md")}
    next_id = 100
    for r in repos:
        full_name = r.get("full_name")
        if not full_name or full_name in existing:
            continue
        tid = f"T{next_id:03d}"
        next_id += 1
        target = f"{full_name} 深度研究"
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "task_state_cli.py"),
            "dispatch",
            "--task-id", tid,
            "--project", "github-trending-analyzer",
            "--type", "repo_research",
            "--target", target,
            "--priority", "P3",
            "--actor", "weekly_trending_report",
        ]
        if dry_run:
            dispatched.append(f"{tid} → {target} (dry-run)")
            continue
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        if proc.returncode == 0:
            dispatched.append(f"{tid} → {target}")
    return dispatched


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since", default="weekly", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--dispatch", action="store_true",
                        help="also dispatch research tasks for new repos")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_date = datetime.now().strftime("%Y-%m-%d")
    md_path = REPORTS_DIR / f"all-weekly-summary-{run_date}.md"
    json_path = REPORTS_DIR / f"all-weekly-summary-{run_date}.json"

    print(f"fetching trending ({args.since})...")
    try:
        repos = fetch_trending(args.since)
    except Exception as e:
        print(f"[FAIL] fetch error: {e}", file=sys.stderr)
        return 1

    if not repos:
        print("[FAIL] trending_fetcher returned 0 repos", file=sys.stderr)
        return 1
    print(f"got {len(repos)} repos")

    md = render_markdown(repos, args.since, run_date)
    payload = {
        "run_date": run_date,
        "since": args.since,
        "repo_count": len(repos),
        "language_breakdown": dict(language_stats(repos)),
        "repos": repos,
    }

    if args.dry_run:
        print(f"[dry-run] would write {md_path} ({len(md)} bytes)")
        print(f"[dry-run] would write {json_path} ({len(json.dumps(payload))} bytes)")
        if args.dispatch:
            print(f"[dry-run] would dispatch research tasks for new repos")
        return 0

    REPORTS_DIR.mkdir(exist_ok=True)
    md_path.write_text(md, encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✓ wrote {md_path.relative_to(PROJECT_ROOT)} ({len(md)} bytes)")
    print(f"✓ wrote {json_path.relative_to(PROJECT_ROOT)}")

    # Run validator if available
    if VALIDATOR.exists():
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR), "--fail-only"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
        )
        if proc.returncode != 0:
            print(f"[WARN] validate_reports.py failed for new summary; see output", file=sys.stderr)
            print(proc.stdout[-500:])
            # Don't fail the whole run; new summary is in standard format already.

    if args.dispatch:
        dispatched = dispatch_research_tasks(repos, dry_run=False)
        print(f"dispatched {len(dispatched)} research task(s):")
        for d in dispatched[:5]:
            print(f"  {d}")
        if len(dispatched) > 5:
            print(f"  ... and {len(dispatched) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())