---
id: entity-shazeer_noam
title: "Noam Shazeer"
type: entity/person
domain: [ai-learning]
created: 2026-04-06
updated: 2026-04-06
sources: [AI关键人物图谱, 01_transformer_2017, 21_moe_2017, MoE_混合专家_深度解析_20260406]
---

# Noam Shazeer

## 身份
Google Brain 研究员（2017 年前后），《Attention Is All You Need》（2017）共同作者，《Outrageously Large Neural Networks》（2017）第一作者，Character.AI 联合创始人兼 CEO。活跃于 2010 年代至今。

## 核心贡献
- **Transformer 共同作者（2017）**：与 Ashish Vaswani 等七人共同发表《Attention Is All You Need》，奠定现代 LLM 的架构基础，论文引用量超 10 万次。来源：01_transformer_2017 基本信息卡片；AI关键人物图谱 §一
- **MoE 奠基：Noisy Top-K Gating（2017）**：作为《Outrageously Large Neural Networks》第一作者，提出 Noisy Top-K 门控机制、负载均衡双损失（Importance Loss + Load Loss），首次将混合专家架构扩展至 137 亿参数规模，在多个大规模语言建模和机器翻译基准上超越 SOTA，计算成本仅为基线的 6%-40%。来源：21_moe_2017 基本信息卡片；MoE_混合专家_深度解析_20260406 §技术细节
- **Multi-Query Attention（2019）**：提出 MQA，所有 Query 头共享同一组 Key/Value，KV Cache 显存减少 h 倍，成为现代高效推理的关键组件。来源：KV_Cache_深度解析_20260330 §变体
- **LaMDA/Bard 早期贡献**：在 Google Brain 期间参与了对话大模型 LaMDA 的早期工作。来源：AI关键人物图谱 §一

## Noisy Top-K Gating 关键设计
- 加入可学习高斯噪声打破专家对称性，防止专家崩塌
- Importance Loss 和 Load Loss 两个辅助损失（系数 w=0.1）约束门控均衡
- 验证规模：137B 参数，1 Billion Word / 100 Billion Word / WMT'14 基准

来源：21_moe_2017 核心贡献；MoE_混合专家_深度解析_20260406 §数学描述

## 在本项目的相关报告
- [Transformer 2017 论文精读](../../reports/paper_analyses/01_transformer_2017.md)
- [MoE 奠基论文 2017 精读](../../reports/paper_analyses/21_moe_2017.md)
- [MoE 混合专家深度解析](../../reports/knowledge_reports/MoE_混合专家_深度解析_20260406.md)
- [KV Cache 深度解析](../../reports/knowledge_reports/KV_Cache_深度解析_20260330.md)

## 与其他人物/机构的关系
- 与 Ashish Vaswani 等同为 Transformer 作者，是 Google Brain 输出的核心研究者
- 2017 年 MoE 论文合著者包括 Geoffrey Hinton 和 Jeff Dean，体现 Google Brain 内部交叉合作
- 离开 Google 后创立 Character.AI，专注于 AI 对话角色场景的商业化
- Shazeer 2017 的 MoE 工作是 Switch Transformer（Google 2021）、Mixtral 8x7B（Mistral 2023）和 DeepSeek-V3（2024）的直接技术前驱
