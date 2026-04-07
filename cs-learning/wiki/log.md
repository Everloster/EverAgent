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

<!-- 后续 ingest / query-archive / lint 在此追加 -->
