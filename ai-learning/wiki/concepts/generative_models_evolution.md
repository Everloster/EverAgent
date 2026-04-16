---
name: generative_models_evolution
description: 生成模型四代演化：GAN→DDPM→LDM→DiT，包含核心机制、设计权衡与Flow Matching前沿方向
type: concept
updated_on: 2026-04-16
---

# 生成模型演化（Generative Models Evolution）

## 一句话定义

生成模型经历"对抗博弈（GAN）→ 马尔科夫链去噪（DDPM）→ 潜空间扩散（LDM）→ Transformer骨干（DiT）"四次范式跳跃，每次跳跃都针对上一代的核心缺陷提供更稳定、更可扩展的解法。

## 四代演化速览

| 模型 | 年份 | 解决的上一代问题 | 引入的新问题 |
|------|------|-----------------|------------|
| GAN | 2014 | 无需MCMC，快速单步采样 | 模式崩溃、训练不稳定 |
| DDPM | 2020 | 训练稳定，FID优于GAN | 像素空间计算昂贵，采样慢 |
| LDM (SD) | 2021 | 潜空间节省50×计算，文本条件 | U-Net骨干Scaling受限 |
| DiT | 2022 | Transformer骨干验证Scaling Laws | 步数多（Flow Matching缓解） |

## 核心公式

**DDPM损失（预测噪声ε）**：
$$L_{simple} = \mathbb{E}_{t,x_0,\epsilon}\left[\|\epsilon - \epsilon_\theta(\sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon, t)\|^2\right]$$

**LDM潜空间编码**：$z = E(x)$，在 $z$ 上运行扩散，解码 $\hat{x} = D(z)$

**DiT AdaLN-Zero**：$x = \text{LayerNorm}(x) \cdot (1 + \gamma_c) + \beta_c$，其中 $[\gamma_c, \beta_c] = \text{MLP}(c)$

## 演化脉络

```
GAN (2014) → BigGAN / StyleGAN → [训练不稳定封顶]
              ↓
DDPM (2020) → [像素空间太贵]
              ↓
LDM/SD (2021) → ControlNet / SDXL / IP-Adapter → [U-Net骨干限制Scaling]
              ↓
DiT (2022) → SD3 / Flux.1 / Sora (Video DiT)
              ↓
Flow Matching (2022+) → 一步/少步高质量采样
```

## 与其他概念的关系

- **[[attention_mechanism]]**：DiT的Self-Attention是核心模块
- **[[scaling_laws]]**：DiT实验验证生成模型也满足幂律Scaling
- **[[latent_diffusion]]**：LDM的详细机制（感知压缩+交叉注意力）
- **[[diffusion_transformer]]**：DiT的详细架构（AdaLN-Zero, patchify）
- **[[large_scale_data_filtering]]**：LAION-5B是Stable Diffusion的数据来源
- **[[self_supervised_learning]]**：DDPM的预测噪声ε目标类似自监督的去噪代理任务

## 当前前沿（2026年初）

- **Flow Matching**：直线ODE路径取代DDPM曲线路径，SD3/Flux.1已采用
- **Consistency Models**：蒸馏扩散模型为1步生成
- **Video DiT**：Sora / Wan2.1 将时空patch化，视频生成成为DiT主战场
- **多模态统一**：DiT骨干+流匹配+CLIP文本编码正在成为新一代图像/视频生成标准架构

## 被引用于

- 报告：`reports/knowledge_reports/生成模型演化全景_GAN_DDPM_LDM_DiT_20260416.md`
- 源论文：`08_gan_2014` / `09_ddpm_2020` / `20_stable_diffusion_2021` / `27_dit_2022`

## 开放问题

1. Flow Matching是否会完全取代DDPM？LCM/Consistency Models是否能达到Flow Matching的质量上限？
2. DiT的最优patch size（$p=2$）是否有理论解释，还是纯实验结论？
3. 扩散模型的训练数据版权问题（LAION-5B诉讼）如何影响未来数据工程？
