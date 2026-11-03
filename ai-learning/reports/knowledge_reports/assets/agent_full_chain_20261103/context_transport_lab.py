#!/usr/bin/env python3
"""Synthetic paperwork demo: transmitted JSON is not the logical context.

No model, tokenizer, network, or real sales data is used. This is not an
implementation or benchmark of Anthropic Message Threads. It only checks
that an application can reconstruct the same conversation from a stored
prefix plus a delta, and can replay its own copy after losing that prefix.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path


def encode(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def run() -> dict[str, object]:
    system = "你是销量分析助手。只使用工具中的数据；缺失就说明，不猜数字。"
    tools = [{
        "name": "get_sales",
        "description": "查询指定城市和月份的销量。仅用于合成数据演示。",
        "input_schema": {
            "type": "object",
            "properties": {"city": {"type": "string"}, "month": {"type": "string"}},
            "required": ["city", "month"],
        },
    }]
    # Repeated text stands in for a verbose tool return. Its length is chosen
    # for visibility, not measured from a real application or sales database.
    tool_result = {
        "units": 12000,
        "unit": "台",
        "synthetic": True,
        "coverage": "同一组虚构门店",
        "detail": "这是合成的销量明细说明，不是真实数据。" * 2000,
    }
    history = [
        {"role": "user", "content": "查一下2026年6月杭州空调销量。"},
        {"role": "assistant", "content": [{
            "type": "tool_use", "id": "toolu_demo_june", "name": "get_sales",
            "input": {"city": "杭州", "month": "2026-06"},
        }]},
        {"role": "user", "content": [{
            "type": "tool_result", "tool_use_id": "toolu_demo_june",
            "content": encode(tool_result).decode("utf-8"),
        }]},
        {"role": "assistant", "content": "合成数据中，6月销量为12000台。"},
    ]
    new_messages = [{"role": "user", "content": "那和5月相比呢？"}]
    fixed = {"model": "claude-opus-5-5", "max_tokens": 1024}
    full = {**fixed, "system": system, "tools": tools, "messages": history + new_messages}
    delta = {
        **fixed,
        "thread": {"type": "continue", "previous_message_id": "msg_demo_previous"},
        "messages": new_messages,
    }

    stored_prefix = {"system": system, "tools": tools, "messages": copy.deepcopy(history)}
    reconstructed = {
        **fixed,
        "system": stored_prefix["system"],
        "tools": stored_prefix["tools"],
        "messages": stored_prefix["messages"] + delta["messages"],
    }
    assert encode(reconstructed) == encode(full)
    assert len(encode(delta)) < len(encode(full))

    # A missing thread does not authorize re-running a sales query. This toy
    # replay reconstructs messages from the application's copy; it runs no tool.
    replay = {**fixed, "system": system, "tools": tools,
              "messages": copy.deepcopy(history + new_messages), "thread": {"type": "create"}}
    assert encode(replay["messages"]) == encode(full["messages"])

    return {
        "experiment": "synthetic JSON transport versus logical conversation",
        "synthetic_data": True,
        "model_called": False,
        "tokenizer_used": False,
        "network_used": False,
        "serialization": "UTF-8 JSON, ensure_ascii=False, compact separators",
        "full_request_bytes": len(encode(full)),
        "thread_continue_request_bytes": len(encode(delta)),
        "full_request_message_count": len(full["messages"]),
        "thread_continue_message_count": len(delta["messages"]),
        "reconstructed_message_count": len(reconstructed["messages"]),
        "logical_request_identical": True,
        "logical_request_sha256": hashlib.sha256(encode(full)).hexdigest(),
        "expired_thread_replay_messages_identical": True,
        "checks_passed": 3,
        "limitations": [
            "Does not measure tokens, billing, TTFT, model quality, or API behavior.",
            "Byte counts depend on the chosen synthetic history and serialization.",
            "Does not implement thread expiry, durable task recovery, or tool idempotency.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Write JSON to a new file; refuse overwrite")
    args = parser.parse_args()
    output = json.dumps(run(), ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(output)
    print(output, end="")


if __name__ == "__main__":
    main()
