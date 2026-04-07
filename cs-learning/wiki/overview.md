---
id: overview-cs_learning
title: "cs-learning · 全局综述"
type: overview
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
status: active
---

# cs-learning · 全局综述

> 基于截至 2026-04-07 已读 20 篇精读论文 + 3 篇知识报告蒸馏。
> 每 10 篇新论文后更新一次。

---

## 一、领域骨架：四主线 + 一支线

```
                Turing(1936) / Shannon(1948) / Lamport(1978)
                              ↓
        ┌─────────────────┬───┴───┬──────────────────┐
        │                 │       │                  │
   主线1: Storage    主线2: Consensus   主线3: Coordination   主线4: Messaging
   ────────         ────────         ────────             ────────
   UNIX FS / FFS    Lamport Clocks   Chubby (2006)       TCP/IP (1974)
   GFS (2003)       Byzantine (1982) ZooKeeper (2010)    CSP (1978)
   Bigtable (2006)  Paxos (1989)                         MapReduce (2004)
   Dynamo (2007)    Raft (2014)                          Kafka (2011)
   Spanner (2012)
                              │
                          支线: P2P/Lookup
                          ────────
                          Chord DHT (2001)
```

参考的源报告分布：Storage 6 篇、Consensus 4 篇、Coordination 2 篇、Messaging 4 篇、P2P 1 篇、底层（Unix/FFS/Turing/Shannon）4 篇 + 知识报告 3 篇（CS人物图谱 / 分布式系统知识图谱 / DHT 实战排查）。

---

## 二、关键技术拐点（按时间）

| 年份 | 事件 | 性质 |
|------|------|------|
| 1936 | Turing 机 / 停机问题 | 计算理论奠基 |
| 1948 | Shannon 信息论 | 通信与压缩理论奠基 |
| **1969** | **Unix（Thompson + Ritchie）** | 系统设计哲学的开端 |
| 1972 | C 语言 | 可移植系统编程语言 |
| 1974 | TCP/IP（Cerf + Kahn） | 互联网架构出生证 |
| **1978** | **Lamport Clocks + CSP（Hoare）** | 分布式时序 + 并发理论 |
| 1982 | 拜占庭将军问题 | 恶意节点共识理论 |
| 1984 | FFS | 文件系统物理布局优化 |
| **1989/2001** | **Paxos** | 分布式共识理论标准 |
| 2001 | Chord | DHT 一致哈希 |
| **2003–2006** | **GFS / MapReduce / Bigtable / Chubby** | Google 大数据基础设施四件套 |
| 2007 | Dynamo | CAP 的 AP 工程典范 |
| 2010 | ZooKeeper | 开源协调服务 |
| 2011 | Kafka | 消息日志范式 |
| **2012** | **Spanner + TrueTime** | 全球强一致数据库 |
| **2014** | **Raft** | 可理解性优先的共识 |

---

## 三、核心概念间的依赖关系

```
              tcp_ip                    unix_philosophy
                │                              │
        ┌───────┼────────┐                     │
        │                │                     │
   distributed_     csp_concurrency      distributed_storage
    messaging                                  │
        │                                      │
        │                               ┌──────┴──────┐
        │                               │             │
        │                          consensus_      coordination_
        │                          paxos_raft      chubby_zk
        │                               │             │
        │                               └─────┬───────┘
        │                                     │
        │                              lamport_clocks
        │                                     │
        └──────── mapreduce          byzantine_fault_tolerance
                                             │
                                      dht_chord（最终一致变体）
```

每条边的意义：
- tcp_ip → distributed_messaging：Kafka 是"持久化的 TCP"
- csp_concurrency → distributed_messaging：Consumer Group ≈ 持久化 channel
- consensus → distributed_storage：Spanner Paxos Group / Bigtable 依赖 Chubby
- coordination → distributed_storage：GFS / Bigtable Master 选举
- lamport_clocks → consensus：所有共识协议依赖逻辑时序
- byzantine → consensus：恶意节点扩展
- unix_philosophy → distributed_storage：inode 抽象传承到 GFS Chunk

---

## 四、技术分歧与未决问题（截至 2026-04）

| 议题 | 主流立场 | 反方立场 |
|------|---------|---------|
| 强一致 vs 最终一致 | Spanner 证明强一致可行 | Dynamo 系统在高可用场景仍主流 |
| Paxos vs Raft | Raft 因可理解性成为开源首选 | Paxos 在 Google 内部仍主导 |
| Push vs Pull 消息 | Kafka Pull 模型成事实标准 | RabbitMQ 等 Push 在低延迟 RPC 场景仍存 |
| 中心化协调 vs 去中心化 | 数据中心内 Chubby/ZK 主流 | 区块链 / DHT 在跨信任域场景 |
| BFT vs CFT | 数据中心内 CFT 足够 | 区块链 / 跨域必须 BFT |
| LSM vs B-Tree | LSM 在写密集场景胜出 | B-Tree 在读密集 OLTP 仍主流 |

---

## 五、当前 wiki 的概念覆盖度

| 已建 concept 页面 | 状态 |
|------------------|------|
| lamport_clocks | active |
| consensus_paxos_raft | active |
| byzantine_fault_tolerance | active |
| distributed_storage | active |
| coordination_chubby_zk | active |
| mapreduce | active |
| dht_chord | active |
| csp_concurrency | active |
| tcp_ip | active |
| distributed_messaging | active |
| unix_philosophy | active |

**已建 entity 页面**：12 个（turing / shannon / lamport / dijkstra / hoare / thompson_ritchie / dean_ghemawat / cerf_kahn / knuth / torvalds / bell_labs / google_research / mit_csail）

**plan §8 短期成功标准**（cs-learning 维度）：
- [x] cs-learning wiki/ 有 ≥ 10 个 entity 页面、≥ 8 个 concept 页面
- [ ] 每次新摄入后 log.md 有记录（待新摄入触发）
- [ ] 一篇新论文摄入后能通过 wiki/ 而非 reports/ 回答"这个概念是什么"（待验证）

---

## 六、缺失的概念页面（建议下次摄入触发时补建）

| 概念 | 触发条件 |
|------|---------|
| cap_theorem | 多篇报告引用，可独立蒸馏 |
| two_phase_commit | Spanner 跨 Paxos Group 事务依赖 |
| consistent_hashing | 已在 dht_chord 和 distributed_storage 中提及，但可独立成页 |
| linearizability_vs_serializability | Spanner 区分点，仍偏简单 |
| dns | 30_dns_1987 已读但未蒸馏 |
| information_theory | Shannon 1948 论文未独立成 concept |
| computation_theory | Turing 1936 / Church-Turing 论题未独立成 concept |

---

> 操作日志 → [log.md](./log.md)
> 索引 → [index.md](./index.md)
> 原始报告 → [reports/](../reports/)
