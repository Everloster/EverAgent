# AI 自动数学研究（AI for Math / Automated Mathematical Research）

> 2026 年爆发的方向：大模型从"刷数学评测"转向"直接产出研究级成果"。本页为概念锚点，事件细节见报告。

## 核心事件线（均见报告《OpenAI数学手稿事件_核实与深度分析_20261008》附源）

- 2024-07：DeepMind AlphaProof+AlphaGeometry 2 达 IMO 银牌水平（28/42）
- 2025-07：多家达 IMO 金牌水平（DeepMind 35/42 官方评分；OpenAI 自报 35/42）
- 2025-10：Kevin Weil "GPT-5 解决 10 个 Erdős 问题"翻车（实为检索已有文献）
- 2026-05：OpenAI 模型推翻 Erdős 1946 平面单位距离猜想；Gowers 等 9 人写配套论文（arXiv:2605.20695）
- 2026-05-21：DeepMind AlphaProof Nexus 自主解 353 个 Erdős 问题中的 9 个，全部 Lean 机检（arXiv:2605.22763）
- 2026-09-04：Anthropic 用 Claude agent 11 天把费马大定理证明形式化为约 1300 万行 Lean（形式化，非新证明）
- 2026-09-08：OpenAI 宣布带光滑外力 3D Navier–Stokes 有限时间爆破（Clay 表述 C/D；约 1 万 agent、88 小时、数百万美元）；引发 Buckmaster/Alpöge 优先权与署名争议
- 2026-09-11：28 位菲尔兹奖得主联名信《A Severe Misalignment of AI in Mathematics》（一周内 7000+ 联署）
- 2026-09-21/29：IAS 顾问组 AGMAI 成立并发布《Responsible Release of AI-Generated Mathematics》（要求中立仓库、公开模型名/prompt/算力、报告失败、停止专有模型测前沿数学；OpenAI 拒绝最后一项）
- 2026-10-06/07：openai/math 发布——719 手稿/372 成果组/约 4000 开放问题/平均 3h ChatGPT Pro 算力每结果；头条：准黎曼 Re(s)>7/8（已 Lean 化）、矩阵乘法 ω≤9/4、四维挂谷、UGC、CM 阿贝尔簇霍奇、整数乘法推翻 Schönhage–Strassen 最优性。48 小时内因符号错误撤稿 3 篇（722→719）

## 关键概念

- **评判器成本 / 验证不对称**：AI 攻破学科的顺序≈验证答案的成本排序。数学（Lean）、代码（测试）裁判近乎免费故先爆炸；湿实验科学裁判昂贵故后至。可证伪预测：下一批应是裁判可自动化的领域（TCS/组合/形式化程度高的分支）
- **开放问题评估范式**：benchmark 饱和后直接拿前沿开放问题当评测集；新问题=无标准答案如何评分 + 选择性报告如何防（4000 进 372 出，失败不可见）
- **Lean 形式化的两条缝隙**：①编译通过≠证的是原题（statement 翻译需专家审计）；②告诉你"对不对"不告诉你"重不重要"。本次个别 Lean 条目陈述范围窄于标题
- **生成便宜→审核稀缺**：瓶颈从"产出证明"转移到"理解与审查证明"；数学界审稿激励体系与 AI 产出吞吐不匹配

## 关联

- 报告：`reports/knowledge_reports/OpenAI数学手稿事件_核实与深度分析_20261008.md`
- 缝合：[model_calibration](model_calibration.md)（外部验证器≈校准器）、[rl_scaling](rl_scaling.md)（grader compute=最便宜裁判）、[craft_displacement](craft_displacement.md)（个人技能替代 vs 学科结构替代）、[llm_evaluation_systems](llm_evaluation_systems.md)（评估范式）
- 方法论呼应：[problem_dissolution_rising_sea](problem_dissolution_rising_sea.md)（格罗滕迪克"涨潮"——AI 路线是反面：不是等海平面上升，而是直接排水）
