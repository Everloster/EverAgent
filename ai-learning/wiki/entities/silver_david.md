---
id: entity-silver_david
title: "David Silver"
type: entity/person
domain: [ai-learning]
created: 2026-04-25
updated: 2026-04-25
sources: [43_alphago_zero_2017]
---

# David Silver

## 身份

David Silver 是 DeepMind 强化学习与游戏 AI 研究的核心人物之一。本项目当前仅记录其在 AlphaZero 论文中的角色：`Mastering Chess and Shogi by Self-Play with a General Reinforcement Learning Algorithm` 第一作者，与 Thomas Hubert、Julian Schrittwieser 并列贡献。

## 本项目相关贡献

- **AlphaZero（2017）**：将 AlphaGo Zero 的 tabula rasa self-play reinforcement learning 推广到国际象棋、日本将棋和围棋。
- 论文中 AlphaZero 使用策略价值网络 `(p, v) = f_theta(s)` 与 MCTS 结合，不使用人类棋谱、开局库、残局库或手工评估函数。
- 关键结果包括对 Stockfish `28` 胜 `72` 和 `0` 负，对 Elmo `90` 胜 `2` 和 `8` 负，对 3 天训练版 AlphaGo Zero `60` 胜 `40` 负。

## 关联报告

- [AlphaZero 论文精读](../../reports/paper_analyses/43_alphago_zero_2017.md)
