# Agent 互操作协议（MCP / A2A / AGENTS.md）

> 一页速览：2024-2026 年出现的三个 Agent 互操作"事实标准"协议
> 详细报告 → [MCP_A2A_Agents_md_标准化深度解析_20260621.md](../../reports/knowledge_reports/MCP_A2A_Agents_md_标准化深度解析_20260621.md)

---

## 三者一句话定义

| 协议 | 一句话 | 通信对象 | 类比 |
|------|--------|---------|------|
| **MCP** (Model Context Protocol) | 让 LLM 标准化访问工具/数据 | 模型 ↔ 工具/数据 | USB-C |
| **A2A** (Agent-to-Agent) | 让 Agent 跨厂商发现与协作 | Agent ↔ Agent | TCP/IP |
| **AGENTS.md** | 让 AI 编码 Agent 理解项目 | Agent ↔ 项目仓库 | README |

---

## 关键时间线

- **2024-11-25**：Anthropic 发布 MCP（首个稳定 spec 2024-11-05）
- **2025-03-26**：MCP spec 升级（Streamable HTTP 替代 SSE、OAuth 2.1、Elicitation）
- **2025-03-27**：Sam Altman 宣布 OpenAI 全面支持 MCP
- **2025-04-09**：Google Cloud Next 发布 A2A spec
- **2025-06-25**：Google 将 A2A 捐赠给 Linux 基金会
- **2025-08-19**：OpenAI + Google + Cursor + Sourcegraph + Anthropic + Amp + Factory 共同发布 AGENTS.md
- **2026-02**：Cloudflare 推出 Markdown for Agents（HTML→Markdown 自动转换）
- **2026-06**：AGENTS.md 被 60,000+ 开源项目采纳

---

## 三者核心差异（速查表）

| 维度 | MCP | A2A | AGENTS.md |
|------|-----|-----|-----------|
| 发起方 | Anthropic | Google（已捐 Linux 基金会） | OpenAI/Google/Cursor 联盟 |
| 传输 | JSON-RPC 2.0 + stdio/Streamable HTTP | JSON-RPC 2.0 + HTTP/SSE | 文件 IO（无协议） |
| 寻址 | Tool Schema (JSON) | Agent Card (`/.well-known/agent.json`) | repo-root Markdown |
| 安全 | Host 进程控制 + OAuth 2.1 | OpenAPI 兼容企业级 Auth | Repo 政策（用户自约束） |
| 状态 | Stateless + Client session | Task ID 全生命周期 | N/A（一次性读取） |
| 学习曲线 | 中 | 高 | 低 |
| 生态规模 | 1000+ MCP servers | 100+ 合作厂商 | 60,000+ 项目 |

---

## 关系与互补

三者**不竞争**而是**互补**：
- MCP 解决"AI 怎么操作外设"
- A2A 解决"AI 怎么找同伴协作"
- AGENTS.md 解决"AI 怎么理解工作环境"

**典型组合**：企业 SaaS 内部使用 MCP 连接遗留系统 → 多个 MCP-enabled Agent 通过 A2A 协作 → 各 Agent 在自己负责的代码仓库读 AGENTS.md 学习约定。

---

## 已知局限

**MCP**：
- 设计争议：JSON 配置文件解析、prompt injection 风险（OX Security 2025-04 报告 32K+ 仓库暴露）
- 2025-03-26 升级才正式加入 OAuth 2.1

**A2A**：
- `/.well-known/agent.json` 是约定非强制，需要额外发现机制
- 状态管理复杂：Task 持久化与 stateless 原则冲突

**AGENTS.md**：
- 隐性知识难表达（架构判断、不变量）
- 文件过长会挤占 LLM 上下文窗口
- 多数项目 6 个月后严重过期

---

## 关键人物与机构

- **Anthropic**（MCP 发起方）
- **Google Cloud**（A2A 发起方，2025-06 捐给 Linux 基金会）
- **Linux Foundation**（A2A 治理方）
- **OpenAI / Google / Cursor / Sourcegraph / Anthropic / Amp / Factory**（AGENTS.md 共同发起方）

---

## 关联概念

- [agent_systems.md](./agent_systems.md) — ReAct Loop · Function Calling · MCP 协议
- [test_time_compute.md](./test_time_compute.md) — Test-Time Scaling Laws
- [agent_orchestration.md](./agent_orchestration.md) — MIT 2026 三主线之一
- [agent_skill_ecosystem.md](./agent_skill_ecosystem.md) — Skills 与 AGENTS.md 同属元信息层

---

**数据采集**：2026-06-21
**最后更新**：2026-06-21
**报告路径**：`ai-learning/reports/knowledge_reports/MCP_A2A_Agents_md_标准化深度解析_20260621.md`
