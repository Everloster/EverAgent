---
id: entity-muse_agent
title: "Meta Muse（个人 AI Agent 产品）"
type: entity/product
domain: [ai-learning]
created: 2026-09-28
updated: 2026-09-28
sources: [2026-09-22_meta-muse_product-research]
---

# Meta Muse

## 身份
Meta 2026-09-08 发布的个人 AI Agent（非聊天机器人）：目标制工作流、关 App 后继续干活、代发邮件/订票/购物/砍账单/打电话。入口 muse.ai + App + WhatsApp；免费为主，Power $20 / Maximum $100 月。底层模型 Muse Spark 1.3（权重不公开）。来源：2026-09-22_meta-muse_product-research §1

## 架构与争议（⚠️ APK 逆向部分为孤证）
- 官方口径：Secure VM（每用户专属云端虚拟机）+ Sentinel 哨兵 Agent（出网动作二次审批）+ 凭据盲区
- 逆向孤证（微信公众号，未获独立验证）：包名 `com.facebook.aura`，手机端是"能力执行器 Node"——云端经 Noise 加密长连接**主动下发命令**，约 60 项权限（短信/通话/后台定位/Health Connect 全量/通知监听与代点击）；云端调用手机能力走**标准 MCP 协议**
- HITL 闸门：`allow/ask/deny` × READ/WRITE 权限矩阵，审批状态云端同步

## 关键事实时间线
- 2026-09-08 发布，次日股价 +6.5%
- 2026-09-17 outbound calls 上线（代打美国商家电话）；~09-23 404 Media/Reuters 曝光真人承包商接部分电话且用户不知情；~09-25 Meta 回滚该测试
- 截至 09-28：总下载约 340 万 [待验证]，曾登顶美国 iOS 免费榜 #1
- 模型独立评测：BenchLM Reasoning #5/19（79.1）但整体不给公开排名；ApprenticeBench 19%（端到端真实岗位任务）vs Claude Fable 5.1 72%

## 对位
OpenClaw（自托管开源龙虾）：Muse = 全托管高权限，OpenClaw = 自部署权限可控；"普通人的 OpenClaw，用权限广度换安全感"。

## 在本项目的相关报告
- [Meta Muse 深度产品研究报告 v2](../reports/2026-09-22_meta-muse_product-research.md)（v1 2026-09-22，v2 2026-09-28 补 APK 逆向+独立评测+事件线）

## 关联
- [[meta_ai]]（母公司 AI 体系）
- 未解问题：[[open-questions]] 2026-09-28 Meta Muse 节（孤证复核 / 评测鸿沟 / 真人接线员监管 / 欧盟版）
