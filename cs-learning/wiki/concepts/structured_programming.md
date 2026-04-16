---
id: concept-structured_programming
title: "结构化编程（Structured Programming）"
type: concept/programming_paradigm
domain: [cs-learning]
created: 2026-04-16
updated: 2026-04-16
sources: [32_dijkstra_goto_1968]
---

# 结构化编程（Structured Programming）

## 定义
结构化编程是一种编程范式，要求程序控制流只能通过三种基本结构来表达：**顺序（sequence）**、**选择（selection / if-then-else）**、**重复（repetition / while/for）**，并禁止或强烈反对使用无条件跳转（GOTO）。

**理论基础**：Böhm-Jacopini 定理（1966）证明上述三种结构在计算上是完备的——任何可计算函数都可以用这三种结构表达，无需 GOTO。

## 核心原则

1. **进度可描述性（Process Traceability）**：任意时刻程序的"动态执行进度"必须可以用程序文本的静态坐标（位置 + 循环变量值）来描述。GOTO 打破了这一映射关系。
2. **局部性（Locality of Reasoning）**：代码块的正确性可独立证明，后通过组合保证整体正确性。
3. **层次化分解（Hierarchical Decomposition）**：大程序 = 多个结构化子程序的组合，避免扁平的意大利面代码。

## 理论分析

Dijkstra (1968) 的关键论证：
- 顺序执行：进度 = 行号（1维坐标）
- 条件分支：进度 = 行号 + 分支路径（有界扩展）
- 循环：进度 = 行号 + 循环计数器（有界动态坐标）
- **GOTO**：进度 = 跳转目标 × 任意历史路径（**无界**，难以静态推理）

## 历史演化

```
汇编 JMP 指令（1940s）
        ↓
FORTRAN GO TO (1957) / BASIC GOTO (1964)
        ↓
Böhm-Jacopini 定理 (1966) — 理论可行性
        ↓
Dijkstra "Go To Considered Harmful" (1968) — 宣言
        ↓
Hoare Logic (1969) — 形式化基础
        ↓
Pascal (1972) — 第一个主流"无 GOTO"语言
        ↓
C (1972) — 有 goto 但实践中受抑制，break/continue/return 作为结构化替代
        ↓
Java/Python/Go (1990s–2000s) — 主流语言默认结构化，GOTO 消失或严格限制
        ↓
Rust (2015) — loop { break value }：GOTO 能力完全封装在语法糖中
```

## 与其他范式的关系

- **面向对象编程（OOP）**：在结构化基础上增加数据封装与继承，本质兼容
- **函数式编程（FP）**：以递归 + 高阶函数替代命令式循环，是结构化的更严格形式
- **异常处理**：是"跨层次非局部跳转"的结构化替代（有类型约束的 GOTO）
- **async/await**：是并发控制流的结构化替代（将回调地狱转化为顺序结构）

## 相关概念

- 圈复杂度（Cyclomatic Complexity）：量化控制流复杂度的工程指标，根植于结构化编程理论
- 控制流图（CFG）：编译器分析程序控制流的数据结构，是结构化编程理论的工程实现
- Hoare 三元组 `{P} C {Q}`：结构化程序正确性的形式化表达

## 来源

- Dijkstra, E.W. (1968). "Go To Statement Considered Harmful." *CACM* 11(3).
  → 报告：`reports/paper_analyses/32_dijkstra_goto_1968.md`
