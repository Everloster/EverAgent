# cs-learning — Project Context

**领域**：计算机科学基础·系统·算法·分布式
**三维度**：理论深度 × 系统演化 × 工程实践

## 已有报告
**论文精读** (`reports/paper_analyses/`)
- `01_turing_1950` — Computing Machinery and Intelligence，图灵测试奠基
- `02_shannon_1948` — A Mathematical Theory of Communication，信息熵·信道容量·Shannon极限（2026-03-25）
- `10_mapreduce_2004` — MapReduce，大规模数据处理范式
- `12_bigtable_2006` — 列族模型·LSM-Tree·分布式结构化存储·HBase/Cassandra原型（2026-03-25）
- `05_lamport_clocks_1978` — happens-before偏序·逻辑时钟·全序扩展·分布式互斥算法·向量时钟先驱（2026-03-26）
- `09_gfs_2003` — Google文件系统·单Master+ChunkServer·64MB大块·Lease机制·追加写语义·Hadoop HDFS原型（2026-03-26）
- `11_dynamo_2007` — Amazon高可用KV存储·一致性哈希·Sloppy Quorum·向量时钟·Gossip·Merkle Tree反熵·AP系统典范（2026-03-26）
- `13_raft_2014` — 可理解性优先共识算法·强Leader+随机超时选举·日志复制两阶段·五大安全性质·etcd/TiKV/CockroachDB原型（2026-03-26）

**知识深度解析** (`reports/knowledge_reports/`)
- `CS关键人物图谱` — 图灵→香农→Dijkstra→现代系统工程师的思想传承

## 离线知识库
→ [`knowledge/INDEX.md`](./knowledge/INDEX.md)

## Skills
- `skills/paper_analysis/SKILL.md` — CS 论文 7 步分析法
- `skills/knowledge_deep_dive/SKILL.md` — CS 概念 5 层理解模型

## 导航
- 学习路径：`roadmap/Learning_Roadmap.md`
- 论文索引：`papers/PAPERS_INDEX.md`（30 篇）
- 书籍索引：`books/BOOKS_INDEX.md`（25 部）

## ⚠️ 边界（防幻觉）
以下内容**尚未研究**，禁止推测，须告知用户：
- OS、网络、编译器等方向尚无独立精读报告
- 论文索引中列出的大多数论文**未精读**（仅有索引，无分析报告）
- #02 Shannon (1948) ✅ 已完成（02_shannon_1948）
- #12 Bigtable (2006) ✅ 已完成（12_bigtable_2006）
- #05 Lamport Clocks (1978) ✅ 已完成（05_lamport_clocks_1978）
- #09 GFS (2003) ✅ 已完成（09_gfs_2003）
- #11 Dynamo (2007) ✅ 已完成（11_dynamo_2007）
- #13 Raft (2014) ✅ 已完成（13_raft_2014）
- 下一步推荐：Spanner (#14)、Zookeeper (Zab 协议)、Paxos Made Simple 对比
