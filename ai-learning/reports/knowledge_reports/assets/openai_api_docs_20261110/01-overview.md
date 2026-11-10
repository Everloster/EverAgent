# Overview｜入门与核心概念

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md) · [官方 API Docs](https://developers.openai.com/api/docs)

本卷从第一次 API 请求讲起，说明模型怎样接收输入、保存会话、返回流式结果，以及工具运行期间怎样接收补充要求。每个条目都附有对应的官方页面。

## Get started｜开始使用

<a id="doc-241"></a>
### Developer quickstart｜开发者快速开始

[原文](https://developers.openai.com/api/docs/quickstart)

调用 OpenAI API，先在控制台创建 API key，把它放入本机环境变量，再安装所用语言的官方 SDK。SDK 会从环境中读取密钥。随后通过 Responses API 发送输入、指定模型，读取返回的结果。

快速开始提供 JavaScript、Python、.NET、Java、Go、Ruby 和终端示例。在第一次文本请求之后，可以继续尝试图像与文件输入、内置工具、流式输出和 Agents SDK；各项能力的详细用法见后面的专题。

<a id="doc-11"></a>
### Key concepts｜关键概念

[原文](https://developers.openai.com/api/docs/concepts)

文本生成模型根据输入生成输出。输入通常称为 prompt，可以包含指令、材料和示例。设计 prompt，就是说明希望模型完成什么，以及合格的结果应当是什么样子。

Embedding 是内容的向量表示，常用于搜索、聚类、推荐和分类。Token 是模型处理内容的单位：一个词可能拆成多个 token，标点和部分词语也可能单独计数。生成模型的上下文窗口需要容纳输入和输出；embedding 模型则有输入长度限制。

<a id="doc-25"></a>
### API credits for ChatGPT subscribers｜ChatGPT 订阅者的 API 赠额

[原文](https://developers.openai.com/api/docs/guides/chatgpt-api-credits)

符合条件的 ChatGPT Pro 和 Business 订阅可以领取 API 赠额。领取时，将订阅关联到自己拥有的 API organization；后续符合资格的账期会自动发放，未用完的额度在账期结束时到期。首次领取按本期剩余时间折算。

领取资格涉及付费订阅状态、组织所有者身份和账号邮箱。赠额抵扣的是关联组织的合资格 API 消费，不增加 ChatGPT 或登录态 Codex 的额度，也不覆盖通过 API key 使用 Codex 的这项消费。各档金额、组织上限和到期规则见原文表格。

## Core concepts｜核心概念

<a id="doc-126"></a>
### Responses API / Migrate to the Responses API｜Responses API 与迁移

[原文](https://developers.openai.com/api/docs/guides/migrate-to-responses)

OpenAI 推荐新项目使用 Responses API，Chat Completions 仍受支持。Responses 把文本消息、推理信息、工具调用和工具结果分别表示为有类型的 Item，统一放在输入或输出序列中。

迁移时，调用入口改为 `/v1/responses`，`messages` 改为 `input`，`choices[].message` 改为 `output`；结构化输出配置由 `response_format` 移到 `text.format`。函数调用与返回值通过 `call_id` 配对。Responses 没有 Chat Completions 的 `n` 参数。多轮会话可以自行保存历史，也可以用 `previous_response_id` 续接；使用后者时仍要为新请求提供所需的 `instructions`。

<a id="doc-75"></a>
### Decisions｜结构化决策

[原文](https://developers.openai.com/api/docs/guides/decisions)

Decisions API 根据同一份文本、图像、JSON 或对话记录，回答一组预先定义的问题。请求的 `model` 指定模型，`input` 提供共用材料，`questions` 列出要判断的问题。每个问题有独立的 `name`，返回答案沿用它配对。

`predicate` 判断条件成立的概率；`choice` 从给定类别中选择；`score` 根据有序等级计算概率加权分数。请求可以共用输入、缓存重复材料，也可以为问题提供参考图像。它适合分类、路由和优先级判断。需要按自定义 JSON schema 生成字段或文字说明时，使用 Responses 的 Structured Outputs。

<a id="doc-65"></a>
### Conversation state｜会话状态

[原文](https://developers.openai.com/api/docs/guides/conversation-state)

多轮会话需要把先前的信息提供给后续请求。可以由应用重发历史，用 Conversations API 保存一个可持续引用的 conversation，或用 `previous_response_id` 连接前后两次响应。

自行保存历史时，应保留完整的 `output` 条目，包括推理条目和 assistant 消息的 `phase`。只保存可见文字，可能丢失续接状态。通过响应 ID 续接也会对历史输入 token 计费。WebSocket 连接会缓存近期响应；缓存失效且没有可恢复的持久状态时，需要重新提交完整上下文。

<a id="doc-36"></a>
### Background mode｜后台模式

[原文](https://developers.openai.com/api/docs/guides/background)

长时间生成可以放到后台执行：创建响应时设置 `background: true`，随后通过 retrieve 查询状态。`queued` 表示等待执行，`in_progress` 表示仍在运行；进入终态后检查结果。需要停止时调用 cancel，重复取消具有幂等语义。

创建时同时启用 `stream`，就可以记录事件的 `sequence_number`，断线后用 `starting_after` 接着读取。后台执行和轮询需要临时保存响应数据，因此 `store: false` 也会产生短期状态；具体保留期限取决于项目的数据控制配置。

<a id="doc-190"></a>
### Streaming API responses｜流式响应

[原文](https://developers.openai.com/api/docs/guides/streaming-responses)

普通 HTTP 请求等模型完成后一次性返回结果。设置 `stream: true` 后，服务端通过 SSE 陆续发送事件，应用可以边接收边显示或处理输出。

事件都有类型：`response.created` 表示响应已创建，`response.output_text.delta` 携带新增文字，`response.completed` 表示生成完成。SDK 提供类型化事件，也可以直接按 `type` 分派。工具参数和结构化输出使用相应的事件类型。对流式内容做审核时，要考虑尚未生成完整的文本；完整输出的审核结果不会随着每个文字片段一起返回。

<a id="doc-229"></a>
### WebSocket mode｜WebSocket 模式

[原文](https://developers.openai.com/api/docs/guides/websocket-mode)

Responses 的 WebSocket 模式适合需要多次模型与工具往返的任务。应用保持到 `/v1/responses` 的连接，用 `response.create` 发起生成；后续请求通过 `previous_response_id` 引用前一次响应，只发送新增输入。

一个连接可以通过 `stream_id` 承载多个会话。同一通道按顺序处理，不同通道可并行，事件可能交错到达，应用需要按通道分发。响应 ID 决定上下文从哪里接续，也支持从其他通道的可用响应分叉。断线后优先尝试恢复可用状态；无法恢复时重新提交上下文。生成过程中补充要求的用法见下节。

<a id="doc-122"></a>
### Mid-turn steering｜运行中调整方向

[原文](https://developers.openai.com/api/docs/guides/steering)

Mid-turn steering 允许用户在模型生成期间补充要求。当前指南适用于通过 Responses WebSocket 调用 GPT-6 系列的场景。收到 `response.created` 后，在同一连接发送 `response.steer`，以 `previous_response_id` 指定目标响应，并在 `input` 中放入补充内容。

`response.steer.accepted` 表示补充已进入队列。服务端在适当边界应用它并创建后继响应；原响应可能正常完成，也可能以 `incomplete` 状态结束，并标注原因 `steered`。缺少工具结果或审批时，应用仍需正常回填这些输入，无须重发已接受的补充。已输出的内容和已开始的工具不会被撤销；断线后的待处理输入需要按失败与恢复规则处理。

<a id="doc-135"></a>
### Multi-agent｜Responses 多 Agent

[原文](https://developers.openai.com/api/docs/guides/responses-multi-agent)

Responses 的 Multi-agent beta 让主 Agent 将独立任务交给子 Agent 并行处理，再汇总结果。请求中设置 `multi_agent.enabled` 即可启用；可用模型、beta 请求头和并发限制见原文。并发限制统计整棵任务树中活动的子任务，不包含主 Agent。

创建、通信和等待等协作动作由 API 执行，应用收到 `multi_agent_call` 时只需处理相应事件。自定义函数仍由应用执行：HTTP 模式在任务暂停后返回结果；WebSocket 模式可以通过 `response.inject` 将结果交给运行中的响应，并读取成功或失败确认。并行工作会增加上下文和 token 消耗，适合能拆成独立工作的任务。

<a id="doc-226"></a>
### Webhooks｜事件通知

[原文](https://developers.openai.com/api/docs/guides/webhooks)

Webhook 会把 API 事件发送到应用提供的 HTTP 地址，例如批处理结束或后台响应完成。在控制台注册接收地址和事件类型后，保存签名密钥，使用官方 SDK 或 Standard Webhooks 库验证请求原始内容及签名。

接收端应尽快返回成功状态，耗时工作放到后台。失败通知会退避重试，重定向不会被自动跟随。重复通知可用 `webhook-id` 去重。Agents session、项目安全和组织安全通知另有对应专题，但接收、验签和去重的基本做法相同。

<a id="doc-88"></a>
### File inputs｜文件输入

[原文](https://developers.openai.com/api/docs/guides/file-inputs)

Responses API 通过 `input_file` 接收文件，可以引用已上传的文件 ID、提供 base64 数据或外部 URL。Chat Completions 的文件输入限于 PDF，不支持外部文件 URL。

PDF 在支持视觉的模型上同时提供提取的文字和页面图像；Word、幻灯片及一般文本文件主要提取文字，内嵌图表不会完整保留。需要保留图表时可以先转成 PDF。电子表格有专门的解析流程。PDF 的 `detail` 控制页面图像细节，具体格式和大小限制见原文；大文件检索用 File Search，复杂表格计算可用 Hosted Shell。

<a id="doc-48"></a>
### Compaction｜上下文压缩

[原文](https://developers.openai.com/api/docs/guides/compaction)

上下文压缩会缩小会话历史，同时保留后续生成需要的状态。可以在 Responses 请求中设置 `context_management` 和 `compact_threshold`，达到阈值后由服务端压缩；也可以单独调用 `/responses/compact`。压缩项中的内容是加密状态，供后续模型使用。

两种方式的输出处理不同。服务端压缩后，自行维护输入数组的客户端可按指南移除最新压缩项之前的旧条目；用响应 ID 续接时，无须手动裁剪。独立 `/responses/compact` 返回的整段窗口则应原样用于下一次请求，包括压缩项及其他返回条目。

<a id="doc-68"></a>
### Counting tokens｜输入 token 计数

[原文](https://developers.openai.com/api/docs/guides/token-counting)

发送生成请求前，可以调用 `POST /v1/responses/input_tokens` 计算输入 token 数。它接受与 Responses 相同的输入形式，包括消息、指令、图片、文件、工具定义和会话，可用于检查上下文是否足够、估算费用或选择处理路线。

计数包括消息角色、边界和工具 schema 等结构开销。只对可见文字做本地分词会遗漏这些部分。输出用量也可能包括格式和推理 token，因此 API 返回的 token 数与用户看到的文字长度通常不同。

## SDKs and CLI｜开发库与命令行

<a id="doc-234"></a>
### SDKs and CLI｜SDK 与 CLI 总览

[原文](https://developers.openai.com/api/docs/libraries)

OpenAI 提供应用 SDK、命令行工具和 Agents SDK。应用 SDK 用于从程序调用 API；命令行工具适合终端操作；Agents SDK 管理模型、工具和交接组成的运行循环。也可以直接使用 HTTP 客户端。

官方应用 SDK 覆盖 JavaScript、Python、.NET、Java、Go 和 Ruby，并从环境变量读取 API key。原文提供安装与首次调用示例，另列 Azure 库和社区维护的语言库；具体支持范围和用法由各自文档说明。

<a id="doc-235"></a>
### OpenAI CLI｜官方命令行工具

[原文](https://developers.openai.com/api/docs/libraries/openai-cli)

`openai` CLI 可以直接在终端调用 API。先用 `openai explore` 搜索可用命令，它只展示所选命令，方便检查和修改参数。调用时从 `OPENAI_API_KEY` 读取密钥，管理端点使用 `OPENAI_ADMIN_KEY`。

结果可输出为 JSON、JSONL、YAML 等格式，`--transform` 可提取或重组字段；复杂请求可以通过 YAML 文件提交。CLI 覆盖文本、文件、图像、语音和管理操作。若命令与文档不同，检查是否仍在使用旧 Python SDK 附带的同名程序；涉及旧语音模型的示例应连同迁移说明一起阅读。
