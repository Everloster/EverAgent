#!/usr/bin/env python3
"""Filter starred repos by time window, categorize, and generate summary report.

Reads:  raw/page_NNN.json (must contain starred_at via Accept: application/vnd.github.star+json)
Writes: data/starred_{period}_detailed.json (already enriched by API response)
        data/categories_{period}.json
        reports/everloster-star-{period}-summary-{YYYY-MM-DD}.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw"
DATA = ROOT / "data"
REPORTS = ROOT / "reports"

# --- 分类规则: (category, topic_set, desc_keywords) ---
CATEGORY_RULES: list[tuple[str, set[str], set[str]]] = [
    ("AI/LLM Agent", {
        "llm", "agent", "agents", "llm-agent", "agentic", "mcp", "langchain",
        "llama-index", "openai", "claude", "gpt", "rag", "chatbot", "prompt",
        "anthropic", "huggingface", "transformer", "chatgpt", "gemini",
    }, {
        " llm", "agent", "agents", "chatgpt", "claude", "gpt", "rag ",
        "language model", "prompt", "anthropic", "langchain",
    }),
    ("机器学习/深度学习", {
        "machine-learning", "deep-learning", "pytorch", "tensorflow",
        "keras", "scikit-learn", "neural-network", "reinforcement-learning",
        "computer-vision", "nlp", "stable-diffusion", "diffusion", "jax",
        "mlops", "ml",
    }, {
        "machine learning", "deep learning", "pytorch", "tensorflow",
        "neural", "training", "model", "inference",
    }),
    ("前端/UI", {
        "react", "vue", "angular", "svelte", "nextjs", "nuxt", "frontend",
        "tailwindcss", "css", "design-system", "ui", "ux", "web-components",
        "typescript", "javascript",
    }, {"react", "vue", "angular", "frontend", "ui kit", "design system"}),
    ("后端/API", {
        "api", "rest-api", "graphql", "grpc", "backend", "framework",
        "fastapi", "django", "flask", "express", "nestjs", "spring",
        "postgresql", "mysql", "redis", "mongodb", "database", "orm",
        "sql",
    }, {"rest api", "graphql", "backend", "api framework", "orm"}),
    ("基础设施/DevOps", {
        "kubernetes", "docker", "devops", "terraform", "ansible", "helm",
        "ci-cd", "github-actions", "cloud", "aws", "gcp", "azure",
        "observability", "monitoring", "logging", "linux", "server",
        "nginx", "prometheus", "grafana",
    }, {"kubernetes", "docker", "devops", "terraform", "ci/cd", "observability"}),
    ("命令行/终端", {
        "cli", "terminal", "shell", "tui", "command-line", "zsh", "bash",
        "vim", "neovim", "tmux", "productivity", "dotfiles",
    }, {"command line", "cli tool", "terminal", "tui", "shell script"}),
    ("编辑器/IDE", {
        "vscode", "editor", "ide", "neovim", "vim", "emacs", "intellij",
        "vscode-extension", "jetbrains",
    }, {"vscode", "editor plugin", "ide plugin", "neovim plugin"}),
    ("安全/密码学", {
        "security", "cybersecurity", "infosec", "cryptography", "pentest",
        "vulnerability", "ctf", "oauth", "auth", "iam",
    }, {"security tool", "vulnerability", "pentest", "cryptography"}),
    ("数据/分析", {
        "data-science", "data-analysis", "data-engineering", "analytics",
        "jupyter", "pandas", "spark", "kafka", "etl", "data-pipeline",
        "elt", "dbt",
    }, {"data pipeline", "etl", "data analysis", "analytics"}),
    ("区块链/Web3", {
        "blockchain", "web3", "cryptocurrency", "ethereum", "bitcoin",
        "solidity", "smart-contracts", "nft", "defi",
    }, {"blockchain", "web3", "ethereum", "smart contract"}),
    ("移动端", {
        "ios", "android", "mobile", "react-native", "flutter", "swift",
        "kotlin", "swiftui", "jetpack-compose",
    }, {"ios app", "android app", "react native", "flutter"}),
    ("游戏开发", {
        "game", "gamedev", "game-engine", "unity", "godot", "unreal-engine",
    }, {"game engine", "gamedev"}),
    ("多媒体/音视频", {
        "audio", "video", "ffmpeg", "media", "streaming", "image",
        "image-processing", "graphics",
    }, {"video processing", "audio processing", "ffmpeg", "image processing"}),
    ("文档/知识库", {
        "docs", "documentation", "wiki", "knowledge-base", "note-taking",
        "markdown", "obsidian", "blog", "static-site", "hugo", "jekyll",
    }, {"knowledge base", "note taking", "static site", "wiki engine"}),
    ("学习/教程/书籍", {
        "tutorial", "course", "learning", "education", "awesome",
        "awesome-list", "roadmap", "book", "interview", "resources",
    }, {"awesome list", "tutorial", "learning resource", "roadmap"}),
    ("嵌入式/IoT/硬件", {
        "iot", "embedded", "arduino", "raspberry-pi", "hardware",
        "robotics", "firmware",
    }, {"iot", "embedded system", "raspberry pi", "arduino"}),
]


def categorize(item: dict) -> str:
    topics = {t.lower() for t in (item.get("topics") or [])}
    desc = " " + (item.get("description") or "").lower() + " "
    name = (item.get("full_name") or "").lower()
    for cat, topic_set, desc_kws in CATEGORY_RULES:
        if topics & topic_set:
            return cat
        if any(kw in desc for kw in desc_kws):
            return cat
    lang = (item.get("language") or "").lower()
    lang_fallback = {
        "python": "Python 工具",
        "javascript": "JavaScript 工具",
        "typescript": "TypeScript 工具",
        "go": "Go 工具",
        "rust": "Rust 工具",
        "java": "Java 工具",
        "kotlin": "Kotlin 工具",
        "swift": "Swift 工具",
        "c++": "C++ 工具",
        "c": "C 工具",
        "ruby": "Ruby 工具",
        "php": "PHP 工具",
        "shell": "Shell 工具",
        "html": "前端/HTML",
        "css": "前端/CSS",
        "jupyter notebook": "数据/分析",
    }
    return lang_fallback.get(lang, "其他/未分类")


def period_to_cutoff(period: str, today: datetime) -> datetime:
    if period == "all":
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    years = int(period.rstrip("y"))
    return today - timedelta(days=365 * years + 1)  # +1 for leap-year safety


def load_raw() -> list[dict]:
    items = []
    for f in sorted(RAW.glob("page_*.json")):
        items.extend(json.loads(f.read_text()))
    return items


def write_report(
    items: list[dict],
    raw_total: int,
    period: str,
    today: datetime,
    cutoff: datetime,
    out_path: Path,
) -> None:
    total = len(items)
    by_year = Counter()
    by_year_month = Counter()
    by_lang = Counter()
    by_cat = Counter()
    by_license = Counter()
    repo_by_cat: dict[str, list[dict]] = defaultdict(list)
    for it in items:
        sa = it.get("starred_at") or ""
        if len(sa) >= 4:
            by_year[sa[:4]] += 1
        if len(sa) >= 7:
            by_year_month[sa[:7]] += 1
        by_lang[it.get("language") or "未注明"] += 1
        cat = categorize(it)
        by_cat[cat] += 1
        repo_by_cat[cat].append(it)
        lic = (it.get("license") or {}).get("spdx_id") if isinstance(it.get("license"), dict) else None
        by_license[lic or "未注明"] += 1

    top = sorted(items, key=lambda x: x.get("stargazers_count") or 0, reverse=True)

    # Time-range labels
    period_label = {
        "1y": "近 1 年", "2y": "近 2 年", "3y": "近 3 年",
        "5y": "近 5 年", "all": "全部",
    }[period]

    lines: list[str] = []
    p = lines.append

    p(f"# Everloster Star 分析报告 — {period_label}({today.strftime('%Y-%m-%d')})")
    p("")
    p("> 数据来源:GitHub REST API `/user/starred`(`Accept: application/vnd.github.star+json`)。")
    p(f"> 截止时间(UTC):{cutoff.isoformat()} 当日 00:00 之后 starred 的仓库。")
    p(f"> 报告生成时间(UTC):{today.isoformat()}")
    p("")

    # 1. 报告概览
    p("## 1. 报告概览")
    p("")
    p(f"- 时间窗:**{period_label}**(自 {cutoff.strftime('%Y-%m-%d')} 起,UTC)")
    p(f"- 样本数:**{total}** 个 starred 仓库")
    p(f"- 编程语言种类(去重):**{len(by_lang)}**")
    p(f"- 主题类别数:**{len(by_cat)}**")
    if total:
        earliest = min((it.get("starred_at") or "") for it in items if it.get("starred_at"))
        latest = max((it.get("starred_at") or "") for it in items if it.get("starred_at"))
        p(f"- 最早 star:{earliest}")
        p(f"- 最晚 star:{latest}")
    p("")

    # 2. 总量与时间分布
    p("## 2. 总量与时间分布")
    p("")
    p("### 按年")
    p("")
    p("| 年份 | Star 数 | 占比 |")
    p("|------|---------|------|")
    for y, n in sorted(by_year.items()):
        p(f"| {y} | {n} | {n / total * 100:.1f}% |" if total else f"| {y} | {n} | - |")
    p("")

    # 按月
    p("### 按月(仅含 ≥ 1 个的月份)")
    p("")
    p("| 年月 | Star 数 |")
    p("|------|---------|")
    for ym, n in sorted(by_year_month.items()):
        p(f"| {ym} | {n} |")
    p("")

    # 季度热力(简单柱状文字)
    if by_year_month:
        p("### 月度活动强度(文本柱状,1 个 ▇ ≈ 1 个 star)")
        p("")
        max_n = max(by_year_month.values())
        for ym, n in sorted(by_year_month.items()):
            bar = "▇" * n
            p(f"- `{ym}` **{n:>3}** {bar}")
        p("")

    # 3. 编程语言分布
    p("## 3. 编程语言分布")
    p("")
    p("| 排名 | 语言 | 数量 | 占比 |")
    p("|------|------|------|------|")
    for i, (lang, n) in enumerate(by_lang.most_common(), 1):
        p(f"| {i} | {lang} | {n} | {n / total * 100:.1f}% |" if total else f"| {i} | {lang} | {n} | - |")
    p("")

    # 4. 主题分类
    p("## 4. 主题分类与代表项目")
    p("")
    p("| 排名 | 类别 | 数量 | 占比 | 代表项目 |")
    p("|------|------|------|------|---------|")
    sorted_cats = sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)
    for i, (cat, n) in enumerate(sorted_cats, 1):
        # 选该类别下 star 最高的 1 个做代表
        repr_repo = max(repo_by_cat[cat], key=lambda x: x.get("stargazers_count") or 0)
        repr_link = f"[{repr_repo['full_name']}]({repr_repo.get('html_url', '')}) ({repr_repo.get('stargazers_count', 0):,} ★)"
        p(f"| {i} | {cat} | {n} | {n / total * 100:.1f}% | {repr_link} |" if total else f"| {i} | {cat} | {n} | - | {repr_link} |")
    p("")

    # 5. Top N
    p("## 5. 高 Star 项目 Top 30")
    p("")
    p("| 排名 | 仓库 | 描述 | Stars | Forks | 主要语言 | Star 时间 |")
    p("|------|------|------|-------|-------|---------|---------|")
    for i, it in enumerate(top[:30], 1):
        desc = (it.get("description") or "").replace("|", "\\|").replace("\n", " ")
        if len(desc) > 80:
            desc = desc[:77] + "..."
        p(
            f"| {i} | [{it['full_name']}]({it.get('html_url', '')}) "
            f"| {desc} | {it.get('stargazers_count', 0):,} | {it.get('forks_count', 0):,} "
            f"| {it.get('language') or '-'} | {(it.get('starred_at') or '')[:10]} |"
        )
    p("")

    # 6. 趋势观察
    p("## 6. 趋势观察")
    p("")
    p("> 以下为对实际分布数据的描述性观察,不做预测。")
    p("")

    # 6.1 年度 Top 类别
    year_cats: dict[str, Counter] = defaultdict(Counter)
    for it in items:
        sa = it.get("starred_at") or ""
        if len(sa) < 4:
            continue
        year_cats[sa[:4]][categorize(it)] += 1
    if year_cats:
        p("### 6.1 各年份 Top 3 类别")
        p("")
        p("| 年份 | #1 | #2 | #3 |")
        p("|------|----|----|----|")
        for y in sorted(year_cats):
            top3 = year_cats[y].most_common(3)
            row = [y] + [f"{c} ({n})" for c, n in top3] + ["-"] * (3 - len(top3))
            p("| " + " | ".join(row[:4]) + " |")
        p("")

    # 6.2 关键词洞察
    keyword_counter: Counter = Counter()
    for it in items:
        text = " ".join([
            " ".join(it.get("topics") or []),
            it.get("description") or "",
        ]).lower()
        for kw in ("agent", "rag", "llm", "gpt", "claude", "mcp", "rust", "kubernetes",
                   "web3", "blockchain", "stable", "diffusion", "rag", "vector",
                   "knowledge", "graph", "tui", "wasm", "edge", "serverless"):
            if kw in text:
                keyword_counter[kw] += 1
    if keyword_counter:
        p("### 6.2 高频关键词(从 topics + description 提取)")
        p("")
        p("| 关键词 | 出现仓库数 |")
        p("|--------|-----------|")
        for kw, n in keyword_counter.most_common(20):
            p(f"| {kw} | {n} |")
        p("")

    # 6.3 Star 区间分布
    buckets = Counter()
    for it in items:
        s = it.get("stargazers_count") or 0
        if s < 100:
            buckets["< 100"] += 1
        elif s < 1000:
            buckets["100 ~ 1k"] += 1
        elif s < 10000:
            buckets["1k ~ 10k"] += 1
        elif s < 100000:
            buckets["10k ~ 100k"] += 1
        else:
            buckets[">= 100k"] += 1
    p("### 6.3 当前 Star 数区间分布")
    p("")
    p("| 区间 | 数量 | 占比 |")
    p("|------|------|------|")
    for k in ["< 100", "100 ~ 1k", "1k ~ 10k", "10k ~ 100k", ">= 100k"]:
        n = buckets.get(k, 0)
        p(f"| {k} | {n} | {n / total * 100:.1f}% |" if total else f"| {k} | {n} | - |")
    p("")

    # 6.4 月度峰值
    if by_year_month:
        peak_ym, peak_n = max(by_year_month.items(), key=lambda kv: kv[1])
        p(f"### 6.4 峰值月份:`{peak_ym}`(共 {peak_n} 个 star)")
        p("")
        peak_items = [it for it in items if (it.get("starred_at") or "").startswith(peak_ym)]
        peak_items.sort(key=lambda x: x.get("stargazers_count") or 0, reverse=True)
        p("| 仓库 | Stars | 描述 |")
        p("|------|-------|------|")
        for it in peak_items[:10]:
            desc = (it.get("description") or "").replace("|", "\\|")
            if len(desc) > 70:
                desc = desc[:67] + "..."
            p(f"| [{it['full_name']}]({it.get('html_url', '')}) | {it.get('stargazers_count', 0):,} | {desc} |")
        p("")

    # 7. 总结
    p("## 7. 总结")
    p("")
    top3_cats = [f"**{c}**({n},占 {n / total * 100:.1f}%)" for c, n in sorted_cats[:3]] if total else []
    top_lang = by_lang.most_common(1)[0] if by_lang else (None, 0)
    p(f"- **{period_label}** 共 star **{total}** 个仓库,平均每月 {(total / max((today - cutoff).days / 30.44, 1)):.1f} 个。"
      if total else f"- 时间窗内无数据。")
    if top3_cats:
        p(f"- 兴趣最集中的三类:{', '.join(top3_cats)}。")
    if top_lang[0]:
        p(f"- 最常 star 的语言:**{top_lang[0]}**({top_lang[1]} 个)。")
    if top:
        p(f"- 单仓 star 最高:[{top[0]['full_name']}]({top[0].get('html_url', '')}) "
          f"({top[0].get('stargazers_count', 0):,} ★,{top[0].get('language') or '-'})。")
    p("")

    # 8. 附录
    p("## 8. 附录")
    p("")
    p("### 8.1 数据来源")
    p("")
    p(f"- API:`GET /user/starred?per_page=100`")
    p(f"- 鉴权:`gh` CLI(token 存于 keyring,账号 `Everloster` / user_id `2820419`)")
    p(f"- 媒体类型:`Accept: application/vnd.github.star+json` —— 必需,否则响应不含 `starred_at`")
    p(f"- 拉取页数:全量共 {len(list(RAW.glob('page_*.json')))} 页,合计 **{raw_total}** 个 starred 仓库(全量,最早可追溯到 2012-11-17),本报告按 `{period}` 过滤后剩 **{total}** 个")
    p("")
    p("> 数据观测:全量 867 个 starred 仓库的时间分布存在两个活跃段(2015-2017 与 2025-2026),2023-2024 区间内无任何 star 记录。若非账号闲置,可能与当时的 GitHub 使用习惯/隐私设置变更有关,本报告仅如实反映 API 返回数据。")
    p("")
    p("### 8.2 方法")
    p("")
    p("- **过滤**:仅保留 `starred_at >= cutoff` 的项目")
    p("- **分类**:基于 repo `topics` 字段 + `description` 关键词的规则分类,见 `scripts/analyze.py` `CATEGORY_RULES`")
    p("- **统计**:Counter 计数,占比基于时间窗内子集")
    p("- **数据未做二次 enrich**:`/user/starred` 响应已包含 `topics` / `created_at` / `updated_at` / `license` / `stargazers_count` / `forks_count` / `language` 等字段,无需额外 API 调用")
    p("")
    p("### 8.3 限制")
    p("")
    p("- 分类为规则分类,无法归入任何规则的项目落入「其他/未分类」,可能掩盖真实兴趣")
    p("- GitHub API 返回的 `stargazers_count` 为拉取时刻的值,后续变化不在本报告反映")
    p("- `starred_at` 字段依赖 star+json 媒体类型,若 API 行为变更需同步脚本")
    p("- 公开/私有仓库均包含(token 鉴权读取)")

    out_path.write_text("\n".join(lines) + "\n")
    print(f"[REPORT] written to {out_path}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", default="3y", choices=["1y", "2y", "3y", "5y", "all"])
    ap.add_argument("--cutoff-date", default=None,
                    help="Override cutoff date (YYYY-MM-DD UTC), default: today - period")
    ap.add_argument("--data-date", default=None,
                    help="Override data date stamped in filename (YYYY-MM-DD), default: today UTC")
    args = ap.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    today = datetime.now(timezone.utc).replace(microsecond=0)
    if args.cutoff_date:
        cutoff = datetime.fromisoformat(args.cutoff_date).replace(tzinfo=timezone.utc)
    else:
        cutoff = period_to_cutoff(args.period, today)

    items = load_raw()
    raw_total = len(items)
    print(f"[INFO] loaded {raw_total} raw items", file=sys.stderr)

    in_window = [it for it in items if (it.get("starred_at") or "") >= cutoff.isoformat()]
    print(f"[INFO] in window {args.period} (>= {cutoff.isoformat()}): {len(in_window)}", file=sys.stderr)

    # 保存过滤后的子集
    detailed_path = DATA / f"starred_{args.period}_detailed.json"
    detailed_path.write_text(json.dumps(in_window, ensure_ascii=False, indent=2))

    # 保存分类结果
    cat_path = DATA / f"categories_{args.period}.json"
    cat_summary: dict[str, int] = Counter()
    for it in in_window:
        cat_summary[categorize(it)] += 1
    cat_path.write_text(json.dumps(dict(cat_summary.most_common()), ensure_ascii=False, indent=2))

    # 写报告
    data_date = args.data_date or today.strftime("%Y-%m-%d")
    out_path = REPORTS / f"everloster-star-{args.period}-summary-{data_date}.md"
    write_report(in_window, raw_total, args.period, today, cutoff, out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
