---
title: 从零实现 Transformer 语言模型
type: experiment_analysis
status: done
experiment_id: exp_001
notebook: notebooks/step-by-step.ipynb
updated_on: 2026-04-20
---

## 实验摘要

> 不依赖 HuggingFace，纯 PyTorch 从零实现仅解码器 Transformer 语言模型，在销售教科书数据集上进行自回归预训练，验证 Transformer 核心组件的实现正确性。

## Step 1 实验目标

- **假设验证**：手写实现多头自注意力、位置编码、残差连接等核心组件，确认与原论文架构一致
- **背景**：对应 ai-learning 中 `Attention Is All You Need`（2017, Vaswani et al.）的实践复现
- **数据**：`data/sales_textbook.txt`（来源：HuggingFace goendalf666/sales-textbook_for_convincing_and_selling，452KB，1460行，66,323词）

## Step 2 实现方法

**框架**：PyTorch（纯手写，无 transformers 库依赖）

**分词器**：TikToken `cl100k_base`（与 GPT-3/4 同款编码，vocab_size ≈ 100,000+）

**模型架构**（超参数，来自 `src/model.py:10-19`）：

| 超参数 | 值 | 说明 |
|--------|-----|------|
| `d_model` | 64 | 嵌入维度 |
| `num_blocks` | 8 | Transformer 层数 |
| `num_heads` | 4 | 多头注意力头数 |
| `head_size` | 16（=64/4） | 每头维度 |
| `context_length` | 16 | 最大上下文长度（tokens） |
| `batch_size` | 4 | 训练批次大小 |
| `dropout` | 0.1 | Dropout 率 |
| `learning_rate` | 1e-3 | AdamW 学习率 |
| `max_iters` | 5000 | 最大训练迭代数 |
| `eval_interval` | 50 | 评估间隔 |

**数据划分**：90% 训练 / 10% 验证（`src/model.py:43`）

**架构注意点**（与原 Transformer 论文差异）：
- 使用 Pre-LN（先 LayerNorm 再 Attention），而非原论文的 Post-LN（`src/model.py:156-157`）
- 位置编码在每次 forward 时重新计算，非参数化（`src/model.py:197-203`）
- FFN 激活函数用 ReLU（原论文），非 GELU（GPT-2 改进版）

## Step 3 关键发现

**模型参数量估算**（基于架构，未实际统计）：
- Embedding 层：约 `vocab_size × 64` 参数
- 每个 TransformerBlock：约 `4 × 64² = 16,384` 参数
- 8 个 Block 合计约 131K 参数 + Embedding

**训练指标**：`[未运行 - 需执行 src/model.py 获取实际 loss 曲线]`

结构验证发现：
- Pre-LN 结构（非原论文 Post-LN）更稳定，与 GPT-2 实践一致
- context_length=16 极短，导致模型只能捕获非常局部的语言模式
- 教学规模（d_model=64）参数量远小于实际 LLM，训练速度快

## Step 4 代码参考

| 组件 | 文件路径 | 行号 |
|------|---------|------|
| 超参数配置 | `src/model.py` | 11-19 |
| FeedForward | `src/model.py` | 48-65 |
| Scaled Dot-Product Attention | `src/model.py` | 67-105 |
| MultiHeadAttention | `src/model.py` | 107-132 |
| TransformerBlock（Pre-LN） | `src/model.py` | 134-158 |
| 正弦位置编码 | `src/model.py` | 197-203 |
| 完整模型 TransformerLanguageModel | `src/model.py` | 161-235 |
| 训练循环 | `src/model.py` | 271-287 |
| 自回归生成 | `src/model.py` | 220-235 |

**核心可复用函数**：
- `get_batch(split)` — 随机采样训练/验证批次（`src/model.py:238-244`）
- `estimate_loss()` — 无梯度评估 train/val loss（`src/model.py:246-258`）

## Step 5 局限性与下一步

**局限性**：
- `context_length=16` 过短，生成文本缺乏长程连贯性
- `d_model=64` 为教学规模，远未达到实际 LLM 能力
- 每次 forward 重算位置编码，效率低（应缓存或使用可学习 PE）
- 无 KV Cache 机制，推理时计算量与序列长度成平方增长

**建议后续实验**：
1. 将 `context_length` 扩展到 256/512，观察生成质量变化
2. 引入可学习位置编码（nn.Embedding 替换正弦函数）
3. 与 `exp_003` 的预训练模型对比，量化规模效益
