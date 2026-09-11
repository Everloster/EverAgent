# Anthropic 经济情景模型（Economic Scenarios for Transformative AI）

> Anthropic Institute 工作论文 2026-02（Korinek/Jones/Sacher/Cotter/McCrory，2026-09）+ 官网 Scenario Explorer：把 AI 能力预测翻译成 2030 年宏观变量的第一台"官方翻译机"

## 一句话定义

任务实例级 CES 模型：五条外生路径（能力面 m × 采用 d × 单点增益 a × 自动化份额 ψ × 新任务回补 ρ）+ 两个劳动市场摩擦（工资刚性 ξ、跨职业搜索折扣 μ），映射到 GDP / 劳动份额 / 分组工资 / 失业率。**m·d = AI 执行的经济任务实例份额**，是一切的核心乘积。

## 核心结论（2030，相对无 AI 反事实）

| | Modest | Substantial | Extreme |
|---|---|---|---|
| GDP | +1.6% | +8.3% | +32.4%（增速 15.4%/年） |
| 劳动份额 | 59.4% | 56.1% | **45.2%**（基准 60%） |
| 认知工资 | +0.4% | −0.3% | **−11.5%** |
| 认知失业率 | 2.9% | 4.5% | **17.9%** |

- 平均工资跟随 m·d·a（生产率），不跟随位移；工资转负需要 "so-so automation"（Acemoglu-Restrepo）
- 创新效应刻意保守：半内生增长，RSI 被硬编码进外生 a_t，作者自认"创新效应是下界"
- 万人调查（10,980，Morning Consult 2026-08）：公众中位数预期 ≈ substantial 情景
- 作者护栏："scenarios are not predictions"；但参数皆可测量，"数据会告诉我们身处哪个情景"

## 判别点

- 三情景 2026 年中锚点重合（m=0.14 / d=0.10，Economic Index + BTOS 实测），**分化发生在 2027 年后**
- 2027-28 宏观数据显著偏离 2% 增长/3.8% 失业 → modest 排除
- ε（资本供给弹性）是暗中主角：ε=1 时 substantial 平均工资转负

## 与其他概念的关联

- 供给侧镜像 ↔ podcast-learning [[ai-capex-bubble-debate]]（庄明浩 CAPEX 泡沫之辩）
- 政治经济学版本 ↔ [[intelligence_curse]] 相关报告（2026-07-30，劳动份额下滑的激励机制版）
- 计量检验器 ↔ 曾鸣三阶段论（podcast-learning 2026-09-03）："第二阶段开场"≈ d_t logistic 爬升段
- 来源报告：[[Anthropic经济情景模型_深度解析_20260911]]
