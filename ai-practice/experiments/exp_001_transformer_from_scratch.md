---
title: 从零实现 Transformer 语言模型
type: tutorial_note
stage: 1
notebook: notebooks/01_transformer_from_scratch.ipynb
prerequisites: ["pytorch_basics", "linear_algebra", "softmax"]
updated_on: 2026-04-20
---

## 学习目标

- [ ] 理解缩放点积注意力的数学原理（Q、K、V 是什么，为什么要除以 √d_head）
- [ ] 能读懂并解释 `MultiHeadAttention` 的完整实现
- [ ] 理解 Pre-LN 与 Post-LN 的结构差异及训练稳定性影响
- [ ] 理解自回归语言模型的训练与生成流程
- [ ] 能独立修改超参数并观察训练效果变化

---

## 核心概念（Why）

### 为什么要从零实现？

HuggingFace 一行代码就能加载 GPT-4 级别的模型。那为什么还要手写 Transformer？

因为**理解 = 能复现**。当你真正手写了 Attention 机制后：
- 你会知道 KV Cache 为什么能加速推理（因为 K、V 不需要重算）
- 你会理解 FlashAttention 解决的是什么内存瓶颈
- 你会明白为什么 `context_length` 对显存的影响是平方级的

### 注意力机制的直觉

注意力的核心问题：**序列中每个位置，应该"关注"其他哪些位置？**

传统 RNN 用固定大小的隐藏状态压缩所有历史信息，导致长序列遗忘。  
注意力机制让每个位置直接"查询"所有历史位置，没有信息损失。

**数学表达**：
```
Attention(Q, K, V) = softmax(Q × K^T / √d_head) × V
```

- Q（Query）：当前位置在"问什么"
- K（Key）：历史位置在"提供什么关键词"
- V（Value）：历史位置的实际内容
- `/ √d_head`：缩放因子，防止点积值过大导致 softmax 梯度消失

**为什么要缩放**？d_head 维的随机向量内积期望为 0，方差为 d_head。除以 √d_head 后方差归一到 1，softmax 的梯度不会饱和。

### 为什么用多头？

单头注意力只能学习一种"关注模式"（如语法依存）。  
多头让模型同时学习多种模式（语法 + 语义 + 位置等），拼接后投影合并信息。

### Pre-LN vs Post-LN

原论文（Vaswani 2017）用的是 **Post-LN**（LayerNorm 在残差之后）：
```
x = LayerNorm(x + Attention(x))   # Post-LN
```

本项目用的是 **Pre-LN**（LayerNorm 在 Attention 之前，GPT-2 采用的方案）：
```
x = x + Attention(LayerNorm(x))   # Pre-LN
```

Pre-LN 训练更稳定（梯度不容易爆炸），是现代大模型的标配。代价是最终表示没有经过 LayerNorm 归一化。

---

## 实现解析

### 模型架构（教学规模）

| 超参数 | 值 | 含义 |
|--------|-----|------|
| `d_model` | 64 | 嵌入维度（决定参数量） |
| `num_blocks` | 8 | Transformer 层数 |
| `num_heads` | 4 | 注意力头数 |
| `head_size` | 16（=64/4） | 每头的维度 |
| `context_length` | 16 | 最大上下文长度 |
| `batch_size` | 4 | 训练批次大小 |

### 关键实现片段

**缩放点积注意力**（`src/model.py`，Attention 类）：
```python
# Q × K^T / √d_head
weights = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
# 下三角 mask：防止看到未来信息（自回归）
weights = weights.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
weights = F.softmax(weights, dim=-1)
out = weights @ v
```

**残差连接（Pre-LN）**（`src/model.py`，TransformerBlock 类）：
```python
x = x + self.multi_head_attention_layer(self.layer_norm_1(x))
x = x + self.feed_forward_layer(self.layer_norm_2(x))
```

**正弦位置编码**（`src/model.py`，forward 方法）：
```python
position = torch.arange(0, context_length).unsqueeze(1)
div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
PE[:, 0::2] = torch.sin(position * div_term)
PE[:, 1::2] = torch.cos(position * div_term)
```

### 训练数据

- 文件：`data/sales_textbook.txt`（来源：HuggingFace，452KB，~66,000 词）
- 分词器：TikToken `cl100k_base`（与 GPT-4 相同的分词方案）
- 划分：90% 训练 / 10% 验证

---

## 实验结果

**注**：本实验需要运行 `notebooks/01_transformer_from_scratch.ipynb` 获取实际结果。  
在 CPU 上约需 30-60 分钟（5000 步），GPU 约需 5-10 分钟。

**理论参数量估算**：
- Embedding：vocab_size × 64 ≈ 640 万参数
- 每层 TransformerBlock：约 16K 参数（8 头 × 4 个线性层）
- 8 层合计：约 13 万参数 + Embedding

**已知结果特征**（基于代码结构推断）：
- 初始 loss（随机权重）：约 `ln(vocab_size)` ≈ 11.5
- 训练 5000 步后，训练 loss 应下降至 4-6 范围
- 生成文本在教学规模下语义连贯性有限（context_length=16 过短）

---

## 思考题与延伸实验

1. **参数规模影响**：将 `d_model` 从 64 改为 128，预期训练时间和最终 loss 如何变化？为什么？

2. **上下文长度影响**：将 `context_length` 从 16 改为 64，生成的文本连贯性会有什么变化？

3. **注意力分析**：如何提取并可视化注意力权重矩阵？（提示：修改 `Attention.forward` 返回 `weights`）

4. **温度采样**：`src/inference.py` 的生成目前用 `torch.multinomial` 采样。如何添加 temperature 参数来控制生成的多样性？（temperature > 1 更随机，< 1 更确定）

5. **可学习位置编码**：当前用正弦/余弦固定位置编码。如果改用 `nn.Embedding(context_length, d_model)` 作为可学习位置编码，训练行为会如何变化？

---

## 参考资料

- **原始论文**：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)（Vaswani et al., 2017）
- **推荐视频**：Andrej Karpathy 的 [Let's build GPT](https://www.youtube.com/watch?v=kCc8FmEb1nY)（本实验的灵感来源）
- **深度阅读**：[The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)（Jay Alammar，图示最清晰）
- **本项目 Wiki**：[wiki/concepts/transformer_from_scratch.md](../wiki/concepts/transformer_from_scratch.md)
