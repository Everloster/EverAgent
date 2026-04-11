# Robin Rombach

> Latent Diffusion Models / Stable Diffusion 第一作者，LMU Munich & Runway ML

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Robin Rombach |
| 机构 | Ludwig Maximilian University of Munich (LMU) · IWR Heidelberg · Runway ML |
| 核心贡献 | Latent Diffusion Models (LDM) / Stable Diffusion |
| 代表作 | "High-Resolution Image Synthesis with Latent Diffusion Models" (CVPR 2022) |

## 学术脉络

```
LMU Munich / Heidelberg 出身
    └── Latent Diffusion Models (2021)
         ├── Stable Diffusion 开源（Stability AI 合作）
         │    → 成为开源社区最流行的文生图模型
         └── 后续：Stable Diffusion 2/3 / ControlNet 等衍生

关联：
  - Andreas Blattmann：LDM 合作作者
  - Patrick Esser：LDM 合作作者，Runway ML 联合创始人
```

## 在本项目中的关联

- 直接关联报告：`20_stable_diffusion_2021.md`
- 关联论文：DDPM (#09), CLIP (#12), DiT (#27)
- 概念关联：`latent_diffusion.md`

## 关键贡献

### Latent Diffusion Models (LDM)

将扩散过程从高维像素空间迁移到预训练自编码器的低维潜空间：
- 计算效率提升数十倍，使扩散模型在消费级 GPU 上运行成为可能
- 交叉注意力条件机制支持任意模态（文本、布局、语义图）条件生成
- 奠定了 Stable Diffusion 及后续开源生态的技术基础

### 开源影响

LDM 的开源代码 + Stability AI 的 LAION 数据训练 → Stable Diffusion
- 第一个公开可用的高质量文生图扩散模型
- 催生了 ComfyUI、ControlNet、LoRA 等庞大开源生态
- 成为开源生成式 AI 的里程碑事件
