---
name: "EVA-02 与现代视觉 Transformer"
type: concept
domain: ai-learning
created: 2026-04-16
source_reports:
  - reports/paper_analyses/41_eva02_2023.md
---

# EVA-02 与现代视觉 Transformer

## 核心概念

EVA-02 代表了"将 LLM 架构改进迁移至视觉 Transformer"的工程范式。其三大架构升级——SwiGLU FFN、2D RoPE、sub-LayerNorm——均来自语言模型社区，通过跨域迁移显著提升视觉表示能力。

## 技术要点

**SwiGLU FFN**：
- 公式：`FFN(x) = (xW₁ + b₁) ⊗ Swish(xW₂ + b₂) · W₃`
- 门控机制赋予网络选择性激活能力，比 GELU 更高效
- 来源：Shazeer (2020)，在 LLaMA/PaLM 中广泛验证

**2D RoPE（旋转位置编码）**：
- 将 1D RoPE 扩展为 2D：分解为水平+垂直两个独立旋转
- 无需绝对位置嵌入，天然支持变分辨率推理
- 对密集预测任务（检测/分割）优势尤为明显

**Sub-LayerNorm（Pre-Norm）**：
- 位于 Attention 和 FFN 之前（每 Block 2 个 LN）
- 相比 Post-Norm 训练更稳定，梯度流更好

**MIM 预训练目标**：
- 掩码率：75%（继承 MAE）
- 重建目标：CLIP-ViT-bigG 中间层特征（语言对齐语义）
- 关键突破：从 raw pixel 升级为跨模态语义特征

## 模型规格

| 变体 | 参数量 | ImageNet-1K top-1 |
|------|--------|------------------|
| Ti | 6M | — |
| S | 22M | — |
| B | 86M | 88.7% (89.3% w/ IN-21K) |
| L | 304M | 89.7% (90.0% w/ IN-21K) |

COCO 检测（L）：58.3 box AP / 50.2 mask AP  
ADE20K 分割（L）：59.0 mIoU

## 在 EVA 系列中的位置

```
EVA-01 (2022, 1.8B) — 验证 CLIP MIM 目标
    ↓ 缩参数 + 现代化架构
EVA-02 (2023, 304M) — 高效视觉基础模型
    ↓ CLIP 微调
EVA-CLIP (2023) — 零样本分类 80.4% IN-1K
```

## 与相关概念的关联

- → `self_supervised_learning.md`（MAE/DINO 预训练体系）
- → `attention_mechanism.md`（RoPE 是 Attention 位置编码的改进）
- → `latent_diffusion.md`（EVA-02 常作为多模态模型的视觉编码器）
- → `scaling_laws.md`（EVA-02 验证参数效率的重要性）
