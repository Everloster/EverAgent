---
id: concept-distributed_messaging
title: "分布式消息：Kafka 与日志范式"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [22_kafka_2011, 分布式系统知识图谱]
status: active
---

# 分布式消息系统

## 一句话定义
将"消息队列"重新定义为"持久化追加写日志 + 消费者自主拉取 offset"，使数据流可重放、多消费者共享同一份数据。

## Kafka 核心设计
- **追加写日志**：每个 Partition 是磁盘顺序追加文件，顺序写速度接近内存
- **Pull 模型**：消费者自主控制 offset，Broker 完全无状态（不追踪消费进度）
- **零拷贝**：`sendfile()` 系统调用，数据从磁盘 → socket 不经过用户空间
- **Consumer Group**：同一份数据可被多个独立消费者组并行消费，无需复制
- **ISR 副本**：In-Sync Replicas 保证 `acks=all` 时无数据丢失

来源：22_kafka_2011

## Push vs Pull

| 模型 | 代表 | 特点 |
|------|------|------|
| Push（传统 MQ） | RabbitMQ / ActiveMQ | Broker 主动推，消费者速率不一时易崩溃 |
| Pull（Kafka） | Kafka / Kinesis | 消费者完全控制速率，broker 简化 |

来源：分布式系统知识图谱 §4.3

## 传递语义

| 语义 | 实现 |
|------|------|
| At-Least-Once | Kafka 默认 |
| At-Most-Once | Consumer offset 自动提交 |
| Exactly-Once | 幂等 Producer + 事务 API |

来源：分布式系统知识图谱 §4.3

## 与 TCP/CSP 的关系
Kafka 的追加写日志某种意义上是"持久化的 TCP"——有序、可靠、可重放，但落盘并支持多消费者。Consumer Group 也可视为"持久化的 CSP channel"。来源：分布式系统知识图谱 §4.2

## 应用脉络
- **流处理**：Kafka → Flink / Spark Streaming
- **Schema Registry**：消息格式演进
- **Event Sourcing / CQRS**：将日志作为应用主存储

## 在本项目的相关报告
- [22_kafka_2011](../../reports/paper_analyses/22_kafka_2011.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [tcp_ip](./tcp_ip.md)：依赖 TCP 作为传输层
- [csp_concurrency](./csp_concurrency.md)：Consumer Group ≈ 持久化 channel
- [consensus_paxos_raft](./consensus_paxos_raft.md)：ISR / Leader 选举使用 ZAB（ZooKeeper），Kafka 2.8+ 用自身 KRaft（Raft）替代
- [coordination_chubby_zk](./coordination_chubby_zk.md)：早期 Kafka 用 ZooKeeper 做控制平面

## 被引用于
- [csp_concurrency](./csp_concurrency.md)
- [tcp_ip](./tcp_ip.md)

## 开放问题
- Exactly-Once 的性能上限
- 数据流与批处理的统一接口（Kappa vs Lambda 架构）
