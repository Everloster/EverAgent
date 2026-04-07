---
id: concept-consistent_hashing
title: "一致哈希（Consistent Hashing）"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [11_dynamo_2007, 28_chord_2001, 分布式系统知识图谱]
status: active
---

# 一致哈希

## 一句话定义
将节点和数据键都映射到同一个环形哈希空间，键由顺时针第一个节点负责——节点增删时只迁移该节点相邻段的数据，而非全量再哈希。

## 与传统取模哈希的对比

| 方案 | 节点变化时迁移量 | 节点扩缩容代价 |
|------|------|------|
| `hash(k) % n` | 几乎全部数据 | 极高，触发雪崩 |
| 一致哈希 | 仅 O(1/n) | 低，可在线 |

来源：11_dynamo_2007

## 核心设计
1. **环空间**：哈希函数（如 SHA-1）将节点 IP 与数据键映射到 0 ~ 2^m 的环
2. **归属规则**：键 k 存储在 `successor(k)`——环上顺时针第一个节点
3. **节点加入**：新节点 N 从 successor(N) 接管 [predecessor(N), N] 区间的数据
4. **节点离开**：N 的数据交给 successor(N)

来源：28_chord_2001

## 关键改进：虚拟节点（vnode）

**问题**：节点在环上分布不均时会出现热点（少数节点承载大部分数据）。

**解**：每个物理节点对应 V 个**虚拟节点**（vnode），将其分散到环的不同位置。Dynamo 默认每个节点 ~150 个 vnode，典型 V=100~256。来源：11_dynamo_2007

**附带好处**：
- 节点能力异构时可分配不同数量的 vnode
- 节点故障时其 vnode 数据被多个其他节点接管，恢复负载均衡

## 应用脉络
- **Chord（2001）**：DHT 一致哈希的学术起点（关注查找路由：见 [dht_chord](./dht_chord.md)）
- **Dynamo（2007）**：工业级一致哈希 + vnode + NWR 复制
- **Cassandra**：直接借用 Dynamo 的环模型
- **Memcached / Redis Cluster**：客户端一致哈希做缓存分片
- **Akka Cluster Sharding**：Actor 模型下的一致哈希

来源：分布式系统知识图谱 §5.1 / §1.2

## 与 DHT 的区别
- **一致哈希**关注"键如何分布到节点"——一个数据结构问题
- **DHT（如 Chord）**关注"如何在 P2P 网络中**查找**键所在的节点"——一个路由问题
- 两者经常配合使用，但概念正交

来源：28_chord_2001 / 分布式系统知识图谱 §5.1

## 在本项目的相关报告
- [11_dynamo_2007](../../reports/paper_analyses/11_dynamo_2007.md)
- [28_chord_2001](../../reports/paper_analyses/28_chord_2001.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [dht_chord](./dht_chord.md)：Chord 在一致哈希之上加 Finger Table 解决 P2P 查找
- [distributed_storage](./distributed_storage.md)：Dynamo / Cassandra 的数据分布层
- [cap_theorem](./cap_theorem.md)：一致哈希是 AP 系统的常用分片基础

## 被引用于
- [dht_chord](./dht_chord.md)
- [distributed_storage](./distributed_storage.md)
- [overview.md](../overview.md)

## 开放问题
- vnode 数量的最优值（与节点规模、心跳代价的权衡）
- 一致哈希在地理就近路由（geo-aware sharding）下的扩展
