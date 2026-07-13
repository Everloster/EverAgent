# ResearAI/OpenScience 深度研究报告

## 项目概述

`ResearAI/OpenScience` 是一个 **2026 年 7 月初刚开源的、本地优先（local-first）的 AI 科研桌面应用**。官方一句话描述是："OpenScience organizes research questions, evidence, tasks, and agent work into a traceable collaboration workspace."（把研究问题、证据、任务和 Agent 工作组织进一个可追溯的协作工作空间）。[README]

它的产品形态不是命令行库，也不是网页服务，而是一个 **Electron 桌面客户端**（支持 macOS / Windows / Linux），本地跑 Agent、本地存数据，强调"可追溯"与"数据不出本机"。[代码][README]

从代码内部命名可以看出它的来历：包名是 `@deeporganiser/desktop`，提交历史里反复出现 `deeporganiser` 字样——**OpenScience 是内部项目 "DeepOrganiser" 的对外品牌重塑**。[代码] 而其 Agent 内核则构建在 **Codex agent core** 之上（提交里出现 "Codex self-identity override" 等字样），并通过 ACP（Agent Client Protocol）与模型层通信。[代码]

产品叙事上，它对标的是"把科研工作流交给 AI Agent"这一方向（README 提及受 "Claude Science" 式产品方向启发）：不是简单的问答，而是把**一整套科研生命周期**——提问、检索证据、拆任务、Agent 执行、产出图表/论文——收拢进一个带审计轨迹的桌面工作台。[README][推测]

> 一句话定位：**一个本地优先、以 Codex/ACP 为 Agent 内核的桌面科研工作台，把"证据检索 → 任务编排 → 多 Agent 执行 → 学术产出"全链路装进一个可追溯的应用里。**

## 基本信息

| 项目 | 数据 |
|------|------|
| 仓库 | ResearAI/OpenScience |
| 内部代号 | DeepOrganiser（包名 `@deeporganiser/desktop`）[代码] |
| 创建时间 | 2026-07-02 [API] |
| 最近推送 | 2026-07-05 [API] |
| Stars | 23 [API] |
| Forks | 2 [API] |
| 开放 Issue | 0 [API] |
| 许可证 | AGPL-3.0-only [API] |
| 主语言（API 显示） | Stata（10.6 MB，疑为大文件/vendored 产物）[API][推测] |
| 实际技术栈 | TypeScript（8.7 MB）+ Python（3.9 MB）[API] |
| 贡献者 | ResearAI（59 次提交）、Anny-hudi（5 次提交）[API] |
| 最新发版 | v0.1.3（2026-07-05）；此前 v0.1.2 / v0.1.1（均 2026-07-03）[API] |

**关于"主语言 Stata"的说明**：GitHub Linguist 把主语言判为 Stata（10.6 MB），但仓库定位是 Electron 桌面应用，实际开发语言是 TypeScript + Python。Stata 字节数最大，极可能是某个被计入统计的大体积数据/词典/生成文件被误判，**不代表项目真实用 Stata 编写**。[API][推测]

## 技术分析

### 架构：Electron monorepo + 三层能力栈

从仓库配置看，OpenScience 是一个标准的现代 Electron 工程 [代码]：

- **monorepo**：`workspaces: packages/*`，多包管理。
- **构建**：`electron-vite`（主进程/渲染进程统一构建）。
- **代码质量**：`oxlint` + `oxfmt`（Rust 系高性能 lint/format 工具链）。
- **测试**：`vitest`（单测）+ `playwright`（端到端）。
- **UI**：`@arco-design/web-react`（字节跳动 Arco 设计体系）+ CodeMirror 系列编辑器组件。[代码]

### Agent 内核：Codex + ACP + 多模型接入

关键依赖揭示了它的 Agent 层设计 [代码]：

- **`@agentclientprotocol/sdk`（ACP，^0.18.2）**：Agent Client Protocol，是 Agent 与前端/工具之间的标准化通信协议。
- **`@anthropic-ai/sdk`（^0.71.2）** 与 **`@aws-sdk/client-bedrock`**：直连 Anthropic 及通过 AWS Bedrock 接入模型，多供应商能力明确。
- **Codex agent core**：提交历史出现 "Codex self-identity override"、MCP/ACP approvals 等，说明其 Agent 执行内核复用了 Codex，并在其上做了身份/审批层的定制。[代码][推测]

这套组合意味着：OpenScience **不是从零写 Agent，而是把成熟的 Codex 执行核 + ACP 协议 + Anthropic/Bedrock 模型层组装成一个带审批与 MCP 工具接入的桌面 Agent 运行时**。

### 多 Agent 协作："team" 是一等公民

最能体现其野心的是端到端测试里的一整套 **多 Agent "team"** 用例 [代码]：`team-create`、team 生命周期、`whitelist`（成员白名单）、team `communication`（Agent 间通信）。这表明产品设计中，**多个 Agent 组成"研究团队"协同工作**是核心场景，而非单 Agent 问答——与它"可追溯协作工作空间"的定位一致。[代码]

### 四种工作模式与内置技能库（README 宣称）

README 宣称产品提供四种模式与庞大的默认能力 [README]：

- **Science Mode（科研模式）** / **Medical Evidence Mode（医学循证模式）** / **Goal Mode（目标模式）** / **Knowledge Distillation Mode（知识蒸馏模式）**。
- **352 个默认科研技能**，覆盖 10+ 研究方向。[README]

> 注：以上模式与技能数为 README 的产品宣称，属项目自述，尚未逐条代码核验。[README][推测]

### 可追溯性：把"研究问题—证据—任务—Agent 工作"串成审计链

产品名里的 "traceable collaboration workspace" 不是口号，而是其核心数据模型。官方描述把四类实体显式列出并组织在一起：**research questions（研究问题）、evidence（证据）、tasks（任务）、agent work（Agent 工作）**。[README]

这种设计的意图是解决 AI 深研工具最大的信任痛点——**"结论从哪来"**：

- 每条结论应能回溯到支撑它的**证据**（哪篇论文、哪个数据库记录）。[README][推测]
- 每个 Agent 动作应挂在某个**任务**下，任务又服务于某个**研究问题**。[README][推测]
- 配合 MCP/ACP 的**审批（approvals）机制**，敏感操作需人类确认，形成"人在环上"的可控执行。[代码]

对科研、尤其是医学循证场景，这种"每一步都可审计"的能力，比单纯"答得快"更关键——它决定了产出能否被同行信任与复用。[推测]

### 证据层：对接大规模科研数据源（README 宣称）

README 列出的"证据层"覆盖面很大 [README]：

| 数据类型 | 规模宣称 |
|----------|----------|
| 论文 | 1100 万+ |
| 药品/器械文档 | 22.5 万+ |
| 临床试验 | 100 万+ |
| 摘要 | 1.5 亿+ |

数据源包括 PubMed、ChEMBL、GEO、AlphaFold 等 20+ 数据库家族；产出物覆盖图、表、notebook、论文手稿。[README] 这些规模数字来自 README 自述，属**营销性能力宣称**，需以实际接入情况为准。[README][推测]

## 社区活跃度

- **极新、极小、但迭代密集**：仓库 2026-07-02 才创建，截至 2026-07-05 已连发 **v0.1.1 → v0.1.2 → v0.1.3** 三个版本，几乎每天一个 tag。[API] 这是典型的**产品刚上线、高频打磨期**特征。[推测]
- **Star 体量尚小**：23 stars / 2 forks / 0 open issues。[API] 作为一个刚开源几天的项目，热度还未起来，也没有社区 issue 反馈积累。
- **贡献者高度集中**：仅 ResearAI（59 次提交）与 Anny-hudi（5 次提交）两人，且 ResearAI 占绝对主导。[API] 属于**单一团队/核心作者驱动**，尚无外部社区贡献。
- **无历史包袱**：0 open issues 更多反映"太新还没人提"，而非"质量极高"，不宜过度解读。[推测]
- **版本节奏透露质量意识**：短短几天连打三个 patch 版本（v0.1.1→v0.1.3），且都在 2026-07-03～07-05 之间，说明团队在**快速修 bug、稳定首个可用版本**，而非一次性丢出代码后不管。[API][推测]
- **命名迁移的痕迹**：仓库仍保留 `deeporganiser` 内部代号，说明"DeepOrganiser → OpenScience"的品牌切换发生得很晚（临近开源），对外统一心智尚在建立中。[代码][推测]

## 发展趋势

- **本地优先 + 可追溯**是差异化主轴：在 gpt-researcher、STORM 等偏"云端/服务化"的深研工具之外，OpenScience 押注**桌面端、数据本地化、全链路可审计**，瞄准对数据隐私与合规敏感的科研/医疗场景。[README][推测]
- **医学循证是重点垂类**：单列 Medical Evidence Mode，并接入 ChEMBL、临床试验、药品文档等，显示它想在**医学/生命科学循证研究**这个高价值垂直领域切入，而非泛泛的"通用深研"。[README][推测]
- **多 Agent 团队化协作**：从 team e2e 用例看，产品会继续往"多 Agent 分工协作完成一个课题"方向演进，这也是它区别于单轮深研工具的护城河设想。[代码][推测]
- **AGPL-3.0 的信号**：选择传染性最强的 AGPL，意味着团队大概率走 **"开源内核 + 商业授权/托管"** 的双轨路线——鼓励自托管，同时用 copyleft 约束把商业闭源分叉挡在门外。[API][推测]
- **早期风险**：项目太新（几天）、核心依赖单团队、README 宣称的能力（352 技能、亿级证据）尚待社区验证，短期内稳定性与真实覆盖度存疑。[推测]

## 竞品对比

OpenScience 处在 **"AI 深度研究 / 自主科研 Agent"** 这条 2025–2026 年极热的赛道上，同类项目的 star 体量远大于它，但定位各有侧重。

| 项目 | Stars | 许可证 | 最近推送 | 定位差异 |
|------|-------|--------|---------|---------|
| **ResearAI/OpenScience** | **23** | AGPL-3.0 | 2026-07-05 | 本地优先桌面应用，Codex/ACP 内核，多 Agent team，主打医学循证与可追溯 |
| bytedance/deer-flow | 76,324 | MIT | 2026-07-07 | 字节开源深研框架，模块化多 Agent，社区体量最大 [API] |
| stanford-oval/storm | 29,882 | MIT | 2025-09-30 | 斯坦福出品，自动生成带引用的类维基长文，偏"写综述" [API] |
| assafelovic/gpt-researcher | 28,127 | Apache-2.0 | 2026-07-05 | 老牌自主研究 Agent，联网检索+报告，生态成熟 [API] |
| langchain-ai/open_deep_research | 11,949 | MIT | 2026-06-26 | LangChain 官方深研范式，强调可配置的研究图 [API] |

**关键区别**[代码][API][推测]：
- **vs deer-flow / open_deep_research**：后者是**框架/库**，供开发者搭建深研流水线；OpenScience 是**开箱即用的桌面成品应用**，面向终端科研用户而非二次开发者。
- **vs STORM**：STORM 聚焦"生成带引用的综述文章"这一窄产出；OpenScience 覆盖更全的科研生命周期（证据→任务→Agent→图表/论文/notebook），且强调本地与多 Agent 协作。
- **vs gpt-researcher**：gpt-researcher 生态成熟、以联网检索+报告为主；OpenScience 差异在**本地优先 + 医学循证垂类 + Codex 执行核 + team 协作**，但成熟度与社区体量目前远不及前者。
- **共性**：都在解决"让 AI 自主完成一轮研究"的问题，OpenScience 的赌注是**桌面化、可追溯、垂直医学**这三点能否换来差异化价值。

## 总结评价

**优点**：
- **定位清晰且差异化**：本地优先 + 可追溯 + 多 Agent team + 医学循证，在拥挤的深研赛道里选了一个有护城河潜力的组合。[README][代码]
- **工程底座现代且务实**：Electron monorepo + electron-vite + oxlint/oxfmt + vitest/playwright，并复用 Codex 执行核与 ACP 协议，不重复造轮子。[代码]
- **多供应商模型接入**：同时接 Anthropic SDK 与 AWS Bedrock，避免单一模型锁定。[代码]
- **迭代积极**：开源几天内连发三个版本，团队推进节奏快。[API]
- **不重复造轮子**：Agent 执行核复用 Codex、协议用 ACP、UI 用成熟的 Arco，把精力集中在"科研工作流编排"这个真正的差异点上。[代码][推测]

**局限**：
- **极其早期**：2026-07-02 才建仓、23 stars、仅两名贡献者，稳定性与生态几乎空白。[API]
- **能力宣称待验证**：README 的"352 技能 / 1100 万论文 / 1.5 亿摘要"等属自述营销数字，尚无社区独立验证。[README][推测]
- **AGPL 门槛**：传染性 copyleft 会劝退部分想商业集成的用户。[API][推测]
- **主语言被误判**：GitHub 显示主语言为 Stata，反映仓库里混入了大体积非源码文件，工程整洁度上有优化空间。[API][推测]
- **依赖重、启动门槛高**：作为 Electron + 本地 Agent + 多数据源的桌面应用，安装体积与本地资源占用大概率不低，对轻量试用不友好。[推测]
- **协议与心智仍在迁移**：`deeporganiser` 代号残留、README 宣称与实际实现的差距，都需要后续版本收敛。[代码][推测]

**评价**：OpenScience 是一个**方向感很强、但仍处于"产品刚上线"阶段**的项目。它没有走"再造一个深研框架"的老路，而是把赌注押在**本地优先的桌面科研工作台 + 医学循证垂类 + 多 Agent 协作**上，工程选型（Codex 内核 / ACP / Arco / Bedrock）也显示背后是一支有经验的团队（很可能与字节 Arco 体系相关）。[代码][推测] 它的真正考验不在技术栈，而在于 README 里那些宏大的能力宣称能否兑现、以及能否在 deer-flow、gpt-researcher 等巨头环伺下跑出自己的用户群。**现在关注它，看的是潜力与方向，而非成熟度。**

---
*报告生成时间: 2026-07-07*
*研究方法: github-deep-research 多轮深度研究*
