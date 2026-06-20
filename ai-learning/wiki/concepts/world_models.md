# World Models（世界模型）

> 维护日期：2026-04-27 | 分类：机器人 / 多模态 / 仿真规划

---

## 概念定义

**世界模型** 是 AI 对环境状态、约束和动作后果的内部表征。它不仅识别当前场景，还要预测如果 agent 或机器人采取某个动作，环境接下来会如何变化。

在 MIT 2026 AI 趋势语境中，世界模型被视为训练机器人和 agent 理解真实环境的重要路径，尤其适合与视觉语言模型、仿真环境、强化学习和经典规划器结合。

## 判断标准

- **状态一致性**：物体、位置、身份和约束在时间上保持一致。
- **可交互性**：动作变化会引发环境状态变化。
- **因果预测**：不只是生成画面，而是预测动作后果。
- **可用于规划**：输出能被规划器、控制器或 agent 框架使用。
- **可迁移性**：仿真训练能提升现实任务表现。

## 关联报告

- [MIT 2026 AI 三条主线深度研究](../../reports/knowledge_reports/MIT_2026_AI_三条主线_深度研究报告.md)
- [生成模型演化全景](../../reports/knowledge_reports/生成模型演化全景_GAN_DDPM_LDM_DiT_20260416.md)
- [DiT 论文精读](../../reports/paper_analyses/27_dit_2022.md)
- [World Models / JEPA 路线深度报告](../../reports/knowledge_reports/World_Models_JEPA_路线深度报告_20260621.md) — 双路线对比，参数表，工业落地分支

## 关键派生概念

- **JEPA（Joint Embedding Predictive Architecture）**：在抽象表征空间预测而非像素重建
- **V-JEPA 2**：Meta 2025-06 发布的视频版 JEPA，1.2B 参数，1M+ 小时训练视频
- **AMI 实验室（Advanced Machine Intelligence）**：LeCun 2025-11 离 Meta 后 2026-01 创办，融资 €350M
- **Cosmos**：NVIDIA 2025-01 发布的物理 AI 世界基础模型，4B-14B 参数
- **GAIA-1/2**：Wayve 自动驾驶生成式世界模型
- **Genie 2/3**：DeepMind 交互式 3D 环境世界模型
