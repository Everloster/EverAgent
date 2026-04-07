---
id: entity-lamport_leslie
title: "Leslie Lamport"
type: entity/person
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [CS关键人物图谱, 05_lamport_clocks_1978, 08_byzantine_generals_1982, 13_paxos_2001]
---

# Leslie Lamport（1941– ）

## 身份
美国计算机科学家。SRI → Compaq → Microsoft Research（2001 至今）。分布式系统理论的核心奠基人，2013 年图灵奖得主。来源：CS关键人物图谱 §第二代

## 核心贡献
- **Lamport 时钟（1978）**：用消息传递定义 happens-before 偏序，奠定分布式时序的数学基础。来源：05_lamport_clocks_1978
- **拜占庭将军问题（1982，与 Shostak、Pease）**：将共识问题从崩溃故障扩展到恶意节点，给出 n ≥ 3f+1 下界。来源：08_byzantine_generals_1982
- **Paxos 共识算法（1989 写成，1998/2001 发表）**：分布式共识算法的理论标准。原稿《The Part-Time Parliament》以希腊议会故事包装被拒稿，2001 年《Paxos Made Simple》才广为采用。来源：13_paxos_2001 / CS关键人物图谱 §Lamport
- **LaTeX（1984）**：基于 Knuth 的 TeX 构建的学术排版系统。来源：CS关键人物图谱 §Lamport
- **TLA+（1999）**：时序逻辑规范语言，被 AWS、Microsoft 用于关键系统规范。来源：CS关键人物图谱 §Lamport

## 核心洞察
"分布式系统的根本问题是：多台机器只同意一件事（共识），就需要如此复杂的协议。"来源：CS关键人物图谱 §Lamport

## 在本项目的相关报告
- [05_lamport_clocks_1978](../../reports/paper_analyses/05_lamport_clocks_1978.md)
- [08_byzantine_generals_1982](../../reports/paper_analyses/08_byzantine_generals_1982.md)
- [13_paxos_2001](../../reports/paper_analyses/13_paxos_2001.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 传承影响
- Paxos → Raft（Ongaro 2014）→ etcd → Kubernetes 状态管理
- Lamport Clock → 向量时钟（Dynamo）→ HLC（CockroachDB）
- TLA+ → AWS 关键系统形式化验证
