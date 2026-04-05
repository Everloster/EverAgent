# GitHub Trending Analyzer: Tool Guide

> 离线知识库摘要。完整规则见各技能的 SKILL.md，本文件只做入口索引。

## 两个技能

| 技能 | SKILL.md 路径 | 用途 |
|------|--------------|------|
| `github-trending-analyzer` | `github-trending-analyzer/SKILL.md` | 抓取榜单 → 驱动深度分析 → 生成汇总报告 |
| `github-deep-research` | `github-deep-research/SKILL.md` | 对单个 Repo 进行多轮深度研究（所有 Agent 均可直接调用） |

## 辅助脚本（快速参考）

```bash
# 获取榜单
python3 github-trending-analyzer/trending_fetcher.py fetch daily

# 检查缓存（7天内有效则跳过）
python3 github-trending-analyzer/trending_fetcher.py check owner/repo

# GitHub API 数据获取
python3 github-deep-research/scripts/github_api.py <owner> <repo> summary
```

## 输出目录

所有报告统一写入 `github-trending-reports/`：
- `all-{daily|weekly|monthly}-summary-YYYY-MM-DD.md` — 汇总报告
- `research_{owner}_{repo}.md` — 单项目报告（保留 GitHub 原始大小写）

完整索引：[`reports_index.md`](./reports_index.md)
