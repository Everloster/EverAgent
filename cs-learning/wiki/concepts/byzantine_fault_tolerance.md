---
id: concept-byzantine_fault_tolerance
title: "拜占庭容错（BFT）"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [08_byzantine_generals_1982, 分布式系统知识图谱]
status: active
---

# 拜占庭容错（Byzantine Fault Tolerance）

## 一句话定义
将共识问题从"节点崩溃停机"扩展到"节点可能恶意欺骗"——即使部分节点说谎、伪造消息，系统仍能达成一致。

## 核心结果
**n ≥ 3f + 1 下界**：要容忍 f 个恶意节点，至少需要 3f+1 个总节点数。这是 Lamport / Shostak / Pease 1982 年的核心定理。来源：08_byzantine_generals_1982 §2

**Oral Message 算法 OM(m)**：
- 递归多数投票
- 消息复杂度 O(n^m)
- 同步系统假设

来源：08_byzantine_generals_1982 §3

**Signed Message 算法**：
- 用密码学签名让消息可验证
- 复杂度降到 O(n²)
- 容错可提升到任意 f（无 3f+1 限制）

来源：08_byzantine_generals_1982 §4

## 为什么重要
拜占庭故障模型是区块链、太空系统、金融交易等高可靠性场景的理论基础。来源：分布式系统知识图谱 §2.2

## 演化脉络
- **PBFT（1999, Castro & Liskov）**：第一个工业级 BFT 实现，部分同步假设
- **Tendermint**：Cosmos 区块链共识
- **Bitcoin PoW**：将共识成本外化为工作量证明
- **Ethereum PoS**：继承 BFT 传统的权益证明

来源：分布式系统知识图谱 §2.1

## 与崩溃容错（CFT）的对比

| 维度 | CFT（Paxos/Raft） | BFT（PBFT/Byzantine） |
|------|------|------|
| 故障模型 | 节点崩溃停机 | 节点可能任意行为（包括恶意） |
| 节点下界 | 2f+1 | 3f+1 |
| 复杂度 | O(n) 消息 | O(n²) 消息（带签名） |
| 典型场景 | 数据中心内部 | 区块链 / 跨信任域 |

来源：分布式系统知识图谱 §2.3

## 在本项目的相关报告
- [08_byzantine_generals_1982](../../reports/paper_analyses/08_byzantine_generals_1982.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- consensus_paxos_raft：BFT 是其在恶意节点下的扩展
- 区块链共识（PoW/PoS）

## 开放问题
- BFT 在 WAN 环境下的吞吐上限
- BFT 与 sharding / 分片的组合方案
