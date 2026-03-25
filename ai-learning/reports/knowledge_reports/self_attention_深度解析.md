---
title: "Self-Attention 深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-03-23"
---
# 知识深度解析：Self-Attention（自注意力机制）

> 生成日期：2026-03-23 | 难度：⭐⭐⭐

---

## 🎯 知识定位

```
主题：Self-Attention（自注意力机制）
所属领域：深度学习 / NLP / Transformer 架构
难度等级：⭐⭐⭐（中级）
学习前置：矩阵乘法、softmax 函数、基本神经网络概念
学习时长预估：3-5 小时（读懂原理）+ 2-3 小时（代码实现）
```

---

## 🔍 层次一：5岁小孩也能懂的类比

**类比：在课堂上回答问题**

想象你在一个班级里，老师问了一个问题（这就是 Query）。
每个同学都有自己的知识领域标签（Key），比如"擅长数学"、"了解历史"等。
每个同学的实际知识内容（Value）也各不相同。

当你要回答这个问题时，你会：
1. 看看哪些同学的标签（Key）与问题（Query）最相关
2. 更多关注相关度高的同学
3. 综合这些同学的知识（Value）得出答案

**Self-Attention 就是**：每个词语在理解自己时，自动衡量句子中其他词语对自己的相关性，然后综合最相关词语的信息来更新自己的表示。

**核心直觉**：让每个位置的词"看看"句子中所有其他词，自主决定应该关注谁。

---

## 📖 层次二：概念定义与基本原理

### 正式定义

Self-Attention 是一种注意力机制，其中 Query、Key、Value 均来自同一个序列，使得序列中每个位置能够直接关注序列中的所有其他位置。

**公式**：
```
Attention(Q, K, V) = softmax(QK^T / √d_k) · V
```

### 与普通 Attention 的区别

| 类型 | Q 来源 | K/V 来源 | 用途 |
|------|--------|---------|------|
| Self-Attention | 本序列 | 本序列 | 编码序列内部关系 |
| Cross-Attention | 解码器序列 | 编码器输出 | Decoder 关注 Encoder 信息 |
| Bahdanau Attention | 解码器隐状态 | 编码器隐状态 | 早期 Seq2Seq 注意力 |

---

## ⚙️ 层次三：技术细节

### 步骤分解

**输入**：序列 X（形状：[序列长度 n, 词向量维度 d_model]）

**Step 1：线性变换生成 Q, K, V**
```
Q = X · W_Q    # [n, d_k]
K = X · W_K    # [n, d_k]
V = X · W_V    # [n, d_v]
```
- W_Q, W_K, W_V 是可学习的权重矩阵
- 将输入投影到 Query、Key、Value 子空间

**Step 2：计算注意力分数（相关性）**
```
scores = Q · K^T / √d_k    # [n, n]
```
- 每对位置 (i, j) 都计算相关性分数
- 除以 √d_k 防止梯度问题（当 d_k 大时，点积会很大，softmax 梯度消失）

**Step 3：Softmax 归一化**
```
weights = softmax(scores)    # [n, n]，每行和为1
```
- 将分数转化为概率分布（注意力权重）

**Step 4：加权求和 Value**
```
output = weights · V    # [n, d_v]
```
- 每个位置的输出 = 所有位置 Value 的加权平均

### 可视化

```
位置 1 "猫"  ───→ Q_1 ─┐
位置 2 "喜欢"────→ Q_2  │  × K^T → scores → softmax → weights
位置 3 "鱼"  ───→ Q_3 ─┘
                          ↓
              V_1, V_2, V_3 → weighted sum → output
```

### 为什么要除以 √d_k？

若 Q 和 K 的每个元素均来自均值0、方差1的分布，则 Q·K 的点积结果的方差为 d_k。除以 √d_k 将方差归一化为1，防止 softmax 进入饱和区（梯度极小的区域）。

---

## 💻 层次四：代码实现

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class SelfAttention(nn.Module):
    """
    单头自注意力的最简实现
    """
    def __init__(self, d_model: int, d_k: int):
        super().__init__()
        self.d_k = d_k

        # 线性变换矩阵（可学习参数）
        self.W_Q = nn.Linear(d_model, d_k, bias=False)
        self.W_K = nn.Linear(d_model, d_k, bias=False)
        self.W_V = nn.Linear(d_model, d_k, bias=False)

    def forward(self, x, mask=None):
        """
        x: [batch_size, seq_len, d_model]
        返回: [batch_size, seq_len, d_k]
        """
        # Step 1: 生成 Q, K, V
        Q = self.W_Q(x)   # [B, n, d_k]
        K = self.W_K(x)   # [B, n, d_k]
        V = self.W_V(x)   # [B, n, d_k]

        # Step 2: 计算注意力分数
        scores = torch.matmul(Q, K.transpose(-2, -1))  # [B, n, n]
        scores = scores / math.sqrt(self.d_k)           # 缩放

        # Step 3: 可选遮挡（用于 Decoder 防止看到未来信息）
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        # Step 4: Softmax 归一化
        weights = F.softmax(scores, dim=-1)  # [B, n, n]

        # Step 5: 加权聚合 Value
        output = torch.matmul(weights, V)    # [B, n, d_k]

        return output, weights  # 返回 weights 便于可视化

# 使用示例
batch_size, seq_len, d_model, d_k = 2, 10, 512, 64
x = torch.randn(batch_size, seq_len, d_model)

attn = SelfAttention(d_model=512, d_k=64)
output, weights = attn(x)
print(f"输入形状: {x.shape}")      # [2, 10, 512]
print(f"输出形状: {output.shape}") # [2, 10, 64]
print(f"权重形状: {weights.shape}") # [2, 10, 10]
```

### 多头注意力（Multi-Head Attention）实现

```python
class MultiHeadAttention(nn.Module):
    """
    多头注意力：并行多个注意力头，捕获不同子空间的信息
    """
    def __init__(self, d_model: int, num_heads: int):
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads  # 每个头的维度

        # 合并所有头的投影（更高效）
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)  # 输出投影

    def split_heads(self, x):
        """将 [B, n, d_model] 分割为 [B, h, n, d_k]"""
        B, n, _ = x.shape
        x = x.view(B, n, self.num_heads, self.d_k)
        return x.transpose(1, 2)  # [B, h, n, d_k]

    def forward(self, x, mask=None):
        B, n, _ = x.shape

        # 生成并分割多头 Q, K, V
        Q = self.split_heads(self.W_Q(x))  # [B, h, n, d_k]
        K = self.split_heads(self.W_K(x))
        V = self.split_heads(self.W_V(x))

        # 每个头独立计算注意力
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        weights = F.softmax(scores, dim=-1)
        output = torch.matmul(weights, V)  # [B, h, n, d_k]

        # 拼接所有头
        output = output.transpose(1, 2).contiguous()
        output = output.view(B, n, self.d_model)  # [B, n, d_model]

        return self.W_O(output)  # 最终输出投影
```

---

## 🏗️ 层次五：在实际系统中的应用

### GPT/Claude 中的 Causal Self-Attention
使用 Decoder-only 结构，加入 Causal Mask（下三角矩阵），使每个位置只能看到它之前的词。

### BERT 中的 Bidirectional Self-Attention
使用 Encoder-only 结构，不使用 Mask，每个词可以看到全句所有词（包括后面的词）。

### 工程实践注意事项

- **内存瓶颈**：注意力矩阵 [n, n] 对长序列代价巨大（4K tokens 需要 ~16M 个值）
- **FlashAttention**：通过 IO-Aware 计算避免完整实例化注意力矩阵，节省内存和时间
- **KV Cache**：在推理时缓存 K 和 V，避免重复计算（对自回归生成非常重要）

---

## 🔬 深度扩展：前沿进展

- **RoPE（旋转位置编码）**：取代原始的绝对位置编码，支持更好的长度外推
- **GQA（分组查询注意力）**：减少 KV 头数量，降低推理内存，用于 LLaMA 3
- **Flash Attention 1/2/3**：大幅提升注意力计算效率
- **Sparse Attention**：只关注局部或特定位置，降低 O(n²) 复杂度

---

## ✅ 知识检验题

**基础级**：
1. Self-Attention 中 Q、K、V 分别代表什么？用类比解释。
2. 为什么注意力分数要除以 √d_k？

**进阶级**：
3. Decoder 中的 Masked Self-Attention 与 Encoder 中的有什么区别？
4. 如果不使用多头，只用单头注意力会有什么问题？

**专家级**：
5. 注意力机制的 O(n²) 时间复杂度是如何被 FlashAttention 绕过的？
6. 请解释 KV Cache 在推理时的工作原理，并说明它如何加速自回归生成。

---

## 📚 学习资源推荐

**入门可视化**：
- [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/) — 必读！
- [Attention? Attention! - Lilian Weng Blog](https://lilianweng.github.io/posts/2018-06-24-attention/)

**深入理解**：
- 原始论文：*Attention Is All You Need* (Vaswani et al., 2017)
- *Formal Algorithms for Transformers* (DeepMind, 2022) — 严格数学推导

**动手实践**：
- Andrej Karpathy [nanoGPT](https://github.com/karpathy/nanoGPT) — 200行实现GPT
- [minGPT](https://github.com/karpathy/minGPT) — 更详细的教学版本

