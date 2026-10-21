---
title: "DeepInfer：从模型协同设计到生产推理内核"
domain: "ai-learning"
report_type: "repo_deep_research"
status: "completed"
updated_on: "2026-10-21"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["deepinfer", "llm_inference", "speculative_decoding", "dspark", "kv_cache", "moe", "eplb", "asynchronous_scheduling"]
related_concepts: ["llm_inference_engines", "speculative_decoding", "kv_cache", "kv_compression_architectures", "vllm_v1_architecture"]
---

# DeepInfer：从模型协同设计到生产推理内核

> 研究时点：2026-10-21  
> 源码版本：[`deepseek-ai/DeepInfer@774ce244`](https://github.com/deepseek-ai/DeepInfer/tree/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01)  
> 研究范围：仓库真实源码、DeepSeek V4.1 Flash 技术报告、DSpark 论文、DeepSeek 官方部署博客、公开 benchmark 脚本，以及 vLLM、SGLang、TensorRT-LLM 的官方材料。  
> 验证边界：本报告没有在 NVIDIA SM100 或 Huawei Ascend 950 上编译、部署或复现性能；所有性能数字均标明是官方自报、脚本推导还是源码可验证事实。

## 一、结论先行：这次开源很重要，但不是“完整 DeepSeek 云服务”

DeepInfer 值得认真研究。它公开的并非只有几组针对 DeepSeek 的 kernels，而是一套约 5.2 万行 Python/C++ 的推理 engine core：请求状态机、C++ 批调度器、GPU KV/state 内存管理、异步 CPU/GPU 流水线、DSpark 变长验证、Expert Parallel Load Balancer、结构化输出，以及 NVIDIA/Ascend 两套后端都在仓库里。

但它目前也不能被准确描述成“一下载就能搭出 DeepSeek 线上服务”。官方 README 明确写着，完整服务仍缺少外部 KV cache system、Vision Encoder/Prefill/Decode 分离编排，以及跨数据并行副本的负载均衡；源码中的 P/D 拆分、KV 落盘和跨阶段发送接口也只是空钩子，没有公开实现。[源码：README](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/README.md#L33-L42)；[源码：LLMEngine 空钩子](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/engine/llm_engine.py#L800-L856)

我的核心判断有五条：

1. **DeepInfer 是生产推理内核的开源版，不是完整 serving 产品。** 当前公开入口是 offline batch inference，没有 OpenAI-compatible server、路由器、3FS KV 存储或 autoscaler。
2. **它最值得学习的是模型与系统的闭环协同。** CED、CSA2、FP4 KV、SWA Bounded Replay、DSpark 不是论文里的孤立模块；源码把它们落实到 cache layout、调度器、CUDA Graph 和 kernel 流水线中。
3. **DSpark 的关键不是“一次猜 5 个 token”，而是把每个 draft token 的接受概率视为稀缺算力的投资回报。** 调度器结合 confidence 和真实硬件吞吐曲线，为整个 batch 动态分配验证长度。
4. **官方性能曲线有价值，但不能当作跨框架冠军榜。** Decode 图把实测 steps/s 与假设的 75% draft acceptance 相乘得到 token/s；仓库没有发布生成曲线的 raw JSON，也没有同硬件下的 vLLM/SGLang/TensorRT-LLM 对照。
5. **[推测] 截至 2026-10-21，严肃的独立分析和复现尚未出现。** SemiAnalysis、Artificial Analysis、vLLM Blog、LMSYS/SGLang 官方渠道均未检索到 DeepInfer 专文；现有第三方文章主要复述官方材料。公开检索无法证明不存在未被索引或未公开的分析，当前最可靠的判断仍需以源码、论文和官方部署文档交叉核验。

### 证据标签

- **[源码]**：可以在固定 commit 的实现中定位。
- **[论文]**：来自 DeepSeek 技术报告或 DSpark 原始论文。
- **[官方自报]**：来自官方博客、Q&A 或性能图，尚无独立复现。
- **[二手分析]**：第三方整理，不作为关键结论的唯一依据。
- **[推断]**：由源码与材料综合得到，仍可能被后续版本修正。

### 发布快照

| 维度 | 2026-10-21 快照 | 解读 |
|---|---:|---|
| GitHub stars | 约 12.3K | 发布后关注度极高，数字会持续变化 |
| forks | 约 1.1K | 社区正在快速进入源码 |
| commits | 3 | 几乎是一次性首发快照，缺少演化历史 |
| tags / releases | 0 | 尚无稳定版本线 |
| package version | `0.1.0`，Beta classifier | API 与部署边界可能快速变化 |
| 支持模型 | 1 个：DeepSeek-V4.1-Flash | 高度模型专用 |
| 支持硬件 | NVIDIA SM100、Huawei Ascend 950 | 不是通用 GPU 框架 |
| 公开 CI workflow | 无 | 有测试代码，不等于已有公开持续集成 |

GitHub 元数据来自 2026-10-21 的 [GitHub API 快照](https://api.github.com/repos/deepseek-ai/DeepInfer)；源码历史、tag 和代码规模来自固定 commit 的本地 Git 静态核验。

## 二、研究对象：开源了哪一层，哪些仍留在 DeepSeek 内部

### 2.1 完整生产系统与开源仓库不是同一个边界

DeepSeek 官方部署图描述的是一个 EPD 系统：请求先经过协议与 token 编解码层，再由独立的 Vision Encoder、Prefill 和 Decode 服务处理；Prefill/Decode 之间传递 KV cache，外部 3FS 存储长期保存全局 KV，各阶段都有自己的负载均衡器。[官方部署博客](https://zhuanlan.zhihu.com/p/2095560295930508953)

开源仓库覆盖其中的“单个 engine 实例内部”：

| 组件 | 是否开源 | 说明 |
|---|---|---|
| Offline `LLM` API | 是 | 批量提交请求并循环 `engine.step()` |
| 模型加载与 V4.1 runtime | 是 | DeepSeek-V4.1-Flash 专用实现 |
| C++ Scheduler | 是 | waiting/running/prompted、prefill/decode、抢占、MTP 状态 |
| GPU KV block / state slot | 是 | main KV、indexer K、SWA ring、compression state |
| DSpark draft + verification | 是 | Markov head、Confidence Head、变长验证 |
| EPLB | 是 | 冗余专家、历史统计、动态权重 shuffle |
| Structured Output | 是 | regex、JSON Schema、EBNF，基于 xgrammar |
| NVIDIA / Ascend kernel 适配 | 是 | CUDA/NCCL 与 CANN/HCCL 路径 |
| 在线 API server | 否 | `LLMEngine` 文档明确说本次发布没有 online wrapper |
| DeepSeek Recipe | 独立仓 | 协议、prompt 编码与流式输出解析，不在 DeepInfer 仓内 |
| Prefill/Decode/Vision 路由器 | 否 | 官方文档描述，源码没有实现 |
| 3FS KV cache store | 否 | 只有 state slice 与接入钩子 |
| 自动扩缩容与故障迁移 | 否 | 官方文档描述，源码没有实现 |

源码中的 `LLMEngine` 直接写明：`LLM` 只是 offline batch wrapper，本次 release 不包含 online-serving wrapper。[源码](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/engine/llm_engine.py#L130-L142)

### 2.2 为什么这种“只开 engine core”仍然很有价值

多数推理框架会公开通用 serving 功能，却很难展示 frontier model 在生产中的专用协同。DeepInfer 反过来：产品完整性弱，模型系统细节强。它公开了四类通常很难同时看到的资产：

1. **模型结构如何改变 cache 物理布局**：哪些层保存 main KV，哪些层复用，哪些 SWA state 可丢弃并重算。
2. **推测解码如何进入系统调度**：confidence 不只用于算法评估，而是决定 batch 内每个请求消耗多少验证 token。
3. **CPU/GPU 流水线如何处理异步状态滞后**：ZOS 下调度器必须容忍 sampling 结果晚一拍。
4. **MoE 热点专家如何在线迁移**：EPLB 不只是离线 placement，而是收集窗口统计并 shuffle 权重。

它因此更像一份“可执行的 production systems paper”。

### 2.3 官方公开的生产规模：它证明系统跑过，不等于仓库已经包含这些能力

DeepSeek 在官方部署博客中给出了一组很少见的生产数据。以下全部属于 **[官方自报]**，当前无法从开源仓库独立复现：

| 维度 | 官方披露 | 正确解读 |
|---|---:|---|
| 单集群服务量 | 155 万亿 tokens/天 | 完整线上系统的数据，不是当前 offline 仓库单独跑出的结果 |
| 商业口径 | 38 美元/GPU-hour revenue（谷价） | 是官方收入口径，不是成本、利润或通用租卡价格 |
| 持久 Block KV | 约 100 PiB 3FS | 3FS/kvcache-store 没有随 DeepInfer 开源 |
| 3FS 峰值带宽 | 读约 10 TiB/s、写约 850 GiB/s | 面向约 112 KiB KV block 随机 I/O 的集群总带宽 |
| Global KV TTL | Agent 3 天、Chatbot 7 天 | 官方称 Chatbot 设为约 3 天会损失 0.5%–1% 命中率 |
| SWA host-memory pool | TTL 约 180 秒、命中率 98% 以上 | 生命周期短，miss 由 Encoder SWA Bounded Replay 兜底 |

[官方部署博客](https://zhuanlan.zhihu.com/p/2095560295930508953)

自动扩缩容与容错同样位于未开源服务平面：Prefill 按未命中 token 量估算容量，Decode 按运行请求数扩缩；Decode 实例下线有 1 分钟宽限期，未完成请求连同 KV 转移；配额占用高于 0.8 时禁止缩容；大 EP 实例发生卡故障后，平台会按健康卡数重新确定 EP size。官方称单实例重启仍是分钟级，容错依赖冗余配额与请求级重路由。

这些数字的价值是证明 DeepInfer 的设计来自真实大规模系统；它们也再次说明，**开源 engine core 与承载这些数字的数据中心平面不是同一个交付物。**

## 三、源码架构：一次请求如何穿过 DeepInfer

### 3.1 六层代码结构

```text
LLM offline API
  deepinfer/entrypoints/llm.py
            │
            ▼
Engine lifecycle + Python/C++ bridge
  deepinfer/engine/llm_engine.py
            │
            ▼
C++ request state and scheduler
  csrc/engine/{sequence,scheduler,block_manager}.hpp
            │
            ▼
Per-GPU worker pipeline
  deepinfer/worker/{base,worker,model_runner,cache_engine}.py
            │
            ▼
V4.1 model runtime + DSpark + EPLB
  deepinfer/model_executor/**
            │
            ▼
FlashMLA / DeepGEMM / DeepEP / DeepSelect / TileLang
  NVIDIA CUDA or Huawei Ascend backend
```

代码中有 23 个文件显式标注“Derived from vLLM; modified by DeepSeek”。这与 README 的自述一致：DeepInfer 最初主要建立在 vLLM 上，同时吸收了 SGLang 与 TensorRT-LLM 的思路。[源码：README acknowledgments](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/README.md#L93-L95)

但当前热路径已经不是“换名 vLLM”。C++ Scheduler、V4.1 cache layout、DSpark、ZOS、EPLB 和大量 TileLang kernels 都是深度定制。

### 3.2 请求进入 engine

`LLM.generate()` 做三件事：

1. 将 prompt 转成 token IDs；
2. 为每个请求创建 `SamplingParams` 与 request id；
3. 不断调用 `LLMEngine.step()`，直到 scheduler 与 structured-output builder 都没有未完成请求。

[源码：`LLM.generate`](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/entrypoints/llm.py#L90-L195)

`LLMEngine.add_request()` 再完成：

- token 合法性校验；
- 多模态 prompt 覆写；
- Engram compressed tokenizer 映射；
- 异步构建 xgrammar matcher；
- 创建 C++ `Sequence` 并放入 scheduler waiting queue。

[源码：`add_request`](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/engine/llm_engine.py#L471-L631)

### 3.3 初始化不是简单 `load_model`

Engine 启动顺序是：

```text
加载 tokenizer / multimodal processor
→ 按 CP rank 启 worker process
→ 加载模型权重
→ 用最大形状跑 profile，测显存峰值
→ 计算剩余显存能放多少 KV blocks
→ 分配 paged KV 与 per-sequence state slots
→ capture 主模型与 DSpark CUDA Graphs
→ profile decode graph 的 batch-size/latency 曲线
→ 创建 C++ Scheduler
```

这里有一个重要联系：**启动期 profile 出来的 decode 曲线会被 DSpark 调度器直接使用。** 它不是只供日志展示，而是运行时决策的一部分。

### 3.4 `step()` 的真实流水线

传统同步 decode 可以写成：

```text
schedule(N) → forward(N) → sample(N) → post-process(N)
```

`post-process(N)` 需要等 GPU sampling 结束，再把结果拿到 CPU；CPU 此时更新请求长度、停止状态和 scheduler 账本。若下一步必须等它完成，GPU 会在 CPU 工作期间空闲。

DeepInfer 的 `Worker.execute_model_step()` 改成：

```text
forward(current)
→ post-process(previous)
→ sample(current)
→ pre-sampler sync
→ prompt / 同步模式：处理 current
→ ZOS decode：把 current 留到下一轮
```

[源码：Worker pipeline](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/worker/worker.py#L88-L189)

这就是官方所谓 Asynchronous Scheduling / Zero-Overhead Batch Scheduler 的核心。它让第 N 步的 CPU 后处理与第 N+1 步的 GPU forward 重叠。

### 3.5 异步带来的难题：调度时不知道真实接受了几个 token

ZOS 不是免费午餐。第 N+1 步排队时，第 N 步 draft token 的接受结果尚未回到 CPU：

- CPU 看到的是“乐观推进”的 sequence length；
- 当前 batch 与上一 batch 的请求集合可能变化；
- speculative verification 的每请求 `seqlen_q` 也可能变化。

DeepInfer 用 `prepare_zos_inputs()` 生成新旧 batch 的 remap，在 GPU 上修正 `seqlens_q / seqlens_k`；sampling 结束后，`commit_processed_tokens()` 再用真实接受数覆盖乐观值。[源码：ZOS 修正](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/worker/worker.py#L191-L245)；[源码：KV token 账本](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/csrc/engine/sequence.hpp#L200-L227)

这段设计说明，DeepInfer 真正解决的是“异步系统中的正确性账本”，不只是把两个线程并行起来。

## 四、四个关键机制

### 4.1 C++ Scheduler：公开的是 engine 内调度，不是集群路由

Scheduler 维护三类队列：

- `waiting`：等待 prefill，或抢占后等待重算；
- `prompted`：prefill 完成，等待进入 decode；
- `running`：当前活跃 decode 请求。

它支持三种 engine type：

- `NORMAL`：同一 engine 混合做 prefill 与 decode；
- `PROMPT`：只做 prefill；
- `COMPLETION`：只做 decode。

#### NORMAL engine 如何决定本步做 Prefill 还是 Decode

同一个 DP group 的 ranks 必须执行相同步型，否则 collective 会死锁。DeepInfer 设计了两个投票点：

- 默认每 70 个 decode steps 到一次 **ALL 点**：所有 rank 都有可调度 prefill 才切换；
- 默认每 100 个 decode steps 到一次 **ANY 点**：任一 rank 有 prefill 就集体切换，防止孤立 rank 长期饿死。

如果投票后实际没有 rank 能排出 prompt，例如 KV block 不足，就退回 decode，避免全组反复执行空 prompt step。[源码：Scheduler vote](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/csrc/engine/scheduler.hpp#L270-L345)

#### Prefill

开源 Scheduler 按以下约束选 prompt：

- 最大序列数；
- `max_num_batched_tokens`；
- `sum(seqlen_k)` 上限；
- KV block 与 state slot 是否可分配；
- context parallel 对齐；
- 多模态图片 token 不能从中间切开；
- chunked prefill checkpoint。

[源码：Prefill scheduling](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/csrc/engine/scheduler.hpp#L347-L553)

#### Decode 与抢占

Decode 优先让输出较短的请求继续；block 不足时，较长请求成为 victim。普通请求可以释放 block 后回 waiting 重算；structured-output 请求因为 matcher 状态难以重放，会被结束。Completion-only engine 没有 prefill 通道，因此禁止“抢占后重算”。[源码：Decode scheduling](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/csrc/engine/scheduler.hpp#L555-L660)

#### 与官方生产调度的差异

DeepSeek 官方博客还描述了一套更上层的 Prefill Load Balancer：按总长度分桶、跨 engine 分配 compute quota、DP rank 内再分配负载，单卡 scheduler 用拟合的二次代价模型 `cost(q,c)` 从纳秒预算反解本步 `q`。

当前开源代码没有 `compute_quota` 或这套二次方程调度；`FlopsEstimator` 只为统计计算量服务。**所以仓库公开了 engine 内 batching 与状态机，没有公开完整的 production Prefill Load Balancer。**

### 4.2 DSpark：从“猜几个”升级为“算力投给谁”

#### 模型侧

V4.1 Flash 技术报告描述的 DSpark 包含：

- 3 个 draft Transformer blocks；
- sliding attention window = 128；
- 一次 forward 并行计算 5 个 draft positions 的 base logits；
- Markov head 用上一个 draft token 修正相邻依赖；
- Confidence Head 预测每个位置的条件接受概率。

[论文：V4.1 Flash §2.4.3](https://arxiv.org/html/2609.19969v1#S2.SS4.SSS3)

源码类名仍叫 `DFlash`，但其中已经实现 Markov embedding、Confidence Head 和变长调度所需输出，因此不能用文件名把它误判成论文中的旧 DFlash baseline。[源码：DFlash/DSpark runtime](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/model_executor/models/mtp/dflash.py#L82-L187)

#### 调度目标

对请求 `r` 的第 `j` 个 draft token，Confidence Head 给出条件接受概率：

\[
c_{r,j}=P(\text{第 }j\text{ 个 token 被接受}\mid 1\ldots j-1\text{ 已接受})
\]

因为 speculative decoding 只能接受连续前缀，第 `j` 个 token 真正存活的概率是：

\[
a_{r,j}=\prod_{i\le j}c_{r,i}
\]

若 batch 有 `R` 个请求，每个请求至少验证一个 target token，再为请求 `r` 追加 `\ell_r` 个 draft tokens，则 target forward 的总 token batch 为：

\[
B=\sum_{r=1}^{R}(1+\ell_r)
\]

期望产出的有效 token 数为：

\[
\tau=\sum_{r=1}^{R}\left(1+\sum_{j=1}^{\ell_r}a_{r,j}\right)
\]

启动时已经 profile 出不同 batch size 的 `SPS(B)`，调度器要最大化：

\[
\Theta=\tau\cdot SPS(B)
\]

直觉上：轻载时多验证一个低 confidence token 的机会成本小，可以“多赌几手”；重载时 batch capacity 稀缺，应该只验证最可能被接受的 token。

[论文：DSpark §3.2](https://arxiv.org/html/2607.05147v1#S3.SS2)

#### 源码如何求解

`MTPVarlen`：

1. 把每个请求的 confidence 累乘成 prefix survival probability；
2. 将所有候选 token 按 `a_{r,j}` 全局排序；
3. 逐步增加验证 token；
4. 对齐到可用 CUDA Graph batch size；
5. 用 profile 曲线、在线估计的 forward residual 和 sampler 时间计算吞吐；
6. 取最佳总 budget，再回填每个请求的 `seqlen_q`。

[源码：`MTPVarlen`](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/csrc/engine/mtp_varlen.hpp#L133-L267)

这里还有一处论文算法与生产实现的关键差异。DSpark 论文的 Algorithm 1 在吞吐第一次下降时 `break`，用 early stopping 保证决策不偷看未来 candidate；但真实硬件的 `SPS(B)` 是离散、锯齿状曲线，第一次下降未必是全局最优。论文 §5.2 因此说明生产实现会移除这个 `break`，扫描全部候选 budget。为了不破坏无损 speculative decoding，它只用 **N-2 轮的历史 confidence 决定总容量 K**，当前轮 token 只负责按最新 confidence 排序；两步时间隔离形成了 causal barrier。源码 `MTPVarlen` 也确实遍历全部候选，不在第一次下降处停止。[论文：DSpark §5.2](https://arxiv.org/html/2607.05147v1#S5.SS2)

这使“推测长度”从模型超参数变成系统负载相关的调度变量。

#### ZOS 下为什么要保存 N-1 / N-2 两轮 confidence

当 CPU 提前排 N+1 时，N 的 confidence 还在 GPU 上。源码用 `schedule_cnt / process_cnt` 判断当前可用的 `accept_rates` 属于哪一轮：

- 已完成配对：当前值是 N-1，上一值是 N-2；
- 还有一轮在途：当前值是 N-2，上一值是 N-3。

总 batch budget 先在 CPU 侧决定，精确的 per-request length 再由 GPU TileLang kernel 修正。这与官方 Q&A 对生产路径的描述一致。

### 4.3 KV cache：把“存什么、重算什么”写进物理布局

DeepInfer 的 GPU cache 分两类：

1. **Paged block KV**：main KV 与 indexer K，按 block 分配；
2. **Per-sequence state slot**：SWA ring 与 compression state，每条活跃请求一个固定 slot。

#### 为什么 V4.1 需要定制 cache layout

V4.1 的 CSA2 在层维度复用 main KV、indexer K 和 Top-K indices：

- **Full Mode**：新算 main KV、indexer K 和 Top-K；
- **Reindex Mode**：复用 KV，但重新打分选 Top-K；
- **Reuse Mode**：KV 与 Top-K 都复用。

[论文：CSA2](https://arxiv.org/html/2609.19969v1#S2.SS3)

源码中的 `KVCacheManager` 会根据 share-KV / share-index map 让多个层引用同一个 tensor view；复用层不会再次推进 KV buffer offset。[源码：KV cache layout](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/worker/cache_engine.py#L376-L477)

这不是“框架支持一种新 attention”那么简单，而是模型的 layer-sharing topology 已经进入显存分配器。

#### StateBlock 的 stored / dropped 区

每个 sequence state slot 被分成：

```text
[stored region: 需要跨请求恢复的 SWA]
[dropped region: decoder/consumer SWA | compression state]
```

[源码：StateBlock](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/worker/cache_engine.py#L221-L306)

这个布局直接服务 SWA Bounded Replay：可便宜重算的 decoder/consumer SWA 不必进入持久化路径。

#### SWA Bounded Replay 的核心取舍

SWA 的依赖会跨层累积。精确恢复 `L` 层、窗口 `W` 的 state，最坏需要 replay `L×W` 个 token；V4.1 只 replay 最后 `W` 个 token，并把注意力窗口截断在 replay 区间，接受一个近似 state。

对 V4.1：

- Encoder SWA miss：只重算命中前缀最后 128 token，global KV 原样复用；
- Decoder SWA：每次 prefill 只让 20 层 decoder replay 最后 128 token，而非精确跑 2,560 token；
- 论文称这使 persistent KV 约降到 V4 的 1/8，同时几乎减半 prefill 计算。

[论文：Inference System / SWA Bounded Replay](https://arxiv.org/html/2609.19969v1#S3.SS2)

近似并非无代价。论文在 limitations 中明确承认，CSA2 selection error 与 SWA state reconstruction 可能在未覆盖的极端输入、长上下文稀疏检索和 cache-resumption 边界造成能力下降。[论文：Limitations](https://arxiv.org/html/2609.19969v1#S6)

#### 开源到哪里为止

仓库实现了 GPU 内布局、ring 重排、state slice、block pin/clone/free 和 bounded replay metadata，但没有实现：

- 3FS 持久存储；
- hash-chain prefix matching；
- 3FS 到 shared memory 的异步 fetch；
- 用 GDR 将 block 搬入 HBM；
- SWA 跨机目录与 400G 网络拉取；
- TTL 与 GC。

这些内容只能从官方生产博客理解，不能从当前开源仓库直接部署出来。

### 4.4 EPLB：热点 expert 不只路由，还会复制和搬家

MoE 的问题不是平均 token 数，而是最慢 rank 决定整个同步 step。DeepInfer 的 EPLB 为热点 logical expert 创建冗余 physical experts：

1. 每步统计本地 physical expert 收到的 token 数；
2. 在窗口内累计，并在 EP group 中 all-reduce；
3. 贪心决定哪些 logical experts 获得额外副本；
4. 再将全部 physical experts 分布到 ranks，尽量降低历史每步的峰值 rank load；
5. 同一 scale-up domain 内使用 PyTorch symmetric memory / IPC shuffle 权重，跨域走通用通信路径。

[源码：EPLB runtime](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/model_executor/eplb/__init__.py#L42-L289)；[源码：placement policy](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/deepinfer/model_executor/eplb/policy.py#L73-L140)

官方线上策略把 Prefill 与 Decode 分开：Prefill 使用较短统计窗与较频繁重排，Decode 使用更长窗口与更低重排频率。这里也体现了同一模型在两个阶段的负载分布不同。

需要注意一个文档冲突：

- 当前中文官方博客称 Prefill `moe_lb` 为 1.0320（EP2/DP2）和 1.0618（EP4/DP4）；
- 仓内英文 Q&A 称 1.045（EP2/DP2）和 1.074（EP4/DP4）。

两组数字不同。报告不裁定哪一组正确，只把它作为首发文档尚在整理的证据。

## 五、性能证据：哪些可信，哪些暂时只能参考

### 5.1 官方公开曲线

README 给出的环境是：

- Prefill：4 张 SM100，EP4/DP4；
- Decode：64 张 SM100，EP64/DP64；
- context = 131,072；
- 都位于一个 scale-up domain 内。

[官方性能图与说明](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/README.md#L77-L87)

下面的数值是 **[官方自报｜性能图视觉读数]**，并由 MarkTechPost 的二手读图交叉检查；仓库没有配套 raw `results.jsonl`，因此只能视为近似值，不能精确复算：

- Prefill 的 non-cached throughput 随 batch 增大，从约 60K tokens/s/GPU 上升到接近 90K；代价是单 step latency 从约 70ms 增至约 730ms。
- Decode 在 256 requests/rank 附近超过 25K estimated tokens/s/GPU，每用户约 100 tokens/s；低并发时每用户速度超过 300 tokens/s，但总吞吐下降。
- EP64 曲线整体高于 EP8，官方将其解释为 Wide-EP 降低每步 MoE expert memory traffic。图副标题同时显示冗余 expert 从 32 增到 64，因此它不是只改变 EP size 的单变量实验。

### 5.2 最容易被误读的地方：Decode token/s 是推导值

发布图副标题给出 `nextn=3` 与逐 token acceptance 75%；这两个值也是 **[官方图视觉读数]**。`examples/README.md` 和 `plot_pareto.py` 公开了对应计算公式：

1. 真实测量 `avg_SPS`，即每秒 decode steps；
2. 发布图设置 `nextn=3`，并假设每个 draft token 接受率为 75%；
3. 于是每步期望 token 数：

\[
\tau=1+3\times0.75=3.25
\]

4. 图中的吞吐：

\[
\text{tokens/s/GPU}=avg\_SPS\times requests\times 3.25 / CP
\]

[源码：benchmark metric](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/examples/README.md#L31-L57)；[源码：plot formula](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/examples/sweep/plot_pareto.py#L58-L75)

所以图中 25K+ 不是直接统计线上用户实际吐出的 token，而是实测 step rate 在一个明确接受率假设下的折算。这个口径合理，但必须写出来。

### 5.3 DSpark 的两组收益不要混为一谈

**第一组：DSpark 对旧 MTP-1。** DSpark 原始论文在 V4 preview 线上流量中报告：

- V4-Flash 在 80 tok/s/user SLA 下，总吞吐比 MTP-1 高 51%；
- 在匹配的实用吞吐区间，每用户生成速度提高 60%–85%；
- 高 SLA 下出现 661% 这类巨大比例，论文自己提醒：这是 baseline 已接近不可用边界，不应解释成常规 6.61× 加速。

[论文：DSpark production evaluation](https://arxiv.org/html/2607.05147v1#S5.SS4)

**第二组：变长验证对 fixed-5。** DeepInfer 官方 Q&A 比较的是 DSpark 内部两种 scheduler：

- 约 60 sequences/rank：+5.4%；
- 72 sequences/rank：+6.7%；
- 96 sequences/rank：+11.0%；
- 16 sequences/rank：反而 −1.5%。

[官方 Q&A：Speculative decoding](https://github.com/deepseek-ai/DeepInfer/blob/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01/doc/inference_deployment_qa.md#L239-L264)

这两组对比的 baseline 不同。把“60%–85%”说成“变长 scheduler 的收益”是错误的。

### 5.4 Benchmark 的优点

- 脚本公开，warmup 与 measurement window 有明确说明；
- 会排除 MoE LB stats flush 污染的 interval；
- 明确 profiler 可使小 batch step time 膨胀近 50%，不能用 trace 推导 SPS；
- 支持落 raw metric JSONL；
- evaluation 把 generation 与 scoring 分开，并要求 `coverage_complete=true` 才能报告 Pass@1；
- 仓内还有 batch-invariant、PPL、EPLB、state cache、structured output 等回归测试。

### 5.5 Benchmark 的缺口

1. 仓库没有发布生成 README 曲线的 raw `results.jsonl`；
2. 没有多次重复、误差条、功耗、频率或更具体的 SM100 SKU；
3. 没有同硬件、同 checkpoint、同采样参数的竞品对照；
4. offline benchmark 排除了完整服务层的存储、路由、autoscaling 和协议开销；
5. Vision benchmark 明确不计 CPU preprocessing 与 H2D；
6. Wide-EP 图副标题显示，除了 EP8→EP64，冗余 expert 也从 32 增到 64，不是严格单变量实验；
7. 官方 Q&A 自报线上约达到“完美均衡 offline benchmark”的 80%，说明离线曲线不能直接等同生产容量。

### 5.6 第三方分析现状

[MarkTechPost](https://www.marktechpost.com/2026/10/20/deepseek-deepinfer-open-source-inference-framework) 是目前较完整的公开英文整理，正确指出了 offline-only、硬件窄、缺 KV store/P-D/load balancer 等边界，也整理了性能图。但其主要证据仍来自 README 与 Q&A，没有独立运行或源码级验证。

[推测] 截至研究时点，公开搜索未发现 SemiAnalysis、Artificial Analysis、vLLM Blog 或 SGLang/LMSYS 官方团队对 DeepInfer 的独立 benchmark 或深度源码评审；这不能排除未被索引或未公开的工作。发布只有一天，这个缺口是正常的。当前更稳妥的做法是等待：

- SM100/Ascend 950 的社区复现；
- vLLM/SGLang/TensorRT-LLM 同 checkpoint 对照；
- raw benchmark JSON；
- 第一批 issue/PR 反馈和正式 tag。

## 六、与 vLLM、SGLang、TensorRT-LLM 比较：谁该用它

| 维度 | DeepInfer | vLLM | SGLang | TensorRT-LLM |
|---|---|---|---|---|
| 主要目标 | V4.1 Flash 模型系统协同 | 通用、易用、高吞吐 serving | Agent/RL/多模态与大规模 serving | NVIDIA 全栈性能 |
| 当前模型覆盖 | 1 个 | 200+ architectures | LLM/VLM/diffusion 等 | 官方 support matrix |
| 硬件覆盖 | SM100、Ascend 950 | NVIDIA、AMD、Intel、CPU 与多类插件 | NVIDIA、AMD、TPU、Intel、Apple、Ascend 等 | NVIDIA GPU |
| 在线 API | 无 | OpenAI、Anthropic Messages、gRPC | 有，生态完整 | LLM API，可接 Triton/Dynamo |
| P/D/Encode disaggregation | engine hooks，服务层未开源 | 已支持 | 已支持并有 llm-d/Dynamo 等编排 | 已支持 |
| Speculative decoding | DSpark confidence scheduler | n-gram、suffix、EAGLE、DFlash 等 | SpecForge 等 | 多种方案 |
| 核心优势 | CED/CSA2/cache/DSpark/EPLB 深度定制 | 广泛兼容与社区规模 | Agent workload、前缀复用和 rollout 生态 | NVIDIA kernel 与部署整合 |
| 当前主要风险 | 首发、模型/硬件窄、缺 serving 层 | 通用性带来复杂度 | 组件多、调优面广 | NVIDIA 锁定与工程复杂度 |

竞品事实分别来自 [vLLM README](https://github.com/vllm-project/vllm/blob/main/README.md)、[SGLang README](https://github.com/sgl-project/sglang/blob/main/README.md) 和 [TensorRT-LLM README](https://github.com/NVIDIA/TensorRT-LLM/blob/main/README.md)，检索于 2026-10-21。

### 6.1 适合直接采用的情况

- 目标就是 DeepSeek-V4.1-Flash；
- 有 SM100 或 Ascend 950；
- 团队能补 API、路由、KV store 与运维控制面；
- 需要研究或复用 DSpark、SWA replay、EPLB 的实现；
- 愿意跟随一个尚无稳定 tag 的快速演进项目。

### 6.2 暂不适合的情况

- 想在常见消费级 GPU、H100/H200、AMD 或 CPU 上开箱运行；
- 想用一个 server 托管几十种模型；
- 需要 OpenAI-compatible API、鉴权、流式输出和生产监控开箱可用；
- 把 README 曲线当作无需复测的容量规划依据；
- 没有能力维护模型专用 kernels 和环境变量密集的运行配置。

### 6.3 如果目的是学习，应该读哪些文件

最有价值的阅读顺序：

1. `README.md` 与 `doc/inference_deployment_qa.md`：先划清开源边界；
2. `deepinfer/entrypoints/llm.py`：外部调用面；
3. `deepinfer/engine/llm_engine.py`：生命周期与 step；
4. `csrc/engine/scheduler.hpp`、`sequence.hpp`：请求状态机；
5. `deepinfer/worker/worker.py`：ZOS；
6. `csrc/engine/mtp_varlen.hpp`：DSpark hardware-aware scheduler；
7. `deepinfer/model_executor/models/mtp/dflash.py`：draft 模型与 confidence；
8. `deepinfer/worker/cache_engine.py`：V4.1 cache 物理布局；
9. `deepinfer/model_executor/eplb/*`：expert 动态重排；
10. `examples/README.md`、`benchmark.py`、`plot_pareto.py`：性能口径。

## 七、它对推理系统演进意味着什么

### 7.1 推理框架正在从“通用执行器”变成“模型的另一半”

过去常把模型和 serving engine 画成清晰两层：模型给出算子图，框架负责 batching、KV cache 和通信。DeepInfer 展示的是更强的耦合：

- CED 决定哪些层在 prefill 真正执行；
- CSA2 决定不同层能否共享 KV 与 indices；
- FP4/MXFP8 决定 cache 每 token 的物理字节；
- DSpark confidence 决定 scheduler 给每个请求多少 target compute；
- bounded replay 决定 persistent cache 中什么值得保存；
- EPLB 根据真实流量改变 expert 的物理副本。

推理系统不再只是忠实执行模型，而是在运行时继续完成模型设计。

### 7.2 Scheduler 开始消费“模型的不确定性”

传统 scheduler 主要看长度、到达时间、显存和优先级。DSpark 增加了一个新信号：**模型自己预测的接受概率**。

这可能代表一条更广的路线：未来 runtime 可以消费模型提供的计算价值估计，例如：

- 继续推理一层的边际收益；
- 某个 retrieval branch 的命中概率；
- 某个 expert、视觉 crop 或 tool call 的预期价值；
- 更高 reasoning effort 是否值得当前延迟与算力。

[推断] DeepInfer 的长远意义可能不是某个 benchmark，而是把“质量概率 × 硬件成本曲线”做成通用 runtime primitive。

### 7.3 持久 KV 的问题本质是数据生命周期，不只是压缩率

官方部署材料指出：global KV 有数天的长尾复用，SWA KV 只有分钟级会话内复用。V4.1 不再把两者都塞进长 TTL SSD，而是：

- global KV 进入长期 3FS；
- SWA 留在短 TTL host memory pool；
- miss 用 bounded replay 兜底。

这是一条普适系统原则：**存储层级应匹配数据的复用半衰期，不能只按数据类型统一落盘。**

### 7.4 开源策略也值得读懂

DeepSeek 公开了最能展示模型系统协同、也最有研究价值的 engine core；同时把与内部基础设施绑定最深的路由、存储和运维控制面留在内部。

这既不是“只开玩具”，也不是“完整开源生产栈”。更准确的说法是：

> DeepInfer 公开了生产推理系统的计算内核和状态机，并把数据中心级 serving 平面留作外部依赖。

### 7.5 局限

1. **版本太新**：3 个 commits、无 tag，无法从历史判断维护节奏与兼容承诺。
2. **硬件门槛高**：README 只承诺 SM100 与 Ascend 950。
3. **服务面不完整**：用户仍需自行实现或整合 API、路由、缓存服务和观测。
4. **模型专用性强**：cache layout 和 runtime 深度编码 V4.1 结构。
5. **性能尚待独立复现**：图表与线上数字均来自 DeepSeek；本文引用的图中坐标、`nextn=3`、75% acceptance 与冗余 expert 变化属于视觉读图，缺少 raw JSON 精确复算。
6. **近似算法有能力边界**：SWA replay 与稀疏 selection 在极端输入上可能退化。
7. **文档存在首发漂移**：中英文 EPLB 数字不一致；生产 compute-quota 机制也不在源码中。
8. **公开工程治理仍早期**：无公开 CI workflow，issues 在 GitHub API 中处于关闭状态，社区协作方式尚不清晰。

### 7.6 思考与追问

1. DeepSeek 会不会把 P/D engine 子类、3FS client 或 load balancer 继续拆仓开源？
2. Production 的 compute-quota scheduler 是否会回流当前 C++ Scheduler？
3. DSpark 的 Sequential Temperature Scaling 参数是否包含在 checkpoint 中？源码默认 temperature=1.0 与生产校准值差多大？
4. 变长验证在真实 mixed workload 中，质量、吞吐和尾延迟如何三维权衡？
5. Batch-invariant inference 的吞吐代价是多少？它是否应成为线上可审计推理的默认能力？
6. SWA Bounded Replay 在 1M context 的针尖检索、频繁 cache-resume 与恶意边界输入上会如何失效？
7. Ascend 950 路径与 SM100 能否做到相同输出、相同 acceptance 与相近 utilization？
8. Wide-EP 的收益中，有多少来自 EP 宽度，有多少来自更多冗余 experts？
9. 如果把 DeepInfer 的 DSpark scheduler 抽成通用接口，vLLM/SGLang 能否直接消费其他模型的 confidence head？
10. 当模型结构越来越为 serving 反向设计，通用推理框架会走向插件化，还是每家 frontier lab 都会维护自己的专用 engine？

## 资料来源

### 一手来源

1. [DeepInfer GitHub repository，固定 commit `774ce244`](https://github.com/deepseek-ai/DeepInfer/tree/774ce244b87cc0eb8d4b94ab9f5de2ab22049f01)，访问于 2026-10-21。
2. DeepSeek-AI, [DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression](https://arxiv.org/abs/2609.19969), 2026。
3. Cheng et al., [DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation](https://arxiv.org/abs/2607.05147), 2026。
4. DeepSeek, [DeepSeek V4.1 Flash 大规模推理部署实践](https://zhuanlan.zhihu.com/p/2095560295930508953)，访问于 2026-10-21。
5. [DeepSeek-V4.1-Flash-1017 Model Card](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)，访问于 2026-10-21。
6. [vLLM README](https://github.com/vllm-project/vllm/blob/main/README.md)，访问于 2026-10-21。
7. [SGLang README](https://github.com/sgl-project/sglang/blob/main/README.md)，访问于 2026-10-21。
8. [TensorRT-LLM README](https://github.com/NVIDIA/TensorRT-LLM/blob/main/README.md)，访问于 2026-10-21。

### 二手来源

9. MarkTechPost, [DeepSeek Open-Sources DeepInfer, the Inference Framework Behind DeepSeek-V4.1-Flash](https://www.marktechpost.com/2026/10/20/deepseek-deepinfer-open-source-inference-framework), 2026-10-20。仅用于核对公开讨论覆盖面，关键结论均回到一手材料复核。

### 检索说明

- 联网搜索、网页读取、公开仓库读取优先通过项目 `eacli` Token Plan 能力完成。
- eacli 对两篇 arXiv HTML 的读取在 32 KB 处截断，无法覆盖后半部分 DSpark 与 inference system 章节；在已确认论文 ID 和 URL 后，使用 arXiv HTML 做最小直连补读。该降级只用于补齐同一原始论文，不引入替代来源。

