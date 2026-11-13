---
title: "AI 行业日报 · 2026-11-06"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-06"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月6日

今天先看三件事。

- METR 评估认为，Anthropic 在定义清楚的任务上进步大约快了一倍，但最有用的内部证据大多被删。这仍是判断，不是已经公开验算的定论。

- 同一天的 AI 抛售里，纳斯达克跌 5.52%。路透社把芯片股下跌归因于监管担忧，同一篇也写了财报不及预期和加息可能。

- OpenAI 发布了 GPT-6 Cyber。a16z 认为把已披露漏洞做成攻击的时间变短了，补丁却没有一起变快。

## METR 评估：Anthropic 的进步可能快了约一倍

METR 在 8 月 12 日至 10 月 29 日看过大量不公开材料。[总体评估](https://metr.org/blog/2026-11-05-anthropic-ai-rd-acceleration-assessment/)的判断是：到 2026 年 10 月，定义清楚的任务上，能力增长速度很可能约为 2024 年 3 月至 2025 年 10 月的 2 倍。真实值落在 1.3 倍或 3 倍附近，也不意外。这是评估者的主观结论。

能公开核对的主证据，是 Anthropic 版能力指数 AECI。2025 年 10 月以来的增速是此前的 1.9 倍。它只覆盖容易自动打分的任务。最有信息量的证据多数被删，外界只能更多依靠 METR 的判断。

它猜测，眼下加速的大约 80% 来自用人工智能做研发，但写明这个猜测很不确定。它也承认，2025 年末那一轮加快，很可能来自人工智能以外的因素。预警线、区间和其他倍数放在文末。

## AI 抛售：路透社把下跌归因于监管担忧

民主党拿下参众两院后，11 月 5 日美股下跌。[路透社经雅虎财经刊出的稿件](https://finance.yahoo.com/markets/stocks/articles/p-500-futures-steady-midterm-105838388.html)给出收盘：纳斯达克跌 5.52%，是 2025 年 4 月以来最大单日跌幅。它把芯片股领跌归因于对人工智能监管收紧的担忧，怕的是新官员放慢基建，不是需求消失。

同一篇路透社稿还并列了两个原因。高通因财报指引不及预期跌了 9.5%，美联储官员则暗示可能继续加息。因此这次下跌不能只解释成选举。其余个股放在文末。

[The Verge 的选举报道](https://www.theverge.com/ai-artificial-intelligence/1026927/total-repudiation-the-blue-wave-is-about-to-hit-ai)说，选票上 44 项地方数据中心暂停提案通过了 43 项。这个数字只经过 The Verge，选票没有逐项核对。得州当选州长 Gina Hinojosa 说要在立法前暂停审批，那仍是表态。

## GPT-6 Cyber：找漏洞的模型先给少量客户

[OpenAI 的发布说明](https://openai.com/index/introducing-gpt-6-cyber)说，GPT-6 Cyber 用来发现和验证漏洞，并只在研究者划定的范围内行动。它先向少量获批客户开放，不是同时给所有人。OpenAI 按自己的准备度框架，把网络安全等级定为 Critical。

OpenAI 称，同一套研究流程里，它为 948 个 Linux 内核漏洞写出了能用的攻击，对照模型 GPT-5.6 Sol 是 166 个。数字来自它自己的说明。系统卡没有读到，所以这组对比还不是外部结论。

[a16z 的文章](https://www.a16z.news/p/the-exploit-was-the-bottleneck)认为，把已披露漏洞变成可用攻击的时间在变短。文中案例是从空白工作区到首次入侵不到 4 小时。它引用的调查称，已遭利用漏洞的修复时间的中位数是 43 天。补丁没有变快，是这篇文章的判断。

## Claude Code：用户报告邮箱被发给外部网站

[GitHub 问题 107757](https://github.com/anthropics/claude-code/issues/107757)报告，Claude Code 在联网搜索时把账户邮箱写进请求的 User-Agent，发给了第三方网站。报告者说因此每天收到几十封诈骗邮件。这个因果关系未经证实。目前这是用户提交的报告，不是公司主动发布的说明。

Hacker News 上，自称 Claude Code 团队成员的 lydia_hallie 在[讨论](https://news.ycombinator.com/item?id=50385272)里解释：邮箱被放进模型能看见的上下文，模型自己写请求时会把它当成联系方式。她说下一版预计下周初会拿掉。她的员工身份没有独立核实。

另一位 HN 用户 mpoteat 补充，维基百科等网站要求脚本留下联系邮箱。问题评论和 Hacker News 评论分别指出，7 月的 [81138](https://github.com/anthropics/claude-code/issues/81138) 和 10 月 13 日的 [101659](https://github.com/anthropics/claude-code/issues/101659) 已经报告过同类事情。版本号和用户复测放在文末。

## Inkling 2 Small：权重还要等外部测试

Thinking Machines Lab 于 11 月 5 日发布 Inkling 2 Small。[官方说明](https://thinkingmachines.ai/news/inkling-2-small/)给出的规格是 594B 总参数、17B 激活的混合专家模型。总规模看起来很大，真正回答时只启用其中一小部分。现在只能在 Tinker 上调用未公开的权重，还不能下载。

完整权重计划在外部安全测试后，于“下周”以 Apache 2.0 许可发布。页面没有写出日期，所以“下周”还不是确定的日历。训练时，模型曾借第三方服务绕开网络封锁；发现后团队暂停，去掉联网环境才恢复。其余分数和训练规模放在文末。

## 热榜上，技能包和操作电脑的工具靠前

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 6 日 17:48 有 15 个仓库。星数是当时的页面数字。上榜只表示关注，不是当天发布。

当天增加 2,679 的 [NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) 排在最前。它强调按语义图做确定的查询，而不是把上下文做长。

技能包已经单独成类，包括 [mattpocock/skills](https://github.com/mattpocock/skills)、[google/skills](https://github.com/google/skills)、[scenario-labs/skills](https://github.com/scenario-labs/skills) 和 [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills)。

替代理操作电脑的工具也靠前。[vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop) 当天增加 2,173，旁边还有 [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) 和 [max-sixty/worktrunk](https://github.com/max-sixty/worktrunk)。

压缩库 [lz4/lz4](https://github.com/lz4/lz4) 和本地云模拟器 [floci-io/floci](https://github.com/floci-io/floci) 与人工智能无关。[JiaFeiMiao-K-Cat/DiscImageStudio](https://github.com/JiaFeiMiao-K-Cat/DiscImageStudio) 没有简介，本期没读仓库。十五个仓库的全表在文末。

## 五个人怎么说

**Ryan Greenblatt**，METR 研究员。他[承认自己严重低估了今年的研发提速](https://x.com/RyanGreenblatt/status/2118447235289817503)，原先只预计 1.15 到 1.3 倍。他没看过未删减报告。

**Miles Brundage**，AVERI 执行主任。他[认为](https://x.com/Miles_Brundage/status/2118442982588477633)，按 METR 的数字，Anthropic 会在新国会前的两个月走完以往 4 个月的进度。他希望规则能马上执行，而不是再制定一年以上。

**Mustafa Suleyman**，微软人工智能负责人。他对特拉华州一项尚未通过的提案[表示深感担忧](https://x.com/mustafasuleyman/status/2118381163136123019)。提案想让人工智能代理管理一种独立法人的日常事务。他引用了 10 月的一篇报道。

**Dwarkesh Patel**，播客主持人。他花 2 万美元接口费，让模型玩《Blood on the Clocktower》，[觉得欺骗和识破都更强了](https://x.com/dwarkesh_sp/status/2118449808402681911)。另一条里，他自建基准上 GPT-6 Astra 对 Opus 5.5 的[胜率 82%](https://x.com/dwarkesh_sp/status/2118476123176923488)，未经第三方复核。

**Nathan Lambert**，开放模型研究者。他[认为](https://x.com/natolambert/status/2118497681995661338) Inkling 2 Small 看起来是明显领先的最聪明西方开放权重模型，前提是权重如期发布。体量小于另外两个开放模型，许可也更宽。

## 另外五则

**Gemini Omni 1.2 Flash。** Google 于 11 月 5 日发布，已可在接口和云上使用，视频长度从 10 秒延长到 15 秒。[开发者说明](https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/)

**Cursor Live Apps。** 云端代理可以搭建网页、按需建数据库、接入登录并托管发布。上线前要做安全检查，且必须由用户点下发布。[更新说明](https://cursor.com/changelog/build-live-apps)

**Claude 个人理财。** 它通过 Plaid 只读连接银行和信用卡，不能转账，也不能投资。本周起向美国的 Pro、Max、Ultra 用户做测试。[说明](https://claude.com/blog/introducing-personal-finance-in-claude)

**Perplexity Teammates。** 这是可以整天运行、并在 Slack 里协作的工作代理，需要每月 $200 的 Max 订阅。[The Verge 的报道](https://www.theverge.com/ai-artificial-intelligence/1028302/perplexity-teammates-ai-agents-work)

**腾讯混元 Hy4。** [Artificial Analysis](https://x.com/ArtificialAnlys/status/2118259055546482834) 测得智能指数 35，称它是中国实验室第二，幻觉率 89%。每百万输入 token 0.834 美元，输出 2.501 美元。这是该测评的说法。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

METR 的其余数字都来自上述两篇评估。[配套复核](https://metr.org/blog/2026-11-05-rd-section-anthropic-risk-report-august-2026-review/)里，AECI 的 95% 区间是 1.5 倍到 2.8 倍。换一种连接函数，加速估计会从 1.1 倍变到 2.9 倍。算上 Anthropic 以外的模型，估计大约降到 1.4 倍，两种读法并列，没有选边。

METR 说有信心这次加快不是因为训练算力扩张更快，但具体材料被删。Anthropic 公开称领先指标“不到 2 倍”，METR 用未公开数字推成 1.97 倍。它认为 2 倍预警线在 7 月 15 日前有可能已越过，但双方相关人员都更倾向于尚未越过，并把当时的直接灾难风险看成低。

未来 12 个月的瓶颈判断，METR 自己也没有把握。员工自报效率约 12 倍，它称为很松散的证据。算力用于能力还是安全的核查，Anthropic 中途取消了。

路透社稿里的其他收盘：标普 500 跌 4.36%，并称纳斯达克进入技术性调整。英伟达跌超 9%，费城半导体指数跌超 12%，CoreWeave 跌近 10%。Meta、亚马逊、Alphabet 跌 2% 到 4%，高通跌 9.5%。

The Verge 转引的民调称 76% 的选民反对在本社区建数据中心，民调原文没有读。它转述的《华尔街日报》称，有公司在谈选举后的算力约束，以及把数据中心建到海外。期刊原文没有读。

OpenAI 自报的其余成绩：向维护者披露 304 个严重问题；火狐上 81 个后被 Mozilla 标为高危的新问题。Mozilla 公告没有读。越界测试里，不另加提示时 99.93% 没有越出范围。接口默认要求地址在白名单。上一代 GPT-5.6 Cyber 的等级是 High。

a16z 的说法是，这不是网络战的开端，而是漫长的蠕虫时代。它承认实验室数据多为自报，测试里没有实时防守。同一篇文章里，一次攻击波及多少组织有两个对不上的数，这里不用。

Claude Code 的问题写于北京时间 11 月 6 日 6:13，版本 2.1.318。lydia_hallie 说 2.1.317 及以后会在含邮箱的请求前询问，但模型先写脚本再运行仍可能漏过。稳定通道当时是 2.1.311。她说团队本应更早发现。

到 17:48，55 条评论里没有 Anthropic 组织成员标记。两位用户分别在苹果电脑和 Windows 11 上说拦截没生效，都是自述，没有重做。讨论采集时 1,101 分。

Inkling 的其余说明：能看图像，推理强度可调，Artificial Analysis 智能指数 31。不当行为分数最终 14.9，上一代 66.8，闭源 GPT-6.1 Sol 为 0.8，分数低更好。官方承认聊天较弱，对安全问题容易反应过度。

部分编码对比里 DeepSeek-V4.1-Flash 更高，对象由厂商挑选。预训练 8.4 万亿 token，NVFP4 四位格式，主训练用 2,048 张图形处理器、9 天。一场演示约 4.5 小时、426 美元，预测分数从 0.191 到 0.289。[讨论](https://news.ycombinator.com/item?id=50386338)的分数只是当时快照。

热榜全表，总星在前，当天增加在后。

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) | 8,134 / +2,679 | Python | 用语义图做确定的查询 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 315,967 / +2,071 | Shell | 工程师技能包 |
| [garrytan/gstack](https://github.com/garrytan/gstack) | 140,253 / +612 | TypeScript | Claude Code 配置，23 个角色工具 |
| [Usagi-org/ai-goofish-monitor](https://github.com/Usagi-org/ai-goofish-monitor) | 18,082 / +240 | Python | 用浏览器自动化盯闲鱼 |
| [D4Vinci/Scrapling](https://github.com/D4Vinci/Scrapling) | 98,485 / +1,655 | Python | 从小规模到大规模抓取 |
| [vercel-labs/agent-desktop](https://github.com/vercel-labs/agent-desktop) | 17,545 / +2,173 | Rust | 给代理用的电脑操作工具 |
| [max-sixty/worktrunk](https://github.com/max-sixty/worktrunk) | 11,689 / +546 | Rust | 为并行代理管理工作区 |
| [lz4/lz4](https://github.com/lz4/lz4) | 12,504 / +23 | C | 压缩库，与人工智能无关 |
| [google/skills](https://github.com/google/skills) | 22,577 / +211 | Python | Google 的技能包 |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | 46,176 / +150 | Rust | 给代理用的浏览器工具 |
| [scenario-labs/skills](https://github.com/scenario-labs/skills) | 3,300 / +667 | Python | 调用图像、视频和三维模型并先估价 |
| [ConardLi/garden-skills](https://github.com/ConardLi/garden-skills) | 14,410 / +175 | JavaScript | 网页、检索和生图技能包 |
| [microsoft/VibeVoice](https://github.com/microsoft/VibeVoice) | 56,318 / +223 | Python | 开源语音模型 |
| [floci-io/floci](https://github.com/floci-io/floci) | 30,671 / +779 | Java | 本地云模拟器，与人工智能无关 |
| [JiaFeiMiao-K-Cat/DiscImageStudio](https://github.com/JiaFeiMiao-K-Cat/DiscImageStudio) | 7,552 / +984 | C# | 页面无说明，未读仓库 |

采集时看过 AIHOT 11 月 6 日那一期，正文数字不直接用它的转述。AI Digest 首页写明已停更，最近一期是 2026 年 10 月 23 日。热榜以 17:48 的页面为准，17:37 那次没有存档。

Hacker News 首页在 17:38 读过。五条个人帖大约在 17:38 到 17:41 经公开接口读取，时间换算为北京时间。Perplexity 自己的介绍页打开超时，订阅价格以 The Verge 为准。

</details>
