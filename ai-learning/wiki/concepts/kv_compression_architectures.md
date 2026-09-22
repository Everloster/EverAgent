---
id: concept-kv_compression_architectures
title: "KV Cache 压缩架构谱系（KV Compression Wars）"
type: concept
domain: [ai-learning]
created: 2026-09-19
updated: 2026-09-19
sources: [DeepSeek-V4.1-Flash架构解剖_20260919]
status: active
---

# KV Cache 压缩架构谱系

## 一句话

长上下文推理的成本瓶颈是 KV cache（内存墙）；2024–2026 各家的架构竞争本质是"压 KV 的路线之争"——已从"压每个 token 的字节"进入"压层与层之间的冗余"时代。

## 谱系（均已核实）

| 代际 | 机制 | 一句话 |
|---|---|---|
| MLA（DeepSeek V2/V3, 2024） | 低秩潜在向量缓存 | KV 投影到低秩潜空间，推理时上投影还原 |
| NSA（2025-02） | 原生可训练稀疏 | 粗压缩 + top-k 细选 + 滑窗三分支 |
| DSA（V3.2-Exp, 2025-09） | lightning indexer | 轻量打分器做细粒度 top-k token 选择 |
| CSA+HCA（V4, 2026-04） | 压缩+稀疏混合 | CSA=序列维压缩+DSA top-k+shared-KV MQA；HCA=128:1 激进压缩 dense。**注意：无 "high-rank MQA" 术语（二手来源误植）** |
| **CSA2（V4.1-Flash, 2026-09）** | **跨层复用** | Full/Reindex/Reuse 静态三模式：借上层笔记重新打分 or 连笔记全盘复用；decoder 层级索引候选池与上下文长度解耦；FP4 全局 KV → 890 B/token |
| KDA（Kimi Linear/K3, GLM-5.3-Flash） | 线性注意力混合 | 3:1 线性层:全注意力层交错，绕开 KV 膨胀本身 |
| IndexPool（GLM-5.3-Flash） | indexer 池化 | 4 个 indexer key 加权池化为 1 |

## CED（Causal Encoder-Decoder，V4.1-Flash 首发）

- 40 层 = 20 因果编码器（prefill 8B 激活）+ 20 解码器（decode 16B 激活）——把 Agent 负载"读长写短"的非对称刻进架构。
- decoder 全局 KV 由**编码器末层隐状态经层相关投影生成**（非交叉注意力）；prefill 复杂度 O(NL)→约 O(NL/2)。
- 代价：decoder 对长上文的精细检索能力削弱（LongBench-V2 45.2 < V4-Pro 51.5，官方数据）。
- 生态成本：推理框架 decoder-only 同质层假设被打破（vLLM 发布 9 天仍在收尾 vs SGLang 官方共建 Day-0）。

## 配套机制

- **Engram**：经典 N-gram embedding 现代化为 O(1) 哈希查找的"条件记忆"稀疏轴（与 MoE"条件计算"互补）；DRAM 异步预取掩蔽延迟；U 型稀疏分配 scaling law（arXiv:2601.07372）。
- **Bounded Replay**：SWA（窗口 128）不持久化，恢复时只重放最近 128 token 接受近似状态——省线性级存储、花常数级重算，上下文越长越划算。
- **Single-Pass mHC**：混合系数滞后一个 block 消除数据依赖，单 kernel 融合，激活访存减半至理论下界 (2n+2)d。

## 与什么相关

- [[kv_cache]] / [[attention_mechanism]] / [[long_context_systems]] / [[sparse_activation]] / [[moe_architecture]]
- [[bitter_lesson]] 镜像：KV 压缩战争是"在硬件约束内做结构化归纳偏置"的反 bitter-lesson 案例（约束真实存在时，结构就是收益）

## 相关报告

- [DeepSeek-V4.1-Flash 架构解剖（2026-09-19）](../../reports/knowledge_reports/DeepSeek-V4.1-Flash架构解剖_CED非对称与KV压缩极限_20260919.md)

## 未解问题 / 追踪

- CED 长文精细检索的逐长度损失曲线（官方只有 LongBench-V2 一个点；第三方 RULER/NIAH 复现缺位）
- CSA2 三模式静态指派的确定方法（搜索/手工？）与组内 1 Full + 5 Reuse 比例依据
- Engram U 型分配律在 552B+196B 规模上的最优配比
