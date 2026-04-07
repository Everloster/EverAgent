# ai-learning · Wiki Index

> LLM 维护的知识百科入口。每次摄入新论文后更新。
> 查询时优先读此文件定位相关页面，再深入阅读。

---

## Overview

| 页面 | 简介 |
|------|------|
| [overview.md](./overview.md) | ai-learning 全局综述：四条主线、技术拐点、概念依赖图 |

---

## Entities（人物 / 机构）

### 人物
| 页面 | 简介 |
|------|------|
| [hinton_geoffrey.md](./entities/hinton_geoffrey.md) | 深度学习三巨头之一，AlexNet 导师，2023 年警示 AI 风险 |
| [lecun_yann.md](./entities/lecun_yann.md) | CNN/LeNet 发明者，Meta AI 首席科学家，倡导 World Model |
| [bengio_yoshua.md](./entities/bengio_yoshua.md) | 序列建模先驱，Mila 创立者，AI 安全立场积极发声 |
| [vaswani_ashish.md](./entities/vaswani_ashish.md) | Transformer 第一作者，含 8 位作者后续去向 |
| [shazeer_noam.md](./entities/shazeer_noam.md) | Transformer 与 MoE 双线作者，Character.AI 创始人 |
| [wei_jason.md](./entities/wei_jason.md) | Chain-of-Thought 与 Emergent Abilities 提出者 |
| [brown_tom.md](./entities/brown_tom.md) | GPT-3 第一作者，Anthropic 联合创始团队成员 |
| [schulman_john.md](./entities/schulman_john.md) | PPO 提出者，InstructGPT/ChatGPT 后训练核心 |
| [dao_tri.md](./entities/dao_tri.md) | FlashAttention 第一作者 |

### 机构
| 页面 | 简介 |
|------|------|
| [openai.md](./entities/openai.md) | GPT 系列、InstructGPT、ChatGPT 系列发起方 |
| [google_brain_deepmind.md](./entities/google_brain_deepmind.md) | Google Brain × DeepMind 2023 合并，AlphaFold/Gemini |
| [meta_ai.md](./entities/meta_ai.md) | FAIR / LLaMA / MAE / DINOv2 / VideoMAE 大本营 |

---

## Concepts（核心概念）

| 页面 | 简介 |
|------|------|
| [attention_mechanism.md](./concepts/attention_mechanism.md) | 序列内任意位置的动态加权聚合机制 |
| [transformer_architecture.md](./concepts/transformer_architecture.md) | 完全基于自注意力的编码器-解码器，现代 LLM 底座 |
| [scaling_laws.md](./concepts/scaling_laws.md) | N/D/C 三大幂律，Kaplan vs Chinchilla 之争 |
| [rlhf.md](./concepts/rlhf.md) | SFT → RM → PPO 三阶段对齐流程，DPO/GRPO 替代 |
| [lora_peft.md](./concepts/lora_peft.md) | 低秩适应，0.01%~1% 参数实现接近全量微调 |
| [moe_architecture.md](./concepts/moe_architecture.md) | 稀疏门控混合专家，参数量×n 而计算量基本不变 |
| [kv_cache.md](./concepts/kv_cache.md) | Transformer 自回归推理 K/V 缓存，O(t²) → O(t) |
| [self_supervised_learning.md](./concepts/self_supervised_learning.md) | 三大范式：遮蔽重建 / 自回归 / 对比自蒸馏 |
| [sparse_activation.md](./concepts/sparse_activation.md) | 条件计算的设计哲学，MoE 是其最成功的实现 |

---

## Syntheses（合成分析 / 问答归档）

| 页面 | 简介 |
|------|------|
| [moe_vs_dense_inference_cost.md](./syntheses/moe_vs_dense_inference_cost.md) | MoE vs Dense 推理成本与参数效率本质区别，DeepSeek-V3 671B/37B 配比解析 |

---

> 操作日志 → [log.md](./log.md)
> 全局综述 → [overview.md](./overview.md)
> 原始报告 → [reports/](../reports/)
> 原始论文 → [papers/](../papers/)
