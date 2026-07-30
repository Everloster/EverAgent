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
| 前沿专题(Agent/推理/多模态) | ✓ | Agent Harness 三大流派、自进化路径、AI 编码 Agent 终端；**进化式 harness 一手实证（paper 46）**；**Harness 请求全链路（报文级 function calling/tool use + agentic loop）** | 进化循环的过拟合防护、reward 消融、跨家族迁移机制待补 |
| 可解释性 & AI 安全 | ✓ | J-space/J-lens 全局工作空间（paper 45） | 点火实验、机制可解释性系统方法（SAE 等）待补 |
| **AI 行业与商业观察** | ✓ | 伪智力繁荣评论批判（07-13）、Anthropic 人才信号核实（07-14）、Evoken 陈冕访谈精读——AI 应用生存策略（07-29）、**《Intelligence Curse》智能诅咒精读——AGI→资源诅咒式"掌权者不再投资普通人"的政治经济学（07-30）** | 消耗率行业基准、模型吞噬应用的边界条件、「应用时代」信号追踪（2027-01 首次回访）、智能诅咒可证伪信号、「对齐到个人用户」可行性 |

---

## 优先级队列

> 接下来最想补的缺口，按优先级。AI 可主动从这里提议。

- **活跃线（2026-07-20 对话确认）**：
  - Agent/Harness 工程线（进化 harness 过拟合与跨家族迁移、Bitter Lesson 镰刀、请求链路 compaction/caching）
  - 模型效率线（MoE 专家结构、投机解码）
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
