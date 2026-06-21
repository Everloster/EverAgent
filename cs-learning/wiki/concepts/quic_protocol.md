---
id: concept-quic
title: "QUIC Protocol (RFC 9000)"
type: concept
domain: [cs-learning]
created: 2026-06-21
updated: 2026-06-21
sources: [35_quic_rfc9000_2021]
status: active
---

# QUIC Protocol

## 一句话定义
QUIC（Quick UDP Internet Connections）是 IETF 2021 年标准化的用户态传输协议，架在 UDP 之上、内嵌 TLS 1.3、以 Connection ID 而非 IP:Port 标识连接，提供流多路复用（无 HoL 阻塞）+ 0-RTT/1-RTT 握手 + 连接迁移抗 NAT rebind。

## 核心设计决策

- **UDP 作为承载**：绕过 TCP 内核协议栈与中间盒生态，使协议可在用户态快速迭代（来源：RFC 9000 §1.1）
- **内嵌 TLS 1.3**：握手消息走 CRYPTO 帧（独立流），首次连接 1-RTT、重连 0-RTT（来源：RFC 9001 §4）
- **Connection ID**：连接由 8 字节 CID 标识，与 4-tuple 解耦，实现连接迁移（来源：RFC 9000 §5.1）
- **独立 Streams**：每流独立的流控窗口 + 偏移，单流丢包不阻塞其他流（来源：RFC 9000 §2）
- **可插拔拥塞控制**：CUBIC、BBR、PBB 等共存（来源：RFC 9002 §6）
- **Header Protection**：Packet Number 加密，防止观察者推测流量（来源：RFC 9001 §5.4）

## 关键 RFC 引用

| RFC | 标题 | 角色 |
|-----|------|------|
| RFC 9000 | QUIC: A UDP-Based Multiplexed and Secure Transport | 核心传输 |
| RFC 9001 | Using TLS to Secure QUIC | TLS 1.3 嵌入 |
| RFC 9002 | QUIC Loss Detection and Congestion Control | 丢包恢复 + 拥塞控制参考 |
| RFC 8999 | Invariants for QUIC | 协议不变量 |
| RFC 9221 | Bootstrapping WebSockets with HTTP/3 / Unreliable Datagrams | 不可靠扩展 |
| RFC 9298 | Carrying QUIC over UDP Datagrams | v2 早期 |
| RFC 9287 | Greasing QUIC | 防中间盒特化 |
| RFC 9369 | QUIC Version 2 | v2 正式版 |

## 数据包结构

```
QUIC Packet = Header + Payload (加密)
├── Long Header (握手阶段)
│   ├── Fixed bit + Type
│   ├── Version (32 bit)
│   ├── DCID Length + DCID
│   ├── SCID Length + SCID
│   ├── Token (可选)
│   ├── Packet Number (8/16/32 bit)
│   └── Payload (AEAD 加密)
└── Short Header (1-RTT)
    ├── Fixed bit + Type
    ├── DCID (0/32/64 bit)
    ├── Packet Number (8/16/32 bit)
    └── Payload (AEAD 加密)
```

## Stream 与 Frame

- Stream ID: 62-bit (含方向、初始化方标志)
- Stream 类型: Client/Server-Initiated × Bidirectional/Unidirectional
- 关键帧: STREAM / ACK / CRYPTO / MAX_DATA / MAX_STREAM_DATA / NEW_CONNECTION_ID / PATH_CHALLENGE / DATAGRAM (RFC 9221)

## 握手时序

```
Client                              Server
  |--- Initial (ClientHello) -------->|
  |<-- Initial + Handshake -----------|
  |--- Handshake + 1-RTT data ------->|
  |<-- 1-RTT data --------------------|

重连 0-RTT:
  |--- Initial + 0-RTT (PSK) -------->|
  |<-- Initial + 1-RTT ---------------|
```

## 解决的根本问题

| TCP 缺陷 | QUIC 解法 |
|---------|----------|
| TCP 字节流串行化 → HoL 阻塞 | 独立 streams，单流丢包不阻塞他流 |
| TCP + TLS 至少 2-3 RTT 握手 | 内嵌 TLS 1.3 = 1-RTT（首次）/ 0-RTT（重连） |
| 4-tuple 绑定 → NAT rebind 断连 | Connection ID 与地址解耦 |
| 内核协议栈迭代慢 | 用户态实现，浏览器/库可独立升级 |
| 拥塞控制硬编码 | 可插拔拥塞控制（CUBIC/BBR/PBB） |

## 性能数据（Cloudflare 实测）

| 场景 | HTTP/2 over TLS 1.3 | HTTP/3 over QUIC | 提升 |
|------|---------------------|------------------|------|
| 0% 丢包 RTT | ~80ms | ~50ms | -37% |
| 5% 丢包吞吐 | 12% | 78% | +550% |
| 视频卡顿率（移动） | 6.8% | 1.3% | -80% |

> 来源：Cloudflare "Comparing HTTP/3 vs HTTP/2 Performance"（2020-04 / 2024-03）。

## 演化脉络

- **2012**：Google 内部 gQUIC 启动（Jim Roskind 设计）
- **2016**：IETF QUIC Working Group 成立，重写为通用传输协议
- **2018**：HTTP-over-QUIC 改名 HTTP/3
- **2021.05**：RFC 9000/9001/9002/8999 四件套发布
- **2022.03**：RFC 9221（Unreliable Datagrams）
- **2023.06**：RFC 9369（QUIC v2）
- **2026**：HTTP/3 占主流 CDN 边缘 >50%

## 在本项目的相关报告

- [35_quic_rfc9000_2021](../../reports/paper_analyses/35_quic_rfc9000_2021.md)

## 跨域连接

- [tcp_ip](./tcp_ip.md)：QUIC 是 TCP 在 21 世纪的"二次革命"，保留了端到端可靠性、加入了用户态灵活性
- [tailscale_wireguard_vpn](./tailscale_wireguard_vpn.md)：WireGuard/Tailscale 也用 UDP 隧道绕过 TCP NAT 限制；QUIC 与 WireGuard 是"用户态 UDP 之上的两种抽象"（可靠流 vs 加密隧道）
- [distributed_messaging](./distributed_messaging.md)：Kafka 历史上也曾尝试 KIP-500 替代 ZooKeeper；QUIC 的 Connection ID 给分布式系统的"连接身份"设计提供新范式

## 被引用于
- HTTP/3、Masque、WebTransport、MoQ、DoQ（DNS over QUIC）等下一代协议

## 开放问题
- QUIC v2 部署速度 vs 网络生态收敛速度
- QUIC over IP（绕过 UDP）的工程可行性
- 用户态 QUIC 在数据中心内（高带宽低 RTT）是否真有优势
- DATAGRAM 扩展是否会被滥用为"无监督 UDP"通道

## 主要实现

| 实现 | 语言 | 维护者 |
|------|------|--------|
| quiche | Rust | Cloudflare |
| msquic | C | Microsoft |
| ngtcp2 | C | ngtcp2 项目 |
| quic-go | Go | Lucas Clemente |
| quant | Rust | Lennart Grahl |
| libquic | C++ | Chromium |
| picoquic | C | Private Octopus |