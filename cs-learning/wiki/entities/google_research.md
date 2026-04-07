---
id: entity-google_research
title: "Google Research"
type: entity/org
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [CS关键人物图谱, 09_gfs_2003, 10_mapreduce_2004, 12_bigtable_2006, 21_spanner_2012, 29_chubby_2006]
---

# Google Research

## 身份
Google 内部的工业研究机构。2000s 初一系列分布式系统论文奠定了大数据时代的基础设施范式。来源：CS关键人物图谱 §第三代

## 核心贡献（分布式系统维度）
- **GFS（2003）**：分布式文件系统范式。来源：09_gfs_2003
- **MapReduce（2004）**：大规模并行计算模型。来源：10_mapreduce_2004
- **Bigtable（2006）**：结构化分布式存储 + LSM-Tree。来源：12_bigtable_2006
- **Chubby（2006）**：分布式锁 + 命名服务。来源：29_chubby_2006
- **Spanner（2012）**：TrueTime + 全球强一致事务。来源：21_spanner_2012

## 关键人物
Jeff Dean、Sanjay Ghemawat、Mike Burrows（Chubby）、Andrew Fikes 等。

## 在本项目的相关报告
- [09_gfs_2003](../../reports/paper_analyses/09_gfs_2003.md)
- [10_mapreduce_2004](../../reports/paper_analyses/10_mapreduce_2004.md)
- [12_bigtable_2006](../../reports/paper_analyses/12_bigtable_2006.md)
- [21_spanner_2012](../../reports/paper_analyses/21_spanner_2012.md)
- [29_chubby_2006](../../reports/paper_analyses/29_chubby_2006.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 历史影响
Google 的论文公开（而非保留商业秘密）直接催生了 Hadoop / HBase / Cassandra / Kubernetes 等开源生态。"每一篇 Google 论文 → 一个开源项目"几乎成了 2000s–2010s 大数据生态的元规律。
