---
id: concept-mapreduce
title: "MapReduce 与批处理"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [10_mapreduce_2004, 分布式系统知识图谱]
status: active
---

# MapReduce

## 一句话定义
将大规模并行处理抽象为 Map（key/value 转换）+ Reduce（按 key 聚合）两步函数式模型，由框架自动处理分片、调度、容错、数据传输。

## 核心设计决策
- **数据分片（Split）**：64MB 分片，调度器优先将 Map 任务分配到数据所在机器（数据本地性）
- **Shuffle 阶段**：框架自动按 key 分组并跨机传输到 Reducer
- **Straggler 处理**：Backup Tasks（备份任务）应对慢节点——44% 延迟减少，代价仅 5% 资源
- **幂等性**：Map / Reduce 函数无副作用，失败可安全重跑

来源：10_mapreduce_2004

## 为什么重要
将"分布式"的全部复杂性（容错、调度、数据传输）封装在框架中，应用开发者只写两个纯函数。这是"编程模型 → 自动容错"思想的最成功案例。来源：分布式系统知识图谱 §4.2

## 演化脉络
- **MapReduce（2004）→ Hadoop**：开源克隆，催生大数据职业
- **Spark（2012）**：内存中保留 RDD，避免每步落盘，显著快于 MapReduce
- **Flink**：流式优先的下一代批流一体引擎
- **FlumeJava / Beam**：高层 DSL，编译到 MapReduce/Spark/Flink

来源：分布式系统知识图谱 §4.1

## 局限
- 严格两阶段模型表达力有限（迭代算法、图算法低效）
- 中间结果落盘成本高（Spark 改进点）
- 调度延迟使其不适合低延迟查询

## 在本项目的相关报告
- [10_mapreduce_2004](../../reports/paper_analyses/10_mapreduce_2004.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [distributed_storage](./distributed_storage.md)：Map 任务从 GFS 读，Reduce 写回 GFS
- [unix_philosophy](./unix_philosophy.md)：Map/Reduce 是"纯函数管道"在分布式上的延伸
- 函数式编程：纯函数 + 不可变数据 → 自动并行化

## 被引用于
- [distributed_storage](./distributed_storage.md)
- [unix_philosophy](./unix_philosophy.md)

## 开放问题
- 批流一体的最优抽象（DataFlow / Beam vs Spark Structured Streaming）
- Exactly-Once 语义在批处理中的代价
