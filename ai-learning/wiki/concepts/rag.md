---
id: concept-rag
title: "RAG（检索增强生成）"
type: concept
domain: [ai-learning]
created: 2026-04-09
updated: 2026-04-09
sources: [RAG_深度解析_20260409, 16_rag_2020]
status: active
---

# RAG（检索增强生成）

## 一句话定义
RAG（Retrieval-Augmented Generation）通过先检索外部知识库、再由 LLM 结合检索结果生成的范式，让模型在闭卷考试中也能开卷回答。

## 核心流程

```
用户问题 → 向量检索（ANN） → Top-k 相关文档 → 拼接为上下文 → LLM 生成
```

三阶段：索引（Indexing）→ 检索（Retrieval）→ 生成（Generation）。原始论文：Lewis et al., NeurIPS 2020。

## Naive RAG → Advanced RAG → Modular RAG 演进

| 范式 | 核心改进 | 代表技术 |
|------|---------|---------|
| **Naive RAG** | 原始流程 | 检索 → 拼接 → 生成 |
| **Advanced RAG** | 查询改写 / 重排序 | HyDE, Self-RAG, Reranker |
| **Modular RAG** | 模块可插拔 | GraphRAG, Agentic RAG |

## RAG vs. Fine-tuning vs. Tool Use

| 维度 | RAG | Fine-tuning | Tool Use |
|------|-----|-------------|----------|
| 知识更新 | 即时（改文档） | 需重训练 | 即时（API） |
| 计算成本 | 检索 + 生成 | 高（梯度计算） | API 调用 |
| 知识容量 | 可外挂海量文档 | 受限参数规模 | 受限 API 能力 |
| 适用场景 | 知识密集型 | 风格/领域适配 | 实时行动 |

## Reranker 的作用

两阶段检索（粗召回 → 精排）：
1. **召回（Recall）**：ANN 检索 top-50 ~ top-100
2. **精排（Rerank）**：Cross-Encoder 重排序，取 top-3 ~ top-10 送 LLM

## GraphRAG vs. Naive RAG

- Naive RAG：平面向量检索，适合单跳问答
- GraphRAG：构建知识图谱，用实体关系检索，适合多跳推理（如"A 的 B 是什么"）
- Microsoft GraphRAG（2024）开源实现

## 核心挑战

| 挑战 | 说明 |
|------|------|
| 检索质量决定上限 | 垃圾进 → 垃圾出 |
| Context 长度浪费 | 大量 chunks 时 LLM 难以聚焦 |
| 多跳推理失败 | Naive RAG 对复杂关系建模能力弱 |
| 评估困难 | 检索指标（Recall）与生成质量不完全相关 |

## 在本项目的相关报告

- [RAG 深度解析（2026-04-09）](../../reports/knowledge_reports/RAG_深度解析_20260409.md)

## 跨域连接

- RAG 是 Test-time Compute 思路的一种（推理时加载外部知识）→ concept: test_time_compute
- Tool Use 是 RAG 的"行动版"（检索 vs. 执行）→ concept: agent_systems
- GraphRAG 与知识图谱的关联 → cs-learning 的知识图谱相关概念
