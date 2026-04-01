# 🤖 AI Learning Project

> 系统学习人工智能的个人知识库与学习项目
> 创建日期：2026-03-23 | 最后更新：2026-03-26（任务板校正 + 协作分发优化）

---

## 项目目标

建立一套完整的 AI 自学体系，覆盖近20年 AI 发展史、核心技术原理、关键论文精读，并持续积累深度分析报告。
项目的三个维度：**技术深度**（论文精读）× **历史叙事**（人物图谱、硬件彩票）× **工程实践**（Infra与数据）。

---

## 📁 完整目录结构

```
ai-learning/
│
├── README.md                                    # 本文件，项目总览与导航
│
├── roadmap/                                     # 📍 学习路径规划
│   ├── AI_Development_Timeline.md              # 近20年AI发展时间线 + 硬件彩票分析
│   └── Learning_Roadmap.md                     # 系统学习路径（Phase 1-4 + Infra模块）
│
├── papers/                                      # 📄 关键论文（30篇 PDF 已下载）
│   ├── PAPERS_INDEX.md                         # 32篇论文索引（含 Arxiv 链接）
│   ├── download_papers.html                    # Chrome 辅助下载页面
│   ├── 01_attention_is_all_you_need_2017.pdf
│   ├── 02_bert_2018.pdf
│   ├── 03_gpt3_2020.pdf
│   ├── 04_instructgpt_rlhf_2022.pdf
│   ├── 05_scaling_laws_2020.pdf
│   ├── 07_resnet_2015.pdf
│   ├── 08_gan_2014.pdf
│   ├── 09_ddpm_2020.pdf
│   ├── 10_chain_of_thought_2022.pdf
│   ├── 11_clip_2021.pdf
│   ├── 12_llama_2023.pdf
│   ├── 13_word2vec_2013.pdf
│   ├── 14_bahdanau_attention_2014.pdf
│   ├── 15_lora_2021.pdf
│   ├── 16_rag_2020.pdf
│   ├── 17_react_2022.pdf
│   ├── 18_flashattention_2022.pdf
│   ├── 19_vit_2020.pdf
│   ├── 20_stable_diffusion_2021.pdf
│   ├── 21_moe_2017.pdf
│   ├── 23_distilling_2015.pdf
│   ├── 24_alphago_zero_2017.pdf
│   ├── 25_zero_2019.pdf
│   ├── 26_tulu3_2024.pdf
│   ├── 27_dit_2022.pdf
│   ├── 28_brook_2004.pdf
│   ├── 29_laion5b_2022.pdf
│   ├── 30_refinedweb_2023.pdf
│   ├── 31_megascale_2024.pdf
│   └── 32_diffusion_original_2015.pdf
│   ⚠️  注：06_alexnet（NeurIPS付费）、22_bitter_lesson（博客，非PDF）需手动获取
│
├── skills/                                      # 🛠️ 学习技能模板
│   ├── paper_analysis/
│   │   └── SKILL.md                            # 论文深度分析技能（7步分析法）
│   └── concept_deep_dive/
│       └── SKILL.md                            # AI 知识深挖技能（5层理解模型）
│
├── reports/                                     # 📊 分析报告
│   ├── AI演义_笔记分析与项目整合报告.md          # 《AI演义》PDF 解析与项目改进建议
│   ├── paper_analyses/                         # 论文精读报告（24 篇已完成）
│   │   ├── 01_transformer_2017.md
│   │   ├── 04_instructgpt_2022.md
│   │   ├── 12_clip_2021.md
│   │   └── 26_tulu3_2024.md
│   └── knowledge_reports/                      # 概念深度解析（7 篇）
│       ├── self_attention_深度解析.md
│       ├── RLHF_深度解析.md
│       └── AI关键人物图谱.md
│
└── notes/                                       # 📝 个人学习笔记与参考资料
    └── 终版：AI演义，36篇论文开启你的探索之旅.pdf  # 参考PDF（已分析）
```

---

## 🚀 快速开始

### 第一步：建立全局视野（推荐首先阅读）

| 文档 | 内容 | 读完后你能做到 |
|------|------|--------------|
| [AI 发展时间线](./roadmap/AI_Development_Timeline.md) | 近20年关键节点 + **硬件彩票分析** | 理解每个架构为何胜出 |
| [学习路径规划](./roadmap/Learning_Roadmap.md) | Phase 1-4 + **Infra与数据模块** | 制定个人学习计划 |
| [AI关键人物图谱](./reports/knowledge_reports/AI关键人物图谱.md) | Transformer作者去向、OpenAI分裂史、三巨头分歧 | 理解AI生态的权力结构 |

### 第二步：选择你的学习起点

```
有编程基础，AI 零基础  →  Phase 1（数学与机器学习）→ 约4-6周
有 ML 基础             →  Phase 2（深度学习核心）  →  约6-8周
有深度学习经验         →  Phase 3（大模型与NLP）   →  约8-10周
工程师，关注基础设施   →  Phase 3.7（Infra与数据） →  约2-3周
```

### 第三步：精读论文（按优先级）

查阅 [论文索引](./papers/PAPERS_INDEX.md) 获取所有32篇论文的下载链接与核心摘要。

### 第四步：阅读已有深度报告

**论文精读报告（17 篇已完成）：**
- [Transformer 论文分析](./reports/paper_analyses/01_transformer_2017.md) ← **推荐第一篇读**
- [BERT 论文分析](./reports/paper_analyses/02_bert_2018.md) ← 双向预训练
- [GPT-3 论文分析](./reports/paper_analyses/03_gpt3_2020.md) ← Few-shot
- [InstructGPT 论文分析](./reports/paper_analyses/04_instructgpt_2022.md) ← RLHF 起点
- [Scaling Laws 论文分析](./reports/paper_analyses/05_scaling_laws_2020.md) ← 训练策略与算力配置
- [AlexNet 论文分析](./reports/paper_analyses/06_alexnet_2012.md) ← 深度学习复兴拐点
- [ResNet 论文分析](./reports/paper_analyses/07_resnet_2015.md) ← 残差连接
- [GAN 论文分析](./reports/paper_analyses/08_gan_2014.md) ← 生成对抗网络
- [DDPM 论文分析](./reports/paper_analyses/09_ddpm_2020.md) ← 扩散模型
- [Chain-of-Thought 论文分析](./reports/paper_analyses/10_chain_of_thought_2022.md) ← 思维链
- [ViT 论文分析](./reports/paper_analyses/11_vit_2020.md) ← Vision Transformer
- [CLIP 论文分析](./reports/paper_analyses/12_clip_2021.md) ← 多模态表示学习
- [Swin Transformer 论文分析](./reports/paper_analyses/13_swin_transformer_2021.md) ← 层次化视觉 Transformer
- [LoRA 论文分析](./reports/paper_analyses/15_lora_2021.md) ← 低秩适应微调
- [LLaMA 论文分析](./reports/paper_analyses/16_llama_2023.md) ← 开源大模型
- [MAE 论文分析](./reports/paper_analyses/17_mae_2022.md) ← 自监督视觉预训练
- [Tulu 3 后训练流程分析](./reports/paper_analyses/26_tulu3_2024.md) ← SFT→DPO→RLVR 完整解析

**知识深度解析（5 篇）：**
- [Self-Attention 深度解析](./reports/knowledge_reports/self_attention_深度解析.md) — 含代码实现
- [RLHF 深度解析](./reports/knowledge_reports/RLHF_深度解析.md) — PPO/DPO 对比
- [Scaling Laws 深度解析](./reports/knowledge_reports/Scaling_Laws_深度解析.md) — Kaplan 幂律·Chinchilla 修正
- [LoRA 深度解析](./reports/knowledge_reports/LoRA_深度解析.md) — 低秩适应·QLoRA·DoRA
- [AI关键人物图谱](./reports/knowledge_reports/AI关键人物图谱.md) — 研究者生涯与机构演化

### 第五步：用技能模板生成新报告

- 精读任意论文 → 使用 [论文分析技能](./skills/paper_analysis/SKILL.md)
- 深入理解某概念 → 使用 [知识深挖技能](./skills/concept_deep_dive/SKILL.md)

---

## 📊 论文阅读状态追踪

| # | 论文 | 年份 | 优先级 | 分析报告 |
|---|------|------|--------|---------|
| 01 | Attention Is All You Need (Transformer) | 2017 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/01_transformer_2017.md) |
| 02 | BERT | 2018 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/02_bert_2018.md) |
| 03 | GPT-3 | 2020 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/03_gpt3_2020.md) |
| 04 | InstructGPT (RLHF) | 2022 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/04_instructgpt_2022.md) |
| 05 | Scaling Laws | 2020 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/05_scaling_laws_2020.md) |
| 06 | AlexNet | 2012 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/06_alexnet_2012.md) |
| 07 | ResNet | 2015 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/07_resnet_2015.md) |
| 08 | GAN | 2014 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/08_gan_2014.md) |
| 09 | DDPM (Diffusion) | 2020 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/09_ddpm_2020.md) |
| 10 | Chain-of-Thought | 2022 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/10_chain_of_thought_2022.md) |
| 11 | ViT | 2020 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/11_vit_2020.md) |
| 12 | CLIP | 2021 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/12_clip_2021.md) |
| 13 | Swin Transformer | 2021 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/13_swin_transformer_2021.md) |
| 17 | MAE | 2022 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/17_mae_2022.md) |
| 16 | LLaMA | 2023 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/16_llama_2023.md) |
| 15 | LoRA | 2021 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/15_lora_2021.md) |
| 20 | Stable Diffusion (LDM) | 2021 | ⭐⭐⭐ | ⬜ 待读 |
| 21 | MoE | 2017 | ⭐⭐⭐ | ⬜ 待读 |
| 22 | The Bitter Lesson | 2019 | ⭐⭐⭐ | ✅ [已保存](./papers/22_bitter_lesson_2019.md)（英中双语）|
| 25 | ZeRO | 2019 | ⭐⭐ | ⬜ 待读 |
| 26 | Tulu 3 | 2024 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/26_tulu3_2024.md) |
| 27 | DiT | 2022 | ⭐⭐ | ⬜ 待读 |

> 完整32篇索引见 [PAPERS_INDEX.md](./papers/PAPERS_INDEX.md)
> 当前已完成论文精读 17 篇，最新库存以 [CONTEXT.md](./CONTEXT.md) 为准。

---

## 🗓️ 推荐学习节奏

```
Week 1-2:   AI_Development_Timeline + 硬件彩票分析 + AI人物图谱（建立历史视野）
Week 3-4:   Transformer 精读 + Self-Attention 深度解析
Week 5-6:   BERT + GPT-3 论文（预训练范式）
Week 7-8:   Scaling Laws + InstructGPT + RLHF 深度解析（对齐技术）
Week 9-10:  ViT + Stable Diffusion + CLIP（多模态）
Week 11-12: ZeRO + MegaScale + Infra模块（工程实践）
Week 13-14: Tulu 3 后训练报告 + DPO/RLVR 实验复现
Week 15+:   选择感兴趣方向深入（推理模型 / Agent / 生成模型）
```

---

## 📌 三个核心视角（项目特色）

本项目在标准技术学习路径之外，额外引入三个常被忽视的视角：

**1. 硬件彩票视角**：为什么技术上"更优"的算法不一定赢？
→ 见 [AI发展时间线 · 硬件彩票章节](./roadmap/AI_Development_Timeline.md)

**2. 人的视角**：Transformer 8位作者去了哪里？OpenAI 为何分裂成 Anthropic？
→ 见 [AI关键人物图谱](./reports/knowledge_reports/AI关键人物图谱.md)

**3. The Bitter Lesson 元认知**：AI 70年最大的教训是什么？
→ 原文：http://www.incompleteideas.net/IncIdeas/BitterLesson.html
→ 在 [PAPERS_INDEX.md #22](./papers/PAPERS_INDEX.md) 有详细解读

---

## 🔗 与其他子项目的关联

| 关联领域 | 关联点 | 代表性交叉话题 |
|---------|-------|-------------|
| [哲学](../philosophy-learning/) | 心灵哲学 × AI：意识、语义理解、伦理对齐 | 塞尔中文房间 vs. LLM 是否"理解"语言；辛格功利主义 → RLHF 价值对齐框架 |
| [心理学](../psychology-learning/) | 认知偏差 → AI 对齐；行为主义 → 强化学习 | 前景理论损失厌恶 → RLHF 奖励设计；习得性无助 → 探索-利用困境 |
| [CS](../cs-learning/) | 系统基础 → AI 训练/推理基础设施 | GFS+MapReduce → AI 数据管道；Raft → 分布式训练协调；LLVM → XLA/Triton 编译器 |
| [开源追踪](../github-trending-analyzer/) | 实时追踪 AI 领域热门项目与工具 | 每日/周报告中的 AI/LLM/Agent 分类趋势分析 |

---

## 🛠️ 待办事项

- [ ] 精读 FlashAttention (2022) 并补齐 LLM 推理/训练工程专题
- [ ] 精读 ZeRO (2019) 并结合 Infra 模块实践
- [ ] 精读 Mistral 7B 或 LLaMA 2，补开源大模型第二阶段
- [ ] 精读 DINO v2 或 VideoMAE，补自监督视觉后续脉络
- [ ] 完成 Tulu 3 RLVR 代码复现实验

---

*"能随算力扩展的通用方法，长期总是赢。" — Rich Sutton, The Bitter Lesson (2019)*
