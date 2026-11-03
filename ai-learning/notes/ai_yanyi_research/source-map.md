# 《AI演义》：路线与研究对象地图

本页保存**初始路线与来源身份核定阶段**的清单，不把身份核定等同于全部原文结论已审。后续各路线的原文研究、独立核查及主稿状态见[研究入口](./README.md)；这里保留当时的待核边界，避免改写原始核查记录。

## 36个对象是怎样数出来的

- 模型结构与使用方式：12个对象，第12页拆为seq2seq和Bahdanau Attention两篇。
- The Bitter Lesson：1篇观点文章，第21—25页连续讲同一篇，不重复计数。
- Infra与数据：6个对象，第28页拆为Scaling Laws和Chinchilla两篇。
- 语言模型：8个对象；GPT-1、GPT-2按研究报告计。
- 视觉、多模态与生成：9个对象。

合计 **33篇论文＋2篇研究报告＋1篇观点文章＝36个对象**。标题数与这个口径相符，但不能据此假装知道作者最初怎样计算；硬件背景、人物履历顺带提及的工作和后续产品不额外凑数。

## 讲义的阅读结构

| 页码 | 内容 |
|---|---|
| 1–9 | 阅读与叙事入口：P1–6说明为什么读、怎么读和如何讲；P7总览、P8模型路线、P9硬件前史。问题主轴是算力、软件、数据与模型如何配合。 |
| 10–20 | 模型结构与使用方式：GPU计算抽象与CNN突破；序列编码—解码和注意力；深层结构、稀疏计算、压缩与适配；自弈搜索、推理提示与环境交互。不是每项按正文顺序直接导致下一项。 |
| 21–31 | 跨路线解释、infra与数据：先完整引述一篇Bitter Lesson，再讨论训练显存、计算分配、开放图文数据、网页质量与大集群可靠性。P28必须保留两篇研究的差异。 |
| 32–40 | 语言模型：词表示、翻译系统、预训练迁移、双向理解、自回归扩展、上下文示例、指令偏好后训练、开放配方。P40纠正题名和链接。 |
| 41–50 | 视觉、多模态与生成：视频理解是一条支线；GAN与扩散是生成路线；ViT提供视觉架构，CLIP提供图文表示，LDM降低扩散计算成本，DiT重用Transformer骨干。P49论文与产品分开。 |
| 51 | 收束：致谢，无新增技术对象。 |

## 核定清单

下表年份按核定的首次公开或发表年份记录；修订版年份另在机器清单中保留。页码列主要展开页，不重复列总览图。链接指向核定原文或正式出版入口；身份核定不等于主张全部核实。

### 模型结构与使用方式

| 对象 | 年份 | 主要页 | 核定原文 |
|---|---:|---|---|
| Brook | 2004 | 10 | [Brook for GPUs: Stream Computing on Graphics Hardware](https://dl.acm.org/doi/10.1145/1015706.1015800) |
| AlexNet | 2012 | 11 | [ImageNet Classification with Deep Convolutional Neural Networks](https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html) |
| seq2seq | 2014 | 12 | [Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) |
| Bahdanau Attention | 2014 | 12 | [Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) |
| 知识蒸馏 | 2015 | 13 | [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) |
| ResNet | 2015 | 14 | [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385) |
| Transformer | 2017 | 15 | [Attention Is All You Need](https://arxiv.org/abs/1706.03762) |
| AlphaGo Zero | 2017 | 16 | [Mastering the game of Go without human knowledge](https://www.nature.com/articles/nature24270) |
| 稀疏 MoE | 2017 | 17 | [Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/abs/1701.06538) |
| CoT | 2022 | 18 | [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) |
| LoRA | 2021 | 19 | [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) |
| ReAct | 2022 | 20 | [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) |

### 跨路线解释、infra与数据

| 对象 | 年份 | 主要页 | 核定原文 |
|---|---:|---|---|
| The Bitter Lesson | 2019 | 21、22、23、24、25 | [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) |
| ZeRO | 2019 | 27 | [ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://arxiv.org/abs/1910.02054) |
| Scaling Laws | 2020 | 28 | [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361) |
| Chinchilla | 2022 | 28 | [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) |
| LAION-5B | 2022 | 29 | [LAION-5B: An open large-scale dataset for training next generation image-text models](https://arxiv.org/abs/2210.08402) |
| RefinedWeb | 2023 | 30 | [The RefinedWeb Dataset for Falcon LLM: Outperforming Curated Corpora with Web Data, and Web Data Only](https://arxiv.org/abs/2306.01116) |
| MegaScale | 2024 | 31 | [MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs](https://arxiv.org/abs/2402.15627) |

### 语言模型

| 对象 | 年份 | 主要页 | 核定原文 |
|---|---:|---|---|
| Word2Vec | 2013 | 33 | [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) |
| GNMT | 2016 | 34 | [Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation](https://arxiv.org/abs/1609.08144) |
| GPT-1 | 2018 | 35 | [Improving Language Understanding by Generative Pre-Training](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) |
| BERT | 2018 | 36 | [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) |
| GPT-2 | 2019 | 37 | [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) |
| GPT-3 | 2020 | 38 | [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) |
| InstructGPT | 2022 | 39 | [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) |
| Tulu 3 | 2024 | 40 | [Tulu 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) |

### 视觉、多模态与生成

| 对象 | 年份 | 主要页 | 核定原文 |
|---|---:|---|---|
| DeepVideo | 2014 | 42 | [Large-scale Video Classification with Convolutional Neural Networks](https://openaccess.thecvf.com/content_cvpr_2014/html/Karpathy_Large-scale_Video_Classification_2014_CVPR_paper.html) |
| 双流网络 | 2014 | 43 | [Two-Stream Convolutional Networks for Action Recognition in Videos](https://arxiv.org/abs/1406.2199) |
| GAN | 2014 | 44 | [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) |
| Diffusion（2015） | 2015 | 45 | [Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/abs/1503.03585) |
| DDPM | 2020 | 46 | [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) |
| ViT | 2020 | 47 | [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) |
| CLIP | 2021 | 48 | [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) |
| LDM | 2021 | 49 | [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) |
| DiT | 2022 | 50 | [Scalable Diffusion Models with Transformers](https://arxiv.org/abs/2212.09748) |

## 已解决的身份问题，和还没完成的研究

以下问题已核到正式来源；旧文件没有被擅自删除或替换：

| 位置 | 核查结果 |
|---|---|
| PDF第12页 | 一个链接承载了两篇工作，seq2seq与Attention的贡献和首次公开时间须分开。 |
| PDF第28页 | Scaling Laws与Chinchilla是两篇论文，不能共用同一题名或结论。 |
| PDF第40页 | Tulu 3的题名和内嵌链接不匹配，正确对象为arXiv:2411.15124；原链接指向无关论文。 |
| PDF第42页 | DeepVideo内嵌arXiv链接指向无关论文，已改用CVPR官方入口作为研究依据。 |
| 第21—25页 | The Bitter Lesson应按作者原文的2019-03-13日期理解，页头2018.08不能沿用。 |
| 第49页 | 2021年的LDM论文与2022年公开发布的Stable Diffusion产品分开记录。 |
| 本地28_brook_2004.pdf | 实际不是Brook论文，不纳入Brook原文证据。 |
| 本地24_alphago_zero_2017.pdf | 实际为AlphaZero论文，不当作AlphaGo Zero原文。 |

尚未系统核查的部分包括：讲义中的历史优先性、各节点量化效果、人物履历、跨论文因果解释。Tulu作者姓名在当前元数据与本地版本间还有一处差异，保留待核，不猜测原因。

因此，这张地图的作用是**让下一步研究不读错、不错配，也知道哪些还不能下结论**，不是用一张清单替代整部发展史。

## 进入两段路线样章

- [从seq2seq到Transformer：三篇论文，改的是三个不同的问题](./sample_sequence.md)
- [Scaling Laws到Chinchilla：为什么“把模型做大”还不是完整答案？](./sample_scaling.md)

来源与覆盖细节：[机器清单](./source-map.json)；阶段独立核查：[inventory.review.json](./inventory.review.json)。原始讲义：[PDF](../终版：AI演义，36篇论文开启你的探索之旅.pdf)。
