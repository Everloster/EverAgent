"""开发者译解的最小客户端工具循环；默认不联网。

只实现同步、完整响应、客户端函数工具与客户端自管历史。
不实现 SSE、WebSocket steering、服务端工具、持久化或生产授权系统。
显式 --live 后才导入官方 SDK 并调用 API；凭据和模型从环境读取。
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from typing import Any


INSTRUCTIONS = "查询演示工单。只调用提供的只读工具，不编造状态；用中文简要答复。"
QUESTION = "请查询 DEMO-1 的当前状态和阻塞原因。"
PARAMETERS = {
    "type": "object",
    "properties": {"ticket_id": {"type": "string", "enum": ["DEMO-1"]}},
    "required": ["ticket_id"],
    "additionalProperties": False,
}
OPENAI_TOOLS = [{
    "type": "function", "name": "lookup_ticket", "description": "只读查询演示工单。",
    "parameters": PARAMETERS, "strict": True,
}]
ANTHROPIC_TOOLS = [{
    "name": "lookup_ticket", "description": "只读查询演示工单。", "input_schema": PARAMETERS,
}]


class ProtocolError(RuntimeError):
    """接口状态、输入关联或适配器支持范围不符合预期。"""


@dataclass(frozen=True)
class ToolReply:
    text: str
    is_error: bool


@dataclass(frozen=True)
class RunResult:
    answer: str
    model_requests: int
    tool_executions: int


class DemoExecutor:
    """封闭工具注册表 + 小范围手工校验 + 当前运行内的去重账本。

    仅处理固定演示数据。不解释模型生成的代码，不访问文件或业务系统。
    进程重启会丢失账本，因此它不是持久化幂等或 exactly-once 保证。
    """
    def __init__(self) -> None:
        self.executions = 0
        self._completed: dict[str, tuple[str, ToolReply]] = {}

    def call(self, call_id: str, name: str, arguments: Any) -> ToolReply:
        if not isinstance(call_id, str) or not call_id:
            raise ProtocolError("missing tool call id")
        fingerprint = json.dumps([name, arguments], ensure_ascii=False, sort_keys=True)
        old = self._completed.get(call_id)
        if old is not None:
            if old[0] != fingerprint:
                raise ProtocolError("same call id reused with different arguments")
            return old[1]
        valid = (
            name == "lookup_ticket"
            and isinstance(arguments, dict)
            and set(arguments) == {"ticket_id"}
            and arguments["ticket_id"] == "DEMO-1"
        )
        if not valid:
            body = {"ok": False, "error": "只允许 lookup_ticket(ticket_id='DEMO-1')"}
            reply = ToolReply(json.dumps(body, ensure_ascii=False), True)
        else:
            self.executions += 1
            body = {"ok": True, "ticket_id": "DEMO-1", "status": "blocked", "reason": "等待测试环境；合成数据"}
            reply = ToolReply(json.dumps(body, ensure_ascii=False), False)
        self._completed[call_id] = (fingerprint, reply)
        return reply


def run_openai(client: Any, model: str, *, max_steps: int = 4, executor: DemoExecutor | None = None) -> RunResult:
    """Responses：客户端保存全部 output items，不只保存 output_text。"""
    executor = executor or DemoExecutor()
    history: list[Any] = [{"role": "user", "content": QUESTION}]
    for step in range(1, max_steps + 1):
        response = client.responses.create(
            model=model, instructions=INSTRUCTIONS, input=list(history),
            tools=OPENAI_TOOLS, tool_choice="auto", parallel_tool_calls=False,
            max_output_tokens=4096, store=False, include=["reasoning.encrypted_content"],
        )
        if response.status != "completed":
            raise ProtocolError(f"response not completed: {response.status}")
        # 本例只声明 function 工具。遇到其他工具协议必须扩展处理器，不能静默执行。
        for item in response.output:
            if item.type not in {"message", "reasoning", "function_call"}:
                raise ProtocolError(f"unsupported output item: {item.type}")
            if item.type == "message" and any(c.type == "refusal" for c in item.content):
                raise ProtocolError("model refusal")
        history.extend(response.output)
        calls = [item for item in response.output if item.type == "function_call"]
        if not calls:
            if not response.output_text:
                raise ProtocolError("completed without a text answer or supported tool call")
            return RunResult(response.output_text, step, executor.executions)
        # 即使请求 parallel_tool_calls=False，仍遍历完整结果，不假定只有 output[0]。
        for call in calls:
            try:
                arguments = json.loads(call.arguments)
            except (TypeError, ValueError):
                arguments = None
            result = executor.call(call.call_id, call.name, arguments)
            history.append({
                "type": "function_call_output", "call_id": call.call_id, "output": result.text,
            })
    raise ProtocolError("application model-request budget exhausted")


def run_anthropic(client: Any, model: str, *, max_steps: int = 4, executor: DemoExecutor | None = None) -> RunResult:
    """Messages：保存完整 assistant 消息，所有工具结果放入一个 user 消息。"""
    executor = executor or DemoExecutor()
    history: list[Any] = [{"role": "user", "content": QUESTION}]
    for step in range(1, max_steps + 1):
        message = client.messages.create(
            model=model, max_tokens=4096, system=INSTRUCTIONS,
            messages=list(history), tools=ANTHROPIC_TOOLS,
        )
        # 当前官方 Python SDK 提供 to_param()，保留文本、thinking、签名等内容块。
        history.append(message.to_param())
        reason = message.stop_reason
        if reason not in {"tool_use", "end_turn"}:
            # 本例没启用服务端工具，pause_turn 也不擅自作为普通客户端工具处理。
            raise ProtocolError(f"message requires explicit handling: {reason}")
        for block in message.content:
            if block.type not in {"text", "thinking", "redacted_thinking", "tool_use"}:
                raise ProtocolError(f"unsupported content block: {block.type}")
        calls = [block for block in message.content if block.type == "tool_use"]
        if reason == "end_turn":
            if calls:
                raise ProtocolError("end_turn unexpectedly contains a client tool call")
            answer = "".join(block.text for block in message.content if block.type == "text")
            if not answer:
                raise ProtocolError("end_turn without a text answer")
            return RunResult(answer, step, executor.executions)
        if not calls:
            raise ProtocolError("tool_use without tool_use blocks")
        results = []
        for call in calls:
            result = executor.call(call.id, call.name, call.input)
            results.append({
                "type": "tool_result", "tool_use_id": call.id,
                "content": result.text, "is_error": result.is_error,
            })
        history.append({"role": "user", "content": results})
    raise ProtocolError("application model-request budget exhausted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", choices=("openai", "anthropic"), help="显式联网；会产生 API 用量")
    args = parser.parse_args()
    if args.live is None:
        print("未联网。离线检查：运行同目录 test_client_tool_loop.py；真实调用必须显式 --live。")
        return
    # 不接受密钥命令行参数，也不打印凭据。SDK 从执行设备环境解析。
    if args.live == "openai":
        from openai import OpenAI
        model = os.environ["OPENAI_MODEL"]
        with OpenAI(max_retries=0, timeout=45.0) as client:
            result = run_openai(client, model)
    else:
        from anthropic import Anthropic
        model = os.environ["ANTHROPIC_MODEL"]
        with Anthropic(max_retries=0, timeout=45.0) as client:
            result = run_anthropic(client, model)
    print(json.dumps(vars(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
