# github-trending-analyzer — 执行协议

> 公开 GitHub 仓库与 trending 研究。联网和提交规则由根 `AGENTS.md` 负责；本文件只保留分流、证据要求和产物边界。

## 先分流

| 用户意图 | 动作 | 产物 |
|---|---|---|
| 只发送 repo 链接，未要求研究 | 读取仓库概览和 README，口头介绍 | 不落文件 |
| 明确要求“深挖 / 研究 / 出报告” | 使用 [repo-research](./skills/repo-research/SKILL.md) | `reports/research_{owner}_{repo}.md` |
| 要求日、周、月 trending | 使用 [trending-analyzer](./skills/trending-analyzer/SKILL.md) | 汇总报告及必要的 repo 报告 |

已有同名报告时，先说明上次分析时间与变化范围；用户已经明确要求更新时直接更新，只有“覆盖还是换视角”会实质改变产物时才询问。

## 数据与证据

- 公开仓库结构、文件读取和文档搜索先走 eacli 的 `repo.public.*` typed capabilities。
- Stars、forks、issue、PR、release 等 typed capability 未覆盖的精确元数据，可用 `gh api` 最小补充，并记录降级原因。
- 技术分析必须读取真实代码；README 与代码冲突时，以代码为准并指出差异。
- 数字现查现填。核心结论就地标 `[代码]`、`[API]`、`[README]`、`[Web]` 或 `[推测]`。
- 临时材料放 `/tmp/github-trending-{date}/`，不得提交。

## 报告合同

- 单 repo 报告保留七部分：概述、基本信息、技术分析、社区活跃度、发展趋势、竞品对比、总结评价。
- 新报告增加标准 frontmatter 与 `quality_schema: "report-v1"`。
- 报告命名保持 GitHub 原始大小写与连字符：`research_{owner}_{repo}.md`；换视角追加小写英文后缀。
- Trending 报告如实区分本轮新研究与缓存复用。

详细研究轮次、命令和异常处理只在两个 skill 中维护，不复制到本文件。

## 完成定义与策展

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

每次任务都做简短反思；只有跨 repo 可复用的失败、取数方法或证据要求才以局部 delta 更新 skill。一次性项目特例留在报告，避免把经验无限堆进常驻 context。
