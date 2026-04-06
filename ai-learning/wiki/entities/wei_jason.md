---
id: entity-wei_jason
title: "Jason Wei"
type: entity/person
domain: [ai-learning]
created: 2026-04-06
updated: 2026-04-06
sources: [10_chain_of_thought_2022]
---

# Jason Wei

## 身份
Google Research / Google Brain 研究员，《Chain-of-Thought Prompting Elicits Reasoning in Large Language Models》（NeurIPS 2022）第一作者，Chain-of-Thought 提示范式的提出者。

## 核心贡献
- **Chain-of-Thought Prompting（2022）**：提出在 few-shot 示例中插入中间推理步骤，激发大语言模型的多步推理能力。该方法无需微调，仅通过修改 prompt 即可大幅提升推理任务准确率。来源：10_chain_of_thought_2022 核心贡献
- **涌现现象系统研究**：系统记录了 CoT 效果在约 ≥100B 参数才显现的涌现特征——小模型使用 CoT 后性能反而下降，大模型（PaLM 540B）在 GSM8K 上从 17.9% 跃升至 58.1%。来源：10_chain_of_thought_2022 实验结果

## 关键数据
- GSM8K（小学数学）：GPT-3 175B 使用 CoT 后，准确率从 17.9% 升至 46.9%；PaLM 540B 从 17.9% 升至 58.1%（标准 few-shot vs CoT prompting）。来源：10_chain_of_thought_2022 实验结果
- 论文引用量约 20,000+（截至 2025 年），是 AI 提示工程领域引用最高的论文之一。来源：10_chain_of_thought_2022 基本信息卡片

## 在本项目的相关报告
- [Chain-of-Thought 2022 论文精读](../../reports/paper_analyses/10_chain_of_thought_2022.md)

## 与其他人物/机构的关系
- 合著者包括 Xuezhi Wang、Dale Schuurmans、Maarten Bosma、Brian Ichter、Fei Xia、Ed Chi、Quoc V. Le、Denny Zhou，均来自 Google Research / Google Brain
- CoT 工作直接启发了 Zero-shot CoT（Kojima 2022）、Self-Consistency（Wang 2023）、Tree of Thoughts（Yao 2023）等后续研究
- OpenAI o1 和 DeepSeek-R1 将 CoT 内化为模型的训练目标，是 Wei 工作的最终延伸
