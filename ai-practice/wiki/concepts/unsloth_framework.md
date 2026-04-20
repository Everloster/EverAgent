# Unsloth 框架

> 来源：exp_004 | 类型：LLM 微调加速框架

---

## 核心定义

Unsloth 是专为 LLM 微调设计的加速框架，通过手写 Triton kernel 和优化内存布局，在不损失精度的情况下将训练速度提升 2-5x，显存降低 60-70%。

## 核心能力

| 功能 | 说明 |
|------|------|
| `FastLanguageModel` | 统一接口加载 Qwen/Llama/Mistral 等模型 |
| `load_in_4bit` | NF4 量化加载，显存约为 fp16 的 25% |
| `PatchFastRL` | 修改 TRL 的 GRPO/PPO 内核为 Unsloth 优化版 |
| `for_inference()` | 切换模型到推理模式（禁用梯度，优化 KV cache） |

## 与标准 HuggingFace PEFT 的关系

Unsloth 兼容 HuggingFace PEFT LoRA 权重格式，训练完成的 LoRA 可用标准 `peft.PeftModel` 加载，无厂商锁定风险。

## 在 exp_004 中的使用

```python
from unsloth import FastLanguageModel, PatchFastRL
PatchFastRL("GRPO", FastLanguageModel)  # GRPO 内核 patch
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Qwen/Qwen2.5-3B-Instruct",
    load_in_4bit=True,
    lora_rank=64,
)
```
