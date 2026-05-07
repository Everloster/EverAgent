---
title: "Long Context Simulation"
type: concept
domain: ai-practice
updated_on: 2026-05-07
source: experiments/exp_006_long_context_1m_simulation.md
---

# Long Context Simulation

Long Context Simulation 是用缩小的上下文窗口模拟 1M context 系统的工程机制。

它不追求训练真实百万 token 大模型，而是把真实系统拆成三个可观察接口：

```text
pretraining: max_seq_len / position ids / attention mask
post-training: needle-in-a-haystack / evidence QA
inference: prompt packing / RAG / prefill / KV cache
```

## 实验入口

```bash
python3 ai-practice/src/long_context_simulation.py \
  --context-len 4096 \
  --needle-position 0.73 \
  --chunk-size 256 \
  --top-k 3
```

## 关键观察

- `seq_len` 线性增长时，标准全量 attention 近似平方增长。
- needle 数据用于模拟后训练阶段的证据定位能力。
- full-context 证据全在场，但成本高、噪声多。
- RAG 通过检索减少 prompt tokens，但有召回风险。
- KV cache 显存随 `seq_len * layers * kv_heads * head_dim` 增长。

## 与已有实验关系

- 继承 `transformer_from_scratch` 中的 context window、causal mask、position encoding 直觉。
- 与 `mixture_of_experts` 同属阶段 1 之后的架构/系统扩展实验。
- 为后续 vLLM 推理速度基准、RAG 实验、长上下文微调实验提供前置概念。
