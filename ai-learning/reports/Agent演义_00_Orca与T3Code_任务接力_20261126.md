---
title: "《Agent 演义》总览｜高频开发者的 Orca 与 T3 Code 产品指南"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-26"
semantic_tags: ["agent_products", "orca", "t3code", "professional_development"]
source_scope: "Orca官方文档与本机CLI 1.4.277；T3固定源码2b0f633d随附指南与CLI 0.1.8；演示范围单列"
---

# 《Agent 演义》总览｜高频开发者的 Orca 与 T3 Code 产品指南

## 概述

《Agent 演义》研究 Orca 与 T3 Code 怎样帮助高频开发者组织 Agent 工作：从项目和任务开始，经过输入、并行、反馈、审查与交付，再延伸到远程和长期使用。源码用来回答操作背后的具体疑问，产品、功能和专业用户的判断构成主线。

Orca 将项目、worktree、聊天、原生终端、浏览器与多 Agent 编排放在一套开发现场里；T3 将 environment、project、thread 与受控执行者组织成可继续、可切换、可回看的工作主线。两者能力有交集，选择应放回自己的任务习惯。[^orca][^t3]

**提炼句：** 好用的 Agent 工作台，应该让你随时知道工作在哪、谁负责、下一步怎样验收。

## 取景框 f(x)

**x｜问题：** 已经每天使用 Claude Code 和 Codex，Orca 与 T3 能怎样改善真实开发工作？

**f｜取景框：** 沿一项任务的开始、推进、介入、交付与恢复看产品，观察要求、执行者和文件现场之间的关系。

**f(x)｜判断变化：** 比较产品时，先看常见操作是否省去协调成本，再看机制和扩展能力；功能数量和聊天窗口的连续性不能单独决定是否适合你。

## 从你现在的工作开始读

想先理解 Orca，顺读 01–08；想先理解 T3，顺读 09–16。已经熟悉两套产品，就从 17 的一项功能、18 的并行工作或 19 的长期使用开始，按疑问回到产品篇。

原来“session 切 harness，API 怎么换、缓存与推理怎么续”的问题仍保留。先读 12 理解使用选择，再读附录 A／B 区分协议与状态；遇到消息投递或恢复问题，再看附录 C。机制解释集中之后，正文可以沿用户动作连贯阅读。

## Orca：从一个项目到多个开发现场

| 篇章 | 阅读入口 |
|---|---|
| 01 | [Orca 的产品全貌与工作方式](knowledge_reports/Agent演义_01_Orca_产品全貌与工作方式_20261126.md) |
| 02 | [Orca：管好项目、worktree 与并行现场](knowledge_reports/Agent演义_02_Orca_项目与并行工作区_20261126.md) |
| 03 | [Orca：在聊天与终端之间工作](knowledge_reports/Agent演义_03_Orca_聊天终端与会话_20261126.md) |
| 04 | [Orca：一个人怎样管理多个 Agent](knowledge_reports/Agent演义_04_Orca_多Agent分工与监督_20261126.md) |
| 05 | [Orca：浏览器、Design Mode 与界面反馈](knowledge_reports/Agent演义_05_Orca_浏览器与界面反馈_20261126.md) |
| 06 | [Orca：从改动审查到提交与 PR](knowledge_reports/Agent演义_06_Orca_审查提交与PR_20261126.md) |
| 07 | [Orca：远程机器与手机上的工作](knowledge_reports/Agent演义_07_Orca_远程与移动工作_20261126.md) |
| 08 | [Orca：Bots、自动化与个人配置](knowledge_reports/Agent演义_08_Orca_Bots自动化与配置_20261126.md) |

这一组先说明如何开工与组织现场，再讲聊天、终端和多 Agent，接着讲浏览器反馈、审查交付，最后延伸到远程、Bots 与配置。官方配图用于定位功能；具体按钮与能力以所用发行版为准。

## T3：从一个 environment 到一条工作主线

| 篇章 | 阅读入口 |
|---|---|
| 09 | [T3：产品全貌与接入方式](knowledge_reports/Agent演义_09_T3_产品全貌与接入_20261126.md) |
| 10 | [T3：项目、worktree 与项目动作](knowledge_reports/Agent演义_10_T3_项目工作区与动作_20261126.md) |
| 11 | [T3：把线程用成日常工作单元](knowledge_reports/Agent演义_11_T3_线程与日常工作_20261126.md) |
| 12 | [T3：什么时候换模型，什么时候换 Agent](knowledge_reports/Agent演义_12_T3_换模型与换Agent_20261126.md) |
| 13 | [T3：委派、子 Agent 与并行任务](knowledge_reports/Agent演义_13_T3_子Agent与任务委派_20261126.md) |
| 14 | [T3：从实现到反馈与交付](knowledge_reports/Agent演义_14_T3_实现反馈与交付_20261126.md) |
| 15 | [T3：多环境、远程与移动工作](knowledge_reports/Agent演义_15_T3_多环境与移动工作_20261126.md) |
| 16 | [T3：用量、权限、自动化与日常维护](knowledge_reports/Agent演义_16_T3_用量权限与自动化_20261126.md) |

这一组先说明 host 与 client、项目和 worktree，再讲 thread、换模型与换执行者，随后讲委派、反馈与交付，最后讲多环境、用量和自动化。

## 放回工作流比较

- [17｜完成一项功能：两套产品怎样配合开发](knowledge_reports/Agent演义_17_工作流_完成一项功能_20261126.md)
- [18｜同时推进多项工作：分工、监督与整合](knowledge_reports/Agent演义_18_工作流_同时推进多项工作_20261126.md)
- [19｜建立自己的长期 Agent 工作台](knowledge_reports/Agent演义_19_工作流_建立长期工作台_20261126.md)

比较篇用同一项 Card Gallery 任务讨论操作路线，解释在哪些地方需要做选择。不按未经测量的模型质量、缓存命中或开发速度排名。

## 技术附录：需要时展开

- [技术附录 A：对象、协议与能力边界](knowledge_reports/Agent演义_附录A_对象协议与能力边界_20261126.md)
- [技术附录 B：上下文、推理与缓存](knowledge_reports/Agent演义_附录B_上下文推理与缓存_20261126.md)
- [技术附录 C：协作、投递与恢复](knowledge_reports/Agent演义_附录C_协作投递与恢复_20261126.md)

三篇附录承接旧机制稿中的身份、适配、切换、历史预算、原生推理、缓存与恢复分析，保留固定源码和离线探针入口。主篇与附录共 23 篇，其中主篇 20 篇。

## 可以自己打开的演示项目

Card Gallery 是作者自拟的前端、API 与测试项目。搜索标题和描述，支持中文与大小写匹配，标签与搜索取交集，分页与异步响应遵守明确合同。项目不需要模型或第三方 Python 包。

从仓库根目录运行：

```sh
cd ai-learning/experiments/agent-harness-series/web-project
python3 -m unittest discover -s tests -v
python3 api/server.py --port 4188
```

然后打开 `http://127.0.0.1:4188`。在 Orca 或 T3 练习时，可将该目录复制到独立临时目录、初始化 Git，再作为演示项目打开；[README](../experiments/agent-harness-series/web-project/README.md)提供合同与可复走任务。

它的用途是让“反馈具体”“上下文保住了”“功能完成”落到同一份可检查的要求。代码由本次作者实现，没有让两套产品的模型实际完成任务。

## 来源版本与实际检查范围

| 材料或操作 | 本次依据 |
|---|---|
| Orca 产品与机制 | 官方文档、公开源码提交 `60eb66f2`；本机 CLI／应用 1.4.277 |
| T3 产品与机制 | 提交 `2b0f633d` 随附用户指南和源码；本机 CLI 0.1.8 |
| 产品图片 | 上述公开仓的官方示意或营销截图，逐图标明来源 |
| 本地页面 | 自拟 Card Gallery；实际核对搜索、标签、空状态与分页归一 |
| T3 界面 | 独立数据环境的启动、配对、项目加入与选定控件检查；未执行模型任务 |
| 代码与阅读 | 九项演示 API／页面服务测试；23 篇阅读器内容与配图检查 |
| 机制探针 | 原有 32 项选定内核／队列检查及教学协议观察，结果与范围保留 |

T3 固定源码和随附指南比本机 CLI 更新，文档功能不能一律视为 0.1.8 已实测。Orca 本机版也不等同于源码快照。实际操作部分与文档说明分别标注，不由官方示意图推断某次运行已经发生。

本次没有测真实模型费用、命中率或推理收益，没有运行完整生产 adapter／orchestrator 故障重放，也没有部署远程、外部应用、自动化或发布 PR。相关章节回答入口、选择条件和机制边界；实验细节集中在[实验说明](../experiments/agent-harness-series/README.md)。

[^orca]: [Orca 公开仓与产品功能](https://github.com/stablyai/orca/blob/60eb66f230d445107a32e55eae695d7090087acf/README.md)、[官方文档](https://orca.dev/docs/model/worktrees)。
[^t3]: [T3 固定版用户指南](https://github.com/pingdotgg/t3code/blob/2b0f633db3ba23e692750be2f578ecb089d6a852/docs/user/README.md)。
