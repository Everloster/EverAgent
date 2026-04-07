---
id: concept-kv_cache
title: "KV Cache（键值缓存）"
type: concept
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [KV_Cache_深度解析_20260330]
status: active
---

# KV Cache（Key-Value Cache）

## 一句话定义
在 Transformer 自回归推理时缓存每层注意力的 K/V 矩阵，避免对历史 token 重复计算，将每步推理从 O(t²) 降至 O(t)。

## 为什么可以缓存
设当前已生成 t 个 token，生成第 t+1 个时需要计算 `Attention(Q, K, V)`：
- **Q**：仅由第 t+1 个 token 生成，每步都是新的；
- **K, V**：由前 t 个 token 生成，**与上一步相比只新增了第 t 个 token 的部分**。

因此历史 K/V 不需要重新算，只需追加最新 token 的 K/V。来源：KV_Cache_深度解析 §核心原理

## 增量计算示意
```
# 缓存中已有 K_{1:t-1}, V_{1:t-1}
q_t = x_t · W_Q              # shape: (1, d_k)
k_t = x_t · W_K              # 只算新 token
v_t = x_t · W_V

K_t = concat(K_cache, k_t)   # 追加
V_t = concat(V_cache, v_t)
out = softmax(Q_t · K_t^T / √d_k) · V_t
```
计算量：每步 O(1)，总量 O(T)；相比无缓存的 O(T²) 节省一个量级。来源：KV_Cache_深度解析 §数学描述

## 显存占用
单层 KV Cache 显存：
```
KV_mem = 2 × seq_len × num_heads × head_dim × bytes_per_param
```
**LLaMA-2 7B 实例**（32 层，32 头，head_dim=128，seq_len=4096，FP16）：
```
2 × 4096 × 32 × 128 × 2 bytes × 32 layers ≈ 2 GB
```
长上下文（128K token）下 KV Cache 可达数十 GB，是推理显存的主要来源。来源：KV_Cache_深度解析 §显存占用计算

## 减少 KV Cache 的四类技术
| 技术 | 提出 | 机制 | 主流模型 |
|------|------|------|---------|
| **MQA**（Multi-Query Attention） | Shazeer 2019 | 所有 Q 头共享一组 K/V，KV 显存 ÷ h | Gemma 7B（16:1） |
| **GQA**（Grouped-Query Attention） | Ainslie 2023 | Q 头分组共享 K/V，MQA 与 MHA 之间的折中 | LLaMA-2 70B（8:1）、Mistral 7B（4:1） |
| **Prefix / Prompt Caching** | — | 固定 System Prompt 的 KV 提前算并复用，节省 80%+ TTFT | OpenAI / Anthropic |
| **PagedAttention** | vLLM, Kwon 2023 (SOSP) | 类 OS 虚拟内存的分页管理，解决显存碎片 | vLLM，吞吐 5-10× |

来源：KV_Cache_深度解析 §常见变体 / §主流模型的 GQA 配置

## 推理框架对比
| 系统 | KV 策略 | 特色 |
|------|--------|------|
| vLLM | PagedAttention | 最高吞吐量 |
| TensorRT-LLM | 静态 KV 分配 | 最低延迟 |
| TGI（HuggingFace） | 连续批处理 + KV Cache | 生产级 |
| llama.cpp / Ollama | 滚动窗口 | 边缘设备 |

来源：KV_Cache_深度解析 §主流推理框架

## 前沿压缩技术
- **H2O（Heavy-Hitter Oracle）**：识别并保留最重要的 KV 对
- **SnapKV (2024)**：通过 Attention 权重识别关键 KV，压缩率 1000× 仅损失 0.5%
- **PyramidKV**：不同层使用不同压缩率（浅层保留更多）
- **Streaming LLM (MIT 2023)**：保留 Attention Sink + 滑动窗口，支持无限流式
- **Radix Attention**（vLLM）/ **SGLang RadixCache**：跨请求共享前缀 KV

来源：KV_Cache_深度解析 §前沿进展

## 在本项目的相关报告
- [KV Cache 深度解析](../../reports/knowledge_reports/KV_Cache_深度解析_20260330.md)

## 跨域连接
- KV Cache 直接依赖 Attention 的 K/V 结构 → concept: attention_mechanism
- 与 FlashAttention 正交（FA 优化 prefill 阶段，KV 优化 decode 阶段），可同时使用 → concept: transformer_architecture

## 开放问题
- 1M+ token 超长上下文下 KV Cache 的有效管理仍是挑战
- 如何无损将 KV Cache 压缩到 2-4 bit？
- 跨层 KV 共享是否可行（减少层数但保留表达力）？
