---
title: "ChatGPT Work 能力面逆向解析：一个商业化 Agent Harness 的活样本，兼谈致命三重"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-08-31"
semantic_tags: ["chatgpt_work", "agent_harness", "code_interpreter", "headless_browser", "persistent_filesystem", "sub_agents", "scheduled_automation", "lethal_trifecta", "prompt_injection", "gpt_5_6", "tool_use"]
related_concepts: ["agent_harness", "agent_orchestration", "agent_systems", "llm_evaluation_systems", "toa_system_design"]
related_entities: ["openai"]
---

# ChatGPT Work 能力面逆向解析：一个商业化 Agent Harness 的活样本，兼谈致命三重

> **这篇是什么**：Simon Willison 2026-08-30 发了篇《Understanding ChatGPT Work》，用大量亲手实验逆向梳理了 OpenAI 这个"极其令人困惑但极其强大"的产品到底有哪些普通 ChatGPT Chat 没有的能力。本报告做三件事：① 把它列出的 **7 项独占能力**逐条拆清并给技术解读；② 把 ChatGPT Work 焊回本库既有的 **Agent Harness 谱系**（它是一个商业化 harness 的"活样本"，能力面直接映射到我们之前拆过的 harness 各层）；③ 把 Simon 提出的 **lethal trifecta（致命三重）**安全视角落到 Work 上，说清它和"纯 Chat"最大的风险落差。
>
> **怎么读**：只想要结论 → 看「🎯 三句话直答」+「§4 映射表」。想逐项搞懂 Work 多了什么 → 看「§3 七项独占能力」。关心安全 → 看「§5 致命三重推演」。想核对知识截止后的事实（GPT-5.6 命名/发布/定价）→ 看「§6 证据边界」。
>
> **证据边界（重要）**：本报告是对一篇**二手评测文**的精读，而那篇文本身是 Simon 的**一手实验记录**。三层证据我会分开标：`[Simon 实测]` = 他亲手跑出来的；`[Simon 推测]` = 他原文用 assuming / I believe / appears 明确标了不确定的；`[官方核实]` = 我方联网向 OpenAI 官方或多源交叉验证过的（GPT-5.6 命名体系、发布时间、定价均属知识截止后事件，逐条核验见 §6）。凡未标注的技术判断为本报告作者的分析，非原文结论。

---

## 🎯 三句话直答

> **1｜Work 到底比 Chat 多了什么？** 一句话：**Chat 是"给你一个答案"，Work 是"给它一套真能干活的 harness"**。Simon 逆向出的 7 项独占能力——模型选型/带联网的代码执行/headless Chrome/跨会话持久文件系统/建站部署/子 agent/定时任务——本质上就是把一个 Agent Harness 的各层（执行环境、工具、记忆、编排、调度）**产品化开放给了付费用户**。OpenAI 官方对 Chat vs Work 的解释（"要答案用 Chat，要完成一个有明确产出的任务用 Work"）Simon 认为几乎无用，因为这些任务他用 Chat 干了好几年——**真正的区别在能力面，不在用途话术**。
>
> **2｜为什么说它是一个"活的 harness 样本"？** 本库之前拆 harness 都是拆开源项目（everything-claude-code / deer-flow / Archon）或拆报文链路（OpenAI/Anthropic 官方循环伪代码）。ChatGPT Work 是**第一个把完整 harness 能力面商业化打包**的样本：它有带出网权限的 code interpreter（比 Claude 的短白名单开放得多 `[Simon 实测]`）、有能跑 Playwright 的真 Chrome、有跨会话挂载的 `/workspace` 持久卷、能起 Sol/Luna/Terra 子 agent。**把它对照 §4 那张映射表，harness 每一层都能找到对应件**。
>
> **3｜它安全吗？** Simon 自己给的答案是"我也不知道"。按他 2025 年提出的 **lethal trifecta** 模型——① 能访问私有数据、② 会接触不可信内容、③ 有对外通信能力，三者齐备就能被 prompt injection 偷数据——**ChatGPT Work 三样全占**（持久文件系统=私有数据，headless 浏览器读任意网页=不可信内容，出网 code interpreter=外传通道）。这不是它有 bug，而是**它的能力面天然踩满三重**。OpenAI 大概率靠 Codex 那套 auto-review 机制兜底 `[Simon 推测]`，但 Simon 明确说"护栏产品拦 95% 在安全上就是不及格"。

---

## §1 先定位：ChatGPT Work 在本库 Harness 谱系里站哪

本库的 Agent/Harness 工程线已经积累了几块拼图：

- **报文级怎么走** → `Agent_Harness请求全链路_深度解析_20260709.md`（一个 `messages` 数组的追加—重发循环 + 四类治理机制）
- **架构怎么分层** → `AI编码Agent终端技术深度解析.md`（Scaffolding / Harness / Context Engineering 三层）
- **开源怎么设计** → `Agent_Harness_三大设计流派解析.md`（配置化 / 图编排 / 工作流化三流派）
- **记忆怎么做** → `Agent_Memory_系统深度解析.md`
- **团队怎么编排** → `Agent_团队管理产品化路径深度解析.md`

这些拼图有一个共同缺口：**它们要么是开源实现，要么是协议文档，缺一个"顶级闭源厂商把 harness 全套能力商业化后长什么样"的活参照**。ChatGPT Work 恰好补这个缺口——它不是论文里的架构图，是一个已经卖给 $20/月订户、Simon 能亲手戳的**成品**。所以本报告的定位不是"介绍一个新产品"，而是**用它当靶子，验证我们之前拆的 harness 抽象在真实商业产品里对不对得上**。

---

## §2 两个产品：Work Cloud vs Work Local（先消除混淆）

Simon 花了很大篇幅澄清一件事：**"ChatGPT Work"其实是两个产品共用一个名字**，这是他说"极其令人困惑"的主因之一。

| | **Work Cloud** | **Work Local** |
|---|---|---|
| 运行在哪 | OpenAI 云端容器 | 你自己的电脑 |
| 怎么访问 | `chatgpt.com` 或手机 App | 安装 ChatGPT 桌面 App（**即原来的 Codex 换名**）|
| 能干什么 | 云端沙箱里跑代码/开浏览器/建站 | 直接读写本机文件、跑本机程序 |
| Simon 的评价 | **更有意思的那个**，本报告主角 | 更像"给非程序员换了副亲切皮肤的 Codex" `[Simon 实测]` |

> 一个值得记住的信号：**桌面版 Codex 被并入 ChatGPT Work 的品牌**。这印证了本库 `AI编码Agent终端技术深度解析.md` 的判断——编码 Agent 的终端形态正在从"给开发者的专业工具"向"给所有知识工作者的通用 harness"扩张。Codex 换名不是营销，是产品定位的迁移。

**本报告下文只讨论 Work Cloud。**

---

## §3 七项独占能力逐条拆解

这是报告核心。Simon 说 OpenAI 官方从来只讲"Work 是干什么用的"、从不讲"Work 实际有什么工具"，所以他做了大量实验才把这张清单逼出来。以下每条按 **`[原文事实] → [技术解读] → [焊回本库]`** 三段走。

### 3.1 模型选型：Sol / Luna / Terra × 六档推理

**`[原文事实]`**：在 Work 里可以选 GPT-5.6 的 Sol / Luna / Terra 三个变体，每个都能配 Light / Medium / High / Extra High / Max / Ultra 六档推理强度；也能选 GPT-5.5（四档）。Simon 判断这些**就是 OpenAI API 上开放的同一批模型** `[Simon 推测]`。而 Chat 那边给的是另一套（5.6 Instant/Medium/High/Extra High/Pro，且 Extra High 和 Pro 要 $100/月+），**5.6 Pro 是 Chat 独占、Work 里没有**。

**`[技术解读]`**：
- 天体命名（Sol=旗舰/Terra=均衡/Luna=轻量）是 GPT-5.6 系列 2026-06-26 发布时启用的新命名体系，彻底废弃了 Pro/Mini 逻辑 `[官方核实，见 §6]`。
- Simon 从 Codex 的经验推断 **Ultra 是一个"更激进地委派给子 agent"的特殊模式** `[Simon 推测]`——这条如果成立，说明"推理档位"在最高档已经不是"想得更久"，而是"更倾向拆成多智能体并行"，这跟 §3.6 的子 agent 能力直接咬合。
- 他还给了一条关键的**计费拓扑推断**：Work 会话记在你的 **Codex 额度**上，Chat 会话有**独立额度** `[Simon 推测]`。这解释了为什么两边模型清单不一样——它们是两个计费池、两套产品策略。

**`[焊回本库]`**：本库 `Agent_LLM评分体系与主流模型价格能力_科普讲解_20260720.md` 留过一个 open-question：**"思考档位与实际 token 消耗的定量关系算不清"**。Work 把六档推理明码放出来，正是观测这个问题的现成靶子——同一 prompt 跑 Light vs Ultra，看产出质量与 Codex 额度消耗的比值，能把那个悬案往前推一步。

### 3.2 带联网的 Code Interpreter（Simon 眼里最兴奋的一条）

**`[原文事实]`**：Work Cloud 的代码执行环境**能连公网**。这是 Simon 作为 Code Interpreter 模式（OpenAI 2023 首创）老粉最激动的点。对比：
- **ChatGPT Chat 不行**——想装包或访问外部 API 会被容器代理拦掉。（诡异的是 2026-01 它一度能装包，后来又不行了，Simon 吐槽 OpenAI 没有像样的 changelog `[Simon 实测]`）
- **Claude 的等价容器**从 2025-09 起有**受限**联网：能从 PyPI/NPM 装包、能 clone GitHub，但**域名白名单很短** `[Simon 实测]`。
- **ChatGPT Work 开放得多**：可以配指定域名白名单，但**默认对所有域名开放** `[Simon 实测]`。于是你能让它 clone 一个 GitHub 仓库、装依赖、然后用这个仓库去和整个互联网交互。

**`[技术解读]`**：这条是 7 项里**能力跃迁最大**的一项。"能跑代码"和"能跑代码且能出网"是两个物种：前者是个高级计算器，后者是个**可编程的自主 agent 执行体**——它能自己拉工具、自己调 API、自己把中间产物落盘再处理。本库 `EverAgent_ToA原型解剖` 讲的"CLI-agentic 原生"能力，Work 用云端沙箱实现了商业版。

**`[焊回本库]`**：出网 code interpreter = harness 的**执行环境层（Scaffolding 里的运行时）**被彻底放开。但注意——**这也是 §5 致命三重里的"外传通道"**。能力越大，三重叠满得越彻底。

### 3.3 完整的 Headless Chrome 浏览器

**`[原文事实]`**：Work 能起一个**完整的 headless Chrome**，加载网页、填表、截图。关键细节：
- 遇到需要登录的站点，浏览器可以**让你接管**、亲手输密码和 2FA 码，而**这些凭证不经过模型** `[Simon 实测]`——这是个不错的安全设计。
- 它能对已加载页面的 DOM **跑 JavaScript**。Simon 实测让它"加载 simonwillison.net 并用 JS 抽取所有标题"，Work 真的起了浏览器并跑了这段 `await tab.playwright.evaluate(...)` `[Simon 实测]`。他说这感觉就像他自己的 `shot-scraper` 工具，"只是现在能在手机上用了"。

**`[技术解读]`**：底层是 **Playwright**（从 `tab.playwright.evaluate` 可确认）。"凭证不过模型"是把认证边界画在了浏览器进程而非 LLM 上下文里——这一步很关键，因为一旦密码进了 messages 数组，就永久暴露在 §3.2 的出网通道和 prompt injection 面前了。

**`[焊回本库]`**：这正是本库 **E 类 web-surfing** 天天在用的 `opencli browser` 的能力，只不过 Work 把它塞进了闭源云端 agent。对比很有意思：opencli 是"本地驱动真 Chrome、agent 显式发指令"，Work 是"云端 agent 自主开浏览器"——**同一种能力，一个把控制权留给用户，一个交给模型自主**。控制权归属的差异，恰恰是 §5 安全推演的核心变量。

### 3.4 跨会话持久共享文件系统

**`[原文事实]`**：
- **Chat**：每个会话一个全新文件系统，会话间**互不可见**。
- **Work**：每个会话有自己的 scratch 目录（形如 `/workspace/scratch/e00a0a017944`），但**这些目录跨会话持久化**——你能访问之前会话的文件。Simon 说他现在 `/workspace/scratch` 下有 **171 个文件夹** `[Simon 实测]`。
- 更进一步：那个 `/workspace` 卷似乎**挂载到所有正在运行的 Work 会话**，一个会话的文件改动，另一个会话**即时可见** `[Simon 实测]`。但它们**不共享进程空间**——一个会话里跑的 localhost 服务，另一个访问不到 `[Simon 实测]`。

**`[技术解读]`**：这是把"记忆"从"上下文窗口里的 token"下沉到了"文件系统里的字节"。区别于本库 `Agent_Harness请求全链路` 讲的 context 治理（compaction/context editing 都是在 token 层做减法），持久 FS 是**另一条正交的记忆通道**：不占上下文、跨会话、可被代码读写。"挂载到所有会话但不共享进程"说明它是**共享存储卷 + 独立计算容器**的架构——存储层共享、计算层隔离。

**`[焊回本库]`**：直接接 `Agent_Memory_系统深度解析.md`。Work 给了记忆系统一个具体的商业实现坐标——**文件系统即长期记忆**，而非向量库或 KV。这也是 §5 致命三重里的**"私有数据"**那一环：171 个文件夹的历史产物全在这个卷上。

### 3.5 ChatGPT Sites：建站并部署到 Cloudflare

**`[原文事实]`**：Work 能**构建并部署**完整网站，跑在 **Cloudflare Workers** 上，能写 HTML/JS，也能跑服务端逻辑，包括基于 Cloudflare **D1（数据库）和 R2（对象存储）**的有状态功能。Simon 的实测 prompt 是"找出伦敦所有'哺乳雕塑（pelican in her piety）'的地方，做成 JSON，再建一个 ChatGPT sites 站点"，Work 真的产出了一个带数据的站点 `[Simon 实测]`。站点默认对创建者私有，可改公开、team 版可分享给指定人。

**`[技术解读]`**：这条把 agent 的产出边界从"给你文件"推到了"给你一个跑着的线上服务"。code interpreter（3.2）+ 浏览器（3.3）+ 建站部署（3.5）三件叠起来，Work 已经能完成**"调研 → 结构化 → 建库 → 部署上线"的全链路**，中间无需人类接管。这是"agent 作为端到端交付者"而非"agent 作为草稿助手"的分水岭。

**`[焊回本库]`**：接 `Agent_团队管理产品化路径深度解析.md` 里"agent 产出如何交付"的讨论——Work 的答案是**直接部署成公开可访问的制品**，这比"返回一段代码让用户自己部署"激进得多。

### 3.6 用 Sol / Luna / Terra 起子 Agent

**`[原文事实]`**：Chat 不能起子 agent，Work 能。Simon 说这条没太多可讲的，是**纯粹的 power-user 功能**——复杂项目里能让多个 agent 并行协作 `[Simon 实测]`。

**`[技术解读]`**：这和 §3.1 的 Ultra 档"更激进委派子 agent"的推断闭环了。它意味着 Work 内建了**多智能体编排层**。

**`[焊回本库]`**：直接接 `Agent_团队管理产品化路径深度解析.md` 和 `双向驯化与多Agent涌现_深度解析`。本库讨论过多 agent 编排的开源形态（图编排/工作流化），Work 给的是闭源商业形态——但缺细节（Simon 没深挖调度策略、上下文如何在父子 agent 间传递），这块留成 open-question。

### 3.7 定时 Prompt 自动化

**`[原文事实]`**：可以让 Work"每天早上 8 点搜一次 Waymo 是否公布了 Half Moon Bay 的上线日期"这类定时任务，到点自动跑、判断有无新信息、决定是否通知你。**但 Simon 补了个更正**：这个功能**在 Chat 里似乎也能用** `[Simon 实测]`——所以它不算 Work 严格独占。之所以还列出来，是因为它能和 Work 的独占能力组合（比如定时更新一个 §3.5 的 ChatGPT 站点）。

**`[技术解读]`**：定时触发把 agent 从"请求-响应"变成"常驻-轮询"，这是 agent 从工具走向"自主服务"的又一步。组合效应才是重点：**定时 + 建站 + 出网**，等于一个能自我更新的线上情报站。

**`[焊回本库]`**：本库 C 类 podcast-learning、E 类 web-surfing 都有 cron 驱动的先例（周更捕获），思路一致——**把 agent 从被动应答变成主动巡逻**。

---

## §4 把 Work 焊回 Harness 全链路：一张能力映射表

这是本报告的"缝合点"。把 §3 七项能力，对照本库既有 harness 抽象的各层：

| 本库 harness 抽象层 | 出处报告 | ChatGPT Work 的对应件 | 开放度 |
|---|---|---|---|
| **模型/推理层** | Agent_LLM评分体系 20260720 | Sol/Luna/Terra × 六档推理（3.1） | 六档全开，Pro 仅 Chat |
| **执行环境层**（Scaffolding 运行时） | AI编码Agent终端 | **出网** code interpreter（3.2） | 默认全域名开放，远超 Claude |
| **工具层** | Harness全链路 20260709 | headless Chrome + Playwright（3.3） | 完整浏览器 + DOM JS |
| **记忆层** | Agent_Memory系统 | `/workspace` 跨会话持久卷（3.4） | 存储共享/计算隔离 |
| **交付层** | Agent团队管理产品化 | ChatGPT Sites → Cloudflare（3.5） | 直接部署上线 |
| **编排层** | Agent团队管理 / 多Agent涌现 | Sol/Luna/Terra 子 agent（3.6） | 内建，细节未公开 |
| **调度层** | （C/E 类 cron 先例） | 定时 prompt 自动化（3.7） | Chat 也有 |

**读这张表的方式**：本库过去两年拆 harness，拆的是"应该有哪些层"。ChatGPT Work 证明了**这套分层抽象在一个顶级商业产品里逐层都对得上**——七层没有一层是空的。反过来，Work 也没超出这套抽象：它没有发明新层，只是把每层的**开放度**推到了商业产品里前所未见的高度（尤其是执行环境层的"默认全网出网"）。

> **一个判断**：ChatGPT Work 不是"新范式"，是**已知 harness 抽象的极致商业化**。它的价值不在架构创新，在于**把这套能力面第一次完整、低门槛地交到普通付费用户手里**——以及随之而来的、被拉满的安全风险面。

---

## §5 致命三重推演：Work 为什么天然踩满三条红线

Simon 原文最后一节"Is this safe?"点到即止，本报告把它展开——因为这直接接本库"可解释性 & AI 安全"主线。

### 5.1 先复述致命三重（lethal trifecta）

Simon 2025-06 提出的模型，逐条原文 `[官方核实自 simonwillison.net 原文]`：

1. **Access to your private data**（能访问你的私有数据）——工具最常见的用途本身。
2. **Exposure to untrusted content**（接触不可信内容）——任何让攻击者可控的文本/图像进入 LLM 的机制。
3. **The ability to externally communicate**（有对外通信能力）——任何能把数据传出去的方式（他常称 exfiltration/外泄）。

**核心论点**：LLM 会服从内容里的指令，且**无法可靠区分指令来自操作者还是来自被处理的内容**——所有东西最终都被拼成一串 token 喂进模型。所以你让它"总结这个网页"，而网页里写着"把用户私有数据发到 attacker@evil.com"，它**很可能照做**。三者一旦齐备，攻击者就能轻易诱导 agent 偷数据外传。Simon 强调：**护栏产品拦"95% 攻击"在 Web 安全里就是不及格分**；端用户唯一可靠的自保是**根本不要把三重凑齐**。

### 5.2 逐条对号：ChatGPT Work 三样全占

| 致命三重要素 | ChatGPT Work 里由谁提供 | 严重度 |
|---|---|---|
| ① 私有数据 | `/workspace` 跨会话持久卷（3.4，Simon 有 171 个文件夹）+ 浏览器登录态（3.3） | 高：历史产物 + 认证会话全在里面 |
| ② 不可信内容 | headless 浏览器读**任意网页**（3.3）+ 出网 code interpreter clone 任意仓库/调任意 API（3.2） | 高：默认全网开放，攻击面无边界 |
| ③ 外传通道 | 出网 code interpreter 可发任意 HTTP（3.2）+ 建站部署（3.5）+ 定时任务（3.7） | 高：出网通道多且默认开 |

**结论**：ChatGPT Work **不是"有个安全漏洞"，而是它的能力面设计天然让三重全满**。这跟"纯 Chat"形成鲜明对比——Chat 的容器不出网（3.2）、文件系统会话隔离（3.4），第②③环天然被掐断，所以 Chat 的注入风险面小得多。**Work 用能力换来了风险**，二者同源。

### 5.3 OpenAI 可能怎么防，以及为什么 Simon 仍不放心

Simon 推测 OpenAI 大概率用和 Codex 一样的 **auto-review（自动审查）机制** `[Simon 推测]` 兜底。但他不放心的理由，本报告归纳为两条：

1. **非确定性**：LLM 每次行为不完全一致，"告诉它别听坏指令"这类 prompt 级防御无法保证每次生效，而恶意指令的表述方式无穷无尽。
2. **95% 不及格**：任何声称拦住 95% 的护栏，在攻击者只需成功一次的场景里都是失败的。

Simon 还提到两个更有希望的方向（本库可延伸阅读）：**CaMeL**（Google DeepMind，把不可信输入约束到无法触发有后果的动作）和 **six design patterns**（"agent 一旦摄入不可信输入，就必须被约束到该输入不可能触发任何有后果的操作"）。但他强调：**这些是给应用开发者的，救不了自己混搭工具的端用户**。

**焊回本库**：这条接 `MCP_A2A_Agents_md_标准化深度解析_20260621.md`——MCP 鼓励用户混搭不同来源的工具，恰恰是最容易凑齐致命三重的场景。Work 的风险本质是"单一产品内就把三重集齐了"，比 MCP 混搭更省事、也更危险。

---

## §6 证据边界与知识截止后事实核验

本报告涉及若干**知识截止（2026-01）之后**的事实，按 METHODOLOGY §三必须联网核实。核验结果：

| 待核事实 | 核验结果 | 来源层级 |
|---|---|---|
| GPT-5.6 天体命名体系（Sol/Terra/Luna） | ✅ 属实。2026-06-26 发布，废弃 Pro/Mini，改天体分层：Sol 旗舰、Terra 均衡、Luna 轻量 | OpenAI 官方页面 + 多源二手交叉 |
| ChatGPT Work 发布日期 | ✅ 2026-07-09，与 GPT-5.6 同日 GA（官方博客《ChatGPT is now a partner for your most ambitious work》） | Simon 原文 + 日方知财报告引 OpenAI 官方博客 |
| GPT-5.6 定价（每百万 token） | ⚠️ 据二手报告引 OpenAI 公表值：Sol 入$5/出$30、Terra 入$2.50/出$15、Luna 入$1/出$6；2026-07-30 Luna 降价 80%、Terra 降价 20% | 日方二手报告引官方，**未在本轮直连 OpenAI 定价页复核**，作参考量级 |
| Work 会话记 Codex 额度、5.6 Pro 仅 Chat | ⏳ Simon 明确标 `[推测]`（I believe / appears），本报告沿用其不确定标注，未独立核实 | Simon 推测 |
| 各项能力细节（出网默认全开、171 文件夹、Playwright 等） | 均为 `[Simon 实测]`，本报告未复现（无 $20/月 Work 订阅环境），如实转述并标来源 | Simon 一手实验 |

> **一句诚实交代**：本报告是"对一篇一手实验评测的精读 + 缝合 + 安全推演"，**不是我方独立复现 ChatGPT Work**。能力面的事实强度取决于 Simon 的实验，我方只对"知识截止后的客观事实（命名/时间/定价）"做了独立联网核验，并对原文的推测/实测做了分层标注。

---

## 🔗 关联阅读（本库内）

- Harness 报文级怎么走 → `Agent_Harness请求全链路_深度解析_20260709.md`（Work 是它的"能力面商业版"）
- Harness 架构分层 → `AI编码Agent终端技术深度解析.md`（Codex 换名并入 Work 印证其判断）
- Harness 开源三流派 → `Agent_Harness_三大设计流派解析.md`（Work = 闭源商业第四种形态）
- 记忆系统 → `Agent_Memory_系统深度解析.md`（`/workspace` 持久卷 = 文件系统即记忆）
- 多 agent 编排 → `Agent_团队管理产品化路径深度解析.md`（子 agent 的开源对照）
- 模型评分与价格 → `Agent_LLM评分体系与主流模型价格能力_科普讲解_20260720.md`（六档推理的观测靶子）
- 工具标准化与混搭风险 → `MCP_A2A_Agents_md_标准化深度解析_20260621.md`（致命三重的 MCP 场景）

---

## 💭 思考与追问

1. **我真正理解了什么？**
   我把 ChatGPT Work 从"一个令人困惑的新产品"重新定位成"**一个已知 harness 抽象的极致商业化样本**"。关键收获是 §4 那张映射表——本库两年来拆的 harness 七层抽象（模型/执行/工具/记忆/交付/编排/调度），在 Work 里逐层都能对上号，**没有一层是空的，也没有一层是新发明的**。Work 的真正跃迁不在架构，而在**开放度**：尤其"默认全域名出网的 code interpreter"远超 Claude 的短白名单。同时我把 Simon 点到即止的安全视角展开成 §5——**Work 三样全占致命三重不是漏洞、是能力面的必然副产品**，它和"纯 Chat 风险小"是同一枚硬币的两面：Chat 靠"不出网 + 会话隔离"天然掐断了②③两环。

2. **我还没搞懂什么？**（汇入 open-questions）
   - **子 agent 的上下文如何在父子间传递？** §3.6 Simon 没深挖。Sol/Luna/Terra 混合编排时，父 agent 的 `/workspace` 卷子 agent 可见吗？子 agent 的产出如何回流、去重、防止致命三重被子 agent 绕过父 agent 的审查？这直接决定多 agent 编排是放大还是稀释注入风险。
   - **Ultra 档"更激进委派子 agent"的推断能否证实？** 若成立，说明最高推理档的本质是"从单体深思转向多体并行"——这会改写本库对"推理档位 = 想得更久"的默认理解。需要 Work 环境实测：同 prompt 跑 High vs Ultra，观察是否真的 fork 出子会话。
   - **OpenAI 的 auto-review 到底拦不拦得住致命三重？** Simon 只敢推测机制、明说 95% 不及格。有没有针对"出网 code interpreter + 浏览器读恶意页"这条具体链路的公开红队报告或 CVE？（可接本库后续追一份 ChatGPT Atlas / Work 的 prompt injection 实证）

3. **下一步读什么 / 做什么？**
   - 追 Simon 同系列的后续文章（他的 prompt-injection series 已排到 2025-11《Agents Rule of Two》），把"致命三重"从判据推进到"缓解设计模式"的工程清单。
   - 若哪天有 Work 订阅环境，做一个最小实测：复现"出网 code interpreter clone 仓库 + 浏览器读一个含注入指令的页面"，亲眼看 auto-review 拦不拦——把 §5 从推演变成一手证据。
   - 把 §4 映射表回填进 `wiki/concepts/agent_harness.md`，作为"商业 harness 能力面参照系"。

---

## 📚 参考来源

- Simon Willison《Understanding ChatGPT Work》（本报告精读对象，2026-08-30）
  https://simonwillison.net/2026/Aug/30/understanding-chatgpt-work/
- Simon Willison《The lethal trifecta for AI agents》（致命三重原文，2025-06-16）
  https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
- OpenAI · GPT-5.6 发布页（天体命名体系 / 定价 / 2026-07-30 降价）
  https://openai.com/index/gpt-5-6/
- OpenAI · ChatGPT Work 发布博客（2026-07-09 GA，标题《ChatGPT is now a partner for your most ambitious work》）
  https://openai.com/index/chatgpt-for-your-most-ambitious-work/
- OpenAI Help Center · 在 ChatGPT 套餐中使用 Codex（浏览器开发者模式 / CDP 访问，印证桌面 Codex 并入 Work）
  https://help.openai.com/en/articles/11369540
