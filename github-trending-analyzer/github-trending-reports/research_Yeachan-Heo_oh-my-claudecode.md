# Yeachan-Heo/oh-my-claudecode

> Teams-first Multi-agent orchestration for Claude Code

## 项目概述

oh-my-claudecode 是一个面向 Claude Code 工作流的多智能体编排插件，核心定位不是“再造一个 IDE”，而是把多个模型、多个代理和一组可复用技能组织成一套团队执行系统。它主打 Claude 作为主控，同时可协同 Gemini、Codex 和 MCP 工具，把代码实现、架构分析、设计审查和文档整理拆给不同角色执行。

从当前仓库状态看，这个项目已经从早期的“插件化增强”演化为更完整的协作层。官网和仓库都强调 teams-first、多模型协同、运行时护栏和 stop enforcement，说明它的重心已经从“功能堆叠”转向“多人/多代理协作时如何稳定运行”。

## 基本信息

| 指标 | 数值 |
|------|------|
| Stars | 12,208 |
| Forks | 823 |
| 语言 | TypeScript 为主，辅以 JavaScript / Shell / Python |
| 今日增长 | 576 ⭐ |
| 开源协议 | MIT |
| 创建时间 | 2026-01-09 |
| 最近更新 | 2026-03-26 |
| GitHub | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |

## 技术分析

### 技术栈

- **核心语言**：TypeScript
- **运行形态**：Claude Code 插件 / 编排层
- **辅助能力**：Shell、Python 工具调用，MCP 集成
- **多模型接入**：Claude 为主，官网明确提到 Gemini 与 Codex 协同

### 架构设计

从项目公开介绍和发布说明看，oh-my-claudecode 的架构重点在“编排”而不是“推理模型本身”：

- **主控代理**：统一调度任务和上下文
- **专业子代理**：把分析、设计、审查等任务分发给不同角色
- **技能系统**：用成组技能和预定义工作流降低重复操作
- **MCP 工具层**：连接外部工具与上下文扩展
- **运行时护栏**：最近版本持续强化 runtime guardrails、默认模型集中管理和 stop-hook 安全策略

这类设计适合高频、多步骤、需要角色分工的代码协作场景。

### 核心功能

- 多模型协同编排
- 任务拆解与并行执行
- 技能与模板复用
- Claude Code 团队协作增强
- 运行时安全控制与中止保护

## 社区活跃度

### 贡献者分析

项目当前约有 64 位贡献者，说明它已经不是单人实验仓库，而是进入了有一定社区维护规模的阶段。以 2026 年 1 月创建、3 月就达到 12k+ Stars 的速度来看，增长曲线非常陡。

### Issue/PR 活跃度

当前公开 issue 数约 19，最新 release 为 `v4.9.1`（2026-03-24）。这说明项目迭代节奏快，且已经进入较频繁的小版本修补阶段，不再只是概念验证。

### 最近动态

- `v4.9.1` 发布，延续 4.x 快速迭代节奏
- 官网近期重点宣传 runtime guardrails、集中式模型默认值、stop enforcement 稳定性
- 作为 Claude Code 生态插件，近期在 agentic coding 圈层曝光度很高

## 发展趋势

### 版本演进

- **早期阶段**：以 Claude Code 增强和技能封装为主
- **中期阶段**：扩展到多代理协作与多模型接入
- **当前阶段**：开始强调运行时安全、团队执行一致性、任务中止与守护逻辑

### Roadmap

从当前方向看，后续很可能继续强化：

- 多模型路由与成本控制
- 团队模式下的上下文隔离
- 技能市场与共享
- 更强的 CI / release 校验

### 社区反馈

社区对它的兴趣主要来自两个点：

- 它贴近真实 coding workflow，而不是抽象聊天 demo
- 它把 Claude、Gemini、Codex 放在一个编排层里，适合“谁擅长什么就让谁做”的团队思路

## 竞品对比

| 项目 | Stars | 语言 | 特点 |
|------|-------|------|------|
| oh-my-claudecode | 12,208 | TypeScript | 面向 Claude Code 的 teams-first 多智能体编排插件 |
| bytedance/deer-flow | 47,902 | Python | 更完整的 Agent 运行时与沙箱执行框架 |
| agentscope-ai/agentscope | 20,172 | Python | 开发者中心的通用 Agent 编程框架 |

## 总结评价

### 优势

- 紧贴 Claude Code 实际使用场景
- 多模型与多角色编排概念清晰
- 版本迭代快，护栏与稳定性持续增强
- 团队协作导向明显，差异化强

### 劣势

- 生态高度依赖 Claude Code / MCP 场景
- 抽象层较高，理解和调试成本不低
- 若团队流程本身混乱，插件难以单独解决协作问题

### 适用场景

- 多人协作的 agentic coding 团队
- 需要把设计、审查、实现拆给不同代理的工作流
- 已经深度使用 Claude Code 的组织或个人

---
*报告生成时间: 2026-03-26 23:50:00*
*研究方法: GitHub API 多维度分析 + 官方网站/仓库信息交叉核对*
