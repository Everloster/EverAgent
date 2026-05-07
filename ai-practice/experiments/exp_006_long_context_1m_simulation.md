---
title: "Long Context 1M 缩尺模拟实验"
type: tutorial_note
stage: 1.6
script: src/long_context_simulation.py
prerequisites: ["transformer_from_scratch", "attention", "tokenization"]
updated_on: 2026-05-07
---

# exp_006：Long Context 1M 缩尺模拟实验

## 1. 学习目标

完成本实验后，你应该能够：

- [ ] 解释 `max_seq_len` 为什么不是普通配置项，而会改变位置编码、mask、attention 成本和训练样本组织。
- [ ] 区分 1M context 在预训练、后训练、线上推理三个阶段的不同代码入口。
- [ ] 用 needle-in-a-haystack 数据模拟长上下文后训练为什么需要证据定位任务。
- [ ] 比较 full-context 与 RAG prompt packing 在 tokens inspected、latency 和召回上的差异。
- [ ] 用 KV cache 公式估算长上下文推理的显存压力。

本实验不是训练真实 1M-token 大模型，而是用小窗口复刻真实工程路径：

```text
真实生产：1M tokens
本地教学：4K / 8K / 32K tokens
```

这样可以在 CPU 上观察相同趋势，而不需要昂贵 GPU 集群。

---

## 2. 核心概念（Why）

### 2.1 1M context 不是一个单点功能

“模型支持 1M 上下文”容易被误解成：

```text
把输入框从 32K 改成 1M。
```

真实情况更像三段管线：

```text
预训练：模型结构和训练过程能承受长序列
后训练：模型学会在长序列里找证据、抗干扰、回答问题
推理：线上系统能承担 prefill、KV cache、token budget 和延迟
```

本实验把这三段分别映射为可运行代码。

### 2.2 预训练阶段：max_seq_len 改变训练表面

在 `src/model.py` 的教学 Transformer 里，已有一个小窗口：

```python
context_length = 16
```

这个值影响：

- batch 取样长度
- 下三角 causal mask 的尺寸
- 位置编码表的长度
- 每次 attention 需要处理的 token 数

如果把它扩大到 4096、32768 或 1M，相关结构都会一起变大。

本实验不真的构造 1M x 1M mask，而是计算其规模：

```python
causal_mask_cells = seq_len * seq_len
attention_cells = seq_len * seq_len * heads
```

这能直观看到为什么标准全量 attention 难以硬上百万 token。

### 2.3 后训练阶段：needle 数据让模型学会“找”

预训练让模型“看过长文本”，但不会天然让它按指令找证据。

后训练常构造类似任务：

```text
Context:
  filler filler filler ...
  SECRET_KEY=blue-river-7-4096
  filler filler filler ...

Question:
  What is the SECRET_KEY?

Answer:
  blue-river-7-4096
```

这就是 needle-in-a-haystack 的缩小版。

它训练或评估的是：

- 模型是否能定位关键片段
- 关键片段在开头/中间/结尾时是否都能找回
- 大量无关上下文是否会干扰回答

### 2.4 推理阶段：full-context 与 RAG 的取舍

线上推理有两种常见方式。

第一种是 full-context：

```text
把所有材料都塞进 prompt。
```

优点是证据都在场，缺点是贵、慢、噪声大。

第二种是 retrieval packing：

```text
先切块检索，再把 top-k 片段塞进 prompt。
```

优点是便宜、快、干净，缺点是检索漏召会直接丢证据。

本实验用同一个 needle 样本比较两者需要检查多少 token。

---

## 3. 实现解析（关键代码 + 解释）

核心代码位于：

```text
src/long_context_simulation.py
```

### 3.1 预训练窗口成本模拟

关键函数：

```python
def simulate_pretraining_window(seq_lens, heads, shape):
    rows = []
    baseline = min(seq_lens)
    for seq_len in seq_lens:
        attention = full_attention_cells(seq_len, heads)
        rows.append({
            "seq_len": str(seq_len),
            "position_ids": f"0..{seq_len - 1}",
            "causal_mask_cells": human_number(causal_mask_cells(seq_len)),
            "attention_cells": human_number(attention),
            "vs_baseline_attention": f"{attention / full_attention_cells(baseline, heads):.1f}x",
            "kv_cache_mb": f"{mb(kv_cache_bytes(seq_len, shape)):.1f}",
            "rope_phase_drift": f"{rope_phase_drift(baseline, seq_len):.3f}",
        })
    return rows
```

它对应预训练里的四个工程入口：

- `seq_len`：训练样本长度
- `position_ids`：位置编码覆盖范围
- `causal_mask_cells`：下三角 mask 规模
- `attention_cells`：全量注意力计算表面

`rope_phase_drift` 是一个教学指标，用来展示 RoPE 位置外推时，长位置和短位置的旋转相位几何会发生变化。

### 3.2 Needle 样本生成

关键函数：

```python
def build_needle_sample(context_len, needle_position, seed=7):
    random.seed(seed)
    vocab = make_haystack_vocab()
    tokens = [random.choice(vocab) for _ in range(context_len)]
    answer = f"blue-river-{seed}-{context_len}"
    needle = f"SECRET_KEY={answer}"
    needle_index = max(0, min(context_len - 1, int(context_len * needle_position)))
    tokens[needle_index] = needle
    return NeedleSample(tokens, "What is the SECRET_KEY?", answer, needle_index)
```

这里的 `needle_position=0.73` 表示把关键证据放在 73% 的上下文位置。

真实长上下文评估会扫描多个位置，因为模型常出现 lost-in-the-middle：开头和结尾更容易被用到，中间信息更容易被忽略。

### 3.3 Full-context 扫描

```python
def full_context_answer(sample):
    inspected = 0
    for token in sample.tokens:
        inspected += 1
        if token.startswith("SECRET_KEY="):
            return token.split("=", 1)[1], inspected
    return None, inspected
```

这模拟“把全部上下文交给模型”的理想证据可见性。

如果 needle 在第 2990 个 token，full-context 至少要读到第 2991 个 token 才能找到它。

### 3.4 RAG packing

```python
def rag_answer(sample, chunk_size, top_k):
    token_chunks = chunks(sample.tokens, chunk_size)
    selected = retrieve_chunks(sample.question, token_chunks, top_k)
    inspected = 0
    selected_ids = []
    for chunk_id, chunk, _score in selected:
        selected_ids.append(chunk_id)
        for token in chunk:
            inspected += 1
            if token.startswith("SECRET_KEY="):
                return token.split("=", 1)[1], inspected, selected_ids
    return None, inspected, selected_ids
```

这模拟“先检索 chunk，再把 top-k chunk 放进 prompt”。

在本实验中，检索器会给包含 `SECRET_KEY` 的 chunk 更高分。真实系统里，这一步通常由 BM25、向量检索、reranker 或混合检索完成。

### 3.5 KV cache 成本模型

```python
KV bytes = 2 * seq_len * layers * kv_heads * head_dim * bytes_per_value
```

代码对应：

```python
def kv_cache_bytes(seq_len, shape):
    return 2 * seq_len * shape.layers * shape.kv_heads * shape.head_dim * shape.bytes_per_value
```

这就是推理阶段最重要的显存账本之一。

---

## 4. 实验结果

运行命令：

```bash
python3 ai-practice/src/long_context_simulation.py \
  --context-len 4096 \
  --needle-position 0.73 \
  --chunk-size 256 \
  --top-k 3 \
  --new-tokens 128
```

实际输出摘要如下。

### 4.1 预训练窗口成本

| seq_len | causal_mask_cells | attention_cells | vs_baseline_attention | kv_cache_mb | rope_phase_drift |
|---------|-------------------|-----------------|-----------------------|-------------|------------------|
| 128 | 16.38K | 131.07K | 1.0x | 12.0 | 0.000 |
| 512 | 262.14K | 2.10M | 16.0x | 48.0 | 1.248 |
| 2048 | 4.19M | 33.55M | 256.0x | 192.0 | 1.454 |
| 4096 | 16.78M | 134.22M | 1024.0x | 384.0 | 1.693 |

结论：

```text
seq_len 从 128 增加到 4096，长度增加 32x，但全量 attention cells 增加 1024x。
```

这就是长上下文训练不能只靠“把窗口调大”的原因。

### 4.2 Needle 后训练样本

| context_len | needle_index | needle_position | answer |
|-------------|--------------|-----------------|--------|
| 4096 | 2990 | 73.00% | blue-river-7-4096 |

这个样本代表后训练中的长上下文 QA 数据。

它不考模型常识，而考“能否根据上下文证据回答”。

### 4.3 Full-context vs RAG

| mode | answer_ok | tokens_inspected | selected_chunks | latency_ms |
|------|-----------|------------------|-----------------|------------|
| full_context | True | 2991 | all | 0.230 |
| rag_top_k | True | 175 | 11 | 0.208 |

在这个样本里，RAG 只检查了 175 个 token 就找到了答案，而 full-context 需要读到第 2991 个 token。

注意：这是教学检索器，真实系统的关键风险是 top-k 没有召回 needle。

### 4.4 推理成本模型

| prompt_tokens | new_tokens | prefill_attention_cells | decode_attention_cells | kv_cache_mb |
|---------------|------------|-------------------------|------------------------|-------------|
| 4096 | 128 | 134.22M | 4.19M | 396.0 |

结论：

```text
长上下文主要增加 prefill 和 KV cache；decode 每步仍要访问已有上下文。
```

---

## 5. 思考题与延伸实验

1. 把 `--needle-position` 改成 `0.1 / 0.5 / 0.9`，full-context 的 `tokens_inspected` 如何变化？

2. 把 `--chunk-size` 从 `256` 改成 `64`，RAG 会更快还是更慢？为什么？

3. 把 `--top-k` 改成 `1`，如果检索器不完美，会出现什么风险？

4. 加上 `--include-1m` 观察 1,048,576 tokens 的成本估算。为什么脚本只估算而不真的构造 attention matrix？

5. 把 `--kv-heads` 从 `8` 改成 `1`，模拟 MQA；KV cache 会下降多少？

6. 如果要把这个实验升级成小模型训练，应增加哪些模块？

   - tokenizer
   - TinyTransformer
   - RoPE/ALiBi 开关
   - long-sequence dataloader
   - SFT loss masking
   - retrieval evaluation

7. 为什么 1M context 与 RAG 不是互斥关系？

---

## 6. 参考资料

- ai-learning: `Long_Context_1M_三阶段深度解析_20260507.md`
- ai-learning: `KV_Cache_深度解析_20260330.md`
- ai-learning: `RAG_深度解析_20260409.md`
- ai-learning: `18_flashattention_2022`
- ai-practice: `src/model.py`
- ai-practice: `experiments/exp_001_transformer_from_scratch.md`

本实验的定位是机制级模拟：用小输入展示真实 1M context 系统在三个阶段的代码入口和成本形状。
