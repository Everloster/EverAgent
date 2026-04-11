# Latent Diffusion（潜空间扩散模型）

> 扩散模型的效率革命：将像素空间扩散迁移到预训练自编码器的低维潜空间

## 一句话定义

Latent Diffusion (LDM) 通过预训练自编码器将扩散过程从高维像素空间压缩到低维潜空间，在大幅降低计算成本的同时保持生成质量，并通过交叉注意力机制实现灵活的多模态条件生成。

## 核心思想：感知压缩与语义生成的解耦

```
图像信息 = 感知细节（高频纹理）+ 语义内容（低频结构）

像素空间扩散的痛点：
  → 大量计算花在学习对人类感知不重要的细节上

LDM 的洞察：
  → 用自编码器压缩掉感知冗余（f = {4, 8}）
  → 在潜空间做扩散，只学习语义内容
  → 解码时自然恢复感知细节
```

## 两阶段架构

```
阶段一：感知压缩（Perceptual Compression）
  编码器 E: x ∈ R^{H×W×3} → z ∈ R^{h×w×c}  (h=H/f)
  解码器 D: z → x̃ ≈ x

  正则化：KL-reg（轻量 KL 散度）或 VQ-reg（向量量化）
  训练：重建损失 + 对抗损失 + 感知损失

阶段二：潜空间扩散（Latent Diffusion）
  在 z 空间训练标准扩散模型（UNet 骨架）

  训练目标：
  L = E_{z~E(x), ε~N(0,I), t}[||ε - ε_θ(z_t, t, τ_θ(y)))||²]
```

## 关键技术：交叉注意力条件机制

```
条件信号 y（文本/类别/布局）
  → 领域编码器 τ_θ(y)（如 BERT → Transformer）
  → 中间表示 τ_θ(y) ∈ R^{M×d_τ}
  
UNet 特征 φ_i(z_t) ∈ R^{h×w×d}
  → W_Q^(i) · φ_i → Q（Query）
  → W_K^(i) · τ_θ(y) → K（Key）
  → W_V^(i) · τ_θ(y) → V（Value）

Attention = softmax(QK^T/√d) · V
```

关键优势：同一机制处理任意模态条件，无需针对每种模态设计专用注入方式。

## 条件生成配置

| 任务 | 条件模态 | 编码器 τ_θ | 下采样因子 |
|------|---------|-----------|-----------|
| 文生图 | 文本 | BERT + Transformer | f=8 |
| 类别条件 | 类别标签 | 可学习嵌入 | f=4 |
| 布局生图 | 语义布局 | 空间 concatenation | f=8 |
| 图像修复 | 原始图像 | concatenation | f=4 |

## 与其他概念的关系

```
DDPM（像素空间扩散）
    │
    │ + 感知压缩（VQ-VAE/VQ-GAN）
    ↓
LDM（潜空间扩散） ← CLIP 文本编码器
    │
    ├── DiT（Transformer 替换 UNet 骨架）
    │    └── Sora（视频生成）
    │
    ├── ControlNet（精确空间控制）
    │
    └── Stable Diffusion（开源民主化）
         ├── SDXL（更大规模）
         └── 无数下游应用（LoRA、ControlNet 等）
```

## 训练效率对比

| 方法 | 参数量 | 生成质量 | 训练/推理效率 |
|------|--------|---------|-------------|
| ADM（像素空间） | 554M | SOTA | 低 / 慢 |
| **LDM-4** | 400M | 接近 SOTA | **高 / 快** |

f=4 配置：训练速度提升 ~3.5 倍，生成速度提升 ~35 倍（64× 下采样）。

## 来源

- Rombach et al., "High-Resolution Image Synthesis with Latent Diffusion Models", CVPR 2022
- 项目报告：`reports/paper_analyses/20_stable_diffusion_2021.md`
