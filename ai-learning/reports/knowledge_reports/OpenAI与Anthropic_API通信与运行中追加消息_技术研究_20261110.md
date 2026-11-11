---
title: "运行中追加消息与修改目标——OpenAI Responses、Claude Messages 和 Managed Agents 官方 API 对照"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-11"
semantic_tags: ["api_protocol", "responses_api", "messages_api", "managed_agents", "steering", "tool_use", "codex", "context_management"]
---

# 运行中追加消息与修改目标

OpenAI Responses 的 `response.steer` 允许用户在响应运行时补充信息、修改要求或改变方向。**Claude 也能接受新目标，但要分清调用的是哪个 API：直接使用 Messages 时，新目标随下一次请求进入；使用 Managed Agents 时，官方另有中断当前工作、随后按新消息继续的会话接口。**[^openai-steering][^claude-messages][^claude-managed]

| 官方接口 | 怎样提交用户更新 | 何时按更新继续工作 |
|---|---|---|
| OpenAI Responses WebSocket，`response.steer` | 向正在运行的 response 发送事件；限 GPT-6 系列及支持的执行配置 | 服务端排队，在规定输出边界结束原响应，再创建带更新的后继 response；缺客户端结果时等待回填 |
| Claude Messages，`POST /v1/messages` | 在下一次请求的 `messages` 中加入用户更新，并保留所需历史 | 下一次模型调用；当前文档未提供向已在生成的这次 Messages 响应追加输入的等价操作 |
| Claude Managed Agents，session events | 向运行中的 session 依次发送 `user.interrupt`、`user.message` | 中断生效后结束当前 turn，下一 turn 处理新消息；工具运行可能延迟中断生效 |

表中比较的是**接收更新与继续执行的契约**。同一句“先别修复，改为只分析原因”可以通过三条路径表达；差别在交接时机、状态管理和由谁发起后续推理。Claude 的普通 `user` 消息本来就能携带指令，不能把差异写成“OpenAI 能改目标，Claude 只能补背景”。[^claude-mid]

本文以 2026-11-11 读取的官方文档为依据，沿用同一个自拟例子：原任务是“定位并修复测试失败”，工作中追加“先别修复，改为只分析原因，不要修改文件”。如果追加的是“失败只出现在空列表输入”，那是补充事实；如果追加的是“改为只分析原因”，那是改变任务范围。接口都需要把更新交到后续判断中，原任务和已获得的测试结果仍应保留。

工具调用的完整报文与 SDK 循环另见[《OpenAI、Anthropic API 开发者中文译解》](./OpenAI与Anthropic_API开发者中文译解_请求与执行循环_20261110.md)。本文集中解释运行中追加，Codex 放在[文末补充](#codex-supplement)。

<a id="openai-steering"></a>

## 1. OpenAI：运行时接收更新，在后继 response 中应用

深入连接缓存、并发通道、分支等待和断线恢复，可继续读[《OpenAI Responses WebSocket 与 Steering：协议详解》](./OpenAI_Responses_WebSocket与Steering_连接续接与运行中改向_深度解析_20261111.md)。本节保留与 Claude 对照所需的主要契约。

### 哪些模型支持，什么时候加入的

官方 steering 指南写明：**GPT-6 系列支持，GPT-5.6 及更早模型不支持；传输必须使用 Responses WebSocket。** 普通 HTTP/SSE 请求与 Chat Completions 不能因此获得这个事件接口。官方更新日志在 **2026-09-03** 的 Responses 条目中加入 Mid-turn steering，与 GPT-6 Astra 发布同日。[^openai-steering][^openai-changelog]

当前 GPT-6 指南涉及的通用模型包括 GPT-6 Astra、GPT-6 Sol、GPT-6 Luna、GPT-6.1 Sol 和 GPT-6.1 Terra。这里采用官方的“GPT-6 系列”支持口径；第三方代理的别名、兼容端点和特殊执行模式仍需分别确认，模型名称相似不足以证明事件可用。[^openai-models]

模型支持还只是一个条件。当前官方 WebSocket 事件参考进一步限定为**支持 steering 的单 Agent response**，并排除绑定 `conversation` 或启用自动 compaction 的响应。这些是核验时的接口限制。[^openai-events]

### 从发送到应用，中间有哪些状态

先在 WebSocket 上发送 `response.create`。拿到 `response.created` 中的响应 ID 后，用户有更新时向**同一连接**发送：

```json
{
  "type": "response.steer",
  "previous_response_id": "resp_demo_1",
  "input": "先别修复，改为只分析原因，不要修改文件。"
}
```

这个事件只接受 `type`、`previous_response_id`、`input`。`input` 可以是字符串，或受支持的 user 消息数组；工具结果、system 消息和新的生成配置不属于它的输入。也不要添加 `stream_id`，目标 response 已确定所属通道。[^openai-events]

服务端接着发出 `response.steer.accepted`，用 `steer.id` 标识这条更新。**accepted 表示服务端接管并排队了输入；后继 response 的 `response.created` 才是文档规定的提交点。** 从提交点可以确认更新进入了后继响应，是否正确完成新目标还要看后续输出与行动。[^openai-events]

没有客户端工具结果或审批阻塞时，过程如下：

```text
response.create → resp_1 开始工作
                        │
用户更新 → response.steer → response.steer.accepted
                        │
        完成当前输出 item 和已经运行的托管工具工作
                        │
                 resp_1 结束
                        │
        服务端自动创建 resp_2，带入更新
                        │
                 resp_2 按新目标继续
```

这里的输出 item 是协议中的输出条目，不是任意一个 token。若 steering 使原响应提前结束，会收到 `response.incomplete`，其中 `incomplete_details.reason` 为 `steered`；若原响应先正常完成，可以保留 completed 状态，再进入后继响应。客户端要继续读事件，不能把原响应结束当成整个任务结束。[^openai-steering]

自动后继响应继承原请求设置。此时由服务端发起续接，客户端不用再创建一次。收到后继 `response.created` 后，下一条 steer 应改用后继响应的 ID。各 response 分别计算 token 和工具调用上限；应用若需要整项任务的总预算，要另外累计。[^openai-steering]

### 需要客户端工具结果时，怎样继续

假设 `resp_1` 已请求应用执行 `read_test`。用户的新要求可以先被接受，但服务端仍需要那次调用的结果。原响应完成后，可能收到如下事件；示例 ID、工具名与结果均为自拟：

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

应用用 `call_id` 找到已执行调用的结果，在同一连接、对应通道发送显式 `response.create`。下面展示相关字段；这次请求需要的指令、工具等设置由应用一并提供：

```json
{
  "type": "response.create",
  "model": "gpt-6-astra",
  "previous_response_id": "resp_demo_1",
  "instructions": "你是代码助手。根据用户当前要求继续工作。",
  "input": [{
    "type": "function_call_output",
    "call_id": "call_demo_read",
    "output": "合成结果：测试期望空列表，实际返回 null。"
  }]
}
```

服务端会把已接受的 steer 按提交顺序放到这次新增 `input` 前面。应用**不用再复制用户更新**，也不应因为多个 pending 通知指向同一个工具，就重新执行它或按每条 steer 分别续接。同一父 response 所需的结果由一次匹配的显式请求提交；与自动续接不同，显式请求使用自己的设置。[^openai-events]

`response.steer.pending` 是提醒，不是返回工具结果的前置许可。若应用已经及时发出了匹配的 `response.create`，服务端可以直接继续，不先发送该通知。[^openai-steering]

### 失败、断线和已经执行的动作

`response.steer.failed` 表示更新未通过 steering 应用，服务端也不会稍后自动应用它；事件带回未提交的输入和错误。应用应按 `steer.id` 关联此前的接受记录，处理不支持的模型、无效输入或过期目标等具体原因。[^openai-events]

待处理 steering 只存在于当前连接，不随原 response 持久保存。断线后，要用应用保留的更新记录对照已收到的响应和历史，再决定如何恢复。**已接受、已提交、已完成目标**应当分别记录。[^openai-steering]

官方同时明确：steering 不会改写已经发出的输出、撤销先前动作或取消已经开始的工具。因此，“不要修改文件”影响后续判断；它本身不构成对已开始写入的回滚保证。[^openai-steering]

<a id="claude-messages"></a>

## 2. Claude Messages：新目标随下一次请求进入

### 普通用户消息就可以改变目标

Messages 的普通多轮调用由应用提交所需会话历史，再加入新的用户消息。官方指南把它与负责会话执行的 Managed Agents 分开说明。当前 Messages、Threads 与中途 system 消息文档**没有给出向正在生成的那次 Messages 响应发送 steer 的等价操作**；这一定义范围不包括后文的 Managed Agents。[^claude-messages][^claude-threads]

对示例任务，应用可以在收到更新时记下“只分析原因”，然后在下一次 `POST /v1/messages` 中提交。若模型上一轮请求了客户端工具，合法的 `messages` 数组可包含如下内容；这里只展示一个简化的工具回合：

```json
[
  {
    "role": "user",
    "content": "定位并修复测试失败。"
  },
  {
    "role": "assistant",
    "content": [{
      "type": "tool_use",
      "id": "toolu_demo_read",
      "name": "read_test",
      "input": {"path": "tests/demo.py"}
    }]
  },
  {
    "role": "user",
    "content": [
      {
        "type": "tool_result",
        "tool_use_id": "toolu_demo_read",
        "content": "合成结果：测试期望空列表，实际返回 null。"
      },
      {
        "type": "text",
        "text": "先别修复，改为只分析原因，不要修改文件。"
      }
    ]
  }
]
```

新调用同时拿到原任务、工具调用、执行结果和用户改目标的原话。已查出的失败现象仍能用于分析，修复动作则不再属于用户当前要求。真实调用须保留返回消息中按协议需要继续携带的内容，不能只挑可见文本或一个 `tool_use` 块复制。

工具结果通过 `tool_use_id` 配对，结果消息紧接对应的 assistant 工具请求；同一 user 消息里，工具结果放在其他文字之前。不能把一条单独的用户更新夹进尚未配对的工具请求与结果之间。[^claude-tools]

在这个过程中，用户可以在应用界面随时输入，应用也可以立即收下；模型读到更新的时间取决于下一次调用。流式 SSE 负责向应用输出事件，并未提供修改已发送请求体的输入通道。`content_block_delta` 或 `input_json_delta` 等也是模型输出事件，后者传的是工具参数片段。[^claude-stream]

### 中途 system 消息解决什么问题

支持的模型允许在 `messages` 中加入 `role: "system"`，把后来才出现的运行规则放在会话的相应位置。它随**携带它的新请求**进入模型，从该位置往后适用；例如应用运行模式改成只读，或者新增一条操作者约束。[^claude-messages]

官方解释的重点是**指令权限和缓存**：普通 user 消息也可以下指令；system 消息代表应用操作者，冲突时有更高优先级。把新的操作者规则追加在历史末尾，还能保留之前未改变的缓存前缀，避免改写顶层 `system`。实际缓存命中仍受缓存配置、前缀匹配和最小长度等条件影响。[^claude-mid]

如果应用转述的是本次对话用户的更新，应说明用户改变了什么，例如“用户刚将任务改为只分析原因，不再要求修复”。文档要求按事实转述，不使用“忽略用户”一类表述。这里的“作为上下文转述”，不等于禁止用户改变目标。来自工具、检索网页和第三方文档的文本仍放在相应数据内容中，不升级为 system 指令。[^claude-mid]

<a id="claude-system-support"></a>

2026-11-11 读取的指南正文列出以下中途 system 消息支持范围：

| 模型 | `messages` 中途 `role: "system"` |
|---|---|
| Claude Fable 5、5.1、5.2 | 支持 |
| Claude Mythos 5、5.1、5.2 | 支持 |
| Claude Opus 4.8、5、5.5 | 支持 |
| Claude Sonnet 5.5、Haiku 5.5 | 支持；用户原话另按下面的位置规则传递 |
| Claude Sonnet 5 | 指南明确不支持；操作者指令使用顶层 `system` |

这张表仅说明**中途 system 消息**这项能力，不是能否接收普通后续 user 消息的模型名单。基础中途 system 消息无需 beta header；`clear_at`、工具变更等扩展有各自的 beta 条件，不能合并成同一项支持结论。[^claude-mid]

位置也受约束：带内容的 system 消息紧随 user turn，或文档允许的以服务端工具结果结束的 assistant turn；之后是 assistant turn 或数组结束。它不能放在 `messages` 第一项，也不能夹在工具请求与结果之间。[^claude-messages][^claude-mid]

对 **Sonnet 5.5 与 Haiku 5.5**，官方具体要求把用户原话放在同一 user 消息里、最后一个 `tool_result` 后的 `text` 块中，正如上面的例子。Harness 自己的提醒另放 system 消息。文档解释，这两类模型可能把紧跟工具结果的 system 转述当成不可信注入，因此不能把用户原话和 Harness 提醒混写。[^claude-mid]

### Threads 能续接历史，但要等这次 message 结束

Message Threads 可以由服务端保存会话，使后续请求只发送新增消息。流式调用在 `message_start` 就返回 message ID，但官方要求**收到 `message_stop` 后才能从这个 ID 续接**；提前继续可能返回 404。[^claude-threads]

因此，这几件事要分别理解：普通 user 消息表达新目标；中途 system 消息表达后来加入的操作者规则；Threads 减少历史重传。三者都可以参与后续请求，但都不由此提供修改当前生成的 steer 事件。

<a id="claude-managed-agents"></a>

## 3. Claude Managed Agents：官方另有运行中改向接口

Managed Agents 是 Anthropic 托管 Agent 执行循环的 API。应用操作一个 session，由服务端管理其中的模型调用、工具工作和会话事件；与自己调用 Messages、自己维护工具循环相比，责任边界不同。当前文档将它标为 beta，使用 `managed-agents-2026-04-01`。[^claude-messages][^claude-managed]

官方的“Interrupt the agent”示例明确给出了运行中改方向的方法：先发 `user.interrupt`，再发 `user.message`。下面只展示已经建立 session 后要提交的事件，文字改为本文的任务：

```python
client.beta.sessions.events.send(
    session.id,
    events=[
        {"type": "user.interrupt"},
        {
            "type": "user.message",
            "content": [{
                "type": "text",
                "text": "先别修复，改为只分析原因，不要修改文件。",
            }],
        },
    ],
)
```

**调用返回只表示事件入队。** `user.interrupt` 的 `processed_at` 在尚未处理时为 `None`。官方列出的执行顺序是：

1. Agent 应用中断。中断作用到正在生成的模型响应时，该响应立即停止；若工具正在运行，中断可能要更久才能生效。
2. 事件流出现 `user.interrupt`，被中断的 turn 结束，通常发出 `session.status_idle`。
3. Agent 开始下一 turn，处理紧随其后的 `user.message`。[^claude-managed]

这里的 idle 原因仍可为 `end_turn`，与自然结束相同，判断是否由用户中断要结合事件记录。若有未结束的 workflow runs，中断不会结束这些 run；仍在运行的 run 可以使 session 保持 `running`，上面第二步的 idle 事件也可能不出现。[^claude-managed]

这条路径确实支持用户在 Agent 工作期间改目标，同时明确结束当前 turn、用下一 turn 处理更新。它与 OpenAI 在输出边界创建后继 response 的契约各有状态和时机，不能把两套事件一一替换。对于运行中单独发送普通 `user.message` 的所有调度细节，本文不作额外推演；明确需要中断并改向时，采用官方上述序列。

Managed Agents 还支持向适用模型发送 `system.message`，追加从当前相关 turn 起生效的操作者上下文。它不替换 agent 定义中的顶层 `system`；后者也不能借此实时改写。本次核验时，其支持模型与[上面的中途 system 消息名单](#claude-system-support)一致；不能从 session 支持 `user.interrupt` 推出所有模型都支持 system 注入。若 session 因 `requires_action` 等待工具结果，`system.message` 必须在同一请求中跟在工具结果事件之后，不能单独发送来跳过待处理工具。[^claude-managed]

<a id="application-boundaries"></a>

## 4. 接口收到“不要改文件”之后，应用还要判断什么

以本文的改目标消息为例，保留历史意味着后续模型还能利用已读到的测试结果，同时知道当前只需分析。保留历史不要求原目标永远不变，也不意味着模型参数记住了这个私有任务。应用或服务端把所需材料交给下一次推理，才形成可续接的工作。

实现时尤其要区分工具执行状态。尚未开始的写入，可以由应用根据新要求停止调度；已经开始的工具，要按执行器实际提供的取消能力处理；已经写入的文件，需单独判断是否及如何恢复。**这是根据接口边界得出的应用设计建议**：不要用“消息已接受”代替工具状态判断。OpenAI steering 明确不取消已开始工具，Claude Managed Agents 也提示运行中工具可能延迟中断。[^openai-steering][^claude-managed]

同样，一条更新进入后继请求，不证明模型已经正确执行它。若要核验这项行为，观察的应是更新所关联的 response/message/turn、后续工具调用与实际结果。无须由聊天框是否清空、输出是否连续来猜测所用协议。

<a id="codex-supplement"></a>

## 5. 补充：Codex `turn/steer` 属于 Agent 接口

Codex app-server 的 `turn/steer` 给活动 Agent turn 追加用户输入，使用 `threadId` 和 `expectedTurnId` 定位。成功后不产生新 `turn/started`；无活动 turn 或目标不匹配会失败，也不能通过它切换模型、工作目录或沙箱设置。[^app-server]

它的目标是 **Agent turn**，OpenAI Responses `response.steer` 的目标是**模型 response**。一个 Agent turn 可以含多次模型调用和工具执行，因此 Codex 能追加输入，不足以证明底层模型支持原生 `response.steer`，也不足以说明当前客户端实际发送了这个事件。

旧稿核验的 Codex 源码固定为 `39b42aaacdbb55b86528b4294443696985c348ee`。保留与这个区分直接相关的证据：

| 固定快照中的位置 | 读到的机制 |
|---|---|
| `session/turn_input.rs` | 核对活动 turn 与目标，将接受的用户输入加入 `pending_input`。[^codex-admission] |
| `session/turn.rs` 的调用循环 | 构造下一次模型请求前，将 pending input 记入历史并创建请求快照；有待处理输入时仍可继续采样。[^codex-loop] |
| 采样与 WebSocket 控制路径 | 区分请求抢占、drain 与整个 turn 的取消，具体行为受配置和工具类型影响。[^codex-sampling][^codex-ws-drain] |
| WebSocket 请求类型与客户端构造 | 所查路径不能证明 `turn/steer` 被直接转发成公开 `response.steer`。[^codex-ws-type] |

这些证据解释了 Harness 怎样调度输入，适用范围是所列源码快照。当前安装包、模型路由或客户端的真实网络行为，需要另行观测；不从这个快照推断。本文也不使用 Claude Code 的键盘或排队行为代替 Claude API 契约。

<a id="sources-and-verification"></a>

## 来源、实验与本次修订范围

2026-11-11 修订将官方 API 放到正文主线，补充 OpenAI 支持范围与发布日期、Claude 改目标的消息语义、Managed Agents 中断后继续的流程。旧标题《管家怎样把新纸条递给正在工作的鹦鹉？》不再使用，文件路径保留以维持已有链接；通用工具报文的展开入口移至开发者译解。

本次重新读取了 steering 指南、OpenAI WebSocket 事件参考、更新日志与模型指南，以及 Claude Messages、中途 system、Threads、Managed Agents 事件页和 Codex app-server 文档。工具与流式基础沿用 2026-11-10 读取的官方资料。旧稿使用的 [OpenAI Python SDK 类型快照](https://github.com/openai/openai-python/blob/13c000d1f32c1e3e3c4b3e16bc6b956dfd4f5216/src/openai/types/responses/response_steer_event_param.py)仍可追溯，本次涉及的 steering 字段及配置限制已改由官方事件参考直接核对。

既有离线实验 [api_turn_lab.py](./assets/api_communication_20261110/api_turn_lab.py) 与[归档结果](./assets/api_communication_20261110/results.json)保留。2026-11-10 的记录为 12 项测试通过，覆盖请求快照、输入顺序、工具配对，以及模拟的 accepted/pending/续接关系。它是手写教学状态机；`queued`、`logical_new_input` 是教学观测字段，不是官方事件字段。复现命令如下，不会联网或覆盖归档结果：

```bash
python3 -I ai-learning/reports/knowledge_reports/assets/api_communication_20261110/api_turn_lab.py
```

该实验没有实现 Claude Managed Agents，也没有验证任何模型的真实兼容性或指令遵循。本次修改正文与引用，未改实验代码。未调用付费模型，未抓取个人会话，未运行 Codex 上游测试；报告的 completed 状态表示本次文档研究已完成，不代表线上集成测试通过。

[^openai-steering]: [OpenAI：Mid-turn steering](https://developers.openai.com/api/docs/guides/steering)，支持范围、运行中更新、输出边界、续接与连接恢复；读取于 2026-11-11。
[^openai-events]: [OpenAI：Responses WebSocket events](https://developers.openai.com/api/reference/resources/responses/websocket-events)，`response.steer`、accepted、pending、failed、输入字段与配置限制；读取于 2026-11-11。
[^openai-changelog]: [OpenAI：Changelog](https://developers.openai.com/api/docs/changelog)，2026-09-03 的 Responses 新增控制条目；读取于 2026-11-11。
[^openai-models]: [OpenAI：Using GPT-6](https://developers.openai.com/api/docs/guides/latest-model)，GPT-6 系列与 Mid-turn steering；读取于 2026-11-11。
[^claude-messages]: [Anthropic：Using the Messages API](https://platform.claude.com/docs/en/build-with-claude/working-with-messages)，Messages 与 Managed Agents 的分工、多轮历史、System role in messages；读取于 2026-11-11。
[^claude-mid]: [Anthropic：Mid-conversation system messages and tool changes](https://platform.claude.com/docs/en/build-with-claude/mid-conversation-system-messages)，权限与缓存、支持模型、用户输入转述及位置限制；读取于 2026-11-11。
[^claude-threads]: [Anthropic：Message threads](https://platform.claude.com/docs/en/build-with-claude/message-threads)，Streaming 的 `message_stop` 续接条件；读取于 2026-11-11。
[^claude-managed]: [Anthropic：Session event stream](https://platform.claude.com/docs/en/managed-agents/events-and-streaming)，Send events、Interrupt the agent、Send system messages；读取于 2026-11-11。
[^claude-tools]: [Anthropic：Implement tool use](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)，`tool_use`、`tool_result`、紧邻与块顺序约束；读取于 2026-11-10。
[^claude-stream]: [Anthropic：Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)，SSE 生命周期与 partial JSON；读取于 2026-11-10。
[^app-server]: [OpenAI：Codex App Server](https://learn.chatgpt.com/docs/app-server)，Steer an active turn；读取于 2026-11-11。
[^codex-admission]: Codex [`turn_input.rs` L953–1046](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/turn_input.rs#L953-L1046)，目标核对、接受顺序与入队；沿用旧稿固定快照。
[^codex-loop]: Codex [`session/turn.rs` L536–690](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/turn.rs#L536-L690)，pending input、请求快照与 follow-up 条件；沿用旧稿固定快照。
[^codex-sampling]: Codex [`session/turn.rs` L3011–3128](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/session/turn.rs#L3011-L3128)，响应流、在途工具、preempt 与 turn cancellation 分流；沿用旧稿固定快照。
[^codex-ws-drain]: Codex [`responses_websocket.rs` L254–381](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/codex-api/src/endpoint/responses_websocket.rs#L254-L381)，Drain 与 Cancel；沿用旧稿固定快照。
[^codex-ws-type]: Codex [`codex-api/src/common.rs` L400–403](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/codex-api/src/common.rs#L400-L403) 的 WebSocket 请求枚举与 [`core/src/client.rs` L1295–1315](https://github.com/openai/codex/blob/39b42aaacdbb55b86528b4294443696985c348ee/codex-rs/core/src/client.rs#L1295-L1315) 的请求构造；沿用旧稿固定快照。
