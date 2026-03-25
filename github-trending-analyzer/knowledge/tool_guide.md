# GitHub Trending Analyzer: Tool Guide

## 两个互补技能

| 技能 | 目录 | 用途 |
|------|------|------|
| `github-trending-analyzer` | `github-trending-analyzer/SKILL.md` | 抓取榜单、驱动深度分析、生成汇总报告 |
| `github-deep-research` | `github-deep-research/SKILL.md` | 对单个 Repo 进行多轮深度研究，供所有 Agent 使用 |

---

## 技能 1：github-trending-analyzer

### 触发方式
用户请求分析 GitHub 热点项目 / 生成 trending 报告时调用。

### 辅助脚本

```bash
# 获取榜单（daily / weekly / monthly）
python3 github-trending-analyzer/trending_fetcher.py fetch daily

# 检查单个 repo 报告缓存状态（7天内有效则跳过重新分析）
python3 github-trending-analyzer/trending_fetcher.py check owner/repo

# 生成报告模板（深度内容需 Agent 补充）
python3 github-trending-analyzer/report_generator.py summary daily '<json>' output.md
```

### 执行顺序（严格遵守）

```
1. 抓取榜单
       ↓
2. 对每个 repo 调用 github-deep-research 完成深度分析
   （7天内有缓存则跳过，但必须确认缓存有效）
       ↓
3. 验证所有 repo 报告完整性（缺一不可）
       ↓
4. 生成汇总报告
```

> ❌ **禁止跳过步骤 2-3 直接出汇总报告**

### 输出格式

**汇总报告**：`github-trending-reports/all-{daily|weekly|monthly}-summary-YYYY-MM-DD.md`

必须包含：概览表 → 语言分布 → 热门领域 → 项目列表（含今日增长）→ 趋势分析（🔥热门/🏢大厂/🔬技术创新/📊语言）→ 详细报告链接 → **报告状态说明**（区分新生成和缓存复用）

---

## 技能 2：github-deep-research

### 触发方式
对单个 GitHub repo 进行深度研究时调用（由 github-trending-analyzer 驱动，或用户直接请求）。

### 研究流程
4 轮：GitHub API → 广度搜索 → 深度搜索+fetch → 深度 API 分析
详见 `github-deep-research/SKILL.md`

### 输出格式

**单项目报告**：`github-trending-reports/research_{owner}_{repo}.md`

> 被 github-trending-analyzer 调用时命名格式为 `research_{owner}_{repo}.md`（owner/repo 保留 GitHub 原始大小写和连字符，无日期后缀）。

必须包含 7 个中文章节：
1. 项目概述
2. 基本信息（Stars/Forks/语言/协议/时间，完整表格）
3. 技术分析（技术栈 / 架构设计 / 核心功能）
4. 社区活跃度（贡献者 / Issue·PR 活跃度 / 最近动态）
5. 发展趋势（版本演进 / Roadmap / 社区反馈）
6. 竞品对比（表格，≥ 2 个竞品）
7. 总结评价（优势 / 劣势 / 适用场景）

报告末尾统一格式：
```
---
*报告生成时间: YYYY-MM-DD HH:MM*
*研究方法: GitHub API 多维度分析 + Web 搜索*
```

---

## 报告存档位置

所有输出统一写入 `github-trending-reports/`，两种命名格式：
- `all-{period}-summary-YYYY-MM-DD.md`
- `research_{owner}_{repo}.md`

完整索引：[`knowledge/reports_index.md`](./reports_index.md)
