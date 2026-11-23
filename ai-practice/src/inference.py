from __future__ import annotations

import argparse
from pathlib import Path

import torch

from transformer_core import DEFAULT_CONFIG, TransformerConfig, TransformerLanguageModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_model(
    checkpoint: Path = PROJECT_ROOT / "model-ckpt.pt",
    data_path: Path = PROJECT_ROOT / "data/sales_textbook.txt",
    config: TransformerConfig = DEFAULT_CONFIG,
) -> TransformerLanguageModel:
    if not checkpoint.is_file():
        raise FileNotFoundError(f"model checkpoint is missing: {checkpoint}")
    from training import load_training_data

    data = load_training_data(data_path, download=False)
    model = TransformerLanguageModel(data.max_token_value, config).to(config.device)
    model.load_state_dict(
        torch.load(checkpoint, map_location=config.device, weights_only=True)
    )
    model.eval()
    return model


def generate_text(
    model: TransformerLanguageModel, prompt: str, max_tokens: int = 100
) -> str:
    import tiktoken

    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    encoding = tiktoken.get_encoding("cl100k_base")
    start_ids = encoding.encode(prompt)
    device = next(model.parameters()).device
    tokens = torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...]
    generated = model.generate(tokens, max_new_tokens=max_tokens)
    return encoding.decode(generated[0].tolist())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=PROJECT_ROOT / "model-ckpt.pt")
    parser.add_argument("--data", type=Path, default=PROJECT_ROOT / "data/sales_textbook.txt")
    parser.add_argument("--prompt", help="generate once instead of opening interactive input")
    parser.add_argument("--max-tokens", type=int, default=100)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.max_tokens < 1:
        raise ValueError("--max-tokens must be positive")
    model = load_model(args.checkpoint, args.data)
    if args.prompt is not None:
        print(generate_text(model, args.prompt, max_tokens=args.max_tokens))
        return 0

    print("输入 'quit' 或 'exit' 退出程序")
    while True:
        prompt = input("\n请输入提示词: ")
        if prompt.lower() in {"quit", "exit"}:
            break
        if not prompt.strip():
            continue
        try:
            print("\n" + generate_text(model, prompt))
        except (OSError, RuntimeError, ValueError) as exc:
            print(f"生成过程中出现错误: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
