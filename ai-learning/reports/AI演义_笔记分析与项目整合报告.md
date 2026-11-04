---
title: "《AI演义》深读：从关键论文看懂AI的发展路径"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-04"
quality_schema: "report-v2"
quality_tier: "flagship"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["ai_history", "representation_learning", "transformer", "pretraining", "scaling_laws", "multimodal", "generative_models", "alignment", "agentic_loop", "research_methodology"]
---

# 《AI演义》深读：从关键论文看懂 AI 的发展路径

谢青池的《AI演义》用51页串联了36个研究对象，从GPU编程讲到语言模型、图像生成和Agent。[^lecture] 这份报告沿着其中的关键转折展开：当时卡在什么地方，一项工作改变了什么，这个改变又怎样接到后来的研究。

可以先记住一条主线：**从数据中学出有用的表示，把表示变成可复用的能力，再让能力接受任务、反馈和环境检验。** 数据、算力与工程决定这条路能走多远；语言、视觉和生成研究则不断交换可用的部件。

这需要同时使用讲义提出的三个视角：

- **历史**：当时的问题、数据、硬件和评价条件是什么？
- **范式变迁**：研究者改变了什么做法，又保留了什么？
- **人和组织**：谁在怎样的研究与工程环境中，使这个改变变得可实施？

正文保留全部36个对象，重点解释机制和连接，几乎不展开公式。第一次阅读可顺着章节走；以后遇到新论文，可以用文末的[连接索引](#verified-connections)和[定位方法](#new-papers)回查。

<a id="route-map"></a>

## 先看总路线：能力怎样形成，又怎样被兑现

| 路线 | 问题怎样推进 | 在哪里与其他路线接上 |
|---|---|---|
| 计算与训练 | Brook降低GPU编程门槛；AlexNet把数据、网络和GPU结合起来；ResNet改善深网络的训练 | 残差连接进入Transformer；训练成本又引出分片、稀疏计算和任务适配 |
| 语言与任务 | Word2Vec复用词表示；GPT-1/BERT复用预训练网络；GPT-2/3用上下文表达任务 | 模型能接受任务后，InstructGPT研究回答偏好，CoT与ReAct研究使用过程 |
| 数据与规模 | Scaling Laws、Chinchilla研究预算分配；RefinedWeb处理数据；ZeRO、MegaScale处理训练系统 | 为语言和多模态训练提供条件；CLIP还能反过来帮助筛选图文数据 |
| 视觉与生成 | 视频研究处理运动；ViT复用Transformer；CLIP连接图文；扩散、LDM、DiT重组生成过程 | Stable Diffusion v1.4将潜空间扩散、文本条件和图文数据组合成具体模型 |

这些是相互穿插的问题线，日期和具体继承关系在正文中分别说明。例如ZeRO早于Chinchilla，GAN与扩散也有长期并行的探索。先抓住**每次改变的是哪一环**，再看方法之间怎样相接。

| 想先弄清的问题 | 阅读入口 |
|---|---|
| 算力怎样变成可用学习能力 | [第一部分](#conditions) |
| 语言模型怎样从部件变成通用接口 | [第二部分](#language) |
| 为什么大模型需要数据与系统共同配合 | [第三部分](#resources) |
| 会生成以后，为什么还要对齐、推理和行动 | [第四部分](#goals) |
| 语言、视觉与生成在哪里真正汇合 | [第五部分](#vision)、[第六部分](#generation) |
| 怎样用历史、范式和人物视角看完整条路线 | [第七部分](#lenses)、[第八部分](#connections) |
| 以后怎样定位一篇新论文 | [第九部分](#new-papers) |

<a id="basics"></a>

### 先约定几个会反复用到的词

| 词 | 在本文里怎样理解 |
|---|---|
| 参数、训练、推理 | 参数是模型中通过学习调整的数值。训练根据数据和目标更新它们；推理用已有参数处理输入。提示中多放几个例子，可以改变输出而不更新参数。 |
| 表示 | 把词、图像或其他输入转成便于模型处理的数值形式。好表示应保留任务需要的区别；Word2Vec的词向量、ViT的图块表示、LDM的潜表示各有用途。 |
| token | 语言模型处理文本的单位，可能是词、词的一部分或其他片段。训练tokens表示处理过多少这样的单位，不等于有多少篇文章，也不等于独立知识条数。 |
| 架构、训练目标 | 架构规定信息怎样流动和计算；目标规定训练鼓励什么结果。Transformer是一类架构，下一token预测和图像去噪是不同目标。同一种骨架可以服务不同目标。 |
| 预训练、后训练 | 预训练先学到可迁移的能力；后训练在已有基座上进一步适配任务或行为。本文的指令微调、偏好优化属于后者，具体阶段和数据要分别看。 |
| 损失、评价 | 损失是训练时优化的误差指标；评价检验模型在选定任务上表现如何。文本预测损失下降，与答案更受用户偏好，是相关但不同的问题。 |

这些区别贯穿后文：**改提示、改训练目标、改网络、改数据和改系统，作用的位置各不相同。**

<a id="conditions"></a>

## 一、把计算、数据与模型接起来：从硬件潜力到可学习表示

<a id="paper-brook"></a>

### 1. Brook：GPU 很快，为什么普通程序还不容易用上它？

GPU 原本面向图形处理。即使它具备很强的并行计算能力，非图形程序员也未必能直接使用：算法往往要被改写成纹理、着色器和一次次图形操作，还要处理不同硬件与图形接口的限制。

2004年的 **Brook for GPUs** 处理的是这道软件门槛。程序员以“数据流”描述一批数据，以“核”描述对数据执行的相似操作，以“规约”描述结果如何汇总；编译器和运行时再将这些表达映射到GPU。[^brook]

它没有发明一种新的学习算法，也没有让任意串行程序自动并行。它让一种硬件能力更容易成为通用计算资源，同时检验这层抽象在什么任务上值得使用。数据传输和调用开销仍可能抵消收益，所以某项计算核很快，不等于整个应用同样快。

Ian Buck 与 Stanford 团队的研究原型，后来进入GPU工业编程平台的发展路径。NVIDIA的历史回顾明确把Brook及Buck的工作与CUDA的演进联系起来。[^gpu-history] 这条连接说明，研究中的编程抽象怎样被继续做成更广泛可用的工业平台。

<a id="paper-alexnet"></a>

### 2. AlexNet：数据、模型和GPU为什么必须合在一起看？

当时卷积神经网络（CNN）已经有研究积累。它用可学习的滤波器在图像局部反复提取特征，再逐层组合。真正困难的是：现实图像变化多，足够大的标注数据逐渐可用，但更大的网络又带来训练时间、显存和过拟合问题。

2012年的 **AlexNet** 因而不是一个孤立技巧获胜，而是一套可运行组合：大规模图像数据、卷积网络、ReLU、优化过的GPU实现、数据增强和Dropout共同进入训练。原论文的主模型约有6000万参数，在两张各3GB显存的GTX 580上训练；显存和通信条件还影响了网络如何分布在两张卡上。[^alexnet]

这件事的历史意义，在于**从像素和标签中学习有用表示的方案，在大规模视觉基准上显示出很强竞争力**。手工设计的结构先验没有消失——卷积仍然利用图像局部性的假设——但越来越多的区分能力来自训练，而不只是预先编写特征。

多伦多团队中的Krizhevsky、Sutskever和Hinton，需要同时处理数据、网络和实现。只讲“一个聪明架构”，会漏掉训练条件；只讲“GPU终于够快”，又解释不了训练目标、结构和正则化为什么重要。

从这里分出的，不是一条“模型继续变大就行”的直线，而是至少两条问题线：**更大的网络能不能顺利学会？学会以后，部署时一定要运行同样繁重的模型吗？**

<a id="paper-resnet"></a>

### 3. ResNet：更有表达能力，为什么反而连训练集都学不好？

ResNet面对的是一个反常现象：加深普通网络后，不只是测试结果可能变差，训练误差也可能变高。理论上，新增层若学会近似不改变输入，深网络至少应能模仿浅网络；现实优化却未必能找到这样的解。

2015年的 **Deep Residual Learning for Image Recognition** 改变了层组的学习方式：保留输入的直接通路，让一组层学习“相对输入还需要做什么修正”，再把修正与输入相加。[^resnet]

它处理的是**表达能力与可训练性之间的落差**。不能简单把论文里的退化问题都归为梯度消失，更不能用“有残差，任意深度都更好”概括结果。论文也展示了极深网络能够拟合训练集、但测试泛化并未继续改善的情况。

微软研究团队通过plain与residual网络的对照，把问题从“层数不够多”转向“学习完整变换与学习残差，优化难度可能不同”。后来，Transformer明确采用并引用了残差连接。[^transformer] 这是一种重要的跨路线传播：**视觉模型中的可用组件进入序列模型，而不是整套CNN被原封不动搬过去。**

<a id="paper-distillation"></a>

### 4. 蒸馏：训练时最强的形态，未必是使用时最合适的形态

同在2015年，蒸馏论文处理另一类瓶颈。大模型或多个模型的集成可能预测得更好，但向大量用户提供服务时，运行它们的成本和延迟可能太高。

Hinton、Vinyals和Dean的 **Distilling the Knowledge in a Neural Network** 将“训练出能力”和“部署能力”拆开：先让强模型或集成产生监督，再训练一个更适合部署的学生模型。[^distill]

学生不必复制教师参数。真实标签只指出正确类别，教师的输出分布还可能透露哪些类别容易混淆。蒸馏让学生学习这类预测关系；它改变的是监督信息的来源和呈现方式。

这不是无损拷贝，学生容量、教师质量和迁移数据都会影响结果。但它打开了一种思路：**能力可以先在较昂贵的训练形态中获得，再尝试转移到另一种使用形态。** 原论文中的语音应用，使这个问题与真实服务需求发生联系；它并不是等到大语言模型出现后才产生的想法。

ResNet与蒸馏从这里分出两条路线：前者改善深网络怎样学，后者改变部署模型向谁学。训练时能充分利用大模型，使用时又能降低成本，两种追求可以同时成立。

<a id="language"></a>

## 二、语言路线的三次改写：复用表示、复用网络、复用能力

<a id="paper-word2vec"></a>

### 5. Word2Vec：先把能复用的语言部件学出来

语言任务常常缺少足够的专用标注，但原始文本可以很多。Word2Vec要解决的，不是第一次把词变成数字，而是怎样高效地从大语料中学到可供其他任务复用的词表示。

2013年的 **Efficient Estimation of Word Representations in Vector Space** 使用较简单的局部预测任务：CBOW用周围词预测中间词，Skip-gram从一个词预测周围词。大量局部预测共同调整词向量，使使用环境相近的词形成有用的关系。[^word2vec]

这时，主要被迁移的是**一张词表示表**。它不是每次出现都会随句子改变的完整上下文表示，也没有独自替代所有语言系统。研究团队对训练目标的简化和对训练基础设施的使用，共同使更大语料变得可处理。

后面的预训练模型会把这个问题继续往前推：能不能复用的不只是词向量，而是一整套处理上下文的网络？在此之前，先要看模型怎样处理长度不定、结构复杂的序列。

<a id="paper-seq2seq"></a>

<a id="paper-bahdanau-attention"></a>

### 6. seq2seq与Attention：先接通输入输出，再改变信息读取

翻译不是逐词替换：源句和译文可以长短不同、词序不同。循环神经网络（RNN）按顺序读取输入，并把状态传到下一步；LSTM是其中一种更善于控制信息保留与遗忘的结构。Sutskever等人的LSTM **seq2seq** 方案，用编码器读取源句，以固定规模状态交接信息，再由解码器逐步生成目标句。它让端到端直接翻译成为有竞争力的研究路线。[^seq2seq]

新的问题随之显现：生成不同目标词时，需要的源信息不同，是否都只能依赖一次性的整句交接？

Bahdanau等人的 **Attention** 方案保留源句各位置的上下文表示，让解码器每一步对它们重新打分、加权汇总，取得当前更需要的信息。[^bahdanau] 改变的是访问方式：从一次性交接整句，转向生成过程中持续读取相关源表示。

这是问题的递进，不应伪装成两篇论文严格的发表接力。Bahdanau论文的首次公开提交略早于上述seq2seq论文，两者都处于当时的编码器—解码器研究环境中。

Attention也没有取消RNN：编码和解码仍沿状态链推进。它改善了源信息的读取，却留下另一个问题——**序列表示本身，是否必须这样逐位置递归计算？**

<a id="paper-gnmt"></a>

<a id="paper-transformer"></a>

### 7. GNMT与Transformer：部署改造和架构改造是两种回应

2016年，吴永辉（Yonghui Wu）等作者的 **GNMT** 将深层LSTM、Attention、残差、WordPiece、并行实现和低精度推理等技术组织成翻译系统。它仍是循环编码器—解码器，不是Transformer。[^gnmt]

它面向的障碍很具体：训练和推理速度、罕见词、漏译，以及自动指标的改善是否真的对应用户感知。Google的研究团队和翻译服务团队因而不能只优化一张离线成绩表；硬件与服务约束会反过来影响架构选择。

2017年的 **Transformer** 则进一步改变计算组织：用self-attention构造序列内部表示，不再依赖同样的逐位置递归链；同时保留生成端读取源序列的Attention。[^transformer]

远处位置可以更直接地交换信息，训练时多个已知位置可以并行计算。不过，未来输出未知时，原始模型的自回归生成仍需逐步进行。去掉RNN，不等于生成整段答案时不再有前后依赖。

GNMT和Transformer不是谁必须先成为谁的完整祖先。它们在同一片问题环境中分别展示了**工程化已有架构**与**改变架构依赖**的价值。组件也会跨过项目边界：BERT论文的WordPiece采用明确引用了GNMT。[^bert] 发展史里经常迁移的是一个部件或一种接口，而不是一整台模型按代替换。

<a id="paper-gpt1"></a>

<a id="paper-bert"></a>

### 8. GPT-1与BERT：可迁移对象从词表扩展为网络，目标开始分叉

有了能处理上下文的网络，下一问是：能否先从原始文本中把这种能力学出来，再用较少标注适应具体任务？

2018年的 **GPT-1** 用下一token预测预训练Transformer解码器，再利用每个任务的标注更新网络。任务差别更多通过输入如何组织和输出层如何使用表达，不必为每个任务重新设计一套大架构。[^gpt1]

被复用的已经不只是一张词表，而是**处理上下文的多层网络**。但这时仍主要依赖监督微调：同一个预训练起点，不等于所有任务都使用同一套冻结权重。

**BERT** 共享预训练—微调的总体问题，却采用另一种信息条件：在恢复被选中的词片时，利用左右两侧的上下文；另用句对任务学习特定关系。[^bert]

两条路线的分叉在于**训练时允许看见什么，随后准备怎样使用**：GPT根据已有内容继续生成，BERT从左右文中恢复被遮蔽的内容。前者自然适合逐步续写，后者适合利用完整输入做理解和判别；它们的评价任务也要分别看。

OpenAI与Google AI Language的作者组在不同目标下作出选择：希望从文本中学到什么、怎样使用学到的网络，决定了各自的训练问题。机构标签或某一次排行榜名次，不能代替这种区别。

<a id="paper-gpt2"></a>

<a id="paper-gpt3"></a>

### 9. GPT-2与GPT-3：任务能否通过上下文进入模型？

预训练减少了结构定制，但如果每来一个任务仍要准备标注并更新参数，使用成本并没有消失。

**GPT-2** 将不进行任务参数更新的迁移作为主要评估方式。模型仍预测接下来出现的文本，但前缀可以提示接下来的内容应是摘要、回答或翻译。[^gpt2]

它让**任务接口**成为新的重点：以前主要通过微调权重适配任务，现在可以尝试通过改变输入条件调用已有能力。这个转折不是“微调从此过时”。早期无梯度迁移仍有明显失败；论文中某些实验还使用了上下文示例，不能将其zero-shot用语机械套成后来更严格的“零示例”。

**GPT-3** 随后更系统地分开zero-shot、one-shot、few-shot与微调，跨模型规模和任务比较上下文示例的作用。这里的few-shot主要发生在输入条件中：提示里给几组例子，再给新问题，并不因此执行一次新的反向传播。[^gpt3]

这改变了使用方式，却没有消除预训练成本。最大模型的1750亿参数和3000亿训练tokens，以及高带宽集群，使“推理时只给几个例子”的能力成为可检验对象。少样本使用，不等于少样本训练。

于是，语言路线与资源路线明确汇合：想研究任务如何通过上下文被调用，还需要决定模型多大、数据多少、怎样完成训练。GPT-3论文直接使用Scaling Laws来指导资源配置，而不是仅凭“更大应该更好”。[^gpt3]

最后，一个尚未解决的问题开始变得突出：**能续写出像答案的文本，不等于会按用户真正想要的方式帮助用户。** 预测训练文本与遵循目标，不是同一个目标。这里将接到后训练与行动路线，而不是给已经完备的模型随便套一个聊天界面。

<a id="resources"></a>

## 三、资源线横穿主线：从模型方案到可兑现的训练

<a id="paper-scaling-laws"></a>

<a id="paper-chinchilla"></a>

### 10. Scaling Laws与Chinchilla：先决定预算应该花在哪里

在密集语言模型训练中，参数更多，处理每个token通常也需要更多计算。训练预算固定时，模型规模和可处理的训练量之间存在交换关系。

**Scaling Laws** 将这类决策推进为可预测的实验问题：在一定范围与条件下，模型、数据和计算规模与语言建模损失呈现较规律的变化。它进一步提出，当时的有效预算分配可以偏向较大模型、较短训练，不必将每个模型训练到自身收敛。[^kaplan]

**Chinchilla** 保留了经验缩放和预算优化的思想，却通过同时改变模型规模与训练时长、匹配学习率计划等实验，重新标定分配比例。它强调，预算增加时，参数和训练tokens需要更均衡地共同增长。[^chinchilla]

二者的关系是**在同一个资源配置问题上，新的测量改变了建议**。Chinchilla论文给出一个直观对照：在与Gopher相同的训练计算预算下，把模型从2800亿参数减到700亿，同时把训练量从3000亿tokens增到1.4万亿tokens，所报告的多项下游评价反而更好。[^chinchilla] 这个实验改变的是参数与训练量的搭配，不是单独证明“小模型更好”；这里的计算预算也不等于运行时间或采购费用完全相同。

这里的关键转折是：AI的扩大不再只有一个参数数字，而是一组需要匹配的资源。接下来，工程与数据研究要回答，这种匹配在现实中怎样实现。

<a id="paper-zero"></a>

### 11. ZeRO：多加GPU，为什么还可能放不下训练？

普通数据并行让不同GPU处理不同样本，却可能在每张卡上保留一整套参数、梯度和优化器状态。工人多了，并没有自动减少每个工人要保管的那份状态。

**ZeRO** 将状态管理从“各卡都存完整副本”改为“各卡负责一部分，用时通信协调”。它逐步分片优化器状态、梯度和参数，在显存与通信之间寻找可用的组织方式。[^zero]

它不改变语言模型应该预测什么，也不压缩掉模型本身的能力；它改变的是**训练方案能否放得下**。激活、缓冲和碎片等还需要另外处理，不能把模型状态的节省直接当作整个GPU峰值显存的节省。

微软作者组将这类优化接入DeepSpeed，也使接口本身成为贡献：研究者不必为每次扩展都手动改写整套模型并行实现。这里的人的视角，是系统团队怎样把复杂性封装成可供其他研究者使用的训练条件。

ZeRO发表于2019年，不能按本章的讲述顺序写成Chinchilla催生了它。两者是不同层次的问题：**一项研究告诉你怎样配置资源更值得，另一项研究帮助这种配置成为可执行方案。**

<a id="paper-refinedweb"></a>

### 12. RefinedWeb：需要更多数据，不等于机械地堆网页

Chinchilla对训练量的重新强调，也把数据获取推到前台。**RefinedWeb** 的引言直接引用这项工作，接着问：需要可扩展的大语料时，质量是否一定来自书籍、论文等“精选来源”标签？[^refinedweb]

它通过正文提取、过滤与严格去重处理网页，再用训练对照检验效果。问题不再是先把来源划成高低等级，而是**经过什么加工的数据，在什么训练目标下有价值**。

去掉导航、模板和重复文本，能改变模型经常看见什么；但过滤也可能误伤有价值内容。去重不是删得越多越好，数据质量也不是与任务、训练量和评价无关的绝对属性。

这条连接把“数据要和模型一起扩展”落成了数据工程问题：可扩展的采集只是起点，还要检验清洗后的材料究竟让模型学到了什么。

<a id="paper-laion5b"></a>

### 13. LAION：模型开始参与数据建设，数据再反过来支持模型

图文模型面对类似问题，但数据质量标准不同。网页上的图片与说明文字并不总是匹配；大规模低成本配对，需要某种筛选机制。

**LAION-5B** 利用已有CLIP模型的图文匹配能力筛选候选配对，并开放数据索引、分数与配套工具。这里形成了一条值得在总图里画出的回路：**已有模型帮助整理数据，数据再支持训练和检查新的模型。**[^laion]

它不是原始CLIP的训练数据，也不是发布了一个新的图像生成器。它改变的是外部研究者能否取得、重跑和调整训练条件。OpenCLIP在明确LAION子集上的训练，为这条回路提供了具体证据。

开放同样依赖资源。论文的作者贡献和致谢展示了采集管道、训练评估、社区协作、资助及超级计算资源如何共同工作。把它讲成某位个人凭热情独自完成一切，会漏掉“谁能参与研究”背后的真正条件。

同时，模型筛选会带入模型自己的盲点；数据索引的开放许可也不等于获得每张图片的版权。开放训练条件提高可检查性，却不是自动消除偏差和权利问题。

CLIP如何学会图文匹配，将在多模态路线中展开；这里先看到它作为数据建设工具的作用。

<a id="paper-megascale"></a>

### 14. MegaScale：算力不仅要买到、用上，还要连续变成进度

当一个训练作业占用万余GPU并持续数周，问题进一步变化：通信、同步、数据加载和故障，都可能让名义上的算力变成等待。

**MegaScale** 在模型与系统之间联合设计，将并行组织、通信重叠、数据管道、观测、故障隔离和恢复放在一起考虑。它的正文明确讨论了ZeRO状态分片及相关通信组织。[^megascale]

因此，“放得下”之后还有“跑得快、跑得久、坏了能继续”。某个训练步骤很快，不等于整个项目可以按相同速度稳定完成；硬件规模很大，也不等于利用率和可靠性天然很好。

ByteDance与北京大学作者组的生产系统工作，提供了与小规模模型实验不同的观察条件：真实集群会出现慢节点、同步等待和故障，系统必须能定位它们。资源规模改变了工程团队必须面对和能够实测的问题。

至此，资源线的作用已经很清楚：**规模研究决定值得做什么，内存与并行组织决定能否做，数据工程决定拿什么来学，运行系统决定能否持续学完。** 它们不是模型论文之外的附录，而是能力成为现实的条件。

<a id="paper-sparse-moe"></a>

### 15. 稀疏MoE：增加容量，是否必须每次运行全部参数？

资源问题也能通过改变模型的计算组织来回答。这里需要回到2017年1月：这篇稀疏MoE论文使用的语言系统仍然包含LSTM，早于Transformer的公开发表，不能把它写成Transformer做大以后才出现的发明。

它把一层组织成多个专家子网，由学习到的门控为每个输入选择少数专家，再合并结果。这样，总参数容量可以增加，而每个输入不必运行全部专家。[^moe]

但理论上的少算，不自动变成GPU上的快。不同输入被分给不同专家，会使每位专家拿到的小批量变小；路由若失衡，有的专家忙、有的闲；跨设备取送数据又会产生通信开销。论文因此同时研究路由、负载均衡、批量和分布式计算。

把它与Brook并置，能看到同一个工程问题以不同形式回来：**可并行的计算，还必须具有适合硬件的粒度和数据组织。** MoE扩大的是可用容量，不是证明总参数可以免费增长，也不保证任何小批量在线服务都同样快。

<a id="paper-lora"></a>

### 16. LoRA：每个任务都得重新更新一整套大模型吗？

共享预训练模型成为起点后，又出现了使用侧的问题：为许多任务分别全量微调、维护梯度和优化器状态，并保存独立大权重，成本可能很高。

2021年的 **LoRA** 冻结基座，学习一个用较少参数表达的任务增量。低秩约束作用于“更新”，不是把整个预训练模型压成一个小模型。[^lora]

因此，少的是大量权重更新相关的状态和每任务增量，基座本身仍然需要参与计算。对于固定任务、可合并的线性更新，增量可事先合入原权重，推理时不必额外运行那条支路；动态多任务等场景则不能直接沿用同样的零额外支路开销结论。

到这里，几条常被放进同一“效率”篮子的路线，实际上各有目标：

| 方法 | 主要重新安排什么 |
|---|---|
| 蒸馏 | 训练与部署采用的模型形态、学生的监督来源 |
| ZeRO | 训练状态在设备间怎样存放与协调 |
| 稀疏MoE | 每个输入实际动用哪些专家计算 |
| LoRA | 适配任务时更新和保存哪些参数 |

它们不是互相取代的四代压缩技术。节省哪笔成本、发生在训练还是使用、依赖哪些系统条件，才决定它们怎样接入完整模型路线。

<a id="goals"></a>

## 四、从预测文本到完成目标：训练、推理与行动的分叉

<a id="paper-alphago-zero"></a>

### 17. 先回看AlphaGo Zero：模仿得像，不等于完成目标更好

要理解这个区别，可以回看2017年的 **AlphaGo Zero**。围棋是一个规则明确、状态可模拟、终局可判定的环境。这不是大语言模型的上一代，而是一个有清晰反馈的对照场景。[^alphago]

网络预测哪些落子值得看、局面有多好，搜索再试探可能分支，形成更强的落子选择；自我对弈的胜负和搜索结果又回到训练中。学习与搜索由此互相加强。

这项工作移除了对人类棋谱起步的依赖，但没有移除规则、网络结构、对称性和评价方式等人的设计。论文中，人类监督的对照可以更会预测职业棋手怎样落子，自弈系统却可以下得更强。**拟合已有行为，与实现任务目标，并不等价。**

把这个问题带回语言模型时，困难也立即改变了：围棋有明确终局，开放语言任务却未必有一个所有人都认可、程序也能准确判定的“好答案”。因此，两条路线可以作主题对照，不能只凭自弈与推理两个词，就画成“AlphaGo Zero直接导致LLM thinking”的历史箭头。

<a id="paper-instructgpt"></a>

### 18. InstructGPT：谁来定义值得产生的回答？

GPT-3能够通过上下文表现出任务行为，但下一token预测仍主要要求模型符合训练文本的分布。互联网里“接下来可能出现什么”，与用户需要的“怎样才算有帮助、真实而合适”，不是同一个目标。

2022年的 **InstructGPT** 在GPT-3基座上继续训练：先用示范建立回答方式，再让标注者比较输出，训练奖励模型近似这些偏好，最后通过优化更新回答策略。[^instruct]

新的信息来自**示范与比较反馈**，它们改变了模型更倾向于产生什么回答。论文中，13亿参数的InstructGPT回答比1750亿参数的GPT-3更受评价者偏好，说明使用价值不只由参数规模决定；这个结果衡量的是指定提示分布和评价人群的回答偏好，不能直接扩展成全部知识与能力的比较。

人的位置在这里也改变了。除了论文作者，还有写示范、比较答案的标注者，以及制定指南和选择提示分布的团队。偏好数据反映的是这些条件下的判断，不是对全人类价值或所有事实的直接测量。更会服从也不自动等于更安全，模型仍可能产生错误、有害或带偏见的回答。

<a id="paper-cot"></a>

### 19. CoT：不改参数，也可以改变调用能力的方式

同在2022年，Jason Wei等Google研究者的 **Chain-of-Thought Prompting** 工作研究另一条路径：在提示中提供包含中间步骤的示例，让模型先生成中间过程，再给出答案。它改变的是推理时的输入和生成组织，不要求为这套提示实验再微调模型。[^cot]

中间步骤会成为后续生成的上下文，使多步问题不必在没有可见中间结果的情况下直接跳到最后答案。但“多写一些token”本身不保证收益，论文的对照并不支持只输出无信息符号也有同样效果。

因此，后训练和CoT不应排成互相替代的前后两代：**一条改变模型如何被训练，另一条改变已有模型如何被使用。** CoT的收益也受模型、任务和示例影响，中间文字既可能帮助完成任务，也可能把错误继续传下去。

<a id="paper-react"></a>

### 20. ReAct：思考过程怎样被环境纠正？

只在上下文里继续推理，缺少的事实不会凭空出现；只生成动作，又可能缺少任务拆解和进度判断。

姚顺雨（Shunyu Yao）、Karthik Narasimhan及合作作者的 **ReAct** 将语言推理、任务动作和环境观察交错组织：推理指导查什么或做什么，动作执行后的真实返回再进入上下文，改变下一步。[^react]

关键变化是从“给出一份答案”转向**维护一个能被外部观察修正的过程**。写出“我已经查到”不是实际查询；模型输出动作，工具或环境执行，然后才有观察结果。交互本身也不等于强化学习——原论文主要提示实验可以在不更新模型参数的情况下运行。

ReAct沿用并组合了此前的推理与交互思路，不是Agent概念的诞生。它在不同任务上的结果也并非总胜过CoT；检索失败、推理错误和重复动作依然可能让过程失败。

到这里，三项职责必须分开：**训练目标决定偏好什么行为，推理组织影响怎样利用计算，环境交互提供新的信息。** 任何一项都不能包办另外两项。

<a id="paper-tulu3"></a>

### 21. Tülu 3：从方法名词，走向可检查的后训练配方

知道监督微调（SFT）、偏好优化和强化学习的名称，仍不足以重做一个有用的助手。需要知道哪些数据用于哪个阶段，反馈由谁产生，评价怎样组织，以及提高一项结果是否损害另一项。

Nathan Lambert等作者在2024年公开的 **Tülu 3** 将这些问题作为开放后训练研究的一部分。本文所读的2025年修订版，按数据策展、SFT、偏好优化、RLVR组织配方；若只数更新模型的训练阶段，则是后三项。其模型基座是Llama 3.1，不是GPT-3权重的后续版本。[^tulu]

这些阶段使用的信号不同：SFT学习范例；直接偏好优化（DPO）使用比较数据调整输出偏好；可验证奖励强化学习（RLVR）针对能够程序化检查的任务结果提供奖励。偏好不是普遍真值，最终答案通过检查也不等于整段推理每一步都正确。

这里的人和组织不只体现在署名中。数据合成、模型评审、训练设施、评价和发布各有分工。与LAION开放训练数据条件类似，Tülu 3将后训练配方展开，使外部研究者更有机会检查和继续研究；开放材料本身却不等于本报告已经独立复现其全部结果。

它也把几条路线重新接到一起：推理示例可以进入训练与评价，可核验结果可以进入参数优化，工程系统让这些阶段运行起来。**提示方法、训练算法、数据配方和评价方式，是可以相互配合但必须分别说明的层次。**

<a id="vision"></a>

## 五、视觉与语言的会合：输入单位、监督与任务接口

<a id="paper-deepvideo"></a>

### 22. DeepVideo：多给一些帧，为什么不自动等于理解运动？

图像CNN取得进展后，一个自然问题是：视频是否只是更多张图像？

2014年的 **Large-scale Video Classification with Convolutional Neural Networks** 比较了单帧和多种时间融合方式，并建设大规模视频数据来测试它们。它问的是如何从视频中得到用于分类的表示，而不是怎样生成视频。[^deepvideo]

多给几帧没有自动带来压倒性的优势，反而暴露了表示问题：场景外观、相机运动和真正的动作变化混在一起，模型未必能从这些输入中有效分离它们。数据量和计算让实验可做，却不能替代输入与结构的选择。

Google与Stanford的合作在这里对应具体研究条件：收集视频、组织标签、承担训练，并比较时间连接方式。后来的职业经历不需要成为这项工作的解释；更重要的是，它把图像成功带到一个更复杂输入上，测试出了新的问题。

<a id="paper-two-stream"></a>

### 23. 双流网络：把运动先作为一种输入，而不是要求模型同时学会一切

同年的 **Two-Stream Convolutional Networks** 明确讨论了上述视频路线。它用两路网络分别处理外观和运动：一路看RGB帧，另一路看从连续帧估计的光流，最后融合分类结果。[^two-stream]

光流将哪里朝哪个方向移动显式呈现给网络。这样，在动作标注有限时，不必要求模型同时学会寻找对应点、估计运动、再识别动作；但它也引入了额外计算和前处理假设。

这让“手工方法到深度学习”的叙述变得更准确：**人类设计没有整体退场，而是在不同数据条件下，决定哪些结构先给模型、哪些关系留给训练去学。** 双流网络不是后来文生视频的直接祖先，而是动作识别路线中对运动表示的一种明确回应。

<a id="paper-vit"></a>

### 24. ViT：视觉与语言共享的是计算骨架，不是同一个任务

2020年公开的 **Vision Transformer** 问了另一类问题：能否尽量少改标准Transformer，就让它处理图像识别？[^vit]

图像不是单词序列，逐像素处理又可能很贵。ViT把图像切成图块，投影为向量序列，加上位置信息，再用Transformer编码器处理。这不是先把图像翻译成语言，而是为同一类计算骨架设计可用输入单位。

它减少了逐层写入的某些视觉结构偏好，更多关系需要从数据中学出来。原论文的大规模预训练结果很重要，而较小数据条件下未必优于CNN。**共享架构不等于不需要足够数据，更不意味着所有视觉任务自动统一。**

Transformer与ViT作者名单存在研究者交集，例如Jakob Uszkoreit；真正的技术连接则是ViT原文明确复用标准Transformer。人员与研究网络帮助我们追踪思路，架构和实验才说明具体继承了什么。

<a id="paper-clip"></a>

### 25. CLIP：让语言成为视觉任务的接口

即使视觉模型的骨架更通用，分类类别仍可能写死在训练标签里。**CLIP** 进一步问：自然语言能否既提供训练监督，又让用户描述新的分类任务？[^clip]

它联合训练图像和文本编码器，学习哪些图文相配。使用时，把候选类别写成描述，与图像表示比较，就能在不为这套类别重新训练分类头的情况下进行选择。

这里的会合不只是骨架：图像编码器可以采用ResNet或ViT，文本侧使用Transformer，而图文对比目标把两边连起来。它不是把现成GPT和现成ViT权重简单拼接，也不是把图像编码器变成生成器。

Radford、Sutskever等同时出现在GPT和CLIP相关作者名单中，而CLIP正文也明确借鉴语言领域的通用预训练和零样本任务问题。共同参与是线索；目标、接口与架构的讨论，才把线索连成可核对的方法关系。

CLIP再与前面的数据路线形成反馈：它可以帮助LAION筛选配对，开放的数据又支持OpenCLIP训练。但筛选会保留模型的盲点，零样本也不是从未见过相关概念。

到这里，语言与视觉已经在**架构、监督和任务接口**几个层面会合。下一问却仍需另答：能判断一张图与一句话是否匹配，怎样进一步产生符合要求的图像？这将进入另一条与识别并行发展的生成路线。

<a id="generation"></a>

## 六、生成路线的重组：训练信号、计算空间与网络骨干

前面的视觉任务主要问“这是什么”或“它与哪段描述相配”。生成任务换了目标：**能否产生符合某种数据规律或条件的新样本？** 这条线与识别长期并行，不能把它讲成视觉分类完成以后才出现的下一阶段。

<a id="paper-gan"></a>

### 26. GAN：能否把判别能力变成生成的训练信号？

2014年的 **Generative Adversarial Nets** 并未发明全部生成模型。它提出一种重要的训练组织方式：生成器从随机输入产生样本，判别器学习区分真实与生成样本；判别器给出的信号再用于改进生成器。[^gan]

这里不是先获得一个完美裁判，再让生成器服从它。两边都在变化，必须共同训练。判别学习的工具因此被用于另一种目的：不只是给样本分类，而是为产生样本提供学习信号。

它也留下了新的困难：双方的学习可能不同步，生成器可能损失多样性，生成质量的评估也不容易。原文的理想分析需要相应假设，不能当作实际训练必然成功的保证。

蒙特利尔的作者团队把已有的判别学习与生成建模积累组织成这一框架。它的作用是打开一条新的训练信号路线，而不是让概率建模的其他方法退出历史。

<a id="paper-diffusion-2015"></a>

### 27. 2015年的Diffusion：把困难生成拆成许多较小的逆问题

另一种想法来自逐步变化的过程：复杂数据可以被一点点扰动，最终接近容易处理的简单分布；反过来，是否可以学习每一步怎样恢复结构？

**Deep Unsupervised Learning using Nonequilibrium Thermodynamics** 将前向扩散与学习逆过程结合起来。生成时，从简单分布出发，沿学到的逆向小步逐渐构造样本。[^diffusion15]

它重写了问题：不要求一次完成复杂生成，而让模型学习一系列局部变化。恢复的是数据分布中的结构，并不是保证把某张加噪图片的唯一原件找回来。

这与GAN是在探索不同的训练组织方式。2015年论文引用并比较GAN，还使用了相关评估代码，但这种接触不证明GAN是扩散机制的直接前因。时间相邻、相互引用和评估工具共享，需要与方法继承分开。

<a id="paper-ddpm"></a>

### 28. DDPM：已有框架，怎样变成有竞争力的图像生成配方？

2020年的 **Denoising Diffusion Probabilistic Models** 直接承接早期扩散模型，再把重点推进到高质量图像生成。[^ddpm]

它通过噪声预测的参数化、简化训练目标、网络结构和具体训练选择，形成了有效的组合。训练时，可以抽取一个噪声级别，构造对应的带噪样本，让网络预测已知噪声；生成时，则依采样规则多步推进。

因此，**训练如何形成监督，与生成如何展开过程，不是同一条计算路径**。训练不必为每个样本反向传播整条长生成链，但生成仍可能需要许多次网络计算。

DDPM并不是只因为“换成预测噪声”就自动解决一切。原文的对照显示参数化与目标选择需要合在一起理解；样本质量、似然和采样成本也存在取舍。它的历史作用，是把扩散从一个可表达的建模框架，推进为更有竞争力的图像生成方案，同时把反复计算的成本进一步暴露出来。

这也再次体现可复用部件的重要性：原文的具体网络使用了U-Net及残差、自注意力等设计。新的生成过程并不要求所有网络组件都重新发明。

<a id="paper-ldm"></a>

### 29. LDM：为什么还要在每个像素上反复计算？

如果很多计算都花在高分辨率图像的细节上，能否先学到一个较小、可解码的表示，再在这个空间中完成昂贵的生成？

2021年公开的 **Latent Diffusion Models** 将感知压缩与扩散生成分成两阶段：先训练编码器和解码器，再在较小的空间表示中训练和运行扩散，最后解码回图像。[^ldm]

它没有把图像变成一句语义描述，也不是无损压缩。压得太少，节省有限；压得太多，又可能限制细节与质量。它改变的是**反复生成计算发生在哪里**，不是取消生成过程。

这里出现了一次比“扩散取代GAN”更有解释力的会合：LDM的压缩器使用感知损失和对抗目标。对抗训练的思想经由相关两阶段生成工作，以部件形式进入了扩散系统。**一种方法可以不再占据主流程中心，却继续在另一个位置发挥作用。**

条件控制则接入另一条线：文本先被编码成序列，再通过交叉注意力影响去噪过程。本文所读LDM v2的文本方案使用BERT tokenizer与联合训练的Transformer条件编码器；这不等于直接加载完整预训练BERT，也不等于使用冻结的CLIP文本编码器。

<a id="paper-sd14"></a>

### 30. Stable Diffusion v1.4：方法、文本条件与数据怎样组合

讲义把LDM论文放在“Stable Diffusion”标题下。为了把论文方法与产品实现接清楚，这里只补一个明确例子：**Stable Diffusion v1.4**。

它的官方模型卡描述了固定的预训练CLIP文本编码器、潜空间U-Net和交叉注意力条件输入，也列出了上游checkpoint及所用LAION子集的训练路径。[^sd14]

于是，前面几条线在这里形成两种不同连接：

```text
CLIP的图文匹配能力
        │ 用于筛选
        ▼
明确的LAION子集 ── 训练材料 ──► Stable Diffusion v1.4

CLIP的文本编码器 ─ 条件表示 ──► 潜空间去噪网络

LDM方法 ───── 潜空间扩散与条件接口 ─────► 具体实现
```

CLIP没有直接变成像素生成器，数据筛选与生成时的条件输入也不是同一个作用。v1.4的配方不能倒填到原始LDM，更不能推广成所有Stable Diffusion版本的统一实现。

这段连接也体现研究与产品之间的工程过程：LDM论文由学术与工业研究者共同参与，具体公开模型又通过模型卡说明组件与训练条件。论文、checkpoint、数据子集和产品名称，是需要分别核对的对象。

<a id="paper-dit"></a>

### 31. DiT：统一骨架，不等于统一训练目标

William Peebles与谢赛宁在2022年公开的 **Scalable Diffusion Models with Transformers** 进一步问：潜空间扩散已经将工作空间缩小，去噪网络是否一定要采用U-Net骨架？[^dit]

DiT保留潜空间扩散的生成框架及预训练自编码器，将带噪潜表示切成小块，用Transformer处理这些块之间的关系，再预测扩散过程需要的输出。它明确采用了ViT的部分设计，同时为时间和类别条件作适配。

因此，ViT与DiT共享的是可复用的骨架和输入组织方式，**不是同一个任务目标**：前者的主要实验是分类与表示迁移，后者是类别条件图像生成；使用Transformer也不意味着改成语言模型式的下一词生成。

原论文研究了模型规模、图块大小和计算量等因素。它显示，参数量不是唯一的扩展维度；但不能把ImageNet类别条件实验直接写成自由文本、视频或所有模态已经统一的证明。

这条线的会合已经足够清楚：**扩散规定生成过程如何学习与展开，潜表示决定在哪个空间计算，Transformer决定去噪器怎样处理表示，条件机制决定它依据什么生成。** 这些层次可以组合，却需要分别评价。


<a id="lenses"></a>

## 七、回看这些路线：计算、方法与人的选择

<a id="paper-bitter-lesson"></a>

### The Bitter Lesson：更值得建设的是答案，还是发现答案的方法？

《AI演义》用多页介绍Sutton的 **The Bitter Lesson**。这是一篇2019年的观点文章，不是一项与前面所有论文共享实验设置的统一证明。[^bitter]

它提出的核心问题是：在可用计算长期增长的环境里，研究者应主要把精力放在不断编码已有的人类发现，还是建设能够借更多计算继续发现规律的学习与搜索方法？

“苦涩”不只是一句算力口号，也包含人的研究选择：我们会对亲手设计、自己能够解释的方案投入时间和认同；即使短期有效，这种投入也可能让我们不愿转向更容易扩展的路线。Sutton以若干历史案例作归纳，主张更重视可继续利用计算的方法。

但它不等于“人类知识、结构和工程都没用”。原文并没有否定所有归纳偏置或专用实现，也不能替我们决定MoE怎样路由、LoRA选多大更新空间、训练数据怎样分配。前面每条成功路线，都包含大量具体设计。

它更适合作为贯穿全书的一个问题：**今天的办法只是把当前问题解决得巧，还是也为下一轮数据、计算和任务变化留下了改进空间？**

### 硬件彩票：算法的机会，也取决于它能在什么条件下被尝试

讲义反复提到“硬件彩票”。为解释这个视角，本文补读了Sara Hooker的 **The Hardware Lottery**，作为必要延伸，而不额外计入原讲义的36个对象。[^hardware]

这个视角提醒我们：研究方法并不在一个抽象、对所有想法同样友好的赛场上竞争。已有硬件、编译器、软件、资金和研究激励，会使某些路线更容易实现、优化和测试，另一些路线则成本很高。

两种视角不必互相否定：**The Bitter Lesson追问什么方法能持续利用更多计算；The Hardware Lottery追问这些计算机会由哪些软硬件和组织条件塑造。**

因此，Brook、AlexNet、MoE、ViT这些案例不能只归结为“算法更好”或“抽中了GPU”。编程抽象、数据、训练目标、计算粒度和硬件支持，共同决定了一种想法能否得到充分尝试。

<a id="connections"></a>

## 八、三种视角，落在同一张问题图上

把前面分开的章节重新连起来，可以先走完两段完整行程。下面是依据前述原文作出的综合解释：问题的承接与组件的采用分别说明，不把它们统一当作直接技术继承。

### 第一段：从读懂一句话，到完成一个需要查证的任务

语言路线最初的一道门槛，是怎样把文字变成可计算、可迁移的表示。Word2Vec交出词向量；seq2seq、Attention和Transformer进一步处理整段输入中信息怎样保存、读取和交换。到GPT-1/BERT时，被复用的从语言部件扩展成处理上下文的网络，具体任务可以从这个起点继续训练。

下一道门槛是使用：每次换任务都要更新参数，能否更方便？GPT-2/3把任务描述和示例放进上下文，使同一套参数能尝试不同任务。这种灵活使用依赖昂贵的预训练，因而语言线在GPT-3处直接接到Scaling Laws的资源配置。Chinchilla随后修正预算分配建议；数据建设与训练系统则分别解决“拿什么学”和“怎样学完”。这些系统工作有各自的时间线，是让规模方案可执行的共同条件。

模型能接受任务后，还会遇到两种不同失败：**有能力却不按需要回答，或者缺少完成任务所需的信息。** InstructGPT用示范与偏好反馈改变回答倾向；CoT让中间步骤参与后续生成；ReAct再让搜索和环境返回纠正下一步。以“比较两篇论文的实验条件”为例，清晰的回答方式、比较步骤和实际读取原文各有作用：训练改善行为，推理组织比较，工具取得证据。Tülu 3则让若干后训练阶段、数据和评价配方更容易被外部检查和继续研究。

这段路上，瓶颈从**表示信息**，转向**迁移与调用能力**，再转向**目标、证据和行动**。前面的问题没有消失，而是进入了后面系统的底层。

### 第二段：从认出一张图，到按一句话生成一张图

先分清三种输出：图像分类给出类别；CLIP比较图像与文字是否相配；图像生成需要产生新的图像内容。ViT让视觉复用Transformer骨架，CLIP让语言进入视觉监督和任务接口，但生成仍需要自己的学习过程。

扩散研究把生成拆成逐步去噪，DDPM形成有竞争力的图像生成配方，LDM把反复计算移到较小的潜空间。到Stable Diffusion v1.4这个明确例子，生成过程、CLIP文本条件和LAION子集的训练材料接到一起。CLIP还曾参与LAION的数据筛选：**训练前筛哪些图文，与生成时怎样读提示，是两个不同的位置。**

DiT又把ViT的图块组织和Transformer骨架放进潜空间去噪器。在这条路上，复用网络骨架、改变生成过程、缩小计算空间、接入文本条件可以分别发生。以后读到“Transformer生成模型”，就要继续问：它用了哪种生成目标，在哪个表示空间计算，又由什么条件控制？

### 历史、范式与人物怎样共同解释这些转折

回到原讲义的组织方法，对同一个转折，三个视角各补上一块解释。

| 视角 | 应当追问什么 | 本文中的连接例子 |
|---|---|---|
| 历史 | 当时的限制是什么，哪些条件已经成熟？ | 可编程GPU与软件抽象，遇到大规模数据和可训练网络后，才转化为学习机会 |
| 范式变迁 | 被学习、复用、优化或评价的对象改变了什么？ | 从复用词向量到复用上下文网络；从微调接口到上下文任务接口；从预测文本到加入偏好与可核验反馈 |
| 人与组织 | 谁能把问题变成实验，知识和资源怎样被传递？ | Brook到CUDA的工业连接；研究与翻译服务团队共同处理部署；LAION与Tülu 3将部分训练条件开放给外部研究者 |

这张图里至少有四种不同的连接，不能只画成一种箭头：

1. **直接采用组件**：如ResNet残差连接进入Transformer、Transformer骨架进入ViT。
2. **支撑条件**：数据、GPU编程、显存管理和可靠训练，让某种模型方案能够被实际训练。
3. **问题的继承与修正**：如Scaling Laws与Chinchilla共同研究预算分配，但新实验改变了建议。
4. **并行探索或主题对照**：如蒸馏与ResNet分别处理部署和训练；AlphaGo Zero让我们思考清晰反馈，但不能因此认定它是语言推理的直接祖先。

还有反馈回路：CLIP帮助筛选数据，开放数据再支持图文模型训练。只有把关系类型分开，才能同时保留发展路径的连贯性与真实历史的复杂性。

<a id="verified-connections"></a>

### 连接索引：几条有明确依据的跨路线桥梁

下表用于回查，不替代正文。这里特意不把所有关系都叫“继承”。

| 连接 | 关系类型 | 原文支持的具体内容 |
|---|---|---|
| Brook → CUDA | 编程抽象与工业化线索 | 官方历史介绍联系了研究原型、Buck与CUDA的发展；不表示AlexNet直接使用Brook |
| ResNet → Transformer | 组件采用 | Transformer采用并引用残差连接 |
| seq2seq / Attention → GNMT | 方法继承与部署 | GNMT把循环编码—解码、Attention及工程改造组织为翻译系统 |
| GNMT → BERT | 部件复用 | BERT的WordPiece采用明确引用GNMT |
| Transformer → GPT-1 / BERT | 骨架复用、目标分叉 | 分别使用不同信息可见性和预训练目标，不是同一模型换名字 |
| Scaling Laws → GPT-3 | 资源配置依据 | GPT-3明确使用缩放研究指导训练资源选择 |
| Chinchilla → RefinedWeb | 研究动机 | 更多训练tokens的需求转化为可扩展数据获取与质量检验问题 |
| ZeRO → MegaScale | 系统部件与通信组织 | 后者明确讨论状态分片及相关通信重叠 |
| Transformer → ViT；ViT / ResNet → CLIP | 骨架与接口的会合 | ViT复用序列骨架；CLIP可用ViT或ResNet作图像编码器，并加入图文目标 |
| CLIP → LAION → OpenCLIP | 模型—数据反馈 | 表示模型参与配对筛选，开放数据再支持图文模型训练 |
| DDPM → LDM | 问题与框架承接 | 从像素细节与反复计算的代价，转向潜空间扩散 |
| 对抗训练 → LDM压缩器 | 部件再利用 | 对抗目标进入感知压缩阶段，并非整个LDM变成GAN |
| LDM + CLIP文本表示 + LAION子集 → SD v1.4 | 指定版本的实现组合 | 方法、条件编码器、数据路径各有对应角色，不推广到全部产品版本 |
| ViT / LDM → DiT | 骨架与生成框架组合 | 潜表示的patch化、Transformer去噪器与扩散目标组合；原实验仍有任务边界 |
| GPT-3 → InstructGPT | 基座上的行为目标转换 | 从文本预测能力转向示范与偏好反馈驱动的后训练 |
| CoT → ReAct | 使用过程的组合 | 推理步骤与环境动作、观察交错；交互不等于每轮都在训练 |

这些连接的逐项原文位置见[跨路线研究记录](../notes/ai_yanyi_research/README.md)及本文证据账本。源论文链接与阅读版本列在文末。

### 人物线不是附录，也不是英雄谱

同一研究者参与不同工作，确实能帮助我们发现连接。Sutskever出现在AlexNet、seq2seq和GPT相关作品中；Vinyals参与seq2seq、蒸馏和GNMT；Radford、Sutskever又参与了CLIP。Narasimhan参与GPT-1与ReAct，将人物线索从预训练迁移接到了交互研究。这些共同参与，显示研究网络跨越了视觉、语言和使用方式的问题。[^people]

但方法具体继承了什么，仍要由论文的设计、引用和实验来确认。另一类同样重要的“人”，是搭建数据管道、封装分布式训练、提供计算资源、写示范和做偏好评价的人。没有这些条件，模型的思想可能无法成为可用的研究和产品。

因此，人的视角最终也要回答**他们改变了哪一个条件或问题**，而不只是作者后来去了哪家公司。

<a id="new-papers"></a>

## 九、以后拿到一篇新论文，先把它放回哪里？

阅读新论文时，不必把整段AI历史重新学一遍。可以先用五个问题定位它：

1. **它的瓶颈是什么？** 是表示、训练目标、数据、计算、部署，还是任务过程与评价？
2. **它改变了哪一层？** 换了骨架、学习信号、数据配方、计算组织，还是调用模型的方式？
3. **它依赖什么已经成立的条件？** 预训练模型、特定数据、硬件、工具环境或评价机制是否被默认拥有？
4. **证据具体支持到哪里？** 比较对象、任务、预算和指标是否一致？效果改善与原因解释是不是同一等级的证据？
5. **它接上了哪条旧问题，又留下什么新问题？** 是真正采用某项方法，还是只是同一个主题下的另一种尝试？

“用了Transformer”“用了强化学习”“参数更少”都只是入口，不能代替这五个问题。把新工作放到正确的位置，才能看到它的增量，而不是只记住一个新名字。

讲义作者提到先建框架、借助工具阅读和关注人物脉络。本文沿用的是这套阅读目的，不把其个人数学准备路径强加给每个读者。AI可以帮助提取信息、解释术语和组织问题，但关键判断仍应回到原文及其证据；本报告的路线图同样需要随着新的证据更新。

## 思考与追问

### 我真正理解了什么？

AI的发展不只是模型名单变长，而是学习对象、可用信息、计算组织、任务接口和反馈目标不断被重新安排。数据与工程不是舞台背景，人物与组织也不只是履历；它们参与决定哪些问题能够被提出和验证。

### 我还没搞懂什么？

一项在固定数据和预算下有效的方法，换到另一种资源、任务分布或部署环境后，还保留多少优势？哪些历史连接有直接证据，哪些只是合理但可被修正的解释？这些问题需要继续沿具体新论文和真实系统检验。

### 下一步读什么或做什么？

选择一篇新的AI论文，先尝试写下“旧瓶颈—改变的环节—证据范围—留下的问题”，再把它接到本文的一条或几条路线。若找不到适合的位置，先检查分类是否错了；也可能它确实提出了这张路线图还没有覆盖的新问题。


## 原讲义与本文的对应关系

原PDF的36个主线对象在本文都有说明，但不是每篇都展开全部公式、附录和实验。按核定口径，包含33篇论文、2篇研究报告和1篇观点文章。第12页与第28页各合讲两篇；第21—25页连续介绍同一篇The Bitter Lesson。

| 原PDF范围 | 本文如何承接 |
|---|---|
| 1—9：学习目的、方法、三视角、总图与硬件背景 | 导言、总路线与第七至第九部分；不把个人数学准备路径当读者门槛 |
| 10—20：模型结构及使用方法 | 第一至第四部分；按问题拆分，并保留年代与不同关系类型 |
| 21—31：Bitter Lesson、Infra与数据 | 第三、第七部分；把观点、工程可行性和经验结果分开 |
| 32—40：语言模型 | 第二、第四部分；保留预训练、任务接口与目标反馈的分叉 |
| 41—50：视觉、多模态与生成 | 第五、第六部分；解释并行路线及具体组件的会合 |
| 51：致谢 | 无新增技术节点；保留原讲义来源 |

### 36个研究对象的正文定位

年份按核定的首次公开或发表口径；实际阅读的修订版见参考来源。

| 研究对象 | 年份 | 正文定位 |
|---|---:|---|
| [Brook for GPUs: Stream Computing on Graphics Hardware](https://dl.acm.org/doi/10.1145/1015706.1015800) | 2004 | [转到正文](#paper-brook) |
| [ImageNet Classification with Deep Convolutional Neural Networks](https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html) | 2012 | [转到正文](#paper-alexnet) |
| [Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) | 2014 | [转到正文](#paper-seq2seq) |
| [Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) | 2014 | [转到正文](#paper-bahdanau-attention) |
| [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) | 2015 | [转到正文](#paper-distillation) |
| [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385) | 2015 | [转到正文](#paper-resnet) |
| [Attention Is All You Need](https://arxiv.org/abs/1706.03762) | 2017 | [转到正文](#paper-transformer) |
| [Mastering the game of Go without human knowledge](https://www.nature.com/articles/nature24270) | 2017 | [转到正文](#paper-alphago-zero) |
| [Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/abs/1701.06538) | 2017 | [转到正文](#paper-sparse-moe) |
| [Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/abs/2201.11903) | 2022 | [转到正文](#paper-cot) |
| [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685) | 2021 | [转到正文](#paper-lora) |
| [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) | 2022 | [转到正文](#paper-react) |
| [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) | 2019 | [转到正文](#paper-bitter-lesson) |
| [ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://arxiv.org/abs/1910.02054) | 2019 | [转到正文](#paper-zero) |
| [Scaling Laws for Neural Language Models](https://arxiv.org/abs/2001.08361) | 2020 | [转到正文](#paper-scaling-laws) |
| [Training Compute-Optimal Large Language Models](https://arxiv.org/abs/2203.15556) | 2022 | [转到正文](#paper-chinchilla) |
| [LAION-5B: An open large-scale dataset for training next generation image-text models](https://arxiv.org/abs/2210.08402) | 2022 | [转到正文](#paper-laion5b) |
| [The RefinedWeb Dataset for Falcon LLM: Outperforming Curated Corpora with Web Data, and Web Data Only](https://arxiv.org/abs/2306.01116) | 2023 | [转到正文](#paper-refinedweb) |
| [MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs](https://arxiv.org/abs/2402.15627) | 2024 | [转到正文](#paper-megascale) |
| [Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/abs/1301.3781) | 2013 | [转到正文](#paper-word2vec) |
| [Google's Neural Machine Translation System: Bridging the Gap between Human and Machine Translation](https://arxiv.org/abs/1609.08144) | 2016 | [转到正文](#paper-gnmt) |
| [Improving Language Understanding by Generative Pre-Training](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf) | 2018 | [转到正文](#paper-gpt1) |
| [BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding](https://arxiv.org/abs/1810.04805) | 2018 | [转到正文](#paper-bert) |
| [Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) | 2019 | [转到正文](#paper-gpt2) |
| [Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) | 2020 | [转到正文](#paper-gpt3) |
| [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155) | 2022 | [转到正文](#paper-instructgpt) |
| [Tulu 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124) | 2024 | [转到正文](#paper-tulu3) |
| [Large-scale Video Classification with Convolutional Neural Networks](https://openaccess.thecvf.com/content_cvpr_2014/html/Karpathy_Large-scale_Video_Classification_2014_CVPR_paper.html) | 2014 | [转到正文](#paper-deepvideo) |
| [Two-Stream Convolutional Networks for Action Recognition in Videos](https://arxiv.org/abs/1406.2199) | 2014 | [转到正文](#paper-two-stream) |
| [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) | 2014 | [转到正文](#paper-gan) |
| [Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/abs/1503.03585) | 2015 | [转到正文](#paper-diffusion-2015) |
| [Denoising Diffusion Probabilistic Models](https://arxiv.org/abs/2006.11239) | 2020 | [转到正文](#paper-ddpm) |
| [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929) | 2020 | [转到正文](#paper-vit) |
| [Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/abs/2103.00020) | 2021 | [转到正文](#paper-clip) |
| [High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) | 2021 | [转到正文](#paper-ldm) |
| [Scalable Diffusion Models with Transformers](https://arxiv.org/abs/2212.09748) | 2022 | [转到正文](#paper-dit) |

## 来源与适用范围

本文对历史、机制和作用的解释，以实际读取的原论文相关部分及必要的正式资料为依据。没有声称重现全部训练、评测或生产系统，也没有把未核人物现职、营销性优先权或所有后续产品谱系写成事实。重要比较保留其任务、资源和评价边界。

原讲义和旧索引中的若干错链、论文／产品混同及本地PDF错配已在[来源地图](../notes/ai_yanyi_research/source-map.md)登记。本稿使用核定原文，不用错配文件为结论背书。未采用的精确分数、版本内部冲突和逐案未核的外围判断，保留在[研究记录](../notes/ai_yanyi_research/README.md)，不强行给出答案。

原始研究核验于2026-11-03，本文于2026-11-04补充术语、跨路线讲解并修订阅读呈现。各来源的阅读版本见下方注释，详细核查范围见[研究记录](../notes/ai_yanyi_research/README.md)。

[^brook]: Buck et al.，[Brook for GPUs](https://dl.acm.org/doi/10.1145/1015706.1015800)，2004；读取[Stanford作者稿](https://graphics.stanford.edu/papers/brookgpu/brookgpu.pdf)相关正文。
[^gpu-history]: NVIDIA，[Inside the Programming Evolution of GPU Computing](https://developer.nvidia.com/blog/inside-the-programming-evolution-of-gpu-computing/)，2015发布的历史介绍；只用于Brook、Buck与CUDA的关系，不用作AlexNet直接软件依赖证明。
[^alexnet]: Krizhevsky, Sutskever & Hinton，[ImageNet Classification with Deep Convolutional Neural Networks](https://papers.nips.cc/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf)，2012。
[^resnet]: He et al.，[Deep Residual Learning for Image Recognition](https://arxiv.org/pdf/1512.03385v1)，2015。
[^distill]: Hinton, Vinyals & Dean，[Distilling the Knowledge in a Neural Network](https://arxiv.org/pdf/1503.02531v1)，2015。
[^word2vec]: Mikolov et al.，[Efficient Estimation of Word Representations in Vector Space](https://arxiv.org/pdf/1301.3781v3)，2013。
[^seq2seq]: Sutskever, Vinyals & Le，[Sequence to Sequence Learning with Neural Networks](https://arxiv.org/pdf/1409.3215v3)，2014。
[^bahdanau]: Bahdanau, Cho & Bengio，[Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/pdf/1409.0473v7)，首发2014年，所读修订版2016年。
[^gnmt]: Wu et al.，[Google's Neural Machine Translation System](https://arxiv.org/pdf/1609.08144v2)，2016。
[^transformer]: Vaswani et al.，[Attention Is All You Need](https://arxiv.org/pdf/1706.03762v7)，首发2017年，所读修订版2023年；残差引用、架构与并行范围分别核对。
[^gpt1]: Radford et al.，[Improving Language Understanding by Generative Pre-Training](https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf)，2018。
[^bert]: Devlin et al.，[BERT](https://arxiv.org/pdf/1810.04805v2)，首发2018年，所读修订版2019年。
[^gpt2]: Radford et al.，[Language Models are Unsupervised Multitask Learners](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)，2019。
[^gpt3]: Brown et al.，[Language Models are Few-Shot Learners](https://arxiv.org/pdf/2005.14165v4)，2020。
[^kaplan]: Kaplan et al.，[Scaling Laws for Neural Language Models](https://arxiv.org/pdf/2001.08361v1)，2020。
[^chinchilla]: Hoffmann et al.，[Training Compute-Optimal Large Language Models](https://arxiv.org/pdf/2203.15556v1)，2022。
[^zero]: Rajbhandari et al.，[ZeRO](https://arxiv.org/pdf/1910.02054v3)，首发2019年，所读修订版2020年。
[^refinedweb]: Penedo et al.，[The RefinedWeb Dataset for Falcon LLM](https://arxiv.org/pdf/2306.01116v1)，2023。
[^laion]: Schuhmann et al.，[LAION-5B](https://arxiv.org/pdf/2210.08402v1)，2022。
[^megascale]: Jiang et al.，[MegaScale](https://arxiv.org/pdf/2402.15627v1)，2024。
[^moe]: Shazeer et al.，[The Sparsely-Gated Mixture-of-Experts Layer](https://arxiv.org/pdf/1701.06538v1)，2017。
[^lora]: Hu et al.，[LoRA](https://arxiv.org/pdf/2106.09685v2)，2021。
[^alphago]: Silver et al.，[Mastering the game of Go without human knowledge](https://www.nature.com/articles/nature24270)，2017。方法依据题名、作者与版式已核对的Nature排版版公开镜像；本文讨论围棋专用的AlphaGo Zero。
[^instruct]: Ouyang et al.，[Training language models to follow instructions with human feedback](https://arxiv.org/pdf/2203.02155v1)，2022。
[^cot]: Wei et al.，[Chain-of-Thought Prompting Elicits Reasoning in Large Language Models](https://arxiv.org/pdf/2201.11903v6)，首发2022年，所读修订版2023年。
[^react]: Yao et al.，[ReAct](https://arxiv.org/pdf/2210.03629v3)，首发2022年，所读修订版2023年。
[^tulu]: Lambert et al.，[Tülu 3](https://arxiv.org/pdf/2411.15124v5)，首发2024年，所读修订版2025年；不将修订新增内容全部倒写为首版。
[^deepvideo]: Karpathy et al.，[Large-scale Video Classification with Convolutional Neural Networks](https://openaccess.thecvf.com/content_cvpr_2014/papers/Karpathy_Large-scale_Video_Classification_2014_CVPR_paper.pdf)，2014。
[^two-stream]: Simonyan & Zisserman，[Two-Stream Convolutional Networks](https://arxiv.org/pdf/1406.2199v2)，2014。
[^vit]: Dosovitskiy et al.，[An Image is Worth 16x16 Words](https://arxiv.org/pdf/2010.11929v2)，首发2020年，所读修订版2021年。
[^clip]: Radford et al.，[Learning Transferable Visual Models From Natural Language Supervision](https://arxiv.org/pdf/2103.00020v1)，2021。
[^bitter]: Sutton，[The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)，2019-03-13；作为作者的历史归纳与方法论主张，不是本文逐案重做的全史因果审计。
[^hardware]: Hooker，[The Hardware Lottery](https://arxiv.org/pdf/2009.06489v2)，2020；为解释讲义的硬件彩票视角补充的必要来源，重点为软硬件、研究激励与方法选择的关系。
[^gan]: Goodfellow et al.，[Generative Adversarial Nets](https://arxiv.org/pdf/1406.2661v1)，2014。
[^diffusion15]: Sohl-Dickstein et al.，[Deep Unsupervised Learning using Nonequilibrium Thermodynamics](https://arxiv.org/pdf/1503.03585v8)，2015。
[^ddpm]: Ho, Jain & Abbeel，[Denoising Diffusion Probabilistic Models](https://arxiv.org/pdf/2006.11239v2)，2020。
[^ldm]: Rombach et al.，[High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/pdf/2112.10752v2)，首发2021年，所读修订版2022年；不将修订的文本模型与训练配方全部倒写为首版。
[^sd14]: [Stable Diffusion v1.4官方模型卡](https://huggingface.co/CompVis/stable-diffusion-v1-4)。本文读取的是2026-11-03的main内容快照，记录了正文哈希但未固定仓库commit；仅支持该模型卡对v1.4的具体陈述，未下载或运行权重。
[^dit]: Peebles & Xie，[Scalable Diffusion Models with Transformers](https://arxiv.org/pdf/2212.09748v2)，首发2022年，所读修订版2023年。

[^lecture]: 谢青池，[《AI演义：36篇论文开启你的探索之旅》](../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf)，本地51页版本。作者身份按封面署名理解，不将其自动视为当前职位。
[^people]: 该段依据AlexNet、seq2seq、蒸馏、GNMT、GPT-1、CLIP和ReAct的原文署名，分别见前述论文链接。共同参与只支持研究网络的连续性；具体方法继承另据正文所列设计与引用。
