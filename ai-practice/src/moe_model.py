"""MoE Transformer teaching model; only routing differs from the dense core."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path

import torch
import torch.nn as nn
from torch.nn import functional as F

from transformer_core import (
    FeedForward,
    MultiHeadAttention,
    TransformerConfig,
    position_encoding,
)

num_experts = 4
top_k = 2
aux_loss_weight = 0.01
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class MoEConfig(TransformerConfig):
    num_experts: int = 4
    top_k: int = 2
    aux_loss_weight: float = 0.01

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.num_experts < 1 or not 1 <= self.top_k <= self.num_experts:
            raise ValueError("top_k must be between 1 and num_experts")


DEFAULT_MOE_CONFIG = MoEConfig()


class Router(nn.Module):
    def __init__(self, config: MoEConfig = DEFAULT_MOE_CONFIG) -> None:
        super().__init__()
        self.config = config
        self.gate = nn.Linear(config.d_model, config.num_experts, bias=False)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        gate_probs = F.softmax(self.gate(x), dim=-1)
        weights, indices = torch.topk(gate_probs, self.config.top_k, dim=-1)
        weights = weights / weights.sum(dim=-1, keepdim=True)
        return indices, weights, gate_probs


class MoELayer(nn.Module):
    def __init__(self, config: MoEConfig = DEFAULT_MOE_CONFIG) -> None:
        super().__init__()
        self.config = config
        self.router = Router(config)
        self.experts = nn.ModuleList([
            FeedForward(config) for _ in range(config.num_experts)
        ])

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        batch, length, channels = x.shape
        flat = x.view(batch * length, channels)
        indices, weights, gate_probs = self.router(flat)
        output = torch.zeros_like(flat)
        for expert_index, expert in enumerate(self.experts):
            token_mask, top_position = (indices == expert_index).nonzero(as_tuple=True)
            if token_mask.numel() == 0:
                continue
            expert_output = expert(flat[token_mask])
            gate_weight = weights[token_mask, top_position].unsqueeze(-1)
            output[token_mask] += gate_weight * expert_output

        with torch.no_grad():
            top1_indices = indices[:, 0]
            fraction = torch.zeros(self.config.num_experts, device=x.device)
            for index in range(self.config.num_experts):
                fraction[index] = (top1_indices == index).float().mean()
        mean_gate = gate_probs.mean(dim=0)
        aux_loss = self.config.num_experts * (fraction * mean_gate).sum()
        return output.view(batch, length, channels), aux_loss


class MoETransformerBlock(nn.Module):
    def __init__(self, config: MoEConfig = DEFAULT_MOE_CONFIG) -> None:
        super().__init__()
        self.config = config
        head_size = config.d_model // config.num_heads
        self.multi_head_attention_layer = MultiHeadAttention(head_size=head_size, config=config)
        self.moe_layer = MoELayer(config)
        self.layer_norm_1 = nn.LayerNorm(config.d_model)
        self.layer_norm_2 = nn.LayerNorm(config.d_model)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        x = x + self.multi_head_attention_layer(self.layer_norm_1(x))
        moe_out, aux_loss = self.moe_layer(self.layer_norm_2(x))
        return x + moe_out, aux_loss


class MoETransformerLanguageModel(nn.Module):
    def __init__(
        self, vocab_size: int, config: MoEConfig = DEFAULT_MOE_CONFIG
    ) -> None:
        super().__init__()
        if vocab_size < 1:
            raise ValueError("vocab_size must be positive")
        self.config = config
        self.max_token_value = vocab_size
        self.token_embedding_lookup_table = nn.Embedding(vocab_size + 1, config.d_model)
        self.transformer_blocks = nn.ModuleList([
            MoETransformerBlock(config) for _ in range(config.num_blocks)
        ])
        self.final_layer_norm = nn.LayerNorm(config.d_model)
        self.language_model_out_linear_layer = nn.Linear(config.d_model, vocab_size)

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        _batch, length = idx.shape
        x = self.token_embedding_lookup_table(idx) + position_encoding(
            self.config, length, idx.device
        )
        total_aux_loss = torch.zeros((), device=idx.device)
        for block in self.transformer_blocks:
            x, aux_loss = block(x)
            total_aux_loss += aux_loss
        x = self.final_layer_norm(x)
        logits = self.language_model_out_linear_layer(x)
        loss = None
        if targets is not None:
            batch, length, channels = logits.shape
            cross_entropy = F.cross_entropy(
                logits.view(batch * length, channels), targets.view(batch * length)
            )
            loss = cross_entropy + self.config.aux_loss_weight * total_aux_loss
        return logits, loss

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int) -> torch.Tensor:
        for _ in range(max_new_tokens):
            idx_crop = idx[:, -self.config.context_length:]
            logits, _loss = self(idx_crop)
            probabilities = F.softmax(logits[:, -1, :], dim=-1)
            idx_next = torch.multinomial(probabilities, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx


def count_parameters(model: nn.Module) -> int:
    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data/sales_textbook.txt")
    parser.add_argument("--checkpoint", type=Path, default=PROJECT_ROOT / "moe-model-ckpt.pt")
    parser.add_argument("--download", action="store_true", help="explicitly download missing training data")
    parser.add_argument("--max-iters", type=int)
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"])
    parser.add_argument("--prompt", default="The salesperson")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DEFAULT_MOE_CONFIG
    if args.max_iters is not None:
        if args.max_iters < 1:
            raise ValueError("--max-iters must be positive")
        config = replace(config, max_iters=args.max_iters)
    if args.device:
        config = replace(config, device=args.device)

    from training import (
        load_training_data,
        save_checkpoint,
        train_model,
    )

    torch.manual_seed(config.torch_seed)
    data = load_training_data(args.data, download=args.download)
    model = MoETransformerLanguageModel(data.max_token_value, config).to(config.device)
    print(f"设备: {config.device}")
    print(f"模型参数量: {count_parameters(model):,}")
    print(f"MoE: experts={config.num_experts}, top_k={config.top_k}")
    if args.checkpoint.exists():
        model.load_state_dict(
            torch.load(args.checkpoint, map_location=config.device, weights_only=True)
        )
        print(f"已加载模型：{args.checkpoint}")
    else:
        train_model(model, data, config)
        save_checkpoint(model, args.checkpoint)
        print(f"模型训练完成并保存：{args.checkpoint}")

    model.eval()
    start_ids = data.encoding.encode(args.prompt)
    if not start_ids:
        raise ValueError("prompt must contain at least one token")
    tokens = torch.tensor(start_ids, dtype=torch.long, device=config.device)[None, ...]
    generated = model.generate(tokens, max_new_tokens=100)
    print(data.encoding.decode(generated[0].tolist()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
