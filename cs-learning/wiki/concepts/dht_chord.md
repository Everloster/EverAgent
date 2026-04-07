---
id: concept-dht_chord
title: "DHT 与一致哈希（Chord）"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [28_chord_2001, 11_dynamo_2007, 分布式系统知识图谱, DHT实战排查：从协议理论到工程故障诊断]
status: active
---

# DHT（分布式哈希表）

## 一句话定义
将键值对去中心化地分布到环形拓扑的节点上，通过 O(log N) 跳完成查找，无中心元数据服务。

## Chord 核心设计
- **一致哈希环**：SHA-1(node_ip) 映射到 0~2^m 环，键 k 存储在 successor(k)
- **Finger Table**：每个节点维护 m 个指针，分别指向 `n + 2^(i-1)` 位置
- **O(log N) 查找**：每次转发至少将剩余距离减半
- **稳定化协议**：周期性 `stabilize()` + `fix_fingers()` 处理节点动态加入/故障

来源：28_chord_2001

## 为什么一致哈希重要
**节点增删时只需迁移局部数据**——传统取模哈希需要全量再平衡。详见独立成页的 [consistent_hashing](./consistent_hashing.md)（DHT 关注**路由**，consistent_hashing 关注**分布**，两者正交）。来源：11_dynamo_2007

**虚拟节点（vnode）**：让数据更均匀分布，避免热点。来源：11_dynamo_2007

> ⚠️ **矛盾标记**：DHT 默认**最终一致**与 Spanner 类**强一致存储**形成对比，详见 [overview §4](../overview.md#四技术分歧与未决问题) 的"强一致 vs 最终一致"分歧。

## 应用脉络
- **Cassandra 分区环**：直接借鉴 Chord 一致哈希
- **Dynamo 数据分布**：vnode + 一致哈希
- **CDN / Memcached / Redis Cluster**：一致哈希的变体
- **BitTorrent Mainline DHT**：Kademlia 协议的工程实现

来源：分布式系统知识图谱 §5.1

## 工程教训（DHT 实战）
DHT 在生产环境的失败常见于：
- 路由表收敛慢（节点流失率高时 finger table 漂移）
- 攻击向量（恶意节点劫持路由）
- NAT 穿透与公网连通性

来源：DHT实战排查：从协议理论到工程故障诊断

## 在本项目的相关报告
- [28_chord_2001](../../reports/paper_analyses/28_chord_2001.md)
- [11_dynamo_2007](../../reports/paper_analyses/11_dynamo_2007.md)
- [DHT 实战排查](../../reports/knowledge_reports/DHT实战排查：从协议理论到工程故障诊断.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [consistent_hashing](./consistent_hashing.md)：环 + vnode 的数据结构层面（与 DHT 路由正交）
- [distributed_storage](./distributed_storage.md)：Dynamo / Cassandra 数据分布
- [consensus_paxos_raft](./consensus_paxos_raft.md)：DHT 通常用最终一致而非强一致
- [dns](./dns.md)：DNS 是层级命名 vs DHT 的平面命名空间——对比典范

## 被引用于
- [consistent_hashing](./consistent_hashing.md)
- [distributed_storage](./distributed_storage.md)
- [dns](./dns.md)

## 开放问题
- DHT 在公网恶意环境下的安全性边界
- DHT 与现代云数据中心拓扑（fat-tree）的契合度
