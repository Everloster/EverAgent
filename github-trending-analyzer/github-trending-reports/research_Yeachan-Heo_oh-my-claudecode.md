# Yeachan-Heo/oh-my-claudecode

> Teams-first Multi-agent orchestration for Claude Code

## 项目概述

oh-my-claudecode（简称 OMC）是一个面向 Claude Code 的多智能体编排插件，目标不是替代 Claude Code 本体，而是在其上方叠加“团队执行层”。它把单一助手扩展成一组可分工的代理、技能、模式和运行时工具，让用户以更接近“指挥团队”而不是“亲自逐步操作”的方式完成编码、审查、调试和规划任务。

从 README、官方文档和仓库结构综合看，OMC 的核心卖点有三层。第一层是 **Team-first orchestration**，即把多代理执行视为主流程而不是附加功能；第二层是 **tri-model routing**，明确把 Claude、Codex、Gemini 放入一个统一编排表面；第三层是 **runtime hardening**，持续加强 stop-hook、worker 生命周期、tmux pane 管理、通知和运行时护栏。这使它不只是“提示词集合”或“技能仓库”，而更像一个围绕 Claude Code 的工作流操作系统。

更重要的是，OMC 已经表现出明显的产品化倾向：有官网、文档站、CLI、插件市场安装路径、版本化 release note、Discord 社区和较完整的 agent catalog。对于 GitHub Trending 观察来说，它代表的是一个更成熟的 `agentic coding runtime` 方向，而不是单次爆红的 workflow 模板项目。

## 基本信息

| 指标 | 数值 |
|------|------|
| Stars | 12,249 |
| Forks | 825 |
| 语言 | TypeScript 为主，辅以 JavaScript / Shell / Python / Dockerfile |
| 今日增长 | 日榜抓取时约 +576 ⭐ |
| 开源协议 | MIT |
| 创建时间 | 2026-01-09 |
| 最近更新 | 2026-03-26 |
| GitHub | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |

补充观察：

- 贡献者约 64 人，社区参与度已经超过“个人项目爆红”的典型形态。
- 最新 release 为 `v4.9.1`（2026-03-24）。
- topic 明确指向 `agentic-coding`、`claude-code`、`parallel-execution`、`multi-agent-systems`。

## 技术分析

### 技术栈

从仓库和文档可见，OMC 的技术栈很鲜明：

- **主语言**：TypeScript
- **CLI / 插件形态**：面向 Claude Code 插件与命令行工作流
- **辅助语言**：Shell 与 Python 用于桥接、脚本与外部工具协同
- **会话/多工基础设施**：tmux 为核心，Windows 则通过 `psmux` 兼容
- **多模型协同**：支持 Claude、Codex、Gemini 等外部 CLI / provider 路由
- **MCP 工具链**：文档明确提到 25+ MCP tools，覆盖语言服务、AST grep、Python REPL 等

从实际产品定位来看，OMC 的技术重点不是自研模型，而是 **把多模型、多代理、多工具、多会话组合成可用的执行运行时**。

### 架构设计

OMC 当前最值得关注的，是它已经形成了相对稳定的分层架构：

1. **编排层**
核心是 Team 模式和 staged pipeline。官方文档明确给出：

`team-plan → team-prd → team-exec → team-verify → team-fix`

这意味着它不是简单地“并发开多个 agent”，而是把多代理协作包装成一个显式分阶段流水线。

2. **执行层**
`omc team` 可以直接拉起真实的 tmux worker panes，让 `claude`、`codex`、`gemini` 各自作为独立 worker 运行。这一点非常关键，因为很多“多代理框架”其实只是逻辑上的角色切分，而 OMC 强调的是 **真实外部 CLI worker 进程**。

3. **技能与代理层**
仓库中有大量 `agents/*.md`，包括 `architect`、`executor`、`qa-tester`、`security-reviewer`、`tracer`、`verifier` 等角色。README 里写“32 specialized agents”，而文档首页写“19 agents across 3 lanes”。这说明项目近期做过 agent catalog 收敛，文档和 README 存在轻微版本漂移，但也反过来说明项目处在高频重构状态。

4. **状态与记忆层**
文档明确存在 `.omc/notepad.md`、`.omc/project-memory.json`、`.omc/state/`、`.omc/sessions/*.json` 等状态文件。换句话说，OMC 正试图把“长会话上下文”和“可恢复执行状态”做成运行时能力，而不仅靠单轮 prompt。

5. **集成与通知层**
包含 Discord、Telegram、Slack、Webhook、OpenClaw 集成，以及 stop callback 配置。这类能力通常出现在更接近“运维化使用”的工具里，而不是纯演示型代理框架。

### 核心功能

结合 README、文档与 release notes，当前最核心的功能可以概括为：

- **Team 模式**：显式团队编排，是当前推荐主入口
- **CLI worker orchestration**：真实拉起 Codex/Gemini/Claude worker panes
- **Tri-model synthesis (`/ccg`)**：让 Claude 汇总 Codex 与 Gemini 的结果
- **Magic keywords / mode system**：包括 autopilot、ralph、ultrawork 等模式
- **技能系统**：支持项目级和用户级技能目录
- **HUD / observability**：实时显示 orchestration 状态、token 使用和 agent heartbeat
- **Notifications & OpenClaw integration**：适合远程监控与自动化对接

可以说，OMC 的真正价值并不是“单个功能多强”，而是 **把一整套本来离散的 coding-agent 能力整合进统一表面**。

## 社区活跃度

### 贡献者分析

当前约 64 位贡献者，已经明显超过“单作者主导的脚本仓库”阶段。README 尾部还有自动生成的 `Featured Contributors` 区块，说明项目已经开始把社区运营和自动化文档维护纳入正式流程。

从 release 信息看，维护者本人仍是最主要的方向推动者，但已有一批持续贡献者参与 agent、hook、build、Windows 支持、文档和 runtime 稳定性改进。对这类高节奏工具来说，这通常意味着项目有一定持续性，不完全依赖一次性流量。

### Issue/PR 活跃度

当前 open issues 约 19，但这并不表示项目“改动少”，反而说明许多修改以 PR 形式高速流动。最近一天的 PR/issue 活动非常活跃，主题包括：

- TypeScript 构建稳定性（如 `TS2589` 深类型问题）
- 独立 MCP server 注册保护
- 安全、稳定性和代码质量修补
- Obsidian CLI MCP 集成

这类信号说明 OMC 当前最重要的工程焦点是：**在快速扩展功能的同时，努力把运行时做稳**。

### 最近动态

近期版本演进非常密集，几个节点尤其值得注意：

- **v4.7.x**：强调 Team runtime、CLI worker、通知、路由和 HUD 稳定性
- **v4.8.x**：更强的 runtime hardening、remote MCP、stop-hook 与安全加固
- **v4.9.0**：强调 autoresearch、team/runtime reliability、安全路径修补
- **v4.9.1**：继续修 HUD、worker duplication、Windows `.cmd`、plugin cache sync、ask skill 安全等问题

一个很明确的结论是：OMC 已经从“新增功能冲刺期”进入“新增功能 + 工程稳态并重期”。

## 发展趋势

### 版本演进

从公开文档和 release note 可以重建出相对清晰的演进脉络：

- **早期阶段**：以 Claude Code 增强、技能和关键词工作流为主
- **Team 架构阶段**：从 `swarm` 等旧入口迁移到更显式的 Team 模式
- **CLI worker 阶段**：Codex / Gemini 不再只是被动 provider，而是实际 worker 进程
- **运行时硬化阶段**：集中修 stop-hook、tmux、worker 生命周期、安全与平台兼容性

这条路线说明 OMC 的核心问题意识非常明确：不是“如何多加功能”，而是“如何让多代理系统在真实终端环境里稳定活下去”。

### Roadmap

虽然项目没有在 README 中给出特别正式的 roadmap 文档，但从文档和 release note 可以推测后续重点大概率还会落在这几个方向：

- 更成熟的 Team API 与任务管理
- 更稳定的 tri-model 路由与 provider 协调
- 更强的安全治理与 runtime guardrails
- 更多工作流模板与技能生态
- 更细粒度的 observability、cost tracking、session replay

### 社区反馈

社区对 OMC 的评价大致可以分成两种：

- **积极面**：它比很多“概念化 agent 框架”更接近真实 coding workflow，尤其适合已经重度使用 Claude Code 的人
- **顾虑面**：模式多、层级深、tmux / CLI / hook / MCP / skills 叠加后，系统理解成本不低，出问题时排查也比简单插件困难

一个值得注意的小信号是：README 与文档里关于 agent 数量、模式表述、某些命令入口存在轻微漂移。这不一定是坏事，但它说明项目演进非常快，文档同步压力已经开始显现。

## 竞品对比

| 项目 | Stars | 语言 | 特点 |
|------|-------|------|------|
| oh-my-claudecode | 12,249 | TypeScript | 围绕 Claude Code 的团队编排层，强调 Team 模式、CLI worker、多模型协同 |
| bytedance/deer-flow | 47k+ | Python | 更完整的 Agent runtime / sandbox / memory 系统，定位更平台化 |
| agentscope-ai/agentscope | 20k+ | Python | 开发者中心的 Agent 框架，强调可见、可控与 runtime 生态 |

更细一点地看：

- **相较 deer-flow**：OMC 更贴近 Claude Code 使用者，切入点更“插件化”和 workflow 化；deer-flow 更像独立 agent runtime 平台
- **相较 AgentScope**：OMC 更强调终端体验、agentic coding 和 CLI worker；AgentScope 更偏框架与平台组合
- **相较技能仓库类项目**：OMC 的优势在于有强运行时和调度层，而不只是 skill collection

## 总结评价

### 优势

- **产品定位清晰**：不是泛化“AI coding everything”，而是明确服务于 Claude Code 编排
- **运行时能力强**：真实 tmux worker、通知、HUD、state、OpenClaw 集成都很完整
- **版本迭代快**：最近 release notes 显示维护节奏非常高
- **团队协作导向强**：Team pipeline 和 tri-model 路由有明显差异化
- **工程意识成熟**：对 stop-hook、platform compatibility、security hardening 的投入很持续

### 劣势

- **系统复杂度较高**：模式、代理、技能、hooks、MCP、tmux 叠加后理解成本不低
- **生态绑定明显**：高度依赖 Claude Code 场景，对非 Claude 用户吸引力有限
- **文档同步压力开始出现**：README 与文档间已有轻微漂移
- **稳定性挑战依然存在**：release note 中大量修补项说明系统仍处于快速收敛阶段

### 适用场景

- 已经把 Claude Code 当作主力终端开发环境的用户
- 想把代码实现、审查、设计、验证拆给不同代理处理的小团队
- 需要多模型协同而不想自己手搓整套 orchestrator 的高级用户
- 对通知、会话管理、可观测性有要求的长期 coding-agent 使用者

不太适合的场景：

- 只想装一个极简技能包、几乎不需要编排层的用户
- 不使用 tmux 或不愿接受较复杂运行时约束的开发者
- 希望最小学习成本快速体验“单代理”流程的人

---
*报告生成时间: 2026-03-27 00:05:00*
*研究方法: GitHub API 多维度分析 + 官方 README + 官方文档站 + release notes + 近期 PR/issue 活动交叉核对*
