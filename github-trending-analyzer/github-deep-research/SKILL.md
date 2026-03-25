---
name: github-deep-research
description: Conduct multi-round deep research on any GitHub Repo. Use when users request comprehensive analysis, timeline reconstruction, competitive analysis, or in-depth investigation of GitHub. Produces structured markdown reports with executive summaries, chronological timelines, metrics analysis, and Mermaid diagrams. Triggers on Github repository URL or open source projects.
---

# GitHub Deep Research

多轮深度研究技能，供**所有 Agent 平台**使用，结合 GitHub API + web_search + web_fetch 生成综合分析报告。

## 4 轮研究流程

| 轮次 | 方法 | 目标 |
|------|------|------|
| Round 1 | GitHub API | 仓库基础数据、README、代码树 |
| Round 2 | 3-5 次 web_search | 项目概况、关键术语、主要竞品 |
| Round 3 | 5-10 次 web_search + web_fetch | 技术架构、时间线、社区评价 |
| Round 4 | 深度 API 分析 | commit 历史、Issue/PR 演进、贡献者活动 |

搜索策略：由宽到窄 — `"{topic} overview"` → `"{topic} architecture"` → `"{topic} vs alternatives"` → `"site:github.com {topic}"`

信息源优先级（高→低）：官方文档/仓库 → 技术博客 → 新闻媒体 → 社区讨论(Reddit/HN) → 社交媒体

## GitHub API 工具

直接执行脚本（不要用 read_file()）：

```bash
python /path/to/skill/scripts/github_api.py <owner> <repo> <command>
```

可用命令：`summary` `info` `readme` `tree` `languages` `contributors` `commits` `issues` `prs` `releases`

## 报告结构

参考 `assets/report_template.md`，必须包含以下章节：

1. **Metadata** — 日期、置信度、研究主题
2. **Executive Summary** — 2-3 句概述 + 关键指标
3. **Chronological Timeline** — 分阶段时间线（含日期）
4. **Key Analysis** — 技术架构、核心功能、使用场景
5. **Metrics & Comparisons** — 数据表格、增长曲线
6. **Strengths & Weaknesses** — 优劣势评估
7. **Sources** — 分类参考来源
8. **Confidence Assessment** — 按置信度分级的声明
9. **Methodology** — 研究方法说明

### 输出文件命名

默认：`research_{topic}_{YYYYMMDD}.md`

> **被 `github-trending-analyzer` 调用时**：使用调用方的命名规范 — `research_{owner}_{repo}.md`（无日期后缀，owner/repo 保留 GitHub 原始大小写和连字符）。trending analyzer 的 `check` 命令依赖此格式检测已有报告，避免重复生成。

## 置信度评分

| 置信度 | 适用条件 |
|--------|---------|
| High (90%+) | 官方文档、GitHub 数据、多源印证 |
| Medium (70-89%) | 单一可靠来源、近期文章 |
| Low (50-69%) | 社交媒体、未验证声明、过期信息 |

## 格式规范

- 中文内容用全角标点（，。：；！？）
- Mermaid 图表仅用：`flowchart` `gantt` `sequenceDiagram` `pie`（禁用 mindmap / timeline 等不兼容类型）
- 数据表格用于指标对比；代码块用于技术示例
- 首次提及技术术语时附 Wiki/文档链接
- 来源标注尽量贴近对应声明

## 核心原则

1. 从官方来源起步，用 commit/PR 时间戳验证日期（比文章可靠）
2. 关键声明至少 2 个独立来源印证；如有矛盾信息，如实标注而非隐藏
3. 区分事实与观点，主观判断明确标注"推测"或"社区反馈"
