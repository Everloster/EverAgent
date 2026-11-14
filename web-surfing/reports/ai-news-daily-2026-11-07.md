---
title: "AI 行业日报 · 2026-11-07"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-07"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月7日

今天先看三件事。

- Bloomberg 称 OpenAI 已收到约 110 亿美元新融资首批资金，估值 1.25 万亿美元；整轮最高或到约 200 亿美元，尚未完全关账。这是知情人士转述，不是公司官方确认。

- 同一天，Anthropic 拟议 IPO 的潜在买家把估值讨论压到约 1.2 万亿到 1.3 万亿美元，有人低到 1.1 万亿。选举后抛售是报道给出的背景，公司发言人拒评。

- 百度开放 ERNIE-5.5-Flash-Base 预训练终点权重；蚂蚁百灵上线原生多模态 Ling-3.2-flash。前者可下载，后者先走聊天与接口，前两周免费。

## OpenAI 融资：110 亿美元首批到账，估值 1.25 万亿

[TechCrunch](https://techcrunch.com/2026/11/06/openai-reportedly-raises-an-additional-11-billion-at-a-1-25-trillion-valuation/) 与路透社转述 Bloomberg：知情人士称，OpenAI 已完成约 110 亿美元新融资的首批到账，公司估值 1.25 万亿美元。这笔钱是更大一轮的开端，整轮预计数周内关账，总额最高约 200 亿美元。

较九月前后流传的约 300 亿美元、约 1.4 万亿估值目标，当前数字明显下调。Investing.com 的转述还写到，此前三月一轮曾按约 8520 亿美元估值融资约 1220 亿美元。报道把目标收缩与人工智能股抛售、数据中心监管担忧并列，但没有给出投资方名单。OpenAI 尚未公开回应 TechCrunch 的置评请求。

## Anthropic IPO：买家把估值压到约 1.1 万亿起

[Bloomberg Tax 刊出的稿件](https://news.bloombergtax.com/financial-accounting/anthropic-ipo-buyers-see-valuation-as-low-as-1-1-trillion-1)说，正式路演预计下周启动前，潜在买家讨论的估值区间约 1.2 万亿到 1.3 万亿美元；有人低到 1.1 万亿。此前投资者曾向投行报出约 1.4 万亿到 1.5 万亿，十月初市场传闻曾到约 2 万亿。

文中把重新议价与选举后科技股抛售联系起来，并提到纳斯达克 100 指数周四跌 6.4%。部分基金经理公开建议把定价再压低，以降低上市后波动。Anthropic 发言人拒绝置评。这些数字都来自匿名知情人士，不是招股书定稿。

## ERNIE-5.5-Flash-Base：280B 总参数，14B 激活

百度文心于 11 月 5 日在[官方说明](https://ernie.baidu.com/release/ernie-5-5-flash-base/)发布 ERNIE-5.5-Flash-Base。它是稀疏混合专家语言模型，总参数 280B，每 token 激活 14B；预训练约 33.5 万亿 token，训练上下文到 128K，微调与推理可到 1M。

权重是预训练终点、未经中期或后训练的 Base 检查点，在 Hugging Face 提供 FP8 与 BF16 safetensors，许可为 ERNIE 5.5 Flash Base Model License Agreement v1.0。官方说它面向继续训练、领域适配与强化学习研究，不是现成聊天模型。厂商自报在同类开源 Base 对比中偏强；对照模型由其挑选，外部独立复核仍缺。

## Ling-3.2-flash：原生多模态，先免费两周

蚂蚁百灵[更新日志](https://developer.ant-ling.com/en/docs/getting-started/changelog)写于 11 月 5 日：Ling-3.2-flash 总参数 560B、单步激活约 25B，上下文到 1M，原生支持图像、文本和视频。官方强调复杂视觉理解、长程多模态代理、三维理解与交互，以及医疗多模态。

可在聊天界面体验，接口兼容 OpenAI 与 Anthropic 协议；上线后前两周免费。参数体量与上一代 Ling-3.1-flash 接近，但官方强调这次是架构内原生多模态，而不是外挂视觉模块。截至目前文档未宣布开源权重。TechNode 等第三方报道与官方口径一致，本期以官方更新日志为准。

## Cursor 语音通话与 OpenRouter 新路由器

[Cursor 更新说明](https://cursor.com/changelog/voice-chat)于 11 月 6 日推出与智能体的实时语音通话。Agents Window、IDE、网页和 iOS 可用；语音层由 Grok Voice 驱动，编码智能体仍用用户所选模型。通话中可以问差异、查运行状态，或在多 worker 的项目里切换对象。它与听写分开：听写只转文字，语音通话是双向说话。隐私模式下号称零数据留存；日配额与具体套餐费用页面未写清。

[OpenRouter](https://openrouter.ai/blog/announcements/auto-and-auto-code-routers/) 同日发布新一代 Auto Router（`openrouter/auto`）与面向编码的 Auto Code（`openrouter/auto-code`）。公司自报路由步骤 p90 延迟约 0.65 秒，相对旧版约 1.96 秒；Auto Code 在其五项基准上自报接近 Claude Opus 5.5，单任务成本约低 74%。旧 slug 仍可用，治理策略与零留存限制会先裁剪候选模型池。数字来自厂商说明。

## 热榜上，技能包和安全审计技能仍靠前

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 7 日约 09:05 前后采集。星数是当时页面与接口数字。上榜只表示关注，不是当天发布。

[cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) 页面显示当天约增加 2,548，面向编码代理的多阶段安全审计技能，强调可独立核验、机器可读的发现。[mattpocock/skills](https://github.com/mattpocock/skills) 当天约增加 2,070；[NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) 约增加 2,015，继续强调语义图上的确定查询。

编辑器 [zed-industries/zed](https://github.com/zed-industries/zed) 与 [google/skills](https://github.com/google/skills) 也靠前。技能包类仓库连续两天出现在前列。Rails、Rust、React、VS Code 等老牌仓库同期上榜，与人工智能无直接关系。全表在文末。

## 三个人怎么说

**Ryan Greenblatt**，METR 研究员。他[推荐](https://x.com/RyanGreenblatt/status/2118844317817303131) Ajeya Cotra 讨论 METR 研发加速评估的文章，并概括对方观点：两倍提速很剧烈，对员工有效“时间泡”更大，可能快速复合，而我们尚未准备好。帖发于北京时间 11 月 7 日 07:13。这是个人推荐，不是 METR 官方补充声明。

**Miles Brundage**，AVERI 执行主任。他[认为](https://x.com/Miles_Brundage/status/2118829955618664463)第三方评估的价值，在于评估组织自身的身份与偏差也重要；即便信息不全，METR 报告仍突出，因为 METR 的公开记录若有偏向，更常是低估而不是高估进步。帖发于北京时间 11 月 7 日 06:16。这是政策研究者个人判断。

**Nathan Lambert**，开放模型研究者。他[写到](https://x.com/natolambert/status/2118825864494235964)，选举后数据中心放缓的预期下，更看好编码代理与推理算力改写工作方式的路径，并认为这与 METR 报告里 AECI 加速一致；同时强调这不意味着更猛的加速必然到来。帖发于北京时间 11 月 7 日 06:00。链接指向他引用的一篇 Substack。

## 另外几则

**Ajeya Cotra 谈 METR 评估。** 她在[个人文章](https://www.planned-obsolescence.org/p/ai-is-dramatically-accelerating-ai)中称，按公开报告阅读，Anthropic 或已触及 RSP 里“因人工智能而显著加速”的门槛；她未参与该项目，也未看未删减报告。文中把两倍能力进度外推成员工侧更大的“时间泡”，并讨论若加速平滑复合，朴素外推会指向极短时间线。这是个人推演。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

OpenAI 融资相关：TechCrunch 发于北京时间 11 月 7 日 06:53；路透社经 Investing.com 转载时间为 11 月 6 日。Bloomberg 原文受墙，本期以 TechCrunch、路透社转述与 Techmeme 摘要交叉核对。九月目标约 300 亿美元、估值约 1.4 万亿，以及三月约 1220 亿美元、估值约 8520 亿美元，均来自转述，不是 OpenAI 新闻稿。

Anthropic IPO：Bloomberg Tax 时间戳为北京时间 2026 年 11 月 7 日 00:06。The Edge Malaysia、FA Mag、Moneycontrol 等转载口径接近；部分标题写 1.1 万亿，部分视频摘要写 1.2 万亿。正文采用“讨论区间约 1.2–1.3 万亿，有人低到 1.1 万亿”。纳指 100 周四跌 6.4% 来自同一组报道。

ERNIE Base：官方对比表含 DeepSeek-V4-Flash-Base、Hy3-preview-Base、MiMo-V2.5-Base。MMLU 93.3、MMLU-Pro 78.4、HumanEval+ 82.3、LiveCodeBench 40.1 等为厂商同套评估。许可不是 Apache 2.0，商用与营收门槛以许可证全文为准。

Ling-3.2-flash：官方模型页与更新日志一致；Neural Brew 等第三方称暂无开源权重宣布。免费两周写在更新日志。视频理解文档另有时长与帧数限制，正文未展开。

Cursor：更新页日期 2026-11-06。Grok Voice 声线举例含 Ara、Eve、Leo、Rex、Sal。约 10 分钟无说话且无任务会挂断，是文档说明。

OpenRouter：自报每月处理超 2.5 万亿 token、超 10 万人；相对旧路由，无效工具调用约降到 1/4，代理回复被截断约减半。这些是厂商 beta 数据。

Ajeya Cotra：文章日期 2026-11-06。她把员工自报约 12 倍效率与推演中的劳动提速对照，并讨论若加速平滑复合、一年内触及极端超智能的朴素外推。她写明行业尚未达到保护模型权重免于国家级对手的安全门槛。

热榜全表（总星为接口快照，当天增加为热榜页面数字，采集约北京时间 09:05）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [zed-industries/zed](https://github.com/zed-industries/zed) | 93,632 / +306 | Rust | 高性能多人协作编辑器 |
| [NVIDIA/auto-ontology](https://github.com/NVIDIA/auto-ontology) | 9,041 / +2,015 | Python | 用语义图做确定的查询 |
| [rails/rails](https://github.com/rails/rails) | 59,026 / +142 | Ruby | Ruby on Rails |
| [mpv-player/mpv](https://github.com/mpv-player/mpv) | 未记录 / +37 | C | 命令行播放器，与人工智能无关 |
| [rust-lang/rust](https://github.com/rust-lang/rust) | 121,450 / +192 | Rust | Rust 语言 |
| [react/react](https://github.com/react/react) | 252,257 / +248 | JavaScript | Web 与原生界面库 |
| [angular/angular](https://github.com/angular/angular) | 未记录 / +135 | TypeScript | 前端框架 |
| [symfony/symfony](https://github.com/symfony/symfony) | 未记录 / +128 | PHP | PHP 框架 |
| [prometheus/prometheus](https://github.com/prometheus/prometheus) | 67,184 / +148 | Go | 监控与时序库 |
| [google/skills](https://github.com/google/skills) | 22,840 / +534 | Python | Google 的技能包 |
| [microsoft/vscode](https://github.com/microsoft/vscode) | 195,024 / +301 | TypeScript | 代码编辑器 |
| [nushell/nushell](https://github.com/nushell/nushell) | 未记录 / +131 | Rust | 新型 shell |
| [etcd-io/etcd](https://github.com/etcd-io/etcd) | 未记录 / +128 | Go | 分布式键值存储 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 316,722 / +2,070 | Shell | 工程师技能包 |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 64,027 / +2,548 | JavaScript | 编码代理用的安全审计技能 |

来源覆盖：已阅读 AIHOT 11 月 7 日页、Hacker News 首页及三位个人 X 原帖；正文关键数字以原站或一手转述为依据。AI Digest 中文首页仍写明停更，最近一期为 2026-10-23。Bloomberg 原文未能直接阅读，相关融资报道以 TechCrunch、路透社转述与 Techmeme 摘要交叉核对。未获得直接来源或未完成核对的简讯不纳入本期。

</details>
