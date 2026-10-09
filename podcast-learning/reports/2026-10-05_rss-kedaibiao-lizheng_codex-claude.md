---
title: "课代表立正216：Codex迭代十几轮的网站，Claude一天作废——个人网站与叙事主权"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（transistor RSS，视频音频版）
source_url: https://share.transistor.fm/s/eafb2ed7
show: "课代表立正"
episode: "立正说 216｜Codex跟我迭代十几轮，Claude一天就全作废？"
host: "课代表立正（孙煜征，单口）"
guest: "无"
duration: "14m17s"
duration_seconds: 857
transcript_segments: 610
hanzi_chars_raw: 4993
hanzi_chars_polished: 4902
total_chars_raw: 20178
total_chars_polished: 6714
audio_size_mb: 13.1
speech_rate_cjk: "350 字/min"
chapters: 10
polished: true
polished_by: "Claude (pi)"
polished_at: 2026-10-09
status: archived
created: 2026-10-09
updated_on: 2026-10-09
transcript_path: reports/transcripts/2026-10-05_rss-kedaibiao-lizheng_codex-claude.transcript.txt
polished_transcript_path: reports/transcripts/2026-10-05_rss-kedaibiao-lizheng_codex-claude.polished.txt
pipeline: transistor feed enclosure mp3 → 本地 whisper.cpp / large-v3 / Metal / VAD+`-mc 0`（Razer worker 域名白名单不批 share.transistor.fm，走 transcribe.py CLI fallback，与 215 期同路径）→ eacli web.read（智谱）拉 transistor shownotes → 按 10 章节重组润色
source_shownotes_chapters: true
notable_correction: "co-work→Claude Cowork/Claude Code（shownotes 确认）｜contacts→context｜超强性→超线性｜Versailles→Vercel｜rock→Grok｜孤独九仙→独孤九剑｜自考过程→思考过程；8 处 [?] 保留（I can force/文文力正/tubox/进攻性能位/白河亮/克里巴利州/预证/ICU→SEO[?]）；日期：RSS 显示 10-05、shownotes 显示 October 6"
---

# 课代表立正216：Codex 迭代十几轮的网站，Claude 一天作废

## 概览

- **缘起**：创业者朋友有超[?]推荐试 Opus 5.5 做网站。孙煜征把打磨过几十轮的 Codex/GPT 版个人主页交给 Claude 重做，一天出稿，新旧对比"完全天差地别"——审美代差。
- **工作流（本集方法论核心）**：**Claude Cowork 讨论方向 → 沉淀成文档 → 交给 Claude Code 实现**。Document first：文档是可移植资产，能喂给 Codex、Grok 等任何 agent。个人网站上线 lizheng.ai。
- **两个亮点模块**：①**社区地图**——超线性学院 2 万多成员做成可点开的点阵图（"我们在建一座城"），GitHub Action 每月自动抓 Circle 数据到 Vercel Blob，聚光灯随鼠标移动（prompt："高级但不 busy"）；②**"问问立正"**（ask.lizheng.ai）——基于他全部公开文章/判断的免费 Agentic RAG 问答（Grok 4.5 后端，每天免费 3 次），依托社区 Builder Space 基建部署。
- **为什么做个人网站（三理由）**：①叙事主权——控制"别人（人和 AI）怎么了解我"的确定性入口，专门做了 SEO+sitemap 让 AI 搜索靠前；②自留地——算法不可依赖，"粉丝刷不到你就忘了"，立正.ai 域名=确定性入口+信任构建+合作方式入口；③长期积累的具象化——substance 被直观呈现。
- **《禅与摩托车维修艺术》垫片故事**：易拉罐拉环垫片背后是极贵的机器，质量高于店里货——高手找本质联系、化繁为简，不搞 fancy prompting technique（辅证：宋亚东一拳 vs 花拳绣腿、梅西不踩单车）。

## 章节地图

| 时间 | 章节 | 核心命题 |
|---|---|---|
| 00:00 | Claude 重做网站，新旧版本差在哪 | Opus 5.5 一天 vs Codex 几十轮，审美代差 |
| 01:33 | 从 Cowork 到 Code：先写文档，再做网站 | Document first 工作流 |
| 02:48 | 两万多人的社区，怎么变成一张可探索的地图 | n(n-1)/2 链接具象化，GitHub Action 自动更新 |
| 04:36 | 问问立正：用我的文章和判断回答你的问题 | 免费 Agentic RAG，"很有态度"的回答 |
| 05:23 | AI 问答背后的基础设施与 Agentic RAG | Builder Space 部署，"不是前端界面" |
| 06:59 | 真正的 AI 高手，为什么不用花哨技巧 | 摩托车垫片/宋亚东/梅西三个类比 |
| 09:55 | 为什么做个人网站：拿回自己的叙事主权 | 对人+对 AI 的确定性入口 |
| 11:14 | 给自己留一个不靠平台推送的入口 | 自留地逻辑，立正.ai 域名 |
| 12:31 | 注意力、信任，以及长期积累的价值 | 算法时代的注意力/信任构建 |

## 关键人物

- **孙煜征（课代表立正）**：主播，康奈尔经济学博士、《真本事》作者、Superlinear Academy 创始人（shownotes 身份）。
- **有超[?]**：创业公司 Founder，频道常客，本次 Opus 5.5 推荐 initiator。
- **宋亚东**：UFC 搏击选手（"一拳打疼 UP 主曹岩"类比素材）。
- **梅西**：不踩单球的"最简有效动作"类比素材。

## 主要话题

### 1. 工具代差与 Document first

标题的戏剧性在于对比：Codex/GPT 版已经过几十轮打磨+几次大迭代，Opus 5.5 一天出稿即有"代差"。但孙煜征的重点不在"哪个模型强"，而在**流程**：Cowork（对话讨论方向、给 update 建议）→ 文档（需求沉淀）→ Code（实现）。文档成为人机之间、模型之间的**可移植接口**："我现在是从 Claude Cowork 变成 Claude Code，我把这个文档去交给 Codex，或者交给 Grok，也是一样可以去做的。"

### 2. 社区的定义：链接数而非人头数

newsletter 不是社区、微信群勉强是——社区的定义是"每一个人跟每一个人都可以产生链接"。2 万人 → n(n-1)/2 ≈ 2 亿条链接。"我不是要一个中心的分发的东西，而是要一个希望人和人之间能产生链接的东西。"地图是这个抽象概念的具象化。实现是全自动的：GitHub Action 每月抓 Circle API → Vercel Blob → 自动更新。

### 3. Agentic RAG："问问立正"

与普通 RAG 的区别：不是检索片段拼接，而是"把我所有的文章调出来，然后再去综合，最后再去形成答案"，且回答"很有态度"（例：对"DS 在 AI 时代会被取代吗"直接答"我认为就是会消亡的、是浪费时间的"+转型方向）。部署门槛在"怎么把模型部署给其他人"——靠社区自建 Builder Space 基建（登录后可调多种 API、直接部署内核）。

### 4. 高手不搞花哨技巧

三个类比同构：①易拉罐垫片（Pirsig《禅与摩托车维修艺术》）：便宜常见但背后是昂贵机器的高质量产出，菜鸟反而去店里找 fancy 货；②宋亚东：打得准打得快打得用力，不搞降龙十八掌；③梅西：不踩单车，每个动作最简单有效。映射到 AI 用法："我们没有教任何翻写的东西，我们所有的方法都是跟 AI 直接说话就好了，可是背后那个东西其实是很厉害的"——普通的话+深厚的积累与基建。

### 5. 叙事主权与自留地

- 叙事主权：你无法控制别人脑子里的印象、无法控制平台算法，但能控制"一个确定性的入口"——我的故事我来讲，我关心什么、什么信息放前面、过去的判断与最近的思考。
- 对 AI 的叙事主权：做了 SEO+sitemap，AI 搜索"课代表立正"大概率索引到个人主页。"无论是对人还是对 AI：掌握我自己的叙事主权。"
- 自留地：YouTube 一周发七条视频"绝大多数你是看不到的"；粉丝刷不到就忘，"不要觉得有人会真的去点自己的关注列表"。注意力与信任在算法时代难构建，需要不靠推送的入口。
- 社区自我介绍=互联网名片：留痕（context）未来可使用、帮助形成信任——又是 n×n 链接的意义。

## 引用书目

- 《禅与摩托车维修艺术》（Robert Pirsig）——垫片故事的出处
- 孙煜征《真本事》（"问问立正"的知识源之一）

## 关键概念词

叙事主权｜自留地｜Document first｜Cowork→Code 工作流｜Agentic RAG｜Builder Space｜社区=n(n-1)/2 链接｜垫片效应（fancy vs 本质有效）｜确定性入口｜互联网名片｜substance 具象化

## 关键观点（原话）

> "掌握自己的叙事主权——无论你是面对其他人，还是面对 AI，都是这样的。信息泛滥和整个平台算法统治的年代，这件事尤为重要。"

> "我们在做什么东西呢？其实到最后要形成一个 document，然后这个 document 你就可以拿到各种地方去用。"

> "社区的意思就是说，我们每一个人跟每一个人都可以产生链接……所以说这些链接才是一个社区真正的价值和真正的意义。"

> "真正的高手他能找到事物之间的本质联系，化繁为简，然后去找到最有效的那个方案。"

> "你哪怕在一个平台上再多的粉丝，平台明天不给你流量，那你这些粉丝就没有用……大家刷不到就把你忘掉了。"

> "你可以抄我的提示词……我相信 AI 都可以抄得很好；但是真正的那个实质，是需要我们自己自己去构建的。"

## 关键数字

| 数字 | 含义 |
|---|---|
| 几十轮 vs 1 天 | Codex/GPT 版历史迭代轮数 vs Opus 5.5 重做耗时 |
| 2 万+ 点/人 | 社区地图规模（每个点可点开） |
| 2 亿条 | n(n-1)/2 链接数（2 万人） |
| 每月 1 次 | GitHub Action 自动抓取 Circle → Vercel Blob 更新频率 |
| 7 条/周 | 其 YouTube 平均发视频量（"绝大多数你刷不到"） |
| 每天 3 次 | "问问立正"免费提问额度 |
| Grok 4.5 | "问问立正"后端模型 |
| 13.1MB / 350 字/min | 音频大小 / 语速 |

## Limitations

- Razer worker 域名白名单不批 share.transistor.fm，本集走本地 transcribe.py fallback（Metal/VAD/`-mc 0`），与 215 期同路径——已在 pipeline 标注。
- 这是**视频节目的音频版**，大量内容是"大家可以看到""鼠标移动"等视觉指代，纯听会缺失画面信息；报告以可听懂的部分为准。
- 日期不一致：RSS pubDate 2026-10-05，transistor shownotes 标 October 6, 2026；文件名按 RSS 用 10-05。
- 8 处 [?] 未确认专名保留原音（见 frontmatter）；"ICU→SEO[?]"为推测修正，不确定原词。
- whisper 把"course/context"相关英文多次转成 contacts，已按上下文统一修正为 context，但可能存在过度修正处。

## 思考与追问

1. **我真正理解了什么？**孙煜征把"个人在 AI 时代的存在方式"拆成了三层：**内容实质（自己构建）→ 文档化（Document first，可移植）→ 入口化（个人网站+叙事主权，对人和对 AI 双通道）**。这与 EverAgent 的两仓结构+AGENTS.md 思路同构——EverAgent 本身就是"给 AI 看的自我叙事"。另外"垫片效应"是对 prompt 花活派的精准反讽：功夫在基建与积累，不在话术。

2. **我还没搞懂什么？**①"问问立正"的 Agentic RAG 具体实现（多轮检索？还是单次全文召回+综合？）；②Opus 5.5 的审美优势来自哪里——模型本身还是 Cowork 的交互模式（对照实验没做：同样的文档给 Codex 会怎样？）；③社区地图的隐私边界：2 万人默认公开可点开，成员是否知情/可退出？

3. **下一步读什么/做什么？**①试用 ask.lizheng.ai 亲测"态度型回答"质量（免费 3 次/天）；②把"Document first"对照自己的 eacli/两仓实践写一篇短注（ai-practice 或直接在 EverAgent 根目录）；③关注孙煜征的"个人网站+agentic RAG 分身"模式会不会成为创作者标配——与 215 期"反 hype 判断方法"构成他的连续方法论输出。
