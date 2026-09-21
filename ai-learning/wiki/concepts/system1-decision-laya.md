# System 1 决策模型 / Laya（非自回归校准决策）

> 概念页 · 2026-09-22 · 来源：[Laya 深度解析报告](../../reports/knowledge_reports/Laya_System1决策模型_深度解析_20260922.md)

## 一句话
不生成文本、一次前向输出「choice/score/noul」三原语及数学校准概率的 421M 模型（ModernBERT-large + RLCD）；本机 MPS 实测 4 问 34.5ms / 1 问 10.7ms。

## 要点
- **攻击点**：用 8B-70B LLM 做反射式决策（路由/分级/布尔判断）是浪费——慢、贵、要解析、置信度无校准
- **RLCD**：严格适当评分规则（log/球面/RPS）作 RL 奖励——只有报告诚实概率才能得最高分；G=8 零和高斯探索 + 组均值基线（GRPO 风格）
- **act/escalate 头**：成本矩阵（对+1/错-3/升级-0.5）→ 自动学出置信度>62.5% 才行动；「何时不信自己」内置
- **校准**：置信度=1-归一化熵；选择性自动化（top-50% 置信）→ 92.2% 精度
- **实测警告**：choice≥11 选项温度越界被钳制，该桶 confidence 未校准；中文需 multilingual checkpoint（路由实测 3/3）
- **不适合**：需解释的决策、System 2 任务、回复质量类（58%）

## 关联
- [[Agent Harness 学习计划]] 的路由/门控层实物样本（置信度门控设计模式）
- 李继刚「服务裹着能力」的自动化形态；colibrì=省显存 vs Laya=省 token/延迟
- 双仓场景：EverAgent 播客段落分类/trending 过滤；infra 告警分级+升级门控（本地推理零外流）

## 未解
- 自定义选项集上的校准衰减（落地前必测 reliability diagram）
- RLCD vs 后处理校准（temperature scaling）的增量——无 ablation
