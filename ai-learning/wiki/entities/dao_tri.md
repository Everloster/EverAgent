---
id: entity-dao_tri
title: "Tri Dao"
type: entity/person
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [18_flashattention_2022]
---

# Tri Dao

## 身份
FlashAttention（NeurIPS 2022）的第一作者。论文合著者包括 Daniel Y. Fu、Stefano Ermon、Atri Rudra、Christopher Ré。来源：18_flashattention_2022 基本信息卡片

## 核心贡献
- **FlashAttention（IO-aware Exact Attention）**：从 GPU 内存层级（HBM ↔ SRAM）出发重排注意力计算流程，通过 tiling 与 online softmax 在不物化完整 attention 矩阵的前提下保持精确计算，显著降低显存占用并提升长序列训练吞吐。来源：18_flashattention_2022 §一句话总结 / §技术方案
- **改变了大模型工程优化的视角**：让 Transformer 性能优化的关注点从单纯的 FLOPs / O(n²) 复杂度转向 GPU memory hierarchy。来源：18_flashattention_2022 §证据与论证
- **FlashAttention-2 / 3 等后续工作**：推动了 PagedAttention、KV Cache 优化等整条 LLM 推理效率路线。来源：18_flashattention_2022 §影响力分析

## 在本项目的相关报告
- [FlashAttention (2022) 深度分析](../../reports/paper_analyses/18_flashattention_2022.md)

## 与其他人物/机构的关系
- 论文合著者 Christopher Ré 是 Stanford DAWN 实验室负责人，Tri Dao 在该实验室完成博士工作。来源：18_flashattention_2022 基本信息卡片
- FlashAttention 已成为现代 LLM 训练栈（PyTorch、Megatron-LM、DeepSpeed 等）的标准组件之一。来源：18_flashattention_2022 §影响力分析
