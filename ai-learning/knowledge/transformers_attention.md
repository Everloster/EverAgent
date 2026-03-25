---
topic: "Transformer 架构与 Self-Attention"
related_papers: ["#01 Transformer 2017", "#02 BERT 2018", "#14 Bahdanau Attention 2014", "#19 ViT 2020"]
last_updated: "2026-03-26"
---

# Transformer 架构与 Self-Attention 机制

## 核心概念

### Self-Attention（自注意力）
每个词通过**查询、键、值机制**关注序列中所有其他词，实现位置间的直接交互。

**核心公式**：
```
Attention(Q, K, V) = softmax(QK^T / √d_k) · V
```

- **Q（Query）**：当前位置的查询
- **K（Key）**：所有位置的索引标签
- **V（Value）**：所有位置的信息内容
- **√d_k 缩放**：防止点积过大导致梯度消失

**直观理解**：根据问题与目录的匹配度，加权提取书籍内容。

### 多头注意力（Multi-Head Attention）
并行运行 h 个独立的注意力头，每个头关注不同的语义子空间：
```
MultiHead(Q,K,V) = Concat(head_1,...,head_h) W^O
head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```

---

## Transformer 架构（2017）

### 整体设计
```
输入 → Embedding + 位置编码
     → Encoder Stack (N层)
       ├─ Multi-Head Attention
       ├─ Add & Norm
       ├─ Feed-Forward Network
       └─ Add & Norm
     → Decoder Stack (N层)
       ├─ Masked Multi-Head Attention (自因果)
       ├─ Cross-Attention (关注编码器输出)
       └─ FFN
     → Linear + Softmax → 输出概率
```

**关键创新**：
1. **完全基于注意力**，无 RNN 的串行瓶颈
2. **可完全并行化**训练，GPU 利用率远优于 RNN
3. **长程依赖直接建模**（路径长度 O(1)）

### 位置编码
使用正弦/余弦函数注入位置信息：
```
PE(pos, 2i)   = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```

**为什么用正弦？** 支持长度外推，模型可泛化到未见序列长度。

### 性能
- **WMT14 英德翻译**：28.4 BLEU（+2.0 vs 之前 SOTA）
- **英法翻译**：41.0 BLEU
- **训练速度**：12 小时（8 个 P100 GPU），远快于 RNN

---

## BERT（2018）— 双向预训练

### 核心创新：掩码语言模型（MLM）
随机遮盖 15% 的 token，让模型基于**完整上下文**预测被遮盖词：
- 80%：替换为 `[MASK]`
- 10%：替换为随机词
- 10%：保持原词

**关键洞见**：这样实现了深层双向上下文建模（而非 ELMo 的浅层拼接）。

**数学形式**：
```
L_MLM = -Σ_{i ∈ M} log P(x_i | x_1,...,x_{i-1},[MASK],x_{i+1},...,x_n)
```

相比自回归 LM 只能看左侧，MLM 在条件中包含右侧上下文。

### BERT 架构版本
```
BERT-Base：12层，d_model=768，12个头，≈1.1亿参数
BERT-Large：24层，d_model=1024，16个头，≈3.4亿参数
```

**输入表示**（三重嵌入叠加）：
```
InputEmbedding = TokenEmbedding + SegmentEmbedding + PositionEmbedding
```

特殊 token：
- `[CLS]`：序列开头，其最终隐状态用于分类任务
- `[SEP]`：句子分隔符

### 微调范式（Fine-tuning）
预训练后，对不同下游任务只需轻量级任务头：
- **文本分类**：`[CLS]` 向量 → Linear(768, num_labels)
- **NER**：每个 token 向量 → 逐 token 分类
- **问答**：预测答案起始和结束位置

### 实验结果
- **GLUE Benchmark**（9个任务）：BERT-Large 平均分 80.5（+4.7 vs RoBERTa/ALBERT）
- **SQuAD 1.1**：F1 = 93.2（**首次超越人类 91.2%**），EM = 86.7
- **SQuAD 2.0**：F1 = 83.1，EM = 80.0
- **CoNLL-2003 NER**：F1 = 92.8

**消融实验**：
| 配置 | SQuAD F1 | MNLI-m |
|------|----------|--------|
| BERT-Base | 88.5 | 84.4 |
| 去掉双向性 | 77.8 | 82.1 |
| 去掉 NSP | 87.9 | 83.9 |

结论：**双向性是关键**（-10.7 F1 若移除），深层双向优于 ELMo 风格浅层拼接。

### 产业影响
- 开创了"预训练 + 微调"的 NLP 新范式
- 2019年10月，Google 将 BERT 部署到搜索，**改善约 10% 的英语搜索质量**
- HuggingFace 等模型分享平台的繁荣

---

## GPT 系列（2018-2024）

### GPT-3（2020）— 规模化的突破

**架构**（175B 版本）：
```
层数：96
d_model：12,288
注意力头：96
FFN隐层：49,152
最大序列长度：2,048 tokens
词汇表：50,257
```

也训练了 8 个规模版本（125M → 175B）来研究 scaling 效应。

**核心创新：In-Context Learning（上下文学习）**

不需要梯度更新，仅通过改变 prompt 完成任务：

```
Zero-shot：
  Prompt: "Translate English to French: cheese =>"

Few-shot（k=32）：
  Prompt: "Translate English to French:
           sea otter => loutre de mer
           ...（32个示例）...
           cheese =>"
```

**关键发现**：
- Zero-shot BLEU：21.2
- Few-shot (k=32) BLEU：32.6
- 示例数量 k>32 后收益递减（context window 限制）

**数据量**：约 5000 亿 tokens
```
Common Crawl：4100亿 tokens（60%，过滤后）
WebText2：190亿 tokens（22%）
Books1/2：670亿 tokens（16%）
Wikipedia：30亿 tokens（3%）
```

实际训练 ~3000亿 tokens。

### Scaling Laws 与涌现能力

训练了 8 个规模模型，发现 loss 与参数量呈幂律关系：
```
L(N) ≈ (N_c/N)^α_N
```

**关键发现**（SuperGLUE）：
```
GPT-3 125M：  63.8（zero-shot）→ 67.2（few-shot）
GPT-3 1.3B：  67.5 → 69.1
GPT-3 13B：   70.1 → 73.6
GPT-3 175B：  71.8 → 74.4
```

**涌现能力**示例（某特定规模阈值才出现）：
- 多步算术推理：>10B 参数
- 多语言翻译：>10B 参数
- 代码生成：>50B 参数

### 实验数据

| 任务 | GPT-3 zero-shot | GPT-3 few-shot | 微调 SOTA |
|------|-----------------|--|--|
| 翻译（BLEU）| 21.2 | 32.6 | 45.6 |
| TriviaQA EM | 64.3 | 71.2 | T5-11B 50.1 |
| Penn Treebank PPL | 20.50 | - | ~15 |

**意外发现**：代码生成（训练数据含 GitHub），暗示了 Codex 和后来 Copilot 的可能。

### 局限与后续
- **上下文窗口**：2048 tokens，无法处理长文档
- **知识截止**：无法学习新信息
- **幻觉（Hallucination）**：高置信度生成错误事实（至今仍是核心问题）
- **提示敏感性**：对 prompt 格式极为敏感，示例顺序不同可差 30%+

---

## 工程实践

### 内存瓶颈与优化
- **注意力矩阵**：O(n²) 复杂度，4K tokens 需 ~16M 个值
- **FlashAttention**：IO-Aware 计算，避免完整实例化注意力矩阵
- **KV Cache**：推理时缓存 K/V，加速自回归生成（对推理至关重要）
- **GQA（分组查询注意力）**：减少 KV 头数，降低推理内存（Llama 3 采用）

### 位置编码的演进
- **原始正弦编码**：固定，支持长度外推
- **RoPE（旋转位置编码）**：相对位置，更好的长度外推能力
- **ALiBi（注意力线性偏置）**：无需编码，仅在注意力分数加偏置

---

## 小结
从 Transformer 的通用架构，到 BERT 的双向预训练，再到 GPT-3 的规模化涌现，形成了现代 LLM 的技术基础。BERT 的 MLM 和微调范式适合理解任务，GPT 的自回归和 in-context learning 适合生成任务。当前主流大模型（GPT-4、Claude、Gemini）均基于这些核心设计，只是通过 Scaling Laws、数据质量、后训练对齐等方式进行增强。
