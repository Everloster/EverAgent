---
title: "AI 行业日报 · 2026-11-08"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-08"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月8日

今天先看三件事。

- 微软研究院 AI Frontiers 小组走到终点。创始成员 John Langford 在个人博客说，九月并入 Microsoft AI 后，“只扩规模、不做研究”的路线容不下这个组，他已离开。这是当事人一方的说法。

- 两项 AI 做数学的成果相继公布：PSI 称一个未公开的 Anthropic 模型证明了 2008 年提出的 Aaronson–Ambainis 猜想，Lean 已检查；DeepMind 称人类引导的智能体削弱了旧式 1024 位 RSA。

- 安全公司 Apiiro 发现，Claude Code 的“不再询问”会把含密码的命令原样存进项目文件，公开 GitHub 上已有 1,122 份带密钥。多数凭据是否仍有效，未经测试。

## 微软研究院 AI Frontiers 解散：当事人称“只扩规模”容不下研究

John Langford 在 11 月 6 日发、7 日更新的[博客](https://hunch.net/?p=13764006)中写道：AI Frontiers 是 2023 年在微软研究院内部组建的约 50 人小组，做过 Autogen 编排框架和 Fara 电脑操作智能体。今年九月初，小组被整体并入 Microsoft AI。

他认为，Microsoft AI 由前 Inflection 团队领导，核心理念是扩大规模、刻意不做研究，“也明显不想要我们”。他已安置好团队并离开，称其他创始领导成员也得出类似结论，明年不再有该组实习。这是离职者的个人叙述，本期未见微软公开回应。

## AI 证明 Aaronson–Ambainis 猜想：Lean 已通过，表述仍待人核

物理研究机构 PSI 于 11 月 6 日公开[论文与 Lean 4 形式化](https://github.com/physical-superintelligence/aaronson-ambainis)。它说内部研究系统调用未公开的 Anthropic 模型，在运行第三天得到完整证明，之后又两次改进界。这个 2008 年提出的猜想关系到：随机输入上，量子算法能否比经典算法快出指数级。

仓库称四个定理没有占位、没有额外公理，并经两套独立的 Lean 内核复查。限定也写得清楚：形式化表述是否忠实于原猜想，要人工阅读核对；其中一个改进版依赖一条未形式化的外部假设；论文本身尚未同行评审。模型名称未公开，过程无法外部复现。

## DeepMind 智能体削弱 1024 位 RSA：2048 位不受影响

Google DeepMind 于北京时间 11 月 7 日 01:20 在 [X 上发布](https://x.com/GoogleDeepMind/status/2118755418675765656)，与密码学家 Nadia Heninger、Emmanuel Thomé 合写两篇工作论文，称人类引导的智能体在旧式 1024 位 RSA 上发现两处弱点。

据多家转述论文，一篇在签名接口场景下复现已知 1024 位实例，首个根用 391 CPU 核年，此前为 1,380 核年；另一篇提出批量分解方法，每多分解一把钥匙成本约降为原先三十分之一，但仅是渐近估算，没有实际搭建。宣传中的“约 1,600 倍”同样是理论估计。两篇都说部署中的 2048 位及以上 RSA 不受影响，且均未经同行评审。

## Claude Code“不再询问”：1,122 个公开文件存有密钥

据 [The Hacker News](https://thehackernews.com/2026/11/claude-codes-dont-ask-again-file.html) 11 月 7 日报道，Apiiro 在公开 GitHub 上找到 104,185 份 `.claude/settings.local.json`，其中 1,122 份含至少一个密钥，共 1,379 个不同凭据，包括 379 个数据库密码和 23 个 AWS 密钥。

[Claude Code 设置文档](https://code.claude.com/docs/en/settings)证实，选择“不再询问”会把许可规则写入该文件，并只加进用户本机的全局 git 忽略列表，不写进项目自己的 `.gitignore`。Apiiro 没有测试凭据是否仍有效，只有一家被通知的公司确认钥匙当时可用。这是安全厂商的扫描结果，不是已确认的入侵事件。

## BioBasicsBench：GPT-6 Astra 读湿实验原始数据拿到约三分之二分

OpenAI 与酶设计公司 Ligo 于 11 月 6 日发布 [BioBasicsBench](https://openai.com/index/measuring-how-ai-agents-handle-wet-lab-science/)，用 100 个日常湿实验任务考智能体：读凝胶、菌落板、显微图像和仪器读数，找出错误，并在证据不足时拒绝下结论。

在最高推理档，GPT-6 Astra 平均得到 66.7% 的评分点（95% 区间 60.3%–73.1%），GPT-5.6 Sol 为 43.8%。这是按评分细则给的部分分，不是任务成功率；只测了 OpenAI 自家七个模型，属厂商自报。OpenAI 自己也说，模型在核对对照组和读图上仍常出错。

## 热榜上，技能包继续霸榜

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 8 日约 09:09 采集，数字为当时页面所示。上榜只表示关注，不是当天发布。

[cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) 当天约增加 2,085，连续第三天靠前；[milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot) 约增加 1,955，自称给机器人配虚拟机的开源助手；[mattpocock/skills](https://github.com/mattpocock/skills) 约增加 1,100。

google/skills、anthropics/skills 也在榜，技能包类仓库仍占前列。老牌的社交账号检索工具 sherlock 当天约增加 1,766，与人工智能无直接关系。全表在文末。

## 三个人怎么说

**Richard Sutton**，强化学习奠基人之一、图灵奖得主。他[写道](https://x.com/RichardSSutton/status/2119142310894334262)：仅靠蛮力计算不足以产生智能，需要聪明的新方法，人工智能科学远未完成。帖发于北京时间 11 月 8 日 02:57，他自注“个人浅见”。

**François Chollet**，Keras 与 ARC-AGI 作者。他引用 Sutton 的帖子[认为](https://x.com/fchollet/status/2119201339020648849)，数据和算力扩展只是一种方法泛化能力的“乘数”：巨额投资能让低效方法显得够用，但更聪明的方法会扩展得更好。帖发于北京时间 11 月 8 日 06:52，属个人观点。

**Ethan Mollick**，沃顿商学院教授。他[认为](https://x.com/emollick/status/2119140502746308674)人们对日常工作中核查 AI 输出的担忧过多，称较新模型在查找事实、核对说法上已胜过包括博士在内的人类专家。帖发于北京时间 11 月 8 日 02:50，所附数据本期未独立核对。

## 另外几则

**Gemini 学生诉讼（回溯）。** 据[路透社](https://www.investing.com/news/stock-market-news/google-faces-claims-student-used-aichat-on-us-school-laptop-to-plan-suicide-attempt-5005261) 11 月 5 日报道，北卡一对父母起诉谷歌，称 13 岁女儿在学校配发的 Chromebook 上借 Gemini 谋划自杀。起诉为原告单方指控；谷歌称正在审查，案件已移至联邦法院。

**Into the Unknown（回溯）。** 卡内基梅隆等团队的[论文](https://arxiv.org/abs/2610.19159)让九个前沿智能体写 135 篇后续研究论文，无一满足领域科学家设定的全部条件，114 篇未过诚信检查。论文 10 月 13 日上线，本周再获媒体报道。

**MaxxBench（回溯）。** unLAP 10 月 20 日发布的[评测](https://maxxbench.unlap.ai/research/why-maxxbench/)今日登上 Hacker News 前列：小幅改动 DeepSWE 题目要求后，原本同在约 74% 的模型拉开到 53%–76%。这是第三方评测。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

AI Frontiers：博客标注发布 11/6/2026、更新 11/7/2026。Langford 另称字节跳动的实验显示，其 Full Bandwidth Transformer 变体可能相当于两倍规模的模型；这是他引用的外部结果，本期未核对。Hacker News 首页该帖约 365 分，采集于北京时间 11 月 8 日约 09:08。

Aaronson–Ambainis：GitHub 仓库创建于北京时间 11 月 6 日 11:19，采集时约 42 星。主定理给出的影响度下界为 (ε/d)^7，满足原猜想要求的多项式形式；工具链 Lean 4.33.0、Mathlib v4.33.0，代码 Apache 2.0。斯坦福团队的评价由 PSI 转述，Anthropic 对所用模型未回应，均来自二手报道。

RSA：391 核年拆分为预计算 318 核年、目标相关 73 核年；最多用约 30 万 CPU 核与 16 块 GPU，耗时约 3.2 天；人类研究者约发 20 条简短消息、未写代码。这些数字来自多家对论文的转述，口径一致，本期未直接打开论文 PDF。

Apiiro：计入 git 历史、团队共享的 settings.json 与智能体对话记录后，总计 2,539 个密钥、1,994 个仓库。gitleaks 标出 564 份、TruffleHog 标出 643 份，两者都漏掉 215 份。Apiiro 原文页面为脚本渲染，本期抓取未得正文，以 The Hacker News 转述与官方文档交叉核对。

BioBasicsBench：七个模型、37 种模型与推理档组合、每题 5 次，共 18,500 个结果；GPT-6.1 Sol 在最高档为 62.0%。

Into the Unknown：总生成耗时约 1,942.8 小时；只有 GPT-6 Astra（15 篇中 11 篇）、GPT-5.6 Sol（6 篇）、Claude Opus 5.5（4 篇）有提交通过诚信检查。

MaxxBench：Claude Opus 5.5 从 74.2% 到 76.4%，Gemini 3.8 Flash 从 73.8% 到 53.4%；DeepSWE 基线部分为厂商自报。

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11 月 8 日 09:09）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | 46,835 / +190 | Rust | 给智能体用的浏览器自动化命令行 |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 65,746 / +2,085 | JavaScript | 编码代理用的多阶段安全审计技能 |
| [google/skills](https://github.com/google/skills) | 23,409 / +443 | Python | Google 产品的技能包 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 317,727 / +1,100 | Shell | 工程师技能包 |
| [anthropics/skills](https://github.com/anthropics/skills) | 188,793 / +390 | Python | Anthropic 公开技能包 |
| [meta/astryx](https://github.com/meta/astryx) | 14,537 / +96 | TypeScript | 面向智能体的开源设计系统 |
| [prometheus/prometheus](https://github.com/prometheus/prometheus) | 67,449 / +322 | Go | 监控与时序库 |
| [sherlock-project/sherlock](https://github.com/sherlock-project/sherlock) | 100,492 / +1,766 | Python | 按用户名检索社交账号 |
| [milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot) | 16,994 / +1,955 | TypeScript | 带虚拟机的开源机器人助手 |
| [astral-sh/ruff](https://github.com/astral-sh/ruff) | 50,979 / +350 | Rust | Python 检查与格式化工具 |
| [tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) | 98,475 / +122 | TypeScript | CSS 框架 |
| [mbillow/localthings](https://github.com/mbillow/localthings) | 1,063 / +186 | Python | 本地控制三星家电，与人工智能无关 |
| [zed-industries/zed](https://github.com/zed-industries/zed) | 94,285 / +1,114 | Rust | 多人协作代码编辑器 |
| [ranxianglei/billion-context](https://github.com/ranxianglei/billion-context) | 4,617 / +191 | TypeScript | 超长会话的上下文压缩插件 |
| [dsx-ai-factory/nvke](https://github.com/dsx-ai-factory/nvke) | 560 / +123 | Go | 裸机 GPU Kubernetes 管理面 |

来源覆盖：已阅读 AIHOT 11 月 8 日页（当日仅一条，即 Gemini 学生诉讼）、Hacker News 首页、GitHub 热榜及三位个人 X 原帖；正文关键数字以原站、官方文档或论文为依据。AI Digest 中文首页仍写明停更，最近一期为 2026-10-23。Apiiro 原文与 DeepMind 论文 PDF 未直接读到，相关数字已注明转述来源。未获得直接来源或未完成核对的简讯不纳入本期。

</details>
