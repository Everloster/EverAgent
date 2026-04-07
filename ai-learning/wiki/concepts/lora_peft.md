---
id: concept-lora_peft
title: "LoRA / 参数高效微调（PEFT）"
type: concept
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [LoRA_深度解析, 15_lora_2021]
status: active
---

# LoRA（Low-Rank Adaptation）与 PEFT

## 一句话定义
冻结预训练权重，仅在每个权重矩阵旁注入一对低秩可训练矩阵（B×A），以全量微调 0.01%~1% 的参数量近似全量微调效果。

## 核心原理
**关键观察（Aghajanyan et al., 2020）**：预训练模型微调时，权重变化量 ΔW 的**内在维度（intrinsic dimensionality）极低**——投影到随机低维子空间后，微调效果几乎不变。来源：15_lora_2021 §核心动机

**低秩分解**：
```
ΔW = B × A
W ∈ ℝ^(d×d),  A ∈ ℝ^(r×d),  B ∈ ℝ^(d×r),  r ≪ d

参数量对比：d² vs 2rd
例：d=768, r=8 → 589,824 vs 12,288，节省约 98%
```
来源：LoRA_深度解析 §层次二

**前向传播**：
```
h = W₀x + (α/r) · BAx
A 用随机高斯初始化；B 用零初始化（确保训练开始时 ΔW = 0，不破坏预训练权重）
```
来源：LoRA_深度解析 §技术细节

**推理零开销**：训练完成后将 BA 合并回原权重 W' = W + (α/r)·BA，推理与原模型完全相同，无额外延迟。来源：LoRA_深度解析 §原理3

## 关键数据点
- **GPT-3 上 r=4 时**：可训练参数仅为全量微调的 **0.01%**，显存从 350GB 降至约 35GB（8× 48GB A100 可用）。来源：15_lora_2021 §核心贡献
- **常用注入位置**：注意力的 Q/V 投影矩阵；K/O 投影与 FFN 层（gate/up/down_proj）也常加，能再获 1-2% 提升。来源：LoRA_深度解析 §应用位置 / §陷阱3
- **典型超参数**：r ∈ {4, 8, 16}，α 通常 = r 或 = 2r，dropout 0.05~0.1。来源：LoRA_深度解析 §关键超参数

## 与其他 PEFT 方法对比
| 方法 | 可训练参数 | 推理开销 | 性能 |
|------|-----------|---------|------|
| **全量微调** | 100% | 无 | 最高基准 |
| **LoRA** | 0.01%~1% | 无（合并后） | 接近全量 |
| **Adapter**（Houlsby 2019） | ~3% | 有（串联层） | 略低 |
| **Prefix Tuning** | <0.1% | 有（占用上下文） | 不稳定 |
| **BitFit**（仅训练偏置） | ~0.1% | 无 | 上限低 |

来源：LoRA_深度解析 §与相关方法的区别

## 重要变体
- **QLoRA**（Dettmers et al., 2023）：基础模型 4-bit NF4 量化 + LoRA，单张 24GB 消费级显卡可微调 65B 模型。来源：LoRA_深度解析 §常见变体
- **DoRA**（Liu et al., 2024）：将权重分解为幅度（magnitude）和方向（direction），分别适配，更接近全量微调，代码/推理任务上优于 LoRA 1-2%。来源：LoRA_深度解析 §2024-2025 新进展
- **LoRA+**（Hayou et al., 2024）：A 与 B 使用不同学习率（B 远大于 A），显著提升效果。来源：LoRA_深度解析 §常见变体
- **AdaLoRA**：动态分配各层的秩，相同总参数量下效果更好。来源：LoRA_深度解析 §改进方向

## 工程价值场景
- **多任务 LoRA 切换**：单份基础模型 + 多个轻量适配器，按请求动态切换（每个 LoRA 通常仅 ~15MB）。来源：LoRA_深度解析 §应用场景3
- **LLaMA 指令微调**：Alpaca-LoRA、Vicuna 等开源模型几乎全部基于 LoRA。来源：LoRA_深度解析 §应用场景1

## 在本项目的相关报告
- [LoRA 深度解析](../../reports/knowledge_reports/LoRA_深度解析.md)
- [LoRA (2021) 论文精读](../../reports/paper_analyses/15_lora_2021.md)

## 跨域连接
- DPO/RLHF 训练时几乎都用 LoRA 减少显存 → concept: rlhf
- LoRA 主要注入 Transformer 注意力层的 Q/V → concept: attention_mechanism / transformer_architecture
- MoLoRA：对 MoE 的每个专家分别做 LoRA 微调 → concept: moe_architecture

## 开放问题
- LoRA 微调后是否存在"遗忘"？（研究表明有，但比全量微调小）
- 不同任务的 LoRA 是否可以无损合并（Task Arithmetic）？
- LoRA 是否能完全替代 RLHF？目前 LoRA + DPO 已成标配，但效果上限仍低于全量 RLHF。
