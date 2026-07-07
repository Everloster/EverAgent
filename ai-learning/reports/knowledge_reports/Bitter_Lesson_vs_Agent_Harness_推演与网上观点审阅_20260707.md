---
title: "Bitter Lesson 会杀死 Agent Harness 吗？——一场推演与网上观点交叉审阅"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-07-07"
semantic_tags: ["bitter_lesson", "agent_harness", "scaffolding", "context_engineering", "self_evolving_agent", "prompt_engineering", "compute_allocation"]
related_concepts: ["agent_harness", "test_time_compute", "self_improvement", "in_context_learning", "agent_orchestration"]
related_entities: ["anthropic", "deepseek", "posthog", "tavily"]
---

# Bitter Lesson 会杀死 Agent Harness 吗？

> **这篇是什么**：一场"讨论型"报告，不是精读某一篇论文，而是把本库两篇报告（**22 Bitter Lesson** × **46 进化 Harness**）碰撞出的一个尖锐问题——
> **"当模型越来越强，我们手搭的 harness 会不会像 SIFT 特征一样被 Bitter Lesson 的镰刀彻底淘汰？"**——推演到底，并**交叉审阅网上已有的观点**看我的推演站不站得住。
>
> **怎么读**：只想要结论 → 看「🎯 一句话」+「⚔️ 两把镰刀」+「🔪 生死表」。想看我 vs 网上的分歧 → 看「🌐 网上观点交叉审阅」。想要可证伪的预测 → 看「🔮 可证伪信号」。
>
> **一手/二手边界**：Sutton 原文引句我从 Miessler 转引处核对（他贴了 incompleteideas.net 原文原句）；网上观点均标注作者与链接；本库 22/46 的数字是此前已核验的一手数据。**标 `[网络观点]` 的是他人主张，非定论。**

---

## 🎯 一句话总结

> **Bitter Lesson 没失效，它只是把战场搬到了 harness 内部重新分了一次生死。** 手工编码"该怎么做题"的那部分（提示词 playbook、固定编排、专职子代理）会被模型 scaling 碾掉；而"搜索过程本身"（进化循环）和"高风险场景的确定性保证"（校验闸门）躲得过镰刀。**而且——"进化 harness"这个动作本身就是 Search，是 Bitter Lesson 亲自钦点的两大永动方法之一。它不是反例，是 Bitter Lesson 在 2026 年新长出来的一只手。**

---

## 🧩 问题从哪来：两篇报告的正面对撞

| | 报告 22 · Bitter Lesson (Sutton 2019) | 报告 46 · 进化 Harness (Niklaus 2026) |
|---|---|---|
| 核心主张 | 通用方法 + 算力**长期必胜**；编码人类知识短期有效、长期必败 | **冻结模型**、只进化外层 harness，就把法律基准 63.4%→80.1% |
| 最刺眼的点 | "手工特征（SIFT）终将被淘汰" | "最大单点收益是**手写的确定性代码**（landing_gate），零算力" |
| 表面矛盾 | 人类工程终将被算力碾压 | 人类工程（harness）恰恰是被低估的杠杆 |

**撞点**：如果 Sutton 对，Niklaus 报告里那些手搭 harness 是不是只是"algorithm still too expensive"时代的临时产物，等模型一强就该进垃圾桶？

---

## ⚔️ 关键发现：其实有两把镰刀，不是一把

推演到一半我意识到，"harness 会不会死"被大多数人低估成了**单变量**问题。实际上有**两个独立的解构力**同时在削 harness：

### 镰刀一 · 模型 scaling（经典 Bitter Lesson）
吸收掉"知识/管理"型 harness。**这里有个定时炸弹**：Niklaus 的"被管理糟糕的天才假说"里，harness 填的**正是模型当前的"自我管理赤字"**。而 agentic RL / computer-use 训练**干的就是把这个赤字训掉**。所以提示词/管理层的寿命，被 agentic RL 的进度**直接倒计时**。

### 镰刀二 · 环境适配（生态迁移）
MCP、agent-native API、模型友好的工具正在铺开。这会**从另一头**溶解"胶水/接口"型 harness——不是模型变聪明了，而是**世界主动改成了模型好用的样子**。

> **两把镰刀都躲过的，只剩两样**：**进化搜索这个过程**（Sutton 祝福），和**高风险场景的硬保证确定性**（需求类型豁免，见下）。

---

## 🔪 生死表：拿"检验句"逐层过 harness

**唯一的检验句**（从 Sutton 纲领提炼）：

> 这个组件是在编码"人类觉得该怎么做题"（→ **会被砍**），还是在提供"模型无论多聪明都绕不开的接口/底座/保证"（→ **砍不到**）？

| Harness 组件 | 是"知识"还是"底座" | 判词 | 依据（含一手信号） |
|---|---|---|---|
| **提示词 playbook** | 纯知识编码 | **☠️ 几乎必死** | 46 一手已证：换模型家族**失效甚至倒扣分**——SIFT 式不泛化 |
| **手工任务分解 / 固定 DAG** | 知识（人替模型想步骤） | **☠️ 慢性死亡** | 网上多篇实证：PostHog/Tavily 都推翻了图编排 [网络观点] |
| **专职子代理固定分工** | 进口人类组织的限制 | **☠️ 高危** | "把认知有限、沟通成本高的人类约束凍进架构" [网络观点] |
| **确定性校验/兜底闸门** | **环境契约**，非解题知识 | **🛡️ 活最久，但性质变** | 见下"最锋利一点" |
| **工具/环境接口** | 底座（模型变不出法律数据库） | ⚖️ 接口存在=底座（活）；选哪个/怎么编排=知识（死） | — |
| **上下文/记忆/检索** | 混合 | 手调 chunking 死、学习式检索活 | 22 已判 RAG 为"搜索+学习组合" |
| **进化循环本身** | **就是 Search** | **✅ 零风险，越砍越强** | Sutton 两大永动方法之一 |

### 🔪 最锋利的一点：`landing_gate` 这种确定性代码会不会死？

表面看：模型一强，自己会放对文件，这段代码就该像 SIFT 一样被淘汰。但这里有条**镰刀砍不动的裂缝**：

> **确定性代码给的是"保证"（0% 失败），聪明模型给的是"概率"（99.9%）。在高风险场景，保证的价值是概率永远替代不了的。**

法律、金融、幂等写操作、安全网关——要的不是"几乎不出错的天才"，而是"结构上不可能出错的闸门"。所以这层**可能不是因为"模型学不会"而活，而是因为"确定性本身是产品需求"**。它逃过镰刀，靠的不是能力缺口，而是**需求类型**——**镰刀只砍"能力缺口填补物"，砍不到"保证型需求"。**

这正好接上报告 22 Step 6 自己记的局限："搜索空间的设计仍需人类智慧，Transformer 本身就是人设计的通用方法"——总有一层薄薄的人造底座砍不到底。

---

## 🌐 网上观点交叉审阅（看我的推演站不站得住）

搜完发现：**这个问题在 2026 年上半年已是热议话题**，而且业界结论与我的推演**高度收敛**——但也有几处比我更激进/更细，值得吸收。

### 观点 A · Minh Pham《Why Most Agent Harnesses Are Not Bitter Lesson Pilled》 [网络观点]
（经 aihao.tw 中文转述 + 原 X 长文）
- **三个反模式**：**工作流陷阱**（拖拉式建构器把任务分解假设硬编码）、**专职子代理幻觉**（进口人类组织限制）、**For-Loop 天花板**（唯一扩展旋钮是迭代次数，一维扩展）。
- **判断准则（金句）**：*"如果模型能力明年翻倍，你的系统会不会在不需要大幅重构的情况下，变得显著更简单、更便宜、或更可靠？"* 是 → 你站在 Bitter Lesson 这边。
- **正解方向**：动态子代理生成 + 递归语言模型（RLM）——**"把额外算力转化为更好决策，而不依赖固定的人类设计分解"**。
- **收束句**：*"结构不应从设计中强加，而应从学习中浮现。Agent 框架应该是通往可规模化运算的**薄薄介面**，而不是你把智慧藏进去的地方。"*
- **⟶ 与我推演的关系**：**强烈印证"镰刀一"**。他的"薄介面 vs 藏智慧"正是我"底座（活）vs 知识（死）"的另一种说法。他比我更强调"For-Loop 天花板"——这点补充了我：连"LLM+loop+tools"这种极简 harness，如果唯一旋钮是迭代次数，也不够 Bitter-Lesson-pilled。

### 观点 B · blog.exe.dev / ClawdBytes《Prompt Engineering Is Dead》 [网络观点]
- 原话：*"The bitter lesson has finally come for the harnesses."* — 明确宣告镰刀已到 harness。
- 论据：作者的 CLAUDE.md **只剩三行**（一条硬规则 never git push、一条操作偏好、一条元指令），其余全靠信任。金句 *"Goals are durable, orders are brittle."*
- **但它自己暴露了残余**：那三行里"never git push"是什么？**正是一条确定性硬约束（安全闸门）。**
- **⟶ 与我推演的关系**：**双重印证**。既证"提示词 playbook 必死"（500 行系统提示变噪音），又**反手印证我的"确定性保证活最久"**——它砍到只剩三行，但**砍不掉那条 never-push 硬规则**。这几乎是我"需求类型豁免"的活体标本。

### 观点 C · Daniel Miessler《Bitter Lesson Engineering (BLE)》 [网络观点]
- 造词 **BLE-hobbled**：*"a system where the scaffolding has aged to the point of making your overall system worse instead of better"*——脚手架老化到反而拖累系统。
- 核心规则：***"Don't confuse the 'what' with the 'how'."*** 对 what 极度具体，把 how 交给最强的模型 + 最好的工具。
- **⟶ 与我推演的关系**：给了我一个**更好的分类维度**。我原来按"知识 vs 底座"分，他按"what vs how"分——**"how"型脚手架（执行步骤）会 BLE-hobbled；"what"型（目标/偏好/工具）不会。** 这与我的表基本同构（how≈知识、what≈底座+需求），但"scaffolding 变成 about preferences than execution"这个表述更精炼，我采纳进结论。

### 观点 D · DevDash / PostHog / Tavily 的**生产实战**（最硬的一手工业证据）[网络观点]
一年生产 agent 的复盘，全是可验证的工程事实：
- **PostHog**："Model improvements change more than you think." 图编排（GPT-4o 时代必需）→ 今天单 LLM loop 反而更可靠；**"agents beat workflows"**。曾经加编排图是为了补可靠性，"the architecture that was supposed to add reliability actually reduced it"。
- **Tavily**：七个月后**整个推翻**第一版 deep research 架构——"sophisticated and clever，they thought that was a good thing，但下一代模型来了假设就变瓶颈"。用**上下文蒸馏**（每步压成 2-3 句反思）把 token 砍 66% 且刷到 SOTA。
- **结构化输出**：为老模型写的 retry/fallback parser，新模型一来就成"dead weight"——教科书级 Bitter Lesson。
- **但他们保留了什么？** `todo_write` 工具（极简、自我强化）、trace 监控（"Traces Hour" 比 eval 分数信号更高）、低层可控 primitive（避免框架锁定）。
- **⟶ 与我推演的关系**：**最强印证"每个架构都有保质期"**，且给了"镰刀一"三个真实死亡案例（编排图、多代理、结构化输出 workaround）。**但它对我有一个修正**：我原以为"确定性代码"整体耐久，PostHog 的经验细化了——**只有"极简、自我强化、模型友好"的代码（todo_write）耐久，"补模型缺陷"的代码（JSON retry）照死不误。** 判据不是"代码 vs 提示词"，而是回到 Sutton：**是不是在补一个"会被 scaling 填平"的能力缺口。**

### 观点 E · Howardism / TML 引用 [网络观点]
- 直接引 Bitter Lesson 论证**交互层**：手工的 VAD、轮次检测、对话管理 harness *"will be outpaced by the advance of general capabilities"*，所以 *"for interactivity to scale with intelligence, it must be part of the model itself."*
- **⟶ 与我推演的关系**：把"镰刀一"推到了我没覆盖的**交互/多模态层**——连"什么时候该说话"这种 harness 都将被吸进模型。印证了镰刀的普适性。

### 交叉审阅小结：我的推演 vs 网上共识

| 我的推演 | 网上是否支持 | 需要修正的地方 |
|---|---|---|
| 提示词 playbook 必死 | ✅ 全体一致（B/C/D 都实证） | 无 |
| 固定编排/多代理死 | ✅ PostHog/Tavily/Minh Pham 实证 | 无 |
| 进化循环=Search，不死反强 | ✅ Minh Pham "compute allocation engine"、动态委派 | 无 |
| 确定性代码"活最久" | ⚠️ 部分支持，需细化 | **不是所有确定性代码，只有"非能力缺口填补型"（安全闸门/自我强化）活；"补模型缺陷型"照死** |
| 两把镰刀（scaling + 生态） | 🆕 网上少见明确拆成两把 | 这算本报告相对原创的贡献 |

**最大收获**：业界已从"要不要 harness"进化到**"harness 该薄成什么样"**——共识是"**thin interface to scalable compute, not where you hide the intelligence**"。我的"知识/底座"二分，与他们的"how/what""能力缺口填补物 vs 保证型需求"是同一枚硬币。

---

## 🔮 可证伪信号（这场推演怎么被证明对/错）

**支持"harness 被反杀"**（我押这边为主）：
- 同一基准（如 LAB）上，**代际更新的模型，harness 增量（今天 +16.7 点）逐代缩小**；
- **提示词部分的收益比代码部分萎缩得更快**（46 已给半个微观信号：提示词跨家族失效、代码跨家族迁移）；
- agentic-RL 过的模型需要的脚手架明显更少（Miessler："The smarter the model, the less 'how' scaffolding you need"）。

**支持"harness 耐久"**：
- 模型 scaling 了，delta 却**不缩小**；
- 确定性**安全**闸门在生产里**不因换模型而下岗**（ClawdBytes 那条 never-push 就是活标本）。

> **46 的一手数据已提供半个微观信号**：单篇实验内部，提示词（知识层，脆）跨家族失效、代码（底座层，韧）跨家族迁移——**镰刀预言的"知识/底座分裂"，在一篇实验里就显形了。**

---

## 🤔 个人理解：三层嵌套，不是三方互斥

读完两篇 + 五份网上观点，我最终的心智模型是**嵌套**而非对立：

```
① 模型 scaling（Bitter Lesson）——决定天花板有多高
        └── ② Harness ——决定你离天花板多近
                 ├── ②a 知识层（提示词/编排/补缺陷代码）→ 被镰刀吃掉，随模型变强而变薄
                 └── ②b 底座层（安全闸门/工具接口/自我强化）→ 薄薄一层，砍不到底
        └── ③ 进化循环（Search）——"够到天花板"这个动作本身
                 └── 是 Sutton 亲儿子，不死反强；人退到"设计 reward 和搜索空间"的位置
```

**最漂亮的自洽**：镰刀**砍掉的是 harness 搜索的"产物"，却祝福 harness 搜索的"过程"**——这跟它当年砍掉手工特征、却祝福"从数据学特征"是**同一个动作**。所以进化 Harness 非但不是 Bitter Lesson 的反例，它是 Bitter Lesson 在 2026 年的**自然延伸**。

**我最警惕的过度解读**：不要把"prompt engineering is dead"读成"harness engineering is dead"。网上标题党在这滑坡。准确的说法是——**"how 型脚手架在死，what 型底座在活；工作被从'写规则'搬到了'设计搜索循环 + 守住确定性闸门'。"** 工程量不是归零，是**换性质**。

---

## 🧩 关联与回链

**本库内**：
- 报告 22《The Bitter Lesson》——本推演的"矛"。
- 报告 46《不要训模型，进化 Harness》——本推演的"盾"，提供一手数字。
- 《Agent_Harness_三大设计流派解析》——三大流派（配置化/图编排/工作流化）在本推演里可重排：图编排/工作流化正是"镰刀一"高危区。
- 《Agent_自进化技术路径深度解析》——进化循环作为"不死项"的技术谱系。
- wiki: `concepts/agent_harness.md`（本报告更新了它的"会不会被反杀"小节指针）。

**网络来源**（均 [网络观点]）：
- Minh Pham, "Why Most Agent Harnesses Are Not Bitter Lesson Pilled"（经 blog.aihao.tw 转述）

https://blog.aihao.tw/2026/02/17/bitter-lesson-agent-harness/

- blog.exe.dev / ClawdBytes, "Prompt Engineering Is Dead", 2026-05-23

https://clawdbytes.com/article/2026-05-23-prompt-engineering-is-dead-but-claude-still-tries

- Daniel Miessler, "Bitter Lesson Engineering", 2026-02-22

https://danielmiessler.com/blog/bitter-lesson-engineering

- Gopal Khakda (DevDash Labs), "Context Engineering and the Bitter Lesson of AI Agent Architecture", 2026-02-26（引 PostHog / Tavily / Lance Martin）

https://devdashlabs.com/insights/context-engineering-ai-agent-architecture

- Sutton 原文（引句核对源）

http://www.incompleteideas.net/IncIdeas/BitterLesson.html

---

## 💭 思考与追问

1. **我真正理解了什么？**
   我把 Bitter Lesson 与进化 Harness 的表面矛盾拆解为**嵌套关系**：scaling 定天花板、harness 定接近度、Search 是接近动作本身。关键判据从我最初的"知识 vs 底座"，经网上观点校正为更准的 **"是不是在填补一个会被 scaling 填平的能力缺口"**——是则死（提示词、JSON retry、图编排），否则活（安全闸门、工具接口、self-reinforcing 的 todo 工具、进化循环）。网上业界共识（"thin interface, not where you hide intelligence"）与我的推演高度收敛，并让我识别出"两把镰刀"（scaling + 生态适配）这个相对原创的拆分。

2. **我还没搞懂什么？**（汇入 open-questions）
   - **"能力缺口填补物 vs 保证型需求"能否形式化判定？** PostHog 的 todo_write（活）和 JSON retry（死）都是确定性代码，事后好解释，但**有没有事前判据**能预测哪段代码会 BLE-hobbled？
   - **"两把镰刀"哪把更快？** agentic-RL（镰刀一）和 MCP 生态（镰刀二）谁先削平 harness？若生态更快，harness 是"被模型吸收"还是"被标准协议标准化"消失——机制不同。
   - **进化循环真的完全免疫吗？** Search 是 Sutton 祝福的，但"设计 reward 和搜索空间"仍是人类活。会不会连 reward 设计也被 meta-search 吃掉（AlphaEvolve 式）？那时人退到哪？
   - **Sutton 原文我仍是转引**：BLE 文章里那几句引文需回 incompleteideas.net 原文逐字核对，消掉 [转引] 标注。

3. **下一步读什么 / 做什么？**
   - 回 incompleteideas.net 读 Sutton 原文全文，核对本报告所有引句。
   - 追 Minh Pham 的 X 原长文 + MIT 的 RLM（Recursive Language Models）论文，把"动态子代理/递归"作为"不死 harness"的正例补进报告 46 或本报告。
   - 在 `ai-practice/` 做一个**跨代模型对照实验**：同一 harness 在弱模型/强模型上跑，量"harness 增量随模型变强而缩小"这条可证伪信号，把推演变实测。
