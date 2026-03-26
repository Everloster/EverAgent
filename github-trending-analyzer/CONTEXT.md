# github-trending-analyzer — Project Context

> **Agent 协议**：操作本项目前须完成 [AGENTS.md](../AGENTS.md) §0 初始化。任务3（执行任务）完成后须按 §4 自动提交推送。

**领域**：GitHub 开源热点追踪·Repo 深度研究·趋势洞察知识库
**双重身份**：自动化分析工具 + 开源生态知识库

## 工具能力
- 按日/周/月抓取 GitHub Trending，对**每个 repo 完成深度分析后**再生成汇总报告
- 对单个 Repo 多轮深度研究（GitHub API + 网络搜索），使用 `github-deep-research` 技能
- 输出含架构分析·竞品对比·Mermaid 图表的结构化报告

> ⚠️ **执行顺序铁律**：汇总报告（`all-*.md`）必须在榜单内所有 repo 的深度分析报告全部生成或确认缓存有效后才能生成。禁止先出汇总、再补深度分析。

## 知识库现状（`github-trending-reports/`）
- **汇总报告**：daily ×4、weekly ×1、monthly ×2（共 7 篇）
- **Repo 深度报告**：57 篇（AI/ML、DevTools、Infra、Agent 等类别）
- 完整索引 → [`knowledge/reports_index.md`](./knowledge/reports_index.md)

## 离线知识库
→ [`knowledge/INDEX.md`](./knowledge/INDEX.md)

## Skills
- `github-trending-analyzer/` — 热点趋势分析
- `github-deep-research/` — 单 Repo 深度研究

## 导航
- 报告目录：`github-trending-reports/`
- 工具脚本：`github-trending-analyzer/` · `github-deep-research/`

## 变更记录
→ [`CHANGELOG.md`](./CHANGELOG.md)（记录各 Agent 的变更与 review 结论）

## ⚠️ 边界（防幻觉）
- 只有 `knowledge/reports_index.md` 中列出的 Repo 才有分析报告，其余禁止推测
- 报告内容须读取对应文件确认，禁止凭记忆复述报告细节
