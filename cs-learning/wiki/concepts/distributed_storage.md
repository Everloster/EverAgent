---
id: concept-distributed_storage
title: "分布式存储：GFS / Bigtable / Dynamo / Spanner"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [09_gfs_2003, 11_dynamo_2007, 12_bigtable_2006, 21_spanner_2012, 分布式系统知识图谱]
status: active
---

# 分布式存储

## 一句话定义
将 PB 级数据切分到数千台廉价机器上，提供"高可用 / 高吞吐 / 一定程度一致性"的存储服务。一致性、可用性、分区容忍性（CAP）的权衡是其核心设计空间。

## 四个里程碑

### GFS（2003）— 分布式文件系统的奠基
**核心设计决策**：
- **单 Master + ChunkServer**：元数据放内存，数据放 ChunkServer（64MB 大块）
- **追加写优先**：Google 工作负载以批量读、追加写为主，放弃随机写
- **Lease 机制**：Primary ChunkServer 决定写入顺序
- **宽松一致性**：Record Append At-Least-Once，应用层处理重复

来源：09_gfs_2003

**核心洞察**：针对工作负载设计，而非追求通用性——放弃 POSIX 兼容、放弃强一致，换取极高吞吐。来源：分布式系统知识图谱 §1.2

### Bigtable（2006）— 结构化宽列存储
**核心设计决策**：
- **列族数据模型**：`row_key + column_family:qualifier + timestamp` → value
- **LSM-Tree 存储引擎**：随机写 → 顺序写 WAL + Memtable → SSTable
- **Tablet 架构**：按行水平分片，三层元数据寻址
- **依赖 Chubby**：Master 选举与 Tablet 归属

来源：12_bigtable_2006

**衍生**：HBase / Cassandra（数据模型）/ LevelDB → RocksDB → TiKV。来源：分布式系统知识图谱 §1.2

### Dynamo（2007）— 最终一致性的工程典范
**核心设计决策**：
- **一致性哈希 + 虚拟节点**：节点增删只迁移局部数据
- **Sloppy Quorum + NWR**：可调一致性参数（R+W > N 保证强一致）
- **向量时钟**：追踪多版本历史，冲突由应用层合并
- **Gossip 协议**：去中心化故障检测，无单点

来源：11_dynamo_2007

**哲学差异**：Dynamo 说"可用性优先，短暂不一致可接受"；Bigtable 说"系统保证正确性"。来源：分布式系统知识图谱 §1.2

### Spanner（2012）— 全球强一致
**核心设计决策**：
- **TrueTime API**：GPS + 原子钟，将时钟误差从 NTP 毫秒降到 ~1-7ms，返回时间区间
- **Commit Wait**：写事务提交时等待 2ε（约 2~14ms），确保外部一致性
- **Paxos Group**：每个 Tablet 是一组跨 Zone 的 Paxos 副本
- **半关系模型 + INTERLEAVE IN PARENT**：相关行物理聚合到同一 Tablet

来源：21_spanner_2012

**核心洞察**：CAP 的 C 与 A 在工程上可同时达到——通过 TrueTime 提供有界时间误差。来源：分布式系统知识图谱 §1.2

## 一致性谱系（强 → 弱）

| 强度 | 模型 | 系统示例 |
|------|------|---------|
| 线性一致 | Linearizability | Spanner（外部一致） |
| 顺序一致 | Sequential | ZAB / Raft 日志顺序 |
| 因果一致 | Causal | Dynamo 向量时钟 |
| 客户端一致 | Client-Specific | ZooKeeper 本地读 |
| 最终一致 | Eventual | Dynamo Gossip 反熵 |

来源：分布式系统知识图谱 §6.1

## 在本项目的相关报告
- [09_gfs_2003](../../reports/paper_analyses/09_gfs_2003.md)
- [11_dynamo_2007](../../reports/paper_analyses/11_dynamo_2007.md)
- [12_bigtable_2006](../../reports/paper_analyses/12_bigtable_2006.md)
- [21_spanner_2012](../../reports/paper_analyses/21_spanner_2012.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- consensus_paxos_raft：Spanner 的 Paxos Group / Bigtable 的 Chubby 协调
- coordination_chubby_zk：GFS / Bigtable 都依赖 Chubby
- lamport_clocks：Dynamo 向量时钟、Spanner TrueTime

## 开放问题
- LSM-Tree 在 NVMe 时代的读放大最优解
- TrueTime 的开源替代（HLC）精度上限
