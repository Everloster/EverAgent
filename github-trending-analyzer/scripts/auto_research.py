#!/usr/bin/env python3
"""Auto-generate research_*.md skeleton from GitHub repo metadata.

Triggered by weekly_trending_report.py --auto-research, or run standalone:

    python3 scripts/auto_research.py <owner/repo> [<owner/repo> ...]
    python3 scripts/auto_research.py --from-weekly-summary all-weekly-summary-2026-06-21.md

What it generates:
  - research_{owner}_{repo}.md under github-trending-reports/
  - 7 chapter skeleton (项目概述 / 基本信息 / 技术分析 / 社区活跃度 / 发展趋势 / 竞品对比 / 总结评价)
  - README excerpt (first ~800 chars) embedded in 项目概述
  - Real metadata table populated from GitHub API
  - Other chapters marked "[待补充]" as honest stubs

What it does NOT do:
  - Fabricate technical analysis content
  - Invent competitor comparisons
  - Guess at roadmap or trends

This is an honest scaffold; deeper analysis must be filled by a Subagent (TrendAgent
or general-purpose) using the project as context. Each skeleton ships with explicit
"[待补充]" markers so a reviewer can see what's been added vs. what's stub.

Rate limit: GitHub API allows 60 unauthenticated requests/hour. Each repo uses 2
(metadata + readme). With 19 repos/week, we use 38 of 60 — comfortable headroom.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "github-trending-reports"


def fetch(url: str, accept: str = "application/vnd.github+json") -> dict | str | None:
    """GET a GitHub API endpoint, return parsed JSON or raw text."""
    req = urllib.request.Request(url, headers={
        "Accept": accept,
        "User-Agent": "EverAgent-TrendAnalyzer/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  [WARN] rate-limited: {e.headers.get('x-ratelimit-remaining', '?')} remaining")
        else:
            print(f"  [WARN] HTTP {e.code}: {url}")
        return None
    except (urllib.error.URLError, json.JSONDecodeError) as e:
        print(f"  [WARN] {type(e).__name__}: {e}")
        return None


def fetch_repo_meta(owner: str, repo: str) -> dict | None:
    return fetch(f"https://api.github.com/repos/{owner}/{repo}")


def fetch_readme(owner: str, repo: str) -> str:
    data = fetch(f"https://api.github.com/repos/{owner}/{repo}/readme")
    if not isinstance(data, dict) or not data.get("content"):
        return ""
    try:
        return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    except Exception:
        return ""


def strip_readme_noise(readme: str, max_chars: int = 800) -> str:
    """Drop badges, HTML, links; keep prose for the excerpt."""
    lines = []
    for ln in readme.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("![") or s.startswith("[!["):
            continue  # badges
        if s.startswith("<") and s.endswith(">"):
            continue  # HTML / comments
        if s.startswith("|") and "|" in s[1:]:
            continue  # tables
        if s.startswith("```"):
            continue  # code fence markers
        if s.startswith("- ") and len(s) < 60 and not lines:
            continue  # short TOC items at top
        lines.append(s)
        if sum(len(l) for l in lines) >= max_chars:
            break
    return "\n".join(lines)[:max_chars]


def render_skeleton(owner: str, repo: str, meta: dict, readme_excerpt: str) -> str:
    """Render the research_*.md skeleton following the 7-chapter structure."""
    full = meta.get("full_name", f"{owner}/{repo}")
    description = (meta.get("description") or "(no description)").strip()
    stars = meta.get("stargazers_count", "?")
    forks = meta.get("forks_count", "?")
    language = meta.get("language") or "Unknown"
    license_ = (meta.get("license") or {}).get("spdx_id") or "Unknown"
    created = (meta.get("created_at") or "")[:10]
    updated = (meta.get("updated_at") or "")[:10]
    pushed = (meta.get("pushed_at") or "")[:10]
    topics = meta.get("topics") or []
    open_issues = meta.get("open_issues_count", "?")
    default_branch = meta.get("default_branch", "main")
    html_url = meta.get("html_url", f"https://github.com/{owner}/{repo}")

    today = datetime.now().strftime("%Y-%m-%d")

    header = f"""# {full} 深度研究报告

## 项目概述

{description}

> 来源：README 与 GitHub 项目元信息自动摘要（**仅作骨架，每章 `[待补充]` 段需人工/agent 补全**）

### README 摘要

{readme_excerpt or "[待补充：截取 README 关键章节]"}

---

## 基本信息

| 属性 | 数值 |
|------|------|
| 全称 | {full} |
| GitHub URL | {html_url} |
| GitHub Stars | {stars:,} |
| GitHub Forks | {forks:,} |
| 主语言 | {language} |
| 许可证 | {license_} |
| 项目创建日期 | {created} |
| 最近推送日期 | {pushed} |
| 默认分支 | {default_branch} |
| 开放 Issue/PR 数 | {open_issues} |
| 话题标签 | {', '.join(topics) if topics else '[待补充]'} |

---

## 技术分析

[待补充：从 README / 源码 / 文档提取：
- 核心架构（模块划分、数据流）
- 关键技术栈与依赖
- 性能/扩展性设计
- 与同类项目的差异化设计]

---

## 社区活跃度

| 指标 | 数值 | 数据源 |
|------|------|--------|
| Stars | {stars:,} | GitHub API |
| Forks | {forks:,} | GitHub API |
| 开放 Issue/PR | {open_issues} | GitHub API |
| 最近活跃 | {updated} | GitHub API |

[待补充：贡献者数量、近 30/90 天 commit 频率、PR review 周期、issue 响应时间]

---

## 发展趋势

[待补充：
- 版本演进（最近 5 个 release 主题）
- star 增长曲线（基于历史 trending 数据）
- 应用领域扩展方向
- 维护活跃度趋势]

---

## 竞品对比

[待补充：列出 2-5 个直接竞品并对比：
- 功能覆盖
- 性能基准
- 生态完整度
- 维护活跃度]

---

## 总结评价

### 优势

[待补充：列出 3-5 个该项目显著优于同类之处]

### 劣势

[待补充：列出 3-5 个该项目显著的局限或风险]

### 学习/使用建议

[待补充：面向不同读者（学习者 / 工程团队 / 投资人）的优先级建议]

---

*报告生成时间: {today}*
*研究方法: github-api 元信息 + README 自动提取（**骨架**，每章 [待补充] 待人工/agent 补全）*
"""
    return header


def process_repo(full_name: str) -> bool:
    if "/" not in full_name:
        print(f"  [FAIL] invalid format: {full_name} (expected owner/repo)")
        return False
    owner, repo = full_name.split("/", 1)
    out_path = REPORTS_DIR / f"research_{owner}_{repo}.md"

    if out_path.exists():
        print(f"  {full_name}: research exists, skip")
        return False

    print(f"  fetching metadata: {full_name}")
    meta = fetch_repo_meta(owner, repo)
    if not meta or not isinstance(meta, dict):
        print(f"  [FAIL] could not fetch metadata for {full_name}")
        return False

    print(f"  fetching readme...")
    readme = fetch_readme(owner, repo)
    excerpt = strip_readme_noise(readme) if readme else ""

    skeleton = render_skeleton(owner, repo, meta, excerpt)
    out_path.write_text(skeleton, encoding="utf-8")
    print(f"  ✓ wrote {out_path.relative_to(PROJECT_ROOT)} ({len(skeleton)} bytes)")
    return True


def extract_repos_from_summary(md_path: Path) -> list[str]:
    """Pull owner/repo from a weekly-summary markdown table."""
    text = md_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\[([\w\-.]+/[\w\-.]+)\]\(https://github\.com/([\w\-.]+/[\w\-.]+)\)")
    names: list[str] = []
    for m in pattern.finditer(text):
        names.append(m.group(2))
    seen = set()
    return [n for n in names if not (n in seen or seen.add(n))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repos", nargs="*", help="owner/repo pairs")
    parser.add_argument("--from-weekly-summary", help="extract repos from a weekly-summary .md")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.from_weekly_summary:
        path = PROJECT_ROOT / args.from_weekly_summary
        if not path.exists():
            print(f"[FAIL] file not found: {path}", file=sys.stderr)
            return 1
        repos = extract_repos_from_summary(path)
        print(f"extracted {len(repos)} repos from {path.name}")
    else:
        repos = list(args.repos)

    if not repos:
        print("no repos to process")
        return 0

    if args.dry_run:
        print(f"[dry-run] would process {len(repos)} repos:")
        for r in repos:
            print(f"  {r}")
        return 0

    print(f"processing {len(repos)} repo(s):\n")
    ok = skip = fail = 0
    for r in repos:
        if process_repo(r):
            ok += 1
        else:
            # process_repo prints its own skip/fail reasons; bucket as such
            if (REPORTS_DIR / f"research_{r.replace('/', '_')}.md").exists():
                skip += 1
            else:
                fail += 1

    print(f"\nsummary: created={ok}, skipped={skip}, failed={fail}")
    # Run validator on the new files
    if ok > 0:
        validator = PROJECT_ROOT / "scripts" / "validate_reports.py"
        if validator.exists():
            print("\nrunning validate_reports.py on new files...")
            subprocess.run(
                [sys.executable, str(validator), "--fail-only"],
                cwd=PROJECT_ROOT,
                capture_output=True,
            )
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())