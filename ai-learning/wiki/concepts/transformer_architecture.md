---
id: concept-transformer_architecture
title: "Transformer 架构"
type: concept
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [01_transformer_2017, 03_gpt3_2020, 02_bert_2018, 11_vit_2020]
status: active
---

# Transformer 架构

## 一句话定义
完全基于自注意力（Self-Attention）的编码器-解码器序列建模架构，取代 RNN/LSTM 成为现代 LLM 的底层基础。

## 核心原理
原作者 Vaswani 等人的关键假设：**注意力机制本身就足够了**——不需要循环结构，只用注意力就能建模序列任意位置之间的依赖，且支持高度并行化。来源：01_transformer_2017 §背景与动机

整体结构：
```
Input → Embedding + Positional Encoding
     → N × [Multi-Head Self-Attention → Add&Norm → FFN → Add&Norm]   (Encoder)
     → N × [Masked Self-Attention → Cross-Attention → FFN]            (Decoder)
     → Linear + Softmax
```
来源：01_transformer_2017 §技术方法

## 五个核心组件
| 组件 | 作用 | 关键公式/参数 |
|------|------|--------------|
| Scaled Dot-Product Attention | 序列内部信息聚合 | `softmax(QKᵀ/√d_k)·V` |
| Multi-Head Attention | 多子空间并行注意力 | h=8 头（原论文） |
| Positional Encoding | 注入位置信息（注意力本身无序） | sin/cos 函数 |
| FFN（Feed-Forward） | 每位置独立两层全连接，引入非线性 | `max(0, xW₁+b₁)W₂+b₂` |
| Add & Norm（残差 + LayerNorm） | 训练稳定、缓解梯度消失 | Pre-LN / Post-LN 两种变体 |

来源：01_transformer_2017 §技术方法

## 关键数据点
- **WMT 2014 英德翻译**：28.4 BLEU，超过当时所有模型（之前最好 26.4）。来源：01_transformer_2017 §实验
- **训练效率**：英德任务仅用 8 个 P100 GPU × 12 小时。来源：01_transformer_2017 §实验
- **消融**：去掉多头注意力 → 性能下降 0.9 BLEU；去掉位置编码 → 性能大幅下降。来源：01_transformer_2017 §实验
- **复杂度局限**：注意力计算为 O(n²)，对超长序列（>10K tokens）代价极高。来源：01_transformer_2017 §论文局限

## 三大分支
| 分支 | 代表模型 | 用途 |
|------|---------|------|
| Encoder-Only | BERT (2018) | 双向理解、分类 |
| Decoder-Only | GPT 系列、LLaMA | 自回归生成（现代 LLM 主流） |
| Encoder-Decoder | T5 (2019)、原始 Transformer | 翻译、Seq2Seq 任务 |

来源：01_transformer_2017 §影响 / 03_gpt3_2020 §背景

## 演化脉络
LSTM (1997) → Bahdanau Attention (2014) → **Transformer (2017)** → BERT / GPT-1 (2018) → GPT-2 (2019) → GPT-3 (2020) → ViT (2020，跨域到图像) → ChatGPT (2022) → GPT-4 / Claude / Gemini (2023+)。来源：01_transformer_2017 §历史位置 / 03_gpt3_2020 §时间线

## 在本项目的相关报告
- [Transformer (2017) 论文精读](../../reports/paper_analyses/01_transformer_2017.md)
- [Self-Attention 深度解析](../../reports/knowledge_reports/self_attention_深度解析.md)
- [BERT (2018) 论文精读](../../reports/paper_analyses/02_bert_2018.md)
- [GPT-3 (2020) 论文精读](../../reports/paper_analyses/03_gpt3_2020.md)
- [ViT (2020) 论文精读](../../reports/paper_analyses/11_vit_2020.md)

## 跨域连接
- 注意力机制 → 见 concept: attention_mechanism
- KV Cache 是 Transformer 自回归推理的核心优化 → concept: kv_cache
- LoRA 将低秩矩阵注入 Transformer 注意力层的 Q/V 投影 → concept: lora_peft
- MoE 架构将 Transformer 的 FFN 层替换为稀疏专家层，Attention 保持不变 → concept: moe_architecture

## 开放问题
- 如何高效突破 O(n²) 复杂度（Sparse / Linear / FlashAttention 等路线）？
- 状态空间模型（Mamba 等）是否会取代 Transformer 在长序列上的地位？
- Decoder-Only 是否是 LLM 的最终架构形态？
