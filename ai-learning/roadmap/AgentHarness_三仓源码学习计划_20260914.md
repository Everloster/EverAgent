# Agent Harness 三仓源码学习计划（codex / deepseek-harness / pi）

> 2026-09-14 用户拍板启动（「三家源码学习实践，类似 vllm 学习计划」）。定位：ai-learning「Agent/Harness 工程线」长期主线。
> 形式仿 [vLLM 源码级学习计划](./vLLM_源码级学习计划_20260821.md)：阶段制、每阶段对照真实源码出报告、每完成一阶段回填进度。
> 与 vLLM 线的关键差异：**三仓横向对照**——同一子系统，看三家怎么各自实现，训练的是"设计取舍"的眼光，不只是"读代码"。

## 对齐决策（2026-09-14）

| 维度 | 拍板 |
|------|------|
| 深度目标 | **源码级 + 对照式**：核心路径读真实源码，能讲清三家各自的取舍；非核心模块架构级带过 |
| 学习对象 | 三仓固定：codex（OpenAI）、deepseek-harness（DeepSeek）、pi（earendil-works/badlogic） |
| 报告体裁 | **直接深度专业**（对照源码主题，不走科普开路）；存量科普当预科（见下） |
| 范围节奏 | 七阶段 + 验收，长期主线慢慢啃；每阶段收反馈再排下一阶段 |

## 三仓档案（源码基准）

| | codex | deepseek-harness（dsh） | pi |
|---|---|---|---|
| 本地路径 | `../codex` | `../deepseek-harness` | `../pi` |
| 厂商 | OpenAI | DeepSeek | earendil-works（badlogic / Mario Zechner） |
| 语言形态 | Rust workspace（`codex-rs/` 100+ crate） | TS pnpm monorepo（`packages/*/*` 50+ 能力域包 + python SDK + native） | TS monorepo（`packages/` 11 包） |
| 架构哲学 | 产品级巨石：安全工程拉满（execpolicy/多平台沙箱/process-hardening） | **everything-is-a-plugin**，基于 Cordis 时空可组合范式（arXiv 2608.25512） | **极简内核**：一个 agent loop 讲清楚，无内置权限系统，沙箱/扩展全外置（self-extensible） |
| pin 基准 | `5b1d656018`（2026-09-14 pull，main） | `c291e7961a`（v0.1.5，master） | `71dca87`（2026-09-14 clone，main） |
| 关键入口 | `codex-rs/core`、`codex-rs/protocol`、`codex-rs/tui` | `packages/core/core`、`packages/llm`、`apps/`（web/desktop） | `packages/agent/src/agent-loop.ts`、`packages/coding-agent/src/main.ts`、`packages/ai` |
| 快速跑法 | `npm i -g @openai/codex`（或 cargo build，重） | `npx @deepseek-ai/dsh web`（:3080 Web UI） | npm 全局装 coding-agent，配 OpenAI 兼容 key |

## 一根主线

**「一个 agent turn 的一生」**——用户输入进来 → prompt 组装 → LLM 调用 → 工具调用解析 → 审批与沙箱执行 → 结果写回上下文 → 循环或终止。每阶段拆这条生命线的一环，**三家同题对照**；封顶报告即三张并排的完整一图流 + 取舍总表。

辅助对照主线：**同一任务三家各跑一遍**（如"在空目录写一个 todo CLI"），拿各自的 trace/session 文件回源码对账——harness 独有的实验手段，vLLM 线没有的玩法。

## 存量加速项（不复读，直接当预科）

- [Agent Harness 请求全链路深度解析](../reports/knowledge_reports/Agent_Harness请求全链路_深度解析_20260709.md)（07-09）→ **阶段 1 预科**：报文级 tool_calls 循环已讲透，源码阶段补"工程真身"
- [Agent Harness 三大设计流派解析](../reports/knowledge_reports/Agent_Harness_三大设计流派解析.md) + wiki [agent_harness](../wiki/concepts/agent_harness.md) → **阶段 0 预科**：流派框架拿来给三仓对号入座
- [ChatGPT Work 能力面与 Harness 样本深度解析](../reports/knowledge_reports/ChatGPT_Work_能力面与Harness样本_深度解析_20260831.md)（08-31）→ 阶段 5/6 预科：七层 harness 抽象映射表
- Bitter Lesson × Harness 双稿（[深度](../reports/knowledge_reports/Bitter_Lesson_vs_Agent_Harness_推演与网上观点审阅_20260707.md) / [科普](../reports/knowledge_reports/Bitter_Lesson_vs_Harness_科普讲解_20260720.md)）→ 全程底色：读三家时不断问"这层脚手架会被模型吃掉吗"
- wiki [agent_orchestration](../wiki/concepts/agent_orchestration.md) / [agent_interop_protocols](../wiki/concepts/agent_interop_protocols.md) / [agent_observability](../wiki/concepts/agent_observability.md) → 阶段 5 对照素材

## 实验环境备注

- 三家均可本地跑：pi 用现有 GLM/Kimi coding plan key（pi-ai 原生支持 OpenAI 兼容 provider，顺手成为阶段 4 实操）；dsh 一条 `npx` 起 Web UI；codex 用官方 npm 包（账号/key 走用户家底，细节不落本仓）。

## 课程载体：OpenMAIC（2026-09-14 增补，用户拍板「需要 openmaic 课程，这个效果好」）

**vLLM 线「一阶段一循环」模式整体继承**：每阶段 = ①概念课开路（建直觉，到不了源码级——课是地图，码是地形）→ ②源码精读（对照课论断找代码证据标行号）→ ③阶段报告入 reports/。课与源码主线不互相替代。

### 课程序列（骨架 9 节排定，逐批生产逐批收反馈）

| 课 | 暂定课名（系列前缀「Agent Harness」） | 对应阶段 | 核心内容 | 预科存量 |
|----|------|------|------|------|
| 1 | Agent Harness 入门：一个 turn 的一生 | 0/1 开路 | harness 定义与边界（模型之外的脚手架）、turn 完整循环、四件套（prompt 组装/LLM 调用/工具执行/上下文写回） | 请求全链路报告（报文层已懂，课建 turn 级直觉） |
| 2 | Agent Harness 三种哲学：巨石、插件与极简 | 0 | codex 安全工程巨石 / dsh everything-is-a-plugin / pi 极简内核，为什么三家都成立；取舍维度：安全边界放哪、扩展怎么做、复杂度预算 | 三大流派报告、ChatGPT Work 七层映射 |
| 3 | Agent Harness 主循环解剖 | 1 | turn 状态机、流式处理、错误重试、终止条件；pi 一个文件 vs codex/core 的反差 | — |
| 4 | Agent Harness 工具执行与沙箱 | 2 | tool schema/调用解析/审批链；execpolicy、多平台沙箱、pi「不做权限」的外置哲学——三家里反差最大的一课 | — |
| 5 | Agent Harness 上下文工程 | 3 | compaction 触发与策略、context 组装、session 持久化与重放 | 存量「四类上下文治理」论断（请求全链路报告） |
| 6 | Agent Harness 统一 LLM API | 4 | provider 抽象、模型路由、流式解析、OpenAI 兼容适配；可嵌自家 plan 家底实操 | 模型 plan 家底速查 |
| 7 | Agent Harness 插件化与 MCP | 5 | everything-is-a-plugin vs extensions 自扩展 vs codex 插件族 | ChatGPT Work 报告生态层 |
| 8 | Agent Harness 外壳与协议（点菜） | 6 | TUI/Web/Server 三形态、app-server/CBOR 协议设计 | — |
| 9 | Agent Harness 封顶：同一个 turn，三种哲学 | 验收 | 三图流对照 + 取舍总表 + 「哪层会被模型吃掉」（回扣 Bitter Lesson） | Bitter Lesson 双稿 |

- **生产节奏（仿 vLLM 实际演化）**：第一批课 1+2 单做（验证 harness 主题的课程手感）→ 收反馈 → 课 3-7 批量（约 3h 机器时间）→ 课 8 点菜、课 9 等验收。
- **配方照抄制度化版**：slide+quiz only（禁交互/模拟/3D 重型场景）、每页≤5 条要点每条一句话宁少勿多、场景 8、`enableTTS:true`、glm-5.3 主力 + flash 分流轻活、本地 VoxCPM 48kHz 配音。
- **成本预估**：~35 分钟/节（文本 ~8min + TTS ~25min）+ ~30 万 token/节；9 节全量 ≈ 5.5h 机器时间 + ~270 万 token。
- **前置**：OpenMAIC dev server（`cd ../OpenMAIC && pnpm dev`）+ voxcpm-server 先起（配音必须生成时 enableTTS:true，事后无法补）。
- **导出**：`EverAgent/scripts/export_openmaic_courses.py` 需扩第二个系列（当前 SERIES 硬编码 vLLM 关键词、输出 `vLLM课N_*`）——新增 AgentHarness 系列：关键词对**生成后的实际课程名**（教训：课程名优先于场景标题匹配）、输出 `AgentHarness课N_<id>.md` 落 `ai-learning/courses/`。每交付新课重跑导出。
- **合集门户**：`OpenMAIC/public/portal.html`（vLLM 7 节合集页）改造为**双系列门户**（vLLM 区块 + AgentHarness 区块，继续学习按系列记忆）——方案待用户拍板（备选：独立 harness 门户页）。

---

## 阶段 0 · 三仓总览与跑通（约 1-2 次）

- **目标**：三家架构地图 + 目录↔组件映射 + 各自跑通一个最小任务；把「三大设计流派」框架对号入座，看预言准不准。
- **读**：三仓 README/AGENTS.md/docs；codex `codex-rs/core` 顶层与 `protocol` 的消息类型清单；dsh `packages/core` 与 AGENTS.md 的包依赖图；pi `packages/agent/src/agent-loop.ts`（先通读一遍建立"最小 harness"标尺）。
- **动手**：三家各跑同一个任务（空目录 todo CLI），收 trace/session 产物留档，供后续阶段回查。
- **产出**：《三家 Harness 架构总览对照：同一个问题的三种答案》

## 阶段 1 · Agent 主循环（约 2-3 次）

- **目标**：一个 turn 的完整控制流。**从 pi 开始**（agent-loop.ts 最小可读，先立标尺）→ codex `codex-rs/core`（会话状态机、turn 驱动、中断/压缩触发点）→ dsh `packages/core/core`（Cordis 插件化下循环怎么组织）。对照：事件模型、流式处理、错误重试、终止条件。
- **读**：`pi: packages/agent/src/{agent-loop.ts,agent.ts,stream-fn.ts,harness/}`；`codex: codex-rs/core`（主循环与 turn 处理相关文件）、`codex-rs/protocol`；`dsh: packages/core/core`、`packages/session`。
- **动手**：三家各抓一次"多工具串联 turn"的日志，逐行对回源码。
- **产出**：《一个 agent turn 的一生：三份主循环源码对照》

## 阶段 2 · 工具系统与执行安全（约 2-3 次）

- **目标**：tool 定义 schema、调用解析、审批链、沙箱。**哲学反差最大的一环**：codex 把安全做进内核（`execpolicy` + `sandboxing` + linux/windows/mxc 多平台沙箱矩阵 + `process-hardening`）；dsh 有 `sandbox`/`guard`/`code-runtime` 但插件化；pi 干脆**不做**内置权限，外置 Gondolin/Docker/OpenShell 三模式——读三方各自论证。
- **读**：`codex: codex-rs/{tools,exec,execpolicy,sandboxing,linux-sandbox,windows-sandbox-rs,shell-command,shell-escalation,apply-patch}`；`dsh: packages/{sandbox,guard,code-runtime,shell}`；`pi: packages/coding-agent/src/core`（read/bash/edit/write 工具定义）+ `docs/containerization.md`。
- **动手**：各触发一次"危险命令"，观察三家的审批/拦截行为差异。
- **产出**：《工具执行与沙箱：三种安全哲学的源码对照》

## 阶段 3 · 上下文工程与会话（约 2 次）

- **目标**：compaction（压缩）、context 组装、session 持久化与重放。衔接存量《请求全链路》里"四类上下文治理"的论断，找工程真身。
- **读**：`dsh: packages/{compaction,context,session,session-query}`；`codex: codex-rs/{rollout,context-fragments,memories,message-history,history}`；`pi: packages/session-backends/*`、`packages/agent/src/types.ts`（会话数据结构）。
- **动手**：各造一次超长会话触发压缩，抓压缩前后报文对比策略。
- **产出**：《上下文工程三家对照：压缩、组装、持久化》

## 阶段 4 · LLM 接入层（约 1-2 次）

- **目标**：provider 抽象、模型路由、流式解析、错误重试。**pi 的 `ai` 包是主打卖点**（unified LLM API + 模型自动发现），codex 有 `model-provider`/`model-provider-info`/`backend-client`/`lmstudio`/`ollama` 一族，dsh 是 `packages/llm`。
- **读**：`pi: packages/ai/src/{api,compat,providers…}`；`codex: codex-rs/{model-provider,model-provider-info,codex-api,codex-client,responses-api-proxy}`；`dsh: packages/llm`。
- **动手**：三家各挂 GLM coding plan key 实跑（OpenAI 兼容端点），对照各自的 provider 适配代码路径；顺手结清「plan 家底速查」的端点兼容性问题。
- **产出**：《统一 LLM API 的三种做法》

## 阶段 5 · 扩展与互操作生态（约 2 次）

- **目标**：MCP/ACP/插件/技能四件套。dsh "everything-is-a-plugin" 的极致形态 vs codex 的 `codex-mcp`+`rmcp-client`+`core-plugins`+`skills` vs pi 的 extensions 自扩展哲学（示例里就有 custom-provider/gondolin 沙箱）。
- **读**：`dsh: packages/{mcp,acp,extensions,skill,plugins 相关包}`；`codex: codex-rs/{codex-mcp,rmcp-client,core-plugins,plugin,skills,ex}`；`pi: packages/coding-agent/src/extensions` + `examples/extensions/*`。
- **动手**：给 pi 写一个最小 extension、给 dsh 装一个插件，体感两种扩展模型的差别。
- **产出**：《插件化与 MCP：生态接入三种姿势》

## 阶段 6 · 产品形态与前后端分离（约 1-2 次，按兴趣点菜）

- **目标**：同一内核怎么长出不同外壳。pi `tui`+`protocol`（CBOR）+`server`；codex `app-server-*` 协议族（transport/protocol/daemon）+ `tui` + `cloud-tasks`（云端委派）；dsh `apps/` web/desktop + `packages/api`（gateway/controllers）。
- **读**：上表路径 + 各自 IPC/协议定义文件。
- **动手**：任选一家用 server/SDK 模式驱动一次 headless 会话。
- **产出**：点菜后定（候选：《Harness 的外壳：TUI/Web/Server 三种形态的协议设计》）

## 验收（约 1-2 次）

- 试金石一：三仓各挑 1 个近期 PR（共 2-3 个），讲清改了什么、为什么、换到另两家会怎么实现——源码级理解 + 跨哲学迁移双重检验。
- 试金石二：同一任务三家实测对照（阶段 0 任务的进阶版），用产物+trace 讲清行为差异的代码根源。
- **封顶报告**：《同一个 turn，三种哲学：agent harness 源码对照总结》（三张一图流 + 取舍总表 + "哪层会被模型吃掉"预判，回扣 Bitter Lesson 底色）。

---

## 纪律

- 源码引用一律以三仓本地 clone 的 pin 基准为准（见「三仓档案」表）；每阶段开始前 `git fetch` 看一眼相关模块有无大改，有则更新本表 pin 并注明。
- 报告按 ai-learning 规范：frontmatter + 结尾「思考与追问」三问，追问在原报告续写；存量报告已覆盖的概念直接引用不重讲。
- 每阶段交付后收一次学习反馈（懂了 / 卡在哪 / 深度不够），反馈 > 配方自检 > 脚本自检；必要时调整后续阶段顺序（阶段 2-6 允许按兴趣重排）。
- 每完成一阶段：回本文件勾进度 + 更新 MAP.md 覆盖状态。

## 进度

- [ ] 阶段 0 · 三仓总览与跑通
- [ ] 阶段 1 · Agent 主循环
- [ ] 阶段 2 · 工具系统与执行安全
- [ ] 阶段 3 · 上下文工程与会话
- [ ] 阶段 4 · LLM 接入层
- [ ] 阶段 5 · 扩展与互操作生态
- [ ] 阶段 6 · 产品形态与前后端分离
- [ ] 验收 · 封顶对照报告
