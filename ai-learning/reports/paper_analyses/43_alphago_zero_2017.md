---
title: "Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-04-25"
---

# Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm

## 重要说明：文件名与论文标题不一致

本报告基于项目本地 PDF `ai-learning/papers/24_alphago_zero_2017.pdf`。

PDF 正文标题是：

```text
Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
```

作者为 David Silver、Thomas Hubert、Julian Schrittwieser、Ioannis Antonoglou、Matthew Lai、Arthur Guez、Marc Lanctot、Laurent Sifre、Dharshan Kumaran、Thore Graepel、Timothy Lillicrap、Karen Simonyan、Demis Hassabis，机构为 DeepMind。

这不是 Nature 2017 的 `Mastering the game of Go without human knowledge` 原文，而是 arXiv:1712.01815v1，发表于 2017-12-05，主题是 AlphaZero 将 AlphaGo Zero 的 tabula rasa 自我对弈强化学习泛化到国际象棋、日本将棋和围棋。

因此，本报告按 PDF 真实内容精读 AlphaZero；文件名沿用项目任务预期的 `43_alphago_zero_2017.md`，但正文不把两篇论文混写。

---

## 基本信息卡片

```text
论文标题：Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm
作者：David Silver, Thomas Hubert, Julian Schrittwieser, Ioannis Antonoglou, Matthew Lai, Arthur Guez, Marc Lanctot, Laurent Sifre, Dharshan Kumaran, Thore Graepel, Timothy Lillicrap, Karen Simonyan, Demis Hassabis
机构：DeepMind, 6 Pancras Square, London
发表年份：2017
版本：arXiv:1712.01815v1, cs.AI, 2017-12-05
核心系统：AlphaZero
核心任务：Chess, Shogi, Go
重要性评级：⭐⭐⭐
```

---

## 一句话总结

> AlphaZero 用同一个自我对弈强化学习算法，在只知道规则、不使用人类棋谱和领域启发的条件下，数小时内超越 Stockfish、Elmo 和旧版 AlphaGo Zero。

---

## 读前定位

这篇论文的历史位置很特殊。

它不是 AlphaGo 第一次击败人类的论文。

它也不是 AlphaGo Zero 只研究围棋的 Nature 论文。

它的核心问题是：

如果把 AlphaGo Zero 中“人类知识最小化”的思想从围棋拿出来，是否能成为通用游戏学习算法？

作者选择了三个棋类领域：

- 国际象棋：AI 史上最经典的专家系统与搜索领域。
- 日本将棋：棋盘更大，吃子后可以打入，复杂度高于国际象棋。
- 围棋：AlphaGo 与 AlphaGo Zero 已经验证过神经网络加 MCTS 的路线。

论文想证明的不是“DeepMind 又做了一个更强棋类程序”，而是“规则 + 搜索 + 学习”可以替代大量人工特征、开局库、残局库和领域剪枝规则。

---

## Step 1 | 背景与动机（WHY）

### 1.1 传统棋类 AI 的强项

传统国际象棋程序已经非常强。

论文以 2016 TCEC 冠军 Stockfish 为代表，指出这类程序通常包含：

- 手工设计的位置特征。
- 中局和残局不同的物子价值。
- 兵型、王安全、机动性、象对、前哨等人工模式。
- alpha-beta 搜索。
- 静态交换评估、killer heuristic、history heuristic 等排序规则。
- 开局库。
- 六子或七子残局表。
- 专门处理“安静局面”的 quiescence search。

这些组件很有效，但它们高度依赖领域工程。

日本将棋程序 Elmo 也类似，依赖高优化 alpha-beta 搜索与领域适配。

### 1.2 AlphaZero 要解决的问题

AlphaZero 的目标是去掉这些人工组件。

论文明确说，AlphaZero 不使用：

- 手工评估函数。
- 手工 move ordering heuristics。
- 开局库。
- 残局表。
- 针对国际象棋或将棋定制的搜索增强。
- 人类专家棋谱监督学习。

它只使用：

- 棋类规则。
- 棋盘状态编码。
- 合法动作生成。
- 自我对弈。
- 神经网络。
- 通用 MCTS。

这个设定把研究问题变成：

> 给定规则，一个随机初始化的网络能否通过自我对弈学出超人策略？

### 1.3 为什么棋类仍是好测试

国际象棋并不天然适合卷积网络。

论文列出几个原因：

- 规则位置相关：兵从第二排可走两格，升变在第八排。
- 规则不对称：兵只向前，王翼和后翼易位不同。
- 存在长距离交互：后、车、象可跨越棋盘。
- 动作空间更复杂：需要选择棋子和目的地。
- 结果可能是胜、负、和，而不是围棋那样二元胜负。

将棋更复杂：

- 棋盘更大。
- 被吃掉的棋子会换边。
- 被吃棋子可重新打入棋盘。

所以如果 AlphaZero 在这些任务上成功，就比“围棋适配卷积网络”更能说明算法的通用性。

---

## Step 2 | 核心贡献（WHAT）

### 2.1 贡献一：单一 AlphaZero 算法跨三种棋类

论文把 AlphaGo Zero 思想推广成 AlphaZero。

同一套算法分别训练三个实例：

- Chess。
- Shogi。
- Go。

除少数探索噪声参数随典型合法动作数缩放之外，论文强调三种游戏使用相同算法设置、网络架构和超参数。

这是核心贡献。

它把“为每个游戏定制专家系统”的范式，替换为“给规则，自己学”。

### 2.2 贡献二：策略价值网络取代手工评估

AlphaZero 使用一个深度神经网络：

```text
(p, v) = f_theta(s)
```

其中：

- `s` 是棋盘位置。
- `p` 是所有动作的先验概率分布。
- `v` 是从该位置出发的期望结果。

论文把 `v` 定义为对最终结果 `z` 的估计。

结果编码为：

```text
loss = -1
draw = 0
win = +1
```

这比 AlphaGo Zero 只优化二元胜率更通用，因为国际象棋和将棋存在和棋。

### 2.3 贡献三：MCTS 取代 alpha-beta 搜索

AlphaZero 不做传统 minimax alpha-beta。

它使用通用 Monte Carlo Tree Search。

每次搜索由一系列模拟组成，从根节点走到叶节点。

选择动作时综合三个因素：

- 低访问次数。
- 高神经网络先验概率。
- 高平均价值。

搜索结束后返回根节点访问次数形成的策略分布 `pi`。

训练时下棋动作按 `pi` 采样。

评估时动作按根访问次数贪婪选择。

### 2.4 贡献四：自我对弈训练目标

每局自我对弈结束后得到最终结果 `z`。

训练目标同时做两件事：

- 让价值头 `v` 拟合最终结果 `z`。
- 让策略头 `p` 拟合 MCTS 产生的搜索策略 `pi`。

论文给出损失函数：

```text
(p, v) = f_theta(s)
l = (z - v)^2 - pi^T log p + c ||theta||^2
```

三个部分分别是：

- 价值均方误差。
- 策略交叉熵。
- L2 权重正则。

### 2.5 贡献五：连续更新而非“最佳玩家替换”

AlphaGo Zero 训练时维护历史最佳玩家。

每轮训练后，新玩家要以 55% 胜率超过旧最佳玩家，才会替换为新的 self-play 生成器。

AlphaZero 简化为单个持续更新的神经网络。

自我对弈始终使用最新参数。

它省掉了评估新旧玩家和选择 best player 的步骤。

---

## Step 3 | 技术细节（HOW）

### 3.1 输入表示

AlphaZero 把棋盘编码为 `N x N x (M T + L)` 的 image stack。

其中：

- `T = 8`，表示最近 8 个时间步历史。
- 当前玩家视角作为棋盘朝向。
- 棋子位置用平面表示。
- 额外常量平面编码当前颜色、总步数、特殊规则状态。

论文表 S1 给出三种游戏输入平面数：

```text
Go:    17 planes
Chess: 119 planes
Shogi: 362 planes
```

国际象棋输入包含：

- 当前玩家棋子 6 类。
- 对手棋子 6 类。
- 重复局面计数 2 平面。
- 当前颜色 1 平面。
- 总步数 1 平面。
- 双方王翼/后翼易位权利各 2 平面。
- 无进展步数 1 平面。

将棋输入更大，是因为有 14 类棋子、重复计数、双方持驹数量等。

### 3.2 动作表示

国际象棋策略输出是：

```text
8 x 8 x 73 = 4,672 possible moves
```

73 个动作平面包括：

- 56 个 queen moves：8 个方向乘以 1 到 7 格。
- 8 个 knight moves。
- 9 个 underpromotion moves。

将棋策略输出是：

```text
9 x 9 x 139 = 11,259 possible moves
```

139 个平面包括：

- 64 个 queen moves。
- 2 个 knight moves。
- 64 个 promoting queen moves。
- 2 个 promoting knight moves。
- 7 个 drop moves。

围棋沿用 AlphaGo Zero 表示：

```text
19 x 19 + 1
```

对应 361 个落子点和 pass。

非法动作会被 mask 为 0，并重新归一化合法动作概率。

### 3.3 训练配置

论文训练三个单独的 AlphaZero 实例。

共同设置：

```text
training steps: 700,000
mini-batch size: 4,096
self-play generation: 5,000 first-generation TPUs
neural network training: 64 second-generation TPUs
MCTS simulations during training: 800
```

学习率：

```text
initial learning rate: 0.2
drops: 0.02, 0.002, 0.0002
```

Dirichlet exploration noise 的 `alpha`：

```text
Chess: 0.3
Shogi: 0.15
Go:    0.03
```

这个缩放依据是典型合法动作数量。

### 3.4 三个游戏的训练统计

论文表 S3 给出：

```text
Chess:
  mini-batches: 700k
  training time: 9h
  training games: 44 million
  training MCTS: 800 simulations
  thinking time: 40 ms

Shogi:
  mini-batches: 700k
  training time: 12h
  training games: 24 million
  training MCTS: 800 simulations
  thinking time: 80 ms

Go:
  mini-batches: 700k
  training time: 34h
  training games: 21 million
  training MCTS: 800 simulations
  thinking time: 200 ms
```

这组数字很关键。

它说明 AlphaZero 的“数小时超越”不是小规模实验，而是大规模 TPU 自我对弈系统。

---

## Step 4 | 实验评估（EVALUATION）

### 4.1 训练中达到超人水平的速度

论文 Figure 1 报告：

```text
Chess: AlphaZero after 4 hours / 300k steps outperformed Stockfish
Shogi: AlphaZero after less than 2 hours / 110k steps outperformed Elmo
Go:    AlphaZero after 8 hours / 165k steps outperformed AlphaGo Lee
```

注意这里比较的是训练过程中的 Elo 评估。

论文同时说明，AlphaGo Master 和 AlphaGo Zero 最终训练长度是这里的 100 倍；本论文没有复现那种训练量。

### 4.2 100 局锦标赛结果

完全训练后的 AlphaZero 在三类游戏中分别对战：

- Stockfish。
- Elmo。
- AlphaGo Zero 3-day。

设置：

```text
matches: 100 games
time control: 1 minute per move
AlphaZero machine: single machine with 4 TPUs
Stockfish: 64 threads, 1GB hash
Elmo: 64 threads, 1GB hash
```

论文表 1 的结果如下，均从 AlphaZero 视角计。

国际象棋：

```text
AlphaZero as White vs Stockfish: 25 wins, 25 draws, 0 losses
Stockfish as White vs AlphaZero: 3 wins for AlphaZero, 47 draws, 0 losses
Total: 28 wins, 72 draws, 0 losses
```

将棋：

```text
AlphaZero as first player vs Elmo: 43 wins, 2 draws, 5 losses
Elmo as first player vs AlphaZero: 47 wins for AlphaZero, 0 draws, 3 losses
Total: 90 wins, 2 draws, 8 losses
```

围棋：

```text
AlphaZero as first player vs AlphaGo Zero 3-day: 31 wins, 19 losses
AlphaGo Zero 3-day as first player vs AlphaZero: 29 wins for AlphaZero, 21 losses
Total: 60 wins, 40 losses
```

国际象棋最醒目的事实是：AlphaZero 对 Stockfish 零负。

将棋最醒目的事实是：AlphaZero 对 Elmo 90 胜 8 负。

围棋最醒目的事实是：同等 100 局下，AlphaZero 以 60 胜 40 负超过 3 天训练版 AlphaGo Zero。

### 4.3 搜索速度对比

论文表 S4 给出位置评估速度：

```text
Chess:
  AlphaZero: 80k positions/second
  Stockfish: 70,000k positions/second

Shogi:
  AlphaZero: 40k positions/second
  Elmo: 35,000k positions/second

Go:
  AlphaZero: 16k positions/second
```

这不是小差距。

Stockfish 每秒搜索位置数是 AlphaZero 国际象棋版本的 875 倍。

Elmo 每秒搜索位置数是 AlphaZero 将棋版本的 875 倍。

但 AlphaZero 用神经网络先验和价值估计，把搜索集中到更有价值的变化上。

论文用 Shannon 早期观点解释这种方式：不是蛮力展开更多位置，而是更选择性地搜索。

### 4.4 思考时间扩展性

Figure 2 比较了 AlphaZero、Stockfish、Elmo 随每步思考时间增加的 Elo 变化。

论文结论是：

AlphaZero 的 MCTS 随思考时间扩展更有效。

这挑战了“alpha-beta 在国际象棋和将棋中天然优于 MCTS”的传统观点。

这里要谨慎理解。

论文不是证明 MCTS 总是优于 alpha-beta。

它证明的是：

当 MCTS 与强神经网络表示结合时，传统 MCTS 在棋类任务上不强的结论不再可靠。

### 4.5 人类开局分析

Table 2 分析了 12 个最常见人类开局，每个开局都在在线人类棋局数据库中出现超过 100,000 次。

AlphaZero 在自我对弈中独立发现并频繁使用这些开局。

论文还从这些开局位置出发，让 AlphaZero 对 Stockfish 打 100 局。

汇总结果：

```text
AlphaZero as White:
  242 wins, 353 draws, 5 losses
  percentage: 40.3 / 58.8 / 0.8

AlphaZero as Black:
  48 wins, 533 draws, 19 losses
  percentage: 8.0 / 88.8 / 3.2
```

这个实验说明两件事：

第一，AlphaZero 不是靠走怪招绕过 Stockfish。

第二，它能覆盖人类常见开局空间，并在这些开局下保持优势。

---

## Step 5 | 历史叙事与影响（IMPACT）

### 5.1 前驱谱系

论文把 AlphaZero 放在三个历史线索交汇点。

第一条线是经典博弈搜索：

```text
Shannon chess program idea
  -> minimax
  -> alpha-beta pruning
  -> Deep Blue
  -> Stockfish / Elmo
```

第二条线是强化学习自我对弈：

```text
Samuel checkers
  -> temporal-difference learning
  -> TD-based chess/shogi attempts
  -> AlphaGo / AlphaGo Zero
  -> AlphaZero
```

第三条线是深度神经网络表示：

```text
handcrafted evaluation features
  -> learned value functions
  -> policy/value neural networks
  -> search-guided self-play policy iteration
```

### 5.2 与 AlphaGo Zero 的关系

论文明确说，AlphaZero 是 AlphaGo Zero 的更通用版本。

主要变化包括：

- 从二元胜负改成期望结果，支持和棋。
- 不使用旋转/反射数据增强。
- 不在 MCTS 中随机变换棋盘。
- 不维护历史最佳玩家，改为单网络持续更新。
- 不做游戏特定超参数调优，除探索噪声按合法动作数缩放。

因此 AlphaZero 不是“围棋系统的简单复刻”。

它是在降低游戏特化假设。

### 5.3 对 Bitter Lesson 的意义

这篇论文是 Bitter Lesson 的典型案例。

国际象棋和将棋长期由人工知识和搜索工程统治。

AlphaZero 用可扩展计算替换了这些手工知识：

- 自我对弈生成数据。
- 神经网络学习评估和先验。
- MCTS 在推理时投入计算。
- TPU 集群提供训练规模。

它的核心启示不是“人类知识无用”。

更准确地说：

在可模拟、可评分、可大规模自我对弈的环境里，规则加计算可以学出比人工特征更强的策略。

### 5.4 与 Test-time Compute 的关系

AlphaZero 的每步 MCTS 是典型 test-time compute。

训练时，MCTS 改善当前策略，生成更强监督信号。

评估时，MCTS 在当前局面投入额外计算，选择访问次数最高的动作。

这与现代 reasoning model 的关系是结构类比，而非直接等同：

- 棋类有精确定义的状态转移和终局奖励。
- 语言推理任务没有可靠模拟器。
- AlphaZero 的搜索树节点是棋盘状态。
- LLM 推理树节点通常是文本中间步骤。

所以 AlphaZero 给 test-time compute 提供了清晰原型，但不能直接推出 LLM 内部也在执行同样算法。

---

## Step 6 | 工程实践与复现难点（ENGINEERING）

### 6.1 复现所需核心模块

复现 AlphaZero 至少需要：

```text
game engine:
  legal move generation
  state transition
  terminal detection
  scoring

neural network:
  policy head
  value head
  board representation
  action masking

search:
  MCTS selection
  expansion
  neural network evaluation
  backup
  root visit distribution

self-play loop:
  generate games
  store (state, pi, z)
  train on replay data
  update latest network

evaluation:
  fixed time control
  opponent adapters
  Elo estimation
```

### 6.2 最大工程成本

第一是合法动作和状态编码。

棋类规则边界很多。

国际象棋有易位、升变、三次重复、50 步规则。

将棋有持驹、打入、升变、重复规则。

这些如果实现错误，学习会从根上偏掉。

第二是自我对弈吞吐。

论文用了 5,000 个第一代 TPU 生成 self-play，64 个第二代 TPU 训练网络。

普通复现很难达到同等时间尺度。

第三是 MCTS 与神经网络批量推理的工程耦合。

搜索需要大量叶节点评估。

如果不能高效批处理网络推理，硬件利用率会很低。

第四是评估公平性。

论文中 Stockfish 和 Elmo 使用 64 CPU threads 与 1GB hash，AlphaZero 使用单机 4 TPU。

这不是相同硬件资源的严格成本比较，而是比赛强度比较。

### 6.3 论文局限

局限一：任务都是完全信息、规则明确、可模拟的零和棋类游戏。

局限二：训练计算资源极高。

局限三：虽然声明无领域知识，但仍使用规则、棋盘结构、动作编码、合法动作 mask 和典型合法动作数。

局限四：论文没有把 AlphaZero 应用到非棋类、非精确模拟的开放任务。

局限五：报告的 PDF 是 AlphaZero 论文，不是 AlphaGo Zero Nature 原文；围棋细节主要作为比较项出现。

---

## Step 7 | 个人评价与关联学习

### 7.1 最重要的洞察

AlphaZero 的最重要洞察是：

> 策略提升不一定要靠人类样本，可以靠当前模型加搜索产生更强的训练目标。

这构成一个闭环：

```text
current network
  -> MCTS search
  -> improved policy pi
  -> self-play game outcome z
  -> train network
  -> stronger current network
```

这个闭环是 AlphaZero 的灵魂。

神经网络提供泛化，MCTS 提供局部规划，自我对弈提供无限数据。

### 7.2 为什么它强

AlphaZero 不是单靠神经网络。

也不是单靠搜索。

它强在二者互相放大：

- 网络让搜索更聚焦。
- 搜索让训练目标更强。
- 自我对弈让数据分布随能力提升。
- 规则环境让奖励无噪声。

传统 alpha-beta 搜索每秒评估更多节点。

AlphaZero 每秒评估更少节点，但每个节点由深度网络提供更强语义。

这就是论文中 80k 对 70,000k positions/second 仍然能赢的原因。

### 7.3 学习优先级

建议学习顺序：

```text
1. MDP / 强化学习基础
2. Monte Carlo Tree Search
3. AlphaGo 2016
4. AlphaGo Zero 2017 Nature
5. 本篇 AlphaZero 2017 arXiv
6. MuZero
7. Test-time compute / Tree-of-Thought / reasoning search
```

如果只想理解现代 AI 的一条主线，本篇的价值在于：

- 它展示了搜索与学习如何闭环。
- 它展示了不依赖人类数据的自举学习。
- 它展示了推理时计算如何提升决策质量。
- 它展示了通用算法如何击穿专家工程。

### 7.4 知识图谱位置

```text
Samuel self-play
  -> TD learning / game-tree search
  -> AlphaGo 2016
  -> AlphaGo Zero 2017
  -> AlphaZero 2017
  -> MuZero
  -> modern test-time compute
```

与本项目已有报告的关系：

- `22_bitter_lesson_2019`：AlphaZero 是搜索与学习可扩展性的强证据。
- `Test_Time_Compute_深度解析_20260409`：AlphaZero 的 MCTS 是推理时计算的清晰原型。
- `05_scaling_laws_2020`：AlphaZero 展示的是决策任务中的计算扩展，而不是语言建模 loss scaling。
- `42_distilling_2015`：二者都体现“训练/部署形态可以不同”，但机制完全不同。

### 7.5 一句话类比

传统棋类程序像一位背满人类棋谱、开局库和残局表的专家。

AlphaZero 像一个只知道规则、能和自己无限下棋、并且每一步都认真推演的学生。

它没有继承人类知识，却用计算把知识重新发现出来。
