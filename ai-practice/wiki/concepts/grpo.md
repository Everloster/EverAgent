# GRPO（Group Relative Policy Optimization）

> 来源：exp_004 | 提出者：DeepSeek（2025）

---

## 核心定义

GRPO 是 PPO 的变体强化学习算法，**去除了 Critic 网络**，改用同组采样输出的相对奖励作为基线，大幅降低显存和计算开销，适用于 LLM 对齐微调。

## 与 PPO 的关键差异

| 维度 | PPO | GRPO |
|------|-----|------|
| Critic 网络 | 需要（与 Actor 同规模） | **不需要** |
| 基线估计 | Critic 输出的 Value | **组内采样的平均奖励** |
| 显存开销 | Actor + Critic × 2 | **仅 Actor** |
| 适用场景 | 通用 RL | LLM 对齐（奖励模型评估） |

## GRPO 工作流

```
1. 对每个 prompt 采样 G 个回答（Group）
2. 计算每个回答的奖励 r_i
3. 组内均值 r̄ 作为基线
4. 优势 A_i = r_i - r̄（标准化后）
5. PPO-clip 目标函数更新策略
```

## 在 exp_004 中的配置

- 框架：Unsloth + TRL GRPOTrainer
- 模型：Qwen2.5-3B-Instruct（4-bit LoRA）
- 奖励函数：数学答案正确性（XML格式提取）
- 初始 reward（Step 1）：0.125

## 与 ai-learning 的关联

- → ai-learning 中 DeepSeek-R1 论文精读（若已有）
- 与 SFT 对比见 `concepts/sft_vs_rlhf.md`
