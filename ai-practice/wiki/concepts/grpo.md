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

---

## 本项目实现（exp_004）

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

---

## 与相关概念的关系

- **→ [sft_vs_rlhf.md](sft_vs_rlhf.md)**：SFT 是监督模仿，GRPO/PPO 是 RL 探索
- **→ [lora_peft.md](lora_peft.md)**：实践中 GRPO 几乎总是配合 LoRA 使用（否则显存不够）
- **→ [unsloth_framework.md](unsloth_framework.md)**：Unsloth 的 `PatchFastRL` 优化了 GRPO 的内核实现

---

## 进一步学习

- **原始论文**：[DeepSeekMath: Pushing the Limits of Mathematical Reasoning](https://arxiv.org/abs/2402.03300)
- **DeepSeek-R1**：[DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL](https://arxiv.org/abs/2501.12948)（GRPO 的大规模应用）
- **PPO 原论文**：[Proximal Policy Optimization Algorithms](https://arxiv.org/abs/1707.06347)（理解 PPO 再看 GRPO 差异）
- **TRL 文档**：[GRPOTrainer](https://huggingface.co/docs/trl/grpo_trainer)
