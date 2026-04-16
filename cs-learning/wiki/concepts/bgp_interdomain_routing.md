---
name: "BGP 与互联网域间路由"
type: concept
domain: cs-learning
created: 2026-04-16
source_reports:
  - reports/paper_analyses/31_bgp_rfc4271_2006.md
---

# BGP 与互联网域间路由

## 核心概念

BGP-4（RFC 4271）是路径向量协议，运行于 TCP 179 端口，负责在自治系统（AS）之间交换路由信息。它是互联网"黏合剂"：所有 AS 之间的路由通告与撤销均通过 BGP 完成。

## 关键机制

**路径向量防环**：AS_PATH 属性记录路由经过的所有 AS 号。若本 AS 号已在 AS_PATH 中，丢弃该路由，从根本上避免路由环路。

**四种消息类型**：
- OPEN（29字节最小）：建立会话，协商参数
- UPDATE：通告新路由（含路径属性）或撤销旧路由
- KEEPALIVE（19字节）：保活，每 Hold Time/3 发送一次
- NOTIFICATION：错误报告，发送后立即关闭 TCP 连接

**六态有限状态机**：
`Idle → Connect → Active → OpenSent → OpenConfirm → Established`

**路径属性优先级**（选路顺序）：
```
LOCAL_PREF（越高越优）
→ AS_PATH 长度（越短越优）
→ ORIGIN 类型（IGP < EGP < INCOMPLETE）
→ MED（越低越优）
→ eBGP 优于 iBGP
→ IGP 度量 → Router-ID（最终打平仲裁）
```

## iBGP vs eBGP

| 维度 | iBGP | eBGP |
|------|------|------|
| 范围 | 同一 AS 内 | 不同 AS 之间 |
| TTL | 通常不限 | 默认 1（直连） |
| 拓扑要求 | 全互联或路由反射器 | 点对点 |
| LOCAL_PREF 传递 | 是 | 否 |

## CIDR 与路由聚合

BGP-4 引入 CIDR，废弃 A/B/C 类网络概念：
- 用 `{前缀, 前缀长度}` 表示路由
- 支持聚合：`192.168.0.0/24` + `192.168.1.0/24` → `192.168.0.0/23`
- 有效遏制路由表爆炸（全球表已超 100 万条）

## 重要安全事件

- **2008 Pakistan Telecom YouTube 劫持**：错误通告更精确前缀，流量被重定向约 90 分钟
- **2014 "512k Day"**：路由表超出部分路由器 TCAM 限制，触发大规模中断
- **解决方向**：RPKI（RFC 6480）提供路由来源验证，但部署尚不完整

## 在 CS 基础体系中的位置

```
TCP/IP (1974) ──→ BGP 的传输层（TCP 179）
DNS (1987)    ──→ 与 BGP 共同构成互联网寻址体系
BGP-4 RFC 4271 (2006)
    ↓ 扩展
MP-BGP (IPv6) / Route Reflector / RPKI / EVPN
```

## 与相关概念的关联

- → `tcp_ip.md`（BGP 运行于 TCP 之上）
- → `dns.md`（互联网基础设施的另一支柱）
- → `distributed_messaging.md`（大规模分布式通信协议设计的类比）
