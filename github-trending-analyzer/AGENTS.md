# github-trending-analyzer — 领域协议

> 公开 GitHub 仓库与 trending 研究。

## 路由

| 用户意图 | 入口 | 产物 |
|---|---|---|
| 只发送 repo 链接 | 读取概览和 README | 口头介绍，不落文件 |
| 明确深挖、研究或出报告 | [repo-research](./skills/repo-research/SKILL.md) | 单仓深研报告 |
| 日、周、月 trending | [trending-analyzer](./skills/trending-analyzer/SKILL.md) | 汇总及必要的单仓报告 |

长期报告同时使用根级 [`everagent-report`](../.agents/skills/everagent-report/SKILL.md)。已有报告且用户明确要求更新时直接更新；只有覆盖原视角会改变预期时才询问。

## 领域约束

- 仓库结构、文件和文档先走 eacli `repo.public.*`；未覆盖的精确元数据才用 `gh api` 最小补充并记录原因。
- 技术结论读取真实代码；README 与代码冲突时指出差异并以代码为准。
- Stars、forks、issue、PR 和 release 数字现查现填；结论标 `[代码]`、`[API]`、`[README]`、`[Web]` 或 `[推测]`。
- 临时材料放 `/tmp/github-trending-{date}/`，不得提交。

七章结构、命名、研究轮次和检查命令由对应 skill 与根级工作流拥有。
