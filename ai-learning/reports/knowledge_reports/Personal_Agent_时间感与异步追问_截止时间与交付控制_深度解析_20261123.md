---
title: "有截止时间的 Personal Agent：异步追问、时钟提醒与交付控制"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
report_depth: "deep"
source_url: "https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents"
source_published_on: "2026-11-20"
updated_on: "2026-11-26"
semantic_tags: ["personal-agent", "agents-api", "responses-api", "async-tool-calling", "deadline", "steering"]
---

# 有截止时间的 Personal Agent：异步追问、时钟提醒与交付控制

## 概述

OpenAI 用会前简报说明，助手可以边追问边调研，但到追问期限要结束等待，到交付期限要送出可用产物。模型获得时间信息，应用负责后台函数、回复绑定、计时与收尾。

Agents API 与自行维护的 Responses 循环承担不同工作。回复到了应用，不代表当前响应已看见；异步工具、steering、事件唤醒和后台生成必须按依赖与生效时机区分。 [原文](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents)

**提炼句：** 能继续做的先做，必须等的仍等；截止时间由执行程序守住。

## 取景框 f(x)

**x｜问题：** 助手边调研边追问时，怎样接回用户回复，又保证简报到点交付，不把沉默或请求已接受误当作完成？

**f｜取景框：** 从依赖关系和固定预算看助手：独立工作与待回结果可以并行，依赖结果的判断仍要等待。模型规划与应用控制分别处理怎样分配时间、何时停止等待。

**f(x)｜判断变化：** 追问截止与交付截止要分开，原调用 ID 与最新续接状态也要分开。沉默只能触发已定义的降级，不能生成授权；已完成文字还要对应可用简报。

## 先把“十五分钟”拆成三个时刻

原文的会议在 16:15 开始，简报在 16:12 交付，未回答的问题在 16:10 关闭。三个时刻解决的问题不同：

| 时刻 | 应用需要作出的动作 | 理由 |
| --- | --- | --- |
| 16:10：追问截止 | 对仍未回答的问题返回明确的无回答结果 | 留出最后两分钟整理简报 |
| 16:12：交付截止 | 停止继续等新结果，交付已完成的简报或说明材料不足 | 保住用户阅读时间 |
| 16:15：会议开始 | 用户开始使用简报 | 这是任务服务的最终目的 |

16:10 不是用户默认同意某个选项的时刻。它只是应用不再为这次简报等待可选信息的时刻。原文选择在无回复时覆盖两种会议目标，是这个调研任务的降级办法；购买、发消息或提交合同等动作，仍须满足各自的授权条件。[原文：Return the tool result](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#return-the-tool-result)

应用要在任务开始时，把“十五分钟后”“提前三分钟”换成固定的绝对时间。不能每次继续调用模型时重新计算“现在起十二分钟”，否则一个不断续接的任务可以永远不超时。

这里还需要两种时钟。发给模型的 UTC 时间便于它理解会议安排；应用内部用单调时钟计算已过去多久，避免系统校时把期限往后移动。原文 Python 示例将 `datetime.now(UTC)` 用于提示，将事件循环的 `loop.time()` 与 `asyncio.timeout_at()` 用于超时。时钟提醒改变模型接下来怎样分配工作，计时器改变应用是否继续等下去。[原文：Responses 循环示例](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#time-awareness-in-a-responses-api-loop)

## 模型继续工作，函数仍由应用执行

普通函数调用需要结果才能继续相应的模型工作。把函数定义中的 `async` 设为 `true` 后，模型可以先提出调用，再处理不依赖结果的部分。应用负责启动后台工作、保存状态、收集结果；这个设置不会把你的函数搬到 OpenAI 的服务器，也不会替你管理任务队列。[Async tool calling](https://developers.openai.com/api/docs/guides/async-tool-calling#how-async-tools-work)

例如，助手一边查公司公告，一边问“这次会议主要谈技术还是价格”。查到的产品信息可以先整理；只有决定简报的侧重时，才需要把用户回答纳入判断。异步化的价值来自这种依赖关系，而不是函数名字中出现了 `async`。

官方文档还专门说明：`request_user_input_async` 和 `wait_for_tasks` 都是应用可以定义的函数名称，**不是 Responses API 的内置工具**。应用要实现问卷、输入框、超时和等待行为。它可以给后台任务分配 `task_handle`，再把这个业务句柄绑定到 API 的原始 `call_id`。[追问工具](https://developers.openai.com/api/docs/guides/async-tool-calling#add-a-tool-to-ask-the-user-for-input)、[等待工具](https://developers.openai.com/api/docs/guides/async-tool-calling#add-a-wait-tool)

几个能力容易被混在一起，实际作用如下：

| 能力 | 谁在等待、谁继续工作 | 当前官方说明中的边界 |
| --- | --- | --- |
| Async tool calling | 应用函数在后台执行，模型可处理独立部分 | 适用于应用执行的 function/custom 工具，托管内置工具不因此变成异步函数 |
| Background mode | 响应生成作为后台任务运行 | 与函数结果是否阻塞模型是不同问题 |
| Mid-turn steering | 用户把新要求交给正在运行的响应 | Responses WebSocket 的单独协议；输入接受后还要等服务处理续接 |
| Agents API time awareness | 托管 harness 给模型周期性时间提醒 | 博客以 `experimental.time_awareness: true` 启用；应用仍须负责交付期限 |

2026-11-23 的异步工具文档将兼容性表述为“GPT-6 Astra 及后续模型”，没有给出逐型号的完整矩阵；博客使用 `gpt-6.2-astra`。不能据此把所有老模型或第三方模型都列为支持。Steering 文档另行规定 GPT-6 家族通过 Responses WebSocket 支持，GPT-5.6 及更早型号不支持。两个功能的支持范围要分别查。[异步工具兼容性](https://developers.openai.com/api/docs/guides/async-tool-calling#compatibility)、[Steering](https://developers.openai.com/api/docs/guides/steering)

## Agents API：一次追问怎样走完

博客先保存一个 agent 配置：选择模型、启用 `experimental.time_awareness`，添加实时 `web_search`，再定义一个 `async: true` 的追问函数。随后创建 session，传入公司、会议时间和简报期限。这里的 agent 保存可复用配置，session 保存这一份工作及其对话；更新保存的 agent 并不会自动改变已有 session 的配置。[原文：Create the agent](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#create-the-agent)、[配置与更新](https://developers.openai.com/api/docs/guides/agents-api/configuration#update-a-saved-agent)

实际收发需要这样串起来：

1. 应用消费 session 事件流。
2. 收到 `agent.session.turn.item.done`，检查完整 item 是否是指定的追问函数调用。
3. 保存 `session_id`、`turn_id`、`call_id`，展示问题并启动独立输入处理器。
4. 继续消费事件，让调研和用户输入同时推进。
5. 用户回答或追问到期时，通过 session events endpoint 返回原调用的结果。

博客明确提醒，`required_actions` 描述的是阻塞动作。只等那里出现追问，可能遗漏异步问题。另一方面，普通 Functions 文档要求从 `required_actions` 确认哪些阻塞调用确实还在等结果；历史中出现过一个函数 item，并不证明现在仍有待处理动作。这两段文档适用的场景不同。[原文：Display a pending question](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#display-a-pending-question)、[Functions](https://developers.openai.com/api/docs/guides/agents-api/tools/functions#handle-required-actions)

因此，应用应把异步问题登记为自己的待办记录，并在解决或关闭后保留完成标记。重放同一个事件时，不应再弹一个输入框；一个已经过期的问题，也不能被迟到回复重新变成另一份答案。跨 session 复用注册表时，键要包含 session 和 turn，不能只拿显示文本或列表位置做绑定。

返回结果使用 `agent.session.input.tool_result`。其中 `turn_id` 和 `call_id` 标识原调用，`success` 描述函数处理是否成功，`output` 承载业务结果。原文在用户未回答时仍设置 `success: true`，因为输入处理器成功完成了超时流程；内容里明确说明 `status: "no_answer"`。这与“用户同意了”没有关系。[返回工具结果](https://developers.openai.com/api/docs/guides/agents-api/tools/functions#return-the-result)

session 事件接口的 HTTP 202 只确认接受，不能作为工具结果已被持久处理或整份任务已完成的证据。应用还要继续看事件与保存的工作状态。对于有副作用的函数，官方建议按 session、turn 和 call ID 持久保存执行结果；结果未保存而执行可能已经发生时，先查实际结果，再决定是否重跑。[事件接口](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/subresources/events/methods/create)、[断线后恢复函数](https://developers.openai.com/api/docs/guides/agents-api/tools/functions#recover-after-a-disconnect)

## Responses API：回复回来的时间，与模型看见它的时间

自行维护 Responses 循环时，应用得把时间与结果接入每一次请求。博客的请求辅助函数先算剩余时间，再将当前 UTC 时间作为 developer message 放入 `input`；原始期限仍保留在对话历史中。初始请求、继续调研和提交工具结果，都经过同一个辅助函数。[原文：Add the current time before every model request](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#time-awareness-in-a-responses-api-loop)

这里最容易弄错的是两种 ID：

| 字段 | 绑定什么 | 如何更新 |
| --- | --- | --- |
| `call_id` | 这份函数结果回答哪一次调用 | 始终使用原调用的 ID |
| `previous_response_id` | 新请求接在哪一份对话状态后面 | 使用最新完成的响应 ID |

假设追问发生在响应 A，随后调研继续产生了响应 B。用户此时回答，结果仍使用 A 中的原 `call_id`；新的请求却应该接在 B 后面。回到 A 续接，会把后续已有工作从这条续接链中漏掉。[Async tool calling：Call an async tool](https://developers.openai.com/api/docs/guides/async-tool-calling#call-an-async-tool)

博客中的 Python 循环在完整函数 item 到达时启动输入处理器，继续读取当前响应；当前响应完成后，收集已经准备好的工具结果并发起下一次请求。因此，“用户在响应生成途中回答了”和“当前这次响应已经吸收了回答”不能画等号：**在这个实现里，回答进入下一次请求。**

如果用户要在响应尚未结束时修改要求，应另外使用 Steering 支持的传输与事件。`response.steer.accepted` 表示排队；服务会完成当前 output item 和已运行的托管工具工作，然后建立带新要求的自动续接。Steering 不撤回已经送出的输出，也不撤销已经启动的工具动作。[Steering：Send a steering message](https://developers.openai.com/api/docs/guides/steering#send-a-steering-message)

下一步是否能做，要按依赖判断。整理已取得的公司公告可以继续，比较两份尚未返回的报价则仍需等待。应用定义的同步 wait 函数结束时，应先交回各原调用的实际结果，再交回 wait 自身的完成状态，让模型先获得判断依据。允许继续工作，没有改变结果尚未取得这一事实。[等待结果的顺序](https://developers.openai.com/api/docs/guides/async-tool-calling#deliver-results-before-wait-status)

## 怎样交付一份真正完成的简报

事件流中的一段文字可能只是进度说明。Agents API 的博客示例筛选 `role: assistant`、`status: completed`、`phase: final_answer` 的消息，在 root turn 完成后读取保存的 items。列表有分页，不能拿第一页没看到答案当作不存在；断线时也要从保存的状态恢复，而不是把连接关闭当作任务完成。[原文：Retrieve and deliver the answer](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#retrieve-and-deliver-the-answer)、[Events and items](https://developers.openai.com/api/docs/guides/agents-api/sessions/events#fetch-items-and-turns)

原文的 Responses 示例允许 `phase` 为 `None` 或 `final_answer` 的已完成 message，而 Agents API 示例要求明确的 `final_answer`。接入时应使用各自的消息合同，不能给所有接口套同一个字符串筛选规则。

到交付期限，应用做三件事：停止继续等待正在运行的生成；交付最近一份已完成的简报，或说明没有可用材料；关闭尚未解决的输入处理器，再处理会话、保存响应和后台资源的清理。原文 Python 示例用外层 `asyncio.timeout_at()` 覆盖整个循环，包括请求和事件消费，不只是给每一次 HTTP 请求单独设置超时。[原文：Enforce delivery while a request is in flight](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents#time-awareness-in-a-responses-api-loop)

取消也有层次。关闭客户端 stream 是停止本地读取；向 session 发 `agent.session.input.cancel` 才是在请求取消活动 turn；应用自己启动的函数还需要它自己的取消或结果查询机制。官方事件接口说明取消会保留已保存结果、已发布文件和已有终端执行结果。不能把取消当成事务回滚。[Session 输入事件接口](https://developers.openai.com/api/reference/resources/beta/subresources/agents/subresources/sessions/subresources/events/methods/create)

“最后一份已完成消息”确认的是生成状态。交付简报时，还要确认它覆盖任务要求、依据对应实际资料；否则，筛选出完整消息也可能交出内容不合格的简报。

## 用算例检查期限与结果绑定

[controller.py](./examples/personal-agent-time/controller.py) 是自拟的虚拟时间程序。它不复刻 OpenAI 服务，只验证应用能直接控制的规则：

| 情形 | 实际检查结果 |
| --- | --- |
| 用户在截止前回答 | 原调用收到 `answered`，内容保留 |
| 到期未回答、恰在到期时提交、迟到回复 | 返回一次 `no_answer`，迟到内容不覆盖它 |
| 函数事件与回答重放 | 不重复登记或完成同一个问题 |
| 把回复发到另一个 session | 拒绝错误绑定，原问题仍待答 |
| 生成在交付时仍未结束 | 交付已保存的完成稿，拒绝晚到替换 |
| 只有半段文本或 analysis 消息 | 不把它们交付为最终简报 |
| 旧响应中的调用后来返回结果 | 使用原 `call_id`，从最新响应继续；确认后不再重复提交 |
| 问题到期但购买未获授权 | 权限仍关闭 |
| 显示时钟被向后校正 | 已固定的单调时间期限不延长 |

执行 `python3 ai-learning/reports/knowledge_reports/examples/personal-agent-time/controller.py`，10 个场景全部通过。程序把构造结果批次与确认提交分开，但没有模拟网络提交结果不明、持久数据库或服务端幂等处理；这些仍是实际接入时需要验证的部分。没有测量模型在时间提醒下的能力变化，也没有测量用户等待减少多少。

**资料范围：** 接口说明依据官方博客及关联文档，以 2026-11-23 的资料为准。离线算例检查应用控制规则，不测量模型能力或线上 API 效果。
