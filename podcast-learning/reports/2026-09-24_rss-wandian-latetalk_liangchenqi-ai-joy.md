---
title: "晚点聊182：梁琛奇——用 AI 创造开心：猫箱推演、动念引线与养女儿方法论"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（晚点 LatePost RSS）
source_url: https://podcast.latepost.com/182
show: "晚点聊 LateTalk"
episode: "182: 对话梁琛奇：抖音、猫箱、创业，「他们都搞生产力，我想用 AI 创造开心」（2026-09-24）"
host: "程曼祺（晚点 LatePost）"
guest: "梁琛奇（动念引线创始人；前字节 7 年：抖音/实时社交产品负责人/猫箱）"
duration: "3h22m"
duration_seconds: 12120
transcript_segments: 8446
chapters: 5+（shownotes 时间轴覆盖前 36 分钟，后续为自由漫谈）
polished: true
polished_by: "Claude (pi)（结构化精编，约 raw 的 7%，头部已标注；后半漫谈按主题抽取）"
polished_at: 2026-10-10
status: archived
created: 2026-10-10
updated_on: 2026-10-10
transcript_path: reports/transcripts/2026-09-24_rss-wandian-latetalk_liangchenqi-ai-joy.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-24_rss-wandian-latetalk_liangchenqi-ai-joy.polished.txt
pipeline: latepost feed enclosure mp3 → 本地 whisper.cpp / large-v3 / Metal / VAD+`-mc 0`（Razer 白名单不批 latepost 域）→ RSS description shownotes → 精编（SKILL v2）
source_shownotes_chapters: true
notable_correction: "梁琛琪→梁琛奇｜曼琪→程曼祺｜猫香/猫腔→猫箱｜Carrot AI/卡尔特亚→Character.AI｜Durea→BeReal｜设证网→摄政王｜四杰→字节｜邪律→斜率｜RI打招→ROI 打正｜type→tab｜DL→DAU｜APU→ARPU｜待机→代际｜弹载派对→蛋仔派对｜Cdance→Seedance｜巨神→具身｜客战价→客单价｜淋漪与后门→冯诺依曼；卷卷[?]/NFA[?]/比斯比克[?]/Wish[?] 保留"
hanzi_chars_raw: 67930
total_chars_raw: 276210
hanzi_chars_polished: 3778
total_chars_polished: 6234
---

# 晚点聊 182：梁琛奇——用 AI 创造开心

## ⚡ 速览

- 娱乐比工具慢的三要素：token 成本（DeepSeek 后 ROI 打正）×模态（视频过了 bar）×用户已被工具教育。
- 动念引线：AI 是引线不是烟花——**点燃脑中三千个念头，激励"脑中有巨大天赋的人"**。
- AI 产品方法论：从"造房子"到"**养女儿**"——教框架+原则+SFT+RL，等一个 wow 的 moment。

## 概览

- **人物线**：96 年，字节 7 年没碰过娱乐以外的事——2017 校招强烈要求去抖音（人群/表达动机/快手已存在三判断）→做第二个 tab 朋友页（留存打正的关键竟是"朋友看完了回主页"一个小跳转）→2021 从零 lead 实时社交产品（上百人一年关掉：**不逆势+娱乐只赌一个假设**）→2023 Flow 做出猫箱→2025 夏创立动念引线（Default）。
- **娱乐三要素**：token=新时代流量（娱乐时长是工具 10-20 倍，DeepSeek 让猫箱去年底 ROI 打正）；模态=GPT-4o/Sora/Seedance/Nano Banana 真过了"愿意看"+"遵循指令"两道 bar；用户习惯=工具类 AI 产品已完成用户教育。
- **猫箱推演**：AI native=互动内容（input→reasoning→定制化反馈 × 内容主动/被动轴）；AI 导演模型（人类编剧写剧本+用户选择+AI 推进剧情）；火山口解荷尔蒙问题（一群人有主线剧情的沉浸式话剧）；第一天就 diverse 品类+只做 18-30 岁女性。
- **核心框架**：供给端碎片化继续（普通人文字表达→AI build）；消费端超拟合的无限分支（计算机从有限级变无限级——长尾自由感产生真实感）+推荐系统的下一级（面向三千万人创作→专门为你 design；但 strange 部分必须留给人）。
- **人难被替代五事**：数据少/不好评估/起心动念/具身未成/**情感加成**（妈妈的蛋糕）。
- **字节门槛**：DAU×ARPU——普通产品要千万 DAU、AI 产品约五百万——"很多方向字节在涨起来之前不会做"。

## 增量观点（polished 之外的连接与分析）

1. **"familiar×strange"二元结构是本周注意力线的美学版**：[[2026-09-27_xiaoyuzhou-crossing_yuhong-sel|于红]]的 SEL（接纳=熟悉桥梁，惊喜=strange）、[[2026-10-08_xiaoyuzhou-crossing_kk-shanyin|KK]] 的"隔着雾的文化策略"（似与不似）、本集的"完全由 AI 接管的内容世界不会发生"——**三个独立领域都收敛于：纯粹的贴合（familiar）不构成体验，张力（strange）来自人的多样性**。这是对 E255"模型 61%"的人文侧补充：AI 能逼近最大公约数，但 max 之后剩下的部分定义了艺术。
2. **"养女儿方法论"与 harness 公式是同一认知的两种表达**：[[2026-09-22_xiaoyuzhou-tulong-zhishu_ai-production-stage|IDC]] 的 Agent=Model+Harness（工程侧）、[[2026-09-23_xiaoyuzhou-weishijie_ruanliang-ai-org|阮良]]的"换木桶"（组织侧）、本集的"无法遍历无限 input→只教世界观+principle+SFT+RL"（产品侧）——**三者都在说：当系统无限化，控制方式从"定义每个分支"变为"定义价值观和边界"**。这与 EverAgent 的 AGENTS.md 哲学（协议而非状态机）完全同构。
3. **"起心动念不可替代"补全了工作观线**：梁琛奇列的 AI 不可替代清单第 3 条（AI 永远在 response，起点是你要干嘛）正是 [[2026-10-09_rss-kedaibiao-lizheng_career-methods-series|孙煜征九讲]]"90% 无意义→找到那 10%"的形而上版本；与 [[2026-09-27_xiaoyuzhou-crossing_yuhong-sel|于红]]"发现天赋=做什么开心"构成三角：**意图（你要什么）×信号（什么让你开心）×执行（AI 全包）——人的残留价值收缩到意图层**。
4. **"娱乐是非效率的"给模型厂商边界论提供了最干净的定义**：与 Today 277 的"Personal AI 对立面是高委托成本"、大小马的"娱乐=单点极致"拼成边界三部曲——**是否 serious 解决问题决定 UI 简单 vs 体验复杂**；这解释了为什么 OpenAI 向生活渗透可以但吃不掉娱乐（enjoy time 的产品价值在新交互新容器本身）。
5. **实时社交产品的失败 learning 是创业方法论的最强浓缩**："娱乐新体验里关键变量最好只有一个，十个 90% 假设相乘约等于零"——与孙煜征"失败是期权"、大卫翁"五步决策"同属"降低赌注数量"的智慧；而"从 3 万个里找 100 个快速测试"是它的对偶（单赌概率低就广测）。

## 关键人物

- **梁琛奇**：动念引线（Default）创始人；字节 7 年（抖音产品经理→实时社交业务负责人→Flow 猫箱团队）。
- **朱骏（Alex）**：抖音产品负责人（Window 比喻、"细节变态"、转 Character.AI 链接给梁）。
- **程曼祺**：晚点科技报道负责人，主播。
- **药水哥**：被点名的"天才随机分布"例证。

## 引用书目

无书籍；关键作品参照：Musical.ly/抖音、Roblox、蛋仔派对、BeReal、多闪、Character.AI/星野/Glow/Talkie、猫箱、群图（梁的大学小程序）。

## 关键概念词

娱乐三要素（token/模态/用户教育）｜enjoy time vs save time｜表达动机的第一性（火力值之弊）｜代际社交平台｜不要做太多假设（10×90%≈0）｜动念引线/Default｜脑中世界的天赋｜AI native=互动内容｜AI 导演模型｜火山口解荷尔蒙｜familiar×strange｜超拟合的无限分支｜推荐系统的下一级｜人难被替代五事（起心动念/情感加成）｜造房子→养女儿｜想象力曲线｜3 万个里找 100 个｜字节门槛（DAU×ARPU）

## 关键观点（原话）

> "他们都在搞生产力，我想用 AI 创造开心——让更多的人有创造力，在一种新体验里获得新的快乐。"

> "你可以用物质激励平台的建设者，但它不能成为第一性动机——它会影响后边所有的生态。"（火山 vs 抖音）

> "在娱乐里，在新体验里，不要做太多假设——十个 90% 的假设相乘，非常小。"（实时社交产品的 learning）

> "最终的创造力不来自 AI，也不来自我们公司——它来源于普通的用户自己。我们只是燃放那个烟花的引线。"

> "内容要同时提供 familiar（桥梁）和 strange（惊喜）——完全由 AI 接管的内容供给世界，我觉得不会发生。"

> "AI 之前计算机是有限级的……AI 之后是无限级——恰恰因为你能做任何长尾的事，所以你觉得自己是自由的。"

> "你只能教她框架：世界观、principle、SFT、目标让它自己 RL——她成年礼演话剧打动你时，你必须 wow 一下。没有一个这样的 moment，你就错了。"（养女儿）

## 关键数字

| 数字 | 含义 |
|---|---|
| 7 年 / 96 年 | 梁琛奇在字节时长 / 出生年 |
| 10-20 倍 | 娱乐产品推理成本（相对工具，时长差） |
| 去年底 | 猫箱 ROI 打正的时点（离任时测算） |
| 上百人 / 1 年 | 实时社交产品关停时的规模 |
| 2000 万→2000 万种 | 计算机输入从有限级到无限级 |
| 3000 万人 | 推荐系统创作者面向的最大公约数 |
| 18-30 岁 | 猫箱第一天锁定的人群 |
| 千万 / 五百万 DAU | 字节普通产品 / AI 产品的立项门槛 |
| 0.5-1 元 | 普通 ARPU 基准（DAU×ARPU 乘数） |
| 一天 3 千个念头 | "动念"的数量级描述 |
| 一两个月 | 抖音朋友页从想法到上线 |

## Limitations

- polished 为精编版（约 raw 7%）——3h22m 超长对谈，后半 2 小时漫谈按主题抽取（字节预算制/context 收集/商业化细节等有遗漏，查原文用 transcript）。
- **专名 [?] 与修正风险高**：面试官"卷卷"、NFA、"比斯比克"（疑"彼时彼刻"梗）等未还原；猫箱/Character.AI/BeReal/蛋仔派对/Seedance 等按行业知识+上下文裁定。
- 时间线为口播自述（对年份"比较模糊"自认）；"最年轻业务负责人"[?]、猫箱 ROI 打正等内部数据无公开来源。
- 主播立场：晚点科技报道负责人，中立访谈；嘉宾为创业者（动念引线未发布产品），愿景部分（Default/平行世界）属个人信念表达。

## 思考与追问

1. **我真正理解了什么？**这期提供了"AI 娱乐第一性原理"的完整推导链：**成本（token）→模态（过了 bar）→教育（工具先行）→无限分支（体验的本质变化）→familiar×strange（人机分工的边界）**。最有穿透力的是"起心动念"与"情感加成"两条人类防线——它们恰好无法被数据化（数据少/不好评估），形成自我实现的护城河。"养女儿"比喻是 2026 年听到的最好的 AI 产品方法论表述。
2. **我还没搞懂什么？①动念引线的具体产品形态（口播未发布，只有愿景）；②"想象力曲线"的具体解法（产品如何为低想象力用户设计）；③猫箱两种 use case（内容 vs bonding）的占比与商业化差异；④字节"预算清零"机制的具体运作。
3. **下一步读什么/做什么？①把"familiar×strange"框架用于 EverAgent 报告写作自查（纯贴合用户已知=无张力；纯 novelty=无桥梁——增量观点节的设计准则）；②追踪动念引线首个产品发布（接 Today 277/275 的个人 Agent 与 AI 娱乐双线）；③"养女儿方法论"与自家 SKILL.md 的维护方式对照（教框架不教分支=写协议不写状态机）；④《晚点》对梁琛奇的原始报道文字版（shownotes 附链接）可补对谈外的细节。
