---
id: concept-alphazero_self_play_rl
title: "AlphaZero Self-Play Reinforcement Learning"
type: concept
domain: [ai-learning]
created: 2026-04-25
updated: 2026-04-25
sources: [43_alphago_zero_2017]
---

# AlphaZero Self-Play Reinforcement Learning

## 定义

AlphaZero 是 DeepMind 在 2017 年提出的通用自我对弈强化学习算法。它从随机初始化开始，只使用游戏规则，通过神经网络、MCTS 和自我对弈，在国际象棋、日本将棋和围棋中学出超人水平策略。

本项目报告 `43_alphago_zero_2017` 基于本地 PDF `Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm`，即 AlphaZero 论文，而不是 Nature 2017 的 AlphaGo Zero 围棋原文。

## 核心机制

```text
(p, v) = f_theta(s)
l = (z - v)^2 - pi^T log p + c ||theta||^2
```

- `p`：神经网络输出的动作先验概率。
- `v`：神经网络输出的局面期望结果。
- `pi`：MCTS 在根节点访问次数形成的搜索策略。
- `z`：最终棋局结果，胜为 +1，和为 0，负为 -1。

训练闭环是：

```text
latest network -> MCTS self-play -> (state, pi, z) -> gradient update -> latest network
```

## 论文关键数字

- 训练步数：`700,000` mini-batches。
- mini-batch size：`4,096`。
- self-play：`5,000` first-generation TPUs。
- training：`64` second-generation TPUs。
- training MCTS：每步 `800` simulations。
- Chess 训练：`9h`，`44 million` games。
- Shogi 训练：`12h`，`24 million` games。
- Go 训练：`34h`，`21 million` games。
- 对 Stockfish：`28` 胜、`72` 和、`0` 负。
- 对 Elmo：`90` 胜、`2` 和、`8` 负。
- 对 AlphaGo Zero 3-day：`60` 胜、`40` 负。

## 与 AlphaGo Zero 的差异

- AlphaZero 支持和棋，优化期望结果而不只是胜率。
- AlphaZero 不使用旋转/反射数据增强。
- AlphaZero 不在 MCTS 中随机变换棋盘。
- AlphaZero 不维护历史最佳玩家，而是持续更新单一网络。
- AlphaZero 除探索噪声按合法动作数缩放外，不做游戏特定超参数调优。

## 关联报告

- [AlphaZero 论文精读](../../reports/paper_analyses/43_alphago_zero_2017.md)
- [The Bitter Lesson 精读](../../reports/paper_analyses/22_bitter_lesson_2019.md)
- [Test-Time Compute 深度解析](../../reports/knowledge_reports/Test_Time_Compute_深度解析_20260409.md)
