---
id: overview-ai_learning
title: "ai-learning · 全局综述"
type: overview
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
status: active
---

# ai-learning · 全局综述

> 基于截至 2026-04-07 已读 26 篇精读论文 + 8 篇知识报告蒸馏。
> 每 10 篇新论文后更新一次。

---

## 一、领域骨架：四条主线

```
                    Transformer (2017)
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
   主线1: 架构        主线2: 规模        主线3: 对齐
   ─────────         ─────────         ─────────
   BERT (2018)       Scaling Laws      InstructGPT (2022)
   GPT-1/2/3         (Kaplan 2020)     RLHF / DPO / GRPO
   ViT (2020)        GPT-3 (175B)      Constitutional AI
   Swin (2021)       Chinchilla (2022) Tulu 3 (2024)
   FlashAttention    LLaMA / LLaMA-2
   MAE / DINOv2      MoE (Mixtral / DeepSeek-V3)
                          │
                    主线4: 系统工程
                    ─────────
                    KV Cache / GQA / MQA
                    PagedAttention (vLLM)
                    ZeRO / MegaScale
                    LoRA / QLoRA
```

参考的源报告分布：架构 11 篇、规模 3 篇、对齐 4 篇、系统工程 8 篇（含知识报告）。

---

## 二、关键技术拐点（按时间）

| 年份 | 事件 | 性质 |
|------|------|------|
| 2014 | Bahdanau Attention | 注意力机制前驱 |
| **2017** | **Transformer** | 架构革命，序列建模新范式 |
| 2017 | Sparsely-Gated MoE (Shazeer) | 稀疏激活的首次规模化验证 |
| 2018 | BERT / GPT-1 | 双向理解 vs 自回归生成两条路线 |
| **2020** | **GPT-3 + Scaling Laws** | "规模就是一切"成为业界共识 |
| 2020 | ViT | Transformer 跨域到图像 |
| 2021 | LoRA / Switch Transformer | 参数效率 + 万亿参数稀疏模型 |
| **2022** | **InstructGPT → ChatGPT** | RLHF 商业化，对齐成为主流 |
| 2022 | FlashAttention | 工程效率论文获得与架构论文同等地位 |
| 2022 | Chain-of-Thought | "推理"作为新 scaling 维度 |
| 2022 | MAE / Chinchilla | 视觉自监督 + 数据导向 scaling |
| 2023 | LLaMA / Mistral / DINOv2 | 开源生态崛起 |
| 2024 | Mixtral 8×7B / DeepSeek-V2/V3 | MoE 开源化主流化 |
| 2024 | OpenAI o1 | 推理时间 scaling 新维度 |

---

## 三、核心概念间的依赖关系

```
              attention_mechanism
                     │
             ┌───────┴────────┐
             │                │
   transformer_architecture   kv_cache
             │
   ┌─────────┼──────────┬──────────┐
   │         │          │          │
scaling   moe_arch   lora_peft   self_supervised
laws         │                    learning
             │
       sparse_activation
             │
        rlhf (后训练对齐)
```

每条边的意义：
- attention_mechanism → transformer：注意力是 Transformer 的核心算子
- transformer → kv_cache：KV Cache 是 Transformer 自回归推理的核心优化
- transformer → moe：MoE 替换 Transformer 的 FFN 层，Attention 保持 Dense
- transformer → lora：LoRA 主要注入 Transformer 注意力层的 Q/V 投影
- moe ↔ sparse_activation：MoE 是稀疏激活最成功的实现路径
- scaling_laws ↔ moe：MoE 通过总参≫激活参挑战 Dense Scaling Laws
- rlhf 依赖前述所有架构作为后训练底座

---

## 四、技术分歧与未决问题（截至 2026-04）

| 议题 | 主流立场 | 反方立场 |
|------|---------|---------|
| Dense vs MoE | 开源前沿模型大量转向 MoE（DeepSeek-V3 671B/37B） | Dense 仍是 Llama-3.1 405B 等的选择 |
| 数据 vs 参数 | Chinchilla 倒向数据 | 推理成本敏感场景仍偏好"小模型 + 长 context" |
| 涌现能力是否真实 | Wei et al. 2022 证据派 | Schaeffer et al. 2023 评估指标派 |
| LLM 是否通往 AGI | Hinton/Bengio 谨慎；商业派乐观 | LeCun 反对，倡导 World Model |
| RLHF 是否被替代 | DPO 在开源社区已成主流，简化 PPO | PPO 仍是 OpenAI 旗舰流程 |
| 自监督视觉的最佳任务 | MAE / DINO 路线并存 | 尚无共识 |

---

## 五、当前 wiki 的概念覆盖度

| 已建 concept 页面 | 状态 |
|------------------|------|
| attention_mechanism | active |
| transformer_architecture | active |
| scaling_laws | active |
| rlhf | active |
| lora_peft | active |
| moe_architecture | active |
| kv_cache | active |
| self_supervised_learning | active |
| sparse_activation | active |

**已建 entity 页面**：12 个（hinton / lecun / bengio / vaswani / shazeer / wei_jason / brown_tom / schulman_john / dao_tri / openai / google_brain_deepmind / meta_ai）

**plan §8 短期成功标准**：
- [x] ai-learning wiki/ 有 ≥ 10 个 entity 页面、≥ 8 个 concept 页面
- [ ] 每次新摄入后 log.md 有记录（待新摄入触发）
- [ ] 一篇新论文摄入后，能通过 wiki/ 而不是 reports/ 回答 "这个概念是什么" 的问题（待验证）

---

## 六、缺失的概念页面（建议下一次摄入触发时补建）

| 概念 | 触发条件 |
|------|---------|
| diffusion_models | 已有 09_ddpm_2020 + 08_gan_2014，可独立蒸馏 |
| in_context_learning | 已有 03_gpt3_2020 主要内容，但与 attention_mechanism 有部分重合 |
| chain_of_thought | 已有 10_chain_of_thought_2022 |
| emergent_abilities | 已有 03_gpt3_2020 / 05_scaling_laws_2020 中的引用 |
| residual_connection | 已有 07_resnet_2015 |
| zero_optimizer | 已有 25_zero_2019 |
| megascale_distributed_training | 已有 31_megascale_2024 |
| word_embeddings | 已有 13_word2vec_2013 |
| contrastive_learning | 已有 12_clip_2021 / 35_dinov2_2023 |

---

> 操作日志 → [log.md](./log.md)
> 索引 → [index.md](./index.md)
> 原始报告 → [reports/](../reports/)
