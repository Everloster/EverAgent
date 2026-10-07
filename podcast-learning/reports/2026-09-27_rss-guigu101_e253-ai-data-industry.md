---
title: "谁在给大模型出题、卖题、判卷？AI 数据行业的野蛮生长"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（硅谷101 fireside RSS）
source_url: https://sv101.fireside.fm/267
show: "硅谷101"
episode: "E253（2026-09-27）"
host: "一文（Yiwen）"
guest: "何允中（Scale AI 研究总监，前 Meta 搜索推荐）× 孙一铀（UC Berkeley 博后，ALE 研究者）"
duration: "58m04s"
duration_seconds: 3484
transcript_segments: 2407
hanzi_chars_raw: 19041
hanzi_chars_polished: 18133
speech_rate_cjk: "331 字/min"
chapters: 12
polished: true
polished_by: "Kimi (k3) 润色"
polished_at: 2026-10-07
status: archived
created: 2026-10-07
updated_on: "2026-10-07"
transcript_path: reports/transcripts/2026-09-27_rss-guigu101_e253-ai-data-industry.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-27_rss-guigu101_e253-ai-data-industry.polished.txt
pipeline: fireside 直链 → whisper.cpp / large-v3 / Metal / VAD+`-mc 0` → 19 章归并 12 节
source_shownotes_chapters: true
notable_correction: "人名/术语经 Apple Podcasts shownotes 联网核验（何允中、孙一铀、Mercor 100 亿、SWE Atlas 结构等）；Scale/Mercor/AfterQuery 的十余种误写已归一"
---

# 谁在给大模型出题、卖题、判卷？AI 数据行业的野蛮生长

> 两位一线从业者（Scale AI 的何允中 + ALE 的孙一铀）把数据行业的地层结构拆开：数据公司三种基因、Rubric→RL 环境的范式迁移、benchmark 的生意与禁区、专家数据造假的验证难题。本期最有价值的是一句暴论："**Lab 未必有最好的基因来解决数据的问题**——好数商最终解决的是研发问题。"

## 一、概览

- **估值狂飙**：AfterQuery 半年 3 亿→**32 亿美元**（YC 最快独角兽纪录）；Scale AI 被 Meta 入股估值超 290 亿；Mercor C 轮 100 亿。（与屠龙 Q3 数字互洽）
- **三种基因**：招聘平台出身（Mercor/Handshake，卖点是短时间找到足量专家）、众包标注出身（Scale 传统数商）、合成数据新秀；核心取舍=全职自养（能力强、灵活度差）vs 众包网络（灵活、质量难保障）。
- **范式迁移**：预训练时代=人工标注；DeepSeek+o 系列证明 RL 跑通 → 转向 **Agentic Data**。两波：Rubric 数据（专家把"怎样算好"写成打分规则，弱模型照规则改卷——weak-to-strong supervision）→ **RL 环境**（task+工具+沙盒+验证方式一整套；目前无共识，"像当年 rubric 时代，每家要的东西都不一样"）。
- **ALE（Agents' Last Exam）**：把 vibe coding 推广到 **vibe everything**；孙一铀的警钟："**卖评测数据是不能碰的线**，会毁了 benchmark 也毁了别人的模型——benchmark 面向未来，数据面向现在。"
- **行业内幕**：SWE Atlas 的 Q&A 子集是三个子评测里最简单的，因先发布被 Artificial Analysis 收录而突然走红——"榜单火不火有大量随机因素，水很深"；SWE-bench Verified 六个月仅从 74%→80%，剩余 20% 集中在坏题上，已失去对比意义。
- **造假与验证**：ALE 真实遭遇用 agent 合成假数据；最难查的是编造数据（化学模拟没跑过、编得似是而非，几个月查不出）；方案之一是 proof of work（全程录工作流）。"众包 benchmark 难做就难在，人性是非常复杂的。"
- **下一步**：真实工作流数据可化归为 coding 问题（"代码是 agent 的手跟脚"）；并购路径兴起（PE 买公司→AI 提效裁员→数据挖出来卖钱）；数商没法躺平，终局拼 R&D 固化为 flywheel。

## 二、章节地图（12 节）

开场（估值狂飙）→ 数据公司三种基因 → 预训练→后训练（Agentic Data）→ ALE 详解+主观判断量化 → Rubric×环境、人×Agent（决策类任务是空白）→ benchmark 的生意（"面向未来 vs 面向现在"）→ 什么评测值得刷+分布难题 → 小团队机会+垂直采购（游戏源码两三百万一条、医疗缺数据）→ 模型自造数据后数商的存续（"Lab 未必有最好的基因"）→ 数据买回来怎么用（recipe/RSI/防 reward hack/难度适配）→ SWE-bench Verified 争议+专家造假 → 行业下一步（PE 并购/flywheel）。

## 三、关键人物

- **何允中**：Scale AI 研究总监（后训练+评测），自称"整个行业的外包数据 research 团队"；Meta 入股前签的 offer，亲历人才战。
- **孙一铀**：UC Berkeley 博后，ALE（Agents' Last Exam，Berkeley RDI 旗下）研究者。

## 四、主要话题

### 1. Rubric→RL 环境的迁移逻辑

Rubric=专家把判断写成打分规则，弱模型照规则改卷（weak-to-strong）；易获取的专家 rubric 已"收集得比较干净"。RL 环境=task+工具+沙盒+验证方式（programmatic check/rubric/preference），不再只验证聊天输出，要查环境变量、数据库写入、文档里的图。Terminal Bench 纯 programmatic 不要 rubric——无共识期。

### 2. 决策类任务是空白

按"人决策/agent 执行"分工看：agent 纯执行时输出唯一、确定性 rubric 够用；**决策类任务（如上市公司领导决策）每天变、收不到足够数据、没法 train reward model**——是未来趋势也是空白。未来收数据的关键是激励机制设计。

### 3. benchmark 生意的禁区与随机性

造 benchmark 的人有领域权威性 → 自然长出卖数据的生意。孙一铀的线："不能让你做的生意污染 benchmark 的权威性，不然你不仅毁了 benchmark，也毁了别人的模型。"何允中曝内幕：SWE Atlas 的 Q&A 子集最简单却因先发布被收录而走红。LM Arena 式真实分布是理想形态，但 agent 时代长程任务几小时、拿不到 ground truth；评测分数常与线上 A/B test 不一致（Claude Code 在 Arena 领先因输出 format 讨喜）。

### 4. "Lab 未必有最好的基因解决数据问题"（本期暴论）

合成数据本是 lab 后训练本职（买/核/验/洗），但今年增长来自懂行的人在体外合成再卖回；lab deadline 死、没自由度花半年啃一个行业；采购涉 conflict of interest（FDE 派驻企业 vs 搞企业数据，企业不放心）。对外部数商依赖长期存在（太多工作流没被吃透）；同一数据卖多家 → 加钱买断。

### 5. 数据怎么用：recipe、RSI 与难度适配

简单数据直接 SFT；rubric 类做 RL；今年主题 RSI——长程任务跑几天一周、真占 GPU、模型训模型，训练方式开始模糊。防 reward hack：强模型做 red team 找捷径；reward 多维（查 token/步数 budget）。**难度适配**：训练数据要按目标模型定制（厂商把未发布模型给 Scale 筛题）；轨迹采集让厂商跳过 RL 直接照轨迹 SFT——"数据不是越难越好"。

## 五、与库里叙事的接口

- **屠龙 Q3（数据商品化/AfterQuery 32 亿）**：数字互洽（AfterQuery 半年 10 倍、YC 最快独角兽）；本期给了商品化的焦虑面——"margin 越来越低""数商很难把杠杆保持住"。
- **晚点 183（数据是 ROI 最高增量/RL 环境融资热）**：部分互证——RL 环境公司小团队高估值吻合；**Mechanize 被 Google 收购一事本期完全未提**（口径差异记录）。
- **张托肯（好任务=训练数据）**：精神呼应——"benchmark 面向未来，数据面向现在""刷有意义的题=实打实的提升"；好任务/好评测本身是数据生产的源头。
- **课代表 215（评测观）**：孙煜征"评价结论取决于比较坐标系"与本期"榜单权重主观→大家质疑的是榜单本身"是同一问题的两层。

## 六、关键概念词

Rubric data、RL environment、weak-to-strong supervision、Agentic Data、vibe everything、benchmaxxing、benchmark 分布、LM Arena、training recipe、SFT、RSI、reward hack、red team、轨迹采集、难度适配、数据污染/假错误、authorship 激励机制、proof of work、expert matching、买断、PE flip、flywheel、SWE Atlas、SWE-bench Verified、ALE。

## 七、关键观点（原话引用）

> "我能不能用弱模型来监督强模型……我有个专家把他脑海里的知识给写下来了，这样弱的模型拿着它改卷就行了，这就是 rubric data。"（何允中）

> "我们怎么样把 Vibe Coding 迅速发展的趋势推广到 Vibe Everything。"（孙一铀）

> "Benchmark 面向的是未来，做数据面向的是现在。"（孙一铀）

> "不能让你做的生意污染你这个 Benchmark 的权威性，不然的话你不仅毁了你的 Benchmark，也毁了其他人的模型。"（孙一铀）

> "我有个暴论：可能 Lab 未必有最好的基因来解决数据的问题。"（何允中）

> "现在你让 agent 来做事情，代码就是它的手跟脚。"（何允中）

> "众包的 benchmark 为什么难做，就是难做在这里——人性是非常复杂的。"（何允中）

## 八、Limitations

- 话轮无 diarization：主持/允中/一铀靠语义判定，几处归属为推断（已标注）。
- 公司名 Bespoke/Snorkel 为音近推定标 [?]；约 15 处 [?]（MUSE、"AI doomer's view" 等）。
- 数字均为嘉宾口径（估值、时薪、3000 节点、5-10% 覆盖率等），未独立核验。
- 科沃斯赞助口播（02:33-03:28）已从 polished 删除并标注。

## 九、思考与追问

1. **"Lab 未必有最好的基因"对前沿 lab 组织设计的含义**：何允中的论证（deadline 死/无自由度啃行业/采购利益冲突）若成立，前沿 lab 的数据部门会走向"内部数商化"（独立核算、对外接单）还是"全外包"？回看 Anthropic 扶持 YC 数据公司（每家 100 万美元订单）把价格打下来——这是不是在主动培育外部基因？
2. **决策类任务的数据空白是机会还是死区**："上市公司领导决策"类任务收不到数据、训不了 reward model——这和你库里的"判断力护城河"问题（Evoken 期）是同一枚硬币。个人/小团队能不能用"自己工作中的真实决策轨迹"喂出个人 reward model？隐私和有效性的边界在哪？
3. **proof of work 防造假对 EverAgent 的映射**：ALE 用人全程录工作流防 agent 合成假数据——你的 digest 链目前是"信任 subagent 的引用"。要不要给报告流程加 digest 层的 proof of work（引用必须带转写行号/时间戳锚点）？成本很低，防的是"润色稿编造"。

---

*版权与引用：节目版权归硅谷101与嘉宾所有；转录与润色稿仅供个人学习；如版权方要求下架请联系。完整节目请去各播客平台收听。*
