# 身份、会话与脚本契约

面向个人桌面使用和基础设施工作 Agent。公共实现由
[`everagent-core`](../packages/everagent-core/README.md) 拥有；本页解释契约，Git 授权与提交规则回到
[PROTOCOL_COMMON](./PROTOCOL_COMMON.md#c-push-flow推送流程--全局统一)。

## 双仓与安装态

| 层 | 职责 |
|---|---|
| 公共 core | 通用 harness/model 证据、session schema、script catalog、Git 原语 |
| 公开仓入口 | 学习仓策略、作者策略与 staged 质量门禁 |
| 私有 eacli | 私有设备事实与红线、原生 runtime adapter、基础设施策略 |
| 安装包 | 锁定的公共 core 和私有派生资产，无相邻 checkout 依赖 |
| 兼容脚本 | 转交 canonical owner，不维护第二套事实或算法 |

公共仓不接收私有设备、地址、账号、拓扑和任务数据。eacli 是统一使用入口，新协作使用原生 Orca，
Herdr 留给用户手动使用；发现同伴与协作边界见 [AGENT_COLLABORATION](./AGENT_COLLABORATION.md)。

## current → diagnose → declare

本页描述 Go core 0.5.2 及对应 eacli 源码契约；安装态升级与真实平台覆盖分别验收，源码/fixture通过不代表已发布。

- `eacli session current`先自动取当前调用方；`diagnose`解释失败字段、读取器、配置/源码owner及复验入口，不自动修复或扩大访问范围。`eacli session inspect`为diagnose兼容入口；独立core的`everagent-identity inspect`仍是当前身份查询。
- `identity/readers.json`拥有有界进程签名、session环境键、原生根目录与适配字段；`EVERAGENT_IDENTITY_CONFIG`显式覆盖用于修复路径/签名。配置不得提供model答案、把一般进程当Agent、用凭据环境键当会话ID或绕过读取边界；核心仍验证PID创建身份、session与新鲜度。
- 自动读取及可行修复仍无依据，才用`eacli session declare --harness <用户指定> --form cli --model <用户指定> --user-confirmed`，只传用户明确补充的字段。公共core对应`everagent-identity declare`；旧`declare-model`保留仅模型兼容语义。
- 用户facts仅接受device/harness/form/model，默认4小时、允许300–43200秒，字段分别保留原声明时间和到期时间；普通字段更新不续期模型或复活更早声明。模型撤销边界仅抑制旧声明，不是新模型证据；有边界时模型声明时间必须严格更晚，同tick无法证明先后则不放行。
- 已知harness绑定进程创建身份及session/terminal；Desktop/Web没有native session时只绑定当前执行shell，未知harness也必须有exact shell，并核对通用及用户harness适用的model hint。重启、嵌套、会话/提示变化、过期或损坏失效；新的自动事实优先，用户声明不覆盖相冲突的自动证据。
- 声明始终标`user-declared`而非自动确认，不授予权限。device值仍须由私有adapter核对登记/红线；公共core不含私有设备表，声明不能把未知机器擅自认成个人设备。

## 明确回答的问题

Session v2 区分 `actor`（harness 与模型）、`execution`（当前执行设备）、`caller`（来源）、
`host`（当前 runtime 或 Desktop）、`checkout`（实际 Git 工作树）、`task`（原生绑定）、`readiness`。
设备、终端、仓库、模型和任务各自保留来源与核实状态，不能把宿主的默认模型或 focused pane 当作调用方事实。
`interface`单列cli/desktop/web/unknown及来源；`host`是承载环境，嵌套CLI不因外层App已核实就变成Desktop/Web。
没有原生已核实或有效用户声明时，`actor.model.id`为unknown，配置和请求分别在configured/requested字段，不能仅凭显示了型号就认为可提交。

个人桌面场景支持命令行和 Desktop。**Kimi Desktop 是独立的 macOS/Windows App**，身份为
`kimi-desktop`；Kimi Code CLI 身份为 `kimi-cli`。ZCode、MiniMax Code 也作为 Desktop 宿主识别。
Windows 的 Kimi 分类使用调用方可执行文件的产品目录与路径，不能仅靠文件名大小写。
App 身份或版本可见不代表当前模型可见；核实失败保持 unknown/configured，Agent 先诊断并修复可行的自动路径，用户指定作为取证不可行时的兜底。

基础设施工作场景只消费已有原生任务元数据；环境 task ID 是 hint。任务确认要求精确 caller 和原生 owner
记录一致；普通 executor 不冒充 Agent。没有现成任务绑定时报告 unbound/unverified，不另建 controller 或 ledger。

## 模型证据与声明

| 字段/状态 | 含义 | 可用于提交 |
|---|---|---|
| requested | 原生派工/会话step实际请求的Model.Ref；不是provider返回型号 | 否 |
| configured / configured_source | 配置默认值或环境提示及其来源，不是当前有效 profile | 否 |
| observed / session-bound | 新鲜、精确会话范围的原生模型观测 | 是 |
| user-declared / declared | 用户明确指定的本会话模型 | 是 |
| unknown | 无依据 | 否 |

`actor.model.configured_source`为可选提示来源：`config-default`或`env:<白名单键>`；独立身份输出对应
`configured_model_source`。Codex配置提示只读顶层`model`，不合并profile或启动参数；环境提示优先。
没有有效提示时不输出来源，旧版本也可能缺该字段，不能据此猜测。`source`仍表示模型证据来源，
configured与observed不同不说明实际模型串用；这些提示不改变自动核实、用户声明或提交门禁。

原生观测必须来自受支持 adapter，绑定 harness、进程创建身份、session/terminal 并通过新鲜度检查。
**自动核实 → Agent 诊断及可行的源码修复 → 用户明确指定兜底。** 重构必须保留已核实的读取能力。

| 自动来源 | 核实依据 |
|---|---|
| Codex | 当前 thread 的 `turn_context.model`；长 turn 用精确 SQLite 运行态索引与同 thread 的新鲜 usage 元数据核对 |
| Pi | shell 工具每次启动清除继承值，再从当前 session/model 注入的 `PI_SESSION_ID`、`PI_MODEL` |
| TRAE | 精确 thread 的运行日志模型字段与请求时间；支持原有 thread alias，嵌套 Codex 不借外层 ID |
| Claude Code | 精确 UUID session 的原生 assistant `message.model`；绑定当前调用方进程创建时间、原生项目目录和新鲜记录，不借配置中的模型 |
| ZCode | 当前会话 `model-io-<会话标签>` 请求记录前缀的 `modelId`；会话标签取自本执行 shell 启动命令的 bash-startup 路径，绑定 zcode-cli 进程创建时间与新鲜完成记录 |
| MiniMax Code | 本地运行时的 turn 租约绑定的会话元数据：租约 owner 的 pid 必须是当前调用方的祖先进程，再取该会话最新一条模型计量记录 |
| Kimi Code CLI | 当前 Kimi 祖先进程的原生 cwd 定位当前目录会话；只接受当前进程运行期唯一更新会话，并读取其 wire 最新 `llm.request.model`；多会话、过期或未来记录不核实 |
| Kimi Desktop | 活动 turn 经原生 `backgroundTasks.list` 的 running Bash PID 与启动时间绑定当前执行 shell，再以精确会话 wire 的 `usage.record` 和 `llm.request` 交叉核对模型 |
| DSH | 官方 `shellEnv` 扩展绑定当前 tool call 与生成它的 assistant response；只使用 provider 返回的 `responseModel`，并核对 DSH 祖先进程、session 与有效期 |
| OpenCode | 1.18.32通过官方shell.env插件绑定精确运行工具；2.0.27/2.2.5通过原生shell绑定精确会话。分别只读V1/V2 SQLite请求元数据，均为requested-only，不自动放行提交 |

读取器只取当前调用方元数据；Codex、Kimi Code CLI 与 Kimi Desktop 的记录尾部有 4 MiB 上限，SQLite 只读查询指定会话的元数据字段。
配置默认值、同目录的其他会话、全局最近日志与无来源的环境变量不构成核实。原生读取失败保留提示与未核实状态，
未把观察接口定义本身当作覆盖证据。自动来源和未知回退都进入身份回归测试。

DSH 适配文件为 [`dsh_plugin.mjs`](../packages/everagent-core/src/everagent_core/identity/dsh_plugin.mjs)，
使用 0.2.1-rc.2 的官方插件接口，需在所用 profile 加载。每次 shell 调用只写不含正文的临时模型元数据，
调用完成即删除；core 读取上限 4 KiB、有效期 5 分钟。请求别名与返回模型分开记录，缺少返回型号保持未核实。
macOS/Linux 支持原生 Node 启动；容器里的设备身份仍由容器自身事实决定，不冒充宿主。Windows DSH 未验证。

### OpenCode：请求元数据与返回模型分开

V1实现对应官方[`anomalyco/opencode@545f51d26cc39a907d2867492d498d9607ea5fa4`](https://github.com/anomalyco/opencode/tree/545f51d26cc39a907d2867492d498d9607ea5fa4)（1.18.32）。
`packages/opencode/src/tool/shell.ts:416–426`的官方`"shell.env"`提供当前sessionID/callID；
[`opencode_plugin.mjs`](../packages/everagent-core/src/everagent_core/identity/opencode_plugin.mjs)只转交这两个ID和运行进程PID，
无会话绑定时清空继承值，不保存正文或生成模型证明。可由原生配置`plugin`加载该文件的`file://`URI，
或以`.js`文件安装到既有OpenCode配置的`plugins/`目录；加载作用于该配置的后续原生运行，不重启已有任务。

Go读取器要求同一OpenCode祖先进程、精确session/cwd、`part`中唯一运行的Bash call，按FK关联该assistant；
只投影模型/provider/variant/时间等标量，不按同目录最近会话猜身份。未知版本、工具已完成、跨会话、过期、
两次快照变化或数据损坏保持不可用。`request_observation.binding=active-tool`说明调用绑定，不说明返回型号。
`prompt.ts`写入的assistant.modelID仍是请求模型，`llm/ai-sdk.ts`与`processor.ts`未提供可用的provider返回型号；
因此绑定修复后仍为requested-only。这是自动诊断的准确缺口，不用代理拦截、用户声明或配置值伪装自动成功。

V2实现对应官方`anomalyco/opencode@1f4d07a4a519185955ae8ab2ea3607805509e386`（2.0.27）：
`packages/core/src/tool/plugin/shell.ts:199–218`在公共shell create.before hook之后设置OPENCODE_SESSION_ID；
公共hook本身没有session/message/tool字段，不能照搬V1 shell.env或借同目录最近会话。
`packages/schema/src/session-message.ts:212–237`的Assistant.model和`packages/core/src/session/model-request.ts:239–256,355–363`
的http.response事件model均是请求Model.Ref，通用V2 schema没有provider responseModel。

读取器只接受OPENCODE=1、合法native session及唯一OpenCode祖先进程；读取前后核对该PID创建身份和cwd，
要求调用方cwd、祖先cwd、session_v2.directory精确一致。默认读取XDG数据根下opencode/opencode.db，
无XDG时为用户.local/share/opencode；可通过readers配置root或明确OPENCODE_DB定位，不枚举其他数据库。
`:memory:`、未指明的其他channel布局、相对路径逃逸、symlink、未知schema/版本或跨目录工具调用保持不可用。
V2支持存储行version=2.0.27/2.2.5；这不是当前可执行程序版本证明，旧会话行及Windows原生cwd绑定尚未验证。

SQLite只读事务先按id+directory筛session，再取该session最新assistant的有界标量：model id/provider/variant、
created/streamed/completed及更新时刻；不返回或解码正文/工具输入输出，不读其他session或凭据表。
workspace/fork或存在location-switched时保守拒绝；两次精确快照不同、记录早于进程、过期/未来/损坏、
后续模型选择改变均不借旧条目。最新provider流未结束时不可用；streamed已记录但工具未结算时仅返回
`request_observation.step_completed=false`的请求元数据，不能当作完整回复或当前provider模型证明。

自动成功读取后：`requested_model`及`request_observation`保留来源/范围摘要/时间/provider/variant，
`model=unknown`、confidence=requested、current_model_confirmed=false；diagnose说明provider-response-model-unavailable。
实际模型仍可由用户明确声明，且与原生requested分列。V2不声称精确tool-call绑定，两版均不声称provider返回型号；
不为取得返回型号读取完整响应。有更强原生证据时再独立适配和验收，合成回归不代替真实客户端验收。

### 自动核实失败的修复路径

`eacli session diagnose --json` 或在公开仓根运行
`go -C packages/everagent-core run ./cmd/everagent-identity diagnose --json` 返回当前调用方的
`automatic_probe`、原因码、公共 owner、复验入口和最后的用户兜底条件。安装 core 使用
`everagent-identity diagnose --json`。成功的常规 inspect 保持原有精简输出，诊断按需展开。

自动核实失败时，当前身份保留 `model_reason_code`，Session 映射为
`actor.model.automatic_reason_code`；原因来自该次观测，成功时不输出此字段。
eacli diagnose 的 session 与 `diagnosis.identity/automatic_probe` 复用同一次身份观测。
诊断只读，不保存成功缓存或修复记录；另一次 diagnose/current 成功不能解释或追溯认证先前失败。

Agent 可以在任务授权内修复 harness 分类、进程/session 绑定或原生模型读取器；先读诊断所指 owner，
以当前会话元数据或独立合成 fixture 为依据，补针对性回归并复验。读取器失败只提供实际能判断的原因，
`native-metadata-unavailable-or-invalid` 不推断更具体的文件、租约或记录问题。不得为排障扫描全局最近对话、
读取对话正文、借另一会话的模型、把配置升级为实测或自行设置用户确认。

模型未核实阻断提交，已授权的源码修复与只读工作继续。没有可信原生字段、当前来源不可访问或修复后仍
无法核实时，才请求用户给出缺失事实；harness未识别时先修分类，确实不可核实才用绑定当前执行范围的用户声明，不能伪装成自动识别。
诊断元数据和 `repair.order` 不构成模型证据，也不授权安装、权限或生产配置变更。

Claude Code 从自身用户配置目录的 `projects/<cwd 编码>/<session UUID>.jsonl` 读取元数据。
调用方需保留真实 `CLAUDE_CODE_SESSION_ID`；无人值守 wrapper 同时用原生 `--session-id` 启动对应 UUID。
工具 shell 切换到其他工作树、当前 cwd 下没有该记录时，macOS/Linux 可从当前 Claude 祖先进程的
cwd 定位同一 UUID 的唯一原生项目文件；分别使用精确 PID 的 `lsof -d cwd` 或 `/proc/<pid>/cwd`，
读取前后核对进程创建身份，不枚举项目或其他进程。记录中的 cwd 仍须等于该原生项目目录。
当前候选已存在但损坏、过期或不可信时不换目录借证据；原生定位不可用时仍保持未核实。Windows
使用原生进程 cwd 读取器并复核进程创建身份，仍拒绝与当前原生项目目录不匹配的记录。
读取器只解码 session、cwd、时间、assistant UUID 与模型字段，跳过对话正文；文件尾部上限 4 MiB，
单行上限 128 KiB。缺记录、关闭 session persistence、错误 cwd、sidechain、重启、过期或模型字段缺失
均不核实。该规则不把普通 Python executor 识别为 Agent，也不允许静态 `AGENT_ID` 署名。

Claude 的 assistant UUID 标识单条回复，`observation_ref` 随新回复更新并保留为来源证据；它不是新的
提交身份。提交门禁仍前后读取新鲜原件，仅在两次都由原生 Claude 读取器核实、模型与绑定
进程/session/terminal 的 `scope_ref` 均未变化时允许回复推进。其他 adapter 的 turn 引用继续参与比较；
失去核实、模型或绑定改变、声明变化仍阻断。身份变化错误只列出变化字段名，不输出模型、引用或私有原件值。

Claude 原件正在追加、末行 JSON/UTF-8 尚未写完，或读取时钟早于并发写入时，读取器只对同一路径最多
重读三次，两次之间等待 20 ms 并重新取时间。持续未完成返回 `native-observation-in-progress`；不跳过
末行借用旧模型。完整畸形记录、超大记录或缺少最新 assistant 绑定分别给出
`native-metadata-invalid`、`native-record-oversized`、`native-assistant-binding-invalid`，不自动重试或放行。
Go 读取器不输出 `retry_count`。复现某种输入失败不等于证明历史失败原因；缺当时原件时
保留待验证，不能用当前重试成功代替历史证据。

ZCode Desktop 无会话环境变量；会话标签出现在 Bash 工具 shell 启动命令的
`~/.zcode/cli/exec/bash-startup/<会话标签>/` 路径中。读取器沿调用方祖先链逐个用 `ps` 读 shell 命令行，
直到找到携带会话标签的执行 shell（hook 包装层 sh/git 不带标签），再在
`~/.zcode/cli/rollout/model-io-<会话标签>.jsonl` 尾部（4 MiB 上限）按字段顺序锚定请求记录前缀
（completedAt/durationMs/requestId/attempt/model.modelId），从不解码 `request` 正文。会话标签缺失、
rollout 或记录过期（>5 分钟）、记录早于 zcode-cli 进程创建时间、模型字段非法或最近请求记录不可用
均不核实；常驻 zcode-host 不是会话 owner，进程链最近匹配必须是会话级 zcode-cli。

MiniMax Code Desktop 同样没有会话环境变量，且 Bash 工具起的是普通 `/bin/bash -c`，命令行不含会话标签。
运行时把正在执行的 turn 租给对应进程：`~/.minimax/v2/sqlite/runtime-state.sqlite` 的
`local_runtime_session_locks` 以 `session_id` 为主键，`owner_id` 形如 `turn-lease:<pid>:<uuid>`。
读取器只接受 owner 的 pid 属于当前调用方祖先链且租约未过期的记录；租约必须唯一命中一个会话，
否则视为无法区分而不核实。随后取该会话 `local_runtime_token_usage` 中最新一条模型计量记录，
要求时间在 5 分钟内、不早于调用方进程创建时间，模型字段去掉供应商前缀后按模型 ID 校验。
读取器只读运行时元数据表，从不打开会话记录与对话正文。租约缺失、过期、归属他人进程、
同时命中两个会话、计量记录过期或模型字段非法均不核实。

Kimi Desktop 也无会话环境变量。读取器从 `KIMI_SHARE_DIR` 或平台用户数据目录定位
`daimon/agents/main/runner.state.json`，要求 runtime 正在运行、控制端点为 loopback WebSocket，
且 endpoint/daemon PID 一致并属于当前调用方祖先。只枚举其中有界的 `activeKernelTurns`，
不按最近更新时间、active conversation 或 focused pane 猜会话。Go 读取器在内存中使用控制令牌调用
`backgroundTasks.list`（`activeOnly=true`），只消费任务元数据；令牌不进入命令行、查询输入或输出。
同一运行 Bash 任务的 PID 必须命中 App 之前的祖先 shell，任务与 shell 启动时间相差不超过 2 秒，
且任务不早于活动 turn；所有候选合计必须恰好一个绑定。并行会话、重复绑定、他人或结束任务均不核实。

绑定后按 agent、conversation key 与 kernel session 精确查询只读 `conversations.sqlite`，要求 workspace
包含当前 cwd，记录文件是 wire 根内符合 `<workspace>/<session>/agents/main/wire.jsonl` 形状的普通文件，
拒绝 symlink 和越界路径。只扫描尾部 4 MiB，按记录前缀定位最新的 `usage.record` 与 `llm.request`，
只解码 allowlist 标量字段，不解析工具记录和对话正文；单条相关记录上限 128 KiB，最新相关记录损坏或
超大时不借旧模型。计量必须属于 turn，请求必须为 `loop`/`kimi`，两者模型一致且时间相差不超过 2 秒；
模型时间须在 5 分钟内，不早于活动 turn 或 App 创建时间。model alias 若存在必须合法，但不要求与模型同名。
这些原生记录没有请求级关联 ID，因此不声称有该证据；配置默认值与其他会话记录均不兜底。

cursor-cli（Cursor Agent）尚无自动模型读取器。用户声明绑定祖先链中的 `sand-exit-watch`
与会话环境；通用 `node` 进程不构成身份。绑定顺序由公共 `declarations.go` 的 `factScope` 拥有：

1. 必须有 `sand-exit-watch` 锚点，否则整段 scope 为未绑定（`None`）。
2. 若存在合法 `CURSOR_CONVERSATION_ID`，写入 `session_ref`。
3. 若存在合法 `ORCA_TERMINAL_HANDLE` 或 `HERDR_PANE_ID`，写入 `terminal_ref`（可与 `session_ref` 并存）。
4. **仅当**没有 `session_ref`，且（宿主属于 Desktop 应用，或也没有 `terminal_ref`）时，才退到当前执行 shell 的 `execution_ref`。
5. 因此：缺少会话键但已有 `terminal_ref` 时，cursor-cli（非 Desktop）**不会**再加 `execution_ref`，而是以 `process_ref`+`terminal_ref` 为界；并非“缺会话键就一定退到 `execution_ref`”。缺少 `sand-exit-watch` 则保持未绑定。

此次能力是 harness／会话识别，**不是** Cursor 自动模型核实；提交仍需真实模型证据或用户明确声明。

模型声明要求 `--user-confirmed`，它表示用户本次明确指定，不能由 Agent 根据配置自行补旗标。receipt 仅存在本机用户状态目录；默认 4 小时，最长 12 小时。harness 进程或 session/terminal 改变、
嵌套 harness、模型提示变化、过期或记录损坏都会使声明失效。声明一直保持
`current_model_confirmed=false`，通过 `user_model_declared=true` 单独表达依据。
Desktop 缺原生 conversation ID 时，即使继承了 terminal 环境变量，也只在 App 下的当前执行 shell 内复用；
App 外层的启动 shell 不构成执行依据。新批次按用户已明确指定的模型重声明，不能跨对话借用。

`AGENT_ID`/`AGENT_MODEL` 和一般供应商 model 环境变量只作兼容或提示；Pi 的当前 shell context 按上表核实。
旧 Git 配置、历史对话、全局最近日志不放行。

## 脚本描述与门禁

[`scripts/script-catalog.json`](../scripts/script-catalog.json) 登记本族的目的、唯一 owner、canonical/compatibility/internal、
平台、依赖、输入、输出、副作用、授权 owner 和范围。它不取代能力目录或 Skill。
[`SCRIPT_INDEX.md`](../scripts/SCRIPT_INDEX.md) 是生成视图；
`go -C packages/everagent-core run ./cmd/ea-quality scripts --check` 按需查看和校验。

新增或改名必须更新目录，保留已承诺的兼容入口并验证转发。门禁校验目录 schema、唯一 ID/alias、owner/路径、
索引哈希和行为测试；算法移动不要求旧 wrapper 继续出现实现源码。

## 验证边界

公共测试用 fixture 验证模型声明失效、调用方祖先、Desktop 区分、catalog、Git tree 与 trailer。
安装态和真实原生任务由私仓验收；Windows fixture 通过不能写成 Windows 真机通过。
原生接口不提供的模型或任务字段保持未知，已授权的源码和只读工作仍可继续。
