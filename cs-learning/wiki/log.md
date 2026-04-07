# cs-learning · Wiki 操作日志

> append-only。每次 ingest / query-archive / lint 追加一条记录。
> 格式：`## [YYYY-MM-DD] {操作类型} | {标题}`
> 快速查看最近 5 条：`grep "^## \[" log.md | tail -5`

---

## [2026-04-07] phase2-init | Phase 2 起步：cs-learning wiki 内容蒸馏
- 新建 entities：turing_alan / shannon_claude / lamport_leslie / dijkstra_edsger / hoare_tony / thompson_ritchie / knuth_donald / dean_ghemawat / cerf_kahn / torvalds_linus / bell_labs / google_research / mit_csail（共 13 个）
- 新建 concepts：lamport_clocks / consensus_paxos_raft / byzantine_fault_tolerance / distributed_storage / coordination_chubby_zk / mapreduce / dht_chord / csp_concurrency / tcp_ip / distributed_messaging / unix_philosophy（共 11 个）
- 新建 overview.md：四主线 + 技术拐点 + 概念依赖图 + 缺失页面清单
- 更新 index.md：将所有 entity / concept / overview 登记到对应表格
- 数据源：CS关键人物图谱、分布式系统知识图谱、DHT实战排查、01_turing_1950、02_shannon_1948、04_unix_1974、05_lamport_clocks_1978、08_byzantine_generals_1982、09_gfs_2003、10_mapreduce_2004、11_dynamo_2007、12_bigtable_2006、13_paxos_2001、14_zookeeper_2010、15_raft_2014、18_csp_1978、19_tcpip_1974、21_spanner_2012、22_kafka_2011、23_ffs_1984、28_chord_2001、29_chubby_2006
- 状态：plan §8 短期标准 ≥10 entities / ≥8 concepts 双双满足

## [2026-04-07] query-archive | Spanner TrueTime 与 CAP 反例
- 触发查询：Spanner 如何用 TrueTime + Paxos + 半关系模型同时拿到全球强一致与水平扩展？为什么常被称作 CAP 反例？
- 涉及概念：distributed_storage / consensus_paxos_raft / lamport_clocks（≥3，按 plan §3.2 归档）
- 新建：syntheses/spanner_truetime_cap.md
- 更新：index.md syntheses 表新增条目
- 数据源：21_spanner_2012、13_paxos_2001、05_lamport_clocks_1978、分布式系统知识图谱

## [2026-04-07] lint-fix | lamport_clocks.md 补并发反例与向量时钟规则
- 触发：Phase 2 cs-learning 闭环验证 Q2（Lamport Clock 为何无法检测并发？向量时钟怎么修复？）发现缺细节
- 修补 1：给出"两进程独立事件 C 值可比但实际并发"的反例
- 修补 2：补向量时钟的 n 维计数器更新规则与并发判定 V(a) ∥ V(b) 的逐分量定义
- 数据源：05_lamport_clocks_1978 §3 / 分布式系统知识图谱 §6.2
- 验证结论：Q1 ✅ 全 wiki 可答；Q2 ⚠️→✅ 已补全后可答

## [2026-04-07] lint-pass | Phase 2.5 Lint #1：cs-learning wiki 全量健检
- 扫描范围：18 concepts + 13 entities + overview + index + log + 1 synthesis（共 35 页面）
- 发现项：
  - **缺失概念**：7 个（cap_theorem / two_phase_commit / consistent_hashing / linearizability_vs_serializability / dns / information_theory / computation_theory）
  - **孤岛页面**：dht_chord / mapreduce / unix_philosophy 仅有出向链接，无入向
  - **单向引用**：distributed_storage→lamport_clocks、dht_chord→{distributed_storage, consensus}、tcp_ip→coordination_chubby_zk 等多处缺反向
  - **矛盾点**：distributed_storage Spanner vs Dynamo、dht_chord 最终一致 vs 强一致存储、consensus_paxos_raft Paxos vs Raft（均与 overview §4 已有分歧条目对应）
  - **旧层重复**：knowledge/ 4 个文件（432 行）与 wiki/ 内容重叠
- 修补行动 → 见下三条记录

## [2026-04-07] phase2.5-build | 补 7 个缺失 concept 页
- 新建：cap_theorem / two_phase_commit / consistent_hashing / linearizability_vs_serializability / dns / information_theory / computation_theory
- 每页结构：frontmatter + 一句话定义 + 核心原理 + 演化脉络 + 报告链接 + 跨域连接 + 被引用于 + 开放问题
- 数据源：11_dynamo_2007 / 21_spanner_2012 / 28_chord_2001 / 30_dns_1987 / 19_tcpip_1974 / 02_shannon_1948 / 01_turing_1950 / 分布式系统知识图谱

## [2026-04-07] cross-link | concept 双向链接审计 + 矛盾标注
- 为 11 个旧 concept 全部追加 `## 被引用于` 区块（concept-to-concept + synthesis）
- 修复单向引用：distributed_storage 跨域连接从 3 条扩到 9 条；tcp_ip 演化脉络注入 dns；dht_chord 注入 consistent_hashing 区分说明
- 注入 ⚠️ 矛盾标记 3 处：distributed_storage（Spanner vs Dynamo）/ consensus_paxos_raft（Paxos vs Raft）/ dht_chord（最终一致 vs 强一致），均链回 overview §4
- entity 反向链接本轮不做（仅保持现有 entity→concept 单向）

## [2026-04-07] deprecate | knowledge/ 旧层标记
- 为 cs-learning/knowledge/{INDEX,foundations,distributed_systems,key_figures}.md 顶部插入 deprecated banner
- 每条 banner 标明对应迁移目标（→ wiki/index.md / wiki/concepts/{...}.md / wiki/entities/）
- 旧文件不删除以维持 git 历史与外部引用兼容
- CONTEXT.md / AGENTS.md 中对 knowledge/ 路径的旧引用本轮不动，留给后续摄入触发清理

## [2026-04-07] lint-pass | Phase 2.5 Lint #2：回归验证 + 新孤岛修补
- 扫描范围：18 concepts + 13 entities + overview + index + log + 1 synthesis（共 35 页面）
- **回归验证**（Phase 2.5 修补效果）：
  - ✅ 18/18 concepts 均含 `## 被引用于` 区块
  - ✅ 7 个新 concept 全部有实质内容（60-120 行，非 stub）
  - ✅ 原 3 个孤岛已破：mapreduce 入向 2、unix_philosophy 入向 5、dht_chord 入向 2
  - ✅ 3 处 ⚠️ 矛盾标记（distributed_storage / consensus_paxos_raft / dht_chord）均链回 overview §4
- **新发现问题**：
  - ⚠️ Phase 2.5 引入双节点孤岛：information_theory ↔ computation_theory 仅互引，未被任何应用层 concept 反链
- **本轮修补**（共 6 个文件）：
  - tcp_ip → information_theory（Shannon 信道容量是 TCP 重传/FEC 理论上界）
  - distributed_messaging → information_theory（日志压缩/Schema Registry 是熵编码）
  - lamport_clocks → computation_theory（异步系统时序与 FLP 同源于可计算性边界）
  - consensus_paxos_raft → computation_theory（FLP 不可能性是异步共识可计算性下界）
  - information_theory `## 被引用于` 增补 tcp_ip / distributed_messaging
  - computation_theory `## 被引用于` 增补 lamport_clocks / consensus_paxos_raft
- 验证结论：Phase 2.5 收尾完成，wiki 双向链接图完全闭合（18 concept 节点、0 孤岛、3 矛盾标记锚定 overview）

<!-- 后续 ingest / query-archive / lint 在此追加 -->
