---
title: "Long Context Systems"
type: concept
domain: ai-learning
updated_on: 2026-10-27
source: reports/knowledge_reports/Long_Context_1M_三阶段深度解析_20260507.md
---

# Long Context Systems

Long Context Systems 指支持大规模上下文窗口的模型与推理系统组合。它不是单独的模型参数，而是由预训练、后训练和线上推理共同形成的能力。

## 核心定义

```text
long context = 大上下文窗口 + 长序列训练 + 长上下文对齐 + 可承受的推理系统
```

1M context 通常表示一次请求中可处理接近一百万 tokens 的上下文预算，但输入、输出、系统提示和工具结果共享该预算。

## 三阶段含义

| 阶段 | 含义 | 关键问题 |
|------|------|----------|
| 预训练 | 架构和训练过程支持长序列学习 | 看得进 |
| 后训练 | 模型学会长文档检索、综合和抗干扰 | 找得到、用得对 |
| 推理 | 服务系统能承担 prompt packing、prefill、KV cache | 跑得起 |

## 关键技术

- RoPE / ALiBi / 位置插值等位置编码扩展
- FlashAttention / sparse attention / sliding window attention
- long-context SFT 与 needle-in-a-haystack 数据
- citation grounding 与冲突证据判断
- KV cache、GQA/MQA、PagedAttention、prefix caching
- RAG、chunk ranking、hierarchical summary

## 与相关概念的关系

- `attention_mechanism`：长上下文放大 attention 的计算与记忆压力。
- `kv_cache`：推理阶段长上下文的主要显存账本。
- `rag`：与 long context 互补，负责把上下文变干净。
- `in_context_learning`：长上下文扩大 ICL 可见材料，但不保证有效利用。
- `llms_plus`：长上下文是增强型 LLM 系统的重要组成。

## 一句话

1M context 的价值不在于“输入框很大”，而在于模型和系统能在百万 token 级资料中稳定完成证据定位、综合推理和可控生成。

## 多轮 Agent 的历史管理

文档检索、综合推理与多轮行动需要分别评估。Gemini 2.5 报告中“显著超过 100k 后重复历史动作”是特定 Pokémon Agent 设置的经验观察，不能作为通用窗口阈值。

Fork-and-Flush 保留累计工作区、清空对话后分支探索；Scaling Discovery Requires Forgetting 进一步清掉候选历史，只保留最好成果及其分数。两者的证据主要来自有评分器的研究和优化任务，迁移到阅读报告时仍要保护原始来源、反例与当前任务状态。

来源：[上下文工程的失效与修复](../../reports/knowledge_reports/Context_Engineering_失败修复与战略性遗忘_深度解析_20261027.md) §5–8。本文建议的 Personal Context 重建尚未开展行为对比实验。
