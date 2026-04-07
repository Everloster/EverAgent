---
id: concept-consensus_paxos_raft
title: "分布式共识：Paxos 与 Raft"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [13_paxos_2001, 15_raft_2014, 分布式系统知识图谱]
status: active
---

# 分布式共识（Consensus）

## 一句话定义
让多个可能崩溃的节点对一个值（或一系列值）达成一致，且满足 Safety（一致性）和 Liveness（终止性）。

## 核心问题（FLP 不可能性背景）
异步系统中，存在崩溃故障时不存在确定性共识协议同时满足 Safety + Liveness。实际系统通过部分同步假设或随机化绕开此限制。来源：分布式系统知识图谱 §2.3

## Paxos：理论标准

**两阶段协议**：
- **Phase 1**：Proposer 发送 Prepare(n)，多数 Acceptor 回复 Promise(n, accepted_v)
- **Phase 2**：Proposer 选择已被接受的最大编号值（或自己提议的值），发送 Accept(n, v)，多数 Acceptor 回复 Accepted(n, v)

来源：13_paxos_2001 §2

**核心 Safety 论证**：
- 多数派原则：任意两个多数派必有交集
- 值的延续性：Proposer 必须接受已批准的最大编号值——这是 Safety 的数学核心

来源：13_paxos_2001 §2.2

**Multi-Paxos**：选出稳定 Leader 后 Phase 1 只做一次，后续所有 slot 直接进入 Phase 2，将共识从单值推广到日志复制。来源：13_paxos_2001 §3

**为什么难工程化**：原论文《The Part-Time Parliament》（1989）以希腊议会故事包装被拒稿；Multi-Paxos 的 Leader 选举、日志压缩、成员变更均未指明。Google Chubby 工程师花数年才得到正确实现。来源：分布式系统知识图谱 §2.2

## Raft：可理解性优先

**核心设计决策**：
- **强 Leader**：所有写经过 Leader，简化日志一致性
- **随机化超时**：选举超时在 150~300ms 随机化，极大降低多候选人竞争
- **日志复制两阶段**：Leader 追加 → 并发复制 Follower → 多数确认后提交

来源：15_raft_2014 §5

**安全性五要素**：Election Safety / Leader Append-Only / Log Matching / Leader Completeness / State Machine Safety。来源：15_raft_2014 §5

## Paxos vs Raft

| 维度 | Paxos | Raft |
|------|-------|------|
| 设计目标 | 理论最简 | 可理解、可工程化 |
| Leader 模型 | 弱 Leader（可多 Leader） | 强 Leader（单一） |
| 选举 | 自由竞争 | 随机化超时 |
| 工程难度 | 高 | 低 |

Raft 不是"更好的 Paxos"，而是"更容易理解和实现"的等效协议。来源：分布式系统知识图谱 §2.2

## 重要变体
- **Multi-Paxos**：Chubby 内部实现（Google 血泪史）
- **ZAB**：ZooKeeper 原子广播，更接近 Multi-Paxos 工程化
- **Raft**：etcd / TiKV / CockroachDB / Consul / InfluxDB
- **PBFT（1999）**：拜占庭场景的工业实现

来源：分布式系统知识图谱 §2.1

## 在本项目的相关报告
- [13_paxos_2001](../../reports/paper_analyses/13_paxos_2001.md)
- [15_raft_2014](../../reports/paper_analyses/15_raft_2014.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- lamport_clocks：共识依赖逻辑时序
- byzantine_fault_tolerance：容错模型扩展到恶意节点
- coordination_chubby_zk：ZAB ≈ Multi-Paxos 的工程化

## 开放问题
- Multi-Group Paxos/Raft 扩展性与一致性的权衡
- FLP 限制下的 Liveness 工程化策略
