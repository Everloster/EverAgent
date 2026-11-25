---
title: "AI 行业日报 · 2026-11-21"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-21"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---

# AI 日报 · 2026年11月21日

今天先看三件事。

- Anthropic 的 Levent Alpöge 在个人网站宣布，他与 Claude 合作得到了黎曼猜想及广义黎曼猜想的证明，并放出只含 Lean 的分卷归档。这是作者本人的宣布，陶哲轩和 Scott Aaronson 已公开讨论，但数学共同体尚未消化，不能写成已经确认的证明。

- Thinking Machines Lab 11月20日发布开源权重模型 Inkling 2 Mini。它把中间层对每个 token 循环跑三次，总参数 26.4B，激活 3.4B，检查点约 20GB，官方称可在 32GB 及以上内存的苹果芯片设备上本地运行。

- METR 11月20日更新了对公开模型的能力测量。在 TH1.1 与 TH2 的合集上，时间视野大约每 3.6 个月翻倍；他们同时写道，现有公开证据仍不足以排除未来一两年出现剧烈的 AI 研发加速。这是评估机构的判断，不是已经验算的定论。

## Alpöge 宣布与 Claude 合作给出广义黎曼猜想的 Lean 证明

[Levent Alpöge](https://alpo.ge/) 在个人网站的自我介绍里写明任职于 Anthropic, PBC，并担任哈佛 Society of Fellows 初级研究员。他在[短文](https://alpo.ge/remark.pdf)中写道：相信自己与 Claude 合作发现了黎曼猜想的证明，该方法也推广到广义黎曼猜想，并且已经在没有额外假设的情况下形式化。他没有同时给出传统论文，只提供了 14 个分卷的 Lean 归档。

他自己写，思路由他引导到与一个玩具设定类似的情境，接近终点时 Claude 明显超过了他。陶哲轩 11月20日的[博文](https://terrytao.wordpress.com/2026/11/20/unforced-euler-singularity-unforced-navier-stokes-singularity-and-the-generalized-riemann-hypothesis/)把这件事列为当日三项结果里“消化程度最低”的一项，并写成 Alpöge 使用内部模型生成了极其庞大、只有 Lean 的广义黎曼猜想证明。他建议到 Lean Zulip 跟踪核验与策略提炼，并估计消化还需要时间。

Scott Aaronson 同日在[博文](https://scottaaronson.blog/?p=10344)里写，他醒来看到的消息是 Alpöge 称让 Anthropic 的模型证明了广义黎曼猜想，并写出约 1,740 万行 Lean。他个人倾向于证明能够成立，但并不百分之百肯定；他也提醒 Lean 内核过去出现过可推出 0=1 的缺陷。他还写，数学家要到能够亲自解释并提炼出想法时才会满意，而这可能需要数年。行数来自 Aaronson 的转述，Alpöge 原文只说论证目前极长，本期未独立统计归档行数。

同一天，陶哲轩还记录了另外两项“消化程度更高”的工作：Alpöge、Tristan Buckmaster 与 Matei Coiculescu 在大量人工智能协助下，给出三维无外力不可压缩 Euler 方程有限时间爆破的可读证明，并已用 Lean 形式化；Alpöge 与 Buckmaster 又给出三维无外力 Navier–Stokes 方程有限时间爆破的证明和 Lean 形式化，他称策略大体清楚，但仍需写成更规范的论文。

这些同样是宣布与评述，不是已经被广泛接受的定论。此前围绕 Navier–Stokes 已有多次公开讨论，这里只记陶哲轩对这批新文本的分类。

同一天还有另一项独立宣布。Ravi Vakil 在[《Hurried Announcement: Alessandro Masullo GRH》](https://math216.wordpress.com/2026/11/20/hurried-announcement-alessandro-masullo-grh/)中说，Alessandro Masullo 提出了一份广义黎曼猜想的证明草稿，Brian Conrad 已细看数月并给过大量反馈，目前看起来不错，而且“全部由人完成，没有使用人工智能”。这是另一份尚未经共同体确认的稿件，不应与 Alpöge 的 Lean 归档混为一谈。

## Thinking Machines Lab 发布可在笔记本运行的 Inkling 2 Mini

Thinking Machines Lab 11月20日[宣布](https://thinkingmachines.ai/news/inkling-2-mini/)发布 Inkling 2 Mini，并同步给出[模型卡](https://thinkingmachines.ai/model-card/inkling-2-mini/)。这是循环 Transformer：模型卡写明共 24 层，中间 12 层共享权重、每个 token 运行三次，因而每个 token 实际经过 48 次层计算。它是混合专家模型，总参数 26.4B，激活 3.4B；计入循环后，官方称每个 token 的有效激活约为 5.4B。许可为 Apache 2.0，并接受文本和图像输入，上下文最长 1M token。这与此前已报道的 Inkling 2 Small 不是同一个检查点。

官方称，大部分权重量化在 NVFP4，最后四层为 MXFP8，总占用约 20GB。模型卡写明可在内存 32GB 及以上的苹果芯片设备，以及 1 台 NVIDIA DGX Spark 等环境上本地推理。官方演示是在一台 48GB 内存的 MacBook Pro（M5 Pro）上离线构建可玩的飞行模拟器，不能把演示机型写成最低配置。权重和可变循环的研究变体已放到 Hugging Face，也可在 Tinker 上做推理和微调。

公司自报：在总参数不足 100B 的开源权重模型中，它在 DeepSWE v1.1（48.2%）和 Vals Index v2.2（46.5%）等基准上领先。官方图表注明各模型的评测设置并不相同。官方还写，循环有助于推理，但不能让权重记住更多事实；知识类基准并不随循环次数提高，模型更多靠搜索和工具来补足。这些数字和机制说明均来自公司自己的评测与叙述，不是第三方复核。

## METR：与 AI 研发相关的能力约每 3.6 个月翻倍，也更难测量

METR 11月20日发布[能力测量更新](https://metr.org/blog/2026-11-20-q4-2026-capability-update/)，评估对象包括已公开的模型，最前面的是 Opus 5.5 和 GPT-6 Astra。作者写明，他们仍显著不确定：剧烈加速究竟需要哪些能力，以及相关能力到底提升得有多快。这里的“剧烈加速”，是指能力快到人类已无法有意义地理解、评估并应对新系统带来的灾难性风险。

在 TH1.1 与 TH2 的合集上，他们估计时间视野大约每 3.61 个月翻倍（95% 置信区间 2.08 至 4.94），约合 110 天，与此前 TH1.1 约 105 天的趋势接近。他们还写，这一合集上的倍增时间，与 OpenAI 近期在内部研究任务上报告的约 3.8 个月相近。若做他们所称的“朴素外推”，模型在这些任务上达到最长阈值（200 小时）的 50% 时间视野，会落在 2027 年 7 月。这是外推，不是预测承诺。

把 TH1.1 排除、只看 TH2 中可验证子集时，倍增时间缩短为 1.65 个月（95% 置信区间 0.79 至 3.99）。官方写明数据较噪，这可能与近期加速被合集趋势掩盖有关，但他们也列出了其他解释。

他们还观察到：在编程和优化任务上，模型通常达到或超过他们招募到的熟练人类，但在有许多领域专家参加的比赛里，模型多处于很高分位，而不是绝对第一。在缺少清晰经验反馈的任务上，模型的判断看起来不如人类专家。综合能力指数 MCI 在他们测试的公开前沿模型上，没有显示强加速或减速。

## ChatGPT 推出 Space，正在向 Plus 用户开放

OpenAI 帮助中心的[更新说明](https://help.openai.com/en/articles/6825453-chatgpt-release-notes)将日期写为 2026年11月20日：ChatGPT Space 即日起向全球年满 18 岁的 Plus 用户逐步推出。官方称，用户可以和 ChatGPT 一起制作交互式页面与演示文稿，邀请同样拥有 Space 权限的人共同修改，也可以让页面和幻灯片根据已连接的应用与工具自动更新。

侧边栏里的 Space 将取代 Library，成为页面、幻灯片、图片和上传文件的入口。打开别人分享的页面或演示，需要获得查看权限，并且登录到已开通 Space 的 Plus、Pro、Business 或 Enterprise 账号；免费用户打不开，也没有公开链接。官方写明可在网页、桌面应用以及 iOS 和 Android 上创建和编辑页面。这是公司对正在推出功能的说明，不是已经完成的全量开放，也尚未看到独立产品评测。

## 腾讯混元开放 Hy4 权重

腾讯混元官方账号 11月20日 11:52（北京时间）[宣布](https://x.com/TencentHunyuan/status/2123625549147070538)，当天开放 Hy4 权重。官方把它称为原生多模态旗舰混合专家模型，总参数 770B，激活 49B，上下文 1M，并同步给出带安全评估的 Hy4 System Card。这与[上期已写的 Hy4 flash 接口发布](./ai-news-daily-2026-11-17.md)不是同一件事：flash 是 11月16日的接口产品，当时公告并未说明是否开放权重；本次开放的是旗舰 Hy4 的权重。

[Hugging Face 上的 tencent/Hy4](https://huggingface.co/tencent/Hy4) 与[研究页](https://hy.tencent.ai/research/hy4)写明，权重同时放到 Hugging Face、ModelScope、GitHub 和 AtomGit 或 GitCode 等平台，许可为 Tencent Hy License。这是开放权重，不等于对所有商业用途都没有额外条款。官方账号还邀请团队在周五太平洋时间上午 8 点至 10 点到 r/LocalLLaMA 做 AMA；本期采集时未核对其是否已经举行，以及现场说了什么。

## 热榜上，漏洞挖掘技能包增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月21日约 09:16 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 当天约增加 1,622，总星约 14,296，增量最高，页面介绍为面向漏洞挖掘和外部红队的 Claude Code 技能包，昨日已经上榜。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 1,241，总星约 205,285。[XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) 约增加 1,082，总星约 13,716，是下载工具，与人工智能无直接关系。[obra/superpowers](https://github.com/obra/superpowers) 约增加 890，总星约 322,851，昨日增量更高，今天仍在前列。[mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) 约增加 869，总星约 2,752。全表在文末。

## X上顶尖AI大佬最近都说了什么

**François Chollet**，Keras 作者、ARC-AGI 发起人。他[写道](https://x.com/fchollet/status/2123898321647571442)，若把时间拨回 2024年6月14日：那时前沿模型几乎没有流体智力，ARC 1 大约只有 5 分，连两个数相加都不稳。在他的设想里，如果有人告诉你，到 2026年11月会出现测试时归纳的推理模型，ARC 1 以及更难的 ARC 2、ARC 3 都会被做满，代码将大多由人工智能编写，模型还会解决多项千禧年难题，同时英伟达仍占约 80% 的人工智能算力市场、营收和利润增长约 4.5 倍——当时似乎应该买入。

他接着写，到自己发帖时，那样做的投资大约还跌了 5%，计入通胀后更多。帖发于北京时间 11月21日 05:56，是带假设的个人评论，其中的能力判断和股价数字都不是已经核对过的市场或评测结论，也不能用来坐实上文的数学宣布。

**Thomas Wolf**，Hugging Face 联合创始人。他[写道](https://x.com/Thom_Wolf/status/2123852806213730744)，从今年夏天起，Hugging Face 开始运行自建 CDN，每月运力接近 1 exabyte，折合约每秒 420GB、每秒 8 万次请求。他认为传统 CDN 更适合把许多小网页文件送到很多人那里，而人工智能下载往往是少数超大文件、且大量由机器拉取，缓存逻辑因此不同。帖发于北京时间 11月21日 02:55，是他对自家基础设施的说明，数字未经本期独立测量。

**Sebastian Raschka**，《Build a Large Language Model From Scratch》作者。他[写道](https://x.com/rasbt/status/2123853084216455549)，模型会针对特定的运行框架和工具做微调，因此框架本身就是训练安排的一部分，模型很难把框架“吸收掉”；他把它比作指望 CPU 或 GPU 去吸收操作系统。帖发于北京时间 11月21日 02:56，是他对当时一条讨论的个人补充，不是对某一产品的评测。

## 另外几则

**MiniMax 称内部模型 MIM 在多项密码分析任务上做出可执行攻击。** 公司 11月20日[发文](https://www.minimax.io/blog/practical-cryptanalysis-with-minimaxs-latest-internal-model)，报告对历史 NIST 候选算法、近期同行评审方案以及公开挑战实例的结果，并称已提前告知相关作者，开源了部分推理轨迹和概念验证代码。官方同时写明，工作针对学术方案、往届候选和公开挑战参数，不影响已经部署的密码标准。这是公司自报，本期没有独立复现。

**browser-use 发表 1.0 说明，用一个 Python REPL 替换原先的浏览器动作菜单。** [公司博文](https://browser-use.com/posts/browser-use-1-0)发布于 11月20日，但文中写明 1.0 本身的日期是 11月10日，已超出主要 24 小时窗口，这里只作回溯。官方称主工具改为带原生 Chrome DevTools Protocol 的持久 Python REPL，并自报在 BU Bench v2.1 上，同样三个模型的分数高了 14 到 33 分、费用降到约 2.7 到 5.2 分之一；他们自己也写，这次发布还改了默认设置，不能把分数提升全部算在工具替换上。

**Signal 宣布限制操作系统里的人工智能智能体抓取应用数据。** 总裁 Meredith Whittaker 11月20日[写道](https://signal.org/blog/protecting-your-privacy/)，将采取类似去年在 Windows 上阻止 Recall 截屏的做法，在 iOS 27，以及能够检测到人工智能助手试图读取 Signal 屏幕的 Android 版本上，限制此类抓取。

用户可在设置里关闭这项保护，但官方警告这可能暴露自己和联系人的内容，并承认截屏限制并不能挡住通过文件系统等其他途径的读取。这是 Signal 的产品措施和立场说明。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11月21日 09:16；当时页面 16 行；页面 HTML 抓取约 09:16:09）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 14,296 / +1,622 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [obra/superpowers](https://github.com/obra/superpowers) | 322,851 / +890 | Shell | 智能体技能框架与开发方法 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 61,394 / +773 | Python | 让各类软件可被智能体原生调用的 CLI 层 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 67,696 / +847 | Python | 两小时从零训练 64M 大模型 |
| [cursor/plugins](https://github.com/cursor/plugins) | 17,851 / +299 | TypeScript | Cursor 插件规范与官方插件 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 205,285 / +1,241 | TypeScript | 面向智能体的搜索、抓取与数据接口 |
| [nginx/nginx](https://github.com/nginx/nginx) | 32,569 / +246 | C | NGINX 官方开源仓库，与人工智能无直接关系 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 11,791 / +217 | C++ | 优化与部署人工智能推理的工具包 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 69,289 / +636 | HTML | 面向多种编码智能体的图表设计技能 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 71,457 / +681 | Python | 跨多个平台调研话题并汇总的智能体技能 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 11,041 / +315 | TypeScript | 面向 Stitch MCP 服务的智能体技能库 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 2,752 / +869 | Shell | 应用商店审核与合规的公开手册和预检 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 13,615 / +466 | Python | 面向 CI/CD 可靠性的开源智能体 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 75,805 / +676 | TypeScript | 开源知识库，与人工智能无直接关系 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 13,716 / +1,082 | Python | 下载工具，与人工智能无直接关系 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 12,191 / +979 | Python | 开源人工智能视频剪辑桌面工具 |

Alpöge 宣布：个人主页 https://alpo.ge/ 页首自我介绍为 “pt&rl, anthropic, pbc / junior fellow, harvard sof”。短文 https://alpo.ge/remark.pdf 写 “I believe I have, working with Claude, discovered a proof of the Riemann Hypothesis. In fact, the method easily extends much further, resolving the so-called Generalized Riemann Hypothesis”，“Claude and I have also formalized the arguments without assumptions”；脚注给出 https://alpo.ge/lean.tar.gz.part01 至 part14。陶哲轩博文日期 20 November, 2026，将三项结果按“已消化程度”降序排列，第三项原文为 “Levent Alpöge, using an internal AI model, has generated an (enormous) Lean-only proof of the Generalized Riemann Hypothesis”，并指向 Lean Zulip。Scott Aaronson 博文落款为 Friday, November 20th, 2026 at 12:29 pm，未写时区；他写 “Levent Alpöge says that he’s gotten Anthropic models to prove the Generalized Riemann Hypothesis, producing 17.4 million (!!) lines of Lean code”，并称 “I’m not 100% sure, but my bet is that the proof will stand”。Vakil 博文日期 November 20, 2026，原文含 “It is all human, with no AI”“Brian Conrad has been looking closely at it for months”“so far looking good”。

Inkling 2 Mini：官方新闻稿与模型卡日期均为 November 20, 2026。模型卡：“A 24-layer decoder-only transformer… The middle 12 layers run three times with shared weights, giving 48 layer applications per token from 24 layers of weights.”“26.4B, 3.4B active”“each extra pass through the looped layers adds about 1.0B effective active parameters. Since the model runs with three passes, there are 5.4B effective active parameters per token.”许可证 Apache 2.0。硬件原文为 “Apple silicon devices with 32GB or more memory”“1x NVIDIA DGX Spark”“Other GPUs and platforms are possible, with 32GB or more of VRAM recommended”。演示机型原文为 “MacBook Pro (M5 Pro, 48GB) Airplane mode”。基准数字来自官方新闻稿，并注明 “Evaluation setups vary by model”。

METR：博文日期 November 20, 2026。合集倍增原文为 “time horizons are doubling roughly every 3.61 months (95% CI 2.08-4.94), or 110 days”，并写与此前 TH1.1 的 105 天趋势相近；TH2 可验证子集为 “a doubling time of 1.65 months (95% CI 0.79 to 3.99)”，并写 “Our data is noisy”。关于 OpenAI 内部任务：“recently published data from OpenAI seems to imply a doubling time of 3.8 months”。朴素外推原文为 “naive extrapolation would imply that models reach a 50% time horizon equal to the longest score threshold on our task set (200 hours) in July 2027”。公开前沿模型在 TH2 可验证子集上的时间视野写为 “up to 27 hours”。

ChatGPT Space：帮助中心更新说明标题为 “ChatGPT Space is rolling out to Plus”，日期 November 20, 2026。“rolling out globally to Plus users ages 18 and older”；“It replaces Library”；“People on Free can’t open shared pages or presentations. Public links aren’t available.”；“Use Space on the web, desktop app, and iOS and Android to create and edit pages.”

Hy4 权重：官方账号 @TencentHunyuan 帖 ID 2123625549147070538，时间 2026-11-20T03:52:40Z（北京时间 11月20日 11:52）。原文：“Today, we’re releasing the open weights for Hy4. Our natively multimodal flagship MoE (770B total / 49B active, 1M context).” Hugging Face 模型页许可证一节写 “Hy4 is released under the Tencent Hy License.” 平台名称在研究页与模型页的表述不完全一致（GitCode / AtomGit 等），正文只用“等平台”概括。Hy4 模型本身的首次发布不在本期窗口，11月5日的聚合目录已有记录，本期只写开放权重。

MiniMax：官方博文页面含日期 2026-11-20。关键限定原文为 “This work focuses on academic designs, past competition candidates, and public challenge parameters, and does not affect deployed cryptographic standards.”

browser-use：博文页眉与文末为 November 20, 2026；提要写 “browser-use 1.0 (November 10, 2026)”。自报分数：“On BU Bench v2.1 the same three models scored 14 to 33 points higher than on 0.x and cost 2.7x to 5.2x less. That covers the whole release, one run per model, so the tool change can't take all the credit.”

Signal：博文作者 Meredith Whittaker，日期 20 Nov 2026。原文包括对 iOS 27 以及“on Android versions where we can detect an AI assistant attempting to read your Signal screen”的限制，并写用户可在应用设置中关闭保护，以及截屏限制并不覆盖通过文件系统等途径的读取。

Hacker News（HN API 采集约北京时间 11月21日 09:16）：当时 “Levent Alpöge claims proof of the Generalized Riemann Hypothesis [pdf]” 约 2,343 分（item 50574968），“Hurried Announcement: Alessandro Masullo GRH” 约 1,517 分（item 50579568），“Inkling 2 Mini” 约 636 分（item 50581260），陶哲轩博文约 331 分（item 50578358），Aaronson 博文约 208 分（item 50581084），“Language Models Can Rewrite Their Own Weights” 约 332 分（item 50577265），Signal 博文约 503 分（item 50572348）。首页另有与本期主题无直接关系的条目。本期未把 SEC 对英伟达会计问题的“消息人士”报道，以及 Architect Labs 自称由人工智能发现并验证的 Frostbite CPU 架构，作为已核对头条。

X：三帖均经 X 公共读取接口直接读取原帖，并读取了超 280 字帖的全文。François Chollet 原帖时间 2026-11-20T21:56:34Z（北京时间 11月21日 05:56），帖 ID 2123898321647571442。Thomas Wolf 原帖时间 2026-11-20T18:55:42Z（北京时间 11月21日 02:55），帖 ID 2123852806213730744。Sebastian Raschka 原帖时间 2026-11-20T18:56:49Z（北京时间 11月21日 02:56），帖 ID 2123853084216455549。Jason Wei 窗口内仍是昨日已引用的测量方式帖（ID 2123495287377571916），本期不再选用。Simon Willison 窗口内较新的是关于 Gemini 4 Neon 与 Carbon 比较的提问帖，且 11月19日 14:39 的鹈鹕测试帖已在上期用过，本期不再选用。Karpathy、LeCun、Andrew Ng、Noam Brown、Lilian Weng 在排除回复与转发后，窗口内无合格原帖。Jim Fan 有一条祝贺 Alpöge 的帖（ID 2123820604256288978），与今日头条重复，未列入三人精选；其 GR00T 2 演示帖已在更早日报出现过。Nathan Lambert 窗口内多为 Anthropic 上市祝贺、商品与行程，未列入三人精选。Raschka 另有 “Benchmarks loved it.” 一帖，因缺少足够上下文、且可能贴近今日模型发布，未选用。

来源覆盖：已读 AIHOT 11月21日页（每天 08:00 出刊，页面写第 214 期）、Hacker News 首页与官方 API、GitHub 热榜（北京时间 11月21日约 09:16 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以 Alpöge 个人短文与网站、陶哲轩博文、Aaronson 博文、Vakil 博文、Thinking Machines Lab 官方新闻稿与模型卡、METR 官方博文、OpenAI 帮助中心更新说明、腾讯混元官方账号原帖、Hugging Face 模型页、MiniMax 官方博文、browser-use 官方博文和 Signal 官方博文为依据。AIHOT 另列的 Gemini 4 Hydrogen 上线 Gemini 应用和 Search，已在 11月13日日报写过，聚合页虽在今日仍有转述，本期不作为新头条。Nemotron for Science 等更早于 48 小时窗口的条目，未作为新头条。

</details>
