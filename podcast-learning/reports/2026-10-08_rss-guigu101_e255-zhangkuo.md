---
title: "硅谷101 E255：榜单 99 分，用户没感觉——张阔的 107 任务评测与垂直 Agent 成本战"
domain: "podcast-learning"
report_type: episode_summary
source: 播客（硅谷101 fireside RSS）
source_url: https://sv101.fireside.fm/269
show: "硅谷101"
episode: "E255｜模型越来越强，为什么用户没感觉？再访阿里国际站总裁张阔（2026-10-08）"
host: "Yiwen（一文）"
guest: "张阔（阿里国际站总裁）"
duration: "46m13s"
duration_seconds: 2773
transcript_segments: 1669
hanzi_chars_raw: 14550
hanzi_chars_polished: 3571
total_chars_raw: 56984
total_chars_polished: 6527
audio_size_mb: 46
speech_rate_cjk: "315 字/min"
chapters: 8（shownotes 18 时间戳合并）
polished: true
polished_by: "Claude (pi)"
polished_at: 2026-10-09
status: archived
created: 2026-10-09
updated_on: 2026-10-09
transcript_path: reports/transcripts/2026-10-08_rss-guigu101_e255-zhangkuo.transcript.txt
polished_transcript_path: reports/transcripts/2026-10-08_rss-guigu101_e255-zhangkuo.polished.txt
pipeline: fireside feed enclosure mp3 → 本地 whisper.cpp / large-v3 / Metal / VAD+`-mc 0`（Razer worker 白名单不批 aphid.fireside.fm，走 transcribe.py CLI fallback）→ eacli web.read（智谱）shownotes → 8 大节重组润色；数字与 shownotes 交叉核对
source_shownotes_chapters: true
notable_correction: "AsioWork/AXIE Work/Xwork/AXIO/Excel Work/XUwork 等 7+ 种误写→Accio Work（shownotes 确认）｜帕利托→帕累托｜科特巴→哥德巴赫｜Shack Tanks→Shark Tank｜施耐德电器→施耐德电气｜GBT6 Astra→GPT-6 Astra[?]｜Grogbot/Grog Ball→Grok[?]；anti-pride[?]/插程[?]/cash率→cache[?] 等少数存疑"
---

# 硅谷101 E255：榜单 99 分，用户没感觉——107 任务评测与垂直 Agent 成本战

## 概览

- **问题意识**：模型榜单接近满分（99 分级别），但真实经营中没有同幅提升——张阔团队从 alibaba.com 上百万真实经营数据+Accio 问答数据中整理 **107 个任务的开源 benchmark**（七大类，L1-L4 难度分级），统一 harness 评测：**最前沿模型无人干预通过率仅 ~61%**，及格都费劲。
- **coding vs 商务的渗透差**：coding 渗透率估计 99%（绝大多数代码由 AI 产生）；商务 Agent 因任务长程、结果不可即时验证、企业判断标准各异，"整个 agent 刚刚开始"。核心公式：**Agent = Model × Harness × Context（乘法，任何一项为 0 结果为 0）**。
- **Accio Work 三段演进**：AI 搜索（多模态搜索 +130%）→ sourcing 前后延展（Design Pack → Agentic Trade）→ 一站式管理多平台电商后台。案例：找供应商的 Excel 月级流程压缩到 24 小时。
- **成本战**：帕累托最优路由（简单任务→小模型/高性价比国产模型，多模态→特定模型）；107 任务全跑完 **Accio 3.69 美元 vs Codex/Claude Code 9 美元+，约 1/3 成本**。"用得起的 AI 才是有价值的 AI"；绑定自家模型的 agent 没法做路由（对照美国 OpenRouter/Fireworks 生意）。
- **边界**：支付/采购按钮、产品 taste、市场预测、budget 分配永远留给人；"模型 7×24 跑一周不挂 means nothing"；"说 GPT-6 Astra 是 AGI，我现在打保票肯定不是"。

## 章节地图（shownotes 18 时间戳并作 8 节）

| 节 | 覆盖时间戳 | 核心命题 |
|---|---|---|
| 一 AI 同事市场 | 01:18-03:48 | coding 渗透 99% vs 商务 agent 刚开始；为何 coding 容易（数字化+可验证） |
| 二 商家案例 | 06:12-10:13 | Edward 植物监测产品：idea→Design Pack→制造→跨境→多平台售卖；Excel 月级→24h |
| 三 中美生态差异 | 10:13-15:16 | SaaS（美）vs 平台（中）；AI 替代 SaaS 之辨；独立站 vs 平台；agent 第一天即 global |
| 四 Agent 公式 | 15:16-17:46 | Model×Harness×Context 乘法；三者联合优化不能只等模型升级 |
| 五 107 任务 bench | 20:29-28:55 | 榜单 vs 实操的相关性断裂；钓鱼邮件/订船/dispute 任务设计；商业 AGI 定义 |
| 六 成本与路由 | 33:53-38:05 | 3.69 vs 9+ 美元；Auto 模型；GPT-6 Astra"打保票不是 AGI" |
| 七 老板的判断 | 28:55-33:53 | 多平台流水≠利润；发布/客服自动化；taste/budget/节奏留给人；多 agent 冲突 |
| 八 上云与长程 | 40:35-44:43 | 上云是 basic，长程分三种范式；CoCreate 15000 人；15 岁/MIT 冠军案例 |

## 关键人物

- **张阔**：阿里国际站（alibaba.com/1688）总裁；2011-2016 曾在淘系做商家平台/开放平台；Accio Work 负责人。
- **Yiwen（一文）**：硅谷101主持人。
- **Edward**：CoCreate 大会商家案例——植物状态监测消费电子产品创业者。
- **Christian Reed**：去年 CoCreate Pitch 美国冠军（MIT 毕业），测量设备，客户含施耐德电气、SpaceX。
- **15 岁英国冠军**：CoCreate Pitch，自动降温毛巾/宠物降温产品，年销售额约 100 万英镑。

## 主要话题

### 1. 榜单与实操的相关性断裂（本集题眼）

"coding/数学/通用 agentic 得分高，与电商领域能完成更多工作没有很大相关性。"模型发布会说各角度更好、榜单 99 分，但日常使用感受不到——本质水位没拉得那么大。因此需要领域 bench：107 任务开源，希望模型训练时围绕它评测（"这样每次（新模型）出来我们也可以借点大家的光"）。这直接接上硅谷101 E253（数据行业：谁在给大模型出题、卖题、判卷）——**评测数据本身成为垂直 agent 的护城河**。

### 2. 任务设计的三个监测维度

①计算结果正确（quotation 比价：工厂价→含税到手价每一项算清，掺杂钓鱼邮件要识别有害信息）；②执行成功（船公司网站真实 book 船）；③商业判断（dispute 赔/不赔/需更多信息；开环 vs 闭环）。任何环节 fail 即任务未完成——这是"把工作做完"的严格定义，与榜单的"答题"根本不同。

### 3. Agent 公式与垂直壁垒

Model、Harness、Context 是乘法关系：Accio 的 context 优势（20 余年供应链平台积累的沟通/行业/趋势数据）短期无法复制；但 model 与 harness 要联合优化——"不是用一个通用 frontier 模型+简单 prompt 就能产出结果"，要基于一定尺寸模型做后训练+ serving + harness 三方精细打磨（千问小尺寸 post-train 后效果已接近 frontier top）。这也是垂直 agent 能跑出来的原因。

### 4. 成本结构与路由经济学

固定用一个最贵的模型解决所有问题=商家觉得贵的根源。Auto 模型做帕累托路由；模型日益 commodity 化（每段时间都有更好的开源模型）→ 优化空间长期存在。Accio 1/3 成本的另一来源：同样模型下 harness 工程实践与 context 管理效率更高。

### 5. 商业 AGI 的定义与人的位置

商业 AGI 好定义：给定 budget 与供应链，agent 做日常操作判断比人赚到更多钱。但支付按钮、idea 靠不靠谱（真问题？客户群？技术足够大？）、产品 taste、市场节奏、budget 分配（广告 vs 库存 vs 渠道 vs margin）永远是人按按钮。多 agent 冲突的处理：老板要有整体经营目标（毛利/规模/速度），Accio 站"商家一本账"角度做整体优化，不做"统一所有 agent 意见"。

### 6. 上云 vs 长程；长程的三种范式

上云=功能完整性（本地 memory 上云换机可用）；长程=任务范式：定时任务（每日经营报告）/事件驱动（供应商沟通推进）/季度复盘（生意赚没赚钱）。"追求模型 7×24 跑一周不挂，不挂 means nothing。"——对当下 agent 营销话术的精准消毒。

### 7. CoCreate 现场与中小企业放大器

15000 人到场（booth 估小）；美国 AI/agent 用户教育领先。两个冠军案例给出"AI+全球供应链"的放大器叙事：15 岁初中生年销 100 万英镑；MIT 毕业生客户含 SpaceX、年营业额几千万美金。"中小企业的原问题不是 AI 取不取代工作，而是缺资源缺经验又想把生意做大。"

## 引用书目

无书籍。关联往期：E231《从 B2B 到 A2A：Agent 新基建，如何让"一人企业"做全球生意？》；本仓已做 E251（推理芯片）、E253（AI 数据行业）。

## 关键概念词

榜单-实操相关性断裂｜领域 benchmark（107 task/七大类/L1-L4）｜Agent = Model × Harness × Context｜帕累托最优路由｜Auto 模型｜用得起的 AI｜Agentic Trade｜Design Pack｜Ontology（企业上下文）｜商业 AGI 定义｜LUI｜长程三范式（定时/事件驱动/季度复盘）｜"不挂 means nothing"｜多 agent 冲突与一本账

## 关键观点（原话）

> "很多模型的通用评测成绩已经接近满分，但在真实经营中，他们并没有感受到同样幅度的提升。"

> "agent 等于 model 乘以 harness 乘以 context……为什么是乘法？就是哪一项是 0，整个这个公式结果就是 0。"

> "coding 在数学或者在通用的 agentic 的能力上得分比较高，和你在电商领域里能完成更多的工作，这个事情其实没有那么大相关性。"

> "必须是一个用得起的 AI，才是一个有价值的 AI。"

> "它可能做 3D 模型做得不错，也可能在一些 computer use 上有突破，但不代表它在通用商业里面的 agentic 能力强……说它是 AGI，我现在给你打保票的肯定不是 AGI。"

> "你要做一个长程任务……我就追求这个模型能跑 7×24 跑一个礼拜，它不挂——不挂 means nothing，如果没有解决你的问题的话。"

## 关键数字

| 数字 | 含义 |
|---|---|
| 99% | coding 领域 AI 渗透率（张阔估计） |
| +20% / +130% | alibaba.com 整体搜索 / 多模态搜索增长 |
| 107 个 | 开源电商任务 benchmark（七大类，快照数据，持续增加） |
| ~61% | 最前沿模型无人干预通过率（及格线都费劲） |
| 3.69 vs 9+ 美元 | 107 任务全跑完：Accio vs Codex/Claude Code 成本（约 1/3） |
| L1-L4 | 任务难度分级（越长程越开放，通过模型越少） |
| 20 列 Excel × 十几个供应商 × 以月计 | 无 agent 的供应商比选流程 |
| 24 小时 | 有 agent 后同等结果达成时间 |
| 20+ 年 | alibaba.com/1688 context 积累 |
| ~15000 人 | 洛杉矶 CoCreate 到场人数 |
| 100 万英镑/年 | 15 岁英国冠军年销售额 |
| 几千万美金+/年 | Christian Reed 生意规模（客户：施耐德电气、SpaceX） |
| 2011-2016 | 张阔在淘系做商家平台的年份 |

## Limitations

- Razer worker 域名白名单不批 aphid.fireside.fm，走本地 transcribe.py fallback（与课代表 216 同路径）——已在 pipeline 标注。
- 产品名 Accio Work 在转写中有 7+ 种误写，统一按 shownotes 修正；**GPT-6 Astra、Grok（Grogbot/Grog Ball）、WorkBuddy 为口播转写名，未逐一联网核实**；"anti-pride 版本"[?]（疑指供给侧 Supply-side）未能还原。
- 107/61%/3.69 美元等核心数字与 shownotes 交叉核对一致；其余数字（15000 人、100 万英镑、几千万美金）为口播转述未核原始来源。
- 本集为对话节目，张阔立场（阿里国际站总裁）天然偏向自家产品，"1/3 成本"等对比数字来自厂商自测 benchmark，无第三方复核。

## 思考与追问

1. **我真正理解了什么？**"榜单 99 分 vs 实操 61%"不是一个批评模型的段子，而是评测方法论的分野：**榜单测"答题能力"，经营测"把工作做完的能力"（含执行、判断、抗干扰）**。垂直 agent 的护城河 = context（20 年积累）× 领域 bench（107 任务）× 路由经济学（用得起）——这正是 E253"数据行业"报告的下游应用：出题人同时是判卷人。而"任何一项为 0 结果为 0"的乘法公式是最简洁的 agent 工程表述。
2. **我还没搞懂什么？①107 任务的开源地址与具体构成（口播只给了 3 个例子，七大类是什么？）；②"千问小尺寸 post-train 接近 frontier top"的评测口径；③GPT-6 Astra 发布后在这个 bench 上的实际得分（张阔说"过两天去看"——值得追）。
3. **下一步读什么/做什么？①找 107-task benchmark 开源仓库（接 E253 数据行业线：领域评测数据的生产与商业模式）；②对照自己的 agent 实践理解"harness"——eacli 舰队就是 harness 的实例（token 纪律下的成本路由与 Auto 模型思想同构）；③把"榜单-实操断裂"与课代表 216"Opus 5.5 审美代差"对读：一个是能力评测缺口，一个是审美评测缺口，同属"通用能力≠交付质量"。
