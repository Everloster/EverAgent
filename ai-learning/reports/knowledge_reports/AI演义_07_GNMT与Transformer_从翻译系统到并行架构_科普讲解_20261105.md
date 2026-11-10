---
title: "AI演义·07｜GNMT 与 Transformer：翻译系统与并行架构"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["ai_history", "neural_machine_translation", "gnmt", "transformer", "attention", "wordpiece", "quantization"]
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·07｜GNMT 与 Transformer：翻译系统与并行架构

<a id="reading-route"></a>

[返回总览第 7 节](../AI演义_笔记分析与项目整合报告.md#paper-gnmt) · [上一章：seq2seq 与 Attention](./AI演义_06_seq2seq与Attention_模型怎样翻译一句话_科普讲解_20261105.md)

上一章用 **The black cat is sleeping. → Le chat noir dort.** 解释了编码、解码和源句注意力。模型已经有了翻译方法，做成服务时还会遇到漏译、生词、等待时间和质量评价等问题。2016 年的 GNMT 将这些问题放到同一套系统里处理。[^gnmt-overview]

2017 年的 Transformer 改变了另一件事：用注意力直接构造各位置的表示，减少沿词序传递循环状态的等待。它便于并行处理已知序列，原始翻译模型在生成未知译文时仍然一步步预测。[^transformer-overview]

下面继续使用黑猫句子，按词展示的中间过程都是教学示意；真实系统使用词片。

<a id="translation-service"></a>

## 1. GNMT 要解决的服务问题

如果译文是 Le chat dort，black 对应的黑色就丢了。少见名字可能没有词表项，较大的网络和束搜索又可能让解码太慢。即使 BLEU 提高，还需要检查人是否认为译文更准确。

这些问题分别涉及表示、搜索、实现和评价。GNMT（Google Neural Machine Translation）的工作，是把深层循环网络与这些环节结合，而非只扩大网络层数。

<a id="gnmt-architecture"></a>

## 2. 深层 LSTM 怎样利用多张 GPU

GNMT 使用 **8 层编码器、8 层解码器 LSTM**。编码器最底层双向读取，上层单向处理；每端的 8 层分别计数。编码器、解码器都从自底向上的第 3 层开始使用残差连接，帮助深层信号与梯度传播。[^gnmt-architecture][^gnmt-residual]

它的 Attention 用解码器底层前一步的状态，与编码器顶层各位置表示匹配，再把源句上下文直接提供给上面的解码层。这样，下一步的部分计算不必等最顶层全部完成，更容易让不同层和时间步形成流水。

循环网络因此并非完全顺序执行：不同句子、矩阵运算和层间流水都能并行，仍受约束的是同一条循环状态链。GNMT 将一个模型分到 **8 张 GPU**，再以 **12 个共享参数的副本**做数据并行，共使用 **96 张 K80**，英法模型基本训练约 **6 天**。[^gnmt-parallel]

<a id="wordpiece-and-coverage"></a>

## 3. 词片处理生词，搜索减少漏译

### WordPiece 在整词与字符之间取舍

词表若收下每个完整名字，规模会不断增加；全部按字符处理，序列又会变长。WordPiece 使用从数据学到的常见片段，常见词可以保留，较少见的词拆开表示。原文把 Jet 切成 `_J`、`et`，feud 切成 `_fe`、`ud`，下划线表示词首。[^wordpiece]

GNMT 共用源、目标词片表，便于学习复制名字和数字。只要所需片段可用，罕见拼写便有机会被表示出来；极少见字符仍可能被裁掉并映射成未知字符。WordPiece 也已有语音识别应用基础，GNMT 使用的是此前在 Google 日语、韩语语音识别中采用的实现。

WMT 2014 英法的 Table 4 比较如下。32K 词片的 38.95 是 **8 次独立单模型分数的平均**；时间是在 CPU 上按批次 16、每句最多 4 个搜索候选运行后，以总耗时除以句数。[^wordpiece-results]

| 输入、输出单位 | BLEU | CPU 解码时间，按每句折算 |
|---|---:|---:|
| 完整词 | 37.90 | 0.2226 秒 |
| 字符 | 38.01 | 1.0530 秒 |
| 16K 词片表 | 37.60 | 0.1874 秒 |
| 32K 词片表 | 38.95 | 0.2118 秒 |

整词基线也处理生词：保留未知词的首尾字符，再根据 Attention 从源句复制内容替换。词片相对于这套基线取得较好的质量与速度取舍。表中 32K 的 BLEU 更高，16K 更快；附近正文将 32K 同时称为最快，与表格不符。这里的折算时间也不是单个用户请求的响应延迟。

### 长度归一化与覆盖惩罚

词表有了 black，并不保证模型一定译出 noir。GNMT 在束搜索评分中加入长度归一化，缓解候选得分偏爱短句的问题；覆盖惩罚则根据各源位置累计得到的注意力，降低明显忽略部分源信息的候选得分。[^coverage]

这些办法鼓励译得完整，仍需检查语义是否准确。词序重排和多词对应一词也继续由软对齐处理，不要求机械逐词输出。

<a id="integer-and-latency"></a>

## 4. 整数推理与整批解码时间

GNMT 将权重存为 **8-bit 整数**，乘法使用 8-bit 输入，累加器更宽；时间与深度上持续累积的状态，以及激活和逐元素运算使用 **16-bit 整数**。Attention 与 softmax 内部没有量化。训练仍用全精度浮点数，同时裁剪部分状态和输出分数，为整数推理控制范围。[^quantization]

精度分配要考虑舍入误差在深层 LSTM 中的累积，因此不能只把它理解为存储文件变小。这里的 8-bit 整数方案也与 FP8 浮点格式不同。

Table 1 报告 **6,003 句英法开发集**的整批解码结果：

| 解码配置 | BLEU | 全部句子的解码时间 |
|---|---:|---:|
| CPU | 31.20 | 1,322 秒 |
| K80 GPU | 31.20 | 3,028 秒 |
| TPU | 31.21 | 384 秒 |

CPU、GPU 使用浮点路径，TPU 卸载量化运算，嵌入查找和 Attention 等仍有 CPU 参与；主机为同类双 CPU 配置。[^latency] 硬件与实现同时变化，这不是只改变精度的消融。

GPU 反而较慢。作者将原因指向逐步束搜索带来的主机与 GPU 传输、计算利用率，以及双 CPU 主机本身的算力。训练中的大矩阵计算可以充分利用 GPU，细碎的候选管理和频繁往返却可能抵消优势。判断加速效果，需要测到应用真正等待的那一段工作。

<a id="metrics-and-humans"></a>

## 5. 自动指标、人评和生产选择

GNMT 先按正确译文做最大似然训练，再尝试用强化学习改善模型自己生成的候选。单句奖励采用 **GLEU**，比较 1–4 gram 的匹配准确程度与覆盖程度，再与原训练目标混合；人工评分用于之后的效果检查。[^rl-objective]

Table 6 中，单模型分数的平均在英法上由 **38.95 BLEU 提高到 39.92**，英德则由 **24.67 变为 24.60**。英德开发集虽有改善，测试并未呈现同样结果。[^rl-results]

论文又在 **500 个英法例子**上做人评。下面两行神经系统都是 8 模型集成：

| 系统 | BLEU | 人工平均评分，0–6 分 |
|---|---:|---:|
| 基于短语的统计翻译 PBMT | 37.0 | 3.87 |
| 神经翻译，强化学习前 | 40.35 | 4.46 |
| 神经翻译，强化学习后 | 41.16 | 4.44 |
| 人工参考译文 | — | 4.82 |

神经系统相对 PBMT 有改善，强化学习带来的 BLEU 增益却未对应到明确的人评提升。4.46 与 4.44 的差别也不能直接证明质量显著受损。作者讨论了样本量、提升幅度及指标差异，后面的生产数据实验没有采用这项 RL 精调，也没有使用集成。[^human-evaluation]

### 摘要中“错误减少约 60%”的含义

生产评价在每个方向抽取 500 句 Wikipedia 和新闻句子，比较 PBMT、GNMT 与人工译文。Table 10 的英译法人评依次是 **4.932、5.295、5.496**。相对人工，PBMT 差 0.564 分，GNMT 差 0.201 分，分差缩小约 **64%**，对应表中的相对改善。[^production-evaluation]

这是人评分差的缩减，不是逐句统计消除了多少个翻译错误。作者还限定，这些句子较简单且彼此独立，困难翻译和更长输入仍需测试，评分本身也不完美。

Table 11 就展示了问题：原意是“近期事件使外国投资者和当地人不安”，GNMT 译成了“吸引了外国投资者和当地人”。另一条有语法和语义问题的 PBMT 译文却被打了满分。[^gnmt-counterexample] 服务质量既要查模型，也要查评价是否抓住了真正影响理解的错误。

<a id="self-attention"></a>

## 6. Transformer 用注意力构造序列表示

GNMT 的每条循环状态仍沿词序传递。Transformer 则先取得同层所有位置的输入，再让各位置通过注意力相互读取，形成下一层表示。Cat 的本层输出不用等 black 的本层输出，二者都读取已经存在的本层输入。[^transformer-overview]

### 匹配与汇总

输入经过不同的线性变换，产生 Q、K、V：

| 名称 | 用途 |
|---|---|
| Q，Query | 读取位置用来匹配的向量 |
| K，Key | 各可读位置用来被匹配的向量 |
| V，Value | 各位置提供、等待加权汇总的信息 |

例如更新 black 时，用它的 Q 与各位置 K 做点积，除以键维数的平方根，再经 softmax 得到权重，用这些权重汇总 V。缩放可缓解高维点积过大、softmax 落入小梯度区域的问题。[^qkv]

自注意力中的 Q、K、V 来自同一序列，但使用不同变换。把所有位置放入矩阵，就能批量完成匹配与汇总。各向量怎样编码内容由训练学习，权重图本身不能直接证明某种真实语义关系。

### 多头、前馈与位置

多头注意力用多组投影分别读取，再拼接结果并变换。Base 模型的表示为 **512 维**，使用 **8 个头**，每头键和值各 **64 维**。缩小每头维度，使总注意力计算与全维单头相近；它们是一套网络内的不同读取方式，不是八个独立模型投票。[^multihead]

编码器、解码器各有 **6 层**。编码层在注意力后还有逐位置前馈网络，由两个线性变换和中间非线性组成，同层各位置共享参数但独立计算。每个子层外有残差和 LayerNorm，原版在残差相加后归一化，即 post-LN。完整系统还包括词嵌入和输出 softmax。[^transformer-block]

模型需要知道顺序。原论文将不同频率的正弦、余弦位置编码加到词表示上；可学习位置嵌入在对照中取得相近成绩。选择正弦的动机之一是向更长序列推广，尚不能据此推断无限长度上的正确理解。[^position]

<a id="training-and-generation"></a>

## 7. 训练并行与逐步生成

原始翻译 Transformer 有三处注意力：

| 位置 | Q 来源 | K、V 来源 | 可见范围 |
|---|---|---|---|
| 编码器自注意力 | 源句本层输入 | 源句本层输入 | 完整源句 |
| 解码器遮罩自注意力 | 目标序列本层输入 | 目标序列本层输入 | 已有目标前缀 |
| 编码器—解码器注意力 | 解码端前一子层表示 | 编码器最终输出 | 完整源句 |

准备输出 noir 时，解码器先处理 Le chat 等已知前缀，再通过交叉注意力读取英文。源句已经给定，所以可以完整读取；后续法文答案还未生成。[^three-attentions]

训练时答案虽已在数据里，仍要模拟这个信息条件。目标输入右移一位，再加因果遮罩。按词简化后的对应关系如下，`<START>` 和 `<EOS>` 为教学记号：

| 训练位置 | 当前输入 | 可使用的目标输入 | 预测目标 |
|---|---|---|---|
| 1 | `<START>` | `<START>` | Le |
| 2 | Le | `<START> Le` | chat |
| 3 | chat | `<START> Le chat` | noir |
| 4 | noir | `<START> Le chat noir` | dort |
| 5 | dort | `<START> Le chat noir dort` | `<EOS>` |

右移避免当前位置直接收到答案，遮罩阻止读取后面的位置。正确前缀可以预先同时准备好，网络就在这种约束下批量计算各位置的预测与损失，无须等待同层前一个位置更新循环状态。[^causal-training]

推理时，只能把实际生成的 Le 加入前缀后预测下一步，再根据后续真实输出继续。束搜索也只是同时维护多个逐步扩展的候选。Transformer 减少了处理已知序列的循环依赖，未知输出的自回归依赖仍在。

<a id="transformer-evidence"></a>

## 8. 计算、实验与代价

自注意力缩短了位置间的信息路径，同时要做两两匹配。长度由 100 增到 1,000，配对数就从约一万增至一百万；这只是计算结构说明，不是实测耗时或显存。

论文比较普通句长背景下的自注意力与循环层，包含序列长度小于表示维数的条件。较少的顺序操作不意味着整网耗时恒定，也不消除长序列的匹配开销。[^complexity]

### 翻译成绩

WMT 2014 英德的主要结果为：

| 配置 | 参数量 | 英德测试 BLEU | 训练配置与时间 |
|---|---:|---:|---|
| base | 约 6,500 万 | 27.3 | 8 张 P100，约 12 小时 |
| big | 约 2.13 亿 | 28.4 | 8 张 P100，约 3.5 天 |

英德训练约 **450 万句对**，使用 BPE 和约 37K 共享词表；英法约 **3,600 万句对**，使用 32K WordPiece。[^transformer-training]

论文与当时的 GNMT、卷积翻译等文献结果比较，报告较好的英德成绩与较低训练成本。不过，各文献的硬件、实现和训练条件不同，不能直接从 K80 与 P100 的卡数及天数计算单独由架构带来的加速。训练 FLOPs 也是由时间、GPU 数量和估计算力得到，并非在同一设备上重跑所有系统。[^transformer-results]

“单模型”还采用检查点参数平均：base 平均同一次训练最后 5 个检查点，big 平均最后 20 个，最终只有一套推理参数。这与多个独立模型共同预测的集成不同。

英法结果在所读 v7 内有冲突：摘要和 Table 2 为 **41.8 BLEU**，§6.1 正文为 **41.0**。本章保留差异，没有把它解释为未被证实的另一组实验。

### 部件对照

Table 3 使用英德 **newstest2013 开发集**，不做检查点平均：

| 相对 base 的改动 | 开发集 BLEU |
|---|---:|
| 原 base，8 个头 | 25.8 |
| 改成 1 个头，并相应调整头的维度 | 24.9 |
| 改成 32 个头，并相应调整头的维度 | 25.4 |
| 不使用 dropout | 24.6 |
| 不使用标签平滑 | 25.3 |
| 正弦位置编码换成可学习的位置嵌入 | 25.7 |

多头在这里有帮助，增加到 32 头却没有继续改善。Dropout 减少对固定计算组合的依赖；标签平滑将部分目标概率分配到其他词，两者也影响最终成绩。位置编码的两种方式则相近。[^ablations]

标签平滑让困惑度变差、BLEU 变好，也显示指标关心的东西不同：困惑度看参考词概率，BLEU 看生成译文与参考译文的匹配。它与 GNMT 的人评实验一样，需要按应用真正关心的效果判断。

作者还把 4 层模型用于英语句法成分分析。约 **4 万句**监督训练得到 **91.3 F1**，加入约 **1,700 万句**半监督数据后为 **92.7 F1**。[^parsing] F1 衡量预测结构与标注的匹配；这证明架构能用于另一类序列任务，表中仍有成绩更高的系统。

附录以少量句子观察远距离联系、代词回指和不同头的模式。这些图可帮助提出问题，但没有给出每个头的固定职责或模型决定的完整因果解释。[^attention-examples]

<a id="people-and-connections"></a>

## 9. 部件、团队与研究工具

GNMT 的 31 位作者来自 Google 的研究和翻译服务团队，包括 Yonghui Wu、Mike Schuster、Quoc V. Le、Oriol Vinyals 等。后两位也参与了 seq2seq。作者名单体现共同工作，未公开的具体分工不能据此补写。[^people]

Transformer 的 8 位作者在所读 v7 首页说明了贡献：Jakob Uszkoreit 提出以自注意力替代 RNN 的探索；Ashish Vaswani、Illia Polosukhin 设计并实现早期模型；Noam Shazeer 提出缩放点积、多头和无参数位置表示；Niki Parmar、Llion Jones 参与变体、实现、推理与可视化；Łukasz Kaiser、Aidan N. Gomez 推进 Tensor2Tensor 的设计和实现。首页注明共同贡献、顺序随机，这里采用的是修订版记载。[^people]

具体部件也在不同项目之间流动。Transformer 的 WordPiece 与长度惩罚引用 GNMT，残差连接引用 ResNet；BERT 又引用 GNMT 说明 WordPiece。[^component-links] 主体架构改变后，文本表示和训练经验仍可能继续使用。

GNMT 首发于 **2016 年 9 月 26 日**，Transformer 首发于 **2017 年 6 月 12 日**；本章依据的是 GNMT v2（2016-10-08）和 Transformer v7（2023-08-02）。[^history]

<a id="questions"></a>

[下一章 GPT-1 与 BERT](./AI演义_08_GPT1与BERT_预训练怎样迁移到不同任务_科普讲解_20261105.md)转向预训练：能否先从大量文字中学好网络，再用于不同任务。以后遇到新架构，也可以沿本章的办法看信息如何传递、哪些步骤能并行，以及实验是否测到了用户实际关心的质量与等待时间。

<a id="sources-and-corrections"></a>

## 播客、讲义与阅读范围

讲义第 15 页讲 Transformer，第 34 页讲 GNMT；播客中分别位于约 **57:29–1:08:47** 与 **2:28:32–2:33:30**，中间是其他主题，非音频缺失。[^podcast] 两段转写在人名和点积等术语上有识别不稳，GNMT 段另有一次相邻重复；量化按论文采用整数描述，没有沿用“当时使用 FP8”的口述。

本次保留原稿对两篇文字、主要架构图和关键表格的核验记录。Transformer 附录只采用图注和可提取文字支持的定性说明，未逐头测量。音频未人工逐字听校或测词错误率，整期末尾约 16 秒覆盖仍未确认；本次不重训模型、复现 BLEU 或评测当前翻译服务。

## 来源与延伸阅读

[^gnmt-overview]: Wu 等，[Google’s Neural Machine Translation System](https://arxiv.org/pdf/1609.08144v2)，摘要、§1–2、§9：速度、罕见词、覆盖与生产部署问题。神经模型与传统系统均有数据、结构和工程选择。
[^gnmt-architecture]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§3、§3.2–3.3、Figure 1、Figure 3、式 4：8 层编码器、8 层解码器；最底编码层双向，底层解码器前一步状态用于 Attention。底层双向包含两个方向的 LSTM，不能把图中单元或 GPU 标签直接当层数。
[^gnmt-residual]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§3.1、Figures 1–2；残差改善反向传播，使用起点见 Figure 1 图注。与[第 3 节 ResNet](./AI演义_03_ResNet_深层网络如何训练_科普讲解_20261104.md)连接的是残差思想，不是整套卷积架构。
[^gnmt-parallel]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§3.3、§8.3：§3.3 泛述副本数常约 10，§8.3 正式配置为 12 副本、每副本 8 GPU；英法基本训练约 6 天，之后可选 RL 阶段约 3 天。数据并行副本与推理时的多模型集成不同。
[^wordpiece]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§4.1：Jet、feud 的原始切分例子，词首标记，共享源/目标词片表，以及低频字符映射到 unknown character 的边界。8K–32K 是论文中的实验经验，未核为跨任务最佳范围。
[^wordpiece-results]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§8.4、Table 4：WMT 英法 newstest2014，WPM-32K 的 38.95 为 8 次单模型分数平均；CPU batch 16、最多 4 个候选，总耗时除以句数。整词基线用 `<first_char>_UNK_<last_char>` 标记未知词，再按注意力复制源词替换。BLEU 的含义按匹配指标概述，不把分数当成翻译正确率；原文“32K 最快”与表内时间不一致。
[^coverage]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§7、§8.1、Tables 2–3：长度归一化和按 Attention 累计的覆盖惩罚，参数在开发集选择；搜索调优与 RL 的收益有重叠，不能简单相加。机制鼓励覆盖，不证明语义忠实。
[^quantization]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§6、式 10–13、Figure 4：整数权重、乘法、状态与运算精度，Attention/softmax 例外，全精度训练及裁剪约束。本文不从量化训练曲线反推未报告的逐点数值。
[^latency]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§6、Table 1：newstest2012+2013 共 6,003 句，双 Haswell CPU 主机，GPU 路径为 Tesla K80，TPU 路径保留部分 CPU 操作；表中均为整批时间。作者以 CPU 算力、逐步传输与利用率解释 GPU 路径较慢。
[^rl-objective]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§5、式 7–9：先最大似然训练，再可选地混合期望奖励目标；单句 GLEU 使用 1–4 gram 的 precision/recall 最小值。此处奖励自动计算，未采用人工偏好训练。
[^rl-results]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§8.5、Table 6：8 次独立运行的分数平均，英法 38.95→39.92、英德 24.67→24.60。Table 5 的英德 WPM-32K 另报 24.61，本文没有把它替换进 Table 6 的前后对照。
[^human-evaluation]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§8.6–8.7、Tables 7–9：500 例、四份译文比较，神经模型为 8 模型集成；0–6 评分及其边界另见 §8.2、Table 11。Table 9 与 Table 10 的生产数据三方比较是不同设置，4.82 不是评分上限。
[^production-evaluation]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，§8.7、Table 10、Figure 6：每方向 500 句，GNMT 采用 32K WordPiece、不集成、不用 RL，此处也不使用 dropout。本文按英法三项人评分重算相对差距缩减；作者限定简单孤立句、人评不完美及长输入待测。
[^gnmt-counterexample]: [GNMT](https://arxiv.org/pdf/1609.08144v2)，Table 11 最后一个投资者案例与表注中的满分译文质疑；中文是对英文源句、法文译文的解释。该表神经模型对应 Table 9 的 RL 前配置；案例不能用于估算总体错误率。
[^transformer-overview]: Vaswani 等，[Attention Is All You Need](https://arxiv.org/pdf/1706.03762v7)，摘要、§1–4：用自注意力替代序列表示主干的循环/卷积计算，保留编码器—解码器框架；“无循环”与“非自回归生成”是不同性质。
[^qkv]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§3.2.1、式 1、Figure 2：点积除以键维数的平方根，softmax 后乘 V。黑猫句中的读取方向只示意可能的机制，未观测真实注意力权重。
[^multihead]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§3.2.2：多组学习投影、并行 Attention、拼接与输出投影；base 为 8 头，每头键/值维度 64，模型维度 512。缩小每头维度后，总注意力计算成本与全维单头相近；这不代表任意增加头数都没有开销。
[^transformer-block]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§3.1、§3.3–3.4、Figure 1：两端各 6 层，逐位置前馈为两个线性变换与 ReLU；base 中间维度 2,048，外侧表示 512。原版采用残差相加后的 LayerNorm，还包括词嵌入与最终词表 softmax。
[^position]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§3.5、Table 3(E)：加法位置编码、正弦动机与可学习位置对照。更严格地说，无位置线索的普通自注意力对输入置换是等变的；不是词序改变后所有输出数值都必然完全相同。
[^three-attentions]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§3.2.3、Figure 1：encoder self-attention、decoder masked self-attention、encoder-decoder attention 的 Q/K/V 来源及可见范围；表中描述真实词片位置，未展开批次填充的遮罩处理。
[^causal-training]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§3.1–3.2.3、Figure 1 的 outputs shifted right，以及 §6.1 束搜索。法文按词演示，特殊开始符号为教学记号，不声称是论文代码的原始 token 名称。
[^complexity]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§4、Table 1：self-attention 层为 O(n²d)，循环层为 O(nd²)，n 是长度、d 是表示维数；相关比较保留 n<d 条件。原文还将限制局部读取范围、改善长序列计算列为后续方向。
[^transformer-training]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§5.1–5.4、Table 3：句对规模、英德 BPE/英法 WordPiece、长度分批、P100 训练时间及 65M/213M 参数。原文还使用 Adam、学习率预热与衰减；本文未复现这些训练配方。
[^transformer-results]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，摘要、§6.1、Table 2：英德 27.3/28.4，英法 41.8 与正文 41.0 冲突；base/big 检查点参数平均、beam 4、长度惩罚 0.6，以及 FLOPs 估计方法。跨文献表格不能分离架构、硬件与实现的全部影响。
[^ablations]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§5.4、§6.2、Table 3：开发集 newstest2013、无检查点平均；头数对照相应改变每头维度以控制计算量，dropout、标签平滑与位置嵌入分别改变。单行结果不能直接外推为任意规模的通用最优配方。
[^parsing]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§6.3、Table 4：4 层句法模型、约 40K/17M 训练句，WSJ23 F1 为 91.3/92.7；表中另有 91.7、93.0、93.3 等成绩，任务迁移成功不等于全面领先。
[^attention-examples]: [Transformer](https://arxiv.org/pdf/1706.03762v7)，§4 与附录 Figures 3–5 图注。本文依据图注和可提取文字讨论少量可视化的用途，未按图估计权重或进行因果解释实验。
[^people]: [GNMT](https://arxiv.org/pdf/1609.08144v2) 首页、致谢；[Transformer v7](https://arxiv.org/pdf/1706.03762v7) 首页署名与贡献脚注；[seq2seq](https://arxiv.org/pdf/1409.3215v3) 作者连接由[上一节的原文核查](./AI演义_06_seq2seq与Attention_模型怎样翻译一句话_科普讲解_20261105.md#people-and-history)承接。未调查后续职业去向。
[^component-links]: [Transformer](https://arxiv.org/pdf/1706.03762v7) §3.1、§5.1、§6.1 及 References [11]/[38]；[BERT](https://arxiv.org/pdf/1810.04805v2) §3 的 WordPiece 与 Wu et al. (2016) 引用，本轮仅定向复核该处及对应参考文献。
[^history]: [GNMT 官方版本历史](https://arxiv.org/abs/1609.08144)、[Transformer 官方版本历史](https://arxiv.org/abs/1706.03762)，与两份 PDF 的首页版本标记。
[^podcast]: [《张小珺Jùn｜商业访谈录》第 117 期：AI演义](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)，[Apple Podcasts 备用入口](https://podcasts.apple.com/cn/podcast/id1634356920?i=1000733801180)；[讲义第 15 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=15)、[第 34 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=34)。单章时间由转录定位，含相邻交接，并非 shownotes 为两篇单独标注的精确章界。
