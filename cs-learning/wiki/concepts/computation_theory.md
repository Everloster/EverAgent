---
id: concept-computation_theory
title: "可计算性理论：图灵机与 Lambda 演算"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [01_turing_1950, CS关键人物图谱]
status: active
---

# 可计算性理论

## 一句话定义
1930s Church 与 Turing 各自提出 Lambda 演算和图灵机两种计算模型，证明它们等价（Church-Turing 论题），并由此确立"可计算"的形式边界与计算的根本局限（停机问题不可判定）。

## 三大支柱

### 1. 图灵机（Turing Machine, 1936）
**定义**：一个无限长的纸带 + 一个有限状态控制器 + 一个读写头。控制器根据 (当前状态, 读到符号) 决定 (写什么符号, 读写头移动方向, 转到哪个状态)。

**核心结论**：任何"可计算"的数学函数都可以由某个图灵机计算。

来源：CS关键人物图谱 §Turing

### 2. Lambda 演算（Alonzo Church, 1932-36）
**定义**：一种纯函数式的形式系统，仅有三种结构——变量、抽象（λx.M）、应用（M N）+ Beta 归约规则。

**核心结论**：Lambda 演算可表达任意可计算函数（与图灵机等价）。

来源：CS关键人物图谱 §Church

### 3. Church-Turing 论题
**论断**："可计算"的直觉概念与"图灵机可计算"等价。这不是定理而是假设——它无法被证明，因为"可计算"是非形式概念。但至今没有反例。

**等价性证明**：图灵机可模拟 Lambda 演算，反之亦然——任何用一种模型表达的函数都可以用另一种表达。

来源：CS关键人物图谱 §Turing

## 核心局限：停机问题

**问题**：是否存在一个程序 H(P, x)，对任意程序 P 和输入 x，能判断 P(x) 是否会停机？

**Turing 1936 证明**：不存在。证明用对角化论证——若假设 H 存在，可构造矛盾的程序。

**意义**：这是计算的**根本局限**——不是工程难题，而是数学不可能。许多实际重要问题（如"两个程序是否等价"、"程序是否会崩溃"）都可归约到停机问题，因此同样不可判定。来源：CS关键人物图谱 §Turing

## 与 Shannon 信息论的对照

| 维度 | Turing/Church 计算理论 | Shannon 信息论 |
|------|------|------|
| 时间 | 1936 | 1948 |
| 研究对象 | 计算过程的边界 | 信息传输的边界 |
| 核心结果 | 停机问题不可判定 | 信源/信道编码定理 |
| 共同基础 | 用形式化数学定义直觉概念 | 同上 |

两者共同奠定了 1940s 末"信息时代"的两大数学支柱。来源：CS关键人物图谱 §第一代

## 思想传承

- **Lisp（McCarthy 1958）**：直接基于 Lambda 演算的编程语言
- **Haskell / ML / Scheme**：函数式语言谱系
- **Coq / Agda / Lean**：基于类型论的证明助手，类型论由 Lambda 演算扩展而来
- **Rust 所有权系统**：受类型论与线性逻辑启发

来源：CS关键人物图谱 §思想传承脉络

## 在本项目的相关报告
- [01_turing_1950](../../reports/paper_analyses/01_turing_1950.md)
- [CS 关键人物图谱](../../reports/knowledge_reports/CS关键人物图谱.md)

## 跨域连接
- [information_theory](./information_theory.md)：与计算理论同为信息时代的数学基础
- entities/[turing_alan](../entities/turing_alan.md) — 图灵机与图灵测试
- ai-learning 中的"可学习性边界"：与可计算边界的类比

## 被引用于
- [information_theory](./information_theory.md)
- entities/[turing_alan](../entities/turing_alan.md)

## 开放问题
- P vs NP（计算复杂度的另一根本问题）
- 量子计算是否真正扩展了 Church-Turing 论题的边界（量子图灵机理论）
- 超计算（Hypercomputation）是否在物理上可能
