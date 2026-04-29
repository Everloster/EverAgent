---
id: concept-knowledge_distillation
title: "Knowledge Distillation"
type: concept
domain: [ai-learning]
created: 2026-04-25
updated: 2026-04-25
sources: [42_distilling_2015]
---

# Knowledge Distillation

## 定义

知识蒸馏是一种教师-学生训练方法：先训练一个性能强但部署成本高的 cumbersome model，再用它输出的软目标训练更小、更易部署的 distilled model。

在 Hinton / Vinyals / Dean (2015) 中，知识不是参数本身，而是模型从输入向量到输出概率分布的映射。

## 核心机制

- 教师模型使用高温 softmax 生成 soft targets。
- 学生模型在相同温度下拟合教师输出分布。
- 如果 transfer set 有真实标签，学生同时学习 hard-label 交叉熵。
- 训练完成后，学生推理时把温度恢复为 1。
- soft-target loss 的梯度随 `1/T^2` 缩放，因此联合硬标签训练时需要乘以 `T^2`。

## 关键公式

```text
q_i = exp(z_i / T) / Σ_j exp(z_j / T)
```

`T = 1` 是普通 softmax；`T > 1` 会产生更平滑的类别分布，让错误类别之间的相对概率参与训练。

在高温极限下，蒸馏近似等价于匹配教师与学生 logits 的平方差，前提是每个样本的 logits 分别零均值化。

## 论文中的关键证据

- MNIST：普通小模型 `146` 个测试错误；用温度 `20` 的 soft targets 蒸馏后降到 `74` 个错误；大教师模型为 `67` 个错误。
- MNIST 缺类实验：transfer set 删除所有 `3` 后，经 bias 修正，学生在测试集 `3` 上只错 `14/1010`。
- ASR：10 模型 ensemble 的 WER 为 `10.7%`，蒸馏单模型也达到 `10.7%`，baseline 为 `10.9%`。
- Soft targets 正则：只用 `3%` 语音训练数据时，hard labels 测试 frame accuracy 为 `44.5%`，soft targets 为 `57.0%`。

## 工程注意

- 温度是容量相关超参数，小学生模型不一定适合极高温。
- 软标签不是标签平滑，核心价值在非正确类别之间的相对概率。
- 蒸馏继承教师的泛化结构，也可能继承教师偏差。
- 分类蒸馏不自动解决现代 LLM 的长文本、推理链和工具使用行为蒸馏。

## 关联报告

- [Distilling the Knowledge in a Neural Network](../../reports/paper_analyses/42_distilling_2015.md)
- [DINOv2 论文精读](../../reports/paper_analyses/35_dinov2_2023.md)
- [EVA-02 论文精读](../../reports/paper_analyses/41_eva02_2023.md)
