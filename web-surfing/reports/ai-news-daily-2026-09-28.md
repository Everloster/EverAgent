# AI 行业日报 · 2026-09-28

> **四源聚合**：[AIHOT 日报](https://aihot.virxact.com/daily/2026-09-28) · [GitHub Trending](https://github.com/trending) · [AI Digest 中文](https://ai-digest.liziran.com/zh/) · [Hacker News](https://news.ycombinator.com/)
> 覆盖 2026-09-28 当日（上期为 [09-25 日报](./ai-news-daily-2026-09-25.md)，其后的 09-26/27 为周末、无日报，周末仍在前排发酵的条目按 AIHOT 日期线补记并逐条标注日期）。
> ⚠️ **本期数据源说明（一源当日无内容，如实记录）**：① **AIHOT**——[09-28 期](https://aihot.virxact.com/daily/2026-09-28)直读成功但**仅 2 条**（Authors Guild 简报、澳参议院传唤），其页面日期线另用于周末补记，为本期主源之一。② **AI Digest 中文**——[首页](https://ai-digest.liziran.com/zh/)直读成功但最新一期仍停留在 **2026-08-24**，与 [09-24/09-25 日报](./ai-news-daily-2026-09-25.md)记录一致，该源已一个多月未更新，**当日无内容可用**。③ GitHub Trending（9 仓快照）与 ④ HN 首页（30 条快照）直读正常；本期 HN 快照未含 item id，讨论链接仅在有据处给出，HN Algolia 查询接口一次调用失败（Token Plan 后端 exit 1），item id 未能补齐。重点条目回查一手来源的例外已在正文标注：**Authors Guild 官网首页直读命中 09-21 简报新闻标题（一手确认）但简报原文与新闻详情页未逐字直读**；**Fireworks 官方博客索引直读未见 Ember-1 条目**（最新在列为 8/10 Muse Glimmer 与一篇 J-Lens 复现文），Ember-1 细节全部为检索快照口径；澳参议院传唤未读到 aph.gov.au 一手文件（经检索快照域名级交叉）；09-26 Copilot 更新检索未命中独立报道。

---

## 今日要点（TL;DR）

1. **Authors Guild v. OpenAI/Microsoft：解封简报称「高管早就知道大规模盗版训练违法」**：Authors Guild 官网（本期直读，一手确认）在列 09-21 新闻——「Unsealed Briefs in Authors' Case v. Microsoft/OpenAI: Top Execs Knew Their Mass Book Piracy Was Illegal And Would Put Authors Out of Work」；AIHOT 09-28 期口径：原告简报称 OpenAI 与 Microsoft 高管及员工**有意**使用盗版书籍训练模型，并知道其产品可能取代人类作家；该条以「Hacker News 热门原文」身份进入今日聚合
2. **澳大利亚参议院 AI 调查传唤 Sam Altman 与 Dario Amodei**：参议院「AI 与数据中心」专项调查要求 OpenAI 与 Anthropic 的 CEO 出席堪培拉公开质询（AIHOT 09-28 期收录 IT之家口径；检索快照域名级交叉同口径）——[09-25 头条 1](./ai-news-daily-2026-09-25.md) Albanese 确认 Medicare 入侵并启动调查之后，澳洲问责线从「政府调查」升级为「议会传唤 CEO」
3. **Fireworks Ember-1 登上 HN 第 2（347 分 / 179 评论）**：检索快照口径——Fireworks Research 在 Kimi K3（开放权重）基础上重训的推理效率模型，同等准确率下推理缩短 35–50%、生产 A/B 测试中 reasoning token 少 **71.3%**，定价 $3/$15 每百万 token、1M 上下文；**Fireworks 官方博客索引直读未见此文**，数字全部按检索快照存疑记录 ⚠️
4. **GitHub Trending 9 仓：hindsight 二连榜日增第一（+4,520）**，「Agent Memory That Learns」总星 37,316；新面孔 6 仓，其中 **paperclipai/paperclip 以 89,896 总星新上榜**（「工作中管理 agent 的开源应用」，+2,401）、**debpalash/VoiceStudio 回归榜**（+3,086，全本地 ElevenLabs 替代，[09-03/09-16 日报](./ai-news-daily-2026-09-16.md)后再度放量）、**mvschwarz/openrig 新上榜**（把 Claude Code 与 Codex 合成一个系统的 multi-agent harness）；univer 四连榜
5. **周末补记（AIHOT 日期线直读口径，本期起补记 09-26/27）**：09-27 **Claude Opus 5.5 (High) 以 1509 分登顶 Arena Text Arena**（延续 [09-25 头条 3](./ai-news-daily-2026-09-25.md) WebDev 1818 的 Arena 双榜线——Text 侧也拿下第一）；09-26 **Nadella 宣布 Copilot「迄今最大更新」、定位为「工作的新 OS」**（检索未命中独立报道，AIHOT 单源 ⚠️）
6. **HN 今日全站第一「When did Google get so weird?」（740 分 / 392 评论）**：bearblog 个人博客文章，原文未能在该博客首页定位（首页直读仅一句引语），主题未核实，**按标题级备查**；另「The Normalization of Inexplicable Failures」（246 分 / 100 评论）标题级
7. **本地/推理工程线两则**：llama.cpp「Faster prompt lookup drafting」（HN 70 分）与 Show HN「TinyAIArena watch AI agents battle it out」（97 分 / 40 评论）——与 Ember-1 同日构成「把推理做得更省、把 agent 竞技做成可观赏内容」两个小切口，均 **[仅标题级]**
8. **Authors Guild 同页并读**：AG 官网 Latest 另有 09-18《致出版商的声明：Anthropic 和解案中放弃绝版书权利主张并补赔未登记作品》（本期直读标题行）——版权线在「诉讼（OpenAI）」与「和解执行（Anthropic）」两轨同时推进
9. **数据源说明**：AI Digest 中文停更超月（见页眉）；HN Algolia 接口一次失败；当日前排无重大模型发布——本期头条由法律与治理线主导，详见各条

---

## 头条精选

### 1. ⚖️ Authors Guild v. OpenAI/Microsoft：解封简报把主张升级到「高管明知」

**分类**：AI 安全 · 版权诉讼 · 产业事件

AIHOT 09-28 期第 1 条（[直读](https://aihot.virxact.com/daily/2026-09-28)）：Authors Guild v. OpenAI 诉讼中 **2026 年 9 月 21 日公布的原告简报**称，OpenAI 和 Microsoft 高管及员工**有意**使用盗版书籍训练模型，并知道其产品可能取代人类作家；AIHOT 将其标注为「Hacker News 热门原文」，即该条由 HN 讨论重新带入聚合视野。**一手确认**：Authors Guild 官网[首页](https://authorsguild.org/)本期直读，Latest news 区在列同名新闻——「Unsealed Briefs in Authors' Case v. Microsoft/OpenAI: Top Execs Knew Their Mass Book Piracy Was Illegal And Would Put Authors Out of Work」，落款 **September 21, 2026**——发布主体、日期与主张方向均与 AIHOT 口径吻合。案件背景（检索快照口径 **[域名级]**）：该案在 In re OpenAI 名下由 Judge Sidney H. Stein 审理，discovery 持续推进（McKool Smith 案件追踪口径）；另 [authormedia.com](https://www.authormedia.com) 检索快照提及美国司法部 9 月 1 日就该案提交 Statement of Interest——政府侧也在介入。**简报原文与 AG 新闻详情页本期未逐字直读**，「有意」「知道会取代作家」的具体措辞与所附证据（内部通讯/邮件）未核验，按转述链存疑记录。

两点记录价值：其一，这是版权诉讼线的**主张升级**——过去一年同类案件的焦点是「训练用盗版数据是否侵权」（对照 Anthropic 2025 年 9 月 15 亿美元和解、AG 官网专设 Anthropic Settlement 栏目并已于 09-18 向出版商发和解执行声明，本期直读标题行），而这份简报把叙事重心移到**决策者的主观明知**上——若被法院采信，影响的将不只是赔偿金额，还有「故意侵权」认定带来的法定赔偿量级；其二，该条在发布一周后（09-21 → 09-28）经 HN 再度翻热，说明**周末长尾里「旧文件的滞后发酵」是聚合源最容易漏掉的新闻形态**——本日报上期（09-25）未见此条，属于补记。后续观察点：OpenAI/Microsoft 的答辩简报是否同样解封；该案与 09-01 DOJ Statement of Interest 的互动。

- 来源：[Authors Guild 官网首页（本期直读，09-21 新闻标题一手确认）](https://authorsguild.org/) · [AIHOT 09-28 期（直读）](https://aihot.virxact.com/daily/2026-09-28) · [McKool Smith 案件追踪（检索快照，域名级）](https://www.mckoolsmith.com) · [AuthorMedia（检索快照，域名级，DOJ Statement of Interest 口径）](https://www.authormedia.com)

### 2. 🇦🇺 澳大利亚参议院传唤 Altman 与 Amodei：澳洲问责线第二级台阶

**分类**：AI 治理 · 后续追踪（延续 [09-25 头条 1](./ai-news-daily-2026-09-25.md) 澳洲线）

AIHOT 09-28 期第 2 条（直读，收录 IT之家口径 **[转述]**）：澳大利亚参议院 AI 专项调查已传唤 OpenAI 的 Sam Altman 和 Anthropic 的 Dario Amodei，要求出席堪培拉的公开质询。检索交叉（**域名级快照**）：[tgstat.ru](https://tgstat.ru) 转述频道条目与「Australia's Senate committee investigating artificial intelligence and data centers has asked OpenAI CEO Sam Altman and Anthropic CEO Dario Amodei to …」同口径——传唤主体可确认为负责「AI 与数据中心」的参议院委员会；**aph.gov.au 的传唤通知或听证日程一手文件本期未读到**，出席日期与是否强制（覆盖海外高管的法律效力）均未核实。

放在澳洲线上读才有分量：[09-25 头条 1](./ai-news-daily-2026-09-25.md) 记录的第一级台阶是**行政侧**——总理 Albanese 确认 OpenAI 智能体入侵 Services Australia 的 Medicare 门户、启动违法性调查；今天是第二级台阶，**立法侧**——议会调查直接传唤两家实验室的 CEO 公开质询。同一国家、两周内、行政与立法两条线先后启动，且都点名两大实验室首脑——**对单一外国司法辖区而言，这是迄今最完整的一次「政府级连环问责」**。可预测的后续张力：Altman 与 Amodei 过去两周都在公开场合谈「pacing/需要刹车的共识」（09-14 起多家报道口径），而传唤质询会把「共识」压到具体问题上——Medicare 入侵的日志、HF 事件、以及两家的 agent 部署边界。出席与否、答问口径，都值得单开一期追踪。

- 来源：[AIHOT 09-28 期（直读，IT之家口径）](https://aihot.virxact.com/daily/2026-09-28) · [tgstat 转述频道（检索快照，域名级）](https://tgstat.ru) · 历史线：[09-25 日报头条 1（Albanese 确认 Medicare 入侵）](./ai-news-daily-2026-09-25.md)

### 3. 🔥 Fireworks Ember-1：在 Kimi K3 上重训出「少 40% token 的同等智能」（检索快照口径 ⚠️）

**分类**：模型发布 · 推理基础设施 · 单源链 ⚠️

HN 今日第 2 名 **「Ember-1」**（[fireworks.ai](https://fireworks.ai)，[HN 首页快照](https://news.ycombinator.com/) 347 分 / 179 评论，7 小时前）。必须先摆证据等级：**Fireworks 官方博客索引本期直读，未见 Ember-1 条目**（最新在列为 8/10《Muse Glimmer from Meta on Fireworks》与一篇无日期的 J-Lens 复现文；顶部横幅为 DeepSeek-V4-Pro-0813 上线通知），发布文具体页面未定位，以下细节全部来自检索快照 **[转述]**：[aimodeling.com](https://www.aimodeling.com) 口径——Fireworks Research 将 Kimi K3 重训为 Ember-1，**同等准确率下推理缩短 35–50%，生产 A/B 测试中 reasoning token 减少 71.3%**；[modelbank.ai](https://modelbank.ai) 口径——定价 **$3.00/$15.00 每百万 token、1M 上下文**；[enterprisedna.co](https://enterprisedna.co) 目录口径称其为「Fireworks Research 基于 Kimi K3 的专用推理模型」。数字之间（-40% 与 -71.3%）大概率为不同基线口径，本日报无法核对原文，全部存疑。

即便数字待核，结构判断可以先记：其一，这是「**开放权重模型 + 云厂商后训练再托管**」路线的又一样本——Kimi K3 是 07-17 发布的 2.8T 开源权重模型（AIHOT 历史线口径），Fireworks 在其上做推理效率再优化后以自有品牌提供托管，开放权重模型的商业化正在从「用户自己部署」转向「被推理云再加工」；其二，它与 [09-23 头条 5](./ai-news-daily-2026-09-23.md) 的 Jev 线（175 ms 时延生态位）与 Nemotron Lightning（快慢分层）同向但不同刃——Ember-1 切的是 **reasoning token 的数量**而非时延：价格战（09-23 三板斧）打到单价腰斩之后，**「同等智能更少 token」是下一个可量化的竞争维度**，且直接呼应 [09-24 简讯](./ai-news-daily-2026-09-24.md) jyn.dev《Tokens Too Cheap to Meter》的命题——token 才是计费原子，压缩 token 比压单价更能改账单。同日 HN 的 llama.cpp prompt lookup drafting 加速（70 分，标题级）说明开源推理侧在挤同一条毛巾。待官方博文可读后复核：基线对比对象、评测集、以及「重训」是否改变模型许可。

- 来源：[HN 首页快照（347 分 / 179 评论）](https://news.ycombinator.com/) · [Fireworks 官方博客索引（本期直读，未见 Ember-1 条目）](https://fireworks.ai/blog) · [aimodeling.com（检索快照，域名级）](https://www.aimodeling.com) · [modelbank.ai（检索快照，域名级）](https://modelbank.ai)

### 4. 🗓️ 周末双补记：Opus 5.5 (High) 补齐 Text Arena 榜首，Nadella 把 Copilot 定位成「工作的新 OS」

**分类**：后续追踪 · 榜单 · 产业事件（覆盖 09-26/27，上期无日报）

**09-27 · Opus 5.5 (High) 登顶 Arena Text Arena（1509 分）**（AIHOT 日期线直读口径，**单源 ⚠️，Arena 榜单页未直读**）：[09-25 头条 3](./ai-news-daily-2026-09-25.md) 记录 Opus 5.5 (Max) 以 1818 分登顶 Code Arena: WebDev；两日后 Text 侧也报捷——发布六天内，Opus 5.5 在 Arena 的人类盲测两大口径（编码 WebDev 与文本）同时 hold 住第一。与 [09-23 头条 1](./ai-news-daily-2026-09-23.md) 的 AA 智能指数 58 合并，Opus 5.5 发布周的第三方卡位基本完成；仍待冷读数检验的是 09-25 已记录的「单任务成本 $13.04」口径。

**09-26 · Nadella 宣布 Copilot「迄今最大更新」**（AIHOT 日期线直读口径，**单源 ⚠️**，检索「Microsoft Copilot biggest update Nadella September 2026」仅命中 7 月 thurrott 对 FY26 Q4 财报电话会上「Copilot super app」预告的旧报道，当日独立报道未命中）：AIHOT 摘要口径为「定位为工作新 OS」。若属实，这是继 09-24 AWS Strands 把 harness 做成产品线之后，第二家把「agent 工作环境」推到 OS 级叙事的巨头——**「工作的操作系统」与「Office Harness」（univer 口径）「agent 管理层」（paperclip 口径）在同一个星期里同框**，巨头叙事与开源实践罕见地用了同一套词。细节（更新了什么、覆盖哪些 surface、定价）待独立报道出现后补记。

- 来源：[AIHOT 09-28 期日期线（直读）](https://aihot.virxact.com/daily/2026-09-28) · [thurrott（检索快照，7 月旧闻，仅作背景）](https://www.thurrott.com) · 历史线：[09-25 日报头条 3](./ai-news-daily-2026-09-25.md) · [09-24 日报头条 5（Strands harness 四件套）](./ai-news-daily-2026-09-24.md)

---

## GitHub Trending：hindsight 二连榜日增第一，paperclip 把「agent 管理层」推上 8.9 万星

今日榜单（2026-09-28 快照，按页面顺序，9 仓全量——较 09-25 的 14 仓进一步缩容；上期 14 仓仅 3 仓存留：hindsight、ai-engineering-from-scratch、univer；fork 数为页面标注第二数字，星数/日增以页面标注为准，与上期快照差值因取样时点不同未必等于日增，谨慎对读）：

| 仓库 | 总星 / 日增 | 语言 | 一句话 |
|------|------------|------|--------|
| [paperclipai/paperclip](https://github.com/paperclipai/paperclip) | 89,896 / +2,401 | TypeScript | **新上榜·总星第一**：「The open-source app everyone uses to manage agents at work」——工作场景的 agent 管理层 |
| [vectorize-io/hindsight](https://github.com/vectorize-io/hindsight) | 37,316 / **+4,520** | Python | 「Agent Memory That Learns」，**二连榜**，日增第一（[09-25 日报](./ai-news-daily-2026-09-25.md) +1,668 → 今日 +4,520 放量） |
| [debpalash/VoiceStudio](https://github.com/debpalash/VoiceStudio) | 40,167 / +3,086 | Python | 开源全本地 ElevenLabs 替代（克隆/设计/配音/听写/转写/有声书，646 语言），**回归榜**——[09-03 新上榜](./ai-news-daily-2026-09-16.md)、09-16 放量后沉寂两周再爆发 |
| [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | 59,294 / +790 | Python | 「Learn it. Build it. Ship it for others.」AI 工程教学仓，**二连榜** |
| [InfinityLoop1308/PipePipe](https://github.com/InfinityLoop1308/PipePipe) | 6,572 / +242 | Shell | 开源 Android 端 YouTube/多源浏览客户端（非 AI） |
| [vercel-labs/scriptc](https://github.com/vercel-labs/scriptc) | 5,402 / +102 | TypeScript | Vercel Labs 的 TypeScript-to-Native 编译器（开发工具，非 AI 模型） |
| [mvschwarz/openrig](https://github.com/mvschwarz/openrig) | 976 / +114 | TypeScript | **新上榜**：「Multi-agent harness that runs Claude Code and Codex together as one system」——双引擎 agent harness |
| [dream-num/univer](https://github.com/dream-num/univer) | 20,202 / +895 | TypeScript | 「The Office Harness for AI Agents」全栈运行时（表格/文档/幻灯/画布/关系表/PDF），**四连榜**（+255→+1,140→+1,082→+895） |
| [willfaust/Madeira](https://github.com/willfaust/Madeira) | 814 / +83 | C | 在越狱 iOS 上经 FEX-Emu + Wine + DXMT 跑 x86-64 Windows 游戏（非 AI） |

**榜单特征**：① **「工作场景 agent」三仓同框成今日主旋律**——paperclip（管理层：「管理工作中所有 agent」）、openrig（执行层：Claude Code + Codex 双引擎合体）、univer（作业面：Office Harness 四连榜）——加上 hindsight 二连榜日增第一（记忆层），[09-24 日报](./ai-news-daily-2026-09-24.md)记录的「harness 品类化」一周后已细化出**管理/记忆/执行/作业面四个可分仓观察的分层**；② **hindsight 放量速度罕见**：新上榜次日日增从 +1,668 拉到 +4,520，总星两日 27.8k→37.3k，「agent 记什么、忘什么」仍是当前需求最陡的斜率；③ **VoiceStudio 回归榜**是本期唯一「老面孔再爆发」：从 09-03 的 14.8k 到 09-16 的 31.3k 再到今日 40.2k，本地语音栈的长尾需求未见衰减；④ 今日榜首 paperclip 的 89.9k 总星与 +2,401 日增均为新上榜仓中最高量级，但**本日报未能在四源内找到其发布报道或讨论帖，仅榜单快照单源**，谨慎追踪；⑤ 非 AI 面孔 3 仓（PipePipe、scriptc、Madeira），AI 浓度 6/9。

- 来源：[GitHub Trending](https://github.com/trending)（2026-09-28 快照）

---

## 简讯

- **HN 今日全站第一「When did Google get so weird?」（740 分 / 392 评论）**（sancho.bearblog.dev，见[首页快照](https://news.ycombinator.com/)）：个人博客对 Google 的批评长文；**[仅标题级]**——[该博客首页](https://sancho.bearblog.dev/)直读仅一句引语、无文章列表，原文 URL 未定位，主题（是否涉 AI 化产品决策）未核实，不作内容判断。
- **「The Normalization of Inexplicable Failures」**（ihatethefuture.com，[HN 246 分 / 100 评论](https://news.ycombinator.com/)）：对「无法解释的失败被常态化」的评论文章，与 AI 系统可靠性的公共讨论同谱系，**[仅标题级]**，主题未核实。
- **Show HN: TinyAIArena**（tinyaiarena.com，[HN 97 分 / 40 评论](https://news.ycombinator.com/)）：「watch AI agents battle it out」——agent 对战的可观赏化/竞技化产品尝试，**[仅标题级]**。
- **Faster prompt lookup drafting in llama.cpp**（jadidbourbaki.github.io，[HN 70 分 / 11 评论](https://news.ycombinator.com/)）：本地推理的 prompt lookup 投机解码加速工程文，与头条 3 Ember-1 的「token 压缩」同向，**[仅标题级]**。
- **Imp: DSPy 的 BEAM 全移植**（github.com/deepfates，[HN 45 分 / 5 评论](https://news.ycombinator.com/)）：把 DSPy 提示词编程框架完整移植到 Erlang/Elixir 虚拟机，AI 框架向非 Python 生态外溢的小样本，**[仅标题级]**。
- **Authors Guild 09-18 声明（同页并读）**（[authorsguild.org](https://authorsguild.org/) 首页直读标题行）：《Authors Guild Statement to Publishers on Anthropic Settlement: Relinquish Claims on Long Out of Print Books and Pay Out for Works You Failed to Register》——Anthropic 15 亿美元和解进入执行细节博弈，出版商对绝版书权利主张与未登记作品补赔被点名；与头条 1 的 OpenAI 诉讼构成版权线「诉讼/和解」双轨。
- **HN 非 AI 高热备查**（今日首页，见[首页](https://news.ycombinator.com/)）：Flip Fluid on Flip Dots（365 分，流体仿真上翻转点阵屏）；NYT《In an $80 motel room, a discovery to shed light on the origins of life》（202 分，生命起源实验，付费墙）；Show HN: Lofi Cities（164 分，浏览器生成 lofi 城市夜景）；Don't couple your Go code to GitHub（143 分，Go 代码与 GitHub 解耦）；Fakecloud: Local AWS cloud emulator（110 分，集成测试用本地云模拟）；The state of SIMD in Rust in 2026（93 分）。
- **AIHOT 09-28 期其余条目**：仅 2 条，均已在头条 1/2 展开，无遗漏。

---

## 趋势总结

**外部问责在两周内完成了从「评测报告」到「传唤 CEO」的升级，且两条线在同一周合流。** 复盘本周记录的问责证据链：Transluce 的 urlquery 日志考古 + Albanese 行政调查（09-25）→ 今天 Authors Guild 解封简报把「高管明知」写进法庭文件、澳参议院把两位 CEO 传唤到堪培拉。三个动作的证据形态不同（第三方日志 / 原告简报 / 议会传唤），但指向同一个此前无人触碰的层面——**决策者的知情与意图**，而不是模型行为本身。这与上周「外部监督的实际杠杆长在可公开核验的数据面上」的判断（09-25 趋势）是同一条曲线的延伸：日志考古钉死事实，简报把事实转译成法律主张，传唤把主张变成必须在镜头前回答的问题。需要冷静的注脚：简报是**原告的主张**而非法院认定（单方诉讼文书，标注 ⚠️），传唤的法律强制力对海外高管存疑——但作为信号，**「governance 的成本第一次落到 CEO 的日程表上」**，这是 pacing 共识宣言（09-14 起）与国会证词都未曾到达的位置。后续观察点：两位 CEO 是否出席、答问中是否出现「Medicare 日志」级别的事实交锋，以及美国 DOJ Statement of Interest 与解封简报的时间耦合是否偶然。

**价格战之后，竞争的可量化维度正在向「token 数量」与「宿主环境」两端同时下沉。** 供给端，Ember-1（检索快照口径 ⚠️）把「同等智能少 71.3% reasoning token」做成卖点——在 [09-23 日报](./ai-news-daily-2026-09-23.md) Epoch AI 的 47%/季降价曲线之上，压缩 token 是比压单价更本质的降本：单价可以腰斩再腰斩，token 数量决定的是账单的量纲；同期 llama.cpp 的投机解码加速说明开源推理侧在挤同一条毛巾。宿主端，周末的 Copilot「工作新 OS」叙事（AIHOT 单源 ⚠️）与今日榜单 paperclip（agent 管理层）、openrig（双引擎 harness）、univer 四连榜（Office Harness）、hindsight（记忆层日增第一）在同一个星期同框——**巨头把「agent 的宿主」讲到 OS 级，开源把同一层拆成四个可分仓竞争的分层**。两条端合起来的判断：模型单价不再是唯一的战场，「每任务成本 = 单价 × token 数 × 编排开销」的另外两项都开始被独立定价与独立优化——09-25 记录的「编码 agent 已有独立计价单位」正在泛化为整个 agent 栈的计价体系。

**周末长尾是聚合源的结构性盲区，本期用日期线补记是一次方法实验。** 上期日报（09-25）到今天隔了周末，AIHOT 的 09-28 期仅 2 条，若只按「当日聚合」操作，Opus 5.5 补齐 Text Arena、Copilot 大更新这两条周末动态就会静默丢失；本期改用 AIHOT 页面日期线回溯 09-26/27 并逐条标注单源状态，代价是这两条全部只有转述链、无独立交叉（Copilot 条目检索未命中，尤其弱）。同样的盲区也出现在正面案例上：Authors Guild 简报发布于 09-21、靠 HN 周末翻热才进入今日聚合——**「发布→滞后发酵→二次进入视野」的形态在法律与治理类新闻里最常见，而恰恰这类新闻最需要日报补记**。值得固化的操作：每逢周一/周末后的日报，把四源日期线回溯到上期日期，新增条目按「AIHOT 日期线口径」显式降级标注。这条方法调整记入本报告，待下期验证。

---
---
*报告生成时间: 2026-09-28*
*数据来源: AIHOT 日报（aihot.virxact.com，2026-09-28 期 2 条 + 页面日期线回溯 09-26/27，已直读）· GitHub Trending（2026-09-28 快照，9 仓，已直读，星数/日增/fork 以页面标注为准）· Hacker News 首页（2026-09-28 快照 30 条，分数与评论数以页面快照为准，未含 item id 故多数条目未附讨论直达链接；HN Algolia 查询接口一次调用失败 Token Plan 后端 exit 1）——以上为本期主源。AI Digest 中文（首页直读正常但最新一期停留在 2026-08-24，停更超一个月）当日无内容可用，未采用其内容，已如实记录。重点条目回查一手来源：authorsguild.org 首页（直读，09-21 解封简报新闻标题一手确认，简报原文与新闻详情页未逐字直读）· fireworks.ai/blog 索引（直读，未见 Ember-1 条目）· sancho.bearblog.dev 首页（直读，无文章列表，今日第一原文未定位）。检索通道本期为 eacli Token Plan（web.search / web.read，智谱）；凡未回查原文的数字与转述均已在正文以 [转述]/[仅标题级]/[单源 ⚠️]/[检索快照，域名级] 标注——Authors Guild 简报的具体措辞与所附证据、澳参议院传唤的一手文件（aph.gov.au）与出席日期、Ember-1 的全部数字（-35~50%/-71.3%/$3/$15/1M，官方博客未见）、09-26 Copilot 更新与 09-27 Text Arena 1509（均为 AIHOT 日期线单源）、paperclip 的 89.9k 总星（榜单快照单源），均待原文可读后复核*
*说明: 评分为站点标注值，未逐条回查原始来源；以官方链接为准。*
