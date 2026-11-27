---
title: "AI 行业日报 · 2026-11-27"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-27"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---
# AI 日报 · 2026年11月27日

今天先看三件事。

- 《金融时报》11月26日报道，英伟达已通知戴尔、超微电脑等制造伙伴，停止向马来西亚、新加坡、泰国和印度尼西亚发运服务器。报道援引三名知情人士，并写明目前不清楚这是否只是临时安排，以便各方弄清如何遵守美国新的出口管制。英伟达拒绝置评。这是媒体根据匿名消息的报道，不是公司官方声明。

- OpenAI 的 Tibo（账号 thsottiaux，个人简介写明负责 Codex 与 ChatGPT）11月26日发帖称，GPT-6.2 上线时出现计费错误，多数用户的 GPT-6.2 Astra 和 Sol 用量被错误打折。现已修复；与上周相比，同样的工作会更快用完额度，Astra 约快 40%，Sol 约快 25%。他同时写，用量仍应比 GPT-6 Astra 和 GPT-6.1 Sol 更经用；其他模型未受影响，也不会补收此前差额。作为致歉，Go、Plus、Pro 和 Business 用户将获得一次预存的额度重置。

- 腾讯混元人工智能基础设施团队 11月26日宣布，完整开源投机解码草稿模型 DFly2 的权重、训练代码和技术报告。官方称，它复用目标模型稀疏注意力已经选好的缓存与位置，使每个草稿 token 最多关注约 2,000 个 key，也不必再为草稿模型单独维护缓存。文中的加速和接收长度数字，都是该团队自己的评测。

## 英伟达据报暂停向东南亚四国发运服务器，公司未予置评

[《金融时报》11月26日报道](https://www.ft.com/content/7838a715-07d4-4605-aa60-21f5af2b2370)写，英伟达已通知制造伙伴停止向马来西亚、新加坡、泰国和印度尼西亚发运服务器。报道称，戴尔、超微电脑等把英伟达芯片组装成服务器的厂商，已向这四国的买家表示，英伟达不会放行相关订单。消息来自三名知情人士。

报道还写，目前不清楚停运是暂时的，还是英伟达及其伙伴在设法遵守华盛顿新的出口管制。英伟达拒绝置评；戴尔、超微电脑、字节跳动和 Aolani 均未回应置评请求。

[路透社同日转述](https://www.investing.com/news/stock-market-news/nvidia-halts-server-shipments-to-four-southeast-asian-countries-ft-reports-5052112)了上述四国范围、制造伙伴和“是否只是临时安排仍不清楚”等要点。路透社写，它在常规营业时间之外联系英伟达、戴尔和超微电脑，当时未立即收到回复。这仍是对《金融时报》报道的转述，不是英伟达事后确认。

《金融时报》把此事放在美国加强出口管制、防止先进人工智能算力经第三国流向中国企业的背景下。报道引述公司账目称，英伟达 2025 年经新加坡子公司入账 1,040 亿美元，同比增长 72%；部分台湾与中国区收入也经该主体记录。这是该报对账目的转述。

[11月17日日报](./ai-news-daily-2026-11-17.md)已记录美国商务部工业与安全局 11月16日的临时最终规则：据当时媒体报道，向印度尼西亚、马来西亚、新加坡、泰国和巴西的数据中心客户出售先进芯片须申请许可，并向为受限国家企业提供大量算力的境外数据中心提出 90 天许可要求。巴西出现在那条规则的报道中，但并未出现在此次据报停运的四国名单里。

[11月25日日报](./ai-news-daily-2026-11-25.md)还记录了将马来西亚、新加坡和泰国等地 7 家公司列入实体清单的规则，其中包括 Megaspeed 及相关实体。这两项是此前已经作出的政策决定；本期新进展是英伟达据报要求伙伴停止向上述四国发运服务器。停运会持续多久、许可证将如何申请，仍待后续说明。

## OpenAI 称修复 GPT-6.2 计费错误，同类用量会更快触顶

OpenAI 的 Tibo 在 11月26日 10:50（北京时间）的[原帖](https://x.com/thsottiaux/status/2125784147889393806)中写：GPT-6.2 上线时出现计费错误，多数用户的 GPT-6.2 Astra 和 Sol 用量被错误打折；现已修复，因此同样的工作会占用计划里更多的用量额度。与上周相比，用户将更快触顶：GPT-6.2 Astra 约快 40%，Sol 约快 25%。

他接着写，这些模型的用量仍应比 GPT-6 Astra 和 GPT-6.1 Sol 更经用；其他模型未受影响，公司也不会就过去的用量差额补收费。作为对这次失误的小小致歉，Go、Plus、Pro 和 Business 的所有用户将获赠一次预存的额度重置。他在当天 15:26 的[跟帖](https://x.com/thsottiaux/status/2125853628250599730)中写，“预存重置已上线”。

这是该公司员工的公开说明，不是一份单独的产品公告。帖中的“与上周相比”，指的是与错误折扣仍在生效的那一周相比，而不是与一份未写明的官方标价表对账。部分转述还提到向 Business 用户赠送 Fast Mode 至年底，原帖里没有这句话，这里不采用。

## 腾讯混元开源投机解码草稿模型 DFly2

腾讯混元人工智能基础设施团队 11月26日在 [AngelSpec 仓库](https://github.com/Tencent/AngelSpec)宣布，完整开源 DFly2 的[权重](https://huggingface.co/collections/AngelSlim/angelspec)、训练代码和[技术报告](https://arxiv.org/abs/2611.34776)。说明写，DFly2 是 Hy4 与 Hy4 flash 所搭载的投机解码草稿模型，并已在 DeepSeek-V4.1-Flash 和 GLM-5.3-Flash 上训练；同期还发布了面向这三款稀疏注意力目标模型的混合专家草稿权重。

官方和技术报告都把方法概括为：每个草稿层直接读取对应目标层已经缓存的 KV，并只在该层索引器选出的位置上计算，因此不必再为草稿模型单独维护缓存，也不再额外做一遍打分。仓库写，每个草稿 token 最多关注约 2,000 个 key，计算开销不随上下文长度增加；它不参与预填充，从预填充到解码只需额外传输一个末层隐状态。

[预印本摘要](https://arxiv.org/abs/2611.34776)自报：在 DeepSeek-V4.1-Flash、GLM-5.3-Flash 和 Hy4 flash 上，用同一套训练配方比较时，DFly2 每步接收的 token 多于 DFlash 和 DSpark。相对二者中较强基线的领先幅度，在通用负载上为 3.9% 至 10.5%，在最长 128K 的长上下文和智能体负载上扩大到 10.0% 至 31.5%。

在高并发、并保持每用户解码速度相当的条件下，服务 DeepSeek-V4.1-Flash 时，它在 64K 的长上下文和智能体集合上，吞吐分别比该基线高 62% 和 81%。这些都是作者自己的测量，不是独立复现。

## DeepMind 发布质谱解析技能包：库内识别约 97%，不是从头解析未知物

[Google DeepMind 11月25日文章](https://deepmind.google/blog/interpreting-mass-spectra-with-google-antigravity/)介绍了面向 Google Antigravity 的 Mass Spec Skills。官方写，这组技能把 Gemini 的化学推理，与已有的质谱工具和公共化学数据库查询拼在一起，让研究人员用自然语言描述任务，由代理选择并串联相应步骤，再整理可供化学家复核的证据。

文章把标准谱图库检索只能注释约 5% 的实测谱图、人体样本约 10%，称为质谱里的“暗物质”；许多化合物已出现在公共化学数据库中，只是还没有可对照的参考谱图。该文日期为 11月25日，落在本期 48 小时扩展窗口内。

官方评测针对的是参考谱图已经存在的情况。团队从 MoNA 中的 Enamine REAL MS/MS 集合抽取 100 种化合物，这些结构同时也收录在 PubChem，并去掉了几乎没有碎裂的记录。每种谱图尝试三次；超过一小时时限的尝试计为失败，瞬时的基础设施和配额错误则被排除。

比较三种设置：Antigravity 不联网、也不使用技能；允许按用户许可访问公共库和数据库；以及在同样访问之外再加上这组技能。受测模型是 Gemini 3.8 Flash，以及 Gemini 4 Argon 和 Gemini 4 Carbon。

官方自报：在没有网络和技能时，三个模型的准确率都低于 4%；只给网络访问时，两个前沿模型仍会漏掉四分之一到三分之一的谱图，轻量模型则漏掉四分之三以上。加上 Mass Spec Skills 后，三个模型都在约 97% 的尝试中识别并验证了准确分子，轻量模型与前沿模型相当。技能也降低了每次尝试生成的 token：相对“只给网络访问”的路径，Flash 约减至四分之一，Argon 约减半，Carbon 约减少五分之一。

必须分清：这 97% 衡量的是公共库里已有参考谱图的识别与核验，不能写成对未知分子的从头结构解析已经达到同样水平。文中引用合作化学家的评价，属于他们自己的使用感受，这里不以那些数字代替官方基准。

## 腾讯团队在《自然》发表双靶点多肽设计平台 ORIDTP，目前仍是动物实验

《自然》11月25日发表论文[《De novo design of high-potency dual-target therapeutic peptides with ORIDTP》](https://www.nature.com/articles/s41586-026-11338-1)。通讯作者包括腾讯的姚建华等。摘要写，ORIDTP 是一个把单靶点知识迁移与双靶点强化结合起来的人工智能平台，用于设计同时调节两个治疗靶点的高活性多肽。

团队报告，它设计出 GLP-1 受体与胰高血糖素受体的双靶点共激动剂，其中 6 条在生物活性上超过了各受体最强的天然配体；先导多肽 GA-Dual.R5.S3 在饮食诱导肥胖小鼠中带来明显的体重下降和血糖改善，并在 db/db 小鼠中表现出显著的抗糖尿病作用，且未引起恶心或厌恶。

摘要还写，该平台以零样本方式设计了针对 PD-1 和 CTLA-4 的双靶点共抑制剂。15 条设计多肽中，8 条能够阻断这两种检查点的相互作用，其中 3 条在人源检查点敲入的荷瘤小鼠中显示出抗肿瘤效果；先导多肽 IC-Dual.P3 的肿瘤生长抑制最强，肿瘤体积相对对照组减少 94.2%。

代码公布在 [TencentAI4S/ori](https://github.com/TencentAI4S/ori/tree/master/projects/oridtp)。这些结果来自体外活性和小鼠实验，不能外推成已经完成的人体临床试验。论文日期为 11月25日，同样落在 48 小时扩展窗口内。

## 热榜上，漏洞挖掘技能包仍是当天增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月27日约 09:19 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 当天约增加 1,597，总星约 24,625，增量仍最高，已连续多日领先。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 1,046，总星约 210,956。[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) 约增加 955，总星约 73,858。[obra/superpowers](https://github.com/obra/superpowers) 约增加 854，总星约 327,505。[mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) 约增加 759，总星约 75,766。与人工智能没有直接关系、但当天增量仍靠前的是下载器 [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3)，约增加 889，总星约 19,133。其余条目和全表放在文末。

## X上顶尖AI大佬最近都说了什么

本期精选三位研究者或行业人士的个人原帖。时间均为北京时间。以下是个人观点或个人研究观察，不是已核验的事实。

Andrej Karpathy 是人工智能研究者。他在 11月26日 10:31 的[原帖](https://x.com/karpathy/status/2125779541952246039)中写，自己让 Claude 用美国的真实数据填一张文明风格的游戏地图：Opus 5.5 下载并解析了大量公开数据，7 小时和 4.5 万行代码之后，地图可以运行。他列举了人口普查局、经济分析局、劳工统计局、能源信息署、国家海洋和大气管理局等 31 个真实数据源，并把海拔、土地覆被、国内生产总值、就业、电厂、矿山、港口等统一到 25 公里六边形网格上。

数据被转写成游戏语言，例如黄金产量对应国内生产总值，城市街区对应真实的产业专长。项目部署在 [karpathy.ai/usaciv](https://karpathy.ai/usaciv/)。他写，自己不太确定接下来要把它做成什么，浏览起来很有意思，也许能扩展成游戏；还说当周的 Claude 额度只用剩一半，得由别人接着做。这是他对一次个人实验的描述，不能当成对该模型能力的系统评测。

Dario Amodei 是 Anthropic 的首席执行官。他在 11月26日 02:22 的[原帖](https://x.com/DarioAmodei/status/2125656399392690605)中，引用一篇称其他人工智能企业负责人反驳 Anthropic“把人类能动性交给人工智能”的报道，回应说：自己并不主张向人工智能系统“交出人类自由意志”，这样理解很荒谬。他写，自己过去大量文章的一贯主题，是人工智能须由合法的民主程序来治理；即使有人声称专制决策更快，也不应为此牺牲正当性和自我决定。他把这一论证直接用到“由人工智能来治理”上，并称这是一个糟糕的主意。

他同时区分了另一层含义：让人工智能更完整地完成开车、设计抗癌药、端到端写软件这类具体任务。在这一层，他的态度是混合的：许多情况下有经济价值和救命作用，但也有代价。他举出的例子包括：对递归自我改进设限，因为 Anthropic 曾公开表示，不认为让 Claude 在没有有意义的人类监督或理解的情况下完全自主地构建后续前沿模型是安全的；在某些场景放缓或停止端到端部署，以便人们有时间适应就业冲击。

文末他还批评，部分人工智能企业负责人只是在重复“人类控制”“人工智能只应是工具”之类口号，产品和难题上并没有真正不同的做法。这些都是他的个人澄清和评论，不是一份新的监管文件。

Jeremy Howard 是 fast.ai 与 Answer.AI 的联合创始人，个人简介还写明他曾任昆士兰大学教授，并担任过 Kaggle 首任主席。他在 11月27日 07:24 的[原帖](https://x.com/jeremyphoward/status/2126094786004419002)中，回复他人讨论时写道：总体而言，REST 接口比 MCP 接口强大得多；如果最强的执行环境被限制为只能使用 MCP，能力会受到很大限制。这是他对接口选择的个人判断，不能外推成对 Google Workspace 或其他 MCP 服务的系统评价。

## 简讯

AI Digest 中文版仍显示停更于 2026年10月23日，本期只核验一次，未重试。AIHOT 第 220 期以《金融时报》关于英伟达暂停向东南亚四国发运服务器的报道为头条，与已回读的原文一致。黄仁勋复任、实体清单、Anthropic 将 Messages API 迁到 Rust、OpenAI 关于矩阵乘法指数的预印本，以及 OpenAI 蛋白质设计和 Claude 的 Install as app，已在[11月24日](./ai-news-daily-2026-11-24.md)、[11月25日](./ai-news-daily-2026-11-25.md)与[11月26日](./ai-news-daily-2026-11-26.md)日报写过，本期不再当作新消息。

OpenAI 首席执行官 Sam Altman 在 11月26日 01:12 的[原帖](https://x.com/sama/status/2125638790593274259)中写，公司正在与一小群客户测试 Private Inference，这是 OpenAI Private Intelligence 下的最新一项服务。他称，更强的隐私保护将让前沿人工智能能用于更多工作，并请有兴趣的机构联系 @shekar4x。帖中还提到，Zero Data Retention 搭配 Private Safety Processing，可以在不让 OpenAI 人员接触底层内容的前提下做自动安全审查。那是另一项已有能力，不宜与这次测试混成同一件事。

[官方页面](https://openai.com/business/private-intelligence/)把 Private Inference 标为 Alpha，并在示意图中写明 API Preview，称其使用机密计算和严格、可验证的控制。页面没有公布支持的模型、定价或全面开放时间。

[铠侠美国公司 11月25日新闻稿](https://americas.kioxia.com/en-us/business/news/2026/ssd-20261125-1.html)称，该公司与英伟达合作，用 NVIDIA SCADA 软件和铠侠固态硬盘，演示把图形处理器的有效显存扩展到拍字节量级。概念验证使用一台 GB200 NVL72 机架系统，18 个节点共 144 块 KIOXIA XD8 系列 7.68TB E1.S NVMe 固态硬盘，原始容量约 1.1PB，并支持 512 字节访问；注释写，该架构有潜力容纳 2 万亿个 512 字节向量。

新闻稿同时写明，双方仍在评估技术可行性和性能。稿中没有给出吞吐或尾延迟等实测结果，因此不能把它写成已经达到的在线检索指标。该稿日期为 11月25日，落在 48 小时扩展窗口内。

[The Decoder 11月25日文章](https://the-decoder.com/ai-agents-now-control-part-of-deepminds-compute-for-gemini-experiments-but-recursive-self-improvement-remains-distant/)转述 Google DeepMind 研究副总裁、负责 Gemini 开发的 Koray Kavukcuoglu 在公司播客中的谈话。报道写，他认为人工智能代理已经自己掌控一部分算力去跑实验，但实验室距离完整的递归自我改进仍然很远；作为安全措施，训练时不奖励代理的内部思维链，以便意图能以自然语言接受审查。这是对播客谈话的第三方转述，不是实验室的正式技术报告，也不能写成代理已经在自主训练下一代 Gemini。

Google 于 11月24日在 [Workspace 更新说明](https://workspaceupdates.googleblog.com/)中宣布，Workspace 的 MCP 服务器和官方命令行工具一般可用，并配有标准化用量档位与新的管理策略。该公告日期略早于本期主要的 48 小时窗口，这里只作回溯，不当作当天新发布的头条。Hacker News 采集时，一篇讨论此后智能体须经这些 MCP 服务器访问 Workspace、以及 Gmail 服务器发信权限受限的文章约有 234 分，位于首页较前位置。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

采集时点均为中国时区 UTC+8。AIHOT 11月27日页在 09:19:43 至 09:19:50 读取，HTTP 200，页面写第 220 期、每天 08:00 出刊。GitHub 热榜页面 HTML 在 09:19:43 读取。Hacker News 首页约在 09:19 读取，官方 API 条目分数约在 09:23:16 核对。AI Digest 中文版在约 09:18 读取。随后在 09:20 至 09:25 核对《金融时报》与路透社转述、OpenAI 员工原帖、AngelSpec 说明与预印本、DeepMind 博文、《自然》论文摘要、铠侠新闻稿、OpenAI 产品页和个人 X 原帖。热榜数字以 09:19:43 的页面为准。

Hacker News 首页在 09:23 的前若干条及当时点数大致为：AI made self-hosting fun again（283 分）、AMD-specific fork of llama.cpp（279 分）、YouTube Ad Punisher（257 分）、OpenAI may be in cost control mode（269 分，链向个人博文）、Google Will Make AI Agents Use Its MCP Servers. The Gmail One Can't Send Email（234 分，链向第三方文章）、Kamil Khan Mumtaz: Pakistani architect（223 分）、CTO of 'RansomwareHelp' indicted for wire fraud（205 分）。与人工智能更直接相关、但当时位置不一的还有 Moat: OpenRouter replacement（246 分）、Novita, StreamLake, etc. are ByteDance Ark wrappers（35 分）、Top-cited AI scientists at four US companies compared（34 分），以及 AI agents now control part of DeepMind's compute for Gemini experiments（14 分，链向 The Decoder）。首页仍可见前一日已讨论的 Holy shit holy shit holy shit holy shit: The magnitude of what’s now happening（1,983 分，链向 Scott Aaronson 博文）和 1Password Security Incident（1,633 分）。点数会变动，这里只记录采集时的首页快照。

GitHub 热榜全表（总星 / 当天增加，均为 09:19:43 页面原样）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面说明 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 24,625 / +1,597 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [obra/superpowers](https://github.com/obra/superpowers) | 327,505 / +854 | Shell | 代理技能框架与软件开发方法 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 66,376 / +746 | Python | 让各类软件更便于代理通过命令行使用 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 71,653 / +702 | Python | 从零训练小型语言模型的教程项目 |
| [cursor/plugins](https://github.com/cursor/plugins) | 19,792 / +270 | TypeScript | Cursor 插件规范与官方插件 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 210,956 / +1,046 | TypeScript | 为代理提供搜索、抓取和数据接口 |
| [nginx/nginx](https://github.com/nginx/nginx) | 33,528 / +150 | C | 官方 Nginx 源码，与人工智能无关 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 12,823 / +176 | C++ | 推理优化与部署工具包 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 73,858 / +955 | HTML | 给编程代理用的图表设计技能 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 75,766 / +759 | Python | 汇集近期公开讨论并做综述的代理技能 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 13,295 / +309 | TypeScript | 与 Stitch MCP 配合的代理技能库 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 7,043 / +562 | Shell | 应用商店常见拒审模式与提交前检查 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 15,831 / +327 | Python | 面向持续集成可靠性的开源代理 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 78,982 / +525 | TypeScript | 开源知识库 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 19,133 / +889 | Python | 下载器，与人工智能没有直接关系 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 16,948 / +774 | Python | 开源人工智能视频剪辑工具 |

来源覆盖：已读 AIHOT 11月27日页（每天 08:00 出刊，页面写第 220 期）、Hacker News 首页与官方 API、GitHub 热榜（北京时间 11月27日 09:19:43 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以《金融时报》报道与路透社转述、OpenAI 员工原帖、AngelSpec 仓库说明与 arXiv 预印本摘要、DeepMind 官方文章、《自然》论文摘要、铠侠新闻稿和 OpenAI Private Intelligence 产品页为依据。《金融时报》全文页在采集时未能直接打开，报道要点来自检索结果中的文章正文，并与路透社转述交叉核对。预印本中的加速数字是作者自报；IT之家等转述里出现的“单项最高提速 4.2 倍”未写入正文，以免与论文中按基线和负载给出的区间混用。Mass Spec Skills 的约 97% 只适用于库内已有参考谱图的识别，文中已写明。ORIDTP 的 94.2% 是先导多肽相对对照组的小鼠肿瘤体积变化，不是人体试验结果。部分聚合页还提到 Chat 与 Work 模式合并试用，本期未见可独立核对的官方原文，故不写入。劳动或市场评论、以及仍在首页的 Aaronson 博文，已在前一日讨论，这里只保留在快照里。

</details>
