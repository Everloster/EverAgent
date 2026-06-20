# 数据库演化 (Database Evolution)

> **范围**：1966-2026 的通用目的数据管理技术 6 代范式
> **核心思想**：数据库始终在"一致性 × 可用性 × 分区容忍 × 查询表达力"的四维空间做工程折中
> **首次归档**：2026-06-21（ByteAgent）

## 一句话定义

**数据库演化 = 数据模型范式（层次/网状/关系/对象-关系/键值-文档-列族-图/向量）× 一致性模型（ACID/BASE/CAP）× 系统架构（存算一体 / 存算分离 / Serverless）× 查询范式（导航式 / 声明式 SQL / 多模型 / LLM-native）的 50 年迭代史。**

## 6 代范式时间线

| 代 | 年代 | 代表 | 关键论文 / 起源 | 关键人物 |
|----|------|------|------------------|----------|
| 1 | 1960s-70s | IMS (1968), DBTG (1969/71) | IBM / CODASYL | Vernon Watts, Charles Bachman (Turing 1973) |
| 2 | 1970s-80s | Codd 1970, System R (1974-79), Ingres, Oracle v2 (1979) | CACM / SIGMOD | Codd (Turing 1981), Chamberlin, Boyce, Stonebraker (Turing 2014) |
| 3 | 1980s-2000s | POSTGRES (1986), Inmon DW (1990), OLAP 12 rules (1993), PostgreSQL 6.0 (1997) | ACM TODS | Stonebraker, Inmon, Kimball, Codd (OLAP) |
| 4 | 2000s-2010s | Bigtable (2006), Dynamo (2007), Cassandra (2008), MongoDB (2009), Redis (2009), Neo4j | OSDI/SOSP | Dean, Ghemawat, Lakshman, Vogels |
| 5 | 2010s-2020s | Spanner (2012), Aurora (2014), Snowflake (2014/16), CockroachDB (2015), TiDB (2016) | OSDI / SIGMOD | Corbett, Verbitski, Dageville, Kimball |
| 6 | 2020s- | Pinecone (2019), Milvus (2019), Weaviate (2019), Qdrant (2021), SurrealDB, MongoDB 8.0 vectorSearch | 各家文档 | Edo Liberty, Charles Xie (Zilliz), Bob van Luijt |

## 三大理论支柱

| 维度 | ACID (Reuter & Härder 1983) | BASE (Pritchett 2008) | CAP (Brewer 2000 / Gilbert-Lynch 2002) |
|------|----------------------------|----------------------|----------------------------------------|
| **核心** | 4 个事务性质 | 3 个反 ACID 性质 | 3 选 2 不可能三角 |
| **动机** | 商业事务系统理论化 | Dynamo 实践命名 | 分布式正确性边界 |
| **适用** | 单机/小集群强事务 | 大规模分布式 | 任何分布式系统设计 |
| **典型系统** | Oracle, PostgreSQL, Spanner, CockroachDB | Dynamo, Cassandra, Cosmos DB | Spanner (CP) / Cassandra (AP) |

**三者是正交的**：ACID/BASE 描述事务模型；CAP 描述分布式系统在分区下的权衡。常见混用是误读。

## 存算关系演化

| 时期 | 架构 | 代表 |
|------|------|------|
| 1979-2010 | 存算一体 | Oracle, MySQL, PostgreSQL |
| 2010-2020 | 存算分离 | Snowflake, Aurora, BigQuery, Redshift Spectrum |
| 2020- | 存算协同可独立扩展 | Snowflake 多虚拟仓, Aurora Serverless v2, Snowpark, Neon (2022) |

## 关键人物

- **Edgar F. Codd** (IBM San Jose, 1923-2003) — 1970 关系模型，1981 Turing
- **Charles Bachman** (Honeywell/GE, 1924-2017) — 1960s IDS, DBTG chair, 1973 Turing
- **Donald Chamberlin & Raymond Boyce** (IBM) — SEQUEL/SQL 设计
- **Michael Stonebraker** (Berkeley) — Ingres, POSTGRES, 2014 Turing
- **Jim Gray** (IBM → Microsoft) — 事务处理理论, 1998 Turing
- **Eric Brewer** (UC Berkeley → Google → Amazon) — CAP 猜想 (2000)
- **Werner Vogels** (Amazon CTO) — Dynamo 2007
- **Jeff Dean & Sanjay Ghemawat** (Google) — MapReduce, Bigtable, Spanner
- **Benoît Dageville & Thierry Cruanes** (ex-Oracle → Snowflake) — Snowflake Elastic DW

## 与本项目其他报告的衔接

- ✅ 已精读 Bigtable (12), Dynamo (11), Spanner (21), Chubby (29)
- ⏭️ 计划：Codd 1970 独立精读、POSTGRES 1986 内部实现专题、Aurora SIGMOD 2018 精读

## 衍生阅读

- *Database System Concepts* (Silberschatz 7th ed, 2019)
- *Designing Data-Intensive Applications* (Kleppmann, 2017)
- *A Brief History of Database Systems* (CACM 50-Years Retrospective)
- *Fifty Years of Queries* (Chamberlin, CACM 2018)
