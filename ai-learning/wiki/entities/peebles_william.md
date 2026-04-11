# William Peebles

> DiT (Scalable Diffusion Models with Transformers) 第一作者，NYU → OpenAI，Sora 核心贡献者

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | William Peebles |
| 机构 | New York University (NYU) · Meta AI (FAIR) → OpenAI |
| 核心贡献 | DiT — Transformer 骨架的扩散模型，Scaling Laws 验证 |
| 代表作 | "Scalable Diffusion Models with Transformers" (ICCV 2023) |

## 学术脉络

```
NYU 研究生
    └── 与 Saining Xie 合作发表 DiT (2022)
         │
         ├── 加入 OpenAI（DiT 后）
         │    └── 参与 Sora 开发
         │         → Sora = DiT 架构在视频生成上的直接扩展
         │
         └── DiT 开源（facebookresearch/DiT）
              → 催生大量 DiT 视频生成变体
```

## 核心贡献：DiT

### 主要创新

1. **Transformer 替换 U-Net**：首个纯 Transformer 骨架的扩散模型
2. **AdaLN-Zero**：zero-initialization 的自适应层归一化，训练稳定性显著优于其他 Conditioning 机制
3. **Scaling Laws**：证明 DiT 遵循 compute-law，是首个系统研究扩散模型 scaling 特性的工作
4. **采样效率**：DiT-XL/2 仅需 25-35 采样步达到 SOTA（对比 ADM 的 800 步）

### 技术成就

| 指标 | 成就 |
|------|------|
| FID (ImageNet 256) | 2.27（当时 SOTA） |
| 采样步数 | 25-35 步（vs ADM 800 步） |
| 模型规模 | DiT-XL/2 = 675M 参数 |

## 在本项目中的关联

- 直接关联报告：`27_dit_2022.md`
- 关联论文：ViT (#11), LDM (#20), Sora
- 概念关联：`diffusion_transformer.md`（DiT 核心概念）

## 与 Sora 的关系

William Peebles 加入 OpenAI 后，参与了 Sora 的开发：
- Sora 的技术基础是 DiT 架构在视频时空域的直接扩展
- 视频生成 = DiT 处理 3D patch（空间 + 时间）
- DiT 验证的 scaling laws 在 Sora 中得到大规模验证

## 合作者

- **Saining Xie**：DiT 共同作者，NYU 助理教授，Meta AI 背景
