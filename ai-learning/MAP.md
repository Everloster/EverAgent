# AI/ML — 领域地图（MAP）

> 这个领域我想覆盖什么、已覆盖什么、缺口在哪。对话学习时 AI 据此建议"下一步学什么"。
> 维护规则：每出一篇报告，更新对应主线的"已覆盖"；发现新缺口时补充。

---

## 主线与覆盖状态

| 主线 | 想覆盖 | 已覆盖（报告/wiki） | 缺口 |
|------|--------|---------------------|------|
| 数学与ML基础 | ✓ | 待统计 | 待补 |
| 深度学习核心 | ✓ | 待统计 | 待补 |
| 大语言模型与NLP | ✓ | 待统计 | 待补 |
| 前沿专题(Agent/推理/多模态) | ✓ | Agent Harness 三大流派、自进化路径、AI 编码 Agent 终端；**进化式 harness 一手实证（paper 46）**；**Harness 请求全链路（报文级 function calling/tool use + agentic loop）**；**ChatGPT Work 能力面逆向解析（商业化 harness 活样本 + 七层映射表，08-31）** | 进化循环的过拟合防护、reward 消融、跨家族迁移机制待补；Work 子 agent 上下文传递、Ultra 档委派机制、auto-review 抗注入实证待补 |
| 可解释性 & AI 安全 | ✓ | J-space/J-lens 全局工作空间（paper 45） | 点火实验、机制可解释性系统方法（SAE 等）待补 |
| **AI 行业与商业观察** | ✓ | 伪智力繁荣评论批判（07-13）、Anthropic 人才信号核实（07-14）、Evoken 陈冕访谈精读（07-29）、《Intelligence Curse》智能诅咒精读（07-30）、《AI应用创业生死录》Evoken三产品商业分析（07-31）、**《中国AI创业与一级市场故事线2022底-2026》从模型信仰到应用求生——三幕迁徙+全融资轮次表+机构视角(07-31)** | 「应用时代」信号追踪（2027-01）、薄毛利打穿点建模、judgment护城河证伪信号、国资接棒是续命还是改写规则、应用层估值洼地会否修复、IPO后二级市场重估 |

---

## 优先级队列

> 接下来最想补的缺口，按优先级。AI 可主动从这里提议。

- **活跃线（2026-07-20 对话确认）**：
  - Agent/Harness 工程线（进化 harness 过拟合与跨家族迁移、Bitter Lesson 镰刀、请求链路 compaction/caching）
  - 模型效率线（MoE 专家结构、投机解码；**vLLM 推理引擎源码级长线**——2026-08-21 拍板，七阶段全量+GPU 实操+深度专业体，计划见 [roadmap/vLLM_源码级学习计划_20260821.md](./roadmap/vLLM_源码级学习计划_20260821.md)）
  - AI 行业与认知生态（Khanmigo RCT 追踪、Anthropic 人才信号回访）
- 可解释性/意识线（J-space 残留 3 问）：暂缓，不主动提议
- 注意：wiki/open-questions.md 是历史快照 ≠ 当前兴趣，提议前先与用户确认

---

## 更新日志

- 初始化领域地图（EverAgent，architecture-redesign）。覆盖状态待逐步回填。
- `2026-07-07` — 新增"可解释性 & AI 安全"主线，覆盖 J-space/J-lens 全局工作空间（paper 45）。
- `2026-07-07` — 前沿专题(Agent)补充进化式 harness 一手实证（paper 46，Niklaus "Don't Train the Model, Evolve the Harness"）；关联 wiki/concepts/agent_harness.md。
- `2026-07-07` — 新增讨论型报告《Bitter Lesson vs Agent Harness 推演与网上观点审阅》，缝合 paper 22 × 46，交叉审阅 5 份网络观点（Minh Pham/exe.dev/Miessler/PostHog-Tavily/Howardism），提出"两把镰刀 + 知识/底座二分 + 可证伪信号"。
- `2026-07-09` — 前沿专题(Agent)补充《Harness 请求全链路深度解析》：报文级拆解客户端↔网关↔Harness↔LLM↔工具"有来有回"（OpenAI tool_calls / Anthropic tool_use·tool_result·stop_reason 循环），解答 token 单向膨胀因果，四类上下文治理（prompt caching 0.1×、滑窗、compaction、context editing），并澄清 4 个常见认知误区。新缺口汇入 open-questions（compaction 压缩比失真、caching 前缀失效、服务端/客户端历史对账）。定位为纯原理讲解（不含来源评价）。
- `2026-07-13` — 新增评论文精读《伪智力繁荣时代评论文精读与批判》（源：公众号「朋克周」）：提炼原创概念"伪智力繁荣/认知香薰/思想皮肤"，把核心命题"AI 缩小真伪思想外观差距（抬高表达地板而非判断天花板）"与 [Bitter Lesson × Harness]"能力普及削平表层脚手架"缝合；用 METHODOLOGY §二反向审视源文（有新"区分"但缺新"事实"，"摩擦即真"判据有幸存者偏差）。新缺口汇入 open-questions（"摩擦=真"可证伪性、"外观差距缩小"的可测实验设计）。[评] 若"AI 与认知生态"同类议题≥3 次，考虑新建 MAP 主线。
- `2026-07-14` — 新增行业观察《涌进 Anthropic 的 N 个巨佬 核实与深度分析》（源：公众号「数字生命卡兹克」）：原文全文存档 + 对 9 位（+引子 Tom Blomfield）逐个一手核验（10 人多源交叉，全部属实）。增量：文章漏掉的半张名单（Fontoura/Boyd/Instagram/Adept CTO，实为成建制系统挖角）；重排出三个"人才桶"（算力/预训练·RL/AI-for-Science·社科对齐）各对应一条战线；用官方《When AI builds itself》"80%+ 代码由 Claude 写"锚定 Karpathy 线；批判其幸存者偏差与"贝尔实验室"类比裂缝（闭源商业 vs 开放基础研究）。新缺口汇入 open-questions（信号证真/证伪周期、AI 造 AI 杠杆上限、闭源实验室承载"公共地基"的张力）。[评] "AI 行业信号/人物图谱"已是第 2 篇（另有 AI关键人物图谱.md），距新建主线更近一步。
- 2026-07-20：对话确认当前兴趣——活跃线为 Agent/Harness 工程、模型效率（MoE/投机解码）、AI 行业与认知生态；可解释性/意识线暂缓。明确 open-questions 为历史快照，提议前需先确认兴趣。
- 2026-07-20：应用「消费端反馈」重挖优先级——放弃"清 open-questions"路线（历史快照 ≠ 当前兴趣），改为"把已确认活跃线上、只有深度版且用户没读进去的存货，用科普体重写"。首篇产出《AI 越来越强，我们给它搭的脚手架会被自己淘汰吗？》（Bitter Lesson × Harness 科普版，师傅/徒弟贯穿类比），对应深度稿 20260707；顺带一手核实 Sutton 原句消除原稿 [转引] 标注。
- 2026-07-20：消费端反馈路线第二篇——《投机解码科普讲解》（教授/实习生贯穿类比），对应深度稿 20260625，模型效率线的投机解码主题完成科普化（MoE 已于 0719 完成）。增量：① 三词词表手算验证"输出分布严格不变"（0.2/0.6/0.2 全对上，结清深度稿"只懂直觉没推完"的遗留）；② 硬件账算平 2-3× 加速（42ms 搬运 vs 0.8ms 计算）；③ headline 数字对照 Leviathan/Chen 原论文摘要逐字复核，补草稿模型 6M 参数、XSum 1.92× 等精确实测。新缺口（树形验证接受率定量、EAGLE 特征层原理、大 batch 拐点）汇入 open-questions。
- 2026-07-29：**领域扩边界 + 新增主线「AI 行业与商业观察」**（用户拍板"旧边界是遗产"）——第 3 次行业观察类输入达成（07-13 评论文/07-14 巨佬/本次 Evoken），旧 [评] 预言的"≥3 次新建主线"兑现。首篇报告《Evoken 陈冕晚点访谈精读：AI 应用生存策略》：健身房年包定价精算、PMF 后发竞争观、模型吞噬应用与 Bitter Lesson 缝合、高价值 token 论；证据纪律=经营数字全标受访者自述。三缺口汇入 open-questions（消耗率基准/吞噬边界条件/应用时代信号 2027-01 回访）。
- 2026-07-30：行业/政治经济观察线第 2 篇——《Intelligence Curse 智能诅咒精读》(科普体)。把 Luke Drago & Rudolf Laine 66 页长文压成"资源诅咒 → 智能诅咒"一根主类比:掌权者靠 AI 而非人挣钱 → 失去投资普通人的激励(教育/福利/就业回报归零)。三部曲(金字塔替换→权力冻结→社会契约断裂)+ 三出路(Avert/Diffuse/Democratize)。权威锚点核实=Michael Ross《Does Oil Hinder Democracy?》(World Politics 2001)三机制、rentier state theory、Great Leveler,证明类比经济学根基扎实。缝合点:Diffuse 章"替代 vs 补充/别造单体 Agent/对齐到个人用户/开源施压"直接接 [Bitter Lesson × Harness]——技术选型=政治选择。三缺口汇入 open-questions(可证伪信号/类比裂缝/对齐到个人用户可行性)。
- 2026-07-31：行业观察线第 3 篇(深度专业/商业分析)——《AI应用创业生死录:Evoken三产品商业分析》。**跨类复合任务**(E类 opencli 官网实地调研 + A类分析),三源交叉:播客完整版(晚点175陈冕)+ shownotes/图文 + 三产品官网实测(liblib.art/lovart.ai/liblib.tv)。核心增量=**把陈冕的定价哲学在 Lovart 官网定价页逐条实证**(积分制/按模型明码标价 Seedance $0.04/秒/消耗率机制/年包锁LTV),证明"薄毛利+消耗率定价"不是空谈而是精算工程。三产品=应用层价值栈三种活法(Liblib聚合+社区/Lovart Agent编排/LibTV垂类场景)。战略框架"逐鹿中原vs占领江东"=在巨头注意力时间差里偏安求生(真名是体面拖延非必胜)。生死系于两个外部变量:token成本曲线+巨头注意力窗口。缝合[Intelligence Curse]/[Bitter Lesson]:judgment护城河是否也会被模型淹没。三缺口(江东天险量化/薄毛利打穿点建模/judgment证伪信号)。
- `2026-08-21`：用户拍板 vLLM 源码级学习长线（七阶段全量 + GPU 实操 + 深度专业体），录入模型效率线活跃队列，计划文件落 `roadmap/vLLM_源码级学习计划_20260821.md`。该线承载结清 open-questions「EAGLE 特征层原理」的任务；每完成一阶段回本文件回填覆盖状态。
- `2026-08-21`：vLLM 长线**阶段 0 落地**——《vLLM V1 架构总览：一个请求的一生（骨架篇）》（深度专业体）。源码 pin v0.27.1 本地 clone（`../vllm`），三路并行源码勘察 + 主会话抽查复核（V0 alias、step 本体、`vllm/models/` 归属）。要点：四类进程模型（A+DP+N+1）、请求一生 12 跳、EngineCore 三线程 busy loop 与 execute/sample 两相拆分、执行层四层结构、「v0.27.1 vs 教科书 V1」11 条新变化（含 V0 彻底删除、Renderer 抽象、scale_out 前后端分离、Model Runner V2）。GPU 动手清单待 infra 开机补齐。三新问汇入 open-questions。
- `2026-09-02`：vLLM 长线**引入 OpenMAIC 实验载体**（`../OpenMAIC`，清华多智能体互动课堂）。用户反馈《V1 架构总览》直读吃力 → 节奏改「应用驱动」：先建体感再挖源码，源码主线不变。已用 GLM Coding Plan（coding 端点 OpenAI 兼容，glm-5.3 + flash 分流）跑通端到端课堂生成，首课即 vLLM 入门迷你课；阶段 2 prefix caching 实验挂接其 30KB system prompt 复用负载。详见 roadmap「实验载体」节。
- `2026-08-31`：Agent/Harness 工程线 + AI 安全线新增《ChatGPT Work 能力面与 Harness 样本深度解析》（深度专业体）。精读 Simon Willison《Understanding ChatGPT Work》(2026-08-30) 一手实验评测，做三件事：① 逐条拆解 7 项 Chat 没有的独占能力（Sol/Luna/Terra 六档推理·出网 code interpreter·headless Chrome+Playwright·跨会话持久 `/workspace` 卷·ChatGPT Sites 部署到 Cloudflare·子 agent·定时任务）；② 缝合本库 harness 谱系，产出「harness 七层抽象 × Work 对应件」映射表，论断 **Work 不是新范式，是已知 harness 抽象的极致商业化**（开放度拉满，尤其"默认全域名出网 code interpreter"远超 Claude 短白名单）；③ 把 Simon 的 lethal trifecta（致命三重）落到 Work，论证**三样全占是能力面必然副产品而非漏洞**（持久卷=私有数据/浏览器读任意页=不可信内容/出网=外传通道），与"纯 Chat 风险小"同源。证据分层标注 `[Simon 实测]`/`[Simon 推测]`/`[官方核实]`；GPT-5.6 天体命名(2026-06-26)、Work GA(2026-07-09)经联网核实。三缺口汇入 open-questions（子 agent 上下文传递、Ultra 委派机制、auto-review 抗注入实证）。
