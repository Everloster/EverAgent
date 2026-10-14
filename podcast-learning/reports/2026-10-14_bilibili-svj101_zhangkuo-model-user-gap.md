---
title: "硅谷101（再访张阔）：榜单99分与真实61%之间——E255 对篇"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（B 站视频版）
source_url: https://www.bilibili.com/video/BV186pW6kEzU
show: "硅谷101播客"
episode: "模型越来越强，为什么用户没感觉？再访阿里国际站总裁张阔（2026-10-09）"
host: "Yiwen（硅谷101主持人）"
guest: "张阔（阿里国际站总裁）"
duration: "46:15"
duration_seconds: 2775
transcript_segments: 1694
chapters: 4（按主题自组）
polished: true
polished_by: "Claude (pi)（结构化精编，约 raw 的 10.5%（按汉字数），头部已标注）"
polished_at: 2026-10-14
status: archived
created: 2026-10-14
updated_on: 2026-10-14
transcript_path: reports/transcripts/2026-10-14_bilibili-svj101_zhangkuo-model-user-gap.transcript.txt
polished_transcript_path: reports/transcripts/2026-10-14_bilibili-svj101_zhangkuo-model-user-gap.polished.txt
pipeline: opencli bilibili user-videos（关注列表选题）→ yt-dlp --print 拿 B 站简介（shownotes）→ eacli podcast plan/run（Razer whisper large-v3/CUDA，**B 站域名白名单放行实证**）→ eacli pull（86750B）→ 精编（SKILL v2）
source_shownotes_chapters: false
notable_correction: "Axio Work/XUwork/Excel Work/ExoWork→Accio Work｜Cloud Cowork/Corework→Claude Cowork｜Cloud Code→Claude Code｜Grogbot/Grogball→Grok Bot｜网单→榜单｜科特巴→哥德巴赫｜第三pack→Design Pack｜职务→植物｜Honest→Harness｜帕利托/Pilot/parallel投资→帕累托（路由）｜淘气→淘系电商｜商家策→商家侧｜step shot→snapshot｜Post-trim→post-train｜Shack→Shark Tank；disbuild[?]/进队[?]/反弹[?]/antipride[?] 保留"
hanzi_chars_raw: 14564
total_chars_raw: 57618
hanzi_chars_polished: 1559
total_chars_polished: 3395
---

# 硅谷101再访张阔：榜单与真实之间的落差

## ⚡ 速览

- **E255 对篇落地**：同一 107-task 研究在两个播客的数字口径完全一致（61%/3.69 vs 9+ 美元/L1-L4/七大类）——数字可信度大幅提升。
- 本期新增最有价值的两组数据：**商家任务难度从 L1 持续爬到 L4**（使用行为证据）+ **五大高频 use case**（跨平台利润核算/多平台发布/客服复盘/交易预警/供应链全周期）。
- 对子皓"在场"论的正面反驳："**跑 7×24 不挂 means nothing——长程要按场景分类（定时/事件/季度复盘），上云只是 basic 需求**"。

## 概览

- **核心问题**：模型榜单 99 分+，商家真实经营无同幅提升——"coding/数学/agentic 得分高与电商能完成更多工作，没有那么大相关性"。107-task（开源、七大类、L1-L4、snapshot 持续增加）：前沿模型无人干预 ~61%。**"商业 AGI"定义：给定 budget/供应链边界，agent 经营一定比人赚更多钱**。
- **Agent=Model×Harness×Context（乘法）**：Harness 精力最多（电商天生长程）；Context 20 年平台数据优势；Model 现在也要自己后训练（千问小尺寸 post-train 接近 frontier top；Model/Harness/serving 三方同时打磨）。
- **用得起**：帕累托路由（L3 以下→小模型；auto 模式；绑定自家模型的 agent 无法路由——对照 OpenRouter/Fireworks）；107 任务 Accio 3.69 美元 vs Codex/Claude Code 9+（1/3）；每版本 eval 防腐化。
- **难度爬坡**（发布第一天至今截图）：L1 问问题→L2 交任务→L3 复杂任务→L4 经营判断级——商家持续 push 更复杂问题。五大 use case：①跨平台利润核算（流水≠利润）②多平台发布/update/大促③客服复盘④2B 交易预警⑤供应链全周期（Edward 案例：Design Pack→广深厂商→HS code→多平台销售；Excel 月级→24 小时）。
- **人的判断**：支付按钮/idea 靠不靠谱/产品 taste/市场预测/budget 分配；多 agent 冲突不做"统一 agent"——老板以"一本账"（毛利/规模/速度）裁断。
- **上云 vs 长程**：上云=basic（没上云=功能没做完）；长程分定时/事件驱动/季度复盘三类；"7×24 不挂 means nothing"。
- **SaaS/中美/全球化**：SaaS 与 AI 互相集成（ontology：大学生也搞不清企业数据意味着什么）；AI 产品第一天 global（无语言问题+LUI 门槛降——新设计范式，前提需求接近）；CoCreate 洛杉矶 15000 人；冠军案例：**15 岁初中生年销 100 万英镑**（自动降温宠物毛巾）、Christian Reed（客户含施耐德+SpaceX，年营收几千万美金）。
- **Astra**："去 benchmark 上看评分；3D/computer use 突破≠通用商业 agentic 强——打保票不是 AGI"。

## 增量观点（polished 之外的连接与分析）

1. **同题双源交叉验证完成**：[[2026-10-08_rss-guigu101_e255-zhangkuo|E255]] 与本期的核心数字（61%/3.69 vs 9+/107/L1-L4/七大类）逐项一致且出自同一人不同访谈——把"厂商自测无第三方复核"的 Limitations 降了一级（数字至少不受单一播客编辑失真影响）。E255 的独有贡献是公式与成本结构，本期的独有贡献是**使用侧行为数据**（难度爬坡+五大 use case）——两篇合起来才是 107-task 研究的完整拼图。
2. **"难度爬坡 L1→L4"是 IDC 五阶段的电商实证版**：[[2026-09-22_xiaoyuzhou-tulong-zhishu_ai-production-stage|IDC 五阶段]]讲行业渗透阶段，张阔给出的是**单个产品内用户行为的难度分布随时间上移**——微观机制与宏观阶段论的第一次对上；也与 [[2026-10-09_ximalaya-ailianjinshu_juzi-personal-agent|橘子]]"agent 协作使用率低得吓人"（负样本）互为表里：使用率低但难度在爬。
3. **"跑一周不挂 means nothing"与子皓"continuous running"正面相撞**：[[2026-10-12_xiaoyuzhou-42zhangjing_zihao-ambi|Ambi]]把"一直在跑"当本体论（在场 vs 异步），张阔按商业视角拆解：**长程不是一种能力而是一组场景分类（定时/事件/季度）**——"在场"论需要回答"在场时到底执行哪一类"，这是预测对之外新增的第三组可追踪分歧。
4. **15 岁冠军案例给橘子"受益者画像"补了极端样本**：橘子说真实受益者是 30-35 岁有人脉积累的小老板（需要"支使肌肉"），15 岁初中生年销 100 万英镑说明**当 agent 足够强，"支使肌肉"的前提可以部分绕过**（平台 context 替代个人经验）——与 [[2026-10-11_xiaoyuzhou-crossing_yage-ai-strong|鸭哥]]"0 人公司"同向：AI+平台基础设施在替代"人脉/团队"这类传统前置条件。
5. **"AI 产品第一天 global"是本周全球化讨论的第三票**：[[2026-10-08_xiaoyuzhou-daxiaoma-keji_v95-china-us|V95]]从地缘看"中国创业者的题材广度优势"、橘子说"中国 personal agent 创业不成立"，张阔给出修正项：**产品全球化易（语言+LUI），但 harness/context 必须分区域重做**——恰好与他自己的乘法公式自洽；"需求接近→第一天 global 成立"是可证伪的边界条件。
6. **Ontology 一词接上阮良的数据治理线**：[[2026-09-23_xiaoyuzhou-weishijie_ruanliang-ai-org|阮良]]讲企业数据要先治理 AI 才能用，张阔点破难点本质——**"请个大学生也搞不清企业各数据意味着什么"**：企业语义层是比数据清洗更深的壁垒，也是 SaaS 存活（与 AI 互相集成）的资本。

## 关键人物

- **张阔**：阿里国际站总裁；曾负责淘系商家平台（2011-2016）；107-task benchmark 发起人。
- **Yiwen**：硅谷101主持人。
- Edward / 15 岁英国初中生 / Christian Reed（MIT）：CoCreate 商家案例。

## 引用书目

无书目；107-task 开源 benchmark（官网可查各模型评分含 Astra）。

## 关键概念词

榜单 99 分 vs 真实 61%（相关性断裂）｜107-task（开源/七大类/L1-L4/snapshot）｜商业 AGI 定义（同边界下比人赚更多钱）｜Agent=Model×Harness×Context（乘法/零项归零）｜帕累托路由（auto 模式/绑定模型无法路由）｜用得起的 AI｜难度爬坡 L1→L4｜跨平台一本账（流水≠利润）｜ontology（企业语义层）｜上云=basic/长程三分类（定时/事件/季度）｜7×24 不挂 means nothing｜AI 第一天 global（前提：需求接近）｜防腐化 eval｜Design Pack｜红线固定/路线不写死

## 关键观点（原话）

> "Coding 的市场渗透率我估计 99%……第二个垂直的赛道渗透可能都远远小于这个数字。"

> "很多的榜单都已经打到 99 分了，但我们自己在日常使用的时候，又没有感觉到像说的这么好。"

> "必须是一个用得起的 AI，才是一个有价值的 AI——它是一个日常经营使用的产品。"

> "你追求模型 7×24 跑一周不挂，不挂 means nothing，如果没有解决你的问题的话。"

> "AI 这个产品很有意思，就是它的第一天就是 global——这可能是一个新的产品设计范式。"

> "说 GPT-6 Astra 是 AGI，我现在给你打保票的，肯定不是 AGI。"

## 关键数字

| 数字 | 含义 |
|---|---|
| ~99% vs ≪ | coding 渗透率 vs 第二垂直赛道（口播估计） |
| 107 / 61% | 开源电商任务数 / 前沿模型无人干预通过率 |
| 3.69 vs 9+ 美元 | 107 任务全跑完：Accio vs Codex/Claude Code（1/3） |
| L1-L4 / 七大类 | 难度分级 / 任务类别（snapshot 持续增加） |
| 20 列×十几供应商×月级 → 24 小时 | Excel 比选流程 vs agent 后 |
| 15000 人 | CoCreate 洛杉矶到场人数 |
| 100 万英镑/年 | 15 岁初中生冠军年销售额（口播） |
| 几千万美金/年 | Christian Reed 年营收（客户含施耐德/SpaceX，口播） |
| 20 多年 | 平台 context 积累时长 |
| +20% / +130% | alibaba.com 整体搜索 / 多模态搜索增长（沿 3 月首访） |

## Limitations

- polished 为精编版（约 raw 10.5%）；中英混杂口播，长段删节。
- 嘉宾为阿里国际站总裁，Accio Work 为其产品——**107-task/1/3 成本/增长数字全部为厂商自述**；本报告价值在于与 [[2026-10-08_rss-guigu101_e255-zhangkuo|E255]] 的交叉一致性，非第三方验证。15 岁冠军/Christian Reed 案例为大会宣讲口径未核。
- "disbuild back and forth"[?]、"竞对判断"[?]、"商家反弹"[?]、"anti-pride 版本"[?]（沿 E255 未解）等口播未还原。
- 本集为 B 站视频版转写，与硅谷101音频版内容可能存在剪辑差异；shownotes 取自 B 站简介（无时间戳章节）。

## 思考与追问

1. **我真正理解了什么？**同题双源的真正价值不是数字复核，而是**两期各自暴露了研究的不同侧面**：E255 给了公式与成本结构（供给侧），本期给了使用行为数据（需求侧）——"榜单与真实的落差"最终落在"难度爬坡"上：用户不是不用，是在往 L4 爬。这比"61% 及格都费劲"的静态表述乐观得多。
2. **我还没搞懂什么？①107-task 官网各模型最新评分（Astra 跑分"再过两天可查"——现应已出）；②五大 use case 各自的占比/通过率；③"anti-pride 版本"到底是什么（两期都未还原）；④15 岁案例的产品与店铺链接。
3. **下一步读什么/做什么？①查 107-task 官网 Astra 评分（预测对/三组分歧的第一个可验证数据点）；②把"难度爬坡 L1→L4"并入 [[2026-10-12_xiaoyuzhou-42zhangjing_zihao-ambi|子皓]] 预测对的追踪卡（"半年后可数字化任务 100%" vs "61%" vs 本期难度爬坡——三源互证）；③五 use case 对照 EverAgent 个人场景（跨平台一本账=个人财务版值得记入 open-questions）。
