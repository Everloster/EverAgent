# Mixture of Experts（MoE，专家混合）

> 通过稀疏激活实现"参数量与计算量分离"的架构设计——模型拥有大量 Expert（子网络），但每次推理只激活其中一小部分，从而在不成比例增加计算量的前提下扩大模型容量。

---

## 直觉理解（Why it exists）

### Dense Transformer 的扩展困境

标准 Dense Transformer 中，每个 token 都通过**相同的全量 FFN**（FeedForward Network）：

```
token_1 → [相同的 FFN] → 输出
token_2 → [相同的 FFN] → 输出
token_3 → [相同的 FFN] → 输出
```

**问题**：想提升模型能力 → 增大 d_model 或 FFN 宽度 → 参数量和计算量同比例增加。这意味着：
- 处理 1 个 token 的计算量 × 模型大小成正比
- 训练和推理的成本都线性增长

### MoE 的洞察

不同 token 需要的"专业知识"不同：
- "Paris is the capital of..."（地理知识）
- "def fibonacci(n):"（代码逻辑）
- "心理学实验表明..."（社会科学）

为什么要用同一套 FFN 权重处理如此不同的 token？

**MoE 的解决方案**：训练多个专门的 Expert（子网络），让 Router 动态决定每个 token 应该由哪些 Expert 处理。大多数 Expert 对任意给定 token 保持"沉默"——这就是**稀疏激活**（Sparse Activation）。

```
                    ┌─ Expert 0（代码专家）─┐
token → [Router] ──┤                       ├──→ 加权求和 → 输出
                    └─ Expert 3（语言专家）─┘
           （Expert 1, 2 对此 token 不激活）
```

---

## 核心机制（How it works）

### 架构公式

Dense Transformer Block 中的 FFN：
```
h = FFN(LayerNorm(x)) + x
```

MoE Transformer Block 中的 MoELayer：
```
h = MoELayer(LayerNorm(x)) + x

其中 MoELayer(x) = Σ_{i ∈ TopK} g_i · Expert_i(x)
```

**符号说明**：
- `K` = top_k，激活的 Expert 数量
- `g_i` = 门控权重（Router 输出，经过重新归一化）
- `Expert_i` = 第 i 个 FFN（与 Dense FFN 结构相同，独立参数）

### 门控机制（Gating）

**完整的 Top-K Softmax 门控**（本项目实现）：

```
给定 token 表示 x ∈ R^{d_model}：

Step 1：计算 Expert 分数
  logits = W_gate × x，W_gate ∈ R^{num_experts × d_model}

Step 2：Softmax 归一化（得到门控概率）
  g = Softmax(logits) ∈ R^{num_experts}
  g_i ∈ [0, 1]，Σ g_i = 1

Step 3：Top-K 选择
  选出 g 中最大的 top_k 个值及对应 Expert 编号
  TopK_indices = argtopk(g, k)
  TopK_weights = g[TopK_indices]

Step 4：重新归一化
  TopK_weights = TopK_weights / sum(TopK_weights)

输出 = Σ_{i ∈ TopK_indices} TopK_weights[i] × Expert_i(x)
```

### 参数量与计算量的分离

以本项目的教学配置（d_model=64）为例：

| 配置 | FFN 参数量 | 每 token 计算量 |
|------|-----------|---------------|
| Dense（1 个 FFN） | d × 4d × 2 = 32,768 | 32,768 ops |
| MoE（4 experts, top_k=2） | 4 × 32,768 = 131,072 | 2 × 32,768 = 65,536 ops |
| 比值 | **参数量 4×** | **计算量只有 2×** |

**通用公式**：
```
MoE 参数量 = Dense 参数量 × num_experts
MoE 计算量 = Dense 计算量 × top_k

效率增益 = num_experts / top_k
```

### 负载均衡损失（Load Balancing Loss）

**Expert Collapse 问题**：如果不加任何约束，Router 会收敛到反复选择同一个（或少数几个）Expert：

```
正反馈循环：
Expert A 被选中 → Expert A 获得更多梯度 → Expert A 更强
→ Expert A 更容易被选中 → ... → 只有 Expert A 被使用
```

**解决方案**：Switch Transformer（2021）提出辅助负载均衡损失：

```
aux_loss = α × num_experts × Σ_i (f_i × P_i)

其中：
  f_i = Expert i 接收的 token 比例（用 top-1 分配统计，stop_gradient）
  P_i = Expert i 的平均门控概率（可微分）
  α = aux_loss_weight（权衡主损失与均衡约束，通常 0.01）
```

**工作原理**：
- `f_i` 反映实际分配（不可微，用 `torch.no_grad()` 包裹）
- `P_i` 作为 `f_i` 的可微代理，让梯度能够流回 Router
- 当 Expert 负载不均时，不均衡的 `f_i × P_i` 乘积会产生更大的 aux_loss，从而惩罚过度集中的路由

---

## 关键超参数

| 参数 | 本项目值 | 说明 | 影响 |
|------|---------|------|------|
| `num_experts` | 4 | Expert 总数（决定参数量倍数） | 越大参数容量越大，训练内存越多 |
| `top_k` | 2 | 每 token 激活的 Expert 数 | 越大计算量越大，但路由更鲁棒 |
| `aux_loss_weight` | 0.01 | 负载均衡损失权重 λ | 太大影响主任务，太小 Expert Collapse |

**top_k 选择经验**：
- top_k=1（Switch Transformer 风格）：最省计算，但容易不稳定，Expert Collapse 更严重
- top_k=2（Mixtral 风格）：主流选择，稳定性好
- top_k=4+：适合细粒度 MoE（num_experts 很大时）

---

## 现代 LLM 中的 MoE

| 模型 | num_experts | top_k | 总参数量 | 激活参数量 | 特点 |
|------|------------|-------|---------|----------|------|
| Switch-C（2021） | 2048 | 1 | 1.6T | ~7B | 首个超大规模 MoE |
| ST-MoE（2022） | 32 | 2 | — | — | 提出稳定训练技巧 |
| Mixtral-8x7B（2024） | 8 | 2 | 46.7B | ~12.9B | 首个主流开源 MoE LLM |
| DeepSeek-V2（2024） | 160 | 6 | 236B | ~21B | 细粒度 MoE + Expert 专业化 |
| DeepSeek-V3（2024） | 256 | 8 | 671B | ~37B | 目前最大开源 MoE |
| Qwen3-235B（2025） | — | — | 235B | ~22B | 阿里云 MoE 大模型 |
| Gemini 1.5（2024） | — | — | — | ~86B（推测） | Google MoE，长上下文 |

**Mixtral-8x7B 的实际计算量**：
- 8 个 Expert，每个 FFN 约等于 7B 模型中的 FFN
- 激活 top_k=2，FFN 计算量相当于 2 个 7B Dense FFN
- 但注意：Attention 层（非 MoE）仍是完整的，约占总计算的 25-30%
- 实际等效密集参数量约 12.9B（而非 7B 或 46.7B）

---

## 本项目实现（src/moe_model.py）

### 参数量验证

```python
from src.moe_model import MoETransformerLanguageModel, count_parameters
from src.model import TransformerLanguageModel

dense = TransformerLanguageModel()
moe = MoETransformerLanguageModel()

print(f"Dense 参数量: {count_parameters(dense):,}")
print(f"MoE 参数量:   {count_parameters(moe):,}")
print(f"倍数: {count_parameters(moe) / count_parameters(dense):.2f}x")
```

### Router 门控可视化

```python
import torch
import matplotlib.pyplot as plt
from src.moe_model import MoETransformerLanguageModel, get_batch

model = MoETransformerLanguageModel()
# 加载训练后的权重（如有）
# model.load_state_dict(torch.load('moe-model-ckpt.pt'))

model.eval()
x, _ = get_batch('train')

# 获取第一个 Block 的 Router 分配
with torch.no_grad():
    emb = model.token_embedding_lookup_table(x)  # (B, T, d_model)
    x_flat = emb.view(-1, emb.shape[-1])          # (B*T, d_model)
    router = model.transformer_blocks[0].moe_layer.router
    indices, weights, gate_probs = router(x_flat)

# 可视化各 Expert 的接收比例
expert_counts = [(indices == e).sum().item() for e in range(4)]
plt.bar(['Expert 0', 'Expert 1', 'Expert 2', 'Expert 3'], expert_counts)
plt.title('Expert Token Distribution (Block 0)')
plt.ylabel('Number of Assignments')
plt.axhline(y=sum(expert_counts) / 4, color='r', linestyle='--', label='均匀分配目标')
plt.legend()
plt.show()
```

### 训练 MoE 模型

```bash
# 从 ai-practice/ 目录运行
python3 src/moe_model.py
# 预期输出（CPU，约 2-3 小时）：
# Step:     0 | Train: 11.xxxx | Valid: 11.xxxx
# Step:    50 | Train: 8.xxxx  | Valid: 8.xxxx
# ...
# Step:  5000 | Train: X.xxxx  | Valid: X.xxxx
```

---

## 常见问题

### Q：MoE 的训练是否比 Dense 更不稳定？

是的，MoE 有以下额外的训练挑战：
1. **Expert Collapse**：需要 aux_loss 防止路由退化
2. **梯度稀疏性**：每个 Expert 只从被路由到的 token 获得梯度，样本效率低
3. **负载不均衡的早期阶段**：训练初期 Router 还未学会均匀分配

实践技巧：可以在训练初期适当增大 `aux_loss_weight`（如 0.1），待路由稳定后调回 0.01。

### Q：推理时能用批处理吗？

可以，但实现更复杂。不同样本中的同一 token 位置可能被路由到不同 Expert，导致批内各样本的 Expert 激活模式不同。

生产级实现（如 vLLM、DeepSpeed-MoE）会将 Expert 分布到不同 GPU 上，并使用 **Expert Parallelism** 进行高效批处理。

### Q：MoE 模型如何用 LoRA 微调？

MoE 模型的 LoRA 微调需要决定对哪些层应用 LoRA：
- 对 Expert FFN 层应用 LoRA：每个 Expert 独立的低秩增量（参数量多但效果好）
- 只对 Attention 层应用 LoRA：参数更少，但遗漏了 Expert 层的适配
- 混合策略：对 Attention 和部分 Expert 应用 LoRA（常见做法）

```python
# Mixtral 的 LoRA 微调（HuggingFace PEFT）
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,
    lora_alpha=32,
    # 对 Attention 和 Expert FFN 的全连接层都应用 LoRA
    target_modules=["q_proj", "k_proj", "v_proj",
                    "w1", "w2", "w3"],  # Expert FFN 层
)
```

---

## 与相关概念的关系

- **→ [transformer_from_scratch.md](transformer_from_scratch.md)**：MoE 将 Dense Transformer 中的 FeedForward 替换为 MoELayer，其余组件完全相同
- **→ [lora_peft.md](lora_peft.md)**：MoE 模型的参数高效微调需要额外考虑 Expert 层的 LoRA 策略
- **→ [grpo.md](grpo.md)**：GRPO 等 RL 方法与 MoE 的结合是当前研究热点（DeepSeek-R1 使用了 MoE + GRPO）

---

## 进一步学习

- **Switch Transformer**（首个超大 MoE）：[arxiv 2101.03961](https://arxiv.org/abs/2101.03961)
- **Mixtral of Experts**（开源 MoE LLM）：[arxiv 2401.04088](https://arxiv.org/abs/2401.04088)
- **DeepSeekMoE**（细粒度 MoE）：[arxiv 2401.06066](https://arxiv.org/abs/2401.06066)
- **Outrageously Large Neural Networks**（MoE 的 NLP 奠基）：[arxiv 1701.06538](https://arxiv.org/abs/1701.06538)
- **HuggingFace MoE 综述博客**：https://huggingface.co/blog/moe（图文并茂，强烈推荐）
