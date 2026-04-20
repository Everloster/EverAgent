# Transformer From Scratch（从零实现 Transformer）

> 不依赖任何预训练库，纯 PyTorch 手写仅解码器 Transformer 语言模型，用于自回归文本生成。

---

## 直觉理解（Why it exists）

传统 RNN 将所有历史信息压缩到固定大小的隐藏状态 h，长序列中早期信息会被"遗忘"。

Transformer 的核心思想：**让序列中每个位置直接与所有历史位置交互**，没有信息瓶颈。代价是计算量随序列长度平方增长（O(n²)），这是 FlashAttention 等优化工作的出发点。

---

## 核心机制（How it works）

### 缩放点积注意力

```
Attention(Q, K, V) = softmax( Q × K^T / √d_head ) × V
```

**数学推导**：设 Q, K ∈ R^{T×d_head}，内积 Q×K^T 的每个元素期望为 0，方差为 d_head。
除以 √d_head 将方差归一化到 1，防止 softmax 进入饱和区（梯度消失）。

**代码实现**（`src/model.py`, Attention 类）：
```python
q = self.query_layer(x)   # [B, T, head_size]
k = self.key_layer(x)     # [B, T, head_size]
v = self.value_layer(x)   # [B, T, head_size]

weights = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
weights = weights.masked_fill(self.tril[:T, :T] == 0, float('-inf'))  # 因果 mask
weights = F.softmax(weights, dim=-1)
out = weights @ v
```

### 多头注意力

**设计动机**：单头只能学习一种关注模式（如语法依存）。多头并行学习多种模式（语法 + 语义 + 位置），信息更丰富。

**实现**：将 d_model 维空间切分为 num_heads 个独立的 head_size 维子空间，各自计算注意力后拼接，投影回 d_model：
```python
# 4个头并行计算，各自 head_size=16
out = torch.cat([h(x) for h in self.heads], dim=-1)  # [B, T, d_model]
out = self.projection_layer(out)  # 线性投影
```

### 位置编码

Transformer 本身无法感知 token 的位置顺序（注意力是排列不变的）。需要额外注入位置信息。

**正弦/余弦位置编码**（Vaswani 2017 原版）：
```python
PE[pos, 2i]   = sin(pos / 10000^(2i/d_model))
PE[pos, 2i+1] = cos(pos / 10000^(2i/d_model))
```

**特性**：
- 不同位置的编码向量相似度随距离单调递减
- 支持外推（理论上可处理训练时未见过的序列长度）
- 固定不变（无需训练），但现代 LLM 更倾向用可学习位置编码或 RoPE

### Pre-LN vs Post-LN

| | Post-LN（原论文） | Pre-LN（GPT-2+） |
|--|-----------------|-----------------|
| 位置 | LayerNorm 在残差后 | LayerNorm 在残差前 |
| 稳定性 | 较差，需精心调 lr | **更稳定**，默认设置可用 |
| 最终表示 | 经 LayerNorm 归一化 | 未归一化 |
| 现代使用 | 较少 | **主流** |

```python
# Post-LN（原论文）
x = LayerNorm(x + Attention(x))

# Pre-LN（本项目实现，src/model.py L156-157）
x = x + Attention(LayerNorm(x))
x = x + FFN(LayerNorm(x))
```

---

## 本项目实现规格

| 组件 | 实现文件 | 行号 |
|------|---------|------|
| 超参数配置 | `src/model.py` | 11-19 |
| FeedForward（d×4d→d，ReLU） | `src/model.py` | 48-65 |
| Attention（缩放点积 + causal mask） | `src/model.py` | 67-105 |
| MultiHeadAttention | `src/model.py` | 107-132 |
| TransformerBlock（Pre-LN + 残差） | `src/model.py` | 134-158 |
| 正弦位置编码（每步重算） | `src/model.py` | 197-203 |
| TransformerLanguageModel（完整） | `src/model.py` | 161-235 |
| 训练循环 + AdamW | `src/model.py` | 265-288 |
| 自回归生成（multinomial 采样） | `src/model.py` | 220-235 |

**教学规模** vs 工业模型对比：

| | 本实验 | GPT-2 | GPT-3 | Qwen2.5-3B |
|--|--------|-------|-------|-----------|
| d_model | 64 | 768 | 12,288 | 2,048 |
| 层数 | 8 | 12 | 96 | 36 |
| 参数量 | ~130K | 117M | 175B | 3B |
| context | 16 | 1024 | 2048 | 32768 |

---

## 与相关概念的关系

- **→ 阶段 2/3 Transformers 库**：BERT、GPT-2 都是 Transformer 变体，原理完全相同，规模不同
- **→ [lora_peft.md](lora_peft.md)**：LoRA 是在预训练 Transformer 权重上做低秩更新
- **→ [tokenization.md](tokenization.md)**：本实验用 TikToken，`src/model.py` L36-41 展示了 tokenization 流程

---

## 进一步学习

- **原始论文**：[Attention Is All You Need](https://arxiv.org/abs/1706.03762)（Vaswani et al., 2017）
- **推荐视频**：[Andrej Karpathy - Let's build GPT](https://youtu.be/kCc8FmEb1nY)
- **图解教程**：[The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/)
- **数学深化**：[Formal Algorithms for Transformers](https://arxiv.org/abs/2207.09238)（DeepMind，严格数学表述）
