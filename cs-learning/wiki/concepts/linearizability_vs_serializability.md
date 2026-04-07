---
id: concept-linearizability_vs_serializability
title: "线性一致 vs 可串行化"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [21_spanner_2012, 分布式系统知识图谱]
status: active
---

# 线性一致 vs 可串行化

## 一句话定义
**线性一致（Linearizability）**关注单对象在实时下的一致性（"全局时钟"维度）；**可串行化（Serializability）**关注多对象事务的隔离等价性（"事务等价于某个串行执行"）。两者正交——可同时具备、单独具备、都不具备。

## 三个独立维度

```
Linearizability （单对象 + 实时顺序）
       ┊
       ┊         Strict Serializability
       ┊       （= Linearizability + Serializability）
       ┊
Serializability （多对象事务 + 等价某串行）
```

来源：分布式系统知识图谱 §6.1

## 精确定义

### Linearizability（线性一致 / 原子一致）
- **范围**：单对象操作
- **要求**：操作看起来在 invocation 与 response 之间的某一**瞬时点**上原子发生，且这些瞬时点的顺序与现实时间顺序一致
- **观察者性质**：一旦某个客户端读到值 v，所有后续客户端必须读到 v 或更新值
- **示例**：CAS、单 key 原子写入

### Sequential Consistency（顺序一致）
- 比 linearizability **弱**：要求所有操作存在一个全局顺序，但**不要求与实时一致**
- 各进程内顺序保持，但跨进程可能"看起来时间错乱"
- 示例：ZAB / Raft 日志顺序

### Serializability（可串行化）
- **范围**：多操作事务
- **要求**：并发事务的执行**等价于**某种串行执行（任意顺序）
- 不限定是哪种串行——可能与现实时间不符
- 示例：传统 RDBMS 的事务隔离级 SERIALIZABLE

### Strict Serializability（严格可串行化 / 外部一致性）
- = Linearizability **+** Serializability
- 事务等价于某种与实时顺序兼容的串行执行
- 这是 **Spanner 的 External Consistency** 所声明的级别

来源：21_spanner_2012 / 分布式系统知识图谱 §6.1

## 为什么这两个常被混淆
- 教科书常把"线性一致"和"强一致"互用，但严格说"强一致"是模糊词
- 单对象 KV 存储里，serializability 退化为 linearizability，导致两者看起来等价
- 真正的差别在多对象事务出现时才显现

## CAP 中的 C 是什么
**CAP 定理中的 C 特指 Linearizability**（不是 Serializability）。所以 CAP 不可能定理只覆盖单对象一致性，**没有覆盖**事务隔离。这是为什么 NewSQL（Spanner / CockroachDB）要在 CAP 之外单独论证"严格可串行化"是否可行。来源：分布式系统知识图谱 §6.1 / [cap_theorem](./cap_theorem.md)

## 工程示例

| 系统 | Linearizability | Serializability | 严格可串行化 |
|------|---|---|---|
| Spanner | ✅ | ✅ | ✅（External Consistency） |
| Bigtable | ✅（单行） | ❌（无跨行事务） | ❌ |
| Dynamo | ❌（最终一致） | ❌ | ❌ |
| 传统单机 RDBMS | ✅ | ✅ | ✅ |
| MySQL Repeatable Read | ❌ | ❌（弱于 Serializable） | ❌ |

来源：21_spanner_2012 / 分布式系统知识图谱 §6.1

## 在本项目的相关报告
- [21_spanner_2012](../../reports/paper_analyses/21_spanner_2012.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [cap_theorem](./cap_theorem.md)：CAP 中的 C 特指 Linearizability
- [distributed_storage](./distributed_storage.md)：Spanner 的 External Consistency = Strict Serializability
- [consensus_paxos_raft](./consensus_paxos_raft.md)：Raft 日志顺序提供 Sequential Consistency
- [lamport_clocks](./lamport_clocks.md)：Linearizability 需要全局时间顺序，逻辑时钟不足以提供

## 被引用于
- [cap_theorem](./cap_theorem.md)
- [distributed_storage](./distributed_storage.md)
- [syntheses/spanner_truetime_cap.md](../syntheses/spanner_truetime_cap.md)

## 开放问题
- 现代数据库的"快照隔离（SI）"在该坐标系中的位置
- Strict Serializability 与 PACELC 中 L 的精确权衡曲线
