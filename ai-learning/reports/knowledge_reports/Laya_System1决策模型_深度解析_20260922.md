---
title: "Laya：把「反射性决策」从 LLM 里拆出来——421M 非自回归 System 1 决策模型解析与本机实测"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-09"
tags: [System1, 非自回归, RLCD, 校准, 决策模型, ModernBERT, 部署实测, 路由, Jev, OpenAI-Decisions-API, 源码深读, v0.4.1]
difficulty: ⭐⭐⭐
source_trigger: "微信公众号 ModelScope《Laya 开源：比Jev快4倍！421M参数，33毫秒完成 System 1 决策》（mp.weixin.qq.com/s/9SJf3nhK25rZcZwQNTg7mw）——用户要求：AI 研究学习 + 能否部署使用 + 双仓场景"
---

# Laya：把「反射性决策」从 LLM 里拆出来（v0.4.1 续深版）

> **x → f → f(x)**（按 METHODOLOGY 框架 A）
> - **x**：AI 流水线里海量「反射式判断」（路由/分级/是否）该由什么模型承担？
> - **f**：作者的回答——判别式编码器 + 类型化问题（choice/score/noul）+ 适当评分规则校准，把决策从生成式 LLM 中剥离成一次前向 [代码]。
> - **f(x)**：接受 f 后，决策层的成本结构被重写（10-30ms、$0、零幻觉），但「校准」大部分来自事后温度拟合而非 RL 训练（#741 实测），零样本能力低于 majority 基线——**它是「微调后用于垂域的快速底座」，不是开箱即用的决策引擎**。该结论已被本机实测（09-22）+ 源码深读（10-09）双重验证。

> **一句话**：Laya 是一个 421M 参数的非自回归决策模型——不生成任何文本，一次前向传播输出「选择/评分/布尔」三类判断及其**数学校准的概率**，本机 Mac MPS 实测 4 问 34.5ms / 1 问 10.7ms。它攻击的是每个 AI 流水线里最浪费的一环：**用 8B-70B 的生成式 LLM 回答"这封邮件该给谁"**。本报告 = 原理解析 + 官方宣称的本机核验 + 双仓（EverAgent / EverAgent-infra）场景评估；**10-09 续篇**追加 v0.4.1 源码深读、Jev→OpenAI 行业博弈全景、社区争议实录与理论定位。

---

## 0. 实测结论先行（部署可行性：✅ 完全可用）

| 项 | 结果 | 对照官方宣称 |
|---|------|------------|
| 安装 | `pip install laya`（v0.3.5，依赖 torch 2.14） | ✅ 一行安装属实 |
| 权重 | `laya.load("convaiinnovations/laya")` 自动拉取 5 文件（~89s，含 multilingual 共两个 checkpoint） | ✅ |
| **设备** | 本机 Mac **MPS 自动识别**；CPU 亦可用 | 官方称"普通 GPU、Mac MPS 或 CPU"——✅ 属实 |
| **延迟（MPS）** | **4 问并行 34.5ms；单问 10.7ms** | 官方 GPU 33-38ms——**MPS 与 GPU 同档** ✅ |
| 延迟（CPU） | 4 问 251.7ms | 可用，慢 7 倍 |
| 官方示例复现 | department→billing conf 0.889（文称 0.94）；churn 0.803（文称 0.892）；phishing 0.181（文称 0.008） | 大体复现，数值有版本间漂移 ⚠️ |
| 中文 | 英文 checkpoint 低置信（边界样本 conf 0.151——"正确地不确定"）；**multilingual checkpoint 路由 3/3 全对**（0.998/0.918/0.997） | 需换 multilingual 子模型 ✅ |
| ⚠️ 发现 | 加载时 RuntimeWarning：choice≥11 选项的温度越界被钳制，**该桶 confidence 视为未校准** | 文章未披露 |

**部署门槛**：约 1.7GB 权重、无 GPU 要求、Apache 2.0 可商用——**这是"当晚就能在自己电脑上跑起来"的模型**。

---

## 1. 问题定义：为什么 LLM 不擅长做决策

文章的第一节论点（也是 Laya 的立项理由）：现代 AI 流水线用生成式 LLM 处理**反射式决策**（工单路由/钓鱼检测/紧急度分级），代价是——
1. 500-2000ms 逐 token 生成的等待；
2. 每次调用的推理成本（Jev 口径 $0.042/M input tokens）；
3. 还要写正则/JSON 解析器从自由文本里抽标签；
4. 最伤的：**LLM 的"confidence: 0.95"只是像自信的 token 序列，背后无数学校准**。

对标的是 Kahneman 双系统理论：这类任务该由 **System 1**（快、反射、并行）做，LLM 留给 System 2（慢、推理、生成）。Laya 的输出空间被严格限定为「概率+数字」——**不生成文本，因此不会幻觉、不可能输出格式损坏的 JSON**。

**与本知识库的连接**：这正是 [Agent Harness 学习计划](../../roadmap/)里 harness 分层设计的「路由/门控」层——以及 [李继刚·易论AI 期]「服务裹着能力」的极致形态：把 FDE 的判断经验固化成一个 10ms 的前置分类器，低置信度才升级给 LLM/人。

## 2. 架构：ModernBERT-large + [MASK] 选项提取（421M）

- **主干**：ModernBERT-large（395M，28 层，hidden 1024，RoPE，8192 token 窗口），**完全双向**——每个 token 同时看到「状态」（邮件/工单/JSON）和「选项」的全部内容（LLM 单向生成做不到）。
- **选项提取**：每个选项配一个 `[MASK]` token，经两层决策头 Transformer 后用 `torch.gather` 抽取这些位置的隐状态 → MLP 打分 → 按问题类型分别拟合的温度 T 做 Softmax → 候选概率分布。
- **行动/升级头**（最有工程价值的部件）：池化 [CLS]（1024 维）拼接 4 个分布特征——max(p)、top1-top2 差、归一化熵、选项预算比 K/255——经 MLP 输出 [P(act), P(escalate)]。即**模型自己学会"何时该交给人工"**。
- **多问一次前向**：5 个问题整理成 batch，一次前向 35ms 全部评完（实测 4 问 34.5ms ✓）。

## 3. RLCD：校准背后的数学（本报告核心）

**朴素方案的失败模式**（文章讲得清楚）：
- 交叉熵训练 → 赢家 logit 趋向无穷 → **过度自信**；
- 二元奖励的标准 RL → 策略梯度把最高概率推向 1.0 → **通过破坏校准来最大化准确率**，成为"自信地犯错的机器"。

**RLCD（RL for Calibrated Decisions）的解法**：把**严格适当评分规则**（strictly proper scoring rules）作为奖励——当且仅当报告分布 q = 真实分布 p 时期望得分唯一最大。即：**只有说真话（诚实概率）才能拿最高分**。复合奖励含三种：
1. **对数评分** S_log：真值概率低时重罚（截断 -9.21 保数值稳定）；
2. **球面评分** S_sph∈[0,1]：奖励把概率质量放对位置，避免对数损失的梯度尖峰；
3. **排序概率评分 RPS**：有序量表（0-3 级紧急度）用累积分布的平方距离——猜 2 级（真值 3）比猜 0 级受罚轻，教会模型理解**量表上的距离**。

训练细节：纯策略梯度（零交叉熵）、G=8 组零和高斯探索（噪声投影到各选项和为零——因为给所有 logit 加同一常数会被 Softmax 抵消，这个细节很讲究）、组均值基线（GRPO 风格）、σ 从 1.0 退火到 0.3。

**成本敏感的行动头**（漂亮的推论）：奖励矩阵 = 自动行动对 +1.0 / 自动行动错 -3.0 / 升级人工 -0.5 → 最优策略自动学出**只在置信度 >62.5% 时行动**（1·p + (-3)(1-p) > -0.5 的解）。

**多轮**：TD(λ=1.0) 用逐步前缀（第 1/2/3 轮…）+ 蒙特卡洛终局回报，解决 2025 原方案的数据泄漏（模型偷看未来轮次）。λ=1 意味着不自举、直接对真实终局训练。

**置信度定义**：1 - 归一化香农熵 H(p)/log(K)——完全不确定=0.00，完全确定=1.00。

**数据纪律**：100% 人类标注真实数据集（拒绝合成标签——"用合成标签训练校准模型只会对 LLM 自己的幻觉校准"，这句值得抄进 METHODOLOGY）；防捷径：动态乱序选项、改写问题、原文/嵌套 JSON 交替、注入干扰问题。

## 4. 基准的批判性阅读

| 维度 | 数字 | 我的批注 |
|------|------|---------|
| 任务内宏平均 | 83.8%（ECE 0.060，n=23,024） | **方差极大**：路由 99.1% ↔ 回复质量评分 58.1%——它是"路由/审核之王，质量评估平平" |
| 意图路由 | 99.1%（ECE 0.009） | 最强项，校准近乎完美 |
| 审核/安全 | 96.7%（ECE 0.061） | 强 |
| 钓鱼/邮件分流 | 73.2% | 中等——文章标题场景反而是弱项 |
| 零样本 | 65.1%（情绪类掉到 58.3%） | 泛化有限，换任务族要重新校准预期 |
| 选择性自动化 | 只取 top-50% 置信度 → 92.2% | **核心卖点**：92% 精度自动处理一半流量 |
| vs Jev "快 4 倍/准 16 分" | — | ⚠️ **厂商自测 + 口径不对称**（Jev 用其公开发布数据，Laya 用自建 25,424 题）；Jev 是闭源 API（含网络往返），Laya 是本地进程——延迟对比不完全同维度 |

## 5. 双仓场景评估（用户第三问）

### EverAgent（公开仓）——适合的
1. **播客 ingest 的段落级分类**（高频批处理，最佳场景）：whisper 输出几千段，用 noul/score 原语标「是否广告段 / 是否口水词 / 章节归属候选」——把「删广告、找章节锚点」从纯手工/LLM 判断变成 10ms×N 段的批处理。**这是全仓最直接的落点**（每期 2000-5000 段 × 每段一次判断）。
2. **Trending/日报抓取的条目过滤**：每天几十条 repo/新闻，choice 原语判「是否值得进日报/归属哪条线」——但注意搜索相关性任务族只有 62.8%，**阈值要设保守**（只砍高置信度的垃圾）。
3. **报告自检辅助**（score 原语）：lint 之外给「思考与追问质量」打 0-3 分？——对应任务族 58.1%，**不推荐自动化，只可做人审的预排序**。
4. 入站六类路由（A-F 意图分类）：实测 3/3 全对——但**单用户对话场景收益有限**（LLM 路由在同一会话里"免费"）；真正受益的是未来若做批量任务队列/自动化流水线时的前置分发器。

### EverAgent-infra（私有仓，按功能不涉细节）——适合的
1. **告警/工单分级 + 升级门控**（score + act/escalate 头的教科书场景）：设备告警按 0-3 紧急度评分，置信度 ≥0.85 自动开工单、否则留给人——模型自带"何时交人工"的判断头，且**本地推理=敏感数据零外流**（HIPAA/GDPR 卖点对设备档案场景同样成立）。
2. **Razer M5 AI Lab 支线**：421M 权重 ~1.7GB，CPU 250ms/4 问也够用——**可与 vLLM 共存于同一张卡**，做 Agent Worker 的前置路由层；或者干脆跑在无卡的盒子上。
3. 邮件/消息分流的钓鱼与垃圾过滤（noul）——73.2% 的精度要求人工抽检流程配套。

### 不适合的（同样重要）
- 任何需要**理由/解释**的决策（它不生成文本——这既是特性也是枷锁）；
- System 2 任务：多步推理、开放生成、代码；
- 回复质量/情绪类低一致任务（<60%）；
- 中文场景必须换 multilingual checkpoint（英文版会"正确地沉默"，conf 0.15）。

### 落地形态建议（若做）
`ai-practice/` 起一个最小 demo：laya(MPS) + 播客段落分类器 + 与现有 LLM 判断的准确率对照（拿程乐松期 4466 段的人工校正结果当 ground truth）——正好是 B 类「低成本可运行实现 + 教学笔记」的标准形态。

## 6. 与既有研究线的互链

- **Agent Harness 学习计划**：act/escalate 头 = 「置信度门控」设计模式的实物样本；System1/System2 分层对应 harness 的 router 层与 reasoning 层。
- **李继刚·易论AI 期**：「服务裹着能力」——Laya 就是把 FDE 的路由经验固化为 10ms 前置件；「拉回平均值」的上下文问题在 Laya 上不存在（无状态、每问独立）。
- **colibrì（09-12 介绍）**：两种推理经济学——colibrì 省**显存**（大模型塞进小机器），Laya 省**token 与延迟**（小模型替大模型干活）；都对「每个 token 都是成本」的橘子论断回应。
- **王坚期**：「机器智能不做拟人」——Laya 是极端案例：连语言都不生成，只留判断。

## 🤔 思考与追问（2026-09-22 初版）

1. **我真正理解了什么？**
   Laya 的本质贡献不是 421M 的参数效率，而是**把「校准」从 LLM 的行为问题变成可优化的数学目标**（proper scoring rules 作为 RL 奖励）。工程上最有价值的是 act/escalate 头——「何时不信自己」被做成了模型的一部分，而不是外挂的 if-else。对双仓而言，它是第一批「本机 MPS 跑得起、延迟达标、Apache 2.0」的实用非生成模型。

2. **我还没搞懂什么？**（汇入 open-questions）
   - **温度钳制警告的边界**：choice≥11 选项未校准——多大范围的决策会踩到？（我的六类路由 4-6 选项安全，但 trending 标签可能 >11）需要实测校准曲线（reliability diagram）。
   - **校准的迁移性**：换一组自定义 criteria 后 ECE 还是 0.009 吗？官方基准全是预定义任务族——**自定义选项集上的校准衰减**是落地前必须自测的（正好接上一条的实测计划）。
   - RLCD 与单纯的 temperature scaling / Platt scaling（后处理校准）相比的增量到底多大？文章没给 ablation——「RL 训出来的校准」vs「后处理校准」是本报告最大的未验证假设。
   - Jev 对比的口径问题：闭源厂商 API 的 150ms 含网络，本地 33ms 不含——真实生产对齐的比较需要自己搭。

3. **下一步做什么？**
   - B 类候选：`ai-practice/laya-router-demo`——用程乐松期 4466 段真实数据做「广告段识别」对照实验（laya vs 规则 vs LLM），产出教学笔记；
   - 把「自定义选项集上的校准自测」写进 demo 的必做清单（用 reliability diagram + ECE）；
   - infra 侧若做告警分级，先拿历史告警数据回测 0.85 阈值的覆盖率/准确率曲线再上。

---

# 续篇（2026-10-09 · v0.4.1 · 31,848 stars 时代）

> 初版报告三周后回访。期间发生的事：仓库从 9,984 → **31,848 stars**（3.2x）、821 PR、100 贡献者；版本 v0.3.5 → v0.4.1（20 天 29+ 正式版）；两个 checkpoint → 三个（新增 `laya-typed-decisions`）；OpenAI 入场。本续篇基于**本地 clone 源码深读**（pin `1adc59f`，2026-10-08）+ Wikipedia/Fortune/HN 交叉核验，完整 7 章研究报告另见 `github-trending-analyzer/reports/research_NandhaKishorM_laya.md`。[API]

## 7. 行业叙事完整版：三周内的三方博弈

初版只把 Jev 当对比基准，现在它是一整条行业故事线 [Web]：

| 日期 | 事件 | 信源 |
|---|---|---|
| 2024 | Diogo Almeida 离开 OpenAI（在彼 ~4 年，做过 RLHF/InstructGPT/ChatGPT/GPT-4），与 Erik Gafni、Sasha Sheng 创立 TypeSafe AI | Wikipedia |
| 09-15 | **Jev 发布**（限量 early access）：判别式、typed 输出、宣称比前沿 LLM 快 40-200x/便宜 40-400x；同步宣布 DCVC 领投 **$40M 种子轮**（估值 $200M）| Wikipedia/Forbes/Fortune |
| 09-18 | Laya 开源（作者 NandhaKishorM/Convai Innovations，HN show 帖自称「built on the exact research on jev architecture one year ago」）| HN id=49765348（1,363 分）|
| 10-06 | **OpenAI 跟进发布 Decisions API**（基于 GPT-6 Luna）——品类获得最大玩家背书 | Fortune 10-08 |
| 10-08 | Fortune 专题《Jev…viral hit…OpenAI hot on its heels》；Laya 同日发 v0.4.1 | Fortune/API |

三个值得记住的细节 [Web]：
1. **「Jev」命名自 Jevons 悖论**（Almeida 亲口）：效率提升→消耗总量反而大增——比 LLM 便宜两个数量级的决策智能会催生海量新调用。这是对 Bitter Lesson 的一次经济学倒装：不是算力吞掉方法，而是廉价吞掉犹豫 [推测]。
2. **API 三原语同构**：Jev 的 `noul/choice/score` 与 Laya 完全同名同义（连 confidence 公式 `(p_max−1/n)/(1−1/n)` 都一致）——Laya 的 `laya-serve` 直接做 Jev-compatible HTTP 层。开源对闭源的「协议寄生」策略执行得非常彻底 [代码] [Web Wikipedia]。
3. **TypeSafe 的 RLCD 细节未公开**（Wikipedia 猜测含 Brier 项的监督式）；Laya 同名算法是作者自己的复刻命名。两个 RLCD 不是同一物——引用时必须区分 [Web]。

## 8. 源码深读：回答初版的三个未解问题

### 8.1 未解问题③「RLCD vs 后处理校准的增量」——#741 给出了答案

初版最大的未验证假设是「RL 训出来的校准 vs 后处理校准谁在起作用」。v0.4 源码直接回答了 [代码 `laya/train.py`]：

```python
LOSSES = ("soft-ce", "rlcd")
# "rlcd" (the default) is the notebook's objective: a GRPO-style term over noisy logit
# samples rewarded by `proper_reward`, plus soft cross-entropy...
# #741 measured no gain from the extra term on the typed-decisions split.
```

**结论：GRPO 项在该分割上零增益，`soft-ce` 单独等效**。再叠加上 shipped checkpoints 的出厂校准实际来自温度拟合（见下），README 开头的 "trained with RL against strictly proper scoring rules" 与可验证证据之间有明确缝隙。诚实地说：**Laya 证明了「编码器+类型化输出+事后校准」这条工程路线可行，但没有证明「RL 训练出校准」这个更强的命题**。初版对 RLCD 数学的分析依然成立（作为设计文档读），但要降级理解为「训练目标的设计意图」而非「已验证的增益来源」。

### 8.2 未解问题①「温度钳制的边界」——分桶校准机制全貌

`calibrate.py` 的完整语义 [代码]：温度按 `temp_bucket(qtype, k)` 分桶拟合（LBFGS，NLL on softmax(z/T)）；**桶样本 <2,000 不写入桶级温度**（回退类型级标量，下限 10 样本）；全部 clamp 到 [0.5, 5.0]。初版发现的「choice≥11 桶被钳制」即落在「样本不足→标量→clamp」的路径上。工程含义没变：**自定义选项集必须自带 ≥2,000/桶 的校准集重拟合**，否则置信度只是「看起来校准」。

### 8.3 新发现：编码格式与 token 预算经济学

`build_sequence` 的真实格式 [代码]：
```
[CLS] <qtype> instructions [SEP] [MASK] opt0 [MASK] opt1 … [SEP] state [SEP]
```
- 问题+选项（head）在前、state 在后，`head_max_len`（192/256）封顶，**每选项保底 4 tokens**（`per = max(4, (head_max_len-16)//k)`）——超过 ~head_max_len/4 个选项时 head 会**超出上限**，state 被截断而非仅保守 [README Honest limits]。77 选项 × 4 tokens ≈ 300+ tokens 的 head，每选项 3-4 tokens「文本不可分辨」，0.425 准确率的根因在此。
- state 的 tokenize **每行一次、全问题共享**（`state_ids` 复用）——批量多问的 token 经济学核心 [代码]。
- 补丁双层：`predict_shortlist`（调用方嵌入模型先筛 top-20）与 `predict_tournament`（16 标签分组循环赛）[代码 `shortlist.py`]。

### 8.4 新发现：防御性工程的范本价值

三处值得抄进自己项目的模式 [代码]：
1. **OOM 作用域回退**：GPU 溢出只把当前请求降级 CPU 重试（曾因一次 OOM 永久降速 10-15x，#649 修复），降级计数写进 `/health`——「慢车道可观测」；
2. **懒加载边界**：`import laya` 不拉 torch（模块级 `__getattr__`），路由/语言检测纯 Python 可用——导入开销与推理解耦；
3. **供应链 pin 语义**：per-checkpoint SHA-256 覆盖 shared map 的合并规则、显式 `{}` = 「这条不验证」的掩蔽语义，全部有测试钉死——digest 工程的教科书。

## 9. 社区争议实录：「just BERT」论战

HN 1,363 分主帖的 77 条评论里，批评与赞美同样有信息量 [Web]：

| 阵营 | 论点 | 我的核验 |
|---|---|---|
| NLP 老兵（Oras） | 「it's just BERT」——决策模型=分类器换皮 | ✅ 架构上成立（ModernBERT+头），但低估了「类型化 API+校准+生态」的产品化增量 [代码] |
| 第三方实测 | 合成数据集 1,000 条：Jev 98% vs **Laya 15%** | 与 README 自认「零样本低于 majority 基线」一致——**未微调的 Laya 不可用** [README] |
| 上下文批评（cube2222） | 512-1024 vs Jev 32k 是重大限制 | ✅ 8192 上限后长文准确率 8-17/20 波动 [README] |
| 「vibecoded」质疑 | 代码疑似 AI 生成堆砌 | ⚠️ 与源码实读相反：docstring 即 ADR、防御性极强——更像是「AI 辅助但重度人审」的产物 [代码] [推测] |
| 支持者（zurfer） | Jev 已把 Luna/Gemini 工作负载变 10x 便宜 2x 快，Laya 再开源化一层 | 品类价值的最强证词 [Web] |

这场论战的教学价值：**「架构是否新颖」与「产品是否成立」是两个问题**。Laya 在前者接近零创新（BERT+分类头+适当评分规则都是已知件），在后者做对了 API 设计、诚实基准与生态卡位——而 OpenAI 用 Decisions API 入场证明了后者的市场判断。

## 10. 理论定位：判别式决策模型在谱系里的坐标

- **适当评分规则的数学地位**：log score 对真实分布的期望在 q=p 时取唯一最大（Gibbs 不等式）；spherical score S=(p·q)/‖q‖ 同样严格适当且梯度更平滑；RPS 对有序类别是严格适当的（按累积分布 CDF 距离）。Laya 把三者加权复合（w_sph=0.5, w_rps=1.0），复合保持适当性——**设计正确**；只是其必要性未被 #741 之上的消融支持 [代码] [推测]。
- **判别 vs 生成的分工理论**：Jev/Laya 属于「判别式 zero-shot 指令跟随」——用指令文本在推理时定义标签空间（区别于经典分类器的固定标签训练）。它填补的是「LLM 太贵、FastText 太笨」之间的空档。OpenAI Decisions API 用 GPT-6 Luna 做同样的事，说明路线之争（专用小模型 vs 通用大模型+API 包装）刚刚开始 [Web Fortune]。
- **System 1/2 映射谱系**：Kahneman（2011 心理学）→ TypeSafe（2026 商业化命名「System One models」）→ 社区共识术语。注意这是**隐喻而非同构**：Laya 没有「快而直觉」的认知机制，只有「快而受限的输出空间」——System 1 的「直觉性错误」（如否定句失效 #377）恰好也在 Laya 上复现，倒是个有趣的平行 [推测] [README]。

## 🤔 思考与追问（2026-10-09 续）

1. **我真正理解了什么？** 三周前我以为 Laya 的核心资产是「RLCD 训练出的校准」；源码深读后修正为——它的核心资产是**「类型化决策 API + 可复现的诚实基准 + 微调工具链」这个产品化组合**，校准主要靠后处理温度。这个修正本身就是方法论课：README 的叙事层（RL 训练校准）与证据层（#741 消融）之间的缝隙，只有读代码才能看见。
2. **我还没搞懂什么？**
   - OpenAI Decisions API（GPT-6 Luna）的能力边界与定价——若它以生成式大模型做到 Jev 级速度，专用判别式小模型的存在意义会被压缩到「本地/隐私/边缘」场景；需要等第三方基准。
   - `laya-typed-decisions` 的微调配方（RLCD vs soft-ce 在**其他**分割上是否也无增益——#741 只测了一个分割）。
   - 高基数问题的 shortlist 路线（嵌入模型与决策模型的误差如何叠加）——README 的 Banking77 0.425 没有给出 shortlist 修复后的对照数字。
3. **下一步做什么？**
   - 初版计划的 B 类 demo（`ai-practice/laya-router-demo`，播客段落分类对照实验）依然成立，且 v0.4 的 `train.py` 让「微调后 vs 零样本」对照实验成本大降——优先级上调；
   - 在 demo 中补一组「soft-ce vs rlcd」双目标微调对照（每个只需 ~352 updates，Kaggle 2xT4 可跑）——直接回应未解问题；
   - 跟踪 OpenAI Decisions API 的第三方评测，一个月后回访这条产品线。

## 来源（续篇追加）
- 本地 clone 源码：`NandhaKishorM/laya@1adc59f`（2026-10-08，v0.4.1）——`train.py`/`calibrate.py`/`common.py`/`agent.py`/`router.py`/`shortlist.py`/`pyproject.toml` 逐文件精读 [代码]
- GitHub API（2026-10-09 实测）：stars/contributors/releases/commit_activity/pulls（821 PR）/languages [API]
- Wikipedia: *Jev (AI model)*（2026-10 快照：TypeSafe 创始团队/$40M DCVC 种子轮/技术规格/RLCD 未公开）https://en.wikipedia.org/wiki/Jev_(AI_model)；Fortune 2026-10-08（OpenAI Decisions API 10-06 发布、Almeida 专访）https://fortune.com/2026/10/08/jev-an-ai-for-making-quick-decisions-has-been-a-viral-hit-in-silicon-valley-but-openai-is-hot-on-its-heels；HN show 帖 https://news.ycombinator.com/item?id=49765348（1,363 分主帖+评论，经 Algolia API）；TypeSafe 官方博客 https://typesafe.ai/blog/introducing-system-one-models-and-jev（经搜索摘要）[Web]（eacli web.read 于 10-09 抓取；HN Algolia API 直取——eacli 对该 URL 解析失败的记录降级）
- 竞品 gh 实测（2026-10-09）：urchade/GLiNER 4,067★、huggingface/setfit 2,836★、sentence-transformers 19,161★、AbdelStark/jev-benchmarks 25★、nibzard/decision-model-benchmark 11★ [API]
- 姊妹报告：`github-trending-analyzer/reports/research_NandhaKishorM_laya.md`（7 章完整版，同日）

## 来源（2026-09-22 初版）
- 触发文章：ModelScope 公众号《Laya 开源：比Jev快4倍！421M 参数，33 毫秒完成 System 1 决策》（mp.weixin.qq.com/s/9SJf3nhK25rZcZwQNTg7mw，全文经 web-reader 抓取）
- GitHub：NandhaKishorM/laya（Apache 2.0，2026-09-18 创建，实测时 9,984 星/827 forks，Python）[Web]
- 模型：convaiinnovations/laya（ModelScope/HF 双发布；English + multilingual 两 checkpoint）[Web]
- 本机实测：laya 0.3.5 + torch 2.14，macOS arm64，MPS/CPU 双设备，2026-09-22（全部数字为亲手运行结果）

*报告生成时间: 2026-09-22*
*研究方法: 文章全文精读 → 仓库/安装核实 → 本机 MPS/CPU 实测（延迟/示例/中文/多语路由）→ 基准批判性阅读 → 双仓场景对照；官方宣称逐条标注复现结果*
