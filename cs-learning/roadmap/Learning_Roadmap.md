# 计算机科学系统学习路径

> Phase 1-6 阶梯式课程 + 专题深入模块
> 创建日期：2026-03-24

---

## 学习前的自我定位

```
CS零基础，想系统入门          →  从 Phase 1 开始，配合时间线文档
有编程基础（1门语言）          →  直接进入 Phase 2，补充 Phase 1 的理论部分
大学修过数据结构与算法         →  从 Phase 3 开始，审查 Phase 2 的薄弱点
有系统编程经验（C/C++/Rust）   →  从 Phase 4 开始（分布式 + 数据库）
有明确的深化方向               →  直接进入 Phase 5 或 Phase 6 的专题模块
```

---

## Phase 1：计算理论与编程基础（4-6周）

### 学习目标
- 理解计算的本质：什么是"可计算的"？
- 掌握至少一门系统编程语言（推荐 C 或 Python）
- 建立算法复杂性的直觉

### 第1-2周：计算理论基础

**核心概念**：
1. 图灵机模型 → 理解"算法"的精确定义
2. Church-Turing 论题 → Lambda 演算与图灵机的等价性
3. 停机问题（Halting Problem）→ 有些问题在原理上无法被算法解决
4. 复杂性入门：P vs NP 的直觉理解

**推荐阅读**：
- Turing (1950)《Computing Machinery and Intelligence》（短，可读性强）
- SICP 第1章（Scheme/Python）

**学习要点**：
- 区分"算法"与"程序"：算法是抽象的计算过程，程序是算法的具体实现
- 理解"可判定性"：某些问题即使有无限时间也无法被算法解决
- 图灵完备性：一个语言能模拟图灵机，就能做任何可计算的事

### 第3-4周：编程语言基础与抽象

**核心概念**：
1. 高阶函数与 Lambda 演算的关系
2. 递归 vs 迭代的本质区别
3. 类型系统入门（静态 vs 动态、强类型 vs 弱类型）
4. 内存模型：堆、栈、作用域

**推荐阅读**：
- SICP 第2-3章
- K&R《The C Programming Language》第1-4章

**学习要点**：
- 闭包（Closure）：函数"记住"其创建时的环境
- 尾递归优化：将递归转为循环的编译器技术
- 理解为什么 C 没有垃圾回收：手动内存管理的代价与收益

### 第5-6周：信息论入门

**核心概念**：
1. 信息熵：衡量信息量的数学工具
2. 编码理论：如何用最少的比特表示信息
3. 压缩算法原理（Huffman 编码）

**推荐阅读**：
- Shannon (1948)《A Mathematical Theory of Communication》（第1-3节）

---

## Phase 2：数据结构与算法（6-8周）

### 学习目标
- 掌握核心数据结构及其适用场景
- 理解经典算法的设计思想（不是死记硬背）
- 能够分析算法时间与空间复杂度

### 第1-2周：基础数据结构

**核心数据结构**：
- 数组 & 链表 → 顺序存储 vs 链式存储的权衡
- 栈 & 队列 → LIFO / FIFO 的应用场景
- 哈希表 → 散列函数、冲突解决、装载因子
- 树 → 二叉树、BST、堆

**关键实现**：
```
每种数据结构必须手写实现一遍（推荐用 C 或 Java）
重点：理解指针操作与内存布局
```

### 第3-4周：图论与高级数据结构

**图算法**：
- BFS / DFS → 遍历的本质是什么？
- Dijkstra 最短路径 → 贪心策略
- Bellman-Ford → 动态规划视角
- 最小生成树（Kruskal / Prim）

**高级数据结构**：
- 红黑树 → 为什么数据库索引用 B-Tree 而不是红黑树？
- B-Tree / B+ Tree → 磁盘友好的树结构
- 跳表（Skip List）→ Redis Sorted Set 的实现基础
- 并查集（Union-Find）

### 第5-6周：经典算法设计范式

**四大范式**：
1. **分治（Divide & Conquer）**：归并排序、快速排序、FFT
2. **动态规划（DP）**：最长公共子序列、背包问题、矩阵链乘法
3. **贪心（Greedy）**：活动选择、Huffman 编码
4. **回溯（Backtracking）**：N皇后、图着色

**CLRS 精读章节（推荐）**：
- 第4章：递归与主定理
- 第15章：动态规划（必读）
- 第22-25章：图算法

### 第7-8周：算法复杂性深化

**核心主题**：
- 摊还分析（Amortized Analysis）：动态数组扩容的真实代价
- P / NP / NP-Complete / NP-Hard 的严格定义
- 近似算法：当精确解不可行时
- 随机算法：用概率换取效率

---

## Phase 3：系统核心（8-10周）

> 重点：**操作系统 + 计算机网络** 是理解所有上层系统的基础

### 第1-3周：操作系统原理

**核心概念**：
1. **进程与线程**：虚拟化CPU的两种粒度
2. **内存管理**：虚拟内存、页表、TLB
3. **文件系统**：inode 结构、块分配、日志文件系统
4. **I/O子系统**：中断、DMA、设备驱动
5. **同步原语**：锁、信号量、条件变量、死锁检测

**实战（强烈推荐）**：
- MIT 6.S081 操作系统实验（基于 xv6，一个教学用 Unix）
- 实验内容：实现 fork/exec、实现页表、实现文件系统

**推荐阅读**：
- Ritchie & Thompson (1974)《The UNIX Time-Sharing System》
- McKusick et al. (1984)《A Fast File System for UNIX》
- OSTEP（Operating Systems: Three Easy Pieces）—— 免费在线，极佳

### 第4-5周：计算机体系结构

**核心概念**：
1. **冯·诺依曼架构**：CPU、内存、总线的交互模型
2. **指令集架构（ISA）**：x86 vs ARM vs RISC-V
3. **流水线与分支预测**：CPU如何提高吞吐量
4. **缓存层次结构**：L1/L2/L3 Cache 与 Cache Miss
5. **内存一致性模型**：为什么多核程序会有"可见性"问题

**关键洞察**：
- 理解"内存墙"：CPU 速度增长远快于内存带宽增长，这是现代系统设计的核心矛盾
- 掌握局部性原理（时间局部性 / 空间局部性）：这是所有缓存机制的理论基础

### 第6-8周：计算机网络

**分层模型（自底向上）**：
1. **物理层**：信号、编码
2. **数据链路层**：以太网、MAC 地址、ARP
3. **网络层**：IP 协议、路由算法（OSPF/BGP）
4. **传输层**：TCP（可靠传输）vs UDP（低延迟）
5. **应用层**：HTTP/HTTPS、DNS、TLS

**TCP 深度理解**（重点）：
- 三次握手 / 四次挥手的设计理由
- 拥塞控制（AIMD、慢启动、CUBIC）
- 可靠性保证：序列号、ACK、重传

**推荐阅读**：
- Cerf & Kahn (1974)《A Protocol for Packet Network Intercommunication》
- Clark (1988)《The Design Philosophy of the DARPA Internet Protocols》

### 第9-10周：数据库原理

**核心概念**：
1. **关系模型**：Codd 的十二条规则、规范化理论
2. **SQL 执行引擎**：查询解析、执行计划、优化器
3. **存储结构**：B-Tree 索引、堆文件、行存 vs 列存
4. **事务与 ACID**：原子性、一致性、隔离性、持久性
5. **并发控制**：2PL（两阶段锁）、MVCC（多版本并发控制）
6. **恢复机制**：WAL（Write-Ahead Logging）、Redo/Undo

**推荐阅读**：
- Codd (1970)《A Relational Model of Data》

---

## Phase 4：分布式系统（6-8周）

> 核心问题：**多台机器如何像一台机器一样工作？**

### 第1-2周：分布式系统基础理论

**核心定理**：
- **CAP 定理**：Consistency / Availability / Partition Tolerance 三选二
- **FLP 不可能定理**：在异步网络中，无法同时做到安全性和活性
- **PACELC 模型**：CAP 的延伸——即使没有分区，也存在延迟与一致性的权衡

**时序问题**：
- Lamport 时钟 → 逻辑时钟的基本思想
- 向量时钟（Vector Clock）→ 捕捉因果关系
- 全序广播（Total Order Broadcast）→ 分布式一致性的核心原语

**推荐阅读**：
- Lamport (1978)《Time, Clocks, and the Ordering of Events》

### 第3-4周：共识算法

**Paxos**：
- Basic Paxos：单值共识的实现
- Multi-Paxos：连续共识的工程化
- 理解为什么 Paxos 难以理解（并发、失败、网络分区的组合）

**Raft**（推荐先学）：
- Leader 选举 → 集群如何在 Leader 失败后恢复
- 日志复制 → 如何保证所有节点的日志一致
- 成员变更 → 如何安全地增减节点

**推荐阅读**：
- Lamport (2001)《Paxos Made Simple》
- Ongaro & Ousterhout (2014)《In Search of an Understandable Consensus Algorithm》

### 第5-6周：经典分布式系统设计

**存储系统**：
- GFS → 大文件顺序读写的设计哲学
- Bigtable → 结构化数据的列族存储
- Dynamo → 高可用优先、最终一致性

**计算系统**：
- MapReduce → 批处理计算的抽象
- Kafka → 日志作为分布式系统的中枢

**推荐阅读**（按优先级）：
1. Dean & Ghemawat (2004)《MapReduce》
2. Ghemawat et al. (2003)《The Google File System》
3. DeCandia et al. (2007)《Dynamo》

### 第7-8周：现代分布式数据库

**核心主题**：
- 分布式事务：2PC（两阶段提交）的局限性
- Spanner：用 TrueTime 实现全球强一致性
- NewSQL：在分布式环境下重获 ACID
- CRDT（无冲突可复制数据类型）：乐观并发的数学基础

---

## Phase 5：编程语言理论（4-6周）

### 第1-2周：语言设计基础

**核心概念**：
1. 语法（Syntax）vs 语义（Semantics）vs 语用（Pragmatics）
2. 操作语义 / 指称语义 / 公理语义
3. Hoare Logic：程序正确性的形式化证明
4. 类型系统：Hindley-Milner 类型推断

**推荐阅读**：
- McCarthy (1960)《Recursive Functions of Symbolic Expressions (Lisp)》
- Hoare (1969)《An Axiomatic Basis for Computer Programming》

### 第3-4周：编译器原理

**编译流程**：
```
源代码 → 词法分析 → 语法分析 → 语义分析 → 中间代码（IR）→ 优化 → 目标代码
```

**关键技术**：
1. 词法分析：正则表达式 + 有限自动机（DFA/NFA）
2. 语法分析：LL(1) / LR(1) 解析器
3. 中间表示（IR）：SSA 形式（静态单赋值）
4. 编译优化：常量折叠、死代码消除、循环优化
5. 目标代码生成：寄存器分配（图着色算法）

**推荐阅读**：
- Lattner & Adve (2004)《LLVM》
- Dragon Book（编译原理，第1-4章）

### 第5-6周：现代语言设计

**Rust 的类型系统革命**：
- 所有权（Ownership）与借用（Borrowing）
- 生命周期（Lifetime）
- 内存安全 without GC 的数学基础

**函数式编程实践**：
- Haskell 的 Monad：处理副作用的纯函数式方法
- 类型类（Type Class）vs 面向对象的继承

---

## Phase 6：系统安全（4-6周）

### 第1-2周：密码学基础

**核心概念**：
1. 对称加密（AES）vs 非对称加密（RSA / ECC）
2. 哈希函数：单向性、碰撞抵抗
3. 数字签名：不可否认性
4. TLS/SSL：互联网安全通信的基础

### 第3-4周：系统安全

**经典攻击类型**：
- 缓冲区溢出（Stack Overflow）→ 栈金丝雀（Stack Canary）的防御
- 格式化字符串漏洞
- SQL 注入 / XSS / CSRF

**信任链问题**：
- Thompson (1984)《Reflections on Trusting Trust》
- 供应链攻击（SolarWinds 等）的现实映射

### 第5-6周：网络安全

**核心主题**：
- 认证 vs 授权（Authentication vs Authorization）
- PKI（公钥基础设施）与证书链
- 常见网络攻击：DDoS、中间人攻击（MITM）
- 零信任安全模型（Zero Trust Architecture）

---

## 专题深入模块（Phase 7+，持续进行）

```
方向A：云计算与容器化
  → Docker / Kubernetes 原理
  → Serverless 架构设计
  → 服务网格（Service Mesh）

方向B：形式化方法与程序验证
  → Coq / Isabelle 证明助手
  → TLA+ 系统规范
  → 并发程序的模型检查

方向C：高性能计算
  → SIMD / GPU 编程
  → 缓存友好的算法设计
  → 无锁（Lock-free）数据结构

方向D：编程语言设计
  → 实现一个小型解释器
  → 类型系统理论深化
  → JIT 编译技术

方向E：存储系统深化
  → LSM-Tree vs B-Tree 的工程权衡
  → 日志结构文件系统（LFS）
  → NVM（非易失性内存）对存储设计的影响
```

---

## 推荐学习资源总览

### 在线课程（免费）
| 课程 | 机构 | 适合阶段 |
|------|------|---------|
| MIT 6.S081 操作系统 | MIT | Phase 3 |
| MIT 6.824 分布式系统 | MIT | Phase 4 |
| CS 61A SICP | UC Berkeley | Phase 1 |
| CS 61B 数据结构 | UC Berkeley | Phase 2 |
| Nand to Tetris | 希伯来大学 | Phase 1-3 |

### 必读书籍（精选）
见 [BOOKS_INDEX.md](../books/BOOKS_INDEX.md)

### 论文精读路径
见 [PAPERS_INDEX.md](../papers/PAPERS_INDEX.md)

---

*"The best performance improvement is the transition from the nonworking state to the working state." — John Ousterhout*
