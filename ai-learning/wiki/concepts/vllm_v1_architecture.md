# vLLM V1 架构（源码级学习系列锚点）

> **概念类型**：AI 系统·推理引擎
> **系列计划**：`roadmap/vLLM_源码级学习计划_20260821.md`
> **源码基准**：`../vllm`（本地 clone）@ v0.27.1（commit `6e448d0`）
> **最后更新**：2026-08-21

## 一句话定义

vLLM V1 是 vLLM 现行且唯一的引擎架构（V0 已删除）：多进程（API server / EngineCore / GPU worker / DP coordinator）+ ZMQ-msgpack 通信 + EngineCore busy loop。设计哲学一句话：**让 GPU 永不空转**——HTTP/tokenize/detokenize/调度/序列化等一切 CPU 工作都与 GPU forward 重叠。

## 骨架（v0.27.1）

- **进程模型**：总数 = A + DP + N（+1 if DP>1）；`-tp=4` → 6 进程
- **请求一生 12 跳**：HTTP → render/tokenize（Renderer 前移）→ EngineCoreRequest →(ZMQ)→ Request → schedule → execute → sample →(ZMQ)→ 前端增量 detokenize → SSE
- **EngineCore 三线程**：busy loop / input IO（请求预处理与 forward 并行）/ output IO（buffer 复用零拷贝）
- **step 两相拆分**：`execute_model`（forward）与 `sample_tokens`（采样）独立 RPC，grammar bitmask 与 forward 重叠
- **执行层四层**：Executor → Worker → ModelRunner → Model（每 GPU 一个 worker 进程）

## 系列报告

- 阶段 0：《vLLM V1 架构总览：一个请求的一生（骨架篇）》— `reports/knowledge_reports/vLLM_V1架构总览_深度解析_20260821.md`

## 关联

- 人物口述史（互为表里：代码在本线，人在播客线）：podcast-learning《对游凯超3小时访谈》（vLLM 核心维护者/Inferact 首席科学家游凯超，2026-07-28 期）— `podcast-learning/reports/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.md`；对照组：《对话盛颖》（SGLang 发起人/RadixArk CEO，硅谷101 E247，2026-08-04 期）— `podcast-learning/reports/2026-08-04_rss-guigu101_shengying.md`
- 预科概念：[kv_cache](./kv_cache.md)、[llm_inference_engines](./llm_inference_engines.md)、投机解码（报告 `投机解码SpeculativeDecoding_科普讲解_20260720.md`）
- 上游概念页「LLM 推理优化引擎」的 vLLM 行从本篇起获得源码级支撑
