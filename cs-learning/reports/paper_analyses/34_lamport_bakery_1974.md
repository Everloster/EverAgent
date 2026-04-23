---
title: "A New Solution to Dijkstra's Concurrent Programming Problem (Bakery Algorithm)"
domain: "cs-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-04-22"
---

# 34 | Lamport (1974) Bakery Algorithm 分析报告

**作者**：Leslie Lamport
**年份**：1974
**发表**：Communications of the ACM, Vol. 17, No. 8, pp. 453-455
**分析日期**：2026-04-22
**阅读难度**：⭐⭐（逻辑清晰，算法简洁，但并发推理需要仔细思考）

---

## TL;DR（一段话总结）

Lamport 在 1974 年提出的面包店算法（Bakery Algorithm）是并发编程领域的一座里程碑：它首次证明了**在不依赖任何硬件原子指令**的情况下，仅通过读写普通内存即可实现多进程互斥（mutual exclusion）。算法模拟了面包店取号排队的直觉——每个进程进入临界区前先取一个号码，号码小的先服务，号码相同时按进程编号排序。这篇论文不仅解决了一个具体的并发问题，更深刻地揭示了并发算法设计的本质：互斥问题的根源在于信息的局部性，而解决之道在于建立全局可比较的排序。

---

## Step 1 | 论文定位（背景与问题）

### 历史节点

1970 年代初，多处理器系统和多道程序操作系统开始兴起，并发编程从理论走向实践。1965 年，Dijkstra 在"Cooperating Sequential Processes"中首次形式化描述了互斥问题（mutual exclusion），并提出了基于原子操作（test-and-set）的解决方案。然而，当时的计算机硬件架构各异，许多系统并不提供原子读写指令。

1966 年，Dijkstra 提出了一个公开挑战：能否设计一个**不依赖硬件原子指令**的互斥算法？这一挑战在并发编程领域被称为"Dijkstra 的并发编程问题"。

### 核心问题

Lamport 要解决的核心问题是：

> **在仅提供普通读写操作（read/write）的共享内存模型下，如何实现 N 个进程之间的互斥访问临界区？**

具体来说，需要满足三个经典性质：
1. **互斥性（Mutual Exclusion）**：任意时刻最多只有一个进程在临界区内
2. **无死锁（Freedom from Deadlock）**：如果多个进程都想进入临界区，至少有一个能成功进入
3. **无饥饿（Freedom from Starvation）**：每个请求进入临界区的进程最终都能进入

### 前人方案的不足

在 Lamport 之前，已有若干尝试解决此问题的算法：

- **Dekker 算法**（1965，Dijkstra 改进）：仅适用于 2 个进程，扩展到 N 进程极其复杂
- **Peterson 算法**（1981，实际上晚于 Bakery）：也仅适用于 2 个进程
- **Dijkstra 的第三算法**：使用一个共享变量和忙等待，但证明复杂且不易理解
- **Knuth (1966)** 和 **de Bruijn (1967)**：提出了 N 进程解法，但算法复杂，且部分方案需要更强的硬件假设

这些方案要么限制于 2 个进程，要么算法过于复杂难以理解和验证。

### 论文的核心主张

> **一句话**：通过模拟面包店"取号-等待-叫号"的直觉机制，仅使用普通读写内存操作即可实现满足互斥、无死锁、无饥饿的 N 进程并发控制算法。

---

## Step 2 | 技术方案（How it works）

### 核心思想

面包店算法的灵感来自真实面包店的排队机制：
1. 顾客进门时取一个号码（通常是目前最大号码 + 1）
2. 顾客等待，直到自己的号码是当前最小的
3. 号码相同时（同时取号），顾客编号小的优先
4. 服务完成后，顾客丢弃号码

Lamport 将这个直觉转化为分布式算法，关键洞察在于：**即使没有原子操作，进程仍然可以通过读写共享变量来建立一个全局可比较的排序。**

### 关键设计：算法结构

#### 共享数据结构

```
choosing: array[1..N] of boolean   // 进程 i 正在取号
number:   array[1..N] of integer   // 进程 i 的号码，0 表示不在等待
```

#### 进入临界区（Entry Section）

```
# Step 1: 取号
choosing[i] := true
number[i] := 1 + max(number[1], number[2], ..., number[N])
choosing[i] := false

# Step 2: 等待所有其他进程
for j := 1 to N, j ≠ i:
    # 等待进程 j 完成取号
    while choosing[j] do skip
    
    # 等待进程 j 的号码比自己大，或进程 j 不在等待
    while number[j] ≠ 0 and (number[j], j) < (number[i], i) do skip
```

#### 退出临界区（Exit Section）

```
number[i] := 0
```

### 关键设计决策与权衡

| 设计决策 | 原因 | 代价 |
|----------|------|------|
| `choosing` 标志 | 防止读取到正在取号进程的中间状态 | 增加一轮忙等待 |
| 元组比较 `(number, pid)` | 解决同时取号导致的号码冲突 | 需要比较两个字段 |
| `number` 可能无限增长 | 理论简洁性 | 实际中需要处理溢出（Lamport 证明在合理假设下不会溢出） |
| 纯软件实现 | 不依赖硬件原子指令 | 忙等待（busy waiting）消耗 CPU |

### 为什么不需要原子指令？

这是 Bakery 算法最精妙之处。考虑进程 `i` 读取进程 `j` 的 `number[j]`：
- 如果 `j` 不在取号（`choosing[j] = false`），则 `number[j]` 是稳定的
- 如果 `j` 正在取号（`choosing[j] = true`），则 `i` 等待直到 `j` 完成

因此，**任何进程读取到的 `number[j]` 都是某个完整取号操作后的结果**，不会出现读取到"半个号码"的情况。

---

## Step 3 | 正确性证明

### 互斥性证明（Mutual Exclusion）

**核心引理**：如果进程 `i` 在临界区内，进程 `j`（`j ≠ i`）正在尝试进入，则 `j` 最终会看到 `(number[i], i) < (number[j], j)`。

**证明思路**：
1. 当 `i` 进入临界区时，`number[i] > 0`
2. `j` 在第二轮等待中会检查 `number[i]`
3. 如果 `j` 在 `i` 取号之后取号，则 `number[j] > number[i]`，因此 `(number[i], i) < (number[j], j)`
4. 如果 `j` 在 `i` 取号之前取号，则 `i` 在进入临界区前已经等待 `j` 完成（因为 `i` 看到了 `number[j]` 和 `choosing[j] = false`），因此 `j` 要么已在临界区（矛盾），要么 `number[j] = 0`
5. 如果 `number[i] = number[j]`（同时取号），则按进程编号 `i < j` 或 `j < i` 决定顺序

### 无死锁证明

假设所有进程都在尝试进入临界区。设 `i` 是其中 `number` 最小（或 `number` 相同但 `pid` 最小）的进程。那么对于任何其他进程 `j`，要么：
- `number[j] = 0`（`j` 不想进入），或
- `number[j] > number[i]`，或
- `number[j] = number[i]` 但 `j > i`

因此 `i` 的等待条件对所有 `j` 都满足，`i` 可以进入临界区。

### 无饥饿证明

假设进程 `i` 正在等待进入。在它取号之后，只有有限个进程能在它之前进入临界区：
1. 已经取号且 `(number, pid) < (number[i], i)` 的进程
2. 之后取号但 `number` 更小的进程不可能存在（因为 `i` 取号时已经读取了所有当前号码）

因此最多 `N-1` 个进程能在 `i` 之前进入，之后 `i` 必定能进入。

### 关键假设

1. **内存一致性**：读写操作按程序顺序执行（sequential consistency）
2. **有限进程数**：`N` 是固定的有限值
3. **非零读取**：进程读取其他进程的 `number` 时，不会读到取号过程中的中间值（由 `choosing` 标志保证）

---

## Step 4 | 实验评估

### 实验设计

与 Hoare (1969) 类似，Bakery Algorithm 是一篇**理论论文**，没有传统实验。论文的验证方式是：

1. **形式化证明**：为互斥性、无死锁、无饥饿三个性质提供严格的数学证明
2. **算法简洁性**：整个算法仅约 10 行伪代码，易于理解和实现
3. **无硬件依赖**：明确声明不依赖任何原子操作

### 关键结果

论文的核心"结果"是证明了以下定理：

> **定理**：Bakery Algorithm 满足互斥性、无死锁和无饥饿三个性质，且仅使用普通读写内存操作。

这是计算机科学中少有的"存在性证明"——它证明了某种看似不可能的事情实际上是可能的。

### 局限性

1. **忙等待（Busy Waiting）**：进程等待时持续消耗 CPU 周期，效率低下
2. **内存流量大**：每个进程进入临界区需要读取所有其他进程的 `choosing` 和 `number`，共 `2(N-1)` 次内存访问
3. **号码溢出**：理论上 `number` 可以无限增长（虽然 Lamport 论证在实际中不会溢出）
4. **缓存不友好**：频繁读取共享数组导致缓存一致性流量（cache coherence traffic）
5. **仅适用于共享内存模型**：不直接适用于消息传递（message passing）系统

---

## Step 5 | 演化谱系（Impact & Lineage）

### 前驱工作

```
Dijkstra (1965) "Cooperating Sequential Processes"
    ↓ 首次形式化互斥问题，提出基于原子操作的解决方案
Dijkstra (1966) 公开挑战
    ↓ 提出"能否不用原子指令实现互斥？"
Knuth (1966), de Bruijn (1967)
    ↓ 提出复杂的 N 进程解法
Lamport (1974) "A New Solution to Dijkstra's Concurrent Programming Problem"
    ↓ 简洁优雅的 Bakery Algorithm，纯软件实现
```

### 直接后续发展

```
Bakery Algorithm (1974)
    ├── Peterson (1981) "Myths about the Mutual Exclusion Problem"
    │       └── 提出更简洁的 2 进程 Peterson 算法，并澄清并发算法中的常见误解
    ├── Lamport (1979) "A New Approach to Proving the Correctness of Multiprocess Programs"
    │       └── 引入状态机方法证明并发算法正确性
    ├── Lamport (1986) "The Mutual Exclusion Problem"
    │       └── 系统综述互斥问题的各种解法，包括 Bakery 的改进版本
    ├── Taubenfeld (2004) "The Black-White Bakery Algorithm"
    │       └── 改进版 Bakery，使用有界计数器解决号码溢出问题
    └── 现代互斥原语
            ├── Test-and-Set / Compare-and-Swap（硬件原子指令）
            ├── 信号量（Semaphore, Dijkstra 1965）
            ├── 互斥锁（Mutex）
            └── 读写锁（Read-Write Lock）
```

### 工程落地与现代替代品

| 机制 | 与 Bakery 的关系 | 现代应用 |
|------|-----------------|----------|
| **Test-and-Set** | 硬件原子指令，Bakery 试图避免依赖 | 现代 CPU 标配，用于实现自旋锁 |
| **Compare-and-Swap (CAS)** | 更强大的原子原语 | x86 的 `LOCK CMPXCHG`，用于无锁数据结构 |
| **Ticket Lock** | 受 Bakery "取号"思想启发 | Linux 内核自旋锁实现 |
| **MCS Lock** | 解决 Bakery 的缓存不友好问题 | 现代操作系统和数据库内核 |
| **Futex** | 结合自旋和休眠 | Linux 用户态锁优化 |

### 学术影响

- **并发算法设计范式**：Bakery 算法展示了如何将现实直觉（取号排队）转化为分布式算法
- **形式化验证需求**：算法的正确性证明推动了并发程序验证方法的发展
- **内存模型研究**：Bakery 对内存一致性的假设促使研究者深入探索弱内存模型（weak memory models）下的算法设计
- **Lamport 的学术地位**：这是 Lamport 早期最重要的论文之一，奠定了他在分布式系统领域的宗师地位（后续还有逻辑时钟、Paxos、TLA+ 等里程碑工作）

---

## Step 6 | 个人理解

### 最重要的洞察

Bakery 算法最深刻的价值在于它揭示了一个**反直觉的事实**：

> 互斥问题不需要硬件提供原子性——它只需要进程之间能够建立一种**全局可比较的排序**。

原子操作（如 test-and-set）只是实现这种排序的一种便捷方式，但不是唯一方式。Lamport 通过"取号"机制，用纯软件在异步系统中建立了这种排序。

### 为什么它能成功

1. **直觉的力量**：面包店排队的类比极其自然，使得算法易于理解和记忆
2. **极简主义**：仅使用两个数组（`choosing` 和 `number`），没有复杂的数据结构
3. **通用性**：适用于任意有限数量的进程
4. **教学价值**：至今仍是操作系统和并发编程课程的经典教材案例

### 类比理解

想象一个没有叫号机的银行大厅：
- **传统互斥（test-and-set）**：银行有一个专门的叫号机（硬件原子操作），每次只能一个人按按钮取号
- **Bakery 算法**：银行没有叫号机，但每个人进门时大声喊"我要取号了！"（`choosing[i] = true`），然后自己看目前最大的号码并加 1（`number[i] = max + 1`），再喊"我取完号了！"（`choosing[i] = false`）。其他人通过听喊声和看大家手里的号码来判断谁先办理。

关键在于：虽然没有叫号机（原子操作），但"大声喊"（`choosing` 标志）确保了所有人看到的号码都是完整的、非中间的。

### 疑问记录

- [ ] 在现代弱内存模型（如 ARM 的 relaxed memory model）下，Bakery 算法是否仍然正确？是否需要内存屏障（memory fence）？
- [ ] 如果进程数 `N` 动态变化（进程可以随时创建和销毁），Bakery 算法需要如何修改？
- [ ] Bakery 算法的"公平性"（FIFO）与性能之间存在什么 trade-off？现代 Ticket Lock 如何平衡这两者？

---

## Step 7 | 关联学习

### 前置知识

- [ ] Dijkstra (1965) "Cooperating Sequential Processes" — 理解互斥问题的起源和经典性质
- [ ] 基本并发概念：临界区、竞态条件（race condition）、死锁、饥饿
- [ ] 共享内存模型与缓存一致性基础

### 延伸阅读

- [ ] Peterson (1981) "Myths about the Mutual Exclusion Problem" — 2 进程互斥的经典解法
- [ ] Lamport (1978) "Time, Clocks, and the Ordering of Events in a Distributed System" — Lamport 的另一篇里程碑论文，happens-before 关系
- [ ] Herlihy & Shavit (2008) "The Art of Multiprocessor Programming" — 现代并发编程的权威教材
- [ ] Taubenfeld (2004) "The Black-White Bakery Algorithm" — 解决号码溢出的改进版本
- [ ] Lamport (2011) "Teaching Concurrency" — Lamport 对并发教育的思考

### 知识图谱位置

```
分布式系统与并发
    ├── 理论基础
    │       ├── Turing 可计算性 (1950)
    │       └── Hoare 逻辑 (1969)
    ├── 并发控制
    │       ├── Dijkstra 互斥问题 (1965)
    │       ├── Bakery Algorithm (1974)  ← 当前位置
    │       ├── Peterson Algorithm (1981)
    │       └── 现代锁原语 (Ticket Lock / MCS Lock / Futex)
    ├── 分布式共识
    │       ├── Lamport 逻辑时钟 (1978)
    │       ├── Byzantine Generals (1982)
    │       ├── Paxos (2001)
    │       └── Raft (2014)
    └── 形式化验证
            ├── TLA+ (1999)
            └── 并发分离逻辑 (2007)
```

---

## 原文摘录（精华句）

> "The algorithm is modeled after the protocol used in bakeries, in which a customer takes a number upon entering the store, and waits until his number is called."
> — Leslie Lamport, 1974

---

## 参考链接

- 原文：https://dl.acm.org/doi/10.1145/361082.361093
- Lamport 个人网站（含所有论文）：https://lamport.azurewebsites.net/pubs/pubs.html
- Taubenfeld 改进版 Black-White Bakery：https://dl.acm.org/doi/10.1145/1011768.1011773
