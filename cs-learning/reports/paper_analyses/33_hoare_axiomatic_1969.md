---
title: "An Axiomatic Basis for Computer Programming"
domain: "cs-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-04-22"
---

# 33 | Hoare (1969) An Axiomatic Basis for Computer Programming 分析报告

**作者**：C.A.R. Hoare (Tony Hoare)
**年份**：1969
**发表**：Communications of the ACM, Vol. 12, No. 10, pp. 576-580
**分析日期**：2026-04-22
**阅读难度**：⭐⭐⭐（形式化推理，需要逻辑基础）

---

## TL;DR（一段话总结）

Hoare 在 1969 年的这篇论文中首次提出了以他的名字命名的"Hoare 逻辑"（Hoare Logic），用形式化的三元组 `{P} C {Q}` 将程序正确性证明转化为数学推导。论文引入了赋值公理、顺序组合规则、条件规则、while 循环规则等一套完整的推理系统，使得程序员可以像数学家证明定理一样证明程序的正确性。这项工作奠定了程序验证（Program Verification）的理论基础，直接催生了形式化方法这一整个学科方向，影响了后续从 Floyd、Dijkstra 到现代 TLA+、Coq、Isabelle 等工具的发展。

---

## Step 1 | 论文定位（背景与问题）

### 历史节点

1960 年代末，软件危机（Software Crisis）初现端倪。随着计算机硬件能力的提升，软件系统的规模和复杂度急剧增长，而保证程序正确性的主要手段仍然是人工测试和调试。1968 年 NATO 会议首次提出"软件工程"概念，标志着学术界和工业界开始系统性地思考如何控制软件复杂度。

在这一背景下，形式化方法逐渐兴起：
- 1967 年，Robert Floyd 在《Assigning Meanings to Programs》中首次提出用归纳断言（inductive assertions）验证流程图程序的方法
- 1968 年，Dijkstra 发表《Go To Statement Considered Harmful》，推动结构化编程革命
- 1969 年，Hoare 在本论文中进一步将 Floyd 的思想形式化为一套公理系统

### 核心问题

Hoare 明确要解决的核心问题是：**如何像数学证明定理一样，形式化地证明一个程序的正确性？**

具体来说，他追问：
1. 能否为程序设计语言定义一套公理和推理规则？
2. 能否从程序的规格说明（specification）出发，通过逻辑推导证明程序满足该规格？
3. 这套方法是否足够通用，能覆盖赋值、顺序执行、条件分支、循环等所有基本控制结构？

### 前人方案的不足

Floyd (1967) 的方法虽然开创性地引入了归纳断言，但存在以下局限：
- 基于流程图（flowchart）表示，与当时新兴的结构化编程思想不够契合
- 缺乏一套清晰的公理化体系，证明过程较为 ad-hoc
- 没有将程序验证与程序设计语言语义系统性地联系起来

### 论文的核心主张

> **一句话**：程序正确性可以被形式化为数学公理系统，通过前置条件、后置条件和一组推理规则，实现对程序行为的严格证明。

---

## Step 2 | 技术方案（How it works）

### 核心思想

Hoare 逻辑的核心思想是将程序语句视为**状态转换器**，并用**断言（assertion）**描述程序状态。一个程序语句 `C` 的正确性被表达为一个三元组：

```
{P} C {Q}
```

其中：
- `P` 是前置条件（precondition）：执行 `C` 之前必须满足的条件
- `C` 是程序语句（command）
- `Q` 是后置条件（postcondition）：执行 `C` 之后保证满足的条件

这个三元组的直观含义是：**如果在执行 `C` 之前 `P` 成立，且 `C` 终止，则在执行之后 `Q` 成立。**

### 关键设计：公理与推理规则

Hoare 为每种程序结构定义了对应的公理或推理规则：

#### 1. 赋值公理（Assignment Axiom）

```
{P[E/x]} x := E {P}
```

含义：如果 `P` 在将 `E` 的值代入 `x` 后成立，那么执行赋值 `x := E` 后 `P` 成立。

这是 Hoare 逻辑中最基础、最巧妙的公理。它通过"逆向代入"的方式，从后置条件推导前置条件。

#### 2. 顺序规则（Sequential Composition Rule）

```
{P} C1 {R}    {R} C2 {Q}
-------------------------
      {P} C1; C2 {Q}
```

含义：如果 `C1` 将 `P` 转换为 `R`，`C2` 将 `R` 转换为 `Q`，则顺序执行 `C1; C2` 将 `P` 转换为 `Q`。

#### 3. 条件规则（Conditional Rule）

```
{P ∧ B} C1 {Q}    {P ∧ ¬B} C2 {Q}
----------------------------------
      {P} if B then C1 else C2 {Q}
```

含义：无论条件 `B` 为真或为假，只要对应分支都能将 `P`（结合 `B` 或 `¬B`）转换为 `Q`，则整个条件语句满足 `{P} ... {Q}`。

#### 4. While 循环规则（While Rule）

```
{P ∧ B} C {P}
-------------------------
{P} while B do C {P ∧ ¬B}
```

其中 `P` 称为**循环不变式（loop invariant）**。这是 Hoare 逻辑中最具挑战性的规则：
- 循环不变式 `P` 在每次迭代前后都保持成立
- 循环终止时，`B` 为假，因此 `P ∧ ¬B` 成立

#### 5. 推论规则（Consequence Rule）

```
P ⇒ P'    {P'} C {Q'}    Q' ⇒ Q
---------------------------------
           {P} C {Q}
```

含义：可以通过逻辑蕴含强化前置条件或弱化后置条件。

### 权衡分析

| 获得 | 牺牲 |
|------|------|
| 严格的数学正确性保证 | 需要人工发现循环不变式，对程序员要求高 |
| 与结构化程序设计天然契合 | 仅证明部分正确性（partial correctness），不保证终止性 |
| 模块化推理（组合式验证） | 对复杂数据结构（指针、堆）表达能力有限 |
| 为自动程序验证奠定理论基础 | 原始版本无法处理并发、非确定性 |

---

## Step 3 | 正确性与复杂性

### 正确性论证

Hoare 逻辑的"正确性"体现在两个层面：

**1. 可靠性（Soundness）**

如果 `{P} C {Q}` 在 Hoare 逻辑中可证明，那么程序 `C` 确实满足：从满足 `P` 的状态出发，若 `C` 终止，则最终状态满足 `Q`。

论文中通过结构归纳法论证了每条规则的正确性：
- 赋值公理的正确性基于替换引理（substitution lemma）
- 顺序、条件、循环规则的正确性基于对应控制结构的语义

**2. 相对完备性（Relative Completeness）**

Cook (1978) 在后续工作中证明了：在一阶逻辑完备的前提下，Hoare 逻辑对于 while 程序是**相对完备**的——即所有为真的三元组都可被证明。这被称为 **Cook 完备性**。

### 关键假设

1. **表达式无副作用**：赋值公理假设表达式求值不改变程序状态
2. **确定性执行**：原始 Hoare 逻辑假设程序执行是确定性的
3. **一阶逻辑表达能力**：断言语言必须足够表达所需的不变式
4. **部分正确性**：原始版本只保证"若终止则正确"，不保证一定终止

### 边界情况

- **非终止程序**：`{true} while true do skip {false}` 在 Hoare 逻辑中是可证明的（因为循环不终止，后置条件 vacuously 成立）
- **数组与指针**：原始论文未处理别名（aliasing）问题，后续 O'Hearn 等人发展出分离逻辑（Separation Logic）解决
- **并发程序**：原始 Hoare 逻辑无法直接处理并发，Owicki 和 Gries (1976) 以及后来的并发分离逻辑（Concurrent Separation Logic）进行了扩展

---

## Step 4 | 实验评估

### 实验设计

Hoare (1969) 是一篇**理论论文**，不包含传统意义上的实验或基准测试。论文的"验证"方式是：

1. **形式化定义**：为每种语言结构给出精确的公理/规则
2. **示例证明**：通过多个程序实例展示如何应用规则进行正确性证明
3. **一致性论证**：证明规则与程序直觉语义的一致性

### 关键示例

论文中最经典的示例是**整数除法程序**的正确性证明：

```
{q = 0 ∧ r = x ∧ r ≥ 0}
while r ≥ y do
    r := r - y;
    q := q + 1
{r < y ∧ x = r + q * y}
```

通过构造循环不变式 `x = r + q * y ∧ r ≥ 0`，论文展示了如何逐步应用 while 规则、赋值公理和顺序规则完成证明。

### 局限性

1. **无自动化**：所有证明步骤需要人工完成，对程序员数学素养要求高
2. **不变式发现瓶颈**：循环不变式的发现没有系统方法，依赖直觉
3. **规模限制**：论文示例均为小型算法，未涉及大规模软件系统
4. **仅部分正确性**：不处理程序终止性证明（需额外引入 ranking function / variant）

---

## Step 5 | 演化谱系（Impact & Lineage）

### 前驱工作

```
Floyd (1967) "Assigning Meanings to Programs"
    ↓ 归纳断言方法，基于流程图
Dijkstra (1968) "Go To Statement Considered Harmful"
    ↓ 结构化编程思想
Hoare (1969) "Axiomatic Basis for Computer Programming"
    ↓ 将 Floyd 思想形式化为公理系统，与结构化语言契合
```

- **Robert Floyd (1967)**：首次提出用归纳断言验证程序，使用流程图表示
- **Dijkstra (1968)**：结构化编程革命，为 Hoare 逻辑提供了语言基础（顺序/选择/循环）

### 直接后续发展

```
Hoare Logic (1969)
    ├── Dijkstra (1975) "Guarded Commands, Nondeterminacy and Formal Derivation of Programs"
    │       └── 最弱前置条件（Weakest Precondition）演算
    ├── Cook (1978) "Soundness and Completeness of an Axiom System for Program Verification"
    │       └── 证明了 Hoare 逻辑的相对完备性
    ├── Owicki & Gries (1976) "An Axiomatic Proof Technique for Parallel Programs"
    │       └── 扩展到并发程序验证
    ├── Separation Logic (O'Hearn, Reynolds, Yang, 2001)
    │       └── 解决指针/堆内存验证问题
    └── Concurrent Separation Logic (O'Hearn, 2007)
            └── 并发 + 堆内存的组合验证
```

### 工程落地与现代工具

| 工具/系统 | 关系 | 说明 |
|-----------|------|------|
| **TLA+** (Lamport, 1999) | 直接继承 | 基于时序逻辑的形式化规约与验证语言，广泛用于 AWS、Azure 等云系统 |
| **Coq** / **Isabelle/HOL** | 逻辑基础 | 交互式定理证明器，支持 Hoare 逻辑风格的程序验证 |
| **VCC** (Microsoft) | 工程应用 | 用于验证 Windows 内核 Hyper-V 的并发 C 程序 |
| **Dafny** (Microsoft) | 现代继承 | 基于 Hoare 逻辑的编程语言和验证器，自动生成证明义务 |
| **Frama-C** | 工业工具 | C 程序静态分析框架，支持 ACSL（ANSI C Specification Language）规约 |
| **Rust 类型系统** | 间接影响 | 所有权系统可视为一种轻量级形式化验证，确保内存安全 |

### 学术影响

- **形式化方法学科**：直接催生了程序验证（Program Verification）这一研究方向
- **编程语言语义学**：为公理语义学（Axiomatic Semantics）奠定了基础，与操作语义、指称语义并列为三大语义学流派
- **软件工程**：影响了契约式编程（Design by Contract，Eiffel 语言）、JML（Java Modeling Language）等实践

---

## Step 6 | 个人理解

### 最重要的洞察

Hoare 逻辑最深刻的价值在于它建立了一种**双向桥梁**：
- **自上而下**：从规格说明（specification）出发，通过推理规则约束程序实现
- **自下而上**：从程序代码出发，通过规则推导出程序保证的性质

这种双向性使得程序验证不再是测试之后的"补丁"，而是可以融入程序设计过程的核心方法。

### 为什么它能成功

1. **时机恰到好处**：1960 年代末软件危机爆发，行业迫切需要保证软件质量的新方法
2. **与结构化编程天然契合**：Dijkstra 刚刚推动结构化编程革命，Hoare 逻辑正好为结构化语言提供了验证框架
3. **简洁而强大**：仅用 5 条核心规则就覆盖了顺序程序的所有基本结构
4. **数学美感**：赋值公理的逆向代入思想极其优雅，展现了深刻的数学洞察力

### 类比理解

想象你是一位建筑工程师，要证明一座桥能承受 100 吨重量：
- **测试方法**：让 100 吨卡车开过去，看桥是否塌了（对应传统软件测试）
- **Hoare 逻辑方法**：根据材料力学公式（公理），逐步计算每个结构件的受力（推理规则），最终证明整座桥的承载力 ≥ 100 吨（正确性证明）

测试只能证明"在测试条件下没问题"，而证明可以证明"在所有条件下都没问题"。

### 疑问记录

- [ ] 原始 Hoare 逻辑如何处理异常和错误状态？（需要后续扩展）
- [ ] 在大型工业系统中，如何自动化发现循环不变式？（当前 AI/ML 方法是否有助于此？）
- [ ] Hoare 逻辑与类型系统（如 Haskell 的 Curry-Howard 对应）之间的深层联系是什么？

---

## Step 7 | 关联学习

### 前置知识

- [ ] Floyd (1967) "Assigning Meanings to Programs" — 理解归纳断言的起源
- [ ] 一阶逻辑基础 — 理解蕴含、量词、替换等概念
- [ ] Dijkstra (1968) "Go To Statement Considered Harmful" — 理解结构化编程背景

### 延伸阅读

- [ ] Dijkstra (1975) "Guarded Commands, Nondeterminacy and Formal Derivation of Programs" — 最弱前置条件演算
- [ ] O'Hearn, Reynolds, Yang (2001) "Local Reasoning about Programs that Alter Data Structures" — 分离逻辑
- [ ] Lamport (2002) "Specifying Systems" — TLA+ 形式化规约实践
- [ ] Nipkow, Klein (2014) "Concrete Semantics with Isabelle/HOL" — 现代定理证明与程序验证

### 知识图谱位置

```
理论基础
    ├── 信息论 (Shannon 1948)
    ├── 计算理论 (Turing 1950)
    └── 程序语义与验证
            ├── Floyd 归纳断言 (1967)
            ├── Dijkstra 结构化编程 (1968)
            ├── Hoare 逻辑 (1969)  ← 当前位置
            ├── Dijkstra 最弱前置条件 (1975)
            ├── CSP 进程代数 (Hoare 1978)
            ├── 分离逻辑 (2001)
            └── 现代形式化方法 (TLA+/Coq/Dafny)
```

---

## 原文摘录（精华句）

> "When the correctness of a program, its compiler, and the hardware of the computer have all been established with mathematical certainty, it will be possible to place great reliance on the results of the program, and predict their properties with a confidence limited only by the capacity of the machine."
> — C.A.R. Hoare, 1969

---

## 参考链接

- 原文：https://dl.acm.org/doi/10.1145/363235.363259
- Hoare 图灵奖演讲 (1980)：https://dl.acm.org/doi/10.1145/1283920.1283936
- 分离逻辑综述：https://dl.acm.org/doi/10.1145/3211968
