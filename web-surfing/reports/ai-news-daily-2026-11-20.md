---
title: "AI 行业日报 · 2026-11-20"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-20"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---

# AI 日报 · 2026年11月20日

今天先看三件事。

- Anthropic 已在美国时间 11月19日以代码 ANT 在纳斯达克开始交易。开盘价 111.50 美元，收盘 97.17 美元，较 83 美元发行价上涨约 17%。这是对上期已写定价、但采集时尚未开盘的后续。

- Google 11月19日为 Mac 版 Gemini 应用上线 computer use，可在隔离后台窗口里跨本地文件、桌面应用和网页完成多步任务。目前仅向美国英语、符合条件的付费用户推出。

- Google 同日在 Gemini API 的 Interactions API 中以预览形式推出 Tool Retrieval，按需加载工具参数 schema，而不是每次请求都发送完整工具库。官方称这是为了减少输入 token，并在工具变多时保持选择准确。

## Anthropic 已在纳斯达克开盘，收盘较发行价上涨约 17%

这是对[上期](./ai-news-daily-2026-11-19.md)的后续。上期已记录：Anthropic 11月18日宣布 A 类普通股定价每股 83.00 美元，预计 11月19日（美国日期）以代码 ANT 开始交易；当时北京时间上午采集时，美国当日开盘尚未开始。

[纳斯达克新闻稿](https://www.nasdaq.com/newsroom/anthropic-marks-ipo-at-nasdaq)确认，Anthropic, PBC 已于周四在纳斯达克开始交易，开盘价为 111.50 美元。Dario Amodei 与 Daniela Amodei 在 Nasdaq MarketSite 参加了开市铃仪式。

据[雅虎财经 ANT 行情页](https://finance.yahoo.com/quote/ANT/)在本期北京时间 11月20日约 09:23 的页面：前收显示为 83.00 美元，开盘 111.50 美元，收盘 97.17 美元，涨幅 17.07%；当日区间 92.72 至 115.10 美元，成交量 851,818,130 股。[CNBC 的直播页](https://www.cnbc.com/2026/11/19/anthropic-ipo-ant-live-updates.html)同样写开盘 111.50 美元、收盘 97.17 美元，并称涨约 17%。这两处的开盘价与收盘价一致。

市值算法并不统一。同一行情页给出的盘中市值是 1.272 万亿美元；CNBC 则写收盘时充分稀释市值约 1.8 万亿美元。公司 11月18日的定价公告没有公布已发行总股本，这里不把其中某一个数字当成官方市值。

关于发行规模，上期已按官方股数与定价粗算：公司出售部分约 793.8 亿美元，整次发行含出售股东股份约 813.4 亿美元，这是未扣除承销折扣的粗算。媒体常把约 813 亿美元写成募资额，其中出售股东的部分收益不归公司。定价公告仍写预计 11月20日交割，须满足惯例交割条件。本期采集时对应美国东部 11月19日晚间，不能写成已经交割。

## Mac 版 Gemini 应用上线 computer use

Google 11月19日[宣布](https://blog.google/innovation-and-ai/products/gemini-app/computer-use-mac/)，Mac 版 Gemini 应用新增 computer use。官方称，用户用自然语言描述任务后，Gemini 可在隔离的后台窗口中点击、输入并操作菜单，覆盖本地文件、桌面应用和网页；主屏幕和光标仍留给用户。官方还写，用户可选择允许访问的应用、观看实时预览、随时暂停，并对关键操作先审批再执行。这些是公司对产品机制的说明，不是外部评测。

官方举例包括批量调色、从本地 PDF 提取信息填写运费表、从仪表盘整理幻灯片，以及为转卖商品做批量上架。该功能正在美国以英语推出，需苹果芯片 Mac、macOS Sequoia 15.0 或更高版本，面向年满 18 岁的个人 Google 账号，以及 Google AI Plus、Pro 和 Ultra 用户。官方未说明向其他地区或系统开放的时间。[Macworld](https://www.macworld.com/article/3291400/gemini-can-now-tap-into-your-mac-for-app-automation.html) 称撰稿时下载到的仍是旧版，尚未用上该功能，可见推出是逐步进行的。

## Gemini API 预览 Tool Retrieval，按需加载工具定义

Google 11月19日[宣布](https://blog.google/innovation-and-ai/technology/developers-tools/gemini-api-tool-retrieval/)，在 Gemini Interactions API 中以预览形式推出 Tool Retrieval。官方的问题意识是：智能体接到几十甚至上百个工具时，每次请求都发送完整参数 schema，会增加输入 token 和延迟，并可能降低工具选择的准确性。

用法是在请求中加入 `tool_search`，并对希望暂缓加载的工具设置 `defer_loading: true`。官方称，模型仍能看到这些工具的名称和描述，但参数 schema 先不进入上下文；需要时由 API 在同一次请求里加载，再发出函数调用。也可以把检索交给调用方自己执行。

该功能对 Gemini 3.6 及之后的模型可用，包括所有 Gemini 4 模型；没有单独收费，按所用模型的标准 token 价格计费。官方说，只有在未加载的 schema 比实际加载的更多时，才会节省 token，并建议用自己的流量来衡量。这是预览功能，不是已经完成的全面开放。

## 热榜上，智能体技能框架增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月20日约 09:21 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[obra/superpowers](https://github.com/obra/superpowers) 当天约增加 2,028，总星约 322,094，增量最高，页面介绍为智能体技能框架与开发方法，昨日已经上榜。[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 约增加 1,349，总星约 12,558，是新面孔，页面介绍为面向漏洞挖掘和外部红队的 Claude Code 技能包。[mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) 约增加 954，总星约 70,810。[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) 约增加 898，总星约 60,576。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 825，总星约 204,249。全表在文末。

## X上顶尖AI大佬最近都说了什么

**Jason Wei**，Mercor 首席科学家，曾任职于 Meta、OpenAI 和 Google。他[写道](https://x.com/_jasonwei/status/2123495287377571916)，在人工智能能够优化任何可量化对象的情况下，未来几年很多价值创造，将来自用新的方式去度量我们生活的世界。帖发于北京时间 11月20日 03:15，属个人判断，不是已验证的产业预测。

**Sebastian Raschka**，《Build a Large Language Model From Scratch》作者。他[写道](https://x.com/rasbt/status/2123433827234111659)，Marin Mochi（535B-A23B）检查点的公开量很大，在他看来是好事，并称还有技术报告说明各组件如何为训练稳定性和 GPU 吞吐而选择。他列举的要点包括：在 latent 上额外加 RMSNorm 的 Latent MoE，经典的 3:1 滑动窗口与全局门控 GQA，以及局部 Partial RoPE 与全局 NoPE 等。帖发于北京时间 11月19日 23:10，是他对已公开材料的个人摘要。

检查点本身已在[上期](./ai-news-daily-2026-11-19.md)简讯中写过。Open Athena 11月9日已有架构说明，11月17日的检查点博文仍写技术报告待发布，本期不把它写成新的正式技术报告已经发表。

**Simon Willison**，Datasette 作者、Django 共同创建者。他[写道](https://x.com/simonw/status/2123305131206967571)，pelican riding a bicycle 测试最有用的地方，仍是用来对照同一家族里不同模型、不同努力程度的差别，并贴出了 Gemini 4 Carbon、新发布的 Gemini 4 Neon，以及 Gemini 4 Hydrogen 在 low、medium 和 high 档的结果。帖发于北京时间 11月19日 14:39，属个人演示，不是对官方榜单的复核。

## 另外几则

**OpenAI 介绍用 Codex 驱动的 Performance Factory 自动排查 ChatGPT 性能回退。** 公司 11月19日[发文](https://openai.com/index/how-openai-performance-factory-keeps-chatgpt-fast/)称，该系统在云端运行：性能告警触发后，智能体调查并提议修复，供工程师审阅；部署后再检查是否回到基线。官方写，Regression Workflow 在三个多月里跟踪了超过 1,700 次调查，并定位了超过 600 个根因，相当于每天约 17 次自动调查。这些是公司自报的内部数字。文中也写，眼下的瓶颈可能仍是等待工程师审阅和合并修复。

**Ai2 在 Asta 平台上线 Theorizer，并开源其代码。** Allen Institute for AI 11月19日[宣布](https://allenai.org/blog/theorizer-in-asta)，Theorizer 可针对研究问题检索文献、提取发现并生成带文献依据的解释。官方同时说明，它可能漏掉相关研究、误判新颖性，研究者仍需核对证据。文中案例来自合作科学家的使用经历，不是独立对照试验。

**微软 CEO Satya Nadella 解释向约 6 万名员工提供买断的原因。** 据 [TechCrunch](https://techcrunch.com/2026/11/18/microsoft-ceo-satya-nadella-explains-why-he-asked-60k-employees-to-quit/) 对 11月18日 DealBook Summit 的报道，Nadella 称 10 月的买断是为了让员工在转型中拥有选择权，而不是用人工智能直接替换员工；目标是让工作转向管理人工智能智能体。这是对早先买断计划的事后解释，不是新宣布的裁员。本期未读到微软官方逐字稿。

**Anthropic 11月17日发文称 Claude 解决了两个黑洞物理中的未决问题。** [官方研究博文](https://www.anthropic.com/research/claude-black-hole-physics)标题写明是 Claude Fable 5.2，并称两项工作大体上自主完成，但并不接近解决量子引力问题。这是公司自己的研究说明，日期已超出主要 24 小时窗口；它今日出现在 Hacker News 首页，这里仅作回溯，不当成今日新发布。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11月20日 09:21；当时页面 16 行；页面 HTML 抓取约 09:21:37）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 12,558 / +1,349 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [obra/superpowers](https://github.com/obra/superpowers) | 322,094 / +2,028 | Shell | 智能体技能框架与开发方法 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 60,576 / +898 | Python | 让各类软件可被智能体原生调用的 CLI 层 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 66,886 / +238 | Python | 两小时从零训练 64M 大模型 |
| [cursor/plugins](https://github.com/cursor/plugins) | 17,567 / +384 | TypeScript | Cursor 插件规范与官方插件 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 204,249 / +825 | TypeScript | 面向智能体的搜索、抓取与数据接口 |
| [nginx/nginx](https://github.com/nginx/nginx) | 32,340 / +73 | C | NGINX 官方开源仓库，与人工智能无直接关系 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 11,568 / +246 | C++ | 优化与部署人工智能推理的工具包 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 68,643 / +271 | HTML | 面向多种编码智能体的图表设计技能 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 70,810 / +954 | Python | 跨多个平台调研话题并汇总的智能体技能 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 10,722 / +302 | TypeScript | 面向 Stitch MCP 服务的智能体技能库 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 1,857 / +377 | Shell | 应用商店审核与合规的公开手册和预检 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 13,137 / +38 | Python | 面向 CI/CD 可靠性的开源智能体 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 75,183 / +182 | TypeScript | 开源知识库，与人工智能无直接关系 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 12,742 / +341 | Python | 下载工具，与人工智能无直接关系 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 11,250 / +126 | Python | 开源人工智能视频剪辑桌面工具 |

Anthropic 首日交易：纳斯达克新闻稿日期 November 19, 2026，写明 “began trading on the Nasdaq Stock Market on Thursday”，“opened for trading at $111.50 per share”。雅虎财经行情页（抓取约北京时间 11月20日 09:23:25）显示 Previous Close 83.00、Open 111.50、收盘/regularMarketPrice 97.17（涨幅 17.07%）、Day's Range 92.72–115.10、Volume 851,818,130、Market Cap (intraday) 1.272T；同一页 JSON 中 postMarketPrice 为 92.60，After hours 时间显示 7:59:58 PM EST，盘后不是官方收盘价。CNBC 直播页（更新时间写 Thu, Nov 19 2026 7:04 PM EST）写 closed at $97.17、opened at $111.50、jumped 17%，成交 “More than 846 million shares”，并写收盘充分稀释市值 “roughly $1.8 trillion”。雅虎财经直播稿还写当日最高曾到 115.10，与行情页最高价一致；开始交易时间各稿不完全相同（有的写 just after 11:30 a.m. ET），正文不采用精确到分钟的开盘时刻。路透社条目 https://www.reuters.com/business/finance/anthropics-historic-debut-put-ais-promise-peril-wall-st-test-2026-11-19/ 本期返回 401，未能直接核对。美联社稿返回 403。发行规模口径沿用上期按官方定价公告的粗算：956,351,354 × 83 = 79,377,162,382 美元；980,000,000 × 83 = 81,340,000,000 美元。预计交割日期仍为 2026-11-20，采集时对应美国东部 11月19日约 20:23，不能写成已经交割。AIHOT 转述中的现金储备约 2,200 亿美元，本期未在公司原文中核对，正文不用。

Gemini Mac computer use：官方博客日期 November 19, 2026，作者 Michael Friedman。范围原文为 “rolling out in English in the U.S. in the Gemini app for Mac”，脚注为 “Requires an Apple Silicon Mac running macOS Sequoia 15.0+. Available for personal Google accounts 18+, available to Google AI Plus, Pro and Ultra users.” 控制与审批机制为官方自述。Macworld 称其当时下载到的版本仍是 1.147.5.1526，尚未包含该功能。

Tool Retrieval：官方博客日期 November 19, 2026，作者 Lucia Loher、Nora Kassner。“available in preview in the Interactions API”；支持 “Gemini 3.6 and later models, including all Gemini 4 models”；“no separate charge”，按所用模型标准价格计费。官方写明节省取决于未加载 schema 是否多于实际加载者，并建议 “Measure it against your own traffic”。

Performance Factory：官方博客日期 November 19, 2026，作者 Okay Zed、Cyrus Forbes。“In just over three months, the Regression Workflow tracked more than 1,700 investigations and root caused over 600 cases. That’s 17 automated investigations every day.” 修复需工程师审阅；官方称正在探索智能体是否可自行完成后续步骤。本期用 curl 抓取该页返回 403，正文依据此前已成功打开的页面内容。

Theorizer：Ai2 博客日期 November 19, 2026。官方写明可能 “miss relevant studies and misjudge originality”，研究者仍需核对。案例为合作科学家使用经历。

Nadella：TechCrunch 稿日期 November 18, 2026，4:42 PM PST，报道 DealBook Summit。买断发生在 10 月，属 48 小时窗口内的事后解释。本期未读官方逐字稿。

Claude 黑洞物理：官方研究博文日期 November 17, 2026，标题为 “Claude Fable 5.2 solves two open problems in the physics of black holes”。官方称 “Both were carried out largely autonomously. Neither result settles the question of quantum gravity, or even comes close to doing so”。超窗，仅因今日 HN 热议作回溯。

X：三帖均经 X 公共读取接口直接读取原帖，并读取了超 280 字帖的全文。Jason Wei 原帖时间 2026-11-19T19:15:03Z（北京时间 11月20日 03:15），帖 ID 2123495287377571916。Sebastian Raschka 原帖时间 2026-11-19T15:10:50Z（北京时间 11月19日 23:10），帖 ID 2123433827234111659；昨日已用过的基准比较帖（ID 2123064851383677087）本期不再选用。Simon Willison 原帖时间 2026-11-19T06:39:27Z（北京时间 11月19日 14:39），帖 ID 2123305131206967571。François Chollet 与 Thomas Wolf 在排除回复与转发后，窗口内没有比昨日已引用帖更新的合格原帖。Karpathy、LeCun、Andrew Ng、Noam Brown、Lilian Weng、Ryan Greenblatt 在排除回复与转发后，窗口内无合格原帖。Miles Brundage 的用户名 MilesBrundage 未能解析到账号。Jim Fan 有一条 GR00T 2 实机演示帖（ID 2123470587259732200），因该模型已在更早日报写过，且更接近产品演示，未列入三人精选。Nathan Lambert 窗口内有祝贺 Anthropic 上市等原帖，因与今日头条重复或内容较轻，未列入三人精选。

Hacker News（采集约北京时间 11月20日 09:20）：当时 “Anthropic’s Nasdaq debut” 约 889 分（item 50562754），“Claude solves two open problems in the physics of black holes” 约 373 分（item 50563148），“Gemini 4 Neon is the new #1 on the Models Engineering Index” 约 60 分（item 50568130，本期未回读该榜原文，不作为新头条）。首页另有与本期主题无直接关系的条目。

来源覆盖：已读 AIHOT 11月20日页（每天 08:00 出刊）、Hacker News 首页、GitHub 热榜（北京时间 11月20日约 09:21 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以纳斯达克新闻稿、雅虎财经行情页、CNBC 直播页、Google 官方博客、OpenAI 官方博客、Ai2 官方博客为依据。路透社与美联社的 Anthropic 上市稿未能打开。AIHOT 另列的中国公司云算力合同与芯片交付受阻、英伟达股价复盘等，或为未能核对到足够原文的媒体转述，或与已报道议题重复，本期不作为新头条。Moonshot 取消约 1.5 亿美元印尼算力合同的说法，原始报道来自付费媒体 The Information，本期未能阅读原文，不用作事实。Vals 或第三方关于 Gemini 4 Neon 重新排名的个人页面，未回读原榜，正文不用。

</details>
