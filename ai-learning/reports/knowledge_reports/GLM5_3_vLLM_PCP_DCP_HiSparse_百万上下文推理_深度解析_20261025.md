---
title: "GLM-5.3 在 16×H200 上的 PCP、DCP 与 Hybrid HiSparse：百万上下文推理的机制拆解与口径核验"
domain: "ai-learning"
report_type: "概念深度解析"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["vLLM", "GLM-5.3", "context-parallel", "DCP", "PCP", "HiSparse", "P-D-disaggregation", "long-context", "agent-serving"]
---

# GLM-5.3 在 16×H200 上的 PCP、DCP 与 Hybrid HiSparse：百万上下文推理的机制拆解与口径核验

> **一句话结论**：vLLM 团队用「prefill 侧把长提示按 token 切开（PCP）+ 把 KV cache 按 token 分片（DCP）、decode 侧把 KV 的常驻位置做成可分层的（Hybrid HiSparse）」这套组合，在 16×H200（两台 8 卡节点）上把 GLM-5.3 的 1M token 上下文服务跑了起来，并在其自建的 AgentX 回放基准上报告「相同吞吐下每用户交互速度 1.7–3.2×」；这个数字是 **项目自报、限定在 prefill 受限区间（c≤32）与 142K 上下文扫描内** 的交互性比值，不是端到端吞吐提升，也不是独立验证结论。

> **阅读边界**：本文以 vLLM 官方博客 Part 2（2026-10-23）为主线，配合 Part 1（2026-09-08）、vLLM 官方 Context Parallel 文档、vLLM DCP 博客、vLLM 官方 GLM-5.3 recipe、vLLM 官方 GitHub RFC，以及 GLM-5.3 的官方模型材料（z.ai 博客、智谱开放文档、HuggingFace 模型卡、GLM-5 技术报告）与 SemiAnalysis InferenceX 的 AgentX 方法学。所有性能数字均为 **vLLM / SemiAnalysis 一方产出**，本文只做机制解释、口径重算与外推边界标注，不构成独立复现。

---

## 目录

1. [原文在回答什么问题](#1-原文在回答什么问题)
2. [术语表：把黑话翻译成人话](#2-术语表把黑话翻译成人话)
3. [数据流：一次 1M token 的 agent 请求如何走完全程](#3-数据流一次-1m-token-的-agent-请求如何走完全程)
4. [机制一 PCP：切的是 query，不是 head](#4-机制一-pcp切的是-query不是-head)
5. [机制二 DCP：把 KV 也切开](#5-机制二-dcp把-kv-也切开)
6. [机制三 Hybrid HiSparse：让 KV 在显存与主机内存之间流动](#6-机制三-hybrid-hisparse让-kv-在显存与主机内存之间流动)
7. [拓扑：16×H200 到底怎么摆](#7-拓扑16h200-到底怎么摆)
8. [关键 benchmark 与逐列口径](#8-关键-benchmark-与逐列口径)
9. [硬件与软件前提清单](#9-硬件与软件前提清单)
10. [对比基线与公平性评估](#10-对比基线与公平性评估)
11. [1.7–3.2× 的口径重算与交叉核验](#11-171–32-的口径重算与交叉核验)
12. [三层归因：模型创新 / 推理引擎优化 / 硬件调优](#12-三层归因模型创新--推理引擎优化--硬件调优)
13. [对 Agent 长上下文工作负载与 harness 设计的可迁移启示](#13-对-agent-长上下文工作负载与-harness-设计的可迁移启示)
14. [Limitations](#14-limitations)
15. [思考与追问](#15-思考与追问)
16. [附录 A：来源清单与口径标注](#附录-a来源清单与口径标注)
17. [附录 B：复现命令与版本锚点](#附录-b复现命令与版本锚点)

---

## 1. 原文在回答什么问题

### 1.1 Part 2 的问题设定

Part 1（2026-09-08）解决的是「**单个 8×H200 节点内存不够放 KV**」：Hybrid HiSparse 让 GLM 5.3 在 8 卡节点上首次能跑满 1M 上下文。Part 2（2026-10-23）把问题换成：**Agent 负载下，prefill 会成为整条链路的瓶颈，而单个节点的权重又吃掉了大部分显存**。

原文自己给出的两条约束线是：

- **KV cache 内存线**：H200 上 GLM-5.3 的权重占了每张卡的大部分显存，留给长上下文 KV 的空间很少。
- **prefill 速度线**：agent 每一轮都会把更多工具输出和文件内容塞进 prefill，负载上来之后 prefill 引擎成为整个部署的瓶颈。

所以 Part 2 的答案不是单点优化，而是 **一次部署形态的重排**：把 16 张 H200 拆成「1 个 prefill 节点 + 1 个 decode 节点」，prefill 节点用 PCP×DCP 提速并省显存，decode 节点用 Hybrid HiSparse 换并发。

原文 TL;DR 的四条（一手，vLLM 自述）：

1. **PCP** 把每条 prompt 按 token 而不是按 head 切到多张卡上，对 GLM-5.3 的稀疏注意力比 tensor parallel 更合适；
2. **DCP** 把 prefill 引擎的 KV cache 按 token 分片，使 1M 上下文能装进 prefill 节点；
3. **Hybrid HiSparse** 让 decode 把 KV 留在主机内存，使 1M token 的请求能被服务；
4. 在 AgentX 上，PCP8×DCP8 prefill + Hybrid HiSparse decode 在**相同吞吐**下给出数据并行部署 **1.7–3.2× 的每用户速度**，并且是原文测试过的配置中**唯一**能服务 1M token 上下文的配置。

### 1.2 为什么「不是 TP 也不是 DP」

原文给了一个很清楚的二选一论证：

| 方案 | 一个长 prompt 的注意力怎么算 | KV 放在哪 | 死结在哪 |
|---|---|---|---|
| **DP8** | 整条 prompt 落在**一张**卡上，另外 7 张卡闲着 | 必须全部塞进这一张卡 | 长 prompt 的 TTFT 无法被摊薄；单卡装不下就不行 |
| **TP8** | 64 个 attention head 切给 8 张卡，每卡算 8 个 head | MLA 的 latent KV 被 **64 个 head 共享**，每张卡都存**完整**一份 cache | 8 张卡各存整份 KV 却只服务 8/64 的 head；indexer 完全没被切分，其**二次方**成本在每张卡上重复一遍 |

原文因此给出一句总结：两种方案都 **无法在不重复保存整份 KV 的前提下把一条长 prompt 的注意力摊到 8 张卡上**。于是：

- **PCP 解决「算」**：把 query（也就是待计算的 token）按 token 切开。
- **DCP 解决「存」**：把 KV 也切开。

原文特别加了一句容易被忽略的澄清：**「PCP 切 query；DCP 切 KV。名字是历史包袱。」** DCP 当初是为 decode 设计的（decode 每步只有一个 query token，KV 是唯一值得切的东西）；PCP 当初是为 prefill 设计的（prompt 里大量 query token 才是工作量所在）。但在本文描述的部署里，**两者同时跑在 prefill 引擎里**。

### 1.3 与模型侧的关系

GLM-5.3 官方材料给出的关键事实：

- GLM-5.3 **与 GLM-5.2 使用同一套基座模型，全部提升来自后训练**（智谱官方文档、z.ai 官方博客、HuggingFace 模型卡一致表述）。
- 官方支持 **1M 上下文窗口、最大输出 128K**；思考功能始终开启，`reasoning_effort` 支持 `low / high / max`（默认 `max`）。
- vLLM 官方 recipe 给出规模：GLM-5.3 是 **约 743B 参数的 MoE（激活 39B）**，默认 `zai-org/GLM-5.3` checkpoint 已是 **原生 FP8**，BF16 版本另存为 `GLM-5.3-BF16`。
- GLM-5 技术报告（arXiv:2602.15763）说明 GLM-5 系列采用 **DSA**（稀疏注意力）以降低训练与推理成本并保持长上下文保真度。

也就是说：**模型侧提供的是「稀疏 + 1M 原生窗口」，引擎侧提供的是「让稀疏在受限显存里真的跑得动」**。这两者的耦合点非常具体：稀疏注意力的 indexer 只挑 top-2,048 个 token attended，engine 才能据此只让这部分 KV 常驻显存 —— 这正是 HiSparse 成立的前提。

---

## 2. 术语表：把黑话翻译成人话

| 术语 | 白话解释 | 技术定义 / 出处 |
|---|---|---|
| **MLA**（Multi-head Latent Attention） | 64 个注意力头共用一份「压缩过的 KV」 | 把 K/V 压成一个低秩 latent 向量供所有 query head 共享，等效只有 1 个 KV head（vLLM DCP 博客） |
| **DSA / 稀疏 MLA** | 每个 token 只「看」历史里被挑中的 2,048 个 | indexer 对每个历史 token 打分，选 top-k 后才做 attention（Part 2 脚注 1） |
| **Indexer** | 决定「该看哪 2,048 个 token」的轻量打分器 | Part 2：它对每个更早的 token 打分，成本随 prompt 长度**二次方**增长，且在 TP 下**不被切分** |
| **IndexShare** | 4 层稀疏 MLA 只配 1 层 indexer | GLM-5.3 的结构，使 indexer KV 相对小（Part 1） |
| **TP / DP / EP** | 切头 / 切请求 / 切专家 | Tensor Parallel 切 attention head；Data Parallel 一个请求一张卡；Expert Parallel 切 MoE 专家 |
| **PCP**（Prefill Context Parallelism） | 把一条长 prompt 的 token 分给多卡分别算 query | vLLM 文档称两种策略（partial query + full KV、partial query + partial KV + ring attention）**仍在开发中** |
| **DCP**（Decode Context Parallelism） | 把 KV cache 按序列维（token）分片给多卡 | 官方文档用 `-dcp <size>`；MLA 下 `tp_size ≥ dcp_size` 且整除 |
| **HiSparse / Hybrid HiSparse** | 稀疏 KV 的「显存不够就放主机内存」策略 | indexer 选中的 token 留 GPU，其余下放 CPU；Hybrid 版本在显存宽裕时**尽量不放** |
| **HMA**（Hybrid Memory Allocator） | 统一分配显存/主机内存块的池子 | hot buffer 与常驻页来自同一个池、同一个 KV tensor，所以对 sparse MLA kernel 来说 hot 页就是普通页（Part 1） |
| **Hot buffer** | 显存里一小块「当前正在被读」的 KV 行缓存 | 默认每请求 2× top-K 行；带 MTP 时需 `(num_speculative_tokens + 2) × top-K`（Part 1） |
| **P/D 分离** | prefill 节点与 decode 节点分开部署 | prefill 算完把 KV 交给 decode；本文用 llm-d 路由 + NIXL connector |
| **NIXL connector** | 跨节点搬 KV 的通道 | 在 P/D 之间把 prefill 的分片 KV **重排**成 decode 需要的整段 paged layout |
| **MTP / MTP3** | 多 token 预测投机解码，草稿 3 个 token | Part 2 全程使用 MTP3 |
| **Prefix caching / CPU KV offload** | 把完成的 KV 前缀搬到主机内存，下轮复用 | prefill 节点 512 GiB；decode 每 rank 16 GiB |
| **TTFT** | 首 token 时间 | agent 场景里用户感知的「等待」 |
| **Interactivity（交互性）** | 每用户每秒看到的输出 token 数 | 本文口径为 AgentX 的 **P90 E2E 归一化 output tok/s per user** |
| **Logical tok/s per GPU** | 计入前缀缓存命中输入 token 的「逻辑」吞吐 | (输入+输出 token，含 prefix-cached)/GPU 数 |

---

## 3. 数据流：一次 1M token 的 agent 请求如何走完全程

```
                    ┌──────────────── 16×H200 部署（两个 8 卡节点）────────────────┐
                    │                                                          │
  agent 客户端 ──► llm-d（前缀感知路由）──►  prefill 节点（8×H200）            │
                    │                            PCP8 × DCP8 × EP8            │
                    │                            ├ PCP：按 token 切 query      │
                    │                            │   （16 段 V 形配对负载均衡）  │
                    │                            ├ DCP：KV 按 token round-robin │
                    │                            │   分到 8 卡（常驻量 ÷8）      │
                    │                            └ 512 GiB CPU KV offload        │
                    │                                    │  产出 KV（分片布局）      │
                    │                                    ▼                       │
                    │                          NIXL connector：把 KV 重排为      │
                    │                          decode 需要的整段 paged layout     │
                    │                                    ▼                       │
                    └──◄── 流式 token ──────────  decode 节点（8×H200）        │
                                                  8 个 DP rank × EP8           │
                                                  Hybrid HiSparse：             │
                                                  ├ 48 GiB/rank host pool      │
                                                  └ 16 GiB/rank 普通 offload   │
                                                  └ MTP3（草稿 3 token）        │
                    └──────────────────────────────────────────────────────────┘

单层、单步的注意力数据流（prefill 引擎内，PCP8 × DCP8）：
  每张卡只持有第 i mod 8 个 token 的 KV（持久态，分片）
  每张卡算自己的 query 分片（chunk g 与 chunk 15−g）
  每层开始 → all-gather 各分片 → 临时拼出「全上下文副本」→ 为自己的 query 做 attention
            → 释放临时副本（只有持久 KV 被 ÷8）
```

关键时序（原文 Figure 3 的说明）：`C` = 之前已 prefill 的 token，`N` = 本步 token，上限 16,384（prefill 引擎的 `max-num-batched-tokens`）；1M token 的 prompt 需要 **64 步**，每步 `C` 增加 `N`。**关键细节**：DCP 实际是逐 token round-robin 发牌（token i 落在 GPU `i mod 8`），所以「哪张卡存哪些 token」与「哪张卡算哪些 query」的布局**并不对齐** —— 这正是每层都需要 all-gather 的原因。

---

## 4. 机制一 PCP：切的是 query，不是 head

### 4.1 做法

在 8×H200 的 prefill 引擎里，PCP8 把每条 prompt 按 token 切成 8 份，**每张卡算其中 1/8 的 query，但用全部 64 个 head**。

朴素切法会严重不均衡：因果注意力下，靠后的 token 要看前面所有 token，所以拿到 prompt 尾部的卡干的活最多。PCP 的做法是：**把 prompt 切成 16 段，两两配对** —— GPU `g` 拿第 `g` 段（靠前）和第 `15−g` 段（靠后），于是每张卡都拿到「便宜 token + 昂贵 token」的同款组合。原文用 V 形图案表示这个分布。

这个「负载均衡分片」直接引自论文 **Context Parallelism for Scalable Million-Token Inference**（arXiv:2411.01783，Yang 等，v3 2025-04-21），该论文报告在最多 128 张 H100、16 节点上实现近线性扩展，1M 上下文 prefill 77s（93% 并行效率、63% FLOPS 利用率），128K prefill 3.8s，并提出 pass-KV / pass-Q 两种无损精确 ring attention 变体。

### 4.2 为什么对稀疏 MLA 特别有效

原文给了两组可核对的数字：

**（a）算术强度（arithmetic intensity）**

每个 query，稀疏 MLA 要读 2,048 行被选中的 KV，每行 660 字节（FlashMLA `fp8_ds_mla` 格式的 656 字节 FP8 KV + 4 字节 index），合计约 1.35 MB。

- 8 个 head：35.7 MFLOPs / 1.37 MB ≈ **26 FLOPs/byte**
- 64 个 head：285 MFLOPs / 1.49 MB ≈ **191 FLOPs/byte**
- H200 SXM 的平衡点：989 dense BF16 TFLOP/s ÷ 4.8 TB/s ≈ **206 FLOPs/byte**

也就是说：TP8 下每张卡读到的每一行 KV 只服务 8 个头，内存带宽先撞墙（26 << 206）；PCP8 下同一行服务全部 64 个头，191 已经很接近 206，H200 重新变成 compute-bound。

**（b）indexer 的二次方成本**

indexer 的成本随 prompt 长度**二次方**增长，而稀疏 MLA 的注意力成本只随长度**线性**增长（因为每个 query 固定 attend 2,048 个 token）。原文的交叉点结论：

| 方案 | indexer 成本超过 sparse MLA 的 prompt 长度 |
|---|---|
| TP8（indexer 在每张卡上重复） | 约 **32K** token |
| PCP8（indexer 不被复制） | 约 **256K** token |

这就是「长 prompt prefill 阶段 PCP 收益最大」的机制性原因。

### 4.3 PCP 自己的两个代价

原文没有回避：

1. **权重不再切分**：每张卡持有全部注意力权重，MoE 专家则仍以 EP8 切分在 8 张卡之间；
2. **KV 仍然被复制**：新产生的 KV 每层都要 all-gather，因此每张卡最终**仍然存着完整的一份 KV cache**。

**所以 PCP 只解决「算得快」，不解决「装得下」** —— 后者是 DCP 的活。

---

## 5. 机制二 DCP：把 KV 也切开

### 5.1 显存账（可自行验算）

原文脚注 3 给出的每 token KV 字节数：

| 组成 | 每 token 字节 |
|---|---|
| 78 层 × 656 B 的 MLA KV | 51,168 B |
| 21 层 indexer keys（128 FP8 值 + 4 B scale） | 2,772 B |
| MTP 层 | 788 B |
| **合计** | **54,728 B** |

- 1,048,576 token × 54,728 B = 54,728 MiB ≈ **53.4 GiB**
- H200 上每卡给 KV 留的空间约 **15 GiB**（原文口径）
- DCP8 之后每卡只存 1/8：**53.4 / 8 = 6.7 GiB** → 装得下。

**推导**：743B 参数的 FP8 权重约 743 GB，摊到 8 卡约 93 GB/卡；H200 SXM 每卡 141 GB，减去权重剩约 48 GB，再减激活与工作区，落到「约 15 GiB 可用 KV」在量级上自洽（此为[分析者推导]的粗算，官方未逐项披露显存分解）。

### 5.2 两种方向相反的数据流

DCP 的关键设计是：**「谁去谁那里」随角色反转**。

- **在 decode 里**：把 query 发到 KV 那边。每张卡只对自己那 1/8 的 KV 分片做 attention，然后用 **log-sum-exp 合并**各卡的部分结果。vLLM DCP 博客给出的节奏是 `AllGather Q → Compute → AllGather + ReduceScatter`（`cp_lse_ag_out_rs`），即用 online-softmax 技巧把各分片的 LSE 与部分输出重加权合并，再 ReduceScatter 把结果发回各自负责的 head 切片。
- **在 prefill 引擎里（本文的用法）**：方向反过来。每层都把各分片 **all-gather 成一份临时的全上下文副本**，各卡为自己的 query 做 attention，然后把临时副本丢掉。**只有持久化 KV 被 ÷8。**

### 5.3 DCP 的代价

all-gather 不是免费的：**每层都要把已缓存的整段上下文重新发一遍**，成本随上下文长度增长。原文用「同一个 2K-token prefill chunk，在同一个 8×H200 PCP8 引擎上，开/关 DCP8、等缓存上下文」来隔离这个开销：

| 缓存上下文长度 | DCP8 每步额外开销 |
|---|---|
| ≤ 64K token | 约 **6%** |
| 248K token | 约 **15%** |

原文的定性结论：**超过约 250K token 后，PCP8 单独已经装不下 KV cache**，此时 DCP 不再是「开销」，而是「让长 prompt 成为可能的前提」。

原文还留了一句明显的待办：这个 all-gather 可以与上一层的计算重叠，**他们正在做这个优化**（即当前数据尚未包含该优化收益）。

### 5.4 与官方文档的关系（重要的一致性检查）

vLLM 官方 Context Parallel 文档对 DCP 的表述是面向 decode 的：`-dcp <size>` 减少 KV 复制，`size` 应落在 `[1, tp_size/H]`（GQA 下），MLA 下要求 `tp_size ≥ dcp_size` 且整除；文档同时指出 **PCP 的两种策略「都还在活跃开发中」**。

对照 Part 2 的实际用法可以发现两处 **文档与博客之间的成熟度差**：

1. Part 2 在 **prefill 引擎内部**同时使用 PCP8 与 DCP8，这比文档中「PCP 仍在开发」的描述更激进；
2. 文档给出的 DCP 语义是 decode 场景的（发 query 到 KV 那边 + LSE 合并），Part 2 则在 prefill 侧用「all-gather 临时全量副本」的反向实现。

结论：**博客展示的是该组件最前沿的一种组合，不等于官方文档中已稳定承诺的通用能力**；文档页本身也处于变动中（例如新增了 `effective_attention_block_size` 这种「含 DCP 的等效块大小」字段说明）。

---

## 6. 机制三 Hybrid HiSparse：让 KV 在显存与主机内存之间流动

### 6.1 为什么稀疏让「分层」成为可能

- **Preemption（抢占）**：踢掉某请求的 KV，之后重新 prefill —— 该请求要**重付一次完整 TTFT**。
- **常规 Offloading**：把块搬到主机内存，但稠密注意力要求每个 token 都在显存里，于是**并发数仍被显存卡死**。
- **HiSparse**：因为稀疏 MLA 只 attend indexer 选中的 top-K，所以**除选中 token 外的全部 KV 都可以下放 CPU**；indexer 的 KV 仍留在 GPU（它还要给所有历史 token 打分），但由于 IndexShare（每 4 层稀疏 MLA 才 1 层 indexer），indexer KV 本身小得多。

### 6.2 Hybrid 的关键设计：只有「有压力时」才付代价

- **Full residency**：全部稀疏 MLA KV 留在 GPU，同时把已完成的 prefix 页**预先**物化到主机内存。
- **Mixed residency**：请求尾部留在 GPU，较老的页只在 CPU，indexer 想要的那几行放在 **hot buffer** 里；block table 里真实块与空占位符并存，尾部永不驱逐。一个融合 kernel 一次解析 top-K：常驻 token 原地读、hot token 读取并刷新 LRU、miss 则从 pinned host memory 拷贝**单行**进 LRU 槽位。**decode 路径上没有任何一步等 CPU 决策，因此保持 CUDA-graph 可捕获。**
- **No residency**：新请求复用的前缀只存在于 CPU，先以占位符 + hot page 起步，行随 indexer 选中而到达 —— **只为模型真正要看的部分付费**。

### 6.3 三个容易被误读的技术点

1. **hot buffer 不是独立分配**：hot buffer 页就是普通 KV block，从 HMA 的同一个池里租借，与常驻页共享**同一个 KV tensor**，所以对 sparse MLA kernel 来说它「看起来就是普通页」；一个请求释放的块可以直接变成另一个请求的 hot buffer 容量。
2. **提前准备**：可缓存 prefix 页一旦完成，HiSparse 就在**继续用 GPU 服务它的同时**排队把它拷到主机内存；这样显存紧张时该页可以立刻释放 GPU 槽位，无需二次拷贝。
3. **热/冷的判定粒度是页**，但 **hot 页里的 token 可以来自许多不同的 CPU 块**，因此压缩收益横跨很长的上下文跨度。

另外两个部署相关的细节：`hisparse-glm` 分支把所有稀疏 MLA 层的拷贝合并为 forward 之后的一次 launch，拷贝排在模型 GPU stream 上以保持同步简单；因为 MLA 的 KV 在各 TP rank 上相同，**pinned host 池按 DP 副本分配、由该副本内的 TP rank 共享**（TP rank 0 写共享副本，所有 rank 可读，用 CUDA event 保序）。hot buffer 默认每请求 **2× top-K 行**；**带 MTP 时 hot buffer 必须一次容纳全部验证 token**，即 `(num_speculative_tokens + 2) × top-K`。

> **注**：HiSparse 目前**仅在 NVIDIA GPU 上实现**（Part 1 明确说明）。

---

## 7. 拓扑：16×H200 到底怎么摆

```
┌──────────────────── 节点 A：Prefill（8×H200）────────────────────┐
│  PCP8（query 按 token 切，16 段 V 形配对）                          │
│  × DCP8（KV 按 token round-robin，持久 KV ÷8）                     │
│  × EP8（MoE 专家切 8 份）                                         │
│  FP8 KV cache                                                      │
│  512 GiB CPU KV offload（后续轮次复用前缀）                        │
│  max-num-batched-tokens = 16,384（1M prompt = 64 步）              │
│  --prefill-context-parallel-size 8                                  │
│  --decode-context-parallel-size 8                                   │
│  --dcp-comm-backend ag_rs                                           │
│  --enable-expert-parallel                                           │
│  --attention-config '{"sparse_mla_force_mqa":true}'                 │
└───────────────────────────┬────────────────────────────────────────┘
                            │ NIXL connector：KV 布局重排（分片 → 整段 paged）
                            ▼
┌──────────────────── 节点 B：Decode（8×H200）─────────────────────┐
│  8 个 DP rank（每 rank 一张卡）× EP8                                │
│  Hybrid HiSparse：48 GiB/rank host pool + 16 GiB/rank 普通 offload  │
│  （合计 8×48 + 8×16 = 512 GiB 主机内存，与 prefill 节点一致）        │
│  MTP3 投机解码（草稿 3 token）                                      │
│  → decode 并发上限由主机内存决定，而非 HBM                          │
└────────────────────────────────────────────────────────────────────┘
```

**关键点**：

- **为什么是「一台 prefill + 一台 decode」**：prefill 与 decode 的 SLO 不同（前者看 TTFT，后者看每用户交互速度），官方文档也明确「需要为两者分别实现 context parallel」。分离后，prefill 侧可以用 PCP 摊薄 TTFT，decode 侧可以用 HiSparse 换并发。
- **路由必须前缀感知**：llm-d 路由要按前缀把请求送到能复用已缓存前缀的引擎；NIXL connector 在两节点之间搬 KV，并且要把 prefill 的「分片布局」转成 decode 需要的「整段 paged layout」（含 MTP 层）。
- **compose 才是工程难点**：原文用一整节讲这件事 —— 每一个特性都改变 KV 的布局、调度或搬运方式，组合起来必须既正确又快。原文特别提到 **Model Runner V2** 这个新的模块化执行核心：把模型特有状态挡在通用执行路径之外，并让投机解码**不产生 CPU–GPU 同步**；Hybrid HiSparse 就建立在它之上。

---

## 8. 关键 benchmark 与逐列口径

### 8.1 基准方法（SemiAnalysis InferenceX AgentX）

| 项 | 内容 |
|---|---|
| 数据来源 | 393 个 Claude Code 会话（opt-in 内部 trace 语料），原始 prompt/代码/工具载荷被移除，保留请求长度与前缀复用结构 |
| 规模 | median 输入 **142k token/请求**，median 输出 **444 token/请求**；44% 会话含 subagent |
| 回放方式 | 闭源（closed-loop）回放：并发客户端数决定负载；合成 token 填充，seed 固定采样与起点 |
| 计量窗口 | 每个配置 1 小时 profiling（warmup 不计入）；每个并发点**重新起一套部署** |
| 投机解码 | AgentX **强制**使用 SPEED-Bench 测得的固定 acceptance length（每模型/投机器/草稿长度/思考模式组合各测一次） |
| DRAM 限制 | 无标准化 DRAM 的服务器上限 3 TB；每配置只能按 GPU 配额比例访问 |
| 明确边界 | AgentX 只测**服务系统性能**，合成载荷不支持模型质量评估 |

### 8.2 Part 2 的实测口径（一手，vLLM 自报）

| 指标 | 原文定义 |
|---|---|
| 吞吐 | **logical tok/s per GPU** = (输入 + 输出 token，**含 prefix-cached 输入**) ÷ 16 张卡 |
| 交互性 | **AgentX 的 P90 E2E 归一化 output tok/s per user**（Figure 5 的横轴） |
| TTFT | 中位 TTFT |
| 扫描点 | 142K 上下文限制下 c8–c64；1M 上下文限制下 c8–c32 |
| 投机解码 | MTP3，acceptance length **合成固定为 2.99**，使各配置的投机收益相同 |
| 每点独立 | 每个并发点用一套全新部署；空心点表示落在自己配置的 Pareto 前沿之外 |

### 8.3 原文报告的结果

| 观察 | 数值（vLLM 自报） | 条件 |
|---|---|---|
| prefill 方案对比 | PCP8×DCP8 相对 DP8，在**相同吞吐**下每用户交互性 **1.7–3.2×** | HiSparse decode 双方都开；**c ≤ 32（prefill 受限区）**；142K 扫描内 |
| TTFT | 中位 TTFT 从 **1.5–5.2 s 降到 0.8–0.9 s** | 同上 |
| decode 方案影响 | 在 c≤32 时影响很小：c8、c16 两个 PCP8×DCP8 配置相差几个百分点，c8 时纯 offload decode 甚至略好 | 同上 |
| 高并发 | c64 时 HiSparse decode 几乎把吞吐**翻倍**到 **8,340 logical tok/s/GPU @ 29.6 tok/s/user**，其他配置掉到 **1–2 tok/s/user** | 142K 扫描 |
| 1M 上下文 | DP8 的单个 prefill rank 装不下一个 1M token 请求，纯 offload 的 decode rank 同样装不下 → 两者都需要 | c8–c32 |
| DCP 开销 | ≤64K 上下文约 **6%/步**，248K 时约 **15%/步**（2K chunk，PCP8 单节点） | 独立测量 |
| PCP 计算性质 | 稀疏 MLA 算术强度 26 → **191 FLOPs/byte**（H200 平衡点 206）；indexer 交叉点 32K → **256K** | 解析计算 |

### 8.4 Part 1 的口径（不可与 Part 2 直接比较）

Part 1 用的是**另一个工作负载**：OpenHands 13 轮多轮会话，首轮 74,160 token、后续轮 753 token、固定 220 token 输出；TP8、MTP3、FP8 KV、142K 准入上限、`max_num_batched_tokens=32768`、`max_num_seqs=256`、`gpu_memory_utilization=0.92`；HiSparse 用 384 GiB pool + 128 GiB offload，基线用 512 GiB offload；交互性定义为 `1000 / mean TPOT(ms)`。**Part 1 与 Part 2 的数字不能直接对比或相加。**

---

## 9. 硬件与软件前提清单

**读懂 Part 2 的任何数字前，先确认你也有这些前提。**

| 类别 | 前提 |
|---|---|
| GPU | **16 × NVIDIA H200 SXM**（141 GB），恰好是「两台 8 卡节点」；每个引擎内部是**单机 8 卡域**（NVLink 域内通信） |
| 显存 | 每卡约 15 GiB 可用于 KV（FP8 KV cache）；权重占掉其余部分 |
| 主机内存 | **每节点 512 GiB**：prefill 侧 512 GiB CPU KV offload；decode 侧 8×48 GiB HiSparse pool + 8×16 GiB 普通 offload = 512 GiB |
| 模型 | `zai-org/GLM-5.3`（原生 FP8 checkpoint，约 743B 总参 / 39B 激活） |
| 引擎版本 | 论文结果测于 vLLM main **`9e38b4111a`**；复现 gist 固定 **`2537629eb2`**；功能需要 **vLLM ≥ v0.32.0**（镜像 `vllm/vllm-openai:v0.32.0`） |
| 关键开关 | `--prefill-context-parallel-size 8`、`--decode-context-parallel-size 8`、`--dcp-comm-backend ag_rs`、`--enable-expert-parallel`、`--attention-config '{"sparse_mla_force_mqa":true}'` |
| `sparse_mla_force_mqa` 的意义 | 不开这个 flag，prompt 短于 2,048 top-k 的 prefill batch 会走**稠密 MHA 路径**；开了才能保证「每行 KV 服务所有 head」，也就是 PCP 的算术强度收益成立 |
| 投机解码 | MTP3（草稿 3 token），acceptance length 合成固定 2.99 |
| 连接 | 节点间靠 NIXL connector 搬 KV；节点内靠 NVLink；路由靠 llm-d（前缀感知） |
| 硬件限制 | **Hybrid HiSparse 目前仅支持 NVIDIA GPU** |
| 模型侧能力 | GLM-5.3 原生 1M 上下文、128K 最大输出（智谱官方） |
| 对照参考 | vLLM 官方 recipe：GLM-5.3 FP8 单节点可放 8×H200 / 8×H20；**单机 8×B200 配 FP8 KV 可达完整 1M 上下文**；vLLM ≥ 0.28.0 |

> **注意这条对照**：官方 recipe 认为「完整 1M 上下文」在单机 8×B200 上就能达成，而 Part 2 强调要 16×H200 + PCP/DCP/HiSparse 组合。两者不矛盾但口径不同 —— **1M 的瓶颈在 B200 上是单卡 KV 容量（180 GB × 8 的 HBM 余量），在 H200 上是权重占比导致的 KV 空间 + prefill 速度**。把 Part 2 的结论推广到 B200/GB200 会得到完全不同的最优配置。

---

## 10. 对比基线与公平性评估

### 10.1 原文对齐了什么

| 变量 | 是否对齐 | 说明 |
|---|---|---|
| GPU 数量 | ✅ | 所有配置都是同一 16 张卡 |
| 主机内存 | ✅ | 两种 decode 配置都用同样的 512 GiB 主机内存 |
| 模型与量化 | ✅ | 同一 GLM-5.3、同一 FP8 KV |
| vLLM 构建 | ✅ | 同一 build（main @ `9e38b4111a`） |
| 投机收益 | ✅ | MTP3 且 acceptance length 固定 2.99，消除了「谁猜得更准」的混淆 |
| 工作负载 | ✅ | 同一 AgentX 回放集、同一并发点、同一 1 小时窗口 |
| 每点独立部署 | ✅ | 每个并发点重新起一套，避免前一点的状态污染 |

### 10.2 变化了什么

- **prefill 侧**：DP8（8 个 DP rank + EP8 + 每 rank 64 GiB CPU KV offload，合计同样是 512 GiB） ⟷ PCP8×DCP8×EP8（+512 GiB CPU KV offload）。
- **decode 侧**：纯 CPU KV offload ⟷ Hybrid HiSparse（48 GiB pool + 16 GiB offload per rank）。

### 10.3 没有对齐 / 没有对比的部分（外推边界）

1. **没有 TP8 的实测基线**。原文只在理论上论证 TP8 的两个缺陷（KV 全复制、indexer 重复），Figure 1 比较的是算术强度而非实测吞吐。**「PCP 比 TP 快多少」在这篇文章里没有实测答案。**
2. **没有与其他推理引擎对比**（SGLang、TensorRT-LLM、NVIDIA Dynamo 等），也没有与其他并行方案（ring attention、序列并行）对比。
3. **没有跨硬件对比**：只有 H200×16；B200、H20、GB200、MI300X 的结论不能直接搬（官方 recipe 显示 B200 的 1M 路径完全不同）。
4. **没有跨模型对比**：结论依赖 GLM-5.3 的**稀疏 MLA + IndexShare** 结构。稠密注意力模型没有「indexer 不被切分」这个痛点，PCP 的核心论证会失效。
5. **没有质量评估**：AgentX 只测服务性能。**「1M 上下文能被服务」≠「1M 上下文下模型质量可用」**，后者在本文所有材料中都没有数据。
6. **没有误差条 / 重复实验**：每个并发点只跑一次 1 小时，没有多次重复与置信区间，也没有报告错误率与失败请求比例。
7. **闭源回放的工作负载漂移**：AgentX 官方明确指出闭源回放下「更快的配置会完成更多请求，从而遇到略有不同的工作负载混合，低并发时最明显」。因此不同配置之间的交互性比值本身带有一定方法论噪声。
8. **DCP 的 all-gather 开销在 1M 上下文处没有被单独测量**（原文只测到 248K），而 1M 场景正是 DCP 不可替代的场景。
9. **未包含的优化**：原文明确说 all-gather 与上层计算重叠的优化「正在做」，因此当前数字是优化前的。

---

## 11. 1.7–3.2× 的口径重算与交叉核验

这是本报告最需要小心的一句话。它的完整原文口径是：

> 「Up to c32, the deployment is mostly prefill-bound, so the prefiller makes the bigger difference. With HiSparse decode in both setups, PCP8 × DCP8 prefill gives 1.7–3.2× the interactivity of DP8 at the same throughput and cuts median TTFT from 1.5–5.2 s to 0.8–0.9 s.」

### 11.1 逐项拆解

| 维度 | 口径 |
|---|---|
| 被比较的量 | **interactivity = P90 E2E 归一化 output tok/s per user**（不是端到端延迟、不是总吞吐） |
| 「×」的分母 | **同吞吐（at the same throughput）下的 DP8** —— 这是 **Pareto 前沿比较**，不是「同一负载下跑得更快」 |
| 分子 | PCP8×DCP8 prefill（**两侧 decode 都开 HiSparse**） |
| 适用范围 | **c ≤ 32**，且在 **142K 上下文扫描**内 |
| 不适用 | c ≥ 32 之后主导因素变成 decode（此时收益来自 HiSparse，不是 PCP）；**1M 扫描（c8–c32）里没有可比的 DP8 基线**（DP8 装不下） |

### 11.2 交叉核验 A：TTFT 与交互性是否自洽

- TTFT 中位数从 1.5–5.2 s 降到 0.8–0.9 s，**幅度约 1.9×–5.8×**；
- 而交互性只提升 **1.7–3.2×**。

两者方向一致（prefill 更快 → 交互更快），且交互性提升**小于** TTFT 改善幅度是合理的：交互性是端到端归一化后的输出速度，还要扣掉 decode 时间、排队与 think time。**没有出现「交互性提升超过 TTFT 改善」的物理矛盾**，这说明 1.7–3.2× 与 0.8–0.9 s 的 TTFT 数字彼此并不打架。[分析者推导]

### 11.3 交叉核验 B：c64 的两个吞吐数字

- 「c64 时吞吐几乎翻倍到 **8,340 logical tok/s/GPU**，即 16 卡合计 **133,440 logical tok/s**」；
- 同时「**29.6 tok/s/user**」，64 个用户 ⇒ **1,894 output tok/s**。

两者相差约 70 倍，不矛盾 —— 因为 **logical tok/s 把命中前缀缓存的输入 token 也计入**，而 AgentX 是多轮 agent 回放，前缀复用率极高。换句话说：**这两个指标度量的是不同的东西**（系统「处理了多少 token」vs「用户「看到多少 token」），**把 8,340 tok/s/GPU 解读为「真实算力吞吐」是错误的**。[分析者推导]

### 11.4 交叉核验 C：1M 上下文下的 KV 账

- 1M token 需要 53.4 GiB FP8 KV（54,728 B/token）；
- DCP8 后每卡 6.7 GiB，H200 每卡约 15 GiB 可用 → **单请求可行**；
- 反过来看，**若没有 DCP**（PCP8 单独）：每卡要存 53.4 GiB > 15 GiB → 不可行。
这与原文「超过约 250K token 后 PCP8 单独就装不下」的定性结论一致（250K × 54,728 B ≈ 12.8 GiB，逼近 15 GiB 上限，量级自洽）。[分析者推导]

### 11.5 交叉核验 D：DCP 开销随长度的外推

已测点：≤64K → 6%，248K → 15%。若按「开销 ∝ 已缓存上下文」近似线性外推：

- 1M（≈1024K）→ 约 **60%** 量级（4× 于 248K）。

但这**只是用两个测量区间做的粗略线性外推**，原文没有给出 1M 测点，真实曲线还会受分块、通信算法与计算重叠影响。这里也必须避免重复计数：54,728 B/token 已经是 **78 层 MLA、21 层 indexer 与 MTP 合计后的整模型 KV**，不是单层数据量。按最朴素的量级估算，1M 上下文对应整模型约 53.4 GiB 持久 KV；DCP8 若为每层重建全量上下文，每张 GPU 在最终 prefill 步跨全部层接收的远端分片约为其 7/8，即 **约 46.7 GiB 量级**，而不是「每层 53.4 GiB、合计 4.2 TB」。这个估算仍未计协议、实现是否覆盖全部组件以及通信重叠，只能说明：**1M 场景的 DCP 通信开销是这套方案最大的未量化风险之一**。[推测]

### 11.6 结论

> **1.7–3.2× 应当被读作**：「在 16×H200、AgentX、142K 上下文、c≤32 的 prefill 受限区间、**同等系统吞吐**的前提下，把 prefill 从 DP8 换成 PCP8×DCP8 之后，**用户侧感知到的输出速度**提升 1.7–3.2×，同时中位 TTFT 从 1.5–5.2 s 降到 0.8–0.9 s。」
>
> 它 **不是**：端到端吞吐提升 3.2×；不是 1M 上下文下的结果；不是跨硬件、跨引擎、跨模型的普适结论；也不是独立第三方验证的结果。

---

## 12. 三层归因：模型创新 / 推理引擎优化 / 硬件调优

这三层必须分开，否则会误判「换个模型行不行」「换个卡行不行」。

### 12.1 模型创新层（GLM-5.3 本身）

| 项 | 内容 | 对推理的约束 |
|---|---|---|
| 稀疏注意力 DSA | 每个 query 只 attend indexer 选中的 top-2,048 | **让 KV 分层成为可能**：只有被选中的行必须常驻显存，其余可下放 CPU（HiSparse 的前提） |
| MLA latent KV | 64 head 共享一份 latent，等效 1 个 KV head | **让「按 head 切」失去意义**（TP 必然复制），从而必须按 token 切（DCP） |
| IndexShare | 每 4 层稀疏 MLA 配 1 层 indexer | indexer KV 只占小头，GPU 常驻开销可控（78 层里只有 21 层 indexer） |
| MTP | 多 token 预测投机 | decode 加速，但**放大 hot buffer 需求**（`(num_spec+2)×top-K`） |
| 原生 1M 窗口 + 后训练 | 与 GLM-5.2 同基座，提升全来自后训练（含 SAO 上下文压缩 + 异步 agent RL） | 提供「能请求 1M」的模型能力，但**不保证 1M 下的服务质量** |

### 12.2 推理引擎优化层（vLLM）

| 组件 | 作用 | 是否模型相关 |
|---|---|---|
| **PCP** | 按 token 切 query + V 形负载均衡 + 每层 all-gather 新 KV | **强相关**：收益来自「indexer 不再被复制」与「每行 KV 服务 64 head」；稠密注意力模型拿不到同等收益 |
| **DCP** | 按 token 切 KV；decode 用 LSE 合并，prefill 用 all-gather 临时副本 | 中等相关：MLA/GQA 通用，但收益幅度强烈依赖 KV 复制程度 |
| **Hybrid HiSparse** | 三态驻留 + hot buffer + 融合 top-K resolver（CUDA-graph 可捕获） | **强相关**：完全依赖稀疏注意力 |
| **Model Runner V2** | 模块化执行核心、投机解码无 CPU–GPU 同步 | 通用基础设施 |
| **P/D 组合工程** | NIXL 重排布局、前缀感知路由、CPU offload 与前缀复用并行工作 | 通用 |

### 12.3 硬件调优层

- **H200 SXM 的具体数字被直接写进论证**：989 dense BF16 TFLOP/s、4.8 TB/s、206 FLOPs/byte 的平衡点 —— PCP 带来的 191 FLOPs/byte 之所以「接近 compute-bound」，是相对 H200 而言；换一张带宽/算力比不同的卡，结论会变。
- **FlashMLA `fp8_ds_mla` 的 656 B 布局 + 4 B index**（= 660 B/行）直接决定了 191 FLOPs/byte 的推导。
- **141 GB HBM 与 93 GB 权重的差距**决定了每卡只剩约 15 GiB 给 KV，进而决定了必须 DCP、必须 HiSparse。
- **512 GiB 主机内存/节点**是「把 KV 放到主机」这一整套策略能成立的前提，也是 AgentX DRAM 配额限制（3 TB 上限、按 GPU 配额比例分配）下的选择空间。
- **单机 8 卡 NVLink 域**：PCP/DCP 的 all-gather / LSE 合并都在节点内完成，跨节点只搬 KV（Part 2 未测试跨节点 context parallel）。

> **一句话归因**：**模型创新提供了「稀疏可分层」的可能性，引擎优化提供了「切得动也放得下」的实现，硬件调优决定了「在 H200 上这套切法的收益刚好成立」**。三者缺一，结论都会退化为「某个具体配置的调参结果」。

---

## 13. 对 Agent 长上下文工作负载与 harness 设计的可迁移启示

### 13.1 可迁移（结构性，不依赖 H200）

1. **长上下文 agent 的第一瓶颈是 prefill，不是 decode。** 每轮把工具输出与文件内容灌进 prompt，等于每轮重付一次 prefill 成本。原文的证据是「c≤32 时部署主要是 prefill 受限」。→ **harness 设计应把「每轮新增 token 量」当作一级指标**（工具输出裁剪、增量摘要、分块写文件而不是整文件读入）。
2. **交互性 ≠ 吞吐，应分别设 SLO。** 原文用两个正交指标：throughput（logical tok/s per GPU）与 interactivity（P90 output tok/s per user）。→ **harness 应同时观测 TTFT、每用户输出速率、端到端任务时长**，只用其中之一会做出错误架构选择。
3. **前缀复用是长上下文经济性的地基。** 原文用 512 GiB CPU offload + 前缀感知路由来实现跨轮复用。→ **harness 应保持 system prompt / 工具 schema / 历史摘要的字节级稳定**，因为 KV 复用按内容哈希对齐；任何在前缀里插入时间戳或随机 ID 的做法都会击穿复用。
4. **KV 驻留策略应作为一等公民。** HiSparse 的教训是：不要问「这个请求能不能放下」，而要问「这块 KV 的温度是多少、该放哪一层」。→ **harness 侧对应的是「上下文分层」**：热区（当前任务与最近工具结果）常驻、冷区（早期历史）可压缩/可下放。
5. **投机解码会与 KV 预算互相牵制。** hot buffer 必须一次装下全部验证 token（`(num_spec+2)×top-K`），草稿越长，KV 预算越紧。→ 选 MTP 长度时要看 KV 容量，而不是只看投机收益。
6. **「能服务」不等于「能用」。** 原文证明了 1M 可被服务，没有任何 1M 下的质量数据。→ **harness 侧必须自建长上下文质量回归**，否则会误把「不报错」当成「有效」。

### 13.2 需要改写后才可迁移（依赖硬件/引擎）

| vLLM 的做法 | 迁移到其它栈时的等价物 | 注意 |
|---|---|---|
| PCP：切 query | 任何「按 token 切 prefill」的方案 | 依赖稀疏注意力才划算；稠密模型收益小得多 |
| DCP：切 KV | 「KV 按序列维分片 + LSE 合并」 | GQA 下 dcp size ≤ tp/H；跨节点实现的复杂度更高 |
| HiSparse | 「稀疏 KV 分层驻留」 | NVIDIA-only；非 NVIDIA 需要另找实现 |
| P/D 分离 + NIXL | 「prefill/decode 分离 + KV 传输层」 | 需要能重排 KV 布局的传输协议 |
| 前缀感知路由 | 「按前缀亲和度调度」 | 静态负载均衡会毁掉前缀复用 |
| `sparse_mla_force_mqa` | 「强制走稀疏 kernel」 | 不开就走稠密路径，算术强度收益消失 |

### 13.3 对 harness 评测方法论的三条具体建议

1. **每个并发点重新起一套部署**：原文与 AgentX 方法学都这么做；否则前一点的 KV/缓存状态会污染后一点，长上下文下污染尤其严重。
2. **闭环回放要注意工作负载漂移**：更快的服务商会完成更多请求，从而遇到不同的负载混合；对比不同配置时要固定 seed 与起点（AgentX 的做法），否则比的是「跑了不同的活」而不是「跑得更快」。
3. **把投机解码的接受长度固定住**再比较引擎，否则比较的是「谁猜得更准」。AgentX 甚至强制用 SPEED-Bench 测得的接受长度。

---

## 14. Limitations

1. **全部性能数字为项目/厂商自报**。Part 2、Part 1、AgentX 数据均由 vLLM 与 SemiAnalysis 产出，本文没有复现任何一项。**没有任何独立第三方验证。**
2. **口径边界窄**：1.7–3.2× 只在 c≤32、142K 扫描、HiSparse 双开、相同吞吐的条件下成立；1M 场景下没有可比的 DP8 基线，因此**「1M 下快多少」是未知数**。
3. **单次测量、无误差条**：每个并发点只跑一次 1 小时，没有重复实验与置信区间，也没有失败率统计。
4. **TP8 只有理论论证，没有实测基线**，因此「PCP 相对 TP 的收益」缺少直接证据。
5. **DCP 在 1M 处的开销未被测量**；由 6%@≤64K、15%@248K 粗略线性外推得到的 ~60% 只是[推测]，两个区间不足以确定真实曲线。
6. **1M 上下文的质量完全未评估**；AgentX 官方声明其合成载荷不支持模型质量评估。
7. **闭源回放的固有偏差**：AgentX 用合成 token 填充，会扭曲投机接受率（AgentX 因此强制固定接受长度），也无法反映真实工具输出长度分布。
8. **官方文档与博客存在成熟度差**：文档称 PCP「两种策略都还在活跃开发中」，而博客已给出 PCP×DCP 组合的生产级部署描述；读者若以文档为准可能误判可用性。
9. **两篇文章之间存在未解释的差异**：Part 1 的预告段说 Part 2 将组合「PCP、DCP、**adaptive verification** 和 Hybrid HiSparse」，但 Part 2 正文**从未提及 adaptive verification**。→ [待验证]
10. **版本锚点会漂移**：Part 1 说 Hybrid HiSparse 计划在 vLLM v0.30 广泛可用、当时需自建 `hisparse-glm` 分支（`e8ef1e07bd`）；Part 2 说功能需要 v0.32.0+，实测在 main `9e38b4111a`。跨版本复现需要自行核对。
11. **其他组件被顺带提及但未展开**：MTP3 的接受长度 2.99 是「合成固定」的，不是实测分布；`adaptive verification`、all-gather/计算重叠优化都在进行中，结果可能变化。
12. **范围限制**：HiSparse 仅 NVIDIA；Part 2 只测 16×H200 两节点；未测多节点 context parallel、非 NVIDIA 加速器、其它模型。
13. **本文自身的推导**（如 191/26 FLOPs/byte 的复算、15 GiB KV 空间的粗算、c64 两个吞吐数字的相除、1M 处 DCP 开销外推）均标注为[分析者推导]或[推测]，**不是原文数据**，也未经实测。

---

## 15. 思考与追问

1. **PCP 的收益到底有多少来自「indexer 不复制」、多少来自「算术强度」？** 原文把两者并列陈述，但没有做消融。对稠密注意力模型，PCP 还能剩下多少收益？这是判断「这套方案是否 GLM 特有」的关键实验。
2. **DCP 在 1M 处的真实开销是多少？** 如果线性外推的 ~60% 成立，那么 PCP×DCP 在 1M 下的 prefill 优势可能被通信吃掉一大半；这会改变「1M 只能靠 PCP×DCP」的结论强度。
3. **all-gather 与上层计算重叠能回收多少？** 原文说正在做。若能回收大部分，248K 处 15% 的开销曲线会整体下移，1M 场景的可行性判断会变。
4. **HiSparse 在 1M 下的 top-K 命中率是否还成立？** indexer 的选择在极长上下文下的准确率、以及 hot buffer（2×top-K）是否够用，原文没有数据。这直接决定「稀疏」在百万 token 时是否仍是稀疏。
5. **prefix-aware 路由的最优策略是什么？** 原文只用 llm-d 的前缀感知路由做传输，没有讨论路由策略对 1.7–3.2× 的贡献。**如果路由策略贡献了其中一部分，那么这个数字就不是 PCP×DCP 的功劳。**
6. **AgentX 的 P90 E2E 归一化 interactivity 具体怎么算？** 官方教程页只给指标名与「报告 throughput + TTFT + interactivity」的指引，没有公开完整公式。这是复现 1.7–3.2× 的最大黑箱。
7. **把 16×H200 的结论搬到 8×B200 会怎样？** 官方 recipe 说 8×B200 + FP8 KV 已能单机跑满 1M，那么在 B200 上 prefill 侧还有没有必要 PCP？本文的「必须 PCP×DCP」结论是 **H200 特定** 的。
8. **这套结论对 EverAgent 自己的 harness 意味着什么？** EverAgent 走的是 Coding Plan 托管 API（不是自建 16 卡集群），但「prefill 受限 / 交互性 SLO / 前缀复用 / 上下文分层」这四条是可迁移的工程原则，应该落到 harness 的观测指标与上下文管理策略上，而不是落到「买 H200」。
9. **上下文长度的「经济最优」在哪里？** 原文证明 1M 能被服务，但没证明 1M 是划算的。更长上下文意味着更长 prefill、更贵 KV、更慢交互。**[推测] 多数 agent 负载的最优上下文长度远低于 1M**，真正稀缺的不是长度而是「在长上下文里仍能快速定位到正确片段」的能力。
10. **能不能不用 1M？** 如果把 300K 上下文 + 强压缩/检索的组合与「1M 裸上下文」对比谁更准，这可能是比「谁更快」更有价值的问题 —— 而这个问题目前没有任何公开数据。

---

## 附录 A：来源清单与口径标注

| ID | 来源 | 类型 | 用途 |
|---|---|---|---|
| S01 | vLLM Blog — *GLM-5.3 Optimizations, Part 2: PCP, DCP, and Hybrid HiSparse on 16 H200s*（2026-10-23）`https://vllm.ai/blog/2026-10-23-glm53-part2-pcp-dcp-hisparse` | 一手（项目方） | 主线：PCP/DCP 机制、部署拓扑、AgentX 结果、复现参数 |
| S02 | vLLM Blog — *GLM 5.3 Optimizations, Part 1: Hybrid HiSparse Offloading in vLLM*（2026-09-08）`https://vllm.ai/blog/2026-09-08-glm53-part1-hybrid-sparse-offloading` | 一手（项目方） | Hybrid HiSparse 机制、三态驻留、hot buffer、OpenHands 口径 |
| S03 | vLLM 官方文档 — *Context Parallel Deployment* `https://docs.vllm.ai/en/latest/serving/context_parallel_deployment` | 一手（官方文档） | PCP/DCP 的官方定义、dcp 与 tp/H 的约束、成熟度说明 |
| S04 | vLLM Blog — *Efficient Decode Context Parallelism with vLLM for Long-context Workloads*（2026-08-07）`https://vllm.ai/blog/2026-08-07-decode-context-parallelism` | 一手（项目方） | DCP 原理与通信节奏、MLA/GQA 差异、B200/Kimi K2.6 对照 |
| S05 | vLLM Recipes — *zai-org/GLM-5.3* `https://recipes.vllm.ai/zai-org/GLM-5.3` | 一手（官方） | 参数量、FP8 checkpoint、8×H200 与 8×B200 的 1M 差异、vLLM 版本要求 |
| S06 | vLLM GitHub Issue #25749 — *[RFC]: Support Prefill Context Parallel (PCP)* `https://github.com/vllm-project/vllm/issues/25749` | 一手（实现讨论） | PCP 与 DCP 的关系（PCP 是 DCP 之后的补充）、KV 沿序列维分段的 interleaved 策略 |
| S07 | vLLM Blog — *Model Runner V2: A Modular and Faster Core for vLLM*（2026-03-24）`https://vllm.ai/blog/2026-03-24-mrv2` | 一手（项目方） | Model Runner V2 的定位与动机 |
| S08 | z.ai 官方博客 — *GLM-5.3: Frontier Coding with Emergent Cyber Capabilities*（2026-08-14）`https://z.ai/blog/glm-5.3` | 一手（厂商） | 「同基座、提升全来自后训练」、IndexShare / SAO / 异步 RL 的背景 |
| S09 | 智谱官方文档 — *GLM-5.3* `https://docs.bigmodel.cn/cn/guide/models/text/glm-5.3` | 一手（厂商） | 1M 上下文、128K 最大输出、thinking/reasoning_effort 规格、内部基准数字 |
| S10 | HuggingFace — *zai-org/GLM-5.3* 模型卡 `https://huggingface.co/zai-org/GLM-5.3` | 一手（厂商） | 基准表与评测口径（厂商自报）、1M/400K 等评测上下文设置、引用要求 |
| S11 | arXiv:2602.15763 — *GLM-5: from Vibe Coding to Agentic Engineering* `https://arxiv.org/abs/2602.15763` | 一手（论文） | GLM-5 系列的 DSA 与长上下文保真度主张 |
| S12 | arXiv:2411.01783 — *Context Parallelism for Scalable Million-Token Inference* `https://arxiv.org/abs/2411.01783` | 一手（论文） | PCP 负载均衡分片的来源；pass-KV / pass-Q；H100 上的扩展性数字 |
| S13 | SemiAnalysis InferenceX — *AgentX Methodology and Datasets* `https://inferencex.semianalysis.com/agentx` | 一手（基准方） | AgentX 方法学：393 会话、median 142k in / 444 out、闭源回放、1 小时窗口、DRAM 配额、固定接受长度、只测服务性能 |

**证据分级说明**：S01–S07 是 vLLM 项目方自己的材料（对「项目做了什么」是一手证据，对「效果有多好」是**自报**）；S08–S11 是模型厂商材料（对「模型规格」是一手，对「能力领先」是**自报**）；S12 是公开论文预印本（用于机制来源，本文未核实其同行评议状态）；S13 是基准方材料（对「基准方法」是一手，但本次测试数据由 vLLM 产出）。

---

## 附录 B：复现命令与版本锚点

Part 2 给出的 prefill 引擎关键参数：

```bash
--prefill-context-parallel-size 8 \
--decode-context-parallel-size 8 \
--dcp-comm-backend ag_rs \
--enable-expert-parallel \
--attention-config '{"sparse_mla_force_mqa":true}'
```

- 镜像：`vllm/vllm-openai:v0.32.0` 或更新；
- 实测版本：vLLM main `9e38b4111a`；复现 gist 固定 `2537629eb2`；
- Part 1 的 HiSparse 版本锚点：`e8ef1e07bd`（HiSparse）/ `80cb71c9ff`（offload 基线），Part 1 给出完整的 `vllm serve` 命令与 OpenHands 数据集构建脚本（`build_openhands_padded_dataset.py`、`evalscope` 固定在 `acd09b44384d53174768bb1063f675420f76fae9`）。

> **说明**：以上命令与版本号均转录自原文，本文未在本机执行（本次任务不具备该硬件条件）。
