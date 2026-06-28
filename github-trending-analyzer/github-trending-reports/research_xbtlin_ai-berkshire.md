# xbtlin/ai-berkshire 深度研究报告

## 项目概述

ai-berkshire（仓库地址：https://github.com/xbtlin/ai-berkshire）是一套运行在 Claude Code 与 Codex 客户端之上的价值投资研究 Skill 合集。项目自我定位为"AI 时代的伯克希尔"，将巴菲特（Warren Buffett）、芒格（Charlie Munger）、段永平、李录四位价值投资大师的方法论系统化为可调用工作流，通过 4 个 AI Agent 并行执行多视角研究，输出可决策的投资研究报告。

项目核心交付物是 18 个 Markdown Skill 模板，覆盖深度研究、财报分析、行业筛选、持仓管理、思维工具五大场景。配套 7 个 Python 工具负责金融数据精确计算（`financial_rigor.py` 用 `decimal.Decimal` 防浮点误差）与报告抽检（`report_audit.py` 对生成报告 15% 随机抽样核验），以及 4 个跨平台同步脚本（同时支持 Claude Code slash command 与 Codex skill 包）。

截至 2026-06-28，仓库获得 4,257 stars / 596 forks [API]，3 个月龄（创建 2026-04-07），单一作者 xbtlin + AI 协作者 claude 共 1,068 次提交（贡献比 617:451），MIT 协议开源。中文 AI Agent + 价值投资双标签组合下，是近期中文圈最具传播势头的开源投研框架之一。[API]

## 基本信息

| 字段 | 值 | 来源 |
|------|------|------|
| 仓库名 | xbtlin/ai-berkshire | [API] `gh repo view` |
| 描述 | "AI 时代的伯克希尔：基于 Claude Code / Codex 的价值投资研究框架。巴菲特·芒格·段永平·李录四大师方法论 + 多Agent并行研究" | [API] |
| 创建时间 | 2026-04-07T11:19:51Z | [API] |
| 最后推送 | 2026-06-27T16:49:55Z | [API] |
| Stars | 4,257 | [API] `stargazerCount` |
| Forks | 596 | [API] `forkCount` |
| Watchers | 12 | [API] `subscribers_count` |
| Open Issues | 17 | [API] `open_issues_count` |
| 默认分支 | main | [API] |
| License | MIT | [API] `license.spdx_id` |
| 仓库体积 | 19,677 KB（约 19.2 MB） | [API] `size` |
| 是否 Fork | 否 | [API] |
| 是否归档 | 否 | [API] |
| 最新 Release | v1.0.0 - AI Berkshire 首发（2026-04-07） | [API] `releases` |
| 主要语言 | Python 125,234 字节 / Shell 2,311 字节 / Mermaid 1,316 字节 | [API] `languages` |
| Topics（20 个） | ai · ai-agent · anthropic · berkshire-hathaway · charlie-munger · china-stock · claude · claude-code · financial-analysis · fintech · fundamental-analysis · investment · investment-research · llm · mcp · portfolio-management · stock-analysis · stock-market · value-investing · warren-buffett | [API] |

### 贡献者

| 登录名 | 类型 | 提交数 | 占比 | 角色 |
|--------|------|--------|------|------|
| claude | User（id 81847） | 617 | 57.8% | AI 协作者（写代码/报告） |
| xbtlin | User（id 6993203） | 451 | 42.2% | 仓库主理人（架构/审稿/推文） |

[API] 来源：`contributors` 接口。

> 关键观察：项目呈现典型"主理人 + AI 协作者"双贡献者结构，与 f2d2fae commit 描述的"双身份"提交流程（Author=Everloster 显头像 + Committer=Agent）一致。AI 提交占多数说明 Skill 模板能高度自动化产出可合并内容，但仍依赖主理人做架构决策与质量把控。[代码]

## 技术分析

### 3.1 仓库结构

顶层目录布局（来源：`tree` 接口）：

```
ai-berkshire/
├── README.md · README_EN.md        — 中英双语文档
├── CLAUDE.md · AGENTS.md · ai_CLAUDE.md — 三套 Agent 协议（Claude Code / Codex / AI 记忆）
├── RKLB-investment-research.md      — 单标的研究范本
├── skills/                          — 18 个 Markdown Skill 源文件（canonical）
├── codex-skills/                    — 18 个 Codex skill 包（由 sync 脚本生成）
├── codex-prompts/                   — 18 个 Codex slash prompt 兼容层
├── tools/                           — 7 个 Python 工具
├── scripts/                         — 4 个同步/安装脚本
├── reports/                         — 95+ 份研究报告（按公司分子目录）
├── data/                            — 数据快照（CSV/JSON）
├── docs/                            — 路线图与专题文档
├── assets/                          — 图片与 Mermaid 架构图源文件
├── logs/                            — 运行日志
├── 实盘记录/ · 筛选公司/             — 中文目录：实盘记录与筛选候选池
└── LICENSE (MIT)
```

[API] 来源：`tree` 接口顶层 200 行扫描。

### 3.2 Skill 设计（核心交付物）

`/investment-team` Skill 全文 214 行（[代码] `skills/investment-team.md`），定义 10 步执行流程：

1. 展示团队框架（5 行表格确认）
1.5. **AI 研究偏见评估**（A/B/C 信息丰富度评级 + 应对策略）
2. TeamCreate（team-lead agent）
3. TaskCreate × 4（4 个研究任务）
4. **同一条消息并行启动** 4 个 general-purpose sub-agent（`run_in_background=true`）
5. 接收报告 + 实时进度展示
6. shutdown_request × 4
7. 汇总最终报告（8 段固定结构）
8. 写入 `reports/{公司名}/最终报告.md`
9. **数据抽检**（`report_audit.py extract` → 取数 → `verdict`）—— 准出门
10. TeamDelete 清理资源

[代码] 关键设计点：

- **4 视角分工（来源：`investment-team.md` 任务 1-4）**：
  | Agent | 视角 | 大师 | 任务核心 |
  |-------|------|------|---------|
  | business-analyst | 商业模式 + 护城河 | 段永平 | 飞轮、定价权、护城河 5 类验证 |
  | financial-analyst | 财务 + 估值 | 巴菲特 | 5 年财务、PE/PB/ROE、**强制 `financial_rigor.py` 验算** |
  | industry-researcher | 行业 + 竞争 | 芒格 | TAM、市占率、产业链、跨学科模型 |
  | risk-assessor | 风险 + 管理层 | 李录 | 监管、治理、长期确定性、10 年视角 |

- **跨平台抽象**：维护三套入口（`skills/*.md` Claude Code 源 / `codex-skills/*/SKILL.md` Codex 包 / `codex-prompts/*.md` 兼容层）。`scripts/sync-codex-skills.py` 头部 50 行展示了从 Claude Skill frontmatter 解析 → 生成 Codex SKILL.md 的转换逻辑（`split_frontmatter` + `metadata_for` + `yaml_quote`）。[代码]

### 3.3 金融严谨性工具栈（Python 实现细节）

`tools/financial_rigor.py` 全文 452 行（[代码]），零外部依赖（仅 stdlib 的 `decimal`/`json`/`math`/`argparse`），是 Skill 框架的"工程地基"。核心能力：

| 命令 | 作用 | 关键实现 |
|------|------|---------|
| `verify-market-cap` | 股价 × 总股本 vs 报告市值 | `_CTX.multiply(p, s)` 精确十进制；偏差 >5% 报 ❌、>1% 报 ⚠️ |
| `verify-valuation` | PE/PB/ROE/P/FCF/Dividend Yield | `_CTX.divide()` 防浮点；EPS=0 时跳过 PE |
| `cross-validate` | 多源数据交叉验证 | 取中位数作参考；偏差 >2% 报 ❌ |
| `benford` | 财务数据本福德分布检查 | 用于发现异常值 |
| `calc` | 通用精确算 | `--expr '510 * 9.11e9'` |

`tools/report_audit.py` 全文约 500 行（[代码]），实现 15% 随机抽样审计：

- **数据点提取**：6 套正则模式（百分比 / 亿元 / 倍数 / 万亿 / 美元绝对值 / 表格数字）+ `_LABEL_RE` + `_TABLE_ROW_RE` 两套复合匹配
- **白名单过滤**：`_is_valid_label` 跳过「来源 / 说明 / 合计 / N/A」等无意义标签
- **三步工作流**：`extract` → 人工取数 → `verdict` 准出/打回（偏差 ≤1% 通过，>1% 打回）

[代码] 关键观察：这是 Skill-first 范式的工程化证据——**投资判断完全由 Skill prompt 中的方法论驱动，Python 工具只承担「精确算 + 抽检」**，与 TradingAgents 把判断逻辑编码进 Python Class 形成鲜明对比。

### 3.4 安装与同步脚本

`scripts/install-claude-commands.sh`（14 行 [代码]）：

```bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${CLAUDE_COMMANDS_DIR:-$HOME/.claude/commands}"
mkdir -p "$DEST"
cp "$ROOT"/skills/*.md "$DEST"/
chmod +x "$ROOT"/tools/*.py "$ROOT"/tools/*.sh 2>/dev/null || true
```

逻辑：将 `skills/*.md` 复制到 `~/.claude/commands/`，把 `tools/` 设为可执行。零依赖，单文件即部署。

## 社区活跃度

### 4.1 Star / Fork 增速

3 个月龄达到 4,257 stars + 596 forks，按时间线性外推约 1,419 stars/月、199 forks/月。[API] 该速度在中文 AI Agent 开源项目中属于头部梯队，但样本期短无法判定可持续性。[推测]

### 4.2 提交频率

最近 50 个 commit 全部落在 2026-06-26 至 2026-06-27 两天内（[API] `commits` 接口）：

- 2026-06-27 单日 ≥10 个 commit（含 8 个长江电力 memo 微调、Yangtze Power 报告新增、A 股 AI 动量报告、Codex research report skill 等）
- 2026-06-26 单日 ≥2 个 commit（PDD 研究覆盖度评估、瓶颈猎手第 305 轮扫描）

[API] 量化结论：**最近一周提交强度极高（>50 commits/week），但分布极度集中**——主理人在 2026-06-27 一天内反复微调同一份长江电力报告（rename → polish → refine → add → 添加茅台）。这种模式与"AI Agent 一次产出多次润色"的工作流吻合，也暴露单一作者单轨制的可持续性问题。[推测]

### 4.3 贡献者结构

仅 2 位贡献者（[API] `contributors`），提交比 617:451 ≈ 1.37:1。**bus factor = 1**（xbtlin 作为架构师不可替代；claude 虽提交多但作为 AI Agent 可被替换）。这是开源治理的典型单点故障。[推测]

### 4.4 Issue / PR 状态

17 个 open issues（[API]），未提供关闭率数据。[推测] 该项目主要使用 GitHub 作为单向发布渠道（主理人 commit + AI 协作者 commit），社区参与度可能以"下载使用 + fork"为主，而非"issue 互动"。

## 发展趋势

### 5.1 项目演进节奏

`ai_CLAUDE.md`（项目 AI 记忆文件）自陈 Skill 数量演进：

- **V1（5 个 Skill）** — 覆盖买入前研究：investment-research / investment-team / investment-checklist / industry-research / private-company-research
- **V2（9 个 Skill）** — 补齐买入后流程：新增 earnings-review / thesis-tracker / portfolio-review / management-deep-dive
- **当前（18 个 Skill）** — 全生命周期 + 行业筛选 + 思维工具

[API][推测] **量化结论**：3 个月内 Skill 数量从 5 → 18，月均增长约 4.3 个 Skill。该速度属于「功能蔓延」区间——用户能否在 18 个 Skill 中准确选择是 UX 问题，而非功能问题。`SKILL.md` / `AGENTS.md` 中均未提供 Skill 选择决策树。[推测]

### 5.2 标的偏好

`reports/` 目录按公司分子目录，最近一周（[API] `commits`）涉及：

- 长江电力（Yangtze Power）：6+ commit，2026-06-27 单日反复润色
- 贵州茅台（Moutai）：新增研报
- 拼多多（PDD）：研究覆盖度评估与信息缺口分析
- 阿里巴巴（Alibaba）：FY2026Q4 外卖业务专题（2026-06-15）
- AI 算力 / AI 模型 / AI 应用 / AI 基建电力：funnel 漏斗筛选报告（4 份，2026-05-09 同日）

[API] **量化结论**：标的分布呈现「**中概互联网（腾讯/阿里/PDD/美团）+ 价值股蓝筹（茅台/长江电力）+ AI 全产业链**」三角，**完全聚焦中国资本市场**，与项目 Topics 中的 `china-stock` 标签一致。

### 5.3 跨平台扩展

最近 commit 中出现：

- `052bfc9  add Codex research report craft skill` — 新增 Codex 专用 skill
- `f375741  添加 Codex 兼容技能入口`
- `9291871  完善 Codex 安装说明`

[API] **趋势判断**：项目从 Claude Code 单端起步，2026-06 开始系统性扩展到 Codex 客户端。`codex-skills/`（19 个 SKILL.md）与 `codex-prompts/`（18 个 prompt）的目录规模印证这一点。[API] 这与 MCP / A2A / AGENTS.md 三大 Agent 互操作协议在 2025-2026 年间的标准化浪潮一致。[推测]

## 竞品对比

下表数据均通过 `gh api repos/{owner}/{repo}` 实测（2026-06-28），禁止凭记忆。

| 维度 | xbtlin/ai-berkshire | virattt/ai-hedge-fund | TauricResearch/TradingAgents | hsliuping/TradingAgents-CN |
|------|---------------------|----------------------|------------------------------|----------------------------|
| Stars | 4,257 [API] | 60,576 [API] | 89,171 [API] | 29,174 [API] |
| Forks | 596 [API] | n/a | n/a | n/a |
| License | MIT [API] | MIT [API] | Apache-2.0 [API] | NOASSERTION（自定义，疑似非标准中文协议）[API] |
| 最后推送 | 2026-06-27 [API] | 2026-06-17 [API] | 2026-06-22 [API] | 2026-04-20 [API] |
| 基础实现 | Markdown Skill + Python 工具 | Python + LangChain | Python + LangGraph | Python + LangGraph（中文 fork） |
| 视角数量 | 4（固定为巴芒段李） | 16（含木头姐等） | 多空双方 + 风控 + 交易 | 与上游一致 |
| 标的偏好 | 中国互联网 + 蓝筹 | 美股为主 | 美股为主 | A 股 / 港股 |
| 输出形式 | Markdown 完整研报（数千字） | JSON 信号 | 结构化决策 JSON | 中文决策 JSON |
| 时序数据 | 不依赖 | 不依赖 | Kronos 预训练模型 | 继承上游 |
| 跨平台 | Claude Code + Codex | Python 单栈 | Python 单栈 | Python 单栈 |
| 可证伪性 | 强（每份报告带估值假设） | 中 | 强（回测） | 强 |

[API] 实测 stars/license/pushed 全部来自 `gh api repos/{owner}/{repo}` 精确返回值，禁止凭记忆。

### 关键对比观察

1. **Star 量级差距显著**：TradingAgents（89,171）是 ai-berkshire（4,257）的 21 倍。但 TradingAgents 是 2025 年初发布（领先 1 年多），ai-berkshire 3 个月龄追赶速度可观。[推测]
2. **范式分化清晰**：ai-berkshire 是 Skill-first / Markdown 派，TradingAgents / ai-hedge-fund 是 Python Class / LangChain 派。前者优势在跨平台 + 可审计，后者优势在工程化 + 时序数据。[推测]
3. **标的偏好互补**：ai-berkshire 唯一聚焦中国资本市场（Topics 中 `china-stock`），与 TradingAgents 的美股偏好形成天然分赛道。这降低了直接竞争风险。[推测]
4. **License 风险**：hsliuping/TradingAgents-CN 使用 NOASSERTION（GitHub 无法识别 SPDX 标识），意味着这是非标准中文协议——fork 自上游但未采用 Apache-2.0。ai-berkshire 保持 MIT 更利于企业采用。[API]

## 总结评价

### 核心优势

1. **范式创新度**：Skill-first 范式在金融域做到了工程化深度。Markdown 作为方法论载体，配合 GitOps 式同步脚本，把"投资方法论迭代"做到了"软件工程纪律"的水平。这是中文 AI Agent 圈少见的工程化胜利。[推测]
2. **跨客户端抽象**：Claude Code 与 Codex 两端共用同一套 canonical workflow（`skills/*.md`），降低用户切换客户端的迁移成本。`scripts/sync-codex-skills.py` 的设计是声明式架构的典型案例。[代码]
3. **金融严谨性工具栈**：三层防御（`decimal.Decimal` 算 → 双源交叉验证 → 15% 抽样审计）让错误显性化而非消除，是数据治理的成熟形态。[代码]
4. **中文市场独占**：在中概互联网 + 蓝筹价值股 + AI 产业链的中国资本市场，ai-berkshire 是目前少有的系统性投研框架（Topics 含 `china-stock`，标的覆盖腾讯/阿里/PDD/茅台/长江电力等）。[API]

### 主要风险

1. **单点故障**：bus factor = 1，2 名贡献者中 xbtlin 不可替代；高频单日提交（2026-06-27 单日 ≥10 commit）暴露作者精力瓶颈。[API][推测]
2. **功能蔓延**：3 个月内 Skill 从 5 → 18，月均 +4.3 个 Skill，缺少 Skill 选择决策树，用户使用门槛随数量上升。[API][推测]
3. **数据时效性依赖**：Skill 要求 Agent 用 WebSearch 收集数据，搜索结果可能过时、源间矛盾；`financial_rigor.py` 双源验证只解决"已有源的一致性"，不解决"源本身是否最新"。[推测]
4. **声称业绩未经审计**：README 自报 2024 年 +69.29%、2025 年至今 +66.38%，但无第三方审计报告；与 Skill 框架质量不完全正交——集中持有优质中概股也可能产生类似收益。[推测]

### 适用人群

- **个人价值投资者**（重点）：希望用 AI 系统化巴芒段李方法论，且标的偏好中概互联网 + A 股蓝筹的用户。
- **AI Agent 开发者**：想学习 Skill-first 范式如何在垂直域工程化的从业者（参考价值高于直接套用）。
- **不适合**：追求 Python 工程化深度（推荐 TradingAgents）、纯美股量化（推荐 ai-hedge-fund）、需要时序数据回测（推荐 Kronos 路线）的用户。

### 总体评分（1-5 星，半星粒度）

| 维度 | 评分 | 备注 |
|------|------|------|
| 创新度 | ★★★★★ | Skill-first 范式在金融域的工程化典范 |
| 工程质量 | ★★★★☆ | 工具栈扎实，但同步脚本与单测覆盖未公开 |
| 文档完整度 | ★★★★★ | 中英双语 README + 三套 Agent 协议 + AI 记忆文件 |
| 社区活跃度 | ★★★★☆ | 3 个月 4,257 stars，但单点故障 |
| 中文市场覆盖 | ★★★★★ | 同赛道唯一系统化框架 |
| 可证伪性 | ★★★★☆ | 每份报告带估值假设，但声称业绩缺审计 |
| **综合** | **★★★★☆** | 中文圈价值投资 AI Agent 当前最完整实现 |

---

*报告生成时间: 2026-06-28*
*研究方法: github-deep-research 多轮深度研究*