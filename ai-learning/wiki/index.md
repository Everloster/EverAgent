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
| [radford_alec.md](./entities/radford_alec.md) | GPT-1/2、CLIP、Whisper 核心作者，OpenAI 早期研究员 |
| [sutton_rich.md](./entities/sutton_rich.md) | 强化学习奠基人，The Bitter Lesson 作者，Alberta/DeepMind |
| [rombach_robin.md](./entities/rombach_robin.md) | LDM / Stable Diffusion 第一作者，LMU Munich & Runway ML |
| [peebles_william.md](./entities/peebles_william.md) | DiT 第一作者，NYU→OpenAI，Sora 核心贡献者 |
| [xie_saining.md](./entities/xie_saining.md) | DiT 共同作者，NYU 助理教授 |
| [yao_shunyu.md](./entities/yao_shunyu.md) | ReAct 第一作者，00后代表，SWE-bench 作者，Princeton→Meta AI |
| [schuhmann_christoph.md](./entities/schuhmann_christoph.md) | LAION 创始人，LAION-5B 项目负责人 |
| [penedo_guilherme.md](./entities/penedo_guilherme.md) | RefinedWeb 第一作者，TII，Falkon LLM 核心贡献者 |
| [tii.md](./entities/tii.md) | 阿联酋技术创新研究院，Falkon LLM 与 RefinedWeb 诞生地 |
| [wu_yonghui.md](./entities/wu_yonghui.md) | GNMT 第一作者，Google Brain，深层残差 LSTM + WordPiece |
| [karpathy_andrej.md](./entities/karpathy_andrej.md) | Deep Video 第一作者，Stanford→Tesla，CS231n 讲师 |

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
| [agent_systems.md](./concepts/agent_systems.md) | ReAct Loop · Tool Use · Function Calling · MCP 协议 · Multi-Agent 协作 |
| [test_time_compute.md](./concepts/test_time_compute.md) | 推理时计算扩展，o1/o3 · DeepSeek-R1 · GRPO · PRM · MCTS，与 training-time scaling 互补 |
| [rag.md](./concepts/rag.md) | 检索增强生成，Naive → Advanced → Modular RAG 演进，GraphRAG · Self-RAG · Reranker |
| [in_context_learning.md](./concepts/in_context_learning.md) | 通过 prompt demonstrations 无梯度学习，Bayesian / Task Recognition / Knowledge Activation 三派理论 |
| [pretraining_finetuning.md](./concepts/pretraining_finetuning.md) | 预训练-微调两阶段范式，GPT-1 确立，BERT 巅峰，LoRA/ICL 演化 |
| [bitter_lesson.md](./concepts/bitter_lesson.md) | 苦涩教训：通用计算方法长期总赢，搜索与学习可无限扩展 |
| [latent_diffusion.md](./concepts/latent_diffusion.md) | 潜空间扩散：两阶段感知压缩+语义生成，交叉注意力条件机制 |
| [diffusion_transformer.md](./concepts/diffusion_transformer.md) | DiT：Transformer 替换 U-Net，AdaLN-Zero，Scaling Laws 验证 |
| [large_scale_data_filtering.md](./concepts/large_scale_data_filtering.md) | billion级数据多级过滤：URL去重/CLIP评分/progressive质量过滤 |
| [toa_paradigm.md](./concepts/toa_paradigm.md) | ToA 范式：产品第一用户从人类转为 Agent；CLI 原生论；硅碳加速剪刀差 |
| [bidirectional_domestication.md](./concepts/bidirectional_domestication.md) | 双向驯化：硅基对碳基的四种认知侵蚀；多Agent涌现的四种类型与Alignment升维 |
| [toa_system_design.md](./concepts/toa_system_design.md) | ToA系统设计模式：双入口文档·自包含Subagent·审计链·质量回顾缺失等工程洞察 |
| [toc_as_data_infrastructure.md](./concepts/toc_as_data_infrastructure.md) | ToC ChatBot 的真实战略价值：人类偏好数据采集器·数据飞轮·防 Model Collapse |
| [opensource_vs_closedsource_toa.md](./concepts/opensource_vs_closedsource_toa.md) | ToA 世界开源 vs 闭源重新博弈：CLI 生态利好开源·数据飞轮利好闭源·三种终局场景 |
| [generative_models_evolution.md](./concepts/generative_models_evolution.md) | 生成模型四代演化：GAN对抗博弈→DDPM扩散去噪→LDM潜空间→DiT Transformer骨干·Flow Matching前沿 |
| [eva02_vision_transformer.md](./concepts/eva02_vision_transformer.md) | EVA-02：SwiGLU+2D RoPE+sub-LN+CLIP MIM，LLM架构迁移至视觉的里程碑，304M参数达90.0% IN-1K |

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
