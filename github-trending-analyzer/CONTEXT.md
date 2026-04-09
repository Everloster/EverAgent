# github-trending-analyzer — Project Context

> **Agent 协议**：操作本项目前须读取 [AGENTS.md](./AGENTS.md)（TrendAgent 自包含协议）。执行完成后按协议 §5 提交推送。

**领域**：GitHub 开源热点追踪·Repo 深度研究·趋势洞察知识库
**双重身份**：自动化分析工具 + 开源生态知识库

## 任务类型
→ **[TASK_PROTOCOL.md](./TASK_PROTOCOL.md)**（执行前必读，定义全部任务类型、脚本调用、命名规则和验收标准）

| 类型 | 场景 |
|------|------|
| TT-1 trending_report | 生成日/周/月 trending 汇总报告 |
| TT-2 repo_research | 对单个 repo 深度研究 |
| TT-3 index_sync | 同步知识索引（每次 TT-1/TT-2 后必执行） |
| TT-4 validate_all | 验证全部报告质量（`python3 scripts/validate_reports.py --fail-only --index`） |

## 工具能力
- 按日/周/月抓取 GitHub Trending，对**每个 repo 完成深度分析后**再生成汇总报告
- 对单个 Repo 多轮深度研究（GitHub API + 网络搜索），使用 `github-deep-research` 技能
- 输出含架构分析·竞品对比·Mermaid 图表的结构化报告
- **报告质量验证**：`scripts/validate_reports.py` 执行 8 项检查（命名/结构/长度/精度/竞品/页脚/路径/语言），TT-1/TT-2 每次写入后必须通过

## 知识库现状（`github-trending-reports/`）
- **汇总报告**：daily ×7、weekly ×1、monthly ×2（共 10 篇）
- **Repo 深度报告**：73 篇（AI/ML、DevTools、Infra、Agent 等类别）
- 完整索引 → [`knowledge/reports_index.md`](./knowledge/reports_index.md)

## 离线知识库
→ [`knowledge/INDEX.md`](./knowledge/INDEX.md)

## Skills
- `github-trending-analyzer/SKILL.md` — 热点趋势分析（TT-1 主技能）
- `github-deep-research/SKILL.md` — 单 Repo 深度研究（TT-1/TT-2 子技能）

## 导航
- 任务协议：`TASK_PROTOCOL.md`
- 报告目录：`github-trending-reports/`
- 工具脚本：`github-trending-analyzer/` · `github-deep-research/`

## 变更记录
→ [`CHANGELOG.md`](./CHANGELOG.md)（记录各 Agent 的变更与 review 结论）

## ⚠️ 边界（防幻觉）
- 只有 `knowledge/reports_index.md` 中列出的 Repo 才有分析报告，其余禁止推测
- 报告内容须读取对应文件确认，禁止凭记忆复述报告细节
