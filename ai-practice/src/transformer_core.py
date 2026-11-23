from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn
from torch.nn import functional as F


@dataclass(frozen=True)
class TransformerConfig:
    batch_size: int = 4
    context_length: int = 16
    d_model: int = 64
    num_blocks: int = 8
    num_heads: int = 4
    learning_rate: float = 1e-3
    dropout: float = 0.1
    max_iters: int = 5000
    eval_interval: int = 50
    eval_iters: int = 20
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    torch_seed: int = 1337

    def __post_init__(self) -> None:
        if self.d_model <= 0 or self.d_model % 2:
            raise ValueError("d_model must be a positive even integer")
        if self.num_heads <= 0 or self.d_model % self.num_heads:
            raise ValueError("d_model must be divisible by num_heads")
        if min(self.batch_size, self.context_length, self.num_blocks, self.max_iters) < 1:
            raise ValueError("batch, context, block and iteration counts must be positive")


DEFAULT_CONFIG = TransformerConfig()


class FeedForward(nn.Module):
    def __init__(self, config: TransformerConfig = DEFAULT_CONFIG) -> None:
        super().__init__()
        self.d_model = config.d_model
        self.dropout = config.dropout
        self.ffn = nn.Sequential(
            nn.Linear(config.d_model, config.d_model * 4),
            nn.ReLU(),
            nn.Linear(config.d_model * 4, config.d_model),
            nn.Dropout(config.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.ffn(x)


class Attention(nn.Module):
    def __init__(self, head_size: int, config: TransformerConfig = DEFAULT_CONFIG) -> None:
        super().__init__()
        self.d_model = config.d_model
        self.head_size = head_size
        self.context_length = config.context_length
        self.dropout = config.dropout
        self.key_layer = nn.Linear(config.d_model, head_size, bias=False)
        self.query_layer = nn.Linear(config.d_model, head_size, bias=False)
        self.value_layer = nn.Linear(config.d_model, head_size, bias=False)
        self.register_buffer(
            "tril", torch.tril(torch.ones((config.context_length, config.context_length)))
        )
        self.dropout_layer = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        _batch, length, channels = x.shape
        if length > self.context_length or channels != self.d_model:
            raise ValueError("attention input exceeds its configured shape")
        query = self.query_layer(x)
        key = self.key_layer(x)
        value = self.value_layer(x)
        weights = (query @ key.transpose(-2, -1)) * (1.0 / math.sqrt(key.size(-1)))
        weights = weights.masked_fill(self.tril[:length, :length] == 0, float("-inf"))
        weights = self.dropout_layer(F.softmax(weights, dim=-1))
        return weights @ value


class MultiHeadAttention(nn.Module):
    def __init__(self, head_size: int, config: TransformerConfig = DEFAULT_CONFIG) -> None:
        super().__init__()
        self.num_heads = config.num_heads
        self.head_size = head_size
        self.d_model = config.d_model
        self.context_length = config.context_length
        self.dropout = config.dropout
        self.heads = nn.ModuleList([
            Attention(head_size=head_size, config=config) for _ in range(config.num_heads)
        ])
        self.projection_layer = nn.Linear(config.d_model, config.d_model)
        self.dropout_layer = nn.Dropout(config.dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = torch.cat([head(x) for head in self.heads], dim=-1)
        return self.dropout_layer(self.projection_layer(out))


class TransformerBlock(nn.Module):
    def __init__(self, config: TransformerConfig = DEFAULT_CONFIG) -> None:
        super().__init__()
        self.d_model = config.d_model
        self.context_length = config.context_length
        self.num_heads = config.num_heads
        self.dropout = config.dropout
        head_size = config.d_model // config.num_heads
        self.multi_head_attention_layer = MultiHeadAttention(head_size=head_size, config=config)
        self.feed_forward_layer = FeedForward(config)
        self.layer_norm_1 = nn.LayerNorm(config.d_model)
        self.layer_norm_2 = nn.LayerNorm(config.d_model)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.multi_head_attention_layer(self.layer_norm_1(x))
        return x + self.feed_forward_layer(self.layer_norm_2(x))


def position_encoding(config: TransformerConfig, length: int, device: torch.device) -> torch.Tensor:
    table = torch.zeros(config.context_length, config.d_model)
    position = torch.arange(0, config.context_length, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(
        torch.arange(0, config.d_model, 2).float()
        * (-math.log(10000.0) / config.d_model)
    )
    table[:, 0::2] = torch.sin(position * div_term)
    table[:, 1::2] = torch.cos(position * div_term)
    return table[:length, :].to(device)


class TransformerLanguageModel(nn.Module):
    def __init__(
        self, vocab_size: int, config: TransformerConfig = DEFAULT_CONFIG
    ) -> None:
        super().__init__()
        if vocab_size < 1:
            raise ValueError("vocab_size must be positive")
        self.config = config
        self.d_model = config.d_model
        self.context_length = config.context_length
        self.num_heads = config.num_heads
        self.num_blocks = config.num_blocks
        self.dropout = config.dropout
        self.max_token_value = vocab_size
        self.token_embedding_lookup_table = nn.Embedding(vocab_size + 1, config.d_model)
        self.transformer_blocks = nn.Sequential(*(
            [TransformerBlock(config) for _ in range(config.num_blocks)]
            + [nn.LayerNorm(config.d_model)]
        ))
        self.language_model_out_linear_layer = nn.Linear(config.d_model, vocab_size)

    def forward(
        self, idx: torch.Tensor, targets: torch.Tensor | None = None
    ) -> tuple[torch.Tensor, torch.Tensor | None]:
        _batch, length = idx.shape
        positions = position_encoding(self.config, length, idx.device)
        x = self.token_embedding_lookup_table(idx) + positions
        x = self.transformer_blocks(x)
        logits = self.language_model_out_linear_layer(x)
        loss = None
        if targets is not None:
            batch, length, channels = logits.shape
            loss = F.cross_entropy(
                logits.view(batch * length, channels), targets.view(batch * length)
            )
        return logits, loss

    @torch.no_grad()
    def generate(self, idx: torch.Tensor, max_new_tokens: int) -> torch.Tensor:
        for _ in range(max_new_tokens):
            idx_crop = idx[:, -self.context_length:]
            logits, _loss = self(idx_crop)
            probabilities = F.softmax(logits[:, -1, :], dim=-1)
            idx_next = torch.multinomial(probabilities, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)
        return idx
