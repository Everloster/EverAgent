---
id: entity-vaswani_ashish
title: "Ashish Vaswani 及 Transformer 合著者团队"
type: entity/person
domain: [ai-learning]
created: 2026-04-06
updated: 2026-04-06
sources: [AI关键人物图谱, 01_transformer_2017]
---

# Ashish Vaswani 及 Transformer 合著者团队

## 身份
Ashish Vaswani 是《Attention Is All You Need》（NeurIPS 2017）的第一作者，论文作者共八位，均来自 Google Brain / Google Research，发表时间 2017 年。该论文引用量超过 10 万次，是 AI 史上被引最多的论文之一。来源：01_transformer_2017 基本信息卡片

## 八位作者去向

| 作者 | 后续去向 |
|------|---------|
| Ashish Vaswani | Google → Adept AI 联合创始人（后离开） |
| Noam Shazeer | Google Brain → Character.AI 联合创始人/CEO；LaMDA/Bard 早期贡献 |
| Niki Parmar | → Adept AI 联合创始人 |
| Jakob Uszkoreit | → Adept AI 联合创始人 |
| Llion Jones | → Sakana AI 联合创始人（2023，与 David Ha 共创） |
| Aidan Gomez | → Cohere CEO/联合创始人（2019，企业 LLM 领域） |
| Łukasz Kaiser | → OpenAI（2019），后离开回 Google Research |
| Illia Polosukhin | → NEAR Protocol（区块链 + AI） |

来源：AI关键人物图谱 §一

## 核心贡献
- **Transformer 架构**：提出完全基于自注意力的编码器-解码器结构，彻底取代 RNN/LSTM，成为 GPT、BERT、Claude 等现代 LLM 的底层基础。来源：01_transformer_2017 核心贡献
- **WMT 2014 英德翻译 28.4 BLEU**：在当时超过所有已有模型（之前最好为 26.4 BLEU），训练仅用 8 个 P100 GPU 跑 12 小时。来源：01_transformer_2017 实验结果
- **多头注意力**：并行 h=8 个注意力头，每个头关注不同语义子空间，弥补单头注意力表达能力不足的问题。来源：01_transformer_2017 技术方法

## 在本项目的相关报告
- [Transformer 2017 论文精读](../../reports/paper_analyses/01_transformer_2017.md)
- [AI 关键人物图谱](../../reports/knowledge_reports/AI关键人物图谱.md)

## 与其他人物/机构的关系
- 八人来自 Google Brain / Google Research；论文发表后 7 人离开 Google 创业，体现"大公司孵化、创业公司收割"规律
- Noam Shazeer 同年（2017）参与 MoE 奠基论文，是 Transformer 和 MoE 两条主线的交汇点
- Vaswani 团队的工作直接催生了 BERT（Google）、GPT 系列（OpenAI）、ViT（Google）等后续论文
