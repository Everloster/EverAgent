---
title: "智能的下一幕：庄明浩 73 页 PPT 的 2026Q3 行业复盘（模型狂奔/智能分化/循环自生/界面重构）"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6aa82d11129fe965d33288ca
show: "屠龙之术"
episode: "2026-09-15 单口《智能的下一幕，让人兴奋——73页PPT solo》"
host: "庄明浩"
guest: "（单口）"
duration: "55m21s"
duration_seconds: 3320
transcript_segments: 2009
hanzi_chars_raw: 12452
hanzi_chars_polished: 11863
speech_rate_cjk: "225 字/min"
chapters: 4
polished: true
polished_by: "Kimi (k3) 润色 + eacli 核查"
polished_at: 2026-09-22
status: archived
created: 2026-09-22
updated_on: 2026-09-22
transcript_path: reports/transcripts/2026-09-15_xiaoyuzhou-tulong-zhishu_next-act.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-15_xiaoyuzhou-tulong-zhishu_next-act.polished.txt
pipeline: yt-dlp → whisper.cpp / ggml-large-v3 / Metal / VAD → eacli web.read shownotes → 按四章重组 → eacli web.search 抽查核实
source_shownotes_chapters: true
notable_correction: "公司/术语修正 80+ 处（DeepSick→DeepSeek、SOPIC→Anthropic、SpecialX→xAI、Glock→Grok、Skill.ai→Scale AI、Aftercurry→AfterQuery、KPIX→CAPEX 等）；45 处 [?] 存疑（国产办公 agent 产品名等）"
---

# 智能的下一幕：庄明浩 73 页 PPT 的 2026Q3 行业复盘

> 屠龙之术的单口大整理（PPT 制于 9 月上旬，为一家"内部 agent 程度很高"的金融机构演讲改做）。**注意特殊性**：听众要求"往高了讲、不讲二级/一级叙事"，所以 CAPEX、Mag 7、上市融资全部没展开——本期集中在技术+产品。四章：模型狂奔 → 智能分化 → 循环自生 → 界面重构。

## 一、概览

- **模型侧**：供给爆炸到"制造业化"——8-9 月中美头部各发 20+ 模型；OpenRouter 口径 2026 年 4 月达 80 个/月（日均 2 个）；版本号要加日期后缀；benchmark 失效后"需要奇观"（阑夕）；本地 30B 模型追平 SOTA 的延迟从 33 个月缩到 **9 个月**。
- **企业侧（本章最硬）**："用最新最强最贵"的默认前提松动了——Ramp 数据显示 Fable 5 发布后 Claude 系付费占比涨不动；Top 1% 企业人均月 AI 花费 8000 美金 **7 月见顶 8 月回落**；SOTA 单价"过一段时间降一个零"。→ 企业开始算账，红杉语境的 **Own Your Intelligence**（自建智能）登场。
- **产业分工**：模型训练全环节商品化（评估/harness/RL 环境/数据）——Brex 夏榜 Top 25 增长最快 software vendors 里 **14 家**是帮别人构建 AI 模型的；YC 26 夏 200+ 项目里 8 家瞄着 Scale AI；AfterQuery（YC W25 数据公司）五个月估值 3 亿→32 亿美金。
- **Loop/RSI**：《When AI builds itself》+ Sam L1-L5 + 智谱 GLM-6.0"全自训" + Jeff Dean 的 ∞ logo + Ilya 的 TTT + 田元栋公司就叫 RSI——大佬共识收敛到"循环自生"；119 家 new lab 融了 **943 亿美金、仅 16 家公开收入、英伟达投了近 1/3**。但 a16z 四象限泼冷水：只有"强可验证+易编辑"（code/3D）被证明，**"Loop 是一种结构，但不是魔法"**。
- **界面**：苹果 App Store 收入**十年来首次下降**；agent 共识收敛到 coding + personal agent；Codex 周活 2500 万；他吐槽国产办公 agent"把复杂度甩给用户"（侧边栏堆满套件），叙事正在移向 personal AI assistant——"办公 agent 回头看是不是一段弯路？"

## 二、章节地图

| 章 | 时间 | 核心命题 |
|---|------|---------|
| 开场+关键词 | 00:00-07:25 | 六词定调：RSI / Auto Research / Loop / New Lab / Router / Benchmark |
| 一、模型狂奔 | 07:25-20:21 | 发布密度爆炸；制造业化；benchmark 失效→奇观传播；中美/开闭源/云本地分化 |
| 二、智能分化 | 20:21-39:46 | 两大收购（Stripe×OpenRouter、NVDA×HF）；前提松动+价格坍塌→Own Your Intelligence→全环节商品化 |
| 三、循环自生 | 39:46-47:47 | AI 改进 AI 成共识；new lab 疯狂融资与里程碑缺位；a16z 四象限划边界 |
| 四、界面重构 | 47:47-55:21 | App Store 十年首降；coding+personal agent 共识；复杂度批判；国产之问 |

## 三、关键数字（主播转述口径，未经独立核实）

| 数字 | 含义 |
|------|------|
| 80 个/月（2026-04） | OpenRouter 口径模型发布峰值，日均 2 个 |
| 33 → 9 个月 | 本地小模型追平 SOTA 的延迟（GPT-3 年代 → Opus 4.5/千问3.8 27B） |
| 8000 美金/人/月 | Top 1% 企业人均 AI 花费，7 月见顶 8 月回落（Ramp） |
| 53% → 45% | 用最贵档模型的企业占比（8/2→9/6，Ramp） |
| 2/3 vs 1/3 | OpenRouter token 量：开源 et al. 占 2/3、御三家 1/3；花费恰好反过来 |
| 70 亿 / 129 亿美金 | Stripe 收 OpenRouter / 英伟达收 Hugging Face（8-9 月两笔中间层收购） |
| 150 亿美金 | Harvey 新一轮融资额（AI 法律） |
| 943 亿 / 119 家 / 16 家 / 34 家 | new lab 总融资 / 家数 / 公开过收入的家数 / 英伟达投资家数 |
| 2500 万 | Codex 周活（5 月 500 万 → 7 月 900 万 → 2500 万） |
| 十年首次 | 苹果 App Store 收入首次下降 |

## 四、主要话题

### 1. 大模型=残酷的制造业
引赞爱[?]三段：模型厂没有本质区别，无非谁强发谁晚发几天；"判断一个行业是不是制造业的硬指标是马斯克能不能玩明白"；现阶段大模型团队需要"包工头带大伙 007 做题"。benchmark 失效后，评测视频集体转向 3D 效果——阑夕："模型的传播与能力界定需要奇观"。

### 2. Own Your Intelligence（本期题眼）
企业算四笔账：成本、速度、好标准、数据把控。执行路径（红杉）：定战略→设评估标准→harness 与路由→提示词→数据准备→后训练→中训练→online learning——**每个环节都有厂商在商品化**。Harvey 的三步样板：建法律 benchmark → 用它后训练 → 找 infra 厂商合作（RL 环境找 LangChain）。**"没有评估就没有真正的进步。"**

### 3. Loop 与 RSI：共识收敛，但里程碑缺位
大佬们收敛到循环自生（Jeff Dean 的 ∞、Ilya 的 TTT、Mira 的 human-in-the-loop、智谱"全自训"）。但两个问题没答案：①Loop 之后的估值里程碑是什么（SaaS 有阶段、生物医药有临床，new lab 拉人组队发榜"都能算吗"）；②a16z 四象限——只有可验证×可编辑的 code/3D 被证明，物理 AI 难，内容板块弱验证强编辑。

### 4. 界面：复杂度应该产品自己消化
"侧边栏堆满专家套件/技能/连接器/定时任务……向来如此便对吗？这种复杂度不应该产品自己消化吗？"正面案例：Grok Bot、Meta Muse。他观察到产品叙事一年迁移链：Code → OpenClaw 龙虾 → Work → Grok Bot → Muse（personal assistant），问"国产办公 agent 要跟吗？回头看是不是弯路？"

## 五、与 2026-07-17「CAPEX 泡沫之辩」期的关系（续集定位）

- **结构上刻意去资本化**（听众要求），上期第一章（美第奇账本/收入只够折旧/26Q3 FCF 转负）本期零更新；
- **但补了需求侧新证据**：Ramp 的 Top 1% 花费见顶回落 = 上期"token maxxing 被证伪"的续集；"Fable 5 强得可怕但没给 Anthropic 带来超额利润" = SOTA 保质期急缩；
- **泡沫观察点从二级移到一级**：上期是巨头 CAPEX/债，本期是 new lab（943 亿 vs 16 家有收入）；"Loop 之后里程碑怎么确立" = 上期"黄金时代还是泡沫前夜"的估值锚版本；
- 微观测点延续：Codex 周活 500万→900万→2500万；OpenRouter 从"第三方衡量指标"变成被收购对象。

## 六、关键人物与概念

人物：庄明浩；提及梁文锋、阑夕、唐杰、Sam Altman、Jeff Dean、Ilya、Mira、田元栋、张小龙等。概念：Own Your Intelligence、RSI、Auto Research、Loop/一切皆可 Loop、New Lab、Router、benchmark 失效、SOTA 保质期、制造业化、斩杀线、无限流、Share of Tokens/量钱分离、agent=model+上下文+harness（LangChain）、world-apps-task（Mercor）、a16z 四象限、复杂度内化、personal agent。

## 七、Limitations

- 全部金额/估值/月活为主播转述其 PPT，未经独立核实；仅欧倍青、《When AI builds itself》、AfterQuery 三处经 eacli 联网核实（均吻合）。
- 修正 80+ 处（见 polished 校正清单）；45 处 [?] 集中在国产办公 agent 产品名（qcloud/treework/codework/autocloud 未能解出，与 07-17 期一致保留原文）、媒体名（赞爱/广密）等。
- 数字口径存疑两处：Ramp "Top 1%" 的百分号为推断；"22 年很多公司回到 GPT-4"与 Llama 2 时间线有出入（疑口误），未改。
- 语速 225 字/min（单口+PPT 翻页），无循环幻觉。

## 八、思考与追问

1. **Own Your Intelligence 的个人版**：企业 OYI 四笔账（成本/速度/好标准/数据把控）映射到个人就是"Own Your Workflow"——你自己的 herdr/eacli 舰队其实已经是个人版 OYI。红杉路径（评估→harness→路由→数据→后训练）里，个人能走到哪一步？评估标准和数据准备是不是个人版的真正瓶颈？
2. **Loop 的内容象限难题**：a16z 四象限里"弱验证×强编辑"的内容板块没被证明可 Loop——你的学习工作流（报告→wiki→open-questions）本质就是内容生产 Loop。给它装"可验证性"的方向是什么：事实核查自动化？读者（你）反馈结构化？还是本来就不该 Loop（曾鸣说的"人负责无中生有"）？
3. **里程碑缺位的一级市场跟踪**：如果 new lab 的估值锚是"拉人+发榜"，那 26Q4-27H1 该盯什么信号来判别泡沫 vs 范式——英伟达投资名单的集中度变化？AfterQuery 类数据公司的收入披露？"new lab 首次公开收入"事件本身？

---

*版权与引用：节目版权归屠龙之术与庄明浩所有；转录与润色稿仅供个人学习；如版权方要求下架请联系。完整节目与 73 页 PPT 请去小宇宙收听/查看。*
