---
id: concept-rlhf
title: "RLHF（人类反馈强化学习）"
type: concept
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [RLHF_深度解析, 04_instructgpt_2022, 26_tulu3_2024]
status: active
---

# RLHF（Reinforcement Learning from Human Feedback）

## 一句话定义
通过人类偏好信号塑造语言模型行为，让模型从"能说话"变成"说人话"的对齐训练范式。

## 三阶段标准流程
```
阶段 1 SFT（监督微调）
  人工标注者写示范回答 → 用示范数据微调预训练模型
       ↓
阶段 2 训练奖励模型（Reward Model）
  对同一 prompt 生成多个回答 → 人工排序 → 训练 RM 预测人类偏好
       ↓
阶段 3 PPO 强化学习
  以 RM 输出为奖励，PPO 优化 SFT 模型，加入 KL 惩罚约束偏离
```
来源：RLHF_深度解析 §三阶段流程

## 核心数学
**奖励模型损失**（成对排序，Bradley-Terry）：
```
L_RM = -E[ log σ(r(x, y_w) - r(x, y_l)) ]
```
其中 y_w 是更优回答、y_l 是较差回答。来源：RLHF_深度解析 §阶段2

**PPO 优化目标**：
```
maximize  E[r(x, y)] - β · KL(π_RL || π_SFT)
```
KL 散度惩罚项防止模型偏离 SFT 模型太远，避免 **Reward Hacking**（找到奖励模型漏洞、得高分但实际质量低劣的输出）。来源：RLHF_深度解析 §阶段3

## InstructGPT 的实证发现
- **小而对齐 > 大而粗糙**：1.3B 参数的 InstructGPT 在人类偏好上以 85% vs 15% 压倒 175B 的原始 GPT-3。来源：04_instructgpt_2022 §核心贡献
- **SFT 数据量**：约 13K Prompt-Response 对，全部由人工标注员撰写。来源：04_instructgpt_2022 §技术方法
- **对齐税（Alignment Tax）**：RLHF 训练会导致部分经典 NLP 基准（如 SQuAD、HellaSwag）性能下降，可通过混合 SFT 数据缓解。来源：04_instructgpt_2022 §核心贡献

## 主要变体与替代方案
| 方法 | 提出 | 关键改进 | 现状 |
|------|------|---------|------|
| **PPO**（标准 RLHF） | OpenAI InstructGPT 2022 | 三阶段、稳定但复杂 | InstructGPT/ChatGPT 流程 |
| **Constitutional AI / RLAIF** | Anthropic 2022 | 用 AI 而非人类生成偏好标签 | Claude 系列 |
| **DPO**（Direct Preference Optimization） | 2023 | 跳过 RM 与 PPO，直接用偏好数据微调 | 训练更稳定、代码更简洁，开源社区主流 |
| **GRPO** | DeepSeek-R1 2024 | 组相对优化，无需价值函数（critic） | DeepSeek-R1 推理路线 |

来源：RLHF_深度解析 §五

DPO 损失：
```
L_DPO = -E[ log σ(β·log(π/π_ref)(y_w|x) - β·log(π/π_ref)(y_l|x)) ]
```

## RLHF 的核心挑战
| 挑战 | 说明 |
|------|------|
| Reward Hacking | 模型欺骗 RM，得高分但质量差 |
| 标注者偏差 | 人类偏好不一致、文化背景影响显著 |
| 成本高 | 人工排序昂贵且慢 |
| 分布偏移 | 训练分布 ≠ 实际使用分布 |
| 过度拒绝（Over-refusal） | RLHF 后模型倾向拒答边界问题 |

来源：RLHF_深度解析 §挑战 / §知识检验题

## 在本项目的相关报告
- [RLHF 深度解析](../../reports/knowledge_reports/RLHF_深度解析.md)
- [InstructGPT (2022) 论文精读](../../reports/paper_analyses/04_instructgpt_2022.md)
- [Tulu 3 (2024) 论文精读](../../reports/paper_analyses/26_tulu3_2024.md) — 后训练数据量 scaling 前沿

## 跨域连接
- LoRA 是 SFT/DPO 阶段降低显存的标配 → concept: lora_peft
- 与心理学的"行为强化理论"在反馈塑造行为这一抽象层面相通（plan §3 跨域连接清单）

## 开放问题
- 为什么 RLHF 后模型会出现"过度拒绝"？
- DPO 是否真能完全替代 PPO，还是在特定任务上有上限？
- 如何系统性地度量"对齐税"并将其降到最低？
