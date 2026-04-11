# Diffusion Transformer（扩散 Transformer）

> DiT：用 Transformer 架构替代 U-Net 作为扩散模型的骨架，验证 scaling laws

## 一句话定义

Diffusion Transformer (DiT) 是首个用纯 Transformer 骨架替代传统 U-Net 的扩散模型，通过 AdaLN-Zero 条件机制和系统性 scaling 实验，证明了扩散模型遵循与语言模型相同的 compute-law，成为 Sora 等视频生成模型的技术基础。

## 核心设计

### Patchify（从 ViT 继承）

```
输入：潜空间图像 z ∈ R^{h×w×c}（来自 VAE，c=4）

Patchify：
  将图像分割为 2×2×c 的 patches
  每个 patch → 4c 维向量
  序列长度 = (h/2)×(w/2)

  例：256×256 原图（VAE f=8）→ 潜空间 32×32
  → 16×16 = 256 个 patches
  → 与 ViT-B/16 相同序列长度
```

### AdaLN-Zero（核心创新）

```
标准 AdaLN：γ(c), β(c) = linear(c)

AdaLN-Zero：
  1. γ, β 初始化为 0 → LayerNorm = identity
  2. MLP 输出乘以 0 → 零贡献
  3. 残差连接保持原始信号

效果：训练初期 = 无条件 DiT，渐进引入条件信号
      训练稳定性显著提升
```

### DiT Block 流程

```
Input: x ∈ R^{B×N×D}
  ↓
LayerNorm
  ↓
├── Self-Attention (Multi-Head)
├── 残差 + LayerNorm
├── AdaLN 调制 (γ, β)
├── MLP (GELU)
├── 残差
  ↓
Output
```

## Scaling 配置

| 配置 | 参数量 | Gflops | 深度 | 宽度 |
|------|--------|--------|------|------|
| DiT-S | 39M | 167G | 12 | 384 |
| DiT-B | 345M | 1185G | 12 | 768 |
| DiT-L | 657M | 2291G | 24 | 1024 |
| DiT-XL | 675M | 2519G | 28 | 1234 |

## 与其他概念的关系

```
ViT (Vision Transformer)
    │
    │ Patchify + Transformer 架构
    ↓
DiT (Diffusion Transformer)
    │
    ├── 视频生成：DiT → W.A.L.T → Sora
    │
    ├── 图片生成：DiT-XL/2 → FID 2.27 SOTA
    │
    └── Scaling Laws：
         DiT scaling 曲线 ≈ 语言模型 scaling 曲线
         → 扩散模型 scaling 可预测
```

## 为什么优于 U-Net？

| 特性 | U-Net (DDPM/ADM/LDM) | DiT (Transformer) |
|------|---------------------|-------------------|
| 架构来源 | CNN (pixel-level) | Transformer (sequence-level) |
| Scaling 特性 | 规模大时饱和 | 未饱和，线性改善 |
| 全局感受野 | 受限（多尺度） | 天然全局 |
| 训练技巧 | 特定 | 复用 LLM tricks |
| 硬件效率 | 成熟 | FlashAttention 可用 |
| 采样步数 | 50-1000 步 | 25-35 步（XL/2） |

## 关键结论

1. **Scaling Laws 成立**：DiT 是首个系统验证扩散模型 scaling 特性的工作
2. **Transformer > U-Net**：当 compute 足够大时，Transformer 全面超越 U-Net
3. **AdaLN-Zero 是关键**：正确的条件机制选择比架构细节更重要
4. **Sora 的技术基础**：William Peebles 加入 OpenAI 后，DiT 直接演化为 Sora

## 来源

- Peebles & Xie, "Scalable Diffusion Models with Transformers", ICCV 2023
- 项目报告：`reports/paper_analyses/27_dit_2022.md`
