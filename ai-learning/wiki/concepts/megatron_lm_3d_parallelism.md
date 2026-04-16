---
id: concept-megatron_lm_3d_parallelism
title: "Megatron-LM 与 3D 并行体系"
type: concept/distributed_training
domain: [ai-learning]
created: 2026-04-16
updated: 2026-04-16
sources: [Megatron_LM_大规模训练系统_深度解析_20260416]
---

# Megatron-LM 与 3D 并行体系

## 定义
Megatron-LM 是 NVIDIA 开发的大规模 LLM 训练框架，通过三种正交并行维度的组合（3D 并行）使得训练千亿参数模型成为可能：
- **数据并行（DP）**：不同 mini-batch 分发到不同 GPU 副本
- **张量并行（TP）**：单层内矩阵按列/行切分到多 GPU 同时计算
- **流水线并行（PP）**：不同层分配到不同 Pipeline Stage

## 核心机制

### 张量并行（TP）
- Column Parallel：矩阵按列切分，输入 broadcast，输出 concat
- Row Parallel：矩阵按行切分，输入已切分，输出 AllReduce
- 每层仅 2 次 AllReduce（前向+反向各1次）
- 必须在 NVLink 节点内使用（带宽需求高）

### 流水线并行（PP）- 1F1B 调度
- 每个 Pipeline Stage 持有部分 Transformer 层
- 1F1B（1 Forward + 1 Backward）：前向后立即执行可用反向，减少激活驻留
- 气泡率：(p-1)/(m+p-1)，m 为 micro-batch 数

### 序列并行（SP，v3引入）
- LayerNorm/Dropout 沿序列维度切分
- ReduceScatter 替代 TP 中的 AllReduce（通信量不变，激活显存降 t 倍）
- 配合选择性激活重算：激活显存降 5x，额外计算开销 < 3%

## 典型配置（GPT-3 175B, 1024 GPU）
```
DP=16, TP=8, PP=8
每节点 8 GPU，TP 在节点内（NVLink）
PP 跨节点（InfiniBand）
弱扩展效率：86.2%（32→1024 GPU）
```

## 历史谱系
- v1 (2019)：引入 TP，训练 8.3B 参数模型
- v2 (2021)：引入 PP (1F1B)，3D 并行，1024 GPU 训练 175B
- v3 (2022)：引入 SP + 选择性激活重算
- Megatron-DeepSpeed：与 ZeRO 结合，学界标配

## 关联概念
- ZeRO（DeepSpeed）：DP 方向的内存优化，与 TP/PP 互补
- FlashAttention：IO 优化内核，与 Megatron TP 深度集成
- MegaScale：Megatron 的工业万卡升级版本（ByteDance）

## 来源
- 报告：`reports/knowledge_reports/Megatron_LM_大规模训练系统_深度解析_20260416.md`
