# CS 经典论文索引（30篇）

> 计算机科学必读论文合集，覆盖理论基础、操作系统、网络、数据库、分布式系统、编程语言等核心领域
> 创建日期：2026-03-24

---

## 阅读建议

**首先读（建立框架）**：#01、#02、#04、#16、#30
**系统方向**：#04、#23、#19、#20
**分布式方向**：#05、#08、#09、#10、#11、#13、#14、#21、#22
**语言与理论**：#16、#17、#18、#24
**安全**：#06
**数据库**：#03、#11、#21

---

## 📐 理论基础

### #01 | Computing Machinery and Intelligence
**作者**：Alan Turing
**年份**：1950
**发表**：Mind, Vol. 59
**摘要**：提出"机器能否思考"的问题，并设计"模仿游戏"（即图灵测试）作为操作性定义。讨论了对机器智能的主要反驳论点并一一回应。
**为什么读**：CS哲学的起点；任何讨论AI本质的文章都绕不开此文。
**阅读难度**：⭐（无数学，哲学论证）
**链接**：https://academic.oup.com/mind/article/LIX/236/433/986238

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/01_turing_1950.md`）
---

### #02 | A Mathematical Theory of Communication
**作者**：Claude Shannon
**年份**：1948
**发表**：Bell System Technical Journal
**摘要**：定义信息熵 H = -Σ p log p，奠定信息论基础。证明了信道容量定理（Shannon定理）——噪声信道上可靠通信的理论极限。
**为什么读**：理解"信息"的本质；从压缩算法到LLM的token预测都建立在此基础上。
**阅读难度**：⭐⭐⭐（数学密集，建议先读第1-3节）
**链接**：https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/02_shannon_1948.md`）
---

### #16 | Go To Statement Considered Harmful
**作者**：Edsger W. Dijkstra
**年份**：1968
**发表**：Communications of the ACM（以读者来信形式）
**摘要**：主张废除 GOTO 语句，代之以结构化控制流（顺序/选择/循环）。认为程序员对程序的理解能力与程序中 GOTO 的数量成反比。
**为什么读**：结构化编程革命的宣言；现代所有语言的控制流设计都受此影响。
**阅读难度**：⭐（极短，仅1页半，高度可读）
**链接**：https://dl.acm.org/doi/10.1145/362929.362947

---

### #17 | An Axiomatic Basis for Computer Programming
**作者**：C.A.R. Hoare
**年份**：1969
**发表**：Communications of the ACM
**摘要**：提出 Hoare 逻辑（{P} C {Q}）——用前置条件和后置条件形式化地证明程序正确性。引入赋值公理、顺序规则、while循环规则。
**为什么读**：程序验证（Formal Verification）的理论基础；TLA+、Coq等工具都源于此思想。
**阅读难度**：⭐⭐（需要一定逻辑基础）
**链接**：https://dl.acm.org/doi/10.1145/363235.363259

---

### #24 | Recursive Functions of Symbolic Expressions and Their Computation by Machine (Lisp)
**作者**：John McCarthy
**年份**：1960
**发表**：Communications of the ACM
**摘要**：描述 Lisp 语言的理论基础：S-表达式、递归函数、垃圾回收。引入了 car/cdr/cons 原语，展示用 Lisp 本身描述 Lisp 解释器（元循环解释器）。
**为什么读**：函数式编程的理论起点；Python的map/filter/reduce、JS的函数式特性都是其遗产。
**阅读难度**：⭐⭐⭐（需要函数式编程基础）
**链接**：http://www-formal.stanford.edu/jmc/recursive.html

---

## 🖥️ 操作系统

### #04 | The UNIX Time-Sharing System
**作者**：Dennis Ritchie & Ken Thompson
**年份**：1974
**发表**：Communications of the ACM
**摘要**：描述 Unix 的核心设计：文件系统（一切皆文件）、进程（fork/exec）、Shell、管道。分析了 Unix 为何选择简单而非功能丰富。
**为什么读**：Linux/macOS/Android 的精神祖先；Unix 哲学至今主导系统设计。
**阅读难度**：⭐⭐（系统概念为主，代码较少）
**链接**：https://dl.acm.org/doi/10.1145/361011.361061

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/04_unix_1974.md`）
---

### #23 | A Fast File System for UNIX (FFS)
**作者**：Marshall Kirk McKusick, William N. Joy, Samuel J. Leffler, Robert S. Fabry
**年份**：1984
**发表**：ACM Transactions on Computer Systems
**摘要**：重新设计 Unix 文件系统，将磁盘利用率从20%提升到约95%，吞吐量提升10倍。引入柱面组（cylinder group）布局和块碎片化（fragment）优化。
**为什么读**：理解文件系统设计的空间局部性原理；ext4/ZFS等现代文件系统都有其影子。
**阅读难度**：⭐⭐⭐（需要OS基础）
**链接**：https://dl.acm.org/doi/10.1145/989.990

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/23_ffs_1984.md`）
---

### #06 | Reflections on Trusting Trust
**作者**：Ken Thompson
**年份**：1984
**发表**：Communications of the ACM（1984年图灵奖演讲）
**摘要**：证明可以在编译器中植入后门，且该后门在源代码中完全不可见。核心论点："你无法信任任何你没有自己创建的代码。"
**为什么读**：安全领域的必读经典；供应链攻击的思想根源；仅3页但石破天惊。
**阅读难度**：⭐（极易读，代码示例清晰）
**链接**：https://dl.acm.org/doi/10.1145/358198.358210

---

## 🌐 计算机网络

### #19 | A Protocol for Packet Network Intercommunication (TCP/IP)
**作者**：Vint Cerf & Bob Kahn
**年份**：1974
**发表**：IEEE Transactions on Communications
**摘要**：提出互联网架构的基本设计：分组交换、网关、端到端可靠性（TCP），以及无状态的IP层。
**为什么读**：互联网底层协议的起源文献；理解"为什么TCP是这样设计的"。
**阅读难度**：⭐⭐（协议描述，需要网络基础）
**链接**：https://www.cs.princeton.edu/courses/archive/fall06/cos561/papers/cerf74.pdf

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/19_tcpip_1974.md`）
---

### #20 | The Design Philosophy of the DARPA Internet Protocols
**作者**：David D. Clark
**年份**：1988
**发表**：SIGCOMM '88
**摘要**：揭示互联网架构背后的设计优先级顺序：可生存性 > 多类型服务 > 多种网络 > 分布式管理 > 成本效率 > 易接入 > 可追责性。
**为什么读**：理解互联网为什么"没有QoS保证"、"没有内置安全性"——这是当年有意为之的选择。
**阅读难度**：⭐⭐（设计哲学讨论，无数学）
**链接**：https://dl.acm.org/doi/10.1145/52324.52336

---

### #27 | The Anatomy of a Large-Scale Hypertextual Web Search Engine (Google)
**作者**：Sergey Brin & Lawrence Page
**年份**：1998
**发表**：Computer Networks, Vol. 30
**摘要**：描述 Google 搜索引擎的架构：PageRank 算法（通过链接结构判断网页权威性）、倒排索引、分布式爬虫。
**为什么读**：现代搜索引擎的理论与工程基础；PageRank 是图论在工业界最著名的应用。
**阅读难度**：⭐⭐（可读性强，算法不复杂）
**链接**：http://infolab.stanford.edu/~backrub/google.html

---

## 🗄️ 数据库

### #03 | A Relational Model of Data for Large Shared Data Banks
**作者**：Edgar F. Codd
**年份**：1970
**发表**：Communications of the ACM
**摘要**：提出关系数据模型——用关系（表）替代层次/网状模型，引入选择/投影/连接等关系代数操作。
**为什么读**：数据库理论的奠基之作；Codd 凭此获1981年图灵奖。
**阅读难度**：⭐⭐⭐（数学符号较多，但核心思想可读）
**链接**：https://dl.acm.org/doi/10.1145/362384.362685

---

## 📡 分布式系统

### #05 | Time, Clocks, and the Ordering of Events in a Distributed System
**作者**：Leslie Lamport
**年份**：1978
**发表**：Communications of the ACM
**摘要**：定义"事件发生在另一事件之前（happens-before）"的偏序关系，引入 Lamport 逻辑时钟。证明分布式系统中无法依赖物理时间确定事件顺序。
**为什么读**：分布式系统理论的起点；Lamport 最重要的论文之一（另一篇是 Paxos）。
**阅读难度**：⭐⭐（概念清晰，数学推导简洁）
**链接**：https://dl.acm.org/doi/10.1145/359545.359563

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/05_lamport_clocks_1978.md`）
---

### #08 | The Byzantine Generals Problem
**作者**：Leslie Lamport, Robert Shostak, Marshall Pease
**年份**：1982
**发表**：ACM Transactions on Programming Languages and Systems
**摘要**：用将军传递命令的类比形式化"恶意节点"下的分布式共识问题。证明 n ≥ 3f+1（f 为叛徒数量）时可达成共识。
**为什么读**：BFT（拜占庭容错）的理论基础；区块链共识机制的直接来源。
**阅读难度**：⭐⭐⭐（逻辑推导严密）
**链接**：https://dl.acm.org/doi/10.1145/357172.357176

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/08_byzantine_generals_1982.md`）
---

### #09 | The Google File System (GFS)
**作者**：Sanjay Ghemawat, Howard Gobioff, Shun-Tak Leung
**年份**：2003
**发表**：SOSP '03
**摘要**：描述 Google 内部大规模分布式文件系统。单 Master + 多 ChunkServer 架构；针对大文件追加写优化；弱化了对并发随机写的支持。
**为什么读**：Hadoop HDFS 的直接原型；学习如何在实际约束下做系统设计决策。
**阅读难度**：⭐⭐（工程论文，可读性强）
**链接**：https://dl.acm.org/doi/10.1145/945445.945450

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/09_gfs_2003.md`）
---

### #10 | MapReduce: Simplified Data Processing on Large Clusters
**作者**：Jeffrey Dean & Sanjay Ghemawat
**年份**：2004
**发表**：OSDI '04
**摘要**：提出 MapReduce 编程模型：将大规模并行计算抽象为 map 和 reduce 两个操作，自动处理分布式执行、错误恢复和负载均衡。
**为什么读**：大数据处理范式的奠基论文；Hadoop 的直接来源；理解批处理系统设计。
**阅读难度**：⭐（易读，举例清晰）
**链接**：https://dl.acm.org/doi/10.5555/1251254.1251264

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/10_mapreduce_2004.md`）
---

### #11 | Dynamo: Amazon's Highly Available Key-value Store
**作者**：Giuseppe DeCandia et al.（Amazon）
**年份**：2007
**发表**：SOSP '07
**摘要**：描述 Amazon Dynamo：为高可用性牺牲强一致性（最终一致性）；一致性哈希环、向量时钟、Merkle 树、Gossip 协议的综合应用。
**为什么读**：NoSQL 和最终一致性设计的范本；Cassandra、Riak 都基于 Dynamo 思想。
**阅读难度**：⭐⭐⭐（涉及多种分布式技术）
**链接**：https://dl.acm.org/doi/10.1145/1294261.1294281

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/11_dynamo_2007.md`）
---

### #12 | Bigtable: A Distributed Storage System for Structured Data
**作者**：Fay Chang et al.（Google）
**年份**：2006
**发表**：OSDI '06
**摘要**：Google 内部结构化数据存储系统。列族（Column Family）数据模型；LSM-Tree 存储结构；支持随机读写与批量扫描的均衡设计。
**为什么读**：HBase、Cassandra 的设计蓝图；理解 NoSQL 列族存储的来龙去脉。
**阅读难度**：⭐⭐（工程论文，清晰）
**链接**：https://dl.acm.org/doi/10.1145/1365815.1365816

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/12_bigtable_2006.md`）
---

### #13 | Paxos Made Simple
**作者**：Leslie Lamport
**年份**：2001
**发表**：ACM SIGACT News
**摘要**：用简单语言重述 Paxos 共识协议（原论文1989年因太"非传统"被拒稿）。分 Prepare/Accept 两阶段，解决单值共识问题，可扩展为 Multi-Paxos。
**为什么读**：分布式共识的核心协议；ZooKeeper、Chubby 的基础。Lamport 说这是他"写过最简单的论文"。
**阅读难度**：⭐⭐（概念清晰，但需要反复思考）
**链接**：https://lamport.azurewebsites.net/pubs/paxos-simple.pdf

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/13_paxos_2001.md`）
---

### #14 | In Search of an Understandable Consensus Algorithm (Raft)
**作者**：Diego Ongaro & John Ousterhout
**年份**：2014
**发表**：USENIX ATC '14
**摘要**：提出 Raft 共识算法，明确以"可理解性"为首要设计目标。通过强 Leader、随机超时选举、日志复制三个机制，实现比 Paxos 更清晰的分布式共识。
**为什么读**：etcd、TiKV、CockroachDB 等主流系统的共识核心；比 Paxos 更适合入门。
**阅读难度**：⭐⭐（结构清晰，图文并茂）
**链接**：https://raft.github.io/raft.pdf

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/15_raft_2014.md`）
---

### #21 | Spanner: Google's Globally-Distributed Database
**作者**：James C. Corbett et al.（Google）
**年份**：2012
**发表**：OSDI '12
**摘要**：Google 全球分布式关系数据库。用 TrueTime API（GPS + 原子钟）提供外部一致性；首次实现全球规模的强一致性事务。
**为什么读**：证明"全球分布式 + ACID"在工程上可行；NewSQL 的理论和实践起点。
**阅读难度**：⭐⭐⭐（需要分布式事务基础）
**链接**：https://dl.acm.org/doi/10.1145/2491245

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/21_spanner_2012.md`）
---

### #22 | Kafka: A Distributed Messaging System for Log Processing
**作者**：Jay Kreps, Neha Narkhede, Jun Rao（LinkedIn）
**年份**：2011
**发表**：EuroSys '11
**摘要**：将"日志"作为分布式系统的核心抽象。顺序写入磁盘（吞吐量接近内存）；消费者维护自己的 offset；支持 replay 和多消费者。
**为什么读**：理解日志在分布式系统中的本质作用；流处理系统（Flink/Spark Streaming）的基础。
**阅读难度**：⭐⭐（工程论文，清晰）
**链接**：https://dl.acm.org/doi/10.1145/1989323.1989385

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/22_kafka_2011.md`）
---

### #28 | Chord: A Scalable Peer-to-peer Lookup Protocol for Internet Applications
**作者**：Ion Stoica et al.（MIT）
**年份**：2001
**发表**：SIGCOMM '01
**摘要**：提出 Chord DHT（分布式哈希表）协议：O(log N) 路由表大小，O(log N) 跳数查找。一致性哈希环 + finger table 的经典实现。
**为什么读**：P2P 和 DHT 的教科书级论文；理解 Dynamo、Cassandra 中一致性哈希的原理。
**阅读难度**：⭐⭐⭐（算法证明较多）
**链接**：https://dl.acm.org/doi/10.1145/383059.383071
**阅读状态**：✅ 已完成（见 `reports/paper_analyses/28_chord_2001.md`）

---

### #C1 | The Chubby Lock Service for Loosely-Coupled Distributed Systems
**作者**：Mike Burrows（Google）
**年份**：2006
**发表**：OSDI '06
**摘要**：描述 Google 内部粗粒度分布式锁服务。5 副本 Paxos cell + 类文件系统接口 + advisory 锁 + 事件通知。强调可用性优先、吞吐量次要。实际部署中最大用途意外变为命名服务而非锁服务。GFS 和 Bigtable 均依赖 Chubby 选主。
**为什么读**：理解 Paxos → 锁服务 → ZooKeeper 演化链路的中间节点；论文完整记录了设计与实际使用的偏差，是分布式系统工程演化的第一手文献。
**阅读难度**：⭐⭐（工程论文，可读性强；需要 Paxos 基础）
**链接**：https://www.usenix.org/legacy/event/osdi06/tech/full_papers/burrows/burrows.pdf
**阅读状态**：✅ 已完成（见 `reports/paper_analyses/29_chubby_2006.md`）

---

## ⚙️ 编程语言与编译器

### #18 | Communicating Sequential Processes (CSP)
**作者**：C.A.R. Hoare
**年份**：1978
**发表**：Communications of the ACM
**摘要**：提出用"通信"而非"共享内存"来实现并发的理论模型。引入 channel 概念，用代数方式描述并发过程的组合与交互。
**为什么读**：Go 语言 goroutine + channel 的理论来源；理解并发的正确思维模式。
**阅读难度**：⭐⭐⭐（形式化符号较多）
**链接**：https://dl.acm.org/doi/10.1145/359576.359585

**阅读状态**：✅ 已完成（见 `reports/paper_analyses/18_csp_1978.md`）
---

### #26 | A New Solution to Dijkstra's Concurrent Programming Problem (Lamport's Bakery Algorithm)
**作者**：Leslie Lamport
**年份**：1974
**发表**：Communications of the ACM
**摘要**：提出面包店算法（Bakery Algorithm）——无需硬件原子指令实现互斥的软件解法，基于"取号等待"的直觉。
**为什么读**：并发编程基础；理解互斥问题的本质和算法解法的设计思路。
**阅读难度**：⭐⭐（逻辑清晰，算法简洁）
**链接**：https://dl.acm.org/doi/10.1145/361082.361093

---

### #29 | LLVM: A Compilation Framework for Lifelong Program Analysis and Transformation
**作者**：Chris Lattner & Vikram Adve
**年份**：2004
**发表**：CGO '04
**摘要**：提出 LLVM：将编译过程解耦为前端（语言特定）、中间表示（IR）、后端（目标平台）。SSA 形式的 IR 使优化分析与目标无关。
**为什么读**：Swift/Rust/Clang 的编译基础；理解现代编译器架构；WebAssembly 工具链的核心。
**阅读难度**：⭐⭐⭐（需要编译器基础）
**链接**：https://dl.acm.org/doi/10.1145/977395.977673

---

## 🔒 安全

### #15 | Bitcoin: A Peer-to-Peer Electronic Cash System
**作者**：Satoshi Nakamoto
**年份**：2008
**发表**：自发布（https://bitcoin.org/bitcoin.pdf）
**摘要**：提出去中心化数字货币系统：工作量证明（PoW）共识、UTXO 模型、Merkle 树交易验证。在不可信网络上实现拜占庭容错的经济机制。
**为什么读**：密码学、博弈论、P2P 网络的综合应用；区块链技术的原始文献。
**阅读难度**：⭐⭐（极简洁，9页）
**链接**：https://bitcoin.org/bitcoin.pdf

---

## 🧰 系统设计哲学

### #07 | No Silver Bullet: Essence and Accidents of Software Engineering
**作者**：Fred Brooks
**年份**：1987
**发表**：IEEE Computer
**摘要**：区分软件开发的"本质复杂性"（来自问题本身）和"偶然复杂性"（来自工具）。论证在未来十年内不存在任何能将生产效率提升一个数量级的技术。
**为什么读**：软件工程哲学必读；理解为什么没有"银弹"——与 AI 辅助编程时代的对话尤为有趣。
**阅读难度**：⭐（可读性极强，无技术门槛）
**链接**：http://worrydream.com/refs/Brooks-NoSilverBullet.pdf

---

### #30 | Hints for Computer System Design
**作者**：Butler Lampson
**年份**：1983
**发表**：SOSP '83
**摘要**：系统设计经验法则的集合：约30条关于接口、实现、性能的工程经验。"Make it fast, make it right, make it small"的设计哲学。
**为什么读**：系统设计者的"葵花宝典"；Lampson 图灵奖获得者的毕生工程智慧浓缩。
**阅读难度**：⭐⭐（格言体，可随机阅读）
**链接**：https://dl.acm.org/doi/10.1145/773379.806614

---

## 按优先级快速通道

```
⭐⭐⭐ 第一批必读（共识度最高）
  #01 Turing (1950)
  #10 MapReduce (2004)
  #05 Lamport Clocks (1978)
  #13 Paxos (2001)
  #14 Raft (2014)
  #16 Goto Harmful (1968)
  #07 No Silver Bullet (1987)
  #30 Hints for System Design (1983)
  #04 UNIX (1974)
  #09 GFS (2003)

⭐⭐ 第二批（领域深化）
  #02 Shannon (1948)
  #03 Codd Relational (1970)
  #11 Dynamo (2007)
  #06 Thompson Trust (1984)
  #19 TCP/IP (1974)
  #27 Google Search (1998)
  #18 CSP (1978)
  #12 Bigtable (2006)
  #22 Kafka (2011)
  #15 Bitcoin (2008)

⭐ 第三批（专题深入）
  #08 Byzantine Generals (1982)
  #17 Hoare Logic (1969)
  #21 Spanner (2012)
  #23 FFS (1984)
  #24 Lisp (1960)
  #26 Bakery Algorithm (1974)
  #28 Chord (2001)
  #29 LLVM (2004)
  #20 Internet Design Philosophy (1988)
```
