---
id: concept-sparse_activation
title: "稀疏激活（Sparse Activation / Conditional Computation）"
type: concept
domain: [ai-learning]
created: 2026-04-07
updated: 2026-04-07
sources: [21_moe_2017, MoE_混合专家_深度解析_20260406]
status: active
---

# 稀疏激活 / 条件计算

## 一句话定义
对每个输入只激活模型的一部分参数（而非全部），从而在参数量大幅扩张的同时保持计算量基本不变的设计哲学。

## 与 Dense 模型的根本区别
- **Dense 模型**：每个 token 都经过全部参数（所有神经元都"开灯"）
- **稀疏激活**：每个 token 只激活若干子模块，其余参数本次推理为零贡献

来源：MoE_深度解析 §核心直觉

## 理论吸引力与历史困境
理论上，条件计算可以打破"参数量→计算量"的二次方增长，但 Shazeer 2017 之前从未在大规模系统中被证明可行。Bengio 等人 2013/2015 提出框架后停留在小规模实验。来源：21_moe_2017 §背景与动机

**主要工程障碍**（Shazeer 2017 列出）：
1. GPU 远快于分支操作，理论收益难以转化为实际计算节省
2. 每个子网络收到的有效 batch size 缩小（"shrinking batch problem"）
3. 分布式集群中专家参数跨设备通信成为瓶颈
4. 负载均衡：门控趋向集中到少数热门专家，形成自增强不平衡

来源：21_moe_2017 §Prior Work 的局限

## 主要实现路线
| 路线 | 粒度 | 代表 |
|------|------|------|
| **MoE（Mixture of Experts）** | 专家级（FFN 层粒度） | Shazeer 2017、Switch Transformer、Mixtral、DeepSeek-V2/V3 |
| **Sparse Attention** | 注意力 token 对级 | Longformer、BigBird、Sparse Transformer |
| **Dynamic Routing**（如 CapsNet） | 神经元/胶囊级 | 早期探索，未规模化 |
| **Token Pruning** | 输入 token 级 | 推理时丢弃低重要性 token |

> 注：本概念以 MoE 为主线展开；MoE 是当前最成功的稀疏激活范式。来源：MoE_深度解析 §与相关概念的区别

## Shazeer 2017 的关键工程突破
- **Noisy Top-K Gating**：可学习噪声打破对称性，Top-K 强制稀疏（详见 concept: moe_architecture）
- **负载均衡双损失**（Importance + Load Loss）：将最重载专家的相对负载从 17.8x 降至 1.07x-1.47x（w=0.1 时）。来源：21_moe_2017 §负载均衡设计动机
- **数据并行 + 模型并行混合**：标准层与门控网络做数据并行，专家做模型并行，使专家有效 batch size 提升 d 倍（d = 设备数）。来源：21_moe_2017 §核心贡献4
- **首次规模化**：MoE 层扩展到 137 亿参数，在四个大规模基准上超过 SOTA，计算成本仅基线的 6%-40%。来源：21_moe_2017 §核心贡献5

## 与 Scaling Laws 的张力
- Dense Scaling Laws（Kaplan）下，参数量与计算量基本线性绑定
- 稀疏激活打破这一绑定：**总参数量 ≫ 激活参数量**
- DeepSeek-V3 的 671B 总参 / 37B 激活配比是这一逻辑的极致体现，证明大规模 MoE 可以以显著更低的训练 FLOPs 达到 Dense 模型相当的性能。来源：MoE_深度解析 §与 Scaling Laws 的关系 / §历史叙事

## 关键张力与代价
- **显存成本**：总参数仍需全部驻留显存（或跨卡分布），稀疏只省计算不省存储
- **通信开销**：Expert Parallelism 下的 All-to-All 路由通信
- **训练不稳定**：专家崩塌、batch 内激活不均导致梯度稀疏
- **微调难度**：MoE 模型对小 batch 微调不友好

来源：MoE_深度解析 §工程实践

## 在本项目的相关报告
- [MoE 奠基论文 (Shazeer 2017) 论文精读](../../reports/paper_analyses/21_moe_2017.md)
- [MoE 混合专家深度解析](../../reports/knowledge_reports/MoE_混合专家_深度解析_20260406.md)

## 跨域连接
- 具体实现路径 → concept: moe_architecture
- 与 Dense Scaling Laws 形成对照 → concept: scaling_laws
- 与心理学"选择性注意"在"只处理少数信息"这一抽象层面有类比

## 开放问题
- 稀疏激活的"专家专化"是否真的对应可解释的语义/语法功能？
- 是否存在比 MoE 更细粒度的稀疏化方案？（神经元级、子层级）
- 推理时如何动态决定 k 值（不同任务/不同 token 的最优 k 是否相同）？
