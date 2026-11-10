---
title: "AI演义·12｜RefinedWeb：筛选与去重怎样影响训练数据"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
semantic_tags: ["AI演义", "RefinedWeb", "Falcon", "训练数据", "数据去重", "科普讲解"]
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·12｜RefinedWeb：筛选与去重怎样影响训练数据

[返回总览第 12 节](../AI演义_笔记分析与项目整合报告.md#paper-refinedweb) · [上一章：ZeRO](AI演义_11_ZeRO_多卡怎样分担训练显存_科普讲解_20261105.md)

一篇解释猫睡眠的网页，正文旁可能有导航、广告和登录提示；文章被转载或跨月重复抓取后，还会在数据集中出现许多遍。网页文件越来越多，独特且适合训练的材料却未必同比增加。

2023 年的 RefinedWeb 从 CommonCrawl 提取正文、过滤文本并去重，再通过模型训练比较数据效果。在论文的零样本评测中，处理后的网页能达到或超过一些精选混合语料，但过滤规则换到另一套数据上，也可能降低成绩。[^paper]

<a id="data-question"></a>

## 1. 扩大可用语料

Chinchilla 将模型规模与训练量的配比提上日程。RefinedWeb 引用它，继续研究万亿 token 训练所需的数据从哪里来。[^motivation]

Token 是模型处理文本的单位，训练反复预测下一个 token，因此语料决定了它接触的表达、事实和模式。常见方案将网页与书籍、论文、问答等来源混合；“精选”往往指人选择来源和处理规则，不是逐句人工标注。

增加这类来源会遇到数量、格式与使用条件问题。RefinedWeb 选择从充足的公开网页中扩大可用材料，而不是主要依靠更多遍地重复旧数据。“只用网页”描述获取渠道，网页仍可以包含技术文章和专业知识。

<a id="one-webpage"></a>

## 2. 三种处理解决不同问题

对前面的猫文章，需要分别处理页面内部的模板和数据集里的重复：

| 处理 | 要解决的问题 |
|---|---|
| 正文提取 | 将文章与导航、侧栏、页面模板分开 |
| 过滤与修整 | 判断语言、长度、重复行和零碎内容是否适合目标训练 |
| 去重 | 找出近似整篇副本，以及不同文章中的相同长片段 |

干净文章仍可能重复出现，整体不同的文章也可能共享网站声明。论文将处理流水线称为 **Macrodata Refinement（MDR）**，产出的数据叫 **RefinedWeb**，用于检验它的模型叫 **Falcon-RW**。[^pipeline]

<a id="filtering"></a>

## 3. 正文提取与过滤

作者从 CommonCrawl 的原始 HTML 重新提取内容，用 trafilatura 尽量识别正文，而不直接依赖可能混有模板的现成纯文本。网址与域名也参与过滤，Wikipedia、arXiv、Stack Overflow 等常见精选来源被特意排除，以更清楚地检验普通网页路线，也便于之后与精选数据混合。[^filter-details]

这批数据主要用于英语预训练。FastText 做语言识别，规则继续检查异常长度、过多符号、重复行或短片段等。逐行处理还识别社交计数、登录和“阅读更多”等提示；若这类标记行的词数超过全文 **5%**，就丢弃文档。这是当前任务的选择，不能直接用于代码或其他语言的数据。

作者称这类设计为 neutral filtering，意在减少“高质量文本分类器”自身偏好的影响。流程仍会使用模型，例如语言识别，以及 ToxicBERT 提供样本辅助网址规则检查。人工审查发现域名名单误拦正常博客和流行文化新闻后，还修正了名单。

因此过滤包含目标和取舍。评估时既要看噪声减少，也要查有用内容是否被误删。

<a id="deduplication"></a>

## 4. 整篇近重复与精确重复片段

### MinHash 查找近似副本

MinHash 根据文本短片段计算便于比较的指纹。经过大小写、空白等规范化后，转载中少量修改的文档仍可能被归为一组，再随机保留一篇。它检测的是字面重合，不判断谁是原作者、哪篇更新或更可信。[^dedup]

近似检测也可能误删。为扩大查重范围，作者没有对每一匹配再算真实文本相似度来排除误报。附录展示了站点地图提示、Cookie 声明、JavaScript 提示和网址参数变化等重复群；重复不一定来自转载，也可能来自网站生成方式。[^duplicates]

### 精确去重删除长片段

两篇分别讲猫和狗的文章可能整体不同，却包含同一段很长的网站说明。精确片段去重用后缀数组等文本索引寻找规范化后相同的长文本，并切掉识别出的重复片段。

这里会删除该片段的**全部副本**，与 MinHash 留下一篇的处理不同，甚至可能在句中切开，损伤连贯性。[^dedup] 重复内容也可能有用，附录就有不同鞋款共同使用量脚说明的例子；算法没有判断说明是否必要。[^duplicates]

### 先后组合的理由

先做更易扩展的近似去重，能减轻精确查重的规模压力。小规模对照中，单用 MinHash 弱于精确去重，合用也未显著超过单用精确去重，组合包含工程上的取舍。[^dedup-ablation]

作者还试过保留重复片段但不计算其损失，表现较差；直接丢掉含重复片段的整篇文档有时略好，却会损失更多材料。最后选择切片段，兼顾效果和可用数据量。

完整语料分为 **100 份**处理，各份内做内容去重，跨份用网址记录减少同址重复。不同网址、不同分片之间仍可能留下相同内容。

<a id="controlled-experiments"></a>

## 5. 用训练结果判断处理效果

作者控制模型与训练设置，替换数据，比较训练后的表现。Table 4 的 1B、3B 两档分别训练 **27B、60B token**，即270亿与600亿。下表为六项零样本任务的平均准确率：HellaSwag、Winogrande、PIQA、ARC、SciQ 和 BoolQ。[^experiments]

| 预训练数据 | 1B 规模，27B token | 3B 规模，60B token |
|---|---:|---:|
| The Pile：精选混合语料 | 53.4% | 57.9% |
| C4：处理过的网页 | 55.7% | 59.6% |
| OSCAR-21.09 | 55.0% | 59.1% |
| OSCAR-22.01 | 52.7% | 55.9% |
| RW-Raw：流程早期版本 | 52.7% | 57.4% |
| RW-Filtered：再加文本过滤 | 54.3% | 58.2% |
| RefinedWeb：过滤后去重 | **56.2%** | **59.8%** |

RW-Raw 已完成网址处理、正文提取和语言识别，不是未处理的互联网。这里也没有 RefinedWeb 单独去重、不做过滤的对照。

1B 条件下，从早期版本到完整 RefinedWeb 提高 **3.5 个百分点**，比 The Pile 高 **2.8 个百分点**，说明加工后的网页可以成为强基线。相对 C4 的差距只有 **0.5 个百分点**，3B 时缩至 **0.2 个百分点**，不宜描述为普遍的大幅领先。

平均值可能掩盖各任务差异，完整研究模型也没有多次重训以测运行随机性，因此小差距尤其要审慎解释。较大研究模型 Falcon-RW 约 **13亿、75亿参数**，各训练 **3,500亿 token**。[^larger-models] 与外部模型的比较混有不同评测工具、提示和训练预算，应逐项阅读，不能概括为小模型全面超过 GPT-3。

<a id="counterexamples"></a>

## 6. 过滤不是越多越好

Table 5 对 OSCAR-22.01 的小规模结果提供了对照：[^counterexamples]

| 处理方式 | 六项平均准确率 |
|---|---:|
| 原有数据 | 52.7% |
| 再过滤 | 52.3% |
| 再去重 | 55.6% |
| 过滤与去重 | 55.4% |

过滤下降 **0.4 个百分点**，两者合用也略低于单独去重。C4 加过滤与去重后达到 **56.4%**，还略高于 RefinedWeb 的 **56.2%**，但更严格规则会减少最终可用语料，使万亿 token 的数据建设更困难。

质量要结合训练长度、独特材料数量和目标任务判断。数据删得太少，重复会被放大；删得太多，可能只能反复训练剩下的材料。

Pythia 在 The Pile 上观察到较小的去重收益。RefinedWeb 作者提出数据类型、方法和训练遍数等可能原因，但没有逐一排除。小规模多遍实验也只显示部分有利迹象，任务之间变化较大，不能据此假定去重后的文本可以无限重复使用。[^repeat-and-disagreement]

<a id="people-and-scale"></a>

## 7. 数据工程和公开范围

Guilherme Penedo 等九位作者来自 TII、LightOn 和法国高师相关实验室，数据集由 TII 创建并资助。[^people] 工作使用 CommonCrawl、trafilatura、fastText，并借鉴 Lee 等人的去重实现；贡献在于将它们组织为可扩展流程，并用训练验证选择。

处理通常使用约 **1万至2万个 vCPU**，精确去重的云实例最高提供 **2 TiB 内存**。[^compute] VCPU 是虚拟 CPU，TiB 是二进制内存单位。自动化节省了逐项手工处理，却仍需要算力、内存和人工检查规则。

V1 报告完整数据约 **5 万亿 token**，公开其中约 **6,000 亿**。同一公开子集按不同 tokenizer 计算，官方数据卡给出约 **5,000亿至6,500亿**，会议摘要采用 **5,000 亿**；版本和分词口径要同时说明。[^release]

研究模型 **Falcon-RW-1B/7B** 只用 RefinedWeb，**Falcon-7B/40B** 则把它与精选语料混合。验证网页路线，并不等于实际模型必须只使用网页。

V1 还将自家预处理软件标为尚未公开，最终生产数据没有保存全部中间产物。公开子集允许外部研究者训练和比较，却不足以逐步复现完整数据制作。数据也仍可能含敏感信息、偏见、有害内容、错误或残余重复，有限的毒性分析不能代替全部用途审查。[^data-limits]

<a id="route-and-limits"></a>

## 8. 数据规则要随任务变化

Scaling Laws 研究怎样分预算，ZeRO 研究如何执行，RefinedWeb 则检验大量文本的取得与处理。它为扩大可用网页语料提供了证据，但长尾知识、多语言、重复训练和新知识来源仍然需要研究。[^lecture]

[下一章 LAION](AI演义_13_LAION_图文怎样变成训练数据_科普讲解_20261105.md)仍从网页出发，目标却变为图文是否对应，筛选方法也会变化。

<a id="questions"></a>

[推测] 个人资料检索更可能需要保留原文、来源和时间。同一法条在不同文档中的引用，或一个网址在不同日期的版本，可能正是任务需要的证据。可以借鉴处理后评测的方法，但不直接照搬预训练语料的删除规则。平均准确率仅差0.2个百分点时，也应继续检查单项表现、重复实验和成本，而不急于给数据贴上更好的标签。

<a id="source-scope"></a>

## 来源与修订范围

技术与实验依据为 **2023-06-01 的 RefinedWeb arXiv v1**。本次沿用原稿对32页正文、附录及Table 4／5的核验，官方数据卡用于公开子集和模型用途，会议摘要用于对照另一数量口径，没有重做语料或训练。

[讲义第30页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=30)与[第117期播客](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)提供叙事，相关转写约 **02:11:09–02:13:38**，不是节目单独标注的精确章界；另有 [Apple Podcasts](https://podcasts.apple.com/cn/podcast/id1634356920?i=1000733801180)入口。

转写中的技术名按论文校正，未逐字听校或测量准确率。语料垄断的口述未当作行业结论，提到的 Hugging Face“三部曲”也未唯一定位，不补猜链接。原始转写保留在私有来源中。

## 来源与延伸阅读

[^paper]: Penedo 等，[The RefinedWeb Dataset for Falcon LLM](https://arxiv.org/abs/2306.01116v1)，2023-06-01；[仓内 PDF](../../papers/30_refinedweb_2023.pdf)。核心结论见 §4.2–4.3，表 4–5；本报告不把所读版本的实验泛化为所有模型与任务。
[^motivation]: [论文 pp.1–3](../../papers/30_refinedweb_2023.pdf#page=1)，§1–2；引言连接 Chinchilla 的训练数据需求，并讨论扩大采集与重复训练两条路线。
[^pipeline]: [论文 pp.4–6](../../papers/30_refinedweb_2023.pdf#page=4)，§3、图 2；MDR、RefinedWeb、预处理及后续过滤阶段的区别。主文 §3.1 从 WARC 原 HTML 提取内容；附录数据表中另有 WET 字样，本报告的流程解释按详细方法章节。
[^filter-details]: [论文 pp.26–27](../../papers/30_refinedweb_2023.pdf#page=26)，附录 G.1–G.2、表 13–14；包括域名误杀修正、ToxicBERT 辅助检查、精选来源排除名单，以及按标记行词数计算的 5% 规则。
[^dedup]: [论文 §3.3](../../papers/30_refinedweb_2023.pdf#page=6)及[附录 G.3](../../papers/30_refinedweb_2023.pdf#page=28)；MinHash、规范化、精确片段检索及处理方式。附录 G.3.2 明确精确去重删除所有匹配副本，并讨论切断句子的代价；主文说明分为 100 份处理及跨份网址记录。
[^duplicates]: [论文 pp.30–32](../../papers/30_refinedweb_2023.pdf#page=30)，附录 H、表 15–17，列出真实重复群、网址参数变化和精确片段例子。正文猫的文章为教学示意，鞋款量脚说明来自原论文案例。
[^dedup-ablation]: [论文 p.20](../../papers/30_refinedweb_2023.pdf#page=20)，附录 E.1、表 8；使用早期开发版本，1B 规模模型训练 30B token，三项任务聚合。其绝对分数不能与正文表 4、表 5直接混比。
[^experiments]: [论文 p.7](../../papers/30_refinedweb_2023.pdf#page=7)，§4.1–4.2、表 4；1B/3B 规模模型分别训练 27B/60B token。[p.6 表 3](../../papers/30_refinedweb_2023.pdf#page=6)和附录 F.1 区分任务组；此处为 small 六项零样本任务聚合，不含 core 组中的 LAMBADA 与 OpenBookQA。表 5 注明 RefinedWeb 缺少单独去重条件；[p.18 模型卡](../../papers/30_refinedweb_2023.pdf#page=18)说明完整研究模型没有多次训练以测量运行间变异。
[^larger-models]: [论文 pp.7–8](../../papers/30_refinedweb_2023.pdf#page=7)、[附录 F.1–F.2 及表 10–11](../../papers/30_refinedweb_2023.pdf#page=21)。Falcon-RW 的实际参数量为约 1.3B/7.5B；GPT-3 API 的同工具结果与 GPT-3 原论文结果分开登记，未与不同训练预算的 LLaMA 直接比较。
[^counterexamples]: [论文 pp.8–9](../../papers/30_refinedweb_2023.pdf#page=8)，§4.3、表 5。百分比差值按“百分点”理解；作者讨论过滤规则需要随来源调整，以及更严格筛选对总规模的影响。
[^repeat-and-disagreement]: [论文 p.21](../../papers/30_refinedweb_2023.pdf#page=21)，附录 E.3：固定训练量的小规模多遍实验；[p.22](../../papers/30_refinedweb_2023.pdf#page=22)，附录 F.2：与 Pythia 去重结果的差异及未排除的解释。
[^people]: [论文首页](../../papers/30_refinedweb_2023.pdf#page=1)及[附录 A，p.15](../../papers/30_refinedweb_2023.pdf#page=15)。仅据作者署名、单位和数据创建/资助说明，不推断逐人的具体分工。
[^compute]: [论文 p.29](../../papers/30_refinedweb_2023.pdf#page=29)，附录 G.4；这里 vCPU 是虚拟 CPU，TiB 是二进制内存单位，不能当作 GPU 核心数或本机实测成本。
[^release]: v1 [摘要](../../papers/30_refinedweb_2023.pdf#page=1)与 §6 的完整集 5T、公开子集 600B；[附录 A，pp.16–17](../../papers/30_refinedweb_2023.pdf#page=16)说明预处理软件、生产中间产物及完整数据的公开边界。[官方数据卡](https://huggingface.co/datasets/tiiuae/falcon-refinedweb/blob/main/README.md)说明公开子集约 500–650GT，取决于 tokenizer，并区分 Falcon-RW 与 Falcon-7B/40B 的训练数据。GT 在这里表示十亿 token。[NeurIPS 2023 摘要](https://papers.nips.cc/paper_files/paper/2023/hash/fa3ed726cc5073b9c31e3e49a807789c-Abstract-Datasets_and_Benchmarks.html)记作 500B。网页核对日期为 2026-11-05，未将动态数据卡当作固定软件版本。
[^data-limits]: [论文 §5](../../papers/30_refinedweb_2023.pdf#page=9)、[附录 A–B](../../papers/30_refinedweb_2023.pdf#page=15)及[官方数据卡](https://huggingface.co/datasets/tiiuae/falcon-refinedweb/blob/main/README.md)的 Personal and Sensitive Information、Discussion of Biases、Other Known Limitations。许可为 ODC-By 1.0，使用还需遵守 CommonCrawl 条款；可公开访问不等于内容不含敏感信息。
[^lecture]: [《AI演义》讲义 p.30](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=30)提出“数据墙”与数据工程视角；本报告用原论文的实验范围、限制与官方数据卡收束这一概括。
