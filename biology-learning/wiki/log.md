# biology-learning · Wiki 操作日志

> append-only。每次 ingest / query-archive / lint 追加一条记录。
> 格式：`## [YYYY-MM-DD] {操作类型} | {标题}`
> 快速查看最近 5 条：`grep "^## \[" log.md | tail -5`

---

<!-- 日志从此处开始追加 -->

## [2026-04-17] 首次种子 | biology-learning wiki 初始化

**操作**：基于已完成的 5 篇 paper_analyses + 1 篇 concept_report 反向抽取 entities 与 concepts，完成 wiki 骨架填充。

**新增 Entities（5 个）**：roenneberg_till, walker_matthew, van_cauter_eve, born_jan, rutters_femke

**新增 Concepts（7 个）**：social_jetlag, chronotype, slow_wave_sleep, gh_sleep_coupling, circadian_rhythm, metabolic_syndrome, sleep_architecture

**触发来源**：全局优化任务 A2（项目全局基础建设 · wiki 层补齐）。

## [2026-04-25] ingest | Thomas et al. (2020) 定时运动与时型相位移动

**新建报告**：`reports/paper_analyses/P05_thomas_exercise_phase_chronotype_2020.md`

**新增 Wiki 页面**：`wiki/concepts/exercise_phase_shift.md`、`wiki/entities/thomas_matthew_j.md`

**更新 Wiki 页面**：`wiki/index.md`、`wiki/concepts/chronotype.md`、`wiki/concepts/circadian_rhythm.md`

**核心事实**：n=52 健康久坐年轻成年人；5 天、每天 30 分钟、70% VO2peak 跑台运动；早晨运动整体 DLMO 相位提前 0.62 ± 0.18 h；晚间运动效应受 baseline DLMO / chronotype 修饰。

## [2026-04-25] ingest | Shen et al. (2023) 运动对人类昼夜节律的影响

**新建报告**：`reports/paper_analyses/P07_youngstedt_exercise_circadian_2023.md`

**新增 Wiki 页面**：`wiki/concepts/non_photic_zeitgeber.md`、`wiki/entities/shen_bingyi.md`

**更新 Wiki 页面**：`wiki/index.md`

**核心事实**：Frontiers 官方页显示本文作者为 Shen et al.；综述范围覆盖正常光暗、恒定条件、扰乱光暗条件下的运动相位研究，并把 DLMO、aMT6s、体温、睡眠-觉醒行为和骨骼肌钟基因作为主要证据线索。运动是重要非光照授时因子，但效应通常弱于光照，应用建议需按睡眠、代谢、心血管等目标结局分级。
