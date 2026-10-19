---
title: "AI 行业日报 · 2026-10-19"
domain: "web-surfing"
report_type: "daily_digest"
status: "completed"
updated_on: "2026-10-19"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily", "industry_watch"]
---

# AI 行业日报 · 2026-10-19

四源：AIHOT ✅ · GitHub Trending ✅ · AI Digest ❌ · HN ✅
覆盖 2026-10-19（含 10-16 以来发布、今日仍在前排的条目；10-16–10-18 无日报） · [上期日报 →](./ai-news-daily-2026-10-15.md)

---

## 今日要点

1. **Anthropic 就业实证**：初级技术岗占比 21%→14%，agent 工时达员工六倍
2. **德国双判例**：两法院先后判 Google 为 AI Overview 担责，上诉案和解收场
3. **DeepSeek 新 Flash**：DeepSWE 77% 且约 $0.20/任务，权重开放下载
4. **Claude 破悬案**：30 分钟解 NIST 曲线种子之谜，NSA 后门论被排除
5. **ChatGPT 进 Chrome**：可读开放标签页并代操作，全计划可用
6. **中国出口管制**：拟限制 23 项 AI 技术出口，开源权重在列
7. **OpenAI 学术计划**：Rosalind 免费给美国大学实验室 30 席位一年
8. **Trending 换榜**：插件/skills 目录三平台同榜，rea 七连榜终结

---

## 头条 1 · 🏢 Anthropic 自曝就业结构：初级技术岗占比 21%→14%，agent 工时达员工六倍

**三句话速读**：Anthropic 发布内部研究《How employment is changing at Anthropic》，用自家数据量化 AI 对招聘结构的冲击。技术部门初级岗位占比从 2025 年初的 21% 降至 14%，新招初级占比从 27% 降至 9%。同期 AI agent 工时暴涨，8 月起达到员工的六倍。

**关键事实**
- 官方研究页（作者 Nathan Wilmers 等四人）：初级岗位占比 21%→14%，新招初级 27%→9%，空缺初级职位降至 6%，非技术部门基本稳定。
- 空缺初级职位自 2025 年 12 月起加速下降；2026 年 1 月公司内部出现「初级技术需求下降」的讨论。
- agent 交互工时 2026 年 3 月起超过人类员工，8 月全公司 6:1，研究部门 19:1。
- 人均产出：工程师 commit **5.1 倍**、数据科学查询 3.1 倍、法务合同 3.1 倍、销售成单 1.7 倍。
- 人类注意力成为瓶颈：非技术员工读完 Claude agent 输出需半个工作周，员工转向「meta-work」——建可见性工具、监控 agent 管道。
- 招聘经理优先级转向自主性与判断力，技术专长与执行力权重下降。

**细读与质疑**
- 全部数字为公司自报内部口径，无外部审计；绝对岗位数与员工总数未披露。
- 「六倍工时」统计的是交互 agent hours，与人类工时不同质，不能直接折算替代率。
- 研究自己声明 Anthropic 是 AI 浓度极高的特例，不能外推整个经济体；The Decoder 补充外部研究者的「认知公地悲剧」警告——初级岗位消失的代价将在 2030–2045 年以专家断层兑现。

**来源** · [Anthropic 官方研究页（本期直读）](https://www.anthropic.com/research/employment-at-anthropic) · [The Decoder（本期直读，10-18 全文）](https://the-decoder.com/anthropic-has-nearly-stopped-hiring-junior-staff-because-ai-agents-now-work-six-times-as-many-hours) · [AIHOT 10-19 期（直读）](https://aihot.news/daily/2026-10-19)

---

## 头条 2 · ⚖️ 德国两法院先后判 Google 为 AI Overview 担责，公开上诉悄悄和解收场

**三句话速读**：The Decoder 披露，慕尼黑 I 地区法院 5 月底裁定 AI Overview 属于 Google 自己的陈述、须为虚假内容担责；Google 公开宣布上诉后实际以和解结案，上级法院从未审理。9 月 24 日亚琛地区法院在新案中直接援引慕尼黑推理，形成两法院同口径的判例链。

**关键事实**
- 慕尼黑案：AI 错误地把两家慕尼黑出版社关联到诈骗；法院认定 AI Overview 不是搜索结果，而是 Google 自己的陈述。
- 上诉未走到判决：以和解结案，和解原因与是否涉款未知，Google 与当事出版社均不评论。
- 亚琛案：AI Mode 把另一位教授的性侵案安到一位神经放射学主任医生头上，并编造完整法律后果；医生 8 月底要求删除，Google 9 月中旬仍拒绝行动。
- 亚琛法院未经听审紧急禁止三种虚假文本变体，违者每次最高罚 **25 万欧元**；裁定尚未生效，Google 可抗辩。
- 亚琛判词：「提供 AI 生成搜索，就要为其中生成的回答负责」；AI 产出是「独立、新、实质性的陈述」，Google 可将其与源网页比对核查。

**细读与质疑**
- 「用和解规避先例」是 The Decoder 的定性；和解条款双方均不披露，无法核实动机。
- 同文推演：若最高法院确认 AI 回答属原创内容，被引用出版商可进一步主张权利——这是最坏情形推演，非既成事实。
- 全部进展限于德国管辖，跨境可执行性未裁定。

**来源** · [The Decoder（本期直读，10-18 全文）](https://the-decoder.com/two-german-courts-now-hold-google-liable-for-what-its-ai-overviews-say) · [Reuters 上诉报道（检索快照，6-12）](https://www.reuters.com/world/google-appeal-german-court-ruling-assigning-liability-ai-overviews-false-claims-2026-06-12)

---

## 头条 3 · 📏 DeepSeek-V4.1-Flash-1017：agentic 任务约 $0.20/次击败更大模型，搜索引擎同步开放 API

**三句话速读**：DeepSeek 10-17 发布开源权重模型 V4.1-Flash-1017，官方基准在编码与 agent 类别击败 Claude Opus 5、GPT-5.6 Sol、Kimi K3、GLM-5.3 等更大模型。HN 条目 798 分 / 627 评论，为近两日全站最热。同日自建搜索引擎开放为 Search & Fetch API。

**关键事实**
- 权重在 Hugging Face 与 ModelScope 开源；官方称相对前代是性能-成本的 Pareto 改进：基准更好、任务更快、输出更短。
- DeepSWE 基准：top 档 **77.0%**、平均约 **$0.20/任务**；低档 $0.10 达 72% 以上；前代 74.2% 但约 $0.50/次。
- 官方成本图：GPT-6 Astra、Gemini 3.8 Flash、Claude Opus 5 落在 $2 至 $10+ 每任务区间，且分数不及。
- 从零构建完整软件项目采用 RLSF（自反馈强化学习）：以自身置信分数或自生成批评为奖励信号，不需人类评估者或外部奖励模型。
- Search & Fetch API 定价 **$0.75/1,000 次**，基于日处理数亿查询的自建引擎；DeepSeek Harness、Claude Code、Codex 内免费至 10-31。
- Arena 跟进（AIHOT 快讯）：该模型登顶 Code Arena: WebDev 开源模型榜首。

**细读与质疑**
- 全部基准为 DeepSeek 自报，独立评测当时未出；开发者对代码质量的口碑可能与基准背离。
- 「击败更大模型」限于部分编码与 agent 类别，非全面领先。
- AIHOT 10-18 期另给出「API 单价不变」口径，与本文「任务成本下降」并存：降本来自更短输出，非降价。
- 同期中国拟收紧开源权重模型出口（头条 6），开源节奏存在政策变数。

**来源** · [The Decoder（本期直读，10-17 全文）](https://the-decoder.com/deepseek-v4-1-flash-1017-beats-larger-rivals-in-agentic-tasks-while-once-again-massively-cutting-per-task-costs) · [HN 首页快照（DeepSeek 条目 798 分 / 627 评论）](https://news.ycombinator.com/) · [AIHOT 10-19 期（直读，快讯）](https://aihot.news/daily/2026-10-19)

---

## 头条 4 · 🔒 Claude 30 分钟解开 NIST 曲线种子悬案，NSA 后门论被数学排除

**三句话速读**：困扰密码学界 25 年的 NIST 椭圆曲线种子来源之谜被 Anthropic 团队解开：种子由 1997-98 年的 Unix 时间戳喂给 drand48 生成，与传闻中的「英文句子哈希」无关。赏金设立者 Filippo Valsorda 用 Go 复现验证了该结果。3.6 万美元赏金捐给 Let's Encrypt 母组织 ISRG。

**关键事实**
- 悬案：NIST 2000 年在 FIPS 186-2 发布 P-192 至 P-521 五条曲线，种子来源从未公开；已故作者 Solinas 留下「哈希了一句俏皮话」的传说。
- 真相：`srand48(当时时间戳)` 逐字节生成，每 20 字节按 ANSI X9.62 试为种子；P-256 对应 1997-08-16 01:52:34 UTC。
- Anthropic 十人团队 10-15 01:07:51 UTC 认领全额赏金；The Decoder 称 Claude 在 30 分钟内发现 lrand48 仅输出 31 位、部分种子高位系统性为零的模式。
- 安全结论（Filippo）：NSA 的选择自由度最多约 30 位，不足以瞄准弱曲线类或植入 NOBUS 后门；Bernstein-Lange 2017 年的攻击假说被完全排除。
- Filippo 称这补完了 NIST 曲线的「平反弧线」，他现在个人推荐其优先于 Curve25519——恰逢这些曲线将被后量子签名取代。

**细读与质疑**
- 赏金设立者的复现验证是本条最硬一环；但「30 分钟」「Claude 主导」的口径来自 The Decoder 转述，Anthropic 原始 writeup 未直读。
- 遗留未解项：生成的有效种子约为发布数的两倍，RNG 复用与 1997 年 bug 是两种未证实假说。
- 「个人推荐 NIST 曲线」是 Filippo 一家之言，密码学界共识待观察。

**来源** · [words.filippo.io（本期直读，赏金设立者一手，10-16）](https://words.filippo.io/seeds-solved) · [The Decoder（本期直读，10-16）](https://the-decoder.com/anthropics-claude-cracks-a-25-year-old-nsa-cryptography-mystery-in-under-30-minutes)

---

## 头条 5 · 🤖 ChatGPT 变成完整 Chrome 助手：读开放标签页、直接代操作

**三句话速读**：OpenAI 把 ChatGPT Chrome 扩展升级为完整浏览器助手。用户可用 `@chrome` 指定开放标签页提问，Chat 模式跨多个标签页取数；Work 模式经 Computer Use 直接在页面上代操作。升级面向所有 ChatGPT 计划开放。

**关键事实**
- Work 模式能力：发消息、填表单、下载文件、整理标签页；完整对话历史移入升级后的侧边栏。
- 官方示例：跨标签页比较商品的尺寸、材质、时效与退货规则；汇总多篇文章；匹配不同卖家价格页。
- The Decoder 称 GPT-6 Astra 是当前最佳的 Computer Use 模型，可处理多步骤复杂工作流。

**细读与质疑**
- OpenAI 官方公告未直读，细节以 The Decoder 全文口径为准；「最佳 Computer Use 模型」无榜单支撑。
- AI 代操作的法律责任与头条 2 同题：德国法院刚给「AI 生成内容归平台」定了调，浏览器内代操作的边界尚未进入任何判例。
- 与 10-15 简讯的 Claude Code 云端会话同向：产品重心从「回答」全面转向「代做」。

**来源** · [The Decoder（本期直读，全文口径）](https://the-decoder.com/) · 历史线：[10-15 简讯（Claude Code 云端会话）](./ai-news-daily-2026-10-15.md)

---

## 头条 6 · ⚖️ 中国拟把 23 项 AI 技术纳入出口管制：开源权重模型在列

**三句话速读**：商务部与科技部 10-16 公布草案，拟把 40 项技术加入出口管制清单，其中 23 项为 AI 技术，包括模型权重、源码与训练方法。达到 10^26 FLOPs 或 2 万亿参数的系统受限。已开源技术豁免，开源发布登记后走快速通道。

**关键事实**
- 门槛口径（The Decoder 直读）：**10^26 FLOPs 或 2 万亿参数**；覆盖模型、agent 与算力集群。
- FT 与多源快照交叉确认草案同时覆盖 AI 与芯片设计；意见征询中，截止日期各源口径不一（11 月初至中）。
- The Decoder 分析：管制或推动西方公司转向美国开源模型，替代中国模型。
- 与 DeepSeek 开源发布（10-17）几乎同日；DeepSeek 报道文末亦提示「深度整合中国模型的工作流吸引力下降」，是否跻身「前十最强」可能是开源放行的决定因素之一。

**细读与质疑**
- 两部委中文原文未直读，门槛与豁免细节全部为英文转述口径。
- 「前十最强模型决定能否开源」与 23 项清单的对应关系未经原文核对。
- 草案到终稿通常有修订，对 DeepSeek、Kimi、GLM 开源序列的实际影响待定。

**来源** · [The Decoder（本期直读，全文口径）](https://the-decoder.com/china-tightens-export-controls-on-open-weight-models-and-23-key-ai-technologies) · [FT（检索快照，标题级）](https://www.ft.com/content/e0a1295c-4492-4fdd-aaf5-55678a9ef9bf) · [thenextweb（检索快照）](https://thenextweb.com/news/china-ai-export-controls-draft)

---

## GitHub Trending（13 仓快照）

今日榜单（2026-10-19 快照，按页面顺序，**13 仓**；上期 10-15 为 12 仓，**2 仓存留**：VoiceStudio、CLI-Anything，[rea、context-mode、xtool 等 10 仓落榜](./ai-news-daily-2026-10-15.md)）：

| 仓库 | 总星 / 今日星 | 语言 | 一句话 |
|------|------------|------|--------|
| [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | 53,282 / **+2,232** | Python | **新上榜**：跑在本机的 AI 求职框架，基于 Claude Code |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 42,712 / +1,175 | Python | **新上榜**：Anthropic 官方 Claude Code 插件目录 |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | 216,627 / +1,414 | TypeScript | 开源编码 agent，延续 2.0 势能 |
| [cursor/plugins](https://github.com/cursor/plugins) | 12,754 / +350 | TypeScript | **新上榜**：Cursor 官方插件规范与插件 |
| [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 76,533 / +513 | TypeScript | **新上榜**：多玩家 agent swarm 编排 harness |
| [akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory) | 10,506 / +512 | Rust | **新上榜**：agent CLI 长期记忆，跨厂商交接 |
| [stablyai/orca](https://github.com/stablyai/orca) | 96,691 / +1,146 | TypeScript | **新上榜**：agent 舰队工作台，自带订阅跑任意编码 agent |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 54,608 / +589 | Python | 让所有软件 agent-native，二度入榜 |
| [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) | 75,434 / +2,082 | Python | 646 语言全本地语音栈，再入榜 |
| [android/skills](https://github.com/android/skills) | 8,782 / +81 | Kotlin | **新上榜**：Android 官方 agent skills 仓 |
| [mlabonne/llm-course](https://github.com/mlabonne/llm-course) | 84,045 / +375 | — | **新上榜**：LLM 学习课程与 Colab 笔记 |
| [Kruk2/jasna](https://github.com/Kruk2/jasna) | 2,418 / +115 | Python | **新上榜**：视频修复工具 |
| [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | 138,632 / +154 | Python | **新上榜**：diffusion 模块化 GUI 与推理引擎 |

**今日特征**
- 插件/skills 官方目录三平台同榜：anthropics/claude-plugins-official、cursor/plugins、android/skills——agent 生态长出「平台目录」层。
- ai-job-search 以 +2,232 居首：用 AI 找工作的框架与头条 1「初级岗位萎缩」同日对读；多仓 Built by 列表含 @claude。
- rea 七连榜后出清，逆向主题让位；VoiceStudio（+2,082）与 CLI-Anything 为仅有的存留仓。
- agent 编排与记忆工具集中上榜：orca（+1,146）、ruflo（+513）、ai-memory（+512），「管一支 agent 舰队」自成品类。
- AI/agent 浓度 13/13 满格；jasna 视频修复与 ComfyUI 生成生态相邻。

- 来源：[GitHub Trending](https://github.com/trending)（2026-10-19 快照，13 仓直读）

---

## 简讯

- **Browser Use 科普浏览器智能体**（[AIHOT 10-19 期](https://aihot.news/daily/2026-10-19)，一手标注）：浏览器智能体由模型、harness 与浏览器三层组成，经「观察-选择动作-执行-检查」循环工作，可经 DOM、无障碍树或截图读页面。
- **OpenAI 推 Rosalind 学术计划**（[The Decoder](https://the-decoder.com/)，直读）：美国大学研究实验室可免费获至多 30 个 Business Standard 席位、为期一年，不含 API；围绕生命科学模型 GPT-Rosalind 与 Workbench，机构、负责人与用途逐项审核。
- **Codex Desktop 被曝持续生成 Crashpad 转储**（[HN 118 分 / 42 评论](https://news.ycombinator.com/)）：openai 仓 issue，正文未读；Codex 桌面端的常驻行为争议与 10-13 CLI 守护进程一脉相承。[历史线：10-13 头条 3](./ai-news-daily-2026-10-13.md)
- **Llmspeed**（[HN 273 分 / 80 评论](https://news.ycombinator.com/)，Show HN）：买硬件前先「感受」本地 LLM 跑多快，正文未读。
- **You could have invented transformers from memory**（[HN 537 分 / 126 评论](https://news.ycombinator.com/)）：从记忆推导 transformer 架构，正文未读。
- **Sphinx 上线前 quiz 你的 AI 代码**（[HN 59 分 / 14 评论](https://news.ycombinator.com/)，Show HN）：以提问方式复核 AI 生成代码的 hook，正文未读。
- **Opus 5.5 生成 500 座时钟单文件**（[HN 24 分](https://news.ycombinator.com/)，Show HN）：6.3 MB HTML 装 500 个时钟，标题级。
- **HN 备查**（非 AI 为主）：太阳能发电全球首超核电（553 分 / 341 评论）；Lean 4 内置经验证内核（88 分，与 AlphaProof 数学线同族）；Pele 把 Mermaid 图渲染为主题化 SVG（369 分）；Furifong 注音日文字体（324 分）；黄金成美国第一大出口商品（303 分）；NY 州游戏所有权法案（218 分）；Commodore 64 硬件模拟器（173 分）；珊瑚白化接触健康邻居数日内恢复（410 分，Nature）。

---

## 趋势总结

### 1. 🏢 **「AI 替代初级岗位」从轶事变成自家数据**

Anthropic 首次用内部数据把 agent 对招聘结构的冲击量化，同日 Trending 第一恰是「用 AI 找工作」的框架。

- 核心读数：初级占比 21%→14%、新招 27%→9%、agent 工时 6:1；招聘标准转向自主性与判断力。
- 研究自己声明不能外推：AI 浓度极端、增长期、自愿采用三重偏差；「认知公地悲剧」的 2030–2045 专家断层是外部研究者推断。
- 冷读：单一样本先于整体经济数据出现，是领先指标还是特例，取决于未来一年其他公司是否复现。

### 2. ⚖️ **AI 生成内容的法律责任开始串成判例链**

慕尼黑与亚琛两法院采用同一推理，Google 以和解规避上诉先例，禁令罚则升至每次 25 万欧元。

- 「AI 回答=平台自己的陈述」若被最高法院确认，出版商向 AI 搜索主张权利是逻辑上的下一步。
- The Decoder 提示反向激励：定向试探 AI 搜索、申请禁令、谈和解可能成为律所生意模式。
- 冷读：进展全部在德国管辖内；和解使核心法律问题至今未经上级法院检验。

### 3. 📏 **开源模型压到 $0.20/任务，同时撞上管制阴影**

DeepSeek 用更短输出把 agentic 任务成本压到对手的 1/10 至 1/50，同周中国拟把开源权重纳入出口管制。

- 官方口径 77% / $0.20 每任务 vs 对手 $2–10+；独立评测未出，自报基准待验证。
- DeepSeek 同步开放自建搜索引擎 API——模型厂开始输出基础设施，而不只是模型。
- Trending 的 orca（自带订阅跑任意编码 agent）与管制草案同向挤压闭源高价：成本敏感的用户侧已在重组工具链。

---
---
*报告生成时间：2026-10-19*
*主数据源：AIHOT · GitHub Trending · AI Digest · Hacker News*
*检索通道：eacli Token Plan（web.search / web.read）*
*说明：评分为站点标注值；以官方链接为准。*

<details><summary>数据源与直读情况（详）</summary>

- **AIHOT**：10-19 期（第 181 期）直读成功，3 件大事、2 来源、1 件一手，publishedTime 2026-10-19T00:00:14Z；本期经旧址 aihot.virxact.com/daily/2026-10-19 直读成功，canonical 指向 aihot.news/daily/2026-10-19（旧址 10-31 停用，正文链接用 canonical 域）。本期为轻量期：Anthropic 就业研究进头条 1，德国两法院进头条 2，Browser Use 一手文章入简讯，快讯 DeepSeek 登顶 Code Arena: WebDev 开源榜首并入头条 3；前一日栏为 10-18 期 DeepSeek-V4.1-Flash-1017 发布（已展开为头条 3）。
- **GitHub Trending**：2026-10-19 快照 13 仓直读，总星 / fork / 今日星均可读；fork 数未入表（与上期格式一致）。mlabonne/llm-course 快照无语言标注，表中记「—」。上期 10-15 的 12 仓中 2 仓存留，10 仓出清（含七连榜的 rea）。
- **AI Digest 中文**：首页直读正常，最新一期仍停留在 2026-08-24，停更约 8 周，当日无内容可用。
- **Hacker News**：首页 30 条快照直读正常，无 item id；DeepSeek v4.1-Flash-1017（798 分 / 627 评论）、transformers 推导（537 分）、Llmspeed（273 分）、Codex Desktop Crashpad（118 分）等分数以快照为准；中国管制 FT 条目经检索命中 item 50121439。
- **本期直读失败项**：Anthropic 原始 writeup（Claude 解 NIST 种子的官方文档未直读，「30 分钟」口径为 The Decoder 转述）；中国两部委管制草案中文原文未直读（The Decoder 直读 + FT/thenextweb 快照交叉）；OpenAI ChatGPT Chrome 升级与 Rosalind 计划的官方公告未直读（The Decoder 直读替代）；Browser Use 原文未直读（AIHOT 一手标注转述）；Codex Desktop issue、Llmspeed、transformers 推导、Sphinx、500 clocks 均 HN 标题级未读；Reuters 德国上诉报道与 FT 报道为检索快照级。
- **本期一手直读项**：aihot.virxact.com/daily/2026-10-19 · github.com/trending（13 仓）· news.ycombinator.com 首页 30 条 · the-decoder.com 首页与三篇全文（junior hiring 10-18T13:22Z、two German courts 10-18T10:52Z、DeepSeek V4.1 Flash 10-17T10:33Z）· anthropic.com/research/employment-at-anthropic（Key findings 与正文部分）· words.filippo.io/seeds-solved（10-16T18:57Z，赏金设立者一手，本期最硬）。
- **转述级关键条目**（未回查原文，待复核）：ChatGPT Chrome 能力分级与「GPT-6 Astra 最佳 Computer Use」（The Decoder 口径）· 中国管制门槛 10^26 FLOPs / 2T 参数与意见截止日期（英文转述，各源口径有分歧）·「Claude 30 分钟解悬案」（The Decoder 转述 Anthropic）· DeepSeek 自报基准 77% / $0.20 与「击败更大模型」类别边界 · Code Arena: WebDev 榜首（AIHOT 快讯）· Browser Use 三层结构（AIHOT 一手标注转述）· Rosalind 计划细节（The Decoder 直读，OpenAI 帮助文档未回查）。
- **去重说明**：最近三篇（10-15 / 10-14 / 10-13）无与本期六条头条重复的事件；10-16–10-18 无日报，DeepSeek 发布（10-17）、中国管制草案（10-16）、Claude 解悬案（10-15/16）、亚琛裁定（9-24，经 10-18 报道披露）为区间内首录；Codex Desktop Crashpad 延续 10-13 Codex CLI 守护进程争议线（简讯 + 历史链接）；OpenCode 2.0（10-15 头条 6）仅以 Trending 延续提及；欧盟执法、Character.AI、Argon、Modal、Copilot RCE 等上期条目无新增量不再引用。

</details>
