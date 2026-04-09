---
id: concept-in_context_learning
title: "In-Context Learning（上下文学习）"
type: concept
domain: [ai-learning]
created: 2026-04-09
updated: 2026-04-09
sources: [In_Context_Learning_深度解析_20260409, 03_gpt3_2020]
status: active
---

# In-Context Learning（上下文学习，ICL）

## 一句话定义

In-Context Learning（ICL）是大语言模型在不更新任何参数的前提下，仅通过 prompt 中的少量 `<input, output>` 示例（demonstrations）即可完成新任务预测的能力。由 GPT-3 论文（Brown et al., 2020）首次命名。

## 与 Fine-tuning 的本质区别

| 维度 | ICL | Fine-tuning |
|------|-----|-------------|
| 计算成本 | 极低（仅推理） | 高（需 GPU + 梯度） |
| 知识固化程度 | 低（依赖 prompt） | 高（权重直接编码） |
| 部署方式 | 同一模型切换 prompt | 每任务一个专属模型 |

## ICL 三阶段机制（Rubin et al., 2022）

1. **Demonstration Selection**：从候选池选最相关的 k 个示例
2. **Demonstration Ordering**：组织示例顺序（不同排列可差 ±20%）
3. **Label Semantics Recovery**：从格式推断输出标签含义

## ICL 三大理论流派

| 流派 | 核心观点 | 代表工作 |
|------|---------|---------|
| **Bayesian Induction** | LLM 隐式执行贝叶斯推理 | Gould et al., 2023 |
| **Task Recognition** | 从示例中识别任务模式 | Rubin et al., 2022 |
| **Knowledge Activation** | 激活预训练中已存储的知识 | Wei et al., 2023 |

## Position Bias（位置偏差）

关键信息在 context 中间时性能骤降（Lost in the Middle，Liu et al., 2024）。注意力权重分布天然偏向首尾。

## Scaling Laws 与 ICL

ICL 能力随模型规模**涌现**：

| 参数规模 | ICL 能力 |
|---------|---------|
| < 1B | 极弱 |
| ~10B | 开始有统计显著提升 |
| ~175B+ | 显著超越 Fine-tuned SOTA |

## 与 Chain-of-Thought 的关系

CoT 是 ICL 的**增强**：显式推理步骤给 LLM 更多"工作记忆"空间，让 ICL 在多步推理任务上效果更好。GPT-3 + CoT prompting 显著提升复杂任务表现。

## 在本项目的相关报告

- [In-Context Learning 深度解析（2026-04-09）](../../reports/knowledge_reports/In_Context_Learning_深度解析_20260409.md)

## 跨域连接

- ICL 与 Scaling Laws 直接关联（涌现现象）→ concept: scaling_laws
- ICL + CoT 是推理模型（o1/R1）的底层机制之一 → concept: test_time_compute
- ICL 与 RAG 在知识密集型任务上互补 → concept: rag
