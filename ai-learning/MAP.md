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

---

## 优先级队列

> 接下来最想补的缺口，按优先级。AI 可主动从这里提议。

- （待补 — 由对话采集）

---

## 更新日志

- 初始化领域地图（EverAgent，architecture-redesign）。覆盖状态待逐步回填。
- `2026-07-07` — 新增"可解释性 & AI 安全"主线，覆盖 J-space/J-lens 全局工作空间（paper 45）。
- `2026-07-07` — 前沿专题(Agent)补充进化式 harness 一手实证（paper 46，Niklaus "Don't Train the Model, Evolve the Harness"）；关联 wiki/concepts/agent_harness.md。
- `2026-07-07` — 新增讨论型报告《Bitter Lesson vs Agent Harness 推演与网上观点审阅》，缝合 paper 22 × 46，交叉审阅 5 份网络观点（Minh Pham/exe.dev/Miessler/PostHog-Tavily/Howardism），提出"两把镰刀 + 知识/底座二分 + 可证伪信号"。
- `2026-07-09` — 前沿专题(Agent)补充《Harness 请求全链路深度解析》：报文级拆解客户端↔网关↔Harness↔LLM↔工具"有来有回"（OpenAI tool_calls / Anthropic tool_use·tool_result·stop_reason 循环），解答 token 单向膨胀因果，四类上下文治理（prompt caching 0.1×、滑窗、compaction、context editing），并澄清 4 个常见认知误区。新缺口汇入 open-questions（compaction 压缩比失真、caching 前缀失效、服务端/客户端历史对账）。定位为纯原理讲解（不含来源评价）。
- `2026-07-13` — 新增评论文精读《伪智力繁荣时代评论文精读与批判》（源：公众号「朋克周」）：提炼原创概念"伪智力繁荣/认知香薰/思想皮肤"，把核心命题"AI 缩小真伪思想外观差距（抬高表达地板而非判断天花板）"与 [Bitter Lesson × Harness]"能力普及削平表层脚手架"缝合；用 METHODOLOGY §二反向审视源文（有新"区分"但缺新"事实"，"摩擦即真"判据有幸存者偏差）。新缺口汇入 open-questions（"摩擦=真"可证伪性、"外观差距缩小"的可测实验设计）。[评] 若"AI 与认知生态"同类议题≥3 次，考虑新建 MAP 主线。
