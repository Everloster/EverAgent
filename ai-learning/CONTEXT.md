# ai-learning — Project Context

**领域**：人工智能技术·论文精读·技术深度报告
**三维度**：技术深度 × 历史叙事 × 工程实践

## 已有报告
**论文精读** (`reports/paper_analyses/`)
- `01_transformer_2017` — Attention Is All You Need，Self-Attention 机制奠基
- `02_bert_2018` — 双向预训练语言模型
- `03_gpt3_2020` — 大规模语言模型与 Few-shot 能力
- `04_instructgpt_2022` — RLHF三阶段训练·ChatGPT前身·对齐税（2026-03-25）
- `07_resnet_2015` — 残差连接·退化问题解决·深度视觉里程碑·催生Transformer残差（2026-03-25）
- `08_gan_2014` — 生成对抗网络·博弈框架·无需MCMC·JS散度最小化·开创生成模型新范式（2026-03-25）
- `09_ddpm_2020` — 扩散生成模型·前向加噪·反向去噪·预测噪声ε·FID 3.17超越GAN·Stable Diffusion基石（2026-03-26）
- `06_alexnet_2012` — 深度CNN·GPU训练·ReLU激活·Dropout正则化·ILSVRC 2012碾压传统方法·深度学习复兴拐点（2026-03-26）
- `11_vit_2020` — Vision Transformer·16×16 Patch·纯注意力图像分类·无归纳偏置·大数据超越CNN·多模态统一架构基础（2026-03-26）
- `12_clip_2021` — 文本-图像对比学习·WIT-400M·零样本图像分类·双编码器·Prompt Engineering·DALL·E/SD/GPT-4V基础设施（2026-03-26）
- `05_scaling_laws_2020` — 幂律三变量·计算最优配置·Chinchilla对比
- `10_chain_of_thought_2022` — CoT Prompting·思维链激活推理·涌现现象（2026-03-25）
- `15_lora_2021` — 低秩分解微调·零推理开销·0.01%参数·PEFT运动奠基（2026-03-26）
- `26_tulu3_2024` — SFT→DPO→RLVR 后训练完整流程
- `16_llama_2023` — 开源大模型·推理最优策略·7B超越GPT-3·Pre-Norm+SwiGLU+RoPE·开源生态Linux时刻（2026-03-26）
- `13_swin_transformer_2021` — 层次化视觉Transformer·移位窗口注意力·线性复杂度·多尺度特征图·ICCV2021最佳论文·统一分类检测分割（2026-03-26）

**知识深度解析** (`reports/knowledge_reports/`)
- `self_attention_深度解析` — 含代码实现
- `RLHF_深度解析` — PPO/DPO 对比
- `AI关键人物图谱` — Transformer 作者去向·OpenAI 分裂史
- `Scaling_Laws_深度解析` — Kaplan 2020 幂律关系·Chinchilla 修正·涌现能力（2026-03-25）
- `LoRA_深度解析` — 低秩适应原理·QLoRA·DoRA变体·代码实现·多任务部署（2026-03-25）

## 离线知识库
→ [`knowledge/INDEX.md`](./knowledge/INDEX.md)（子话题菜单，离线模型从此进入）

## Skills
- `skills/paper_analysis/SKILL.md` — 论文 7 步分析法
- `skills/concept_deep_dive/SKILL.md` — 概念 5 层理解模型

## 导航
- 学习路径：`roadmap/Learning_Roadmap.md`
- 论文索引：`papers/PAPERS_INDEX.md`（32 篇，含 PDF）

## ⚠️ 边界（防幻觉）
以下内容**尚未研究**，禁止推测，须告知用户：
- GPT-4 / Claude / Gemini 系列的专项分析报告
- 工程类报告（FlashAttention、KV Cache、ZeRO 等尚无独立精读）
- InstructGPT / PPO 的论文级精读 ✅ 已完成（04_instructgpt_2022）
- Scaling Laws 论文（Kaplan 2020）精读级分析 ✅ 已完成（05_scaling_laws_2020）
- LoRA 论文级精读 ✅ 已完成（15_lora_2021）
- 工程类论文精读（FlashAttention #18、ZeRO #25、MegaScale #31 等）
- ResNet (#07) ✅ 已完成（07_resnet_2015）
- GAN (#08) ✅ 已完成（08_gan_2014）
- DDPM (#09) ✅ 已完成（09_ddpm_2020）
- AlexNet (#06) ✅ 已完成（06_alexnet_2012，基于论文知识分析）
- Phase 2 尚缺：DDIM等后续扩散论文；VGGNet、Batch Normalization专项报告
- ViT (#11) ✅ 已完成（11_vit_2020）
- CLIP (#12) ✅ 已完成（12_clip_2021）
- LLaMA (#16) ✅ 已完成（16_llama_2023）
- Swin Transformer (#13) ✅ 已完成（13_swin_transformer_2021）
- 下一步推荐：MAE（掩码自编码器）、LLaMA 2、Mistral 7B、DINO v2
