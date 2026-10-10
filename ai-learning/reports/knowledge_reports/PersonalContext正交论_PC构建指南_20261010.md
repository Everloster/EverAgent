---
title: "Personal Context 正交论：穿越 AI 进步周期的资产，与 PC 的构建工程"
domain: "ai-learning"
report_type: knowledge_report
status: completed
created: 2026-10-10
updated_on: 2026-10-10
tags: [PersonalContext, 正交性, 个人助手, AgentOS, memory层, context-engineering, EverAgent实践, 投资级思考]
difficulty: ⭐⭐⭐⭐
source_trigger: "用户 2026-10-10 今日思考：①做上下文的持续正交（Personal/Work Context）；②去年暴论：未来个人助手=输入法+IM+浏览器+搜索+AgentOS 的综合体；③穿越周期的正交思考：持续积累个人高效的 PC/WC，与 AI 进步持续正交——结合乱翻书275（2026-10-09 转写）、Laya/Jev 研究（2026-10-09）、个人助手产品全景调研（2026-10-09）展开论证"
related_reports:
  - "../..//podcast-learning/reports/2026-09-21_xiaoyuzhou-luanfanshu_personal-agent-wars.md"
  - "./Laya_System1决策模型_深度解析_20260922.md"
  - "../../github-trending-analyzer/reports/research_NandhaKishorM_laya.md"
---

# Personal Context 正交论：穿越周期的资产，与 PC 的构建工程

> **x → f → f(x)**
> - **x**：AI 模型以月为单位快速迭代，个人在 AI 时代应该积累什么，才能让自己的投入不被（甚至因）模型进步而贬值？
> - **f**：正交论——把积累目标从"会用 AI 的技巧"（过程性，随模型进步贬值）切换到"Personal/Work Context"（事实性资产，随模型进步**升值**）：模型越强，同一份 context 兑现的价值越大。Context 是油，模型是越来越高效的炼油厂 [本报告论证]。
> - **f(x)**：接受 f 后，个人策略变为三段链条——**积累事实性 context → 用 memory 工程炼成画像 → 通过反复交付换取委托信任**；工程上则要求 context 自持（所有权）、结构化（可检索）、带 provenance（可审计）、分层维护（按贬值速率区别投入）。验证状态：前段有 2026 年产品/资本市场的强证据支撑（四赌注全部围绕 context 变现 [Web][转写]），中段有反例警示（豆包签证 bad case：context≠画像 [转写]），后段尚未有个人可自持的成熟方案——是本报告的开放前沿。

---

## 0. 论点与来源全景

本报告综合三条研究线（全部为本仓 2026-10-09 一手产出）+ 两轮 web 核实：

| 证据源 | 关键贡献 |
|---|---|
| 乱翻书 275 转写精读（Today 创始 PM Suki 等三位产品经理） | context 只是入门、memory 工程极难、信任和习惯最值钱、四产品四赌注 [转写] |
| Laya/Jev 双报告 | Jevons 悖论（决策智能越便宜→调用越频繁）、决策原语化、OpenAI Decisions API 入场 [代码][Web] |
| 个人助手产品全景调研（12+ 轮 web 核实） | 2026 秋品类爆发时间线、巨头/创业公司格局、OpenClaw heartbeat+daily log 原型 [Web] |
| Web 核实（本报告新增） | Agent memory 竞争格局（Mem0/Letta/Zep/memU/mcp-memory-service）、Anthropic context engineering、AGENTS.md 工程实践 [Web] |
| EverAgent/eacli 自身实践 | 本论点的活体实验：两仓结构 + PROFILE/MAP/wiki 分层 + context catalog/get/search [本仓] |

---

## 1. 为什么"正交"是正确的问题框架

### 1.1 换问题的收益

面对快速迭代的 AI，常问的是"该学什么工具/模型"——这个问题**没有稳定答案**（答案半年一换）。正交论换了一个问法："什么东西在模型变化下不变（甚至受益）？"——这个问题有结构化答案。这是把不可控变量（模型进步）从策略依赖中剥离：**你不预测模型，你让模型的任何进步都为你服务** [推测→论证于§2]。

### 1.2 正交性的两层数学含义

1. **独立性**：PC 的存在与增长不依赖任何特定模型——你的偏好、决策历史、判断对错记录、关系网络是"你的人生函数"的输出，模型换不换它都持续产生。
2. **投影为正收益**：严格说这不是零相关的正交，而是**单调互补**——模型能力 ↑ 时，同一份 PC 的兑现价值 ↑。展开为三个机制：
   - **兑现机制**：去年 GPT-4 级模型拿着你的 context 只能做摘要；今年的 agent（Instinct/Grok Bot/Muse）拿着同一份 context 能把事办完。Context 没变，兑现从"问答"升级到"执行"。
   - **Jevons 机制**（Laya 期已论证）：决策智能成本下降两个数量级 → 单人可调用的决策频次暴涨 → 每份 context 被调用的次数上升。TypeSafe 给模型取名 Jevons（悖论）正是这个逻辑 [Web Wikipedia]。
   - **Bitter Lesson 的个人版**：Sutton 说"能随算力扩展的通用方法长期总赢"；个人版是"**能随模型能力扩展的个人资产长期总赚**"。反过来，依赖模型弱点的方法（prompt 技巧、绕幻觉的手法、特定版本的手感）会随补弱而清零。

### 1.3 关键边界：两类 context，贬值速率天差地别

| | 事实性 context | 过程性 context |
|---|---|---|
| 内容 | 偏好/价值观/决策历史/判断对错记录/知识资产/关系网络 | prompt 模板/工作流配置/工具使用技巧/"怎么用 AI"的经验 |
| 贬值速率 | ≈0（只随人生增长） | 高（强模型平替弱模型时代的手艺） |
| 与模型进步的关系 | 升值（兑现机制） | 贬值（被能力进步吞噬） |
| 维护策略 | 持续投入、只增不删 | 定期允许作废、不恋战 |
| EverAgent 实例 | `reports/`、`wiki/concepts/`、`PROFILE.md` | `AGENTS.md` 流程规则、各 skill 的操作姿势 |

**判别法**：问"下一代模型免费发布后，这条积累是更值钱还是更不值钱？"——偏好与判断记录更值钱；使用技巧大概率不值钱。用户的正交论在事实性 context 上完全成立，在过程性 context 上恰好反向 [本报告论证]。

---

## 2. 证据链：2026 年的市场在为什么定价

### 2.1 四赌注 = context 变现的四条路径

乱翻书 275 的四产品拆解，换个角度看全是"context 资产的变现设计"：

- **Town**：邮箱深耕 = 在**最高频的 context 产生地**（邮件）持续收割，用谨慎交付换委托权——委托权是 context 的期货 [转写]
- **Instinct**：No-App 住 IM + 接信用卡/屏幕/麦克风 = **全谱系 context 捕获**（你看什么、说什么、花什么），$50M→$10B 半年 200 倍 = 资本市场给"独家 context 管道"的定价 [转写][Web]
- **Grok Bot**：Bot 队伍各配云计算机 = context 的**分工持有**（email bot 沉淀邮件 context，research bot 沉淀研究 context）[Web x.ai]
- **Muse**：免费 + 每用户一台 VM = 用现金换 context 规模——小扎的购物叙事（收藏=未兑现的意图）本质是"Instagram 十年种草积累的意图数据今天可以变现了" [转写]

**Meta 愿意烧钱、OpenAI 三周内跟进（Decisions API→Dots）、Instinct 估值超 Airbnb 起步期**——三方同时用真金白银投票给同一个资产类别。这不是炒作叙事能解释的密度 [Web Fortune/NYT/TechCrunch]。

### 2.2 反方证据：context 是必要不充分

播客里两刀锋利的反证，给正交论划出边界：

1. **"光拿到 context 完全不够"**（Suki）：从一堆 context 构建真正画像的 memory 工程比想象中难得多——Today 花大量时间做 context 处理（清洗、关联、画像构建）[转写]
2. **豆包签证 bad case**（Vanessa）：有日本签证的记忆，却在无关话题里强行关联——"有长期记忆但不体贴人"。**裸 context 不是资产，炼成画像并恰当调用的 memory 才是** [转写]
3. **"最值钱的位置是信任和习惯，context 只是入门基础"**（快问快答共识）——第三段链条（委托信任）目前只能通过持续使用某产品积累，个人无法完全自持 [转写]

### 2.3 巨头悖论：为什么正交论对个人比对公司更成立

Vanessa 的判断"这波没有网络效应，谁好用第二天就切换" [转写] 对公司的护城河是坏消息，对个人是好消息：**产品可以换，你的 context 资产不随产品迁移而灭失**（前提是自持，见 §4.1）。公司烧钱抢的是 context 的托管权；个人自持则让所有烧钱者变成你的免费炼油厂——模型军备竞赛的每一分投入都在升值你的存量 context。**这是个人视角下最反直觉的一步：巨头竞争越惨烈，自持 PC 的持有者越受益** [推测→机制论证于§1.2]。

---

## 3. PC 的解剖学：五层结构与贬值地图

构建 PC 先要定义 PC。综合产品实践与 EverAgent 经验，PC 分五层（按贬值速率排序）：

| 层 | 内容 | 贬值速率 | 对应 EverAgent 组件 | 对应产品实践 |
|---|---|---|---|---|
| L1 身份层 | 偏好、价值观、人格画像、"我是谁" | ≈0（缓变） | `PROFILE.md` | Today 的长期画像 |
| L2 事实层 | 决策历史、判断对错记录、已验证知识 | 低（需防腐） | `reports/`、`wiki/concepts/entities` | daily log（OpenClaw 原型） |
| L3 关系层 | 人际网络、协作历史、对他人/机构的判断 | 低 | `wiki/entities/` | IM context（Instinct） |
| L4 程序层 | 工作流、判断启发式、操作技能 | **高** | `AGENTS.md`、`skills/` | agent 的 skills（Grok Bot） |
| L5 委托层 | 信任与授权边界（哪些事可全自动/需确认/不许碰） | 反向增长（越用越厚） | 尚无显式组件（open question） | Town 的"谨慎交付换委托"、Laya 的 act/escalate 头 |

两个关键观察：
- **L5 是终极资产**：L1-L4 都是输入，L5（"我授权你做什么"）是 context 资产的复利形态。Laya 研究里的 act/escalate 头（成本矩阵自动学出 62.5% 置信阈值才行动）是 L5 的模型内置版 [代码]；Town 的整条产品线是 L5 的服务版 [转写]。
- **Work Context 是 PC 的子集而非平行物**：WC = PC 的 L2+L4 在职业域的投影（EverAgent 的 MAP.md=WC 的覆盖地图；CONTEXT.md=WC 的产出台账）。正交积累时用同一套分层，不必建两套系统——切换工作时 L1/L3/L5 全部携带 [本报告设计]。

---

## 4. PC 构建工程：原则、方案与 EverAgent 实践

### 4.1 四条设计原则

1. **自持（Ownership）**：context 存自己控制的存储（本地/git 私有仓优先，开放格式）。Vanessa 原话的镜像："住在别人的 IM 里，接口不属于你，产品的命运也不属于你"——对个人即"context 托管给任何产品都只是租借" [转写]。自持不是拒绝产品，而是**产品为炼油厂、油库在自己手里**。
2. **结构化（Retrievability）**：裸日志 ≠ 资产。OpenClaw 的 daily log 是原型但停留在流水账；EverAgent 的实践是三层结构——报告（叙事与判断）→ wiki 概念页（可引用的知识单元）→ open-questions（缺口即拉力）。结构决定 LLM 能否精准取用 [本仓实践]。
3. **Provenance（可审计）**：每条事实带来源与时间，推测标 `[推测]`（METHODOLOGY §二）。这不仅是防幻觉，更是**资产防伪**——context 中毒（错误判断沉淀为"事实"）是 PC 的 P0 风险（§5.2）。eacli 的 sha256+repo 路径 provenance 是工程化形态 [本仓实践]。
4. **分层维护（Deprecation Policy）**：按 §1.3 判别法区分投入——事实层只增不删（历史判断错了也不删，标注 superseded）；程序层定期重构（允许作废）；委托层只在真实交付后升级。

### 4.2 业界 memory 方案对照（2026-10 web 核实）

Agent memory 已成独立赛道（约 $31.5M 融资、12 万 GitHub stars 量级的竞争群）[Web]：

| 方案 | 路线 | 对 PC 构建的启示 |
|---|---|---|
| **Mem0** | LLM-driven CRUD（模型决定记什么/删什么） | 自动化抽取可行，但"删什么"交给模型有中毒风险 [Web] |
| **Letta**（MemGPT 后继） | agent self-edit（agent 自己编辑自己的记忆） | 记忆与 agent 一体的极限形态；个人自持版=自己的 agent 管自己的库 [Web] |
| **Zep** | 时序知识图谱（temporal KG） | L2 事实层的防腐蚀方案：带时间戳的事实演化链 [Web] |
| **memU** | reinforcement counting（强化计数） | 高频引用=高价值信号，可做 PC 的自动加权 [Web] |
| **mcp-memory-service** | 6-phase consolidation pipeline | 记忆需要"消化管道"（不只是存取）：consolidation 是画像构建的关键词 [Web] |
| **AGENTS.md 生态** | lean 文件 + 引用外部文档 | "入口精简、正文外置"是 context 的注意力经济学（2026-02 实践共识）；EverAgent 的根 AGENTS.md→各域 AGENTS.md 正是此结构 [Web] |
| **Anthropic context engineering** | 官方工程方法论（2025-09） | system prompt 要"right altitude"；context 是有限注意力预算下的编译目标 [Web] |

**判断** [推测]：没有一个方案解决 L5（委托层）的自持——它们都假设 memory 服务于某个产品内的 agent。个人 PC 的完整形态 = 自持四层（L1-L4）+ 可迁移的授权策略（L5），这正是 EverAgent 模式与产品模式的第一性差异。

### 4.3 EverAgent 作为 PC 的一号实验场（自指审计）

用 §3 五层审计本仓现状：

- ✅ **L1**：各域 PROFILE.md（画像）+ 根 AGENTS.md 的路由意图
- ✅ **L2**：reports/ 110+ 篇（判断记录）+ wiki concepts/entities（知识单元）+ 证据分级标注（provenance）
- ⚠️ **L3**：wiki/entities 有人物页但稀疏（无协作历史/对人的判断沉淀）
- ✅ **L4**：AGENTS.md/skills/（允许作废，历史上已多次重写——符合高贬值预期）
- ❌ **L5**：无显式组件。**建议**：新建根级 `DELEGATION.md`（或 PROFILE 内章节）——三级授权表（全自动/需确认/不许碰），随每次真实交付更新。这与 Laya 的 act/escalate 头、Town 的谨慎交付同构，且是 EverAgent 目前唯一缺失的层
- 双仓结构（公开仓知识正文+私有仓敏感事实）本身就是**隐私分级的正交设计**：敏感层永远不进 prompt/公开仓 [根 AGENTS.md]

### 4.4 可操作的构建清单（给任何个人的最小起步）

1. **一个 git 仓**（私有）：`profile.md`（L1）+ `decisions/`（L2：每个重要决策一页——背景/选项/判断/结果）+ `people.md`（L3）+ `workflows/`（L4）+ `delegation.md`（L5）
2. **每日 5 分钟**：当日判断与决策记入（OpenClaw daily log 的个人版——机械积累比灵感可靠）
3. **每周 review**：open-questions 式追问（哪些判断被验证/证伪——事实防腐）
4. **每月一次正交审计**：问 §1.3 判别法，删过程性沉没成本，保事实性资产
5. **接入任一 agent 时**：只给投影（最小切片），不给全库——eacli `context get --domain` 的按域取用模式 [本仓实践]

---

## 5. 风险与边界（正交论的失效场景）

1. **Context 腐烂**：过时事实比没有事实更危险（旧偏好主导新决策）。缓解：时间戳+supersession 机制（EverAgent §4.6 待办正好补这个）。
2. **Context 中毒**：错误判断沉淀为"事实"、或被投毒（个人 context 是高价值攻击目标——社会工程学的新前沿 [推测]）。缓解：provenance 强制+人审关键沉淀。
3. **隐私集中化风险**：自持 PC = 把鸡蛋放进一个篮子。缓解：双仓分级（敏感事实物理隔离）+ 本地推理优先（infra 侧已有此原则）。
4. **画像固化风险**：PC 让 agent 越来越"懂你"，也可能把你锁进过去的自己（推荐系统信息茧房的 agent 版；豆包 bad case 的温和形态）。缓解：L1 画像允许显式改写（"我变了"应该是 PC 的一等操作）[推测]。
5. **正交失效场景**：若未来模型进步到**从少量交互即时推断完整画像**（in-context 人格建模），存量 PC 的边际价值会下降——但"验证过的决策历史与委托边界"仍无法即时推断，L2/L5 保值 [推测]。

---

## 🤔 思考与追问

1. **我真正理解了什么？**
   正交论的力量不在于"context 有用"（这是常识），而在于**给个人提供了一个与模型军备竞赛解耦的复利坐标系**：巨头每烧一美元，自持 PC 的持有者就多一分兑现能力。它的正确形态是三段链条（积累→炼化→委托），缺任何一段都会退化为"context 沃土上的荒地"（豆包 bad case）或"有油无炼油厂"（OpenClaw 用户的流水账）。EverAgent 四年实践（不知不觉）走完了前两段，第三段（L5 委托层）是明日的第一优先级。
2. **我还没搞懂什么？**
   - **L5 的自持协议长什么样**：授权表是静态文件还是与 agent 协商的动态契约？Laya 的成本矩阵自动推导（对+1/错-3/升级-0.5→62.5% 阈值）能否推广为个人委托层的标准形式？
   - **跨产品投影的最小充分集**：给 Instinct/Muse/自建 agent 各投一份什么结构的 PC 切片，能在不交出全库的前提下兑现大部分价值？（eacli 按域取用是初步答案，缺"充分性"度量）
   - **画像固化的度量**：PC 主导的 agent 决策与"空白 agent"决策的分叉率多大算茧房？没有这个度量，§5.4 只是担忧不是风险管理。
3. **下一步做什么？**
   - **建 `DELEGATION.md`**（根仓）：三级授权表 v0——本周内可完成的最小 L5 实物（对 EverAgent 全 agent 生效）
   - **PC 投影实验**：拿乱翻书 275 报告 + 本报告做切片，喂给一个新会话 agent 提问，测"最小充分集"的下界
   - **追踪 Letta/mcp-memory-service 的 consolidation 管道设计**——L2 防腐的工程答案可能从那里先出现（挂 open-questions，2027-01 回访）

## 来源
- 用户 2026-10-10 今日思考（原始论点）
- [[2026-09-21_xiaoyuzhou-luanfanshu_personal-agent-wars]]（乱翻书275 转写精读，2026-10-09 本仓产出）[转写]
- [[Laya_System1决策模型_深度解析_20260922]] 及 10-09 续篇；[[research_NandhaKishorM_laya]] [代码][API]
- Web 核实（2026-10-10，eacli web.search/read）：
  - Agent memory 竞争格局：Mem0/Letta/Zep/memU/mcp-memory-service（The State of Agent Memory, 2026-02-26, blog.virenmohindra.me；The 2026 Agent Memory Race, hashnode 2026-05-02）[Web]
  - Anthropic "Effective context engineering for AI agents"（2025-09-29，anthropic.com/engineering）[Web]
  - AGENTS.md 精简+外置实践（paulswithers 2026-02-23）；Context Engineering 四支柱（sourcegraph 2026-05-28）[Web]
  - arxiv "An Open-Source Personal Agent for Every Device You Own"（2026-10，引 Today 9-15 发布）[Web]
  - 产品融资/发布事实：TechCrunch/Fortune/NYT/Reuters（见乱翻书275 报告 §11 档案）[Web]
- EverAgent/eacli 自身实践（本仓文件，自指证据）[本仓]

---
*报告生成时间: 2026-10-10*
*研究方法: 用户论点形式化 → 三条既有研究线证据重组织（乱翻书275/Laya 双报告/产品全景）→ 2 轮 web 核实（memory 赛道/context engineering）→ EverAgent 自指审计 → 五层结构与构建工程输出*
