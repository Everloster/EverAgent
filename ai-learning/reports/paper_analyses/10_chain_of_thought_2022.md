---
title: "Chain-of-Thought (2022) 论文精读"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-03-25"
---

# Chain-of-Thought Prompting 论文分析报告

> 生成日期：2026-03-25 | 使用「论文7步分析框架」
> 对应路径：Phase 3 大模型与NLP → 提示工程与推理能力

---

## 📋 基本信息卡片

```
论文标题：Chain-of-Thought Prompting Elicits Reasoning in Large Language Models
作者：Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter,
      Fei Xia, Ed Chi, Quoc V. Le, Denny Zhou
机构：Google Research / Google Brain
发表年份：2022
发表场所：NeurIPS 2022
Arxiv ID：2201.11903
引用量：~20,000+（截至2025年，AI提示工程领域引用最高之一）
重要性评级：⭐⭐⭐⭐⭐（开创"推理链"范式，影响至今）
```

---

## 🎯 一句话总结

> 在 few-shot 示例中加入中间推理步骤（"思维链"），可以显著激发大语言模型的多步推理能力，而这种能力在小模型上几乎不存在，呈现出典型的涌现现象。

---

## 🌍 背景与动机（WHY）

### 问题是什么？

GPT-3 等大模型在简单问答上表现出色，但面对**需要多步推理**的任务时表现很差：

- 数学应用题（小学数学 GSM8K 准确率不足 10%）
- 常识推理（需要多跳关联的问题）
- 符号推理（字符串拼接、硬币翻转等）

根本原因：标准的 few-shot prompting 只给出「问题 → 答案」对，模型直接跳到答案，中间没有推理过程可以学习或利用。

### 之前怎么做的？

| 方法 | 做法 | 局限 |
|------|------|------|
| 标准 Few-shot | 提供 (问题, 答案) 示例 | 跳过推理，复杂问题失败 |
| 微调（Fine-tuning） | 在推理数据集上训练 | 需要大量标注数据，成本高 |
| 程序合成 | 让模型生成代码再执行 | 只适合形式化问题 |

### 为什么值得研究？

人类解决复杂问题的方式是**分步思考**——把大问题拆解为小步骤。如果能让 LLM 也"写出思考过程"，或许就能激活其隐含的推理能力，且无需任何参数更新。

---

## 💡 核心贡献（WHAT）

1. **提出思维链提示（Chain-of-Thought, CoT）**：在 few-shot 示例中，在问题和答案之间插入自然语言推理步骤，引导模型生成类似的推理过程。

2. **发现涌现现象**：CoT 的效果只在参数量约 ≥100B 的模型中出现；小模型使用 CoT 后反而会下降。这证明 CoT 是一种涌现能力（Emergent Ability）。

3. **跨任务普适性**：在算术推理、常识推理、符号推理三类任务上均大幅提升，表明 CoT 不是特定任务的技巧，而是通用推理范式。

4. **Zero-shot CoT 的启发**：论文末尾实验证明，仅需加一句 "Let's think step by step" 也能部分激活推理（后续被 Kojima et al. 2022 正式发表）。

---

## 🔧 技术方法（HOW）

### 核心思路：在示例中加入推理轨迹

**标准 Few-shot Prompt**：
```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3. How many tennis balls does he have now?
A: 11
```

**Chain-of-Thought Prompt**：
```
Q: Roger has 5 tennis balls. He buys 2 more cans of 3. How many tennis balls does he have now?
A: Roger started with 5 balls. 2 cans × 3 balls = 6 new balls. 5 + 6 = 11. The answer is 11.
```

只需要将 few-shot 示例中的答案替换为「推理过程 + 答案」，无需任何梯度更新。

### 三类任务

| 任务类别 | 代表数据集 | 典型问题类型 |
|---------|-----------|------------|
| 算术推理 | GSM8K, MATH | 小学/中学数学应用题 |
| 常识推理 | CommonsenseQA, StrategyQA | 多跳常识问答 |
| 符号推理 | 硬币翻转、字母拼接 | 纯形式化符号操作 |

### 关键设计细节

- **示例数量**：通常使用 8 个 few-shot 示例
- **推理步骤写法**：自然语言，逐步演算
- **最终答案提取**：要求模型在推理后明确给出答案（如 "The answer is..."）
- **模型**：主要在 PaLM (540B)、GPT-3 (175B)、LaMDA (137B) 上实验

---

## 📊 实验与结果

### 核心结果

**算术推理（GSM8K，小学数学）**：

| 模型 | 标准 Few-shot | Chain-of-Thought |
|------|------------|-----------------|
| GPT-3 175B | 17.9% | 46.9% |
| PaLM 540B | 17.9% | **58.1%** |
| （人类） | — | 87% |

**涌现曲线**（重要发现）：
- 模型 ≤ 10B 参数：CoT 提升约为 0，甚至有害
- 模型 100B-137B：小幅提升
- 模型 ≥ 540B（PaLM）：大幅飞跃

### 消融实验

论文测试了多种对照变体：
- **方程式替代自然语言**：效果差（模型不擅长直接生成方程）
- **只给出中间结果（无推理）**：效果差
- **推理在答案后**：效果差（必须在答案前推理）

结论：**自然语言推理轨迹 + 出现在答案之前** 是 CoT 有效的必要条件。

---

## 💪 论文的优势

- **无需微调，零成本激活能力**：只需修改 prompt，不改变模型参数
- **可解释性强**：推理链让人能看到模型"怎么想的"，便于调试错误
- **普适性**：在多类推理任务、多个大模型上均有效
- **开创性**：首次系统证明"思考过程"对 LLM 推理的价值

---

## ⚠️ 论文的局限

- **仅在大模型上有效**：≤10B 参数模型几乎无效，限制了应用范围
- **推理链标注成本**：需要人工编写高质量的 CoT 示例（尽管数量不多）
- **错误会传播**：中间推理步骤出错会导致最终答案错误（"幻觉链"问题）
- **上限有限**：在最难的数学题（MATH dataset）上，即使 PaLM 540B + CoT 也只有约 8%，远低于人类

---

## 🌱 影响与后续工作

CoT 开创了「提示工程即能力工程」的新范式，催生了大量后续研究：

| 论文 | 贡献 |
|------|------|
| Zero-shot CoT (Kojima 2022) | "Let's think step by step" 一句话激活推理 |
| Self-Consistency (Wang 2023) | 多次采样取多数投票，进一步提升准确率 |
| Tree of Thoughts (Yao 2023) | 将线性链扩展为树状搜索 |
| ReAct (Yao 2022) | 将推理链与工具调用结合（见 #17） |
| Program of Thoughts (Chen 2022) | 将推理链替换为可执行代码 |
| OpenAI o1 / DeepSeek-R1 | 将 CoT 内化为模型的默认思考过程（训练时） |

**历史地位**：CoT 是从「大模型只是文本补全」到「大模型会推理」这一认知转变的直接证据，也是 OpenAI o1「思维链训练」的思想先驱。

---

## 🧩 与其他论文的关系

```
GPT-3 (2020, #03)         ──→  CoT Prompting (2022, 本文)  ──→  ReAct (2022, #17)
[大模型 few-shot 能力]              [激活推理能力]                 [推理+行动]
                                        │
                                        ↓
                               Self-Consistency (2023)
                               Tree of Thoughts (2023)
                               OpenAI o1 / R1 (2024)
```

---

## 🤔 个人思考与问题

1. **为什么 CoT 只在大模型上有效？** 可能是因为大模型在预训练阶段见过大量"解题过程"文本，已经具备了按步推理的隐含能力，CoT prompt 只是"激活"了这种能力；而小模型根本没有习得这种能力，无论怎么提示都无法激活。

2. **CoT 到底是在"推理"还是在"搜索训练数据"？** 一个开放问题：模型是真的在执行逻辑推理，还是在检索/拼接训练时见过的类似推理模式？这个问题至今没有定论。

3. **实际工程中如何写好 CoT 示例？** 示例的质量、推理步骤的粒度对效果影响很大，这是工程实践中需要反复调试的地方。

---

## 📚 延伸阅读推荐

1. **Zero-shot CoT**（Kojima et al., 2022）— "Let's think step by step" 的系统研究
2. **Self-Consistency**（Wang et al., 2023）— CoT 的采样集成改进
3. **ReAct**（Yao et al., 2022，本项目 #17）— CoT 与工具使用的结合
4. **Tree of Thoughts**（Yao et al., 2023）— 将线性 CoT 扩展为树搜索
5. **OpenAI o1 技术报告**（2024）— CoT 内化进训练过程的工程实践
