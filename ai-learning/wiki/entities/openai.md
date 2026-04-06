---
id: entity-openai
title: "OpenAI"
type: entity/org
domain: [ai-learning]
created: 2026-04-06
updated: 2026-04-06
sources: [AI关键人物图谱, 03_gpt3_2020, 04_instructgpt_2022, 10_chain_of_thought_2022]
---

# OpenAI

## 身份
2015 年成立的 AI 研究公司，总部位于旧金山湾区。以 GPT 系列、InstructGPT、ChatGPT 等产品引领生成式 AI 商业化浪潮。

## 关键人物与组织演变
- **联合创始人**：Elon Musk（2018 年离开董事会）、Sam Altman（CEO）、Ilya Sutskever（首席科学家，2024 年离职创立 SSI）
- **2019 年**：引入微软战略投资（10 亿美元起，后续扩大至百亿级规模）
- **2021 年分裂**：Dario Amuodei、Tom Brown 等约 11 人集体离职，创立 Anthropic
- **2023 年 11 月**：Sam Altman 被董事会短暂解雇（5 天后复职），Ilya Sutskever 参与投票后公开表示后悔

来源：AI关键人物图谱 §二·五

## 核心产品与技术里程碑
- **GPT-3（2020）**：175B 参数，300B tokens 训练，首次大规模证明 few-shot 涌现能力；计算量约 3×10²³ FLOPs。论文第一作者 Tom Brown。来源：Scaling_Laws_深度解析 §应用场景1
- **InstructGPT（2022）**：三阶段 RLHF 训练（SFT → 奖励模型 → PPO），使用约 13K SFT 数据对，首次将人类偏好对齐大规模工程化，是 ChatGPT 的直接前身。来源：RLHF_深度解析 §阶段详解
- **ChatGPT（2022）**：引爆全球 AI 应用热潮，是快速商业化路线的代表产品
- **o1 系列**：将 Chain-of-Thought 内化为训练目标，推理时间 Scaling 的代表。来源：10_chain_of_thought_2022 影响

## 技术路线特征
OpenAI 代表"快速商业化"哲学，与 Anthropic 的"安全研究优先"形成对立。Chinchilla 论文（DeepMind）指出 GPT-3 属于欠训练模型（参数大、数据相对少），在相同计算预算下 Chinchilla 70B 在所有基准上均优于 GPT-3。来源：Scaling_Laws_深度解析 §应用场景2

## 在本项目的相关报告
- [GPT-3 2020 论文精读](../../reports/paper_analyses/03_gpt3_2020.md)
- [InstructGPT 2022 论文精读](../../reports/paper_analyses/04_instructgpt_2022.md)
- [Scaling Laws 深度解析](../../reports/knowledge_reports/Scaling_Laws_深度解析.md)
- [RLHF 深度解析](../../reports/knowledge_reports/RLHF_深度解析.md)

## 与其他人物/机构的关系
- 微软深度绑定，Azure 是主要算力供应商
- Anthropic 是其分裂产物，代表对立的安全优先路线
- 与 Google DeepMind 为主要竞争对手
- Łukasz Kaiser（Transformer 合著者）曾于 2019 年加入 OpenAI
