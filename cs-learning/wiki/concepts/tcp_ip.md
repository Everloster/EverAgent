---
id: concept-tcp_ip
title: "TCP/IP 与端到端论点"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [19_tcpip_1974, 分布式系统知识图谱]
status: active
---

# TCP/IP

## 一句话定义
Cerf & Kahn 1974 年提出的分组交换网络互联架构：无状态网关连接异构网络，可靠性由端系统而非网络保证。

## 核心设计决策
- **网关（Gateway）概念**：无状态路由，连接异构网络，不解释也不修改有效载荷
- **端到端论点（End-to-End Argument）**：可靠性由端系统保证，网络只做尽力而为转发
- **逻辑进程间连接**：五元组 `(src_ip, src_port, dst_ip, dst_port, protocol)` 标识连接
- **TCP 重传 + 滑动窗口**：序号、ACK、超时重传、流量控制

来源：19_tcpip_1974

## 端到端论点的深远影响
端到端论点是 Internet 区别于电话网（智能网络 + 哑终端）的根本差异。它使 Internet 成为可以承载任何上层应用的中立平台——HTTP / Email / BitTorrent / 视频流都共享同一条 TCP/IP 管道。来源：19_tcpip_1974

## 演化脉络
- **1978**：TCP 拆分为 TCP + IP，路由功能移到 IP 网络层
- **1987**：DNS（[dns](./dns.md)）建立在 TCP/IP 之上，把"全球命名"做成应用层服务
- **1988**：Jacobson 拥塞控制（slow start / AIMD），解决 1986 年互联网拥塞崩溃
- **1990s**：NAT 缓解 IPv4 地址耗尽
- **2000s+**：IPv6、QUIC（基于 UDP 的可靠传输）

来源：分布式系统知识图谱 §4.2

## 为什么对分布式系统重要
所有分布式系统都建立在 TCP/IP 之上：MapReduce、Dynamo、Kafka、Spanner……"无状态网络 + 端系统负责可靠性"是整个分布式大厦的地基。来源：分布式系统知识图谱 §4.2

## 在本项目的相关报告
- [19_tcpip_1974](../../reports/paper_analyses/19_tcpip_1974.md)
- [分布式系统知识图谱](../../reports/knowledge_reports/分布式系统知识图谱.md)

## 跨域连接
- [dns](./dns.md)：DNS 是 TCP/IP 之上最早的应用层协议
- [distributed_messaging](./distributed_messaging.md)：Kafka 是"持久化的 TCP"
- [coordination_chubby_zk](./coordination_chubby_zk.md)：ZooKeeper 用 UDP 而非 TCP 心跳的工程教训
- [unix_philosophy](./unix_philosophy.md)：sockets 是 Unix 思想在网络上的延伸
- [information_theory](./information_theory.md)：Shannon 的信道容量与噪声编码定理是 TCP 重传与 FEC 的理论上界

## 被引用于
- [dns](./dns.md)
- [distributed_messaging](./distributed_messaging.md)

## 开放问题
- QUIC 取代 TCP 的边界
- 数据中心内 RDMA / 用户态网络栈对 TCP 端到端模型的挑战
