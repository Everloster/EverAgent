---
title: Qwen2.5-3B GRPO 强化学习微调
type: tutorial_note
stage: 4
notebook: notebooks/04_qwen25_grpo_finetuning.ipynb
prerequisites: ["transformer_architecture", "lora_peft", "grpo_concept"]
updated_on: 2026-04-20
---

## 学习目标

- [ ] 理解 LoRA 的原理：为什么低秩分解能减少可训练参数
- [ ] 理解 4-bit NF4 量化：如何在 8GB 显存上运行 3B 参数模型
- [ ] 理解 GRPO 与 SFT 的本质区别：探索 vs 模仿
- [ ] 能跑通完整的 Qwen2.5-3B GRPO 微调流程
- [ ] 理解奖励函数的设计如何影响模型行为

---

## 核心概念（Why）

### 为什么需要微调？

预训练 LLM（如 Qwen2.5-3B-Instruct）已经有强大的语言能力，但：
- 它可能不遵循特定格式（如你需要 JSON 输出）
- 它在特定领域（如数学推理）还不够强
- 它可能不符合安全/对齐要求

**微调的目标**：在保留预训练知识的前提下，调整模型在特定任务上的行为。

### 为什么用 LoRA 而不是全量微调？

Qwen2.5-3B 有 30 亿参数，全量微调需要：
- 模型权重：~6GB（bf16）
- 优化器状态（Adam）：~12GB（每个参数存两个状态）
- 梯度：~6GB
- **合计：约 24GB 显存**

LoRA 只微调低秩分解矩阵：
- Rank=64 的 LoRA 可训练参数约是全量的 **0.5%**
- 显存需求降至约 **4-8GB**（4-bit 量化后）

**LoRA 数学原理**：
```
原始权重 W（冻结） + 低秩矩阵 ΔW = W + BA
其中 B ∈ R^{d×r}，A ∈ R^{r×k}，r << min(d,k)
```
`rank=64` 意味着 r=64，比原始矩阵维度（通常 4096）低 64 倍。

### 为什么用 GRPO 而不是 SFT？

| | SFT（监督微调） | GRPO（强化学习） |
|--|--------------|----------------|
| 数据 | 需要（prompt, 好回答）对 | 只需要 prompt + 奖励函数 |
| 能力上限 | 受训练数据质量限制 | 可超越训练数据（RL 探索） |
| 适合场景 | 格式学习、知识注入 | 可验证任务（数学、代码） |

GRPO 的关键创新：**用组内相对奖励代替 Critic 网络**，大幅降低显存。对同一个 prompt，生成 G 个回答，以组内平均奖励为基线，优势 = 单个奖励 - 平均奖励。

---

## 实现解析

### 模型加载（4-bit 量化）

```python
from unsloth import FastLanguageModel, PatchFastRL
PatchFastRL("GRPO", FastLanguageModel)  # Patch TRL 使用 Unsloth 优化内核

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-3B-Instruct",
    max_seq_length=1024,
    load_in_4bit=True,    # NF4 量化，显存减少 75%
    fast_inference=False, # 禁用 vLLM（兼容性，启用后推理快 5x）
)
```

### LoRA 配置

```python
model = FastLanguageModel.get_peft_model(
    model,
    r=64,           # LoRA rank（越大效果越好，但显存越多）
    lora_alpha=64,  # 通常等于 r
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
)
```

### GRPO 训练配置

关键超参数（来自 `notebooks/04_qwen25_grpo_finetuning.ipynb`）：

| 参数 | 值 | 说明 |
|------|-----|------|
| `learning_rate` | 5e-6 | 比 SFT 低 10x（RL 训练更敏感） |
| `optim` | `adamw_8bit` | 8-bit Adam，节省优化器显存 |
| `lr_scheduler_type` | `cosine` | 余弦衰减 |
| `warmup_ratio` | 0.1 | 10% 步数做线性预热 |
| `per_device_train_batch_size` | 1 | 显存受限，最小值 |
| `bf16` | 自动检测 | A100/H100 用 bf16，V100 用 fp16 |

### 奖励函数设计

```python
def reward_correct(completions, answer, **kwargs):
    """核心奖励：答案是否正确"""
    responses = [c[0]['content'] for c in completions]
    extracted = [extract_xml_answer(r) for r in responses]
    return [2.0 if r == a else 0.0 for r, a in zip(extracted, answer)]

def reward_format(completions, **kwargs):
    """格式奖励：是否遵循 XML 格式"""
    pattern = r"<reasoning>.*?</reasoning>\s*<answer>.*?</answer>"
    responses = [c[0]['content'] for c in completions]
    return [0.5 if re.search(pattern, r, re.DOTALL) else 0.0 for r in responses]
```

**设计原则**：奖励函数越精确，模型对齐越准确。格式奖励帮助模型先学会"如何回答"，再学会"答什么"。

---

## 实验结果（实际运行）

训练日志（来自 notebook Cell 13）：

| Step | Train Loss | Reward | Reward Std | Completion Length | KL |
|------|:---:|:---:|:---:|:---:|:---:|
| 1 | 0.0000 | 0.1250 | 0.0000 | 200.0 | 0.0000 |

**结果解读**：
- **Step 1 reward=0.125**：模型初始完全不会按格式输出，极少数情况碰巧正确
- **前 100-150 步**：reward 接近 0 是正常的，模型需要先探索格式
- **150 步后**：reward 应开始上升（建议训练到 250 步以上观察收敛）
- **KL=0**：第 1 步参考策略即为当前策略，KL 散度为 0 是正确的

**模型保存路径**：
- Checkpoint：`outputs/checkpoint-250/`
- LoRA 权重：`grpo_saved_lora/`

---

## 思考题与延伸实验

1. **LoRA Rank 的影响**：将 `lora_rank` 从 64 改为 16 或 128，比较：
   - 可训练参数量变化（用 `model.print_trainable_parameters()` 查看）
   - 显存占用变化
   - 250 步时的 reward 值

2. **奖励函数设计**：在当前奖励函数基础上，添加"答案长度惩罚"（超过 500 字扣分）。这会如何影响模型行为？

3. **SFT vs GRPO 对比**：用相同数量的 GSM8K 数据做 SFT 微调，再用 GRPO 微调同一基础模型，在 GSM8K 测试集上对比准确率。

4. **温度探索**：GRPO 训练时，生成多个回答用的采样温度是多少？提高温度会如何影响 exploration（探索）和 exploitation（利用）的平衡？

5. **推理对比**：对比微调前后模型回答"How many r's are in strawberry?"的差异（答案：3 个 r，很多 LLM 会答错）。

---

## 参考资料

- **GRPO 论文**：[DeepSeekMath: Pushing the Limits of Mathematical Reasoning](https://arxiv.org/abs/2402.03300)（GRPO 首次提出）
- **LoRA 论文**：[LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- **Unsloth 文档**：https://docs.unsloth.ai/
- **TRL GRPOTrainer**：https://huggingface.co/docs/trl/grpo_trainer
- **本项目 Wiki**：
  - [wiki/concepts/grpo.md](../wiki/concepts/grpo.md)
  - [wiki/concepts/lora_peft.md](../wiki/concepts/lora_peft.md)
  - [wiki/concepts/sft_vs_rlhf.md](../wiki/concepts/sft_vs_rlhf.md)
  - [wiki/concepts/unsloth_framework.md](../wiki/concepts/unsloth_framework.md)
