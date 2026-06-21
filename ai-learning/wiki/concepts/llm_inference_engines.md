# LLM 推理优化引擎（vLLM / SGLang / TensorRT-LLM / llama.cpp）

> **概念类型**：AI 系统·推理基础设施
> **报告**：`reports/knowledge_reports/LLM_推理优化引擎_20260621.md`
> **最后更新**：2026-06-21

## 一句话定义

**LLM 推理优化引擎**是专门为大型语言模型推理（inference / serving）设计的高性能运行时系统，通过 KV cache 管理、连续批处理、量化、内核融合、跨请求前缀共享等系统级优化，让 LLM 能在生产环境以高吞吐、低延迟运行。

## 核心问题

LLM 推理有三大物理瓶颈：

1. **显存容量** — KV cache 与权重占满 HBM → OOM、batch size 上不去
2. **显存带宽** — Decoder 阶段每 token 要从 HBM 读全模型权重 → memory-bound（NVIDIA 测算 Llama-2-70B 在 A100 上 compute utilization 仅约 5%）
3. **计算吞吐** — Prefill 阶段长 prompt 的 Attention 是 O(n²) → 首 token 时延（TTFT）爆炸

**所有推理引擎的核心优化方向都是：让算力尽量少闲置。**

## 四大主流框架

| 框架 | 首发 | 团队 | 核心创新 | 护城河 |
|------|------|------|----------|--------|
| **vLLM** | 2023-06 | UC Berkeley LMSYS | PagedAttention | 生态最广、production-ready |
| **SGLang** | 2024-01 | Stanford / UC Berkeley | RadixAttention | 前端 DSL、prefix 复用极致 |
| **TensorRT-LLM** | 2023-10 | NVIDIA | Kernel Fusion + In-flight Batching | 极致 kernel 性能、FP8 之王 |
| **llama.cpp** | 2023-03 | Georgi Gerganov | CPU-first 统一量化 | 跨平台最广、Apple Silicon 之王 |

## 关键技术

### 1. PagedAttention（vLLM）
**思想**：把操作系统虚拟内存分页机制搬到 KV cache 管理
- 默认 `block_size=16` token
- 块表（block table）记录逻辑到物理块的映射
- 显存碎片率：传统 60-80% → PagedAttention < 4%
- **来源**：Kwon et al., SOSP 2023

### 2. RadixAttention（SGLang）
**思想**：用 Radix Tree 组织所有活跃请求的 KV cache，跨请求复用任意长度的公共前缀
- 树节点：token + KV cache + ref_count
- 匹配：最长公共前缀（LCP）查找
- 驱逐：LRU / 引用计数
- **多轮对话 cache 命中率提升 3-5x**（SGLang 论文）
- **来源**：Zheng et al., NeurIPS 2024

### 3. Continuous Batching（迭代级调度）
**思想**：以 iteration-level 推进，每一步都允许新请求加入、已完成的请求退出
- GPU 空闲率：Static Batching 40% → Continuous Batching 5%
- NVIDIA 命名为 "In-flight Batching"，本质相同
- 实现差异：vLLM Python（μs 级）/ SGLang Rust（< 1μs）/ TensorRT-LLM C++（< 1μs）

### 4. Kernel Fusion（TensorRT-LLM）
**思想**：AOT 编译时将 5-10 个小算子融合为单个 CUDA kernel
- 减少 kernel launch overhead
- 典型场景：QKV 投影、Attention、RMSNorm、GeLU 全部 fused
- 代价：换模型 / 改配置要重新 build engine（10-60 分钟）

### 5. 量化
- **FP8** (H100 native)：4-8x speedup vs FP16
- **INT8 W8A8**：通用
- **INT4 W4A16** (weight-only)：AWQ、GPTQ、SmoothQuant
- **GGUF Q2-Q8** (llama.cpp 独家)：CPU 端最优

### 6. Multi-LoRA Serving
- **S-LoRA**（UC Berkeley + Stanford 2023）：CPU 存 LoRA 权重，按需 swap 到 GPU
- **Punica**（UW + OctoAI 2023）：单次 GEMM 内混合 base + 多 LoRA 计算
- 单卡支持数千并发 LoRA

## 选型决策树

```
你的部署场景是什么？
│
├─ 数据中心 NVIDIA H100/A100 高并发
│   └─ 性能优先 → TensorRT-LLM
│   └─ 灵活/DSL 优先 → SGLang
│   └─ 生态最广 → vLLM
│
├─ 多卡 AMD GPU → SGLang（2024-12 起最佳）
├─ Apple Silicon Mac 本地 → llama.cpp（Metal 后端）
├─ 纯 CPU / 边缘设备 → llama.cpp（GGUF Q4）
├─ 浏览器内 LLM → MLC-LLM / WebLLM
├─ 复杂 Agent / 多轮对话 / JSON 结构化 → SGLang
└─ 实验 / 研究 / 教学 → vLLM
```

## 前沿动态（2025-2026）

- **Speculative Decoding 工业化**：EAGLE-3、Medusa、Lookahead，1.5-2.5x 额外加速
- **Disaggregated Serving**（Prefill/Decode 分离）：Splitwise、DistServe，异构 GPU 利用率提升
- **MoE 推理优化**：DeepSeek V3 (671B)、Mixtral，专家并行（EP）SGLang Day-1 支持
- **Long Context (1M+)**：稀疏 attention、KV cache compression（SnapKV、H2O）、分层存储
- **端侧 / 浏览器 LLM**：MLC-LLM / WebLLM，WebGPU + 4-bit 7B 模型

## 与本项目其他报告的关系

- **KV_Cache_深度解析_20260330**：理解 KV cache 是理解本概念的基础
- **LoRA_深度解析**：理解 LoRA 原理后，Multi-LoRA serving 的工程价值才显现
- **Megatron_LM_大规模训练系统_深度解析_20260416**：推理系统的并行策略与训练系统高度同构（TP/PP）
- **多模态理解模型对比_GPT4o_Claude_Gemini_QwenVL_20260621**：多模态推理对引擎的特殊要求（vLLM/SGLang 已支持 VLM）

## 参考资料

- [vLLM GitHub](https://github.com/vllm-project/vllm)
- [SGLang GitHub](https://github.com/sgl-project/sglang)
- [TensorRT-LLM GitHub](https://github.com/NVIDIA/TensorRT-LLM)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [MLC-LLM GitHub](https://github.com/mlc-ai/mlc-llm)
- [TGI GitHub](https://github.com/huggingface/text-generation-inference)
- PagedAttention paper: https://www.usenix.org/conference/sosp23/presentation/kwon
- SGLang paper: https://arxiv.org/abs/2312.07104
- S-LoRA paper: https://arxiv.org/abs/2311.03285
- Punica paper: https://arxiv.org/abs/2310.18547
