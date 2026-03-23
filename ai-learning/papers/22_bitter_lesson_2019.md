# The Bitter Lesson

**Rich Sutton — March 13, 2019**
原文链接：http://www.incompleteideas.net/IncIdeas/BitterLesson.html

---

## 英文原文

The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective, and by a large margin. The ultimate reason for this is Moore's law, or rather its generalization of continued exponentially falling cost per unit of computation. Most AI research has been conducted as if the computation available to the agent were constant (in which case leveraging human knowledge would be one of the only ways to improve performance) but, over a slightly longer time than a typical research project, massively more computation inevitably becomes available. Seeking an improvement that makes a difference in the shorter term, researchers seek to leverage their human knowledge of the domain, but the only thing that matters in the long run is the leveraging of computation. These two need not run counter to each other, but in practice they tend to. Time spent on one is time not spent on the other. There are psychological commitments to investment in one approach or the other. And the human-knowledge approach tends to complicate methods in ways that make them less suited to taking advantage of general methods leveraging computation.

There were many examples of AI researchers' belated learning of this bitter lesson, and it is instructive to review some of the most prominent. In computer chess, the methods that defeated the world champion, Kasparov, in 1997, were based on massive, deep search. At the time, this was looked upon with dismay by the majority of computer-chess researchers who had pursued methods that leveraged human understanding of the special structure of chess. When a simpler, search-based approach with special hardware and software proved vastly more effective, these human-knowledge-based chess researchers were not good losers. They said that "brute force" search may have won this time, but it was not a general strategy, and anyway it was not how people played chess. These researchers wanted methods based on human input to win and were disappointed when they did not.

A similar pattern of research progress was seen in computer Go, only delayed by a further 20 years. Enormous initial efforts went into avoiding search by taking advantage of human knowledge, or of the special features of the game, but all those efforts proved irrelevant, or worse, once search was applied effectively at scale. Also important was the use of learning by self play to learn a value function (as it was in many other games and even in chess, although learning did not play a big role in the 1997 program that first beat a world champion). Learning by self play, and learning in general, is like search in that it enables massive computation to be brought to bear. Search and learning are the two most important classes of techniques for utilizing massive amounts of computation in AI research. In computer Go, as in computer chess, researchers' initial effort was directed towards utilizing human understanding (so that less search was needed) and only much later was much greater success had by embracing search and learning.

In speech recognition, there was an early competition, sponsored by DARPA, in the 1970s. Entrants included a host of special methods that took advantage of human knowledge---knowledge of words, of phonemes, of the human vocal tract, etc. On the other side were newer methods that were more statistical in nature and did much more computation, based on hidden Markov models (HMMs). Again, the statistical methods won out over the human-knowledge-based methods. This led to a major change in all of natural language processing, gradually over decades, where statistics and computation came to dominate the field. The recent rise of deep learning in speech recognition is the most recent step in this consistent direction. Deep learning methods rely even less on human knowledge, and use even more computation, together with learning on huge training sets, to produce dramatically better speech recognition systems. As in the games, researchers always tried to make systems that worked the way the researchers thought their own minds worked---they tried to put that knowledge in their systems---but it proved ultimately counterproductive, and a colossal waste of researcher's time, when, through Moore's law, massive computation became available and a means was found to put it to good use.

In computer vision, there has been a similar pattern. Early methods conceived of vision as searching for edges, or generalized cylinders, or in terms of SIFT features. But today all this is discarded. Modern deep-learning neural networks use only the notions of convolution and certain kinds of invariances, and perform much better.

This is a big lesson. As a field, we still have not thoroughly learned it, as we are continuing to make the same kind of mistakes. To see this, and to effectively resist it, we have to understand the appeal of these mistakes. We have to learn the bitter lesson that building in how we think we think does not work in the long run. The bitter lesson is based on the historical observations that 1) AI researchers have often tried to build knowledge into their agents, 2) this always helps in the short term, and is personally satisfying to the researcher, but 3) in the long run it plateaus and even inhibits further progress, and 4) breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning. The eventual success is tinged with bitterness, and often incompletely digested, because it is success over a favored, human-centric approach.

One thing that should be learned from the bitter lesson is the great power of general purpose methods, of methods that continue to scale with increased computation even as the available computation becomes very great. The two methods that seem to scale arbitrarily in this way are search and learning.

The second general point to be learned from the bitter lesson is that the actual contents of minds are tremendously, irredeemably complex; we should stop trying to find simple ways to think about the contents of minds, such as simple ways to think about space, objects, multiple agents, or symmetries. All these are part of the arbitrary, intrinsically-complex, outside world. They are not what should be built in, as their complexity is endless; instead we should build in only the meta-methods that can find and capture this arbitrary complexity. Essential to these methods is that they can find good approximations, but the search for them should be by our methods, not by us. We want AI agents that can discover like we can, not which contain what we have discovered. Building in our discoveries only makes it harder to see how the discovering process can be done.

---

## 中文译文

**苦涩的教训**
理查德・萨顿
2019 年 3 月 13 日

从人工智能七十年的研究历程中，我们能汲取的最重要教训是：**借力计算能力的通用方法，最终会成为最有效的方法，且优势显著**。究其根本，这得益于摩尔定律，或者更准确地说，是单位计算成本持续呈指数级下降的普遍趋势。绝大多数人工智能研究的开展，都默认智能体可调用的计算能力是固定不变的（在这种前提下，借助人类知识成为提升性能的为数不多的途径）；但只要时间跨度稍长于一个典型的研究项目，海量的新增计算能力就必然会出现。为了在短期内取得实质性的改进，研究者们会试图借助自身对相关领域的人类知识，然而从长远来看，唯一真正重要的，是对计算能力的挖掘与利用。这两种思路并非必然相悖，但在实际研究中却往往相互冲突——投入其中一种思路的时间，无法再用于另一种；研究者会在心理上对所选择的研究方法产生投入性的执念；而依托人类知识的研究思路，还容易让方法变得复杂，使其更难适配借力计算能力的通用方法。

人工智能研究者们屡次迟滞才领悟这一苦涩的教训，回顾其中最具代表性的几个案例，能给我们带来诸多启发。

在计算机国际象棋领域，1997 年击败世界冠军卡斯帕罗夫的算法，核心是大规模的深度搜索。彼时，这一结果让绝大多数计算机国际象棋研究者倍感沮丧——他们此前一直深耕的，是依托人类对国际象棋特殊棋理结构的理解所设计的方法。当一种结合了专用软硬件、更简洁的基于搜索的方法展现出远超预期的效果时，这些秉持人类知识导向的象棋研究者，却无法坦然接受失败。他们声称，这种"暴力"搜索或许此次取胜，但并非通用策略，更何况这并非人类下象棋的方式。这些研究者一心希望依托人类知识的方法获胜，而当结果不如所愿时，他们陷入了失望。

计算机围棋领域的研究进展，也呈现出相似的模式，只是这一过程又延后了二十年。最初，研究者们投入了大量精力，试图借助人类对围棋的认知、利用围棋的专属特征来规避搜索；可一旦规模化的高效搜索方法落地，所有这些努力都被证明毫无意义，甚至还起到了反作用。此外，通过自我对弈学习来构建价值函数的方法也至关重要（这一方法也应用于诸多其他棋类游戏，甚至包括国际象棋——尽管 1997 年首个击败世界冠军的国际象棋程序，并未让学习发挥太大作用）。自我对弈学习，乃至广义上的机器学习，与搜索方法有着共通之处：二者都能让海量计算能力发挥实际效用。在人工智能研究中，搜索与学习是挖掘海量计算能力价值的两类最重要技术。和计算机国际象棋一样，计算机围棋的研究者最初也将精力放在利用人类的认知理解上（以求减少对搜索的依赖），直到许久之后，拥抱搜索与学习的思路，才带来了突破性的成功。

语音识别领域也有类似的经历。上世纪 70 年代，美国国防高级研究计划局资助了一场早期的技术竞赛。参赛方中，许多团队采用的是依托人类知识的专用方法——利用关于词汇、音素、人类声道的各类知识；而另一派则是新兴的统计类方法，以隐马尔可夫模型为基础，进行远更大量的计算。最终，统计方法再次战胜了依托人类知识的方法。这一结果推动了自然语言处理全领域的重大变革，数十年间，统计方法与计算能力逐渐成为该领域的核心。近年来，深度学习在语音识别中的崛起，正是这一发展方向的最新延续。深度学习方法对人类知识的依赖进一步降低，而是借助海量训练集的学习，结合更庞大的计算量，打造出性能大幅提升的语音识别系统。与棋类研究的历程如出一辙，研究者们总是试图让系统按照自己所理解的人类思维方式运作——试图将人类的认知知识植入系统；但事实证明，当摩尔定律带来海量计算能力，且人们找到利用这些算力的有效方式后，此前的做法最终会产生反效果，也让研究者的时间付出沦为巨大的浪费。

计算机视觉领域，同样遵循着这一规律。早期的研究方法，将视觉识别拆解为边缘检测、广义柱体识别，或是基于尺度不变特征变换的特征提取。但如今，这些方法均已被摒弃。现代深度学习神经网络仅运用卷积运算和特定的不变性概念，却实现了远更优异的性能。

这是一个至关重要的教训。作为一个研究领域，我们至今仍未彻底领悟它，依旧在重复着同样的错误。要认清这一点，并有效规避这类错误，我们必须理解这些错误背后的吸引力，必须铭记这一苦涩的教训：将人类自身的思维方式硬植入智能体，从长远来看毫无效果。这一教训建立在历史经验的总结之上：

1. 人工智能研究者往往试图将人类知识植入智能体；
2. 这种做法在短期内总能带来成效，也能让研究者获得个人层面的成就感；
3. 但从长远来看，这种方法会陷入发展瓶颈，甚至阻碍后续的技术进步；
4. 突破性的进展最终总会来自相反的研究思路——通过搜索与学习实现计算能力的规模化利用。

这份迟来的成功总带着一丝苦涩，且往往难以被研究者完全接受，因为它战胜了研究者所偏爱、以人类为中心的研究思路。

从这一苦涩的教训中，我们首先应认识到通用方法的巨大威力——这类方法即便在计算能力大幅提升的情况下，仍能持续借助算力实现性能的迭代升级。而在这方面，似乎能无限适配算力提升的两类方法，正是**搜索**与**学习**。

其次，我们还应领悟：人类大脑的实际运作机制，极为复杂，且复杂到无法简化还原。我们应当停止尝试寻找理解大脑运作的简单范式，比如试图用简单的方式去定义空间、物体、多智能体交互或对称性。这些概念都属于纷繁复杂、具有内在复杂性的外部世界，其复杂程度无穷无尽，绝非适合硬植入智能体的内容。相反，我们应当为智能体植入的，只是能够发现并捕捉这种无规复杂性的**元方法**。这类方法的核心特质，是能自主找到对复杂问题的优质近似解，而寻找这些解的过程，理应由方法自身完成，而非由人类代劳。我们想要的人工智能体，是能够像人类一样自主探索发现的智能体，而非仅仅装载着人类已有发现的"容器"。将人类的发现成果硬植入智能体，只会让我们更难探索出智能体自主发现的底层逻辑。

---

## 核心观点提炼

> **一句话概括**：AI 70年历史反复证明，"硬编码人类知识"的方法短期有效但长期必败；"让通用方法配合算力扩展"的路线，长期总是赢。

**四个历史案例的共同模式**：
- 国际象棋（1997）：深度搜索 > 棋理知识
- 围棋（2016）：自我对弈学习 > 人类棋谱
- 语音识别（1970s→2010s）：HMM → 深度学习，统计方法持续胜出
- 计算机视觉（2012）：深度CNN > 手工特征（SIFT/边缘检测）

**两个应该坚信的结论**：
1. 搜索（Search）和学习（Learning）是能随算力无限扩展的两类根本方法
2. 不要试图将"人类对世界的理解"硬编入AI，而要构建能自己学习世界的元方法

**与硬件彩票的关联**：
《The Bitter Lesson》解释了"为什么通用方法会赢"，而硬件彩票视角补充了"为什么这些通用方法恰好在这个时间点赢了"——算力形态（GPU/TPU的矩阵加速）与 Transformer 等架构的完美共振，使"能随算力扩展"的方法得以兑现。

→ 延伸阅读：[AI发展时间线·硬件彩票章节](../roadmap/AI_Development_Timeline.md)
