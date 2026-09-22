# 津晶 & Orca（Stably AI）

> 人物/产品实体 · 首次建档：2026-09-22（课代表立正对话 319，2026-09-17 期）

## 身份

- **津晶**：Orca 联创（母公司 Stably AI）；ex-Google；YC 出身（婚礼直播平台→AI 测试 Stably→Orca）；联创 ex-Uber。本人同时推进 400+ feature（200+ 已 SOP 自动化）
- **Orca**（github.com/stablyai/orca）：ADE（Agent IDE）——多 agent 编排管理面，TUI 优先；录制时 GitHub 4.9 万星；4 人团队、每天一个 stable 版、每版上百 PR

## 核心框架（本期）

- **ADE vs Harness**：harness=agent loop（Codex/Claude Code）；ADE 在其上做人与 agent 的管理 workflow，不绑模型不做 loop
- **400 任务三层法**：索引聚合 → agent 管 agent（orchestration script，"Claude Code 驾驭 Codex"，人只看第一步和最后一步）→ SOP 化 + 定时 manager thread
- 企业侧炸点："Anthropic 的账单已成企业第一大开销、超过工程师工资单"

## 相关期数

- 课代表立正对话 319（2026-09-17）→ [[2026-09-17_rss-kedaibiao-lizheng_jinjing|报告]]

## 与其他实体的关联

- 与 EverAgent 自身的 herdr/eacli 舰队互为镜像（对照见报告第五节）；handoff/状态聚合等机制为本库未有的借鉴点
