---
title: "AI 行业日报 · 2026-11-09"
domain: "web-surfing"
report_type: "daily_summary"
status: "in_progress"
updated_on: "2026-11-09"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily"]
source_url: "https://aihot.virxact.com/daily"
---

# AI 日报 · 2026年11月9日

今天先看三件事。

- 英伟达董事会宣布独立调查：起因是媒体报道黄仁勋成为外国情报行动目标。黄仁勋同日致信员工承认婚外情，表示支持调查。董事会称没有理由认为国家安全或公司机密受损。

- 猫王遗产方和 Eminem 的音乐出版方分别起诉 AI 音乐公司 Suno。前者援引田纳西州专门保护声音与肖像的 ELVIS 法案，后者指控未经授权用 269 首作品训练。

- 一项来自真实编码会话的新基准显示，十个模型中最好的 GPT-6 Astra 平均满足约七成验收条件，但只有 26.4% 的任务全部做对。

## 英伟达董事会启动独立调查，黄仁勋致信承认婚外情

英伟达于美国时间 11 月 8 日（周日）发布[董事会声明](https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors)：鉴于近期有报道称创始人兼 CEO 黄仁勋“成为外国情报行动的目标”，由独立董事组成的委员会在外部律师协助下展开调查。董事会称没有理由认为国家安全或公司机密受损，但会审视全部信息，并对黄仁勋有信心。

同日公司发布黄仁勋[致员工信](https://nvidianews.nvidia.com/news/a-message-to-our-company)，他承认对妻子不忠，并就新闻中的国家安全疑虑表示全力配合调查。据 [CNBC](https://www.cnbc.com/2026/11/08/jensen-huang-nvidia-china-spy-congress.html) 转述《纽约时报》，美国情报评估认为新加坡 Megaspeed 公司高管 Alice Huang 受中国国家安全部招募接近黄仁勋。这是基于情报备忘录的媒体报道，英伟达此前称双方往来与一般客户会面无异。

## 猫王与 Eminem 版权方起诉 Suno：声音克隆与训练数据两条线

据法律资讯站 [Copyright Now](https://copyrightnow.com/news/elvis-presley-enterprises-v-suno-elvis-act-right-of-publicity-ai-music-copyright-complaint-ndcal/) 整理的起诉书，Elvis Presley Enterprises 等原告于 11 月 6 日在北加州联邦法院起诉 Suno（案号 3:26-cv-13398），指控其生成的歌曲模仿猫王声音，违反田纳西州 ELVIS 法案，并称 Suno 用他们持有的 859 首作品训练模型。

Eminem 作品的出版方 Eight Mile Style 另案起诉，涉及 269 首作品。[The Verge](https://www.theverge.com/ai-artificial-intelligence/1029533/elvis-eminem-suno-ai-music-clone-lawsuit) 11 月 8 日报道称，Suno 表示会筛查上传内容并拦截点名艺人的提示词。以上均为原告单方指控，尚无法院认定；ELVIS 法案用于 AI 公司是较新的法律尝试。

## 苹果被曝加速 Siri 智能体化，最早明年能持续执行任务

据 [The Verge](https://www.theverge.com/ai-artificial-intelligence/1029552/apple-siri-ai-agentic) 11 月 8 日转述彭博社 Mark Gurman：CEO John Ternus 正催促软件负责人 Craig Federighi 加快 Siri 路线图。iOS 27.3 预计让 Siri 细粒度操作苹果自家应用，比如在相册里旋转裁剪图片、整理 Safari 标签页。

更大的变化是接入第三方应用，例如通过 Grubhub 下单，预计在明年春季。Gurman 认为苹果最早明年可能让 Siri 像智能体一样追踪目标、连续行动。这是记者依据消息人士的报道与个人判断，苹果未公开确认，具体时间表可能变化。

## 英国公共机构被 AI 生成投诉“堵塞”

[《卫报》](https://www.theguardian.com/technology/2026/nov/08/ai-clog-public-bodies-local-authorities-onslaught-chatbot-generated-correspondence) 11 月 8 日报道，议员办公室、地方政府、学校和法院正收到大量由聊天机器人撰写的投诉、信息公开申请和法律挑战。一名工党议员办公室资深个案员说，收到的邮件约有一半带有 AI 痕迹，处理起来更复杂、更耗时。

地方政府律师组织负责人称，投诉过去平均约两页，现在多数长了十倍，最长的约 200 页，还常引用不相关辖区的判例。研究者把这种现象称为“智能体泛滥”。这些多为受访者的估计和个案，不是系统统计；但伦敦交通局一个财年收到 4,769 份信息公开申请，创下纪录。

## Co-Design Bench：编码智能体平均做对七成，全对仅约四分之一（回溯）

阿里巴巴与复旦等团队的[论文](https://arxiv.org/abs/2610.35138)从 26,314 个真实用户编码会话中整理出 273 个改网页应用的任务，配 2,331 条隐藏验收条件，有的请求附带图片、音频、视频或文档。论文 10 月下旬上线，11 月 8 日起被媒体集中报道。

在统一的 Claude Code 框架下测十个模型，最好的 GPT-6 Astra 每题平均通过 69.9% 的条件，但全部条件都通过的任务只有 26.4%；Opus 5 为 18.3%。评分由大模型裁判加反驳复核完成，人工只抽查了 200 组输出。论文还发现，换一套执行框架，模型之间的排名就可能变化。

## 热榜上，技能包与智能体工具仍在前列

[GitHub 热榜](https://github.com/trending)在北京时间 11 月 9 日约 09:08 采集，当时页面只列出 9 个仓库，数字为当时所示。上榜只表示关注，不是当天发布。

[milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot) 当天约增加 1,439，连续第二天上榜；[meta/astryx](https://github.com/meta/astryx) 与 [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) 各增加八百余；[anthropics/skills](https://github.com/anthropics/skills) 约增加 792。

裸机 GPU Kubernetes 管理面 [dsx-ai-factory/nvke](https://github.com/dsx-ai-factory/nvke) 约增加 345，总星不足千。社交账号检索工具 sherlock 当天约增加 2,373，排在首位，与人工智能无直接关系。全表在文末。

## 三个人怎么说

**Nathan Lambert**，开源模型研究者，曾共同主导 Ai2 的 Olmo，写 Interconnects 通讯。他[认为](https://x.com/natolambert/status/2119536592608268710)，若科技股因黄仁勋事件继续大跌，回头看这可能是本轮热潮的第一次大调整：债务过度、选举结果、黄仁勋事件接连发生。帖发于北京时间 11 月 9 日 05:04，属个人市场判断。

**Gary Marcus**，认知科学家、长期的生成式 AI 批评者。他引用一段 Anthropic CEO 谈 AI 冲击就业的视频[写道](https://x.com/GaryMarcus/status/2119408004764504458)：就业和生产率几乎没变，人们却在听 CEO 随口给的数字。帖发于北京时间 11 月 8 日 20:33；他稍后补充说该视频是 18 个月前的旧视频。

**Miles Brundage**，AI 政策研究者，曾任 OpenAI 政策研究负责人，现为 AVERI 执行董事。他[写道](https://x.com/Miles_Brundage/status/2119198403620139365)：要撑过接下来几年，两党之间、产业与政府之间都得合作，至少在联邦层面。帖发于北京时间 11 月 8 日 06:40，为简短个人观点。

## 另外几则

**llama-modchip。** 一个个人[开源项目](https://github.com/synchopate/llama-modchip)自称能在 64GB 内存、不用 GPU 的电脑上运行 2,843 亿参数的 DeepSeek-V4-Flash，量化到每权重约 1.71 位，生成约每秒 9–15 个词元。今晨登上 Hacker News 前列，数字均为作者自测。

**高盛限用 Claude Code（回溯）。** 据[彭博法律](https://news.bloomberglaw.com/capital-markets/goldman-restricts-traders-and-bankers-from-using-some-ai-tools) 11 月 2 日报道，高盛十月更新内部指引，把 Claude Code 和 GitHub 编码工具限于工程师使用，多数交易员和银行家不能再用。相关帖今晨在 Hacker News 再获热议。

**Elephant-Goldfish 插件（回溯）。** 谷歌 10 月 22 日在[开源博客](https://opensource.googleblog.com/2026/10/introducing-elephant-goldfish-model-plugin.html)发布这个插件：先由长上下文会话写设计文档，再让无对话记忆的子智能体审查，之后才写代码。谷歌称数千名工程师在用，11 月 8 日再获媒体报道。

<details>
<summary>其余数字、热榜全表和采集说明</summary>

英伟达：董事会声明与致员工信均标注 2026 年 11 月 8 日。CNBC 报道发布于美国东部时间 11 月 8 日 13:06（北京时间 11 月 9 日 02:06），称三位众议院共和党委员会主席已请黄仁勋于 11 月 18 日出席闭门简报，民主党议员另行要求调查或作证；公司称黄仁勋将继续担任 CEO。

英伟达公告本身未提婚外情对象，也未点名任何国家。Hacker News 上董事会声明帖约 369 分、致员工信相关帖约 313 分，采集于北京时间 11 月 9 日约 09:08。

Suno：猫王案起诉书 51 页，五项诉由，含 ELVIS 法案、田纳西普通法形象权、直接版权侵权、规避技术保护措施和移除版权管理信息；原告按每部作品法定上限计算的版权赔偿主张约 1.29 亿美元。起诉书称 Suno 用 yt-dlp 等工具绕过 YouTube 加密取得作品，这是“依据信息与信念”的指控。Eminem 案的 269 首数字来自 Copyright Now 另一篇案情整理与 Variety 报道，本期未读起诉书原文。

苹果：Verge 转述称，Gurman 原话认为 Dots、Muse、Grok 等竞品已能追踪目标并连续执行，苹果“没有太多选择”。彭博原文为付费内容，本期未直接读取。

英国 AI 堵塞：“智能体泛滥”一词出自柏林赫蒂学院数字治理中心、合作 AI 基金会和 GovAI 的研究者。GMB 工会称，有统计的议员办公室个案量翻倍或更多；英国四至六月新开劳动仲裁单人诉讼同比增长 28%，但报道未把增长归因于 AI。

Co-Design Bench：分两条赛道，多模态编辑 100 题、仓库编辑 173 题；GPT-6 Astra 在两条赛道上全对率分别为 41.0% 与 17.9%。“69.9%”是逐题通过比例再平均，不是全部条件的总通过率。每次运行上限三小时、120 轮。附录显示，固定模型、更换 codex、opencode、qwen-code 三套框架时，两模型的差距波动 10–16 个百分点。论文作者含阿里巴巴员工，Qwen 模型位列其中，有利益相关；GPT-6 Astra 仍排第一。

llama-modchip：README 标注 v2.4.0、Apache 2.0；称 284B 模型在 16 核 Zen 5 上预填充约 44.4 词元/秒，峰值内存约 57.6 GiB，256K 上下文。1.71 位量化对质量的影响未见独立评测。Hacker News 该帖约 355 分。GitHub API 因限流未取得创建时间与星数。

高盛：发言人称工具会交给“最适合长期使用的人”；兼做工程与量化的 strats 岗位不受限。该帖在 Hacker News 约 576 分，链接的是二手站点，本期以彭博法律与 Quartz 报道为准。

热榜全表（总星与当天增加均为热榜页面数字，采集约北京时间 11 月 9 日 09:08；当时页面仅 9 行）：

| 仓库 | 总星 / 当天增加 | 语言 | 页面上的一句话 |
| --- | --- | --- | --- |
| [sherlock-project/sherlock](https://github.com/sherlock-project/sherlock) | 103,561 / +2,373 | Python | 按用户名检索社交账号，与人工智能无关 |
| [dsx-ai-factory/nvke](https://github.com/dsx-ai-factory/nvke) | 857 / +345 | Go | 裸机 GPU Kubernetes 管理面 |
| [milind-soni/OpenMausBot](https://github.com/milind-soni/OpenMausBot) | 18,269 / +1,439 | TypeScript | 带虚拟机的开源机器人助手 |
| [anthropics/claude-quickstarts](https://github.com/anthropics/claude-quickstarts) | 19,426 / +32 | Python | Claude 应用快速上手示例集 |
| [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | 47,613 / +815 | Rust | 给智能体用的浏览器自动化命令行 |
| [meta/astryx](https://github.com/meta/astryx) | 16,822 / +875 | TypeScript | 面向智能体的开源设计系统 |
| [anthropics/skills](https://github.com/anthropics/skills) | 189,664 / +792 | Python | Anthropic 公开技能包 |
| [google-deepmind/mujoco](https://github.com/google-deepmind/mujoco) | 16,425 / +41 | C++ | 通用物理仿真器 |
| [ranxianglei/billion-context](https://github.com/ranxianglei/billion-context) | 5,162 / +460 | TypeScript | 超长会话的上下文压缩插件 |

来源覆盖：已阅读 AIHOT 11 月 9 日页（当日仅一条，即英伟达董事会调查）、Hacker News 首页、GitHub 热榜及三位个人 X 原帖；正文关键事实以公司公告、论文、起诉书整理或原报道为依据。AI Digest 中文版上期已确认停更于 2026-10-23，本期未重试。METR 与 Redwood 关于 Hugging Face 入侵事件的调查在 11 月 8 日被聚合站重新列出，但原文发布于 8 月 26 日，不属新进展，未纳入。

</details>
