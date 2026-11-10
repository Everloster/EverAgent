---
title: "AI演义·06｜seq2seq 与 Attention：读一句话，再生成另一句话"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["ai_history", "seq2seq", "attention", "neural_machine_translation", "lstm", "encoder_decoder"]
source_url: "https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c"
transcript_visibility: "private"
transcript_source_ref: "sha256:919e4ce5147340e2306748394cdb555bfc6a745119f846e7ce8c985056745b05"
transcript_audit_path: "podcast-learning/reports/transcripts/2026-11-04_ai-yanyi-117.audit.json"
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·06｜seq2seq 与 Attention：读一句话，再生成另一句话

[返回总览第 6 节](../AI演义_笔记分析与项目整合报告.md#paper-seq2seq) · [上一章：Word2Vec](./AI演义_05_Word2Vec_词向量怎样学出来_科普讲解_20261104.md)

**The black cat is sleeping.** 可以译为 **Le chat noir dort.**，即“黑猫正在睡觉”。Black 在 cat 前，noir 却在 chat 后；is sleeping 又合成了一个动词 dort。翻译要保留原意，还要重排词序、改变句长。

本章用这句教学例子解释两种办法：seq2seq 将读入源句与生成译文连接起来，Attention 则让生成器在不同步骤重新读取源句各处的信息。它们是 2014 年同期的探索，讲解顺序不等于发表顺序。[^podcast]

<a id="translation-problem"></a>

## 1. 词表示之后，还缺一套序列处理方法

Word2Vec 提供了词的数值表示，但知道 black、cat 各有什么用法，还不能决定法文应当先写 chat 再写 noir。翻译系统必须让已经读到和写出的内容影响后续选择，并能自行决定输出何时结束。

当时的统计机器翻译（SMT）把短语对应、目标语言模型和词序调整等因素组合起来，再搜索合适译文。它同样会从语料学习，难处在于多个部件需要分别设计、训练和协调。神经机器翻译希望把源句到译句的转换交给一个联合训练的系统。[^background]

输入和输出的词数可以不同。固定维度的表示或计算接口，也不意味着“五个词进去就必须五个词出来”；问题在于怎样用共享计算处理长短未知的两个序列。

<a id="encoder-decoder"></a>

## 2. 编码器读原句，解码器写译文

Sutskever、Vinyals 和 Le 使用两套分别训练参数的 LSTM（长短期记忆网络）。编码器逐词读入源句，解码器根据读入结果逐步产生译文，两者在同一翻译目标下共同训练。[^seq2seq-model]

### 逐步更新内部状态

源词先转换为嵌入向量。编码器读取当前词时，还接收上一步的隐状态，计算新的内部表示。因此，读到 cat 时，状态已经受 The、black 等前文影响。同一套参数在各位置复用，句子更长意味着多执行若干步。

LSTM 通过记忆状态和可学习的控制，帮助信息跨较多步骤保留或更新。它的状态是一组数值，不是模型私下写的一段自然语言摘要。原论文采用四层 LSTM，用 **8,000 个实数**表示句子；这是结构确定的状态规模，不对应固定数量的单词。

读完后，编码器将最终状态交给解码器。此后解码器自己的状态继续变化，但这一方案没有额外通道，让它在每个目标步重新访问源句各位置的编码结果。

### 按已有前文继续生成

假设模型已经学会黑猫这句话的翻译。解码器先给法文词表中的候选词计算概率，选出 Le，将它作为已生成前文，再继续得到 chat、noir、dort，直到产生特殊结束标记 **EOS**。EOS 表示序列结束，并不等同于句号。

这种自回归生成，让已有输出参与下一步预测，整句概率由逐步的条件概率组成。句长不必预先固定，模型也没有在第一步就取得完整答案。[^seq2seq-model]

<a id="training-and-search"></a>

## 3. 学习译文与搜索译文

两篇论文都使用平行语料，即大量相互对应的源句和译句。训练提高正确译文的条件概率，反馈传回词表示、编码器和解码器。预测 noir 时，可以把正确前文 Le chat 提供给模型，这种做法通常称为 teacher forcing。[^training]

实际使用时，正确前文还不存在，模型只能接着自己的输出继续。一处错误可能影响后面的选择。作者因此使用束搜索（beam search），在每一步保留少量得分较好的候选前缀，让它们分别向后扩展。

例如 Le chat 和 Le petit 各自保存前缀与解码状态，继续尝试后续词，再按累计得分筛选；遇到 EOS 的候选进入完整译文集合。它们不会把前文混成同一句。[^search]

束搜索只探索部分路径，既不保证找到模型评分最高的全局解，也不保证高概率译文忠实于原句。模型、词表和搜索方法共同影响结果。端到端训练统一了许多参数的学习目标，语料准备、网络结构和搜索策略仍由研究者选择。

<a id="reverse-source"></a>

## 4. 把源句倒过来读

Sutskever 等人的实际训练将源句倒序，目标句保持正常顺序。忽略标点，黑猫例子变为：

- 输入：sleeping → is → cat → black → The
- 输出：Le → chat → noir → dort

编码与解码接在同一时间链上，倒序后，靠近源句开头的 The 出现在编码结束处，离最早生成的 Le 更近。作者认为，这增加了较短的依赖，使一部分源词与目标词的联系更容易学习；对应词之间的平均距离没有改变，论文也没有给出完整解释。[^reverse]

在相同束宽 12 的单模型比较中，正常源词序为 **26.17 BLEU**，倒序后为 **30.59 BLEU**。倒序输入是方案的一部分，不能将全部成绩归因于 LSTM 名称。

固定规模的状态在这项实验中也能处理长句。Figure 3 的图注称，少于 35 词的句子没有性能退化，最长句也只出现较小退化。[^seq2seq-long] 这项结果需要和 Attention 的动机并列理解：增加表示容量、改善训练依赖、改变读取方式，都可能帮助翻译，没有一条由“固定向量”直接推出“长句必败”的结论。

<a id="attention-step"></a>

## 5. 每生成一个词，重新读取源句

Bahdanau、Cho 和 Bengio 的 RNNsearch 保存源句各位置的表示，让解码器在每一步重新加权读取。这里的 search 指源句中的软对齐，不是搜索网页。[^attention-model]

### 源位置表示已经包含上下文

编码器用一条循环网络从左向右读，另一条从右向左读，将同一位置的两份状态拼接成 annotation，即源位置表示。Black 的 annotation 因此可以同时受到前面的 The 和后面的 cat、is sleeping 影响，超出了单独查词向量表所得的信息。

源句有多少位置，就保留多少份 annotation，每份维度仍固定。双向编码需要完整源句，所以这套论文模型也不能直接当作尚未听完一句话的实时同声传译系统。

### 权重、加权和与下一词预测

模型已经生成 Le chat 后，要利用现有信息继续预测。它用上一步解码状态和各位置 annotation 计算分数，经 softmax 得到非负、总和为 1 的权重，再将源表示加权相加，形成当前的 context vector（上下文向量）。这份信息与已有输出一起参与后续状态更新和下一词预测。[^attention-model]

用两个位置做算术演示：

```text
0.75 × [1, 0] + 0.25 × [0, 2] = [0.75, 0.5]
```

得到的是两份信息按比例混合的结果，不是挑一个位置留下。权重在下一步改变，context vector 也会改变。这些向量和比例均为自拟，没有把维度规定成某种词义。

回到翻译，如果模型学会了合适的读取方式，准备生成 noir 时可能更重视 black 附近，生成 dort 时再转向 is sleeping。计算注意力分数时，模型还不知道正确下一词就是 noir；它只使用已有解码状态与源表示。

| 对象 | 含义 |
|---|---|
| Annotation | 源句一个位置经过编码后的向量，已含上下文 |
| 注意力权重 | 当前目标步分给各源位置的比例 |
| Context vector | 按这些权重汇总出来的源信息 |
| 解码器隐状态 | 生成过程自身的内部状态 |

一个目标词可以同时读取多个源位置，权重也能随重排关系改变，所以称为 soft alignment（软对齐）。若人为把权重全部设为相等，每步得到的就是同一份源表示平均值，失去随生成进度调整读取重点的能力；解码器仍能运行，效果需要通过消融实验判断。

Sutskever 模型使用 LSTM，Bahdanau 实验则采用 Cho 式门控循环单元，通常归入 GRU。两者同属循环网络，但不是同一个模型只加了一个 Attention 开关。[^attention-implementation]

<a id="learn-alignment"></a>

## 6. 翻译反馈怎样学出对齐

训练不要求人工标注“black 对应 noir”的逐词连线。正确译文的损失可以通过输出计算、加权和、注意力分数和源编码传回去，让这些部分共同更新。柔和的权重和加权和便于传递梯度。对齐模型本身是一个小型前馈网络，也随整个翻译系统学习。[^alignment-training]

训练目标是译文概率，annotation 又包含周边信息，因此一个源位置权重较高，不能被简单解释为目标词只来自那个孤立源词。

论文 Figure 3 用灰度矩阵显示权重，英文源词在横轴，生成的法文词在纵轴，越亮表示权重越大。可以看到沿对角线的对应、名词与形容词换序，以及多个源位置共同参与。四幅图的后三幅来自无未知词、长度为 10–20 词的测试句。[^alignment-figure] 它们是定性观察，没有给出整个测试集上的人工标准对齐准确率，也不是完整的因果解释。

注意力处理一条候选内部怎样读取源信息，束搜索处理多条译文候选中保留哪些路径。两种机制可以一起使用。

<a id="experiments"></a>

## 7. 两组实验各自说明了什么

BLEU 将机器译文与参考译文比较，统计受截断计数约束的 n-gram 匹配，再惩罚过短译文。它主要用于整批译文比较，34.81 BLEU 不表示 34.81% 的句子翻译正确。分词、大小写与评分脚本也会影响分数。[^bleu]

### seq2seq 的直接生成与重排

Sutskever 等人使用 WMT’14 英法语料约 **1,200 万句对**，约含 **3.04 亿英文词、3.48 亿法文词**。源词表 **16 万**，目标词表 **8 万**，词表外内容映射为 UNK。下表来自 Table 1，以及 Table 2 对最佳 WMT 系统用同一脚本重算的结果。[^seq2seq-results]

| 直接生成译文的方法 | 比较条件 | 测试 BLEU |
|---|---|---:|
| 单个 LSTM，正常源词序 | 束宽 12 | 26.17 |
| 单个 LSTM，倒序源句 | 束宽 12 | 30.59 |
| 五个倒序 LSTM 集成 | 束宽 2 | 34.50 |
| 五个倒序 LSTM 集成 | 束宽 12 | 34.81 |
| 论文的短语统计翻译基线 | 同一测试与评分口径 | 33.30 |
| 该论文按同脚本重算的最佳 WMT’14 系统 | 当时水平参照 | 37.0 |

五模型集成超过了 33.30 的统计基线，单个倒序模型尚未超过；集成的 34.81 也低于表中的 37.0。论文另有 **36.5 BLEU**，来自先由统计系统生成 1,000 个候选，再用神经模型重排的实验，不能与纯神经直接生成混在一起。

单模型约 **3.84 亿参数**。作者将四层 LSTM 分到四张 GPU，另外四张负责大词表输出，所述实现训练约十天。[^seq2seq-engineering] 模型规模、输出成本、搜索和并行实现共同决定了这套实验。

### Attention 与作者的基本编码器—解码器

Bahdanau 等人同样用 WMT’14 英法平行语料，筛选后约 **3.48 亿词**，没有另用单语料。每种语言词表 **3 万词**，测试集 **3,003 句**。训练句长上限分别为 30 或 50，模型名中的数字表示训练数据选择，不是测试时的硬长度上限。[^attention-results]

| 模型 | 全部测试句 BLEU | 无未知词子集 BLEU |
|---|---:|---:|
| 基本编码器—解码器 RNNencdec-50 | 17.82 | 26.71 |
| Attention 模型 RNNsearch-50 | 26.75 | 34.16 |
| 训练更久的 RNNsearch-50 | 28.45 | 36.15 |
| Moses 统计翻译系统 | 33.30 | 35.63 |

RNNsearch 明显改善了所比较的基本模型，完整测试集上的最好结果仍低于 Moses。36.15 高于 35.63 的比较，仅针对源句和参考译文都无未知词的子集，并禁止神经模型输出 UNK。Moses 还用了额外单语料。

两个神经模型共享数据与训练程序，但 RNNsearch 多了反向编码网络，参数与结构不同。这支持整套方案的效果，不能当作严格等参数的单组件消融。继续训练也有成本：在 Quadro K-6000 上，RNNsearch-50 约用 **111 小时**，更长训练的版本约用 **252 小时**。[^attention-training]

<a id="long-sentence-case"></a>

## 8. 通顺的译文也可能改变关系

论文 Appendix C 有一个长句，讲医生因为拥有医院医护人员身份，可以让病人入院诊断或治疗。基本编码器—解码器到后半句却把“医护人员身份”译成“健康状况”；Attention 模型在展示的译例中保住了这个职业身份。另一个 Disney 数字平台的例子里，基本模型在后面偏离原意并未收好引号，Attention 的版本保留了更多内容。[^long-examples]

这些案例说明持续读取源句可能帮助保留关系和细节，但长度实验仍受训练分布影响：RNNsearch-50 较稳定，RNNsearch-30 超过训练句长后仍明显下降。它们不能替代前面倒序 LSTM 的长句结果，也不能将一种较弱固定状态基线当作所有同期模型。

几项限制仍然存在：

- 词表外名字可能成为 UNK，读取位置不会自动增加目标词表。
- 每个目标步要与源位置配对打分，这部分次数随源句长度与译句长度的乘积增长；完整成本还包含隐藏维度、循环网络和词表输出。
- 编码器和解码器仍沿循环状态逐步计算，Attention 改变读取方式，没有去掉循环。
- Annotation 和 context vector 都有有限维度，权重和生成都可能出错。句子实验没有证明整本书或无限长度上下文上的可靠性。[^attention-cost]

<a id="people-and-history"></a>

## 9. 同期发展的两条路线

Seq2seq 论文的 **Ilya Sutskever、Oriol Vinyals、Quoc V. Le** 均署名 Google，Ilya 也参与了 AlexNet。Attention 论文的 **Dzmitry Bahdanau** 署名 Jacobs University Bremen，**Kyunghyun Cho、Yoshua Bengio** 署名 Université de Montréal。[^history]

Bahdanau 论文首次提交于 **2014 年 9 月 1 日**，seq2seq 为 **9 月 10 日**。本章资料采用的却是后续修订的 Bahdanau v7 和 seq2seq v3，因此需要区分首发时间、版本内容与教学顺序。

修订版本会讨论彼此及更早的编码器—解码器研究。Bahdanau 还分析了 Graves 在手写生成中的注意力及其单向移动限制；这项工作的历史位置，是将可学习软对齐引入神经机器翻译的有力实践。[^attention-cost]

从 Word2Vec 到这里，可复用的对象从词表示扩展到了处理序列的网络，但这不表示两篇模型直接采用了 Word2Vec 权重。Seq2seq 还展示了句子状态的二维投影：它对词序变化敏感，对部分主动、被动改写较稳定。[^seq2seq-representation] 这是少量句子的定性观察，提示翻译训练也可能形成有用的整句表示。

<a id="questions"></a>

继续阅读时，可以把“增加状态容量”和“改变信息访问方式”分开，再检查译文是否保住主体、身份、否定和时间关系。[第 7 章 GNMT 与 Transformer](./AI演义_07_GNMT与Transformer_从翻译系统到并行架构_科普讲解_20261105.md)会接着讨论：怎样把翻译做成服务，以及表示计算能否减少循环等待。

<a id="sources-and-corrections"></a>

## 播客、讲义与阅读范围

[讲义第 12 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=12)与播客约 33:50–46:30 提供了从图像模型转向序列学习的叙事。转写在模型名、人名和上下文向量等处不稳定，约 43:22、43:57 附近有重复，原稿已按论文处理。音频未逐字听校或测量词错误率，整期末尾约 16 秒覆盖仍未确认。[^podcast]

本次沿用原稿对两篇正文、Bahdanau 的模型与长句附录，以及 BLEU 论文的阅读记录。黑猫句子、搜索前缀和加权和都是教学例子，没有重新训练模型或复现 BLEU。图表数值保留模型数量、词表、训练时长与子集筛选等条件。

## 来源与延伸阅读

[^podcast]: [《张小珺Jùn｜商业访谈录》第 117 期：AI演义](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)，[Apple Podcasts 备用入口](https://podcasts.apple.com/cn/podcast/id1634356920?i=1000733801180)。Shownotes 将 seq2seq 与 Attention 放在 19:35 开始的 Part 1；约 33:50–46:30 的单章范围由转录定位，并非节目另行标注的精确章界。[讲义 PDF 第 12 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=12)。
[^background]: Sutskever 等，[Sequence to Sequence Learning with Neural Networks](https://arxiv.org/pdf/1409.3215v3)，§1–2、§4；Bahdanau 等，[Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/pdf/1409.0473v7)，§1–2、§6.2。这里区分传统系统的多个组成部分与神经模型的联合训练，不把 SMT 描述成纯人工规则。
[^seq2seq-model]: [seq2seq 原论文](https://arxiv.org/pdf/1409.3215v3)，§2、§3.4、Figure 1：两套 LSTM、四层、每层 1,000 cells、EOS 与不同长度输入输出；论文明确写用 8,000 个实数表示句子。LSTM 的说明只用于建立结构直觉，未展开全部门控公式。
[^training]: [seq2seq](https://arxiv.org/pdf/1409.3215v3) §2、§3.1–3.4 的条件概率分解、正确译文对数概率训练目标；[Bahdanau](https://arxiv.org/pdf/1409.0473v7) §2–4、Appendices A–B。使用正确目标前缀解释其训练目标，不能把它当成推理时可获得的答案。
[^search]: [seq2seq](https://arxiv.org/pdf/1409.3215v3) §3.2：左到右束搜索，保留 B 个部分候选，EOS 后移入完整候选；[Bahdanau](https://arxiv.org/pdf/1409.0473v7) §4.2。束搜索宽度与集成数量是不同参数。
[^reverse]: [seq2seq](https://arxiv.org/pdf/1409.3215v3) §2、§3.3、Table 1。表 1 单模型束宽 12 的成绩为 26.17 与 30.59；§3.3 另概述 BLEU 25.9→30.6、困惑度 5.8→4.7，本文对照表采用表 1 数字，不把不同位置的数值混作精确相同的一次记录。作者对倒序原因的解释保留了不确定性。
[^seq2seq-long]: [seq2seq](https://arxiv.org/pdf/1409.3215v3)，§3.7、Figure 3 及其图注；本篇只使用图注给出的条件与趋势，不从像素估算逐点 BLEU，也不将未出现的退化外推到无限长度。
[^attention-model]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，§3.1–3.2、Figure 1、Appendix A.2。对齐分数用前一步解码状态与源位置 annotation；softmax 权重在源位置上归一化，再求加权和。实现附录在输出层使用前一步状态，正文则以当前状态概述输出函数；本文按两者共有的信息依赖解释，不把简化步骤写成逐行实现。
[^attention-implementation]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，Appendix A.1.1–A.1.2：Cho 式门控单元使用 update/reset gates，与 LSTM 相似但并非同一种结构；对齐网络采用单隐层前馈计算。源位置中与当前目标步无关的变换可以预先计算。
[^alignment-training]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，§3.1：软对齐允许翻译损失梯度反向传播，对齐模型与整个翻译模型联合训练；无需另外提供人工逐词对齐标签。这不等于无需平行句对。
[^alignment-figure]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，Figure 3 与 §5.2.1：灰度 0 为黑、1 为白；图 (a) 为一个选定句子，(b–d) 从无未知词、长度 10–20 词的测试句中随机选取。图展示软权重，没有提供全测试集的金标准对齐准确率。
[^seq2seq-results]: [seq2seq](https://arxiv.org/pdf/1409.3215v3)，§3.1、§3.6、Tables 1–2。BLEU 采用分词后的预测与参考、区分大小写、multi-bleu.pl；作者对最佳 WMT 系统重算为 37.0，与网站原报 35.8 不同。36.5 来自五个倒序 LSTM 参与重排统计基线的 1,000-best 候选。
[^bleu]: Papineni 等，[BLEU: a Method for Automatic Evaluation of Machine Translation](https://aclanthology.org/P02-1040.pdf)，ACL 2002，§2.1–2.2：modified n-gram precision、对重复计数的截断、语料级汇总与 brevity penalty。这里解释评价机制，不将表面片段匹配当成完整语义判断；原文也明确提醒，单句得分常会偏离人的判断。
[^seq2seq-engineering]: [seq2seq](https://arxiv.org/pdf/1409.3215v3)，§3.4–3.5：单模型约 384M 参数，四层 LSTM 与词表输出分别分配到八张 GPU，训练约十天；该时间与实现对应，不是五模型集成的总耗时承诺。
[^attention-results]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，§4、§5.1、Table 1。无未知词列同时筛源句与参考译文，并禁止模型输出 UNK；Moses 使用额外 418M 词单语料。RNNsearch 使用双向编码器，不能把与基本模型的对照描述成严格等参数的单组件消融。
[^attention-training]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，Appendix B、Table 2：RNNsearch-50 为 111 小时、2.2 epochs；星号版本为 252 小时、5.0 epochs，均为 Quadro K-6000。表中其余约五天模型与继续训练版本分开。
[^long-examples]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，Figure 2、§5.2.2、Appendix C。正文中的医生与 Disney 例子是对论文所列英文、法文的中文解释；它们是特定测试案例，不是对所有长句的承诺。
[^attention-cost]: [Bahdanau](https://arxiv.org/pdf/1409.0473v7)，§6.1、§7、Appendix A.1.2：每目标位置需处理全部源位置，另讨论 Graves 的单调注意力前驱及未知、稀有词问题。这里讨论打分次数，不把它当成含隐藏维度与词表输出的完整复杂度。
[^history]: [seq2seq 官方版本历史](https://arxiv.org/abs/1409.3215)、[Bahdanau 官方版本历史](https://arxiv.org/abs/1409.0473)，及两篇首页署名。本文用 seq2seq v3（2014-12-14）与 Bahdanau v7（2016-05-19，页眉 ICLR 2015）；Ilya 的 AlexNet 作者身份可参见[第 2 节](./AI演义_02_AlexNet_图像识别突破_科普讲解_20261104.md)。没有采用口播中未进一步核实的当代职务或完整合作履历。
[^seq2seq-representation]: [seq2seq](https://arxiv.org/pdf/1409.3215v3)，§3.8、Figure 2：句子隐状态的二维 PCA 投影展示词序与主动、被动语态的部分关系。图中有限例子不构成一般句义理解的完整评估。
