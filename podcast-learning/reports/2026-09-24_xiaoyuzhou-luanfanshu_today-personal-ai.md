---
title: "乱翻书277：Today 中国首发——Memory×Proactive、单 session 终局与产品经理的价值回归"
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/6ab4b804e742e36efcbab131
show: "乱翻书"
episode: "277.从提醒你，到替你办：Today想把Personal AI带到哪一步？（2026-09-24）"
host: "潘乱"
guest: "高策（Today 技术负责人，前向量数据库创业者）、Suki（Today founding PM，前 Monica/Manus 团队）"
duration: "1h39m"
duration_seconds: 5940
transcript_segments: 3554
chapters: 4（shownotes 板块）
polished: true
polished_by: "Claude (pi)（结构化精编，约 raw 的 11%，头部已标注）"
polished_at: 2026-10-10
status: archived
created: 2026-10-10
updated_on: 2026-10-10
transcript_path: reports/transcripts/2026-09-24_xiaoyuzhou-luanfanshu_today-personal-ai.transcript.txt
polished_transcript_path: reports/transcripts/2026-09-24_xiaoyuzhou-luanfanshu_today-personal-ai.polished.txt
pipeline: eacli podcast（Razer whisper large-v3/CUDA/VAD）→ pull 成功（176KB）→ web.read（智谱）shownotes → 精编（SKILL v2）
source_shownotes_chapters: true
notable_correction: "特点/TEDay→Today（产品名被写成'特点'数十次）｜Mindless→Manus｜鲜艳→先验｜奔驰→bench｜悦耳→育儿｜销量/限量→向量数据库｜奇威→企微｜朱小虎→朱啸虎｜加克伯克→扎克伯格｜OPPO 4.8→Opus 4.8[?]｜Solta/骚→SOTA｜SP→system prompt｜Canada→Calendar｜tudu→to-do｜烫→Town；OpenCloud[?]/Athorpec[?]/Rapt[?]/River.ai[?]/OPOS[?]/齐俊元[?]/深圳海味[?] 保留"
hanzi_chars_raw: 28408
total_chars_raw: 118881
hanzi_chars_polished: 3638
total_chars_polished: 7409
---

# 乱翻书 277：Today 中国首发

## ⚡ 速览

- 国产第一个正式上线的 Personal Agent：**Memory×Proactive** 双引擎，"没有记忆的主动是骚扰，没有主动的记忆是档案"。
- 判断：模型已 AGI 只剩成本问题（Scaling Law 年降 10 倍）→**模型不再是瓶颈，产品经理的价值回归**。
- 终局想象：单 session 无限增长；执行闭环做到"连 approve 都不需要"；"为降低注意力干扰而存在的 AI"。

## 概览

- **时机**：Instinct 半年 5000 万→100 亿估值、Muse 登顶——共识窗口极快（coding→work→personal 复制速度一致）；各家定位都是"better OpenCloud"（长程能力已验证但 self-host 难、体验差）。都没 PMF（用户全是 early adopter）→提前发布换场景。
- **需求**：从通用往 niche 泛化（与上代 Glean/Otter.ai 反向）；email/日程在 founders/育儿人群泛化（育儿留存最好）；**数字资产前提**——赛博足迹少的人 onboarding 成本极高，先从数字资产多的人开始。
- **定位**：Personal AI 的对立面不是工作，是**高委托成本**；从生活泛化到工作比反向容易；"委托成本低于琐事总成本"之后很多事才可能交给 AI。
- **竞争**：大厂擅长高举高打、不擅长看见和坚持（千问/豆包探索过又放弃）；TAM 现在太小（AI 办公三大件 <100 亿/年）；Muse 靠钱（24h 云电脑 sandbox）；创业公司学 Town（订阅制+email killer feature；"短期被高估、长期被低估"）。
- **单 vs 多 agent**：高策实验养三个总管最后只跟一个聊；多 agent=另一种手动管理 context+协同烧 token（情绪价值为主）；multi-agent 可作架构，产品必须暴露单 agent（情感连接不可复制）。
- **Memory 设计**：Timeline/consolidation/delta 三路（chat+connector+录音）；关系用图、时序用 timeline；"发件箱信息密度>收件箱"这类 rubrics=先验壁垒。
- **Proactive 四维**：理解用户/学习反馈/频次/时效性——"agent-driven 推荐系统但停留时长一定不是优化目标"。
- **执行闭环**：提醒→准备→确认→执行，终极是 auto 模式（学历史同意权限）；"帮我抢票才是关心的，summary 跟听写员上网一样"。

## 增量观点（polished 之外的连接与分析）

1. **与 [[2026-09-21_xiaoyuzhou-luanfanshu_personal-agent-wars|275 期]]构成完整拼图**：275 拆格局（Town/Instinct/Grok Bot/Muse 四强），277 给出中国参赛者的第一手产品哲学——**两期合起来是个人 Agent 战争的"开战纪实"**。高策的"模型同质化→产品价值回归"与 275 的判断一脉相承，但给出了最硬的证据（小米 RL 数据配比 60-70% coding/3.5% chat；交互 bench 最高分不是 SOTA）。
2. **"泛化性怀疑"是本周五份报告的第四方收敛**：[[2026-10-08_rss-guigu101_e255-zhangkuo|张阔]]的 107-task 61%、[[2026-09-23_xiaoyuzhou-weishijie_ruanliang-ai-org|阮良]]的 20→17 天、[[2026-09-22_xiaoyuzhou-tulong-zhishu_ai-production-stage|IDC]]的全链路评测转向、本集的交互 bench——**四个独立信源都说"模型榜分≠交付质量"，且解法一致：harness+先验知识（人类 rubrics）**。于红那句"我有个想法→我有个假设"正是人类先验的微缩版。
3. **"数字资产前提"给知行 E253 的折叠世界补了机制**：83% 没用过 AI 的人不是不想用，是**赛博足迹太少导致 agent 无法低成本了解他们**——数字鸿沟的新形态：从"接入鸿沟"变成"上下文鸿沟"。这与于红"知识获取时间变短→ SEL 更重要"构成同一枚硬币：AI 时代人的差异化资产从知识转向（a）被记录的数字生活（b）不可被泛化的判断力。
4. **单 session 论证直接命中 EverAgent 的设计取向**：高策"上下文 all in one place"+multi-agent 只用于互相监督（eval）——与阮良红蓝军（重大决策才多模型 PK）、eacli 舰队（日常单通道+关键任务多设备）三方一致；**"协同花的也是你的钱"应记入个人 token 纪律**。
5. **"为降低注意力干扰而存在的 AI"接上注意力保护线**：与 KK 的"AI 无限人生有限"、课代表的"认知余裕（90% 工作无意义）"、AK 的"勿扰模式时代"四期同构——**2026 年秋的共识正在形成：个人 AI 的第一性指标不是效率而是注意力净收益**。Slogan 对照：Today"让你有时间散步踢球" vs 工作提效"只会让你接受更多任务"。

## 关键人物

- **高策**：Today 技术负责人；前连续创业者（模型基础设施/向量数据库）；2026 年 2 月因模型 coding 跃升而转向。
- **Suki**：Today founding PM；前 Monica（Manus 前身）团队。
- **潘乱**：乱翻书主播。
- **Peak[?]**：Manus 首席科学家（高策"梦想请过来的人"）。

## 引用书目

无书籍；关联：[[2026-09-21_xiaoyuzhou-luanfanshu_personal-agent-wars|乱翻书 275 个人 Agent 战争]]（前篇）、Manus 25 年 7 月博客（上下文感知状态机）、Instinct Memory 逆向文章、小米开源 RL 过程。

## 关键概念词

Memory×Proactive（双引擎）｜没有记忆的主动=骚扰｜better OpenCloud｜技术成熟度前夜（做产品时机）｜数字资产前提/上下文鸿沟｜高委托成本（Personal AI 的对立面）｜单 session 无限增长｜多 agent=手动管理 context｜协同即 token 成本｜context 利用率（vs GPU 利用率）｜发件箱>收件箱（rubrics 例）｜先验知识=壁垒｜泛化性怀疑｜Proactive 四维度｜执行闭环/auto 模式｜从通用往 niche｜短期高估长期低估（Town）｜Today is your day

## 关键观点（原话）

> "做产品不能站在遥远的未来（会成为先烈），要站在技术成熟度的前夜。"（Suki）

> "模型的智能已经是 AGI 了……唯一需要在乎的是 cost——成本遵循 Scaling Law，每年降 10 倍没有问题。"（高策）

> "Personal AI 的对立面并不是工作，是高委托成本。"（Suki）

> "没有记忆的主动很容易变成骚扰；没有主动的记忆只是档案。"

> "模型的泛化性没有想象中那么强……产品经理的价值是非常大的。"（高策）

> "它连你的 Calendar 都 book 好、邮件都发出去——我绝对不可能让 Codex 帮我约会。"

> "希望被提及时说：这个东西让我有了更多时间去生活、去散步去踢球——而不是工作效率又变高了，可以做更多工作了。"（高策）

## 关键数字

| 数字 | 含义 |
|---|---|
| 5000 万→100 亿 / <10 万用户 | Instinct 半年估值与用户量 |
| 60-70% / 3.5% | 小米 RL 数据配比：coding vs chat |
| 60K token | Grok Bot 在 Slack 的常驻消耗（拉群成本极高） |
| 5 层 | Town 处理一封邮件的 subagent workflow 深度 |
| 1 亿 token + 1 个月 Pro | Today 新用户礼包 |
| 40+30+30 亿 <100 亿 | 钉钉/飞书/企微年营收（大厂为何看不上 agent TAM） |
| 10×/年 | 模型成本下降假设（Scaling Law） |
| 2 月份（2026） | 高策"智能跃升"的时间锚点 |
| 3 个→1 个 | 高策多 agent 实验的存活聊天对象 |

## Limitations

- polished 为精编版（约 raw 11%）。
- **专名 [?] 重灾区**：OpenCloud（两期一致的口播名，疑某开源 agent 项目）、Athorpec、Rapt、River.ai、OPOS（2 月发模型的厂商）、Opus 4.8/GPT-5.3/Kimi K3（版本号口播）、齐俊元、Manus 的 Peak——均未联网核实；产品名"Today"被转写成"特点"数十次已全量修正。
- 嘉宾为 Today 创始团队，产品判断（通用优于垂直/单 session 终局等）带立场；"国内第一个"的 claim 按口播归档。
- 育儿留存好/付费转化等行业数据为内部观察无公开来源。

## 思考与追问

1. **我真正理解了什么？**这期最有长期价值的是"**技术成熟度前夜**"的产品时机论和"先验知识=壁垒"的分工论——前者解释了为什么同一季度所有产品一起 ready（都在等同一个技术拐点），后者把"模型 AGI 后人还剩什么"回答为：rubrics 的设计能力（哪个信号密度高、频率怎么调、时效怎么判）。**产品经理的价值回归不是怀旧，是 token 成本曲线上的必然**。
2. **我还没搞懂什么？①OpenCloud 究竟是什么（阮良/潘乱两期口播一致但均未核实——很可能是理解 2026 agent 格局的关键缺口）；②Today 的 memory 具体架构（Timeline/图/时序的融合方案只给了方向）；③"上下文鸿沟"能否量化（数字资产与 agent 可用性的关系）；④Instinct Memory 逆向文章原文。
3. **下一步读什么/做什么？①核实 OpenCloud（web.search，两期报告的 [?] 即可清掉）；②把"协同即 token 成本/单 session 优先/多 agent 只用于 eval"写进 eacli 舰队的设计备忘；③对照 [[2026-09-24_rss-kedaibiao-lizheng_codex-claude|216 期]]的 Document first：Today 用记忆降低委托成本、孙煜征用文档降低委托成本——同一个问题的个人版与团队版解法，可合并进跨期笔记；④关注 Today 上线后的留存数据（育儿场景是否如 Suki 所说成立）。
