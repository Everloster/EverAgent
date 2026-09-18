---
id: concept-rl_scaling
title: "RL Scaling（强化学习扩展）"
type: concept
domain: [ai-learning]
created: 2026-09-17
updated: 2026-09-17
sources: [MiMo-V2.6公开RL训练直播_RL-Scaling三维度体系研究_20260917]
status: active
---

# RL Scaling（强化学习扩展）

## 一句话定义

把"模型与环境交互 → 产生经验 → 评价经验 → 学习经验"的 RL 循环整体工程化为一台可持续扩大规模的机器，检验 RL 能否像预训练一样沿算力轴可预测地变强。

## 三维度体系（小米 MiMo-V2.6 公开版，2026-09）

| 维度 | 内容 | 算力之外的瓶颈 |
|------|------|----------------|
| **训练计算量** | 每 Step ~2B token（1568 prompt × 16 rollout），Fully Async 流水线 | staleness 控制（train/infer KL 监控、IS 校正、max-staleness 阈值） |
| **环境与 Harness** | Multi-task Agentic RL，code/visual/general/cyber/chat 混入同一 run、不同 harness | 任务构造与环境设计（人类工程判断，决定信号质量） |
| **评分计算量（Grader Compute）** | test-case + rubric-based rewards + Agentic In-group Credit Assignment | rubric 质量（Gao et al.：固定 proxy 评分器被 overoptimize 后 gold reward 反降） |

## 关键判据

- **"RL Scaling 有效"的证据标准**：曲线形状（数百 step 后是否平台化）× 维度消融（哪一维贡献多少）× held-out 泛化 × 与头部差距的收敛速度。短期正向斜率 ≠ scaling 成立。
- **算力是三维度的共同放大器，但每个维度都有一个算力之外的人类判断瓶颈**（环境设计/rubric 质量/评测完整性）——"都是算力"的锐评漏掉了这一层。

## 行业位置

- 主张源头：OpenAI *Learning to Reason*（2024-09，RL 训练算力 + test-time 两条轴）；能力证据源头：DeepSeek R1-Zero（纯 RL 涌现）。
- 工程系统 2025 年成熟：AReaL / slime / verl / PipelineRL / PRIME-RL 全部解决异步与 staleness。
- 透明度先例：Prime Intellect INTELLECT-2（志愿者分布式 32B）；MiMo-V2.6 是**一线实验室生产级 RL run 直播**（成本计数器 + 逐 step 内部指标 + 故障公告）的首例，其成本计数器是行业首个公开 frontier 级 RL 成本数据点（~$3 万/小时，两天 ≈ DeepSeek-V3 预训练窄口径的 1/5）。

## 与什么相关

- [[scaling_laws]] — 预训练幂律是参照系；RL 侧尚无已验证 scaling law
- [[test_time_compute]] — o 系列/R1 流派表；RL 训练算力轴是 test-time 轴的训练端孪生
- [[rlhf]] — reward hacking / KL 约束；grader compute 是抗 hacking 能力的扩展
- [[agent_harness]] — harness 成为训练基础设施一等公民
- [[bitter_lesson]] — 通用方法+算力 vs 环境/奖励工程的人类杠杆

## 相关报告

- [《小米 MiMo-V2.6 公开直播 RL 训练》研究（2026-09-17）](../../reports/knowledge_reports/MiMo-V2.6公开RL训练直播_RL-Scaling三维度体系研究_20260917.md)

## 未解问题 / 追踪

- Agentic In-group Credit Assignment 具体算法（官方承诺数周内开源，回访核对该报告 §2.2 推测命中率）
- MiMo-V2.6 run 的奖励曲线长程形状：平台化拐点是否存在（2–4 周后复查直播页/后续技术报告）
- RL scaling 的成本-能力曲线 vs 预训练幂律：是否存在可外推的 RL 版 L(C)？
