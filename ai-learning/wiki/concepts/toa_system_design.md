---
name: "ToA 系统设计模式（EverAgent 实证）"
description: "从119次真实commit历史提炼的ToA产品设计模式：双入口文档、自包含Subagent、审计链、身份规范漂移等工程洞察"
type: concept
related: [toa_paradigm, agent_systems, bidirectional_domestication]
---

# ToA 系统设计模式（EverAgent 实证）

## 系统画像

EverAgent 是目前可观测的最小完备 ToA 系统：119 commits、8 种模型身份、跨 OpenAI/Anthropic/MiniMax/智谱四家厂商的真实多模型协作历史。

## 可复用的设计模式（⭐ = 工业适用性）

| 模式 | 实现 | 适用性 |
|------|------|:---:|
| **双入口文档** | README.md（人类）+ AGENTS.md（Agent） | ⭐⭐⭐⭐⭐ |
| **自包含 Subagent** | 各项目 AGENTS.md 完全独立，不依赖全局状态 | ⭐⭐⭐⭐⭐ |
| **审计链 commit 格式** | `[type] scope: desc` + Agent 身份标注 | ⭐⭐⭐⭐⭐ |
| **失败如实记录** | `interrupted by limit` commit 原样保留 | ⭐⭐⭐⭐⭐ |
| **知识蒸馏 Wiki 层** | wiki/entities + concepts + syntheses 三层 | ⭐⭐⭐⭐ |
| **CLI 原生工作流** | git + markdown + python scripts，无 GUI | ⭐⭐⭐⭐ |

## 暴露的未解问题

| 问题 | 现状 | 工业场景需要 |
|------|------|------------|
| Agent 身份验证 | 软约定，存在命名漂移（3 种 MiniMax 写法）| 中央化注册 + 硬验证 |
| 质量回顾 | 已完成列表只增不减，无质量抽查 | 定期采样 + 质量基线 |
| 协议遵守 | 依赖 Agent 自律，无越界操作强制 | 沙盒隔离 + 权限系统 |
| 并发锁 | .agent-lock 软锁，不进 git | 分布式锁服务 |

## 人类角色的自然演化（实证）

git history 时间轴显示：早期人类是主要提交者 → 中期 Agent 产出量超过人类 → 近期人类只做决策和质量判断。**这个演化不是被设计出来的，是从实际使用中自然涌现的。**

## 核心发现

系统最深刻的 Alignment 问题：AGENTS.md 中最关键的越界禁止规则没有技术强制，依赖 Agent 自律。这是整个 ToA 范式面临的微缩版 Alignment 困境。

## 关联报告

- 深度报告：`reports/knowledge_reports/EverAgent_ToA原型解剖_20260415.md`
- 理论框架：`toa_paradigm.md`、`bidirectional_domestication.md`
