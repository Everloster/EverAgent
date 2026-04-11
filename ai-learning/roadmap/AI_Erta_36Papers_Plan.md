# AI 演义四条时间线：论文补全推进计划

> 基于《AI演义：36篇论文开启你的探索之旅》(谢青池) 的四条时间线框架
> 创建日期：2026-04-11
> 状态：进行中

---

## 背景

《AI演义》以四条时间线串联 36 篇论文，构成完整的 AI 发展叙事。当前项目已完成 26 篇论文分析 + 11 篇知识深度报告，但四条时间线上存在关键断点。本计划旨在补全这些断点，使知识体系形成完整闭环。

### 四条时间线

| 线索 | 关键节点 | 核心主题 |
|------|--------|--------|
| **模型范式变迁** | Brook -> AlexNet -> Attention -> ResNet -> Transformer -> MoE -> CoT -> LoRA -> ReAct | 从 GPU 计算到 Agent 落地 |
| **Infra 与数据** | ZeRO -> Scaling Law -> LAION-5B -> RefinedWeb -> MegaScale -> Bitter Lesson | 算力、数据、分布式训练 |
| **语言模型** | Word2Vec -> Google Translate -> GPT-1/2/3 -> BERT -> InstructGPT -> Tulu 3 | 从词向量到后训练 |
| **多模态模型** | DeepVideo -> 双流网络 -> GAN -> Diffusion -> DDPM -> ViT -> CLIP -> Stable Diffusion -> DiT | 从视频到文生图 |

---

## 总览：10 篇待补报告 x 3 个批次

| 批次 | 论文 | 所属时间线 | 优先级 | 状态 |
|------|------|---------|--------|------|
| **P0** | GPT-1 (2018) | 语言模型 | 最高 | [x] 已完成 2026-04-11 |
| **P0** | GPT-2 (2019) | 语言模型 | 最高 | [x] 已完成 2026-04-11 |
| **P0** | The Bitter Lesson (2019) | Infra/哲学 | 最高 | [x] 已完成 2026-04-11 |
| **P1** | Stable Diffusion / LDM (2021) | 多模态 | 高 | [x] 已完成 2026-04-11 |
| **P1** | DiT (2022) | 多模态 | 高 | [x] 已完成 2026-04-11 |
| **P1** | ReAct (2022) | 模型范式 | 高 | [x] 已完成 2026-04-11 |
| **P2** | LAION-5B (2022) | Infra/数据 | 中 | [x] 已完成 2026-04-11 |
| **P2** | RefinedWeb (2023) | Infra/数据 | 中 | [x] 已完成 2026-04-11 |
| **P2** | Google Translate (2016) | 语言模型 | 中 | [x] 已完成 2026-04-11 |
| **P2** | DeepVideo (2014) | 多模态 | 中 | [x] 已完成 2026-04-11 |

> 双流网络 (Two-Stream, 2014) 降为可选 -- 它对当前 AI 主线影响较小。

---

## Batch P0：补全核心叙事线（3 篇）

### P0-1：GPT-1 论文分析
- **论文**: "Improving Language Understanding by Generative Pre-Training" (2018.06)
- **作者**: Alec Radford, Karthik Narasimhan, Tim Salimans, Ilya Sutskever
- **PDF**: 需下载（项目中暂无）
- **报告路径**: `reports/paper_analyses/37_gpt1_2018.md`
- **状态**: [x] 已完成 2026-04-11
- **关键分析点**:
  - 预训练+微调范式的开创（CV 迁移学习思路移植到 NLP）
  - Decoder-only + next token prediction 的选择
  - BooksCorpus (~5GB)，参数量 0.1B
  - Ilya 2015 年的数学证明与预训练的关系
  - 与 BERT 的路线之争：单向 vs 双向
- **Wiki 更新**:
  - `wiki/entities/`: 新建 Alec Radford 页面
  - `wiki/concepts/`: 新建 `pretraining_finetuning.md`
  - 更新 `wiki/index.md`, `wiki/log.md`

### P0-2：GPT-2 论文分析
- **论文**: "Language Models are Unsupervised Multitask Learners" (2019.02)
- **作者**: Alec Radford, Jeffrey Wu, Rewon Child, David Luan, Dario Amodei, Ilya Sutskever
- **PDF**: 需下载
- **报告路径**: `reports/paper_analyses/38_gpt2_2019.md`
- **状态**: [ ] 待执行
- **关键分析点**:
  - 从微调到零样本的范式跳跃
  - WebText 数据集构建方法（Reddit 爬取, ~40GB）
  - 1.5B 参数，数据和模型同时 10x 扩展
  - OpenAI 的 scaling 信号识别（从 GPT-2 到 GPT-3 的决策）
  - Dario Amodei 参与（后创立 Anthropic）
- **Wiki 更新**:
  - `wiki/concepts/`: 新建 `zero_shot_learning.md`
  - 更新 OpenAI entity 页面

### P0-3：The Bitter Lesson 分析
- **文章**: Rich Sutton, "The Bitter Lesson" (2019.03)
- **已有文件**: `papers/22_bitter_lesson_2019.md`（Markdown 格式，无需下载）
- **报告路径**: `reports/paper_analyses/22_bitter_lesson_2019.md`
- **状态**: [x] 已完成 2026-04-11
- **关键分析点**:
  - 70 年 AI 历史的核心教训：通用计算方法 > 人类知识编码
  - 国际象棋、围棋、语音识别、计算机视觉四个领域的验证
  - 搜索与学习是两大可无限扩展的方法
  - 与 Scaling Law、AlphaGo Zero、GPT-3 的深度关联
  - 对当前 AI 工程实践的指导意义
- **Wiki 更新**:
  - `wiki/entities/`: 新建 Rich Sutton 页面
  - `wiki/concepts/`: 新建 `bitter_lesson.md`

### P0 完成后的效果
- **语言模型线**完整闭合：Word2Vec -> GPT-1 -> BERT -> GPT-2 -> GPT-3 -> InstructGPT -> Tulu 3
- **Infra 线**获得哲学基础：Bitter Lesson 串联 Scaling Law -> ZeRO -> MegaScale

---

## Batch P1：补全高价值节点（3 篇）

### P1-1：Stable Diffusion (LDM) 论文分析
- **论文**: "High-Resolution Image Synthesis with Latent Diffusion Models" (2021.12)
- **已有 PDF**: `papers/20_stable_diffusion_2021.pdf`
- **报告路径**: `reports/paper_analyses/20_stable_diffusion_2021.md`
- **状态**: [ ] 待执行
- **关键分析点**:
  - 潜空间扩散的核心创新（像素空间 -> 潜空间）
  - 交叉注意力层实现条件生成
  - CLIP Text Encoder 的集成
  - 与 DDPM (#09) 的技术演进关系
  - 开源生态影响（Stability AI）
- **Wiki 更新**:
  - `wiki/concepts/`: 新建 `latent_diffusion.md`

### P1-2：DiT 论文分析
- **论文**: "Scalable Diffusion Models with Transformers" (2022.12)
- **已有 PDF**: `papers/27_dit_2022.pdf`
- **报告路径**: `reports/paper_analyses/27_dit_2022.md`
- **状态**: [ ] 待执行
- **关键分析点**:
  - Transformer 替换 U-Net 的架构决策
  - Scaling 特性（Gflops vs FID 的关系）
  - 与 ViT 的架构联系
  - Sora 的技术基础（William Peebles 后加入 OpenAI）
  - 架构统一趋势：NLP + CV + 生成全部 Transformer 化

### P1-3：ReAct 论文分析
- **论文**: "ReAct: Synergizing Reasoning and Acting in Language Models" (2022.10)
- **已有 PDF**: `papers/17_react_2022.pdf`
- **报告路径**: `reports/paper_analyses/17_react_2022.md`
- **状态**: [ ] 待执行
- **注意**: 已有 `reports/knowledge_reports/Agent_ReAct_ToolUse_深度解析_20260409.md`，本次补充论文级分析
- **关键分析点**:
  - Reasoning + Acting 交错的核心范式
  - 与 CoT 的对比（纯推理 vs 推理+行动）
  - 姚顺雨的研究背景（00后，SWE-bench 作者）
  - Agent 从理论到落地的关键一步
  - LangChain/LangGraph 对 ReAct 的工程化

### P1 完成后的效果
- **多模态线**完整闭合：GAN -> Diffusion -> DDPM -> ViT -> CLIP -> Stable Diffusion -> DiT
- **模型范式线**完整闭合：Brook -> ... -> CoT -> LoRA -> ReAct

---

## Batch P2：扩展视野（4 篇）

### P2-1：LAION-5B 论文分析
- **论文**: "LAION-5B: An open large-scale dataset for training next generation image-text models" (2022.10)
- **已有 PDF**: `papers/29_laion5b_2022.pdf`
- **报告路径**: `reports/paper_analyses/29_laion5b_2022.md`
- **状态**: [ ] 待执行

### P2-2：RefinedWeb 论文分析
- **论文**: "The RefinedWeb Dataset for Falcon LLM" (2023.06)
- **已有 PDF**: `papers/30_refinedweb_2023.pdf`
- **报告路径**: `reports/paper_analyses/30_refinedweb_2023.md`
- **状态**: [ ] 待执行

### P2-3：Google Translate (GNMT) 论文分析
- **论文**: "Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation" (2016.09)
- **PDF**: 需下载
- **报告路径**: `reports/paper_analyses/39_google_translate_2016.md`
- **状态**: [ ] 待执行

### P2-4：DeepVideo 论文分析
- **论文**: "Large-scale Video Classification with Convolutional Neural Networks" (2014.06)
- **PDF**: 需下载
- **报告路径**: `reports/paper_analyses/40_deepvideo_2014.md`
- **状态**: [ ] 待执行

### P2 完成后的效果
- **Infra/数据线**完整闭合：ZeRO -> Scaling Law -> LAION-5B -> RefinedWeb -> MegaScale -> Bitter Lesson
- **语言模型线**补全工程视角：Google Translate（NMT 工业部署）

---

## 每篇报告的标准执行流程

```
1. 读取 PDF 论文原文（或下载后读取）
2. 按 skills/paper_analysis/SKILL.md 的 7 步模板撰写报告
3. 报告包含完整 YAML frontmatter
4. Wiki 操作（按 CLAUDE.md 规定）:
   a. 更新/新建 wiki/entities/ 页面
   b. 更新/新建 wiki/concepts/ 页面
   c. 追加 wiki/log.md
   d. 更新 wiki/index.md
5. 更新 papers/PAPERS_INDEX.md（如有新论文）
6. 更新 CONTEXT.md 已完成列表
7. 更新本文件中对应任务的状态 [ ] -> [x]
```

---

## 四条时间线覆盖率追踪

| 时间线 | 当前 | P0 后 | P1 后 | P2 后 |
|--------|------|-------|-------|-------|
| 模型范式变迁 | 9/11 (82%) | 9/11 | 11/11 (100%) | 11/11 |
| Infra 与数据 | 3/6 (50%) | 4/6 (67%) | 4/6 | 6/6 (100%) |
| 语言模型 | 5/8 (63%) | 7/8 (88%) | 7/8 | 8/8 (100%) |
| 多模态模型 | 6/10 (60%) | 6/10 | 8/10 (80%) | 9/10 (90%) |
| **总计** | **23/35 (66%)** | **26/35 (74%)** | **29/35 (83%)** | **34/35 (97%)** |

> 唯一剩余：双流网络 (Two-Stream, 2014)，可选补充。

---

## 断点续传指南

在新的会话中继续执行时，请：

1. 读取本文件查看当前进度（哪些 `[ ]`，哪些 `[x]`）
2. 读取 `ai-learning/CONTEXT.md` 确认已完成列表
3. 从第一个 `[ ]` 任务开始执行
4. 每完成一篇，更新本文件状态为 `[x]`
5. 按标准执行流程完成所有配套更新（Wiki、Index 等）
