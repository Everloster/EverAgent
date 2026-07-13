# EverMind-AI/EverOS 深度研究报告

## 项目概述

EverOS 是 EverMind AI 开源的 **自演化智能体长期记忆操作系统**，定位为"智能体领域的第一个专门为自演化设计的记忆层"。项目于 2025 年 10 月 28 日创建，2026 年 4 月 14 日完成品牌升级并正式公测。

**核心价值主张**：将无状态 LLM 转变为具备持续学习能力的智能体——每次对话不再从零开始，而是从历史经验中积累结构化知识，并自动蒸馏出可复用的技能（Standard Operating Procedures）。

**三句话定性**：
- 学术背景扎实：EverCore、HyperMem、EverMemBench 均有 arXiv 论文支撑，HyperMem 被 ACL 2026 收录。
- 性能基准领先：LoCoMo 93.05%、LongMemEval-S 83.00%，超越 Mem0、Zep、Letta 等主流竞品。
- 生态整合广泛：已整合 MCP、OpenClaw、TEN Framework、Claude Code 等主流 Agent 框架，应用场景覆盖游戏、可穿戴、多 Agent 编排等 8+ 领域。

---

## 基本信息

| 字段 | 数值 |
|------|------|
| 仓库名称 | EverMind-AI/EverOS |
| 主页 | https://github.com/EverMind-AI/EverOS |
| 官网 | https://evermind.ai |
| Stars | 3926 |
| Forks | 406 |
| Open Issues | 81 |
| 主语言 | Python（代码量 6,611,955 字节，占比约 99%） |
| 其他语言 | JavaScript（45,484 字节）、Shell（8,740 字节）、Makefile、Dockerfile |
| 许可证 | Apache-2.0 |
| 创建时间 | 2025-10-28 |
| 最后更新 | 2026-04-15（昨日仍有推送） |
| 贡献者数量 | 13 人 |
| Topics | agent-memory, agentic-ai, llm, long-term-memory, mcp, memory, rag, skills |

**Top 贡献者（按提交数）**：

| 用户 | 提交数 |
|------|--------|
| daoxize1 | 112 |
| gloryfromca | 83 |
| ZuyiZhou | 79 |
| cyfyifanchen | 52 |
| chuanruihu | 29 |
| troyhua | 16 |
| shallyan | 9 |

---

## 技术分析

### 3.1 仓库结构

```
EverOS/
├── methods/
│   ├── EverCore/        # 自组织记忆操作系统（核心引擎）
│   └── HyperMem/        # 超图记忆架构
├── benchmarks/
│   ├── EverMemBench/    # 记忆质量评测
│   └── EvoAgentBench/   # 智能体自演化评测
└── usecases/            # 示例应用（8+ 场景）
```

### 3.2 四层架构

EverOS 采用四层解耦架构：

1. **Agentic Layer（智能体层）**：任务理解与执行，对接 OpenClaw、Hermes 等 Agent 框架
2. **Memory Layer（记忆层）**：长期记忆存取，基于"Engram 生命周期"模型（仿生记忆印迹原理）
3. **Index Layer（索引层）**：向量嵌入 + 知识图谱双索引
4. **API/MCP Interface Layer（接口层）**：标准 REST API + MCP 协议，对接企业系统

### 3.3 核心技术模块

**EverCore（EverMemOS）**

仿照生物记忆印迹（Engram）原理构建的自组织记忆 OS。记忆不是平铺存储，而是经历 提取→结构化→演化 三个阶段的生命周期管理，防止垃圾记忆堆积导致的性能退化。论文：arXiv:2601.02163。

**HyperMem**

基于超图（Hypergraph）的分层记忆架构，ACL 2026 收录。核心思想：一条超边可连接多个节点，精准捕获现实世界的高阶关联关系。分为 topic、event、fact 三层，支持粗到细的长期对话检索。LoCoMo 92.73%，超低延迟。论文：arXiv:2604.08256。

**Skills Evolution Engine（技能演化引擎）**

将原始任务经验自动蒸馏为可复用技能 SOP 的三阶段流水线：

- Agent Case Extraction：从完成的任务中提取意图、方法、关键洞察和质量评分
- Semantic Clustering：基于向量语义聚类，合并相似案例
- Agent Skill Emergence：从聚类经验中蒸馏技能；成功路径强化步骤，失败路径添加"陷阱警告"

实测效果：软件工程任务成功率提升 234.8%（27B 模型，GDPVAL 基准）。

**mRAG 混合检索**

融合密集语义向量 + 稀疏关键词匹配 + 多模态对齐，原生支持 PDF、图片、文档、表格、URL 等格式，实现精准的跨模态记忆检索。

### 3.4 基础设施依赖

Docker Compose 部署，依赖组件：MongoDB（结构化存储）、Elasticsearch（全文检索）、Milvus（向量检索）、Redis（缓存），以及 uv 包管理器，支持 GitHub Codespaces（4 核起）。

### 3.5 MCP 集成

仓库 Topics 明确包含 `mcp`，已有第三方实现 `evermemos-mcp`（将 EverOS 接入 AI 编程助手），官方也发布了 Claude Code 插件（`EverMind-AI/evermem-claude-code`）。

---

## 社区活跃度

**量化指标（2026-04-15 实测）**：

| 指标 | 数值 |
|------|------|
| Stars | 3926 |
| Forks | 406 |
| Open Issues / PRs | 81 |
| 贡献者 | 13 人 |
| 最近推送 | 2026-04-15T00:20:38Z（当日有更新） |
| 仓库年龄 | 约 5.5 个月 |

**社区渠道**：
- Discord（在线用户动态徽章，活跃社区）
- WeChat 群（Issue #67）
- X（@evermind）
- 官方维护者：@elliotchen200（X）、@cyfyifanchen（GitHub）

**近期重大事件（2026 年 4 月）**：

- **2026-04-14**：品牌升级 + EverOS 全球公测正式启动（PR Newswire 发布）
- **2026-04-14**：Memory Genesis Competition 发布，奖励池 $80,000（商业积分配额 + 技术支持）
- **2026-04**：HyperMem 被 ACL 2026 收录
- **2026-04**：EvoSkills 论文（arXiv:2604.01687）发布

**Issue 活跃度**：81 个 open issues/PRs，最新 PR（#174）为 README 文档更新，维护者响应迅速。

**生态整合吸引力**：TEN Framework、OpenClaw、Hermes、Claude Code 等主流 Agent 框架均已或正在接入 EverOS，体现出较强的生态号召力。

---

## 发展趋势

### 5.1 成长轨迹

- 2025-10-28 建仓，5.5 个月内积累 3926 Stars，增长曲线陡峭
- 2026-04-14 公测，标志从研究项目转向商业产品
- 代码库以 Python 为核心（6.6M 字节），JS 为辅，体现后端优先策略

### 5.2 技术演进方向

根据 README 注释中已折叠的部分内容（Key Results 表格被注释隐藏），以及近期 PR 和 Issue 内容，推断以下为主要演进方向：

- **EverOS Cloud**（everos.evermind.ai）：SaaS 化，开发者无需自部署
- **Memory Sparse Attention（MSA）**：突破 LLM 100M Token 上下文限制的端到端长期记忆架构（已有 Blog 文章和 GitHub 仓库 EverMind-AI/MSA）
- **EvoAgentBench 纵向评测**：将静态快照评测扩展为纵向成长曲线评测，衡量技能转移效率、错误规避率
- **EverMemBench-Dynamic**：HuggingFace 数据集持续更新

### 5.3 商业化路径

开源（Apache-2.0）+ Cloud SaaS 双轨，与 Mem0、Letta 策略类似。Memory Genesis Competition 是开发者获客工具。

### 5.4 风险与不确定性

- 无正式 Release 版本（GitHub Releases 列表为空），版本管理依赖主分支推送，稳定性待观察
- 重度依赖 5 个基础设施服务（MongoDB、Elasticsearch、Milvus、Redis + LLM API），自托管门槛较高
- 13 名贡献者中头部集中（前 3 人贡献量占 65%+），バス风险存在

---

## 竞品对比

### 6.1 基准性能对比（数据来源：EverMind 官方 Blog + 独立第三方测试 vectorize.io）

| 对比项 | LoCoMo | LongMemEval-S | 开源协议 | 自托管难度 |
|--------|--------|---------------|----------|-----------|
| EverOS | 93.05% | 83.00% | Apache-2.0 | 简单（Docker） |
| Zep | 80.32% | 63.8% | 社区版已弃用 | 复杂（Graphiti+DB） |
| Mem0 | 未公布 | 49.0% | 部分开源 | 支持 |
| Letta | 未公布 | 未公布 | Apache-2.0 | 支持 |
| Cognee | 未公布 | 未公布 | 开源 | 支持 |

### 6.2 架构特性对比

| 对比项 | EverOS | Mem0 | Zep | Letta |
|--------|--------|------|-----|-------|
| 记忆模型 | Engram 生命周期 | 混合（向量+图） | 时序知识图谱 | OS 分层 |
| 图记忆 | 原生（超图） | 仅 Pro 版 | 原生 | 原生 |
| 时序推理 | 支持 | 不支持 | 最强 | 通过 Agent 逻辑实现 |
| 技能演化 | 独有（SOP 蒸馏） | 无 | 无 | 无 |
| 多模态检索 | 原生 mRAG | 无 | 无 | 无 |
| MCP 集成 | 官方支持 | 第三方 | 第三方 | 第三方 |

### 6.3 定价对比

| 对比项 | EverOS | Mem0 | Zep | Letta | Cognee |
|--------|--------|------|-----|-------|--------|
| 自托管 | 免费（Apache-2.0） | 免费（有限） | 社区版已弃用 | 免费 | 免费 |
| 云服务起价 | 公测免费 | $19/月 | $25/月 | $20/月 | $200/月 |

### 6.4 核心差异化

EverOS 与竞品最本质的差异在于**技能演化引擎**：其他系统均聚焦于记忆存储与检索，EverOS 更进一步，将记忆转化为可复用的行为规范（SOP），实现智能体的持续自我改进——这是目前公开的记忆系统中独有的能力。

---

## 总结评价

### 7.1 综合评价

EverOS 在 2026 年 4 月的公测发布，代表了 Agent 记忆领域的一次质的跃升：从"会记忆"到"会学习"的范式转变。其学术支撑（3 篇 arXiv 论文，1 篇 ACL 2026）、基准成绩（LoCoMo 93.05% SOTA）和生态整合广度（Claude Code、TEN Framework、OpenClaw）三者协同，构成了较强的综合竞争力。

### 7.2 优势

- **性能领先**：LoCoMo 93.05% 和 LongMemEval-S 83.00% 均为公开测试中最高分
- **技术独特性**：技能演化引擎（Skills Evolution Engine）是目前记忆系统中独有的自改进机制
- **生态广度**：8+ 已验证的应用场景，覆盖 iOS 伴侣、可穿戴、游戏、多 Agent 编排、Claude Code 等
- **学术可信度**：EverCore、HyperMem、EverMemBench 均有同行评审论文支撑

### 7.3 风险

- **成熟度不足**：无正式 Release 版本，核心功能仍在快速迭代
- **部署门槛**：生产级自托管需维护 5 个基础设施服务
- **核心贡献集中**：前 3 位贡献者承担 65% 以上工作量，社区驱动度待提升
- **商业化路径尚早**：Cloud SaaS 仍在公测，定价未公布

### 7.4 适用场景

- **高度适合**：需要长期用户记忆的 Agent（客服、个人助理、AI 伴侣）；需要自动积累技能的代码 Agent；研究 Agent 记忆的学术团队
- **谨慎评估**：生产环境稳定性要求极高的企业场景（建议等待正式 v1.0 Release）

### 7.5 GitHub Trending 关注度评估

- **上榜潜力：高**。公测发布（2026-04-14）与 ACL 2026 论文收录形成双重曝光，预计近期 Star 增速将显著加快
- **长期价值：高**。Agent 记忆赛道是 2026 年 AI 工程化的核心基础设施方向，EverOS 技术路线清晰、论文支撑充足

---

*报告生成时间: 2026-04-15*
*研究方法: github-deep-research 多轮深度研究*
