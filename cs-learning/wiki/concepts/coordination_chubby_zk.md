---
id: concept-coordination_chubby_zk
title: "分布式协调服务：Chubby 与 ZooKeeper"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [14_zookeeper_2010, 29_chubby_2006, 分布式系统知识图谱]
status: active
---

# 分布式协调服务

## 一句话定义
将"分布式锁 + 命名服务 + 配置 + 选主 + 服务发现"抽象为通用基础设施，为其他分布式系统提供控制平面。

## 核心原语
- **选主（Leader Election）**：Chubby/ZooKeeper ephemeral 节点
- **分布式锁**：Chubby advisory lock / ZooKeeper sequential 锁
- **配置管理**：ZooKeeper znode / Chubby 文件
- **服务发现**：写入地址到协调服务的命名空间

来源：分布式系统知识图谱 §3.3

## Chubby（Google, 2006）
**核心设计决策**：
- **5 副本 Paxos Cell**：多数派共识保证强一致，Master 持 lease 期间独立处理读
- **Sequencer**：持锁方传递不透明序列号给下游，防止过期锁
- **Grace Period（45s）**：session 断开后宽限期，客户端可恢复而非重建
- **粗粒度锁**：只支持小时/天级，不支持细粒度

来源：29_chubby_2006

**意外发现**：论文 §6.1 坦承 Chubby 实际最大用途是命名服务而非锁服务——60% 的打开文件与命名相关。这个"设计意图与实际使用的偏差"是论文最有价值的工程教训。来源：分布式系统知识图谱 §3.2

## ZooKeeper（Yahoo, 2010）
**核心设计决策**：
- **树形命名空间（znode）**：persistent / ephemeral / sequential 三种节点类型
- **Watch 机制**：数据变化时**一次性**通知，避免轮询（用过必须重新注册）
- **ZAB 原子广播**：类似 Multi-Paxos，Leader 顺序提交 + 多数确认
- **读可在本地副本服务**：在语义允许下牺牲一致性换取低延迟

来源：14_zookeeper_2010

**意外收获**：论文披露 ZooKeeper 的 UDP 心跳设计是为了避开 Chubby 在 TCP KeepAlive 拥塞时导致的大量 session 丢失问题。来源：分布式系统知识图谱 §3.2

## Chubby vs ZooKeeper

| 维度 | Chubby | ZooKeeper |
|------|--------|-----------|
| 接口 | 类文件系统 + 显式锁 API | znode + watch，无显式锁 |
| 读语义 | Master 本地读（lease 保护） | 任意副本读（较弱语义） |
| Grace period | 有（45s） | 无直接等价 |
| 开放性 | Google 内部 | 开源（Hadoop 生态控制平面） |

来源：分布式系统知识图谱 §3.2

## 应用场景
- **Bigtable / GFS Master 选举**：用 Chubby
- **Kafka / HBase 控制平面**：用 ZooKeeper
- **Kubernetes**：用 etcd（Raft 实现）

来源：分布式系统知识图谱 §3.1

## 在本项目的相关报告
- [14_zookeeper_2010](../../reports/paper_analyses/14_zookeeper_2010.md)
- [29_chubby_2006](../../reports/paper_analyses/29_chubby_2006.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [consensus_paxos_raft](./consensus_paxos_raft.md)：ZAB ≈ Multi-Paxos 的工程化
- [distributed_storage](./distributed_storage.md)：Bigtable / GFS 都依赖 Chubby
- [lamport_clocks](./lamport_clocks.md)：ZAB 的 zxid 是 Lamport 时钟变种
- [cap_theorem](./cap_theorem.md)：协调服务通常选择 CP

## 被引用于
- [consensus_paxos_raft](./consensus_paxos_raft.md)
- [distributed_storage](./distributed_storage.md)
- [tcp_ip](./tcp_ip.md)
- [distributed_messaging](./distributed_messaging.md)

## 开放问题
- 协调服务的 client 数量上限（Chubby 论文坦承新 session 流量是瓶颈）
- 跨数据中心协调的延迟权衡
