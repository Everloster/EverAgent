# Agent Harness / 进化式 Harness

> 维护日期：2026-10-29 · AI Agent / 上下文工程

## Harness 管什么

Agent Harness 是模型周围的执行系统：它组织指令、提供工具、保存任务状态，并决定如何检查结果、继续执行或交还控制权。修改 Harness 可以改变 Agent 的表现，而不更新模型权重。

这些内容经常一起出现，但成本和可靠性不同：

| 内容 | 例子 | 需要注意什么 |
| --- | --- | --- |
| 指令与按需知识 | 系统提示、`AGENTS.md`、Skill、示例 | 由模型理解；效果受模型、任务、加载方式和其他指令影响 |
| 工具与执行代码 | 文件操作、格式校验、权限检查、重试逻辑 | 纯本地步骤可以不调用模型；工具定义、调用参数与返回内容仍可能消耗 token，接口也需要维护 |
| 上下文与任务状态管理 | 历史裁剪、Memory 检索、checkpoint、工具回执 | 保存资料、组装模型输入、恢复执行是不同职责，不能只靠一段摘要包办 |

因此，“提示词换模型就失效”和“确定性代码零成本、天然通用”都不准确。前者需要验证适用性，后者需要检查接口、环境和执行成本。代码只保证它实际检查到的条件；文件存在不代表报告内容正确。

## 模型升级后，重看哪些指令

[OpenAI 原文](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)总结了 GPT-6 Astra 上的工程观察：过宽的 Skill 描述会误触发，过细的步骤可能限制判断，强制通读文档和反复测试会拖慢简单任务，含糊的权限边界与完成条件可能让 Agent 提前停下。

原文建议把指令放在合适的位置：

- **Skill 描述**说清何时使用；正文先给必要工作流，再指向相关材料。
- **`AGENTS.md`**保留跨任务适用的规则，并按任务路由到文档。
- **任务提示**写清目标、交付物、完成条件和可自主推进的范围。

这是针对特定模型的官方实践总结，没有公布受控实验的成功率或成本降幅。它支持重新检查旧规则，不能推出“提示词越少越好”或“所有模型都适用同一份最短配置”。详细论证见 [GPT-6 Astra 指令架构报告](../../reports/knowledge_reports/GPT6_Astra指令架构_从Prompt堆叠到按需控制_深度解析_20261015.md)。

**[推测] 规则的去留可以按作用判断：**为某次模型失误加的补丁，应在升级后复核；项目事实、工具合同与授权边界仍需明确，只是表达和执行方式可以变化。固定工作流在步骤稳定、验收明确的任务中仍有用途。Bitter Lesson 提供长期思考方向，不能证明哪段 Harness 或哪种进化循环永远不会过时。

## 程序性 Memory 也可能有用

[IBM 的 ALTK-Evolve 实验](https://huggingface.co/blog/ibm-research/altk-evolve-bc)从训练任务轨迹中提炼操作规则，再加入 Agent 的提示词。模型权重保持不变，在 τ²-bench 的留出客服任务上观察到了收益；GPT-4.1 与 GPT-5.5 的实验都出现改善。

这里有三个不能省略的条件：

- GPT-5.5 的规则从它自己的轨迹重新提炼，不能据此声称同一套规则已跨模型迁移成功。
- 最合适的规则数量随领域和指标变化；支持次数统计的是规则来自多少个训练任务，不是正确概率。
- 输入 token 增加；含训练任务的排行榜成绩与留出测试成绩应分别阅读。

这项实验说明，做事经验可以在特定条件下改善后续任务，不能按“过程性知识必然贬值”一概丢弃。跨领域泛化、错误规则传播和长期维护仍需验证。数据与限制见 [ALTK-Evolve 报告](../../reports/knowledge_reports/ALTK_Evolve_学习型Memory与Agent服务任务_深度解析_20261021.md)。

## 保存上下文与恢复任务

长期资料可以供多个 Agent 使用，每次模型调用仍要选择当前需要的部分。Drew Breunig 的[上下文故障分类](https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html)提醒我们检查错误反复传播、历史干扰、无关内容和指令冲突。这是一组诊断视角，不能把其中个别案例的长度阈值外推到所有模型。

任务恢复还需要运行系统的支持。例如 [Codex app-server](https://developers.openai.com/codex/app-server)用 `thread/resume` 继续已保存的 thread；[Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/sessions)将会话历史与文件系统分开保存，跨主机恢复有会话文件和 `cwd` 等条件。共享资料库本身不能替代这些条件。

[LangGraph 持久执行文档](https://docs.langchain.com/oss/python/langgraph/durable-execution)进一步说明：恢复可能重放步骤。如果外部操作已经完成、回执却未保存，仍需幂等键或查询已有结果，避免重复执行。checkpoint 不会自动撤销外部操作。

这些区别在 [Personal Context 概念页](./personal-context-orthogonality.md)和[多设备、多 Agent 会话续接报告](../../reports/knowledge_reports/多设备多Agent共享Context与会话续接_Manus实践与架构边界_深度解析_20261029.md)中展开。

## 如何判断 Harness 改动有效

进化式 Harness 是“运行任务 → 分析失败 → 提出改动 → 对照评估 → 选择版本”的循环。它优化模型之外的结构；优化循环本身也有成本和过拟合风险。

既有 [Niklaus / LAB 实验报告](../../reports/paper_analyses/46_evolve_the_harness_2026.md)记录了冻结模型、修改 Harness 的结果，其中交付文件校验等代码修复有明显贡献。引用时需区分逐条标准通过率与整题全对率，也不能从整套 Harness 的跨模型结果，直接推断某一种组件的普遍迁移能力。该报告中的固定 token 轨迹价格估算也不是端到端实测账单。

**[推测] 对具体项目，足够小的验证应回答以下问题：**

1. 哪种已观察到的失败被修复了？先跑受影响任务，并检查相关反例。
2. 收益在未用于调规则的任务上还在吗？跨模型迁移要单独比较，不能同时换模型、规则和工具再归因。
3. 质量变化付出了什么代价？统计从开始到验收的总耗时与成本，包括检索、重试、交接和复核。

文档更短、token 更少、评审分更高，各自只能说明一个方面。是否改善任务表现，要由最终产物和实际执行记录回答。待解问题见[问题池](../open-questions.md)。

## 继续阅读

- [专题阅读路线](../index.md#contextmemoryharness-专题)：从指令、记忆读到多 Agent 接班。
- 早期专题：[三大设计流派](../../reports/knowledge_reports/Agent_Harness_三大设计流派解析.md)、[自进化技术路径](../../reports/knowledge_reports/Agent_自进化技术路径深度解析.md)、[请求全链路](../../reports/knowledge_reports/Agent_Harness请求全链路_深度解析_20260709.md)。
- [Agent Systems](./agent_systems.md)：Agent 的基本组成。
- [Agent Orchestration](./agent_orchestration.md)：任务如何分工与合并。
- [Agent Observability](./agent_observability.md)：如何定位执行失败。
