---
id: concept-dns
title: "DNS：分布式层级命名"
type: concept
domain: [cs-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [30_dns_1987, 19_tcpip_1974]
status: active
---

# DNS（Domain Name System）

## 一句话定义
将命名空间组织为倒置树形层级，通过委托授权（delegation）让每个 zone 由独立机构管理，配合缓存与递归/迭代查询，实现一个无需中央数据库的全球命名服务。

## 历史背景
1980s 初 ARPANET 用 `/etc/hosts` 文件集中管理主机名，每周从 SRI-NIC 通过 FTP 分发。1983 年 Flag Day 切换到 TCP/IP 后主机数激增，集中文件方案彻底崩溃。1987 年 Mockapetris 等人发布 RFC 1034/1035 建立 DNS。来源：30_dns_1987 §背景

## 核心设计

### 1. 层级命名空间
```
                  [.] (root)
                 /    |    \
              .com  .org  .net   ← TLD（顶级域）
              /          \
       example.com    google.com
            /    \
       www       mail
```
- 标签 ≤ 63 字符，FQDN 总长 ≤ 255 字符，大小写不敏感
- **域 vs 主机**：域是子树，主机是叶节点

来源：30_dns_1987 §技术方案

### 2. Zone 与委托授权
- **Zone** = DNS 树中由同一权威机构管理的连续子树
- **委托** = 父 zone 通过 NS 记录指向子 zone 的权威服务器，将管理权移交
- 每个 zone 至少 2 个 nameserver（冗余容错）

委托授权是 DNS 最关键的创新——它让"全球命名"在没有中央数据库的情况下成为可能。来源：30_dns_1987 §委托授权

### 3. 服务器类型

| 类型 | 职责 |
|------|------|
| **Root Server** | 13 组（A-M root），知道所有 TLD 服务器地址 |
| **TLD Server** | 管理顶级域（.com 由 Verisign 运营等） |
| **Authoritative Server** | 持有 zone 的最终权威数据（SOA + 记录） |
| **Recursive Resolver** | 替客户端完成完整查询路径，不持有数据（如 8.8.8.8） |

来源：30_dns_1987 §技术方案

### 4. 递归 vs 迭代查询

**迭代查询**：每一步只返回"下一个该问的服务器地址"，客户端/resolver 自己跟链
```
Client → Root      : "www.example.com?"
Root  → Client    : "去问 .com server"
Client → .com      : ...
Client → example.com : 最终 IP
```

**递归查询**：客户端只发一次，由 resolver 自己完成全链
```
Client → Recursive Resolver : "www.example.com?"
Recursive 自己跑完所有迭代步骤
Recursive → Client : 93.184.216.34
```

**RFC 1034 的工程选择**：**权威服务器禁用递归**（性能不应被消耗在递归上），**递归服务器启用递归**（复用缓存命中率）。**根服务器只做迭代**——这是为了让根服务器尽可能轻量、避免被海量递归请求拖垮，全球只有 13 组根服务器要承载所有 DNS 解析的入口。来源：30_dns_1987 §查询类型

### 5. 缓存与 TTL
- 每条 RR 自带 TTL，告诉 resolver 缓存多久
- 典型 TTL：知名网站 300~3600 秒，权威记录 ~86400 秒
- **TTL 驱动的最终一致性**：IP 更新后，旧值最多被缓存 TTL 秒
- **Negative Caching（RFC 2308, 1998 补充）**：NXDOMAIN 答案也可缓存

来源：30_dns_1987 §缓存

### 6. 资源记录（RR）

| 类型 | 用途 |
|------|------|
| A / AAAA | IPv4 / IPv6 地址 |
| CNAME | 别名 |
| MX | 邮件交换 |
| NS | 权威 nameserver |
| SOA | zone 管理信息（序列号 / 刷新间隔） |
| TXT | SPF / 验证等 |

来源：30_dns_1987 §资源记录

## 与一致性谱系的关系
DNS 是分布式系统中**最终一致性**最成功的工程案例之一——为了高读取性能，明确接受 TTL 时间窗内的数据不一致。这是与 Spanner 类强一致系统的根本对比。来源：30_dns_1987 §权衡 / [cap_theorem](./cap_theorem.md)

## 演化脉络
- **1987**：RFC 1034/1035 正式发布
- **1995**：RFC 1995（IXFR 增量传输）
- **1998**：RFC 2308（Negative Caching）
- **2005**：DNSSEC（加密签名抵御 DNS 欺骗）
- **2018**：DoH（DNS over HTTPS）/ DoT（DNS over TLS）

## 在本项目的相关报告
- [30_dns_1987](../../reports/paper_analyses/30_dns_1987.md)
- [19_tcpip_1974](../../reports/paper_analyses/19_tcpip_1974.md)

## 跨域连接
- [tcp_ip](./tcp_ip.md)：DNS 是建立在 TCP/IP 之上的应用层协议
- [cap_theorem](./cap_theorem.md)：DNS 选择 AP（最终一致 + 高可用）
- [consistent_hashing](./consistent_hashing.md)：与 DNS 的层级命名形成对比——DHT 是平面命名空间

## 被引用于
- [tcp_ip](./tcp_ip.md)
- [overview.md](../overview.md)

## 开放问题
- DNSSEC 部署率低的根本原因（密钥管理 + 旧 resolver 兼容）
- DoH / DoT 对 DNS 性能与隐私的真实影响
