---
id: concept-attention_mechanism
title: "Attention Mechanism（注意力机制）"
type: concept
domain: [ai-learning]
created: 2026-04-06
updated: 2026-04-06
sources: [self_attention_深度解析, 01_transformer_2017]
status: active
---

# Attention Mechanism（注意力机制）

## 一句话定义
序列中每个位置通过计算与其他位置的相关性，动态加权聚合信息的机制。

## 核心原理
Self-Attention 中，Query（Q）、Key（K）、Value（V）均来自同一序列。每个位置生成 Q 向量"问"什么，其他位置的 K 向量作为"索引"，通过点积衡量相关性，Softmax 归一化为注意力权重，最后加权求和 V 向量得到输出。

核心公式（Scaled Dot-Product Attention）：
```
Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
```

除以 sqrt(d_k) 的原因：当 d_k 较大时，点积方差为 d_k，不缩放则 Softmax 进入饱和区导致梯度消失。来源：self_attention_深度解析 §技术细节

## 关键数据点
- Transformer 原始实现：h=8 个注意力头，d_model=512，d_k=64（每头）。来源：01_transformer_2017 技术方法
- 注意力矩阵大小 [n, n]：序列长度 4K tokens 时需约 16M 个值，内存瓶颈显著。来源：self_attention_深度解析 §工程实践
- WMT 2014 英德翻译消融：去掉多头注意力后性能下降 0.9 BLEU。来源：01_transformer_2017 实验结果

## 三种注意力类型对比

| 类型 | Q 来源 | K/V 来源 | 用途 |
|------|--------|---------|------|
| Self-Attention | 本序列 | 本序列 | 编码序列内部关系 |
| Cross-Attention | 解码器序列 | 编码器输出 | Decoder 关注 Encoder 信息 |
| Bahdanau Attention | 解码器隐状态 | 编码器隐状态 | 早期 Seq2Seq 注意力前驱 |

来源：self_attention_深度解析 §概念定义

## 多头注意力（Multi-Head Attention）
并行运行 h 个独立注意力头，每头关注不同的语义子空间，最后拼接输出并做线性变换。公式：
```
MultiHead(Q,K,V) = Concat(head_1,...,head_h) * W^O
其中 head_i = Attention(Q*W_i^Q, K*W_i^K, V*W_i^V)
```
来源：01_transformer_2017 技术方法

## 演化脉络
Bahdanau Attention（2014，Encoder-Decoder 跨序列）→ Self-Attention（2017，序列内部，Transformer）→ Multi-Head Attention（2017，多子空间并行）→ FlashAttention（2022，IO-aware 实现，规避 O(n²) 内存壁垒）→ GQA / MQA（2019/2023，减少 KV 头数降低推理成本）

## 在本项目的相关报告
- [Self-Attention 深度解析](../../reports/knowledge_reports/self_attention_深度解析.md)
- [Transformer 2017 论文精读](../../reports/paper_analyses/01_transformer_2017.md)
- [KV Cache 深度解析](../../reports/knowledge_reports/KV_Cache_深度解析_20260330.md)

## 跨域连接
- KV Cache 直接依赖于注意力的 K/V 结构（见 concept: kv_cache）
- MoE 架构中 Attention 层保持 Dense，只有 FFN 层被替换（见 concept: moe_architecture）
- LoRA 主要注入注意力层的 Q/V 投影矩阵（见 concept: lora_peft）
