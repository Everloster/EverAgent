---
title: "42章经：锐评国模与 Neo Lab，畅谈 RL 人生与 RLaaS——对话 Mind Lab 首席科学家骁腾"
domain: "podcast-learning"
report_type: "episode_summary"
source: "小宇宙播客"
source_url: https://www.xiaoyuzhoufm.com/episode/6aec6bc06381f0f964c45068
show: "42章经"
episode: "锐评国模与 Neo Lab，畅谈 RL 人生与 RLaaS | 对谈 Mind Lab 首席科学家骁腾"
host: "曲凯（42章经创始人）"
guest: "马骁腾 Pony（Mind Lab 联合创始人、首席科学家；清华直博；Mindverse CRO）"
published_on: "2026-11-07"
created: "2026-11-13"
updated_on: "2026-11-13"
status: "completed"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "standard"
reader_contract: "standalone"
semantic_tags: ["podcast", "42zhangjing", "ma-xiaoteng", "mind-lab", "rl", "rlaas", "post-training", "lora", "neo-lab", "chinese-models", "deepseek", "glm", "rsi"]
chapters: "25"
source_shownotes_chapters: false
polished: true
polished_at: "2026-11-13"
transcript_visibility: "private"
transcript_path: null
polished_transcript_path: null
transcript_source_ref: "sha256:63fb3f81be6e7c2c891b748fbefb3c89a062fb76a4c567c28524ba82036d46e3"
polished_transcript_sha256: "72c002963b7d546b6d1470f2ce6632b81c01b72a23dced07dbfc921339a55cd8"
transcript_audit_path: "podcast-learning/reports/transcripts/2026-11-07_xiaoyuzhou-42zhangjing_xiaoteng-rl-rlaas.audit.json"
duration: "1h02m19s"
duration_seconds: 3739
pipeline: "本机 whisper.cpp large-v3 + Silero VAD（m4a→wav 通道）→ 确定性审计 → Claude 高保真精编（86.1%）→ 报告"
transcription_service: "whisper.cpp large-v3 + Silero VAD（本机转写）"
transcript_sha256: "63fb3f81be6e7c2c891b748fbefb3c89a062fb76a4c567c28524ba82036d46e3"
hanzi_chars_raw: 18998
total_chars_raw: 114000
transcript_segments: 2311
hanzi_chars_polished: 16350
total_chars_polished: 22000
speech_rate_cjk: 305
polished_by: "Claude（高保真精编，正文按汉字数为 raw 的 86.1%（16350/18998，精编稿头部口径），头部已标注）"
notable_correction: "肖腾/小腾→骁腾（马骁腾 Pony）｜MindLab→Mind Lab｜手续科学家→首席科学家｜安卓→Andrew（联创）｜茶院→叉院｜张成杰→张崇杰[?]｜John Shuman→John Schulman｜Android Capacity→Dario Amodei｜驱老师→曲老师（曲凯）｜RO/千万学习→RL｜iOS service→RLaaS｜Lauritin→LoRA｜征流→蒸馏｜1T（一体）｜preview→prefill｜酸力→算力｜GLM-5.3[?]系列等 45 处按原音保留"
---

# 42章经：锐评国模与 Neo Lab，畅谈 RL 人生与 RLaaS

这是[42章经](../wiki/show-indexes/42zhangjing.md)曲凯与 [Mind Lab 联合创始人、首席科学家马骁腾（Pony）](../wiki/entities/ma-xiaoteng.md)的对谈，全长约 **1 小时 2 分**。骁腾是大规模 RL 工程出身（2018 年就在 1 万核 CPU + 100 张 V100 的机群上做对战式 RL），2025 年 10 月与陈凯杰、Andrew 创办 Mind Lab。节目三段式：RL 人生（探索/知行合一/长期主义的方法论化）→ 国模与 Neo Lab 锐评（"中美最好的模型都出自创业公司"的机制解释）→ RLaaS 商业模式（帮客户做 post-train，按 token 收钱）。对本库最有价值的是一组互文：他给 harness 的定义——"**记得住名马，记不住名鞍**"——恰好从供给侧印证了 E255 的 Agent=Model×Harness×Context 与鸭哥的"harness 与模型 90% 场景可互换"。

## ⚡ 速览

- **国模锐评**：海外 pick OpenAI（pre-training 阶段调整了 harness/reasoning 结构）；国内**显著看好 DeepSeek**——infra-model co-design 飞轮（encoder/decoder 分离、encoder 未来跑国产卡 prefill）带来极低价格→更多数据/token→更快 RL；GLM 最务实、数据生产线最完善；Kimi fancy；MiniMax"信仰不坚定"（弃 linear attention、先上市分心）。
- **大厂集体失败论**："近两年中美最好的模型均非大厂产出"——千问在林俊阳[?]走前是第一梯队、后被集团按 ROI 审账；Google 早于 ChatGPT 做出同类物因广告顾虑未发布；大厂靠算力置换盈利，"商业上不输、模型技术竞争会集体失败"。
- **RLaaS 数字**：按 token 定价挂钩算力；frontier 开源模型单次训练迭代约几万元人民币，完整项目几十万到一百万；客户筛选两维度（有自有 benchmark + 已 PMF 或高价值垂域）。
- **RSI 判断**："现在完全就是一个宣传口号"——本质是高速可迭代 infra 上的自动化数据构建 pipeline；reward 设计离不开人（Dario Amodei 承认写作能力无法自我迭代）。

## 背景

- **嘉宾**：[马骁腾](../wiki/entities/ma-xiaoteng.md)，清华自动化系 2017 级直博（叉院张崇杰[?]门下）、2023 毕业留系博后；Mind Lab 属 Mindverse（心识宇宙）体系，研究主题 Experiential Intelligence / 持续学习[独立核实：xtma.github.io、36kr 2026-07-28]。联合创始人：陈凯杰、Andrew。
- **本库位置**：42章经上期读过的[子皓（Ambi）期](2026-10-12_xiaoyuzhou-42zhangjing_zihao-ambi.md)是交互侧；本期补模型/训练侧。Neo Lab 话题与十字路口 2026-11-09 年终复盘②（"RSI 可能是 NeoLab 的机会"，未做专题报告）同源。

## 内容地图

精编稿按 shownotes 重组（开场+25 个编号章+片尾，与官方 25 个时间戳对齐），本报告按四条主线归并；国内 RL"立山头"与硅谷 RL 人进入 LM 训练史两章（13:24/16:20）及 Mind Lab 争议话题按 standard 深度省略未展开。

| 主线 | 覆盖章节 | 本报告重点 |
|---|---|---|
| RL 人生 | 为何不进 Lab、三件事、90 分主义、创业即 RL loop、没进过厂凭什么（争议话题部分省略） | exploration/知行合一/长期主义；大厂局部信息做不好 value 更新 |
| 国模与格局 | 短期悲观长期乐观、Anthropic 担忧、大厂集体失败、拼什么、锐评分家、Seedance vs Sora | 蒸不了了+国产算力+数据 operation；DeepSeek 飞轮 |
| Neo Lab 与 RSI | 啥是 Neo Lab、致命错误、先模型还是先产品、RSI 是宣传口号 | research-product co-design；锤子找钉子 |
| RLaaS 与终局 | Macaron→RLaaS、中间层、客户画像、意义与账、LoRA 心路、continual learning、不担心被吃 | 定价与客户筛选；100 万 LoRA；百花齐放立场 |

## 一、RL 人生：把强化学习活成方法论

骁腾把 RL 的三件事直接翻译成人生态度：**exploration/exploitation**（Atari 靠 10% 随机动作保证探索——训大模型要控熵防"探索受损"）；**知行合一**（policy 与 value 的一致性）；**长期主义**（折扣因子 γ=0.99 对应约 100 步的视野，"time horizon 决定你 optimize 什么"）。"我一直都是一个 90 分主义者"——做到 90 分就用剩 10% 的精力探索新领域，创业中由 Andrew 与凯杰补足商业化拼成 100 分。

最有杠杆的一句是"**创业是最符合 RL loop 的事**"：能不停 connect real experiments，而大厂只有局部信息、做不好 value/policy 更新与探索。这个判断与他后面的"大厂集体失败论"同构——不是人不行，是组织的信息结构与 reward 结构不行。

## 二、国模锐评：飞轮、账单与信仰

总判断：**短期悲观、长期乐观**。悲观因子："蒸不了了"（前沿模型防蒸馏做得越来越好，公开数据已用完、预训练靠蒸馏回收（"美国追求 30T"为曲凯转述的传闻）；GPT-6 明显优化了 Blender；Anthropic 以暴力收购获取未公开数据）。乐观两支点：国产算力明年进入"能用"状态 + 中国组织数据 operation 的能力远强于美国。产业落点：**绝大多数应用发生在 1T 以下、最常用 300B-500B 的 flash 档**，制药级 frontier 才真有差距。

**大厂集体失败的机制**（本报告认为这是本期最有解释力的段落）：千问在林俊阳[?]离开前是公认第一梯队（BigGo 转写作"林俊暘"），之后"被账单摆在集团面前"、按 ROI 审计重组；Google 早在 ChatGPT 前做出同类系统，因广告业务顾虑未发布；大厂商业上靠把算力置换给创业公司盈利——"商业上不输、模型技术竞争会集体失败"。

分家锐评（口播，利益相关：Mind Lab 与多家存在合作竞争关系）：
- **OpenAI**：pre-training 阶段就调整了 harness 与 reasoning 结构，Anthropic 未跟进；
- **DeepSeek**：显著看好——infra-model co-design（encoder/decoder 分离、encoder 未来跑国产卡做 prefill）→ 极低价格 → 更多数据/token → 更快 RL 训练的**系统性飞轮**；
- **GLM**：最务实，自有数据生产线为几家中最完善；
- **Kimi**：fancy（此词为曲凯的归纳、嘉宾默认）；
- **MiniMax**："信仰不坚定"——自己开创 linear attention 又放弃、先做营收先上市（"第一个上市"）分心今年模型竞争；
- **Seedance vs Sora**：Seedance 成功三要素=数据好+明确场景+足够算力（"纯粹是数据"）；OpenAI 切掉 Sora all in 语言模型，Seed 切卡做视频没 all in 语言——他判断这"肯定有这个因素"影响了 Seed 的语言模型（自认不能断言）。

## 三、Neo Lab 与 RSI：从锤子找钉子到宣传口号

骁腾对 Neo Lab 的定义是**research-product co-design**（对标 DeepSeek 的 infra-model co-design）："拿着投资人真金白银、不尝试商业化闭环的都不是 Neo Lab。"致命错误清单："所有 researcher 都在造锤子找钉子"；美国 Neo Lab 更高比例由真实业务驱动。落地路径：先 research/模型，用不投流的 prototype 收 real data，形成闭环。

**RSI 判断**毫不留情："现在完全就是一个宣传口号。"本质是高速可迭代 infra 上的自动化数据构建 pipeline（模型自己找数据、造 workflow 回训）；两层硬边界——reward 设计离不开人（Dario Amodei 承认 Anthropic 难让模型自我迭代写作能力，写作变差需人拉回），RSI 也解决不了企业私有数据来源。这与本库[庄明浩 RSI 两路线](2026-09-15_xiaoyuzhou-tulong-zhishu_next-act.md)的怀疑侧完全同频。

## 四、RLaaS：中间层的生意经

从早年的 Macaron App 到今天的 RL Service（转写未给年份），实质都是超大模型 RL："post-train 像互联网时代的推荐系统，是 fundamental 技术。"

- **定价**：按 token、直接挂钩算力消耗（与 Fireworks、Tinker 一致）；frontier 开源模型单次训练迭代约几万元人民币，完整项目经验值控制在几十万到一百万；"对融资一两千万美金的 B 轮公司，花 10 万美金做一次非常值。"
- **客户画像**：横向看技术理解（有自有 benchmark，往前才是 agent/RAG 阶段），纵向看收入与 PMF（已 PMF 创业公司 vs 垂域传统企业）；不为 PR 接单；核心阻力是 data access 敏感与中国特色本地部署要求。
- **价值主张**："模型是体验差异最大的东西——记得住名马，记不住名鞍，Harness 就是那个马鞍子。"自建 infra team 成本高（多维并行调优难），这是中间层存在的理由；"国内瓶颈不在卡，在接受服务的意识。"

**LoRA 心路**（时间线完整）：2025-03 只有四台 H800 起步 → 2025-09 Thinking Machines《LoRA without Regret》与自己同期结论一致 → follow Tinker 自建 LoRA 训练服务 Mint → scale up/down/out 三维战略 → **2026-04 做出单底座挂 100 万 LoRA 的推理系统**，展望 Agent's Society。人与人的基因差异 <0.5%（与曲凯核到 <0.2%）被他用来类比 base model + LoRA adapter。**Continual learning** 是他押的下一层：模型需要储存长期记忆与 taste 的轻量可迭代单元（类 LoRA 结构、需新更新方式），据他称 Ilya 也在讲该方向。

**终局立场**：Claude Code 领先 OpenAI 半年、靠产品积累数据——"有一个产品是 access 最真实数据的最好方式，没有之一"；Anthropic 若不做 Claude Code"绝对不能跟 OpenAI 抗衡"。两种未来——全知全能 AI 世界洗牌 vs 百花齐放——"我应该为了第二种情况而奋斗。"

## 关键数字

| 数字 | 语境 | 来源层级 | 本报告核验 |
|---|---|---|---|
| 2018 年起 5000 万元级项目；1 万核 CPU + 100 张 V100 | 履历/工程能力 | 口播 | 未独立核实；与 Ray 0.2/PyTorch 0.4 时代吻合 |
| 传闻美国追求 30T（数据量级） | 数据现状 | 口播（传闻） | 未核实，按传闻层级标注 |
| 产业应用集中在 1T 以下、常用 300B-500B flash | 落点判断 | 口播 | 观点性判断 |
| frontier 开源模型单次迭代几万元；项目几十万-100 万；B 轮公司 10 万美金/次 | RLaaS 定价 | 口播 | 未独立核实；与 Fireworks/Tinker 按算力计费模式一致 |
| 2025-03 四台 H800 起步；2026-04 单底座 100 万 LoRA | Mind Lab 时间线 | 口播 | 未独立核实；《LoRA without Regret》为 Thinking Machines 公开论文（2025-09）属实 |
| Atari 10% 随机动作；γ=0.99≈100 步视野 | RL 方法论 | 口播 | 标准 RL 常识，量级正确 |
| Anthropic"暴力收购"获取未公开数据 | 数据策略 | 口播（观察） | 未核实；与本库 OpenRouter/Stripe 收购等资本动作同期频发的方向一致 |
| 基因差异 <0.5%（与曲凯 <0.2%） | LoRA 类比 | 口播 | 人类基因差异公开口径约 0.1%-0.5%，量级自洽 |

## 金句

> "记得住名马，记不住名鞍——Harness 就是那个马鞍子。"

> "创业是最符合 RL loop 的事。"

> "RSI 现在完全就是一个宣传口号。"

> "拿着投资人真金白银、不尝试商业化闭环的，都不是 Neo Lab。"

> "有一个产品是 access 最真实数据的最好方式，没有之一。"

> "我应该为了百花齐放的第二种情况而奋斗。"

（引语为精编稿口径的压缩转述；原转写含大量同音误识别（RL/蒸馏/算力/叉院等），已按公开资料修正，[?] 项保留存疑。）

## 思考与追问

1. **我真正理解了什么**：骁腾把"谁能做出好模型"这个问题从人才论转成了**信息结构论**——大厂失败不是因为没有聪明人，而是账单审计（reward 结构）+局部信息（observation 结构）从组织上决定了 value/policy 更新做不好。"名马名鞍"句与 E255 乘法公式、鸭哥"harness/模型 90% 可互换"构成三方互文：模型差异化收窄时，体验差异沉淀在 harness 与数据管线。
2. **我还没搞懂什么**（已汇入 [open-questions](../wiki/open-questions.md)）：
   - "DeepSeek 飞轮"（encoder 跑国产卡→低价→更多数据→更快 RL）与 vLLM 系列揭示的 serving 侧优化，哪一侧对最终价格曲线的斜率贡献更大？可对照 DeepSeek API 定价历史与国产卡 prefill 渗透率检验。
   - RLaaS 定价"按 token 挂钩算力"在客户侧的接受度：当模型迭代效果不可预付审计时，几万元/次的迭代如何签 SLA？
   - "100 万 LoRA 挂单底座"的推理系统与鸭哥"反向对微调"是否指向同一个终局——个性化 adapter 池成为新中间层？
3. **下一步**：读 Thinking Machines《LoRA without Regret》原文（骁腾心路的印证件）；跟踪 Mind Lab Mint 服务的公开定价。

## Limitations

- 转写由**本机 whisper.cpp large-v3 + Silero VAD** 完成（m4a 经 ffmpeg 转 wav），2311 段，确定性审计通过（最大连续重复 2、尾部干净）；润色为 Claude 高保真精编，正文 86.1%（16350/18998 汉字），修正清单 4 类（"骁腾/RL/蒸馏"系同音误识别重灾区）。
- 存疑保留 [?]：GLM-5.3 系列拼写、Vispro[?]、"腾讯顺宇"[?]、WorkBuddy[?]（此节目语境下的写法）、Jab[?]（GPT-6 蒸馏端侧模型名）、张崇杰[?]（导师名按音近修正）、"5D 一体"[?] 等 45 处 [?] 标记按原音保留；不据此展开。
- 嘉宾为 Mind Lab 联创，涉及国模各家（DeepSeek/GLM/Kimi/MiniMax）与 RLaaS 商业模式的锐评均按**利益相关方口播**处理；除嘉宾身份与《LoRA without Regret》论文外未做逐项独立核实。
- 阅读口径分层：精编稿由独立精编 agent 逐段通读，主会话基于其全量章节摘要与关键事实清单撰写并抽查原始转写，独立复核者复核；未逐句听音。完整转写与精编稿存仓库外私有目录，公开仓仅留脱敏[审计收据](transcripts/2026-11-07_xiaoyuzhou-42zhangjing_xiaoteng-rl-rlaas.audit.json)。

## 来源与核验范围

- [小宇宙节目页](https://www.xiaoyuzhoufm.com/episode/6aec6bc06381f0f964c45068)：节目身份；音频为官方 enclosure（61,095,912 bytes），转写输入。
- [马骁腾主页 xtma.github.io](https://xtma.github.io)：身份（Mindverse CRO、Mind Lab、Experiential Intelligence）。[独立核实]
- [36kr：在大模型的下一阶段议题上（2026-07-28）](https://m.36kr.com/p/3916202023660929)：Mind Lab 与 Thinking Machines Lab 的持续学习定位对照。
- [BigGo 播客转写页](https://finance.biggo.com.tw/podcast/c2d07991f8aff5fe)：本期部分口径的第三方转写对照（"账单摆在集团面前"）。
- 本库关联：[E255 张阔](2026-10-08_rss-guigu101_e255-zhangkuo.md)（乘法公式）、[鸭哥期](2026-11-10_xiaoyuzhou-ai-lianjinshu_yage-superalinear.md)（harness 互换）、[庄明浩 Q3](2026-09-15_xiaoyuzhou-tulong-zhishu_next-act.md)（RSI 两路线）、[子皓期](2026-10-12_xiaoyuzhou-42zhangjing_zihao-ambi.md)（42章经上期）、[vLLM Vera Rubin 解析](../../ai-learning/reports/knowledge_reports/vLLM_Vera_Rubin_NVL72_58x吞吐与机架级内存池_深度解析_20261113.md)（serving 侧对照）。

资料核验日期：2026-11-13。

---

节目版权归《42章经》及嘉宾所有；本文为个人学习分析，短引与转述均注明来源，不发布完整转写或精编稿。完整节目请回到[官方播放页](https://www.xiaoyuzhoufm.com/episode/6aec6bc06381f0f964c45068)。
