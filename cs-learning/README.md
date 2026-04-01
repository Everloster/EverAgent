# 💻 Computer Science Learning Project

> 系统学习计算机科学的个人知识库与学习项目
> 创建日期：2026-03-24 | 最后更新：2026-03-26（任务板校正 + 协作分发优化）

---

## 项目目标

建立一套完整的计算机科学自学体系，覆盖近80年CS发展史、核心理论与系统原理、经典论文精读，并持续积累深度分析报告。
项目的三个维度：**理论深度**（经典论文与教材精读）× **历史叙事**（人物图谱、技术演化）× **工程实践**（系统设计与代码实现）。

---

## 📁 完整目录结构

```
cs-learning/
│
├── README.md                                    # 本文件，项目总览与导航
│
├── roadmap/                                     # 📍 学习路径规划
│   ├── CS_Development_Timeline.md              # 近80年CS发展时间线（1940s-2020s）
│   └── Learning_Roadmap.md                     # 系统学习路径（Phase 1-6 + 专题模块）
│
├── papers/                                      # 📄 经典CS论文索引（30篇）
│   └── PAPERS_INDEX.md                         # 30篇必读论文索引（含来源链接与摘要）
│
├── books/                                       # 📖 经典CS教材与书籍（本项目特色）
│   └── BOOKS_INDEX.md                          # 25部必读经典索引（按领域分类）
│
├── skills/                                      # 🛠️ 学习技能模板
│   ├── paper_analysis/
│   │   └── SKILL.md                            # CS论文深度分析技能（7步分析法）
│   └── concept_deep_dive/
│       └── SKILL.md                            # CS概念深挖技能（5层理解模型）
│
├── reports/                                     # 📊 分析报告
│   ├── paper_analyses/                         # 论文精读报告（19 篇已完成）
│   └── knowledge_reports/                      # 概念深度解析
│       └── CS关键人物图谱.md                    # ✅ CS先驱生涯轨迹与技术传承图谱
│
└── notes/                                       # 📝 个人学习笔记与参考资料
```

---

## 🚀 快速开始

### 第一步：建立全局视野（推荐首先阅读）

| 文档 | 内容 | 读完后你能做到 |
|------|------|--------------|
| [CS发展时间线](./roadmap/CS_Development_Timeline.md) | 近80年关键节点 + **技术范式迁移分析** | 理解每次技术革命背后的驱动力 |
| [学习路径规划](./roadmap/Learning_Roadmap.md) | Phase 1-6 + **专题深入模块** | 制定个人学习计划 |
| [CS关键人物图谱](./reports/knowledge_reports/CS关键人物图谱.md) | 图灵、冯·诺依曼、Knuth、Unix创始人等 | 理解CS知识体系的传承脉络 |

### 第二步：选择你的学习起点

```
CS零基础，编程入门      →  Phase 1（编程基础 + 计算理论）  →  约4-6周
有编程基础，无系统知识  →  Phase 2（数据结构与算法）       →  约6-8周
有算法基础              →  Phase 3（系统核心：OS + 网络）   →  约8-10周
有系统基础              →  Phase 4（分布式系统 + 数据库）   →  约6-8周
全面基础，深化某方向    →  Phase 5-6（专题深入）            →  持续进行
```

### 第三步：按类型选择学习材料

- **经典论文**（30篇）→ 查阅 [论文索引](./papers/PAPERS_INDEX.md)（理论奠基 + 系统设计）
- **经典教材**（25部）→ 查阅 [书籍索引](./books/BOOKS_INDEX.md)（深度系统学习）

### 第四步：阅读已有深度报告

**论文精读报告：**
- [Turing (1950)](./reports/paper_analyses/01_turing_1950.md)
- [Shannon (1948)](./reports/paper_analyses/02_shannon_1948.md)
- [Lamport Clocks (1978)](./reports/paper_analyses/05_lamport_clocks_1978.md)
- [GFS (2003)](./reports/paper_analyses/09_gfs_2003.md)
- [MapReduce (2004)](./reports/paper_analyses/10_mapreduce_2004.md)
- [Dynamo (2007)](./reports/paper_analyses/11_dynamo_2007.md)
- [Bigtable (2006)](./reports/paper_analyses/12_bigtable_2006.md)
- [Paxos (2001)](./reports/paper_analyses/13_paxos_2001.md)
- [Raft (2014)](./reports/paper_analyses/13_raft_2014.md)
- [Spanner (2012)](./reports/paper_analyses/21_spanner_2012.md)

**概念深度解析：**
- [CS关键人物图谱](./reports/knowledge_reports/CS关键人物图谱.md) — 从图灵到Linus的技术传承

### 第五步：用技能模板生成新报告

- 精读任意CS论文 → 使用 [论文分析技能](./skills/paper_analysis/SKILL.md)
- 深入理解某概念 → 使用 [知识深挖技能](./skills/concept_deep_dive/SKILL.md)

---

## 📊 论文阅读状态追踪

| # | 论文 | 年份 | 领域 | 优先级 | 分析报告 |
|---|------|------|------|--------|---------|
| 01 | Computing Machinery and Intelligence (Turing) | 1950 | 计算理论 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/01_turing_1950.md) |
| 02 | A Mathematical Theory of Communication (Shannon) | 1948 | 信息论 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/02_shannon_1948.md) |
| 03 | A Relational Model of Data for Large Shared Data Banks (Codd) | 1970 | 数据库 | ⭐⭐⭐ | ⬜ 待读 |
| 04 | The UNIX Time-Sharing System (Ritchie & Thompson) | 1974 | 操作系统 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/04_unix_1974.md) |
| 05 | Time, Clocks, and the Ordering of Events (Lamport) | 1978 | 分布式 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/05_lamport_clocks_1978.md) |
| 06 | Reflections on Trusting Trust (Thompson) | 1984 | 安全 | ⭐⭐⭐ | ⬜ 待读 |
| 07 | No Silver Bullet (Brooks) | 1987 | 软件工程 | ⭐⭐⭐ | ⬜ 待读 |
| 08 | The Byzantine Generals Problem (Lamport et al.) | 1982 | 分布式 | ⭐⭐⭐ | ⬜ 待读 |
| 09 | The Google File System (Ghemawat et al.) | 2003 | 分布式存储 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/09_gfs_2003.md) |
| 10 | MapReduce (Dean & Ghemawat) | 2004 | 分布式计算 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/10_mapreduce_2004.md) |
| 11 | Dynamo: Amazon's Highly Available Key-value Store | 2007 | 分布式数据库 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/11_dynamo_2007.md) |
| 12 | Bigtable (Chang et al.) | 2006 | 分布式存储 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/12_bigtable_2006.md) |
| 13 | Paxos Made Simple (Lamport) | 2001 | 共识算法 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/13_paxos_2001.md) |
| 14 | In Search of an Understandable Consensus Algorithm (Raft) | 2014 | 共识算法 | ⭐⭐⭐ | ✅ [已完成](./reports/paper_analyses/13_raft_2014.md) |
| 15 | Bitcoin: A Peer-to-Peer Electronic Cash System (Nakamoto) | 2008 | 密码学/分布式 | ⭐⭐ | ⬜ 待读 |
| 16 | Go To Statement Considered Harmful (Dijkstra) | 1968 | 编程语言 | ⭐⭐⭐ | ⬜ 待读 |
| 17 | An Axiomatic Basis for Computer Programming (Hoare) | 1969 | 形式化方法 | ⭐⭐ | ⬜ 待读 |
| 18 | Communicating Sequential Processes (Hoare) | 1978 | 并发理论 | ⭐⭐⭐ | ⬜ 待读 |
| 19 | A Protocol for Packet Network Intercommunication (TCP/IP) | 1974 | 网络 | ⭐⭐⭐ | ⬜ 待读 |
| 20 | The Design Philosophy of the DARPA Internet Protocols | 1988 | 网络 | ⭐⭐ | ⬜ 待读 |
| 21 | Spanner: Google's Globally Distributed Database | 2012 | 分布式数据库 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/21_spanner_2012.md) |
| 22 | Kafka: A Distributed Messaging System for Log Processing | 2011 | 消息队列 | ⭐⭐ | ✅ [已完成](./reports/paper_analyses/22_kafka_2011.md) |
| 23 | A Fast File System for UNIX (McKusick et al.) | 1984 | 文件系统 | ⭐⭐ | ⬜ 待读 |
| 24 | Recursive Functions of Symbolic Expressions (McCarthy) | 1960 | 编程语言 | ⭐⭐ | ⬜ 待读 |
| 25 | An Efficient Algorithm for Determining the Convex Hull | 1973 | 算法 | ⭐ | ⬜ 待读 |
| 26 | A New Solution to Dijkstra's Concurrent Programming Problem | 1974 | 并发 | ⭐⭐ | ⬜ 待读 |
| 27 | The Anatomy of a Large-Scale Hypertextual Web Search Engine | 1998 | 搜索引擎 | ⭐⭐⭐ | ⬜ 待读 |
| 28 | Chord: A Scalable Peer-to-peer Lookup Protocol | 2001 | P2P/分布式 | ⭐⭐ | ⬜ 待读 |
| 29 | LLVM: A Compilation Framework for Lifelong Program Analysis | 2004 | 编译器 | ⭐⭐ | ⬜ 待读 |
| 30 | Hints for Computer System Design (Lampson) | 1983 | 系统设计 | ⭐⭐⭐ | ⬜ 待读 |

> 完整30篇索引（含摘要与下载链接）见 [PAPERS_INDEX.md](./papers/PAPERS_INDEX.md)
> 当前已完成论文精读 12 篇，最新库存以 [CONTEXT.md](./CONTEXT.md) 为准。

---

## 📚 六大核心领域

```
┌─────────────────────────────────────────────────────────────┐
│                  计算机科学知识体系                           │
├──────────┬──────────┬──────────┬──────────┬────────┬────────┤
│ 理论基础 │ 算法与DS │ 系统核心 │ 分布式   │ 编程   │ 安全   │
│          │          │          │ 系统     │ 语言   │        │
│ 计算理论 │ 排序搜索 │ 操作系统 │ 一致性   │ 编译器 │ 密码学 │
│ 信息论   │ 图算法   │ 计算机   │ 分布式   │ 类型   │ 网络   │
│ 复杂性   │ 动态规划 │ 网络     │ 存储     │ 系统   │ 安全   │
│ 逻辑     │ 数据结构 │ 数据库   │ 消息队列 │ 范式   │ 协议   │
└──────────┴──────────┴──────────┴──────────┴────────┴────────┘
```

---

## 🗓️ 推荐学习节奏

```
Week 1-2:   CS_Development_Timeline + CS人物图谱（建立历史视野）
Week 3-6:   Phase 1 编程基础 + 计算理论（图灵机、Lambda演算、复杂性）
Week 7-12:  Phase 2 数据结构与算法（CLRS精读）
Week 13-18: Phase 3 操作系统（xv6实战 + OS三大件）+ 计算机网络
Week 19-24: Phase 4 数据库原理 + 分布式系统（Lamport论文群）
Week 25-28: Phase 5 编程语言理论 + 编译器原理
Week 29-32: Phase 6 系统安全 + 密码学基础
Week 33+:   专题深入（选择感兴趣方向：云计算 / 编译优化 / 形式验证等）
```

---

## 📌 三个核心视角（项目特色）

**1. 理论奠基视角**：CS的每个实践都有理论根源，先理解"为什么可能"再学"怎么做"。
→ 图灵机 → 冯·诺依曼架构 → 香农信息论 → 现代CS

**2. 系统演化视角**：技术不是凭空出现的，每次系统革新都在解决前代的具体瓶颈。
→ 见 [CS发展时间线](./roadmap/CS_Development_Timeline.md)

**3. 工程权衡视角**：所有系统设计都是在**CAP三角**上做取舍，理解trade-off才能设计系统。
→ 贯穿分布式系统、数据库、OS的核心思维方式

---

## 🔗 与其他子项目的关联

| 关联领域 | 关联点 | 代表性交叉话题 |
|---------|-------|-------------|
| [AI](../ai-learning/) | 系统基础 → AI 训练/推理基础设施 | GFS+MapReduce → AI 数据管道；Raft → 分布式训练协调；LLVM → XLA/Triton |
| [哲学](../philosophy-learning/) | CS 的哲学起点；逻辑学 × 编程语言理论 | 图灵 (1950) 同时出现在 CS 和心灵哲学中；弗雷格/罗素逻辑 → 类型论/程序验证 |
| [心理学](../psychology-learning/) | 认知心理学 × HCI 与系统设计 | Miller 7±2 → 界面信息密度与 API 设计；记忆研究 → 缓存策略直觉 |
| [开源追踪](../github-trending-analyzer/) | 追踪 CS 领域（系统/工具/语言）热门项目 | Rust/Go/分布式工具的趋势分析 |

---

## 🛠️ 待办事项

- [ ] 精读 Chubby 或 ZooKeeper/ZAB，补齐协调服务主线
- [ ] 精读 A Fast File System for UNIX，补齐操作系统/文件系统脉络
- [ ] 精读 TCP/IP 或 DARPA Internet Protocols，补齐网络主线
- [ ] 阅读 CLRS 第1-10章并做笔记
- [ ] 完成 xv6 操作系统实验（MIT 6.S081）

---

*"Computer science is no more about computers than astronomy is about telescopes." — Edsger W. Dijkstra*
