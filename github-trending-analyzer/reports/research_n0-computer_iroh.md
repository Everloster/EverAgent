# n0-computer/iroh 深度研究报告

## 项目概述

IP addresses break, dial keys instead. Modular networking stack in Rust.

> 来源：README 与 GitHub 项目元信息自动摘要（**仅作骨架，每章 `[待补充]` 段需人工/agent 补全**）

### README 摘要

less net work for networks
Docs Site
Rust Docs
## What is iroh?
Iroh gives you an API for dialing by public key.
You say “connect to that phone”, iroh will find & maintain the fastest connection for you, regardless of where it is.
### Hole-punching
The fastest route is a direct connection, so if necessary, iroh tries to hole-punch.
Should this fail, it can fall back to an open ecosystem of public relay servers.
To ensure these connections are as fast as possible, we [continuously measure iroh][iroh-perf].
### Built on [QUIC]
Iroh uses [noq] to establish [QUIC] connections between endpoints.
This way you get authenticated encryption, concurrent streams with stream priorities, a datagram transport and avoid head-of-line-blocking out of the box.
## Compose Protocols
Use pre-existing protocols

---

## 基本信息

| 属性 | 数值 |
|------|------|
| 全称 | n0-computer/iroh |
| GitHub URL | https://github.com/n0-computer/iroh |
| GitHub Stars | 10,421 |
| GitHub Forks | 472 |
| 主语言 | Rust |
| 许可证 | Apache-2.0 |
| 项目创建日期 | 2022-03-14 |
| 最近推送日期 | 2026-06-20 |
| 默认分支 | main |
| 开放 Issue/PR 数 | 150 |
| 话题标签 | does-anyone-read-these, holepunching, memes, multipath, p2p, quic, realtime, rust, tags, tagsoftags |

---

## 技术分析

[待补充：从 README / 源码 / 文档提取：
- 核心架构（模块划分、数据流）
- 关键技术栈与依赖
- 性能/扩展性设计
- 与同类项目的差异化设计]

---

## 社区活跃度

| 指标 | 数值 | 数据源 |
|------|------|--------|
| Stars | 10,421 | GitHub API |
| Forks | 472 | GitHub API |
| 开放 Issue/PR | 150 | GitHub API |
| 最近活跃 | 2026-06-21 | GitHub API |

[待补充：贡献者数量、近 30/90 天 commit 频率、PR review 周期、issue 响应时间]

---

## 发展趋势

[待补充：
- 版本演进（最近 5 个 release 主题）
- star 增长曲线（基于历史 trending 数据）
- 应用领域扩展方向
- 维护活跃度趋势]

---

## 竞品对比

[待补充：列出 2-5 个直接竞品并对比：
- 功能覆盖
- 性能基准
- 生态完整度
- 维护活跃度]

---

## 总结评价

### 优势

[待补充：列出 3-5 个该项目显著优于同类之处]

### 劣势

[待补充：列出 3-5 个该项目显著的局限或风险]

### 学习/使用建议

[待补充：面向不同读者（学习者 / 工程团队 / 投资人）的优先级建议]

---

*报告生成时间: 2026-06-21*
*研究方法: github-api 元信息 + README 自动提取（**骨架**，每章 [待补充] 待人工/agent 补全）*
