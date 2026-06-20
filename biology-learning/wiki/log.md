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

## [2026-05-05] ingest | 女童月经初潮提前与中枢性性早熟

**新建报告**：`reports/concept_reports/女童初潮提前与中枢性性早熟_深度研究报告.md`

**新增 Wiki 页面**：`wiki/concepts/early_menarche.md`、`wiki/concepts/central_precocious_puberty.md`、`wiki/entities/chinese_pediatric_endocrinology_group.md`、`wiki/entities/eugster_erica.md`

**更新 Wiki 页面**：`wiki/index.md`

**核心事实**：三年级女童初潮通常提示月经初潮提前，应由儿科内分泌评估是否存在中枢性性早熟；报告整合中国 CPP 专家共识、国内儿童早发育队列和 JCEM/Lancet/JAMA 等国际证据，形成家庭就医清单和观察/治疗分层框架。

## [2026-05-05] ingest | 2022 中国 CPP 专家共识全文与前沿论文补充分析

**更新报告**：`reports/concept_reports/女童初潮提前与中枢性性早熟_深度研究报告.md`

**更新 Wiki 页面**：`wiki/concepts/central_precocious_puberty.md`、`wiki/concepts/early_menarche.md`

**核心事实**：根据用户提供的《中枢性性早熟诊断与治疗专家共识（2022）》PDF，补充女童 7.5 岁前乳房发育或 10.0 岁前初潮的国内界值、GnRH 激发试验参数、盆腔超声和 MRI 分层、GnRHa 指征/监测/安全性，并加入 JAMA Pediatrics 2020、Endocrine Reviews 2022、JCEM 2020/2022/2023、韩国 2022 指南等逐篇前沿论文分析。

## [2026-06-21] ingest | 蓝光与褪黑素的光生物学深度研究

**操作**：完成 concept_report 蓝光与褪黑素的光生物学_20260621.md（T067），系统拆解 ipRGC × 黑视蛋白 × SCN-松果体通路，整合 Czeisler 1980 / Brainard 2001 / Zeitzer 2000 ED50 / Berson 2002 / Lucas 2014 五项核心研究 + CIE S 026:2018 melanopic EDI 标准 + AASM/AAO/Endocrine Society 三大临床立场。

**新建报告**：`reports/concept_reports/蓝光与褪黑素的光生物学_20260621.md`（454 行，2 个 mermaid 通路图，4 个决策表）

**更新 Wiki 页面**：
- 新建 `wiki/concepts/blue_light_melatonin.md`（5 层模型 + 跨域连接）
- 更新 `wiki/index.md`（追加新概念条目）
- 更新 `CONTEXT.md`（追加新报告条目 + 边界区更新）

**决策框架亮点**：7 设备 × 7 时间窗口配置矩阵 + 紧急场景决策流程；强调 iPhone Night Shift 单独开启不够，必须降亮度 + 增加距离 + 多管齐下；指出 AAO 与 AASM 立场不矛盾（前者关心视网膜光毒性，后者关心节律干扰，两者剂量阈值相差 3–4 个数量级）。
