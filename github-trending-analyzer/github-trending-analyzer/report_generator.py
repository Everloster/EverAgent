#!/usr/bin/env python3
"""
Report Generator for GitHub Trending Analyzer
Generates individual project reports and summary reports.

Cross-platform compatible - works on macOS, Linux, and Windows.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def get_skill_dir() -> Path:
    """
    Get the directory where this skill is located.
    Works regardless of current working directory.
    """
    return Path(__file__).parent.resolve()


def get_default_reports_dir() -> Path:
    """
    Get default reports directory.
    Priority:
    1. TRENDING_REPORTS_DIR environment variable
    2. github-trending-reports in current working directory
    """
    env_dir = os.environ.get("TRENDING_REPORTS_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.cwd() / "github-trending-reports"


def ensure_dir(path: Path):
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def safe_format_number(value, default="N/A"):
    """Safely format a number with thousands separator."""
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return default


def generate_project_report(
    repo_data: Dict,
    analysis_data: Dict,
    output_path: Path,
    research_method: str = "Web搜索 + GitHub页面分析",
) -> Path:
    """
    Generate a single project report.

    Args:
        repo_data: Basic repo info from trending fetcher
        analysis_data: Deep research analysis data
        output_path: Path to save the report
        research_method: Human-readable description of how research was done.
            Passed by the caller so the footer accurately reflects the actual
            method used (e.g. "github-deep-research 多轮深度研究" vs
            "Web搜索 + GitHub页面分析"). Defaults to the web-search variant
            which is the common case for non-Trae platforms.

    Returns:
        Path to the generated report
    """
    if isinstance(output_path, str):
        output_path = Path(output_path)
    
    ensure_dir(output_path.parent)
    
    content = f"""# {repo_data.get('owner', '')}/{repo_data.get('repo', '')}

> {repo_data.get('description', 'No description available')}

## 项目概述

{analysis_data.get('summary', '暂无分析数据')}

## 基本信息

| 指标 | 数值 |
|------|------|
| Stars | {safe_format_number(repo_data.get('stars'))} |
| Forks | {safe_format_number(repo_data.get('forks'))} |
| 语言 | {repo_data.get('language', 'Unknown')} |
| 今日增长 | {safe_format_number(repo_data.get('today_stars'))} ⭐ |
| 开源协议 | {analysis_data.get('license', 'N/A')} |
| 创建时间 | {analysis_data.get('created_at', 'N/A')} |
| 最近更新 | {analysis_data.get('updated_at', 'N/A')} |
| GitHub | [{repo_data.get('url', 'N/A')}]({repo_data.get('url', '#')}) |

## 技术分析

### 技术栈

{format_languages(analysis_data.get('languages', {}))}

### 架构设计

{analysis_data.get('architecture', '暂无架构信息')}

### 核心功能

{analysis_data.get('core_features', '暂无核心功能信息')}

## 社区活跃度

### 贡献者分析

{format_contributors(analysis_data.get('contributors', []))}

### Issue/PR 活跃度

{analysis_data.get('issue_pr_activity', '暂无 Issue/PR 活跃度数据')}

### 最近动态

{analysis_data.get('recent_activity', '暂无最近动态')}

## 发展趋势

### 版本演进

{format_releases(analysis_data.get('releases', []))}

### Roadmap

{analysis_data.get('roadmap', '暂无 Roadmap 信息')}

### 社区反馈

{analysis_data.get('community_feedback', '暂无社区反馈')}

## 竞品对比

{format_competitors(analysis_data.get('competitors', []), repo_data)}

## 总结评价

### 优势

{format_advantages(analysis_data.get('advantages', []))}

### 劣势

{format_disadvantages(analysis_data.get('disadvantages', []))}

### 适用场景

{analysis_data.get('use_cases', '暂无适用场景信息')}

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*研究方法: {research_method}*
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def format_languages(languages: Dict[str, int]) -> str:
    """Format language distribution."""
    if not languages:
        return "暂无语言数据"
    
    total = sum(languages.values())
    lines = []
    for lang, bytes_count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
        percentage = (bytes_count / total * 100) if total > 0 else 0
        lines.append(f"- **{lang}**: {percentage:.1f}%")
    return "\n".join(lines)


def format_contributors(contributors: List[Dict]) -> str:
    """Format contributors list."""
    if not contributors:
        return "暂无贡献者数据"
    
    lines = []
    for c in contributors[:10]:
        login = c.get("login", "Unknown")
        contributions = c.get("contributions", 0)
        lines.append(f"- [{login}](https://github.com/{login}) - {contributions} commits")
    return "\n".join(lines)


def format_releases(releases: List[Dict]) -> str:
    """Format releases list."""
    if not releases:
        return "暂无发布版本"
    
    lines = []
    for r in releases[:5]:
        tag = r.get("tag_name", "N/A")
        date = r.get("published_at", "N/A")[:10] if r.get("published_at") else "N/A"
        name = r.get("name", tag)
        lines.append(f"- **{tag}** ({date}): {name}")
    return "\n".join(lines)


def format_competitors(competitors: List[Dict], repo_data: Dict) -> str:
    """Format competitors comparison table."""
    if not competitors:
        return "暂无竞品对比数据"
    
    lines = ["| 项目 | Stars | 语言 | 特点 |", "|------|-------|------|------|"]
    
    lines.append(f"| 本项目 | {safe_format_number(repo_data.get('stars'))} | {repo_data.get('language', 'Unknown')} | {repo_data.get('description', '')[:50]}... |")
    
    for c in competitors[:3]:
        name = c.get("name", "Unknown")
        stars = safe_format_number(c.get("stars", "N/A"))
        lang = c.get("language", "Unknown")
        feature = c.get("feature", "N/A")[:50]
        lines.append(f"| {name} | {stars} | {lang} | {feature} |")
    
    return "\n".join(lines)


def format_advantages(advantages: List[str]) -> str:
    """Format advantages list."""
    if not advantages:
        return "暂无优势信息"
    return "\n".join([f"- {a}" for a in advantages])


def format_disadvantages(disadvantages: List[str]) -> str:
    """Format disadvantages list."""
    if not disadvantages:
        return "暂无劣势信息"
    return "\n".join([f"- {d}" for d in disadvantages])


def generate_summary(repo_data: Dict, analysis_data: Dict) -> str:
    """Generate a summary paragraph."""
    parts = []
    
    lang = repo_data.get("language", "Unknown")
    stars = repo_data.get("stars", 0)
    today = repo_data.get("today_stars", 0)
    
    parts.append(f"这是一个使用 **{lang}** 开发的项目，目前拥有 {stars:,} 个 Star。")
    
    if today > 0:
        parts.append(f"今日获得 {today:,} 个新 Star，显示出强劲的增长势头。")
    
    desc = repo_data.get("description", "")
    if desc:
        parts.append(f"项目定位：{desc}")
    
    return " ".join(parts)


def _format_report_status(repos: List[Dict], missing_repos: List[str]) -> str:
    """
    Build the status block for the summary report footer.

    Shows ✅ only when every individual report was successfully generated.
    When some are missing, shows a ⚠️ list so readers know which projects
    lack a full research write-up — rather than silently claiming completeness.
    """
    total = len(repos)
    if not missing_repos:
        return f"✅ 所有项目报告已完整生成，共 **{total}** 份深度研究报告。"

    lines = [
        f"⚠️ **以下 {len(missing_repos)} 个项目报告未生成或不完整**（共 {total} 个项目）：",
        "",
    ]
    for r in missing_repos:
        lines.append(f"- `{r}` — 报告缺失或内容不完整，建议手动补充")
    complete = total - len(missing_repos)
    lines.append(f"\n已完整生成 **{complete}** 份报告。")
    return "\n".join(lines)


def generate_summary_report(
    period: str,
    repos: List[Dict],
    output_path: Path,
    missing_repos: Optional[List[str]] = None,
    research_method: str = "Web搜索 + GitHub页面分析",
) -> Path:
    """
    Generate a summary report for all trending repos.

    Args:
        period: 'daily', 'weekly', or 'monthly'
        repos: List of repo data with analysis
        output_path: Path to save the report
        missing_repos: List of 'owner/repo' strings whose individual research
            reports could not be generated or were found incomplete. When
            non-empty the status section shows a ⚠️ warning instead of ✅.
            Pass an empty list (or omit) if all reports are complete.
        research_method: Description of the research approach used, written
            into the report footer for transparency.

    Returns:
        Path to the generated report
    """
    if missing_repos is None:
        missing_repos = []
    if isinstance(output_path, str):
        output_path = Path(output_path)
    
    ensure_dir(output_path.parent)
    
    period_names = {
        "daily": "日榜",
        "weekly": "周榜",
        "monthly": "月榜"
    }
    
    language_stats = {}
    for repo in repos:
        lang = repo.get("language", "Unknown")
        language_stats[lang] = language_stats.get(lang, 0) + 1
    
    total_stars = sum(r.get("stars", 0) for r in repos)
    total_today = sum(r.get("today_stars", 0) for r in repos)
    
    content = f"""# GitHub Trending {period_names.get(period, period)}报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 概览

| 统计项 | 数值 |
|--------|------|
| 分析项目数 | {len(repos)} |
| 总 Stars | {total_stars:,} |
| 今日新增 Stars | {total_today:,} |

### 语言分布

{format_language_stats(language_stats)}

## 项目列表

| 排名 | 项目 | 语言 | Stars | 今日增长 | 描述 |
|------|------|------|-------|----------|------|
{format_repo_table(repos, period)}

## 趋势分析

{analyze_trends(repos, language_stats)}

## 详细报告链接

{format_report_links(repos, period)}

## 报告状态说明

{_format_report_status(repos, missing_repos)}

---
*本报告由 GitHub Trending Analyzer 自动生成*
*分析方法: {research_method}*
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path


def format_language_stats(stats: Dict[str, int]) -> str:
    """Format language statistics."""
    if not stats:
        return "暂无数据"
    
    total = sum(stats.values())
    lines = []
    for lang, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        lines.append(f"- **{lang}**: {count} 个项目 ({pct:.1f}%)")
    return "\n".join(lines)


def format_repo_table(repos: List[Dict], period: str) -> str:
    """Format repos as markdown table rows."""
    lines = []
    for i, repo in enumerate(repos, 1):
        owner = repo.get("owner", "")
        name = repo.get("repo", "")
        lang = repo.get("language", "Unknown")
        stars = repo.get("stars", 0)
        today = repo.get("today_stars", 0)
        desc = repo.get("description", "")[:50] + "..." if len(repo.get("description", "")) > 50 else repo.get("description", "")
        desc = desc.replace("|", "\\|")
        
        lines.append(f"| {i} | [{owner}/{name}](./research_{owner}_{name}.md) | {lang} | {stars:,} | +{today:,} | {desc} |")
    return "\n".join(lines)


def analyze_trends(repos: List[Dict], language_stats: Dict[str, int]) -> str:
    """Analyze and describe trends."""
    if not repos:
        return "暂无数据可供分析"
    
    parts = []
    
    top_lang = max(language_stats.items(), key=lambda x: x[1])[0] if language_stats else "Unknown"
    parts.append(f"**热门语言**: {top_lang} 以 {language_stats.get(top_lang, 0)} 个项目领跑榜单。")
    
    top_repo = repos[0] if repos else {}
    if top_repo:
        parts.append(f"**榜首项目**: [{top_repo.get('owner', '')}/{top_repo.get('repo', '')}]({top_repo.get('url', '#')}) "
                    f"今日获得 +{top_repo.get('today_stars', 0):,} Stars。")
    
    ai_related = sum(1 for r in repos if any(kw in r.get("description", "").lower() 
                   for kw in ["ai", "agent", "llm", "gpt", "claude", "model"]))
    if ai_related > 0:
        parts.append(f"**AI 热点**: {ai_related} 个项目与 AI/LLM 相关，持续保持高热度。")
    
    return "\n\n".join(parts)


def format_report_links(repos: List[Dict], period: str) -> str:
    """Format links to individual reports."""
    lines = []
    for repo in repos:
        owner = repo.get("owner", "")
        name = repo.get("repo", "")
        link = f"./research_{owner}_{name}.md"
        lines.append(f"- [{owner}/{name}]({link})")
    return "\n".join(lines)


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python report_generator.py <command> [args]")
        print("Commands:")
        print("  project <repo_json> <analysis_json> <output_path>")
        print("  summary <period> <repos_json> <output_path>")
        print("  info                                     - Show skill directory info")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "project":
        if len(sys.argv) < 5:
            print("Usage: python report_generator.py project <repo_json> <analysis_json> <output_path>")
            sys.exit(1)

        try:
            repo_data = json.loads(sys.argv[2])
            analysis_data = json.loads(sys.argv[3])
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON argument — {e}", file=sys.stderr)
            sys.exit(1)
        output_path = Path(sys.argv[4])

        result = generate_project_report(repo_data, analysis_data, output_path)
        print(f"Report generated: {result}")

    elif command == "summary":
        if len(sys.argv) < 5:
            print(
                "Usage: python report_generator.py summary <period> <repos_json>"
                " <output_path> [missing_repos_json] [research_method]"
            )
            sys.exit(1)

        period = sys.argv[2]
        try:
            repos = json.loads(sys.argv[3])
        except json.JSONDecodeError as e:
            print(f"Error: invalid repos JSON — {e}", file=sys.stderr)
            sys.exit(1)
        output_path = Path(sys.argv[4])
        try:
            missing_repos = json.loads(sys.argv[5]) if len(sys.argv) > 5 else []
        except json.JSONDecodeError as e:
            print(f"Error: invalid missing_repos JSON — {e}", file=sys.stderr)
            sys.exit(1)
        research_method = sys.argv[6] if len(sys.argv) > 6 else "Web搜索 + GitHub页面分析"

        result = generate_summary_report(period, repos, output_path, missing_repos, research_method)
        print(f"Summary report generated: {result}")
    
    elif command == "info":
        skill_dir = get_skill_dir()
        reports_dir = get_default_reports_dir()
        print(json.dumps({
            "skill_directory": str(skill_dir),
            "default_reports_directory": str(reports_dir)
        }, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
