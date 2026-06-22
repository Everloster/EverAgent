# 归档任务索引 — 2026-06-21

> 13 个 `tasks/*.yaml` 因与 `.project-task-state` 状态漂移，被 2026-06-21 调度器误判为「open」并派发 4 个 Subagent。
> 4 个 Subagent 全部回 `help_needed`（AGENTS.md §2.2 / §6.1 防幻觉铁律），确认任务实为 `done`。
> 调度方决策：**封存老任务，整库刷新**。本目录下的 13 个 YAML 标记为 `status: archived`，从下次调度候选中排除。
>
> 关联 wiki 概念（按需查阅）：[[everagent-task-state-sync]]

---

## 归档清单（13 个任务）

| ID | Project | Priority | Type | claimed_by | done_at | 报告路径 | 行数 |
|---|---|---|---|---|---|---|---|
| T030 | ai-learning | P2 | knowledge_report | NeuronAgent | 2026-04-23 | `ai-learning/reports/knowledge_reports/Agent_心跳检测与实时Dashboard设计.md` | 425 |
| T031 | biology-learning | **P1** | paper_analysis | BioAgent | 2026-04-22 | `biology-learning/reports/paper_analyses/P02_stutz_evening_exercise_sleep_2025.md` | 311 |
| T032 | biology-learning | P2 | concept_report | BioAgent | 2026-04-22 | `biology-learning/reports/concept_reports/昼夜节律与运动表现_深度研究报告.md` | 358 |
| T033 | biology-learning | P2 | paper_analysis | BioAgent | 2026-04-22 | `biology-learning/reports/paper_analyses/P03_dattilo_sleep_muscle_2011.md` | 292 |
| T034 | cs-learning | **P1** | paper_analysis | ByteAgent | 2026-04-22 | `cs-learning/reports/paper_analyses/33_hoare_axiomatic_1969.md` | — |
| T035 | cs-learning | P2 | knowledge_report | ByteAgent | 2026-04-22 | `cs-learning/reports/knowledge_reports/编程语言范式演化_从Lisp到Go的并发模型变迁.md` | — |
| T036 | cs-learning | P2 | paper_analysis | ByteAgent | 2026-04-22 | `cs-learning/reports/paper_analyses/34_lamport_bakery_1974.md` | — |
| T037 | biology-learning | **P1** | paper_analysis | BioAgent | 2026-04-24 | `biology-learning/reports/paper_analyses/P04_roenneberg_circadian_health_2022.md` | 309 |
| T038 | biology-learning | P2 | paper_analysis | BioAgent | 2026-04-24 | `biology-learning/reports/paper_analyses/P17_hayes_circadian_exercise_2013.md` | 299 |
| T039 | biology-learning | P2 | concept_report | BioAgent | 2026-04-24 | `biology-learning/reports/concept_reports/运动时间生物学_个体化训练时间窗.md` | 348 |
| T040 | philosophy-learning | **P1** | text_analysis | SocratesAgent | 2026-04-24 | `philosophy-learning/reports/text_analyses/03_gettier_1963.md` | 233 |
| T041 | philosophy-learning | P2 | text_analysis | SocratesAgent | 2026-04-24 | `philosophy-learning/reports/text_analyses/05_russell_on_denoting_1905.md` | 253 |
| T042 | philosophy-learning | P2 | text_analysis | SocratesAgent | 2026-04-24 | `philosophy-learning/reports/text_analyses/08_singer_famine_1972.md` | 276 |

**总计**：13 个任务（4 个 P1 + 9 个 P2）跨 4 个子项目，4 月 22–24 日期间全部完成并 commit 推送至 main。

---

## 修复记录

- `tasks/T030.yaml` ~ `tasks/T042.yaml` → `tasks/archive/2026-06-21-stale-tasks/`（`git mv`）
- 每个 YAML 新增 `metadata.status: archived` / `metadata.archived_at: 2026-06-21` / `metadata.archive_reason: <人类可读>`
- `cs-learning/papers/PAPERS_INDEX.md` 中 #17（Hoare 1969）、#26（Bakery 1974）补「阅读状态：✅ 已完成」与 CONTEXT.md 对齐

---

## 后续防御

- 调度方下次派发任务时，**先读 `.project-task-state` 的 open 任务**，不要只看 `tasks/*.yaml` 目录。
- 推荐运行 `python3 scripts/everagent.py audit` 巡检 registry/task/lock 漂移。
- 任何 `status: archived` 任务在 `execution_validator.py --mode=input` 阶段应直接 [FAIL] skip，避免再次误派。
