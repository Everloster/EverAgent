# Wiki Log（追加式操作记录）

## [2026-04-20] init | scaffold
- 初始化项目骨架

## [2026-04-20] ingest | exp_001 — 从零实现 Transformer 语言模型
- 新建 wiki/concepts/transformer_from_scratch.md
- 更新 wiki/index.md

## [2026-04-20] ingest | exp_002 — HuggingFace 数据集与模型 API 实践
- 无新增 wiki 页面（exp_002 概念已在 exp_001/exp_003/exp_004 中覆盖）

## [2026-04-20] ingest | exp_003 — Transformers 库加载预训练模型
- 无新增 wiki 页面（Transformers 库概念属于 HuggingFace 生态，实体在 entities/ 中处理）

## [2026-04-20] ingest | exp_004 — Qwen2.5-3B GRPO 强化学习微调
- 新建 wiki/concepts/grpo.md
- 新建 wiki/concepts/unsloth_framework.md
- 新建 wiki/concepts/sft_vs_rlhf.md
- 新建 wiki/entities/qwen_series.md
- 更新 wiki/index.md

## [2026-04-21] ingest | exp_005 — MoE Transformer 稀疏激活实验
- 新建 wiki/concepts/mixture_of_experts.md
- 更新 wiki/index.md
- 同步 README.md 与 CONTEXT.md 的 exp_005 导航和边界说明

## [2026-05-07] ingest | exp_006 — Long Context 1M 缩尺模拟实验
- 新建 src/long_context_simulation.py
- 新建 experiments/exp_006_long_context_1m_simulation.md
- 新建 wiki/concepts/long_context_simulation.md
- 更新 CONTEXT.md、README.md、LEARNING_PATH.md、wiki/index.md

## [2026-05-13] ingest | exp_007 — SkillOS 技能库策展小型实验复现
- 新建 src/skillos_curator_simulation.py
- 新建 experiments/exp_007_skillos_curator_simulation.md
- 新建 wiki/concepts/skillos_curator_simulation.md
- 更新 CONTEXT.md、wiki/index.md
- 实测 grouped 与 shuffled 两种任务流，对比 no_memory、raw_memory、skillos_heuristic 三种策略
