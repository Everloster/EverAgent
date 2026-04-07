---
id: concept-self_supervised_learning
title: "自监督学习（Self-Supervised Learning）"
type: concept
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [17_mae_2022, 35_dinov2_2023, 36_videomae_2022, 13_word2vec_2013, 02_bert_2018]
status: active
---

# 自监督学习（Self-Supervised Learning）

## 一句话定义
不依赖人工标注，直接从数据自身的结构中构造监督信号（如遮蔽预测、对比学习、下一词预测）来学习通用表征的预训练范式。

## 三大典型范式
| 范式 | 代表方法 | 监督信号来源 | 模态 |
|------|---------|------------|------|
| **遮蔽重建（Masked Modeling）** | BERT、MAE、VideoMAE | 遮蔽部分输入，预测被遮蔽内容 | 文本 / 图像 / 视频 |
| **下一词预测（Autoregressive）** | Word2Vec、GPT 系列 | 用历史预测下一 token | 文本 |
| **对比学习 / 自蒸馏** | DINO、DINOv2、CLIP | 同一样本不同视图的特征应一致 | 图像 / 多模态 |

来源：02_bert_2018 / 17_mae_2022 / 13_word2vec_2013 / 35_dinov2_2023

## NLP 路线
- **Word2Vec (2013)**：Mikolov 等人，CBOW / Skip-gram，把"上下文预测中心词 / 中心词预测上下文"作为自监督信号，奠定词向量表示学习。来源：13_word2vec_2013
- **BERT (2018)**：双向 Transformer + Masked Language Modeling（MLM）+ Next Sentence Prediction（NSP），开启 NLP 自监督预训练黄金时代。来源：02_bert_2018
- **GPT 系列**：Decoder-Only + 下一词预测，从 GPT-1 至 GPT-3 证明自回归语言建模的 scaling 极限。来源：03_gpt3_2020

## 视觉路线：MAE
**核心主张**：用 **75% 高掩码率 + Patch 像素重建** 作为视觉自监督任务，训练出强大的 ViT 编码器。来源：17_mae_2022 §核心主张

**为什么直接搬 BERT 到视觉很难**（Kaiming He 三点观察）：
| 差异 | NLP | 视觉 |
|------|-----|------|
| 信息密度 | Token 高语义密度 | 像素冗余度极高 |
| 解码器 | 简单线性层即可 | 像素重建需更复杂解码器 |
| 基本单元 | 离散 token，天然可 mask | 连续信号，mask 策略不直观 |

来源：17_mae_2022 §Step 1

**关键设计**：不对称 Encoder-Decoder
- Encoder（重型 ViT-L/H）只处理 25% 可见 patch，省 4× 计算
- Decoder（轻型 Transformer）补全 mask token 后重建像素，仅预训练时使用
- 损失：仅对被遮蔽 patch 计算 MSE

来源：17_mae_2022 §Step 2

## 视觉路线：DINOv2
**核心突破**：纯自监督 ViT 首次在多视觉任务上超越 OpenCLIP 等弱监督方法，无需微调。来源：35_dinov2_2023 §一句话总结

**关键工程**：
- **数据**：从 12 亿张未筛选图像中自动构建 **LVD-142M**（1.42 亿张），无需人工标注或元数据。来源：35_dinov2_2023 §核心贡献
- **方法**：基于 DINO（2021）+ iBOT 的自蒸馏 + 系统性训练优化
- **意义**：证明纯图像模态也能产生"视觉基础模型"，对比 CLIP 不再依赖图文配对

来源：35_dinov2_2023 §背景与动机

## 在本项目的相关报告
- [MAE (2022) 深度分析](../../reports/paper_analyses/17_mae_2022.md)
- [DINOv2 (2023) 论文精读](../../reports/paper_analyses/35_dinov2_2023.md)
- [VideoMAE (2022) 论文精读](../../reports/paper_analyses/36_videomae_2022.md)
- [Word2Vec (2013) 论文精读](../../reports/paper_analyses/13_word2vec_2013.md)
- [BERT (2018) 论文精读](../../reports/paper_analyses/02_bert_2018.md)

## 跨域连接
- 自监督是 Transformer 大模型时代的"燃料供给"，与 scaling laws 协同 → concept: scaling_laws
- 与认知心理学的"无监督学习/感知学习"在抽象层面相通

## 开放问题
- 自监督预训练的"涌现能力"是否与监督训练有本质区别？
- 视觉自监督的最佳预训练任务尚无定论：MAE 重建 vs DINO 自蒸馏 vs 对比学习
- 多模态自监督（如何让图、文、音、视频共享同一表征空间）仍是开放挑战
