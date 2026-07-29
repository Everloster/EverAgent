---
title: "为什么 FDE 在 AI 时代这么火？因为差距不在模型，在业务细节"
domain: "podcast-learning"
report_type: episode_summary
source: bilibili
source_url: https://www.bilibili.com/video/BV1tXKi6NE4b/
show: "课代表立正（B站对谈频道）"
episode: "单期"
host: "课代表立正"
guest: "Jove（温哥华，Cresta 公司 FDE 团队负责人；前 Splunk/EMC 管理、数据库创业者）"
duration: "41m41s"
duration_seconds: 2501
published: "2026-07-29"
updated_on: "2026-07-29"
---

# 为什么 FDE 在 AI 时代这么火？—— Jove(Cresta)对谈精读

> 本地转写驱动：whisper.cpp(ggml-large-v3）转写 + B站官方字幕双源对校。
> 标注纪律：节目观点标 `[节目]`，我的分析标 `[评]`；中英术语已按双源订正（FDE/Cresta/Palantir/Claude Code 等字幕误识别高发词）。

## 0. 一句话总结

模型人人能调，落地能力才是稀缺品。**FDE(Forward Deployed Engineer，前置部署工程师）就是补上 AI 落地"最后一公里"的人**——他们既懂 AI 的坑（幻觉/RAG/guardrail/低延迟），又懂客户的业务和信任经营，对最终结果负责 `[节目]`。

## 1. FDE 是什么：AI 语境下的新物种

- 词源 Palantir，但**AI 时代的 FDE 和传统驻场工程师/外包/咨询是两回事**：必须绑在 AI 语境里——模型（GPT、语音模型）花钱就能拿到，"so what，你不见得知道这模型该怎么用" `[节目]`。
- 职责闭环：结合客户业务逻辑 + 自家 AI 平台功能 → 做出符合业务场景的 AI agent 系统 → 处理幻觉、RAG/KB 低延迟准确化、guardrail、测试 `[节目]`。
- 客户自己不是不能做，而是**要学半年一年，竞争对手已经抢跑了**；FDE 让落地"更可靠更快"，各方 focus 各自专业 `[节目]`。
- 能力画像是"一群创业公司的 CTO":AI native + 愿意贴身服务（own API over IP[A] 式陪跑）+ 赢信任（CEO/CTO/技术 lead 都能对话）+ 知道哪里发力、哪里 say NO `[节目]`。

## 2. 为什么是现在：三个结构性原因

1. **落地能力断层**：传统行业想用 AI 但完全没有人才；"用人把不确定性变成确定性"（餐馆老板案例：不用自己学，FDE 全搞定）`[节目]`。
2. **市场换算**：红杉等分析——软件市场没那么大，**labor 市场极大，AI 取代的是 labor**；要把 labor 换成 AI，需要既懂 AI 又懂 business 的人 `[节目]`。
3. **赛道验证**:voice AI 已被证明是 **top3 赛道**（另两个：coding、multimedia 生成）——coding 太卷、多媒体烧钱，enterprise AI"问 100 个 business owner，50% 以上都想要" `[节目]`。

## 3. Cresta 样本（嘉宾一手）

- Cresta(2017 年成立）做 customer experience：call center 起家（Marriott、United 等大客户多年），现在做 **unified human + AI 平台**——挑哪些环节 AI 完成、哪些留 human `[节目]`。
- 典型场景：客服电话（补寄信用卡这类全流程 AI 可闭环）、**AI receptionist**（牙医/咖啡馆/花店没有 call center，但需要一个 AI 前台：接电话、约时间、发 summary 给老板）`[节目]`。
- 商业设计两个妙处 `[节目]`:
  - **只 SaaS，不做 on-premise** → 客户甩不开你，且模型快速迭代（4.x→5.x）反而成了持续续约的推手——"他要不停地 engage 你用最好的模型"，AR 很自然；
  - **FDE 归 product engineering**（直属 CEO），不归 customer success/售前——职责一是把 deployment 做成功，二是**用做 agent 的过程反证产品 PMF、回头改产品**（microservice/UI 都改）。"不想把自己培养成 consulting firm"——目标是平台把简单 case 模板化，FDE 去做越来越难的事、变成某领域专家。
- 组织分工学 Palantir 两队制：技术向 FDE + 非技术向 FD PM（管 business logic/期望/风险/排期，客户内部没 align 好的会先由 PM 理顺）`[节目]`。

## 4. 落地方法论：know-how 复利 + 信任前置

- **行业 know-how 复利**:"今天给饺子馆做，明天给西餐厅做"——翻台率、礼貌拒客、VIP 定位这些行业知识跨客户复用，"最后有可能我们比餐馆还要懂餐馆" `[节目]`。
- **细节是魔鬼**（举 voice AI):VAD(voice activity detection）一个点就有 silence-based / LM-based / 语义判断多种做法——停顿不等于该插话、报号码中间的停顿有讲究。"让餐馆 IT 去学这些，too much" `[节目]`。
- **信任比技术难**：创业公司进大公司的 final list 要一两年；Cresta 能拿下酒店/银行是因为"在那边时间足够久 + reputation + 数据合规"。客户 CEO/CTO 是**拿自己的职业为 Cresta 背书**——这层 trust 是慢功夫 `[节目]`。

## 5. 招聘画像与面试（想入行者的硬信息）

- **engineer 是底线**:3 年以上；面试仍保留"不用任何 AI 手写简单 Python"环节（变量命名/流程 sense)+ engineering best practice(unit test/分层）——没有工程素养的人做 agent"看起来 work 其实到处是洞"（登录界面全塞前端的笑话）`[节目]`。
- **会 Claude Code/Codex 不是加分项**:"就像不会打字一样，在简历上和'精通 Excel'一样"——**必须做过 AI agent**(LangChain/CrewAI/RAG/voice 其一）才算数 `[节目]`。
- **founder/cofounder 经历加分**（有 agency、能揽脏活）；consulting 背景好但**要防"按时间计件"的旧思维**(Cresta 是 SaaS 不是人力外包）`[节目]`。
- 实操面：90 分钟内用 Claude Code 等基于给定 API + knowledge base 做出一个高质量 agent（看设计、测试、guardrail 处理）`[节目]`。
- **AI 产品六层次**（host 的知识框架，嘉宾认可 voice AI 场景到 L4 够用）:prompt wrapper → 带知识的 AI → 能调工具 → 固定流程里的 LLM workflow → agent 框架（plan/act/observe 循环）→ AI-native product `[节目]`。
- **不招 junior**:FDE 对主动性要求高，"进来第二三周就可能 forward deploy 到客户那" `[节目]`。

## 6. win trust:这门软技能的核心参数

- 能 win trust 的人：经历过失败并能讲出 lessons；从客户角度察觉真实 motivation（哪些是假信号、哪些是不好意思说的）；让对方来推动方案而不是强行 say NO `[节目]`。
- host 补刀：愿意 listen + 站对方角度 + **ego 低**（"会就会不会就不会，为把事做好，不在乎自己对不对"）`[节目]`。
- 反例信号：面试答 6-10 分钟停不下来、列十个点不如讲两三点——"信息密度都不会把握，怎么做 FDE" `[节目]`。
- **"信任具象化到最后是落到人身上的，不是抽象的东西上"**——所以人在这里面极重要 `[节目]`。

## 7. 金句库（原文保留）

- "你只要肯花钱，是可以 access 到一些最好的模型的。但是 so what，你不见得能够知道这个模型应该怎么用。"
- "名词是非常有限的，10 分钟就能学会一个名词；**真正想要做好的都在动词里**——routing 这个词你听说过，但那个人 routing 做得好、这个人做得不好，你完全无法想象里边的功夫差得有多深。"
- "FDE 就像咖啡师：几千块的辣妈咖啡机你买了，也做不出好咖啡；又像 omakase——你不用问今天有什么菜，相信我们，最好的食材最好的技术给你一个体验。"
- "过去你为 skill 生存，现在 skill 大规模被取代；**你可以为结果负责——只要越来越接近结果，你就越难被取代**，因为 AI 没法为结果担责任。"
- "FDE 是属于（被 AI 取代焦虑中的）一个港湾、避风港。"

## 8. 争议与边界（国内适用性）

- 嘉宾明确：**FDE 模式"种在哪块土"很关键**——北美人工贵、为结果买单意愿强、SaaS 成熟，所以成立；国内人工便宜、toB 市场 tricky、"没有 enterprise 市场",FDE 很难讲 `[节目]`。
- 对 Palantir 的冷思考：很多人眼馋它的市值，"但你很难证明 FDE 在那张饼里占百分之几，不见得超过 10%" `[节目]`。

> [评] 这期与 ai-learning 刚入档的 Evoken 访谈正好构成"一体两面":**陈冕（ToC 应用）赌的是"消耗率精算 + 注意力先发",Jove(ToB 落地）赌的是"信任复利 + know-how 沉淀"**——同一个命题"模型吞噬应用价值"，ToC 的解法是速度和定价，ToB 的解法是关系和责任。两边共同的底层判断：**模型层只剩 commodity，价值向"对齐/交付/责任"层迁移**。另外"为结果负责最难被取代"这条，对 PROFILE 里"AI 时代水温变化下的学习/工作方法调整"这条兴趣线是直接的弹药。

---

## 思考与追问

1. **FDE 的"know-how 复利"有没有规模化上限？** Jove 说目标是让平台模板化、FDE 做越来越难的事——但模板化的过程是不是也在把 FDE 自己的 know-how 喂给"下一个吞噬者"?FDE 会被自家平台内化吗（客服界的"节点式工作流"命运）?
2. **"为结果负责"到底怎么计价？** Cresta 按省时间/成单数抽成的思路（"按 AI 帮你省多少时间、摊多少单子收比例"）和 Evoken 的订阅精算完全不同——结果计费（outcome-based）会不会才是 AI ToB 的终局定价？有哪些公司已经在跑？
3. **国内的"人工便宜"还能撑多久？** 嘉宾判 FDE 在北美成立、国内难讲，但国内 AI 客服（营销外呼类）其实已在爆发——是路径不同（国内走"进攻向"营销机器人）还是时机未到？值得追踪一个国内对照样本。

---
*报告生成时间： 2026-07-29*
*转写： whisper.cpp ggml-large-v3 本地离线（原始转录 2011 段）+ B站官方字幕对校；术语已订正，无法辨识处以原样保留。*
