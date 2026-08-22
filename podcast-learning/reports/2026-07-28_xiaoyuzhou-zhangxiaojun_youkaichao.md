---
title: "对游凯超3小时访谈：开源Infra、和模型Co-design、「如果vLLM失败，我们会后悔一辈子」"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6a66ed17a3fec224d5a3f744
show: "张小珺Jùn｜商业访谈录"
episode: "Vol.148"
host: "张小珺"
guest: "游凯超（Kaichao You）"
duration: "3h00m26s"
duration_seconds: 10826
transcript_segments: 6120
hanzi_chars_raw: 53373
hanzi_chars_polished: 49568
total_chars_raw: 206959
total_chars_polished: 61150
audio_size_mb: 173
speech_rate_cjk: "296 字/min (raw)"
chapters: 8
polished: true
polished_by: "Kimi (kimi-cli-k3)，8 章并行分章润色"
polished_at: 2026-08-22
status: archived
created: 2026-08-22
updated_on: 2026-08-22
transcript_path: reports/transcripts/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.transcript.txt
polished_transcript_path: reports/transcripts/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.polished.txt
pipeline: yt-dlp → whisper.cpp / ggml-large-v3 / Metal / 约16min墙钟 → episode 页 JSON-LD + shownotes（8 章节时间戳）→ 8 章并行分章润色 → 组装
source_shownotes_chapters: true
notable_correction: "whisper 系统性误识别约 300 处（VLM/VM/为我们→vLLM 70+、杨斯多伊克→Ion Stoica 20+、归机→硅基、推力引擎→推理引擎、语言集世界→语言即世界 等），约 40 处不确定项标 [?]"
---

# 对游凯超 3 小时访谈：vLLM 三年，从论文到社区到公司

> 嘉宾**游凯超（Kaichao You）**：Inferact 联合创始人兼首席科学家、vLLM 核心维护者（第四个主要成员）。清华大学本博（2019 年清华特奖），2019 暑研 Berkeley Michael Jordan 组，2024 赴 SkyLab 交流时加入 vLLM。
> 本期既是 vLLM 的「官方口述史」，也是一位系统派研究者对「模型 × Infra × 硬件 co-design 时代」的完整方法论输出。
> 关联：本期与 ai-learning 的 [vLLM 源码级学习线](../../ai-learning/wiki/concepts/vllm_v1_architecture.md) 互为表里——那边读代码，这边读人。

---

## 一、概览

- **vLLM 三年三级跳**：SOSP 2023 论文「低分过线」（审稿人批 Too Simple）→ 因 Artifact Evaluation 要求开源的原型 → 2023 年 6 月开源 → 2024 年 V0→V1 大重构 → 2025 年捐入 PyTorch 基金会（顶级项目，商标归社区）→ 2025 年底成立 Inferact，2026-01-22 官宣 **1.5 亿美元种子轮、8 亿美元估值**（a16z + Lightspeed 领投，Sequoia/Altimeter/Redpoint/真格跟投——融资细节为公开报道，见 Limitations）。
- **治理模式是「仁慈的独裁者」分级制**：4 人决策层 + 十来个核心维护者 + 几十个 Committer + 2000 多贡献者；管理的核心是取舍——游凯超亲自把 Beam Search 从引擎里删掉（「要做什么，更重要的是不做什么」）。
- **创业的三个硬约束**：人力（社区人来人往撑不起长期 feature）、法务（新模型/新硬件的 NDA 开源社区不是实体签不了）、机器（2025 年起必须集群级优化，只能各处「乞讨」算力）。注册前夕某顶级大厂给四位创始人每人 **2000 万美元年薪**挖角，全员无犹豫拒绝——本章标题来历：「如果我们自己赚了很多钱但是 vLLM 项目失败了，我觉得我们都是会后悔一辈子的」。
- **技术主线：co-design 时代**。摩尔定律终结 → 专用算力时代 → 算法必须抽中「硬件彩票」（被系统高效实现）才能存活；模型结构决定推理效率上界；DeepSeek 的护城河是算法 × infra 双料人才坐在一起。
- **宏观判断**：开源模型最后会赢（token 带着模型的烙印 → 模型藏不住 → 护城河只在迭代速度）；token 不是电（异质、不可调制、非 commodity）；与人打交道的模型上下文需求百万级就够（hot take）。

## 二、章节地图

| 时间 | 章节 | 核心命题 |
|---|---|---|
| 00:00-00:37:56 | 开场白 + 从算法到机器学习系统 | 学术圈「礼崩乐坏」+ 算法成果依赖大规模系统 → 转向系统；「你可以说我的东西不 novel，但是不可以说我的东西没有用」 |
| 00:37:56-01:07:25 | 开源项目 vLLM 的诞生 | 伯克利五年周期传统（AMPLab→Spark、RISE→Ray、SkyLab→vLLM）；PagedAttention 论文「Too Simple」低分过线 |
| 01:07:25-01:20:11 | 「如果 vLLM 失败了，我们会后悔一辈子」 | 为什么大厂靠不住、必须有公司；2000 万美元挖角与「后悔一辈子」说服话术 |
| 01:20:11-01:37:16 | 「仁慈的独裁者」 | 分级治理；删 Beam Search；coding agent 打破开源善意假设（AI slop） |
| 01:37:16-01:52:56 | 从社区到创业 | 先有基金会捐赠后定公司；Inferact = Bring Inference into Action；按量收费而非卖工程师时间 |
| 01:52:56-02:15:10 | 模型与 Infra 的 Co-design | hardware lottery；RoPE 案例；DeepSeek 双料模式；投机解码谱系（EAGLE/MTP/DFlash/DSpark） |
| 02:15:10-02:35:41 | Token VS 电力 | token 异质不可调制、非 commodity；Test-Time Scaling 三阶段；FP8 分块量化案例；第一性原理方法论 |
| 02:35:41-03:00:26 | 技术预测（含快问快答） | 上下文 hot take；开源模型会赢的第一性论证；「硅基提供执行能力，人类提供灵感」 |

## 三、关键人物

| 人物 | 身份 | 本期角色 |
|---|---|---|
| **游凯超** | Inferact 联创兼首席科学家；vLLM 核心维护者；清华本博（2019 特奖） | 嘉宾 |
| **Simon Mo** | Inferact CEO；曾 Anyscale 创业、Character.AI；vLLM 第三个全职维护者 | 创始团队 |
| **Woosuk Kwon** | Inferact CTO；PagedAttention 一作；「历史上的技术决策都是他做的」 | 创始团队（被「逼宫」回归） |
| **Ion Stoica** | Berkeley 教授；Databricks 联创；LMArena 发起人 | Inferact 创始人之一/advisor，开公司的主要推动者 |
| **李卓翰（Zhuohan Li）** | vLLM 论文主要作者、发起人之一 | 2024 毕业最早未能等创业，现于 Meta（曾 OpenAI） |
| **Roger** | 合伙人，与团队共做开源多年 | 创始团队 |
| **Michael Jordan** | Berkeley 教授（机器学习理论派） | 游本科暑研导师，劝其长期支持 vLLM |
| **David Patterson** | 图灵奖得主 | 《How to build a bad research center》(2014) 与「后摩尔时代 AI 上限取决于系统」论断出处 |
| **季逸超（Peak）** | Manus 创始人 | 本期介绍人（2025-12 介绍，当时 Manus 尚未被 Meta 收购） |
| 提及 | 何凯明（个人心中算法天花板）、张祥雨（2022 年点醒他的硬件现实）、杨植麟（Kimi 学长）、翁嘉义[?]（本科同学/天授合作者，疑为翁家翌 Jiayi Weng）、Edward Yang（PyTorch 维护者，同类博客）、Songlin Yang 松林（FLA 作者） | — |

## 四、主要话题

### 4.1 从算法到系统的人生转向

游凯超的转向是三条线汇成的：① **学术圈「礼崩乐坏」**——2018 年入行时一届会议几百篇论文、审稿有建设性；投稿量几何增长后「投稿就像抽彩票」「大厦将倾，不是我能改变的」；② **算法成果依赖大规模系统**——以何凯明为天花板，「同样的 idea 组会上也讨论过、做过小实验」，但「我们只是在玩玩具数据集，螺蛳壳里做道场」，支撑实验的系统与数据才是成败关键，而非「雕 cross entropy 的五种加权方法」；③ **工业界的真实痛点**——2022 年拉着张祥雨聊一个多小时，发现目标检测大佬头疼的不是调参而是特化硬件的多级缓存、给英伟达写算子。

系统的吸引力在于**确定性**：算法要争 novelty，系统只说加速多少倍、可验证可归因；衡量标准从论文引用数变成 GitHub star 和 issue 里的感谢信，论文变成系统做好后的副产物。金句（原话）：「你可以说我的东西不 novel，但是你不可以说我的东西没有用。」

### 4.2 vLLM 诞生与伯克利传统

- 谱系：BSD、RISC-V、RAID、Spark、Ray 都出自伯克利；David Patterson《How to build a bad research center》（2014）：实验室只做五年（一个博士周期），与工业界需求「共振」时诞生重要项目——AMPLab→Spark、RISE Lab→Ray、SkyLab→vLLM。
- 时间线：2022 年底启动，SOSP 2023 中稿，2023 年 6 月开源。**PagedAttention 的学术创新性「甚至是偏低的」**，被批 Too Simple，「以低分过线的状态被会议接受」；开源契机是 Artifact Evaluation 要求。Ion Stoica 看到机会推动学生团队重点维护。
- 游凯超 2024 年加入，是第四个主要成员（李卓翰 + Woosuk 最初维护 → Simon 第三 → 游第四）。入伙判断：2023 年底大家都在研究怎么训模型，「你把模型训出来之后你需要去做推理」。
- 两年主旋律：2024 = V0→V1 大重构（「最难的是保持用户兼容」）；2025 = 大规模部署 + 开源重心从欧美转到中国（他 2024 年 12 月回国恰逢 DeepSeek V3/R1 爆发；DeepSeek 内部基于 vLLM 的自优化变种「比我们往前面走了很多，我们当时在不断地跟他们学习」）。

### 4.3 开源治理：仁慈的独裁者与 coding agent 冲击

- 结构：4 人「仁慈的独裁者」决策层（Simon、Woosuk、游凯超、Johan[?]，外加 Red Hat 同学）每周碰一次 → 十来个核心维护者 → 几十个 Committer → 2000 多贡献者。2025 年 GitHub 统计按贡献者活跃度 vLLM 是全 GitHub 最活跃项目（自述）。
- **取舍实例**：游凯超亲自删掉 Beam Search——推荐系统用户持续抱怨，但大模型推理主 workload 已不需要它，继续维护只会累积不可维护的复杂性。「你需要对方向进行一些取舍，就是不能够做一个老好人。」几百兆小模型同理不接：「你可以用我们，但是如果你有这方面的性能优化的需求我们并不会接。」
- **coding agent 打破善意假设**（本期最有信息量的治理段落）：2026 年 5 月发现培训机构批量提交垃圾 PR 给学员包装简历（「我是 vLLM 贡献者」）。「它彻底打破了我们对于开源社区的用户都是善意的这一基本假设。」应对：认证机制、重视知名机构来源、拉黑机器人（十分钟 20 个 PR 必为机器人）、纯 AI 生成的无营养 PR 称「AI slop」直接 block。
- 他的演进判断：代码变廉价 → 维护者看 PR 不如自己让 coding agent 重写（自己有更多 context）→ 社区二分为**维护者 + 用户**，用户只提 bug report / feature request。vLLM 不走「AI 提交、AI 审、AI 合并」的自治社区路线，因为维护是在解决「接下来将要发生的问题」（未来 3 个月的新模型、半年到一年的新硬件），必须带人的 context。

### 4.4 从社区到公司

- **为什么必须有公司**（Ion Stoica 2023 年起劝）：Linux 有 Red Hat、Kubernetes 有 Google、PyTorch 有 Meta、Spark 有 Databricks——vLLM 体量已到量级却缺支撑公司。大厂靠不住（Meta/NVIDIA/AMD 互为利益相关，只能做参与者不能做战略决策）；Simon 在 Character.AI 内部借人借机器也行不通。
- **顺序很重要**：先捐给 PyTorch 基金会（2025，商标归社区、法律保证永远开源、基金会只做治理辅助不管技术），后定公司。「如果我们想做闭源的话，我们就可以自己去找家公司做了。」
- 2025 年三大困境倒逼：人力 / NDA 法务 / 集群级机器（「花一个月劝对方给机器、机器一个月就到期、135 我要自己拿过来用 246 给你用、甚至提前一小时紧急收回」）。Ion Stoica 警告「这个公司再不成立，这个项目就要完了」。
- 分工与商业化：Simon 任 CEO；四位主要创始人「四位一体、共享一个大脑」；Ion 任 advisor。公司名 Inferact = **Bring Inference into Action**。模式：Endpoint Service / BYOC / 生态合作，按量收费——「我们不是技术外包，我们不是在售卖工程师的时间。」商业客户与社区冲突时「我们不接这样的商业客户」（供少于求的底气）。
- 公司成立后 30 多人近 40 人；种子轮后仍有人开价几千万美元 SAFE 求下一轮入场；「我们不是为了融资而融资」，下一 milestone 是打通可规模化的商业模式。

### 4.5 模型 × Infra × 硬件 co-design

- **hardware lottery（硬件彩票）**：摩尔定律黄金期软硬件各自为战（通用性能两年翻一倍）；结束后进入专用算力时代（黄氏定律：算力两年翻几倍但都是专用算力），算法用不上专用算力 = 没抽中彩票。例：Hinton 强推 Capsule Network，概念 make sense 但 GPU 不友好，至今未广泛应用；「Transformer 就是抽中了 GPU 的彩票」（大量矩阵乘法、适合并行）。（概念出处实为 Sara Hooker 2020，嘉宾访谈中有澄清非 Patterson 所写。）
- 「模型的结构决定了推理效率的一个上界，如果你的上界太低了，系统工程师就无力回天了。」「模型团队和 infra 团队如果各干各的，我觉得这个团队就完全没有前途。」假想反例：head size 开 1024，infra 团队会晕过去。
- **RoPE 案例**：FlashAttention 成训练必须后，凡需改 attention kernel 内部实现的位置编码（ALiBi 等上百种）都被淘汰；RoPE 独立注入 query/key、与 kernel 互补，成为最佳搭档——「模型结构与 infra 共鸣」。
- **DeepSeek 模式**：infra 团队全球顶级（功底源自幻方量化自建机房的全栈压榨），且算法同学懂 infra——DeepSeekMoE 的高效粗粒度实现、细粒度 MoE 在推理系统的首次实现都出自算法同学。机制：招双料人 + 坐在一起办公耳濡目染。反例：infra 太主导时会为负载均衡选 expert choice 路由，算法上不可接受。
- **投机解码谱系**（与 ai-learning 投机解码线直接衔接）：EAGLE/MTP 猜 3-5 个 token、接受率高；DFlash 一次猜约 16 个、验证浪费算力；DSpark 按置信度把大概率不准的 token 丢掉不再验证（16 → 只验前 8）。算法上不算 novel（腾讯混元 DCart、上交 Domino 更早），但「DSpark 继承了 DeepSeek 一如既往非常扎实的 infra 基础，把推理优化压榨到极致」。vLLM × NVIDIA 技术博客：DFlash 支持使某些模型达**每秒上千 token**。
- **FP8 案例**：Hopper 卖点 FP8（比 16 比特快两倍）；DeepSeek 第一个大规模跑通 FP8 训练，靠分块量化（符合下一代 MX 格式）+ 矩阵乘法后用向量单元累加，精度不损失「领先了其他竞争对手一个身位」，细节都公开在技术报告里。
- **第一性原理方法论**：不懂 continuous batching 只能修修补补、不懂 GPU 性能测试做优化像抽彩票；他从 GPU 编程模型推出「应存在 core dump 工具」，倒逼英伟达找出 CUDA Core Dump 并推广。「通过第一性原理去看清楚这个时代发展的主线，然后屏蔽噪音，持续在一个有用的方向投入。」

### 4.6 Token vs 电力与宏观判断

- 类比框架：token=电、模型=发电机、硬件=风光水自然资源、推理引擎=电力系统（屏蔽模型与硬件复杂性）。但**token 不是电**：电可调制、出口统一 220V；token 带着模型的烙印、不可跨模型转化、异质——「它不是像电一样的 commodity」。Harness 设计、训练期 Harness、推理引擎都影响产出 token 的质量。
- Test-Time Scaling 三阶段：Ensemble（scale 次数）→ o1 式长思考（scale 单次输出几十万 token，只服务特殊群体）→ 2026 Coding Agent 爆发（scale 环境交互次数，每次思考仅几百 token；**prefix caching 成关键**）。Agent 场景需要 Harness × Infra co-design：保持前缀稳定复用计算；反例是 System Prompt 塞精确到秒的时间戳 + 定时任务卡整点——Moonshot 同学的说法：「一群小龙虾（OpenClaw）一到整点就集体出动攻打月球」。
- **开源模型最后会赢**（他最重的判断）：模型不是核武器——「你只需要爆炸一次给别人看」对模型不成立；民用技术必然大规模使用 → 必然被收集数据 → 必然能被复制（公司级机构约一个月可收集足够自训数据）；「每一个 token 它都是带着模型的烙印的」，模型藏不住；护城河只在快速迭代。「你 bet 中国，我 bet 开源模型；中国模型开源我就支持中国模型，其他国家的模型开源我也支持。」
- 由此推出 Inferact 的生态位：模型公司自研引擎难以外部部署（DeepSeek 再给 10 倍机器也无法马上产出 10 倍 token），vLLM 做「更公用化的推理」；Red Hat 已把 vLLM 打包进多个企业发行版——「AI 操作系统」。
- Hot take：与人打交道的模型上下文需求**百万级**就够；长程任务/终身学习靠外部工具（记忆模块、技能模块、subagent）；若此预测成立，现有模型结构与 Infra 范式还能延续很久。生化等自然科学数据可能需千万/亿级。
- 历史观：技术指数积累到临界点，AI 把整个人类历史拿来训练；理想状态「硅基提供执行能力，人类提供灵感」。
- 冷知识（原话类）：给大模型输入 **1000 个感叹号**，它一定会输出大量感叹号——可从吐出的 token 反推对方推理引擎开了几步投机采样。

## 五、引用与提及文献

shownotes 本期无书单。提及：David Patterson《How to build a bad research center》（2014）；《送东阳马生序》（「以中有足乐者，不知口体之奉不若人也」自况）；论文 Transformer / GPT-3 / FlashAttention / vLLM（PagedAttention, SOSP 2023）/ Flash Linear Attention；李宗盛《山丘》（「想说却还没有说的还很多」）；维特根斯坦「我的语言的极限就是我的世界的极限」（游的现场联想：五次以上方程无有限求根公式——语言之外或有更高维存在）。

## 六、关键概念词

vLLM / PagedAttention / continuous batching / co-design / hardware lottery（系统彩票）/ 仁慈的独裁者（BDFL）/ AI slop / PyTorch 基金会 / SAFE / BYOC / Endpoint Service / EP / DP / EAGLE / MTP / DFlash / DSpark / prefix caching / FP8 分块量化 / MX 格式 / Token vs 电力 / commodity / 数据飞轮 / scaling law / RoPE / ALiBi / DeepEP / DeepGEMM / NSA

## 七、关键观点（原话）

- 「你可以说我的东西不 novel，但是你不可以说我的东西没有用。」
- 「有的人追求金钱……有的人追求权利……我觉得我追求的就是意义，就是我做的事情是不是有意义。」
- 「如果我们自己赚了很多钱但是 vLLM 项目失败了，我觉得我们都是会后悔一辈子的。」（说服 Woosuk 的原话变体：「十年之后我们项目失败了，你是开心还是不开心」）
- 「要做什么，更重要的是不做什么。」
- 「它彻底打破了我们对于开源社区的用户都是善意的这一基本假设。」（coding agent 时代的垃圾 PR）
- 「如果你没有办法清晰的写下来，说明你对它还不够了解。」「你需要大胆猜想，但是小心求证。」
- 「模型的结构决定了推理效率的一个上界。」
- 「这个 token 它是带着模型的烙印的。」「Token 它比电复杂很多，它有一个异质性在这里，它不是像电一样的 commodity。」
- 「只要你是一个好的软件，总会有人用的。」（Ion Stoica，转述）
- 「通过第一性原理去看清楚这个时代发展的主线，然后屏蔽噪音，持续在一个有用的方向投入。」

## 八、关键数字

- Inferact：种子轮 **1.5 亿美元**、估值 **8 亿美元**（2026-01-22 官宣，公开报道；shownotes 亦述）；公司 30 多人近 40 人（自述）；种子轮后仍有人塞几千万美元 SAFE 求下一轮（自述）
- 挖角 offer：**每人年薪 2000 万美元** × 4 位创始人，某顶级大厂一号位亲自致电（自述）
- vLLM 社区：贡献者 **2000 多家**（自述）；2025 年 GitHub 统计全站最活跃项目（自述）；支持**两三百种**模型结构（自述）
- 融资前史：2023 年起 VC 资助几十万美元级；2024 年 Sequoia、真格以开源社区捐赠形式给钱（自述；Simon Mo 曾入选 Sequoia Open Source Fellow）
- 投机解码：EAGLE/MTP 猜 3-5 token；DFlash ~16 token；DSpark 示例 16→验前 8；DFlash 在 vLLM 内使某些模型**每秒上千 token**（自述）
- 训练：推理开销现已可达 **1:1**（嘉宾判断）
- 转写统计：音频约 173MB（按 128kbps × 10826s 估算）；raw 53,373 汉字 / 6,120 段；polished 49,568 汉字；语速 296 字/min（正常区间 300-400 下沿）

## 九、Limitations

- **whisper 系统性误识别约 300 处已修**（分章校正清单合计）：最大族是 `VLM/VM/VOM/为我们/维吾尔文` 等 → `vLLM`（70+ 处，均已确认语境为推理引擎；视觉语言模型语境已排除）；`杨斯多伊克/IoStoic` 等 → `Ion Stoica`（20+ 处）；`归机→硅基`、`探机→碳基`、`推力引擎→推理引擎`、`语言集世界→语言即世界`、`DeepSeq/DeepSig→DeepSeek`、`小骏→小珺`、`Infrot→Inferact`、`David Pattinson→David Patterson`、`F18→FP8`、`记忆超→季逸超`、`换方量化→幻方量化` 等。
- **约 40 处不确定项保留原文标 [?]**，重要的几个：`翁嘉义[?]`（多处变体统一；据「天授合作者/知乎青苹果」语境疑为翁家翌 Jiayi Weng，未 100% 确认）；`Johan[?]`（决策层第四人，疑为 Zhuohan 的音误）；ch6「某海外大咖」整段人名被吞（02:06 前后，语境指向某海外 AI 公司一号位，无法确定，勿猜）。
- **嘉宾口述的两处事实性存疑**（未改正文，按原话保留）：① OpenSSH「十多年前漏洞致全世界裸奔、事后成立基金会」——史实对应 **OpenSSL Heartbleed（2014）** 与 Core Infrastructure Initiative，OpenSSH 无此事件，疑为口误；② ALiBi 被称为「absolute position bias」——ALiBi 实为基于相对距离的线性偏置。另：hardware lottery 概念出处为 Sara Hooker（2020），嘉宾访谈中已自行澄清非 Patterson 所写。
- **数字口径**：融资细节（估值 8 亿、a16z/Lightspeed 领投、Sequoia/Altimeter/Redpoint/真格跟投、2026-01-22 官宣）来自公开报道（TechCrunch/彭博/真格官宣，已交叉验证），访谈自述仅「1.5 亿美元种子轮」；嘉宾自述的经营/性能数字（2000 万挖角、2000 家贡献者、每秒上千 token 等）未独立核实。
- whisper 无说话人区分，对谈归属按语义判断；音频未保留（大小为估算）。

## 十、思考与追问

1. **「vLLM 是 AI 推理领域的 Linux」的商业类比成立到什么程度？** Red Hat 靠订阅支持收费，Inferact 是 Endpoint Service/BYOC 按量收费——卖「运行开源软件的确定性服务」与卖「 token 计量」的单位经济完全不同。开源推理引擎商业化的历史窗口有多大（模型公司自研引擎外溢 vs 公用推理的张力）？可结合 ai-learning 行业观察线的「薄毛利打穿点」框架对照。
2. **「系统彩票」如何反塑模型架构？** 若算法必须被系统高效实现才能存活，下一代硬件（NVIDIA 路线图、国产卡）的押注者就在间接设计未来的模型。RoPE/FlashAttention 的共赢能否复制到 linear attention（KDA/Gated DeltaNet 等）？——与 ai-learning 的 K3 报告、vLLM 源码线阶段 3（attention backend 选择机制）直接联动。
3. **coding agent 时代的开源治理分岔**：vLLM 走「人审 + 认证 + 拉黑 AI slop」，OpenClaw 式社区走「AI 提交、AI 审、AI 合并」。如果维护的核心价值是「解决未来 3 个月问题的 context」，AI 自治社区能积累这种 context 吗？开源社区的价值是否正从「代码贡献」不可逆地迁往「维护者判断」？
