---
name: "github-trending-analyzer"
description: "Analyzes GitHub trending repositories by day/week/month using deep research. Invoke when user asks to analyze GitHub trending projects or generate trending reports."
---

# GitHub 热点项目分析

对 GitHub Trending 热点项目进行深度分析，生成结构化趋势报告。

## 触发条件

- 分析 GitHub 热点项目 / 生成 trending 报告 / 查询当前热门项目趋势

> 完整执行规范见 [`TASK_PROTOCOL.md`](../TASK_PROTOCOL.md) TT-1 章节，本文件提供技能摘要和脚本速查。

## 环境配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `GITHUB_TOKEN` | 避免 API 速率限制 | 无 |
| `TRENDING_REPORTS_DIR` | 报告输出目录 | `./github-trending-reports` |

## 辅助工具

### trending_fetcher.py

```bash
python3 <skill_dir>/trending_fetcher.py fetch daily      # 获取日榜（daily/weekly/monthly）
python3 <skill_dir>/trending_fetcher.py fetch daily python  # 按语言过滤
python3 <skill_dir>/trending_fetcher.py check owner/repo  # 检查报告缓存状态
python3 <skill_dir>/trending_fetcher.py info             # 查看技能路径
```

`check` 命令输出：`{"exists": bool, "age_days": float, "needs_update": bool}`

### report_generator.py

```bash
python3 <skill_dir>/report_generator.py project '<repo_json>' '<research_json>' output.md
python3 <skill_dir>/report_generator.py summary daily '<repos_json>' output.md
```

生成基础模板；深度内容需 Agent 补充。

---

## 目录结构（严格遵守）

```
github-trending-analyzer/     ← 只读，Agent 不可修改
github-deep-research/         ← 只读，所有 Agent 使用此技能完成单个 repo 深度研究
github-trending-reports/      ← 【唯一输出目录】
├── all-{period}-summary-YYYY-MM-DD.md   ← 汇总报告
└── research_{owner}_{repo}.md           ← 单项目报告（仅允许这两种格式）
knowledge/                    ← 仅追加更新 reports_index.md，不可删除已有条目
```

**写入限制**：只能写 `github-trending-reports/` 和 `knowledge/`，禁止在其他目录创建文件，禁止修改 SKILL.md / 脚本 / README / CONTEXT.md。

**文件命名**：`{owner}` 和 `{repo}` 必须与 GitHub 原始名称大小写完全一致。
- ✅ `research_hsliuping_TradingAgents-CN.md`
- ❌ `research_hsliuping_tradingagents_cn.md`

## 临时文件（Tmp）

使用 `/tmp/github-trending-{YYYY-MM-DD}/` 存放中间文件。**任务完成后必须清理**，禁止将路径写入报告，禁止提交到 Git。

```python
import shutil; shutil.rmtree(f"/tmp/github-trending-{today}", ignore_errors=True)
```

---

## 执行流程

### 1. 获取 Trending 列表

```bash
python3 <skill_dir>/trending_fetcher.py fetch daily
```

### 2. 逐项目深度分析

对每个项目：
1. 运行 `check` 命令 → 7 天内有缓存则跳过
2. **调用 `github-deep-research` 技能** 完成深度研究（所有 Agent 平台均应使用此技能）
3. 将研究结果转换为本技能的 7 章中文格式写入 `research_{owner}_{repo}.md`

### 3. 验证报告完整性

**必须在汇总前完成**：每份报告应包含以下 7 章，且总行数 ≥ 150：

| 章节 | 最低要求 |
|------|---------|
| 项目概述 | ≥ 50 字 |
| 基本信息 | 完整表格（Stars/Forks/语言/协议/时间）|
| 技术分析 | ≥ 2 子章节（技术栈/架构/核心功能）|
| 社区活跃度 | ≥ 2 子章节 |
| 发展趋势 | ≥ 1 子章节 |
| 竞品对比 | 表格，≥ 2 个竞品 |
| 总结评价 | 优势/劣势/适用场景 |

### 4. 生成汇总报告

> ❌ **禁止跳过步骤 2-3 直接生成汇总**。必须确认榜单内**每个 repo** 的深度报告均已生成（或缓存有效）后，才能执行本步骤。

见下方模板。**报告状态说明必须如实区分新生成和缓存复用**（见常见失误 #1）。

---

## 报告格式

### 单项目报告

```markdown
# {owner}/{repo}

> {描述}

## 项目概述
{2-3 句定位与核心价值}

## 基本信息
| 指标 | 数值 |
|------|------|
| Stars | {stars} |
| Forks | {forks} |
| 语言 | {language} |
| 开源协议 | {license} |
| 创建时间 | {created_at} |
| 最近更新 | {updated_at} |
| GitHub | [{url}]({url}) |

## 技术分析
### 技术栈
### 架构设计
### 核心功能

## 社区活跃度
### 贡献者分析
### Issue/PR 活跃度
### 最近动态

## 发展趋势
### 版本演进
### Roadmap
### 社区反馈

## 竞品对比
| 项目 | Stars | 语言 | 特点 |

## 总结评价
### 优势
### 劣势
### 适用场景

---
*报告生成时间: {datetime}*
*研究方法: GitHub API 多维度分析 + Web 搜索*
```

### 汇总报告

```markdown
# GitHub Trending {周期}报告

> 生成时间: {datetime}

## 概览
| 统计项 | 数值 |
| 分析项目数 / 总Stars / 今日新增 |

### 语言分布
### 热门领域

## 项目列表
| 排名 | 项目（链接） | 语言 | Stars | 今日增长 | 描述 |

## 趋势分析
### 🔥 热门趋势
### 🏢 大厂动态
### 🔬 技术创新
### 📊 语言趋势

## 详细报告链接
- [owner/repo](./research_xxx.md) - 简短描述

## 报告状态说明
✅ 今日新生成（N 份）：...
📦 缓存复用（N 份，7天内已生成）：...

---
*本报告由 GitHub Trending Analyzer 自动生成*
```

---

## 注意事项

1. **深度研究**：单项目研究必须调用 `github-deep-research` 技能；研究结果转换为本技能的 7 章中文格式后存档
2. **数据精度**：Stars/Forks 等必须使用 API 精确返回值，禁止使用"17,000+"等模糊表达
3. **缓存机制**：7 天内已生成的报告跳过重新分析；汇总状态必须如实区分新生成和缓存
4. **Mermaid 限制**：仅用 `flowchart` / `sequenceDiagram` / `gantt` / `pie`；禁用 `mindmap`、`timeline` 等不兼容类型
5. **路径安全**：报告内容禁止出现宿主机路径（`/sessions/`、`/mnt/`、`/tmp/` 等）
6. **API 控速**：批量分析时控制并发，避免触发 GitHub API 限制

---

## ❌ 常见失误

| # | 错误行为 | 正确做法 |
|---|---------|---------|
| 1 | 汇总报告写"✅ 所有 N 份完整生成"，实际有缓存复用 | 如实列出新生成和缓存复用两部分 |
| 2 | 将 github-deep-research 的英文模板直接存档（Executive Summary / Confidence Assessment 等章节） | 研究结果必须转换为本技能 7 章中文结构后存档 |
| 3 | 报告页脚出现"Github Deep Research by DeerFlow"等其他品牌 | 统一用 `*报告生成时间: ...` / `*研究方法: ...` |
| 4 | Stars 写"17,000+"等模糊值 | 使用 API 精确返回的整数 |
| 5 | 趋势分析只写 2-3 行 | 必须包含 🔥/🏢/🔬/📊 四个子章节 |
