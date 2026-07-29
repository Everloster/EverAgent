---
name: kimi-k3-tech-report
description: "Kimi K3 技术报告（Moonshot AI，2.8T MoE 开放前沿模型）蒸馏而成的可查询 skill。按需加载章节回答 K3 架构（KDA/AttnRes/Stable LatentMoE）、预训练、后训练/RL、基础设施、评估等问题。由 book-to-skill 从官方 47 页技术报告 distill。"
---

# Kimi K3 技术报告 · Skill

> 由 [book-to-skill](https://github.com/virgiliojr94/book-to-skill) 从官方 `k3_tech_report.pdf`（47 页，docling technical 模式抽取，38K token）蒸馏。**提取结构，非摘要。**
> 用法：问"KDA 怎么工作 / Stable LatentMoE 怎么均衡负载 / K3 benchmark 强在哪" → 按需读对应 `chapters/` 文件，从真实内容作答，不幻觉。

## 一句话心智模型

K3 = **一座 2.8 万亿参数的"城市"，沿三个方向疏通信息流**，从而敢把开源模型做到 3T 级：
- **序列长度（长街）** → Kimi Delta Attention（线性注意力+遗忘门）+ Gated MLA，3:1 混合
- **网络深度（高楼）** → Attention Residuals：把注意力从"时间维"搬到"深度维"，每层按需取任意前层
- **模型宽度（路口）** → Stable LatentMoE：896 选 16 极端稀疏 + SiTU-GLU + Quantile Balancing

核心指标：2.8T 总参 / 104B 激活 / 93 层 / 896 专家选 16 / 100 万 token 上下文 / 原生多模态。较 K2 整体扩展效率 **≈2.5×**。定位：**开源新王，长程 agentic 强，纯推理仍逊于 Claude Fable 5 / GPT-5.6 Sol**。

## 章节索引（按需加载）

| 主题 | 文件 | 关键内容 |
|------|------|---------|
| **KDA + 混合注意力** | `chapters/ch02-architecture-kda.md` | delta-rule 递归、通道遗忘门、有下界 sigmoid decay、Gated MLA+NoPE |
| **AttnRes 注意力残差** | `chapters/ch02-attnres.md` | 伪 query 选层、Block AttnRes 分 8 块降开销 |
| **Stable LatentMoE** | `chapters/ch02-latentmoe.md` | 潜空间路由、SiTU-GLU 软天花板、Quantile Balancing 负载均衡 |
| **预训练/Scaling** | `chapters/ch03-pretraining.md` | 数据、scaling law、长上下文扩展 |
| **后训练/RL** | `chapters/ch04-posttraining.md` | 多档推理 RL、多教师蒸馏、agentic 环境合成 |
| **基础设施** | `chapters/ch05-infra.md` | KDA 算法-系统协同、MoonEP 专家并行、百万 token agentic RL |
| **评估** | `chapters/ch06-evaluation.md` | benchmark 全表 + 强弱项诚实解读 |

> 本 demo 只精蒸了最硬核的**架构三章 + 评估章**作为质量样本（`ch02-*` + 关键速查）；其余章节索引已列，按需可续蒸。

## 速查（决策/事实级）

- **KDA vs MLA 分工**：KDA 管高效长序列+位置感；MLA 管全局内容交互，用 NoPE（位置全交给 KDA）。3:1，末层必为 MLA。
- **K3 相对 Kimi Linear 的关键改进**：log-decay 从无界 negative-Softplus 换成**有下界 scaled-sigmoid（gmin=−5）** → 对角 tile 也能用 Tensor Core 稠密矩阵乘，消掉慢速位置对计算。
- **极端稀疏的三个翻车点 & 解法**：①通信爆→潜空间路由；②激活爆→RMSNorm+SiTU-GLU 软天花板（β1=4/β2=25）；③负载不均→Quantile Balancing（分位数定偏置，只影响分流不影响计费）。
- **强项**：SWE-Marathon 42.0(第一)、BrowseComp 91.2(第一)、MCPMark 94.5(第一)、FrontierSWE 81.2。**弱项**：HLE-Full 43.5（明显落后 Fable 5 的 53.3）。

## 术语表

见 `glossary.md`（KDA / AttnRes / LatentMoE / SiTU-GLU / Quantile Balancing / Gated MLA / NoPE / MoonViT-V2 / Per-Head Muon 等）。
