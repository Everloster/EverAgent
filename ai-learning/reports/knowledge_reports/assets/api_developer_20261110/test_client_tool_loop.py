"""使用可注入的 Fake Client 检查示例控制流；不导入供应商 SDK，不访问网络。"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace as Obj
import unittest


# 只加载同目录、随本报告编写的示例文件；不加载下载的第三方源码。
module_path = Path(__file__).with_name("client_tool_loop.py")
spec = importlib.util.spec_from_file_location("report_client_tool_loop", module_path)
assert spec and spec.loader
lab = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lab
spec.loader.exec_module(lab)


class FakeEndpoint:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.requests = []

    def create(self, **request):
        self.requests.append(copy.deepcopy(request))
        return next(self.replies)


def client(kind, replies):
    endpoint = FakeEndpoint(replies)
    return Obj(**{kind: endpoint}), endpoint


def openai_call(call_id="call_1", *, arguments='{"ticket_id":"DEMO-1"}', name="lookup_ticket"):
    return Obj(type="function_call", call_id=call_id, name=name, arguments=arguments)


def openai_response(*items, status="completed", text=""):
    return Obj(status=status, output=list(items), output_text=text)


def openai_answer(text="工单被测试环境阻塞。"):
    return openai_response(Obj(type="message", content=[Obj(type="output_text", text=text)]), text=text)


class FakeMessage:
    def __init__(self, reason, *content):
        self.stop_reason = reason
        self.content = list(content)

    def to_param(self):
        return {"role": "assistant", "content": list(self.content)}


def anthropic_call(call_id="toolu_1", *, arguments=None, name="lookup_ticket"):
    return Obj(type="tool_use", id=call_id, name=name, input=arguments if arguments is not None else {"ticket_id": "DEMO-1"})


def anthropic_answer():
    return FakeMessage("end_turn", Obj(type="text", text="工单被测试环境阻塞。"))


class LoopTests(unittest.TestCase):
    def test_openai_round_trip_preserves_reasoning_and_instructions(self):
        reasoning = Obj(type="reasoning", encrypted_content="opaque-demo-state")
        c, endpoint = client("responses", [openai_response(reasoning, openai_call()), openai_answer()])
        result = lab.run_openai(c, "test-model")
        self.assertEqual((result.model_requests, result.tool_executions), (2, 1))
        second = endpoint.requests[1]
        self.assertEqual(second["input"][1].encrypted_content, "opaque-demo-state")
        self.assertEqual(second["input"][-1]["call_id"], "call_1")
        self.assertEqual(second["instructions"], lab.INSTRUCTIONS)
        self.assertFalse(second["store"])
        self.assertEqual(len(endpoint.requests[0]["input"]), 1)

    def test_openai_multiple_call_ids_are_paired(self):
        c, endpoint = client("responses", [openai_response(openai_call("a"), openai_call("b")), openai_answer()])
        result = lab.run_openai(c, "test-model")
        outputs = [i for i in endpoint.requests[1]["input"] if isinstance(i, dict) and i.get("type") == "function_call_output"]
        self.assertEqual([i["call_id"] for i in outputs], ["a", "b"])
        self.assertEqual(result.tool_executions, 2)

    def test_openai_malformed_arguments_return_error_without_execution(self):
        c, endpoint = client("responses", [openai_response(openai_call(arguments="{")), openai_answer()])
        result = lab.run_openai(c, "test-model")
        payload = json.loads(endpoint.requests[1]["input"][-1]["output"])
        self.assertFalse(payload["ok"])
        self.assertEqual(result.tool_executions, 0)

    def test_openai_incomplete_does_not_execute_tool(self):
        executor = lab.DemoExecutor()
        c, _ = client("responses", [openai_response(openai_call(), status="incomplete")])
        with self.assertRaises(lab.ProtocolError):
            lab.run_openai(c, "test-model", executor=executor)
        self.assertEqual(executor.executions, 0)

    def test_openai_refusal_not_mistaken_for_answer(self):
        c, _ = client("responses", [openai_response(Obj(type="message", content=[Obj(type="refusal", refusal="no")]))])
        with self.assertRaisesRegex(lab.ProtocolError, "refusal"):
            lab.run_openai(c, "test-model")

    def test_openai_unknown_tool_protocol_fails_closed(self):
        c, _ = client("responses", [openai_response(Obj(type="web_search_call"))])
        with self.assertRaisesRegex(lab.ProtocolError, "unsupported"):
            lab.run_openai(c, "test-model")

    def test_anthropic_round_trip_preserves_signed_content(self):
        thinking = Obj(type="thinking", thinking="", signature="opaque-demo-signature")
        c, endpoint = client("messages", [FakeMessage("tool_use", thinking, anthropic_call()), anthropic_answer()])
        result = lab.run_anthropic(c, "test-model")
        messages = endpoint.requests[1]["messages"]
        self.assertEqual(messages[1]["content"][0].signature, "opaque-demo-signature")
        self.assertEqual(messages[2]["role"], "user")
        self.assertEqual(messages[2]["content"][0]["tool_use_id"], "toolu_1")
        self.assertEqual((result.model_requests, result.tool_executions), (2, 1))

    def test_anthropic_parallel_results_share_one_user_message(self):
        c, endpoint = client("messages", [FakeMessage("tool_use", anthropic_call("a"), anthropic_call("b")), anthropic_answer()])
        lab.run_anthropic(c, "test-model")
        messages = endpoint.requests[1]["messages"]
        self.assertEqual(len(messages), 3)
        self.assertEqual([b["tool_use_id"] for b in messages[-1]["content"]], ["a", "b"])

    def test_anthropic_invalid_arguments_mark_is_error(self):
        c, endpoint = client("messages", [FakeMessage("tool_use", anthropic_call(arguments={"ticket_id": "private"})), anthropic_answer()])
        result = lab.run_anthropic(c, "test-model")
        self.assertTrue(endpoint.requests[1]["messages"][-1]["content"][0]["is_error"])
        self.assertEqual(result.tool_executions, 0)

    def test_anthropic_stop_reasons_are_not_generic_success(self):
        for reason in ("max_tokens", "pause_turn", "refusal", "model_context_window_exceeded", "stop_sequence", None):
            with self.subTest(reason=reason):
                c, _ = client("messages", [FakeMessage(reason)])
                with self.assertRaises(lab.ProtocolError):
                    lab.run_anthropic(c, "test-model")

    def test_anthropic_tool_use_requires_call_blocks(self):
        c, _ = client("messages", [FakeMessage("tool_use")])
        with self.assertRaisesRegex(lab.ProtocolError, "without tool_use"):
            lab.run_anthropic(c, "test-model")

    def test_anthropic_end_turn_cannot_dispatch_tool(self):
        executor = lab.DemoExecutor()
        c, _ = client("messages", [FakeMessage("end_turn", anthropic_call())])
        with self.assertRaises(lab.ProtocolError):
            lab.run_anthropic(c, "test-model", executor=executor)
        self.assertEqual(executor.executions, 0)

    def test_duplicate_call_id_uses_memory_ledger(self):
        executor = lab.DemoExecutor()
        first = executor.call("id", "lookup_ticket", {"ticket_id": "DEMO-1"})
        second = executor.call("id", "lookup_ticket", {"ticket_id": "DEMO-1"})
        self.assertEqual(first, second)
        self.assertEqual(executor.executions, 1)

    def test_reused_call_id_with_changed_arguments_rejected(self):
        executor = lab.DemoExecutor()
        executor.call("id", "lookup_ticket", {"ticket_id": "DEMO-1"})
        with self.assertRaises(lab.ProtocolError):
            executor.call("id", "lookup_ticket", {"ticket_id": "other"})
        self.assertEqual(executor.executions, 1)

    def test_unknown_tool_never_executes(self):
        executor = lab.DemoExecutor()
        self.assertTrue(executor.call("id", "shell", {"command": "anything"}).is_error)
        self.assertEqual(executor.executions, 0)

    def test_model_request_budget_stops_loop(self):
        c, endpoint = client("responses", [openai_response(openai_call())])
        with self.assertRaisesRegex(lab.ProtocolError, "budget"):
            lab.run_openai(c, "test-model", max_steps=1)
        self.assertEqual(len(endpoint.requests), 1)

    def test_missing_call_id_rejected(self):
        with self.assertRaises(lab.ProtocolError):
            lab.DemoExecutor().call("", "lookup_ticket", {"ticket_id": "DEMO-1"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LoopTests))
    summary = {
        "kind": "offline-sdk-shaped-client-loop-tests",
        "scope": "Fake Client 控制流测试；不导入真实 SDK、不请求 API、不验证实际模型行为",
        "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors), "passed": result.wasSuccessful(),
    }
    text = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as out:
            out.write(text)
    print(text)
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
