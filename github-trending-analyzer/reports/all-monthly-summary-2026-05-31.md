---
title: "GitHub Trending 月榜报告 — 2026 年 5 月"
domain: "github-trending-analyzer"
report_type: "monthly_summary"
status: "completed"
updated_on: "2026-06-21"
---

# GitHub Trending 月榜报告 — 2026 年 5 月

> 生成时间: 2026-06-21
> 数据源: `trending_fetcher.py` 在 2026-05 月期间**未运行**（自动化空白期），本月报基于以下证据合成：
>   1. 已落盘的 `research_*.md` 深度研究文件（生成时间集中在 2026-04 下旬 ~ 2026-05）
>   2. `all-daily-summary-2026-04-05.md`（4 月初最近一次完整日榜）
>   3. Q1 月报（2026-03-17 / 2026-03-18）作为对照基线
>   4. WebSearch 抽样验证（少量 star 数字与项目活跃度交叉核验）
> **置信度**：低-中（不是完整 monthly snapshot，是基于代理证据的合成）。**强烈建议** TrendAgent 后续补一次 5 月 trending 回填抓取或承认 5 月数据缺失。

---

## 概览

| 统计项 | 数值 | 备注 |
|--------|------|------|
| 已落盘 research 文件数 | 74+ | 涵盖 2026-03 ~ 2026-05 期间 trending 仓库 |
| 估计分析项目数 | 25-30 | 基于 research 文件 + WebSearch 抽样 |
| 总 Stars（聚合估算） | 1,200,000+ | 跨 25-30 项目聚合 |
| 主要语言 | TypeScript, Python, Rust, Go | 与 Q1 主导语言一致 |
| 主导领域 | AI Agent Skills / 编码 Agent / 容器 / 安全 | 较 Q1 进一步集中 |

### 语言分布（基于 research 文件聚类）

| 语言 | 项目数（估） | 占比 |
|------|-------------|------|
| TypeScript | 10-12 | 38% |
| Python | 7-9 | 30% |
| Rust | 3-4 | 13% |
| Go | 2-3 | 10% |
| C++ | 1-2 | 5% |
| 其他（Swift/Java/Solidity） | 1-2 | 4% |

### 热门领域（与 Q1 对比）

| 领域 | 5月项目占比 | Q1 占比 | 变化 |
|------|-----------|--------|------|
| AI Agent 框架 | 35% | 35% | → 持平 |
| AI Agent Skills 生态 | 22% | 8% | ↑↑ 显著增长（`everything-claude-code`, `claude-skills`, `learn-claude-code`, `pm-skills`, `taste-skill` 集中爆发） |
| 编码 Agent / IDE | 12% | 10% | ↑ 微增（`deer-flow`, `Archon`, `page-agent`） |
| 容器 / 基础设施 | 8% | 7% | → 持平 |
| 数据库 / 向量库 | 8% | 13% | ↓ 略降（`SpacetimeDB`, `zvec` 持续但新项目减少） |
| 安全 / 红队 | 5% | 5% | → 持平 |
| 浏览器自动化 | 5% | 5% | → 持平（`browser-use` 持续） |
| 其他（OCR / 评测 / 文档） | 5% | 17% | ↓ 显著下降 |

**主要观察**：5 月 GitHub 生态**显著向 Agent Skills 化倾斜**——Claude Code 生态（`everything-claude-code`, `claude-skills`, `huggingface/skills`）在 4 月底发布后于 5 月持续爆火，标志着"Agent 工具调用 → 技能复用"的范式转变。

## 项目列表（5 月代表性 trending，按研究文件 + WebSearch 抽样）

| 排名 | 项目 | 语言 | Stars（估） | 5 月新增（估） | 简评 |
|------|------|------|------------|--------------|------|
| 1 | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | Shell | 157,000+ | ~80,000 | Claude Code 全套配置（skills + agents + hooks） |
| 2 | [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | TypeScript | 35,000+ | ~28,000 | Claude Code 教学项目 |
| 3 | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | Python | 65,000+ | ~32,000 | Long-horizon SuperAgent 框架 |
| 4 | [coleam00/Archon](https://github.com/coleam00/Archon) | TypeScript | 8,000+ | ~4,000 | "First open-source harness builder" |
| 5 | [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) | Python | 12,000+ | ~8,000 | Claude Skills 集合 |
| 6 | [browser-use/browser-use](https://github.com/browser-use/browser-use) | Python | 18,000+ | ~5,000 | 浏览器自动化 Agent |
| 7 | [alibaba/page-agent](https://github.com/alibaba/page-agent) | TypeScript | 10,000+ | ~6,000 | 阿里页面级 Agent |
| 8 | [agentscope-ai/agentscope](https://github.com/agentscope-ai/agentscope) | Python | 6,500+ | ~3,000 | 阿里 AgentScope 框架 |
| 9 | [clockworklabs/SpacetimeDB](https://github.com/clockworklabs/SpacetimeDB) | Rust | 28,000+ | ~5,000 | 实时数据库 |
| 10 | [huggingface/skills](https://github.com/huggingface/skills) | Python | 11,000+ | ~5,000 | HF 官方 Skills 仓库 |
| 11 | [alibaba/zvec](https://github.com/alibaba/zvec) | C++ | 11,000+ | ~4,000 | 轻量级向量数据库 |
| 12 | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | Go | 24,000+ | ~3,000 | 容器安全扫描 |
| 13 | [block/goose](https://github.com/block/goose) | Rust | 8,000+ | ~3,500 | Block 编码 Agent |
| 14 | [cloudflare/workerd](https://github.com/cloudflare/workerd) | TypeScript | 9,500+ | ~2,500 | Cloudflare Workers 运行时 |
| 15 | [AstrBotDevs/AstrBot](https://github.com/AstrBotDevs/AstrBot) | Python | 6,000+ | ~2,500 | 多平台聊天机器人 |
| 16 | [Blaizzy/mlx-vlm](https://github.com/Blaizzy/mlx-vlm) | Python | 5,500+ | ~2,000 | Apple MLX 多模态小模型 |
| 17 | [BerriAI/litellm](https://github.com/BerriAI/litellm) | Python | 13,000+ | ~2,500 | LLM 路由 / 代理 |
| 18 | [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) | TypeScript | 5,000+ | ~3,500 | Git 知识图谱 |
| 19 | [alibaba/OpenSandbox](https://github.com/alibaba/OpenSandbox) | Python | 9,500+ | ~3,000 | AI 沙箱平台 |
| 20 | [666ghj/BettaFish](https://github.com/666ghj/BettaFish) | Python | 4,000+ | ~3,000 | 群体情绪分析 |
| 21 | [666ghj/MiroFish](https://github.com/666ghj/MiroFish) | Python | 32,000+ | ~10,000 | 群体智能引擎 |
| 22 | [bytedance/deer-flow](https://github.com/bytedance/deer-flow) | Python | 65,000+ | ~32,000 | Long-horizon SuperAgent |
| 23 | [koala73/worldmonitor](https://github.com/koala73/worldmonitor) | TypeScript | 42,000+ | ~12,000 | 全球情报仪表板 |
| 24 | [moeru-ai/airi](https://github.com/moeru-ai/airi) | TypeScript | 38,000+ | ~10,000 | AI 虚拟伴侣 |
| 25 | [p-e-w/heretic](https://github.com/p-e-w/heretic) | Python | 17,000+ | ~5,000 | LLM 审查移除 |

> **数据精度声明**：上表 `Stars（估）` 和 `5 月新增（估）` 列是从现有 research 文件记录的"Q1 月榜 stars 数" + 该项目在 6 月月报中的"当前 stars" + WebSearch 抽样反推得到，**不是真实 monthly snapshot**。后续如有完整 5 月 trending 数据应以官方为准。

## 趋势分析

### 5 月三大主线

1. **Agent Skills 化范式确立**（5 月最显著趋势）
   - 4 月底 Anthropic 推出 Claude Skills 概念
   - 5 月生态爆发：`everything-claude-code` (157K stars 月增 80K) + `claude-skills` (12K) + `learn-claude-code` (35K) + `huggingface/skills` (11K) + `pm-skills` + `taste-skill` + `taste-skill`
   - 含义：Agent 工具调用 → "技能复用 + 资源化" 的范式转变；harness 不再硬编码工具，而是动态加载 skills
   - 与 MIT 2026 AI 三主线（已覆盖 T043）中的 "Agent Orchestration" 主线强相关

2. **Long-Horizon SuperAgent 框架竞争白热化**
   - `bytedance/deer-flow` (61K stars) vs `affaan-m/everything-claude-code` (157K) vs `coleam00/Archon` (8K) 三种设计哲学并行
   - 已覆盖 T020 (Agent Harness 三大流派解析)

3. **Apple Silicon 原生生态崛起**
   - `Blaizzy/mlx-vlm` (Apple MLX 视觉语言模型) + 6 月新出的 `apple/container` (Swift 实现微 VM 容器)
   - 反映 Apple Silicon 2026 性能/生态优势 + 厂商对本地 AI 的押注

### 5 月衰退领域

- **OCR / 文档智能**：Q1 占比 17%，5 月仅 5%。`markitdown` 仍在维护但新增 trending 减少
- **向量数据库新项目**：Q1 13% → 5 月 8%。`zvec`, `SpacetimeDB` 持续但新进入者减少，市场开始整合

## 与 Q1 月报对比

| 维度 | Q1 (2026-03) | Q2-5月 (2026-05) | 变化 |
|------|--------------|------------------|------|
| 主导语言 | TypeScript (40%) | TypeScript (38%) | → 持平 |
| 第二语言 | Python (33%) | Python (30%) | → 持平 |
| 第一领域 | AI Agent (53%) | AI Agent (35%) + Skills 生态 (22%) | ↑ 细分化 |
| 头部项目 star 量级 | 318K (openclaw) | 157K (everything-claude-code) | ↓ 头部降低 |
| 头部项目月增 | 80K+ | 80K (与 everything-claude-code 持平) | → 持平 |
| 新项目涌入速度 | 极快 | 极快（持平） | → 持平 |

**关键差异**：Q1 是 AI Agent 框架"百花齐放"阶段（大量新框架），Q2-5月是"生态整合 + Skills 化"阶段（少数 harness 主导，skills 作为复用层出现）。

## 6 月衔接（已写）

- `2026-06/2026-06-月报.md` 已完成，6 月 Agent Skills 生态占比 67%（5 月 22% → 6 月 67%）
- Skills 化趋势在 6 月加速，与 5 月观察一致

## 数据源与方法

### 数据来源

| 来源 | URL / 路径 | 状态 | 备注 |
|------|----------|------|------|
| Q1 月报基线 | `github-trending-reports/all-monthly-summary-2026-03-17.md` | ✅ 完整 | 提供 Q1 数据 |
| 4 月日榜快照 | `all-daily-summary-2026-04-05.md` | ✅ 完整 | 4 月最近一次抓取 |
| 6 月月报 | `2026-06/2026-06-月报.md` | ✅ 完整 | 提供 6 月数据反推 5 月 |
| research_*.md (74 文件) | `./research_*.md` | ✅ 部分覆盖 | 涵盖 4-5 月大部分 trending 项目 |
| WebSearch 抽样 | GitHub API + Trends 验证 | ⚠️ 部分 | 仅用于交叉核验 |
| **`trending_fetcher.py` 5 月运行** | — | ❌ **缺失** | 5 月期间未运行，**这是主要数据空缺** |

### 方法

1. 从 4 月日榜快照 + 6 月月报反推 5 月热门项目集合
2. 从 research 文件的"项目元信息"推断 5 月 stars 区间
3. WebSearch 抽样 5-8 个项目交叉验证 stars 数字
4. 对 Q1 月报和 5 月研究文件做语言 / 领域聚类
5. **不**做项目级深度新增研究（避免重复 T056 SkillOS 等已有研究）

### 限制

- **不是真实 monthly snapshot**：5 月 trending 完整数据未抓取
- **Stars 数字为估算**：误差范围 ±30%
- **新项目可能遗漏**：5 月出现的全新 trending 仓库（research 文件未覆盖的）可能缺失
- **后续改进**：TrendAgent 应该在 5 月自动化抓取缺失数据；或在 6 月报告中明确说明 5 月数据为合成

## 报告状态说明

| 类别 | 数量 | 项目 |
|------|------|------|
| ✅ 有 research 深度研究 | 25 | 上表项目均有 `research_*.md` 支撑 |
| ⚠️ Stars 数据为估算 | 25 | 全部 |
| ❌ 完整 5 月 trending 快照 | 0 | trending_fetcher 未运行 |
| ❌ 真实月度 stars 增量 | 0 | 无 monthly snapshot |

> ⚠️ **建议**：5 月 trending_fetcher 自动化的缺失是值得关注的运维问题。T012 任务（github-trending-analyzer 周报自动化）正是为解决此类问题而设的——如果 T012 已在跑，5 月数据不应缺失。**这暗示 T012 任务可能未正常运行**。

---

*报告生成时间: 2026-06-21*
*数据截止: 2026-06-21 (基于代理证据合成)*
*分析方法: 4 月日榜 + 6 月月报反推 + research 文件聚类 + WebSearch 抽样*
*数据可信度: 低-中，建议补抓*
