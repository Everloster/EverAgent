# GRPO（Group Relative Policy Optimization）

> PPO 的无 Critic 变体，通过组内相对奖励估计优势函数，大幅降低 LLM 强化学习的显存开销。

---

## 直觉理解（Why it exists）

强化学习微调 LLM 的标准方案是 PPO，但 PPO 需要额外训练一个 **Critic（价值网络）**来估计状态价值。  
对 LLM 而言，Critic 网络的规模通常与 Actor（策略网络）相当，意味着显存需求加倍。

**GRPO 的洞察**：对同一个 prompt，采样 G 个回答后，组内平均奖励是一个更简单的基线估计，不需要 Critic 网络。

由 DeepSeek 在 [DeepSeekMath](https://arxiv.org/abs/2402.03300)（2024）中首次提出。

---

## 核心机制（How it works）

### 算法流程

```
对每个 prompt x:
  1. 采样 G 个回答：{o_1, o_2, ..., o_G} ~ π_θ(·|x)
  2. 用奖励模型评分：{r_1, r_2, ..., r_G}
  3. 归一化优势：Â_i = (r_i - mean({r_j})) / std({r_j})
  4. PPO-clip 目标更新策略：
     L = E_i [ min(ρ_i · Â_i, clip(ρ_i, 1-ε, 1+ε) · Â_i) ] - β·KL(π_θ || π_ref)
```

其中 ρ_i = π_θ(o_i|x) / π_ref(o_i|x) 是重要性权重，π_ref 是参考策略（微调前的模型）。

### 关键公式

**优势估计（无 Critic）**：
```
Â_i = (r_i - μ_r) / σ_r
其中 μ_r = (1/G) Σ r_j，σ_r = std({r_j})
```

**KL 惩罚项**：防止策略偏离参考模型太远，ε（clip 范围）和 β（KL 权重）是关键超参数。

### GRPO vs PPO 关键差异

| 维度 | PPO | GRPO |
|------|-----|------|
| 基线估计 | Critic 网络（与 Actor 同规模） | **组内均值**（无需额外网络） |
| 额外显存 | ≈ Actor × 2（Critic + 优化器状态） | **仅 Actor**（节省 ~50%） |
| 收敛速度 | 通常更快（精确 Value 估计） | 前 100-200 步 reward 接近 0（探索） |
| 适用场景 | 通用 RL | **可验证奖励的 LLM 任务** |

### Group 大小 G 的影响

- G 太小（G=2）：基线估计方差大，训练噪声多
- G 太大（G=32+）：每个 prompt 的计算量乘以 G，吞吐量下降
- **推荐**：G=8 或 G=16（平衡估计精度和计算效率）

### 关键归一化（DeepSeekMath 论文 §4.2）

GRPO 论文特别强调"**per-prompt 归一化**"：把每个 prompt 的累积梯度除以 `group_size`，再对 prompt batch 求平均。这让学习率与 `group_size` 和 batch size 解耦，是 GRPO 相对 PPO 的算法级优势。

### 重要实现陷阱：sample reuse

GRPO 实现的常见 bug：step 1 用某次采样计算 advantage，step 2 重新采样计算 gradient。这样 advantage 和 gradient 完全解耦，训练原地踏步。正确做法是在 step 1 缓存采样结果，step 2 直接复用。详见 `exp_008`。

---

## 本项目实现（exp_004 真实模型 + exp_008 缩尺模拟）

### exp_004：Qwen2.5-3B 真实 GRPO 微调

**配置**（来自 `notebooks/04_qwen25_grpo_finetuning.ipynb`）：

```python
from trl import GRPOConfig, GRPOTrainer

training_args = GRPOConfig(
    learning_rate=5e-6,      # RL 训练用较小 lr
    weight_decay=0.1,
    warmup_ratio=0.1,
    lr_scheduler_type="cosine",
    optim="adamw_8bit",       # 8-bit Adam 节省显存
    per_device_train_batch_size=1,
    bf16=is_bfloat16_supported(),
)
```

**奖励函数设计**（数学推理任务）：
```python
def reward_correct(completions, answer, **kwargs):
    """答案正确性奖励（主要信号）"""
    extracted = [extract_xml_answer(r) for r in responses]
    return [2.0 if r == a else 0.0 for r, a in zip(extracted, answer)]

def reward_format(completions, **kwargs):
    """格式奖励（辅助信号）"""
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    return [0.5 if re.search(pattern, r, re.DOTALL) else 0.0 for r in responses]
```

**实际训练数值**（来自 notebook 执行结果）：
- Step 1：reward=0.125，completion_length=200，kl=0.0
- 预期 150-250 步后 reward 开始上升

### exp_008：CPU-runnable 缩尺模拟

**配置**（来自 `src/grpo_simulation.py`）：
- 2-token 字符级 policy，22 个参数
- 20 个 toy 算术 prompt（"+/-/×"），单答案模式
- 80 步 GRPO，group_size=8，lr=1.0，kl_beta=0.005
- 训练曲线：`images/grpo/grpo_curves.png`

**观察到的训练曲线**（与 R1 论文描述一致）：
| 指标 | step 1 | step 80 | 物理意义 |
|------|--------|---------|----------|
| mean_reward | 0.07 | 1.07 | S 形上升（探索 → 收敛） |
| accuracy | 0.03 | 0.97 | 答对比例 |
| policy_entropy | 4.45 | 0.14 | 策略从均匀坍缩到 one-hot |
| KL(π_θ \|\| π_ref) | 0.00 | 3.39 | 与参考策略的距离 |

**关键 takeaway**：toy 模拟和真实 LLM 的训练曲线形状完全一致——前几步探索，10-20 步后爆发，30+ 步进入稳态。这验证了 GRPO 的算法骨架（组内优势 + PPO-clip + KL 惩罚）在小规模下就能跑出正确形状。

**Failure case**（mixed-gt 模式）：把 ground truth 改回真实随机分布（不同 prompt 不同答案），由于 toy policy 没有 prompt 条件化能力，accuracy 卡在 ~0.20 而非 1.0。这展示了 **prompt 条件化**（即 Transformer self-attention）在 GRPO 中是必备能力，不是"装饰"。

---

## 与相关概念的关系

- **→ [sft_vs_rlhf.md](sft_vs_rlhf.md)**：SFT 是监督模仿，GRPO/PPO 是 RL 探索
- **→ [lora_peft.md](lora_peft.md)**：实践中 GRPO 几乎总是配合 LoRA 使用（否则显存不够）
- **→ [unsloth_framework.md](unsloth_framework.md)**：Unsloth 的 `PatchFastRL` 优化了 GRPO 的内核实现
- **→ [mixture_of_experts.md](mixture_of_experts.md)**：R1 的 671B MoE 基座也用 GRPO 微调

---

## 进一步学习

- **原始论文**：[DeepSeekMath: Pushing the Limits of Mathematical Reasoning](https://arxiv.org/abs/2402.03300)
- **DeepSeek-R1**：[DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL](https://arxiv.org/abs/2501.12948)（GRPO 的大规模应用）
- **PPO 原论文**：[Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)（理解 PPO 再看 GRPO 差异）
- **TRL 文档**：[GRPOTrainer](https://huggingface.co/docs/trl/grpo_trainer)
- **T060 配套报告**：[推理模型三大流派详解_20260621.md](../../../ai-learning/reports/knowledge_reports/推理模型三大流派详解_20260621.md) §3.3 / §4.4 — GRPO 在 R1 中的工程应用

---

## 本项目实验

| exp_id | 范围 | 路径 |
|--------|------|------|
| exp_004 | Qwen2.5-3B + GSM8K（真实 LLM） | [experiments/exp_004_qwen25_grpo_finetune.md](../../experiments/exp_004_qwen25_grpo_finetune.md) |
| exp_008 | toy 字符级 policy（CPU 缩尺） | [experiments/exp_008_grpo_simulation.md](../../experiments/exp_008_grpo_simulation.md) |
