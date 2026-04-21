---
title: "MoE Transformer：用稀疏激活扩大模型容量"
type: tutorial_note
stage: 1.5
notebook: notebooks/05_moe_transformer.ipynb
prerequisites: ["transformer_from_scratch", "tokenization"]
updated_on: 2026-04-21
---

# exp_005：MoE Transformer——稀疏激活与专家混合

## 1. 学习目标

完成本实验后，你应该能够：

- [ ] 解释 MoE 的核心价值：**参数量与计算量的分离**（更多容量，不等于更多计算）
- [ ] 手写 `Router`（Top-K 门控）和 `MoELayer`（加权聚合多 Expert）
- [ ] 理解 **Expert Collapse** 问题，以及辅助负载均衡损失如何解决它
- [ ] 对比 Dense Transformer 和 MoE Transformer 的训练曲线，解释差异原因
- [ ] 能回答："Mixtral-8x7B 有 8 个 Expert，但实际计算量相当于几个 7B Dense 模型？"

---

## 2. 核心概念（Why）

### 2.1 Dense Transformer 的扩展瓶颈

在 Stage 1 中，我们实现的是标准的 Dense Transformer：每个 token 通过相同的 FeedForward 网络（FFN）。

**扩展公式**：想提升模型能力 → 增大 `d_model` 或 `num_blocks` → 参数量和计算量**同比例增加**。

这是一个根本性的效率问题。以 Qwen2.5-7B 为例：
- 7B 参数全部用于每个 token 的计算
- 推理时每生成一个 token，都要"过"完整的 7B 参数

### 2.2 MoE 的洞察：条件计算（Conditional Computation）

**核心思想**：不同 token 需要的"知识"不同，不需要全部 Expert 参与每次计算。

> "让 Router 根据输入动态选择最合适的 Expert，其他 Expert 保持沉默。"

**MoE 的参数/计算量分离**：

```
Dense FFN（d_model=64）:
  参数量 = d × 4d × 2 = 32,768
  每 token 计算量 = 相同

MoE（4 experts, top_k=2）:
  参数量 = 4 × 32,768 = 131,072（4 倍！）
  每 token 计算量 = 2 × 32,768 = 65,536（2 倍，而非 4 倍）

结论：花 2 倍计算量，获得 4 倍参数容量。
```

### 2.3 Top-K 门控机制

Router 的工作原理（以 top_k=2, num_experts=4 为例）：

```
token 表示 x ∈ R^{d_model}
  ↓
Router.gate: Linear(d_model → 4)
  → logits: [1.2, -0.3, 0.8, 2.1]
  ↓
Softmax
  → gate_probs: [0.25, 0.05, 0.18, 0.52]   ← 原始概率（用于 aux_loss）
  ↓
Top-2 选择
  → 选中 Expert 3（0.52）和 Expert 0（0.25）
  ↓
重新归一化（使选中 Expert 的权重 sum=1）
  → weights: [0.33, 0.67]
  ↓
输出 = 0.33 × Expert_0(x) + 0.67 × Expert_3(x)
```

**为什么要重新归一化？** 保证梯度尺度稳定，不受绝对门控值影响。

### 2.4 Expert Collapse 与负载均衡

**Expert Collapse**：不施加任何约束时，Router 会收敛到总是选同一个 Expert（因为被选中的 Expert 获得更多梯度，训练得更好，于是被选得更频繁——正反馈循环）。

**解决方案**：辅助损失（Switch Transformer，2021）

```python
# aux_loss = num_experts × Σ(f_i × P_i)
# f_i = Expert i 接收的 token 比例（离散，stop_gradient）
# P_i = Expert i 的平均门控概率（连续，可微分）
aux_loss = num_experts * (fraction.detach() * mean_gate).sum()
```

直觉：
- 如果 Expert 0 接收了 80% 的 token（f_0=0.8），但 Expert 1 只有 5%（f_1=0.05）
- aux_loss 会惩罚这种不均衡，推动 Router 更均匀地分配

---

## 3. 实现解析

核心代码位于 `src/moe_model.py`。

### 3.1 Router（L111-144）

```python
class Router(nn.Module):
    def __init__(self):
        super().__init__()
        # 线性门控层：d_model → num_experts（无 bias）
        self.gate = nn.Linear(d_model, num_experts, bias=False)

    def forward(self, x):
        # x: (N, d_model)，N = B*T
        gate_probs = F.softmax(self.gate(x), dim=-1)   # (N, num_experts)
        
        # Top-K 选择
        top_k_weights, top_k_indices = torch.topk(gate_probs, top_k, dim=-1)
        
        # 重新归一化（使选中权重 sum=1）
        top_k_weights = top_k_weights / top_k_weights.sum(dim=-1, keepdim=True)
        
        return top_k_indices, top_k_weights, gate_probs
```

**关键设计点**：
- `gate` 的 `bias=False`：Router 应该是纯粹的内容路由，不受偏置项影响
- 先 Softmax 再 Top-K（而非先 Top-K 再 Softmax）：确保 gate_probs 的语义是概率

### 3.2 MoELayer（L147-214）

```python
class MoELayer(nn.Module):
    def __init__(self):
        super().__init__()
        self.router = Router()
        self.experts = nn.ModuleList([FeedForward() for _ in range(num_experts)])

    def forward(self, x):
        B, T, C = x.shape
        x_flat = x.view(B * T, C)              # 合并 batch 和 seq 维度
        
        indices, weights, gate_probs = self.router(x_flat)
        output = torch.zeros_like(x_flat)
        
        # 逐 Expert 处理（稀疏计算的关键）
        for expert_idx, expert in enumerate(self.experts):
            token_mask, k_pos = (indices == expert_idx).nonzero(as_tuple=True)
            if token_mask.numel() == 0:
                continue
            expert_output = expert(x_flat[token_mask])
            gate_weight = weights[token_mask, k_pos].unsqueeze(-1)
            output[token_mask] += gate_weight * expert_output
        
        # 辅助损失（负载均衡）
        with torch.no_grad():
            fraction = torch.zeros(num_experts, device=x.device)
            for e in range(num_experts):
                fraction[e] = (indices[:, 0] == e).float().mean()
        mean_gate = gate_probs.mean(dim=0)
        aux_loss = num_experts * (fraction * mean_gate).sum()
        
        return output.view(B, T, C), aux_loss
```

### 3.3 总损失的计算（L261-270）

```python
# MoETransformerLanguageModel.forward()
total_aux_loss = 0.0
for block in self.transformer_blocks:
    x, aux_loss = block(x)
    total_aux_loss += aux_loss          # 累积所有 Block 的 aux_loss

# 最终损失 = CE + λ × 负载均衡
loss = ce_loss + aux_loss_weight * total_aux_loss
```

**注意**：Dense Transformer 使用 `nn.Sequential`，MoE 不能用它，因为需要收集每个 Block 的 `aux_loss`。

---

## 4. 实验结果

### 4.1 参数量对比

| 配置 | 总参数量 | FFN 参数量 | 每 token 激活参数 |
|------|---------|-----------|----------------|
| Dense（model.py） | [待补充] | [待补充] | 100%（全量） |
| MoE-4E2K（moe_model.py） | [待补充] | [待补充] × 4 | 50%（top_k/num_experts） |

运行以下代码获取实际数值（Notebook Cell 3）：

```python
from src.model import TransformerLanguageModel
from src.moe_model import MoETransformerLanguageModel, count_parameters

dense = TransformerLanguageModel()
moe = MoETransformerLanguageModel()
print(f"Dense: {count_parameters(dense):,}")
print(f"MoE:   {count_parameters(moe):,}（{count_parameters(moe)/count_parameters(dense):.1f}x）")
```

### 4.2 训练损失对比（5000 步）

| 步数 | Dense Train Loss | Dense Val Loss | MoE Train Loss | MoE Val Loss |
|------|-----------------|---------------|----------------|-------------|
| 0    | [待补充] | [待补充] | [待补充] | [待补充] |
| 1000 | [待补充] | [待补充] | [待补充] | [待补充] |
| 5000 | [待补充] | [待补充] | [待补充] | [待补充] |

> 实际数值需运行 Notebook 获取。运行 Cell 10-11 即可得到对比数据。

### 4.3 Expert 利用率（训练结束时）

| Expert | 接收 token 比例 |
|--------|--------------|
| Expert 0 | [待补充] |
| Expert 1 | [待补充] |
| Expert 2 | [待补充] |
| Expert 3 | [待补充] |

均匀分配目标：每个 Expert 接收约 25%（=100%/num_experts）。实际值越接近均匀，说明 aux_loss 效果越好。

---

## 5. 思考题 & 延伸实验

### 思考题

**Q1（核心）**：Mixtral-8x7B 有 8 个 Expert，每次激活 top_k=2。它的实际推理计算量相当于几个 Dense 7B 模型？（提示：思考 FFN 参数占总参数量的比例）

**Q2（动手）**：将 `top_k` 从 2 改为 1，重新训练 1000 步，观察：
- 训练损失是否更高/更低？
- Expert 利用率分布是否更不均衡？
- 为什么减少 top_k 会影响训练稳定性？

**Q3（关键）**：将 `aux_loss_weight` 从 0.01 改为 0，重新训练，观察 1000 步后各 Expert 接收的 token 比例。Expert Collapse 何时出现？（运行 Notebook Cell 9 的对比演示）

**Q4（数学）**：当 `num_experts=4, top_k=2` 时，MoE FFN 的参数量是 Dense FFN 的 4 倍，但计算量只有 Dense 的 2 倍。如果将 `top_k` 改为 3，计算量变成 Dense 的几倍？参数量仍是 4 倍吗？

**Q5（扩展）**：DeepSeek-V3 使用了"细粒度 MoE"（num_experts=256, top_k=8）。相比 Mixtral 的（8, 2），这种设计有什么优缺点？

---

## 6. 参考资料

### 奠基论文

- **Switch Transformer**（Google, 2021）：首次在超大规模（Trillion 参数）验证 MoE 的可行性，提出辅助负载均衡损失
  [arxiv: 2101.03961](https://arxiv.org/abs/2101.03961)

- **Outrageously Large Neural Networks**（Shazeer et al., 2017）：将 MoE 引入 NLP 的奠基工作（LSTM + MoE）
  [arxiv: 1701.06538](https://arxiv.org/abs/1701.06538)

- **Mixtral of Experts**（Mistral AI, 2024）：开源 MoE LLM，8 experts top_k=2，性能超过 Llama 2-70B
  [arxiv: 2401.04088](https://arxiv.org/abs/2401.04088)

- **DeepSeekMoE**（DeepSeek, 2024）：细粒度 MoE（256 experts, top_k=8）+ Expert 专业化机制
  [arxiv: 2401.06066](https://arxiv.org/abs/2401.06066)

### 博客与视频

- **Mixture of Experts Explained**（HuggingFace Blog）：最全面的 MoE 入门综述
  https://huggingface.co/blog/moe

- **本项目实现**：[src/moe_model.py](../src/moe_model.py)

- **概念深化**：[wiki/concepts/mixture_of_experts.md](../wiki/concepts/mixture_of_experts.md)
