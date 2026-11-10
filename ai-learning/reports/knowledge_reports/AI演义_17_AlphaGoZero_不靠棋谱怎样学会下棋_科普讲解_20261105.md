---
title: "AI演义·17｜AlphaGo Zero：从搜索与自弈中学习下棋"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["ai_history", "alphago_zero", "reinforcement_learning", "self_play", "mcts", "test_time_compute"]
revision_scope: "文字与结构修订；保留原稿技术资料和历史核验记录，未重新复现实验。"
---

# AI演义·17｜AlphaGo Zero：从搜索与自弈中学习下棋

[返回总览第 17 节](../AI演义_笔记分析与项目整合报告.md#paper-alphago-zero) · [上一章：LoRA](AI演义_16_LoRA_少量参数怎样适配新任务_科普讲解_20261105.md)

2017 年，DeepMind 的 AlphaGo Zero 从随机网络开始，不用人类棋谱训练，通过自我对弈超过了此前的 AlphaGo 版本。网络先判断局面，搜索在落子前比较后果，整盘棋的输赢再提供反馈，三者共同产生下一轮训练所需的数据。[^paper]

<a id="problem-and-history"></a>

## 1. 不用棋谱，仍需要规则与算法

击败李世石的 AlphaGo 已经使用人类棋谱监督、自弈强化学习和搜索，另有人工围棋特征、分开的策略与价值网络等组件。Zero 撤去棋谱监督，并重组网络、搜索与训练流程。[^history]

预测高手会下哪里，与找到更有利于获胜的走法，是两个相关但不同的目标。减少对示范的依赖，也有助于研究缺少优质示范的任务；不过，“模仿一定不能超越人类”并不是这篇论文证明的结论。

研究者仍然提供围棋规则、合法动作、计分和棋盘表示，设计网络与学习算法。“从零”指随机权重和无人类棋谱的起点，不意味着撤去所有人类设计。论文共同第一作者为 David Silver、Julian Schrittwieser、Karen Simonyan，成果也承接了搜索、残差网络和团队的大规模实验。

<a id="state-policy-value"></a>

## 2. 网络输出落子建议与局面评价

假设轮到黑方，有两个候选落点 A、B。这是说明流程的例子，没有对应某张真实棋谱。

网络有两个输出头。策略头给出各落子及停着的建议分布 p；p(A)较高，表示更倾向选A。价值头给出当前执棋方最终输赢的估计 v，范围为 −1 到 +1。前者不是每个落子的胜率，后者也不是直接落在0到1之间的概率。

两个头共享残差主干，先提取局面特征，再分别用于决策与评价。这里用到了 [ResNet](AI演义_03_ResNet_深层网络如何训练_科普讲解_20261104.md) 的结构。[^network]

输入包括当前及此前共八个时刻双方的棋子分布，加上执棋颜色，共17个19×19平面。历史用来表达重复局面等规则所需的信息，单张当前棋盘并不充分。网络判断还可能出错，因此程序会在真正落子前继续搜索。

<a id="mcts-one-move"></a>

## 3. 搜索怎样改变建议

下面用一组自拟数字展示变化：

| 候选落子 | 网络建议 p | 搜索访问次数 |
|---|---:|---:|
| A | 55% | 480 |
| B | 35% | 960 |
| 其他合计 | 10% | 160 |

MCTS（蒙特卡洛树搜索）将自己的落子、对方应手和后续选择展开成树。每轮从当前局面出发，结合平均评价、网络建议和访问次数，选择值得进一步检查的分支；到达尚未展开的节点时，调用网络取得策略与价值，若已终局则按规则计分。随后沿路径更新访问次数和平均评价，注意随执棋方切换评价视角。重复到预算用完，再由根节点访问次数形成落子建议。[^search]

这些操作更新的是搜索树统计。一步搜索期间，网络权重保持不变，同一个网络会被反复调用；参数训练发生在之后。

表中共1,600次访问。直接归一化后，A、B、其他为 **30%、60%、10%**，得到搜索后的分布 π。网络原先更偏A，额外计算使搜索更偏B。π仍受网络误差、探索规则和预算影响，不保证是最优策略。

自弈开局前30手按访问次数分布采样，之后温度趋近零，基本选择访问最多的落子，因而表中的概率只说明前一种情况。三天训练版每步使用 **1,600次模拟**；一次模拟通常走到一个待评估节点，并非下完一盘棋，也不是向后看1,600手。Zero去掉旧版快速下到终局的rollout，改用网络评价非终局叶节点，树搜索本身仍然保留。

<a id="self-play-learning"></a>

## 4. 让网络学习搜索结果和真实输赢

每个训练位置保存局面s、搜索分布π和最终输赢z。沿用上表，策略头朝30%／60%／10%调整；价值头学习本盘结果，黑胜时黑方视角记+1、白方记−1。终局奖励很粗，一盘赢棋仍可能有坏着，需要大量局面帮助模型学出更稳定的关系。

训练损失包含策略误差、价值误差与参数正则项。[^training] 数据流如下：

```text
当前网络提出建议
        ↓
搜索比较后续可能
        ↓
按搜索结果落子，直至终局或认输
        ↓
保存局面、搜索建议、最终输赢
        ↓
训练新的网络，再检查是否进步
```

起初网络很弱，但规则已经能判输赢。网络从这些经验中改善，下一轮搜索获得更好的起点，再产生新的学习目标。论文将其解释为近似策略迭代。

自弈还需要避免过早固定做法。根节点加入Dirichlet噪声，增加尝试；允许明显败局提前认输以节省计算，同时让 **10%的棋局关闭认输、下到终局**，估计本来可能获胜却提前放弃的比例，调整阈值以争取将误认输控制在 **5%以下**。

数据生成、训练和评估异步运行。每1,000个训练步保存一个候选网络，与当前最佳网络对弈400局，胜率超过55%才替换用于后续自弈的版本。候选需要经过检验，单次参数更新并不保证棋力提高。

<a id="training-results"></a>

## 5. 两次训练的结果与计算开销

论文分别从随机权重训练三天版和四十天版，后者使用更大的网络，并非前者接着训练37天。[^results]

| 项目 | 三天版 | 四十天版 |
|---|---:|---:|
| 网络简称 | 20块 | 40块 |
| 自弈训练时长 | 约3天 | 约40天 |
| 自弈棋局 | 约490万盘 | 约2,900万盘 |
| 直接比赛对手 | AlphaGo Lee | AlphaGo Master |
| 100局结果 | 100–0 | 89–11 |

比赛采用每方2小时基本用时等条件。Lee是此前与李世石对弈的版本，Master是更强的另一版；表中两场比赛的对手均为程序。学习曲线在约36小时处显示三天版棋力超过Lee，72小时后才进行了100局直接比赛，两种证据要分开读。

20／40块是论文简称，Methods实际描述为一个卷积块加19／39个残差块。更大训练版虽然重新初始化，搜索参数曾借助较小实例优化，具体比赛规则与设置见脚注。

对弈搜索使用 **4个TPU**，网络参数优化另有 **64个GPU worker与19个CPU参数服务器**。每批2,048个局面，从最近50万盘自弈中抽样；两版分别完成约70万与310万个训练批次。[^training] 这些还不能单独代表自弈生成、优化和比赛的全部资源，因此不能用4个TPU估算整项训练成本。

<a id="imitation-versus-winning"></a>

## 6. 模仿落子与赢棋的分数并不一致

作者另用KGS人类棋谱训练同架构的监督网络，再用GoKifu职业棋谱比较它与三天自弈网络。[^comparison]

| 职业棋谱验证指标 | 监督版 | 自弈版 |
|---|---:|---:|
| 预测实际落子的准确率 | 54.3% | 49.0% |
| 胜负预测误差 ↓ | 0.207 | 0.177 |

监督版更会猜棋手下一手，自弈版对输赢估计更好，实际棋力也更强。自弈训练在24小时内就超过这一监督对照。若棋谱记录高手下A，预测A会提高模仿准确率；对局则要看A或B怎样影响胜负，两个目标未必一致。

胜负误差是按论文方式缩放的均方误差，不是输棋比例。此外，监督版降低了胜负损失的权重，两版并非仅数据来源不同的单变量实验，也不能据此断言人类棋谱普遍无用。

<a id="architecture-and-discovery"></a>

## 7. 架构与学出的棋法

Zero同时改了学习方式和网络架构。为辨别架构收益，作者固定先前训练的最后200万盘自弈数据，比较普通卷积／残差网络、策略价值分开／合并的四种组合。残差结构带来超过约600 Elo的提升，合并策略与价值网络也带来约600 Elo。[^ablation] Elo表示给定赛事下的相对棋力，两项增益不能当作任意场景可相加的常数。

合并输出头后，模仿人类落子略差，胜负评价与实际棋力却更好。作者认为，两个任务共同约束共享表示有助于学习；这是一种解释，尚非所有多任务训练都受益的规律。

作者的棋谱分析显示，早期网络偏爱吃子，随后逐渐表现出死活、全局布局与复杂战斗能力，重新发现若干职业定式，也偏好一些少见变化。[^knowledge] 征子是一种可能延伸很远的连续追吃战术，人类初学者常较早接触，Zero却较晚掌握。总体棋力和局部能力的发展顺序并不一致。这些是作者的棋谱分析；棋法相似仍不足以说明内部概念与人类相同。

<a id="search-and-reasoning"></a>

## 8. 训练后继续计算的收益

四十天版网络直接选策略概率最高的落子，在每步5秒的内部赛事评价中为 **3,055 Elo**；完整搜索版为 **5,185 Elo**。[^search-gain] 训练已经改善了网络判断，落子前的额外搜索仍带来很大收益。这说明一次前向输出与带搜索的决策过程，可能具有明显不同的能力。

讲义将这条线联系到o1。Sequoia对研究团队的访谈中，Noam Brown确实用AlphaGo解释行动前增加计算的价值，同时指出围棋MCTS依赖具体领域条件，o1则面向通用文本接口。OpenAI的公开文章报告，o1通过强化学习改进思维链，表现随训练计算和答题时计算增加而提高。[^o1] 两份材料支持思想联系，没有说o1直接采用每步1,600次MCTS，也未将其全部来源归于本篇论文。

Brown同时谈到人类数据的作用：早期AlphaGo从棋谱起步，GPT显示了大规模预训练的力量，强化学习可以与之结合。他以数独和首都知识作对比：数独有继续尝试、验证的路径；缺少某个首都的知识，单纯延长思考未必能补上。

同样，本章Elo差距只对应所测程序与赛事，不能外推成所有无搜索围棋模型都弱于任何人类。

<a id="transfer-limits"></a>

## 9. 自弈依赖怎样的环境

围棋具有可精确模拟的状态变化、合法动作、明确终局计分和双方可见的完整棋盘。论文将最直接适用范围定位于 **零和、完全信息博弈**。[^limits] 程序可以从同一局面分别试A、B；现实任务若无法准确模拟、试错昂贵或不可恢复，数据生成与搜索条件就变了。

奖励是否衡量了想要的行为，也需要单独检查。[推测] 如果研究报告只按引用数量奖励，模型可能学会堆引用，却没有学会判断来源是否支持结论。这是说明奖励设计的思想实验，论文未测过报告写作。

自弈还可能使Elo估计偏高，论文用已有程序和人类对局作参照。赢过当前版本与达到外部标准需要分别衡量。开放语言任务往往同时缺知识、可靠裁判和便宜的试错环境，因而不能从Zero成功直接推出应该撤去预训练与示范。DeepMind当年博客中的蛋白质、材料、能源应用属于愿景，并非这篇围棋论文的实验结果。

<a id="route-connections"></a>

<a id="questions"></a>

要进一步判断搜索何时有用，可以在可完全求解的小棋盘游戏中固定同一网络，比较直接落子、少量搜索和更多搜索，并用已知最优结果评估。这是一个后续实验设想。它也能帮助观察：不准确的网络何时会被搜索纠正，何时会反复强化原有偏差。

[下一章InstructGPT](AI演义_18_InstructGPT_模型怎样学会按要求回答_科普讲解_20261105.md)转向没有确定输赢的语言任务：邮件是否得体、回答是否有用，需要从人的示范与偏好建立训练反馈。

<a id="source-notes"></a>

## 来源与修订范围

本次沿用原稿对2017年围棋专用AlphaGo Zero论文正文、Methods和Extended Data图表的核验，未重训或复跑基准。它与后来研究围棋、国际象棋和将棋的AlphaZero论文不同。原稿全文来自身份对应的公开PDF镜像，Nature页面核对书目信息；未做逐字节文件认证，附录棋谱也未逐手复盘。Noam Brown访谈仅阅读相关段落，未观看整场视频。

讲义第16页，播客相关内容约 **01:08:31–01:15:35**，时间来自转写定位，并非shownotes的逐章标记。转写没有逐字听校或测量字错率，人物与公司后续故事未用于算法结论；原有[转写核查摘要](.quality/AI演义_17_AlphaGoZero_不靠棋谱怎样学会下棋_科普讲解_20261105.transcription-review.json)保留。

## 来源与延伸阅读

[^paper]: Silver et al.，[Mastering the game of Go without human knowledge](https://www.nature.com/articles/nature24270)，Nature 550, 354–359，2017-10-19，DOI 10.1038/nature24270。[本次实读的公开 PDF 镜像](https://augmentingcognition.com/assets/Silver2017a.pdf)，18 页，包含 Methods 与 Extended Data；正文首次介绍见 p. 1。
[^history]: 同论文 p. 1、[p. 7，Methods：AlphaGo versions、Domain knowledge](https://augmentingcognition.com/assets/Silver2017a.pdf#page=7)。另读 David Silver、Demis Hassabis 于 2017-10-18 发布的 [AlphaGo Zero: Starting from scratch](https://deepmind.google/discover/blog/alphago-zero-starting-from-scratch/)。讲义及节目：[讲义第 16 页](../../notes/终版：AI演义，36篇论文开启你的探索之旅.pdf#page=16)，[张小珺 Jùn 第 117 期小宇宙页面与 shownotes](https://www.xiaoyuzhoufm.com/episode/68ff9d1b083a71a4eb86c52c)，[Apple Podcasts 备用入口](https://podcasts.apple.com/cn/podcast/id1634356920?i=1000733801180)，2025-10-28，谢青池。
[^network]: 同论文 [p. 2，Figure 1](https://augmentingcognition.com/assets/Silver2017a.pdf#page=2)，[pp. 8–9，Neural network architecture](https://augmentingcognition.com/assets/Silver2017a.pdf#page=8)。输入 19 × 19 × 17；价值头采用 tanh，范围 −1 到 +1；策略头还含 pass。历史与颜色的必要性由重复局面规则、贴目等条件解释。
[^search]: 同论文 [p. 2，Figure 2](https://augmentingcognition.com/assets/Silver2017a.pdf#page=2) 和 [p. 8，Search algorithm、Self-play](https://augmentingcognition.com/assets/Silver2017a.pdf#page=8)。选择规则结合平均价值 Q 与探索项 U；π 按访问次数的 1/τ 次幂归一化。自弈前 30 手 τ=1，之后 τ→0；根节点加入 Dirichlet 噪声。原论文快棋训练每步 1,600 simulations，约 0.4 秒，时间限于当时系统配置。
[^training]: 同论文 [pp. 7–8，Reinforcement learning、Self-play training pipeline](https://augmentingcognition.com/assets/Silver2017a.pdf#page=7)。损失包含价值均方误差、策略交叉熵和 L2 正则。Optimization 为 64 GPU workers、19 CPU parameter servers，每 worker 32 个样本、总批量 2,048；最近 500,000 盘局面中均匀抽样。Evaluator 为 400 局、每步 1,600 simulations、最高访问次数落子，胜率超过 55% 晋级。Self-play 说明在 10% 的自弈中关闭认输，估计本可获胜却认输的 false positives，并将阈值目标设为低于 5%；Play 说明认输判断使用根节点及最佳子节点的价值。对弈搜索配置与梯度优化配置须分开。
[^results]: 同论文 [pp. 2–3，Empirical analysis、Figure 3](https://augmentingcognition.com/assets/Silver2017a.pdf#page=3) 与 [p. 5，Final performance、Figure 6](https://augmentingcognition.com/assets/Silver2017a.pdf#page=5)。两实例分别为 4.9 M／29 M 自弈棋局、700,000／3.1 M 训练批次，每批 2,048 个局面。直接对局采用每方 2 小时基本时间、3 次 60 秒读秒，中国规则、贴 7.5 目，见 p. 9 Evaluation；40 天版从随机网络权重重新训练，但搜索参数曾借助较小训练实例重新优化，不等于所有设置完全独立重选。
[^comparison]: 同论文 [p. 3，Figure 3](https://augmentingcognition.com/assets/Silver2017a.pdf#page=3)、[p. 16，Extended Data Table 1](https://augmentingcognition.com/assets/Silver2017a.pdf#page=16) 与 [p. 17，Extended Data Table 2](https://augmentingcognition.com/assets/Silver2017a.pdf#page=17)。表中两列均为论文称 20 块的网络，GoKifu validation 上为 54.3%／49.0%、0.207／0.177。Figure 3c 将原始胜负均方误差乘以 1/4，缩放到 0–1。监督版用 KGS 棋谱训练 3 天，其损失中的 MSE 项权重为 0.01，自弈版两项等权，见 p. 8 Supervised learning。
[^ablation]: 同论文 [pp. 3–4，Figure 4](https://augmentingcognition.com/assets/Silver2017a.pdf#page=3) 与 [p. 9，Neural network architecture comparison](https://augmentingcognition.com/assets/Silver2017a.pdf#page=9)。固定先前训练产生的最后 200 万盘自弈数据；四种组合为 dual–res、sep–res、dual–conv、sep–conv，网络均配合 Zero 搜索，图注比较为每步 5 秒。约 600 Elo 是各自对照下的结果，不是可以任意相加的通用收益。
[^knowledge]: 同论文 [pp. 4–5，Knowledge learned、Figure 5](https://augmentingcognition.com/assets/Silver2017a.pdf#page=4)，以及 Extended Data Figures 2–4。关于定式、征子和新变化，采用作者对棋局与频率的观察；未逐手复核所有附录棋谱。
[^search-gain]: 同论文 [p. 5，Figure 6b 及邻近正文](https://augmentingcognition.com/assets/Silver2017a.pdf#page=5)。每步 5 秒的内部赛事中，raw network 3,055、Zero 5,185、Master 4,858、Lee 3,739、Fan 3,144。Zero／Master 使用单机 4 TPU，其他对手的配置不同。Elo 的锚定及 self-play bias 见 p. 9 Evaluation，不宜外推为绝对人类等级。
[^o1]: [OpenAI：Learning to reason with LLMs](https://openai.com/index/learning-to-reason-with-llms/)，实读开篇、Chain of Thought 等公开正文；[Sequoia：Noam Brown and Team on Teaching LLMs to Reason](https://sequoiacap.com/podcast/training-data-noam-brown/)，实读访谈文字稿中的 Conviction in o1、What is reasoning?、Lessons from gameplay、The trough of disillusionment 及相关上下文。Noam 的 AlphaGo 比较是受访者本人陈述；网页开篇的“AlphaGo-style”概括来自编辑导语，二者不混作直接引言。没有确认节目所指的具体视频就是这场访谈，也未观看视频。
[^limits]: 同论文 [p. 7，Self-play reinforcement learning in games、Domain knowledge](https://augmentingcognition.com/assets/Silver2017a.pdf#page=7)，以及 p. 9 Evaluation。自弈／搜索使用 Tromp–Taylor 计分，比赛与评估使用中国规则。方法最直接适用零和、完全信息博弈；奖励漏洞与报告例子是本节分析，不是论文的跨领域实测结果。
