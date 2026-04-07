---
id: entity-dean_ghemawat
title: "Jeff Dean & Sanjay Ghemawat"
type: entity/person
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [CS关键人物图谱, 09_gfs_2003, 10_mapreduce_2004, 12_bigtable_2006, 21_spanner_2012]
---

# Jeff Dean（1968– ）& Sanjay Ghemawat（1966– ）

## 身份
Google 最传奇的工程师搭档（1999 至今）。共同设计了 Google 早期分布式基础设施核心组件。Dean 后任 Google AI 高级副总裁，主导 Google Brain。来源：CS关键人物图谱 §第三代

## 核心贡献（合作）
- **GFS（2003，Ghemawat 主作者）**：分布式文件系统的奠基之作，支撑 Google 数据基础设施。来源：09_gfs_2003
- **MapReduce（2004）**：大规模并行处理的编程抽象，催生整个 Hadoop 生态。来源：10_mapreduce_2004
- **Bigtable（2006）**：宽列存储模型 + LSM-Tree 引擎，Google 内部 60+ 系统的存储底座。来源：12_bigtable_2006
- **Spanner（2012）**：基于 TrueTime 的全球分布式数据库，证明 CAP 的 C 与 A 在工程上可同时达到。来源：21_spanner_2012

## 传奇故事
2000 年 Google 服务器崩溃，两人花数天时间手动重建大部分数据，因为他们对系统每个细节了如指掌。来源：CS关键人物图谱 §Dean_Ghemawat

## 在本项目的相关报告
- [09_gfs_2003](../../reports/paper_analyses/09_gfs_2003.md)
- [10_mapreduce_2004](../../reports/paper_analyses/10_mapreduce_2004.md)
- [12_bigtable_2006](../../reports/paper_analyses/12_bigtable_2006.md)
- [21_spanner_2012](../../reports/paper_analyses/21_spanner_2012.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 传承影响
GFS + MapReduce + Bigtable 三篇论文直接催生 Hadoop / HDFS / HBase / Spark 生态，开启大数据工程师这一职业。
