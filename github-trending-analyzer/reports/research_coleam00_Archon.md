# coleam00/Archon

> The first open-source harness builder for AI coding. Make AI coding deterministic and repeatable——首款开源 AI 编程 harness 构建器，将 AI 编码过程定义为 YAML 工作流，使每次执行都具备确定性和可重复性

## 项目概述

Archon 是一款面向 AI 编程智能体的开源工作流引擎，于 2025 年 2 月正式发布，定位为 AI 编码过程的"基础设施层"。其核心主张是：当前 AI 编码智能体（如 Claude Code、Codex）的行为高度依赖模型心情，同一指令每次执行可能产生完全不同的序列——跳步、漏测、不写 PR 描述等。Archon 通过将开发流程编码为 YAML 工作流，为 AI 编程提供了结构化的确定性框架。

Archon 的设计哲学借鉴了三个历史先例：Dockerfile 之于基础设施、GitHub Actions 之于 CI/CD——Archon 则试图为 AI 编码工作流做同样的事。项目自称是"n8n，但面向软件开发"。截至 2026 年 4 月，项目已获得 14,262 颗 stars、2,444 个 forks、10 名贡献者，最新版本 v0.3.2 发布于 2026 年 4 月 8 日，呈现高度活跃的开发态势。

## 基本信息

| 字段 | 详情 |
|------|------|
| **项目名称** | Archon |
| **所有者** | coleam00 |
| **Stars** | 14,262 |
| **Forks** | 2,444 |
| **Open Issues** | 26 |
| **今日新增 Stars** | +18（参考近期日均增速） |
| **主要语言** | TypeScript（3,586,769 字节） |
| **协议** | MIT |
| **创建时间** | 2025-02-07 |
| **最近更新** | 2026-04-09 |
| **默认分支** | dev |
| **最新版本** | v0.3.2（2026-04-08） |
| **贡献者数** | 10 |
| **GitHub 链接** | https://github.com/coleam00/Archon |
| **官方文档** | https://archon.diy |
| **Topics** | ai, automation, bun, claude, cli, coding-assistant, developer-tools, typescript, workflow-engine, yaml |

**语言分布**：

| 语言 | 字节数 | 占比 |
|------|--------|------|
| TypeScript | 3,586,769 | 98.4% |
| Shell | 32,176 | 0.9% |
| PowerShell | 23,689 | 0.7% |
| JavaScript | 17,209 | 0.5% |
| Dockerfile | 8,324 | 0.2% |
| 其他 | 9,966 | 0.3% |

**主要版本发布历史**：

| 版本 | 发布日期 | 备注 |
|------|----------|------|
| v0.3.2 | 2026-04-08 | Archon CLI 最新稳定版 |
| v0.3.x | 2026-03~04 | 持续迭代，CLI 成熟化 |
| v0.2.x | 2026-01~02 | Web UI 与平台适配器扩展 |
| v0.1.x | 2025-09~12 | 早期测试版 |
| Beta | 2025-02 | 首个公开版本 |

## 技术分析

### 核心架构

Archon 采用模块化分层架构，核心分为四大层次：

```
┌──────────────────────────────────────────────────────────┐
│  平台适配层 Platform Adapters                              │
│  Web UI / CLI / Telegram / Slack / Discord / GitHub       │
└─────────────────────────────┬────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│  编排层 Orchestrator（消息路由与会话管理）                    │
│  AI Assistant Clients / Command Handler / Isolation        │
└─────────────┬──────────────────────────┬─────────────────┘
              │                          │
      ┌───────┴────────┐          ┌───────┴────────┐
      │ Command System  │          │  Workflow      │
      │ (Markdown 命令) │          │  Executor(YAML)│
      └────────────────┘          └────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────┐
│  数据层：SQLite / PostgreSQL（7 张核心表）                  │
│  Codebases / Conversations / Sessions / Workflow Runs     │
│  Isolation Environments / Messages / Workflow Events      │
└──────────────────────────────────────────────────────────┘
```

**平台适配器**（Platform Adapters）：通过 `IPlatformAdapter` 接口接入不同消息平台（Web UI、CLI、Slack、Telegram、Discord、GitHub），实现跨平台统一编排。

**编排器**（Orchestrator）：消息路由中枢，管理会话持久化，通过流式传输（AsyncGenerator）实时推送 AI 响应。

**AI 客户端**（AI Assistant Clients）：封装 Claude Code SDK 和 Codex SDK 为统一接口，支持多模型切换。

**隔离提供者**（Isolation Providers）：通过 git worktree 为每次工作流运行创建隔离环境，确保并行任务互不干扰。

**命令系统**（Command System）：基于 Markdown 的文件化命令，存储在 `.archon/commands/`，通过 git 版本化管理。

### 工作流节点类型

Archon 工作流以 YAML 定义，支持 6 种互斥节点类型：

| 节点类型 | 说明 | AI 参与 |
|----------|------|----------|
| `command` | 从 `.archon/commands/` 加载命令文件 | 可选 |
| `prompt` | 内联 AI 提示字符串 | 必选 |
| `bash` | Shell 脚本执行（stdout 捕获为 `$nodeId.output`） | 无 |
| `loop` | AI 循环迭代直到完成信号（`until: COMPLETE`） | 必选 |
| `approval` | 暂停等待人工审批（`interactive: true`） | 必选 |
| `cancel` | 以指定原因终止工作流 | 无 |

**条件执行**：通过 `when:` 字段实现 DAG 条件分支，支持字符串（`==`、`!=`）和数值（`>`、`>=`、`<`、`<=`）比较，以及 `&&`、`||` 复合条件。

**触发规则**（trigger_rule）：

- `all_success`（默认）：所有依赖节点必须成功
- `one_success`：至少一个依赖成功
- `none_failed_min_one_success`：无失败且至少一个成功
- `all_done`：所有依赖到达终态

**重试配置**：

```yaml
retry:
  max_attempts: 3    # 1-5，默认2
  delay_ms: 5000     # 1000-60000，默认3000
  on_error: transient
```

**模型与工具限制**：

```yaml
allowed_tools: [Read, Grep, Glob]   # 白名单
denied_tools: [WebSearch]           # 黑名单
output_format:                      # 强制结构化JSON
  type: object
  properties:
    type:
      type: string
      enum: [BUG, FEATURE]
```

### 默认工作流库

Archon 打包了 17 个开箱即用的默认工作流，覆盖常见开发场景：

| 工作流 | 功能 |
|--------|------|
| `archon-assist` | 通用问答与调试 |
| `archon-fix-github-issue` | Issue → 调查 → 计划 → 实现 → PR |
| `archon-idea-to-pr` | 想法 → 计划 → 实现 → 验证 → PR → 5 并行审查 |
| `archon-plan-to-pr` | 执行已有计划 → PR |
| `archon-smart-pr-review` | 智能 PR 复杂度分类 → 定向审查 |
| `archon-comprehensive-pr-review` | 多审查智能体并行（5 个） |
| `archon-architect` | 架构扫描与健康改进 |
| `archon-refactor-safely` | 安全重构（含类型检查钩子） |
| `archon-resolve-conflicts` | 合并冲突自动检测与解决 |
| `archon-create-issue` | 问题分类 → 上下文收集 → 创建 Issue |

### 数据持久化

Archon 使用 SQLite（默认）或 PostgreSQL 存储 7 张核心表：`remote_agent_codebases`、`remote_agent_conversations`、`remote_agent_sessions`、`remote_agent_isolation_environments`、`remote_agent_workflow_runs`、`remote_agent_workflow_events`、`remote_agent_messages`。会话数据持久化意味着 AI 会话可在进程重启后恢复。

### 安装与部署

| 方式 | 命令 |
|------|------|
| Linux/Mac 一键 | `curl -fsSL https://archon.diy/install \| bash` |
| Windows | `irm https://archon.diy/install.ps1 \| iex` |
| Homebrew | `brew install coleam00/archon/archon` |
| Docker | `docker run --rm -v "$PWD:/workspace" ghcr.io/coleam00/archon:latest workflow list` |
| 源码 | `git clone && bun install` |

运行时依赖：Bun、Claude Code（或 Codex）、GitHub CLI。

## 社区活跃度

### 贡献者结构

项目拥有 10 名贡献者，贡献集中度较高：

| 贡献者 | 贡献次数 | 角色 |
|--------|----------|------|
| Wirasm | 730 | 核心维护者 |
| coleam00 | 324 | 创始人/所有者 |
| leex279 | 32 | 外部贡献者 |
| 其他 7 名 | 各 1~4 次 | 边缘贡献者 |

Wirasm 以 730 次贡献成为实际上的核心维护者，体现了开放协作模式。GitHub Actions Bot 和 Copilot 也有少量自动贡献。

### Issue 与 PR 状态

截至研究时点（2026-04-10），Open Issues 共 26 个，处于正常维护状态。PR 活跃度较高，最新提交为 2026-04-09 的 PowerShell 路径修复（#1000）和 setup.md 文档修复（#1013）。

### 版本迭代节奏

从 v0.3.2（2026-04-08）来看，项目保持每周多次小版本迭代，开发分支（dev）活跃。当前处于 0.x 阶段，API 尚未完全稳定。

### 生态扩展

Archon 的生态覆盖多个关联项目：

- `coleam00/ottomator-agents`：开放 AI 智能体集合，托管于 oTTomator Live Agent Studio 平台
- `coleam00/Archon` 自身的多分支结构包含 `archon-example-workflow`、`archon-ui-main`、`python/` 等子模块

## 发展趋势

### 核心定位演进

Archon 经历了从"AI 知识与任务管理骨干"（Beta v1）到"AI 编程 harness 构建器"（v0.3.x）的定位转变。早期版本（`archive/v1-task-management-rag` 分支）保留了对标 Browser-use/GitLab 的任务管理+RAG 方向；当前版本聚焦于 YAML 工作流引擎，解决了 AI 编码一致性问题这一更精准的痛点。

### 技术方向

1. **多智能体并行审查**：`archon-comprehensive-pr-review` 工作流展示了 5 个并行审查智能体的设计，通过 DAG 并行节点实现"鱼群效应"式多视角代码审查。
2. **Harness Pattern 确立**：将 AI 编码过程结构化为"计划-实现-验证-审查-PR"的确定性管道，是当前技术方向的核心。
3. **平台无关性**：通过 `IPlatformAdapter` 接口同时支持 Web UI、CLI、Slack、Telegram、Discord 等多平台，统一消息入口。
4. **隔离执行**：git worktree 隔离确保并行工作流不会污染主仓库，这是其相对于直接在主仓库运行 AI 编码的关键安全优势。

### 市场需求背景

AI 编码工具正在经历从"单次对话"到"结构化工作流"的范式转变。Claude Code（SWT-bench 80.8%）、Cursor、Windsurf 等工具在单次任务上表现优异，但在复杂多步骤任务上缺乏一致性保证。Archon 填补了这一空白，其"harness builder"定位恰好契合企业级 AI 编程治理需求。

## 竞品对比

| 维度 | **Archon** | **Cline（VS Code 插件）** | **Claude Code（CLI）** | **LangGraph** | **n8n** |
|------|-----------|--------------------------|------------------------|---------------|---------|
| **定位** | AI 编程 harness 构建器 | AI 编程助手（IDE 插件） | 单次 AI 编码 CLI | AI 工作流编排框架 | 通用工作流自动化 |
| **核心抽象** | YAML 工作流 + Markdown 命令 | 自然语言对话 | 自然语言对话 | Python DAG 图 | 可视化节点流 |
| **确定性强弱** | 高（YAML 强制结构） | 低（依赖模型） | 低 | 中（Python 代码可控） | 高（节点可配置） |
| **隔离执行** | ✅ git worktree | ❌ 直接修改 | ❌ | ❌ | ❌ |
| **多平台** | ✅ 6 个平台 | ❌ 仅 VS Code | ❌ 仅 CLI | ❌ 仅代码 | ✅ 500 个集成 |
| **上手门槛** | 中（需学 YAML DSL） | 低（对话即可） | 低 | 高（需写 Python） | 中（可视化或 YAML） |
| **开源** | ✅ MIT | ✅ AGPL | ❌ 闭源 | ✅ MIT | ✅ Apache 2.0 |
| **Stars** | 14,262 | 60,078 | N/A（闭源） | 28,801 | 183,255 |
| **循环节点** | ✅ `loop:` | ❌ | ❌ | ✅ | ✅ |
| **人工审批门** | ✅ `approval:` | ❌ | ❌ | 需自定义 | 需自定义 |

**Archon 的差异化优势**：

1. **隔离性**：唯一提供 git worktree 级别隔离的 AI 编程工具，并行运行零冲突
2. **YAML 确定性**：用 YAML 替代自然语言描述流程，使 AI 行为从"概率性"变为"确定性"
3. **平台聚合**：唯一同时聚合 Web/CLI/Slack/Telegram/Discord/GitHub 的 AI 编程入口
4. **审批门设计**：`approval` 节点使人类可以介入 AI 工作流的任意阶段

## 总结评价

Archon 是当前 AI 编程工具链中一个独特的存在——它不是又一个 AI 编码助手，而是一个**结构化治理框架**。其核心价值主张"Make AI coding deterministic and repeatable"精准命中了企业在生产环境中使用 AI 编码的最大痛点：不可预测性。

从技术实现看，Archon 的分层架构（平台适配 → 编排 → AI 客户端 → 隔离执行 → 数据持久化）设计合理，模块间通过接口解耦，具备良好的可扩展性。YAML 工作流 DSL 简洁但表达能力足够（6 种节点类型 + 条件分支 + 循环 + 重试 + 工具限制），覆盖了从简单单步任务到复杂多阶段 PR 管道的全场景。

活跃度方面，14,262 stars 的体量在 AI 编程工具中属中大型项目，保持每日更新的开发节奏，v0.3.2 版本刚发布（2026-04-08），生态处于快速成长期。Wirasm 作为核心维护者的贡献占比（730 vs 324）显示项目依赖少数活跃个人，需关注长期维护风险。

**适合场景**：企业开发团队希望在多个项目中标准化 AI 辅助开发流程；需要并行运行多个 AI 编程任务且要求隔离不冲突；希望在 AI 工作流中嵌入人工审批门以满足合规或代码审查要求。

**不适用场景**：个人简单快速编码任务（Cline/Claude Code 更轻量）；需要复杂状态机或外部服务集成的场景（LangGraph/n8n 更成熟）；对开源许可证有顾虑的场景（Archon 为 MIT，限制较少）。

**一句话总结**：Archon 将 GitHub Actions 的 CI/CD 理念引入 AI 编码领域，是目前最接近"AI 编程 DevOps"定位的开源工具。

---

*报告生成时间: 2026-04-10*
*研究方法: github-deep-research 多轮深度研究*
