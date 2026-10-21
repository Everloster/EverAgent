---
title: "AI 行业日报 · 2026-10-20"
domain: "web-surfing"
report_type: "daily_digest"
status: "completed"
updated_on: "2026-10-20"
quality_schema: "report-v2"
quality_tier: "standard"
semantic_tags: ["ai_news", "daily", "industry_watch"]
---

# AI 行业日报 · 2026-10-20

五源：AIHOT ❌ · GitHub Trending ✅ · AI Digest ❌ · HN ✅ · AI Tech Blog Radar ✅（10-21 补核）
覆盖 2026-10-20（含前日发布、今日仍在前排的条目） · [上期日报 →](./ai-news-daily-2026-10-19.md)

---

## 今日要点

1. **MiniMax M3.1 Flash**：AA 指数 42 追平 GLM，$0.22/任务，10-23 开源
2. **Minecraft 全自主通关**：四个 Argon agent 27 小时无人工屠龙
3. **Stripe agent 账单**：9 月交易数增 38 倍，约 200 个 agent 在花钱
4. **neocloud 洗牌**：CoreWeave 市值跌四分之一，业内料仅 7–10 家幸存
5. **Anthropic 谈判规范**：就 agent 代用户砍价咨询律所，防放大不平等
6. **Mistral Timestral**：5M–209M 时间序列模型，三基准零样本第一
7. **Trending 换血**：插件目录仓出清，headroom、claude-code 新上榜
8. **Ask HN 热议**：看不懂的 AI 代码敢不敢上线，389 条评论

---

## 头条 1 · 📏 MiniMax M3.1 Flash：AA 智能指数 42 追平 GLM，$0.22/任务再压价格线

**三句话速读**：MiniMax 发布推理模型 M3.1 Flash，AA 智能指数 42（前代 M3 为 29），追平 GLM-5.3-Flash、略超 Gemini 3.8 Flash（41），仍落后 DeepSeek V4.1 Flash 1017（45）。官方 DeepSWE v1.1 最高 73.7%、单任务成本低于 $0.30，The Decoder 归纳为与 DeepSeek 1017「性能与价格双持平」。权重定于 10-23 开放。

**关键事实**
- AA 口径逐项：Humanity's Last Exam **48%**（DeepSeek 43%）；研究级物理推理 CritPt **22%**（GLM-5.3-Flash 15%、Gemini 3.8 Flash 18%、DeepSeek 24%）；事实准确 AA-Omniscience **56%**（GLM 28%、DeepSeek 43%）。
- AA 套件成本：每任务约 **$0.22** vs DeepSeek 1017 的 $0.26，来源是输出 token 更少（189M vs 224M）；官方称速度为 M3 的三倍。
- 弱点同样醒目：AA 测得 **93% 幻觉率**——模型从不弃答，不确定时也硬答。
- 规格与定价：1M token 上下文，文本+图像输入；API **$0.15/M 输入、$0.60/M 输出**、缓存 $0.015/M；platform.minimax.io 已上线，另有桌面端 MiniMax Code。
- OpenRouter 10-19 数据日：M3.1 Flash（free）以 **1.05T tokens** 新进日榜第 7；HN 条目 375 分 / 163 评论。

**细读与质疑**
- 基准数字来自 MiniMax 自报图表与 AA 单家指数，独立评测未出；「价格战没有地板」是 The Decoder 的定性。
- 56% 事实正确率与 93% 幻觉率并存：便宜且肯答，但答案可信度要打折，两者是同一枚硬币的两面。
- 10-23 开源是承诺而非既成事实；OpenRouter 的 1.05T 走免费变体，含引流因素，不能直接读作付费采用。
- 与 10-19 记录的 DeepSeek 1017「约 $0.20/任务」口径不同源：那是官方 DeepSWE 均值，本文 $0.26 是 AA 套件口径，两者不矛盾但不可混用。

**来源** · [The Decoder 全文（本期直读，10-19T18:22Z）](https://the-decoder.com/minimax-m3-1-flash-shows-chinas-ai-price-race-has-no-floor-in-sight) · [MiniMax 官方模型页（本期直读）](https://agent.minimax.io/tools/m3-1-flash-preview) · 历史线：[10-19 头条 3（DeepSeek V4.1 Flash 1017）](./ai-news-daily-2026-10-19.md)

---

## 头条 2 · 🤖 四个 Gemini 4 Argon agent 全自主通关 Minecraft：27 小时 14 分、$1,620

**三句话速读**：Google DeepMind 团队把四个 Gemini 4 Argon agent 投进随机生成的 Minecraft 世界，不指派角色、策略或专用工具，首次在无人工干预下击败末影龙。四个 agent 自行分工、互相示警、从阵亡队友回收物资，并把错误写入共享记忆。全程 27 小时 14 分，成本 $1,620。

**关键事实**
- 自主分工：任务自拆、威胁互告、阵亡队友物品回收、错误共享记忆——协调行为未被预编程。
- 总账：共写 **2,783 个 JavaScript 程序**，交换 229 条聊天消息，死亡 **605 次**。
- 成本 **$1,620** 按 2027 年生效的标准 Argon 价格折算；论文署名 Faldor 等。
- The Decoder 点评：几年前这类游戏还需从零专门训练的 AI 系统，现在通用 agent 模型直接拿下。

**细读与质疑**
- 全部细节为 The Decoder 首页全文口径，DeepMind 原始论文与博客未直读；「首次」为报道口径。
- $1,620 依赖 2027 年定价口径，随官方价格变动；605 次死亡说明「自主」包含大量试错成本。
- 通关一个有既有基准的游戏，与开放世界的真实任务之间还有距离，不宜直接外推。

**来源** · [The Decoder（本期直读，首页全文口径）](https://the-decoder.com/) · 历史线：[10-14 头条 1（Gemini 4 Argon 全面开放）](./ai-news-daily-2026-10-14.md)

---

## 头条 3 · 🏢 Stripe 首披露 agent 消费数据：9 月交易数增长 38 倍，约 200 个 agent 在花钱

**三句话速读**：据 Upstarts Media 报道，经 Stripe 支付服务 Link 代用户购物的 AI agent 在 9 月交易数增长 38 倍、支付量增长 20 倍。Stripe 做分析时约 70 个 agent 接入，如今约 200 个，含 Meta 的 Muse 与 Grok Bot。Stripe 高管 Dan Hill 称量级正在变得显著。

**关键事实**
- 消费结构：多数 agent 单笔约 **$100**，部分被用来订机票、买数千美元家具；零售占交易 36% / 金额 32%，旅行占金额 28%。
- 安全设计：Link 不向 agent 提供真实卡号，改发独立 16 位号码，用户可设消费限额。
- Anthropic 与 OpenAI 也在用 Link，但尚未用于 agent 购买；Hill 承认 PayPal、Shop Pay 会跟进，市场仍极早期。

**细读与质疑**
- Stripe 未披露绝对交易数与金额；报道自己声明增长从小基数起，倍数不等于规模。
- 单一支付渠道口径，PayPal 等竞品的 agent 支付数据未覆盖。
- 该主张为 The Decoder 对 Upstarts Media 的转述，原文未直读。

**来源** · [The Decoder（本期直读，首页全文口径，转述 Upstarts Media）](https://the-decoder.com/)

---

## 头条 4 · ⚙️ neocloud 洗牌启动：CoreWeave 市值缩水四分之一，微软退出 Nscale 芯片交易

**三句话速读**：The Decoder 分析称，继多轮股价暴跌与 Firmus 撤回 IPO 后，业内高管预计数百家 AI 云（neocloud）中只有 7–10 家能活下来。CoreWeave 市值缩水四分之一，微软退出了与 Nscale 的 23,000 块 Nvidia 芯片交易。Nvidia 敞口最大：hyperscaler 之外客户占其数据中心收入 45%。

**关键事实**
- 事件锚点：CoreWeave 市值缩水四分之一；微软–Nscale 23,000 块芯片交易告吹；Firmus IPO 撤回。
- 出清预期：「数百家只剩 7–10 家」来自匿名业内高管的判断，非公告。
- Nvidia 的传导链：neocloud 是 hyperscaler 之外的最大买家群，占数据中心收入 **45%**，洗牌直接冲击其营收结构。

**细读与质疑**
- 这是观点分析文而非单一事件报道，核心判断（7–10 家）无实名来源。
- 与 10-15 记录的「银行转手 AI 数据中心债」同属一条金融链：钱从债端和股权端同时退潮。
- 微软退出交易的原因（需求还是商务条款）原文未展开，单一事件不宜过度解读。

**来源** · [The Decoder（本期直读，首页全文口径）](https://the-decoder.com/) · 历史线：[10-15 趋势 2（AI 基建两端重估）](./ai-news-daily-2026-10-15.md)

---

## 头条 5 · ⚖️ Anthropic 咨询律所为 AI agent 谈判立规：强模型谈出好价格会放大不平等

**三句话速读**：据 Financial Times 报道，Anthropic 正与律所咨询制定「公平谈判规范」，为 AI agent 代用户砍价、处理投诉、改进合同报价立规。公司实验已显示更强的模型能谈成更好的交易，可能扩大社会不平等。同一周，其 Conceptual Reasoning Fellows 岗位开始招律师。

**关键事实**
- 规范对象：agent 代用户讨价还价、投诉解决、合同条款改进三类场景。
- 人才动作：Conceptual Reasoning Fellows（明确招律师）以 **$100,000–167,000** 聘期四个月，测试 Claude 在法律、哲学、认知科学、经济学、政治学上的判断题。
- 动机口径：数学与代码有充足可验证数据，人文学科没有；研究员 Justin Curl 称法律上「定义质量出了名地难」。

**细读与质疑**
- FT 原文未直读，全部细节为 The Decoder 转述口径。
- 「谈判规范」处于咨询早期，离产品与行业标准都远；Anthropic 单方面立规的约束力未知。
- 与同日 Taste-Bench（最强模型二元战略题正确率不足 60%）对读：先立规范还是先有能力，两条线在赛跑。

**来源** · [The Decoder（本期直读，首页全文口径，转述 FT）](https://the-decoder.com/)

---

## 头条 6 · 📄 Mistral 开源 Timestral：5M–209M 参数时间序列基础模型，CPU 毫秒级推理

**三句话速读**：Mistral 发布首个时间序列基础模型家族 Timestral，四档 5M/28M/123M/209M 参数。209M 档在 GIFT-Eval、TIME、fev-bench 三个公开基准的预训练零样本模型中全部第一，参数只有前 SOTA 的约三分之二。今日 HN 讨论 540 分 / 103 评论，为全站最热 AI 条目。

**关键事实**
- 跨尺寸战绩：28M 档胜约四倍大的 Chronos-2（GIFT-Eval 与 TIME）；209M 档以更少参数胜 TimesFM-3 与 Falcon-2.0。
- 工程卖点：无需 GPU——8 线程服务器 CPU 上，用三周 15 分钟粒度历史预测一天，5M 档 **10ms**、209M 档 140ms；123M 档以 3/4 延迟达到 209M 档分数 0.2% 以内。
- 能力面：概率预测输出 21 个分位；支持多变量目标、past-only 与 known-future 协变量、类别协变量；上下文 32,768 时间步。
- 技术要点：解耦视界预测（DHF）、协变量感知注意力、训练数据以合成为主、两阶段训练；技术报告后续发布。
- 开放度：Modified MIT 许可，GitHub 仓已放出，可 on-prem / VPC / air-gapped 部署，另可经 Mistral Forge 微调。

**细读与质疑**
- 「全部第一」限定预训练 + 零样本类别，不含按数据集微调的专模型；成绩为 Mistral 自报（已提交 GIFT-Eval 与 TIME 榜）。
- 发布时间口径不一：Hugging Face 与多方快照指向约 10-16，官方页 publishedTime 元数据异常（显示 7-15），按多源记 10-16、今日 HN 热议首录。
- 训练数据以合成为主，真实企业序列上的泛化要等技术报告与第三方复现。

**来源** · [Mistral 官方公告（本期直读，一手全文）](https://mistral.ai/news/timestral) · [HN 首页快照（Timestral 条目 540 分 / 103 评论）](https://news.ycombinator.com/)

---

## GitHub Trending（12 仓快照）

今日榜单（2026-10-20 快照，按页面顺序，**12 仓**；上期 10-19 为 13 仓，**8 仓存留**，[claude-plugins-official、cursor/plugins、VoiceStudio、android/skills、llm-course 5 仓落榜](./ai-news-daily-2026-10-19.md)）：

| 仓库 | 总星 / 今日星 | 语言 | 一句话 |
|------|------------|------|--------|
| [MadsLorentzen/ai-job-search](https://github.com/MadsLorentzen/ai-job-search) | 57,297 / **+3,856** | Python | 本机 AI 求职框架（Claude Code），二连榜居首 |
| [anomalyco/opencode](https://github.com/anomalyco/opencode) | 217,820 / +1,311 | TypeScript | 开源编码 agent，二连榜 |
| [akitaonrails/ai-memory](https://github.com/akitaonrails/ai-memory) | 11,354 / +666 | Rust | agent CLI 长期记忆与跨厂商交接，二连榜 |
| [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | 139,729 / +1,011 | Python | diffusion 模块化 GUI，二连榜且日增放大 |
| [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | 77,193 / +564 | TypeScript | 多玩家 agent swarm 编排 harness，二连榜 |
| [stablyai/orca](https://github.com/stablyai/orca) | 98,298 / +1,590 | TypeScript | agent 舰队工作台，二连榜 |
| [headroomlabs-ai/headroom](https://github.com/headroomlabs-ai/headroom) | 76,250 / +310 | Python | **新上榜**：进 LLM 前压缩工具输出/日志/RAG 块 |
| [withmarbleapp/os-taxonomy](https://github.com/withmarbleapp/os-taxonomy) | 6,128 / +284 | JavaScript | **新上榜**：描述缺失，功能待核 |
| [Kruk2/jasna](https://github.com/Kruk2/jasna) | 2,896 / +498 | Python | 视频修复工具，二连榜 |
| [HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything) | 55,241 / +606 | Python | 让所有软件 agent-native，三度入榜 |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) | 152,658 / +167 | TypeScript | **新上榜**：官方仓本体进快照 |
| [shiyu-coder/Kronos](https://github.com/shiyu-coder/Kronos) | 41,678 / +363 | Python | **新上榜**：金融市场基础模型 |

**今日特征**
- 上期同榜的三平台插件/skills 目录仓（anthropics、cursor、android）今日全部出清，「平台目录」热度退潮；取而代之的是 anthropics/claude-code 官方仓本体首次进本周期快照。
- ai-job-search 二连榜居首（+3,856），总星破 5.7 万——「用 AI 找工作」与 10-19 Anthropic 初级岗位数据同周发酵。
- 新上榜 headroom（+310）：在内容进 LLM 前压缩工具输出与 RAG 块，称编码 agent 省 20%、JSON 省 60–95% token，与 HN「token-maxxing 已死」同题。
- Kronos（+363）金融市场基础模型回榜，与 Mistral Timestral 同日呼应「基础模型走出语言」。
- AI/agent 浓度 11/12（os-taxonomy 无描述存疑）；ai-job-search、ai-memory、ruflo、headroom、jasna、CLI-Anything 六仓 Built by 列表含 @claude。

- 来源：[GitHub Trending](https://github.com/trending)（2026-10-20 快照，12 仓直读）

---

## 顶尖技术博客更新

### AI Tech Blog Radar · 2026-10-21 补核

本节于 **2026-10-21 16:36 UTC（上海时间 10-22 00:36）** 补核：雷达请求 20 个已登记技术源，20 个成功返回；保留 12 条候选。以下三条 feed 时间按 Asia/Shanghai 换算后，落在本报要求的 **2026-10-19 至 2026-10-20** 窗口。

- **2026-10-20 · NVIDIA Technical Blog**：[Accelerating Mamba-2 with High-Performance Forward Pass Kernels in NVIDIA CUDA Tile](https://developer.nvidia.com/blog/accelerating-mamba-2-with-high-performance-forward-pass-kernels-in-nvidia-cuda-tile)。只确认官方 feed 的标题、发布日期和可用摘要；正文与实验结果尚未直读。
- **2026-10-20 · Hugging Face Blog**：[ALTK-Evolve: How learned memory tops the τ²-bench leaderboard on customer service tasks without a frontier model](https://huggingface.co/blog/ibm-research/altk-evolve-bc)。只确认官方 feed 的标题、发布日期和可用摘要；正文与实验结果尚未直读。
- **2026-10-20 · Hugging Face Blog**：[AnyLanguageModel 1.0: One Year of Local Models on Apple Platforms](https://huggingface.co/blog/anylanguagemodel-1-0)。只确认官方 feed 的标题、发布日期和可用摘要；正文与实验结果尚未直读。

边界：查询的是补核时的当前索引，并有 12 条候选上限；它不能复原完整的 10-20 历史快照。相对日期检索结果与上海时间 10-21 的条目未纳入本节，未直读正文的标题不能支持具体性能结论。部分 feed 在 eacli 未返回完整 XML 时使用了已记录原因的只读 HTTP XML 降级。

## 简讯

- **Kling AI 发布 4.0**（[The Decoder 首页](https://the-decoder.com/)，直读）：视频生成器支持 30 秒片段、10 张关键帧输入、8,000 token 提示理解，配立体声与多语言口型同步，另有轻量 Flash 变体。与 Wan 3.0、Seedance 2.5 对比「不落下风也未拉开」，该刊提示视频模型进步或开始变平。
- **Taste-Bench 发布**（[The Decoder 首页](https://the-decoder.com/)，直读）：测长任务战略选择的新基准，最强模型 GPT-5.6 Sol 在简单二元题上正确率也不足 60%，延长思考无改善。
- **DeepSeek V4.1 Flash 1017 登顶 OpenRouter 日榜**（[OpenRouter Rankings](https://openrouter.ai/rankings)，本期直读）：10-19 数据日处理 3.61T tokens（+19%）居第一，DeepSeek 周请求份额 24.4% 亦居首。[历史线：10-19 头条 3](./ai-news-daily-2026-10-19.md)
- **Ask HN：看不懂的 AI 代码敢上线吗**（[HN 246 分 / 389 评论](https://news.ycombinator.com/)，标题级）：与 10-19 Anthropic 初级岗位数据同题对读，正文未读。
- **Launch HN: Laminar（YC S24）**（HN 45 分 / 22 评论，标题级）：RL 训练的模型专找 agent 轨迹中的错误。
- **RuneScape Bench: MMOs for Agents**（HN 148 分 / 59 评论，标题级）：给 agent 玩的 MMO 基准，视频未读。
- **RTX Spark 笔记本首波 Linux 移植**（HN 171 分 / 74 评论，标题级）：10-16 上市的新品被用户自行装 Linux。[历史线：10-14 头条 6](./ai-news-daily-2026-10-14.md)
- **Token-maxxing is dead**（HN 28 分 / 29 评论，标题级）：OpenRouter 称 token 用量进入平台期，正文未读。
- **去护栏模型的安全代价**（HN 15 分 / 8 评论，标题级）：abliterated 模型可被用于入侵（「bonsoir, Elliot」），正文未读。
- **HN 备查**（非 AI 为主）：Wine 移植 OpenBSD（492 分 / 164 评论）；It's still ok to enjoy programming（430 分 / 406 评论）；动物实验替代品起飞（IEEE，317 分）；Let's Encrypt 增加两个远程验证视角（242 分）；Plex 漏洞被在野利用投递挖矿程序（144 分）；法国超市冰箱联网暴露数月（32 分）。

---

## 趋势总结

### 1. 📏 **中国 Flash 价格战继续下探，用量已先于口碑收敛**

MiniMax 把 AA 指数 42 的模型压到 $0.22/任务，DeepSeek 1017 同日登顶 OpenRouter 日榜。

- OpenRouter 10-19 数据日日榜前十中九席为 Flash/免费/低价变体，唯一例外是 Claude Opus 5.5（第 6，1.08T，+31%）；DeepSeek 周请求份额 24.4% 居首。
- HN「token-maxxing is dead」（标题级）与 Trending 新上榜的 headroom（进 LLM 前压缩上下文）从两端指向同一事实：token 预算从「冲量」转向「省钱」。
- 冷读：token 数≠质量，免费变体含引流；M3.1 的 93% 幻觉率提醒便宜有代价，价格战还没有卷到可信度。

### 2. 🏢 **AI 基建的钱继续挤出泡沫，应用层支付却在放量**

neocloud 出清预期与 Stripe agent 消费 38 倍增长同日出现，同一条产业链两端信号相反。

- 出清端：CoreWeave 市值缩水四分之一、微软退出 Nscale 芯片单、业内料仅 7–10 家幸存，接续 10-15 的银行甩债信号。
- 放量端：约 200 个 agent 经 Link 消费、多数单笔 $100、零售与旅行占大头——agent 商业闭环第一次有了支付侧数据。
- 冷读：两端的账最终要对上——如果 agent 消费撑不起算力债，出清会比预期更快；[推测] 下一季度 Stripe 类数据的绝对值比倍数更值得盯。

### 3. 🤖 **多智能体协作拿下新里程碑，判断力基准仍在掉队**

四个 Argon agent 27 小时全自主通关 Minecraft，同日 Taste-Bench 显示最强模型战略选择题正确率不足 60%。

- 协作能力（分工、示警、共享记忆）已经可在长时程任务中自组织，$1,620 的成本口径首次给出「通关一个游戏多少钱」的读数。
- 判断力短板（Taste-Bench <60%、延长思考无改善）说明「会做」与「会选」仍是两种能力。
- Anthropic 提前找律所定谈判规范，是把规范做在能力前面的尝试；规范跑不跑得过能力，取决于 Taste-Bench 类曲线的斜率。

---
---
*报告生成时间：2026-10-20*
*主数据源：AIHOT · GitHub Trending · AI Digest · Hacker News · AI Tech Blog Radar*
*检索通道：eacli Token Plan（web.search / web.read）*
*说明：评分为站点标注值；以官方链接为准。*

<details><summary>数据源与直读情况（详）</summary>

- **AIHOT**：当日不可用。旧址 aihot.virxact.com/daily/2026-10-20 两次、canonical 域 aihot.news/daily/2026-10-20 一次共三次尝试，均被 zhipu web-reader 内容过滤拦截（MCP error -400，code 1301，提示输入或生成内容含敏感内容）；web.search 检索亦未命中 10-20 期正文。本期中文聚合源缺口由 The Decoder 全文/首页与多源检索补足，未伪造补齐；标 ❌。
- **GitHub Trending**：2026-10-20 快照 12 仓直读，总星 / fork / 今日星均可读；fork 数未入表（与上期格式一致）。上期 13 仓中 8 仓存留、5 仓出清（三平台插件/skills 目录仓全部落榜），4 仓新上榜（headroom、os-taxonomy、claude-code、Kronos）。
- **AI Digest 中文**：首页直读正常，最新一期仍停留在 2026-08-24，停更约 8 周，当日无内容可用，标 ❌。
- **Hacker News**：首页 30 条快照直读正常，无 item id；Timestral（540 分 / 103 评论）、MiniMax M3.1 Flash（375 分 / 163 评论）、Ask HN AI 代码（246 分 / 389 评论）、RTX Spark Linux（171 分）等分数以快照为准。
- **AI Tech Blog Radar**：2026-10-21 16:36 UTC 经正式雷达入口补核，20/20 源返回、12 条候选；仅选择 feed 时间换算到 Asia/Shanghai 后落在 10-19 至 10-20 的三条条目，正文未直读。补核时刻、上海时间及报告日期分列，条数上限和历史窗口不完整见上节。
- **本期直读失败项**：AIHOT 全站（provider 内容过滤，见上）；FT 原文（Anthropic 谈判规范，The Decoder 转述）；Upstarts Media 原文（Stripe agent 消费，The Decoder 转述）；DeepMind Minecraft 论文/博客原文（The Decoder 首页口径）；Reuters M3.1 报道与 Reddit 权重时间帖（检索快照级）；Timestral 的 Hugging Face 模型页（检索快照级）；Kling 4.0 官方公告与 Taste-Bench 原论文（The Decoder 首页口径）；Ask HN / Show HN / Launch HN 系列均 HN 标题级未读；AA 原始图表未直读（经 The Decoder 转载口径）。
- **本期一手直读项**：the-decoder.com/minimax-m3-1-flash-shows-chinas-ai-price-race-has-no-floor-in-sight（10-19T18:22Z，全文）· mistral.ai/news/timestral（官方全文）· agent.minimax.io/tools/m3-1-flash-preview（官方全文）· openrouter.ai/rankings（usage through Oct 19 全量：日榜/周榜/月榜/份额）· the-decoder.com 首页（Minecraft、Stripe、neocloud、谈判规范、Kling 4.0、Taste-Bench 首页全文口径）· github.com/trending（12 仓）· news.ycombinator.com 首页 30 条。
- **转述级关键条目**（未回查原文，待复核）：M3.1 全部基准与定价数字（MiniMax 自报图表 + AA 单家，经 The Decoder）· Minecraft 27h14m / $1,620 / 2,783 程序 / 605 死亡（The Decoder 口径，Faldor 等原文未读）· Stripe 38 倍 / 20 倍 / 约 200 agent / $100 单笔（The Decoder 转述 Upstarts Media）· neocloud 7–10 家幸存与 Nvidia 45% 敞口（The Decoder 观点文）· Anthropic 谈判规范与 Fellows 薪酬（The Decoder 转述 FT）· Kling 4.0 对比结论与 Taste-Bench <60%（The Decoder 首页口径）· Timestral 发布日期（HF/Reddit 多源快照，官方页元数据异常）。
- **去重说明**：对照最近三篇（10-19 / 10-15 / 10-14）——DeepSeek V4.1 Flash 1017（10-19 头条 3）仅以 OpenRouter 登顶日榜增量进简讯并链历史线；Gemini 4 Argon（10-14 头条 1）以 Minecraft 四 agent 成果为新增量进头条；RTX Spark（10-14 头条 6）以 Linux 移植简讯续线；Anthropic 初级岗位研究（10-19 头条 1）The Decoder 首页仍在推但无新增量，不再引用；德国判例、中国出口管制草案、Character.AI、Modal、Copilot RCE 等无新增量不引用；MiniMax M3.1 Flash、Minecraft 通关、Stripe agent 消费、neocloud 洗牌、谈判规范、Timestral（约 10-16 发布，10-19 未收录）、Kling 4.0、Taste-Bench 均为本期首录。

</details>
