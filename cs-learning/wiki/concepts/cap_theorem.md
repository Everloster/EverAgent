---
id: concept-cap_theorem
title: "CAP 定理"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [11_dynamo_2007, 21_spanner_2012, 分布式系统知识图谱]
status: active
---

# CAP 定理

## 一句话定义
分布式系统在网络分区（Partition）发生时，无法同时保证强一致性（Consistency）与可用性（Availability）——只能在 CP 与 AP 之间二选一。

## 历史与证明
- **1998 Brewer 猜想**：在 PODC 演讲中提出"分布式系统不可能同时满足 C/A/P"
- **2002 Gilbert & Lynch 形式化证明**：在异步网络模型下证明 CAP 不可能性

来源：分布式系统知识图谱 §6.1

## 精确表述
- **C（Consistency）**：所有节点在同一时刻读到的数据相同（线性一致）
- **A（Availability）**：每个非故障节点对每次请求都能在有限时间内返回响应
- **P（Partition tolerance）**：网络可能丢失/延迟任意多消息

**关键澄清**：P 在真实分布式系统中**几乎不可避免**，所以现实选择只有"P 发生时弃 C 还是弃 A"——即 CP 或 AP，而非"三选二"。来源：分布式系统知识图谱 §6.1

## CP vs AP 的工程典范

| 系统 | 派别 | 工程取舍 |
|------|------|---------|
| **Spanner** | CP | 分区时少数派副本不可用，但通过 TrueTime + Paxos 提供线性一致；可用性极接近 100%（5-9 以上） |
| **Bigtable** | CP（单行强一致） | 依赖 Chubby 协调，分区时可能短暂不可用 |
| **Dynamo** | AP | 始终可写，向量时钟记录冲突；冲突由应用层（如购物车取并集）解决 |
| **Cassandra** | AP（可调） | NWR 参数允许在请求级在 CP/AP 间切换 |

来源：11_dynamo_2007 / 21_spanner_2012 / 分布式系统知识图谱 §1.2

## Brewer 2017 修正
Brewer 自己在 *Computer* 杂志撰文澄清：
- **"必须二选一"是过度简化**——大部分时间没有分区，C 与 A 都能保证
- 真正的设计问题是"分区发生后**如何恢复一致性**"
- Spanner 这类"高可用 CP" 系统的存在不算违反 CAP，而是说明 P 实际很罕见

来源：分布式系统知识图谱 §6.1

## 与一致性谱系的关系

CAP 中的 C 实际上是**线性一致性（Linearizability）**这一最严格的一致性模型。放宽 C 可以换得不同程度的可用性：

```
Linearizability（CAP 的 C，最强）
   ↓
Sequential Consistency（顺序一致）
   ↓
Causal Consistency（因果一致，向量时钟）
   ↓
Eventual Consistency（最终一致，Dynamo）
```

来源：分布式系统知识图谱 §6.1

## 在本项目的相关报告
- [11_dynamo_2007](../../reports/paper_analyses/11_dynamo_2007.md)
- [21_spanner_2012](../../reports/paper_analyses/21_spanner_2012.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [linearizability_vs_serializability](./linearizability_vs_serializability.md)：CAP 中的 C 是线性一致，与可串行化不同
- [distributed_storage](./distributed_storage.md)：CP/AP 工程示例
- [consensus_paxos_raft](./consensus_paxos_raft.md)：CP 系统的实现工具

## 被引用于
- [overview.md §四 技术分歧与未决问题](../overview.md)（强一致 vs 最终一致）
- [syntheses/spanner_truetime_cap.md](../syntheses/spanner_truetime_cap.md)

## 开放问题
- "高可用 CP" 系统的可用性下限到底由什么决定（网络拓扑？协议？）
- PACELC 扩展（Even when there's no Partition, the trade-off is Latency vs Consistency）的实用价值
