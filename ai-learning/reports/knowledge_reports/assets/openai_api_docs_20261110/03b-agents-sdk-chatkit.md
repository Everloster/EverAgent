# Agents｜Agents SDK 与 ChatKit

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

Agents SDK 在你的应用中运行 Agent，ChatKit 为它提供聊天界面。本卷说明 Agent 的定义、运行循环、状态保存、工具接入和前端交互。

## Choose a runtime｜选择运行方式

<a id="doc-21"></a>
### Agents｜Agent 路线总览
[原文](https://developers.openai.com/api/docs/guides/agents)

选择开发方式，先看谁运行 Agent、谁保存状态。

| 需求 | 对应入口 |
|---|---|
| 由 OpenAI 运行和维护 Codex Harness | Agents API |
| 在自己的应用里编排模型、工具和交接 | Agents SDK |
| 直接调用模型，自行组织执行流程 | Responses API |
| 嵌入聊天界面 | ChatKit |

会话记录和执行环境分别管理。session、conversation 与 sandbox 各有自己的保存期限和清理方式，选定运行方式后还要分别配置。

<a id="doc-24"></a>
### Agents SDK｜SDK 总览
[原文](https://developers.openai.com/api/docs/guides/agents/sdk)

Agents SDK 提供 Python 和 TypeScript 两个版本。定义一个 Agent，给它模型、指令和工具，再由 SDK 运行模型与工具之间的循环。应用负责部署、存储、连接和审批策略。

可以先完成一次简单运行，再按实际需要加入多轮状态、专家交接、沙箱、校验和追踪。SDK 仓库提供更完整的示例及语言参考；需要 OpenAI 托管整个 Harness 时，使用 Agents API。

<a id="doc-160"></a>
### Quickstart｜快速开始
[原文](https://developers.openai.com/api/docs/guides/agents/quickstart)

安装 SDK、设置 API key 后，先定义一个职责明确的 Agent 并运行一轮。返回结果包含最终输出和这次运行的历史。接着可以添加函数工具，或让另一个 Agent 接手特定任务。

下一轮可以重用本地历史，让 SDK session 负责读写记录，或通过服务端 continuation ID 续接。若运行因审批暂停，应保存 RunState 和 interruptions，作出决定后恢复。发生 handoff 后，也可以让最后负责工作的 Agent 继续处理下一轮。内置 trace 能帮助查看这些步骤。

## Build and run｜定义与运行

<a id="doc-20"></a>
### Agent definitions｜Agent 定义
[原文](https://developers.openai.com/api/docs/guides/agents/define-agents)

一个 Agent 将模型、指令和运行能力放在一起。配置项包括 `tools`、`handoffs`、guardrails、MCP 连接及输出类型。指令可以固定，也可以根据用户或本次运行的上下文动态生成。

本地 run context 用来保存数据库客户端、认证信息等应用依赖，不会自动送入模型。只有需要不同职责、工具或策略时，才值得拆成多个 Agent；同一个任务里的普通步骤可以由一个 Agent 完成。

<a id="doc-132"></a>
### Models and providers｜模型与供应商
[原文](https://developers.openai.com/api/docs/guides/agents/models)

生产环境应明确指定模型。可以在 Agent 上设置 `model`，为一次 run 设置默认值，或用进程级默认值供未指定模型的 Agent 使用。这样更容易控制不同任务的质量、成本和延迟。

供应商适配器和传输设置决定请求怎样发送。推理强度、回答详略及工具行为等参数是否可用，取决于具体模型和接口。Responses WebSocket 服务于模型与工具的多次往返；实时语音应采用相应的语音接口。

<a id="doc-173"></a>
### Running agents｜运行 Agent
[原文](https://developers.openai.com/api/docs/guides/agents/running-agents)

一次 run 对应应用中的一轮任务。Runner 调用当前 Agent 的模型，执行返回的工具调用，再把结果送回；如果发生 handoff，就切换到接手的 Agent。模型给出最终回答、无需继续用工具时，run 返回结果。

多轮状态可以由本地历史、SDK session、Conversations API 或响应 ID 续接管理。通常选择其中一种作为主方式，避免重复传入同一段历史。流式输出沿用这套循环；因审批暂停时，保存并恢复同一个运行状态。

<a id="doc-178"></a>
### Sandbox Agents｜沙箱 Agent
[原文](https://developers.openai.com/api/docs/guides/agents/sandboxes)

沙箱为 Agent 提供隔离的类 Unix 环境，包括文件系统、Shell、软件包、挂载数据、端口和快照。需要处理文件、执行命令、生成产物或稍后继续工作时，可以使用 SandboxAgent。

应用中的 Harness 管理模型调用、工具路由、审批和恢复；沙箱承担实际计算与文件操作。初始化 Manifest、可用 Capabilities 和供应商客户端共同确定环境。恢复时要分别考虑运行状态、沙箱会话和工作区快照，它们保存的内容不同。

<a id="doc-144"></a>
### Orchestration and handoffs｜编排与交接
[原文](https://developers.openai.com/api/docs/guides/agents/orchestration)

Handoff 将当前分支的对话交给另一个 Agent，由接手者负责下一次答复。Agents-as-tools 则把专家当成工具调用，主 Agent 收到结果后仍负责回答用户。

如果下一步需要不同的指令、工具或审批策略，可以交接给专门的 Agent。交接描述应写清它负责什么，便于模型选择；需要时还可以携带结构化信息或过滤后的历史。Python 与 TypeScript 的具体配置方式见各自 SDK 参考。

<a id="doc-103"></a>
### Guardrails and human review｜校验与人工审批
[原文](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)

Guardrails 自动检查输入、输出或工具行为；人工审批让运行在执行敏感动作前暂停，等待批准或拒绝。输入校验可以在主模型运行前阻断请求，输出校验可以在结果交付前验证或处理内容，工具校验则作用于调用参数或结果。

审批暂停会返回待处理的 interruptions 和可恢复状态。作出决定后，将状态交回 Runner 继续运行。Agent 级输入、输出校验与工具级校验的覆盖范围不同，需要按动作所在位置配置。Agents SDK 也不会自动继承 Codex 的 Auto-review 规则。

<a id="doc-170"></a>
### Results and state｜结果与状态
[原文](https://developers.openai.com/api/docs/guides/agents/results)

运行结果同时提供回答和后续状态。以 Python 命名为例，`final_output` 是最终回答，`last_agent` 是最后负责的 Agent，`last_response_id` 用于服务端续接；可重放历史用于应用自行保存上下文。TypeScript 提供对应的属性。

审批暂停时，最终回答可能为空。此时应读取 `interruptions`，保存 `to_state()` 返回的快照，处理审批后恢复运行。发生专家交接后，可以沿用 `last_agent`，让下一轮继续由同一专家负责。

<a id="doc-110"></a>
### Integrations and observability｜集成与可观测性
[原文](https://developers.openai.com/api/docs/guides/agents/integrations-observability)

MCP 可以由平台连接远程服务器，也可以由应用通过 stdio 或 streamable HTTP 直接连接本地、私网服务。后一种方式由应用管理网络连接、工具筛选与审批。

常规服务端运行默认启用 SDK tracing，记录模型调用、工具、交接和 guardrail 等步骤，也允许添加自定义 span。多次 run 可以归到同一条 trace 中。调试时先找出出错的步骤，再把有代表性的运行记录用于后续评估。

<a id="doc-83"></a>
### Evaluate agent workflows｜评估 Agent 工作流
[原文](https://developers.openai.com/api/docs/guides/agent-evals)

调试 Agent 时，trace 能显示一轮任务中用了什么工具、何时交接、是否遵守指令。可以对这些记录设置评分标准，比较修改前后的行为。需要重复评估时，再整理数据集并运行 eval。

数据集、Evals API、外部模型评估和 Prompt optimizer 各有对应入口。部分托管评估功能已进入退役过渡期，当前状态见[历史与迁移卷](07-legacy-resources.md#doc-12)。

## ChatKit｜聊天界面集成

<a id="doc-41"></a>
### ChatKit｜概览
[原文](https://developers.openai.com/api/docs/guides/chatkit)

ChatKit 提供可嵌入的聊天界面，支持组件、工具交互和附件。可以用 ChatKit SDK 连接自己运行的后端，再由模型 API 或 Agents SDK 处理请求。

已有 Agent Builder 托管工作流可在过渡期继续使用，新集成应采用自有服务端方案。服务端负责认证用户、分配唯一用户标识，并向前端提供所需的 session/client secret；前端负责挂载和定制聊天组件。ChatKit 本身继续提供。

<a id="doc-17"></a>
### Advanced integrations with ChatKit｜自托管高级集成
[原文](https://developers.openai.com/api/docs/guides/custom-chatkit)

自托管 ChatKit 时，应用实现 `ChatKitServer`，通过 HTTP 接收前端请求，并在 `respond` 中返回流式事件。Store 保存会话，FileStore 处理文件；辅助函数可以把 Agents SDK 的结果接到聊天界面。

这种方式适合需要自定义认证、存储位置或编排流程的应用。还可以通过线程元数据保存状态、向客户端发起工具调用、发送进度信息，并使用 widgets 和 actions 构建交互。完整的类接口与示例见原文链接的 SDK 文档。

<a id="doc-42"></a>
### ChatKit widgets｜界面组件
[原文](https://developers.openai.com/api/docs/guides/chatkit-widgets)

Widgets 是 ChatKit 自带的容器和界面组件，包括卡片、列表、文字、图片、按钮、选择器及表单。可以在 Widget Builder 中调整布局和预览效果，再把生成的 JSON 交给后端使用。

图片和文件应先由后端托管，再在消息里引用。用户点击组件时，应用收到 action 及其 payload，随后更新组件、调用模型或执行其他逻辑。组件属性分为容器 `WidgetRoot` 和普通节点 `WidgetNode`，具体字段见原文参考表。

<a id="doc-14"></a>
### Actions in ChatKit｜交互动作
[原文](https://developers.openai.com/api/docs/guides/chatkit-actions)

用户点击按钮或其他组件时，ChatKit 可以直接发送 action，无需先提交一条聊天消息。前端也能调用 `sendAction()`，让界面外的操作触发聊天中的响应。

Action 默认由服务器处理，也可以指定客户端处理器。表单按字段名称收集 payload，并支持基础验证和加载状态。服务端需要验证客户端提交的动作及数据，再决定执行什么操作。

<a id="doc-197"></a>
### Theming and customization｜主题与定制
[原文](https://developers.openai.com/api/docs/guides/chatkit-themes)

ChatKit 的外观与交互通过同一份 options 对象配置：React 集成传给 `useChatKit`，其他集成调用 `setOptions`。可以调整主题、字体、颜色、间距、圆角、启动提示和页头按钮。

输入框还可以启用附件、实体 mentions 和自定义工具，或隐藏不需要的界面区域。附件默认关闭，上传方式取决于后端集成；locale 可以覆盖浏览器默认语言。ChatKit Studio 提供主题与组件预览，完整参数见 SDK 参考。
