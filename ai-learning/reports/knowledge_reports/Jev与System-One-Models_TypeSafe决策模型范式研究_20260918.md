---
title: "Jev 与 System One Models — TypeSafe AI「决策模型」新范式全景研究"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-09-18"
---

# Jev 与 System One Models：从 Chat 到决策的范式解剖、生态盘点与批判性评估

**事件**：TypeSafe AI 于 2026-09-15/16 发布 Jev（early access）——首个 "System One Model"：不输出文本，输出**带校准概率的类型化决策**（Choice/Score/Noul 三原语），训练算法自称 RLCD（Reinforcement Learning for Calibrated Decisions）。创始人 Diogo Almeida，前 OpenAI 研究员、InstructGPT 论文第 4 作者 [已核实：arXiv:2203.02155 作者名单]。

> 标注约定：`[官方]`（官网/博客/docs 自述，注意其立场性）、`[已核实]`（第三方/可独立验证）、`[社区]`（HN 等观点）、`[评]/[推测]`（本报告分析）。
> 本报告的一手覆盖：typesafe.ai 首页全部 10 条 FAQ（从 Framer JS chunk 提取）、发布博客 7 条 FAQ、docs.typesafe.ai 全站、evals.typesafe.ai 逐模型原始数值、HN 讨论串（1866 分/491 评论）、GitHub 官方 org 10 仓 + awesome-jev 清单 90 条目。

---

## 开头三行：x → f → f(x)

- **x**：RLHF 把 LLM 优化成了"对人说话"的 chatbot，但软件内部的海量决策（分类、路由、打分、闸门）需要的是机器可消费的**判断**而非文本——模型应该为什么优化？
- **f**：TypeSafe 的回答是换优化目标：放弃字符串生成，模型单次前向并行输出预定义 schema 上的**概率分布**（typed decisions + calibrated confidence），训练目标从"人类偏好"（RLHF）换成"认知诚实的概率"（RLCD）——官方称之为 "the bitterest lesson"：*optimizing for the right task matters more than data, compute, or algorithms* [官方博客]。
- **f(x)**：接受 f 后得到的产物形态是：一个非自回归、输出 token 免费（"too cheap to meter"）、$0.042/M 输入 token、70–500ms 延迟的决策 API。验证状态：**范式方向获生态快速验证**（发布 3 天内 Vercel AI Gateway 上架、browser-use 官方集成、开源复现萌芽 [已核实]）；但全部性能/成本数字为厂商自报、无独立复现、RLCD 无论文——**"决策即接口"为真，具体数字待第三方检验**（§4 详拆）。

---

## 一、一手核实：官网 FAQ 与文档的关键事实

### 1.1 FAQ 逐条提炼（官方自辩的核心逻辑）

以下来自 typesafe.ai 首页 10 条 FAQ + 发布博客 7 条 FAQ 的原文提取 [官方]：

1. **与 JSON mode/structured outputs 的区别**——官方论证不是格式而是训练目标："Valid JSON gives software a format it can read. But forcing an LLM into that format can leave some of its intelligence on the table." System One 从训练起就为结构化决策优化，返回带校准概率的答案，代码可按概率决定行动/收集更多信息/升级人工。
2. **为何快且便宜**——"Jev replaces sequential generation with parallel computation, answering multiple structured questions in a single request." 官方自比"从串行到并行的跳跃类似 transformer 超越 RNN"。
3. **定价是否补贴**——首页否认补贴（"We can serve Jev profitably at our current prices"），但博客更诚实："We can't prove it isn't subsidized; we'll need the long-term to prove the sustainability of our pricing (which we expect to go down, not up)." [评] 即**官方自己承认无法证明无补贴**——DataCamp 也抓住了这点。
4. **"Zero Hallucinations" 的官方定义**——首页把 "Hallucinations" 划掉改为 "Zero Hallucinations"，正文定义实为："Every Jev decision comes with a confidence estimate, so your software can act when confidence is high and escalate when it is not." 博客的技术版更精确：放弃字符串生成后 "can't hallucinate"，"No type errors: mathematically impossible"。关键自曝：**"Our number is not empirical. Schema matching is guaranteed, thus we can confidently add 0% into the plots."**——0% 是构造性的（输出空间被 schema 封闭），不是实测值 [官方]。
5. **能力边界（罕见的坦率）**——docs 的 model-jaggedness 页（2026-09-17 更新）：不能可靠计数、数学/数字精度差、日期比较不可靠、双重否定掉精度、大 state 有 context rot、**对对抗性注入无防护**、instructions 与 criteria 矛盾会混淆、**Noul 与其否定式提问的概率和不为 1（官方自举例子：0.72 vs 0.47）**、不能生成文本。
6. **确定性**——不承诺 deterministic，改承诺 consistency（"语义相似则决策相似"）。
7. **数据**——"TypeSafe is primarily a data research lab… We make all the data ourselves." 训练数据构造方法拒绝披露；不用客户数据训练（所有账户共享同一权重；企业有 ZDR）。
8. **公开 benchmark**——官方**刻意不发**（"We deliberately chose not to publish performance against public benchmarks"），主张用户自建 eval（有其 antibenchmaxxing 博文）。[评] HN 对此的反应一针见血："I bet they would publish them if their score on those benchmarks were good" [社区]。

### 1.2 API 形态（docs.typesafe.ai 事实层）

- 单端点 `POST /v1/systemone`；请求三字段：`state`（被评估内容）+ `model`（`jev-latest`）+ `questions`（map<id, Question>，一次请求可混用多问、并行独立评估）。上下文预算 64k tokens/请求。
- **三种决策原语**：**Noul**（是非判断，返回 0–1 概率，名字 = Bernoulli 的缩写，映射 if 语句——CEO 在 HN 亲自解释）；**Choice**（≤255 个选项，返回全概率分布 + confidence）；**Score**（2–10 有序等级，返回概率加权期望分 + 分布 + confidence）。
- **置信度的确切语义**：`confidence` = 由 probabilities **分布形状（peakedness）计算的统计量**，分布越平置信度越低；**具体公式未披露**（官方说将出 cookbook）。官方反复强调 confidence ≠ 正确率保证。[评] 这很重要：confidence 目前只是"分布有多尖"，**官方未公布任何校准验证数据（无 ECE/reliability diagram）**——校准是宣称，不是已展示的证据。
- SDK：Python（`typesafe-sdk`）与 JS/TS（`@typesafe-ai/sdk`）；另有官方 agent skills 仓（Claude Code 插件）。限流 250k tokens/s + 1200 req/min（动态调整中）。
- 定价：当前唯一模型 Jev 1.13，**$42/十亿输入 token（$0.042/Mtok），输出免费**；输入仅文本；英文为主训练语言，CJK"handled but not equally well"。
- 命名彩蛋：System One 出自卡尼曼《思考，快与慢》；Jev 出自 Jevons（杰文斯悖论：智能成本每降一个数量级，用例涨几个数量级）——命名本身就是商业叙事的浓缩。

---

## 二、解构 "193.6x Faster, 444.6x Cheaper"

### 2.1 数字的真正出处与口径

证明链：首页 "(proof)" → 发布博客 → evals.typesafe.ai（4 个工作流：Security Incidents 240 案、Agent Trace Observability、Invoice Processing、Customer Service）[官方，原始数值已提取]。

- **方法**：无 ground truth——**假设 harness（代码工作流）正确，用 GPT-6 Astra + Claude Fable 5.1（均 high thinking）的平均预测当 reference 概率标签**；其他模型用各 provider 默认推理档位。LLM 侧成本按公开牌价 "estimated_uncached" 估算。
- **4 工作流平均（workflow 路线）**：Jev 67.8% · $0.0004/案 · 0.4s/案；opus 5 73.1% · $0.1761 · 37.8s；sol 74.1% · $0.0836 · 23.3s；sonnet 5 67.8% · $0.1174 · 78.1s；terra 67.9% · $0.0304 · 10.1s；DS v4 pro 65.5% · $0.0413 · 86.5s；luna 66.8% · $0.0033 · 12.9s；haiku 4.5 53.6% · $0.0195 · 12.5s。
- **头条数字的构造**：444.6x ≈ opus 5 的 $0.1761 ÷ Jev $0.0004；193.6x ≈ sonnet 5 的 78.1s ÷ 0.4s。[评] **两个倍数各自挑了最极端的单一对手**（最贵的算成本、最慢的算速度），不是对固定对手的整体倍数。若换对手：对 terra，成本倍数降到 ~76x、速度 ~25x；对 luna，成本 ~8x。官方博客自己承认："we expect that these are on the higher end of real world gains" [官方]。
- **准确率才是头条该有的位置**：Jev 67.8% 与 sonnet 5 持平、低于 opus 5（73.1%）和 sol（74.1%）——[评] 也就是说叙事应该是"**以 sonnet 5 的精度，做到其 1/300 的价格和 1/200 的延迟**"，这依然惊人，但比 193.6x/444.6x 诚实。
- **偏差自曝（值得称道的部分）**：工作流由自家能力团队制作（"some bias could exist"）；reference 用 Astra+Fable 平均"biased towards OpenAI and Anthropic"（可能低估 Jev/DeepSeek）；eval 从美国西海岸笔记本跑；side-by-side demo 的 state 是短密段落（"paints our model in an advantageous light"），Doom/Wikiracing demo 中 LLM 用非推理模式（官方承认这使 LLM 显得弱）[均为官方自述]。
- **独立复现**：DataCamp 明确指出全部数字 "vendor-reported"，"no large-scale independent reproduction has surfaced yet"；第三方 Jev Phishing Bench 中 Claude Haiku 4.5 准确率反超 Jev [已核实，第三方小样本 bench]。

### 2.2 "Zero Hallucinations"：逻辑漏洞与合理内核

- **合理内核（构造性）**：输出空间被 schema 封闭——给定的类别列表之外不可能发明新类别、类型错误数学上不可能。这与 Kalai & Vempala 2024《Calibrated Language Models Must Hallucinate》的理论结构一致：开放生成下校准与零幻觉不可兼得，但**封闭分类决策上零"越界"是构造可达的** [已核实：arXiv:2311.14648]。官方 0% 写进图表的依据正是构造性而非实测 [官方自曝]。
- **逻辑漏洞（三处）**：①"零幻觉"的公众语义是"不会自信地错"，而 Jev 照样可以选错选项——官方 FAQ 第 8 条承认 "guarantees the shape of its answers, not that every decision is correct"；HN 最高赞质疑即此："if it puts a high confidence value on a wrong answer, that's still hallucinating, no?" [社区]。②confidence 只是分布 peakedness，**校准宣称（"标 0.8 的应约 80% 正确"）无公开验证数据**——RLCD 无论文、无 reliability diagram、无 ECE 数字。③一致性自爆：Noul 正反两问概率和 ≠ 1（0.72 vs 0.47）[官方 jaggedness 页]——一个连"是/否翻转一致性"都没过的模型，"认知诚实的概率"还需要工程验证。
- [评] 准确的表述应该是：**"Zero Type Errors + 显式不确定度"，而不是 "Zero Hallucinations"**。The Register 编辑的判断一致：输出根本不是自然语言，"hallucination-free" 不是公平比较 [已核实]。

---

## 三、开源生态盘点

### 3.1 官方 org（github.com/typesafe-ai，10 仓）：接口开源、模型闭源

[已核实，GitHub API 实测，2026-09-18]

| 仓库 | star | 内容 |
|---|---|---|
| skills | 130 | Agent 技能包（教 Claude Code 等用 System One API） |
| typesafe-sdk-js | 91 | 官方 TS/JS SDK |
| system-one-adapter-python | 91 | **关键仓**：`TypeSafeClient` 的 drop-in 替换、后端走普通 LLM API——官方自己开源的"Jev vs 聊天模型"同题对照工具 |
| typesafe-sdk-python | 59 | 官方 Python SDK |
| 其余 6 仓（LLaDA/vllm/pulumi 等） | 0–6 | 基础设施杂项 |

- **没有 jev/RLCD 仓库，无权重、无论文、无技术报告**；evals 放在 evals.typesafe.ai 网站而非 GitHub。CEO 在 HN 自承 "architecture is close to the chest for now, but we have talked about writing a paper" [社区]。
- [评] `system-one-adapter-python` 是个双刃存在：它让 benchmark 更公平（LLM 以"最准确的方式"出决策），**但也等于官方承认"用普通 LLM API 可以模拟 System One 接口"**——Jev 的护城河只剩速度/成本/校准，接口范式本身可复制（见 §4.2 商业分析）。

### 3.2 awesome-jev 清单与第三方生态

`AnotiaWang/awesome-jev`（CC0，创建于发布第二天 09-17，31 star，~90 条目，自带防蹭收录标准，还记录了 PyPI 抢注 `typesafe-ai` 包名的 slopsquatting 事件）[已核实]。分类盘点：

- **SDK/薄封装**（~15 个：Rust×3、Ruby×2、Elixir、Go、PHP 等）：多为发布 48h 内的一夜封装，0–4 star——典型发布周泡沫。
- **真实信号**：
  - [browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast)——**3077 star**，Browser Use 官方号发布，完整 agent 库 + 性能文档（Google Flights 7.1s），09-18 仍在更新。**生态最大事件：主流 agent 框架直接采用**。
  - [TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev)——**1018 star**，3090 显卡本地跑 Jev-like（读选项 logits 不生成文本）；[vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike)（742 star，自训一遍式 scorer + Doom/棋类 demo）——两者都**明示不是 RLCD 复现**，只是 Jev-like 接口。开源社区在用脚投票：接口范式值得复现，RLCD 无从复现（无论文）。
  - 评测类 ~7 个独立 bench（钓鱼邮件/垃圾邮件/重排序等），其中钓鱼邮件 bench 上 Haiku 4.5 反超 Jev [已核实]。
  - 玩具类（俄罗斯方块/吃豆人/星际争霸等）占相当比例。
- [评] 生态结构判断："官方闭源模型 + 开放 SDK + 大厂框架集成（Vercel AI SDK provider + AI Gateway + eve 用 Jev 做模型路由）+ 开源替代萌芽"在**发布后 3 天内**成形。真实热度集中在 agent 框架集成与开源替代两头，长尾 SDK 是泡沫。

### 3.3 与 Pydantic AI / Instructor / Outlines 的关系：互补 + 被吸收，非正面竞争

- **架构差异是根本性的**：Instructor/Pydantic AI/Outlines/JSON mode 都是"让自回归模型吐符合 schema 的字符串再校验"；Jev 单次前向直接输出类型化值+概率，非自回归。Sean Goedecke 的评论点得准："其实和普通 LLM 的结构化输出没那么不同，但这个接口很酷，希望普及" [已核实：[seangoedecke.com](https://www.seangoedecke.com/jev-means-structured-output-is-interesting-again)]——差异化在**速度/并行性**，不在结构化本身。
- **已被吸收**：Vercel AI SDK 7 官方 provider（`@ai-sdk/typesafe-ai`，experimental `evaluate` API）；AI Gateway 托管 `typesafe-ai/jev`（09/15 上架，context/latency 列全是 "—" 未公布）；Vercel 自家 agent 框架 eve 用 Jev 做路由。
- **功能分工**：Jev 不能写文本、不能产生任意结构化数据——判断 vs 生成是两个子问题。
- Pydantic AI（Colvin）、Instructor（Jason Liu）作者对 Jev 无公开表态 [未查到，HN 491 评论中无其发言]。

---

## 四、技术深读：RLCD、parallel sampling 与校准谱系

### 4.1 校准（calibration）的技术现状

- **度量**：ECE（分桶后 |桶内准确率 − 桶内平均置信度| 的加权平均；Guo et al. 2017 使之流行并指出现代深度网络普遍过度自信、温度缩放是最简后校准 [arXiv:1706.04599]）；理论根基是 proper scoring rules（Gneiting & Raftery 2007）。
- **LLM 校准的共识**：GPT-4 技术报告的经典图——预训练模型校准良好，**RLHF 后显著过度自信** [arXiv:2303.08774]；verbalized confidence 跨模型系统性偏高（Xiong et al. 2023 [arXiv:2306.13063]；Tian et al. 2023 显示 RLHF 模型的口头置信度优于 logit 基线但仍不完美 [arXiv:2305.14975]）；RLVR 同样伤校准，RLCR（2025）证明在二元奖励上加 **Brier score 项**可修复 [arXiv:2507.16806]；Kirk et al. 2023 给出 RLHF 多样性坍缩（mode dropping）的实证 [arXiv:2310.06452]。
- **理论锚点**：Kalai & Vempala 2024《Calibrated Language Models Must Hallucinate》[arXiv:2311.14648] + OpenAI 2025《Why Language Models Hallucinate》（主张评估机制改用 proper scoring rules）[arXiv:2509.04664]——[评] **这两篇是 TypeSafe 整个叙事的学术地基**：如果二元对错评分在统计上奖励"蒙答案"，那就把"诚实的不确定度"直接写进训练目标。TypeSafe 创始人的 OpenAI 出身让这条谱系不是巧合。

### 4.2 RLCD 机制反推（标注推测）

公开锚点：输出 = 预定义 schema 上的概率分布 + confidence；官方对比表中 RLCD 的优化目标写作 "epistemically honest probabilities"；名字直指 "calibrated decisions"。

[推测，按置信度排序]：
1. **Proper scoring rule 直接进 reward**（置信度高）：对每条决策，以真实结果计算 Brier/log score 作为 RL 奖励。依据：校准的唯一严格训练信号就是 proper scoring rules；RLCR 已验证"正确性奖励 + Brier 项"可行；RLCD 大概率是把该思想搬到"纯决策分布"上，且可不再保留正确性项（决策本身即概率）。
2. **在低维离散输出空间上做策略梯度**（置信度中高）：无自回归 token 序列，策略 = 各槽位的 categorical 分布；天然避免 token 级 RL 的熵坍缩，"概率"是原生输出而非事后读出——这解释了"输出 token 免费"（一次前向的常数开销）。
3. **谱系**：与 DPO 无关（无偏好对）；属 RLVR/GRPO 家族，但奖励从"0/1 正确"换成"scoring rule 下的概率质量"——**优化方向从"答对"转向"诚实"**。与 PRM 无直接关系。可能另有一致性正则（官方称 similar inputs → similar answers）[推测，无公开证据]。
4. **关键证据缺口**：RLCD 无论文、无技术报告、数据构造保密——以上全部待官方兑现 "talked about writing a paper"。

### 4.3 "Parallel sampling" 的架构含义

既有文献中 parallel sampling 有三义：best-of-N、自一致性投票、非自回归并行解码。Jev 的用法是第四种含义：**单次前向并行产出全部决策槽位的概率分布**（官方对比表："Parallel. Generates all outputs in a single query."）。[推测] 架构上接近 encoder 骨干 + 每槽位分类/回归头（等价于把模型退化成结构化多任务分类器），或 masked/diffusion 式并行填充——这解释了 70–500ms 延迟与输出免费。[评] 官方"类似 transformer 超越 RNN"的类比是营销放大：transformer 的并行是在**训练**维度，Jev 的并行是在**输出结构**维度，牺牲的是生成能力本身——更接近"把 LLM 退化成分类器"的逆操作，但这个退化方向恰好是软件决策所需要的。

---

## 五、批判性分析

### 5.1 商业分析

- **TAM**：软件内部决策（分诊/路由/审核/打分/闸门）是真实且海量的需求——HN 上已有用户估算 "replace 40–70% of LLM calls in a pipeline" [社区]。Jevons 悖论叙事（命名即押注）：成本降两个数量级会打开"每次 API 调用里都塞一个判断"的新用法空间。[评] TAM 的上限不取决于 Jev 多强，而取决于"决策嵌入软件"的渗透率——这是真机会。
- **护城河评估（弱）**：①算法——RLCD 保密但思想（scoring rule 奖励）文献已有（RLCR），复现门槛低（openjev/jevlike 已在复现接口）；②数据——官方自称"primarily a data research lab"、自造数据，这是唯一可能的真实壁垒，但无法外部验证；③先发——3 天内 Vercel 上架说明渠道壁垒几乎没有。[评] 最大的威胁是**大模型厂商以结构化输出 + 长尾小模型降价碾压**：若 OpenAI/Anthropic 把 haiku/luna 级小模型的结构化决策延迟打到 500ms 内、价格打到同一量级，Jev 只剩校准概率这一个独占特性——而校准本身可以被"LLM + adapter + 后校准"逼近（官方自己的 adapter 就是证据）。
- **融资**：$40M [已核实，The Register]。发布即 Vercel 上架、docs/SDK/skills 齐全——这是一次准备充分的发布，不是仓促营销。

### 5.2 对个人开发者/小团队：现在值得接入吗？

**适合的场景**：高并发、低单值、可容错、可设置信度阈值的决策——内容审核初筛、客服分诊路由、agent loop 的下一步选择、搜索结果重排序、表单字段校验。[评] 判据只有一条：**你的场景是否能用"置信度低于 X 就升级给 LLM/人工"的两级架构**——能，则 Jev 的速度/成本优势直接兑现；不能（需要理由链、需要审计、需要长程推理），则不适合。
**不适合的场景**：需要 rationale 的受监管场景（Jev 只给概率不给理由——DataCamp 指出这是审计硬伤）；数学/计数/日期敏感判断（官方 jaggedness 页自认）；对抗性输入暴露面（无注入防护，官方自认）；中文为主的场景（CJK 支持较弱，官方自认）。
**风险提示**：定价可持续性官方自承无法证明（可能补贴）；early access + waitlist；避免把核心链路绑死在单一供应商的闭源决策模型上——好消息是官方 adapter 与开源替代品让迁移成本不高。

### 5.3 EverOwl 初判的验证结论

- "决策即接口"方向真 → **确认**（生态 3 天成形为佐证）。
- "Zero Hallucination 是营销话术" → **确认但需精确化**：构造性内核为真（封闭空间零越界），语义漏洞为真（可选错、可自信地错、校准无公开证据）。
- "基准对比有自选嫌疑" → **确认且比怀疑的更严重**：两个倍数分别选自不同极端对手；无 ground truth；reference 偏向 OpenAI/Anthropic；官方自认 "higher end of real world gains"。
- "窄模型的价值待任务漂移检验" → **确认**：官方不承诺 deterministic 只承诺 consistency，而 Noul 正反不一致（0.72/0.47）说明 consistency 本身尚在工程早期。

---

## 六、与 EverAgent 已有知识联动

- **[[rlhf]]**：Jev 是"RLHF 批判"的产业版注脚——RLHF 三宗罪（mode dropping/overconfidence/humans-in-the-loop）与本仓 rlhf 页记录的 reward hacking、多样性坍缩（Kirk et al.）完全同构；RLCD = 把优化目标从偏好换成 proper scoring rule。
- **[[test_time_compute]]**：Jev 的 parallel sampling 是 test-time compute 坐标系的**第四维度**——非"更多顺序思考"、非"更多并行采样投票"，而是"取消生成，并行出分布"。Snell 等人的 sequential/parallel 二分在这里需要扩展。
- **[[bitter_lesson]]**：官方自称 "the bitterest lesson"（优化对任务 > 数据/算力/算法）是对 Sutton 原命题的**任务维度改写**——值得在 wiki 中标注这个挪用：Sutton 说的是通用方法胜出，TypeSafe 说的是**选对优化目标**胜出，两者方向相反（一个反手工，一个更手工）。[评] 这是本报告一个独立的观察点。
- 新建概念页：[[model_calibration]]（校准与选择性预测），沉淀 §4.1 的谱系。

---

## 七、思考与追问

1. **我真正理解了什么？** Jev 的本质不是"更快的 LLM"，而是**把模型退化成结构化分类器来换取软件可消费的决策接口**——范式上合法且填补了真空（chat 模型为人优化、不为机器优化）；营销上把三个独立事实（构造性零类型错误、单前向并行、scoring-rule 校准训练）打包成一个夸大的 "Zero Hallucinations + 193x/444x" 叙事。它最大的战略漏洞藏在自家仓库里：system-one-adapter 证明接口可被普通 LLM 模拟，护城河只剩成本/速度/校准证据，而校准证据至今为零。
2. **我还没搞懂什么？** ①RLCD 的实际训练机制（官方承诺"想过写论文"，等 paper）；②confidence 的计算公式与真实校准曲线（无 ECE/reliability diagram 公开）；③"数据自造"具体指什么——合成数据管线？这决定护城河深浅。
3. **下一步读什么 / 做什么？** ①回访锚点：官方若发 RLCD 论文，核对 §4.2 的推测命中率；②等第三方复现（openjev/jevlike 的校准对比实验，或独立 ECE 测评），验证校准宣称；③把 Kalai & Vempala + OpenAI 2025 幻觉论文精读成一篇"幻觉的统计学根源"专题——这是理解整个"反 RLHF"阵营的理论地基。

---

## 来源清单（本报告联网检索，eacli Token Plan-first：web.read / web.search / repo.public / GitHub API）

**官方一手**
- [typesafe.ai 首页（含 10 条 FAQ）](https://typesafe.ai)；[发布博客 Introducing System One Models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)；[docs.typesafe.ai](https://docs.typesafe.ai)（API/SDK/confidence/model-jaggedness 页）；[evals.typesafe.ai](https://evals.typesafe.ai/)（workflow 原始数值）
- GitHub：[typesafe-ai org](https://github.com/typesafe-ai)（skills / typesafe-sdk-python / typesafe-sdk-js / system-one-adapter-python）

**媒体与社区**
- [The Register 2026-09-16](https://www.theregister.com/ai-and-ml/2026/09/16/typesafe-ai-debuts-model-for-machines-that-plays-doom/5296711)；[DataCamp 分析](https://www.datacamp.com/blog/system-one-models-jev)；[HN 讨论串（1866 分/491 评论）](https://news.ycombinator.com/item?id=49717558)；[Sean Goedecke 评论](https://www.seangoedecke.com/jev-means-structured-output-is-interesting-again)；[Vercel changelog](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway)；[Vercel Models & Pricing](https://vercel.com/ai-gateway/models/providers/typesafe-ai)

**开源生态**
- [AnotiaWang/awesome-jev](https://github.com/AnotiaWang/awesome-jev)；[browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast)；[TheoLeeCJ/openjev](https://github.com/TheoLeeCJ/openjev)；[vinnylarouge/jevlike](https://github.com/vinnylarouge/jevlike)；[jkudish/jev-mcp](https://github.com/jkudish/jev-mcp)；[droidrun/mobile-jev](https://github.com/droidrun/mobile-jev)

**学术谱系**
- [InstructGPT arXiv:2203.02155](https://arxiv.org/abs/2203.02155)；[Guo et al. 校准 arXiv:1706.04599](https://arxiv.org/abs/1706.04599)；[GPT-4 报告 arXiv:2303.08774](https://arxiv.org/abs/2303.08774)；[Xiong et al. arXiv:2306.13063](https://arxiv.org/abs/2306.13063)；[Tian et al. arXiv:2305.14975](https://arxiv.org/abs/2305.14975)；[Lin et al. arXiv:2205.14334](https://arxiv.org/abs/2205.14334)；[Kadavath et al. arXiv:2207.05221](https://arxiv.org/abs/2207.05221)；[RLCR arXiv:2507.16806](https://arxiv.org/abs/2507.16806)；[Kirk et al. arXiv:2310.06452](https://arxiv.org/abs/2310.06452)；[Kalai & Vempala arXiv:2311.14648](https://arxiv.org/abs/2311.14648)；[OpenAI《Why Language Models Hallucinate》arXiv:2509.04664](https://arxiv.org/abs/2509.04664)；[Farquhar et al. semantic entropy arXiv:2302.09664](https://arxiv.org/abs/2302.09664)；[Geifman & El-Yaniv 选择性预测 arXiv:1705.08500](https://arxiv.org/abs/1705.08500)
