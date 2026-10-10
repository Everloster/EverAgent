---
title: "乱翻书275：个人Agent的战争——拆解Town、Instinct、Grok Bot与Muse（含产品深研档案）"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6ab029b7ac389df82734ebb6
show: "乱翻书"
episode: "Vol.275"
host: "潘乱"
guest: "莫唯书Mark（前TikTok产品，公众号：莫思Moss）· Suki（Today founding PM）· 郦橙锦妖Vanessa（前字节AI PM）"
duration: "2h06m"
duration_seconds: 7559
transcript_segments: 4039
hanzi_chars_raw: 34034
hanzi_chars_polished: 34034
total_chars_raw: 204189
total_chars_polished: 108135
audio_size_mb: 1387
speech_rate_cjk: "270 字/min"
chapters: 7
polished: true
polished_by: "GLM-4.6 (pi coding agent)"
polished_at: 2026-10-09
status: archived
created: 2026-10-09
updated_on: 2026-10-09
transcript_path: reports/transcripts/2026-09-21_xiaoyuzhou-luanfanshu_personal-agent-wars.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-21_xiaoyuzhou-luanfanshu_personal-agent-wars.polished.txt
pipeline: eacli podcast → Razer yt-dlp + whisper.cpp v1.9.1/ggml-large-v3/CUDA sm_120/Silero VAD/-mc 0 → 按shownotes章节重组 → eacli web.read 拉shownotes校验 → 产品深研（eacli web.search 12+轮）
source_shownotes_chapters: true
notable_correction: "彭乱→潘乱、罗马叔→乱翻书、Percent Agent→Personal Agent、Bungemark→Benchmark、POG→Poke、OpenCloud→OpenClaw、Growbot/Grogbot/Gawkbot/Guard bot→Grok Bot、Mills/MIS/Muse→Muse、Malice/Manas→Manus、Mindless→Midjourney、Tone/Tang→Town、小微→微信小微、米油→Muse（依shownotes+web核实）"
---

# 乱翻书275：个人Agent的战争已经开始

> **一句话**：三位产品经理（含 Today 创始 PM Suki）拆解 Town / Instinct / Grok Bot / Muse 四种 Personal Agent 路线赌注——这一品类争夺的不是工具使用时长，而是**用户意图产生后的第一入口**；胜负手不在模型，在 **Context 处理、执行能力与用户信任**。本报告 = 转写精读 + 七款相关产品的 web 核实深研档案。

---

## 1. 概览（核心 5 条）

1. **时间线（Suki 内部视角）**：OpenClaw 1 月爆火是这波的启发源（heartbeat 心跳 + daily log 机制 → "下一波不一定是一个工具，而是一个人"）；**2 月几乎所有玩家同时立项**（Today 春节建团队、Muse 2-3 月立项、Instinct/Town 同期搭团队）；6 月 Town 在 VC 圈引发热点；8 月 Grok Bot 发布；8 月下旬 Instinct 推特爆论；9-8 Muse 点燃大盘（小扎 6500 字长文 all-in）[转写]
2. **四产品四赌注**：Town=高频场景（邮箱）建立信任换取委托权；Instinct=把委托成本压到一条消息（住 IM，主打支付）；Grok Bot=给用户一支 Bot 队伍（多 Bot+云虚拟机）；Muse=免费+分发+每用户一台虚拟机，烧钱培养市场烧走对手 [转写]
3. **分水岭不是聊天体验而是"把事办完"**：Instinct 接入信用卡、屏幕、麦克风，第一次真正替用户把事办完→病毒式传播；Poke 只做"推送准"没做执行，被收购收场。小龙虾（OpenClaw）一代成先烈的三因：追热点太糙、云上 agent 极难（三套环境的状态保持）、门槛太高 [转写]
4. **意图经济浮出**：从争夺注意力到赢得理解——收藏是"没有兑现的意图"（小扎的 Muse 叙事）；但 Today 实际数据显示真实需求排序是**行政杂事 > 旅行出行 > 省钱理财 > 购物消费**（前四类 >70%），购物排最后——Suki 怀疑小扎的购物故事是给免费模式找商业叙事 [转写]
5. **终局判断**：最值钱的位置是**信任和习惯**（context 只是入门）；Vanessa 的结构性判断——这波**没有网络效应/规模效应叙事**（无双边锁定，谁好用第二天就切换），创业公司比上一波移动互联网更好打 [转写]

## 2. 章节地图

| 章 | 时间 | 核心命题 |
|---|---|---|
| 一、硅谷为什么突然开始争夺 | 07:42 | $10B 估值与 <10 万用户的倒挂；Personal Agent 与工具的分界（长程理解+主动性）；办公 Agent 按任务组织 Context vs Personal Agent 按人组织 |
| 二、四款产品四种赌注 | 30:14 | Town/Instinct/Grok Bot/Muse 路线拆解；补贴战争；Poke vs Instinct；小龙虾先烈分析；24h 在线 agent 之难；大厂三入口困境 |
| 三、最先跑通的都是生活麻烦事 | 49:16 | 退订改签预约账单先跑通；两种生意（雇助理 vs 商家付费中介）；科技平权；Town 家校破圈、Today 育儿重度用户；豆包缺什么 |
| 四、意图经济浮出水面 | 61:31 | 注意力→理解；收藏=未兑现意图；男性/女性购物思维；手机厂商/模型公司/超级APP各自持什么缺什么；AI 手机=AI 浏览器重演 |
| 五、App、IM 和 Bot 队伍终局 | 79:44 | Today 走过的弯路（channel→GUI 地图论）；Instinct vs Grok Bot onboarding；住别人 IM 的命运不由自己；一个总管还是多 Bot |
| 六、美国大三创业者闯进直播间 | 91:35 | 校园版超级课程表；Instinct 融资能力之谜；破圈信号=讨论者从 Twitter 极客转向 Facebook 宝妈 |
| 七、中国玩家入场 | 112:45 | 微信小微+豆包最被期待；豆包与抖音数据打通暴论；快问快答（隐私让渡/三年普及/12个月验证信号/最值钱位置） |

## 3. 关键人物

- **Suki**（Today/today.ai founding PM，本报告最重要的内部视角来源：云上 agent 工程细节、Today 弯路、海外真实用户数据）[shownotes]
- **莫唯书 Mark**（前 TikTok 产品，公众号"莫思Moss"）[shownotes]
- **郦橙锦妖 Vanessa**（前字节 AI PM，曾在 Monica 插件工作）[shownotes]
- **潘乱**（主播，「乱翻书」主理人，《腾讯没有梦想》作者）[shownotes]
- 转写中提及：小扎（Muse 6500 字长文）、蚂蚁 CEO（意图论）、Instinct 23 岁素人创始人、赵凯（美国大三连麦创业者）、小红（Monica 时期，董秘例子）

## 4. 主要话题（按主题归并）

### 4.1 品类定义：为什么是新一波
- 三波前史：Siri/Alexa/小爱小杜（语音助理）→ ChatGPT/元宝（chatbot）→ AI 办公（任务 agent）→ **Personal Agent**：以**人**为中心组织 Context（非任务/项目维度），长程理解 + 主观能动性（不是依赖 prompt 的自动化，是理解目标后主动提方案的"同事"）[转写]
- Personal AI 聚焦 Context/Memory 层，办公 Agent 在意任务完成率与 Harness 层——两者是 Claude Code 与 OpenClaw 式的路线分化 [转写]

### 4.2 四产品赌注详解（+web 核实档案见 §11）
- **Town**：70% 流量在桌面端；只做深邮箱一个高频场景（自动归档、学习写作风格、草拟→确认→自动发送）；前身做企业报税 [转写]
- **Instinct**：无独立 App，住短信/WhatsApp；委托成本=一条消息；重点打支付；全权代理（接信用卡/屏幕/麦克风）[转写]
- **Grok Bot**：多 Bot 队伍（研究/邮件/购物各有专属 Bot，可拉群协作），注册自动配"幕僚长"；城市用户聚会多（北京/深圳/广州/上海，极客为主）[转写]
- **Muse**：什么都做、野心最大；免费+Meta 渠道分发+每用户一台虚拟机（token 消耗巨大）；收购安全公司强调隐私；免费算力补贴类比趣头条金币战争与"直接发一倍的钱" [转写]

### 4.3 为什么小龙虾（OpenClaw）一代成了先烈
1. 追热点太糙：上海展会十个展位八九个做小龙虾方向，同质化+打磨严重不足，4 月热度退潮团队放弃（莫唯书）[转写]
2. 云上 agent 极难：本地与云完全两套复杂度；云上要处理三套环境（用户设备/云端服务/agent 执行环境）的任务状态、中断恢复、上下文传递——Today 花了两个月才让 agent 稳定跑云上；有诚意的作品起码 3-4 个月（Suki）[转写]
3. 门槛太高：安装/配置/调试是极客玩具；且大规模推广必须不出错——隐私泄露/删数据是灾难性后果（Vanessa；例：美团产品误删用户相册、豆包 PC 端 A 可见 B 桌面的隐私事故、Muse 年中就做好但为安全内测数月）[转写]

### 4.4 意图经济与商业模式
- 两种生意：①用户付费雇私人助理（订阅，筛高付费意愿忙人，Town 型）②商家付费的消费中介/经纪人（撮合抽佣，Muse 型）[转写]
- 大摩测算：Muse 或有 1 亿用户 × 订阅两档（$20/$100），更大机会在交易抽佣 [转写]
- 高质量 Context 不在收藏夹：来自线下、IM、邮箱的直接协同交互；抖音/Instagram 收藏对 agent 可能是噪音（Suki 反方）[转写]

### 4.5 终局形态之争
- **GUI = 地图论**（Suki）：GUI 不再承载操作，而是"探索 agent 能力的地图"——agent 是藏宝迷宫，普通人需要地图
- Today 弯路实证：先接微信/Telegram（channel 优先）→ 功能可发现性问题（空白对话框不知干嘛）→ 独立 App + channel 并行引导别扭 → 最终 App 内做 chat；Suki 重度使用后效率类 App（邮箱/Slack/日历）全交 Today 管理——agent 成为"几个 App 的更前台一层" [转写]
- Grok Bot 的角色化 onboarding：用"设角色分工"教育用户能力边界，比 GUI 铺满（豆包式）优雅、比纯文字（Instinct 式）高效；还能弱化 GUI（定时任务直接说不用点入口）[转写]
- 住别人 IM 的隐忧：接口不在手里=命运不在手里；IM 信息浏览效率低、多模态支持差 [转写]

### 4.6 中国玩家
- 最期待：微信小微 + 豆包（最大化积累 context 的两个场景：IM + 内容消费）；前提是生态打通 + 一号位敢下注 [转写]
- 豆包讨巧（国民度+AI native 转型不突兀）；微信敏感信息太多——小微内测时"很多人想的是怎么关闭它" [转写]
- Vanessa 记忆 bad case：申请日本签证的记忆被强行关联到无关新话题——"有长期记忆但不体贴人"；Mark 暴论：豆包真正缺的是与抖音用户数据的彻底打通（24 年讨论过又搁置）[转写]

## 5. 引用书目
（本期为圆桌讨论，无书单）

## 6. 关键概念词
Personal Agent / 意图经济（意图放大器）/ 未兑现的意图 / 委托权 / Context（长程理解）/ Memory / 主动性=主观能动性 / 功能可发现性 / GUI 地图论 / 全权代理 / 补贴战争 / 抽佣 vs 订阅 vs 广告 / 网络效应缺席 / 云上 agent 三套环境 / Stripe Link / heartbeat + daily log

## 7. 关键观点（原话引用）

> "Town 是用高频场景去建立用户的信任，一点一点地去获取用户最终的委托权；Instinct 赌的是极致降低启动成本就一定能获客；Grok Bot 赌的是给你一个团队就有更强的执行能力；Muse 赌的是烧钱培养用户心智。"（莫唯书，概括）[转写]

> "GUI 在今天不再像过去一样是承载用户操作的入口，它像是一张地图——agent 是藏了很多宝藏的迷宫，GUI 是给普通人的一张迷宫地图。"（Suki）[转写]

> "真正的主动性是主观能动性……他能理解你做这件事的目标，主动过来说'我觉得你想做这个事情，我有个方案，我们要不要讨论一下'——这种才是我们愿意合作的同事，Personal AI 要做到这种程度才配称为一个人，而不是 another 工具。"（Suki）[转写]

> "收藏不只是内容沉淀，它变成一个没有兑现的意图。"（小扎 Muse 发布叙事，转述）[转写]

> "用户更多的是想解决那些烦人的、他自己不想做的事情，而不是说今天帮你买东西。"（Suki，对 Muse 购物叙事的反方）[转写]

> "这波有可能就不是规模打造网络效应的叙事……只要你的产品好用，用户第二天就立马转向另一个产品。"（Vanessa）[转写]

> "最值钱的位置是信任和习惯——context 这些只是入门的基础。"（快问快答，Suki/Mark）[转写]

> "从人民中来，到人民中去，最终还是要为人民服务。"（潘乱谈普及）[转写]

## 8. 关键数字

| 数字 | 含义 | 来源 |
|---|---|---|
| $50M → $500M(8月) → $2.5B(8月底) → $10B(本月传闻) | Instinct 估值轨迹，半年 200 倍 | [转写]；C 轮 $1B@10B 已于 09-28 官宣 [Web TechCrunch] |
| <10 万用户 | Instinct 到本期录制时的用户量（2 月开始邀请测试）| [转写] |
| 23 岁 | Instinct 创始人年龄，无公开商业履历的素人 | [转写]；Fortune 09-30 确认 Noah Shinn [Web] |
| 70% | Town 流量在桌面端的比例 | [转写] |
| >70% | Today 前四类场景（行政杂事/旅行/省钱理财/购物）占比 | [转写]（用户数据爬取） |
| 2 个月 | Today 让 agent 稳定跑在云上花的纯工程时间 | [转写] |
| 6,500 字 | 小扎解释 Muse 的长文 | [转写] |
| $20/$100 | Muse 订阅两档（美国订阅中位数锚定 $20） | [转写]；CNBC 确认 [Web] |
| 一台/用户 | Muse 免费配的虚拟机 | [转写] |
| 34034 汉字 / 4039 段 / 2h06m | 本期转写规模（音频 1387MB） | [转写统计] |

## 9. Limitations

- whisper 误识别已按 shownotes+web 核实修正（清单见 frontmatter），但专有名词长尾可能有残留：如"小微熔"（疑为微信小微内测相关）、"辛海"[?]（上下文指手机厂商高管，或为"陈嘿"[?]待核）
- 转写无说话人区分（diarization 缺失），部分观点归属按上下文推断，可能有个别张冠李戴；圆桌三人观点密集交错处已尽量以"（X）"标注
- 数字"半年估值翻 200 倍"为口播原话（$50M→$10B=200x），与"翻了几番"口径不同，保留原貌
- 节目观点均为嘉宾个人观察（明确说"没跟核心团队聊过，只从用户/行业/产品视角分析"），非官方事实；web 核实部分已用 [Web] 区分

## 10. 思考与追问

1. **我真正理解了什么？**
   Personal Agent 品类的本质不是"更聪明的 chatbot"，而是**Context 组织维度的切换**（任务→人）+**交付闭环**（把事办完）+**委托权积累**（信任）。四产品赌注其实是四条通往委托权的路径：场景纵深（Town）、启动成本（Instinct）、组织形态（Grok Bot）、资本分发（Muse）。Poke/小龙虾的失败反证了单点（住 IM、开源热情）不构成壁垒——壁垒是"云上三套环境的状态一致性"这种脏活。
2. **我还没搞懂什么？**
   - **为什么给每个用户配一台固定虚拟机**？节目里 OpenAI 同学的"技术有限"解释被质疑——Meta 的真实考量是隔离安全、成本控制还是算力囤积？[待验证]
   - **信任如何量化迁移**：如果 Vanessa 对的（无网络效应、切换零成本），那"信任和习惯"凭什么立得住？习惯的养成周期 vs 巨头补贴的耐心，哪个先耗尽？
   - **豆包×抖音数据打通**的监管边界在哪（Mark 暴论的反面）——国内个人信息保护法框架下这条路是否根本走不通？
3. **下一步做什么？**
   - 实测 Today 中国版（today.ai，9-24 已上线）与 Muse/Instinct 的 onboarding 差异，验证"GUI 地图论"
   - 追踪 12 个月验证信号（节目给出：普通人使用从对话走向执行）——挂到 open-questions 定期回访
   - Grok Bot 多 Bot vs 单总管的 token 成本实测（嘉宾称多 Bot 协同"浪费时间和 Token"，无实测数据支撑）

---

## 11. 产品深研档案（用户要求延展 · web 核实）

> 以下为报告写作期间经 eacli web.search/read 核实的产品事实（2026-10-09），与节目观点互补；均标注来源。节目未覆盖的 OpenAI Dots / Manus / OpenClaw / Poke 也一并收录。

### 11.1 四主拆产品

| 产品 | 关键事实 | 来源 |
|---|---|---|
| **Town** | 旧金山公司；2026-06 Series A $35.6M（a16z 领投，Dealroom）；09-15 扩至 $55M（a16z+Forerunner，FundraiseInsider）；08-29 Inc 报道正洽谈 ~$10 亿估值融资；定位"深度个性化 AI 助理"，邮箱场景深耕 | [Web] |
| **Instinct** | Spear Street Technology 出品（invite-only）；短信/电话触达的 No-App 形态；操作专用云桌面+连接本地设备（Vellum/spinnable）；连接邮件/消息/屏幕/音频/位置；09-28 C 轮 $1B @ **$10B 估值**（Sequoia/Benchmark/Coatue，TechCrunch）；创始人 Noah Shinn 23 岁（Fortune 09-30）；10 月新推群聊共享 agent（TechCrunch） | [Web] |
| **Grok Bot** | xAI（Google Play 开发者显示 SpaceXAI）2026-08-12 发布；官方定位"team of always-on AI teammates"——每个 Bot 有自己的云计算机、名字、职务、随时间复利的 context；multi-agent 协作/skills/approvals（x.ai 官网/Docs；composio 教程）；用户自建 Sales/Ops/Chief-of-Staff 名册（Cursor 论坛） | [Web] |
| **Meta Muse** | 2026-09-08 发布（about.fb.com）；"世界首个为所有人构建的个人 AI agent"；连接 email/日历/支付/健康等类别，发邮件/订旅行/填表/购买（timesofai/kdnuggets）；免费 + $20/$100 订阅（CNBC）；发布 2 天美国 iOS No.2（TechCrunch 09-10）、后登顶双榜免费 No.1；"human concierge"人工礼宾测试（Reuters 09-23）；09-29 扩展小企业版（elites.zone）；模型为 Muse Spark（Meta Superintelligence Labs，2026-04-08 首发） | [Web] |

### 11.2 延展产品

| 产品 | 关键事实 | 与本期的关系 | 来源 |
|---|---|---|---|
| **Today (today.ai)** | 2026-09-15 海外发布：记忆、主动跟进、云计算机（arxiv 引述）；**中国版 2026-09-24 首发上线**（shownotes 预告）；Suki 为 founding PM | 嘉宾自家产品；海外重度用户=三个孩子的家庭主妇（育儿+采购+缴费进同一长期 Context） | [Web][shownotes] |
| **OpenClaw（"小龙虾"）** | 开源个人 agent（前身 Clawdbot→Moltbot）；跑在自己电脑、住在 Discord/iMessage/Slack/Teams；**2026-01 底一周破 10 万 GitHub stars**；NYT 03-17 报道中国热捧；Wikipedia 有词条 | 节目"先烈"分析对象：heartbeat+daily log 启发了这波；追热点团队 4 月退潮 | [Web] |
| **Poke** | 住在 iMessage/WhatsApp/Telegram/SMS/RCS 的主动助手；2026-06-04 成为 Apple 批准的**第一个 Messages for Business AI agent**（TechCrunch）；Free/$19 Pro/$199 Ultra；"会先发短信给你的助手" | 节目对照组：住 IM 但没做"把事办完"，已被收购 | [Web] |
| **OpenAI Dots** | 2026-09-29 发布（NYT）；always-on agent suite 跑在 GPT-6 Astra 上，接入 4000+ 应用（adcurrent）；DevDay 亮相、后台云计算机执行（infomance）；前身 ChatGPT agent（2025-07-17）已并入 ChatGPT Work（OpenAI help center） | 品类第三极：WSJ 将 Muse/Dots/Instinct 并列为"争夺你 to-do list"的三家 | [Web] |
| **Manus** | 中国蝴蝶效应团队，manus.im；云端异步通用 agent（规划+执行+验证多代理），2025-03 爆红 | 节目提及；被动自动化依赖 prompt，被 Suki 归为"工具"而非"人" | [Web] |
| **千问 App / 豆包 / 元宝** | 千问 2026-01 可直接调用淘宝/支付宝完成下单（"APP 级最高通行证"，smzdm）；节目称豆包/元宝 personal agent 化将在近期宣布 | 中国玩家章核心；豆包×抖音打通是关键变量 | [Web][转写] |
| **Stripe Link** | 支付基础设施，被 Instinct/Muse 接入做比价/支付 | 节目提及最先跑通场景（省钱理财）的技术底座 | [转写] |

### 11.3 品类格局速写

时间线（核实版）：OpenClaw 开源爆火（1月）→ 玩家集体立项（2-3月）→ Poke 获苹果通道（6-4）→ Grok Bot（8-12）→ Today 海外（9-15）→ **Muse（9-8）→ Instinct $10B C 轮（9-28）→ OpenAI Dots（9-29）** → WSJ 定调"个人 bot 之战"（10月初）。资本市场：2026 年第二波个人 agent 创业公司融资 $1.8B（Dealroom）；Instinct 半年估值 200 倍是极端样本。四条路线（场景纵深/启动成本/组织形态/资本分发）+ 第三极（Dots 的模型厂商下场）+ 中国变量（微信小微/豆包/千问/Today 中国版），品类在 6 个月内从开源玩具变成巨头战场。

---
*报告生成时间: 2026-10-09*
*研究方法: eacli podcast Razer 静默转写 → shownotes 校验修正 → 全文精读提取 → 12+ 轮 web 核实产品事实 → episode_summary + 产品深研档案*
