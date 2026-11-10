# Agents｜Agents API

[返回中文导读总目录](../../OpenAI_API_Docs_中文导读_20261110.md)

Agents API 由 OpenAI 托管 Codex Harness。应用提交任务、配置工具并选择执行环境，服务负责会话与运行循环。这里按一次任务的配置、执行和恢复过程说明各项资源。

## Overview and setup｜概览与配置

<a id="doc-22"></a>
### Agents API｜托管 Agent 接口
[原文](https://developers.openai.com/api/docs/guides/agents-api/overview)

Agents API 让应用通过 API 使用 OpenAI 管理的 Codex Harness。OpenAI 保存会话、组织模型和工具调用，并处理上下文压缩与恢复；应用提供任务和工具，选择命令与文件操作在哪里执行。

Agent 保存可复用的配置，Session 保存会话和工作，Environment 提供计算与文件系统，Events 与 Items 分别提供进度和历史记录。模型、工具及托管容器按相应费率计费。自托管沙箱只改变执行环境的位置，模型服务和托管会话仍在 OpenAI。

<a id="doc-23"></a>
### Agents API quickstart｜快速开始
[原文](https://developers.openai.com/api/docs/guides/agents-api/quickstart)

先创建具备会话读写及模型调用权限的应用 API key，再安装 SDK。Agents API 请求需要 `OpenAI-Beta: agents=v1`，官方 SDK 会自动添加。

快速开始示例创建托管沙箱，让 Agent 编写并运行 `tree.py`，显示目录树。保存返回的 session ID，可以继续发送任务或读取结果。等待主 Agent 的 turn 完成后，还应检查脚本的执行结果；仅收到 idle 表示当前空闲。断线后先读取原会话的状态与记录，再决定是否重试，结束后清理资源。

<a id="doc-30"></a>
### Architecture｜架构
[原文](https://developers.openai.com/api/docs/guides/agents-api/architecture)

系统分为三部分：OpenAI 的 Harness 管理模型与工具循环；Environment 运行命令和读写文件；应用服务端提交任务、接收事件并处理自己的函数工具。

不需要工作区时，环境设为 `none`，仍可调用远程 MCP 或应用函数。需要文件与计算时，选择 `openai_hosted`，或用 `self_hosted` 连接自己的设备、容器和云资源。自托管环境的启动、连接、停止与文件保存由应用管理。

<a id="doc-54"></a>
### Configuring Agents｜配置 Agent
[原文](https://developers.openai.com/api/docs/guides/agents-api/configuration)

Agent 配置包含模型、指令、工具、推理设置和输出要求。可以在创建 session 时直接提供，也可以保存为可复用的 Agent，再对某个 session 覆盖指定字段。

保存的 Agent 用于创建新会话，更新它不会自动改变已有 session。已有会话只允许更新规定的字段，并按相应时间点生效。省略、清空、合并和替换配置的语义要逐字段遵循接口定义。

<a id="doc-38"></a>
### Bedrock Managed Agents｜AWS 托管路线
[原文](https://developers.openai.com/api/docs/guides/agents-api/bedrock-managed-agents)

Bedrock Managed Agents 将 OpenAI Harness 和模型推理运行在 Amazon Bedrock 中，命令与工具使用 AgentCore Runtime 或自托管计算。它沿用 Agent、session 等概念，但接入使用 AWS 端点和 IAM／SigV4 认证。

OpenAI Agents API 的自托管沙箱只改变命令执行位置；Bedrock 路线还改变了 Harness 和模型服务的位置。迁移示例前，应按 AWS 文档核对区域、模型、环境和功能支持。

## Sessions｜会话与运行

<a id="doc-172"></a>
### Run and continue sessions｜运行和续接会话
[原文](https://developers.openai.com/api/docs/guides/agents-api/sessions)

Session 持续保存 Agent 的配置、对话和工作。向空闲会话发送消息会开启一个新 turn；在活动 turn 中发送补充消息，则调整当前工作的方向。Turn 异步运行，进度可以通过事件流或 webhook 接收。

创建时可以一并提交初始输入并打开流；后续先订阅再发送消息，以免漏掉早期事件。保存 session ID，使用它续接、读取历史或取消当前 turn。提交发生超时时，用幂等键和已保存状态确认结果，避免重复启动同一工作。

<a id="doc-86"></a>
### Events and items｜事件与历史条目
[原文](https://developers.openai.com/api/docs/guides/agents-api/sessions/events)

Events 用于实时更新界面，Items 保存消息与工具调用，供之后读取。文字增量应按 item 和 content 标识归入正确位置，收到完整的 done 文本后替换临时拼接内容。

断线后先重新订阅并缓冲新事件，再读取 session 和历史 items，恢复界面状态并合并新进度。流不会重放所有错过的中间事件。当前仍需处理的函数或审批，应从 `required_actions` 读取，不能仅凭历史调用记录判断。

<a id="doc-118"></a>
### Manage sessions｜管理会话
[原文](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage)

将 session ID 存入应用的数据记录后，就可以分页查找会话、读取当前配置和环境，或查看历史 items 与 turns。状态为 `requires_action` 时，逐项处理 `required_actions`，例如返回函数结果或连接执行环境。

取消 turn 会停止当前工作并保留会话；删除 session 则移除会话资源。长期需要的结果应在删除前另行保存。

<a id="doc-181"></a>
### Scheduled automations｜计划任务
[原文](https://developers.openai.com/api/docs/guides/agents-api/sessions/automations)

Automation 保存任务的执行时间和目标 session，可以按 cron 周期运行，也可以安排一次性任务。每次运行可创建新会话，或继续已有会话；给 Agent 开放 automations 工具后，它也能安排后续工作。

Invocation 记录的是向 session 投递任务的尝试。投递成功后，还要查看 Agent 的实际执行结果；忙碌会话中的定时任务会等待。暂停或删除计划只影响之后的调度，已经被会话接受的任务需另行处理。

<a id="doc-34"></a>
### Automatic review｜自动审批
[原文](https://developers.openai.com/api/docs/guides/agents-api/sessions/approvals)

会话的 `review` 字段控制自动审批。设为 `auto_review` 时，OpenAI 的 Reviewer 根据动作风险和会话中的用户要求，批准或拒绝支持的权限请求；审核使用的 token 另计。设为 `none` 则不应用自动审批，大部分动作直接受环境权限约束，不会改成逐项交给应用人工审批。

网络限制、浏览器站点访问和登录输入仍按各自规则处理。启用审核前要满足环境的沙箱条件，切换模式也要等待主任务空闲且输入提交稳定。

<a id="doc-185"></a>
### Session webhooks｜会话通知
[原文](https://developers.openai.com/api/docs/guides/agents-api/sessions/webhooks)

Session webhook 在会话创建、开始工作、空闲、失败或需要应用处理动作时发送通知。接收端验证签名后，读取最新 session，取得所需函数参数、环境 ID 或浏览器审批内容。

`environment_connection` 可以触发外部沙箱的启动或重连，`function_call` 则要求返回应用函数结果。每类动作按自己的流程处理。会话空闲、某个 turn 失败与整个 session 失败也应分别记录；删除 session 不会产生删除 webhook。

## Environments and sandboxes｜执行环境

<a id="doc-141"></a>
### OpenAI-hosted sandboxes｜OpenAI 托管沙箱
[原文](https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted)

OpenAI 托管沙箱提供带 Python、Node.js 和命令行工具的 Linux 工作区。创建 session 时可指定软件包、初始文件、环境变量、容器规格、网络和能力目录。依赖与文件准备完成后才执行 setup commands；初始化失败会阻止 Agent 开始工作。

环境模板用于复用配置。需要提前准备实际工作区时，可使用预热环境。任务产物保存到规定输出目录后可以发布为 artifacts；环境的期限、清理和费用按容器规则处理。

<a id="doc-183"></a>
### Self-hosted sandboxes｜自托管沙箱
[原文](https://developers.openai.com/api/docs/guides/agents-api/environments/self-hosted)

自托管环境可以是笔记本、容器或远程沙箱。在其中运行 `codex exec-server`，执行器使用 environment ID 和受限的 environment key 注册，再主动建立出站 WebSocket，接收命令并返回结果。断线后可以重新连接。

应用负责准备文件、依赖和网络，按用户或工作负载隔离环境。应用 API key 留在沙箱之外，执行器只取得限定用途的密钥。模型调用与 Harness 仍由 OpenAI 托管。

<a id="doc-179"></a>
### Sandbox lifecycle｜沙箱生命周期
[原文](https://developers.openai.com/api/docs/guides/agents-api/environments/lifecycle)

自托管计算可以由应用直接创建，也可以在收到环境连接 webhook 后启动或恢复。应为每个 session 保存它对应的计算实例，并明确由哪个组件管理，防止重复请求创建多个沙箱。

关闭资源前，需要协调新输入和正在运行的任务。Session 可以比计算环境存在得更久，但换一个空沙箱不会自动恢复旧文件。停止第三方计算、保存文件和删除 OpenAI session 是分别执行的操作。

<a id="doc-146"></a>
### Pre-warm sandboxes｜预热沙箱
[原文](https://developers.openai.com/api/docs/guides/agents-api/environments/prewarmed)

预热可以在任务到达前创建托管沙箱、安装依赖、载入文件并执行初始化命令。环境准备好后，创建 session 时引用它的 ID，就能缩短用户等待时间。

未附加和已附加的环境有不同的有效期；多个 session 使用同一环境时会共享其中的文件。创建请求超时后，可以用相同的 `Idempotency-Key` 和请求体重试。环境模板保存的是配置，预热环境才是已经创建的工作区。

<a id="doc-180"></a>
### Sandbox security｜沙箱安全
[原文](https://developers.openai.com/api/docs/guides/agents-api/environments/security)

Agent 生成的代码能够访问环境中可见的文件、变量和网络。需要隔离的数据应放在不同环境，出站连接只开放任务需要的目标，应用凭据与执行器凭据分别管理。

托管沙箱可以使用 vault 的占位符，由代理向允许的目标注入真实密钥；自托管环境则由应用建立相应的可信访问方式。自动审批不替代网络和凭据控制，把秘密放进普通沙箱环境变量也不会使它对代码不可见。

<a id="doc-91"></a>
### Files and artifacts｜文件与发布产物
[原文](https://developers.openai.com/api/docs/guides/agents-api/environments/files)

文件存在执行环境中；artifact 是从 OpenAI 托管环境发布出来的文件副本。托管环境可在创建时或运行中接收上传文件，将结果放到 `/workspace/outputs` 后，在 turn 完成时发布为不可变产物。

Artifacts 可以在环境过期后继续下载，自托管文件则通过供应商文件接口或挂载目录取回。需要长期保存的结果，应在删除会话前下载。多个文件可以逐个取回，也可以先打包为一个压缩文件。

## Tools and integrations｜工具与集成

<a id="doc-224"></a>
### Web search｜网页搜索
[原文](https://developers.openai.com/api/docs/guides/agents-api/tools/web-search)

在 `agent.tools` 中添加 `web_search`，Agent 才能使用内置搜索。`live` 允许访问当前网页，`cached` 只搜索保存的网页内容，`disabled` 关闭搜索。仅在提示中要求联网，不会启用未配置的工具。

还可以设置搜索上下文大小、允许的域名和用户位置，用来调整结果的范围及相关性。

<a id="doc-50"></a>
### Computer use｜浏览器操作
[原文](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use)

Agents API 的浏览器运行在 OpenAI 托管环境中。创建时启用 desktop 和 `computer_use`，应用跟踪浏览器活动，处理新站点的访问请求；需要账号时，使用专门的登录输入流程。

站点访问许可只解决是否进入该站点，具体操作仍需遵守任务授权。敏感登录值应通过规定表单提交。断线后恢复同一 session 的待处理请求，避免重复批准或重复执行；任务结束后核对网页结果并清理会话。

<a id="doc-96"></a>
### Functions｜应用函数
[原文](https://developers.openai.com/api/docs/guides/agents-api/tools/functions)

应用函数在 `agent.tools` 中声明名称、说明和 JSON Schema。Agent 请求调用后，应用从最新 `required_actions` 读取参数，执行函数，再按相同的 session、turn 和 call ID 返回结果或错误。函数由应用选择的服务端或 worker 运行，附加沙箱不会自动把它搬进沙箱。

断线恢复时，优先提交已经保存的结果。涉及外部写入的调用，要先检查动作是否执行过，避免重试造成重复。工具较多时可以延迟加载函数定义。

<a id="doc-120"></a>
### MCP connections｜MCP 连接
[原文](https://developers.openai.com/api/docs/guides/agents-api/tools/mcp)

MCP 的连接位置由配置决定。HTTP 连接默认由 OpenAI 服务发起；设置 `connection_origin: environment` 后，由 session 的环境连接。Stdio 服务器则作为环境内的进程启动，需要可用的命令和绝对工作目录。

认证可来自显式配置、vault 或环境变量，取决于连接方式。排障时先确认实际连接方能否访问目标，再检查凭据、依赖和工作目录。这里的 localhost 始终指连接所在的环境。

<a id="doc-145"></a>
### Plugins｜插件
[原文](https://developers.openai.com/api/docs/guides/agents-api/tools/plugins)

插件把 Skills、MCP 配置或两者打包在一起。自托管环境将插件根目录加入 capability directories；托管环境可以上传插件 ZIP，也可以复用环境模板中的配置。

Manifest 中的路径从插件根目录解析，必须留在包内。MCP 的认证和网络仍需单独配置。修改插件文件后，已有 session 不会自动重载工具，需要按配置更新和会话流程处理。

<a id="doc-218"></a>
### Vaults｜凭据库
[原文](https://developers.openai.com/api/docs/guides/agents-api/tools/vaults)

Vault 将凭据保存在 Agent 指令和配置之外，session 通过 `vault_ids` 使用它。服务端连接 MCP 时，可以使用 bearer 或 OAuth 凭据；托管沙箱中的 API 请求则使用环境变量占位符，由代理对批准的目标替换成真实密钥。

读取 vault 不返回秘密值。凭据可以刷新、轮换或删除，目标 URL 也必须匹配相应规则。允许网络访问某个主机，与允许向该主机注入密钥，是两项独立设置。

## Delegation, observability and recovery｜协作、观测与恢复

<a id="doc-134"></a>
### Multi-agent｜托管 Harness 的多 Agent
[原文](https://developers.openai.com/api/docs/guides/agents-api/multi-agent)

设置 `agent.multi_agent.enabled` 后，Harness 提供创建、通信、等待和中断子 Agent 的能力。各子 Agent 有自己的上下文，可以同时处理独立任务，再由主 Agent 汇总。附加环境中的文件可能共享，因此同时编辑时仍需协调。

并发数、可继承的工具和活动事件按 Agents API 的规则配置。查询命令所属 turn 的 `subagent_id`，可以判断是哪一个 Agent 执行了命令。这套托管会话配置与 Responses 的 Multi-agent 请求配置分别使用。

<a id="doc-138"></a>
### Observability and usage｜观测与用量
[原文](https://developers.openai.com/api/docs/guides/agents-api/observability)

可以在控制台查看会话，也可以用实时事件、保存的 items 和 turns 检查工作。命令条目带有 turn ID，查询该 turn 的 `subagent_id` 可识别执行者；空的子 Agent ID 表示主 Agent 工作。

用量数据尽可能记录，但可能暂时为空或稍后更新。缓存输入已经计入 input tokens，推理已经计入 output tokens，不应重复相加。总成本还包括子 Agent、重试、工具和计算资源。

<a id="doc-200"></a>
### Tracing｜调用追踪
[原文](https://developers.openai.com/api/docs/guides/agents-api/tracing)

Trace 按 session、turn 和 span 展示工作：一个会话包含多轮任务，每轮展开为模型、工具和子 Agent 的步骤。可以在控制台查看输入、输出、状态和耗时，也可以分页导出 OTLP JSON。

父 span 的时间包含子步骤，并行步骤还可能重叠，因此不能直接把所有时长相加。Trace 和 usage 可能晚于最终回答出现；一次导出只包含当时可用的记录。

<a id="doc-82"></a>
### Errors and recovery｜错误与恢复
[原文](https://developers.openai.com/api/docs/guides/agents-api/errors)

请求失败时查看 HTTP 状态和 `error` 对象；运行中失败则读取 turn、session 或 environment 的状态与错误。程序按 `error.code` 分类处理，`error.message` 用于解释原因。

恢复前先确认原任务是否仍在运行、保存了哪些结果、外部动作是否已经发生。短暂故障可以退避重试；输入、认证或预算问题需要先修正。断线后读取原会话，再决定续接或开始后续 turn。

## Sandbox providers｜沙箱供应商指南

下列页面是各供应商的接线和生命周期说明，完整配置、安装命令及 Cookbook 示例通过原文查看。

| 原文 | 中文导读 |
|---|---|
| <a id="doc-35"></a>[AWS Lambda MicroVMs](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/aws) | AWS Lambda MicroVM 运行 `codex exec-server` 并保存工作区。应用或 webhook 启动、恢复实例，镜像的运行钩子从 Secrets Manager 取得执行器密钥。任务结束后取回文件并终止实例；自动暂停策略需考虑执行器持续的出站连接。 |
| <a id="doc-39"></a>[Blaxel](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/blaxel) | Blaxel 沙箱安装 Codex 执行器后连接到 session，由应用或 webhook 管理启动和停止。Keep-alive 与超时要配合任务生命周期。Agent Drive 可保留文件，会话历史仍由 Agents API 管理。 |
| <a id="doc-44"></a>[Cloudflare](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/cloudflare) | Cloudflare 参考 Worker 验证 OpenAI webhook，为 session 启动或重连运行执行器的 Container。应用通过 Agents API 发任务并读结果，Worker 管理计算资源。也提供由应用直接管理及单独清理的方式。 |
| <a id="doc-73"></a>[Databricks Sandbox](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/databricks) | Databricks Sandbox 在支持的预览工作区运行命令和处理文件。应用通过 Databricks profile 管理沙箱，执行器使用单独的 environment key 连接 OpenAI。示例完成文件写入和读回检查后，分别清理会话与沙箱。 |
| <a id="doc-74"></a>[Daytona](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/daytona) | Daytona 可由应用直接管理，也可由验证 webhook 的控制器启动或重连 worker。可通过快照预装依赖；运行超时和自动停止策略需要兼顾执行器长连接。任务完成后分别清理 OpenAI session 与 Daytona 资源。 |
| <a id="doc-78"></a>[DigitalOcean](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/digitalocean) | DigitalOcean M.A.R.S. 用 `codex-agentapi` 镜像启动 Firecracker microVM，执行器主动连接 Agents API。可由 webhook、应用或 doctl 流程管理，应用需保存 OpenAI session 与 DigitalOcean 实例之间的对应关系。 |
| <a id="doc-80"></a>[E2B](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/e2b) | E2B 可为每个 session 创建独立 worker，并在连接请求到达时恢复或替换它。暂停保留文件，替换已删除的沙箱不会恢复旧文件。应用还需分别设置沙箱运行期限与执行器命令超时。 |
| <a id="doc-128"></a>[Modal](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/modal) | Modal SDK 或 API 创建隔离工作区，在其中安装 Codex 并启动执行器，再向 Agents API session 提交任务。可用应用管理或 webhook 管理方式；结束时分别停止 Modal 计算并清理 OpenAI session。 |
| <a id="doc-143"></a>[Oracle Cloud Infrastructure](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/oci) | OCI 的 beta 示例由应用创建和删除 Agents API session 与 Oracle 沙箱。需要具备项目和沙箱权限、兼容的运行时及区域认证。安装预览 SDK、连接执行器和读取生成文件的顺序见原文。 |
| <a id="doc-220"></a>[Vercel](https://developers.openai.com/api/docs/guides/agents-api/environments/providers/vercel) | Vercel Sandbox 运行 Codex 执行器，可用快照预装依赖。本地运行使用 Vercel token、团队和项目配置，部署在 Vercel 上则使用 OIDC。完成后取回文件，分别清理沙箱与 OpenAI session。 |
