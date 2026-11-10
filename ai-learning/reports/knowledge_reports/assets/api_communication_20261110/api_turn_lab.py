"""离线教学模型：输入快照、Harness 队列与服务端 steering 交接。

不调用模型、不访问网络、不执行工具。它不是 Codex 或供应商服务端实现。
报文只验证本文关心的关系，不是完整官方 Schema 验证器。
运行：python3 -I <本文件> --output <结果.json>
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import unittest


FIRST = "定位并修复这个测试失败。"
UPDATE = "先只读分析，不要修改文件。"
EXTRA = "结论用中文解释。"
CALL_ID = "call_demo_read"
SCHEMA = {
    "type": "object",
    "properties": {"path": {"type": "string"}},
    "required": ["path"],
    "additionalProperties": False,
}
RESULT = "合成工具结果：测试期望空列表，实际返回 null。"


def user(text: str) -> dict:
    return {"role": "user", "content": text}


def fixtures() -> dict:
    """生成 Responses 和 Messages 两组示意报文；模型 ID 是占位符。"""
    tool = {"name": "read_test", "description": "只读指定的测试文件。"}
    openai_call = {
        "type": "function_call", "id": "fc_demo_read", "call_id": CALL_ID,
        "name": tool["name"], "arguments": json.dumps({"path": "tests/demo.py"}),
    }
    openai_result = {"type": "function_call_output", "call_id": CALL_ID, "output": RESULT}
    openai_first = {
        "model": "<OPENAI_MODEL_ID>", "instructions": "你是代码助手。遵守用户授权。",
        "input": [user(FIRST)],
        "tools": [{"type": "function", **tool, "parameters": SCHEMA, "strict": True}],
        "stream": True,
    }
    openai_next = copy.deepcopy(openai_first)
    openai_next["input"].extend([openai_call, openai_result, user(UPDATE)])
    anthropic_call = {
        "type": "tool_use", "id": "toolu_demo_read", "name": tool["name"],
        "input": {"path": "tests/demo.py"},
    }
    anthropic_result = {
        "type": "tool_result", "tool_use_id": anthropic_call["id"], "content": RESULT,
    }
    anthropic_first = {
        "model": "<CLAUDE_MODEL_ID>", "max_tokens": 1024,
        "system": "你是代码助手。遵守用户授权。", "messages": [user(FIRST)],
        "tools": [{**tool, "input_schema": SCHEMA}], "stream": True,
    }
    anthropic_next = copy.deepcopy(anthropic_first)
    anthropic_next["messages"].extend([
        {"role": "assistant", "content": [anthropic_call]},
        {"role": "user", "content": [anthropic_result, {"type": "text", "text": UPDATE}]},
    ])
    return {
        "openai": {"request_1": openai_first, "request_2": openai_next},
        "anthropic": {"request_1": anthropic_first, "request_2": anthropic_next},
    }


class HarnessQueue:
    """仅模拟不抢占路径的一个采样边界；不包含完整 Agent 循环。"""
    def __init__(self) -> None:
        self.turn_id = "turn_demo"
        self.history = [user(FIRST)]
        self.pending: list[dict] = []

    def snapshot(self) -> list[dict]:
        return copy.deepcopy(self.history)

    def steer(self, text: str, expected_turn_id: str) -> dict:
        if expected_turn_id != self.turn_id:
            raise ValueError("expected turn mismatch")
        self.pending.append(user(text))
        return {"turnId": self.turn_id}

    def next_boundary(self) -> list[dict]:
        protocol = fixtures()["openai"]["request_2"]["input"]
        self.history.extend(copy.deepcopy(protocol[1:3]))
        self.history.extend(self.pending)
        self.pending = []
        return self.snapshot()


class ServerSteerModel:
    """手写状态机，仅演示 accepted → pending/continuation，不模拟推理。"""
    def __init__(self) -> None:
        self.pending: list[str] = []
        self.required_call: str | None = None
        self.successor: dict | None = None

    def accept(self, text: str) -> dict:
        self.pending.append(text)
        return {"type": "response.steer.accepted", "queued": True}

    def finish_boundary(self, requires_tool: bool) -> dict:
        if requires_tool:
            self.required_call = CALL_ID
            return {
                "type": "response.steer.pending",
                "required_input": [{"type": "function_call_output", "call_id": CALL_ID}],
            }
        return self._continue([])

    def return_tool(self, call_id: str, result: str) -> dict:
        if self.required_call is None or call_id != self.required_call:
            raise ValueError("missing or mismatched required tool")
        self.required_call = None
        return self._continue([{"type": "function_call_output", "call_id": call_id, "output": result}])

    def _continue(self, explicit_input: list[dict]) -> dict:
        self.successor = {
            "type": "response.created", "id": "resp_demo_successor",
            "logical_new_input": [user(t) for t in self.pending] + copy.deepcopy(explicit_input),
        }
        self.pending = []
        return self.successor

    def disconnect(self) -> None:
        self.pending = []
        self.required_call = None


class ContractTests(unittest.TestCase):
    def test_acceptance_does_not_mutate_inflight_snapshot(self):
        q = HarnessQueue()
        sent = q.snapshot()
        q.steer(UPDATE, q.turn_id)
        self.assertEqual(sent, [user(FIRST)])
        self.assertNotIn(user(UPDATE), q.history)

    def test_same_turn_contains_all_updates_in_order(self):
        q = HarnessQueue()
        for text in (UPDATE, EXTRA):
            self.assertEqual(q.steer(text, q.turn_id), {"turnId": "turn_demo"})
        following = q.next_boundary()
        self.assertEqual([i["content"] for i in following if i.get("role") == "user"], [FIRST, UPDATE, EXTRA])
        self.assertEqual(q.pending, [])

    def test_stale_turn_rejected_without_queue_change(self):
        q = HarnessQueue()
        with self.assertRaises(ValueError):
            q.steer(UPDATE, "old_turn")
        self.assertEqual(q.pending, [])

    def test_tool_output_recorded_once_at_boundary(self):
        q = HarnessQueue()
        q.steer(UPDATE, q.turn_id)
        following = q.next_boundary()
        self.assertEqual(sum(i.get("type") == "function_call_output" for i in following), 1)
        self.assertEqual(following[1]["call_id"], following[2]["call_id"])

    def test_responses_arguments_are_json_string(self):
        call = fixtures()["openai"]["request_2"]["input"][1]
        self.assertIsInstance(call["arguments"], str)
        self.assertEqual(json.loads(call["arguments"]), {"path": "tests/demo.py"})

    def test_messages_tool_result_precedes_new_text(self):
        messages = fixtures()["anthropic"]["request_2"]["messages"]
        self.assertEqual(messages[-2]["role"], "assistant")
        self.assertEqual(messages[-1]["role"], "user")
        self.assertEqual(messages[-1]["content"][0]["tool_use_id"], messages[-2]["content"][0]["id"])
        self.assertEqual(messages[-1]["content"][1], {"type": "text", "text": UPDATE})

    def test_native_acceptance_is_not_a_successor(self):
        server = ServerSteerModel()
        self.assertEqual(server.accept(UPDATE)["type"], "response.steer.accepted")
        self.assertIsNone(server.successor)

    def test_native_tool_wait_does_not_drop_accepted_input(self):
        server = ServerSteerModel()
        server.accept(UPDATE)
        self.assertEqual(server.finish_boundary(True)["type"], "response.steer.pending")
        self.assertEqual(server.pending, [UPDATE])
        self.assertIsNone(server.successor)

    def test_native_continuation_prepends_updates_once(self):
        server = ServerSteerModel()
        server.accept(UPDATE)
        server.accept(EXTRA)
        server.finish_boundary(True)
        result = server.return_tool(CALL_ID, RESULT)["logical_new_input"]
        self.assertEqual(result[:2], [user(UPDATE), user(EXTRA)])
        self.assertEqual(result[2]["type"], "function_call_output")
        self.assertEqual(server.pending, [])

    def test_native_wrong_result_does_not_consume_queue(self):
        server = ServerSteerModel()
        server.accept(UPDATE)
        server.finish_boundary(True)
        with self.assertRaises(ValueError):
            server.return_tool("wrong_call", RESULT)
        self.assertEqual(server.pending, [UPDATE])

    def test_native_no_tool_can_continue_at_boundary(self):
        server = ServerSteerModel()
        server.accept(UPDATE)
        self.assertEqual(server.finish_boundary(False)["logical_new_input"], [user(UPDATE)])

    def test_native_disconnect_requires_application_copy(self):
        server = ServerSteerModel()
        local_copy = [UPDATE]
        server.accept(UPDATE)
        server.disconnect()
        self.assertEqual(server.pending, [])
        self.assertEqual(local_copy, [UPDATE])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ContractTests))
    q = HarnessQueue()
    first_snapshot = q.snapshot()
    q.steer(UPDATE, q.turn_id)
    q.steer(EXTRA, q.turn_id)
    server = ServerSteerModel()
    native_trace = [server.accept(UPDATE), server.finish_boundary(True), server.return_tool(CALL_ID, RESULT)]
    report = {
        "kind": "offline-teaching-contract-lab",
        "scope": "手写状态机与合成报文；没有真实模型、网络、工具执行或供应商 Schema 验证",
        "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "passed": result.wasSuccessful(),
        "harness": {"inflight_snapshot": first_snapshot, "next_request_input": q.next_boundary()},
        "native_steering_trace": native_trace,
        "payload_examples": fixtures(),
    }
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        # 不覆盖已有结果；重新实验时使用新文件名。
        with args.output.open("x", encoding="utf-8") as output:
            output.write(text)
    print(text)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
