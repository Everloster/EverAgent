---
title: Qwen2.5-3B-Instruct GRPO 强化学习微调
type: experiment_analysis
status: done
experiment_id: exp_004
notebook: notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb
updated_on: 2026-04-20
---

## 实验摘要

> 使用 Unsloth 框架对 Qwen2.5-3B-Instruct 进行 GRPO（Group Relative Policy Optimization）强化学习微调，以数学推理任务（GSM8K）为对齐目标，验证 GRPO 替代 PPO 的可行性与训练稳定性。

## Step 1 实验目标

- **假设验证**：GRPO 无需训练 Critic 网络，比 PPO 更高效，是否能在 3B 参数模型上稳定收敛
- **关联概念**：GRPO 由 DeepSeek 提出（见 ai-learning wiki/concepts/）；Unsloth 框架可将微调速度提升 2-5x
- **对齐目标**：让模型学会按 `<reasoning>...</reasoning><answer>...</answer>` 格式输出，并通过奖励函数强化正确答案

## Step 2 实现方法

**框架 & 库**：Unsloth、TRL（`GRPOTrainer`）、PEFT（LoRA）、PyTorch

**模型加载**（来自 `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb`，Cell 8）：
```python
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-3B-Instruct",
    max_seq_length=1024,
    load_in_4bit=True,    # 4-bit NF4 量化，节省约 75% 显存
    fast_inference=False,
)
```

**LoRA 配置**：
```python
lora_rank = 64  # 较大 rank，增强微调效果
```

**GRPOConfig 关键参数**（Cell 12）：

| 参数 | 值 | 说明 |
|------|-----|------|
| `learning_rate` | 5e-6 | 比 SFT 低一个量级 |
| `adam_beta1` | 0.9 | AdamW 动量 |
| `adam_beta2` | 0.99 | AdamW 二阶动量 |
| `weight_decay` | 0.1 | 权重衰减 |
| `warmup_ratio` | 0.1 | 线性 warmup 比例 |
| `lr_scheduler_type` | `cosine` | 余弦学习率衰减 |
| `optim` | `adamw_8bit` | 8-bit AdamW（节省优化器状态显存） |
| `per_device_train_batch_size` | 1 | 显存受限 |
| `use_vllm` | False | 禁用 vLLM 快速推理（兼容性） |
| `bf16` | 自动检测 | bfloat16（支持硬件）或 fp16 |

**数据集**：GSM8K（数学推理，来自 @willccbb 的数据预处理方案）

**奖励函数**：基于答案正确性（XML 格式提取 + 数值比对）

**Patch 机制**：`PatchFastRL("GRPO", FastLanguageModel)` — Unsloth 修改 GRPO 的内部函数以支持其优化的 forward pass

## Step 3 关键发现

**训练日志（来自 notebook Cell 13 输出，实际执行结果）**：

| Step | Training Loss | reward | reward_std | completion_length | kl |
|------|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.000000 | 0.125000 | 0.000000 | 200.000000 | 0.000000 |

- **Step 1 reward=0.125**：初始奖励极低，符合预期（模型尚未学会格式）
- **说明**：前 100-150 步奖励接近 0 属于正常现象（模型需要先学会输出格式）
- **收敛目标**：reward 列应在 150-250 步后开始显著上升

**模型保存**：训练完成后 LoRA 权重保存到 `grpo_saved_lora/`，checkpoint 在 `outputs/checkpoint-250`

**完整训练指标**：`[需完整运行 250 步 checkpoint 后补充 reward 收敛曲线]`

## Step 4 代码参考

| 功能 | 文件 | 单元 |
|------|------|------|
| Unsloth GRPO Patch | `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb` | Cell 6 |
| 模型加载（4-bit） | `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb` | Cell 8 |
| 数据集预处理 + 奖励函数 | `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb` | Cell 10 |
| GRPOConfig + GRPOTrainer | `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb` | Cell 12 |
| Checkpoint 检测 + 跳过训练逻辑 | `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb` | Cell 14 |
| 推理对比（GRPO 前后） | `notebooks/Unsloth-Qwen2.5_(3B)-GRPO.ipynb` | Cell 16-19 |

**LoRA 加载**（可复用）：
```python
from peft import PeftModel
model = PeftModel.from_pretrained(model, "grpo_saved_lora")
```

## Step 5 局限性与下一步

**局限性**：
- `per_device_train_batch_size=1` 导致梯度方差大，需更多步数收敛
- `use_vllm=False` 禁用了推理加速，训练速度受限
- `max_seq_length=1024` 限制了长推理链（DeepSeek-R1 风格的 thinking 需要 4K+）
- 实验 checkpoint 仅 250 步，可能未充分收敛

**建议后续**：
- 启用 `use_vllm=True` 对比推理速度（需 CUDA 环境）
- 扩展 `max_seq_length=4096` 测试更长推理链
- 对比 GRPO vs SFT（相同数据量）在 GSM8K 上的准确率差异
- 尝试不同 `lora_rank`（16/32/64/128）对微调效果的影响
