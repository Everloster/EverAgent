# Transformer From Scratch（从零实现 Transformer）

> 来源：exp_001 | 关联论文：Attention Is All You Need (Vaswani et al., 2017)

---

## 核心定义

不依赖任何预训练库，纯 PyTorch 手写实现仅解码器（Decoder-only）Transformer 语言模型，用于自回归文本生成任务。

## 架构要素

| 组件 | 实现细节 | 与原论文差异 |
|------|---------|------------|
| 注意力机制 | 缩放点积注意力（Q×K^T / √d_head，下三角 mask） | 无差异 |
| 多头注意力 | 4头并行，每头 head_size=16，最后拼接投影 | 无差异 |
| 位置编码 | 正弦/余弦 PE（每次 forward 重算） | 原论文相同；改进版用可学习 PE |
| 层归一化 | **Pre-LN**（LayerNorm 在 Attention/FFN 之前） | 原论文用 Post-LN；Pre-LN 更稳定 |
| 前馈网络 | d_model → 4×d_model → d_model，ReLU 激活 | 原论文同；GPT-2 改用 GELU |
| 残差连接 | 每个子层输出 += 输入 | 无差异 |

## 实现规模（教学版）

```
d_model=64, num_blocks=8, num_heads=4, context_length=16
```

## 关键实现文件

- `src/model.py`（完整实现）：Attention（L67）、MultiHeadAttention（L107）、TransformerBlock（L134）、TransformerLanguageModel（L161）

## 与 ai-learning 的关联

- → `ai-learning/wiki/concepts/attention_mechanism.md`（理论层）
- → `ai-learning/reports/paper_analyses/` Attention Is All You Need 精读
