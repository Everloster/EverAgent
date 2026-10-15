---
name: "trending-analyzer"
description: "Analyze GitHub Trending for a requested day, week, or month, research uncached repositories, and produce a Chinese summary with honest cache and missing-report status."
---

# GitHub Trending 汇总分析

用户明确要求日榜、周榜或月榜研究时使用。产物为 `reports/all-{period}-summary-{date}.md`，并复用或生成榜单内的单 repo 深研报告。

## 流程

1. 明确 `daily / weekly / monthly` 与可选语言筛选；请求已明确时直接执行。
2. 按根协议先选择并调用 eacli `web.read` 读取 GitHub Trending。若返回格式无法支持榜单解析，才运行现有 `scripts/trending_fetcher.py fetch <period> [language]`，并记录降级原因。
3. 对每个 repo 运行 `python3 scripts/trending_fetcher.py check owner/repo`：七天内有效报告记为缓存复用，其余调用 [repo-research](../repo-research/SKILL.md)。
4. 只有每个 repo 都有新报告、有效缓存或明确的缺失原因后，才生成汇总。
5. 汇总必须区分“本轮新研究”“缓存复用”“报告缺失”；缺失报告使用纯文本，不生成不存在的本地链接。

## 证据与写作

- Stars、Forks、协议、最近推送和活跃度数字必须现查；typed capability 未覆盖时才用 `gh api`。
- 单 repo 报告遵守 repo-research 的四轮证据与七章结构。
- 汇总说明抓取时点、榜单周期、语言筛选和缓存阈值。
- 趋势判断至少引用榜单数据或单 repo 证据；把事实、维护者计划与 `[推测]` 分开。
- 新报告使用标准 frontmatter、`quality_schema: "report-v1"` 与 `semantic_tags`。

## 辅助命令

在 `github-trending-analyzer/` 目录运行：

```bash
python3 scripts/trending_fetcher.py fetch daily
python3 scripts/trending_fetcher.py fetch weekly python
python3 scripts/trending_fetcher.py check owner/repo
python3 scripts/report_generator.py summary daily '<repos_json>' output.md '<missing_repos_json>'
```

中间材料放 `/tmp/github-trending-{YYYY-MM-DD}/`，完成后清理。报告只写入 `reports/`。

## 完成定义

从仓库根目录运行：

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

每次任务都做简短反思；只有跨 repo 可复用或高风险的新发现才以最小 delta 更新 skill/reference。
