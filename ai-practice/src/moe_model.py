# moe_model.py — Mixture of Experts Transformer
#
# 基于 src/model.py 的 Dense Transformer，将 FeedForward 替换为 MoELayer。
# 其余架构（Attention、残差连接、位置编码）完全相同，便于直接对比训练曲线。
#
# 运行方式（从 ai-practice/ 目录）：
#   python3 src/moe_model.py
#
# 核心改动：FeedForward → MoELayer（Router + N 个 Expert）

import os
import requests
import math
import tiktoken
import torch
import torch.nn as nn
from torch.nn import functional as F

# ========== 超参数（与 model.py 完全对齐，便于公平对比） ==========
batch_size = 4
context_length = 16
d_model = 64
num_blocks = 8
num_heads = 4
learning_rate = 1e-3
dropout = 0.1
max_iters = 5000
eval_interval = 50
eval_iters = 20
device = 'cuda' if torch.cuda.is_available() else 'cpu'
TORCH_SEED = 1337
torch.manual_seed(TORCH_SEED)

# ========== MoE 特有超参数 ==========
num_experts = 4       # Expert 总数：参数量是 Dense FFN 的 4 倍
top_k = 2             # 每个 token 激活的 Expert 数（Mixtral-8x7B 同款设计）
aux_loss_weight = 0.01  # 负载均衡损失权重 λ（太大影响主损失，太小 Expert Collapse）

# ========== 数据加载（与 model.py 相同） ==========
if not os.path.exists('data/sales_textbook.txt'):
    url = ('https://huggingface.co/datasets/goendalf666/'
           'sales-textbook_for_convincing_and_selling/raw/main/sales_textbook.txt')
    with open('data/sales_textbook.txt', 'w') as f:
        f.write(requests.get(url).text)

with open('data/sales_textbook.txt', 'r', encoding='utf-8') as f:
    text = f.read()

encoding = tiktoken.get_encoding("cl100k_base")
tokenized_text = encoding.encode(text)
max_token_value = max(tokenized_text) + 1
tokenized_text = torch.tensor(tokenized_text, dtype=torch.long, device=device)

split_idx = int(len(tokenized_text) * 0.9)
train_data = tokenized_text[:split_idx]
val_data = tokenized_text[split_idx:]


# ========== Dense 基础组件（与 model.py 相同） ==========

class FeedForward(nn.Module):
    """单个 Expert 的 FFN 实现（与 model.py 中完全相同）

    在 MoE 中，每个 Expert 就是一个独立的 FeedForward 实例。
    d_model → 4*d_model → d_model，使用 ReLU 激活。
    """
    def __init__(self):
        super().__init__()
        self.ffn = nn.Sequential(
            nn.Linear(d_model, d_model * 4),
            nn.ReLU(),
            nn.Linear(d_model * 4, d_model),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.ffn(x)


class Attention(nn.Module):
    """缩放点积注意力（与 model.py 中相同）"""
    def __init__(self, head_size: int):
        super().__init__()
        self.head_size = head_size
        self.key_layer = nn.Linear(d_model, head_size, bias=False)
        self.query_layer = nn.Linear(d_model, head_size, bias=False)
        self.value_layer = nn.Linear(d_model, head_size, bias=False)
        self.register_buffer('tril', torch.tril(torch.ones((context_length, context_length))))
        self.dropout_layer = nn.Dropout(dropout)

    def forward(self, x):
        B, T, C = x.shape
        assert T <= context_length
        q = self.query_layer(x)
        k = self.key_layer(x)
        v = self.value_layer(x)
        weights = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        weights = weights.masked_fill(self.tril[:T, :T] == 0, float('-inf'))
        weights = F.softmax(weights, dim=-1)
        weights = self.dropout_layer(weights)
        return weights @ v


class MultiHeadAttention(nn.Module):
    """多头注意力机制（与 model.py 中相同）"""
    def __init__(self, head_size: int):
        super().__init__()
        self.heads = nn.ModuleList([Attention(head_size=head_size) for _ in range(num_heads)])
        self.projection_layer = nn.Linear(d_model, d_model)
        self.dropout_layer = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([h(x) for h in self.heads], dim=-1)
        return self.dropout_layer(self.projection_layer(out))


# ========== MoE 新增组件 ==========

class Router(nn.Module):
    """Token 路由器：决定每个 token 发送给哪些 Expert。

    核心流程：
      token 表示 (d_model)
        → Linear(d_model → num_experts)   # 计算 Expert 分数
        → Softmax                          # 归一化为门控概率
        → Top-K 选择                       # 只保留概率最高的 top_k 个 Expert
        → 重新归一化（所选 Expert 的权重 sum=1）

    返回：
      indices   (N, top_k)  —— 每个 token 选中的 Expert 编号
      weights   (N, top_k)  —— 对应的门控权重（重新归一化后）
      gate_probs(N, num_experts) —— 原始 Softmax 概率（用于计算 aux_loss）
    """
    def __init__(self):
        super().__init__()
        # 线性门控：d_model → num_experts（常见做法：不用 bias）
        self.gate = nn.Linear(d_model, num_experts, bias=False)

    def forward(self, x):
        # x: (N, d_model)，N = B*T（将 batch 和 seq 维度合并）
        gate_logits = self.gate(x)                       # (N, num_experts)
        gate_probs = F.softmax(gate_logits, dim=-1)      # (N, num_experts)

        # Top-K：取概率最高的 top_k 个 Expert
        top_k_weights, top_k_indices = torch.topk(gate_probs, top_k, dim=-1)
        # top_k_weights: (N, top_k)，top_k_indices: (N, top_k)

        # 重新归一化：只保留选中 Expert 的权重，使其 sum=1
        top_k_weights = top_k_weights / top_k_weights.sum(dim=-1, keepdim=True)

        return top_k_indices, top_k_weights, gate_probs


class MoELayer(nn.Module):
    """Mixture of Experts 层：用 num_experts 个 FFN 替代单个 Dense FFN。

    参数量 vs 计算量的分离：
      参数量：Dense FFN × num_experts（更多容量）
      每 token 计算量：Dense FFN × top_k（只有 top_k 个 Expert 激活）

    以本项目的配置（num_experts=4, top_k=2）为例：
      参数量是 Dense 的 4 倍，但每 token 计算量只是 Dense 的 2 倍。
      这就是 MoE 的核心价值：用更少的计算买到更多的模型容量。

    辅助损失（aux_loss）：
      防止所有 token 都路由到同一个 Expert（Expert Collapse）。
      使用 Switch Transformer 风格的负载均衡损失：
        aux_loss = num_experts × Σ(f_i × P_i)
      其中 f_i 是 Expert i 的 token 接收比例（不可微），
           P_i 是 Expert i 的平均门控概率（可微，用于梯度传播）。
    """
    def __init__(self):
        super().__init__()
        self.router = Router()
        # num_experts 个独立 FFN，每个都是普通的 FeedForward
        self.experts = nn.ModuleList([FeedForward() for _ in range(num_experts)])

    def forward(self, x):
        B, T, C = x.shape
        x_flat = x.view(B * T, C)  # (N, d_model)，N = B*T

        # ① 路由
        indices, weights, gate_probs = self.router(x_flat)
        # indices: (N, top_k)，weights: (N, top_k)，gate_probs: (N, num_experts)

        # ② Expert 计算：按 Expert 编号分组处理
        output = torch.zeros_like(x_flat)  # (N, d_model)

        for expert_idx, expert in enumerate(self.experts):
            # 找出被路由到此 Expert 的 (token行号, top_k位置) 对
            token_mask, k_pos = (indices == expert_idx).nonzero(as_tuple=True)

            if token_mask.numel() == 0:
                continue  # 此 Expert 没有被分配到任何 token，跳过

            # 提取对应 token 的输入，通过 Expert 计算
            expert_input = x_flat[token_mask]            # (num_assigned, d_model)
            expert_output = expert(expert_input)         # (num_assigned, d_model)

            # 加权累加到输出（门控权重决定每个 Expert 的贡献比例）
            gate_weight = weights[token_mask, k_pos].unsqueeze(-1)  # (num_assigned, 1)
            output[token_mask] += gate_weight * expert_output

        # ③ 负载均衡辅助损失（Switch Transformer 风格）
        # f_i：Expert i 接收 top-1 token 的比例（离散，用 no_grad 包裹）
        # P_i：Expert i 的平均门控概率（连续，允许梯度通过）
        with torch.no_grad():
            top1_indices = indices[:, 0]  # (N,)，取 top-1 分配（只用于统计）
            fraction = torch.zeros(num_experts, device=x.device)
            for e in range(num_experts):
                fraction[e] = (top1_indices == e).float().mean()

        mean_gate = gate_probs.mean(dim=0)              # (num_experts,)，可微
        aux_loss = num_experts * (fraction * mean_gate).sum()

        output = output.view(B, T, C)
        return output, aux_loss


class MoETransformerBlock(nn.Module):
    """MoE Transformer Block：将 Dense FFN 替换为 MoELayer。

    与 Dense TransformerBlock 的唯一区别：
      self.feed_forward_layer (FeedForward) → self.moe_layer (MoELayer)

    forward() 额外返回 aux_loss，使上层模型能够累积并加入总损失。
    """
    def __init__(self):
        super().__init__()
        head_size = d_model // num_heads
        self.multi_head_attention_layer = MultiHeadAttention(head_size=head_size)
        self.moe_layer = MoELayer()          # ← 唯一改动
        self.layer_norm_1 = nn.LayerNorm(d_model)
        self.layer_norm_2 = nn.LayerNorm(d_model)

    def forward(self, x):
        # Pre-LN 残差（与 Dense TransformerBlock 相同）
        x = x + self.multi_head_attention_layer(self.layer_norm_1(x))
        # MoE FFN：返回 (输出, aux_loss)
        moe_out, aux_loss = self.moe_layer(self.layer_norm_2(x))
        x = x + moe_out
        return x, aux_loss


class MoETransformerLanguageModel(nn.Module):
    """MoE Transformer 语言模型（完整版）。

    与 TransformerLanguageModel 的关键差异：
    1. TransformerBlock → MoETransformerBlock（FFN 替换为 MoELayer）
    2. 使用 nn.ModuleList 而非 nn.Sequential（需要逐 Block 收集 aux_loss）
    3. forward() 返回的 loss = CE loss + λ × 负载均衡 aux_loss
    """
    def __init__(self):
        super().__init__()
        # 词嵌入层（与 Dense 相同）
        self.token_embedding_lookup_table = nn.Embedding(
            num_embeddings=max_token_value + 1,
            embedding_dim=d_model
        )
        # MoE Transformer Block 序列（ModuleList，不是 Sequential）
        self.transformer_blocks = nn.ModuleList(
            [MoETransformerBlock() for _ in range(num_blocks)]
        )
        self.final_layer_norm = nn.LayerNorm(d_model)
        self.language_model_out_linear_layer = nn.Linear(d_model, max_token_value)

    def forward(self, idx, targets=None):
        B, T = idx.shape

        # 位置编码（与 model.py 相同，正弦/余弦方案）
        position_encoding_lookup_table = torch.zeros(context_length, d_model)
        position = torch.arange(0, context_length, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model)
        )
        position_encoding_lookup_table[:, 0::2] = torch.sin(position * div_term)
        position_encoding_lookup_table[:, 1::2] = torch.cos(position * div_term)
        position_embedding = position_encoding_lookup_table[:T, :].to(device)

        x = self.token_embedding_lookup_table(idx) + position_embedding

        # 逐 Block 前向，累积 aux_loss（这是不用 Sequential 的原因）
        total_aux_loss = torch.tensor(0.0, device=device)
        for block in self.transformer_blocks:
            x, aux_loss = block(x)
            total_aux_loss += aux_loss

        x = self.final_layer_norm(x)
        logits = self.language_model_out_linear_layer(x)

        loss = None
        if targets is not None:
            B, T, C = logits.shape
            logits_reshaped = logits.view(B * T, C)
            targets_reshaped = targets.view(B * T)
            ce_loss = F.cross_entropy(logits_reshaped, targets_reshaped)
            # 总损失：交叉熵 + λ × 负载均衡辅助损失
            # aux_loss_weight 过大会主导训练，过小则无法防止 Expert Collapse
            loss = ce_loss + aux_loss_weight * total_aux_loss

        return logits, loss

    def generate(self, idx, max_new_tokens):
        """自回归文本生成（与 Dense 版本完全相同）"""
        for _ in range(max_new_tokens):
            idx_crop = idx[:, -context_length:]
            logits, _ = self(idx_crop)
            logits_last_timestep = logits[:, -1, :]
            probs = F.softmax(logits_last_timestep, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


# ========== 工具函数 ==========

def get_batch(split):
    """获取一个批次的训练或验证数据（与 model.py 相同）"""
    data = train_data if split == 'train' else val_data
    ix = torch.randint(len(data) - context_length, (batch_size,))
    x = torch.stack([data[i:i + context_length] for i in ix])
    y = torch.stack([data[i + 1:i + context_length + 1] for i in ix])
    return x.to(device), y.to(device)


@torch.no_grad()
def estimate_loss(model):
    """估计训练和验证损失"""
    out = {}
    model.eval()
    for split in ['train', 'valid']:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = get_batch(split)
            _, loss = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


def count_parameters(model):
    """统计模型可训练参数量"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# ========== 主入口：训练 MoE 模型 ==========

if __name__ == '__main__':
    print("=" * 60)
    print("MoE Transformer 语言模型训练")
    print(f"设备: {device}")
    print(f"基础超参: d_model={d_model}, num_blocks={num_blocks}, num_heads={num_heads}")
    print(f"MoE 超参: num_experts={num_experts}, top_k={top_k}, aux_weight={aux_loss_weight}")
    print("=" * 60)

    # 初始化 MoE 模型
    moe_model = MoETransformerLanguageModel().to(device)
    total_params = count_parameters(moe_model)
    print(f"\n模型参数量: {total_params:,}")
    print(f"其中 Embedding 层: {(max_token_value + 1) * d_model:,}")
    print(f"其中 MoE FFN 层（{num_blocks} blocks × {num_experts} experts）: "
          f"{num_blocks * num_experts * (d_model * d_model * 4 * 2):,}")
    print(f"\n【对比参考】Dense FFN 层: "
          f"{num_blocks * (d_model * d_model * 4 * 2):,}（MoE 的 1/{num_experts}）")
    print(f"MoE 每 token 激活的 Expert 数: top_k={top_k}（计算量约 Dense 的 {top_k}x）")

    # 训练
    print("\n开始训练 MoE 模型...")
    optimizer = torch.optim.AdamW(moe_model.parameters(), lr=learning_rate)

    for step in range(max_iters):
        if step % eval_interval == 0 or step == max_iters - 1:
            losses = estimate_loss(moe_model)
            print(f'Step: {step:5d} | Train: {losses["train"]:.4f} | Valid: {losses["valid"]:.4f}')

        xb, yb = get_batch('train')
        logits, loss = moe_model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

    torch.save(moe_model.state_dict(), 'moe-model-ckpt.pt')
    print("\nMoE 模型训练完成，已保存至 moe-model-ckpt.pt")

    # 生成示例文本
    moe_model.eval()
    start = 'The salesperson'
    start_ids = encoding.encode(start)
    x = torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...]
    y = moe_model.generate(x, max_new_tokens=100)
    print('\n--- MoE 模型生成样本 ---')
    print(encoding.decode(y[0].tolist()))
    print('------------------------')
