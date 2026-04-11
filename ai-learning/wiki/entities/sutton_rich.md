# Rich Sutton

> 强化学习奠基人，The Bitter Lesson 作者

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Richard S. Sutton |
| 机构 | University of Alberta → DeepMind (兼任) |
| 主要贡献 | 强化学习理论体系、时序差分学习(TD Learning)、The Bitter Lesson |
| 代表作 | 《Reinforcement Learning: An Introduction》(与 Andrew Barto 合著) |

## 核心贡献

### 强化学习理论体系
- 与 Andrew Barto 合著 RL 经典教材（1998 初版，2018 第二版），定义了整个领域的框架
- 提出时序差分学习 (TD Learning)，统一了蒙特卡洛方法与动态规划
- Dyna 架构：model-based 与 model-free RL 的统一框架

### The Bitter Lesson (2019.03)
- 发表于个人博客 incompleteideas.net，非正式出版物但影响力极高
- 核心论断：70 年 AI 历史反复证明——利用计算能力的通用方法最终总是赢，编码人类知识的专用方法短期有效但长期必败
- 搜索 (Search) 与学习 (Learning) 是能随算力无限扩展的两类根本方法
- 被 OpenAI、DeepMind 等机构广泛引用为 AI 研究的"第一原则"

## 学术血统与影响

```
Andrew Barto (导师)
    └── Rich Sutton
         ├── TD Learning → Q-Learning (Watkins) → DQN (DeepMind)
         ├── Policy Gradient 理论基础 → PPO (Schulman) → RLHF
         └── The Bitter Lesson → Scaling Laws 哲学基础
```

## 在本项目中的关联

- 直接关联报告：`22_bitter_lesson_2019.md`
- 间接关联：Scaling Laws (#05)、AlphaGo (通过 DeepMind)、PPO/RLHF (#04 InstructGPT)
- 概念关联：`bitter_lesson.md`、`scaling_laws.md`、`rlhf.md`

## 身份特点

Sutton 是少数横跨 AI 多次范式转换的亲历者——从符号 AI 到统计方法再到深度学习。这种独特视角使他能在 2019 年提出 Bitter Lesson 这一元认知纲领。他既是 RL 理论的创建者（编码人类知识的一面），也是 Bitter Lesson 的倡导者（通用计算的一面），这种自我反思的诚实使他的论点格外有说服力。
