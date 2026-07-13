---
title: "Yeachan-Heo/oh-my-claudecode"
domain: "github-trending-analyzer"
report_type: "repo_deep_research"
status: "cached"
updated_on: "2026-03-27"
---

# Yeachan-Heo/oh-my-claudecode

> Teams-first Multi-agent orchestration for Claude Code

## 项目概述

oh-my-claudecode（简称 OMC）是一个面向 Claude Code 的多智能体团队协作框架。与传统的单用户 Claude Code 不同，OMC 解决了“多人协作”的问题，包括多个子任务并行执行、团队角色分工、代码审查和规划。项目自称是 Claude Code 的团队协作增强方案，并以“史上最强 copilot”定位自己，支持并行执行和多角色分工。2026 年 1 月上线，v4.9.1，12,359 Stars，是 Claude Code 生态中增长最快的团队协作工具。

## 基本信息

| 指标 | 数值 |
|------|------|
| Stars | 12,359 |
| Forks | 828 |
| Open Issues | 19 |
| 语言 | TypeScript (50.6%), JavaScript (37%), Shell, Python, Dockerfile |
| 开源协议 | MIT |
| 创建时间 | 2026-01-09 |
| 最近更新 | 2026-03-26 |
| 贡献者 | 64 人 |
| 最新版本 | v4.9.1 (2026-03-24) |
| GitHub | [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) |

## 技术分析

### 技术栈

- **TypeScript 主导**：核心框架采用 TypeScript，提供类型安全和 IDE 支持
- **多智能体编排**：支持并行执行、多角色分工（规划者、执行者、审查者）
- **Claude Code 深度集成**：利用 Claude Code 的 agentic-coding 能力扩展团队协作
- **容器化支持**：Dockerfile 支持一键部署

### 核心功能

- **Team-first orchestration**：多人协作框架，多个子任务并行执行
- **tri-model routing**：自动路由到最适合的模型（Claude/Codex/Gemini）
- **runtime hardening**：增强 stop-hook、worker 状态管理、tmux pane 感知
- **并行执行**：多个智能体同时工作，提高效率
- **代码审查**：自动代码审查和规划功能

## 社区活跃度

### 贡献者分析

64 位贡献者，社区参与度极高，说明该项目已经吸引了大量开发者的关注和维护热情。版本发布活跃（v4.9.1），体现了项目的快速迭代能力。

### Issue/PR 活跃度

| 指标 | 数值 |
|------|------|
| Open Issues | 19 |
| 贡献者 | 64 人 |
| 版本发布 | v4.9.1 (2026-03-24) |

### 技术标签

`agentic-coding`, `claude-code`, `parallel-execution`, `multi-agent-systems`, `vibe-coding`

## 发展趋势

### 版本演进

从 2026-01 月上线，v4.9.1 已迭代 4+ 个大版本，核心方向：单人工具 → 团队协作 → 企业级功能。

### 社区反馈

社区反馈积极：GitHub Trending 观察显示该项目增长迅速，是当前最活跃的 `agentic coding runtime` 项目之一。技术社区评价其"为 Claude Code 生态带来了真正的团队协作能力"。

## 竞品对比

| 项目 | Stars | 定位 | 特点 |
|------|-------|------|------|
| **oh-my-claudecode** | 12,359 | 团队协作框架 | 多智能体 + 并行执行 + 代码审查 |
| **DeerFlow** | 48,091 | 长时任务 Agent | 完整 Agent 框架，沙箱+记忆 |
| **Claude Code** | — | 单人开发工具 | 官方 CLI，生态基础 |
| **Cursor** | — | AI IDE | 集成开发环境，内置 AI |

## 总结评价

### 优势

- 真正的团队协作能力，多个子任务并行执行
- 自动模型路由，优化成本和效率
- Claude Code 生态深度集成
- 活跃的社区和快速迭代

### 劣势

- 依赖 Claude Code，生态锁定
- 企业级功能（如权限管理）仍在发展中
- 文档相对较少

### 适用场景

- 软件开发团队的 AI 辅助协作
- 大型项目的多模块并行开发
- 代码审查和重构任务
- 企业级 AI 开发工作流

---
*报告生成时间: 2026-03-27*
*研究方法: GitHub API 多维度分析*
