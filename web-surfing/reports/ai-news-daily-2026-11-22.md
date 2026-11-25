---
title: "AI 行业日报 · 2026-11-22"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-22"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---
# AI 日报 · 2026年11月22日

今天先看三件事。

- Lean 与 Mathlib 社区在 11月21日发表联合声明，并由 Lean FRO 与 Mathlib Initiative 背书，核验 Alpöge 于 11月20日公布的黎曼猜想 Lean 证明。声明写道，对该证明有充分信心，并称命题与证明均正确。这是形式核验的宣布，不等于数学共同体已经消化证明里的新想法。

- Together AI 11月21日通报：2026年6月至7月，其 serverless 推理服务中一部分已存储的提示词样本，在公开仓库暴露凭证后被未授权方下载。样本主要来自 MiniMax M3、GLM-5.2 和 Kimi K2.6 的请求。公司仍在审查是否涉及敏感客户数据。这是公司自己的通报。

- OpenAI 11月20日发布 MedChemBench，用 99 道来自已发表研究的题目，评估模型能否根据分子结构和实验证据做药物化学推理。官方自报在 xhigh 设置下，GPT-6.2 Astra 获得 84.5% 的可用分数。这是公司自己的基准和评分，官方也写明不能据此断言模型能发现新药。

## Lean 与 Mathlib 社区核验 Alpöge 的黎曼猜想 Lean 证明

[Lean 社区博文](https://leanprover-community.github.io/blog/posts/riemann-hypothesis/)发布于 11月21日，页面时间为 13:55；按 UTC 换算，相当于北京时间当晚 21:55。这是 Lean 与 Mathlib 社区的联合声明，并写明得到 Lean FRO 与 Mathlib Initiative 的背书。

声明说，Alpöge 在 11月20日发布的证明是约 1,700 万行的 Lean 库，直接只依赖 Mathlib。社区称已满足他们所引标准中的四项条件：命题采用 Mathlib 中已由专家审定的 `RiemannHypothesis`；库能够编译，并有多人复现同一份原始证明导出文件；用 `comparator` 和 `con-leche --compare` 核对后，所证定理正是该命题。行数来自社区声明，本期未独立统计。

社区还写，导出的原始证明已通过 Lean 官方内核，以及 `con-leche`、`con-ron` 等独立检查器。后两者带有相对于集合论的形式证明，说明它们不能接受错误证明，以回应“Lean 逻辑本身可能有漏洞”的担心。

MIT 的 Andrew Sutherland 在[核验记录页](https://math.mit.edu/~drew/grh/)汇总了更细的检查，并写明检查使用了 Claude Code。本期采集时，该页标注的最后更新时间仍是 2026-11-21 12:55 UTC（北京时间 20:55），早于上述社区声明；结果以当时页面为准。当时 175,187 个模块已全部编译通过，五个头条定理只依赖 `propext`、`Classical.choice` 和 `Quot.sound` 三个标准公理；独立内核 nanoda 与 con-leche 接受了完整导出证明。页面同时写明，针对该导出文件的 Lean 默认内核与 paranoid 内核重放，以及部分 `lake comparator` 流程，当时仍在进行。

五个被核验的定理包括：Mathlib 陈述的黎曼猜想；一条与之定义相等的改写；以及关于所有 Dirichlet L 函数在临界线右侧无零点、临界带内零点落在临界线上的陈述，也就是通常所说的 Dirichlet L 函数上的广义黎曼猜想。页面明确写明，Dedekind zeta、Hecke L 函数以及一般自守 L 函数不在此次核验范围内。

作为不依赖 Mathlib 中 zeta 定义的交叉检查，Sutherland 还把该证明与一份独立的 Robin / Lagarias 判定形式化合在一起，得到两条不再提及 zeta 函数的算术不等式。部分针对合证导出文件的内核检查，在该页最后更新时仍显示为进行中。

需要分清两件事。社区核验的是：在所用内核和 Mathlib 定义下，这些形式命题可由三个标准公理推出。这并不能自动等同于数学家已经理解证明中的新想法。社区声明自己也写，期待数学界接下来解释这些想法。

Sutherland 的页面同样提醒，通过检查依赖于这些内核，以及 Mathlib 的定义确实是它们声称的含义。[上期](./ai-news-daily-2026-11-21.md)已记录的陶哲轩、Scott Aaronson 的评述，以及 Alessandro Masullo 那份未使用人工智能的独立草稿，并不因此失效。

## Together AI 通报 6 至 7 月提示词样本泄露

Together AI 首席执行官 Vipul Ved Prakash 11月21日在公司[博文](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026)中通报：未授权方在一份私有 Hugging Face 仓库的凭证被写入公开代码仓库后，下载了存储在该私有仓库中的提示词样本。这些样本来自公司 serverless 推理服务，涉及 MiniMax M3、GLM-5.2 和 Kimi K2.6，主要日期为 2026年6月24日，以及 7月4日、8日和 14日。公司写道，样本是在例行软件测试中、并在获得相应授权后采集的。

公司称，凭证是在开发公开仓库 xorl 时，由人工智能编码智能体提交的。自动扫描发现后，他们撤回了这次提交，但在暴露窗口内，凭证已被人取得并用于下载样本。对方随后在样本中搜索其他服务的凭证并测试是否有效。其中 5 个被测试的凭证，是与 Dragos 安全实验相关的金丝雀凭证。

公司写道，没有理由认为对方已进一步泄露这些数据，并称了解到数据现已删除。他们已与外部取证公司和执法部门合作调查，目前未发现除此之外的其他提示词泄露。对受影响提示词内容的审查仍在进行，以确定是否暴露了敏感个人信息或其他客户数据，并将在必要时直接通知相关客户。

事后措施包括：改用有范围或短期凭证，并在支持的情况下改用无密钥访问；检查所有拉取请求中的凭证；新账户默认开启零数据保留；以及更新使用人工智能编码智能体的开发流程。公司建议处理敏感提示词的客户在账户中启用零数据保留。这是公司对自己事件的说明，不是独立调查报告。

## OpenAI 发布药物化学推理基准 MedChemBench

OpenAI 11月20日[发布](https://openai.com/index/introducing-medchembench/) MedChemBench，超出本期主要 24 小时窗口，这里作为 48 小时补充。该基准从已发表研究中抽出 99 道题，材料来自 117 篇论文和专利，包含 761 个不同分子结构，考查模型能否把分子结构与实验证据联系起来，解释结果、比较化合物并预测性质。

官方自报：在 xhigh 推理设置下，GPT-6.2 Astra 获得 84.5% 的可用分数，GPT-6 Astra 为 83.3%，GPT-6.1 Sol 为 82.0%，GPT-5.6 Sol 为 58.2%。官方还写，GPT-6 Astra 在重建分子结构和解释实验证据上较强；在同一 xhigh 设置下，结构项得到 95.4% 的可用分数，但在选择化合物和预测数值性质上大约只得到一半分数。这些数字都是公司自己的评测。

官方同时写明：这些结果并不能证明模型能够发现新药，或改善实验室决策；不能排除模型先前见过这些已发表来源；每次作答都是单次尝试，没有工具、反馈或新实验。基准评估的是对历史证据的推理，而不是真实的药物发现过程。

## 联合国会议未能就自主武器的约束性谈判授权达成一致

《卫报》11月21日[报道](https://www.theguardian.com/technology/2026/nov/21/international-talks-control-ai-autonomous-weapons-collapse)，在日内瓦举行的《特定常规武器公约》会议上，为期一周、旨在为具有法律约束力的国际条约确立谈判授权的努力未能成功。该公约有 128 个缔约方，决定需协商一致。报道写，会议在凌晨近 5 点结束通宵讨论后，通过了更弱的文本，要求各国“以协商一致方式拟定”一份未必带有法律义务的文书；俄罗斯提出程序异议，美国等军事大国也不愿承诺约束性议定书。

Al Jazeera 援引法新社的[报道](https://www.aljazeera.com/news/2026/11/21/nations-agree-to-draft-rules-for-killer-robots-at-arms-control-summit)则写为：各国同意在未来两年内“拟定”一项可能的协议。会议主席、瑞士外交官 Julien Thoeni 说，有国家拒绝使用“谈判”一词，因此商定文本改用“拟定一份文书”。他称这是人道主义裁军的重要一步。

Stop Killer Robots 等组织则批评授权被淡化，没有通向具有法律约束力规则的清晰路径。两家报道都指向同一结果：没有获得约束性条约的谈判授权，只就更弱的后续讨论安排达成一致。这是外交会议的结果，不是某项技术发布。

## Qwen4-Max 上线 Together AI，官方用一次整仓修复做演示

Together AI 11月21日[宣布](https://www.together.ai/blog/qwen4-max)，阿里巴巴旗舰模型 Qwen4-Max 已在其 Serverless 推理平台上线，上下文长度为 1M token。这与[11月17日已报道的模型发布](./ai-news-daily-2026-11-17.md)不是同一件事，本期只记平台上线和公司自己的演示。

官方写，促销价截止 11月22日：每百万输入 token 1.05 美元，缓存输入 0.0525 美元，输出 3.15 美元。官方还写，请求必须使用流式输出，思考模式默认开启，思考 token 计入输出。

他们把一份漏洞报告和 Tornado 仓库当时的全部 344 个文件、共 652,519 个 token 放进同一次请求，称模型在没有工具、也没有先做检索的情况下，72 秒后给出补丁，并且通过了维护者针对该漏洞写的测试，费用为 69 美分。这是公司自选的一个例子，补丁所针对的修复由维护者在 11月18日提交。

## 热榜上，漏洞挖掘技能包仍是当天增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月22日约 09:10 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。本期名单与昨日相同，数字已更新。

[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 当天约增加 1,803，总星约 16,080，增量最高，页面介绍为面向漏洞挖掘和外部红队的 Claude Code 技能包，已连续两日增量领先。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 1,006，总星约 206,215。其余条目和全表放在文末。

## X上顶尖AI大佬最近都说了什么

本期精选三位研究者或行业人士的个人原帖。时间均为北京时间。以下是个人观点或个人测试，不是已核验的事实。

Sebastian Raschka 是机器学习研究者，著有《Build a Large Language Model》。他在 11月21日 22:05 的[原帖](https://x.com/rasbt/status/2124142247285235990)中写：他相当认真地认为，如果没有中国的开源权重模型，美国的开源权重模型不会达到现在的水平，反过来也是如此；如果没有开源权重模型，专有模型也不会既好又便宜。他把这归结为竞争是一件好事。这是个人判断。

Nathan Lambert 是 Trillium Labs 的创始人兼主任，此前在 Ai2 共同负责 Olmo。他在 11月21日 22:47 的[原帖](https://x.com/natolambert/status/2124152733145923892)中发布一份关于后训练开放问题的幻灯片，并写明这在很大程度上是他在 Trillium Labs 的目标陈述，并不表示能同时做完所有项目。

他列出六块：面向上下文管理的工具环境设计、模型性格训练、开源强化学习环境、强化学习中的推理效率、强化学习的扩展定律，以及多模型系统协作的扩展定律。材料来自他近期在康奈尔的访问，并说会再录一版视频。

Simon Willison 是 Datasette 作者。他在 11月22日 03:06 的[原帖](https://x.com/simonw/status/2124217876777464269)中写，Gemini 4 Hydrogen 在 high 与 xhigh 思考强度上的差别非常显著。他给出的一次鹈鹕测试数字是：high 花费 3.99 美分、用了 5,311 个输出 token；xhigh 花费 23.61 美分、用了 31,477 个输出 token。这是他个人的一次对比，不能写成官方评测。他随后补了一张 Carbon、Neon 与 Hydrogen 在各推理档位上的对照表。

## 另外几则

**社区项目把 Inkling 2 Mini 的文本权重量化到约 5.4GB 等多档体积。** [ShinMegamiBoson/lookatmyquant](https://github.com/ShinMegamiBoson/lookatmyquant) 的说明写，作者将 Thinking Machines Lab 前一日发布的 Inkling 2 Mini 文本权重从 18.89GB 压成面向苹果芯片的多个 MLX 版本，其中最小一档为 5.38GB。作者自报，在自选的 GSM8K 子集和 HumanEval 等设置下，12.76GB 一档与未量化的 BF16 教师模型分数相同，5.38GB 一档则明显降低。这些数字和设置均来自项目说明，本期没有独立复现；热榜日也不等于该项目首次发布。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11月22日 09:10；当时页面 16 行；页面 HTML 抓取约 09:09:57）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 16,080 / +1,803 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [obra/superpowers](https://github.com/obra/superpowers) | 323,734 / +883 | Shell | 智能体技能框架与开发方法 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 62,081 / +769 | Python | 让各类软件可被智能体原生调用的 CLI 层 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 68,154 / +488 | Python | 两小时从零训练 64M 大模型 |
| [cursor/plugins](https://github.com/cursor/plugins) | 18,113 / +260 | TypeScript | Cursor 插件规范与官方插件 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 206,215 / +1,006 | TypeScript | 面向智能体的搜索、抓取与数据接口 |
| [nginx/nginx](https://github.com/nginx/nginx) | 32,735 / +189 | C | NGINX 官方开源仓库，与人工智能无直接关系 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 11,934 / +200 | C++ | 优化与部署人工智能推理的工具包 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 69,813 / +583 | HTML | 面向多种编码智能体的图表设计技能 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 72,011 / +560 | Python | 跨多个平台调研话题并汇总的智能体技能 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 11,445 / +326 | TypeScript | 面向 Stitch MCP 服务的智能体技能库 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 3,401 / +720 | Shell | 应用商店审核与合规的公开手册和预检 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 13,991 / +450 | Python | 面向 CI/CD 可靠性的开源智能体 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 76,311 / +574 | TypeScript | 开源知识库，与人工智能无直接关系 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 14,457 / +779 | Python | 下载工具，与人工智能无直接关系 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 12,868 / +683 | Python | 开源人工智能视频剪辑桌面工具 |

Lean 核验：社区博文时间为 2026-11-21 13:55，按 UTC 计为北京时间 21:55；原文含 “17 million lines of code”“We have full confidence that Alpöge's proof of the Riemann Hypothesis is correct”“We hereby certify that both the statement and the proof of the Riemann Hypothesis are correct.” 四项标准指向 https://xenaproject.wordpress.com/2026/11/12/and-the-proof-is-checked-in-lean/。Sutherland 页面标注 “Page last updated 2026-11-21 12:55 UTC. Results below are as of that time”。模块数为 175,187；公理为 propext、Classical.choice、Quot.sound。范围原文为 “Scope. "GRH" here means Dirichlet L-functions… Dedekind zeta functions, Hecke L-functions and automorphic L-functions in general are not among the statements that were checked.” 页面还写：Lean default kernel and Lean paranoid kernel on the export 当时为 running；“A passing check shows that the formal statements, as written in Lean against Mathlib's definitions, follow from the three standard axioms according to the kernels used.”

Together AI：博文页眉为 Published 11/21/2026，作者 Vipul Ved Prakash。样本模型与日期原文为 “The samples came from requests to the MiniMax M3, GLM-5.2, and Kimi K2.6 models, primarily on June 24, July 4, July 8, and July 14, 2026.” 金丝雀原文为 “Five of the credentials tested were canary credentials associated with a Dragos security experiment.” Dragos 官方博文日期为 November 19, 2026，已超出本期 48 小时窗口，正文只在 Together 通报提及金丝雀时作为背景，不作为本期新头条。

MedChemBench：官方页面日期 November 20, 2026。题目与材料为 “99 problems”“117 papers and patents”“761 distinct molecular structures”。分数原文为 “At the xhigh reasoning setting, GPT-6.2 Astra earned 84.5% of the available credit, compared with 83.3% for GPT-6 Astra, 82.0% for GPT-6.1 Sol, and 58.2% for GPT-5.6 Sol.” 结构项 95.4%、选择与预测约一半来自对 GPT-6 Astra 的说明。限制原文包括 “These results do not establish whether models can discover new drugs or improve laboratory decisions. Prior exposure to the published sources cannot be ruled out, and each response was a single attempt without tools, feedback, or new experiments.”

联合国会议：卫报首发 Sat 21 Nov 2026 08.15 EST，更新 11.36 EST。关键表述为未能确立 legally binding international treaty 的 negotiating mandate，改通过 “to elaborate by consensus” 一份 “may not carry any legal obligations” 的文书。Al Jazeera 标题与导语为同意在未来两年内 “elaborate” on a possible accord；主席 Julien Thoeni 称有国家拒绝 “negotiate”，商定文本改用 “elaboration” of an instrument。AP 页面在本期抓取时超时，未写入正文。

Qwen4-Max：Together 博文 Published 11/21/2026。促销价原文为 “Through November 22, 2026, it costs $1.05 per 1M input tokens, $0.0525 per 1M cached input tokens and $3.15 per 1M output tokens.” 演示为 Tornado “all 344 files, 652,519 tokens”，72 秒、69 美分，并写所选修复由维护者在 November 18, 2026 提交。约束原文包括 “Requests have to stream, and thinking is on by default, with thinking tokens counted as output tokens.”

LookAtMyQuant：README 写文本权重 18.89 GB，四档为 5.38、8.87、11.18、12.76 GB。5.38GB 一档自报 GSM8K 176/200（88.0%）、HumanEval 116/164（70.7%）。GitHub API 在北京时间约 09:15 读取时星数为 286。视觉塔在说明中为未改动的 637 MB BF16，与文本权重不是同一体积。

Hacker News（HN API 采集约北京时间 11月22日 09:10）：当时 “Lean verification of the Riemann Hypothesis” 约 816 分（item 50589618），“Inkling-2-Mini in 5.4 GB Memory” 约 346 分（item 50591853），“Verification files for the Lean proof of the Riemann Hypothesis” 约 92 分（item 50590441），“International UN talks on controlling use of autonomous weapons collapse” 约 31 分（item 50594564）。昨日已出现、仍在前排的条目包括 Alessandro Masullo GRH 宣布约 2,389 分（item 50579568）、Alpöge 原短文约 2,859 分（item 50574968）、Inkling 2 Mini 官方发布约 1,383 分（item 50581260）。首页另有与本期主题无直接关系的条目。Columbia 与 MIT 的 3SUM / APSP 论文在 arXiv 编号 2610.06783，属于 10 月工作，虽出现在今日 AIHOT 目录，本期不作为新头条。Simple Bench 关于 GPT-6.2 的讨论出现在当日热榜附近，但官网排行榜在静态页面中未能读出具体分数，本期不写入未核对数字。

X：三帖均经 X 公共读取接口直接读取原帖，并读取了超 280 字帖的全文。Sebastian Raschka 原帖时间 2026-11-21T14:05:51Z（北京时间 11月21日 22:05），帖 ID 2124142247285235990。Nathan Lambert 原帖时间 2026-11-21T14:47:31Z（北京时间 11月21日 22:47），帖 ID 2124152733145923892。Simon Willison 原帖时间 2026-11-21T19:06:22Z（北京时间 11月22日 03:06），帖 ID 2124217876777464269。François Chollet 窗口内有关于学习方法多样性和算力需求的长帖，因接口未返回完整长文，本期不引用其截断文本。Thomas Wolf 11月22日 03:52 有一条希望看到 Alpöge 与 Claude 对话轨迹的短帖，因与今日头条重复，未列入三人精选；其 11月20日关于 Hugging Face CDN 的帖已在上期用过。Karpathy、LeCun、Andrew Ng、Jason Wei、Noam Brown、Lilian Weng 在排除回复与转发后，窗口内无合格原帖。Jim Fan 祝贺 Alpöge 的帖已在上期说明中出现，不再选用。

来源覆盖：已读 AIHOT 11月22日页（每天 08:00 出刊，页面写第 215 期）、Hacker News 首页与官方 API、GitHub 热榜（北京时间 11月22日约 09:10 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以 Lean 社区联合声明、Sutherland 核验记录页、Together AI 官方博文、OpenAI 官方博文、《卫报》与 Al Jazeera / 法新社报道、Together AI 的 Qwen4-Max 博文，以及 lookatmyquant 项目说明为依据。AIHOT 今日头条仍以 Alpöge 宣布与 Masullo 草稿为主，这两件事已在 11月21日日报写过；本期改写社区核验这一新进展。Qwen4-Max 模型发布本身已在 11月17日写过，本期只写平台上线。

</details>
