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

同步脚本只覆盖 `docs/external-skills/scientific-agent-skills/{hypothesis-generation,scientific-writing}` 两个目录；上游若改了技能目录名/新增依赖，脚本会失败提示人工处理。

## 消费方式（两种并存）

1. **报告流程内嵌（默认）**：根 AGENTS.md §4 路由——「思考与追问」/open-questions 相关 → 读 `hypothesis-generation/SKILL.md`；报告写作证据纪律 → `scientific-writing/SKILL.md`
2. **Skill 工具原生调用（可选，每台机器）**：`--install` 投射到 `~/.agents/skills/` 后，上游 YAML front matter 生效，可被 agent 自动发现
