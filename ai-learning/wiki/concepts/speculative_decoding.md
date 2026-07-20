# 投机解码 Speculative Decoding

> 概念页 · LLM 推理优化。无损加速大模型自回归生成的核心技术。

## 一句话

用便宜的 draft 模型 $p$ 猜 K 个 token，昂贵的 target 模型 $q$ 一次并行验证，靠访存红利实现 2-3× 加速且输出分布严格不变。

## 核心要点

- **加速来源**：低 batch 推理是 memory-bandwidth bound，并行验 K 个 token 近乎免费
- **无损保证**：接受概率 $\min(1, q/p)$ + 残差重采 $\text{norm}(\max(0,q-p))$ → 输出严格服从 $q$
- **实测**：T5-XXL 2-3×（Leviathan 2023）、Chinchilla 70B ~2×（Chen 2023）
- **加速不均**：依赖 draft/target 对齐度，代码 > 摘要；低资源语言更吃亏（Sandler 2025）

## 前置知识

- [KV Cache](./kv_cache.md) — 同样源于"推理是 memory-bound"这一事实
- [Transformer 架构](./transformer_architecture.md) — 自回归解码的串行瓶颈
- [LLM 推理引擎](./llm_inference_engines.md) — 投机解码是其中一项关键优化

## 延伸 / 变体

- Tree-based（SpecInfer）、Medusa（自带草稿头）、RSD（无放回采样, 2024）

## 相关报告

- [投机解码科普讲解（20260720，建直觉首选）](../../reports/knowledge_reports/投机解码SpeculativeDecoding_科普讲解_20260720.md) — 教授/实习生贯穿类比，三词词表手算验证无损性 + 硬件账算平 2-3× 加速
- [投机解码 Speculative Decoding 深度解析](../../reports/knowledge_reports/投机解码SpeculativeDecoding_深度解析_20260625.md) — 公式逐符号拆解 + 伪代码 + 变体谱系

## 未解问题

- 残差分布正确性的完整测度论证明（见 open-questions）
- draft/target 最优容量比是否有理论刻画
