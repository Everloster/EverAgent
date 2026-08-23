---
title: "对话盛颖：xAI，Infra的浪漫，SGLang，开源，平权与「甄嬛传」"
domain: "podcast-learning"
report_type: episode_summary
source: 硅谷101（Fireside RSS 音频直链）
source_url: https://www.sv101.net/260
show: "硅谷101"
episode: "E247"
host: "陈茜（开场：泓君）"
guest: "盛颖（Ying Sheng）"
duration: "1h46m26s"
duration_seconds: 6387
transcript_segments: 5578
hanzi_chars_raw: 34164
hanzi_chars_polished: 33726
total_chars_raw: 129000
total_chars_polished: 45733
audio_size_mb: 147
speech_rate_cjk: "321 字/min (raw)"
chapters: 12
polished: true
polished_by: "Kimi (kimi-cli-k3)，12 章并行分章润色"
polished_at: 2026-08-23
status: archived
created: 2026-08-23
updated_on: 2026-08-23
transcript_path: reports/transcripts/2026-08-04_rss-guigu101_shengying.transcript.txt
polished_transcript_path: reports/transcripts/2026-08-04_rss-guigu101_shengying.polished.txt
pipeline: yt-dlp → whisper.cpp / ggml-large-v3 / Metal / --vad（silero）/ 约7.5min墙钟 → Fireside shownotes（12 章节时间戳）→ 12 章并行分章润色 → 组装
source_shownotes_chapters: true
notable_correction: "首跑无 VAD 时 whisper 在音乐/过场段陷入循环幻觉（约 39 分钟起整段报废），--vad 重跑恢复；SGLang/RadixArk/盛颖/Elon 等系统性误识别约 200 处已修；Accel 被听成 Axial/Excel，依官方新闻稿修正"
---

# 对话盛颖：SGLang 发起人谈 Infra 的浪漫、xAI 往事与「世间的美好是存在的」

> 嘉宾**盛颖（Ying Sheng）**：RadixArk 联合创始人兼 CEO，SGLang 发起人，xAI 前推理团队负责人。上海交大 ACM 荣誉班 → 哥大 master → 斯坦福 PhD（形式化验证，导师 Clark Barrett）。
> 本期与 [游凯超期](2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.md) 构成开源推理引擎的「双子星对照」：SGLang/RadixArk vs vLLM/Inferact，同一个伯克利圈子（Ion Stoica 两边都是导师），几乎同时成立公司、同样的大额种子轮。

---

## 一、概览

- **人生线**：本想当数学家（「我甚至不需要赚很多钱，我想 stay poor」），因形式化验证「离现实太远」转向 AI；2022 年谷歌实习亲历大模型碾压传统 program analysis（「原来根本不需要什么显式的 reasoning，我是被 shock 到的那个人」），从此扎进 LM inference。
- **SGLang 是 PhD 收官之作**：从第一天就定开源 + production-ready；与 vLLM 是「idea 撞车」的关系，分野在时间轴——**SGLang 先做 scale up（千卡/万卡），vLLM 先做社区覆盖与 long-tail 模型**，如今互相补短板（「老实说其实大家都差不多」）。
- **xAI v1.0 的美好与教训**：「support + freedom」双全的稀缺环境；她亲历的 1.0 时代团结如战友，而今 co-founder 悉数离开——她的诊断：xAI 没抚平「从靠人运转到靠体制运转」的过渡阵痛。
- **RadixArk**：2025 年 7 月「两个月也等不了」地离开 xAI（差 2 个月到一年 cliff，不要了），2026-05-05 官宣 **1 亿美元种子轮、4 亿美元估值，Accel 领投**，股东名单横跨 NVIDIA/AMD/Intel CEO/Broadcom CEO/John Schulman 等。
- **价值观三连**：「我在乎的是 impact，不是 making」（正确的事发生就行，不在乎谁推动）；开源「对我来说是空气一样的存在」（被互联网陌生人养大）；平权——「一个人赢是不需要被解释的，但我的每一场赢都要被解释」。
- **收尾金句**：「我仍然会坚信有一个我想看见的世界，但是我现在没看见，它只是我还没看见它而已」；「你只要不觉得自己在妥协，都没关系」。

## 二、章节地图

| 时间 | 章节 | 核心命题 |
|---|---|---|
| 00:00-16:06 | 违约金、纽约与数学之美 | 宁交违约金也要出国；数学的确定性=心流=「与世界无关」 |
| 16:06-26:01 | 顶刊、低谷期与甄嬛传 | ADHD 自我和解：「找到了怎么使用我自己的一把钥匙」；发 paper/做研究/科学家是三件事 |
| 26:01-31:54 | 谷歌实习：最早的 AI for code | 传统 program analysis 在大模型前「什么忙都帮不上」 |
| 31:54-34:37 | Databricks：Ion Stoica | lifetime mentor；「impact 可能是他做所有事情的动力之源」 |
| 34:37-44:07 | xAI：support + freedom | 无 people game 的 1.0 时代；「在那里待一年顶外面好几年」 |
| 44:07-48:07 | RadixArk：「两个月也等不了」 | 社区网友两年不知道彼此长相；「我只要看到你的代码我就知道你是谁」 |
| 48:07-51:10 | Two Sigma | 「有组织的公司」的样子；infra 稳定性来自业务少巨变 |
| 51:10-01:15:29 | SGLang：「AI Infra 是浪漫的」 | 技术核心章：RadixAttention、day zero、infra 即产品 |
| 01:15:29-01:19:33 | SandHill Road | 融资是被迫学的功课；「所有 average 的东西都有套路」 |
| 01:19:33-01:27:03 | 「养大我」的开源生态 | 江西出身、CSDN/online judge 养大；开闭源共存 + decentralization |
| 01:27:03-01:37:42 | LMSYS：平等与平权 | 「改变 1% 也值得用一生」；赢不需要被解释 |
| 01:37:42-01:46:26 | 世间的美好是存在的 | 书本没有骗我；正反馈循环；割裂是 OK 的 |

## 三、关键人物

| 人物 | 身份 | 与本期关系 |
|---|---|---|
| **盛颖（Ying Sheng）** | RadixArk 联创&CEO；SGLang 发起人；LMSYS 联创 | 嘉宾 |
| **朱邦华（Banghua Zhu）** | RadixArk 联创（官方新闻稿确认） | 共同创业 |
| **连铭[?]**（疑为 Lianmin Zheng 郑连民） | LMSYS/SGLang 联创；盛颖丈夫（节目中自述），同在 xAI | 家人+长期搭档 |
| **Ion Stoica** | 伯克利教授、Databricks 联创 | 她的「lifetime mentor」；也是 vLLM/Inferact 的导师与创始人 |
| **Clark Barrett** | 斯坦福教授（形式化验证/SMT，cvc5） | PhD 导师，「教科书般完美的导师」；低谷期「从来没有断过我的经费」 |
| **Wei-Lin**（疑为 Wei-Lin Chiang） | 把 LM Arena 做成公司的人 | LMArena 归属叙事 |
| 提及 | Elon Musk、John Schulman、陈立武（Lip-Bu Tan）、Hock Tan、Hinton/LeCun/Bengio（拒评未接触过的人） | — |

## 四、主要话题

### 4.1 技术：RadixAttention、day zero 与「infra 即产品」

- **RadixAttention 通俗版**（原话级别）：请求有公共前缀就不必重算其 KV cache；实现 = 对请求前缀关系建**前缀树**做索引 + 把已算 KV 存进 KV memory pool 做映射。多轮对话/agentic 场景几乎必有前缀共享。（与 vLLM PagedAttention 的分页内存管理是不同切入点的互补优化——PagedAttention 解决内存碎片，RadixAttention 解决前缀复用；两者今天的引擎都同时具备。）
- **优先级方法论**：问题是「一次性看见的」，但做要一件一件做；按最大 margin/bottleneck 排序，且有依赖链（先解决 KV cache 管理，才轮得到 prefix caching）。「没有哪个点是难的，就是去做掉就可以了。」
- **day zero 兼容是市场驱动**：用户「第一天就要用上」的人性沿 用户→inference provider→SGLang→模型厂商 链条式传递。DeepSeek V4 架构创新大，SGLang 花了特别大精力做到 feature set 第一天全兼容，并**首次做到 RL 的 day zero**（Miles 框架大部分代码重写）。
- **infra 是浪漫的（本期题眼）**：「infra 不是一个 support 角色，infra 本身在我眼中就是产品」；「没有人会说希望 infra 击中人性，但从我的视角看，infra 也是击中人性的」——taste = 不只关注 end goal，还关注系统是 well-designed 跑起来的还是豆腐渣工程跑起来的。大厂 infra team 是 supporter 角色、在美感上妥协；RadixArk 反过来：training job 可以 pause、刷 benchmark 不是 urgency，问题要 systematically 解决而非打 patch。
- **SGLang 的初心是 language**：当年以 agent 为入口设计，还设计了 frontend 语言；后来因 inference 效率挑战更突出转向 runtime，但「有一天我们会 revisit，最终它还是应该是一个 language 的形式」。
- **inference 市场「没有输家」**：Fireworks/Together 等 provider 多年共存且全部同步增长。（陈茜口述的市场数字：Baseten[?] 3 亿美元融资估值过 10 亿、Fireworks 估值 40 亿、Together 寻求 10 亿新融资——主持人口述未独立核实。）
- **latent space 推理若成熟**，推理引擎很多东西会变，但「这本来就是你写推理引擎的一环，我觉得这个不是变革；真正的难点从来都还是在回归人和团队本身」。
- **RadixArk 的野心**：「我认为 RadixArk 最终使命是要做下一代 AI」——不是模型，是「现代世界上还不存在的东西」（拒绝透露）；inference/infra 只是起点。SGLang 归 LMSYS 社区，公司无 private fork，不靠开源制造差异获利。

### 4.2 创业：从「两个月也等不了」到 Accel 领投

- 社区形态的极限：SGLang 核心开发者全是网上认识的网友，共事两年很多人互不知道长相、开会从不开摄像头——「我只要看到你的代码我就知道你是谁，我也只想看到这个部分」。但 2025 年需求爆发，大家只能熬夜放假写代码，「被 team 的 bandwidth 限制住了，都是 borderline deliver」。
- 2025 年 5 月开始焦虑、7 月到极限：「我再不把这个空白填充的话，我们就快要让外界失望了」——离职时在职 10 个月，差 2 个月到 one-year cliff，vesting 不要了。
- 融资小白扫盲：出来前不知道 Term Sheet、估值、Seed、pitch deck 是什么，靠读书现学；过程「挺曲折」（拒绝展开）；最终「我们容纳[?]下来的这些投资人，也是教科书般完美的投资人」。
- Sand Hill Road 与学术界本质相通：「归根结底所有事情都是人」；「所有 average 的东西都是有套路的」。

### 4.3 开源与平权

- 开源于她是成长环境而非信仰选择：江西长大，编程全靠 CSDN 帖子和 online judge——「我是被互联网上不知道在哪里的人 raise 起来的」；「你有一个 idea 做了一件事，你不分享出来那才觉得奇怪」。
- 开闭源共存论：「闭源它存在，但不 centralize」；RadixArk 提供 toolchain「让所有人都拥有制造属于你自己的 AI 的能力，但你制造出来的 AI 属于你自己」。
- 「全面暂停 AI 研究」违背人性、不可能发生；除非「非常强力的上帝下来安排每一个人」，否则「一定会有人在里面起义」。可见未来 AI 只是功能性取代，但社会/权力结构动荡堪比工业革命；若 AI 真能 dominate 人类则阻止不了，解法是「发明另一条路径，允许 AI 继续前进而人类还不会输」。
- LMSYS 是 non-profit、她的终身事业（「如果 RadixArk 有一天不是走到底的话，LMSYS 是那个我终身会做的事业」）；使命是磨平「没有背景的优秀人才」与 establish 者被看见程度的差异。
- 平权章节金句：「一个人赢是不需要被解释的……但我的每一场赢都要被解释，背后都有个原因叫做我为什么赢，而不是你为什么输」；解法「只有一个方法，就是让所谓的入行者真正拥有权利，你就是不断去赢就好了」。
- 方法论：recursive 链条——「你要培养的是想把学生培养成老师的老师」；「如果我能改变 1%，我愿意用我的一生去改变这 1%」（与 Ion Stoica 的对话）。

### 4.4 自我认知：ADHD、天分的定义与「不妥协」

- ADHD 让她与自己和解：「像是找到了怎么使用我自己的一把钥匙」；被吸引时极度 focus（听不见别人叫名字），不被吸引时完全无法 focus。「很多事情是不要勉强的。」
- 天分定义（金句）：「当外界不把研究当回事、不觉得研究是伟大的事情的时候，你还想做它，那就是你的天分。」
- 「发 paper、做研究、当科学家是三件事」：发 paper 是有套路的技能；真正推动边界的人极少。
- 甄嬛传的顿悟：难题看《甄嬛传》看到中段时，此前读过的 paper 突然 echo 出来——「那真的是有一个 phase transition，是一瞬间的事情」，暂停电视去写。

## 五、引用与提及文献

《甄嬛传》（真实引用，顿悟时刻）；《Fundraising 101》类融资入门书（泛称）；IJCAR 2020 最佳论文（她的 politeness/理论组合工作）；cvc5（SMT solver，她是贡献者之一、TACAS 最佳工具论文奖）。提及但未深谈：H2O（她本人是作者之一）、S-LoRA、Chatbot Arena（LM Arena 前身）、Miles（RadixArk 开源 RL 框架）。

## 六、关键概念词

SGLang / RadixAttention / prefix caching / KV cache / Miles（RL 框架）/ day zero 兼容 / scale up / long-tail 模型 / infra 即产品 / taste / formal verification / SMT solver / cvc5 / ADHD / 心流 / phase transition / making impact / decentralization / LMSYS / LM Arena / one-year cliff / vesting

## 七、关键观点（原话）

- 「我在乎的是 impact，不是 making。」（正确的事发生即可，不在乎谁推动）
- 「我真正自己想做的事情没有人会代劳……你只有自己能够长时间地为那一件事情奋斗，然后让它发生。」
- 「我只要看到你的代码我就知道你是谁，我也只想看到这个部分。」
- 「如果我是在 xAI 上班，我就觉得我要对它有用，不然我就会觉得我不配在这个地方。」
- 「金钱有必须性、没有重要性；如果有天我融不到钱我自己还有钱，这是它对我的意义。」
- 「infra 它不是一个 support 角色，infra 本身在我眼中就是产品。」
- 「当外界不把研究当回事的时候你还想做它，那就是你的天分。」
- 「一个人赢是不需要被解释的……但我的每一场赢都要被解释。」
- 「我仍然会坚信有一个我想看见的世界，但是我现在没看见，它只是我还没看见它而已。」
- 「你是不是按照你自己的想法去认知和行动，还是你其实是被别人牵着走的——你只要不觉得自己在妥协，都没关系。」

## 八、关键数字

- RadixArk：**1 亿美元种子轮、4 亿美元估值**，2026-05-05 官宣，Accel 领投、Spark Capital 共同领投；投资人含 NVentures（NVIDIA）、AMD、MediaTek、Intel CEO 陈立武、Broadcom CEO Hock Tan、John Schulman、Soumith Chintala、Thomas Wolf、Igor Babuschkin（xAI 联创）等（官方新闻稿核实，[BusinessWire](https://www.businesswire.com/news/home/20260505077157/en/)；转写中「Axial/Excel 领投」系 whisper 误识别）
- SGLang：跑在全球**数十万张 GPU** 上，每天为谷歌/微软/英伟达/xAI 生成**数万亿 token**（节目开场白，制作方陈述）
- xAI：她 2024 年 10 月加入时不到一百人；2025 年 7 月离职时在职 10 个月（放弃差 2 个月的 cliff）
- 竞赛：NOI 银牌（「我没有拿金牌」）；纽约区域赛冠军（「队友带飞」）
- 形式化验证三年三篇 paper，每篇真正动笔约三个月；sequencing 论文证明 20 多页、推翻重写两次
- 转写统计：音频 147MB（实测，192kbps）；raw 34,164 汉字 / 5,578 段；polished 33,726 汉字；语速 321 字/min

## 九、Limitations

- **首跑转写曾整段报废**：无 VAD 时 whisper 在音乐/过场段陷入循环幻觉（约 00:39 起循环输出前一期小宇宙广告词），`--vad`（silero）重跑后全量正常。此教训已写入 AGENTS.md 转写经验。音频实际内容完好（volumedetect 各段 -18dB 正常语音电平）。
- **whisper 系统性误识别约 200 处已修**（分章校正清单合计）：`SG Lane/SGMA/Edgeland`→SGLang、`ReddixArc/Radi Shark/Red Sox`→RadixArk、`施琳/摄影`→盛颖、`一浪`→Elon、`Young Stoica`→Ion Stoica、`PSC`→PhD、`Taxbook`→textbook 等。
- **约 60 处 [?] 不确定项保留原文**，重要的：`连铭[?]`（盛颖丈夫，疑为 Lianmin Zheng 郑连民，汉字写法未确认）、`Wei-Lin[?]`（LMArena 公司化主导者，疑为 Wei-Lin Chiang）、ch8 的 `Coconut[?]/Cola[?]`（latent 推理工作所指）、若干处语义存疑。
- **身份更正**：我最初给润色 agent 的简介写「清华→哥大→斯坦福」，转写原文为**上海交大 ACM 荣誉班**，以转写为准（已改）。
- **主持人口述未核实**：Baseten/Fireworks/Together 的融资估值数字、片尾「xAI 被 SpaceX 收并购且上市」的表述（指 2026 年 SpaceX 收购 xAI 及 SpaceX IPO 语境，未独立核实）。
- 陈茜在 ch8 口述「vLLM 核心团队年初商业化成立 Inferact，融资 1.5 亿美元、估值 8 亿」——与公开报道一致（见游凯超期报告），已交叉验证。

## 十、思考与追问

1. **SGLang vs vLLM 的「时间轴分野」会收敛还是分叉？** 盛颖说「大家都差不多，分野在时间轴上」（SGLang 先 scale up，vLLM 先社区覆盖）。两家几乎同时商业化（RadixArk vs Inferact）、同一个导师（Ion Stoica）、同一批投资人圈层——开源推理引擎会走向双寡头、合并，还是被云厂商收编？挂 vLLM 源码线：阶段 1/3 时对照 SGLang 的 scheduler 源码读一遍。
2. **RadixAttention（前缀树）vs vLLM prefix caching（哈希块表）**：两种前缀复用数据结构的真实差异在哪——命中率、开销、适用场景？这是不是理解两家引擎性格的显微镜？挂 vLLM 源码线阶段 2（正好读 `v1/core/` 的 block pool）。
3. **「infra 即产品、infra 击中人性」能成立吗？** infra 的「taste/美感」能否转化为可衡量的竞争优势（留存、成本、开发者心智），还是终究只是 founder 偏好？对照组：RadixArk「无 private fork」的纯开源路线 vs Inferact 的 Endpoint/BYOC 按量收费，五年后谁还活着、活得好？
