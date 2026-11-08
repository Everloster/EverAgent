# AI 学习与研究

围绕 AI/ML 论文、技术机制与行业演化积累可追溯的研究报告。既看模型如何工作，也看数据、算力、研究者与组织如何影响技术路线。

## 阅读入口

| 想看什么 | 入口 |
|---|---|
| 论文中的机制、实验与消融 | [论文精读](./reports/paper_analyses/) |
| 跨论文的概念、系统与专题 | [知识报告](./reports/knowledge_reports/) · [全部报告目录](./reports/) |
| 概念、人物与主题之间的联系 | [Wiki](./wiki/index.md) |
| 已有覆盖与后续方向 | [知识地图](./MAP.md) · [未解问题](./wiki/open-questions.md) |
| 原始论文与选题线索 | [论文索引](./papers/PAPERS_INDEX.md) |
| 技术史与系统阅读路线 | [发展时间线](./roadmap/AI_Development_Timeline.md) · [学习路径](./roadmap/Learning_Roadmap.md) |

报告目录保留完整论证与来源；Wiki 是导航与知识提炼，不代表已经覆盖全部报告。旧路线、索引中的进度与数量可能滞后，查找已有成果以实际报告为准。

## 几条阅读线索

- **Agent 怎样把事情做完**：[请求全链路：连续对话与工具调用](./reports/knowledge_reports/Agent请求全链路_科普讲解_20260715.md) → [续篇：逐字输出、任务进度与断线恢复](./reports/knowledge_reports/Agent请求全链路_流式响应与断线恢复_科普讲解_20261102.md)。前篇讲模型与程序怎样配合，续篇讲结果怎样送到眼前、连接中断后怎样判断任务状态。
- **Agent 怎样从经验里学习**：[Anthropic 记忆组件深读](./reports/knowledge_reports/Anthropic_Agent记忆组件_显著性判断与Dreaming_深度解析_20261108.md)，从错误导航、企业 wiki 和合同条款案例，理解显著性判断、离线纠错、来源回查与维护成本。
- **从机制入手**：[Transformer 精读](./reports/paper_analyses/01_transformer_2017.md) → [Self-Attention 深度解析](./reports/knowledge_reports/self_attention_深度解析.md)。
- **从规模化入手**：[Scaling Laws 精读](./reports/paper_analyses/05_scaling_laws_2020.md) → [Scaling Laws 深度解析](./reports/knowledge_reports/Scaling_Laws_深度解析.md)，结合时间线中的硬件彩票视角。
- **从技术史入手**：[The Bitter Lesson 精读](./reports/paper_analyses/22_bitter_lesson_2019.md)与[关键人物图谱](./reports/knowledge_reports/AI关键人物图谱.md)，关注技术选择背后的条件，而不只记住结论。

系统与计算基础可衔接 [CS](../cs-learning/README.md)，认知与价值问题可衔接[心理学](../psychology-learning/README.md)和[哲学](../philosophy-learning/README.md)，公开代码研究见[开源仓库研究](../github-trending-analyzer/README.md)。

## 继续研究与历史资料

执行入口见 [AGENTS.md](./AGENTS.md)，公共报告流程见[报告工作流](../docs/REPORT_WORKFLOW.md)。按问题选择一种体裁，不必预先通读所有模板。

早期库存、摘要与离线知识包保存在[历史 Context](./archive/legacy-context/CONTEXT.md)和[旧知识层](./archive/legacy-context/knowledge/INDEX.md)。它们保留当时的记录，不是当前执行规则、覆盖清单或选题建议。
