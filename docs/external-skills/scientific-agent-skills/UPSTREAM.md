# UPSTREAM — scientific-agent-skills 同步记录

> 本目录是外部技能的 vendor 副本。**本地是事实源的消费层，上游是事实源的生产层**：
> 平时直接用仓内副本；上游更新后跑同步脚本拉新版（见下）。

## 来源

- 仓库：<https://github.com/K-Dense-AI/scientific-agent-skills>（MIT，Agent Skills 标准）
- 选入原因与评估结论见记忆/对话：163 个技能里只挑了 2 个方法论通用、零依赖（纯 md + Python 3.11 标准库）的；其余与 EverAgent 五领域无交集，不引入
- 上游技能总数 163，本仓只 vendor：`hypothesis-generation`、`scientific-writing`

## 同步记录（新条目加在最上面）

| 日期 | 上游 commit | 技能版本 | 本地改动 | 备注 |
|---|---|---|---|---|
| 2026-09-01 | `1dd0fcc` | hypothesis-generation v2.1 / scientific-writing v2.0 | 无（原样拷入） | 首次引入 |

## 怎么同步上游更新

```bash
scripts/sync-external-skills.sh          # 拉上游 → 覆盖两技能 → git diff 展示变化
scripts/sync-external-skills.sh --install # 额外：把仓内副本投射到 ~/.agents/skills/（本机 Skill 工具原生调用）
```

同步脚本只覆盖 `docs/external-skills/scientific-agent-skills/{hypothesis-generation,scientific-writing}` 两个目录；先完整暂存再替换，本地缺目录也会补齐，上游缺目录则非零失败且不改本地。输出完整上游 commit 供更新记录；`--install` 仍只在显式指定时执行。

## 消费方式（两种并存）

1. 需要发展假设时，可读[假设生成](./hypothesis-generation/SKILL.md)。需要核对科学写作证据时，可读[科学写作](./scientific-writing/SKILL.md)。日常研究遵循[报告工作流](../../REPORT_WORKFLOW.md)。
2. 同步时显式使用 `--install`，可将仓内副本安装到 `~/.agents/skills/`，由 Agent 读取技能元数据。
