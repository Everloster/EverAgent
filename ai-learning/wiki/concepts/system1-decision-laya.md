# System 1 决策模型 / Laya（非自回归校准决策）

> 概念页 · 2026-09-22 建立 · 2026-10-09 更新（v0.4.1）· 来源：[Laya 深度解析报告](../../reports/knowledge_reports/Laya_System1决策模型_深度解析_20260922.md)（含 10-09 续篇）+ [github-trending-analyzer 研究报告](../../../github-trending-analyzer/reports/research_NandhaKishorM_laya.md)

## 一句话
不生成文本、一次前向输出「choice/score/noul」三原语及数学校准概率的 421M 模型（ModernBERT-large）；本机 MPS 实测 4 问 34.5ms / 1 问 10.7ms。Jev（TypeSafe 闭源，$200M 估值）的开源 Apache-2.0 对标，API 兼容。

## 要点
- **攻击点**：用 8B-70B LLM 做反射式决策（路由/分级/布尔判断）是浪费——慢、贵、要解析、置信度无校准
- **RLCD 实相（10-09 源码修正）**：GRPO 项在 typed-decisions 分割零增益（#741），校准主要靠事后分桶温度拟合（桶<2000 样本回退标量，clamp [0.5,5.0]；ECE 0.466→0.081）——「RL 训出校准」是叙事不是已验证增益
- **act/escalate 头**：成本矩阵（对+1/错-3/升级-0.5）→ 自动学出置信度>62.5% 才行动；「何时不信自己」内置
- **三 checkpoint × Router**：english（421M/512ctx）、multilingual（322M/mmBERT/1024→8192）、typed-decisions（微调款）；纯 Python 文字检测 <0.5ms 分流——English 款对非拉丁文字「高自信全错」（Khmer 0.000@0.952conf），必须前置路由
- **硬边界**：基座零样本低于 majority 基线（0.362 vs 0.461）——**不微调不可用**；>20 选项坍塌（每选项保底4 tokens，head 挤爆）；否定句不安全（#377）；512-1024 ctx vs Jev 32k
- **不适合**：需解释的决策、System 2 任务、回复质量类（58%）、零样本直替 Jev/LLM

## 行业坐标（10-09）
- Jev 命名自 **Jevons 悖论**（便宜→用量暴增）；TypeSafe = OpenAI RLHF 老将 Diogo Almeida 2024 创立，$40M DCVC 种子
- **OpenAI 10-06 推 Decisions API（GPT-6 Luna）跟进**——「专用判别小模型 vs 通用大模型包装」路线之争开打
- HN 论战教学：「架构新颖性」≠「产品成立性」；Laya 前者近零（BERT+头+适当评分规则皆已知件），后者做对 API/诚实基准/生态卡位
- 生态位：有标注数据可微调的高频决策层 + 隐私本地推理 + 预算敏感 pipeline

## 关联
- [[Agent Harness 学习计划]] 的路由/门控层实物样本（置信度门控设计模式）
- [[model_calibration]]：温度缩放/ECE 的工业级实例；proper scoring rules 组合（log+spherical+RPS，复合保持严格适当）
- [[bitter_lesson]] 的经济学倒装：Jevons 悖论 vs 算力扩展——廉价决策智能催生海量调用
- 李继刚「服务裹着能力」的自动化形态；colibrì=省显存 vs Laya=省 token/延迟
- 双仓场景：EverAgent 播客段落分类/trending 过滤；infra 告警分级+升级门控（本地推理零外流）

## 未解
- OpenAI Decisions API 能力/定价边界——若生成式大模型做到 Jev 级速度，专用小模型退守「本地/隐私/边缘」
- #741 只测一个分割：soft-ce vs rlcd 在其他分割是否有差
- 高基数 shortlist 路线的误差叠加无对照数据（Banking77 0.425 修复后数字缺失）
- 自定义选项集的校准衰减（落地前必测 reliability diagram；桶级需 ≥2000 样本重拟合）
