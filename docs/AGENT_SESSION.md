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

公共仓不接收私有设备、地址、账号、拓扑和任务数据。eacli 是统一使用入口，Orca/Herdr 继续拥有原生编排。

## 明确回答的问题

Session v2 区分 `actor`（harness 与模型）、`execution`（当前执行设备）、`caller`（来源）、
`host`（当前 runtime 或 Desktop）、`checkout`（实际 Git 工作树）、`task`（原生绑定）、`readiness`。
设备、终端、仓库、模型和任务各自保留来源与核实状态，不能把宿主的默认模型或 focused pane 当作调用方事实。

个人桌面场景支持命令行和 Desktop。**Kimi Desktop 是独立的 macOS/Windows App**，身份为
`kimi-desktop`；Kimi Code CLI 身份为 `kimi-cli`。ZCode、MiniMax Code 也作为 Desktop 宿主识别。
Windows 的 Kimi 分类使用调用方可执行文件的产品目录与路径，不能仅靠文件名大小写。
App 身份或版本可见不代表当前模型可见；无法核实时保持 unknown/configured，等待用户明确指定。

基础设施工作场景只消费已有原生任务元数据；环境 task ID 是 hint。任务确认要求精确 caller 和原生 owner
记录一致；普通 executor 不冒充 Agent。没有现成任务绑定时报告 unbound/unverified，不另建 controller 或 ledger。

## 模型证据与声明

| 字段/状态 | 含义 | 可用于提交 |
|---|---|---|
| requested | 原生派工请求的模型 | 否 |
| configured | 配置或环境中的候选模型 | 否 |
| observed / session-bound | 新鲜、精确会话范围的原生模型观测 | 是 |
| user-declared / declared | 用户明确指定的本会话模型 | 是 |
| unknown | 无依据 | 否 |

原生观测必须来自受支持 adapter，绑定 harness、进程创建身份、session/terminal 并通过新鲜度检查。
**先自动核实，只有自动路径没有当前会话证据时才请用户指定。** 重构必须保留已核实的读取能力。

| 自动来源 | 核实依据 |
|---|---|
| Codex | 当前 thread 的 `turn_context.model`；长 turn 用精确 SQLite 运行态索引与同 thread 的新鲜 usage 元数据核对 |
| Pi | shell 工具每次启动清除继承值，再从当前 session/model 注入的 `PI_SESSION_ID`、`PI_MODEL` |
| TRAE | 精确 thread 的运行日志模型字段与请求时间；支持原有 thread alias，嵌套 Codex 不借外层 ID |
| Claude Code | 精确 UUID session 的原生 assistant `message.model`；绑定当前调用方进程创建时间、cwd 和新鲜记录，不借配置中的模型 |
| ZCode | 当前会话 `model-io-<会话标签>` 请求记录前缀的 `modelId`；会话标签取自本执行 shell 启动命令的 bash-startup 路径，绑定 zcode-cli 进程创建时间与新鲜完成记录 |

读取器只取当前调用方元数据；Codex 日志尾部有 4 MiB 上限，SQLite 只读查询指定 thread 的模型字段。
配置默认值、同目录的其他会话、全局最近日志与无来源的环境变量不构成核实。原生读取失败保留提示与未核实状态，
未把观察接口定义本身当作覆盖证据。自动来源和未知回退都进入身份回归测试。

Claude Code 从自身用户配置目录的 `projects/<cwd 编码>/<session UUID>.jsonl` 读取元数据。
调用方需保留真实 `CLAUDE_CODE_SESSION_ID`；无人值守 wrapper 同时用原生 `--session-id` 启动对应 UUID。
读取器只解码 session、cwd、时间、assistant UUID 与模型字段，跳过对话正文；文件尾部上限 4 MiB，
单行上限 128 KiB。缺记录、关闭 session persistence、错误 cwd、sidechain、重启、过期或模型字段缺失
均不核实。该规则不把普通 Python executor 识别为 Agent，也不允许静态 `AGENT_ID` 署名。

ZCode Desktop 无会话环境变量；会话标签出现在 Bash 工具 shell 启动命令的
`~/.zcode/cli/exec/bash-startup/<会话标签>/` 路径中。读取器沿调用方祖先链逐个用 `ps` 读 shell 命令行，
直到找到携带会话标签的执行 shell（hook 包装层 sh/git 不带标签），再在
`~/.zcode/cli/rollout/model-io-<会话标签>.jsonl` 尾部（4 MiB 上限）按字段顺序锚定请求记录前缀
（completedAt/durationMs/requestId/attempt/model.modelId），从不解码 `request` 正文。会话标签缺失、
rollout 或记录过期（>5 分钟）、记录早于 zcode-cli 进程创建时间、模型字段非法或最近请求记录不可用
均不核实；常驻 zcode-host 不是会话 owner，进程链最近匹配必须是会话级 zcode-cli。

模型声明要求 `--user-confirmed`，它表示用户本次明确指定，不能由 Agent 根据配置自行补旗标。
receipt 仅存在本机用户状态目录；默认 4 小时，最长 12 小时。harness 进程或 session/terminal 改变、
嵌套 harness、模型提示变化、过期或记录损坏都会使声明失效。声明一直保持
`current_model_confirmed=false`，通过 `user_model_declared=true` 单独表达依据。
Desktop 缺原生 conversation ID 时，即使继承了 terminal 环境变量，也只在 App 下的当前执行 shell 内复用；
App 外层的启动 shell 不构成执行依据。新批次按用户已明确指定的模型重声明，不能跨对话借用。

`AGENT_ID`/`AGENT_MODEL` 和一般供应商 model 环境变量只作兼容或提示；Pi 的当前 shell context 按上表核实。
旧 Git 配置、历史对话、全局最近日志不放行。

## 脚本描述与门禁

[`scripts/script-catalog.json`](../scripts/script-catalog.json) 登记本族的目的、唯一 owner、canonical/compatibility/internal、
平台、依赖、输入、输出、副作用、授权 owner 和范围。它不取代能力目录或 Skill。
[`SCRIPT_INDEX.md`](../scripts/SCRIPT_INDEX.md) 是生成视图；`script_catalog.py list|show` 可按需发现。

新增或改名必须更新目录，保留已承诺的兼容入口并验证转发。门禁校验目录 schema、唯一 ID/alias、owner/路径、
索引哈希和行为测试；算法移动不要求旧 wrapper 继续出现实现源码。

## 验证边界

公共测试用 fixture 验证模型声明失效、调用方祖先、Desktop 区分、catalog、Git tree 与 trailer。
安装态和真实原生任务由私仓验收；Windows fixture 通过不能写成 Windows 真机通过。
原生接口不提供的模型或任务字段保持未知，已授权的源码和只读工作仍可继续。
