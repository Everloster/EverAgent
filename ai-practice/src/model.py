"""Dense Transformer teaching model; training runs only through the CLI."""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

import torch

from transformer_core import (
    DEFAULT_CONFIG,
    Attention,
    FeedForward,
    MultiHeadAttention,
    TransformerBlock,
    TransformerLanguageModel,
)

__all__ = [
    "Attention",
    "FeedForward",
    "MultiHeadAttention",
    "TransformerBlock",
    "TransformerLanguageModel",
]

batch_size = DEFAULT_CONFIG.batch_size
context_length = DEFAULT_CONFIG.context_length
d_model = DEFAULT_CONFIG.d_model
num_blocks = DEFAULT_CONFIG.num_blocks
num_heads = DEFAULT_CONFIG.num_heads
learning_rate = DEFAULT_CONFIG.learning_rate
dropout = DEFAULT_CONFIG.dropout
max_iters = DEFAULT_CONFIG.max_iters
eval_interval = DEFAULT_CONFIG.eval_interval
eval_iters = DEFAULT_CONFIG.eval_iters
device = DEFAULT_CONFIG.device
TORCH_SEED = DEFAULT_CONFIG.torch_seed
PROJECT_ROOT = Path(__file__).resolve().parents[1]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data/sales_textbook.txt")
    parser.add_argument("--checkpoint", type=Path, default=PROJECT_ROOT / "model-ckpt.pt")
    parser.add_argument("--download", action="store_true", help="explicitly download missing training data")
    parser.add_argument("--max-iters", type=int)
    parser.add_argument("--device", choices=["cpu", "cuda", "mps"])
    parser.add_argument("--prompt", default="The salesperson")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = DEFAULT_CONFIG
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
    model = TransformerLanguageModel(data.max_token_value, config).to(config.device)
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
    print("---------------")
    print(data.encoding.decode(generated[0].tolist()))
    print("---------------")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
