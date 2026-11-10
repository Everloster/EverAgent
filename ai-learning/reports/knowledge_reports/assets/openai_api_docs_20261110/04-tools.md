# Tools｜工具

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

工具让模型取得外部资料并发起操作。本卷说明各类工具怎样接入、在哪里执行，以及应用需要接收和返回哪些结果。

## Overview｜概览

<a id="doc-217"></a>
### Using tools｜使用工具
[原文](https://developers.openai.com/api/docs/guides/tools)

模型可以通过工具搜索网页、检索文件、调用应用函数、访问 MCP 服务或执行代码。工具定义写在 Responses 请求的 `tools`、Agents API 的 `agent.tools`，或 Agents SDK 的 Agent 配置中。

选择工具时也要确定执行方：托管工具由服务执行，客户端函数由应用处理。各接口的配置和结果回填方式不同，接入时应使用对应运行方式的示例。

<a id="doc-95"></a>
### Function calling｜函数调用
[原文](https://developers.openai.com/api/docs/guides/function-calling)

函数调用把应用的能力开放给模型。应用先提供函数名称、说明和参数 schema；模型返回要调用的函数及参数，应用执行后用原始 `call_id` 交回结果，模型再继续回答或调用工具。

函数工具使用 JSON Schema，custom tools 接收自由文本，也可用支持的 grammar 约束输入。`tool_choice` 控制工具选择，`strict` 约束参数结构，流式事件可以逐步传回参数。Namespaces 和 tool search 适合工具较多的应用。Responses 与 Chat Completions 的调用格式和模型支持范围应分别核对。

## Search and retrieval｜搜索与检索

<a id="doc-225"></a>
### Web search｜网页搜索
[原文](https://developers.openai.com/api/docs/guides/tools-web-search)

`web_search` 让模型取得当前网页资料，并在回答中附上来源。简单问题可以直接查一个事实；复杂研究可以多次搜索、打开网页和页内查找，再综合结果。应用应把返回的引用显示为清楚、可点击的链接。

Responses 支持域名过滤、来源列表、地域、图片结果和实时访问控制。新版工具、旧 preview 工具及 Chat Completions 搜索模型的参数不同。长研究的返回 token 预算单独控制搜索返回量，不改变模型上下文窗口。

<a id="doc-89"></a>
### File search｜文件搜索
[原文](https://developers.openai.com/api/docs/guides/tools-file-search)

File Search 在上传的文件中做语义和关键词检索。先创建 vector store、上传文件并等待处理完成，再将该知识库交给 Responses 的 `file_search` 工具。模型需要资料时，OpenAI 执行检索并返回带文件引用的回答。

可以限制检索结果数量，用文件 metadata 筛选范围，也可以要求响应包含原始检索结果，供应用检查。支持的文件格式与使用限制见原文列表。

<a id="doc-171"></a>
### Retrieval｜检索
[原文](https://developers.openai.com/api/docs/guides/retrieval)

Retrieval API 允许应用直接搜索 vector store，取得相关文本片段、得分和来源。语义搜索可以找出意思相关但关键词不同的内容；应用可以直接使用结果，也可以把片段交给模型生成回答。

检索可配置查询改写、属性过滤、ranker、阈值和混合搜索权重。文件入库包含上传、分块与异步处理，也支持批量操作和过期策略。自定义 `filename` 属性与上传文件名分开管理；移除文件后，搜索结果可能需要短暂时间才完全更新。

## Connect tools and data｜连接工具与数据

<a id="doc-121"></a>
### MCP servers｜MCP 服务器
[原文](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)

Responses 可以连接公开的远程 MCP 服务器，也可以通过 Secure MCP Tunnel 访问私有服务。前者使用 `server_url`，后者使用 `tunnel_id`；认证参数按服务器要求提供。

API 先通过 `mcp_list_tools` 取得工具定义，再用 `mcp_call` 记录调用和返回结果。可以限制允许使用的工具，并要求应用批准特定操作。认证值需要按请求提供，第三方服务也有自己的数据处理政策。旧 `connector_id` 仅在相应兼容范围内保留，新接入应使用服务器地址或隧道。

<a id="doc-182"></a>
### Secure MCP Tunnel｜私有 MCP 隧道
[原文](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels)

Secure MCP Tunnel 让私网中的 MCP 服务器接入支持的 OpenAI 产品。在能访问 MCP 的网络内运行 `tunnel-client`；它主动建立出站 HTTPS 连接，拉取待处理请求，转发给本地 MCP，再通过同一隧道交回结果。无需向公网开放入站端口。

隧道要关联正确的组织或工作区，并分配 Read、Use、Manage 权限。OAuth、mTLS、网络限制和日志按部署需要配置。隧道解决的是私有服务的连通性，所连接产品的数据保留与日志规则仍各自适用。

<a id="doc-15"></a>
### Add custom MCP server｜添加自定义 MCP
[原文](https://developers.openai.com/api/docs/guides/custom-mcp-server)

在 ChatGPT 网页端，可以把自定义 MCP 服务器创建为插件。填写服务器 URL 或选择 Tunnel，配置 OAuth 等认证方式，创建后安装到个人或有权限的工作区，即可在对话中使用。

服务器可以提供读、写工具。工具描述、`readOnlyHint`、刷新与操作确认影响客户端怎样呈现和使用它们；工作区权限和安全设置仍然适用。这条接入路线服务于 ChatGPT 插件，Responses 中的 MCP 则在 API 请求里配置。

<a id="doc-236"></a>
### Building MCP servers for plugins and API integrations｜构建 MCP 服务
[原文](https://developers.openai.com/api/docs/mcp)

MCP 服务器可以把自己的数据源提供给 ChatGPT、Codex 和 API。原文用 vector store 与 FastMCP 演示一个读取型服务：`search` 返回匹配项，`fetch` 取得指定文档的全文。

兼容研究和知识检索流程时，结果包含 ID、标题、正文或搜索条目，以及可引用的规范 URL。相同结构同时放入 `structuredContent` 和文本 content，可兼容不同客户端。非空 URL 用于建立引用；仅有标题的结果仍是普通工具输出。其他用途的 MCP 可以提供自己的工具，认证和写操作审批需单独配置。

## Build tool workflows｜工具工作流

<a id="doc-188"></a>
### Skills｜可复用技能
[原文](https://developers.openai.com/api/docs/guides/tools-skills)

Skill 是一个包含 `SKILL.md` 和辅助文件的目录，用来保存某类任务的说明、脚本或模板。模型发现技能时先看到名称和描述，决定使用后再读取具体内容。说明应写清用途和适用场景，辅助材料按需引用。

Responses 的 Shell 工具可以使用本地技能或上传的版本化技能包；托管执行时将相应版本附加到容器。Agents API 则从沙箱的 capability directories 发现技能。上传、版本指针、删除和文件限制各有规定，技能中的可执行内容也需遵守应用权限。

<a id="doc-198"></a>
### Tool search｜按需工具发现
[原文](https://developers.openai.com/api/docs/guides/tools-tool-search)

Tool search 让模型在需要时查找并加载工具定义，减少初始上下文中大量 schema 带来的开销。启用时添加 `tool_search`，并将待延迟加载的函数、命名空间或 MCP 服务器标为 `defer_loading`。

搜索可以由 OpenAI 托管，也可以由应用执行。客户端执行时，用相同的 `call_id` 返回 `tool_search_output`。加载后的工具可供后续调用；手动重放历史时，应保留工具定义和 `additional_tools` 的出现位置，以维持上下文及缓存。Agents API 的函数加载与 MCP 发现另有配置。

<a id="doc-150"></a>
### Programmatic Tool Calling｜程序化工具调用
[原文](https://developers.openai.com/api/docs/guides/tools-programmatic-tool-calling)

Programmatic Tool Calling 让模型编写 JavaScript，用循环、条件和并行调用组织多个工具，并在程序中处理较大的中间结果。每次程序在独立的托管 V8 环境中执行，通过已开放的工具访问外部系统；该环境没有 Node.js、任意网络访问、通用文件系统或子进程。

Responses 请求通过 `allowed_callers` 规定哪些工具可以直接调用、由程序调用或两者皆可。客户端函数仍由应用执行；续接时保留 program、caller、call ID 和 `program_output` 的关联。Agents API 默认启用的程序调用由托管 Harness 管理。

<a id="doc-31"></a>
### Async tool calling｜异步工具调用
[原文](https://developers.openai.com/api/docs/guides/async-tool-calling)

在函数或 custom tool 定义中设置 `async: true`，模型发出调用后可以继续处理其他独立工作，暂时不用等待工具结果。应用负责启动、登记和管理后台任务，完成后在后续请求中用原始 call ID 返回结果。

应用还可以自定义等待工具，或把询问用户做成异步工具；这些工具的界面、任务状态和结果交付都由应用实现。是否能与 PTC、多 Agent 等功能组合，需按兼容性说明配置。

## Computer and code｜计算机与代码

<a id="doc-187"></a>
### Shell｜终端工具
[原文](https://developers.openai.com/api/docs/guides/tools-shell)

Shell 工具可以在 OpenAI 托管容器中运行命令，也可以把命令交给应用自己的本地执行器。两种方式都通过 `shell_call` 发出请求，再以 `shell_call_output` 返回输出、退出状态或超时结果。

托管容器可以跨请求复用、附加 Skills 并生成可下载产物；网络访问受组织和请求级策略控制，也可配置 domain secrets。本地模式由应用实际实施执行范围与权限，不能仅依赖模型自行遵守命令限制。

<a id="doc-51"></a>
### Computer use｜计算机操作
[原文](https://developers.openai.com/api/docs/guides/tools-computer-use)

Computer use 让模型操作浏览器或桌面。模型根据截图和坐标操作时，用 `ComputerToolset`；应用能提供页面文字、控件和标签页时，可用 `BrowserToolset`。需要 OpenAI 托管浏览器时，使用 Agents API 的对应能力。

直接 API 接入由应用维护操作循环：发送任务，执行模型请求的动作，再回传截图或页面状态。浏览器会话、权限和清理由应用负责。结果应通过页面实际状态核对；仅查公开资料而无需交互时，可以使用网页搜索。

<a id="doc-52"></a>
### Computer use integration recipes｜集成配方
[原文](https://developers.openai.com/api/docs/guides/tools-computer-use-integration)

集成计算机操作时，需要准备浏览器或隔离桌面，将 API 动作映射到实际输入，并把新的截图或状态返回给模型。截图缩放、坐标转换、批量动作和代码执行都应在驱动层明确处理。

原文提供本地浏览器、Docker 桌面和自有执行服务的参考实现，以及 preview 接口迁移到 `computer` 与 `actions[]` 的对照。API 历史和浏览器运行状态分别保存；用户确认与权限检查应在实际动作执行前落实。

<a id="doc-40"></a>
### Browser and desktop drivers｜浏览器与桌面驱动参考
[原文](https://developers.openai.com/api/docs/guides/tools-computer-use-sdk-drivers)

Driver 把允许的工具调用转换为浏览器或桌面动作。浏览器驱动返回文字、控件和标签页状态；桌面驱动返回截图并执行鼠标、键盘动作。SDK 发送和分派请求，应用负责会话存续、权限和清理。

可以限制暴露的方法、设置确认回调和 URL 策略，再按需要加入局部页面引用、指针操作、脚本或文件传输。驱动还要处理取消、未完成的副作用、恢复记录和用量诊断。通过驱动接口检查后，仍需在目标页面验证动作结果。

<a id="doc-29"></a>
### Apply Patch｜结构化补丁
[原文](https://developers.openai.com/api/docs/guides/tools-apply-patch)

`apply_patch` 让模型以结构化补丁提出文件创建、修改或删除。应用读取每个 `apply_patch_call`，解释其中的 V4A diff，在工作区执行操作，再按 call ID 返回 `completed` 或 `failed` 及错误信息。

执行器需要处理路径范围、文件状态变化和部分失败，决定采用逐项提交还是原子操作。模型收到结果后可以继续修补；文件是否真的修改成功，以执行器返回和实际文件状态为准。

<a id="doc-46"></a>
### Code Interpreter｜Python 代码解释器
[原文](https://developers.openai.com/api/docs/guides/tools-code-interpreter)

Code Interpreter 让模型在托管沙箱中编写并执行 Python，用于计算、数据分析、处理文件和图像。代码出错时，模型可以根据错误继续修改并运行。

工具需要一个 container，可由请求自动创建或显式指定。容器保存上传和生成的文件；回答中的 `container_file_citation` 可关联生成文件，应用随后下载。容器有内存规格和有效期，过期后不能通过旧 ID 恢复其中的数据或内存对象。

## Media｜媒体

<a id="doc-105"></a>
### Image generation｜Responses 图像生成工具
[原文](https://developers.openai.com/api/docs/guides/tools-image-generation)

在 Responses 请求中添加 `image_generation`，模型便可根据文字和参考图片生成或编辑图像。顶层 `model` 指定负责对话的模型，工具内部的 `model` 指定图像模型。

结果包含 base64 图像；工具也可能返回优化后的 `revised_prompt`。多轮对话可以继续修改图像，流式模式可逐步返回 partial images。尺寸、格式、质量和成本由图像模型及输出配置决定。
