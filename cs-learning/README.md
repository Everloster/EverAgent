# 计算机科学学习与研究

围绕计算理论、算法、系统、分布式、数据库与网络积累论文精读和专题研究。关注理论为什么成立、系统如何演化，以及设计在什么条件下做出取舍。

## 阅读入口

| 想看什么 | 入口 |
|---|---|
| 经典论文与系统设计 | [论文精读](./reports/paper_analyses/) |
| 跨论文的机制与演化脉络 | [知识报告](./reports/knowledge_reports/) |
| 概念、人物与系统关联 | [Wiki](./wiki/index.md) |
| 已有覆盖与后续方向 | [知识地图](./MAP.md) · [未解问题](./wiki/open-questions.md) |
| 原始材料与书目 | [论文索引](./papers/PAPERS_INDEX.md) · [书籍索引](./books/BOOKS_INDEX.md) |
| 技术史与系统阅读路线 | [发展时间线](./roadmap/CS_Development_Timeline.md) · [学习路径](./roadmap/Learning_Roadmap.md) |

Wiki 用于概念导航，报告保留论证与来源；两者覆盖范围不必相同。旧路线、书目中的阅读状态可能滞后，已有成果以实际报告为准。

## 几条阅读线索

- **分布式系统**：[Lamport 逻辑时钟](./reports/paper_analyses/05_lamport_clocks_1978.md)、[Raft](./reports/paper_analyses/15_raft_2014.md)与[分布式系统知识图谱](./reports/knowledge_reports/分布式系统知识图谱.md)，对照存储、共识、协调与消息的不同职责。
- **系统演化**：[UNIX](./reports/paper_analyses/04_unix_1974.md)与[操作系统内核设计](./reports/knowledge_reports/操作系统内核设计深度解析_20260416.md)，从前代瓶颈理解后续设计。
- **编程与并发**：[CSP](./reports/paper_analyses/18_csp_1978.md)与[编程语言范式演化](./reports/knowledge_reports/编程语言范式演化_从Lisp到Go的并发模型变迁.md)，连接理论模型与语言机制。

阅读时区分证明、复杂度口径与实测性能；系统权衡应放回工作负载和故障模型，不用单一口号解释所有设计。训练与推理系统可衔接 [AI](../ai-learning/README.md)，实际开源实现见[仓库研究](../github-trending-analyzer/README.md)。

## 继续研究与历史资料

执行入口见 [AGENTS.md](./AGENTS.md)，公共流程见[报告工作流](../docs/REPORT_WORKFLOW.md)。

早期摘要与离线知识包保存在[历史 Context](./archive/legacy-context/CONTEXT.md)和[旧知识层](./archive/legacy-context/knowledge/INDEX.md)。归档保留原始解释，不把旧库存、否定式覆盖声明或推荐任务当作当前状态。
