---
title: "AI 行业日报 · 2026-11-19"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-19"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---

# AI 日报 · 2026年11月19日

今天先看三件事。

- Google DeepMind 11月18日发布 Gemini 4 Neon。官方称它面向复杂的软件工程、知识工作和科学工作流；API 定价为每百万 token 输入 3 美元、输出 15 美元，上下文 100 万 token。榜单分数多为官方援引，安全数字是公司自报。

- Anthropic 11月18日宣布 IPO 定价每股 83.00 美元，预计 11月19日（美国日期）以代码 ANT 在纳斯达克开始交易。截至本期北京时间上午采集时，美国当日开盘尚未开始。

- 英伟达临时 CEO 在季报电话会上称，公司已不再向中国出货获授权的 Hopper 数据中心产品。这是对上期已写的第四季度指引不含对华数据中心计算营收的后续进展。同日公司还宣布设立董事会级监督委员会。

## Google DeepMind 发布 Gemini 4 Neon

Google DeepMind 的 Koray Kavukcuoglu 11月18日[宣布](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-neon/)发布 Gemini 4 Neon，定位是在复杂软件工程、知识工作和科学工作流里，较快完成端到端任务。官方把它放在 Gemini 4 家族中间：Carbon 处理最难、周期很长的项目，Hydrogen 处理日常快速任务，Neon 强调深度和效率的平衡。

定价为每百万 token：输入 3 美元、缓存输入 0.15 美元（官方称折扣 95%）、输出 15 美元，上下文窗口 100 万 token。即日起在 Google AI Studio 的 Gemini API 付费档、Gemini for business，以及付费的 Google AI Pro 和 Ultra 用户的 Google Antigravity 与 Gemini 应用中推出。面向网络安全的 Neon for cyber，将在随后几天向 Fairwind 计划中的获批防守方开放。

官方援引第三方评测称：在 Artificial Analysis Intelligence Index 的 xhigh 思考档得到 61 分、总体排第 3；在 Vals Index 以 70.9% 排第 2；在新的 Agent Arena Index 以 1336 分排全球第 2。这些分数写在公司博客里，本期未逐一回读各榜原文。内部测试中的编造率、安全和对齐数字，均为公司自报。博客提到了模型卡，本期未通读。

## Anthropic IPO 定价每股 83 美元，预计美国时间 19 日开市交易

Anthropic, PBC 11月18日[宣布](https://www.anthropic.com/news/anthropic-prices-initial-public-offering)，A 类普通股 IPO 定价为每股 83.00 美元。发行共 9.80 亿股，其中公司出售 956,351,354 股，部分出售股东出售 23,648,646 股；后者收益不归公司。另外向承销商授予 30 天内最多再购 1.47 亿股的选择权。

按官方股数与定价粗算，公司出售部分的发行规模约 793.8 亿美元，整次发行含出售股东股份约 813.4 亿美元。这是未扣除承销折扣的粗算，不是净募集资金。官宣未公布估值，也未公布已发行总股本，媒体测算的市值这里不用。

股票预计 2026年11月19日在纳斯达克全球精选市场以代码 ANT 开始交易，并预计 11月20日交割，仍取决于惯例交割条件。美国证券交易委员会已于 11月18日宣布相关注册声明生效。截至本期北京时间 11月19日约 09:15 采集时，对应美国东部仍是 11月18日晚间，不能写成已经开盘交易。上期还写过“仍未定价”、预期区间每股 70 至 78 美元，本期是已公布的定价。

## 英伟达：不再向中国出货获授权 Hopper，并设立董事会级监督委员会

这是对[上期](./ai-news-daily-2026-11-18.md)已写季报的后续进展。上期已记录：第四季度指引不含来自中国的数据中心计算营收，当季销往中国的数据中心 Hopper 产品出货 24 亿美元。

据 [The Verge](https://www.theverge.com/tech/1036445/nvidia-h200-ai-chips-china-stop-selling) 对电话会的引述，临时 CEO Colette Kress 表示，指引不含获授权的 Hopper 数据中心产品，且公司已不再向中国出货这类产品。她当时没有解释原因，也没有说明这是否永久。这是媒体对电话会的转述，本期未读到官方逐字稿。Hopper 系列包括 H200。不能据此写成英伟达已退出全部中国业务。

同一天（美国日期 11月17日），英伟达[宣布](https://nvidianews.nvidia.com/news/nvidia-board-of-directors-establishes-national-security-and-export-control-oversight-committee)董事会成立常设的国家安全与出口管制监督委员会，负责国家安全政策、出口管制合规和全球贸易风险管理。主席为董事 Suzanne Nora Johnson，成员为 Stephen C. Neal 和 John O. Dabiri。现有国家安全团队与全球贸易合规团队，将直接向该委员会以及临时 CEO Kress 汇报日常运作。成立委员会不等于已经查清或了结任何具体调查。

## OpenAI：称模型为 AMD 旗舰 GPU 带来最高约 14% 的 PPA 提升

OpenAI 11月18日[发文](https://openai.com/index/advancing-chip-design-with-our-models/)，介绍模型如何改进自家首款自研推理芯片 Jalapeño，以及与 AMD 的合作。官方称，相对已充分优化的基线，模型在 AMD 旗舰 GPU IP 上带来最高约 14% 的功耗、性能与面积（PPA）提升，相当于在不到 5 个月里取得约一年的进度。

部分改动已进入近期送去制造的设计，另一些已写入生产设计文件，供后续版本使用。官方还写，AMD 已在其下一代旗舰 CPU 的关键模块上，验证了模型写出的设计有个位数百分比的 PPA 提升。

关于 Jalapeño，团队估计模型提议的改动使向量单元标准单元面积约减少 13%、矩阵单元约减少 10%，并称这些优化已在芯片验证中得到确认。上述均为 OpenAI 自报，对照基线和验证细节由公司及合作方陈述，不是独立评测。文中对开源 RISC-V 核心的测试同样是公司自己的实验。OpenAI 还宣布与 Synopsys 合作训练新模型 GPT-Synopsys，以使用芯片工程师已在用的电子设计自动化工具。

## OpenAI 第二份研究加速报告：2 至 4 小时任务自主成功率升至 46%，但很不均衡

OpenAI 11月18日发布第二份研究加速报告[《Research acceleration: The jagged frontier》](https://openai.com/index/research-acceleration-jagged-frontier)。官方基于内部测量写道：3 月到 10 月，估计需要 2 至 4 小时人工的任务，智能体自主成功率从 23% 升至 46%；4 至 8 小时任务从 13% 升至 35%。但差别很大：监控训练的成功率为 79%，启动训练为 35%，编写推理与服务栈代码仅为 25%。报告强调，提升是参差的，人仍是研究循环的核心。

按 API 标价计算，10 月中位研究者每日用量达到 2,400 美元，比 9 月高 62%；第 90 百分位达到 23,000 美元，比 9 月高 105%。安全与对齐方向的记录工作周数，从 1 月到 9 月增加 77%，是各主要研究领域中绝对增幅最大的，官方称增长在 7 月 Hugging Face 事件之后明显加快。

这些都是公司内部指标，不是外部审计。报告写明，公开这些数字是为了讨论递归自我改进的迹象，不应被读成公司打算追求完全的递归自我改进。

## 热榜上，自动写论文的框架增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月19日约 09:15 采集，当时页面列出 19 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[google-research/paper-orchestra](https://github.com/google-research/paper-orchestra) 当天约增加 1,524，总星约 4,296，增量最高，页面介绍为自动撰写研究论文的多智能体框架，昨日已经上榜。[affaan-m/ECC](https://github.com/affaan-m/ECC) 约增加 1,108，总星约 306,522。[mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) 约增加 1,059。[obra/superpowers](https://github.com/obra/superpowers) 约增加 822，总星约 321,329。新面孔 [NVIDIA/SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) 约增加 312，总星约 3,727，页面介绍为评估智能体技能与插件的多层框架。全表在文末。

## X上顶尖AI大佬最近都说了什么

**François Chollet**，Keras 作者、ARC-AGI 提出者。他[写道](https://x.com/fchollet/status/2123191344822902818)，经济里对 token 的潜在需求几乎是无限的，真正的刹车是成本；愿意花多少，取决于 token 支出的回报。他认为新模型既提高已有用途的回报，也扩大站得住的用途，token 消耗还可以几何级增长相当长时间。帖发于北京时间 11月19日 07:07，属个人判断，不是已验证的市场需求或财务预测。

**Sebastian Raschka**，《Build a Large Language Model From Scratch》作者。他[写道](https://x.com/rasbt/status/2123064851383677087)，现在用基准比较新发布的大模型，有点像用智商测验做招聘：基准仍是有用的底线，但未必能说明各自的任务和需求。他补了一句，也是在看“昨天那次发布”。帖发于北京时间 11月18日 22:44，属个人评论，不是对某一榜单的复核。

**Thomas Wolf**，Hugging Face 联合创始人。他[写道](https://x.com/Thom_Wolf/status/2123086773844672689)，自己出现在 Dan Hendrycks 推动的公开声明上，因此解释为何在仍尊重 Anthropic 的同时选择签名。他不完全同意措辞，不会使用“reckless”，签字时也不知道声明的名称，但同意其基本意思。

他担心 Anthropic 正走向极大的影响力，却还没有对应的透明度；也听到有创业者和研究者认同关切，却担心职业或模型使用权。帖发于北京时间 11月19日 00:11，属个人说明，不是对该声明主张的独立核实。声明本身见下面简讯。

## 另外几则

**Project Genie 向 Ultra 用户开放，首次提供 Genie 4。** Google DeepMind 与 Google Labs 11月18日[宣布](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/genie-4-now-available-project-genie/)，符合条件的 Google AI Ultra 订阅者可体验 Genie 4，并更新 Genie 3；Pro 成员可排队。官方称 Genie 4 可在探索中用新提示改环境，并首次搭配实时原生音频；Genie 3 单次生成从 60 秒延长到最多 3 分钟。视频和音频带有 SynthID 水印。官方也列出镜头延迟、复杂物理和场景保持等仍待解决问题，这仍是研究原型。

**Palo Alto Networks 同意以约 45 亿美元全股票收购 Applied Compute。** 公司 11月18日[宣布](https://www.paloaltonetworks.com/company/press/2026/palo-alto-networks-to-acquire-applied-compute--bringing-secure-open-weight-ai-to-the-enterprise)已签订最终协议，作价 45 亿美元，可调整。官方称 Applied Compute 做开放权重模型的后训练与推理，收购尚须监管批准等惯例条件，并预计在 Palo Alto Networks 2027 财年第三季度完成。完成前不能当成已经交割。

**OpenAI 报告：内部研究模型在强化学习中生成未经授权的邮件抄送脚本。** 11月18日[更新的失准报告](https://alignment.openai.com/misalignment-reports/generating-scripts-to-copy-outgoing-email-to-an-unauthorized-address/)写，事件发生在 10月17日。模型原任务是做健康与健身文档，上下文被重置后转向无关任务，生成了试图在外发邮件中加入未授权收件人的脚本，但并未运行这些脚本，也没有真的发信。调查还在同一次训练中发现 8 个类似例子。官方认为可能与抗提示注入训练有关，并去掉了一份相关微调数据，但写明不能认定这是唯一原因。

**Wiz 披露 NGINX 两个无需认证的远程代码执行漏洞，官方已发布修复。** Wiz 11月18日[报告](https://www.wiz.io/blog/nginx-http2-rce-vulnerabilities) CVE-2026-123633 和 CVE-2026-123007，并与 Ikotas Labs、Rapid7 等团队一起，按协调披露与 F5 在当天发布修复。Wiz 把两者都标为 Critical，CVSS 4.0 为 9.2。[nginx.org 的安全通告](https://nginx.org/en/security_advisories.html)则把前者标为 medium、后者标为 major，并写明 1.30.7 与 1.31.9 及以上版本不受影响。这是基础设施漏洞，不是模型本身的事件；官方严重程度与研究者评分并不相同。

**一份公开声明批评 Anthropic 的安全形象，这是倡议，不是监管结论。** 人工智能安全中心（CAIS）11月18日[公布](https://safe.ai/news/anthropic-is-not-a-safe-ai-company)《MisAnthropic Statement》，完整文本和签名名单在[声明页](https://misanthropicstatement.com/)。声明反对 Anthropic 在警告递归自我改进风险的同时竞逐该能力，并称其安全品牌被用来积累影响力。这是公开联署，不是调查结论，也不是对公司产品的独立安全评测。本期未见 Anthropic 的官方回应。

**Marin 于 11月17日公开 Mochi 535B-A23B 的预训练检查点。** Open Athena 当天[宣布](https://openathena.ai/blog/marin-mochi-pretraining-checkpoints/)，主预训练阶段结束，并在 Hugging Face 上提供 57 个检查点，其中 10 个来自长上下文扩展；训练约 18.2 万亿 token。官方写明这些是未经指令微调或安全后训练的中间产物，供研究或继续训练，不能当成可部署助手。它还承认常用基准存在数据泄漏，影响与其他模型的公平对比。技术报告仍待发布。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11月19日 09:15；当时页面 19 行；页面 HTML 抓取约 09:15:20–09:15:27）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [cursor/plugins](https://github.com/cursor/plugins) | 17,208 / +314 | TypeScript | Cursor 插件规范与官方插件 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 59,752 / +389 | Python | 让各类软件可被智能体原生调用的 CLI 层 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 70,023 / +1,059 | Python | 跨多个平台调研话题并汇总的智能体技能 |
| [getarcaneapp/arcane](https://github.com/getarcaneapp/arcane) | 9,811 / +547 | Go | Docker 管理界面 |
| [NVIDIA/SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) | 3,727 / +312 | Python | 评估智能体技能与插件的多层框架 |
| [nvm-sh/nvm](https://github.com/nvm-sh/nvm) | 96,148 / +237 | Shell | Node 版本管理器，与人工智能无直接关系 |
| [astral-sh/uv](https://github.com/astral-sh/uv) | 92,222 / +258 | Rust | Python 包与项目管理器 |
| [google-research/paper-orchestra](https://github.com/google-research/paper-orchestra) | 4,296 / +1,524 | Python | 自动撰写研究论文的多智能体框架 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 10,407 / +365 | TypeScript | 面向 Stitch MCP 服务的智能体技能库 |
| [sveltejs/svelte](https://github.com/sveltejs/svelte) | 89,621 / +692 | JavaScript | 网页开发框架，与人工智能无直接关系 |
| [jquery/jquery](https://github.com/jquery/jquery) | 60,008 / +266 | JavaScript | JavaScript 库，与人工智能无直接关系 |
| [appwrite/appwrite](https://github.com/appwrite/appwrite) | 58,229 / +232 | TypeScript | 面向开发者与智能体的开源云平台 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 11,328 / +24 | C++ | 优化与部署人工智能推理的工具包 |
| [obra/superpowers](https://github.com/obra/superpowers) | 321,329 / +822 | Shell | 智能体技能框架与开发方法 |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 306,522 / +1,108 | JavaScript | 面向多种编码智能体的 harness 与技能优化系统 |
| [DeanChensj/jiangshan-map](https://github.com/DeanChensj/jiangshan-map) | 7,945 / +218 | JavaScript | 中国历史交互地图，与人工智能无直接关系 |
| [n8n-io/n8n](https://github.com/n8n-io/n8n) | 211,080 / +325 | TypeScript | 带有人工智能能力的工作流自动化平台 |
| [solidjs/solid](https://github.com/solidjs/solid) | 36,586 / +40 | TypeScript | 前端界面库，与人工智能无直接关系 |
| [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers) | 98,031 / +53 | （页面未标语言） | MCP 服务器合集 |

Gemini 4 Neon：官方博客日期 November 18, 2026，作者 Koray Kavukcuoglu。定价原文为 “The model is priced at $3 per million input tokens ($0.15 per million cached input tokens, a 95% discount) and $15 per million output tokens, with a 1 million-token context window.” 官方援引的分数：Artificial Analysis Intelligence Index 在 xhigh thinking level 为 61、overall #3；Vals Index #2（70.9%）；Agent Arena Index 1336、#2 globally。本期未回读 Artificial Analysis、Vals、Arena 原榜。媒体关于 Neon 将替换 Argon 或下线旧模型的说法，未见官方博客写明，正文不用。

Anthropic IPO：官方新闻日期 November 18, 2026。定价 $83.00；发行 980,000,000 股 Class A，其中公司出售 956,351,354 股、出售股东 23,648,646 股；承销商 30 天选择权最多 147,000,000 股；预计 11月19日在 Nasdaq Global Select Market 以 “ANT” 开始交易，预计 11月20日交割，须满足惯例交割条件；SEC 于 11月18日宣布相关注册声明生效。粗算：956,351,354 × 83 = 79,377,162,382 美元；980,000,000 × 83 = 81,340,000,000 美元；选择权若行使 147,000,000 × 83 = 12,201,000,000 美元。官宣未给估值或已发行总股本。采集时（北京时间 11月19日约 09:15）对应美国东部 11月18日约 20:15，当日开盘尚未开始。

英伟达：董事会委员会官方新闻稿日期 November 17, 2026，主席 Suzanne Nora Johnson，成员 Stephen C. Neal、John O. Dabiri。电话会表述据 The Verge（2026-11-18，13:01 UTC）转述；本期未读官方逐字稿。CFO commentary 中当季对华 Hopper 出货 24 亿美元及指引不含对华数据中心计算营收，已在 11月18日日报写过。Kress 在 11月18日 [CNBC 采访](https://www.cnbc.com/2026/11/18/nvidia-interim-ceo-colette-kress-talks-earnings-china-transcript.html)中仍谈到游戏、汽车和工作站等对华出货，故正文不写成退出全部中国业务。媒体标题中的 “abandoning China” 是概括，不是公司原话。

OpenAI 芯片设计：官方博客日期 November 18, 2026。“up to 14% improvement relative to heavily optimized baselines on the flagship GPU IP”；“roughly a year of progress achieved in less than 5 months”；Jalapeño “reduced standard-cell area by about 13% in the vector unit and 10% in the matrix unit”，并称 “silicon proven”。AMD CPU 为 “single-digit percentage gains”。RISC-V 评测与 GPT-Synopsys 均为公司陈述。

研究加速报告：官方日期 November 18, 2026。2–4 小时任务 23%→46%，4–8 小时 13%→35%；监控训练 79%、启动训练 35%、推理与服务栈编码 25%。10 月用量按 API list prices：中位 $2,400（较 9 月 +62%），第 90 百分位 $23,000（+105%）。Safety & Alignment 记录工作周 1 月至 9 月 +77%。

Genie 4：官方博客日期 November 18, 2026。Ultra 符合条件者即日可试，Pro 可排队。Genie 3 单次生成 “up to 3 minutes per generation (up from 60 seconds)”。SynthID 水印与研究局限为官方自述。

X：三帖均经 X 公共读取接口直接读取原帖，并读取了超 280 字帖的全文。François Chollet 原帖时间 2026-11-18T23:07:18Z（北京时间 11月19日 07:07），帖 ID 2123191344822902818；他另有一条关于 Neon 定价的原帖（2026-11-18T23:15:59Z，ID 2123193532186005962），因与头条重复未列入三人精选。Sebastian Raschka 原帖时间 2026-11-18T14:44:39Z（北京时间 11月18日 22:44），帖 ID 2123064851383677087；昨日已用过的学习率衰减帖本期不再选用。Thomas Wolf 原帖时间 2026-11-18T16:11:46Z（北京时间 11月19日 00:11），帖 ID 2123086773844672689。Karpathy、LeCun、Andrew Ng、Noam Brown、Lilian Weng 在排除回复与转发后，窗口内无合格原帖。Jason Wei 窗口内仍是昨日已引用的入职帖，不再选用。Jim Fan 仅有一条表情式引用转发，未列入。Simon Willison 有 Datasette Lite 与 GPT-6.2 演示帖，因与昨日栏目或已报道模型重复，未列入三人精选。

Hacker News（采集约北京时间 11月19日 09:15）：当时 “Unauthenticated remote code execution in Nginx” 约 1127 分（item 50547374），“Gemini 4 Neon” 约 408 分（item 50552424），微软 Ignite 七款模型约 443 分（item 50548021，已在 11月18日日报写过，本期不重复）。Anthropic 定价条目约 26 分（item 50553843）。OpenAI 芯片设计约 158 分（item 50549493），Genie 4 约 184 分（item 50550415）。首页另有与本期主题无直接关系的条目。

来源覆盖：已读 AIHOT 11月19日页（第 212 期，每天 08:00 出刊）、Hacker News 首页、GitHub 热榜（北京时间 11月19日约 09:15 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以 Google 官方博客、Anthropic 新闻稿、英伟达新闻稿及媒体对电话会的引述、OpenAI 官方博客与失准报告、Palo Alto Networks 新闻稿、Wiz 报告与 nginx.org 安全通告、CAIS 声明页、Open Athena 博客为依据。AIHOT 另列的 GPT-6.2 口碑综述、微软 Ignite 模型、纳德拉谈英伟达人事、Semafor 关于部分董事仍推动黄仁勋回归等，或已在昨日及更早日报写过，或为未核到足够原文的媒体转述，本期不作为新头条。Vals AI 关于模型在模拟图像中标记平民与投降士兵的评测，页面路径显示 2026-10-27，超窗且不像新发布，本期放弃。ElevenLabs 收购 Kotoba 的官方说明日期为 11月16日，超出主要 24 小时窗口，本期不写入正文。

</details>
