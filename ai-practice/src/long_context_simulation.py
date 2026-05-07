#!/usr/bin/env python3
"""Scaled simulation of long-context behavior across training, tuning, inference.

This script does not train a real 1M-token model. It keeps the same engineering
interfaces small enough to run locally:

1. pretraining: max_seq_len, position ids, full-attention cost
2. post-training: needle-in-a-haystack data and evidence recovery
3. inference: full-context vs retrieval packing and KV-cache cost
"""

from __future__ import annotations

import argparse
import math
import random
import time
from dataclasses import dataclass
from typing import Iterable


TOKEN_BYTES = 4
DEFAULT_1M = 1_048_576


@dataclass(frozen=True)
class ModelShape:
    layers: int = 24
    kv_heads: int = 8
    head_dim: int = 128
    bytes_per_value: int = 2


@dataclass(frozen=True)
class NeedleSample:
    tokens: list[str]
    question: str
    answer: str
    needle_index: int


def human_number(value: float) -> str:
    if value >= 1e12:
        return f"{value / 1e12:.2f}T"
    if value >= 1e9:
        return f"{value / 1e9:.2f}B"
    if value >= 1e6:
        return f"{value / 1e6:.2f}M"
    if value >= 1e3:
        return f"{value / 1e3:.2f}K"
    return f"{value:.0f}"


def mb(num_bytes: float) -> float:
    return num_bytes / (1024 * 1024)


def full_attention_cells(seq_len: int, heads: int) -> int:
    return seq_len * seq_len * heads


def causal_mask_cells(seq_len: int) -> int:
    return seq_len * seq_len


def kv_cache_bytes(seq_len: int, shape: ModelShape) -> int:
    return (
        2
        * seq_len
        * shape.layers
        * shape.kv_heads
        * shape.head_dim
        * shape.bytes_per_value
    )


def rope_angles(position: int, dim: int = 64, base: float = 10_000.0) -> list[float]:
    """Return RoPE phase angles for even dimensions at a given position."""
    return [position / (base ** (i / dim)) for i in range(0, dim, 2)]


def rope_phase_drift(short_len: int, long_len: int, dim: int = 64) -> float:
    """A small observable for why extrapolating positions changes Q/K geometry."""
    short = rope_angles(short_len, dim)
    long = rope_angles(long_len, dim)
    wrapped_diffs = []
    for a, b in zip(short, long):
        diff = abs((b - a + math.pi) % (2 * math.pi) - math.pi)
        wrapped_diffs.append(diff)
    return sum(wrapped_diffs) / len(wrapped_diffs)


def simulate_pretraining_window(seq_lens: Iterable[int], heads: int, shape: ModelShape) -> list[dict[str, str]]:
    rows = []
    baseline = min(seq_lens)
    for seq_len in seq_lens:
        attention = full_attention_cells(seq_len, heads)
        rows.append(
            {
                "seq_len": str(seq_len),
                "position_ids": f"0..{seq_len - 1}",
                "causal_mask_cells": human_number(causal_mask_cells(seq_len)),
                "attention_cells": human_number(attention),
                "vs_baseline_attention": f"{attention / full_attention_cells(baseline, heads):.1f}x",
                "kv_cache_mb": f"{mb(kv_cache_bytes(seq_len, shape)):.1f}",
                "rope_phase_drift": f"{rope_phase_drift(baseline, seq_len):.3f}",
            }
        )
    return rows


def make_haystack_vocab(size: int = 512) -> list[str]:
    return [f"filler_{i:03d}" for i in range(size)]


def build_needle_sample(context_len: int, needle_position: float, seed: int = 7) -> NeedleSample:
    random.seed(seed)
    vocab = make_haystack_vocab()
    tokens = [random.choice(vocab) for _ in range(context_len)]
    answer = f"blue-river-{seed}-{context_len}"
    needle = f"SECRET_KEY={answer}"
    needle_index = max(0, min(context_len - 1, int(context_len * needle_position)))
    tokens[needle_index] = needle
    return NeedleSample(
        tokens=tokens,
        question="What is the SECRET_KEY?",
        answer=answer,
        needle_index=needle_index,
    )


def full_context_answer(sample: NeedleSample) -> tuple[str | None, int]:
    inspected = 0
    for token in sample.tokens:
        inspected += 1
        if token.startswith("SECRET_KEY="):
            return token.split("=", 1)[1], inspected
    return None, inspected


def chunks(tokens: list[str], chunk_size: int) -> list[list[str]]:
    return [tokens[i : i + chunk_size] for i in range(0, len(tokens), chunk_size)]


def retrieve_chunks(question: str, token_chunks: list[list[str]], top_k: int) -> list[tuple[int, list[str], int]]:
    query_terms = set(question.replace("?", "").split())
    scored = []
    for idx, chunk in enumerate(token_chunks):
        score = sum(1 for token in chunk if "SECRET_KEY" in token)
        score += sum(1 for token in chunk if token in query_terms)
        scored.append((score, idx, chunk))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return [(idx, chunk, score) for score, idx, chunk in scored[:top_k]]


def rag_answer(sample: NeedleSample, chunk_size: int, top_k: int) -> tuple[str | None, int, list[int]]:
    token_chunks = chunks(sample.tokens, chunk_size)
    selected = retrieve_chunks(sample.question, token_chunks, top_k)
    inspected = 0
    selected_ids = []
    for chunk_id, chunk, _score in selected:
        selected_ids.append(chunk_id)
        for token in chunk:
            inspected += 1
            if token.startswith("SECRET_KEY="):
                return token.split("=", 1)[1], inspected, selected_ids
    return None, inspected, selected_ids


def estimate_prefill_decode(seq_len: int, new_tokens: int, heads: int, shape: ModelShape) -> dict[str, str]:
    return {
        "prompt_tokens": str(seq_len),
        "new_tokens": str(new_tokens),
        "prefill_attention_cells": human_number(full_attention_cells(seq_len, heads)),
        "decode_attention_cells": human_number(new_tokens * seq_len * heads),
        "kv_cache_mb": f"{mb(kv_cache_bytes(seq_len + new_tokens, shape)):.1f}",
    }


def print_table(title: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    headers = list(rows[0])
    widths = {h: max(len(h), *(len(row[h]) for row in rows)) for h in headers}
    print(f"\n== {title} ==")
    print(" | ".join(h.ljust(widths[h]) for h in headers))
    print("-+-".join("-" * widths[h] for h in headers))
    for row in rows:
        print(" | ".join(row[h].ljust(widths[h]) for h in headers))


def run(args: argparse.Namespace) -> None:
    shape = ModelShape(
        layers=args.layers,
        kv_heads=args.kv_heads,
        head_dim=args.head_dim,
        bytes_per_value=args.bytes_per_value,
    )
    seq_lens = list(dict.fromkeys([128, 512, 2048, args.context_len]))
    if args.include_1m:
        seq_lens.append(DEFAULT_1M)

    print_table(
        "pretraining: max_seq_len changes the training surface",
        simulate_pretraining_window(seq_lens, args.heads, shape),
    )

    sample = build_needle_sample(args.context_len, args.needle_position, args.seed)
    start = time.perf_counter()
    full_answer, full_inspected = full_context_answer(sample)
    full_ms = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    retrieved_answer, rag_inspected, selected_ids = rag_answer(sample, args.chunk_size, args.top_k)
    rag_ms = (time.perf_counter() - start) * 1000

    print_table(
        "post-training: needle task as long-context supervision",
        [
            {
                "context_len": str(args.context_len),
                "needle_index": str(sample.needle_index),
                "needle_position": f"{sample.needle_index / args.context_len:.2%}",
                "answer": sample.answer,
            }
        ],
    )

    print_table(
        "inference: full-context scan vs retrieval packing",
        [
            {
                "mode": "full_context",
                "answer_ok": str(full_answer == sample.answer),
                "tokens_inspected": str(full_inspected),
                "selected_chunks": "all",
                "latency_ms": f"{full_ms:.3f}",
            },
            {
                "mode": "rag_top_k",
                "answer_ok": str(retrieved_answer == sample.answer),
                "tokens_inspected": str(rag_inspected),
                "selected_chunks": ",".join(str(i) for i in selected_ids),
                "latency_ms": f"{rag_ms:.3f}",
            },
        ],
    )

    print_table(
        "inference: prefill/decode/KV-cache cost model",
        [estimate_prefill_decode(args.context_len, args.new_tokens, args.heads, shape)],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Long-context 1M scaled simulation")
    parser.add_argument("--context-len", type=int, default=4096)
    parser.add_argument("--needle-position", type=float, default=0.73)
    parser.add_argument("--chunk-size", type=int, default=256)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--new-tokens", type=int, default=128)
    parser.add_argument("--heads", type=int, default=8)
    parser.add_argument("--layers", type=int, default=24)
    parser.add_argument("--kv-heads", type=int, default=8)
    parser.add_argument("--head-dim", type=int, default=128)
    parser.add_argument("--bytes-per-value", type=int, default=2)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--include-1m", action="store_true")
    return parser


if __name__ == "__main__":
    run(build_parser().parse_args())
