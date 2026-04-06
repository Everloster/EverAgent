# ai-learning — Project Context

> **Agent 协议**：操作本项目前须读取 [AGENTS.md](./AGENTS.md)（NeuronAgent 自包含协议）。执行完成后按协议 §5 提交推送。

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
- `14_swin_transformer_2021` — 层次化视觉Transformer·移位窗口注意力·线性复杂度·多尺度特征图·ICCV2021最佳论文·统一分类检测分割（2026-03-26）
- `17_mae_2022` — 掩码自编码器·75%高遮蔽率·不对称编解码器·像素重建·ImageNet ViT-H 86.9%·COCO检测超监督预训练·生成式自监督视觉范式（2026-03-26）
- `33_mistral_7b_2023` — 小参数高性能开源LLM·GQA+SWA架构·7B级别推理效率与质量平衡里程碑（2026-03-26）
- `18_flashattention_2022` — IO-aware精确Attention·在线Softmax·显存占用显著下降·长上下文训练提速关键内核（2026-03-26）
- `34_llama2_2023` — 开源基础模型+Chat模型双路线·70B级别开放对话模型·安全微调进入开源主舞台（2026-03-26）
- `13_word2vec_2013` — CBOW与Skip-gram·层次化Softmax·负采样·词嵌入民主化·2023 NeurIPS时间检验奖（2026-03-28）
- `35_dinov2_2023` — 自监督视觉基础模型·LVD-142M数据流水线·KoLeo正则化·蒸馏传承·全视觉任务通用特征（2026-03-28）
- `36_videomae_2022` — 视频MAE·极高掩码率90-95%·Tube Masking·数据高效自监督预训练·K400 87.4%（2026-04-04）
- `31_megascale_2024` — 万卡级LLM训练系统·12,288 GPU 55.2% MFU·3D并行Overlap·算法-系统协同设计·自动化故障恢复·NSDI 2024（2026-04-04）
- `21_moe_2017` — 稀疏门控混合专家·Noisy Top-K Gating·负载均衡双损失·137B参数验证·GPT-4/Mixtral直接前驱（2026-03-31）
- `25_zero_2019` — ZeRO内存优化·优化器状态/梯度/参数三级切分·DeepSpeed核心·万亿参数训练基础设施（2026-03-30）

**知识深度解析** (`reports/knowledge_reports/`)
- `self_attention_深度解析` — 含代码实现
- `RLHF_深度解析` — PPO/DPO 对比
- `AI关键人物图谱` — Transformer 作者去向·OpenAI 分裂史
- `Scaling_Laws_深度解析` — Kaplan 2020 幂律关系·Chinchilla 修正·涌现能力（2026-03-25）
- `LoRA_深度解析` — 低秩适应原理·QLoRA·DoRA变体·代码实现·多任务部署（2026-03-25）
- `KV_Cache_深度解析_20260330` — 键值缓存原理·GQA/MQA变体·PagedAttention·显存计算·PyTorch代码实现·SnapKV等前沿压缩方案（2026-03-30）
- `MoE_混合专家_深度解析_20260406` — MoE条件计算·Noisy Top-K Gating·负载均衡双损失·Switch/Mixtral/DeepSeek变体全景·PyTorch实现·Scaling关系（2026-04-06）

## 离线知识库
→ [`knowledge/INDEX.md`](./knowledge/INDEX.md)（子话题菜单，离线模型从此进入）

## Skills
- `skills/paper_analysis/SKILL.md` — 论文 7 步分析法
- `skills/concept_deep_dive/SKILL.md` — 概念 5 层理解模型

## 导航
- 学习路径：`roadmap/Learning_Roadmap.md`
- 论文索引：`papers/PAPERS_INDEX.md`（34 篇，含 PDF）

## ⚠️ 边界（防幻觉）
以下内容**尚未研究**，禁止推测，须告知用户：
- GPT-4 / Claude / Gemini 系列的专项分析报告
- 工程类论文精读（EVA-02 等后续工程论文）
- Phase 2 尚缺：DDIM 等后续扩散论文；VGGNet、Batch Normalization 专项报告
- 下一步推荐：EVA-02、Megatron-LM 深度分析
