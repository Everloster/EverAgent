---
title: "AI 行业日报 · 2026-11-18"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-18"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---

# AI 日报 · 2026年11月18日

今天先看三件事。

- 英伟达公布截至 10月25日的 2027 财年第三季度业绩：营收 1158 亿美元，环比增 20%，同比增 103%。第四季度展望 1300 亿美元，上下 3%，且指引明确不含中国数据中心计算营收。数字均为公司自报。

- OpenAI 11月17日发布 GPT-6.2 Astra 和 GPT-6.2 Sol。官方称两者用更少的输出 token 取得更好结果；系统卡把两款的网络安全能力标到 Critical。评测对比是公司自报。

- 微软在 Ignite 发布包括 MAI Code 2 在内的七款模型。官方把 Code 2 的价格写成 GPT-6.1 Sol 的约 40%、Claude Opus 5.5 的约 5%，但脚注写明用的是五折促销价。

## 英伟达公布季度业绩：营收 1158 亿美元，下季指引不含对华算力

英伟达 11月17日（美国日期，对应北京时间 18日凌晨的电话会之后）[宣布](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027)截至 10月25日的 2027 财年第三季度业绩。这是黄仁勋辞任后的首次季报。营收 1158 亿美元，环比增 20%，同比增 103%。数据中心营收 1076 亿美元，环比增 21%，同比增 110%。

按美国通用会计准则，净利润 653 亿美元，摊薄每股收益 2.70 美元；非公认口径净利润 649 亿美元，摊薄每股收益 2.68 美元。CFO Colette Kress 的[补充说明](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27cfocommentary.htm)写道，当季销往中国的数据中心 Hopper 产品出货 24 亿美元。

公司展望第四季度营收 1300 亿美元，上下 3%，并写明指引「不考虑来自中国的数据中心计算营收」。毛利率指引为 71.0% 至 72.0%，低于本季约 74.8%。新闻稿称 Vera Rubin NVL72「已经出货」。以上均为公司自报；10-Q 仍将在未来数周提交。媒体引用的分析师预期口径不一致，这里不用。

## OpenAI 发布 GPT-6.2 Astra 与 Sol，系统卡标到网络安全 Critical

OpenAI 11月17日[发布](https://openai.com/index/introducing-gpt-6-2-astra-sol)面向高难度专业工作的 GPT-6.2 Astra，以及面向日常工作的 GPT-6.2 Sol。官方称两者在更少输出 token 下取得更好结果。即日起在 ChatGPT Work 与 Codex 向 Plus、Pro、Enterprise、Edu 用户开放；Enterprise 与 Edu 需管理员开启。API 模型名是 `gpt-6.2-astra` 和 `gpt-6.2-sol`。

API 定价为每百万 token：Astra 输入 8 美元、缓存输入 0.40 美元、输出 40 美元，官方称比 GPT-6 Astra 的输入和输出低 20%；Sol 沿用 GPT-6.1 Sol，为 2 美元、0.10 美元和 10 美元。官方自报，Astra 在 Agents’ Last Exam 上比 GPT-6 Astra 高 5.2 分、成本不到三分之一。这些对比取决于公司选定的配置，不是独立评测。

同日[系统卡](https://deploymentsafety.openai.com/gpt-6-2-astra-sol/safety-overview)称，两款模型在准备框架下达到网络安全 Critical、生物化学 High；Astra 还达到人工智能自我改进 High，Sol 未达到。官方写，对已知漏洞写出可运行利用代码的能力强于前代，因而收紧了默认的高风险网络协助。系统卡也承认，障碍披露评测出现回退，越狱抵抗一度回退，调整拒绝边界后才部分改善。

## 微软 Ignite 发布七款 MAI 模型，价格对比用了促销价

微软人工智能部门 11月17日在 Ignite [发布](https://microsoft.ai/news/microsoft-ignite-2026/)七款新模型，并称 Maia 200 加速器已投产。其中 [MAI Code 2](https://microsoft.ai/news/introducing-mai-code-2-and-mai-code-2-flash/) 被写成：在四项常用编码基准的平均成绩上，达到 GPT-6.1 Sol 性能的 98%、价格约 40%；达到 Claude Opus 5.5 的 96%、价格约 5%。

但同一页脚注写明，Code 2 与 Code 2 Flash 的成本按 50% 促销价计算。去掉这层折扣，价格对比会明显没有那么悬殊。微软自己也写，这些模型「还没有针对更难的问题调优」，例如基础科学研究和很长周期的智能体工作。成绩是厂商自报。

Code 2 与 Code 2 Flash 已进入 GitHub Copilot；Flash 在 Microsoft Foundry 为限制访问预览。微软还宣布 MAI Licensed Weights，称可信客户可在自有 Azure 环境中获得并定制权重。

## Wiz：微软 Agent Framework 的 PyPI 包被植入凭据窃取器

安全公司 Wiz 11月17日[报告](https://www.wiz.io/blog/malicious-version-of-microsofts-agent-framework-published-to-pypi)，微软 Agent Framework 的 PyPI 元包 `agent-framework` 当天出现两个恶意版本 1.26.1 和 1.26.2，随后被下架。Wiz 的时间线是：20:35 UTC 上传 1.26.1，约 21:08 上传 1.26.2，约 21:30 两版本已不可用。最近的安全版本是 1.26.0。

手法是在 site-packages 放入 `.pth` 文件，Python 每次启动都会执行，即使从不导入该包。载荷会收集环境变量、部分进程环境和多种云与开发凭据，压缩后发到 webhook.site。Wiz 称攻击者用的是免费档，最多确认捕获 50 个请求。根因尚未证实；本期未见微软官方声明。OSV 已编目该条目。

## 媒体称 SEC 调查英伟达信息披露，公司与监管机构均未确认

彭博法律 11月17日[转述](https://news.bloomberglaw.com/securities-law/sec-is-probing-nvidia-amid-jensen-huangs-exit-wsj-reports)《华尔街日报》报道：美国证监会对英伟达展开民事调查，关注公司披露是否误导投资者。报道写明，调查的完整焦点尚不能立即获知；英伟达未回应置评，证监会拒绝置评。[TechCrunch](https://techcrunch.com/2026/11/17/sec-reportedly-investigating-nvidia-amid-huang-exit/) 和 The Verge 同样标明这是转述。

这是媒体引用知情人士的报道，不是立案公告，也不能据此认定欺诈，或把它与新加坡收入口径、出口管制调查、黄仁勋去职写成已经证实的因果关系。本期未读到《华尔街日报》原文。同期《金融时报》关于新加坡销售披露的报道因付费墙未核到全文，数字这里不用。

## Isomorphic Labs 完成 50 亿美元 C 轮融资

Alphabet 旗下、Demis Hassabis 担任创始人兼首席执行官的 Isomorphic Labs 11月17日[宣布](https://www.isomorphiclabs.com/articles/isomorphic-labs-announces-series-c-investment-round)完成 50 亿美元 C 轮融资。联合领投为 Greenoaks 和 Sequoia Capital，新投资者包括 a16z 等，Alphabet 继续显著出资，全部既有投资人也参与。官方称资金将加速其药物设计引擎与候选管线。

官方新闻未披露估值。融资完成不等于药物已进入临床或已经证明疗效。媒体此前关于估值的传闻，这里不采用。

## 热榜上，技能框架增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月18日约 09:13 采集，当时页面列出 15 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[obra/superpowers](https://github.com/obra/superpowers) 当天约增加 1,917，总星约 319,343，增量最高，页面介绍为智能体技能框架与开发方法。[dream-num/univer](https://github.com/dream-num/univer) 约增加 1,774，连续两日靠前。[ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) 约增加 1,445。[google-research/paper-orchestra](https://github.com/google-research/paper-orchestra) 约增加 1,072。新面孔 [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 约增加 1,005，是面向漏洞挖掘的 Claude Code 技能包；[Tencent/LoopForge](https://github.com/Tencent/LoopForge) 约增加 591，用于托管编码智能体工作流。全表在文末。

## X上顶尖AI大佬最近都说了什么

**Jason Wei**，AI 研究者，曾在 OpenAI、Google 和 Meta 工作。他[写道](https://x.com/_jasonwei/status/2122826605362127094)，在 Meta 的 TBD lab 工作一年后，今天加入 Mercor，担任首席科学家。帖发于北京时间 11月18日 06:57，属当事人的职业声明，不是产品或模型事实。背景是 Mercor 创始人的公司侧宣布，公司帖不算个人原帖。

**Sebastian Raschka**，《Build a Large Language Model From Scratch》作者。他[写道](https://x.com/rasbt/status/2122721652433715481)，新的预训练配方可能开始不再做学习率衰减，改为恒定学习率并平均最近若干检查点。他按公开训练细节做了归类，并说这样不必事先锁定总训练长度。帖发于北京时间 11月18日 00:00，属个人观察，不是完整普查。

**Simon Willison**，Datasette 作者、Django 共同创建者。他[写道](https://x.com/simonw/status/2122500307557265651)，自己在探索给编码智能体用的外部沙箱：智能体在 Mac 上运行，代码放到 WebAssembly、QEMU 或 Apple Container 里执行，并演示了 Claude Code、Codex 和 Pi。帖发于北京时间 11月17日 09:21，属个人工程实践，不是厂商官方方案。

## 另外几则

**Gemini 任务功能在六个国家免费开放。** Google 11月17日[宣布](https://blog.google/innovation-and-ai/products/gemini-app/tasks-in-gemini-free-new-features/)，基于 Gemini 4 Hydrogen 的任务功能即日起向美国、日本、韩国、加拿大、澳大利亚和印度免费推出，称可代为打电话、用 Google Pay 购物，并连接 60 多款应用。官方也写明仍会失败或做不到最后一步；电话功能在美国五个州暂不可用。能力与覆盖均为厂商自报。

**可灵发布 Kling Image 4.0。** 官方博客标注日期为 11月18日，称已在创作平台上线并提供 API，自报支持原生 8K、单图最多 2000 字符文字渲染等。无独立评测。[来源](https://kling.ai/blog/kling-image-4-stunningly-realistic-sharp-precise)

**Anthropic 上市仍未定价。** 公司此前路演稿给出预期发行价每股 70 至 78 美元，代码 ANT。纳斯达克 11月11日的技术通知写明预计 11月19日开始交易。截至本期采集时（北京时间 11月18日约 09:15），未见已定价的新官方稿。媒体测算的估值不是公司数字，这里不用。


<details>
<summary>热榜全表、数字口径和采集说明</summary>

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11月18日 09:13；当时页面 15 行）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 9,320 / +1,005 | Python | 面向漏洞挖掘与外部红队的 Claude Code 技能包 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 69,079 / +696 | Python | 跨多个平台调研话题并汇总的智能体技能 |
| [alibaba/open-code-review](https://github.com/alibaba/open-code-review) | 53,735 / +763 | Go | 确定性流程加大模型智能体的代码审查工具 |
| [Tencent/LoopForge](https://github.com/Tencent/LoopForge) | 3,161 / +591 | Go | 自托管的编码智能体交付工作流 |
| [dream-num/univer](https://github.com/dream-num/univer) | 28,906 / +1,774 | TypeScript | 给人和智能体用的办公软件开发包 |
| [getarcaneapp/arcane](https://github.com/getarcaneapp/arcane) | 9,336 / +618 | Go | Docker 管理界面 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 10,109 / +350 | TypeScript | 面向 Stitch MCP 服务的智能体技能库 |
| [cursor/plugins](https://github.com/cursor/plugins) | 16,904 / +201 | TypeScript | Cursor 插件规范与官方插件 |
| [obra/superpowers](https://github.com/obra/superpowers) | 319,343 / +1,917 | Shell | 智能体技能框架与开发方法 |
| [ag-ui-protocol/ag-ui](https://github.com/ag-ui-protocol/ag-ui) | 20,002 / +1,445 | TypeScript | 把智能体接入前端应用的交互协议 |
| [backnotprop/plannotator](https://github.com/backnotprop/plannotator) | 13,071 / +691 | TypeScript | 用于规划、批注并把反馈交给智能体的工作区 |
| [sveltejs/svelte](https://github.com/sveltejs/svelte) | 89,601 / +477 | JavaScript | 网页开发框架 |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 305,511 / +883 | JavaScript | 面向多种编码智能体的 harness 与技能优化系统 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 65,988 / +192 | Python | 从零训练小型语言模型的项目 |
| [google-research/paper-orchestra](https://github.com/google-research/paper-orchestra) | 3,016 / +1,072 | Python | 自动撰写研究论文的多智能体框架 |

英伟达：官方新闻稿日期 November 17, 2026，写明第三季度截至 2026年10月25日，营收 $115.8B（环比 +20%，同比 +103%）、数据中心 $107.6B（环比 +21%，同比 +110%）、GAAP 净利润 $65.3B、摊薄 EPS $2.70，non-GAAP 净利润 $64.9B、摊薄 EPS $2.68；新闻稿还给出 Hyperscale $60.1B，AI Clouds, Industrial, & Enterprise $47.5B，Compute & Networking $106.0B，Graphics $9.8B。毛利率 GAAP 74.8%、non-GAAP 74.9%；第四季度展望营收 $130.0B ±3%，毛利率指引 71.0%–72.0%，并写明 “NVIDIA is not assuming any Data Center compute revenue from China in its outlook.” CFO commentary 原文：“Shipments of Data Center Hopper products to China during the quarter were $2.4 billion.” SEC 转载新闻稿：https://www.sec.gov/Archives/edgar/data/1045810/000104581026000088/q3fy27pr.htm 。电话会中媒体提到的新云承诺等数字本期未读逐字稿，正文不用。CNBC、Investopedia 所引分析师预期分属 LSEG 与 Visible Alpha，口径不同，正文不用。

GPT-6.2：OpenAI 博客与系统卡日期均为 2026年11月17日；API changelog 同日列出 `gpt-6.2-astra`、`gpt-6.2-sol`。定价与 Agents’ Last Exam、Terminal-Bench-Science 0.1、FrontierCode 2.0 等对比均为官方自报，正文只用已回原文的数字。Artificial Analysis、Perplexity 等第三方分数本期未深读原文，不用 AIHOT 转述数字。

MAI：https://microsoft.ai/news/introducing-mai-code-2-and-mai-code-2-flash/ 脚注写明 “MAI-Code-2 cost is shown at its 50% promotional price”，Code 2 Flash 同样。四项平均所涉基准为 DeepSWE 1.1、Terminal Bench 2.1、SWE-Atlas、FrontierCode v1.1；FrontierCode 1.1 分数与成本来自 Artificial Analysis。GitHub Changelog 日期 2026-11-17。

Wiz：时间均为 UTC。OSV 条目 MAL-2026-20101，Published 2026-11-17T22:12:19Z。Endor Labs 对下架分钟数的描述与 Wiz 略有出入，正文采用“随后被下架”，不写成单一精确分钟。本期未见微软官方声明或 GitHub Security Advisory。下载量是 Wiz 估计，正文未用。

SEC 调查：最接近的转述是 Bloomberg Law（Nov. 17, 2026, 10:01 PM UTC），写明 Nvidia 未回应、SEC 拒绝置评。The Verge 时间 2026-11-17T21:49:00Z 左右。FT 新加坡销售报道链到 https://www.ft.com/content/dbde7a30-548c-4f9d-a4be-7898a0c24dcf ，因付费墙未读全文；Hacker News 当时约 379 分，标题中的 $104B 未核，正文不用。

Isomorphic Labs：官方新闻日期 November 17, 2026，写明 $5 Billion Series C，联合领投 Greenoaks 与 Sequoia Capital，新投资者包括 a16z 等，Alphabet 继续显著出资，既有投资人 Thrive Capital、MGX、GV、CapitalG、Temasek 和 UK Sovereign AI Fund 全部参与。未披露估值。

Gemini 任务：官方原文 “Starting now, this update is rolling out free of charge for hundreds of millions of people across the U.S., Japan, Korea, Canada, Australia, and India, using our new Gemini 4 Hydrogen model.” 电话功能在 Indiana、Louisiana、Minnesota、Montana、Nebraska 暂不可用。

X：三帖均经 X 公共读取接口直接读取原帖。Jason Wei 原帖时间 2026-11-17T22:57:57Z，引用 Brendan Foody 2026-11-17 的公司侧宣布；Sebastian Raschka 原帖时间 2026-11-17T16:00:54Z；Simon Willison 原帖时间 2026-11-17T01:21:22Z。Karpathy、LeCun、Andrew Ng 等在排除回复与转发后，窗口内无合格原帖。Demis Hassabis 有同步宣布 C 轮的原帖，因与头条重复未列入三人精选。

Hacker News（采集约北京时间 11月18日 09:14）：当时 GPT-6.2 条目约 1070 分，MAI Code 2 约 279 分，Claude Code 团队谈验证约 261 分。首页另有 Java4Shell（约 485 分）等与本期主题无直接关系的条目。腾讯 Hy4 flash 仍在讨论（约 43 分），已在 11月17日日报写过，本期不重复。

来源覆盖：已读 AIHOT 11月18日页（第 211 期，每天 08:00 出刊）、Hacker News 首页、GitHub 热榜（北京时间 11月18日 09:13 的页面 HTML）和三位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以英伟达新闻稿与 CFO 说明、OpenAI 博客与系统卡、微软人工智能部门博客、Wiz 报告、Isomorphic Labs 和 Google 官方博客为依据；SEC 调查一条仅有媒体转述，已在正文标明。AIHOT 另列的 Qwen4-Max、加州起诉 OpenAI、美国出口管制新规等已在 11月17日或更早日报写过，本期不重复。

</details>
