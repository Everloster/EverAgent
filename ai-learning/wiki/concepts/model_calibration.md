---
id: concept-model_calibration
title: "模型校准与选择性预测（Calibration & Selective Prediction）"
type: concept
domain: [ai-learning]
created: 2026-09-18
updated: 2026-09-18
sources: [Jev与System-One-Models_TypeSafe决策模型范式研究_20260918]
status: active
---

# 模型校准与选择性预测

## 一句话定义

校准（calibration）= 模型的置信度与真实频率一致（说 0.8 的事应约 80% 成真）；选择性预测 = 低置信度时弃权，用 coverage–risk 权衡换可靠性。二者是"让模型知道自己不知道"的度量与行动两面。

## 核心事实

- **RLHF 破坏校准**：GPT-4 技术报告经典图——预训练模型校准良好，post-training 后显著过度自信（arXiv:2303.08774）；verbalized confidence 跨模型系统性偏高（Xiong 2023）。
- **修复路径**：proper scoring rules（Brier/log score）进训练奖励——RLCR（2025）在二元正确性奖励上加 Brier 项修复校准；RLVR 的 0/1 奖励本身伤校准。
- **理论极限**：Kalai & Vempala 2024《Calibrated Language Models Must Hallucinate》——开放生成下校准与零幻觉不可兼得；**封闭分类决策上零"越界"构造可达**（Jev "Zero Hallucinations" 的合理内核与语义漏洞都在此）。
- **度量**：ECE（分桶 |准确率−置信度| 加权平均；Guo 2017）、Brier score；后校准最简法 = temperature scaling。
- **检测幻觉的另一路**：semantic entropy（Farquhar 2024 Nature）——按语义等价类聚簇算熵。

## 与什么相关

- [[rlhf]] — 校准破坏是 RLHF 三宗罪之一；RLCD（TypeSafe）是"scoring rule 替代偏好"的产业版
- [[test_time_compute]] — Jev parallel sampling = 第四维度（取消生成、并行出分布）
- [[bitter_lesson]] — TypeSafe 的 "the bitterest lesson" 挪用：优化对任务 > 数据/算力/算法（与 Sutton 原命题方向相反）

## 相关报告

- [Jev 与 System One Models 研究（2026-09-18）](../../reports/knowledge_reports/Jev与System-One-Models_TypeSafe决策模型范式研究_20260918.md)

## 未解问题 / 追踪

- Jev 的 RLCD 论文（官方"想过写论文"）与 confidence 计算公式、cookbook——公开后核对推测命中率
- 独立第三方对 Jev 的 ECE/reliability diagram 测评
- OpenAI 2025《Why Language Models Hallucinate》精读候选：幻觉的统计学根源专题
