---
title: "小米 MiMo-V2.6 公开直播 RL 训练 — RL Scaling 三维度体系研究"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-09-17"
---

# 小米 MiMo-V2.6 公开直播 RL 训练：RL Scaling 能否复制预训练的 Scaling 传奇

**来源**：量子位《罗福莉沉寂半年官宣小米强化学习！直播新模型训练过程，一小时烧3万美元》（2026-09，梦晨）| [原文链接](https://mp.weixin.qq.com/s/3QZ2TU7Y5xss_jjxIYjfNw) | 一手来源：[MiMo 训练直播页](https://mimo.xiaomi.com/rl)、[罗福莉 X 原帖](https://x.com/_LuoFuli/status/2100296686719610932)

> 材料性质：量子位文章是**科技媒体报道**（二手转述）；本报告同时读取了两份一手来源——训练直播页（2026-09-17 本报告实抓快照）与罗福莉 X 原帖（逐字全文）。标注约定：`[直播页实读]`（本报告抓取的一手页面数据，附抓取时刻状态）、`[X原帖]`、`[已核实]`（联网交叉验证，来源见清单）、`[源文]`（量子位文章表述）、`[评]/[推测]`（本报告分析）。

---

## 开头三行：x → f → f(x)

- **x**：预训练 Scaling 红利放缓后，强化学习能否成为下一条**可预测、可持续扩展**的能力轴——罗福莉的原话："过去半年只研究一个问题：RL 能扩展到多远？"（how far RL can scale）
- **f**：小米的回答是把整个 RL 循环工程化为一台可扩展的机器，沿**三个维度**同时 Scaling——训练计算量（每 Step 约 20 亿 token，1568 prompt × 16 rollout，Fully Async 流水线）、环境与执行框架（Multi-task Agentic RL，多类任务多 Harness 混入同一 run）、评分计算量（Grader Compute + Agentic In-group Credit Assignment）；并且**把训练过程本身直播公开**（成本计数器、逐 step 指标、故障公告全透明），把这个问题的答案变成一条全世界可围观的实时曲线。
- **f(x)**：接受 f 后，"RL Scaling 是否成立"从一个信仰问题变成一个**可观测、可回访的经验问题**——奖励曲线、pass rate、离线评测逐 step 公开更新，任何人都可以自己判断斜率。验证状态：早期信号正面但远未确证（Flash 起步 1 天多 dynsam/avg@n +0.089，Pro +0.026 [直播页实读]）；三维度各自的贡献无消融；**判断"RL Scaling 有效"需要 run 跑完后看曲线是否平台化、是否迁移到 held-out 任务**——见 §4.2。

---

## 一、一手信息核实

### 1.1 直播页实读（本报告 2026-09-17 抓取快照）

文章给的链接 `mimo.xiaomi.com/rl_` 现已 404，实际直播页在 **`mimo.xiaomi.com/rl`**（页面顶部 notice 与数据均实时滚动）。实抓时刻的关键状态：

| 项 | MiMo-V2.6-Pro | MiMo-V2.6-Flash |
|---|---|---|
| 启动时间 | 2026-09-15 10:32 UTC | 2026-09-15 15:16 UTC |
| 抓取时进度 | step 10 完成，step 11 **training** 中（已跑 1d 12h） | step 16 完成（该 step 2.6B tok），step 17 **rollout** 中（已跑 1d 7h） |
| dynsam/avg@n | 0.590（▲0.026 vs step 1） | 0.603（▲0.089 vs step 1） |
| DeepSWE v1.1（mini-swe-agent, avg@3） | 62.24 | 60.77 |
| train batch | 1568 × 16 seqs | 1568 × 16 seqs |

[直播页实读] 页面公开的远不止"奖励曲线"，是一份准工程监控面板：

- **训练内部指标**：actor/entropy_loss（Pro 0.390 / Flash 0.433）、actor/pg_loss、actor/grad_norm，以及一个信息密度极高的指标 **`train_infer_diff/new_infer/kl`**（Pro 0.0088 / Flash 0.00827）——训练策略与推理生成策略之间的 KL 散度。[评] 这等于把异步系统的**策略滞后（staleness）水平公开挂牌监控**，见 §2.1。
- **dynamic sampler 实时日志**：滚动显示 `accepted 2,016/1,568 · judged 1,884 · pass 0.601 (n=3,352) · remaining 689 +856 partial +276 rewarding · prewarm 461`。[评] 几个细节值得放大：①**accepted（2,016）超过 target（1,568）**——系统在超采样后筛选，不是简单的"生成多少用多少"；②日志里同时存在 `partial`（被中断/截断的 rollout）与 `prewarm`（预热队列）——这是完全异步流水线处理长尾 rollout 的直接证据；③pass rate（Pro 0.601 / Flash 0.662）公示了当前任务池对模型的实际难度。
- **Batch Composition**：每 step 的 prompt 来源构成，25 个数据源、5 大类。step 10 构成：code 67.7%、visual 13.1%、general 12.1%、cyber 4.1%、chat 3.0%，逐 step 给 Δ share。[直播页实读] 文章"Batch Composition 是在告诉外界模型正从什么任务环境里获取经验"的转述准确。
- **故障公告**："the mimo-v2.6-pro run is restarting due to a vram issue on one node"（单节点显存故障，Pro run 重启中）、"已更新 flash step 12 & pro step 8 的最新 deepswe 结果，离线评测会持续更新"。[评] 连单节点 VRAM 故障都广播——这正是文章"哪个节点的显卡出了故障全部公开可查"的原文依据，属实。

**成本**：另一抓取时刻的页面读数为 Pro $789,169（约 1d14h ≈ $20.5k/h）+ Flash $345,907（约 1d9h ≈ $10k/h），**两 run 合计约 $113.5 万 / 约 38 小时 ≈ $3 万/小时** [直播页实读，经子代理交叉抓取]——与文章"36 小时超 108 万美元、平均每小时 3 万美元"吻合；注意这是**两条 run 合并**的口径。

### 1.2 罗福莉 X 原帖（逐字核实）

> "Nearly half a year of silence. We spent it studying one problem: how far RL can scale. MiMo-V2.6 is in the middle of its RL run right now. Three things we scaled: **compute** (~2B tokens per step, 1568 prompts × 16 rollouts, fully async), **environments and harnesses** (multi-task agentic RL, mixed across multiple harnesses in one run), and **grader compute** (agentic in-group credit assignment, with test-case and rubric-based rewards). We'll open-source the details piece by piece over the coming weeks. Streaming the run: mimo.xiaomi.com/rl/" [X原帖，已核实]

转述出入（小但值得记录）：
- 原帖三维度为 compute / environments & harnesses / **grader compute**，"Agentic In-group Credit Assignment" 挂在第三维之下；文章拆成"评分 Scaling + 信用分配"两层叙述，结构略有放大但无实质失真。
- 原帖明确了 grader 侧的奖励形式为 **test-case 与 rubric-based rewards**——文章只笼统说"评分者消耗越来越多算力"，漏掉了 rubric 这个关键词（它对 §2.3 的技术定位很重要）。
- 原帖承诺"未来几周逐步开源细节"——**具体算法未公开是官方状态**，不是文章遗漏。
- 原帖未提 GPU 规模与框架名，文章同样没有——不存在转述损耗。

### 1.3 文章转述的硬伤与背景人物核实

- **⚠️ "对比 DeepSeek-Flash v1.1 是 74.2%" 疑似误拼**：DeepSWE v1.1 是 Datacurve 2026-05 发布的 benchmark（113 个长程 SWE 任务，mini-swe-agent harness [已核实：[arXiv 2607.07946](https://arxiv.org/html/2607.07946v1)]）；公开渠道**查不到名为 "DeepSeek-Flash" 的模型**，DeepSWE v1.1 上 ~74% 对应的是头部模型（GPT-6 Astra 74.1%、Claude Opus 5 约 74%）。[评] 大概率是编辑把 benchmark 名（DeepSWE）与头部模型分数拼成了"DeepSeek-Flash 74.2%"——**读者应把"与 74.2% 的差距"理解为"与头部闭源模型的差距"**，差距本身（60–64 vs ~74）是实的。
- **"自 4 月份开源 MiMo-v2.5 后沉默近半年"**：方向正确，细节有出入——V2.5 是 2026-04-23 开启公测、随后以 MIT 协议开放权重 [已核实：[GSMArena 2026-04-28](https://www.gsmarena.com/xiaomi_releases_openweight_mimov25_ai_model_claims_frontierlevel_agentic_capability-news-72585.php)、[36氪](https://m.36kr.com/p/3778536198264067)]。
- **罗福莉其人** [已核实]：北师大计算机本科 → 北大计算语言学硕士 → 阿里达摩院（主导 VECO、推动 AliceMind 开源）→ 2022 年入职 DeepSeek 参与 DeepSeek-V2 研发 → 2025-11-12 朋友圈官宣加入小米任 MiMo 大模型负责人，12-17 小米生态大会首秀发布 MiMo-V2-Flash（[IT之家 2025-11-12](https://www.ithome.com/0/896/855.htm)、[IT之家 2025-12-17](https://www.ithome.com/0/905/593.htm)）。旁证：2026-03 她以末位作者与北大发表 Agent RL 资源管理论文 ARL-Tangram（[BlockBeats](https://www.theblockbeats.info/flash/336633)）——"半年只研究 RL"有公开成果轨迹支持。
- **MiMo 系列脉络** [已核实]：MiMo-7B（2025-04-30 开源，[arXiv 2505.07608](https://arxiv.org/abs/2505.07608)）——MiMo-7B-RL-Zero 纯 RL 超 32B 基座的 RL 结果，MiMo-7B-RL AIME 2025 55.4 超 o1-mini 50.7，配套 **Seamless Rollout 系统使 RL 训练加速 2.29×**（[评] 小米在 rollout 系统工程上的积累比这次直播早一年多，Fully Async 不是从零起步）；MiMo-V2-Flash（2025-12-17，309B/15B MoE，MOPD + Agentic RL 后训练，[技术报告 arXiv 2601.02780](https://arxiv.org/html/2601.02780v2)）；MiMo-V2.5-Pro（1.02T/42B MoE、27T token 预训练、1M 上下文）。
- **"ViT 大佬锐评三件事背后都是算力"**：多轮检索（中英文、ViT 领域研究者方向）**均无出处** [未查到]。[评] 视为无法溯源的转述；其观点本身的公允性在 §4.3 单独评估。

---

## 二、技术深读

### 2.1 Fully Async：为什么大规模 Agentic RL 必须异步，staleness 怎么扛

**为什么必须异步**。同步 RL 流水线的死穴是 rollout 长尾：一个 Agent 任务 rollout 可能是几十轮工具调用，完成时间从秒级到分钟级不等；若按"全部生成完 → 统一评分 → 统一训练"排队，整个集群的 GPU 利用率被**最慢的那条轨迹**拖住，产生巨大气泡。Hugging Face 对 16 个开源 RL 库的系统对比（*Keep the Tokens Flowing*）把 rollout 长尾造成的 GPU 气泡列为异步化的首要动机 [已核实：[HF blog](https://huggingface.co/blog/async-rl-training-landscape)]。直播页动态日志里 `remaining + partial + rewarding + prewarm` 四队列并行、accepted 超采后再筛，正是"持续运转的异步流水线"的运转痕迹 [直播页实读]。

**代表性系统谱系**（均为 2025 年公开工作，[已核实]）：AReaL（蚂蚁/清华，生成与训练完全解耦、rollout worker 持续生成训练端流式消费，2.77× 加速，[arXiv 2505.24298](https://arxiv.org/abs/2505.24298)）；slime（清华，SGLang rollout + Megatron 训练，[GitHub](https://github.com/THUDM/slime)）；verl 的 One-Step-Off-Policy 异步 recipe（[文档](https://verl.readthedocs.io/en/latest/advance/one_step_off.html)）；PipelineRL（ServiceNow，in-flight weight update，[arXiv 2509.19128](https://arxiv.org/abs/2509.19128)）；LlamaRL（Meta，[arXiv 2505.24034](https://arxiv.org/abs/2505.24034)）；PRIME-RL / INTELLECT-2（去中心化异步，[arXiv 2505.07291](https://arxiv.org/abs/2505.07291)）。

**staleness（策略滞后）的处理**。异步的代价是：生成某条轨迹的策略版本落后于当前训练策略，等效于 off-policy 学习。文献共识：Noukhovitch et al. *Asynchronous RLHF* 论证异步 RLHF 等价于 off-policy RL，并证明典型 staleness 范围内性能不降、速度提升 [已核实：[arXiv 2410.18252](https://arxiv.org/abs/2410.18252)]；AReaL 的方案是 **decoupled PPO objective（行为策略与目标策略分离）+ importance sampling 校正 + max-staleness 阈值 + 打断过期 rollout**，论文含 staleness 消融 [已核实，同上]。[评] 直播页公开的 `train_infer_diff/new_infer/kl ≈ 0.0088` 正是在监控这个差距——KL 维持在 10⁻² 量级且随训练**下降**（▼0.001），说明滞后被控制在文献认为安全的范围内；至于小米具体用阈值截断还是 IS 校正，官方未公开 [推测：从页面同时存在 partial（打断）与 accepted 超采看，更接近 AReaL 式"阈值 + 打断 + 超采补偿"的组合]。

### 2.2 Agentic In-group Credit Assignment：可能是什么

官方只给了名字和设定（同 prompt 16 条 rollout），算法未公开。基于公开方法谱系的定位分析：

- **组内相对基线是现成的**：GRPO（DeepSeekMath，组内奖励均值作 baseline、标准差归一化，[arXiv 2402.03300](https://arxiv.org/abs/2402.03300)）与 RLOO（leave-one-out baseline，[arXiv 2402.14740](https://arxiv.org/abs/2402.14740)）都利用"同组多条样本"——但它们分配的是**整条轨迹级别**的相对优势：16 条轨迹谁好谁差，解决不了"40 步里哪一步立功"的问题。
- **步骤级信用分配的已有路径**：PRM 过程监督（OpenAI *Let's Verify Step by Step*，[arXiv 2305.20050](https://arxiv.org/abs/2305.20050)）、VinePPO（Monte Carlo rollout 估计每步价值，[arXiv 2410.01679](https://arxiv.org/abs/2410.01679)）；Agent 轨迹级别的最接近先例是 **GiGPO（Group-in-Group Policy Optimization）**——把多条轨迹中"同类锚点状态"下的步骤聚成组、组内算相对优势 [已核实：[arXiv 2505.10978](https://arxiv.org/abs/2505.10978)]；另有 SALT（步骤级 advantage，[arXiv 2510.20022](https://arxiv.org/abs/2510.20022)）与综述 *From Reasoning to Agentic: Credit Assignment in RL*（[arXiv 2604.09459](https://arxiv.org/html/2604.09459v2)）可作谱系骨架。
- [推测] **MiMo 的 "In-group" 大概率是 GiGPO 思路的工程化变体**：同组 16 条轨迹天然提供了"同一任务、不同命运"的对照组——成功的轨迹在第 k 步做了什么、失败的轨迹在同一步做了什么，这种组内对比可以在**不训练独立 PRM**的前提下为步骤级信号提供基线；再叠加 rubric/test-case 的中间检查点（原帖明确提到 rubric-based rewards），把"最终 Reward=1"稀释成沿轨迹分布的稠密信号。置信度中等，待官方开源验证（回访锚点见 §5）。

### 2.3 Grader Compute Scaling：给"判卷"也堆算力

- **这一维度的理论基础恰恰是"评分器是瓶颈"**：Gao, Schulman & Hilton 的 reward model overoptimization scaling law 证明——对固定 proxy reward 持续优化，gold reward 先升后降（模型学会 hacking 评分器）[已核实：[arXiv 2210.10760](https://arxiv.org/abs/2210.10760)]。推论：RL 能 scale 多远，受制于**评分器抗 hacking 的能力**，而提升评分器强度（更大 judge 模型、rubric 逐条核查、test-time verification）就是给这条约束松绑。
- **"给 grader 堆算力"的公开先例**：DeepMind GenRM（验证建模为 next-token 预测，test-time compute 越多验证越准——"verification scaling"，[arXiv 2408.15240](https://arxiv.org/abs/2408.15240)）；RM-R1（把打分本身做成推理任务，[arXiv 2505.02387](https://arxiv.org/pdf/2505.02387)）；OpenAI HealthBench（physician 撰写 rubric + model grader 逐条打分，[arXiv 2505.08775](https://arxiv.org/abs/2505.08775)）；Rubrics as Rewards（rubric 直接当 RL 奖励，把 RLVR 扩展到不可程序验证的任务，[arXiv 2508.12790](https://arxiv.org/abs/2508.12790)）。
- **RLVR 的边界**：Tulu 3 的定型结论是——可程序化判定（数学/代码/格式）用 verifiable reward，开放域仍靠 RM [已核实：[arXiv 2411.15124](https://arxiv.org/abs/2411.15124)]。[评] MiMo 的 batch composition 正好横跨这条边界：code（test-case 可验证）+ cyber/general/visual/chat（必须 rubric/judge）混在同一 run——第三维 grader compute 本质上是**把 RLVR 的可验证性边界往外推**，这与本仓 wiki [[rlhf]] 的 reward hacking 记录一脉相承：评分器越强，hacking 的套利空间越小。

---

## 三、谱系定位：RL Scaling 的行业脉络

- **DeepSeek R1 / R1-Zero**（2025-01，[arXiv 2501.12948](https://arxiv.org/abs/2501.12948)）：纯 RL 无 SFT 涌现自我验证、反思、"aha moment" 与思考长度自动增长——第一次让"RL 本身能长出能力"成为行业共识 [已核实]。
- **OpenAI o 系列**：官方博客 *Learning to Reason with LLMs*（2024-09）明确"性能随 **RL 训练算力**与 **test-time 思考时间**两条轴平滑提升" [已核实：[openai.com](https://openai.com/index/learning-to-reason-with-llms/)]——这是"RL 也有 scaling 轴"的最早官方主张，但曲线从未公开。
- **字节 / 阿里**：DAPO（开源大规模 RL 系统，[arXiv 2503.14476](https://arxiv.org/html/2503.14476v1)）、Seed1.5-Thinking（[arXiv 2504.13914](https://arxiv.org/abs/2504.13914)）、VAPO；Qwen QwQ-32B 与 Qwen3 系列的 agentic RL。RL scaling 是 2025–2026 全行业主线 [已核实]。
- **透明度的先例与小米的独特性**：公开训练过程并非全无先例——Prime Intellect INTELLECT-2（2025-04/05，"首个全球分布式 32B RL 训练 run"，任何人可贡献算力并围观，[博客](https://www.primeintellect.ai/blog/intellect-2)）与 Nous Psyche 去中心化训练网络；但先例都是**志愿者算力 + 小模型**的分布式实验。[评] 小米这次是**一线实验室的生产级 RL run 实时直播**：成本计数器、逐 step 内部指标（含 grad_norm、train/infer KL）、故障公告全部公开——这个透明度级别无先例。它的行业意义超出公关：§一 的成本计数器本身就是**行业首个公开的 frontier 级 RL 成本数据点**（OpenAI 从未公布 o 系列 RL 花费；公开只有"后训练算力占比可达总训练 40%+"的间接估计，[interconnects.ai](https://www.interconnects.ai/p/the-state-of-post-training-2025)）。
- [评] 与本仓 [[test_time_compute]] 三大流派表的对接：小米正在把"OpenAI o-series 的隐式 RL scaling 主张"用 DeepSeek R1 式的开源传统重新做一遍——**过程公开**是它相对两家共同的差异化。

---

## 四、批判性分析

### 4.1 一小时 3 万美元：RL Scaling 的成本曲线可持续吗？

- **量级定位**：合并口径 ≈ $3 万/小时 ≈ $72 万/天 [直播页实读]。对照锚点：DeepSeek-V3 论文口径的完整预训练为 2.788M H800 小时 ≈ $557.6 万（[arXiv 2412.19437](https://arxiv.org/abs/2412.19437)，注意这是论文的窄口径）——**这次 RL run 两天的花费已 ≈ V3 整个预训练账单的 1/5**；若 run 持续数周，累计可达千万美元级，超过 V3 预训练口径。GPT-4 级预训练的公开估计约 $4000 万–1 亿（Epoch AI / SemiAnalysis ~$63M），仍高一个数量级 [已核实-公开估计]。
- [评] **可持续性的真问题不是绝对值而是"能力/美元"曲线的形状**。预训练 Scaling 之所以能成为传奇，是因为幂律让投入可预测（本仓 [[scaling_laws]]：L(N,D,C) 跨数量级可外推）；RL 目前**没有被验证过的 scaling law**——没有人知道奖励曲线的斜率能维持几个数量级、拐点在哪。小米这个 run 的最大价值恰恰是用公开数据做一次现场实验：如果曲线在数百 step 后平台化，"$3 万/小时"就是不可持续的烧钱；如果斜率保持，它就是新预训练。现在就下结论都太早。
- [评] 另一个不对称：预训练成本一次性支付、模型全体受益；RL 的 grader compute 和 rollout 成本**随任务域扩张线性甚至超线性增长**（每加一类环境就要加一套 harness + 一套评分）。RL scaling 的成本结构可能比预训练更"重运营"。

### 4.2 当前数据能否支持"RL Scaling 有效"？

**能支持"有正向斜率"，不能支持"scaling 成立"**。

- 有的证据：Flash dynsam/avg@n +0.089（0.514→0.603，约 1.3 天 16 步）、Pro +0.026（0.565→0.590，10 步）[直播页实读]；DeepSWE v1.1 离线评测 60.77/62.24（后续更新 Pro 63.72）确认提升迁移到了独立 benchmark，不只是训练奖励自嗨 [直播页实读]。
- 缺的证据（判别性清单）：①**曲线形状**——16 个 step 的上升什么都证明不了，需要数百 step 看是否平台化、是否出现 overoptimization 拐点（Gao et al. 的结构预测它存在）；②**维度消融**——三维同时 scale，当前设计无法归因哪一维贡献了多少（环境多样性 vs 评分质量 vs 纯算力）；③**距头部差距的收敛速度**——60–64 vs ~74，追平需要多少 step/多少钱，这决定经济可行性；④**held-out 泛化**——dynsam 是训练分布内的动态采样指标，需要训练分布外的任务验证不是过拟合任务池。
- [评] 值得肯定的是：直播页的设计让这四条全部**可被外部证伪**——这是把"信仰宣称"改造为"公共实验"的正确姿势，比再发一篇只有终点结果的论文信息量大。

### 4.3 "三件事背后都是算力"公允吗？

作为零阶翻译成立（三维确实都烧钱），作为完整解释不成立——**它漏掉了算力买不来的三种稀缺品**：

1. **环境与任务设计**。环境维度的瓶颈不是 FLOPs 而是**任务构造**：什么样的任务池既有区分度又防过拟合、harness 的成功条件怎么定义——这是人类工程判断，且直接决定训练信号质量。直播页的 batch composition（code 67.7% 一家独大）背后是一个**配方决策**，不是算力决策 [直播页实读+评]。
2. **Rubric 质量**。Gao et al. 的教训是：对固定评分器堆优化算力，收益先升后降——**评分标准的质量（rubric 写得好不好）是 grader compute 的天花板**，而 rubric 由人写（HealthBench 用医生写 rubric 是有意的标杆 [已核实]）。算力放大评分器，但放大的方向由人设定。
3. **评测完整性（eval integrity）**。动态采样、超采筛选（accepted > target）、partial 打断策略——这些"数据食谱"决策影响学习信号的统计性质，同样不是算力。

[评] 更精确的表述应该是：**算力是三维度的共同放大器，但每个维度都有一个算力之外的人类判断瓶颈**。这与本仓 [[bitter_lesson]] 的对话值得展开：Bitter Lesson 说通用方法+算力长期胜出，但它不否认**短期内的杠杆在环境/奖励工程**——R1 的规则化奖励、Tulu 3 的 RLVR 边界划分，都是"人设计奖励结构、算力放大之"的合谋。小米三维度的真正创新不在"堆算力"，而在**把环境和评分也工程化为可扩展对象**——锐评者看到了共性（都费 GPU），漏掉了差异（把什么变成了可堆的对象）。

---

## 五、与 EverAgent 已有知识联动

- **[[scaling_laws]]**：预训练幂律是"RL 能否复制传奇"的参照系；RL 侧目前无已验证 scaling law，本 run 是公开实验（§4.1）。
- **[[test_time_compute]]**：o 系列/R1 两大流派已记录；小米路线 = R1 开源传统 × o 系列 RL scaling 主张 × 过程公开（§三）。
- **[[rlhf]]**：reward hacking 与 KL 约束的老问题在 grader compute 维度重现——评分器强度决定 RL 可扩展的上限（§2.3）。
- **[[agent_harness]]**：环境维度的 "harness 混合训练" 直接复用本仓 harness 概念——不同任务跑在不同 harness 里，harness 成为训练基础设施的一等公民。
- **[[bitter_lesson]]**：§4.3 的对话——算力放大器 vs 人类判断瓶颈。
- 新建概念页：[[rl_scaling]]（RL Scaling 三维度），沉淀本篇可复用框架。

---

## 六、思考与追问

1. **我真正理解了什么？** 这次直播的本质不是营销，是把"RL scaling 是否成立"从信仰问题改造成公共经验问题——三维度的真正创新是把**环境和评分也变成可扩展对象**，而不只是堆 token。一手核实还纠正了报道的两处失真：/rl_ 链接已失效（真实地址 /rl）、"DeepSeek-Flash 74.2%"是 benchmark 名与头部模型分数的误拼。直播页公开的 `train_infer_diff/kl` 与超采日志，让外界第一次能实时观察一个生产级异步 RL 系统的策略滞后与数据食谱。
2. **我还没搞懂什么？** ①Agentic In-group Credit Assignment 的具体算法（官方承诺"未来几周逐步开源"，是 GiGPO 式组内对照还是别的？）；②三维度无消融，各自的边际贡献无法归因；③RL 奖励曲线的长程形状（平台化拐点是否存在、在哪）需要 run 跑完才知道。
3. **下一步读什么 / 做什么？** ①回访锚点：小米开源技术细节后（罗福莉承诺数周内），核对 §2.2 的 [推测] 命中多少；②把直播页当作持续数据源，2–4 周后复查 dynsam 曲线斜率与 DeepSWE 分数，检验 §4.2 的判别清单；③沿综述 arXiv 2604.09459 精读信用分配谱系，把 GiGPO/SALT/VinePPO 做成 wiki 概念页，等 MiMo 开源时对照。

---

## 来源清单（本报告联网检索，eacli Token Plan-first：web.read / web.search）

**一手来源**
- [MiMo 训练直播页 mimo.xiaomi.com/rl](https://mimo.xiaomi.com/rl)（2026-09-17 本报告两次实抓）
- [罗福莉 X 原帖 @_LuoFuli](https://x.com/_LuoFuli/status/2100296686719610932)

**背景与行业**
- [IT之家：罗福莉官宣加入小米 2025-11-12](https://www.ithome.com/0/896/855.htm)；[IT之家：MiMo-V2-Flash 发布 2025-12-17](https://www.ithome.com/0/905/593.htm)；[BlockBeats：ARL-Tangram](https://www.theblockbeats.info/flash/336633)
- [MiMo-7B arXiv 2505.07608](https://arxiv.org/abs/2505.07608)；[MiMo-V2-Flash 技术报告 arXiv 2601.02780](https://arxiv.org/html/2601.02780v2)；[GSMArena：MiMo-V2.5 开放权重](https://www.gsmarena.com/xiaomi_releases_openweight_mimov25_ai_model_claims_frontierlevel_agentic_capability-news-72585.php)；[36氪](https://m.36kr.com/p/3778536198264067)
- [DeepSeek-R1 arXiv 2501.12948](https://arxiv.org/abs/2501.12948)；[OpenAI Learning to Reason](https://openai.com/index/learning-to-reason-with-llms/)；[字节 DAPO arXiv 2503.14476](https://arxiv.org/html/2503.14476v1)；[Seed1.5-Thinking arXiv 2504.13914](https://arxiv.org/abs/2504.13914)
- [Prime Intellect INTELLECT-2](https://www.primeintellect.ai/blog/intellect-2)（[arXiv 2505.07291](https://arxiv.org/abs/2505.07291)）
- [DeepSeek-V3 arXiv 2412.19437](https://arxiv.org/abs/2412.19437)（成本口径）；[interconnects：The State of Post-training 2025](https://www.interconnects.ai/p/the-state-of-post-training-2025)；[DeepSWE v1.1 benchmark arXiv 2607.07946](https://arxiv.org/html/2607.07946v1)

**技术文献**
- 异步 RL：[HF: Keep the Tokens Flowing（16 库对比）](https://huggingface.co/blog/async-rl-training-landscape)；[AReaL arXiv 2505.24298](https://arxiv.org/abs/2505.24298)；[slime](https://github.com/THUDM/slime)；[verl one-step-off 文档](https://verl.readthedocs.io/en/latest/advance/one_step_off.html)；[PipelineRL arXiv 2509.19128](https://arxiv.org/abs/2509.19128)；[LlamaRL arXiv 2505.24034](https://arxiv.org/abs/2505.24034)；[Asynchronous RLHF arXiv 2410.18252](https://arxiv.org/abs/2410.18252)
- 信用分配：[GRPO arXiv 2402.03300](https://arxiv.org/abs/2402.03300)；[RLOO arXiv 2402.14740](https://arxiv.org/abs/2402.14740)；[Let's Verify Step by Step arXiv 2305.20050](https://arxiv.org/abs/2305.20050)；[VinePPO arXiv 2410.01679](https://arxiv.org/abs/2410.01679)；[GiGPO arXiv 2505.10978](https://arxiv.org/abs/2505.10978)；[SALT arXiv 2510.20022](https://arxiv.org/abs/2510.20022)；[信用分配综述 arXiv 2604.09459](https://arxiv.org/html/2604.09459v2)
- 评分器：[Gao et al. RM overoptimization arXiv 2210.10760](https://arxiv.org/abs/2210.10760)；[GenRM arXiv 2408.15240](https://arxiv.org/abs/2408.15240)；[RM-R1 arXiv 2505.02387](https://arxiv.org/pdf/2505.02387)；[HealthBench arXiv 2505.08775](https://arxiv.org/abs/2505.08775)；[Rubrics as Rewards arXiv 2508.12790](https://arxiv.org/abs/2508.12790)；[Tulu 3 arXiv 2411.15124](https://arxiv.org/abs/2411.15124)
