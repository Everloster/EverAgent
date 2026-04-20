# LoRA（Low-Rank Adaptation）

> 通过低秩矩阵分解减少微调参数量，使大模型在消费级 GPU 上可训练。

---

## 直觉理解（Why it exists）

微调大模型的核心矛盾：
- 全量微调效果最好，但 3B 模型需要 ~24GB 显存（模型 + 梯度 + Adam 优化器状态）
- 不微调则无法适配特定任务

**LoRA 的洞察**：大模型权重更新矩阵 ΔW 的**内在秩（intrinsic rank）很低**。  
与其直接优化完整的 ΔW（d×k 维），不如将其分解为两个低秩矩阵的乘积：ΔW = BA。

---

## 核心机制（How it works）

### 数学原理

原始前向传播：
```
h = W₀x
```

LoRA 修改后：
```
h = W₀x + ΔWx = W₀x + BAx
其中 B ∈ R^{d×r}，A ∈ R^{r×k}，r << min(d, k)
```

**W₀ 被冻结**，只有 A 和 B 参与训练。

**缩放因子**：实践中用 `ΔW = (α/r) × BA`，α 是超参数（通常设为等于 r），防止不同 rank 下需要重调 lr。

### 参数量计算

以 Qwen2.5-3B 的 Attention 层为例（d_model=2048，假设 q_proj 是 d×d）：
- 原始参数：2048 × 2048 = 4,194,304
- LoRA rank=64：A（2048×64）+ B（64×2048）= 262,144 + 262,144 = **524,288**
- **节省**：524K / 4196K ≈ 12.5%（单层），多层叠加后总体约 0.5-2%

### 初始化策略

- A：随机高斯初始化（使初始 ΔW 不完全为零）
- B：**全零初始化**（确保训练开始时 ΔW = BA = 0，不破坏预训练权重）

---

## 关键超参数

| 参数 | 典型值 | 说明 |
|------|--------|------|
| `r`（rank） | 4, 8, 16, 32, 64, 128 | 越大效果越好，显存越多 |
| `lora_alpha` | 通常 = r | 缩放系数 α，影响 ΔW 的幅度 |
| `target_modules` | q/k/v/o 投影层 | 对哪些权重矩阵应用 LoRA |
| `lora_dropout` | 0-0.1 | LoRA 权重的 Dropout |

**Rank 选择经验**：
- 任务简单（格式微调）→ r=4 或 r=8
- 任务复杂（数学推理）→ r=64 或 r=128
- 不确定 → r=16 是常见基线

### LoRA 应用位置

不同论文对 target_modules 有不同选择：

| 方案 | 模块 | 效果 vs 显存 |
|------|------|------------|
| 仅 QV（原论文） | q_proj, v_proj | 省显存，效果略低 |
| 全注意力 | q/k/v/o_proj | 平衡 |
| 全 MLP + 注意力 | + gate/up/down_proj | 效果最好，显存最多 |

---

## 本项目实现（exp_004）

```python
# Unsloth 的 LoRA 配置（src 来自 04_qwen25_grpo_finetuning.ipynb）
model = FastLanguageModel.get_peft_model(
    model,
    r=64,
    lora_alpha=64,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0,   # Unsloth 优化：dropout=0 更快
    bias="none",
)

# 查看可训练参数量
model.print_trainable_parameters()
# 输出类似：trainable params: 62,914,560 || all params: 3,091,587,072 || trainable%: 2.04
```

**保存与加载 LoRA 权重**：
```python
# 保存（只保存 LoRA 增量，几十 MB 而非几 GB）
model.save_pretrained("grpo_saved_lora")

# 加载（需要先加载基础模型，再叠加 LoRA）
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "grpo_saved_lora")

# 合并权重（LoRA 合并到基础权重，推理时无额外开销）
model = model.merge_and_unload()
```

---

## 与相关概念的关系

- **→ [grpo.md](grpo.md)**：GRPO 微调通常配合 LoRA 使用（全量微调显存太大）
- **→ [unsloth_framework.md](unsloth_framework.md)**：Unsloth 优化了 LoRA 的 forward/backward kernel
- **→ [transformer_from_scratch.md](transformer_from_scratch.md)**：LoRA 作用于 Attention 的 q/k/v 投影矩阵

---

## 进一步学习

- **LoRA 原始论文**：[LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)（Hu et al., 2021）
- **QLoRA**：[QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)（LoRA + 4-bit 量化，本项目阶段 4 用的就是这个方案）
- **PEFT 库文档**：https://huggingface.co/docs/peft/conceptual_guides/lora
- **深度解析**：[Sebastian Raschka - LoRA Explained](https://lightning.ai/pages/community/lora-insights/)
