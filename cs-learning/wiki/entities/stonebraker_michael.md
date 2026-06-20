# Michael Stonebraker

> **生卒**：1943-10-11 (Stoneham, MA, USA)
> **领域**：数据库系统（Ingres, POSTGRES, 各种商业衍生品）
> **首次归档**：2026-06-21（ByteAgent · 数据库50年演化）

## 关键贡献

- **1973-79**：在 UC Berkeley 主持 **Ingres** 项目（与 Eugene Wong, Gerald Held），使用 **QUEL** 查询语言（早于 Oracle 的 SQL 商业实现）。
- **1976-80**：Ingres 衍生出 **Ingres Corp.**（Sybase 同源前身之一）和 **Relational Technology Inc.**，孕育 Sybase 与早期的 Microsoft SQL Server。
- **1986-94**：主持 **POSTGRES** 项目，引入**对象-关系模型**、用户自定义类型、规则系统、复杂对象。
- **1995**：学生 Andrew Yu 和 Jolly Chen 将 POSTGRES 改造为 Postgres95，加入 SQL 解释器。
- **2014 Turing Award**："For fundamental contributions to the concepts and practices that have improved the functionality, reliability, and performance of database systems."

## 商业化成果（Berkeley 衍生）

| 项目 | 衍生公司 / 现状 |
|------|----------------|
| Ingres (1976) | RTI → ASK-Ingres → Computer Associates Ingres |
| POSTGRES (1986) | Illustra → Informix (1996 收购) → IBM Informix |
| Mariposa (1995) | Cohera → Oracle 2001 收购 |
| VoltDB (2010) | Mike Stonebraker 联合创办，NewSQL 内存数据库 |
| Tamr (2013) | 企业级数据整合 |
| Paradigm4 (2014) | SciDB (科学计算数组数据库) |

## 在本项目 (cs-learning) 的影响

- **Ingres / POSTGRES** 谱系是本项目 **`reports/knowledge_reports/数据库50年演化_从层次到向量库_20260621.md`** 的核心节点。
- 通过 POSTGRES → PostgreSQL 影响了 **数据仓库、HTAP、向量检索（pgvector）** 三条 2010s-2020s 路线。
- 2014 Turing Award 与本项目已记录的 **2013 Lamport Turing、2012 Goldwasser & Rabin (已记)/Silvio Micali (已记)** 共同构成 2010s 系统方向图灵奖序列。

## 关键人物关系

- **Eugene Wong, Gerald Held** — Ingres 共同作者
- **Andrew Yu, Jolly Chen** — Postgres95 关键学生 → PostgreSQL 起点
- **Gerald Brose, Wei Hong** — 早期 POSTGRES 博士生
- **Joseph Hellerstein** (Berkeley) — 数据库系统教学与研究同道
- **Andy Pavlo** (CMU) — 2014 年起 Stonebraker 教学承继者，15-445 课程

## 学术与教学影响

- 长期教授 UC Berkeley CS286 (Implementation of Database Systems) — 培养大量工业界数据库领袖
- 撰写 *Readings in Database Systems* (俗称 "Red Book") — 数据库领域事实教科书
- CMU Database Group (Andy Pavlo) 公开致谢其学术影响

## 来源

- ACM Turing Award 2014
- *The Land Sharks are on the Slide* (CACM 2016, Stonebraker 撰)
- Stonebraker 个人主页 (MIT CSAIL)
- POSTGRES 历史 (postgresql.org)
