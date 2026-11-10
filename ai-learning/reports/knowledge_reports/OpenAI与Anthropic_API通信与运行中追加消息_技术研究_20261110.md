---
title: "管家怎样把新纸条递给正在工作的鹦鹉？——OpenAI、Anthropic API 与 Codex 运行中追加消息"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-11"
semantic_tags: ["agent_harness", "api_protocol", "responses_api", "messages_api", "codex", "steering", "tool_use", "streaming", "context_management"]
---

# 管家怎样把新纸条递给正在工作的鹦鹉？

> **研究问题**：在 Codex 还没完成上一条任务时，我为什么能继续发送消息？新消息可以在下一次工具相关判断前参与工作，却不必把整个任务打断。这到底是界面排队、Harness 调度，还是模型 API 的新能力？
>
> **承接前篇**：[《Agent 请求全链路科普·完整版》](./Agent请求全链路_完整版_科普讲解_20261103.md)。仍用“管家 = Harness，鹦鹉 = 模型”的比喻，但这次打开信封，研究里面的真实字段、事件与源码。本文可独立阅读。
>
> **核验范围**：官方 API 文档读取于 2026-11-10；Codex 源码固定为 `39b42aaacdbb55b86528b4294443696985c348ee`。没有抓取个人 Codex 会话或调用付费模型，也没有运行 Codex 上游测试；附带实验是已运行的离线教学模型，不是线上实测。

## 先给答案：连续的是任务，不一定是同一次模型生成

**你描述的体验，关键不在于“鹦鹉学会同时听两个人讲话”，而在于系统可以把新输入插入仍在进行的工作流程，而不是把每条用户消息都当成一项必须串行等到完成的新任务。**

但不能只用一种实现解释它。本次查到三个相关层次：

1. **Codex Harness 的 `turn/steer`**：把补充输入交给正在执行的 turn，先进入待处理队列，再进入后续模型请求。源码还区分普通边界续接与抢占处理。
2. **OpenAI 模型 API 的 `response.steer`**：当前官方文档已提供原生 Mid-turn steering。它在 Responses WebSocket 上接收补充输入，并在规定边界产生带新输入的后继 response。
3. **Anthropic 的消息组织方式**：在工具结果之后追加用户文字，或按适用模型的官方指引使用 mid-conversation system message，让下一次模型调用吸收补充要求。它不能与“修改一个已发出的 SSE 请求”混为一谈。[^app-server][^openai-steering][^claude-mid]

**因此，“后面的消息不会打扰之前的消息”要拆成两句：**

- 可以不取消整个 Agent 任务、不丢失已记录的工具结果和用户要求；
- 不代表底层每一次模型响应都一定完整保留，更不代表已经执行的动作能够撤销。

仅凭界面体验，无法确定某个安装版本、账号路由或第三方客户端具体用了哪条路径。下面先建立基础报文模型，再回到你观察到的行为。

## 1. 从聊天框到模型，实际上有两段不同的通信

### 1.1 给管家交待工作，不等于直接向模型发请求

一次典型操作可以分成：

```text
用户界面
  → Agent 引擎 / Harness：开始任务、追加消息、取消任务
  → 模型服务 API：提交本次推理输入，接收输出事件
  → Harness：检查并执行工具，记录结果
  → 模型服务 API：带着结果和新增要求再次请求
  → 用户界面：展示工作进度与最终答复
```

这里至少有两份契约：

| 通信边界 | 传递的东西 | 本文实例 |
|---|---|---|
| 界面与 Agent 引擎 | 任务、会话、审批、追加输入、取消、执行事件 | Codex app-server 的 `turn/start`、`turn/steer`、`turn/interrupt` |
| Harness 与模型服务 | 模型输入、工具定义、生成参数、输出条目、工具结果 | OpenAI Responses / Chat Completions；Anthropic Messages |

Codex 官方 app-server 文档规定，它使用双向 JSON-RPC 2.0 风格消息，线上报文省略 `jsonrpc` 字段；默认 stdio 传输采用逐行 JSON。它还提供其他传输方式。**这份协议与 OpenAI 模型 API 不是同一份协议。** 某些客户端直接嵌入核心运行库，也不一定经过独立 app-server 进程。[^app-server]

给管家发送：

```json
{
  "method": "turn/steer",
  "id": 32,
  "params": {
    "threadId": "thr_demo",
    "expectedTurnId": "turn_demo",
    "input": [{"type": "text", "text": "先只读分析，不要修改文件。"}]
  }
}
```

收到：

```json
{"id": 32, "result": {"turnId": "turn_demo"}}
```

这表示引擎接受了对这个 turn 的追加，不是模型已经理解并执行了这句话。`expectedTurnId` 防止网络或界面延迟把旧任务的补充错投给新任务；无活动 turn 或 ID 不匹配会失败。官方契约还明确：`turn/steer` 不产生新的 `turn/started`，也不用于切换该 turn 的模型、目录或沙箱策略。[^app-server][^codex-admission]

### 1.2 “管家与鹦鹉之间”还隔着服务层

API 接收的是 JSON 等结构化数据；真正的推理服务还需要解释消息角色、内容块、工具定义和生成配置，再形成模型可用的输入。**不能把 JSON 字符串本身等同于模型内部的全部提示格式。**

客户端能核实的是公开报文、响应事件和返回状态。供应商内部如何序列化全部控制信息、调度计算与复用内部状态，并没有因为 SDK 开源而全部公开。本文不把“模型内部一定按某套隐藏 token 拼接”写成已知事实。

仍然可以保留前篇的比喻：管家负责记录与执行，鹦鹉负责根据本次拿到的材料判断；服务层负责收发和组织材料。**“API 支持保存历史”与“模型参数记住了这段私有对话”是两回事。**

## 2. 打开信封：两家的工具对话怎样表示

贯穿示例：

> 第一条：“定位并修复这个测试失败。”
>
> 正在读取测试时追加：“先只读分析，不要修改文件。”

工具名、ID、文件名与结果均为合成示例。下面的 `<OPENAI_MODEL_ID>`、`<CLAUDE_MODEL_ID>` 是明确的占位符；报文用于讲解，并非已调用真实 API 的记录。真实请求还需要认证以及相应模型支持。

### 2.1 OpenAI Responses：输入和输出是一组有类型的条目

普通 HTTP 请求使用 `POST /v1/responses`。示意请求：

```json
{
  "model": "<OPENAI_MODEL_ID>",
  "instructions": "你是代码助手。遵守用户授权。",
  "input": [{"role": "user", "content": "定位并修复这个测试失败。"}],
  "tools": [{
    "type": "function",
    "name": "read_test",
    "description": "只读指定的测试文件。",
    "parameters": {
      "type": "object",
      "properties": {"path": {"type": "string"}},
      "required": ["path"],
      "additionalProperties": false
    },
    "strict": true
  }],
  "stream": true
}
```

模型可以返回一个 `function_call` 输出条目，而不是直接给最终答案：

```json
{
  "type": "function_call",
  "id": "fc_demo_read",
  "call_id": "call_demo_read",
  "name": "read_test",
  "arguments": "{\"path\":\"tests/demo.py\"}"
}
```

特别注意两个字段：

- `id` 是这个输出条目的标识；
- `call_id` 才是随后工具结果的配对标识。

`arguments` 是 **JSON 编码的字符串**，应用需要解析、检查，再执行实际工具。回填结果：

```json
{
  "type": "function_call_output",
  "call_id": "call_demo_read",
  "output": "合成工具结果：测试期望空列表，实际返回 null。"
}
```

接下来有两种基本做法：自行保存并发送完整所需历史，或者在适用条件下通过 `previous_response_id` 续接，并只发送新增条目。**两者都不能把工具结果的调用关联丢掉。** 对返回 reasoning items 的推理模型，官方还要求在手动管理历史时保留相关 reasoning items，而不是只复制可见答案。[^openai-tools][^openai-ws]

`strict: true` 主要约束参数结构，不证明路径有访问权限，也不保证工具选择正确。模型输出“调用 read_test”，与程序真的读了文件，是两个事件。

### 2.2 Anthropic Messages：消息里面再装内容块

基础入口是 `POST /v1/messages`。相同任务的请求：

```json
{
  "model": "<CLAUDE_MODEL_ID>",
  "max_tokens": 1024,
  "system": "你是代码助手。遵守用户授权。",
  "messages": [{"role": "user", "content": "定位并修复这个测试失败。"}],
  "tools": [{
    "name": "read_test",
    "description": "只读指定的测试文件。",
    "input_schema": {
      "type": "object",
      "properties": {"path": {"type": "string"}},
      "required": ["path"],
      "additionalProperties": false
    }
  }],
  "stream": true
}
```

模型响应的相关片段：

```json
{
  "role": "assistant",
  "content": [{
    "type": "tool_use",
    "id": "toolu_demo_read",
    "name": "read_test",
    "input": {"path": "tests/demo.py"}
  }],
  "stop_reason": "tool_use"
}
```

这里最终 `input` 是对象，而不是 OpenAI 示例里的 JSON 字符串。执行后，结果放进 `user` 消息的内容块：

```json
{
  "role": "user",
  "content": [{
    "type": "tool_result",
    "tool_use_id": "toolu_demo_read",
    "content": "合成工具结果：测试期望空列表，实际返回 null。"
  }]
}
```

**这里的 `role: user` 是协议角色，不代表工具结果由真人敲入。** Claude 把工具请求和工具结果融入 assistant/user 消息结构，而不是使用单独的 `tool` 消息角色。[^claude-tools]

### 2.3 为什么“兼容 OpenAI API”不能只换一个地址

| 项目 | OpenAI Chat Completions | OpenAI Responses | Anthropic Messages |
|---|---|---|---|
| 主要输入 | `messages` | `input` 条目 | `messages` + 内容块 |
| 客户端工具申请 | `tool_calls[]` | `function_call` 条目 | `tool_use` 内容块 |
| 参数表示 | `function.arguments` 字符串 | `arguments` 字符串 | 最终 `input` 对象 |
| 工具结果 | `role: tool` + `tool_call_id` | `function_call_output` + `call_id` | `role: user` 内的 `tool_result` + `tool_use_id` |
| 连续工作 | 应用维护循环 | 应用循环，另有服务端状态与 steering 能力 | 应用循环，另有 Threads 和中途消息组织能力 |

前三列不是简单的字段别名。适配器还要处理工具顺序、流式事件、停止原因、历史与推理内容的保留，以及不支持的能力。普通文本聊天能成功，不证明复杂 Agent 循环全部兼容。[^openai-tools][^claude-tools]

## 3. 一次“回复”其实有四个不同的边界

这正是你观察到的变化最容易被误解的地方。

| 单位 | 结束意味着什么 | 不意味着什么 |
|---|---|---|
| 一条屏幕消息 | 一个可见气泡或文本片段结束 | 整个任务结束 |
| 一次模型 response/message | 本次生成完成、停止或被截断 | 工具已执行，或所有要求已完成 |
| 一次工具执行 | 一项外部操作返回结果／错误／运行中句柄 | 模型已重新评估结果 |
| 一个 Agent turn／任务 | Harness 判定这段工作结束 | 必然只调用过模型一次 |

一次任务常常是：

```text
模型请求 R1 → 工具 A → 模型请求 R2 → 工具 B → 模型请求 R3 → 最终答复
```

如果界面把整个任务当成一个不可插入的整体，用户就要等 R3。若 Harness 在 R1、R2 之间检查新输入，你就可以在工具 A 执行期间追加要求，R2 已经会带上它。

**这并不要求在 R1 正在解码的 token 序列中，直接修改 R1 的输入。**

### 流式输出只是让你提前看见，不自动提供输入通道

OpenAI Responses 的工具参数流可包含：

```text
response.output_item.added
response.function_call_arguments.delta ...
response.function_call_arguments.done
response.output_item.done
```

Anthropic 的对应结构是：

```text
message_start
content_block_start
content_block_delta ...
content_block_stop
message_delta
message_stop
```

Anthropic 的 `input_json_delta.partial_json` 仍是**模型向外输出**的工具参数片段；名字里有 input，不表示用户正通过它向模型输入新话。参数可能尚不是完整 JSON，应用不能拿半截内容执行有副作用的动作。[^openai-tools][^claude-stream]

SSE 是服务端向客户端发送事件的方式；界面能够继续收键盘输入，是界面和 Harness 的并发处理能力，不是这条 SSE 响应自动变成了双向聊天。WebSocket 能双向传输，但“允许发送什么、何时生效”仍由上层协议决定。

还有一个细节：某个完整工具调用条目到达后，Harness 可以开始执行，而整个响应流未必已经结束。Codex 的采样处理器用流事件与在途工具集合管理这种重叠。因此，不能把“等当前工具边界”机械理解成“整个 API 请求结束之后才允许任何工具运行”。[^codex-sampling]

## 4. Codex 源码：补充要求先进入谁的队列

### 4.1 界面的“排队”和“立即追加”是两种状态

固定版本的 TUI 分别处理 `InputResult::Submitted` 与 `InputResult::Queued`，并维护 `queued_user_messages`、`pending_steers` 等不同队列。普通提交在满足条件时可以送入正在运行的工作；明确排队则走另一条输入流程。某些设置等待、计划展示或恢复状态会暂缓发送。[^codex-ui]

这意味着不能只问“消息发出去了吗”，还应问：

- 它还只在 UI 的后续任务队列里吗？
- Harness 已经接受到当前 turn 了吗？
- 新的模型请求是否已经包含它？

本文不把某个快捷键当成永久契约：按键映射与客户端可以变化，真正要确认的是提交模式。

### 4.2 接受 steer：锁住活动 turn、核对目标、按接受次序入队

在 `session/turn_input.rs` 的 `steer_input` 中，关键动作是：

1. 取得活动 turn 的锁，确认当前存在可追加的任务；
2. 核对 `expected_turn_id`；
3. 拒绝不适用的 review／compact turn 与空输入等情况；
4. 为用户输入登记接受次序；
5. 追加到 `pending_input`，通知等待输入变化的部分。

它并没有在这里直接改写已经发出的模型请求。[^codex-admission]

“已接受”与“已进入推理”之间因此存在一个真实的时间间隔。这也是应用需要显示 pending 状态、处理目标过期，而不是简单清空输入框就算完成的原因。

### 4.3 后续采样：把新消息并入历史，再创建请求快照

`session/turn.rs` 在主循环中明确注释：pending input 在构造下一次模型请求前被排入历史。随后它取得该次请求的 `StepContext`，克隆历史，再执行 `run_sampling_request`。[^codex-loop]

把这段逻辑压缩成教学伪代码：

```python
while task_is_active:
    # 实现还有首次采样、压缩、抢占等边界条件。
    record(accepted_pending_input())
    request_context = capture_step_context()
    request_history = snapshot(history)

    outcome = await sample_and_handle_tools(request_context, request_history)

    if outcome.needs_follow_up or has_pending_input():
        continue
    finish_task()
```

这里最重要的不是循环语法，而是两条保证：

- **新输入进入一个新的请求快照，不会自动改写旧请求快照；**
- **即使模型这次没有再要求工具，只要还有待处理输入，仍可以进入下一次采样。**

后者对应源码中的 `model_needs_follow_up || has_pending_input`。所以追加消息不必等着偶然再有一个工具调用才被处理。[^codex-loop]

### 4.4 “不打扰”不是“永远不抢占底层响应”

源码存在 `InstantInterrupt` 功能。本次固定快照中，它的配置名是 `instant_interrupt`，标为 `UnderDevelopment`，源码默认值为 `true`；**这不证明用户安装包、托管配置和当前会话实际启用了同样的路径。**[^codex-feature]

启用时，请求级 `StepContext` 带有单独的 preempt token。输入监视器先订阅通知，再检查队列，避免订阅与检查之间漏掉新输入；发现用户消息后触发这个 token。[^codex-preempt]

这和取消整个 turn 使用的 cancellation token 不是一回事：

- 普通边界路径：让当前响应及工具处理完，后续采样加入新输入；
- 抢占路径：提前结束当前采样等待、排空响应或让前台工具观察返回，然后继续同一任务；
- 明确中断：取消 turn，最终进入 interrupted 等结束状态。

具体行为受传输和工具类型影响。当前代码在有可用响应控制通道时会处理 drain；没有该通道的路径可以结束当前采样处理，再发后继请求。对可让出的 code-mode 执行，还可能先返回“脚本仍在运行”的句柄，而不是杀掉实际脚本。不能把这些情况都说成“模型刚才想的东西完全没有被打断”。[^codex-sampling][^codex-ws-drain]

### 4.5 上游测试具体检查了什么

本文阅读了以下测试，**没有在本机执行它们**：

| 测试 | 代码中的验证目标 |
|---|---|
| `user_input_does_not_preempt_after_reasoning_item` | 关闭 InstantInterrupt 时，补充输入不抢断当前 reasoning 后的工具调用和答案，后续请求再吸收它 |
| `steers_during_tool_drain_preserve_tool_output_and_each_input` | 工具仍在进行时连续追加两条输入，后继请求保留原问题和两条补充，并且实际工具结果只登记一次 |
| `input_preempts_response_and_yields_running_code_mode_call` | 开启相关功能时，前台执行可以让出观察；尚未接收到的第二个调用不会凭空进入后继请求 |

这些测试把“不丢问题、不丢已取得结果、不过度重复执行”变成了可检查的消息关系，而不只是界面文案。另一个名为 `injected_user_input_triggers_follow_up_request_with_deltas` 的相关测试在该快照中标为 flaky 并被忽略，本文不将它当作已通过的验证。[^codex-tests]

**回到你的体验：最稳妥的解释是，用户补充可以进入正在工作的 Agent turn，Harness 再在可处理的边界生成带新要求的后继推理。它可能不取消任务，但不承诺旧 API 响应始终毫无变化。**

## 5. OpenAI 原生 `response.steer`：把交接的一部分交给服务端

这不是 Codex `turn/steer` 的另一种拼写。

- `turn/steer` 发给 **Codex 引擎**，定位 Agent turn；
- `response.steer` 发给 **OpenAI Responses WebSocket 服务**，定位模型 response。

截至核验日，官方指南将原生 steering 的支持范围限定为 **GPT-6 系列与 Responses WebSocket**，明确不支持 GPT-5.6 及更早模型。官方 SDK 的类型说明还列出：仅适用于支持该能力的单 Agent 响应，不支持绑定 `conversation` 或使用自动 compaction 的响应。不要把它推广为“所有 OpenAI-compatible 模型都支持”。[^openai-steering][^openai-steer-type]

### 5.1 接受、结束旧响应、提交后继响应，是三步

先发送正常 `response.create`。收到目标的 `response.created` 后，可以在同一连接发送：

```json
{
  "type": "response.steer",
  "previous_response_id": "resp_demo_1",
  "input": "先只读分析，不要修改文件。"
}
```

该事件只接受 `type`、`previous_response_id`、`input`。输入限于支持内容类型的用户消息，不能趁机塞入工具结果、系统角色或一套新生成参数；也不能把 `stream_id` 加进这个事件，目标 response 已确定其通道。[^openai-steer-type]

服务端首先发出 `response.steer.accepted` 并给这条追加分配 `steer.id`。**accepted 只证明输入已经归服务端排队，不证明模型已经据此行动。** SDK 把后继响应的 `response.created` 描述为提交点。[^openai-steer-type]

在没有外部工具结果或审批阻塞时，通常经历：

```text
resp_1 正在输出
    用户提交 steer → 服务端 accepted
    当前输出 item 与已在运行的托管工具工作到达规定边界
    resp_1 结束
    服务端自动创建 resp_2，带入补充输入
    resp_2 继续工作
```

如果 steering 提前结束原响应，原响应以 `response.incomplete` 和 `incomplete_details.reason: "steered"` 结束；如果原响应恰好已正常完成，也可以保留 completed 状态并产生 steering continuation。**因此，旧响应的 incomplete 与整个任务失败不是同义词。** 应用必须识别原因并继续读后继事件。[^openai-steering]

此时不要自己再发一次重复的 `response.create`，因为服务端负责自动续接。自动 continuation 继承原请求设置；每个 response 分别应用 token 和工具调用限制，不能假设原始单响应限制自动成为整个任务总预算。

### 5.2 卡在客户端工具时：服务端没有你电脑里的执行结果

假设 `resp_1` 已提出 `read_test` 调用，此时追加“不要改文件”。服务端知道新要求，却不知道本地读取的结果，不能凭空跳过工具协议。

原响应完成后，可以收到：

```json
{
  "type": "response.steer.pending",
  "sequence_number": 12,
  "steer": {
    "id": "steer_demo_1",
    "previous_response_id": "resp_demo_1"
  },
  "reason": "waiting_for_required_input",
  "required_input": [{
    "type": "function_call_output",
    "call_id": "call_demo_read",
    "name": "read_test"
  }]
}
```

应用接着在**同一连接、对应通道**用 `response.create` 回填结果，`previous_response_id` 指向原 response。此时这是一次显式续接，使用它自己携带的工具、指令等设置。服务端会将已接受的 steer 按提交顺序放到这次新增 input 前面，**应用不要再复制那条补充消息**。[^openai-steering][^openai-steer-type]

也不要因为多个 steer 都提示同一个缺失工具结果，就执行工具多次或为每条 steer 分别发一次 continuation。它们可以共享一次对父 response 的结果回填。官方 SDK 对 `response.steer.pending` 的说明专门约束了这一点。[^openai-steer-pending]

### 5.3 为什么它仍不是“在同一只脑袋里无缝改一个 token”

公开契约实际暴露的是：**排队 → 规定输出边界 → 后继 response**。它没有向客户端保证“直接修改尚在计算中的同一份隐藏状态，并且一个 token 都不浪费”。

用比喻说，是服务前台可以先收下新纸条，在鹦鹉处理完一个合适单元后，把补充材料连同既有工作交给后继处理。你可以持续接收事件，不必手工重启整项工作。

它也明确不回写已经交付的输出、不撤销先前动作、不取消已经开始的工具。更短的交接延迟，不等于对外部副作用的硬取消保证。[^openai-steering]

### 5.4 断线后，accepted 也不是永久保管凭证

官方指南说明：排队的 steering 输入只存在于当前连接，并不随原 response 持久保存。客户端应记录自己发送的输入、`steer.id` 与后继响应事件，断线后先对照历史再恢复，不能盲目认定“已接受的一定处理过”或“一定没处理过”。[^openai-steering]

还要区分两个 ID：WebSocket 的 `stream_id` 是有序通道，`previous_response_id` 是上下文血缘。当前 WebSocket 文档允许不同通道并发，同一通道请求保持 FIFO、不重叠。**多通道并发与同一任务的 steering，是两种不同能力。**[^openai-ws]

### 5.5 当前 Codex 是否直接在用这个公开事件？

本次沿 Codex app-server → 核心输入队列 → 采样循环 → Responses 客户端追踪到的是第 4 节的路径。在已检查的 WebSocket 请求枚举中，普通请求变体是 `ResponseCreate`；响应控制路径另有 drain／interrupt 逻辑。**这些证据不支持把 Codex `turn/steer` 直接等同于对外发送 `response.steer`。**[^codex-ws-type][^codex-ws-drain]

本文没有核验用户安装版本和实际网络事件，所以保留这个缺口。服务端有原生能力、公开 Codex 有输入调度机制、某个产品部署已经将两者接起来，是三项需要分别证明的事实。

## 6. Anthropic：下一封信怎样既带工具结果，又带新要求

### 6.1 最直接的合法形状：先工具结果，再追加用户文字

在 §2 的 assistant `tool_use` 之后，回填这一条 user 消息：

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_demo_read",
      "content": "合成工具结果：测试期望空列表，实际返回 null。"
    },
    {"type": "text", "text": "先只读分析，不要修改文件。"}
  ]
}
```

下一次调用的逻辑上下文就同时包含：原始任务、模型提出的读取请求、读取结果、用户补充。模型可以继续诊断，但应按新要求暂停修改。

官方要求：工具结果紧接对应的 assistant 工具请求；在包含工具结果的 user 消息中，`tool_result` 块必须位于其他文字之前。**不要为了“立即插入新话”，把一条普通消息硬塞在 `tool_use` 和它的结果之间。** 多个工具调用也应按要求配对，并组织在合法的结果消息中。[^claude-tools]

### 6.2 新的 mid-conversation system message，为什么与此有关

Anthropic 当前文档还给出一种更细的组织方式：允许在会话中途追加 `role: "system"` 消息，而不改动开头的顶层 `system`。

这解决两个问题：

- Harness 的新状态或运行约束可以在发生的位置出现；
- 不必为了新增一条规则修改整个历史的开头，有利于保留已缓存前缀。

文档明确把“用户在 Agent 工具执行期间发来补充，但不希望重启整个工作”列为使用场景。对适用模型，Harness 可以在工具结果之后用 system 消息说明“用户刚提供了新的上下文……”，让模型把它纳入正在进行的工作。**不要把“补充背景”写成“忽略用户原来的要求”。**[^claude-mid]

不过这里有一个重要的模型差异：

- 当前文档对多数适用模型讨论了工具结果后的 system 转述方式；
- 对 **Claude Sonnet 5.5 与 Haiku 5.5**，官方明确要求把用户原话放在同一 user 消息中、最后一个 `tool_result` 后面的 `text` 块里；Harness 提醒则另放 system 消息，不能与用户原话混成一块。

因此，§6.1 的结构不是为了好看而排列，而是当前模型指引直接关心的输入语义。**API 解析接受某个形状，与模型能正确区分“用户补充”和“不可信工具文本”，仍是两个层次。**[^claude-mid]

### 6.3 权限与位置不能借机混淆

mid-conversation system 消息不是任意位置都可插入：带内容的这种消息须紧接 user turn（或文档允许的服务端工具结果位置），之后是 assistant turn 或数组结束；不能夹在工具申请与对应结果之间，也不能作为最初消息替代顶层 system。[^claude-mid]

更重要的是，**不要把检索网页、工具输出或第三方文档包装成 system 消息**。这会把低信任资料提升为运行系统指令。官方建议转述的是同一对话的最终用户输入，不是“凡是运行中收到的文本都可以升级权限”。

对当前已明确要求“不改文件”的用户，Harness 还可以在执行层直接限制写工具权限。这比单纯希望模型每次都注意到那句话更可靠；但是否实施这种权限变更，要遵守具体应用的授权和配置契约。

### 6.4 Message Threads 不是生成中追加接口

前篇已经讨论过 Threads：首次发送完整会话，随后通过 `thread: {type: "continue", previous_message_id: ...}` 发送增量，让服务端重建上下文。

本次重新核验的文档仍要求：流式调用虽然在 `message_start` 已给出响应 ID，**必须等 `message_stop` 后再从该 ID 续接**。Threads 节省重复上传与前处理，但不是在已有 SSE 生成过程中追加输入的通道。[^claude-threads]

同理，mid-conversation system message 的“mid-conversation”，指它出现在多步会话的中间位置，不自动等于“mid-generation”。它的文档说明的是后续请求的消息组织，而不是提供一个与 OpenAI `response.steer` 完全等价的事件。

在本文核验的 Messages、Threads 和中途消息文档中，没有据此确认一个同名同语义的 Claude 生成中注入接口；**这不应扩大成对所有 Anthropic 产品、Managed Agents 或未来能力的不存在声明。**

## 7. 为什么模型能连续判断，却没有丢掉前一项工作

### 7.1 连续性来自材料的保留与重新解释

把原始任务记为 U1，新补充记为 U2，已得到的结果记为 T1。下一次判断的输入不是孤立的 U2，而近似为：

```text
原规则 + U1 + 已生成的工具请求 + T1 + U2 + 其他仍有效的上下文
```

模型据此判断“继续完成 U1，但按 U2 限制做法”。上一轮发现的失败原因仍在；新的只读约束也在。**不是前一句被后一句覆盖，也不是必然启动第二个互不相干的 Agent。**

但保存了上下文不保证理解一定正确。补充如果相互矛盾、描述含糊，或者压缩丢失了关键限制，模型仍可能漏做或误解。协议能保证顺序与配对，不能独自证明语义层面的所有要求都被满足。

### 7.2 新消息影响的，是被它赶上的那个判断边界

假设你说“不要改文件”时，模型已经提交过一个写入调用：

- 如果尚未授权或调度，Harness 有机会拦住；
- 如果调用已经执行，追加消息不会自动回滚；
- 如果模型还未生成下一步调用，新输入就可能改变下一次决定；
- 如果多个工具调用已并行发出，不能保证每个调用之间都有一次读新消息的机会。

所以，“能在下一轮工具调用前发过去”应理解为产品提供了更及时的输入机会，**不是所有已经排出的工具动作都拥有可撤回保证**。涉及删除、转账、部署或外发，应使用实际审批、取消和执行状态核验，而不是仅发送一条自然语言补充。

### 7.3 快，是因为不用等到最终答复，不是没有额外成本

旧方式可能要等整个任务结束再问一次；边界追加让 U2 提前参与当前任务。若历史前缀保持稳定，缓存还有机会减少重复计算。Threads 或 `previous_response_id` 可以减少重复传输。

这些机制分别解决不同问题：

| 机制 | 主要改变什么 |
|---|---|
| Harness pending input | 用户补充何时进入下一次推理 |
| 原生 `response.steer` | 运行中追加的服务端排队与续接 |
| SSE／WebSocket | 事件如何传输，是否有双向消息通道 |
| Threads／响应 ID 续接 | 历史怎样被带入下一次请求 |
| Prompt caching | 重复前缀能否复用处理 |
| Compaction | 下一次逻辑上下文保留哪些内容 |

续接仍可能消耗新的输入、输出与工具调用；抢占也可能使部分生成没有继续用于最终交付。本文没有测量这些路径的真实成本或延迟，不用“感觉流畅”推出“免费”或“同一次无限推理”。

## 8. 本地实验：让队列与报文关系变得可检查

本文附带一个标准库 Python 实验：[api_turn_lab.py](./assets/api_communication_20261110/api_turn_lab.py)，运行结果保存在 [results.json](./assets/api_communication_20261110/results.json)。

**它是手写教学状态机与合成报文，不是 Codex 源码的复制，也不是供应商服务端实现。** 没有模型、网络或实际工具；不会证明模型是否服从补充要求。原生 steering trace 中的 `queued`、`logical_new_input` 等是教学观测字段，不是声称真实事件包含这些字段。

2026-11-10 本地执行结果：**12 项测试通过，0 failure、0 error。** 主要覆盖：

- 请求快照已经创建后，接受新输入不会修改旧快照；
- 原问题与连续两条追加按顺序进入后继输入；
- 过期 turn ID 不会污染队列；
- 工具请求与结果 ID 正确配对，结果不因两条 steer 而重复登记；
- 两家示例报文中的参数类型和结果位置差异；
- 模拟服务端 accepted 不等于已创建后继响应；
- 缺工具结果时保留已接受的追加，回填后只注入一次；
- 断线清空服务端临时队列时，应用副本仍有必要。

实验保存的 Harness 轨迹是：

```text
已经发出的输入快照：
  U1 定位并修复测试失败

接受两条补充后，下一次输入：
  U1 定位并修复测试失败
  assistant 请求读取测试
  tool 返回读取结果
  U2 先只读分析，不修改文件
  U3 用中文解释
```

模拟原生 steering 则展示另一种合并位置：服务端先排队，遇到客户端工具时返回 pending；显式 continuation 的新增输入前面被放入已接受补充，再接工具结果。**两个例子都保留信息，但不能因此要求所有 API 用同一个固定排列。**

复现时不覆盖已归档结果，直接运行即可在终端输出测试和 JSON：

```bash
python3 -I ai-learning/reports/knowledge_reports/assets/api_communication_20261110/api_turn_lab.py
```

实验只检查本文选取的关系，不进行完整官方 Schema 校验，也不包含 Codex 抢占、网络丢包、服务端推理、并行工具与持久恢复的生产实现。

## 9. 怎样判别自己实际走的哪条路径

不必先抓完整私人提示词。更有用的是查看**经过脱敏的事件名和 ID 关系**：

| 想确认什么 | 优先观察 |
|---|---|
| 输入还在界面排队吗 | 队列／pending 展示，以及引擎是否已确认接受 |
| 是追加当前任务，还是新开任务 | `turn/steer`、返回的 `turnId`、是否出现新 `turn/started` |
| 模型服务是否用了原生 steering | 是否实际发送 `response.steer`，以及 accepted／pending／failed 与后继 response 事件 |
| 底层响应是否被改道 | 旧 response 的终态、`incomplete_details.reason`、新 response ID |
| 新要求真正进入哪次判断 | 对应请求的新输入记录或已提交的后继历史，而不只看输入框清空 |
| 已开始工具有没有被重复执行 | 工具调用 ID、执行记录、返回结果与后继输入的对应关系 |

这是后续实机实验的方法，不是本文已经完成的观测。若要对自己的 Codex 做验证，先记录客户端版本、模型、连接方式与相关功能配置；只保留必要事件和合成任务，避免把认证头、私人消息、源码和工具输出上传到公共诊断服务。

## 最后，把“管家与鹦鹉”的比喻升级一下

过去的直觉是：管家递一张纸条，等鹦鹉回答完，再接收下一张。

更准确的系统是：

> **管家有收件队列、任务账本和工具执行权；服务端也可能有临时收件队列。鹦鹉的工作被组织成有边界的生成与行动步骤。新纸条可以提前被接收，在合适的下一步与旧账本一起交付，不必把整个任务推倒重来。**

你感兴趣的“模型能连续判断”，由几个部分共同形成：

1. 用户输入不再被最终答复阻塞；
2. 新旧要求、已完成工作与工具结果有清晰的记录和顺序；
3. Harness 或模型服务在明确边界创建后继推理；
4. 模型根据更新后的上下文重新判断下一步；
5. 应用区分接受、应用、完成与失败，避免漏消息或重做外部动作。

**最关键的三组区分：`turn/steer ≠ response.steer`；`accepted ≠ applied`；`任务不中断 ≠ 底层响应绝不结束或改道`。**

## 来源、版本与未覆盖范围

- 本文优先使用官方文档和固定提交源码。公开仓库索引只用于导航，不用自动生成的仓库介绍替代代码证据。
- Codex 源码：`39b42aaacdbb55b86528b4294443696985c348ee`；OpenAI Python SDK steering 类型：`13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216`。源码快照不是用户安装版本的证明。
- API 文档读取于 2026-11-10；它们可能继续更新。工具页面上的模型推荐、吞吐数字等不是本报告研究对象，没有据此做性能或价格比较。
- 未实测：真实模型调用、个人 Codex 路由、服务端内部计算、线上错误恢复、上游 Rust 测试。完成状态仅表示本次报告与离线实验已完成，不表示独立审稿或生产兼容性认证。
- 不把本篇结论追溯改写到旧报告；前篇的流式、缓存和 Threads 基础仍可参考，运行中追加与当前原生 steering 的差异以本篇明确的来源范围为准。

[^app-server]: [OpenAI：Codex App Server](https://developers.openai.com/codex/app-server)，Overview、Steer an active turn、Interrupt a turn；读取于 2026-11-10。
[^openai-tools]: [OpenAI：Function calling](https://developers.openai.com/api/docs/guides/function-calling)，工具循环、Chat Completions 与 Responses 报文、reasoning items 保留、Streaming；读取于 2026-11-10。
[^openai-steering]: [OpenAI：Mid-turn steering](https://developers.openai.com/api/docs/guides/steering)，模型范围、accepted、自动续接、客户端工具 pending、失败与断线；读取于 2026-11-10。
[^openai-ws]: [OpenAI：WebSocket mode](https://developers.openai.com/api/docs/guides/websocket-mode)，`/v1/responses`、`response.create`、增量续接、`stream_id` 与恢复；读取于 2026-11-10。
[^openai-steer-type]: [OpenAI Python SDK：ResponseSteerEventParam](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/types/responses/response_steer_event_param.py)，支持范围、后继 response 提交点、输入限制与显式续接合并规则。
[^openai-steer-pending]: [OpenAI Python SDK：ResponseSteerPendingEvent](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/types/responses/response_steer_pending_event.py)，多个 steer 可共享所需结果，同一父 response 不重复续接；该文件在核验时从官方 main 读取，SDK 当时 HEAD 为所列提交。
[^claude-tools]: [Anthropic：Implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)，工具 schema、`tool_use`、`tool_result`、紧邻与块顺序约束；读取于 2026-11-10。
[^claude-stream]: [Anthropic：Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)，SSE 生命周期与 partial JSON；读取于 2026-11-10。
[^claude-mid]: [Anthropic：Mid-conversation system messages and tool changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)，When to use、Placement after tool results、Limitations；读取于 2026-11-10。
[^claude-threads]: [Anthropic：Message threads](https://platform.claude.com/docs/en/build-with-claude/message-threads)，重建会话与 Streaming 的 `message_stop` 续接条件；读取于 2026-11-10。
[^codex-admission]: Codex [`turn_processor.rs` L1072–1214](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/app-server/src/request_processors/turn_processor.rs#L1072-L1214) 与 [`turn_input.rs` L953–1046](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/turn_input.rs#L953-L1046)，目标核对、接受顺序与入队。
[^codex-loop]: Codex [`session/turn.rs` L536–690](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/turn.rs#L536-L690)，pending input、请求快照与 follow-up 条件。
[^codex-feature]: Codex [`features/src/lib.rs` L1355–1360](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/features/src/lib.rs#L1355-L1360)，`instant_interrupt` 的快照默认值和开发阶段；不代表某安装态实测。
[^codex-preempt]: Codex [`session/mod.rs` L4596–4603](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/mod.rs#L4596-L4603) 与 [`input_queue.rs` L321–341](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/input_queue.rs#L321-L341)，请求级 preempt token 与通知监听；同文件 L400–468 为入队与取出。
[^codex-sampling]: Codex [`session/turn.rs` L3011–3128](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/turn.rs#L3011-L3128)，响应流、在途工具、preempt 与 turn cancellation 分流。
[^codex-ws-drain]: Codex [`responses_websocket.rs` L254–381](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/codex-api/src/endpoint/responses_websocket.rs#L254-L381)，连接串行访问、Drain 与 Cancel 的区别。
[^codex-ws-type]: Codex [`codex-api/src/common.rs` L400–403](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/codex-api/src/common.rs#L400-L403) 的 WebSocket 请求枚举；[`core/src/client.rs` L1295–1315](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/client.rs#L1295-L1315) 展示 Responses 请求的实际构造。
[^codex-ui]: Codex [`chatwidget/input_flow.rs` L21–101](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/tui/src/chatwidget/input_flow.rs#L21-L101) 与 [`chatwidget/input_queue.rs`](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/tui/src/chatwidget/input_queue.rs)，提交、明确排队和 pending steer 分离。
[^codex-tests]: Codex [`pending_input.rs` L1881–1980](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/tests/suite/pending_input.rs#L1881-L1980)、[L2275–2403](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/tests/suite/pending_input.rs#L2275-L2403)、[L2424–2481](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/tests/suite/pending_input.rs#L2424-L2481)；被忽略的相关测试见同文件 L1222–1224。以上均为源码阅读，不是本次执行结果。
