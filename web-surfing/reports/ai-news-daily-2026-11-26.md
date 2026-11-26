---
title: "AI 行业日报 · 2026-11-26"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-26"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.news/daily"
---
# AI 日报 · 2026年11月26日

今天先看三件事。

- Anthropic 11月25日发表文章，复盘把 Messages API 从 Python 迁到 Rust 的做法。官方称，从 2024 年初到 2026 年秋，该 API 流量大约增长了 1,800 倍；迁移后每请求 CPU 约降低 70%，首 token 中位时间约缩短 20%，且未停服，也没有冻结功能开发。公开流量是在 2026 年 9 月切到 Rust 的。这些都是该公司自己的工程叙述。

- 一个由 42 名总检察长组成的两党联盟，反对 Character.AI 在破产程序中拍卖平台及用户私密聊天记录。加州总检察长 11月24日、科罗拉多州总检察长 11月25日分别发表声明，称涉及逾 2,100 万个美国账户的聊天记录，其中逾 210 万个登记为未成年人账户，拍卖原定 12月1日。这是尚未裁定的法律反对，不是法院已禁止拍卖。

- OpenAI 11月24日在公开数学仓库中加入预印本，声称方阵乘法的指数在任意域上都精确等于 9/4，也就是为 10 月给出的上界补上了匹配的下界。仓库把这些稿件称为模型产出的「原始研究数据」，并写明部分尚未形式化的结果「可能有问题」。这是声称，不是已经完成的外部独立核验。

## Anthropic 复盘 Messages API 迁到 Rust：官方称校验比写代码更难

[Anthropic 11月25日文章](https://www.anthropic.com/research/migrating-api-to-rust)由 Lance Martin 等人撰写。Messages API 是客户以及 Claude Code、Cowork 等自家应用访问 Claude 的主要入口，2023 年用 Python 写成。官方写，从 2024 年初到 2026 年秋，流量大约增长了 1,800 倍；到 2025 年末，每个请求都要经过校验、提示词转换、分词和安全分类，回复还要把文本、思考和工具调用分开，Python 在对象创建、内存回收和任务交接上的开销变得难以承受。

团队先把解析模型输出的部分改成 Rust、再从 Python 调用，CPU 大约只降了 8% 到 10%，却让每个 token 在两种语言之间往返三次。官方认为这点收益不值得增加的复杂度。到 2026 年 5 月，Anthropic 合并的代码中已有八成以上由 Claude 编写；Claude 大约用一周写出了核心请求路径的第一版 Rust 实现。真正的瓶颈变成了校验：Python 版仍在继续改动，对账目标在变；同一请求的回复并不确定，输出不同不一定是缺陷；公司又不能阅读客户请求，难以直接看出两套实现分叉在哪里。

做法是把正在运行的生产 API 本身当成校验器。团队在生产流量上做对照，比较模型调用前后的各个阶段；为了避开回复的随机性，模型只跑一次，再把同一份输出回放到 Rust 侧，要求两边精确一致。发现差异后，系统自动派代理去修复。官方自报：迁移后每请求 CPU 约降低 70%，首 token 中位时间约缩短 20%，服务没有中断，功能开发也没有冻结。公开流量在 2026 年 9 月切到 Rust。文中图注写明，CPU 数字来自单一区域，内存来自全部生产环境，时延则来自客户的 Claude Code 请求，而且统计窗口更短。这些都是该公司自己的测量。

## 42 州总检察长反对拍卖 Character.AI 用户私密聊天记录

[加州总检察长 Rob Bonta 11月24日新闻稿](https://oag.ca.gov/news/press-releases/attorney-general-bonta-opposes-asset-sale-characterai-amid-child-safety-concerns)写，一个由 42 名总检察长组成的两党联盟，反对 Character.AI 出售其平台，以及逾 2,100 万个美国账户的私密聊天记录；其中逾 210 万个账户登记为未成年人。声明称，聊天内容将连同 IP 地址等元数据在 2026年12月1日拍卖，买方将获得其中可能包含的敏感信息，尽管该公司曾向消费者表示不会出售个人信息。[科罗拉多州总检察长 Phil Weiser 11月25日声明](https://coag.gov/press-releases/weiser-challenges-auction-of-millions-of-private-character-ai-conversations/)给出了同样的账户规模，并写明拟议条款下，买方没有义务尊重用户删除或限制使用数据的请求。

新闻稿还写：目前披露的唯一竞买人是 2026年11月13日在特拉华州注册的 Smirks and Pangs Acquisition LLC，次日被选为拍卖的基准出价方；销售合同未写明母公司或投资人，并允许只向 Character.AI 披露姓名的外国投资者。各州要求法院拒绝拟议销售条款，否定该公司作为领先竞买人的地位，并拒绝其提出的 35 万美元「分手费」。它们至少要求把未成年人的聊天和其他敏感数据排除在外，并附加保护用户的条件。联盟认为，进入破产程序并不能使公司摆脱保护这些数据的法律，包括未经父母核实许可不得分享 13 岁以下儿童个人信息的联邦规定。这些都是检方主张，不是已经认定的违法事实。

[TechCrunch 11月25日报道](https://techcrunch.com/2026/11/25/state-ags-fight-character-ais-plan-to-auction-off-users-private-chats/)的发布时间是太平洋时间上午 9:35，对应北京时间 11月26日 01:35。报道转述了上述规模和竞买人信息，并提到 Character.AI 曾在博文中向用户保证，其信息仍受隐私政策保护。该报道同时回顾，一个类似但不完全相同的联盟，此前已反对向迪士尼出售许可；那是另一笔交易，并不包括用户聊天。Character.AI 的破产本身此前已有报道，本期新进展是总检察长对这次拍卖提出反对。拍卖能否进行、条款会否修改，仍待法院处理。

## OpenAI 预印本声称矩阵乘法指数精确为 9/4，仍待外部核验

OpenAI 公开数学仓库的[更新记录](https://github.com/openai/math/blob/main/history.md)写，2026年11月24日新增两个结果族、九篇稿件，并附有部分结果的 Lean 形式化。其中一篇预印本题为《The matrix multiplication exponent is nine fourths》。[摘要](https://github.com/openai/math/blob/main/preprints/The-matrix-multiplication-exponent-is-nine-fourths-November-24-2026/paper.pdf)声称：方阵乘法的指数在任意域上都是 9/4；上界此前已知，本文给出匹配的下界。文中还写，对每个 n ≥ 2，把两个 n×n 矩阵相乘的形式算术电路，至少需要 n^{9/4}/2 个乘法或除法门。仓库[说明](https://github.com/openai/math/blob/main/README.md)把这些稿件定位为由未具名内部模型产出的「原始研究数据」，而不是已打磨的学术论文，并写明：并非全部结果都有 Lean 形式化，部分尚未形式化的结果「可能有问题」。

同一天加入的还有其他高声称稿件，包括一篇自称给出确定性强多项式时间线性规划算法、回应 Smale 第九问题，以及一篇自称否定有界简单有理多面体的多项式 Hirsch 猜想。这些同样是仓库中的声称。仓库还写，11月23日发布的《VP and VNP are different》已被 11月24日的部分稿件涵盖；该结果此前已在[11月24日日报](./ai-news-daily-2026-11-24.md)的简讯中出现过讨论，本期不再当作新的独立头条。

这些声称尚未经过数学共同体的独立核验，也不能写成已经定论。Hacker News 首页在采集时，Scott Aaronson 11月25日至26日的[博文](https://scottaaronson.blog/?p=10379)位于靠前位置。他写，自己正试图重新估量眼下进展的分量，并对出现 ω > 2 的下界表示震惊；这是个人反应，不是对证明的审核。OpenAI 研究员 Sébastien Bubeck 的原帖见下文，同样是当事人的评价。

## Sand.ai 发布 480B 视频模型 MAGI-2

[Sand.ai 11月24日官方博文](https://sand.ai/blog/magi-2/)宣布推出旗舰模型 MAGI-2。官方称，它由 2026 年 8 月的 MAGI-2 Preview（总参数约 114B，激活约 6B）扩大到总参数 480B、激活约 28B，预训练数据大约增加到 4 万亿 token。公司写，它可以原生生成最长 30 秒、1080p、每秒 25 帧的音视频，支持在一次请求中使用最多 20 个图像、视频或音频参考，并提供时间轴控制和视频编辑。开源与详细技术报告仍写为即将发布，因此目前不能把它写成已经开放权重。

官方自报：在 Artificial Analysis Video Arena v2.1 的四项任务平均 Elo 上，MAGI-2 相对 Preview 提高了 151.8 分，从 998.5 升到 1150.3。这是该公司引用的基准数字，不是独立复现。[官方定价页](https://platform.sand.ai/docs/model-pricing/)写明，magi-2 在 1080p 下为每秒 0.08 美元，同时提示暂不支持充值。博文也列出了局限，例如高速运动偶尔会出现轨迹或连贯性问题，中远景二维动画的局部运动可能过平滑，复杂声景的层次和物理真实感仍不足。聚合页里把质量与价格拿去和 Seedance 对比的说法，来自第三方实测，这里不以它作依据。该文日期为 11月24日，落在本期 48 小时扩展窗口内。

## 热榜上，漏洞挖掘技能包仍是当天增量最高

[GitHub 热榜](https://github.com/trending)在北京时间 11月26日约 09:13 采集，当时页面列出 16 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) 当天约增加 1,652，总星约 23,034，增量仍最高，已连续多日领先。[cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) 约增加 1,141，总星约 73,048。[firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) 约增加 1,135，总星约 210,054。[HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) 约增加 1,106，总星约 65,684。[obra/superpowers](https://github.com/obra/superpowers) 约增加 903，总星约 326,625。与人工智能没有直接关系、但当天增量仍靠前的是下载器 [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3)，约增加 951，总星约 18,252。其余条目和全表放在文末。

## X上顶尖AI大佬最近都说了什么

本期精选三位研究者或行业人士的个人原帖。时间均为北京时间。以下是个人观点或个人研究观察，不是已核验的事实。

Sébastien Bubeck 是 OpenAI 的人工智能研究者，个人简介写明他曾任微软人工智能副总裁和杰出科学家。他在 11月25日 09:33 的[原帖](https://x.com/SebastienBubeck/status/2125402576145572334)中写：10月6日那批结果里，矩阵乘法指数有一个干净的新上界 9/4；此后模型一直在做这个指数的下界，而过去对下界几乎一无所知。他称今天宣布 9/4 是紧的，并说这是他从未想过有生之年能看到的结果。帖中还提到，按 Yin Tat Lee 及其合作者的旧结果，这也意味着线性规划可在 n^{9/4} 时间内求解。稍后一条跟帖则谈到，线性规划现在可以在强多项式时间内求解。这些是参与方的个人评价和引申，不能代替对预印本的独立核验；其中线性规划的时间上界，也不应直接写成新下界的推论。

Sebastian Raschka 是机器学习研究者和工程师，个人简介写明他曾任统计学教授，并著有从零训练大语言模型的教材。他在 11月25日 22:06 的[原帖](https://x.com/rasbt/status/2125591837691793581)中写：今天的代码审查，感觉像是往同事的代码上贴海量单元测试；可这些测试又由谁来审查呢？这是他对当前开发流程的感叹，不是一项评测结论。

Lucas Beyer 是现任职于 Meta 的研究者，个人简介写明他此前曾在 OpenAI、DeepMind 和 Google Brain 工作。他在 11月26日 04:03 的[原帖](https://x.com/giffmana/status/2125681858117845411)中，回复他人观察时写道：自己也注意到了这一点；Opus 很适合交谈，但经常编造内容，或得出错误结论。这是个人使用体验，不能外推成对该模型的系统评价。

## 简讯

AI Digest 中文版仍显示停更于 2026年10月23日，本期只核验一次，未重试。AIHOT 第 219 期以 Anthropic 的 Messages API 迁移为头条，与已回读的官方文章一致。黄仁勋复任、实体清单，以及 OpenAI 蛋白质设计和 Claude 的 Install as app，已在[11月24日](./ai-news-daily-2026-11-24.md)与[11月25日](./ai-news-daily-2026-11-25.md)日报写过，本期不再当作新消息。

[METR 11月24日博文](https://metr.org/blog/2026-11-24-interpreting-a-recent-acceleration-in-pretraining-loss/)讨论 OpenAI 最近公布的、在固定自有代码持有集上的基座模型对数困惑度。METR 写，自 2026 年初以来，该损失下降速度大约是 2022 年至 2025 年的七倍。这是对[11月23日日报](./ai-news-daily-2026-11-23.md)已记录的那组公开数据的解读，不是新的原始测量。文章明确写，机构内部对如何解释这一加速、以及应否据此改写能力预测，尚无一致看法，并列举了过拟合、基准与困惑度哪一项更接近真实能力等不同可能。

[Thinking Machines Lab 11月24日客座文章](https://thinkingmachines.ai/news/training-a-scalable-forecasting-agent/)由 Mantic 团队与 Thinking Machines 合作撰写。文中称，他们在 Tinker 上对 Inkling 2 Small 做后训练，得到一个能自己检索并提交概率分布的预测智能体。官方自报：在 200 道来自 Metaculus、Polymarket、Kalshi 及自身平台的持有数值问题上，准确度大致接近 Fable 5.2（medium），单次预测成本约为后者的 1/15；预测时点均在 2026年9月15日之后，也就是该基座的知识截止日期之后。这些是合作方自己的评测，不是独立复现。

Hacker News 采集时，[Google Research 仓库](https://github.com/google-research/google-research/tree/master/cogentic_research_papers)新增的 Cogentic 论文条目约有 443 分，标题涉及整数分解和离散对数等。这是仓库发布，不是经过同行评审的结论，本期未把这些论文全文作为头条复核。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

采集时点均为中国时区 UTC+8。AIHOT 11月26日页在 09:12:57 读取，HTTP 200，页面写第 219 期、每天 08:00 出刊。GitHub 热榜在约 09:13:00 读取。Hacker News 首页在 09:12:59 读取，官方 API 条目分数约在 09:13:26 核对。AI Digest 中文版在 09:12:57 读取。Anthropic、加州与科罗拉多州总检察长、TechCrunch、OpenAI 数学仓库与预印本 PDF、Sand.ai、Thinking Machines、METR 与个人 X 原帖，随后在 09:14 至 09:18 核对。热榜数字以 09:13 的页面为准。

Hacker News 首页在 09:13 的前若干条及当时点数大致为：1Password Security Incident（1,103 分，链向 1Password 博文）、Holy shit holy shit holy shit holy shit: The magnitude of what’s now happening（854 分，官方 API 随后为 855 分，链向 Scott Aaronson 博文）、Much shorter version of GRH Lean verification from Anthropic（244 分，官方 API 随后为 246 分）、The New York Times warns photographers not to update Photoshop over AI features（183 分，链向 The Verge）、GPT-6.2 Astra is the first model to beat Googlers' code golf records（233 分）、Slow Ubuntu security response times（121 分）、Nfs2root: A 12-year-old pre-auth remote root in the Linux kernel's NFS server（77 分）。与人工智能更直接相关、但当时位置不一的还有 Jev is probably Qwen3.5-35B-A3B（202 分，链向第三方推测）、The polynomial Hirsch conjecture is false（118 分，官方 API 随后为 119 分，链向 OpenAI 预印本 PDF）和 Google releases Cogentic papers on integer factorization, discrete logs and more（443 分，链向 Google Research 仓库）。点数会变动，这里只记录采集时的首页快照。

GitHub 热榜全表（总星 / 当天增加，均为 09:13 页面原样）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面说明 |
| --- | --- | --- | --- |
| [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter) | 23,034 / +1,652 | Python | 面向漏洞挖掘和外部红队的 Claude Code 技能包 |
| [obra/superpowers](https://github.com/obra/superpowers) | 326,625 / +903 | Shell | 代理技能框架与软件开发方法 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 65,684 / +1,106 | Python | 让各类软件更便于代理通过命令行使用 |
| [jingyaogong/minimind](https://github.com/jingyaogong/minimind) | 70,959 / +826 | Python | 从零训练小型语言模型的教程项目 |
| [cursor/plugins](https://github.com/cursor/plugins) | 19,534 / +416 | TypeScript | Cursor 插件规范与官方插件 |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | 210,054 / +1,135 | TypeScript | 为代理提供搜索、抓取和数据接口 |
| [nginx/nginx](https://github.com/nginx/nginx) | 33,375 / +176 | C | 官方 Nginx 源码，与人工智能无关 |
| [openvinotoolkit/openvino](https://github.com/openvinotoolkit/openvino) | 12,654 / +191 | C++ | 推理优化与部署工具包 |
| [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) | 73,048 / +1,141 | HTML | 给编程代理用的图表设计技能 |
| [mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill) | 75,115 / +945 | Python | 汇集近期公开讨论并做综述的代理技能 |
| [google-labs-code/stitch-skills](https://github.com/google-labs-code/stitch-skills) | 12,985 / +355 | TypeScript | 与 Stitch MCP 配合的代理技能库 |
| [mjmirza/app-store-compliance](https://github.com/mjmirza/app-store-compliance) | 6,481 / +858 | Shell | 应用商店常见拒审模式与提交前检查 |
| [Tracer-Cloud/opensre](https://github.com/Tracer-Cloud/opensre) | 15,522 / +348 | Python | 面向持续集成可靠性的开源代理 |
| [toeverything/AFFiNE](https://github.com/toeverything/AFFiNE) | 78,497 / +574 | TypeScript | 开源知识库 |
| [XiaoYouChR/Ghost-Downloader-3](https://github.com/XiaoYouChR/Ghost-Downloader-3) | 18,252 / +951 | Python | 下载器，与人工智能没有直接关系 |
| [zhouxiaoka/autoclip](https://github.com/zhouxiaoka/autoclip) | 16,163 / +880 | Python | 开源人工智能视频剪辑工具 |

来源覆盖：已读 AIHOT 11月26日页（每天 08:00 出刊，页面写第 219 期）、Hacker News 首页与官方 API、GitHub 热榜（北京时间 11月26日约 09:13 的页面 HTML）和多位个人 X 原帖。AI Digest 中文版页面仍显示停更于 2026-10-23，只查一次，未重试。正文关键事实以 Anthropic 官方文章、加州与科罗拉多州总检察长新闻稿、TechCrunch 报道、OpenAI 数学仓库说明与预印本 PDF、Sand.ai 官方博文与定价页、Thinking Machines 客座文章和 METR 博文为依据。加州新闻稿导语写 42 名总检察长，文中一句引语写 45 名，正文按导语及具名名单计为 42。聚合页把 MAGI-2 与 Seedance 的对比写成作者实测，正文不以它为依据。劳动论文《AI-Assisted Programming and Labor Demand》标注日期为 2026年11月6日，超出本期窗口，不作为头条。1Password 安全事件位于 HN 首页首位，与本期人工智能主题无直接关系，仅保留在快照里。

</details>
