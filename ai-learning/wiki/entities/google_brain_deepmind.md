---
id: entity-google_brain_deepmind
title: "Google Brain / Google DeepMind"
type: entity/org
domain: [ai-learning]
created: 2026-04-06
updated: 2026-04-25
sources: [AI关键人物图谱, 01_transformer_2017, 10_chain_of_thought_2022, 21_moe_2017, 42_distilling_2015, 43_alphago_zero_2017, Scaling_Laws_深度解析]
---

# Google Brain / Google DeepMind

## 身份
Google Brain 于 2011 年由 Jeff Dean、Greg Corrado、Andrew Ng 创立；DeepMind 于 2010 年由 Demis Hassabis 创立，2014 年被 Google 收购。2023 年 4 月，两者合并为 Google DeepMind，由 Demis Hassabis 担任 CEO。来源：AI关键人物图谱 §三

## 关键人物
- **Jeff Dean**（Google Brain 灵魂人物）：设计 TPU 架构，推动 Google Brain 成立，合并后任 Google DeepMind 首席科学家。来源：AI关键人物图谱 §三
- **Demis Hassabis**（DeepMind CEO）：游戏开发者出身（《主题医院》），神经科学 PhD，主导 AlphaGo → AlphaFold → Gemini 三次里程碑，2024 年因 AlphaFold 获诺贝尔化学奖。来源：AI关键人物图谱 §三
- **Oriol Vinyals**（DeepMind）：Seq2Seq 模型提出者，AlphaStar 核心，参与 Gemini 多模态研究。来源：AI关键人物图谱 §三
- **David Silver**（DeepMind）：AlphaZero 第一作者，代表 DeepMind 自我对弈强化学习与游戏 AI 路线。来源：43_alphago_zero_2017

## 核心技术贡献
- **Transformer（2017）**：Google Brain / Google Research 的 8 位工程师发表《Attention Is All You Need》，引用量超 10 万次，是 AI 史上影响力最大的论文之一。论文第一作者 Ashish Vaswani。来源：01_transformer_2017 基本信息卡片
- **知识蒸馏（2015）**：Hinton、Vinyals、Dean 在 Google Inc. 发表《Distilling the Knowledge in a Neural Network》，将高温 softmax 软标签与教师-学生训练确立为模型压缩范式。来源：42_distilling_2015
- **AlphaZero（2017）**：DeepMind 将 AlphaGo Zero 的自我对弈强化学习推广到国际象棋、日本将棋和围棋；对 Stockfish 100局结果为 `28` 胜 `72` 和 `0` 负。来源：43_alphago_zero_2017
- **MoE 奠基（2017）**：《Outrageously Large Neural Networks》，第一作者 Noam Shazeer，合著者含 Geoffrey Hinton 和 Jeff Dean，在 Google Brain 完成。来源：21_moe_2017 基本信息卡片
- **Chain-of-Thought（2022）**：Jason Wei 等人在 Google Research / Google Brain 提出 CoT Prompting，引用量约 20,000+。来源：10_chain_of_thought_2022 基本信息卡片
- **Chinchilla（2022）**：DeepMind Hoffmann 等人通过 400+ 模型规模实验修正 Kaplan Scaling Laws，提出"最优数据量 ≈ 20 × 参数量"，成为业界新标准，并指出 GPT-3 严重欠训练。来源：Scaling_Laws_深度解析 §Chinchilla修正
- **AlphaFold**：DeepMind 的蛋白质结构预测系统，Demis Hassabis 因此获 2024 年诺贝尔化学奖

## 在本项目的相关报告
- [知识蒸馏 2015 论文精读](../../reports/paper_analyses/42_distilling_2015.md)
- [AlphaZero 2017 论文精读](../../reports/paper_analyses/43_alphago_zero_2017.md)
- [Transformer 2017 论文精读](../../reports/paper_analyses/01_transformer_2017.md)
- [MoE 奠基论文 2017 精读](../../reports/paper_analyses/21_moe_2017.md)
- [Chain-of-Thought 2022 论文精读](../../reports/paper_analyses/10_chain_of_thought_2022.md)
- [Scaling Laws 深度解析](../../reports/knowledge_reports/Scaling_Laws_深度解析.md)

## 与其他人物/机构的关系
- Transformer 8 位作者几乎全部离开 Google 创业，体现"大公司孵化、创业公司收割"规律
- Google DeepMind 是当前对抗 OpenAI + Anthropic 格局的主力
- Jeff Dean 与 Shazeer、Hinton 合著 MoE 奠基论文，体现 Google Brain 的交叉合作文化
- Gemini 系列是当前 Google DeepMind 对抗 GPT-4 的核心产品线
