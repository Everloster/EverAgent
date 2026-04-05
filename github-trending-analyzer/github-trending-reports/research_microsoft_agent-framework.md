# microsoft/agent-framework 深度研究报告

## 项目概述

Microsoft Agent Framework（简称 AF）是微软官方推出的用于构建、编排和部署 AI Agent 及多 Agent 工作流的开发框架，同时提供 Python 和 .NET/C# 两种语言实现。该项目由微软于 2025 年 4 月 28 日创建，经过约一年的高频开发，于 2026 年 4 月 2 日同步发布了 Python-1.0.0 和 .NET-1.0.0 两个稳定版本，标志着框架正式达成 GA（General Availability）里程碑。

作为一个多语言、多平台的 Agent 开发框架，Microsoft Agent Framework 的核心理念是通过图（Graph）结构连接 Agent 与确定性函数，构建数据流驱动的工作流。框架内置了流式处理（streaming）、检查点（checkpointing）、人在环中（human-in-the-loop）以及时间旅行（time-travel）等高级能力，支持与 Azure OpenAI、OpenAI、Microsoft Foundry、Anthropic、GitHub Copilot、Ollama 等多种 LLM 提供商集成。

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **仓库全名** | microsoft/agent-framework |
| **星标数（Stars）** | 8765 |
| **分叉数（Forks）** | 1442 |
| **开放 Issue 数** | 576 |
| **开放 PR 数** | 154 |
| **总提交数（Commits）** | 1834 |
| **贡献者数量** | 100 |
| **发布版本总数** | 69（含 Python 与 .NET 双平台）|
| **主语言** | Python（50.6%）+ C#（45.2%）+ TypeScript（3.7%）|
| **许可证** | MIT |
| **创建日期** | 2025-04-28 |
| **最新稳定版** | python-1.0.0 / dotnet-1.0.0（2026-04-02）|

**标签话题:** python, sdk, ai, dotnet, orchestration, multi-agent, workflows, agents, agent-framework, agentic-ai

---

## 技术分析

### 技术栈概览

**Python 技术栈（50.6% 代码量）：**

| 子包 | 功能定位 |
|------|---------|
| agent-framework-core | 框架核心抽象 |
| agent-framework-openai | OpenAI 提供商适配 |
| agent-framework-anthropic | Anthropic Claude 提供商适配 |
| agent-framework-azure-ai-search | Azure AI Search 集成 |
| agent-framework-azure-cosmos | Azure Cosmos DB 历史存储 |
| agent-framework-bedrock | AWS Bedrock 支持 |
| agent-framework-ollama | 本地 Ollama LLM 支持 |
| agent-framework-foundry | Microsoft Foundry 集成 |
| agent-framework-github_copilot | GitHub Copilot 集成 |
| agent-framework-a2a | Agent-to-Agent 通信协议 |
| agent-framework-ag-ui | AG-UI 协议支持 |
| agent-framework-mem0 | 记忆管理 |

**Python 子包总数：24 个**

### 架构设计

**（1）图式工作流编排（Graph-based Workflow Orchestration）**

框架以有向图作为 Agent 编排的核心抽象，通过数据流连接各个 Agent 和函数节点。工作流引擎内置以下关键能力：
- **流式处理（Streaming）:** 支持流式 token 输出
- **检查点（Checkpointing）:** 支持工作流状态持久化与恢复
- **人在环中（Human-in-the-loop）:** 允许人工干预 Agent 执行过程
- **时间旅行（Time-travel）:** 支持回溯到历史状态重新执行

**（2）多提供商适配器（Provider Adapters）**

通过统一的抽象接口连接不同的 LLM 提供商，目前官方支持：Azure OpenAI、OpenAI、Microsoft Foundry、Anthropic Claude、GitHub Copilot、AWS Bedrock、Ollama 等。

**（3）A2A 与 AG-UI 双协议支持**

- **A2A（Agent-to-Agent）协议:** 支持不同 Agent 之间的标准化通信
- **AG-UI 协议:** 支持 MCP（Model Context Protocol）工具调用的 AG-UI 事件发射

### 核心功能总结

1. **多语言 Agent 构建:** Python 与 .NET 双平台，API 高度一致
2. **图驱动编排引擎:** 支持复杂多 Agent 工作流、流式输出、检查点与恢复
3. **多 LLM 提供商集成:** 24 个 Python 包和 30 个 .NET 项目覆盖主流 LLM 服务
4. **标准化通信协议:** A2A（Agent 间）和 AG-UI（MCP 工具事件）双协议
5. **内置可观测性:** OpenTelemetry 原生集成
6. **多部署模式:** Azure Functions、Durable Task、本地容器等

---

## 社区活跃度

### 贡献者与提交活动

| 指标 | 数值 |
|------|------|
| 贡献者总数 | 100 |
| 总提交次数 | 1834 |
| 每周提交频率 | 高频（截至 2026-04-05 持续活跃）|

### 项目看板状态分布（截至 2026-04-03）

| 状态 | 数量 |
|------|------|
| Planned | 9 |
| In Progress | 18 |
| In Review | 17 |
| Done | 76 |
| Community PR | 1 |

---

## 发展趋势

### 版本演进路径

| 时间 | 里程碑 |
|------|--------|
| 2025-04-28 | 项目创建，启动双语言开发 |
| 2026-03-04 | Python RC3 / .NET RC3 — 新增 Shell 工具、Code Interpreter 增强 |
| 2026-03-30 | Python RC6 — 拆分为 agent-framework-openai 和新 agent-framework-foundry 包 |
| **2026-04-02** | **Python-1.0.0 + .NET-1.0.0 同步 GA** |

### 技术债务与清理

1.0.0 GA 前夕进行了大规模 API 清理：
- 移除 Python 侧废弃的 BaseContextProvider 和 BaseHistoryProvider 别名
- 移除 Message 构造函数的 text 参数
- Azure Foundry 更名为 Microsoft Foundry（统一品牌）

---

## 竞品对比

### 核心竞品对比表

| 维度 | **Microsoft Agent Framework** | **Microsoft AutoGen** | **LangChain** |
|------|------|------|------|
| **Stars** | 8765 | 56700 | 132000 |
| **Forks** | 1442 | 8500 | 21800 |
| **主语言** | Python + C#（双语言）| Python + .NET | Python（99.3%）|
| **创建时间** | 2025-04 | 2023-08 | 2022-10 |
| **最新版本** | 1.0.0（2026-04-02）| 未明确 GA | 1.2.26（2026-04-03）|
| **多 Agent 编排** | 图驱动工作流 | 多 Agent 对话协作 | LCEL 链式调用 |
| **协议支持** | A2A + AG-UI 双协议 | Agent 间消息传递 | LangChain Agents 协议 |
| **工作流持久化** | 检查点 + 时间旅行 + Durable Task | 会话状态管理 | 记忆 + 链状态 |
| **人在环中** | 原生支持 | 支持（Human Feedback）| 通过工具调用实现 |
| **可观测性** | OpenTelemetry 原生集成 | 有限 | 有限 |

---

## 总结评价

### 核心优势

1. **双语言一等公民支持:** Python 和 C# 在 API 层面保持一致，非事后桥接
2. **成熟的图驱动编排引擎:** 超越简单链式调用，支持检查点、流式处理、时间旅行等高级工作流能力
3. **标准化 Agent 通信:** A2A 和 AG-UI 双协议为多 Agent 系统提供了厂商无关的互操作标准
4. **企业级可观测性:** OpenTelemetry 原生集成，满足生产环境分布式追踪与监控需求
5. **丰富的提供商生态:** 24 个 Python 包和 30 个 .NET 项目覆盖主流 LLM 服务

### 现有劣势

1. **社区成熟度不足:** 8765 stars 远低于 LangChain（132k）和 AutoGen（56.7k）
2. **文档覆盖仍有缺口:** Issue 中有多个"找不到文档"的求助
3. **破坏性变更风险:** GA 后首个 RC（RC6）仍进行了包拆分和 API 清理
4. **.NET 侧部分功能滞后:** 某些 Python 侧特性在 .NET 侧迁移进度不一

### 适用场景

| 场景 | 适用度 |
|------|--------|
| 企业级多 Agent 工作流系统 | 非常适合 |
| .NET 技术栈下的 AI Agent 开发 | 首选 |
| Python + .NET 混合团队 | 非常适合 |
| Microsoft Foundry / Azure AI 深度用户 | 首选 |
| 快速原型 / 学术探索 | 一般 |
| 需要大量第三方插件生态 | 一般 |

---

*报告生成时间: 2026-04-05*
*研究方法: github-deep-research 多轮深度研究*
