from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path

import tiktoken
import torch

from transformer_core import TransformerConfig

DATA_URL = (
    "https://huggingface.co/datasets/goendalf666/"
    "sales-textbook_for_convincing_and_selling/raw/main/sales_textbook.txt"
)
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class TrainingData:
    encoding: object
    tokenized_text: torch.Tensor
    train_data: torch.Tensor
    val_data: torch.Tensor
    max_token_value: int


def download_text(url: str, path: Path) -> None:
    import requests

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            handle.write(response.text)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_training_data(
    path: Path, *, download: bool = False
) -> TrainingData:
    if not path.exists():
        if not download:
            raise FileNotFoundError(
                f"training data is missing: {path}; pass --download to fetch it explicitly"
            )
        download_text(DATA_URL, path)
    text = path.read_text(encoding="utf-8")
    encoding = tiktoken.get_encoding("cl100k_base")
    tokenized_text = encoding.encode(text)
    if len(tokenized_text) < 3:
        raise ValueError("training data must contain at least three tokens")
    max_token_value = max(tokenized_text) + 1
    tokens = torch.tensor(tokenized_text, dtype=torch.long)
    split_idx = int(len(tokens) * 0.9)
    return TrainingData(
        encoding=encoding,
        tokenized_text=tokens,
        train_data=tokens[:split_idx],
        val_data=tokens[split_idx:],
        max_token_value=max_token_value,
    )


def get_batch(
    data: TrainingData, split: str, config: TransformerConfig
) -> tuple[torch.Tensor, torch.Tensor]:
    source = data.train_data if split == "train" else data.val_data
    if len(source) <= config.context_length:
        raise ValueError("split is too short for the configured context length")
    indexes = torch.randint(
        len(source) - config.context_length, (config.batch_size,)
    )
    x = torch.stack([
        source[index:index + config.context_length] for index in indexes
    ])
    y = torch.stack([
        source[index + 1:index + config.context_length + 1] for index in indexes
    ])
    return x.to(config.device), y.to(config.device)


@torch.no_grad()
def estimate_loss(
    model: torch.nn.Module, data: TrainingData, config: TransformerConfig
) -> dict[str, torch.Tensor]:
    result = {}
    was_training = model.training
    model.eval()
    for split in ("train", "valid"):
        losses = torch.zeros(config.eval_iters)
        for index in range(config.eval_iters):
            x, y = get_batch(data, split, config)
            _logits, loss = model(x, y)
            losses[index] = loss.item()
        result[split] = losses.mean()
    if was_training:
        model.train()
    return result


def save_checkpoint(model: torch.nn.Module, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
        torch.save(model.state_dict(), temporary)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def train_model(
    model: torch.nn.Module, data: TrainingData, config: TransformerConfig
) -> list[dict[str, torch.Tensor]]:
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    tracked_losses = []
    model.train()
    for step in range(config.max_iters):
        if step % config.eval_interval == 0 or step == config.max_iters - 1:
            losses = estimate_loss(model, data, config)
            tracked_losses.append(losses)
            print(
                f"Step: {step:5d} | Train: {losses['train'].item():.4f} | "
                f"Valid: {losses['valid'].item():.4f}"
            )
        x, y = get_batch(data, "train", config)
        _logits, loss = model(x, y)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()
    return tracked_losses
