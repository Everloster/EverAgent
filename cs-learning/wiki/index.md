# cs-learning · Wiki Index

> LLM 维护的知识百科入口。每次摄入新论文后更新。
> 查询时优先读此文件定位相关页面，再深入阅读。

---

## Overview

| 页面 | 简介 |
|------|------|
| [overview.md](./overview.md) | cs-learning 全局综述：四主线、技术拐点、概念依赖图 |

---

## Entities（人物 / 机构）

### 人物
| 页面 | 简介 |
|------|------|
| [turing_alan.md](./entities/turing_alan.md) | 图灵机、停机问题、图灵测试，CS 理论奠基者 |
| [shannon_claude.md](./entities/shannon_claude.md) | 信息论创立者，贝尔实验室 |
| [lamport_leslie.md](./entities/lamport_leslie.md) | Lamport 时钟、拜占庭将军、Paxos、TLA+，2013 图灵奖 |
| [dijkstra_edsger.md](./entities/dijkstra_edsger.md) | 结构化编程、Dijkstra 算法、信号量，1972 图灵奖 |
| [hoare_tony.md](./entities/hoare_tony.md) | Quicksort、Hoare Logic、CSP、null reference，1980 图灵奖 |
| [thompson_ritchie.md](./entities/thompson_ritchie.md) | Unix + C 语言，贝尔实验室搭档，1983 图灵奖 |
| [knuth_donald.md](./entities/knuth_donald.md) | TAOCP、TeX、算法分析标准化，1974 图灵奖 |
| [dean_ghemawat.md](./entities/dean_ghemawat.md) | GFS / MapReduce / Bigtable / Spanner，Google 传奇搭档 |
| [cerf_kahn.md](./entities/cerf_kahn.md) | TCP/IP 共同发明者，2004 图灵奖 |
| [torvalds_linus.md](./entities/torvalds_linus.md) | Linux 内核 + Git 创造者 |

### 机构
| 页面 | 简介 |
|------|------|
| [bell_labs.md](./entities/bell_labs.md) | Unix / C / 信息论 / 晶体管的诞生地 |
| [google_research.md](./entities/google_research.md) | GFS / MapReduce / Bigtable / Chubby / Spanner |
| [mit_csail.md](./entities/mit_csail.md) | Chord DHT、Liskov、PDOS 分布式系统研究组 |

---

## Concepts（核心概念）

| 页面 | 简介 |
|------|------|
| [lamport_clocks.md](./concepts/lamport_clocks.md) | happens-before 偏序与逻辑时钟，分布式时序基础 |
| [consensus_paxos_raft.md](./concepts/consensus_paxos_raft.md) | 分布式共识：Paxos 理论标准 vs Raft 可理解性优先 |
| [byzantine_fault_tolerance.md](./concepts/byzantine_fault_tolerance.md) | 拜占庭容错：n ≥ 3f+1，区块链共识基础 |
| [distributed_storage.md](./concepts/distributed_storage.md) | GFS / Bigtable / Dynamo / Spanner 四里程碑 + 一致性谱系 |
| [coordination_chubby_zk.md](./concepts/coordination_chubby_zk.md) | 分布式协调服务：Chubby vs ZooKeeper |
| [mapreduce.md](./concepts/mapreduce.md) | 批处理编程模型，自动容错 + 数据本地性 |
| [dht_chord.md](./concepts/dht_chord.md) | 一致哈希环 + Finger Table + O(log N) 查找 |
| [csp_concurrency.md](./concepts/csp_concurrency.md) | 通信顺序进程，Go channel 的理论根 |
| [tcp_ip.md](./concepts/tcp_ip.md) | 端到端论点 + 无状态网关 |
| [distributed_messaging.md](./concepts/distributed_messaging.md) | Kafka 日志范式，Pull 模型 |
| [unix_philosophy.md](./concepts/unix_philosophy.md) | 一切皆文件 + 小工具组合 |

---

## Syntheses（合成分析 / 问答归档）

| 页面 | 简介 |
|------|------|
| [spanner_truetime_cap.md](./syntheses/spanner_truetime_cap.md) | Spanner 如何用 TrueTime + Paxos + INTERLEAVE 同时拿到全球强一致与水平扩展，CAP 反例的精确含义 |

---

> 操作日志 → [log.md](./log.md)
> 全局综述 → [overview.md](./overview.md)
> 原始报告 → [reports/](../reports/)
> 原始论文 → [papers/](../papers/)
