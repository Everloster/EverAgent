---
title: "从 SDK 调用到 Agent 执行循环——OpenAI、Anthropic API 开发者中文译解"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-11"
semantic_tags: ["api_protocol", "developer_guide", "responses_api", "messages_api", "tool_use", "streaming", "steering", "sdk", "error_handling"]
---

# 从 SDK 调用到 Agent 执行循环

## OpenAI、Anthropic API 开发者中文译解

> **适合谁**：会读 Python、JSON 和 HTTP，希望自己接入模型、实现工具循环或维护 Agent Harness 的开发者。
>
> **与专题报告的分工**：[《运行中追加消息与修改目标》](./OpenAI与Anthropic_API通信与运行中追加消息_技术研究_20261110.md)对照 OpenAI Responses、Claude Messages 和 Managed Agents 的官方 API，解释更新何时进入、何时生效；本篇展开 SDK 调用与客户端工具循环。
>
> **译解范围**：OpenAI Responses、Anthropic Messages 的核心调用契约，兼顾 Chat Completions 的迁移差异；覆盖客户端工具、流式响应、历史续接、运行中追加与错误处理。不是两家整个文档站的逐页全文翻译，也不覆盖所有模型参数、云厂商变体和服务端工具。
>
> **证据与验证**：核心调用文档及 SDK 源码核验于 2026-11-10；2026-11-11 重新核对运行中追加的官方文档并修订第 8 节。初稿部分参考页面读取失败，字段语义改由固定版本的官方 SDK 类型定义核对。附带 Python 示例完成 **17 项离线 Fake Client 测试**；没有安装或实调供应商 SDK，没有调用真实模型，不把模拟通过写成线上兼容性认证。

## 1. 先翻译几个容易写错代码的术语

本文的“契约译解”是对官方字段说明的中文整理，紧跟其工程含义；“实现建议”则是本文的设计判断，不冒充供应商强制要求。

| 文档用语 | 建议理解 | 不应混为一谈 |
|---|---|---|
| request | 一次向服务端提交的请求 | 一项完整用户任务 |
| response / message | 服务端返回的一次生成对象 | 最终给用户的完整答案 |
| output item / content block | 有类型的输出单元 | 一段普通字符串 |
| tool call | 模型提出的结构化行动申请 | 工具已经执行 |
| tool output / tool result | 执行结果，关联到某次调用 | 一条任意补充聊天消息 |
| stream | 随时间到达的事件序列 | 一串天然完整的 JSON 对象，或双向输入接口 |
| continuation | 基于已有上下文的后继调用 | 无条件延续同一次内部生成 |
| accepted | 某一层已接受请求或输入 | 模型已经应用它，或者业务已经完成 |
| completed | 这个 API 对象完成 | 整项 Agent 工作完成 |

**工程上的第一条规则：显示文本、保存协议状态、执行外部动作，需要三套不同的处理逻辑。** 只写 `print(response.output_text)` 可以做聊天演示，不能代替 Agent 运行时。

## 2. 一行 SDK 调用，下面究竟发生什么

### 2.1 SDK 不是模型，也不自动成为完整 Agent

开发者通常调用：

```python
response = openai_client.responses.create(**request)
message = anthropic_client.messages.create(**request)
```

两家的官方 Python SDK 都将参数组织成请求体，交给 HTTP 客户端，再把响应解析成对象或事件流。固定快照中：

- OpenAI `responses.create()` 构造 body，调用内部 `_post("/responses", ...)`；结合常规 API base URL，对应 `POST /v1/responses`。
- Anthropic `messages.create()` 构造 body，调用内部 `_post("/v1/messages", ...)`；响应目标类型为 `Message`，流式时改为事件流。
- Anthropic `messages.stream()` 同样发送 Messages 请求，但固定 `stream: true`，返回负责累积消息的 stream manager。[^sdk-wire]

这是**源码阅读路径**，不是让应用依赖 `_post` 等私有方法。应用应使用公开 SDK 方法。

客户端工具的执行循环通常仍属于应用：SDK 把 `tool_use` 或 `function_call` 交给你，不代表它已经执行了你的 Python 函数。某些 SDK 另有 tool runner，可代管循环；“有 runner”也不等于权限、业务幂等和最终交付检查自动解决。[^tools-o][^tools-a]

### 2.2 认证和协议版本交给 SDK，不要复制过期模板

**契约译解：认证数据属于传输层配置，不是 prompt 内容。**

在本文固定的 OpenAI Python SDK 中，普通 API-key 路径生成 `Authorization: Bearer ...`。Anthropic 的同类路径在本次 SDK 快照中也生成 Bearer 头，并附带 `anthropic-version`；其常量值是 `2026-10-21`。这些是**所读版本的实现事实**，不是永远不变的标准，也不是对旧 `x-api-key` 方案兼容性的全面判断。[^auth]

所以示例采用：

```python
from openai import OpenAI
from anthropic import Anthropic

openai_client = OpenAI(max_retries=0, timeout=45.0)
anthropic_client = Anthropic(max_retries=0, timeout=45.0)
```

SDK 从本地环境解析对应的凭据。示例中的重试次数与超时是为了暴露失败、约束实验而设置的**应用配置**，不是厂商推荐的通用生产数值。

实现时应避免：

- 将密钥放进消息、代码仓库、URL 或报错日志；
- 为排查一个参数问题，先把整份私人请求体上传给第三方；
- 把 SDK 版本、API 版本头、模型 ID 当成同一件事。

模型能力也不能仅凭 SDK 字段是否存在来推断：通用客户端可能暴露一个参数，但某个模型或托管平台仍可能不支持它。

## 3. OpenAI Responses：参数说明的中文译解

### 3.1 输入、控制与状态字段

下面不是完整参数表，而是会直接改变执行逻辑的部分。来源为官方 SDK 的 `ResponseCreateParamsBase`。[^params-o]

| 字段 | 契约译解 | 对实现的影响 |
|---|---|---|
| `model` | 指定生成响应的模型 | 与账号可用性、能力范围分别核对，不从模型名猜所有功能 |
| `input` | 本次输入，可以是文本或有类型的输入条目 | 不只包含 user 文本，也可能包含先前输出、工具结果等 |
| `instructions` | 注入本次上下文的 system/developer 指令 | 与 `previous_response_id` 一起使用时，前一次的 `instructions` **不会自动带入** |
| `tools` | 本次允许模型调用的工具定义 | 自定义 function、托管工具、MCP 等并不是同一执行方式 |
| `tool_choice` | 控制模型怎样选择工具 | 控制选择，不取代实际执行器和授权检查 |
| `parallel_tool_calls` | 是否允许模型并行提出工具调用 | 不代表应用可以把任意有依赖或有冲突的操作并发执行 |
| `max_output_tokens` | 本次响应输出 token 的上限，包括可见输出和 reasoning tokens | 不是“最多显示多少字”，也不是整个 Agent 任务总预算 |
| `max_tool_calls` | 本次响应内置工具调用总数上限 | 不应当作你本地任意函数执行次数的统一限额 |
| `previous_response_id` | 以前一个 response 为上下文续接点 | 不能与 `conversation` 同时使用 |
| `conversation` | 从指定 conversation 取上下文，完成后自动追加输入与输出条目 | 这是服务端状态容器，不是一个任意可互换的 request ID |
| `store` | 是否保存响应供以后通过 API 检索 | `false` 不是“完全没有上下文”，也不等于全部数据处理环节都无保留 |
| `stream` | 用事件流交付响应 | 改变读取方式，不消除终态判断 |
| `truncation` | 超过窗口时的处理策略 | `disabled` 默认报错；`auto` 可移除开头条目以适配窗口，不是自动生成摘要 |

这里最值得划线的一条：

> **普通显式 Responses 续接：`previous_response_id` 延续上下文，不替你自动继承上一请求的 `instructions`。**

一个比较稳妥的写法是把应用的稳定请求配置集中维护，每次显式调用都带上，而不是依赖误解出来的隐式继承：

```python
common = {
    "model": model,
    "instructions": "只查询演示工单，按授权执行工具。",
    "tools": tools,
    "max_output_tokens": 4096,
}

first = client.responses.create(
    **common,
    input="查询 DEMO-1。",
)

# 前提：first 的状态允许续接，且它不在等待你尚未返回的工具结果。
second = client.responses.create(
    **common,
    previous_response_id=first.id,
    input="把刚才的结论改写得更简洁。",
)
```

这段只是**普通显式续接**示例，不可套到所有路径。OpenAI 原生 steering 的**自动后继响应**会继承原请求设置；Anthropic Threads continue 又要求省略此前保存的 `system` 和 `tools`。三者的契约不同，见 §7。

### 3.2 返回对象：不能假定 `output[0]` 是答案

官方 `Response` 类型明确提醒：`output` 的长度和顺序由响应决定，不应假定第一项就是包含答案的 assistant message。SDK 的 `output_text` 只是便利属性：它遍历 message 内的 `output_text` 内容并拼接；没有这些内容时返回空字符串。[^response-o]

例如，一个响应可以在概念上包含：

```text
output[0]  reasoning
output[1]  function_call
output[2]  message
```

因此：

- **展示层**可以使用 `output_text`；
- **历史层**需要保存后续请求所要求的完整输出条目；
- **执行层**需要遍历并识别所有支持的 tool call；
- **状态层**需要检查 `status`、`error` 和 `incomplete_details`。

`status` 包括 `completed`、`failed`、`in_progress`、`cancelled`、`queued`、`incomplete`。得到 `completed` 但 output 中有客户端函数调用时，通常意味着轮到应用执行工具，不意味着整个任务结束。[^response-o][^tools-o]

### 3.3 `reasoning`、`include` 与历史保留

`reasoning` 控制适用模型的推理相关设置；`include: ["reasoning.encrypted_content"]` 请求返回可供无状态续接使用的加密 reasoning 内容。官方类型说明将 `store: false` 和 ZDR 场景列为用途。[^params-o]

这里的工程原则是：**把 opaque 状态作为不透明数据保留，不自行解释、编辑或伪造它。** 可见推理摘要不是完整内部状态，也不能自动替代对应的续接条目。

附带示例采用客户端自管历史，并保留整个 `response.output`。这是为了说明运行机制，不意味着把所有历史永远无限堆积就是生产上最好的方案。

## 4. Anthropic Messages：参数与内容块的中文译解

### 4.1 必填字段与关键语义

官方 `MessageCreateParamsBase` 将 `model`、`messages`、`max_tokens` 标为必填。[^params-a]

| 字段 | 契约译解 | 对实现的影响 |
|---|---|---|
| `model` | 选择响应模型 | 能力与版本需明确，不能把所有 Claude 视为同一参数集合 |
| `messages` | 先前对话与本次输入 | 每条消息有 role/content；内容可为文本或内容块 |
| `max_tokens` | 本次生成 token 的上限，模型可能提前停止 | thinking token 也占该上限；不是用户任务的总 token 配额 |
| `system` | 顶层系统指令 | 常驻应用规则通常放这里；新中途 system 消息有单独的位置规则 |
| `tools` | 模型可使用的工具定义 | 客户端工具使用 `name`、`description`、`input_schema` |
| `tool_choice` | 自动选择、指定工具、任意工具或不用工具 | 不同 thinking 模式可能有限制，不能机械复制其他供应商取值 |
| `thinking` | 配置思考行为 | `adaptive` 与手工预算等支持范围按模型不同；不是通用字符串互换 |
| `output_config` | 输出配置，例如结构化输出格式 | 与工具参数的 `input_schema` 是不同方向的约束 |
| `cache_control` | 请求缓存控制 | 缓存不是会话存储，也不表示“模型已记住且以后不用给上下文” |
| `stream` | 增量交付响应 | 原始 create 流与提供累积帮助的 `messages.stream()` 要区分 |

`messages` 中连续的 user 或 assistant 消息会按接口规则合并为一个 turn。这里的 turn 是 Messages 协议的概念，不应直接对应 UI 气泡数或 Codex Agent turn。某些模型允许 assistant prefill，某些不允许；不要因为能在类型层写出一个末尾 assistant 消息，就认为所有模型都支持部分答案预填。[^params-a]

### 4.2 Message 的 `content` 是数组，不是一个字符串字段

返回对象的 `role` 为 assistant，`content` 是内容块列表。常见块包括文本、thinking、redacted thinking 和 tool use；服务端工具、版本特性还可能引入其他块。[^response-a]

```json
{
  "role": "assistant",
  "content": [
    {"type": "text", "text": "我先查询工单。"},
    {
      "type": "tool_use",
      "id": "toolu_demo",
      "name": "lookup_ticket",
      "input": {"ticket_id": "DEMO-1"}
    }
  ],
  "stop_reason": "tool_use"
}
```

以上是合成报文片段，不是实际模型调用结果。使用时不要写成只取 `content[0].text`：第一个块未必是文本，即使有文本也未必已经是最后答案。

当前官方 Python SDK 的 `Message.to_param()` 将返回消息转为下一次输入可用的 assistant 消息，并保留其内容块。附带示例使用这个公开方法；如果安装的是没有该方法的旧 SDK，应查对应版本的转换方式，而不是随意删除不认识的块。[^response-a]

### 4.3 `stop_reason` 应进入分支判断

| `stop_reason` | 契约译解 | 应用应做什么 |
|---|---|---|
| `end_turn` | 模型自然结束本轮 | 读取结果，再检查业务要求是否完成 |
| `tool_use` | 模型提出一个或多个工具请求 | 识别调用、验证、执行，再回填结果 |
| `max_tokens` | 生成达到 token 上限 | 视为受限输出，不冒充完整成功；按任务选择增加预算或其他恢复方式 |
| `stop_sequence` | 命中自定义停止字符串 | 判断这个停止是否符合你的输出协议 |
| `pause_turn` | 长运行过程暂停，可在后续请求原样带回以继续 | 属于具体服务端循环的续接，不是普通本地函数调用 |
| `refusal` | 触发拒绝行为 | 向调用方返回拒绝状态，不换个名称当作成功 |
| `model_context_window_exceeded` | 上下文窗口超限 | 调整输入或压缩策略，而非只提高输出上限 |

这些值来自官方 `Message` 类型说明。流式 `message_start` 中的 `stop_reason` 可以为空，最终状态不能在刚连上时提前判定。[^response-a]

**附带最小工具循环只处理 `tool_use` 与 `end_turn`，其他情况显式停止并返回需要处理的状态。** 这不是说其余 API 行为非法，而是避免一个小示例假装实现了它没有实现的协议。

## 5. 工具循环：两家的差异实际落在哪几行代码

### 5.1 模型发出的不是函数调用栈，而是调用描述

设我们只提供一个只读演示工具：

```text
lookup_ticket(ticket_id="DEMO-1")
→ {status: "blocked", reason: "等待测试环境；合成数据"}
```

同一 schema 在两家请求中的位置不同：

```json
{
  "type": "function",
  "name": "lookup_ticket",
  "description": "只读查询演示工单。",
  "parameters": {
    "type": "object",
    "properties": {"ticket_id": {"type": "string", "enum": ["DEMO-1"]}},
    "required": ["ticket_id"],
    "additionalProperties": false
  },
  "strict": true
}
```

这是 Responses 的 function 定义；Messages 使用同一个参数 schema 的内容，但字段名为 `input_schema`，普通自定义工具定义不照搬这里的 `type: function` 外壳。[^tools-o][^tools-a]

**严格参数 schema 只能约束形状。** 工具名白名单、实际权限、路径限制、业务数据验证、时间预算以及是否允许写入，必须仍在执行器里落实。不要把 `name` 动态映射到任意 Python 全局函数，更不能对参数使用 `eval()`。

### 5.2 OpenAI：字符串参数 → 函数输出条目

核心节选：

```python
history.extend(response.output)

for call in response.output:
    if call.type != "function_call":
        continue
    args = json.loads(call.arguments)
    result = executor.call(call.call_id, call.name, args)
    history.append({
        "type": "function_call_output",
        "call_id": call.call_id,
        "output": result.text,
    })
```

四个要点：

1. `arguments` 是 JSON 字符串，需要解析；
2. `call_id` 用于结果配对，不是任意业务工单 ID；
3. 保留完整 `response.output`，而不是只存它的文本投影；
4. 结果条目追加后，再向模型发起请求。

完整附件额外处理了参数解析失败、不支持的工具类型、拒绝、响应非 completed 等情况。示例只声明 function 工具；如果收到不能处理的其他工具协议，它会停止，而不是假装执行成功。[^tools-o]

### 5.3 Anthropic：对象参数 → user 消息内的结果块

核心节选：

```python
history.append(message.to_param())

results = []
for call in message.content:
    if call.type != "tool_use":
        continue
    result = executor.call(call.id, call.name, call.input)
    results.append({
        "type": "tool_result",
        "tool_use_id": call.id,
        "content": result.text,
        "is_error": result.is_error,
    })

history.append({"role": "user", "content": results})
```

与 Responses 的差别不只在命名：

- `call.input` 已是解析后的对象；
- `tool_result` 位于 user 消息里，没有额外 `role: tool`；
- assistant 的工具调用消息与结果消息必须按合同紧邻；
- 同轮多个结果应组织为合法的结果消息，不能每返回一个结果就在中间插一段普通对话；
- 如果还要附用户补充，所有 `tool_result` 块在前，补充文字在后。[^tools-a]

### 5.4 Agent 退出条件不能只靠一句“完成了”

本例循环采用有限的模型请求预算。工具请求存在，就进行相应处理；只有返回类型、终态及所需文本符合预期时，才交回答案。

**实现建议**：生产系统进一步区分下面三个预算：

- 模型请求次数与 token 预算；
- 工具执行次数、耗时与权限预算；
- 整项任务的截止时间和业务完成条件。

附件的 `max_steps` 只限制模型请求次数。最后一次允许的请求仍可能产生工具调用，示例随后报告预算耗尽；它不是一个有检查点恢复与全局资源预留的完整调度器。

### 5.5 幂等要由执行层定义

附件用调用 ID、工具名和参数指纹组成一个**当前运行内**的执行账本：同 ID 同参数复用结果，同 ID 不同参数报错。这可以检查重复投递的基本问题，但进程重启后账本就丢失。

不能因此宣称端到端 exactly-once。对于创建订单、发邮件等操作，需要业务幂等键、持久执行状态和查询接口；模型生成的 `call_id` 不一定就是跨请求、跨恢复稳定的业务操作 ID。

## 6. 流式调用：读事件和读完整对象是两套接口使用方式

### 6.1 文档中的 delta 应译为“增量片段”，不是“一个 token”

OpenAI Responses 常见文本事件为 `response.output_text.delta`；工具参数还会通过 `response.function_call_arguments.delta` 等事件增长。Anthropic 使用 `content_block_delta`，其 delta 可以是文本、thinking 或部分工具参数 JSON。[^tools-o][^stream-a]

一个网络读取块不等于一个 SSE 事件，一个 SSE 事件也不必等于一个 token。工具参数中的 partial JSON 在结束前可能不可解析。

**实现建议**：优先让官方 SDK 处理字节解码、事件解析和消息累积。不要自己用 `split("\n")` 就宣布完整支持 SSE；也不要收到半截参数就运行具有副作用的工具。

### 6.2 OpenAI：显示增量，但最终保留完整 response

以下是普通 HTTP 流的读取函数；不处理 WebSocket steering 或 background 模式。`request` 是调用方构造的、不含 `stream` 的参数字典。

```python
def read_openai_stream(client, request):
    final = None
    with client.responses.create(**request, stream=True) as events:
        for event in events:
            if event.type == "response.output_text.delta":
                print(event.delta, end="", flush=True)
            elif event.type == "response.completed":
                final = event.response
            elif event.type in {"response.failed", "response.incomplete", "error"}:
                raise RuntimeError(f"stream did not complete: {event.type}")
    if final is None:
        raise RuntimeError("stream ended without response.completed")
    return final
```

最终的 `final` 仍需进入 §3、§5 的状态和工具处理。打印过的文字只用于 UI，不应用拼接后的字符串替换整个 response。这里没有在参数流到达时提前调度工具，刻意选择了更容易检查的完整响应边界。

如果改做原生 steering，这个函数的 `response.incomplete` 分支就不够了：`reason: steered` 可能意味着需要继续等待后继 response，而不是任务失败。不能拿一个没有 steering 状态机的通用事件循环直接套用。[^steering]

### 6.3 Anthropic：`text_stream` 与 `get_final_message()` 分工

```python
def read_anthropic_stream(client, request):
    with client.messages.stream(**request) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        message = stream.get_final_message()
    return message
```

这段中 `text_stream` 是展示视图，`get_final_message()` 是累积后的协议对象。返回对象仍应检查 `stop_reason`，并保留后续调用所需内容。不能因为 text iterator 没有更多字符，就省略消息终态检查。[^stream-a]

### 6.4 处理未知事件时，兼容性和执行安全要分开

Anthropic 文档说明事件类型可能新增，客户端应能优雅处理未知类型。工程上不宜把每个新通知都当致命错误；但**未知的行动请求**又不能未经支持就执行。[^stream-a]

一种合理区分是：

- 未识别的进度／附加元数据：记录必要信息，不破坏已知事件的处理；
- 未识别且可能要求执行、审批或恢复的对象：显式标记 unsupported，禁止静默跳过后声称任务成功；
- 缺少预期结束事件：保留 incomplete 状态，不把 socket 关闭当作成功。

## 7. 会话续接：谁保存历史，哪些配置会继续有效

### 7.1 四种路径不能混成一个 `continue()`

| 路径 | 客户端下一次发送什么 | 配置与状态责任 |
|---|---|---|
| OpenAI 客户端自管历史 | 完整所需 input 历史与当前请求设置 | 应用保存输出、工具结果和需要的 opaque 条目 |
| OpenAI 显式响应 ID 续接 | `previous_response_id` + 新 input | `instructions` 不自动继承；`conversation` 与其互斥 |
| OpenAI 原生 steering 自动续接 | 已接受 steer 后继续读事件，不另发重复 create | 自动后继响应继承原设置；遇到客户端所需结果时转入显式续接流程 |
| Anthropic Threads continue | `thread.previous_message_id` + 新 messages | 省略已保存的顶层 `system`、`tools`，遵守其他固定字段规则 |

来源：Responses 参数定义、原生 steering 指南及 Message Threads 文档。[^params-o][^steering][^threads-a]

尤其不能从 OpenAI 的“显式续接要重新带 instructions”，推导 Anthropic Threads 也应重复带 system/tools。后者的 continue 合同恰恰要求不要这样做。

### 7.2 `store: false`、缓存和状态续接不是同一开关

OpenAI 的 `store` 控制可检索响应的保存。当前 WebSocket 模式另外有连接内存中的前序响应状态，因此支持在 `store: false` 条件下做适用的续接；断线后不能假定连接内存仍在。[^params-o][^websocket]

Anthropic Threads 是服务端短期会话状态，应用仍应保留自己的副本。收到 `message_start` 的 ID 不足以立即续接，文档要求等待 `message_stop`。[^threads-a]

**少上传历史，不等于模型少看历史；复用缓存，也不等于输入不用计费。** OpenAI 的 conversation-state 指南明确指出，使用 `previous_response_id` 不免除响应链此前输入 token 的输入计费。具体价格和保留政策不在本文展开，不能把这条机制说明替代账单或合规判断。[^state-o]

### 7.3 显示记录不够用，运行记录至少要能表达关联

下面是**本文建议的应用记录结构**，不是厂商原始响应 schema：

```json
{
  "app_turn_id": "turn_demo",
  "provider": "openai",
  "api_request_id": "req_demo",
  "response_id": "resp_demo",
  "state": "waiting_for_tool",
  "pending_user_inputs": [],
  "tool_calls": [{
    "call_id": "call_demo",
    "name": "lookup_ticket",
    "execution_state": "succeeded",
    "result_ref": "local-result-demo"
  }]
}
```

这里分开了应用 turn、HTTP request、模型 response 和 tool call。它们不应共用一个含义模糊的 `id` 字段。日志中的引用也不自动等于状态内容已经持久化；结果必须真的存在并能读取。

<a id="runtime-updates"></a>

## 8. 运行中追加与改目标：先选定 API，再维护状态

OpenAI `response.steer` 在响应运行时接收更新；Claude Messages 在下一次请求带入更新；Claude Managed Agents 另有会话中断后按新消息继续的接口。三者都能表达用户改变了目标，生效时机和续接责任各不相同。[专题报告](./OpenAI与Anthropic_API通信与运行中追加消息_技术研究_20261110.md)给出完整对照与模型支持范围。[^steering][^messages-a][^managed-a]

### 8.1 Harness 队列和模型服务的 steer 队列不能混记

应用自己的输入队列和模型服务的队列有不同的确认状态。Codex `turn/steer` 是 Agent 层接口的一个例子，不能用它证明底层已发送 `response.steer`。实现时分别记录：

- UI 已排队，可能只是 UI 层状态；
- Harness 已接受，可能还没进入下一次模型请求；
- OpenAI `response.steer.accepted` 表示服务端持有待处理输入；
- 后继 `response.created` 才是官方事件参考所说明的 steering 提交点。

**不要在收到任一层 ack 后就从所有层的账本中删除原始输入。**[^steering-events]

### 8.2 OpenAI 原生 steering 的事件分支

连接、通道、历史缓存与 steering 怎样组合，见[《OpenAI Responses WebSocket 与 Steering：协议详解》](./OpenAI_Responses_WebSocket与Steering_连接续接与运行中改向_深度解析_20261111.md)。其中的[完整工具案例](./OpenAI_Responses_WebSocket与Steering_连接续接与运行中改向_深度解析_20261111.md#pending-tools)展开了多条更新共享一次结果回填的时序。

| 收到的事件／状态 | 译解与应用动作 |
|---|---|
| `response.created` | 确定正在工作的 response ID；后续 steer 指向该 ID |
| `response.steer.accepted` | 登记 `steer.id`；输入已入队，但尚不能宣称已应用 |
| `response.incomplete`，原因为 `steered` | 原 response 在规定边界让出；继续等待后继，不按一般失败直接结束任务 |
| `response.steer.pending` | 还有客户端工具结果／审批缺失；按 `required_input` 回填 |
| 后继 `response.created` | 对照已接受输入，推进提交状态与活动 response ID |
| `response.steer.failed` | 输入未通过该路径应用，也不会稍后自动应用；保留并显式处理失败 |
| 连接断开 | 服务端 pending 不具备跨连接保留保证；先对照已知事件与历史，再决定恢复 |

原生发送报文只包含：

```json
{
  "type": "response.steer",
  "previous_response_id": "resp_demo",
  "input": "先别修复，改为只分析原因，不要修改文件。"
}
```

不要给它添加 `stream_id`、新的 tools、系统角色或工具结果；该事件按目标 response 定位通道，只接受受支持的用户输入。当前指南限定为 **GPT-6 系列与 Responses WebSocket**，明确不支持 GPT-5.6 及更早模型。官方事件参考还要求适用的单 Agent response，并排除 conversation 绑定和自动 compaction 等配置。[^steering][^steering-events]

无客户端结果阻塞时，服务端自动创建后继 response 并继承原设置。需要客户端结果时，使用同一连接和正确通道的显式 `response.create` 回填，这次请求使用自己的设置。已 accepted 的更新由服务端合并，不应再次复制，也不能为了多个 pending 通知重复执行同一个工具。[^steering][^steering-events]

### 8.3 Claude Messages：下一次请求也可以改变目标

普通 `user` 消息就可以传达“改为只分析原因”。当前 Messages 文档没有提供向正在生成的那次响应追加 steer 的等价操作；应用保存更新，在后续请求中带入。这个结论的范围是直接 Messages API。[^messages-a]

使用 Messages 客户端工具时，一种明确的输入组织方式是：

```text
assistant: tool_use
user: [tool_result, tool_result, 用户补充 text]
→ 下一次 Messages 请求
```

当前官方中途消息文档，对 Sonnet 5.5 与 Haiku 5.5 明确要求这样传递用户原话；Harness 提醒另放在合法位置的 system 消息里。中途 system 消息主要处理操作者权限与缓存前缀的保留，也随新请求进入；其支持模型名单不代表普通后续 user 消息的支持范围。完整位置规则见[专题的 Claude Messages 一节](./OpenAI与Anthropic_API通信与运行中追加消息_技术研究_20261110.md#claude-messages)。[^mid-a]

这不是把生成中的 SSE 请求体“打开再加几行”。应用接收新消息与下一次调用可以异步衔接，但请求快照、工具结果配对与更新顺序应当确定。

**实现建议**：让一个会话调度器串行提交历史变更；UI、工具进程和网络读取器可以并发产出事件，但不要各自直接修改同一个正在发送的 `messages` 列表。若新要求涉及立即撤销写权限，还需要执行器的权限／取消机制，不能只指望模型在下一次判断时看到文本。

### 8.4 Claude Managed Agents：运行中中断并改向

如果接入的是托管 session，官方提供 `user.interrupt` 后跟 `user.message` 的事件序列。调用返回表示入队；中断应用后结束当前 turn，再用下一 turn 处理新消息。正在运行的工具可能延迟中断；有未结束的 workflow runs 时，session 不一定发出 idle。应用应结合事件与 `processed_at` 跟踪，不能把入队当作处理完成。[^managed-a]

这属于 Managed Agents 的会话执行接口，不能当成直接 Messages API 的能力。具体报文与边界见[专题的 Managed Agents 一节](./OpenAI与Anthropic_API通信与运行中追加消息_技术研究_20261110.md#claude-managed-agents)。本篇附带的客户端工具循环没有实现这条路径。

## 9. 错误、重试和观测：不要把“网络成功”当“任务成功”

### 9.1 至少区分五类失败

| 层次 | 例子 | 正确的处理方向 |
|---|---|---|
| 传输建立 | 连接失败、连接超时 | 按请求的重试政策处理，记录本次尝试 |
| HTTP 接口 | 400 参数错误、401 认证失败、429 限流 | 修参数／修认证／退避；不要对所有错误一律重发 |
| 响应生成 | failed、incomplete、refusal、max_tokens | 读取终态和原因，决定是否允许续接 |
| 流读取 | HTTP 200 后断流或出现 error 事件 | 保留部分接收状态，不能伪造正常结束 |
| 工具与业务 | 工具超时、执行成功但确认丢失、结果不满足要求 | 查询执行状态、幂等处理、反馈错误或报告缺口 |

Anthropic 流式文档展示了响应流中的 error 事件，因此“已经收到 HTTP 200”不是应用成功的充分条件。OpenAI SDK 则将网络问题、HTTP 非成功状态与流读取异常分别映射到相应异常类型。[^stream-a][^sdk-errors-o]

### 9.2 SDK 的默认重试是隐藏的请求倍增器

在本文固定的 OpenAI Python SDK 中，部分连接问题以及 408、409、429、5xx 默认最多重试两次；流消费过程不自动重试，以免重复交付已产生的输出。Anthropic SDK 的默认重试次数同样为两次，源代码对上述 HTTP 状态和可重试异常进行判断，并尊重服务端相关重试提示。[^sdk-errors-o][^retry-a]

这里的“两次”是额外重试预算，不是“最多两次请求”。若应用外层又套一层重试循环，实际尝试数可能进一步扩大。

附带示例关闭 SDK 自动重试，不是建议生产一律关闭，而是为了让教学程序的失败和模型请求次数更明确。生产可以使用适当退避，但应同时定义：

- 每次尝试及整个任务的总期限；
- 已显示的内容能否重放、如何避免 UI 重复追加；
- 已执行工具是否可安全重做；
- 结果未知时，先查询还是允许重试。

**模型请求重试、响应结果恢复、外部操作重做，不是同一个函数应该无条件包住的三件事。**

### 9.3 观测字段应能回答“慢或错在哪一层”

建议记录经过脱敏的：

- 应用 turn ID、API request ID、response/message ID；
- 首条有效输出到达时间、最终协议对象结束时间、工具耗时；
- 输出终态、停止原因、是否等待输入／审批；
- 模型请求次数、工具执行次数、重试次数；
- 原始 usage 的类别和值，以及是否确实取得最终 usage。

OpenAI SDK 的 `_request_id` 来自 `x-request-id` 响应头；虽然名字有下划线，文档明确它是公开属性。失败请求的 request ID 可从相应 APIStatusError 获取。它不是 `response.id`，更不是工具 `call_id`。[^sdk-errors-o]

Anthropic `Message` 的类型文档说明，API 会把请求转换为适合模型的格式，并把模型输出解析为响应，因此 usage 不与可见文本一一对应。其总输入计数为：

```text
input_tokens + cache_creation_input_tokens + cache_read_input_tokens
```

这条公式只按该供应商的字段语义使用，不要把另一家的 cached token 字段也照样重复相加。[^response-a]

## 10. 附带代码：有边界的最小实现，而不是“通用 Agent 框架”

### 10.1 文件与已实现范围

- [client_tool_loop.py](./assets/api_developer_20261110/client_tool_loop.py)：两家同步客户端工具循环、封闭的只读演示执行器、内存去重、调用预算、显式 live 入口。
- [test_client_tool_loop.py](./assets/api_developer_20261110/test_client_tool_loop.py)：可注入 Fake Client 的离线控制流测试。
- [results.json](./assets/api_developer_20261110/results.json)：本次测试结果。

示例使用客户端自管完整历史，刻意不叠加 Threads、conversation、WebSocket、server tools 或原生 steering。它关注的最小闭环是：

```text
创建请求 → 检查返回状态 → 保存完整协议输出
       → 验证客户端工具 → 执行／返回错误 → 配对结果 → 后继请求
```

执行器仅返回固定的 `DEMO-1` 合成工单，不访问真实工单、文件或 shell。

### 10.2 怎样运行

无需安装第三方依赖即可运行离线测试：

```bash
python3 -I ai-learning/reports/knowledge_reports/assets/api_developer_20261110/test_client_tool_loop.py
```

直接运行主文件只显示使用提示，不联网：

```bash
python3 -I ai-learning/reports/knowledge_reports/assets/api_developer_20261110/client_tool_loop.py
```

如果明确要做真实 API 验证，需另外在隔离环境安装官方 `openai`／`anthropic` SDK，并在本地设置相应凭据与模型环境变量：

| 供应商 | 凭据由 SDK 读取 | 模型由示例读取 |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `OPENAI_MODEL` |
| Anthropic | `ANTHROPIC_API_KEY` | `ANTHROPIC_MODEL` |

随后显式选择其中一家：

```bash
python3 -I ai-learning/reports/knowledge_reports/assets/api_developer_20261110/client_tool_loop.py --live openai
python3 -I ai-learning/reports/knowledge_reports/assets/api_developer_20261110/client_tool_loop.py --live anthropic
```

**这两个 live 命令未在本次任务执行，会产生实际 API 用量。** 代码按所引用 SDK 公开接口编写，但本次未验证安装态 SDK、账号权限或模型兼容性。需要使用支持相关字段及 `Message.to_param()` 的 SDK 版本；不要把阅读用源码快照误认为已经锁定了本地依赖。

### 10.3 17 项测试证明什么、不证明什么

本次执行：17 项测试通过，0 failure、0 error。覆盖：

- 工具调用的完整两次请求闭环；
- OpenAI reasoning opaque 内容与指令保留；
- Anthropic thinking 签名块保留及多个结果的消息位置；
- 参数解析失败、未知工具、缺失调用 ID；
- 非完成状态、拒绝和不支持的输出协议；
- 同 ID 同参数去重、同 ID 不同参数拒绝；
- 模型请求预算耗尽。

**这些测试证明的是本地代码对指定输入的分支和记录行为。** Fake Client 不校验服务端 schema，不进行真实分词／生成，不验证模型服从程度，也不覆盖并发、持久恢复和网络重放。

流式代码片段用于说明 SDK 的读取方式；本次只检查其 Python 语法，没有执行真实事件流。原生 steering 的实机事件与 Anthropic 特定模型的中途输入效果，同样属于后续集成验证范围。

## 11. 开发者可以带走的一份实现顺序

这是建议顺序，不是必须完成的庞大清单：

1. **先固定接口和支持范围。** 是 Responses、Chat Completions 还是 Messages？哪些模型、哪些工具类别？
2. **先做单次完整响应。** 看清返回对象和终态，再加流式显示。
3. **增加一个无副作用的客户端工具。** 验证 schema、调用 ID、错误回填与历史保留。
4. **把 UI 文本与运行账本分离。** 不用输出字符串替代完整协议对象。
5. **再选择状态优化。** 自管历史、响应 ID 或 Threads，不把各自配置继承规则混用。
6. **再做运行中追加。** 先有可检查的接受、排队、提交与失败状态，再优化交接延迟。
7. **最后扩展副作用和恢复。** 用业务幂等、权限、任务预算与持久化，而不是只增加一个重试装饰器。

最后用两句话概括本篇：

> **模型 API 提供生成与交互的协议对象；开发者必须据此构建执行状态机。**
>
> **两家都能支撑 Agent，但兼容不只是字段改名：输出保留、结果配对、配置继承、停止语义和恢复边界，都必须按各自合同实现。**

## 资料版本与引用

本篇是官方文档的选题式中文译解与原创工程说明。参数表根据所读范围整理，不声称字段穷尽或替代实时官方参考。新增字段、模型默认值和平台支持可能变化。

- OpenAI Python SDK 固定提交：`13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216`。
- Anthropic Python SDK 固定提交：`d4976414f2cc4652a7ec19947627f993a2959645`。
- 工具与流式基础复用 2026-11-10 实际取得的官方材料；Responses conversation-state 在初稿另行读取。2026-11-11 重新读取 steering、WebSocket 事件参考、Claude Messages、中途 system、Threads 与 Managed Agents 事件文档，更新第 8 节；实验代码未改。
- 初稿中一些参数参考页通过 eacli 读取失败，Anthropic 直接网页读取还遇到地区访问重定向。对应字段当时引用官方 SDK 中实际读取的声明及实现，未推断未读页面内容。
- 完成状态表示当前写作与离线控制流验证完成，不表示生产可用、独立审稿或真实 API 验收。

[^sdk-wire]: [OpenAI SDK `responses.py` L1381 起](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/resources/responses/responses.py#L1381)；[Anthropic SDK `messages.py` L1247 起](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/resources/messages/messages.py#L1247)，以及同文件 L1368–1406 的 stream manager 构造。
[^auth]: [OpenAI SDK `_client_auth.py` L354–360](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/lib/_client_auth.py#L354-L360)；[Anthropic SDK `_client.py` L374–395](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/_client.py#L374-L395) 与 [`_constants.py`](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/_constants.py)，当前快照认证及版本常量；不代表所有认证模式。
[^params-o]: [OpenAI SDK：ResponseCreateParams](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/types/responses/response_create_params.py)，特别是 L70–158、L250–335 的 include、instructions、预算、状态与截断说明。
[^response-o]: [OpenAI SDK：Response](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/types/responses/response.py)，L367–410 的错误与输出，L601–679 的状态和 `output_text` 实现。
[^params-a]: [Anthropic SDK：MessageCreateParams](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/types/message_create_params.py)，必填项、message 组织、thinking 与工具定义。
[^response-a]: [Anthropic SDK：Message](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/types/message.py)，content、stop_reason、usage 与 `to_param()`。
[^tools-o]: [OpenAI：Function calling](https://developers.openai.com/api/docs/guides/function-calling)，Responses/Chat Completions 工具协议、reasoning 保留与参数流；同日已读材料。
[^tools-a]: [Anthropic：Implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)，工具选择、客户端／服务端工具、结果紧邻及内容块顺序；同日已读材料。
[^stream-a]: [Anthropic：Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)，SDK 累积、SSE 事件、partial JSON、流内错误与未知事件；同日已读材料。
[^steering]: [OpenAI：Mid-turn steering](https://developers.openai.com/api/docs/guides/steering)，原生 steering 支持范围、自动／显式 continuation 与失败恢复；2026-11-11 重读。
[^steering-events]: [OpenAI：Responses WebSocket events](https://developers.openai.com/api/reference/resources/responses/websocket-events)，steering 输入、状态、限制与结果回填；读取于 2026-11-11。
[^threads-a]: [Anthropic：Message threads](https://platform.claude.com/docs/en/build-with-claude/message-threads)，create/continue、system/tools 省略、应用副本与 `message_stop`；2026-11-11 重读。
[^websocket]: [OpenAI：WebSocket mode](https://developers.openai.com/api/docs/guides/websocket-mode)，连接内存状态、`store=false`、通道与恢复；同日已读材料。
[^mid-a]: [Anthropic：Mid-conversation system messages and tool changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)，工具结果后的用户输入、模型差异、system 权限、缓存与位置；2026-11-11 重读。
[^messages-a]: [Anthropic：Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)，多轮请求及与 Managed Agents 的分工；读取于 2026-11-11。
[^managed-a]: [Anthropic：Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)，Interrupt the agent 与事件处理时机；读取于 2026-11-11。
[^state-o]: [OpenAI：Conversation state](https://developers.openai.com/api/docs/guides/conversation-state)，响应链状态与历史输入计费；本篇读取。`instructions` 不继承及与 conversation 互斥另以 SDK 参数定义为依据。
[^sdk-errors-o]: [OpenAI Python SDK README：Handling errors 至 Timeouts](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/README.md#handling-errors)，网络／HTTP／流异常、request ID、重试与超时。
[^retry-a]: [Anthropic SDK `_constants.py`](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/_constants.py) 与 [`_base_client.py` L934–992](https://github.com/anthropics/anthropic-sdk-python/blob/d4976414f2cc4652a7ec19947627f993a2959645/src/anthropic/_base_client.py#L934-L992)，默认重试次数及判断规则。
