---
title: "OpenAI API Docs 中文导读"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-11-10"
semantic_tags: ["openai", "api_docs", "chinese_guide", "responses_api", "agents", "tools", "audio", "production"]
---

# OpenAI API Docs 中文导读

这份导读按主题整理 OpenAI API 文档，用中文解释各项能力的用途、工作方式和主要限制。每个条目都有原文链接，读到需要实现的部分，可以继续查完整示例和参数。

内容依据 **2026 年 11 月 10 日**的官方文档索引，共 **244 页，分为 8 卷**。中文采用摘译和概括，保留接口名称、字段和必要的条件，方便对照英文阅读。

初次接触 API，可以从[入门与核心概念](assets/openai_api_docs_20261110/01-overview.md)开始。已经在写应用，可以直接看[工具](assets/openai_api_docs_20261110/04-tools.md)、[Agents SDK](assets/openai_api_docs_20261110/03b-agents-sdk-chatkit.md)或[语音](assets/openai_api_docs_20261110/05-audio-voice.md)。需要处理计费、权限和数据问题时，查[生产部署](assets/openai_api_docs_20261110/06-production.md)。

## 分卷目录

| 分卷 | 内容 | 对应页面 |
|---|---|---:|
| [01 · 入门与核心概念](assets/openai_api_docs_20261110/01-overview.md) | 第一次请求、会话状态、流式输出、WebSocket、steering、文件输入、上下文压缩、SDK 与 CLI | 17 |
| [02 · 模型与生成能力](assets/openai_api_docs_20261110/02-models.md) | 模型选择、价格、文本、推理、提示、结构化输出、图像、embedding 与版本迁移 | 37 |
| [03a · 托管 Agent](assets/openai_api_docs_20261110/03a-agents-api.md) | Agents API、session、事件、环境、审批、定时任务、工具、产物与恢复 | 37 |
| [03b · SDK 与聊天界面](assets/openai_api_docs_20261110/03b-agents-sdk-chatkit.md) | Agents SDK 的运行循环、handoff、沙箱、校验、状态，以及 ChatKit 组件和交互 | 17 |
| [04 · 工具](assets/openai_api_docs_20261110/04-tools.md) | 函数调用、检索、MCP、Skills、工具发现、程序化与异步调用、Shell、计算机操作 | 20 |
| [05 · 音频与语音](assets/openai_api_docs_20261110/05-audio-voice.md) | GPT-Live、Realtime、连接、语音提示、转写、翻译、自定义声音与费用 | 27 |
| [06 · 生产部署](assets/openai_api_docs_20261110/06-production.md) | 性能、缓存、评估、安全、数据、权限、云平台、Terraform、身份联合与限额 | 58 |
| [07 · 历史、迁移与资源](assets/openai_api_docs_20261110/07-legacy-resources.md) | 更新与弃用、旧接口、Agent Builder、Evals、微调、GPT Actions 与官方教程 | 31 |

同名页面按所属主题区分，例如文本应用与语音应用各有 Cost optimization。分卷编号只用于本导读导航。

## 常用官方入口

- [API Docs](https://developers.openai.com/api/docs)：按主题浏览开发指南。
- [Models](https://developers.openai.com/api/docs/models)：查看模型、输入输出形式和支持的功能。
- [Pricing](https://developers.openai.com/api/docs/pricing)：查看模型、工具及各类处理模式的价格。
- [Changelog](https://developers.openai.com/api/docs/changelog)：查功能和参数的发布时间。
- [Deprecations](https://developers.openai.com/api/docs/deprecations)：查弃用通知、停止日期及迁移路线。

## 查具体字段：API Reference

指南解释用法，API Reference 列出端点、请求参数、响应对象和事件。写代码时，可以从下面的入口查具体定义；这套字段参考独立于本导读的 244 页范围。

| 要查的接口 | 原文 |
|---|---|
| 认证与通用行为 | [API overview](https://developers.openai.com/api/reference/overview) |
| Responses | [Responses overview](https://developers.openai.com/api/reference/responses/overview) |
| Chat Completions | [Chat](https://developers.openai.com/api/reference/resources/chat) |
| Realtime | [Realtime](https://developers.openai.com/api/reference/resources/realtime) |
| GPT-Live | [Live](https://developers.openai.com/api/reference/resources/live/primary-websocket) |
| 文件与上传 | [Files](https://developers.openai.com/api/reference/resources/files) · [Uploads](https://developers.openai.com/api/reference/resources/uploads) |
| 图像与音频 | [Images](https://developers.openai.com/api/reference/resources/images) · [Audio](https://developers.openai.com/api/reference/resources/audio) |
| 批处理 | [Batches](https://developers.openai.com/api/reference/resources/batches) |
| 组织与项目管理 | [Administration](https://developers.openai.com/api/reference/administration/overview) |

## 版本与译写说明

本次重写逐条对照摘要所涉及的英文说明段落，尽量直接解释功能和用法。这里是中文导读，未逐句翻译整页文档；完整代码、参数表及媒体示例通过原文查看，本次没有执行文档程序或调用付费 API。

官方文档保留了不同年代的模型和迁移指南。旧页面的推荐型号、参数和“最新”应放回当时理解；准备迁移时，结合当前模型卡和弃用时间表确认。中文条目也保留这些版本差别。

### 来源与校对记录

页面范围取自官方 [llms.txt](https://developers.openai.com/api/docs/llms.txt)。本次使用的 [llms-full.txt](https://developers.openai.com/api/docs/llms-full.txt) 包含其中 240 页，另行取得 Changelog、Models、All models 和 Compare models 四页。重写时核对了源文件摘要，官网索引与保存的基线一致。

[逐页清单](assets/openai_api_docs_20261110/coverage.md)保存原文与中文条目的对应关系；[来源记录](assets/openai_api_docs_20261110/coverage.json)保存获取方式、SHA-256 和本次修订范围。原始英文快照只保存在临时阅读目录中。

本次校对覆盖中文条目使用的说明内容、术语、条件及链接。API Reference、外链仓库和模型卡没有全部递归阅读，音视频与截图也未逐项评测。文件和跳转检查用于发现遗漏与坏链接，不能证明文档中的能力已在实际应用中复现。
