---
id: concept-jtb_knowledge
title: "JTB 知识定义（Justified True Belief）"
type: concept
domain: [philosophy-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [03_gettier_1963, knowledge/epistemology.md, 知识_跨时代比较]
status: active
---

# JTB 知识定义（Justified True Belief）

## 一句话定义
S 知道 P，当且仅当 P 为真、S 相信 P、S 有理由相信 P——即"有理由的真信念"。

## 核心原理
柏拉图《泰阿泰德》中提出的知识定义，2500 年来作为标准被广泛接受：

**S 知道 P ⟺**：
1. **真值条件（Truth）**：P 是真的
2. **信念条件（Belief）**：S 相信 P
3. **辩护条件（Justification）**：S 有理由相信 P

三个条件互相独立、共同充分。直觉支持：
- 没有真值（信了假的）→ 不是知识
- 没有信念（不相信真的）→ 不是知识
- 没有辩护（瞎猜碰对的）→ 不是知识

来源：knowledge/epistemology.md

## 1963 年盖提尔的反例
盖提尔仅 3 页论文构造出**满足 JTB 三条件但直觉上不是知识**的反例。

**反例一（Smith 与工作候选人）**：
- Smith 有充分理由相信 P：「Jones 将获工作，且 Jones 口袋有 10 枚硬币」（总裁告诉他 + 他亲数硬币）
- 推导 Q：「将获工作的人口袋有 10 枚硬币」
- **实际**：Smith 自己被录用（总裁说错了），且 Smith 口袋恰好有 10 枚硬币
- → Q 为真、Smith 相信 Q、Smith 对 Q 有辩护，但**Smith 不知道 Q**——Q 为真完全是巧合

**反例的共同结构**：
1. S 对**假命题** P 有充分辩护
2. S 从 P 正确推导出 Q
3. **恰好** Q 为真，但与 P 无关，纯属巧合
4. 结果：JTB 三条全满足，但直觉拒绝承认这是知识

来源：03_gettier_1963 §三

## 后盖提尔的四条主要应对
| 路线 | 代表 | 主张 | 难题 |
|------|------|------|------|
| 无虚假引理 | Harman | 辩护不依赖任何假前提 | 无假前提反例仍可构造 |
| 因果理论 | Goldman | 信念由事实因果引发 | 抽象知识、偏差因果链 |
| 可靠主义 | Goldman | 可靠认知过程产生知识 | 参考类问题 |
| 知识优先论 | Williamson | 知识不可分析，是原始概念 | 无法解释知识标准 |
| 美德认识论 | Sosa, Zagzebski | 认识论美德的正确运用 | 美德如何界定 |

来源：knowledge/epistemology.md

## 在本项目的相关报告
- [03_gettier_1963](../../reports/text_analyses/03_gettier_1963.md)
- [03_gettier_1963 (paper_analysis)](../../reports/paper_analyses/03_gettier_1963.md)
- [知识_跨时代比较](../../reports/concept_reports/知识_跨时代比较.md)

## 跨域连接
- [theory_of_forms](./theory_of_forms.md)：JTB 的本体论根源——知识的对象必须是不变的
- [socratic_method](./socratic_method.md)：苏格拉底对"知识"定义的反复追问是 JTB 的远祖
- [cogito_ergo_sum](./cogito_ergo_sum.md)：笛卡尔的 Cogito 是基础信念主义的现代起点，与 JTB 同属"辩护"问题
- ai-learning：LLM "知识地位"——若 GPT 答对题目源于统计巧合而非理解，是否构成认识论运气？

## 被引用于
- [theory_of_forms](./theory_of_forms.md)
- [socratic_method](./socratic_method.md)
- [cogito_ergo_sum](./cogito_ergo_sum.md)
- entities/[plato](../entities/plato.md)
- entities/[gettier_edmund](../entities/gettier_edmund.md)

## 开放问题
- 是否存在能抵御所有盖提尔型反例的修补版本？
- 知识是否真的是一个分析性概念，还是 Williamson 所说的原始概念？
