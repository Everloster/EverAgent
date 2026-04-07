---
id: concept-two_phase_commit
title: "两阶段提交（2PC）"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [21_spanner_2012, 分布式系统知识图谱]
status: active
---

# 两阶段提交（Two-Phase Commit, 2PC）

## 一句话定义
跨多个独立资源管理器的原子事务协议：协调者（Coordinator）通过 Prepare → Commit 两个阶段，让所有参与者要么全提交、要么全回滚。

## 协议流程
**Phase 1 — Prepare**：
1. Coordinator 向所有 Participant 发 `PREPARE`
2. 每个 Participant 检查本地是否能提交，写 prepared 日志，回 `YES`/`NO`

**Phase 2 — Commit / Abort**：
- 若所有 Participant 回 `YES`：Coordinator 写 commit 日志，发 `COMMIT`
- 若任一回 `NO`：Coordinator 发 `ABORT`
- Participant 收到决定后，应用并回 `ACK`

来源：分布式系统知识图谱 §1.2 §6.3

## 致命缺陷：阻塞性
**协调者在 Phase 2 之间崩溃**会让所有 Participant 永久阻塞——它们已 prepared 但不知道决定，必须等协调者恢复才能继续。来源：分布式系统知识图谱 §6.3

**缓解方案**：
- 3PC（Three-Phase Commit）：增加 PreCommit 阶段降低阻塞概率，代价是消息复杂度
- Paxos Commit（Gray & Lamport 2006）：用 Paxos 替代单点协调者
- TCC（Try-Confirm-Cancel）：业务层补偿事务

## 与 Paxos 的协同（Spanner 模型）
Spanner 跨 Tablet 事务使用：
- **每个 Tablet 内部**：Paxos Group 多副本写
- **跨 Tablet**：2PC 协调
- **Coordinator 自身**也是一个 Paxos Group，避免单点故障

这使得 Spanner 的跨 Tablet 事务既保证全局原子性，又规避了经典 2PC 的协调者单点问题。来源：21_spanner_2012 / 分布式系统知识图谱 §1.2

## 性能特征
- **延迟**：至少 2 个 RTT
- **吞吐**：被最慢 Participant 限制
- **可用性**：单个 Participant 不可达即整个事务无法提交

这就是为什么 Spanner 通过 `INTERLEAVE IN PARENT` 设计 schema 让大多数事务退化为单 Tablet —— 避开 2PC 的代价。来源：21_spanner_2012

## 在本项目的相关报告
- [21_spanner_2012](../../reports/paper_analyses/21_spanner_2012.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [consensus_paxos_raft](./consensus_paxos_raft.md)：Paxos Commit 用 Paxos 解决 2PC 的协调者单点问题
- [distributed_storage](./distributed_storage.md)：Spanner 跨 Tablet 事务使用 2PC + Paxos Group
- [cap_theorem](./cap_theorem.md)：2PC 是 CP 系统中实现跨节点原子性的标准工具

## 被引用于
- [syntheses/spanner_truetime_cap.md](../syntheses/spanner_truetime_cap.md)
- [overview.md](../overview.md)（待加入概念依赖图）

## 开放问题
- 跨数据中心 2PC 的延迟下限（受光速限制 RTT ≥ 数十毫秒）
- 现代数据库（CockroachDB / YugabyteDB）如何在 2PC 之上做用户透明的优化
