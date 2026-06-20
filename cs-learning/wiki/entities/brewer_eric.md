# Eric Brewer

> **领域**：分布式系统理论、计算经济学
> **代表贡献**：CAP 定理
> **首次归档**：2026-06-21（ByteAgent · 数据库50年演化）

## 关键贡献

- **2000**：在 ACM **PODC** (Principles of Distributed Computing) 大会 keynote 上提出 **CAP Conjecture** (论文 *"Towards Robust Distributed Systems"*)。猜想：在网络分区 (P) 存在时，分布式系统无法同时保证强一致性 (C) 与可用性 (A)。
- **2002**：Seth Gilbert 与 Nancy Lynch 在 *SIGACT News* 33(2) 发表 *"Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services"*，对猜想给出**严格证明**。
- **2012 / 2017**：Brewer 撰写 *"CAP Twelve Years Later: How the 'Rules' Have Changed"*，澄清：
  - P 在分布式系统中几乎必然 → 实际是 C vs A 二选一
  - "2 of 3" 是分区下的瞬时选择；分区恢复后可调整
  - "一致性" 在 CAP 中特指 *linearizability*（与 ACID 的"一致性"语义不同）

## 职业轨迹

- **UC Berkeley** 教授（1989-）：Inktomi 联合创始人 (1996)，后被 Yahoo 收购
- **Google** VP of Infrastructure (2011-)：亲身领导大规模分布式系统
- **Amazon** (2021-)：继续推动分布式系统理论

## 在本项目 (cs-learning) 的影响

- **CAP 定理** 是本项目 **`reports/knowledge_reports/数据库50年演化_从层次到向量库_20260621.md`** 的三大理论支柱之一。
- CAP 解释 Dynamo (本项目 11) 与 Spanner (本项目 21) 的工程选择：Dynamo 选 AP；Spanner 选 CP。
- 与 **本项目 wiki/concepts/cap_theorem.md** 直接关联 — 已有更详细的"12 年后"修正讨论。

## 关键人物关系

- **Seth Gilbert, Nancy Lynch** (MIT CSAIL) — CAP 严格证明者
- **Daniel Abadi** — 进一步发展 PACELC 扩展
- **Werner Vogels** (Amazon CTO) — CAP 在工业实践的最主要发言人
- **Jeff Dean, Sanjay Ghemawat** (Google) — CAP 影响下设计 Bigtable / Spanner

## 来源

- *Towards Robust Distributed Systems* (PODC 2000 keynote)
- *CAP Twelve Years Later* (IEEE Computer 2012)
- Gilbert & Lynch, *Brewer's Conjecture and the Feasibility...* (SIGACT News 2002)
- Wikipedia

