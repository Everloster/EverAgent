---
title: "AI 行业日报 · 2026-11-23"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-23"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---
# AI 日报 · 2026年11月23日

今天先看三件事。

- OpenAI 首席科学家 Jakub Pachocki 11月22日发表博文，公开公司内部预训练的对数困惑度测量，并主张把困惑度（也就是交叉熵损失）作为开发者之间比较、以及制定共享安全标准的指标。他提议在理解与监测能力达到具体里程碑之前，行业应设定共同的开发上限。这是他的主张和公司自报数字，不是已经生效的行业规则。

- OpenRouter 11月22日通报：安全研究者报告部分推理服务商出现数据被获取、或数据政策未被遵守的情况。该公司称自身未被入侵，已下架三家服务商，并将 125 个接口移出“零数据保留”资格，同时通知了可能受影响的客户。这是平台自己的处理说明。

- 美国财政部长贝森特 11月22日在哥伦比亚广播公司《Face the Nation》节目中说，他上周要求英伟达在 10 天内就出口合规给出的答复，目前仍未收到；内阁已与临时管理层、首席董事和律师接触。他强调“不守规文化”仍只是一种可能性，并称要先看清责任落在哪一层，再谈黄仁勋是否回归。这是官员表态，不是调查结论。

## OpenAI 首席科学家提议以困惑度为共享指标，并公开内部预训练测量

[OpenAI 博文](https://openai.com/index/perplexity-and-intelligence)发布于 11月22日，作者是首席科学家 Jakub Pachocki。他认为，现代人工智能的关键进展，主要来自在大规模数据上训练更好的“压缩器”或预测器；跟踪这一过程的速度，有助于把握能力演化的轨迹。

他主张把困惑度，也就是交叉熵损失，确立为开发者之间比较、并用于共享安全标准的指标。作为第一步，他公开了 OpenAI 内部的预训练测量。文章写明，这些数字来自该公司自 GPT-3.5 以来主要跟踪的、取自内部代码库的留出数据集，并且是固定快照。因此不能直接与其他实验室在不同数据集上的数字对比。

官方自报：GPT-3.5 在该数据集上的对数困惑度约为 0.99，对应流畅对话，并成为最初 ChatGPT 的基础；GPT-4 约为 0.91，能够有效使用思维链推理；目前损失已低于 0.8，他写道，网络与数学等领域出现了“变革性”能力。他还写，当模型升级到约 0.76 后，开始在数学开放问题上给出被他称为突破性的结果。这些阈值与能力的对应，是作者的回顾性叙述，并非事先验证的定律。

他担心，预训练算法研究一旦也被人工智能显著加速，监测和对齐研究可能跟不上。他写道，最早在 2027 年，就“可以设想”出现类似的预训练基础进展浪潮。这是个人外推，不是时间表。注脚还写，2026 年曲线变陡，主要归功于长期研究与算力投入，自动化只占较小部分；但最近的模型已有来自人工智能的有意义设计贡献。

据此，他预计在约 0.68 到 0.7 的对数困惑度区间，还可能出现今天未必在测的新能力，并伴随现有对齐审计方式进一步失效。他提议开发者共同设定评估与红队规范，并基于困惑度等测量设立共同上限，在理解与监测能力达到具体里程碑——例如找到思维链监测的替代方案——之前不要越过。

文章也列出该指标的局限：跨实验室难以直接比较；它并不对应某一项具体任务；思维链推理不会降低困惑度，却能显著提高能力；数据的固有熵未知，接近下限时数字进步会变慢，但智力跃迁可能更大。

## OpenRouter 因推理服务商数据事件下架三家，并取消 125 个零数据保留资格

[OpenRouter 11月22日通报](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/)，本周早些时候，安全研究者报告部分推理服务商出现数据被获取，或显示其数据政策未被遵守。公司称已与研究者和相关服务商合作了解情况，并写明：检测结果并未显示 OpenRouter 自身遭到入侵或未经授权的访问。

已采取的措施包括：根据调查结果，从平台下架三家服务商；将 125 个接口移出零数据保留（ZDR）资格，其中既有研究者标出的服务商，也有作为预防措施额外移除的接口；并通知所有可能受影响的客户。正在进行的工作包括：把研究者的检测方法改造成持续检查；核验网络路径，识别请求和响应被转发到第三方的情况；在恢复任何接口的零数据保留资格前，要求相应保证和验证。

页面列出已收到的服务商安全公告，包括 Atlas Cloud、Novita、Phala，以及 Together AI 关于 2026年6月至7月提示词样本泄露的说明。[上期](./ai-news-daily-2026-11-22.md)已报道 Together AI 自己的通报。OpenRouter 写明，并非所有受影响的服务商都已公开发布说明，但无论是否有公开文章，公司都已通知受影响用户。它感谢 Dragos 的报告，并称希望把类似检测方法纳入自身流程。这是平台对事件的说明，不是独立调查报告。

## 贝森特：英伟达仍未给出一周前要求的合规答复

美国财政部长斯科特·贝森特 11月22日（美国日期周日）上了哥伦比亚广播公司《Face the Nation》。[报道](https://www.cbsnews.com/news/bessent-nvidia-china-ai-chips-alice-huang-canard/)与[访谈实录](https://www.cbsnews.com/news/transcript-treasury-secretary-scott-bessent-face-the-nation-with-margaret-brennan-nov-22-2026/)均写明：他上周日在福克斯新闻节目中要求英伟达在 10 天内就出口限制合规作出答复，七天过后仍未收到。

贝森特说，内阁已与临时管理层、首席董事及其律师接触，“我们确实需要答复”，并称英伟达宜尽快说明当时的文化是怎样的。主持人对他先前提出的“不守规文化”表示这是一项严厉指控，他再次强调，当时说的是“可能性”，“我们会看清楚”，并认为董事会正迅速查明这种文化是否存在。[11月16日日报](./ai-news-daily-2026-11-16.md)已记录他在福克斯新闻上的上述要求，以及主张从外部选任首席执行官。官员质疑不能写成已经查实的出口违规。

在黄仁勋是否回归的问题上，贝森特没有直接表态赞成。他说，要先看清“责任落在哪里”：不合规若属实，是底层、中层，还是一直到最高层。节目中也提到，美国总统已公开呼吁黄仁勋回到首席执行官职位。关于黄仁勋与被指有中方情报背景的 Alice Huang 的传闻关系，贝森特称之为“有点像转移视线”，并把它与公司是否存在合规文化分开讨论；他还说，他“假定”黄仁勋当时并不知道对方被指是间谍。这些都是官员个人表态，相关指控本身本期未做独立核实。

访谈还提到，英伟达已在 2025年8月把 Megaspeed 移出销售名单；贝森特说，财政部等部门曾推动将其列入黑名单，并称上周出台的远程访问规则可能更为重要。Megaspeed 是否为向中方实体转运高端芯片的通道，他说“我们会看清楚”。这些同样不是已公布的调查结论。CBS 的报道还写，黄仁勋已同意在 12 月初出席参议院银行委员会作证，并接受众议院相关委员会询问。

## Sarvam 发布 105B 模型的新开源权重检查点

印度实验室 Sarvam AI 11月22日[宣布](https://www.sarvam.ai/blogs/sarvam-105b-1711)发布 Sarvam-105B-1711，这是 Sarvam 105B 的新开源权重检查点，在升级后的 B200 基础设施上训练。官方把它定位为面向客服、语音代理和代理式任务等大量请求场景的 Flash-Lite 模型。权重提供 BF16，以及约 65 GB 的 NVFP4 版本，官方称可在单张工作站 GPU 上运行。

官方自报：在其选定的八项对话代理基准上，平均分由 2 月那个检查点的 42.6 升至 73.9；混合价格由每百万 token 0.44 美元降至 0.15 美元。分项中，IFBench 从 32.5 升至 82.5，客服对话中的工具使用（Tau2）从 46.2 升至 85.5，印度语言套件从 30.1 升至 79.1。在 Tau2 上连续四次都做对的比例为 69.5%，官方列出的对比是 Gemini 3.5 Flash-Lite 的 63.9% 和 Gemma 4 31B 的 62.1%。这些都是公司自己的评测和定价口径。

官方还把 73.9 分、0.15 美元的结果，与 Gemini 3.5 Flash-Lite 的 74.0 分、0.85 美元，以及 Gemma 4 31B 的 73.0 分、0.54 美元并列。对比对象、推理设置和价格来源由该公司选定，不能写成独立榜单结论。语音微调版为 Samvaad，官方称在自建的 Samvaad 基准上得到 68.7 分，高于基础检查点的 57.9 分。训练与推理吞吐的提升数字，同样是公司自报。

## 热榜上，漏洞挖掘技能包仍是当天增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月23日约 09:17 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 当天约增加 1,716，总星约 17,853，增量仍最高，页面介绍为面向漏洞挖掘和外部红队的 Claude Code 技能包，已连续多日增量领先。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 915，总星约 207,054。[obra/superpowers](https://github.com/obra/superpowers) 约增加 788，总星约 324,174，页面介绍为一种代理技能框架与软件开发方法。其余条目和全表放在文末。

## X上顶尖AI大佬最近都说了什么

本期精选三位研究者或行业人士的个人原帖。时间均为北京时间。以下是个人观点或个人测试，不是已核验的事实。

Nathan Lambert 是 Trillium Labs 的创始人兼主任，此前在 Ai2 共同负责 Olmo。他在 11月23日 08:24 的[原帖](https://x.com/natolambert/status/2124660436905926981)中评论 Pachocki 的文章，认为它把智力过多地压成一个量，而智力无论怎么度量都是参差不齐的；黎曼猜想表明数学处于峰值，真正的问题是其他有价值的领域落后多少。这是个人判断。

François Chollet 是 Keras 的作者，也是 ARC-AGI 与 ARC Prize 的联合创始人。他在 11月22日 05:01 的[原帖](https://x.com/fchollet/status/2124246742644461569)中写：要么认为这一轮人工智能扩张已经结束、对算力的需求已经见顶，要么把当前看成少有的买入机会。他提醒，GPU 现货价格仍在上涨，产能很难锁定，HBM 和 DRAM 的生产“实际上已经售罄”。这是个人市场判断，不是交易建议。

Noam Brown 在 OpenAI 研究推理，个人简介写明曾参与 Libratus、Pluribus、CICERO 以及 o 系列推理模型。他在 11月23日 01:26 的[原帖](https://x.com/polynoamial/status/2124555186043818245)中写，人工智能是会影响所有人的变革性技术，因此所有人都有权了解进展的轨迹，包括内部模型的进展。这是个人立场。

## 简讯

AI Digest 中文版仍显示停更于 2026年10月23日，本期只核验一次，未重试。AIHOT 今日目录以 Pachocki 的文章为头条，与已回读的官方原文一致。面壁智能关于 MiniCPM 成为老挝“国家模型”的说法，以及用户在 Mac 上用 MiniCPM5-2B 分析体检报告的实测，目前主要来自公司账号转发，本期不作为可独立核验的头条。NVIDIA Alpamayo 2 Edge、Perplexity Monitor API、Genie 4 等近期仍被聚合页提及的条目，官方发布日期分别早于本期 48 小时窗口，这里不作为新新闻。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

OpenAI 博文页眉日期为 November 22, 2026，作者 Jakub Pachocki, Chief Scientist at OpenAI。对数困惑度原文为 “GPT-3.5, at a log-perplexity of ~0.99”“GPT-4, at ~0.91”“losses below 0.8”“Once we upgraded to a model of log-perplexity ~0.76, it started producing groundbreaking results.”“we should expect further transformative capabilities as we enter the ~0.68-0.7 log-perplexity window.” 数据集注脚为 “The primary held-out datasets we’ve been using since GPT-3.5 are sourced from our internal codebase, and those are the numbers reported here (for a fixed snapshot).” 2027 年外推原文为 “as soon as 2027 we could conceivably see a similar avalanche of fundamental pretraining advancements”。注脚 5 原文为 “On the plot of losses of OpenAI models, you can see a steep acceleration in 2026. We attribute it mostly to the outcomes of long term research and compute investments, and only in a smaller part to automation. However, for the most recent models, we have already seen meaningful design contributions coming from AI.” 共享上限原文包括 “I further propose common limits, based on perplexity and other measurements, that developers are committed to not crossing until our ability to understand and monitor AI behavior achieves a certain concrete milestone (such as the development of a successor to CoT monitors).”

OpenRouter 页面标注 OpenRouter · 11/22/2026。下架与 ZDR 原文为 “Off-boarded three providers from OpenRouter, based on the results of our investigations.”“Removed 125 endpoints from Zero Data Retention (ZDR) eligibility. The removals included providers flagged by researchers, plus additional endpoints that we removed as a precautionary measure.”“Notified all potentially affected customers.” 自身未被入侵原文为 “These findings did not show any breach or unauthorized access of OpenRouter.” 已列出的服务商公告标题为 Atlas Cloud: Our commitment to your security and privacy；Novita: Privacy notice regarding MiniMax requests on Novita；Phala: November preliminary incident report；Together: Security event: prompt leakage for requests in June and July of 2026。页面还写 “Not all affected providers have posted publicly.” 以及 “We are grateful for the Dragos report.”

贝森特访谈于 2026年11月22日在 CBS《Face the Nation with Margaret Brennan》播出。报道页标注 November 22, 2026 / 1:48 PM EST；实录页标注 Updated on: November 22, 2026 / 12:41 PM EST。10 天期限与仍未收到答复，见于实录中主持人 “That was seven days ago. Have you gotten the answers you need?” 及贝森特 “We don't, Margaret.” 接触对象原文为 “We've been in touch with the temporary management, with the lead directors, with their lawyers.” 可能性原文为 “the important word there is possibility.” 回归问题原文为 “I think we have to see where the buck stops.” 对 Alice Huang 传闻的原文为 “I think that is kind of a canard”“Was there a culture of compliance versus one person's foibles?”“I assume he didn't know that she was an alleged spy.” Megaspeed 原文为 “we will see if Megaspeed was indeed a pass-through company, a front company based in Singapore, to get the high-end chips to Chinese entities.”“Nvidia actually took them off their vendor list or sales list in August of '25.” 黄仁勋 12 月作证一事写在 CBS 报道文末，不是访谈实录中的原话。

Sarvam 博文页眉为 Nov 22, 2026。八项对话代理基准平均分与价格原文为 “its average across eight conversational agent benchmarks rose from 42.6 to 73.9”“cut its blended price by two-thirds, from $0.44 to $0.15 per million tokens.” IFBench、Tau2、Indic 套件与 Tau2 pass^4 数字均来自该文图表和正文。65 GB NVFP4、单卡工作站 GPU，以及与 Gemini 3.5 Flash-Lite、Gemma 4 31B 的并列对比，同为公司自报。八项基准在文中写明为 IFBench、MultiChallenge、Advanced-IF、WritingBench（×10）、Arena-Hard v2、Tau2、BFCL v4 和 Sarvam Indic suite。

热榜全表，总星在前，当天增加在后。采集时点为北京时间 2026-11-23 09:17，以当时页面 HTML 为准。

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 17,853 / +1,716 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 207,054 / +915 | TypeScript | 为代理提供搜索、抓取和数据接口 |
| [obra/superpowers](https://github.com/obra/superpowers) | 324,174 / +788 | Shell | 一种代理技能框架与软件开发方法 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 15,165 / +701 | Python | 下载器，与人工智能无直接关系 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 62,786 / +699 | Python | 让各类软件对代理变得可命令行化 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 72,728 / +668 | Python | 汇总 Reddit、X、YouTube、HN 等来源的研究技能包 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 13,455 / +641 | Python | 开源人工智能视频剪辑桌面工具 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 3,989 / +621 | Shell | 应用商店审核与合规技能包 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 76,833 / +542 | TypeScript | 开源知识库，与人工智能无直接关系 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 70,308 / +518 | HTML | 给编码代理用的图表设计技能包 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 11,926 / +494 | TypeScript | 配合 Stitch MCP 的代理技能库 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 68,666 / +473 | Python | 从零训练小型语言模型的教程项目 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 14,431 / +399 | Python | 面向持续集成可靠性的开源代理 |
| [cursor/plugins](https://github.com/cursor/plugins) | 18,455 / +294 | TypeScript | Cursor 插件规范与官方插件 |
| [nginx/nginx](https://github.com/nginx/nginx) | 32,888 / +163 | C | 官方 NGINX 仓库，与人工智能无关 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 12,092 / +158 | C++ | 用于优化和部署推理的开源工具包 |

Hacker News（HN API 采集约北京时间 11月23日 09:17）：当时 “Perplexity and Intelligence” 约 472 分（item 50601525，约 01:06 进入列表），“Data Processing Incidents on Inference Providers” 约 279 分（item 50595554）。昨日已出现、仍在前排的条目包括 Alpöge 原短文约 2,907 分（item 50574968）、Inkling 2 Mini 官方发布约 1,454 分（item 50581260）、Lean 社区核验约 1,211 分（item 50589618）。“Agent swarm trying to solve P vs. NP” 约 99 分（item 50604314），对应公开实验页写明结论仍开放，本期不作为已取得结果的头条。另有 “87% of the Anthropic power will come from gas and 11% from coal in 2028” 约 880 分，但文章日期为 11月16日，超出本期窗口，不作为新头条。

X：三帖均经 X 公共读取接口直接读取原帖。Nathan Lambert 原帖时间 2026-11-23T00:24:57Z（北京时间 11月23日 08:24），帖 ID 2124660436905926981。François Chollet 原帖时间 2026-11-21T21:01:04Z（北京时间 11月22日 05:01），帖 ID 2124246742644461569；接口未返回超 280 字扩展全文，引用以当时返回的完整短帖为准。Noam Brown 原帖时间 2026-11-22T17:26:43Z（北京时间 11月23日 01:26），帖 ID 2124555186043818245。Sam Altman 与 Greg Brockman 窗口内有多条支持该篇 OpenAI 博文的个人帖，因与头条重复，未列入三人精选。Sebastian Raschka、Thomas Wolf 窗口内也有关于该文图表或引语的短帖，同样未另选。Karpathy、LeCun、Andrew Ng、Jason Wei、Lilian Weng、Jim Fan、Ilya Sutskever、Demis Hassabis、Awni Hannun 在排除回复与转发后，窗口内无合格原帖。Lambert 11月21日关于后训练开放问题的幻灯片帖，以及 Chollet 11月21日那条因接口未返回完整长文而未引用的学习方法帖，已在上期处理，不再选用。

来源覆盖：已读 AIHOT 11月23日页（每天 08:00 出刊，页面写第 216 期）、Hacker News 首页与官方 API、GitHub 热榜（北京时间 11月23日约 09:17 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以 OpenAI 官方博文、OpenRouter 官方通报、CBS 报道与访谈实录、Sarvam AI 官方博文为依据。聚合页或转述中出现的 NVIDIA Alpamayo 2 Edge（官方和技术博客日期为 10月21日或 11月10日）、Perplexity Monitor API（11月16日）、GPT-Live-1.1（API 更新日志为 11月19日）、Genie 4（10月27日）以及 11月20日前后的 Signal 截屏限制、OpenAI 对抗蒸馏文章，均超出本期主要窗口或已有更早官方日期，不作为新头条。《自然》与《科学美国人》对黎曼猜想证明的报道，主体是 11月20日至21日对已报道事件的跟进，本期不重复作为新进展。面壁智能/MiniCPM 相关条目未找到可独立核验的官方或政府原文，故只在简讯中说明。

</details>
