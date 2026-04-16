---
title: "Go To Statement Considered Harmful (1968)"
domain: "cs-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-04-16"
---

# 论文深度分析：Go To Statement Considered Harmful

> 分析日期：2026-04-16 | 优先级：⭐ 必读经典（入门级，极短）
> ByteAgent | Task T015

---

## 📋 基本信息卡片

```
论文标题：Go To Statement Considered Harmful
          （原标题投稿为 "A Case Against the GO TO Statement"，编辑 Niklaus Wirth 改为现名）
作者：Edsger W. Dijkstra
机构：Technological University Eindhoven（荷兰埃因霍芬理工大学）
发表年份：1968
发表场所：Communications of the ACM, Vol. 11, No. 3, pp. 147–148
形式：以"读者来信"（Letters to the Editor）形式发表
篇幅：约1.5页（史上最短且最有影响力的CS论文之一）
引用量：数千次（Google Scholar），间接影响无法量化
重要性评级：⭐⭐⭐ 史诗级——结构化编程革命的宣言
```

---

## 🎯 一句话核心贡献

> 通过分析程序员对程序执行进度的认知能力，Dijkstra 论证了 GOTO 语句使程序状态难以追踪，主张以顺序/选择/循环三种结构化控制流彻底替代 GOTO，奠定了现代结构化编程的哲学基础，深刻影响了此后半个世纪所有主流编程语言的控制流设计。

---

## Step 1 | 背景与问题

### 历史节点

1968年是计算机科学的关键分水岭。FORTRAN（1957）和COBOL（1959）普及以来，大量实践表明维护真实程序极其困难：

- **GOTO 无处不在**：早期汇编语言只有跳转指令（JMP），高级语言继承了这一特征。FORTRAN 的 `GO TO`、BASIC 的 `GOTO label` 是核心控制结构。
- **意大利面代码（Spaghetti Code）盛行**：大型程序中控制流跳转如蜘蛛网，难以追踪。
- **软件危机前夜**：1968年的 NATO Software Engineering Conference 正是在讨论日益严重的"软件危机"——项目超期、超预算、质量低劣成为常态。
- **Dijkstra 的前期工作**：他已在 THE 多道程序系统（1968）中实践了结构化设计，积累了第一手经验。

### 核心问题

> 程序员在调试或推理程序时，如何确定程序在任意时刻处于什么状态？

Dijkstra 观察到：程序有两个层次：
1. **静态文本**（the program as written）：程序员写下的代码
2. **动态进程**（the process during execution）：程序实际运行时的状态序列

关键洞察：**如果我们无法轻松地将"程序文本中的某个点"映射到"运行时进程的某个状态"，调试和推理就会变得极其困难。**

### 前人方案的不足

GOTO 的问题在于它切断了文本位置与执行进度之间的对应关系：

- 执行顺序语句时，进度可用行号/语句编号表示（与文本顺序一致）
- 执行循环时，进度需要（语句位置，循环计数器）来描述
- 执行过程调用时，进度是一个动态嵌套的栈
- **GOTO 后**：程序文本顺序与执行顺序完全解耦，进度变为无法用文本坐标静态表达的任意状态

### 论文的核心主张

> **一句话**：GOTO 语句使程序的"动态进度"与"静态文本结构"之间的对应关系遭到破坏，从而使程序正确性的验证和推理变得指数级困难，应当废除。

---

## Step 2 | 技术方案

### 核心思想：进度坐标的可表达性

Dijkstra 用"程序员可以用来描述执行进度的坐标系"作为核心分析框架：

| 控制结构 | 描述进度所需坐标 | 可推理性 |
|----------|-----------------|---------|
| 顺序语句 | 单个行号 | ✅ 极佳 |
| 条件分支（if-else） | 行号 + 分支路径 | ✅ 良好 |
| for/while 循环 | 行号 + 循环变量当前值 | ✅ 可管理（动态但有界） |
| 过程调用（递归） | 调用栈（有界嵌套） | ✅ 可管理 |
| **GOTO** | **任意跳转目标 × 历史路径** | ❌ 无法静态描述 |

关键论证：
- 顺序执行：进度 ≈ 文本位置（一维坐标）
- 循环引入了时间维度，但循环变量提供了有意义的"高维坐标"
- GOTO 引入的是**任意的非局部控制流转移**，进度坐标空间爆炸

### 关键设计：三种充分的控制结构

Dijkstra 引用了 Böhm-Jacopini 定理（1966）的直觉：顺序、选择、重复三种结构在计算上是完备的，GOTO 无需存在。

```
可表达任何算法的最小控制流集合：
  1. 顺序（sequence）：  statement1; statement2; ...
  2. 选择（selection）：  if condition then A else B
  3. 重复（repetition）： while condition do body
```

实践建议：
- 用 `if-then-else` 替代基于 GOTO 的条件跳转
- 用 `while`/`for` 替代基于 GOTO 的循环实现
- 用过程/函数调用替代跨模块的 GOTO

### 权衡分析

| 获得 | 牺牲 |
|------|------|
| 程序状态可静态推理 | 少数场景需多层嵌套跳出（可用异常/break替代） |
| 可组合性：局部推理后可组合全局正确性 | 汇编层面的某些优化机会（1968年非关键） |
| 自文档化：控制结构即是意图的表达 | 极少数性能关键场景的灵活性 |
| 可测试性：单元测试天然对应结构块 | 历史兼容性（已有 GOTO 代码需重构） |

---

## Step 3 | 正确性与复杂性

### 正确性论证

Dijkstra 的论证属于**程序推理的认知复杂性分析**，而非数学证明。核心引理：

**引理（非正式）**：对于程序中任意一点 P，若要判断"是否会到达 P"以及"到达 P 时系统状态是什么"：
- 在纯结构化程序中：仅需考察包含 P 的最内层控制块及其上层嵌套结构（局部性）
- 在含 GOTO 程序中：需考察整个程序中所有可能通过 GOTO 跳转到 P 之前标号的路径（全局性）

这一非形式化论证在1969年被 Tony Hoare 的公理语义（Hoare Logic）体系所形式化，完成了理论闭环。

### 复杂性分析

推理一段含 n 个 GOTO 的程序所需的认知工作量：
- **最坏情况**：O(2^n)（每个 GOTO 都可能为任意目标，路径数指数增长）
- **结构化程序**：O(n)（线性扫描即可理解控制流）

这一对比是 Dijkstra 主张最有力的数量化依据。

### 关键假设

1. 程序的首要目标是可理解性和可维护性，而非最短代码行数
2. 运行时性能不是 1968 年的瓶颈（与今日不同）
3. Böhm-Jacopini 定理保证了表达能力的不损失

---

## Step 4 | 实验评估

### 说明

本论文**没有传统意义上的实验**。这是一篇理论性/哲学性的论证文章，相当于一篇思想实验的论文。

### 间接证据

Dijkstra 提供了两类支持其论点的证据：

1. **经验观察**（全文仅一句，但影响深远）：
   > "For many years I have been familiar with the observation that the quality of programmers is a decreasing function of the density of go to statements in the programs they produce."
   （程序员的质量与他们所写程序中 GOTO 的密度成反比。）
   
   这是作者基于多年教学和工程实践的主观观察，但具有很强的说服力。

2. **理论依据**：引用 Böhm 和 Jacopini 1966 年的论文，证明三种结构足以表达所有计算，为去除 GOTO 提供了可行性基础。

### 局限性

- 缺乏量化实验数据（如代码错误率、调试时间的对比）
- 部分场景（如状态机、错误处理）中 GOTO 仍有一定实用价值（参见后续争论）
- 论文长度仅1.5页，论证密度极高但深度有限，更多细节在后续著作中展开

---

## Step 5 | 演化谱系

### 前驱工作

```
Turing (1950) ──── 计算的形式定义（图灵机）
       │
von Neumann (1945) ─── 存储程序计算机（EDVAC），GOTO 来自汇编 JMP 指令
       │
Böhm & Jacopini (1966) ── 证明了顺序/选择/循环的计算完备性（Dijkstra 引用的理论基础）
       │
Dijkstra (1968) ──── Go To Statement Considered Harmful（结构化编程宣言）
```

### 直接后继

| 时间 | 事件 | 与本文的关系 |
|------|------|------------|
| 1968 | Dijkstra THE OS | 实践验证：大型系统可不用 GOTO |
| 1969 | Hoare Logic | 将 Dijkstra 的直觉形式化为公理语义系统 |
| 1972 | Wirth: Pascal | 语言层面禁止/限制 GOTO，第一个主流"无 GOTO"语言 |
| 1974 | Dijkstra & Hoare: A Discipline of Programming | 结构化编程理论的集大成之作 |
| 1975 | Knuth 的回应论文 "Structured Programming with go to Statements" | CACM，肯定主旨但指出合理 GOTO 用例 |
| 1983 | Ada | 军方强制标准，严格限制 GOTO |
| 1991 | Python | 设计上无 GOTO，`break`/`continue`/`return` 替代 |
| 2000s | 现代 Java/C#/Go | 无裸 GOTO（Go 语言有 `goto` 但强制限制在函数内） |

### 工程落地

**直接影响的语言特性设计**：
- `break` / `continue`：多层循环跳出的结构化替代
- `return` / `throw`：函数提前退出与错误传播的结构化替代
- 异常处理（exception handling）：跨层错误处理的结构化替代
- Rust 的 `loop { break value }`：将 GOTO 能力完全封装在语法糖中

**间接影响**：
- 代码审查（Code Review）文化中"GOTO 是坏味道"的共识
- 圈复杂度（Cyclomatic Complexity）指标：量化控制流复杂度的工程工具
- 编译器的控制流图（CFG）分析：今日编译优化的基础数据结构

---

## Step 6 | 个人理解

### 最重要的洞察

**"程序的静态文本"与"程序的动态执行"之间的对应关系是可理解性的核心。**

Dijkstra 真正天才的贡献不是"GOTO 是坏的"这个结论，而是他提供了一个**分析框架**：可理解性 = 动态进度的可描述性。这个框架解释了为什么：
- 深层嵌套函数比扁平 GOTO 更容易理解（因为调用栈是有序且有界的）
- 异步/并发代码难以理解（进度坐标变成多维，协程/async-await 是解法）
- 递归有时比循环更清晰（递归的进度坐标与数学归纳法同构）

### 类比理解

想象你正在读一本书：
- **顺序阅读**：当前页码完整描述你的位置
- **章节/节/段落嵌套**：像函数调用，任意时刻知道"第2章第3节第1段"
- **GOTO**：相当于书里有随机传送门，读到某处突然跳到第73页，再跳回来，再跳……即使每一页内容都没问题，你的"当前位置"也无法用一个简单的坐标描述

### 疑问记录

- [ ] Knuth (1975) 指出的"合理 GOTO 用例"（如多层跳出）究竟有多大工程价值？今日的异常机制是否完全替代？
- [ ] 现代 Rust 的生命周期检查器是否可以视为 Dijkstra 框架在内存安全领域的延伸？
- [ ] tail call optimization（尾调用优化）是否可以视为"结构化递归"与"性能"之间矛盾的现代解法？

---

## Step 7 | 关联学习

### 前置知识

- [x] 基本编程概念：变量、循环、函数调用
- [x] 汇编语言基础（了解 JMP 指令的来源）
- [ ] Böhm-Jacopini 定理（1966）：为何三种结构足够？

### 延伸阅读

**必读**：
- Dijkstra, E.W. (1972). *Notes on Structured Programming*（结构化编程的理论基础，本文的完整展开）
- Hoare, C.A.R. (1969). "An Axiomatic Basis for Computer Programming"（将本文论证形式化）

**重要补充**：
- Knuth, D.E. (1974). "Structured Programming with go to Statements"（CACM）— 最权威的对立观点，理性讨论 GOTO 的合理用例
- Dijkstra, E.W. (1976). *A Discipline of Programming*（用预条件/后条件正式化结构化推理）

**现代延伸**：
- Martin, R.C. (2008). *Clean Code*（结构化编程原则在现代工程中的应用）
- Rust 语言规范（`?` 操作符、`loop { break }` 等：GOTO 能力的完全结构化封装）

### 知识图谱位置

```
理论基础层：Turing(1950) → Shannon(1948)
                │
编程语言理论层：Dijkstra (1968) ← [本文] ← Böhm&Jacopini(1966)
                │                         │
                ↓                         ↓
        Hoare Logic (1969)         Pascal/Ada 语言设计
                │
        形式验证 → TLA+/Coq/Lean
                         │
        操作系统层：UNIX(1974) ← 结构化编程风格影响
                │
        分布式系统层：Lamport(1978) → ...
```

---

## 原文摘录（精华句）

> "For many years I have been familiar with the observation that the quality of programmers is a decreasing function of the density of go to statements in the programs they produce."
> — Dijkstra, 1968

> "The go to statement as it stands is just too primitive; it is too much an invitation to make a mess of one's program."
> — Dijkstra, 1968

> "My second remark is that our intellectual powers are rather geared to master static relations and that our powers to visualize processes evolving in time are relatively poorly developed."
> — Dijkstra, 1968（这是全文最重要的认知科学洞见）

---

## 附：历史趣闻

1. **标题的由来**：Dijkstra 原本的标题是 "A Case Against the GO TO Statement"，是 CACM 编辑 Niklaus Wirth（Pascal 语言之父）将其改为更有攻击性的 "Go To Statement Considered Harmful"，并开创了 CS 界"X Considered Harmful"命名模式的先河。
2. **Dijkstra 的性格**：他是荷兰人，以观点犀利著称。本文的发表本质上是一封措辞强硬的公开信，而非正式研究论文。
3. **图灵奖**：Dijkstra 于1972年获得图灵奖，部分原因正是本文代表的结构化编程贡献。
4. **后续影响估算**：有人估计，如果以"避免了的 bug 数量"来衡量，本文是CS历史上 ROI 最高的1.5页。

---

## 📊 评分卡

| 维度 | 评分 | 说明 |
|------|------|------|
| 历史影响力 | ⭐⭐⭐⭐⭐ | 改变了此后所有编程语言的设计 |
| 技术深度 | ⭐⭐⭐ | 主要是哲学论证，数学深度有限 |
| 可读性 | ⭐⭐⭐⭐⭐ | 1.5页，今日仍可在15分钟内读完 |
| 工程实践价值 | ⭐⭐⭐⭐⭐ | 每位程序员每天都在受益 |
| 学习优先级 | P2 | 非CS从业者也应了解，从业者必读 |
