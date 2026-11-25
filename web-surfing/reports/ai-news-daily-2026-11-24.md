---
title: "AI 行业日报 · 2026-11-24"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-24"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---
# AI 日报 · 2026年11月24日

今天先看三件事。

- 英伟达董事会 11月23日宣布，黄仁勋即刻复任总裁、首席执行官并重回董事会，董事会称一致投票通过。官方声明写明，决策过程中听取了美国政府高层意见，并据此认为复任不构成国家安全风险；同时强调，此前因他据报成为外国情报行动目标而成立的独立董事调查，仍将进行到底。这是公司声明和董事会判断，不是调查结论。

- 智谱旗下 Z.AI 11月23日发布旗舰模型 GLM-5.4。官方称这是该公司首个采用 Loop Transformer 架构的旗舰模型：把 GLM-5 基座中的 28 层共享权重循环执行两轮，规模按官方说法约为 750B 参数。公司宣称其智能水平可与 2 万亿至 3 万亿参数的模型相比，并称由此开启“泛化编程”。这些都是厂商自报，不是独立评测结论。

- 俄勒冈州总检察长 Dan Rayfield 与弗吉尼亚州总检察长 Jay Jones，于 11月23日（美国日期周一）分别起诉 SpaceX，指控其忽视行业通行防护，并虚假宣传 X 平台与 Grok 的安全性。诉讼焦点是 Grok Imagine 生成非自愿色情深伪等内容。这是尚未判决的指控。X 安全团队随后发声明，称已采取措施，并指相关行为违反服务条款。

## 英伟达董事会宣布黄仁勋即刻复任总裁兼首席执行官

[英伟达 11月23日新闻稿](https://nvidianews.nvidia.com/news/nvidia-board-reinstates-jensen-huang-as-president-ceo-and-board-director)写明：经董事会一致投票，黄仁勋即刻复任总裁、首席执行官并重回董事会。声明说，董事会与他进行了一系列讨论和会面后，对其坦诚和领导能力感到满意。董事长 Harvey Jones 将继续任职；临时首席执行官 Colette Kress 继续担任首席财务官。

声明还写，决策过程中听取了美国政府高层意见，并据此“有信心”认为复任不构成国家安全风险。这是董事会基于其所称政府意见作出的判断，不是已公布的调查结论。

同一份声明重申：鉴于近期有关黄仁勋成为外国情报行动目标的报道，董事会已成立全部由独立董事组成的委员会并聘请独立律师；该调查将进行到底，黄仁勋表示完全支持并愿意配合。董事会还写明，近期已成立国家安全与出口管制委员会，正在招聘向提名与公司治理委员会汇报的首席合规官，并将继续配合正在进行的政府调查和问询。

[CNBC 报道](https://www.cnbc.com/2026/11/23/nvidia-jensen-huang-ceo.html)称，消息公布后英伟达股价收涨 31%。这是该社给出的收盘涨幅，稿中未同时给出当日收盘价。同一篇还引述特朗普当天对 CNBC 的谈话：他曾“直接和间接”与董事会沟通，称黄仁勋“没有做错事”，并说周日与黄仁勋通了话，要求对方承诺“努力工作”。CNBC 另引述匿名人士称，政府官员上周晚些时候向董事会通报“没有违反国家安全法律”，且股价下跌加快了复任讨论。这些来源要求匿名，且未被授权公开讲话，不能当成官方确认。

[TechCrunch](https://techcrunch.com/2026/11/23/trump-endorses-jensen-huangs-return-to-nvidia-says-us-has-no-evidence-of-wrongdoing/)刊出了特朗普当天在 Truth Social 上的完整声明。其中写：美国政府“没有理由认为”黄仁勋回归构成国家安全风险，并称司法部长 Todd Blanche 已确认政府“并不掌握他从事任何非法行为的证据”。该报道同时指出，Blanche 本人尚未就此案发表正式声明。总统表态不能写成司法结论。[11月23日日报](./ai-news-daily-2026-11-23.md)曾记录财政部长贝森特表示，一周前要求英伟达在 10 天内就出口合规作出的答复当时仍未收到。本期未读到他对此次复任的新表态。

CNBC 还写，马萨诸塞州民主党参议员 Elizabeth Warren 当天发表声明，认为让黄仁勋回归是“不计后果的决定”，并称他、公司高管和董事会仍应就出口管制合规向国会作出说明。稿件记录的既定行程是：黄仁勋定于 12月1日接受众议院外交事务等相关委员会闭门询问，总法律顾问 Tim Teter 定于 12月2日出面，参议院银行委员会主席 Tim Scott 则称黄仁勋将于 12月3日作为唯一证人公开作证。这些安排在复任前已定，是否调整，本期未见其律师的说明。

## 智谱发布 GLM-5.4：官方称首次用循环 Transformer 做“泛化编程”

[Z.AI 官方博文](https://z.ai/blog/glm-5.4)标注日期为 2026-11-23。官方把 GLM-5.4 定为该公司首个建立在 Loop Transformer 上的旗舰模型，做法是把 GLM-5 基座中的 28 层循环执行两轮，试验规模写为 750B，以便在参数量不变的情况下加深推理。为控制部署成本，文中列举了三项改动：按 token 调节的门控渐进更新、跨循环共享再加滑动窗口的混合 KV 缓存，以及第二轮复用第一轮稀疏注意力索引。官方称，在 100 万上下文长度下，额外循环只需增加一个滑动窗口的 KV，而不是整段上下文缓存。

公司还写，曾在 10 亿、40 亿、300 亿和 750B 基座上逐步验证，并在与 750B 基座同结构的 300 亿模型上做了等参数对照：总训练算力大约多 10% 时，循环版本出现收益；在 GPQA-Diamond、MMLU-Pro 等基准上，平均输出长度下降 10% 到 14%。官方把更大收益归到数学、科学推理和长上下文任务。这些都是公司自己的实验叙述。

官方宣称，GLM-5.4 的智能水平可与 2 万亿至 3 万亿参数的模型相比，并展示用代码生成和编辑视频、制作完整游戏、在 FreeCAD 中做六轴机械臂建模等演示。它也写明局限：模型容易陷入过长的“马拉松式思考”。推理速度的自报数字是：低峰时段最高约每秒 200 个 token，高峰时段约每秒 70 到 80 个 token。

[开发者文档](https://docs.z.ai/guides/llm/glm-5.4)写明，该模型已向全部 GLM Coding Plan 用户开放，按周配额方案的额度是 GLM-5.3 的 1.5 倍；模型 API 要等安全评估完成后才会提供。上下文长度写为 100 万，最大输出 12.8 万 token。博文还说，计划在完成必要的安全加固后负责任地开源权重，因此目前不能把它写成已经开放权重。

## Anthropic 推出 Claude Ship 测试版，可按仓库策略走完审查、修复和批准

[Claude 官方文章](https://claude.com/resources/articles/introducing-claude-ship)标注日期为 2026年11月23日。Claude Ship 今天以测试版推出，用来审查拉取请求、推动修复，并依据团队写进仓库的策略决定哪些变更可以批准。它由已经正式可用的 Code Review，以及仍在测试的 PR Steward 和 Claude Approvals 组成。

按官方说明，PR Steward 会处理失败的持续集成、合并冲突，以及来自 Code Review、其他工具或同事的意见，但被设计为不负责批准或合并。Claude Approvals 读取仓库中的策略文件，允许的常规变更可由它批准，更高风险的变更仍可要求人工签字。官方建议多数客户先用只观察模式，再考虑把它纳入分支保护。开发者也可在 Claude Code 里运行 `/ship`，推送代码并打开拉取请求；最终能否合并，仍取决于个人权限和仓库分支规则。

官方自报：在 Claude Code 团队内部，Claude 的审查只是更广流程中的一层；6 月到 9 月，合并的拉取请求增加了一倍以上，被回退的比例下降超过 40%。这是该公司自己的内部对照，不能直接当成 Ship 整套产品的外部效果。可用范围是 Claude Team 和 Enterprise 方案，且针对 GitHub 上的仓库。用量按 token 计费。官方写明，采用零数据保留、HIPAA 配置或客户管理加密密钥的组织不能使用该功能。符合条件的 Enterprise 组织可在领取后 30 天内使用至少 1 万美元额度，领取截止日为 2027年1月15日，具体以条款为准。

## 俄勒冈州与弗吉尼亚州起诉 SpaceX，指 Grok 深伪防护不足

[The Verge 11月23日报道](https://www.theverge.com/ai-artificial-intelligence/1040255/x-grok-ai-deepfakes-oregon-virginia-lawsuit)写，俄勒冈州总检察长 Dan Rayfield 与弗吉尼亚州总检察长 Jay Jones 当天分别提起相似诉讼，指控 SpaceX 违反州消费者保护法律：忽视行业通行防护，并虚假宣传 X 平台和 Grok 功能的安全性。两案都寻求经济赔偿。这是起诉主张，不是已认定的违法事实。同一篇报道在介绍产品背景时写，马斯克此后已将 xAI 与 SpaceX 合并；这是该媒体的说法，本期未核对其正式交割文件，但有助于理解为何被告写成 SpaceX。

报道引述弗吉尼亚州诉状称，马斯克被指有意忽视围绕人工智能色情深伪的担忧，反而把它看成盈利机会，并把 Grok 薄弱的防护描述为“不是失败，而是功能”。Jones 的新闻声明还说，xAI 和 X 曾向消费者宣称他们受到保护，但该工具仍被用于制作和传播非自愿私密影像、性化图像以及涉及儿童的性虐待材料。这些表述来自检方，本期未逐份核对诉状原文。

报道回顾的产品背景是：xAI 在 2025年8月为 Grok Imagine 推出可生成色情内容的 “spicy” 模式；2026年1月又允许 X 用户在无需原帖作者同意的情况下编辑任意图片。The Verge 称，xAI 此后曾把部分能力放到付费墙后，并拦截某些性化请求，但该媒体自己的测试认为，这些限制对阻止性化深伪作用有限。这是该媒体的测试判断。

诉讼公布后，X 安全团队发表声明，称对试图生成涉及未成年人的性内容的用户采取了相应措施，并指相关行为故意违反服务条款、积极规避防护。声明还说，防护旨在拒绝生成未成年人或真实人物的露骨图像，并会在生成前后用分类器检查提示词和输出。公司抗辩同样有待法庭检验。

## OpenAI 与 Cisco 开源 Shirudo，用于在补丁到位前保护运行中的 Linux 系统

[OpenAI 11月23日发布说明](https://openai.com/index/introducing-shirudo/)宣布，与 Cisco 推出开源运行时 Shirudo，帮助团队在修补漏洞的同时保护正在运行的 Linux 系统，而不必等待补丁完成或重启服务。代码发布在 [GitHub](https://github.com/shirudo-dev/shirudo)，许可证为 BSD 2-Clause，其中的 BPF 程序采用 BSD 与 GPL 双许可。

官方称，Shirudo 使用 eBPF，在操作系统内的特定位置运行小程序，以观察可疑活动并施加针对性保护。说明列出的能力包括：在系统继续运行时用 eBPF 盾挡住脆弱路径，并可先观察再强制执行；让代理去调查漏洞、编写盾并对照利用和真实负载做验证，但部署仍由安全团队决定；加载前对盾做加密签名和校验；并用可信平台模块（TPM）记录保护被加载或移除的证据。

作为例证，官方写到一次受控测试：团队用 Codex 生成的盾，在无需重启的情况下，挡住了针对正在运行的 Elasticsearch 服务的 Java4Shell 利用尝试。该盾给 Java 的 Base64 解码器加了输入检查，并直接附加到该进程。这是 OpenAI 与合作方自己的演示，不是第三方复现报告。

说明也写明更远期的目标：希望防御者和人工智能代理能够更快定位受影响系统、验证防护，并在不中断负载的情况下部署盾。这是产品方向，不是已经普遍落地的效果。采集时，Hacker News 上这条链接的讨论还很少，重要性不能用当时的热度衡量。

## 热榜上，漏洞挖掘技能包仍是当天增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月24日约 09:13 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 当天约增加 2,029，总星约 19,801，增量仍最高。页面介绍为面向漏洞挖掘和外部红队的 Claude Code 技能包，已连续多日增量领先。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 924，总星约 207,938。[obra/superpowers](https://github.com/obra/superpowers) 约增加 840，总星约 325,082。当天增量第二高的是 [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3)，约增加 1,087，总星约 16,333，页面介绍为下载器，与人工智能没有直接关系。其余条目和全表放在文末。

## X上顶尖AI大佬最近都说了什么

本期精选三位研究者或行业人士的个人原帖。时间均为北京时间。以下是个人观点或个人研究观察，不是已核验的事实。

Yann LeCun 是 AMI Labs 创始人兼主席、纽约大学教授，也是图灵奖得主，简介写明曾任 Meta 首席人工智能科学家。他在 11月23日 01:06 的[原帖](https://x.com/ylecun/status/2124550037912920090)中，回复他人对 Dario Amodei 听证言论的转述时写道：Dario 自 GPT-2 以来的说辞，一直是夸大危险，好让开放模型被定为非法，从而由“他”保持控制；他离开 OpenAI，是因为无法取得控制。他把这比作奥斯曼帝国禁止阿拉伯文印刷，以保持对教义的控制，并称这会阻止民众自由接触多样知识，是一种新的“中世纪蒙昧”。

这是个人批评，不是对听证原话或公司政策的核验。公开接口返回的正文在句中截断，完整表述来自同一条帖子的公开页面标题，与 Hacker News 讨论中的引文一致。

François Chollet 是 Keras 的作者，也是 ARC-AGI 与 ARC Prize 的联合创始人。他在 11月24日 03:03 的[原帖](https://x.com/fchollet/status/2124942035841151448)中写：他所见过的智能系统都恰好有两个适应时间尺度。第一个是即时的情境建模，在人类那里对应流体智力，在现代人工智能里则体现为生成推理链或生成程序。配图把第二个尺度称为训练阶段：从以往经验中提取可复用的抽象；推理阶段则是把这些抽象临时组装成一次性的情境模型。这是他的概念整理，不是新的实验结果。

Ethan Mollick 是沃顿商学院研究人工智能的教授。他在 11月24日 04:56 的[原帖](https://x.com/emollick/status/2124970360445796544)中，评论 a16z 与 The Prompting Company 对购物代理的测试时写：在他们自己的人工智能购物研究里，代理偏好中的每一种模式都很容易崩溃——只要改变模型看到的网站顺序、先与模型交谈，或改一条标题，建议就会变。随后又补充，不同模型的表现也不一样。这是研究者的观察，不能外推成所有购物代理的定律。

## 简讯

AI Digest 中文版仍显示停更于 2026年10月23日，本期只核验一次，未重试。AIHOT 第 217 期以黄仁勋复任为头条，与已回读的英伟达官方新闻稿一致。

[Google DeepMind 11月23日博文](https://deepmind.google/blog/finding-faster-quantum-algorithms-with-agents-and-formal-verification/)说，研究团队用多组 Gemini 4 智能体改进已知量子算法，并用 Lean 为结果做形式化证明。官方自报：惯性约束聚变相关电路的计算成本降至约 1/11.8，纠错量子比特由 5,650 个降到 4,338 个；一种光敏分子的模拟成本降至约 1/8；与药物代谢相关的细胞色素 P450 模拟改进约 2.5 倍，量子比特由 481 个降到 333 个；对 Grover 算法的一种具体实现给出 2.57 倍加速，对 arcsin 例程给出 290 倍加速。

博文同时写明，这些算法若用于科学模拟，所需资源仍超过第一批纠错量子计算机大概能够提供的水平。数字来自官方自报，Lean 库已开源。

[Anthropic 11月23日研究文章](https://www.anthropic.com/research/working-with-ai)基于对 58 家企业客户的 66 次面对面访谈。作者写：几乎看不到由人工智能自动化直接导致的国内裁员；约三分之二的受访公司报告因人工智能而减少招聘，10 家报告因此增加招聘；9 家提到削减外包软件开发、客服、法律或后台职能，其中不少原本已经离岸。文章把价值主要归为扩大产出而非削减成本，并强调高价值用法往往伴随岗位和流程重组。样本全是 Anthropic 的企业客户，访谈内容为当事人自述，不能当成对整体就业市场的统计结论。

[Google 搜索官方博文](https://blog.google/products-and-platforms/products/search/google-search-personal-intelligence-apps/)11月23日宣布，用户可选择把 Google Wallet 接入 AI Mode 中的 Personal Intelligence，Drive 和 Gemini 应用将在未来数周跟进。官方强调需用户选择加入，并且接入 Wallet 后只能读取账户信息，不能转移、管理或投资资金。a16z 当天的[文章](https://www.a16z.news/p/welcome-to-the-b2a-economy-how-agents)则写，该机构与 The Prompting Company 测试了多个购物代理，覆盖 1,270 条提示词和 11,307 次完整运行。这是投资机构与合作方的测试总结，不是独立基准。

AIHOT 还提到 Claude 插件、面向日常对话的 GPT-6.2 Sol、英国 AISI 红队论文和 Figma agent 扩展等条目；其中 GPT-6.2 Sol 一条的聚合来源是个人转发，本期未找到可独立核对的 OpenAI 官方说明，故不作为头条。Hacker News 上也出现了 Anthropic 形式化数学仓库中 “VP ≠ VNP over Every Field” 的讨论，以及 11月7日修订的 Latent Introspection 论文，后者超出本期主要窗口，不作为新进展。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

采集时点均为中国时区 UTC+8。AIHOT 11月24日页在 09:13:49 读取，HTTP 200，页面写第 217 期、每天 08:00 出刊。GitHub 热榜、Hacker News 首页与官方 API、AI Digest 中文版均在约 09:13:53 读取。英伟达新闻稿、Z.AI 博文与文档、Claude Ship 文章、OpenAI Shirudo 说明、The Verge、CNBC、TechCrunch、DeepMind 与 Anthropic 研究原文，以及个人 X 原帖，随后在 09:14 至 09:17 核对。热榜数字以 09:13 的页面为准。

Hacker News 首页在 09:13 的前若干条及当时点数大致为：Nvidia Reinstates Jensen Huang as CEO（2,055 分，链向 CNBC）、Ladybird is now in alpha（1,397 分）、Dario is hyping the dangers so OSS models are illegal and he stays in control（1,106 分，链向 LeCun 原帖）、GLM-5.4（1,047 分，链向 Z.AI 博文）、Free alternative TV network built from the Internet Archive's forgotten videos（941 分）、Per Arm's request, this site will be discontinued on 4 December 2026（830 分）。与人工智能更直接相关、但当时分数较低的还有 VP ≠ VNP over Every Field（216 分）和 Shirudo（19 分）。点数会变动，这里只记录采集时的首页快照。

GitHub 热榜全表（总星 / 当天增加，均为 09:13 页面原样）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面说明 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 19,801 / +2,029 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 16,333 / +1,087 | Python | 下载器，与人工智能没有直接关系 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 207,938 / +924 | TypeScript | 为代理提供搜索、抓取和数据接口 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 14,412 / +907 | Python | 开源人工智能视频剪辑工具 |
| [obra/superpowers](https://github.com/obra/superpowers) | 325,082 / +840 | Shell | 代理技能框架与软件开发方法 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 69,466 / +828 | Python | 从零训练小型语言模型的教程项目 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 73,448 / +797 | Python | 汇集近期公开讨论并做综述的代理技能 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 63,658 / +790 | Python | 让各类软件更便于代理通过命令行使用 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 4,982 / +761 | Shell | 应用商店常见拒审模式与提交前检查 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 70,979 / +620 | HTML | 给编程代理用的图表设计技能 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 77,403 / +595 | TypeScript | 开源知识库 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 14,844 / +436 | Python | 面向持续集成可靠性的开源代理 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 12,300 / +422 | TypeScript | 与 Stitch MCP 配合的代理技能库 |
| [cursor/plugins](https://github.com/cursor/plugins) | 18,812 / +397 | TypeScript | Cursor 插件规范与官方插件 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 12,285 / +184 | C++ | 推理优化与部署工具包 |
| [nginx/nginx](https://github.com/nginx/nginx) | 33,057 / +174 | C | 官方 Nginx 源码，与人工智能无关 |

来源覆盖：已读 AIHOT 11月24日页（每天 08:00 出刊，页面写第 217 期）、Hacker News 首页与官方 API、GitHub 热榜（北京时间 11月24日约 09:13 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以英伟达官方新闻稿、Z.AI 官方博文与开发者文档、Claude 官方文章、OpenAI 官方说明、The Verge、CNBC 与 TechCrunch 报道为依据。DeepMind 量子算法博文和 Anthropic 企业访谈为官方当日发布，放在简讯。聚合页提到的 Claude 插件、GPT-6.2 Sol 日常对话版、AISI 红队论文和 Figma agent 扩展，未在本期完成可独立核对的官方日期与原文复核，不作为头条。Latent Introspection 论文的 arXiv 第三版日期为 2026年11月7日，超出本期主要窗口。Wiz 关于 ARTEX 的研究此前已有报道，不作为新新闻。Foreign Policy 关于黄仁勋回归的评论为付费观点文章，正文不以它作事实依据。

</details>
