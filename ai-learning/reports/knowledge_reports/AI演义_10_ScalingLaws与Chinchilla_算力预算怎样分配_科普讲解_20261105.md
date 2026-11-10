---
title: "AI演义·10｜Scaling Laws 与 Chinchilla：怎样分配训练预算"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
semantic_tags: ["AI演义", "Scaling Laws", "Chinchilla", "语言模型", "训练预算", "科普讲解"]
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·10｜Scaling Laws 与 Chinchilla：怎样分配训练预算

[返回总览第 10 节](../AI演义_笔记分析与项目整合报告.md#paper-scaling-laws) · [上一章：GPT-2 与 GPT-3](AI演义_09_GPT2与GPT3_任务怎样进入上下文_科普讲解_20261105.md)

决定训练一个语言模型时，参数和训练量争用同一份计算预算。大模型每处理一段文字更贵，小模型可以多处理一些文本，哪种组合最后效果更好，需要实验。

2020 年的 Scaling Laws 测量资源与语言建模损失的关系，用较小实验指导更大训练。2022 年的 Chinchilla 重新比较模型大小和训练时长，给出不同配比，并训练一个大模型检查预测。[^kaplan-intro][^chinchilla-intro]

<a id="budget"></a>

## 1. 参数量与训练 token 的交换

对论文中的密集 Transformer，可以先用“参数量 × 累计训练 token”近似理解主要计算开销。常见估算还乘以前向与反向计算的系数，具体论文的参数计数和其他计算项并不完全相同。[^compute-definition]

以下是三种相同粗略预算的教学方案：

| 方案 | 参数量 | 累计训练 token |
|---|---:|---:|
| A | 10 亿 | 200 亿 |
| B | 20 亿 | 100 亿 |
| C | 50 亿 | 40 亿 |

三组乘积相同，但性能不会仅由乘积决定。模型太小可能限制表达，模型太大又可能在预算用完时仍未得到足够训练。

语料规模、累计训练量和上下文长度也需分开。重复读取同一文本会增加训练 token，一次输入能容纳多少 token 则由上下文窗口决定。训练 1 万亿 token 不能解释为一次读取 1 万亿 token。

FLOPs 记录浮点运算工作量，设备天数和费用还受通信、显存和硬件利用率影响。同样的 FLOPs 不保证相同耗时。

<a id="loss-and-curves"></a>

## 2. 缩放曲线测的是什么

给模型前文 The black cat is sleeping on the …，训练文本接着出现 sofa。模型分给 sofa 的概率越低，这一步的交叉熵损失越大。对许多文本位置平均，得到语言建模 loss。

Loss 下降说明模型更善于为所测文本分配预测概率，不能直接转换成问答准确率或统一的智能增长比例。具体任务仍要另外评价。[^loss]

Kaplan Figure 1 分别观察计算量、数据量和参数量与测试 loss 的关系，前提是其他因素尚未成为严重瓶颈。资源和 loss 取对数后，在所测范围内近似形成直线，即幂律关系。[^kaplan-curves] 后续取得相同的绝对改善，往往需要更多资源；这个经验趋势不能无限外推到零损失。

拟合的用途是估计更大投入的收益，再选择值得放大的方案。[^episode-scope] 换数据、架构或进入远超已测的规模，需要重新检查；平均 loss 曲线也无法直接保证某个任务会突然获得新能力。原文明确讨论了理论解释、外推和训练设置的限制。[^kaplan-limits]

<a id="kaplan-allocation"></a>

## 3. Kaplan：更大模型可能更省训练样本

在所测范围内，较大模型到达同一目标 loss 所需的训练样本更少。每个样本计算更贵，但样本数的减少仍可能降低总计算。[^kaplan-efficiency]

因此，固定一个小模型练到几乎不再改善，未必是预算最优方案。换一个较大模型、训练到较早阶段，就可能用更少计算到达相同效果。“固定模型能练到多好”与“允许选择模型大小时怎样最省计算”是不同问题。

论文的效率前沿拟合更偏向增加参数。Figure 14 用约数说明：预算增加 **10 倍**，较优模型约大 **5 倍**，处理数据约多 **2 倍**；更细的增长指数约为 **0.73／0.27**。[^kaplan-allocation] 指数描述规模随预算增长的关系，不是两个预算支出的百分比。

固定预算仍有较优模型规模，太大也会因训练不够而吃亏。数据也需要增加，否则过拟合和信息不足会限制收益；避免有限数据过拟合的配比，与固定计算预算最优的配比不能直接互换。[^kaplan-data]

研究由 Jared Kaplan、Sam McCandlish 主导，Tom Henighan 做 LSTM 实验，Tom Brown、Rewon Child、Scott Gray、Alec Radford 建设 Transformer 实现，Jeff Wu、Benjamin Chess、Radford 处理文本数据，Dario Amodei 提供指导。[^kaplan-people] 比较很多规模需要数据、实现和统一的实验问题共同配合。

<a id="chinchilla-method"></a>

## 4. Chinchilla 怎样重测最优配比

2022 年，许多大模型参数不断增长，训练量却仍在约 **3,000 亿 token** 附近。Chinchilla 作者据此检验：相同计算预算下，缩小模型、多训练一些文本是否更好。[^chinchilla-intro]

团队训练了 **400 多个模型**，摘要给出的范围为约 **7,000 万到超过 160 亿参数**、**50 亿到 5,000 亿训练 token**，同时改变模型规模与训练时长。[^chinchilla-grid]

### 短训练需要自己的学习率安排

一项原本计划长期运行的训练，在某个中间点的成绩，未必等于认真安排的短训练终点。如果短训练的学习率已降下来，而长训练到这里还在较大步幅更新，两者即使处理相同 token，也可能状态不同。

Chinchilla 为不同目标训练量匹配学习率衰减周期，同时扩大比较的模型范围。作者将旧估计的差异部分归因于这些实验安排，不能只用一个学习率技巧解释全部变化。[^schedule]

### 三种估计方法

团队从三个角度寻找较优搭配：

- 从多条训练曲线取下包络：在某个计算量处，找出最低 loss。
- 做 IsoFLOP 对照：固定总计算量，让不同大小模型各自训练到预算结束。
- 拟合参数量、训练量与 loss 的共同关系，再在固定预算下求较优组合。[^three-methods]

第三种方法将损失写成一个经验形式：

```text
L(N, D) ≈ E + A/N^α + B/D^β
```

`N` 是参数量，`D` 是累计训练 token；`E`、`A`、`B` 和指数 `α`、`β` 都由实验拟合。`E` 预期表示文本分布本身的不确定性，另外两项分别描述有限容量及有限训练造成的差距。[^loss-decomposition]

例如黑猫睡在 sofa、bed 或 floor 都可能是合理后续，前文未必能唯一确定真实下一词。更大模型可以缩小容量差距，更多训练可缩小训练差距，却不能消除文本固有的不确定性。三项是用于拟合的模型，并非在网络内部直接测得的三种独立误差。

对 Gopher 的预算，三种方法预测较优规模约为 **670 亿、630 亿和400 亿参数**。最终选择 **700 亿**，还考虑了数据可用性与实际计算效率。[^predicted-range] 这里有估计区间和工程选择，并非公式精确算出唯一答案。

讲义第 28 页下方来自 Chinchilla Figure 2 左图：同一预算处比较各曲线高低，才是在选择搭配。较大模型最终 loss 更低，不表示它在每个预算处都最划算。[^lecture-figures]

<a id="equal-scaling"></a>

## 5. 接近等比例增长的含义

三种拟合的参数／训练量指数分别约为 **0.50／0.50、0.49／0.51、0.46／0.54**，都更接近均衡增长。[^equal-scaling]

用 0.50／0.50 近似：参数和训练 token 都翻倍，总计算约为四倍；预算只翻倍时，两者各约增至 **1.41 倍**。这是预算增长时的趋势，与固定预算内选择模型是两种用法。

常见的“每参数约 20 个训练 token”来自全局总量之比：Chinchilla 的 **1.4 万亿 token ÷700 亿参数＝20**。[^token-ratio] 它没有为每个权重单独分配二十个 token，也不是上下文长度或模型训练完成的统一标准。不同数据、结构和目标都可能改变配比。

<a id="gopher-experiment"></a>

## 6. 大规模训练怎样验证预测

论文在所述相同训练 FLOPs 下比较：

| 模型 | 参数量 | 累计训练 token |
|---|---:|---:|
| Gopher | 2,800 亿 | 3,000 亿 |
| Chinchilla | 700 亿 | 1.4 万亿 |

参数缩至四分之一，训练量约增到 **4.7 倍**。这里采用论文的 1.4 万亿，DeepMind 官方博客另写 **1.3 万亿**，两种口径保留区别。[^gopher-comparison]

用参数量乘 token 的简式，两个乘积并不严格相等。论文还按结构计算其他项，并在 Appendix F 修正了 Gopher 的 FLOPs 估计。[^compute-definition] 因此同预算是论文的计算口径，不代表设备天数或账单完全相同。

| 任务 | 设置与指标 | Gopher | Chinchilla |
|---|---|---:|---:|
| MMLU，57 个学科任务 | 5-shot 平均准确率 | 60.0% | 67.6% |
| LAMBADA，预测末词 | zero-shot 准确率 | 74.5% | 77.4% |
| PIQA，物理常识选择 | zero-shot 准确率 | 81.8% | 81.8% |

MMLU 增加 **7.6 个百分点**，LAMBADA 改善，PIQA 持平。[^task-results] MMLU 内部还有差异：**51 项改善、2 项持平、4 项退步**，退步项是大学数学、计量经济学、道德情境和形式逻辑。[^mmlu-limits]

大模型对照也同时改变了训练配置：MassiveText 来源采样比例、Adam 到 AdamW、tokenizer 的文字规范化方式，以及优化器状态中较高精度的权重副本。小规模实验表明这些改动自身也有影响。[^training-confounds] 大量规模实验、三种拟合和这次验证共同支持更好的预算搭配，却不能把分数差距全归给多读数据。

两模型无提示生成文本的自动毒性分数差异很小，偏见测试的改善也不均衡。语言预测的进步还不足以代替助手行为和安全评价。[^toxicity]

<a id="undertraining-and-data"></a>

## 7. 训练不足与重复数据

Chinchilla 保留了 Kaplan 的判断：优化一次训练的计算效率，通常无需把每个模型练到自身的最低可能 loss。分歧是应当选多大、训练多长。所谓当时的大模型训练不足，主要指规模与训练量失衡，同预算重新分配可能更好，而非要求给选定的大模型无限追加计算。

重复数据会增加累计 token，但未必增加独立信息。Chinchilla 的缩放分析主要在不到一遍整体语料的范围内展开，将多轮重复训练留为后续问题；最终模型按来源混合采样，却确实重复了部分子集：MassiveWeb 约 **1.24 遍**，Wikipedia 约 **3.40 遍**。[^data-repetition] 这两种统计范围需要区分。

错误、重复或含测试内容的数据，也不能仅凭数量视为有效资源。作者同时提出数据质量、污染、偏见和隐私等问题。[^chinchilla-limits]

<a id="training-and-serving"></a>

## 8. 把长期使用成本加进来

训练最优比较一次固定 FLOPs 下的最终 loss。模型部署后，每次回答还有计算、显存和延迟成本。Kaplan 附录已指出考虑推理时较小模型可能更合适，Chinchilla 也强调小模型的推理和后续微调负担更低。[^inference]

[推测] 高频使用时，团队可能愿意让较小模型多训练一些，以一次额外投入换取长期较低的调用成本。是否值得取决于预计用量、质量要求和硬件，不能只凭 20 token／参数决定。

训练时多看数据、单次请求提供更长上下文、回答时使用更多计算，作用位置不同。本章主要研究第一种投入与参数量的搭配，不能直接拿它判断提示长度或 Agent 上下文配置。

<a id="people-and-next"></a>

## 9. 预算计划还需要数据与系统执行

Chinchilla 将 **Jordan Hoffmann、Sebastian Borgeaud、Arthur Mensch、Laurent Sifre** 列为同等贡献，四人也署名官方博客。原文没有逐人列出数据、理论或系统分工，本章不另行分配；可确认训练使用 TPU、JAX 和 Haiku。[^chinchilla-people]

小规模实验帮助选择投入方向，实际训练仍要准备数据、安排采样，并让模型状态和计算任务在设备上运行。[下一章 ZeRO](AI演义_11_ZeRO_多卡怎样分担训练显存_科普讲解_20261105.md)将讨论权重、梯度和优化器状态怎样分布。ZeRO 早于 Chinchilla，这里的连接按问题组织。

训练稳定性还需要检查点和故障处理，缩放曲线并不保证某次运行不会出错。播客中的具体故障次数或不同公司对比没有另行核实，未纳入结论。

<a id="questions"></a>

实际安排下一组实验，可以固定预算和学习率收尾条件，比较模型与训练量，再看目标任务是否跟随 loss 改善。如果模型将长期提供服务，就把推理成本一同计算。两篇论文提供的是这些决策的实验方法，而非永久不变的配比。

<a id="source-scope"></a>

## 来源与修订范围

本次沿用原稿对 [Scaling Laws for Neural Language Models](https://arxiv.org/pdf/2001.08361v1)（2020-01-23 v1）及 [Training Compute-Optimal Large Language Models](https://arxiv.org/pdf/2203.15556v1)（2022-03-29 v1）正文和相关附录的阅读记录。[DeepMind 官方解读](https://deepmind.google/blog/an-empirical-analysis-of-compute-optimal-large-language-model-training)发表于 2022-04-12，训练 token 数与论文的差异已保留。

[讲义第 28 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=28)和[第117期播客](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)提供问题线索，相关转写约 **01:56:17–02:04:10**。[^episode-scope] 未人工听校，整期末尾约 16 秒覆盖仍未确认；本次也没有复现训练。

两篇的规律受各自数据与训练条件限制。Chinchilla 在大尺度上只有 Gopher、Chinchilla 两个可比训练点，效率前沿已有曲率，更远外推可能改变结果。[^chinchilla-limits]

## 来源与延伸阅读

[^kaplan-intro]: Kaplan et al.，[原论文](https://arxiv.org/pdf/2001.08361v1#page=1)，摘要、§1、§6。研究对象为语言建模 loss 与规模、预算关系；不能直接推广为所有能力的规律。
[^chinchilla-intro]: Hoffmann et al.，[原论文](https://arxiv.org/pdf/2203.15556v1#page=1)，摘要、§1–§2。论文保留“训练计算最优通常不要求模型训练到自身收敛”的判断，重测参数与训练量的分配。
[^compute-definition]: Kaplan，[§2.1](https://arxiv.org/pdf/2001.08361v1#page=6)；Hoffmann，[Appendix F，pp.27–28](https://arxiv.org/pdf/2203.15556v1#page=27)。常用近似为 FLOPs ≈ 6 × 参数量 × 训练 token 数，系数包含前向与反向计算。Kaplan 的参数与计算口径排除 embedding；Chinchilla 包含 embedding 并按结构计算其他项，其附录将 Gopher 先前的约 5.76×10²³ FLOPs 估计修正为约 6.3×10²³。近似式不等于设备耗时公式，也不宜直接套在长上下文或稀疏激活模型上。
[^loss]: Kaplan，[§1–§2，pp.2–7](https://arxiv.org/pdf/2001.08361v1#page=2)。论文明确使用语言建模交叉熵损失；黑猫续词为本文教学例子。
[^kaplan-curves]: Kaplan，[Figure 1，p.3](https://arxiv.org/pdf/2001.08361v1#page=3)与 §1.2。三个单因素趋势有其他因素不成为瓶颈的前提；具体拟合与 WebText2、tokenization 等设置有关。
[^kaplan-limits]: Kaplan，[§6.3–§8，pp.17–19](https://arxiv.org/pdf/2001.08361v1#page=17)及 [Appendix C，pp.22–23](https://arxiv.org/pdf/2001.08361v1#page=22)。缺乏完整理论、长期外推、长上下文计算项和超参数等均有局限；本文不把远尺度预测写成已实现事实。
[^kaplan-efficiency]: Kaplan，[§1.1、Figures 2–3，pp.3–4](https://arxiv.org/pdf/2001.08361v1#page=3)；[Appendix B.3–B.4，p.22](https://arxiv.org/pdf/2001.08361v1#page=22)。样本效率指达到指定效果所需的数据量，不代表大模型每 token 的计算更低。
[^kaplan-allocation]: Kaplan，[§6、Figures 12–14，pp.14–16](https://arxiv.org/pdf/2001.08361v1#page=14)。0.73／0.27 是对计算效率前沿的近似增长指数，含 batch 效率调整；图 14 用约 5 倍模型／2 倍数据解释 10 倍计算的分配。固定预算仍有最优模型大小。
[^kaplan-data]: Kaplan，[§4，pp.10–12](https://arxiv.org/pdf/2001.08361v1#page=10)。有限语料与模型规模的共同变化影响过拟合；这部分的数据配比目标与 §6 的固定计算预算最优问题不同。
[^kaplan-people]: Kaplan，[首页 Contributions](https://arxiv.org/pdf/2001.08361v1#page=1)。本文按论文写明的研究、LSTM、Transformer 实现、数据与指导分工叙述，不补未核实的组织动机。
[^chinchilla-grid]: Hoffmann，[摘要与 §3](https://arxiv.org/pdf/2203.15556v1#page=1)。超过 400 个模型；范围按摘要的 70M 至超过 16B 参数、5B–500B tokens 表述，不把这个扫描范围当成最终 70B 模型规模。
[^schedule]: Hoffmann，[§2，p.3](https://arxiv.org/pdf/2203.15556v1#page=3)、[§3.1，p.5](https://arxiv.org/pdf/2203.15556v1#page=5)与 [Appendix B／Figure A1，pp.22–23](https://arxiv.org/pdf/2203.15556v1#page=22)。学习率周期与目标训练长度匹配；论文将旧估计的差异部分归因于训练时长与扫描尺度，本文将其作为作者诊断，不写成单一因素完全解释。
[^three-methods]: Hoffmann，[§3.1–§3.3、Figures 2–4，pp.5–7](https://arxiv.org/pdf/2203.15556v1#page=5)。下包络比较训练曲线上的最低 loss；IsoFLOP 比较等计算预算下的最终 loss；参数化方法拟合模型大小与训练量的共同关系。
[^loss-decomposition]: Hoffmann，[§3.3，式（2），p.6](https://arxiv.org/pdf/2203.15556v1#page=6)：拟合的三项分别为 E、A/N^α、B/D^β。N 是参数量，D 是累计训练 token 数；E、A、B、α、β 是待拟合的系数，E 预期对应自然文本的熵。后两项分别描述有限容量及有限优化步带来的差距，不是可脱离假设逐项测得的真实误差；黑猫的多个合理续词为本文教学解释。
[^predicted-range]: Hoffmann，[§3.1–§3.3，pp.5–7](https://arxiv.org/pdf/2203.15556v1#page=5)及 [§4，p.9](https://arxiv.org/pdf/2203.15556v1#page=9)。三种估计约为 67B、63B、40B；最终在约 40B–70B 范围较大端选 70B，考虑数据与计算效率。
[^lecture-figures]: [讲义第 28 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=28)；上方三联图来自 [Kaplan Figure 1](https://arxiv.org/pdf/2001.08361v1#page=3)，下方彩色曲线来自 [Chinchilla Figure 2 左图](https://arxiv.org/pdf/2203.15556v1#page=5)。图源按原页与原论文核对，不从讲义缩略图估取精确数值。
[^equal-scaling]: Hoffmann，[Table 2，p.8](https://arxiv.org/pdf/2203.15556v1#page=8)。两者各增约 1.41 倍、计算约增两倍，是以 0.50／0.50 及主要计算近似作的算术说明，不是第四组实测结果。
[^token-ratio]: Hoffmann，[Table 3，p.8](https://arxiv.org/pdf/2203.15556v1#page=8)、[§4，p.9](https://arxiv.org/pdf/2203.15556v1#page=9)与 [Appendix D.3，p.26](https://arxiv.org/pdf/2203.15556v1#page=26)。约 20 是训练量与参数量总数之比；不同拟合和外推范围的比值并非完全相同。
[^gopher-comparison]: Hoffmann，[Table 1，p.2](https://arxiv.org/pdf/2203.15556v1#page=2)及 [§4，p.9](https://arxiv.org/pdf/2203.15556v1#page=9)给出 Gopher 280B／300B tokens、Chinchilla 70B／1.4T tokens，并称同训练 FLOPs。[2022 年 4 月 12 日官方博客](https://deepmind.google/blog/an-empirical-analysis-of-compute-optimal-large-language-model-training)写 1.3T；本文以明确的论文口径为准。约 4.7 倍为 1.4T 除以 300B 的算术结果。
[^task-results]: Hoffmann，[Table 6，p.11](https://arxiv.org/pdf/2203.15556v1#page=11)、[Table 7，p.12](https://arxiv.org/pdf/2203.15556v1#page=12)、[Table 8，p.13](https://arxiv.org/pdf/2203.15556v1#page=13)。MMLU 采用主文和表 6 的 67.6%，摘要另写 67.5%，二者不混；60.0% 到 67.6% 为 7.6 个百分点。原文亦提醒语言建模评价可能受训练测试重叠影响。
[^mmlu-limits]: Hoffmann，[§4.2.2，p.11](https://arxiv.org/pdf/2203.15556v1#page=11)明确 4 项退步、2 项无变化，57−4−2 得 51 项改善。四项为 college_mathematics、econometrics、moral_scenarios、formal_logic。
[^training-confounds]: Hoffmann，[§4.1，p.9](https://arxiv.org/pdf/2203.15556v1#page=9)、[Appendix A，p.22](https://arxiv.org/pdf/2203.15556v1#page=22)与 [Appendix G，p.29](https://arxiv.org/pdf/2203.15556v1#page=29)。tokenizer 改动为不再进行 NFKC 规范化；前后向使用 bfloat16，优化器状态保留 float32 权重副本。附录展示这些训练配置对小规模模型的影响。
[^toxicity]: Hoffmann，[§4.2.7，pp.14–15](https://arxiv.org/pdf/2203.15556v1#page=14)。无提示样本的自动毒性分数差异很小；群体偏见测试的改善不均匀。自动分类器测得的毒性也不涵盖全部安全问题。
[^data-repetition]: Hoffmann，[§5，p.15](https://arxiv.org/pdf/2203.15556v1#page=15)与 [Appendix A，Table A1，p.22](https://arxiv.org/pdf/2203.15556v1#page=22)。分析所研究的训练范围与最终模型各子集的采样遍数要分开；不能据此认定重复数据无限有效。
[^chinchilla-limits]: Hoffmann，[§5，pp.15–16](https://arxiv.org/pdf/2203.15556v1#page=15)及 [Appendix E，p.27](https://arxiv.org/pdf/2203.15556v1#page=27)。两个大尺度可比训练点、效率前沿曲率、多轮数据和质量限制均由作者明确提出。
[^inference]: Kaplan，[Appendix B.4，p.22](https://arxiv.org/pdf/2001.08361v1#page=22)；Hoffmann，[§4，p.9](https://arxiv.org/pdf/2203.15556v1#page=9)。两篇都涉及较小模型的使用成本优势；长期调用量改变最优训练选择，是本文据此作出的条件性推测，没有给出部署实测或通用最优倍率。
[^chinchilla-people]: Hoffmann，[首页署名](https://arxiv.org/pdf/2203.15556v1#page=1)、[§4.1，p.9](https://arxiv.org/pdf/2203.15556v1#page=9)、[致谢，p.16](https://arxiv.org/pdf/2203.15556v1#page=16)与[官方博客](https://deepmind.google/blog/an-empirical-analysis-of-compute-optimal-large-language-model-training)。四人同等贡献可核，未见逐人任务分工；训练栈为 TPUv3／TPUv4、JAX、Haiku。
[^episode-scope]: [《张小珺Jùn｜商业访谈录》第 117 期](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)公开 shownotes 与本章转录。小实验指导大训练、训练与推理成本区别作为解释线索；数据是否耗尽、特定公司训练故障次数、组织是否掌握未公开结论等旁支没有另作一手核验。原始转录不作为本文的必读材料。
