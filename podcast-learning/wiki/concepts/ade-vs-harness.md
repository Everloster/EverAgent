# ADE（Agent IDE）vs Harness

> 概念实体 · 首次引入：2026-09-17（课代表立正对话 319，津晶/Orca）

## 定义

津晶提出的分层：**Harness** = 把 input→output 的 agent 做成 loop（routine + tool use），如 Codex/Claude Code/Devin；**ADE（Agent IDE）** 在 harness 之上——不绑模型、不做 loop，专注**人与 agent 的管理 workflow**（状态聚合、并行编排、handoff、SOP 化）。

## 要点

- ADE 商业逻辑：TUI 优先（CLI 用户远多于 desktop）；不 wrap 厂商 harness 内部（避免每次上游更新重写）
- 关键机制：跨 worktree/harness 的 agent status 聚合（working/blocked/needs review）；带现场的 handoff（一家用量到顶转另一家）；PTY snapshot（升级不丢 session）
- 人参与原则："人只看第一步和最后一步"；"要人参与就给容易 review 的东西"（HTML 可视化报告）

## 与其他概念的关联

- 与 EverAgent 自身 herdr/eacli 舰队对照（报告第五节）：她的 handoff ≈ eacli 多 provider 编排，但 eacli 缺"带工作现场的接力"
- 来源：[[2026-09-17_rss-kedaibiao-lizheng_jinjing]]
