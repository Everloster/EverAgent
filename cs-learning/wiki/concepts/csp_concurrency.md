---
id: concept-csp_concurrency
title: "CSP：通信顺序进程"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [18_csp_1978]
status: active
---

# CSP（Communicating Sequential Processes）

## 一句话定义
Hoare 1978 年提出的并发理论：用进程间消息传递（channel + rendezvous）替代共享内存，使并发程序的正确性可数学证明。

## 核心原理
**通信原语**：
- `c!x` —— 沿 channel c 发送值 x
- `c?y` —— 沿 channel c 接收到变量 y
- 默认 **rendezvous 同步语义**：发送方与接收方同时就绪才完成

来源：18_csp_1978

**结构化并发组合子**：
- 顺序组合：`P; Q`
- 选择组合：`P □ Q`（外部选择）
- 并行组合：`P || Q`

来源：18_csp_1978

**Traces 模型**：进程行为 = 所有可能的有限事件序列，正确性可在该模型上数学证明。来源：18_csp_1978

## 与共享内存模型的区别
| 维度 | 共享内存 | CSP |
|------|---------|-----|
| 同步原语 | 锁、信号量、原子变量 | channel send/recv |
| 错误模式 | 数据竞争、死锁难调试 | 死锁仍可能，但模式更结构化 |
| 形式化 | Hoare Logic 困难 | Traces 模型可证明 |

## 工程影响
- **Go 语言（2009）**：goroutine + channel 直接源自 CSP——"Don't communicate by sharing memory; share memory by communicating."
- **Erlang（1986）**：Actor 模型，与 CSP 是表亲
- **Rust async**：受 CSP 启发但语义不完全一致

来源：CS关键人物图谱 §Hoare

## 在本项目的相关报告
- [18_csp_1978](../../reports/paper_analyses/18_csp_1978.md)

## 跨域连接
- [distributed_messaging](./distributed_messaging.md)：Kafka 的 Consumer Group ≈ "持久化的 CSP channel"
- [unix_philosophy](./unix_philosophy.md)：Unix pipe 是 CSP 的小型 OS 级实现
- functional programming：纯函数 + 不可变 + 通信

## 被引用于
- [distributed_messaging](./distributed_messaging.md)
- [unix_philosophy](./unix_philosophy.md)

## 开放问题
- CSP 在分布式（跨机器）环境下的语义扩展
- 与 Actor 模型的本质差异（同步 vs 异步邮箱）
