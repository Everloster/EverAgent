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

<!-- 后续 ingest / query-archive / lint 在此追加 -->
