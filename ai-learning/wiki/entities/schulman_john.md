---
id: entity-schulman_john
title: "John Schulman"
type: entity/person
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [RLHF_深度解析, 04_instructgpt_2022]
---

# John Schulman

## 身份
强化学习研究者，OpenAI 早期成员，PPO（Proximal Policy Optimization）算法主要提出者。PPO 是 InstructGPT / ChatGPT 在 RLHF 第三阶段使用的核心策略优化算法。来源：RLHF_深度解析 §三 / 04_instructgpt_2022 §技术方法

## 核心贡献
- **PPO（Proximal Policy Optimization）**：稳定的策略梯度算法，成为 RLHF 中将语言模型对齐到奖励模型的事实标准方法。优化目标包含 KL 散度惩罚，约束策略偏离 SFT 模型过远。来源：RLHF_深度解析 §三阶段3
- **InstructGPT/ChatGPT 后训练流程**：参与将 RLHF 三阶段（SFT → Reward Model → PPO）从单任务（Christiano 2017 / Stiennon 2020 摘要任务）扩展到通用指令跟随的工程实现。来源：04_instructgpt_2022 §核心贡献

## 在本项目的相关报告
- [RLHF 深度解析](../../reports/knowledge_reports/RLHF_深度解析.md)
- [InstructGPT (2022) 论文精读](../../reports/paper_analyses/04_instructgpt_2022.md)

## 与其他人物/机构的关系
- 工作直接影响 InstructGPT / ChatGPT / GPT-4 的对齐流程；后续的 DPO（2023）与 GRPO（DeepSeek-R1）均以替代或简化 PPO 为目标。来源：RLHF_深度解析 §五
- 与 Dario Amuodei 等人在 OpenAI 共事，但未参与 2021 年 Anthropic 集体离职。来源：AI关键人物图谱 §二（推断：未列入名单）
