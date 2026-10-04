---
title: "如何炒作一个 AI 概念？以 Jev 为例——孙煜征的五步判断法"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（transistor.fm RSS）
source_url: https://share.transistor.fm/s/e6e502cd
show: "课代表立正"
episode: "立正说 215（2026-09-24）"
host: "孙煜征"
guest: "（单口）"
duration: "19m16s"
duration_seconds: 1156
transcript_segments: 827
hanzi_chars_raw: 7321
hanzi_chars_polished: 6816
speech_rate_cjk: "380 字/min"
chapters: 6
polished: true
polished_by: "Kimi (k3) 润色"
polished_at: 2026-10-04
status: archived
created: 2026-10-04
updated_on: 2026-10-04
transcript_path: reports/transcripts/2026-09-24_rss-kedaibiao-lizheng_ai-hype-jev.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-24_rss-kedaibiao-lizheng_ai-hype-jev.polished.txt
pipeline: transistor 直链 mp3 → whisper.cpp / large-v3 / Metal / VAD+`-mc 0` → 6 节重组
source_shownotes_chapters: false
notable_correction: "Jev 七种误识别归一（JAF/Jive/Jeff/JAV/Java/Zive→Jev）；修正 40+ 处（皈依化→归一化、Fantoon→fine-tune、REG→RAG 等）；两处音频缺段（00:03:16 跳 2 秒、00:13:47-56 缺 9 秒）已标注"
---

# 如何炒作一个 AI 概念？以 Jev 为例——孙煜征的五步判断法

> 19 分钟单口，给你一套不被 AI 热点带偏的判断方法。核心一击：**判断新技术最重要的一件事，是找对比较对象**——Jev 的叙事让它去跟 GPT 比速度成本（碰瓷），而它真正的对手是 BERT、JSON mode、本地小模型取 logits 归一化，乃至 Python 自带的 random。结论："Jev 被其他 solution 吊打，不值得关注。"

## 一、概览

- **孙煜征的战绩声明**：小龙虾（OpenClaw）、MCP、RAG、LangChain、fine-tune 都是刚出时"带着时间戳"公开反对并"断定它一定会凉"；Agent、Claude Code、Skill 第一时间呼吁关注（2025-02 Anthropic 内部还在盯 3.7 时他们就推 Claude Code，半年后自媒体才跟风）。
- **五步判断法**：①理解它是什么 → ②适用/不适用边界 → ③自己的评价框架（在哪些维度衡量好坏）→ ④**找对对标对象（最重要）** → ⑤决定对自己有没有用。
- **Jev 解剖**：原理=给当前状态+几个选项，输出各选项概率（抽象成 if-else / SQL case when）；评价框架他称 **"AI referee"**（判断质量/延迟/一致性/可校准+成本）；真正对手是完成同一任务的全部 alternative——BERT、GPT+JSON mode、本地小模型取 logits 归一化、甚至 Python 自带 random。比下来："很多任务上 Jev 与 random 无质变（和猜差不多）"，本地小模型四维俱佳且自有可调，而 Jev 是黑盒云服务。"泯然众人的解决方案，只是叙事让它跟大模型比它最擅长的事。"
- **hype 三成因**：①碰瓷式对标+「machine native」叙事打开脑补（他反驳：machine native 是过去二三十年所有软件程序做的事，无新范式）；②技术博主只有第一二层能力（读论文/跑代码）、没有第三四层（找不到 best alternative），陷入叙事还变成传播者；**叙事符合时代特征与人性→天然利于传播→流量放大**；③第零层（不学固执）和第三四层得出的否定结论一样，于是一二层的人把三四层的人当草包攻击——舆论长期只有肯定声。
- **迁移判断**：被宣传省略的替代方案——Skill 可以很好地取代 MCP；不学 framework 先学底层（LangChain 是把简单变复杂）；小龙虾黑盒+聊天窗口在复杂/长线任务必然出问题，鸭哥自研 OpenCode[?] 作为更好 alternative。
- **在公司表达不同意见的实操**：先亲手做出一个更好的 Jev → 先顺着叙事讲（"你说得对，但我给你一个更好用的 Jev，我们来比较"）→ 换取技术信任后再说"这事没那么重要"——**不做坐在旁边批判大家的人**。

## 二、章节地图（6 节）

开场（战绩声明+立题）→ 最重点：比较对象（邵艾伦跟马斯克比搏击=碰瓷）→ 五步法逐条 → 用五步法走 Jev（原理/边界/标准/对手/结论）→ hype 三成因 → 迁移（Skill>MCP？/小龙虾批判/OpenCode）与判断力习得+公司生存术。

## 三、关键观点（原话引用）

> "你去跟马斯克比较搏击这个行为，我们都知道是碰瓷。但是如果放到技术上，我们就看不出来这一点了。"

> "它就是一个泯然众人的解决方案而已。可是它的技术叙事把它拿去跟大语言模型比较它最擅长的事情，大家就觉得它好像很厉害。"

> "所谓的 machine native 的世界……是整个过去二三十年所有软件、所有程序所做的事。"

> "当你做了第一步第二步、但没有第三步第四步的时候，你就陷入了它的技术陷阱……你变成了它整个叙事框架的一个传播者。"

> "你做了第三层第四层，和你连第一层第二层都没做，得到的结论很可能是一样的。"

> "你可以说'大家说得对，Jev 确实很重要，但是我给你一个更好用的 Jev'……坐在旁边批判大家的人，一般在公司里边是不太受喜欢的。"

## 四、与库里叙事的接口

- **屠龙 Q3"benchmark 失效与奇观传播"**：阑夕"能力界定需要奇观"与本期成因二互为上下游——一个讲传播侧需要奇观，一个讲叙事自带传播性并被流量放大；两期都把"传播"当作与技术价值正交的独立变量。
- **张托肯"模型能力>Harness"**：评价结论完全取决于比较坐标系（5 个 harness 无差异 vs 换模型泾渭分明）——本期第四步是同一命题的评价侧版本。
- **与 EverAgent 自身的真实张力**：本工作台是 OpenClaw 的实际用户（自部署、权限可控），且日常依赖 MCP 工具链——孙煜征批的是"黑盒+聊天窗口"的用法，我们的用法部分落在其批评之外；但"Skill 可以很好地取代 MCP"与工作台重 skills 的架构方向一致。张力值得记录，不用回避。
- **第三方同向判断**：09-27 42章经吴浩哲期对 Jev 独立泼冷水（"适合当门口分拣员，不适合当快递员"），与本期构成两个独立来源的同向结论。

## 五、Limitations

- 两处音频缺段已标注（00:03:16 跳 2 秒、00:13:47-56 缺 9 秒——该处论述不完整）；"OpenCode"与既有 OpenCode harness 是否同一产品未确认；邵艾伦/田元栋（疑田渊栋）等专名标 [?]。
- 单口节目无 shownotes 章节，6 节为自拟。
- 他对 MCP/小龙虾/LangChain 的判断是强立场观点，引用时注意这是他的一贯反方人设（且有可验证战绩），不是中立评测。

## 六、思考与追问

1. **五步法在你工作台的落地**：屠龙 Q3 说"benchmark 失效"，孙煜征说"建立自己的评价框架"——你日常判断新工具（eacli/hermes/MCP 生态新件）时，第三步（评价维度）和第四步（对标对象）有没有成文清单？要不要把它沉淀成 `docs/` 里一页"新技术五步法 checklist"，以后每次选型先过一遍？
2. **"Skill 可以很好地取代 MCP"**：这是对你工作台架构的直接挑战（mcp-gateway 在用）。反过来看，MCP 相对 skill 的不可替代点是什么（跨进程/跨工具互操作协议、第三方生态）？值得写进 MCP gateway 的 refer 里作为设计辩护，还是认真评估迁移成本？
3. **hype 三成因的自检**：成因二说"一二层能力（读论文/跑代码）的人容易变成叙事传播者"——你的研究报告流程里，哪一步是"第三四层"（找 best alternative、自己实现出来证明）？digest 链会不会恰好缺少"替代方案搜索"这一步？

---

*版权与引用：节目版权归课代表立正（孙煜征）所有；转录与润色稿仅供个人学习；如版权方要求下架请联系。完整节目请去各播客平台收听。*
