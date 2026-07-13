# Yeachan-Heo/oh-my-codex 深度研究报告

## 项目概述

OmX（Oh My codeX）是一个面向 OpenAI Codex CLI 的工作流增强层，由韩国开发者 Yeachan Heo 创建并主导维护。项目于 2026 年 2 月 2 日在 GitHub 上公开，采用 MIT 许可证开源。

OmX 的核心设计理念是"保持 Codex 作为执行引擎，在此之上叠加结构化工作流和运行时辅助"。它不替代 Codex，而是通过引入规范化的技能（Skills）、多智能体团队协作（Team Runtime）和 HUD 监控界面，将 Codex 从一个单点执行工具扩展为一个可协作、可追踪、可编排的多智能体开发环境。

项目自创建以来维持极高的发布频率，从 2026 年 3 月 15 日至 4 月 4 日的 20 天内发布了超过 40 个版本（从 v0.8.0 到 v0.11.13），平均每天超过 2 个版本。截至报告日期，GitHub 标星数为 15877，Fork 数为 1497。

---

## 基本信息

| 属性 | 值 |
|------|-----|
| **GitHub 全称** | Yeachan-Heo/oh-my-codex |
| **别名称呼** | OMX、OmX |
| **GitHub 标星数** | 15877 |
| **GitHub Fork 数** | 1497 |
| **主语言** | TypeScript（91.7%）|
| **次要语言** | Rust（4.6%）、JavaScript（2.7%）|
| **许可证** | MIT |
| **创建日期** | 2026-02-02 |
| **最新版本** | v0.11.13 |
| **最新版本发布日期** | 2026-04-04 |
| **贡献者数量** | 33 |
| **总提交次数** | 1295 |
| **开放 Issue 数** | 20 |
| **已关闭 PR 数** | 767 |
| **发布版本数** | 77 |

### 技术环境要求

| 组件 | 最低版本 | 备注 |
|------|---------|------|
| Node.js | >= 20 | 全平台必需 |
| Codex CLI | 已认证 | 需提前安装 |
| tmux | 最新版 | macOS/Linux 可选但团队模式必需 |
| psmux | 最新版 | Windows 替代 tmux 的团队模式方案 |

---

## 技术分析

### 技术栈

OmX 采用 TypeScript（91.7%）为主语言，Rust（4.6%）为性能关键路径语言的双语架构：

| 语言 | 占比 | 用途 |
|------|------|------|
| TypeScript | 91.7% | CLI 主体、提示词管理、团队协调、工作流引擎 |
| Rust | 4.6% | 性能敏感组件（crates/omx-runtime-core 等） |
| JavaScript | 2.7% | 构建脚本、胶水代码 |

### 架构设计

OmX 的整体架构分为四个层次：

```
┌─────────────────────────────────────────────┐
│         Operator Surface（操作员界面）         │
│  omx setup / omx doctor / omx hud --watch    │
│  omx explore / omx sparkshell / omx team   │
├─────────────────────────────────────────────┤
│         Skill System（技能系统）             │
│  36 个技能目录 │ 33 个提示词模板 │ 关键词路由  │
├─────────────────────────────────────────────┤
│       Team Runtime（团队运行时）              │
│  tmux/pmsux 协调 │ 多智能体编排 │ 邮箱通知   │
├─────────────────────────────────────────────┤
│      Codex Integration（Codex 集成层）       │
│  MCP 协议 │ CLI 封装 │ 工作目录状态管理       │
└─────────────────────────────────────────────┘
```

### 核心技能（Skills）

OmX 提供了 36 个规范化技能：

**意图澄清类:** $deep-interview、$ralplan

**执行控制类:** $ralph、$autopilot、$team、$swarm

**质量保障类:** $ultraqa、$tdd、$code-review、$security-review、$visual-verdict、$build-fix

**信息检索类:** $explore、$deepsearch、$web-clone、$analyze

**运维管理类:** $hud、$doctor、$cancel、$note、$trace、$ecomode、$plan

**Provider 桥接类:** $ask-claude、$ask-gemini

### 多智能体团队协作（Team Runtime）

Team Runtime 是 OmX 最核心的差异化功能。

**团队启动命令:**
```bash
omx team <n>:executor "<task>"   # 启动 n 个执行者智能体
omx team status <team-name>       # 查看团队状态
omx team resume <team-name>        # 恢复暂停的团队
omx team shutdown <team-name>      # 关闭团队
```

**团队协作流程:**
```
team-plan → team-prd → team-exec → team-verify → team-fix（循环至终止状态）
```

**技术实现:**
- 使用 tmux（macOS/Linux）或 psmux（Windows）实现会话隔离
- 支持混合调度 Codex 和 Claude 工人
- 工作树编排（worktree orchestration）实现跨分支并行
- 邮箱通知机制实现智能体间通信
- 支持 Telegram/Discord 双向通知（v0.11.2+）

---

## 社区活跃度

### 贡献者构成

| 角色 | 用户名 | 说明 |
|------|--------|------|
| 创建者/主导开发者 | Yeachan-Heo（Bellman） | 所有提交均来自该账号 |
| 维护者 | HaD0Yun | 参与 v0.11.9 等版本贡献 |
| 大使 | Sigrid Jin | 社区推广 |
| 其他贡献者 | 29 人 | 活跃于 Issue 和 PR 社区 |

### 版本发布节奏

| 日期范围 | 发布版本范围 | 版本数量 | 平均每日版本数 |
|----------|------------|---------|--------------|
| 2026-03-15 至 2026-03-21 | v0.8.0 → v0.11.5 | ~20 个 | ~3 个/天 |
| 2026-03-22 至 2026-04-04 | v0.11.6 → v0.11.13 | ~8 个 | ~0.7 个/天 |

---

## 发展趋势

### 版本演进三条主线

**主线一：Team Runtime 成熟化**
- v0.5.0：引入 team runtime 基础架构
- v0.6.0：混合团队工人 CLI 路由（Codex + Claude）
- v0.8.0：team orchestrator brain 和 executor lane split
- v0.11.x 系列：密集修复 team delivery integrity 和 tmux boundary 问题

**主线二：Model Provider 扩展**
- v0.8.0：内置 ask-claude/ask-gemini 技能
- v0.8.2：Gemini CLI worker 支持

**主线三：Operator Surface 完善**
- v0.9.0：omx explore 和 omx sparkshell
- v0.10.1：引导式 autoresearch 设置

### 当前核心路线图（Issue #1243）

项目当前最重要的技术工作是"稳定化 team runtime / notify-hook / tmux 边界"：

1. 定义权威状态机（pending/delivered/notified/integrated/failed/stale）
2. 折叠或硬边界化状态来源
3. 将 Tmux 边界硬化为适配器
4. 分离产品测试和测试工具测试
5. 添加显式升级/迁移合约

---

## 竞品对比

### 核心竞品对比

| 属性 | **OmX (oh-my-codex)** | **Cursor** | **Windsurf (Codeium)** |
|------|----------------------|------------|----------------------|
| **GitHub 标星** | 15877 | 32600 | 未公开 |
| **GitHub Fork** | 1497 | 2200 | 未公开 |
| **创建时间** | 2026-02-02 | 2023-03-12 | 2023 年 |
| **开源方式** | 完全开源（MIT）| 闭源 + 部分开源 | 闭源 |
| **产品形态** | CLI 工具（Codex 外层）| AI 代码编辑器（IDE）| AI 代码编辑器（IDE）|
| **团队协作** | 原生支持（tmux 多智能体）| 不支持 | 不支持 |
| **多智能体** | 支持（36 个技能 + 团队运行时）| 不支持 | 不支持 |
| **最新版本** | v0.11.13（2026-04-04）| 未发布 Releases | 未发布 Releases |
| **发布频率** | 极高（每天 1-3 个版本）| 极低 | 极低 |
| **维护者** | Yeachan-Heo（单人主导）| cursor 团队 | codeium 团队 |

---

## 总结评价

### 核心优势

1. **多智能体团队协作能力:** 唯一将多智能体团队协作深度集成到 AI 编码工作流的开源工具
2. **极高的发布节奏与响应速度:** 20 天内发布 40+ 版本
3. **丰富的技能生态:** 36 个技能目录和 33 个提示词模板构成完整 AI 软件开发方法论库
4. **开源可定制:** MIT 许可证允许任意使用
5. **深度 MCP 集成:** 通过 @modelcontextprotocol/sdk 实现与 Codex 的标准化通信

### 主要劣势

1. **单人主导的开发模式:** 所有提交均来自 Yeachan-Heo 一人，存在单点故障风险
2. **依赖外部服务:** 完全依赖 OpenAI Codex CLI，无法独立工作
3. **Windows 平台支持不成熟:** 多个 Issue 涉及 Windows 特定问题
4. **高变化频率带来的不稳定性:** API 和行为可能在短期内发生重大变化

### 适用场景

**推荐使用:**
- 大型代码库重构（$team 技能提供多智能体并行方案）
- 多智能体研究（开源性质便于实验）
- Codex CLI 增强（现有用户可显著提升开发效率）
- 快速原型开发

**不推荐使用:**
- 新手开发者（陡峭学习曲线）
- 企业保守环境（高频变更不适合稳定性要求高的场景）
- Windows 优先团队

---

*报告生成时间: 2026-04-05*
*研究方法: github-deep-research 多轮深度研究*
