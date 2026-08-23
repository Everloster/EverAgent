# RadixAttention（基数注意力）

> 概念 · 首次出现：2026-08-04（硅谷101 E247 盛颖访谈）；出处论文：Zheng & Sheng et al., NeurIPS 2024（SGLang 论文）

## 定义

请求之间有公共前缀时，不必重算前缀的 KV cache。实现：对所有请求的前缀关系建**前缀树（Radix Tree）**做索引，把已计算的 KV cache 存进 KV memory pool 并建立映射。多轮对话 / agentic 场景几乎必有前缀共享，命中率收益大。

## 与 PagedAttention 的关系

两者是**不同切入点的互补优化**，今天的主流引擎（SGLang/vLLM）都同时具备：

- **PagedAttention**（vLLM，SOSP 2023）：操作系统虚拟内存分页思想管 KV cache——解决**内存碎片**（怎么存）
- **RadixAttention**（SGLang，NeurIPS 2024）：前缀树组织 KV cache——解决**跨请求前缀复用**（怎么省着算）

## 关联

- 项目实体：[[sglang|SGLang]]
- ai-learning 预科：`ai-learning/wiki/concepts/kv_cache.md`、`llm_inference_engines.md`；vLLM 源码线阶段 2 会读 vLLM 侧的 prefix caching 实现（哈希块表，不同数据结构）

## 引用

- [[2026-08-04_rss-guigu101_shengying|对话盛颖]]（E247）
