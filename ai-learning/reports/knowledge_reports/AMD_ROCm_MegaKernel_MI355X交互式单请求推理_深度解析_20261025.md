---
title: "AMD ROCm MegaKernel：MI355X 上交互式单请求推理的持久化内核路线深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["AMD", "ROCm", "MI355X", "MegaKernel", "持久化内核", "投机解码", "MXFP4", "推理优化"]
---

# AMD ROCm MegaKernel：MI355X 上交互式单请求推理的持久化内核路线深度解析

**研究对象**：AMD ROCm 官方技术博客《Bringing Ultra-Fast, Interactive LLM Inference to AMD Instinct™ MI355X GPUs》（2026-10-20，作者 Aditya Nandakumar、Sangeeta Chowdhary、Rohan Doshi、Shubham Sharma、Paul Merolla），并继续读取其直接链接的一手实现与学术材料：arXiv:2604.15379《Fleet: Hierarchical Task-based Abstraction for Megakernels on Multi-Die GPUs》、arXiv:2512.22219《MPK: A Compiler and Runtime for Mega-Kernelizing Tensor Programs》、`proaditya/aiter`（AITER 的临时镜像，含 `aitermk-qwen38` / `aitermk-gpt-oss` 分支）、`proaditya/ATOM`、`sangeeta0201/fleet-chiplet-megakernel`（Fleet 临时仓库，分支 `amd_mi350`）、`ROCm/FlyDSL`。

> **标注约定**（全文通用）
> - `[AMD 自述]`：AMD 博客原文可直接核对的陈述与数字。
> - `[论文事实]`：arXiv 论文摘要可核对内容。
> - `[代码证据]`：仓库结构、分支、提交与文档可核对事实（注明出处）。
> - `[分析者推断]` / `[推测]` / `[待验证]`：本报告作者的推理与未决疑点。
>
> **阅读纪律**：本报告**未运行任何 kernel、未复现任何 benchmark、未在任何 MI355X 上测量**。所有性能数字均为 AMD 自测；其中**最关键的三处口径不一致与一处已确认的正确性异常**在 §6.4 与 §9 单独列出，不与"提速倍数"混读。

---

## 开头三行：x → f → f(x)

- **x**：推理的默认目标是**吞吐**（tokens/s 总量、并发下的 aggregate throughput）。但当推理模型、AI Agent 与交互式应用成为主流，"**用户注意到的是秒，不是每秒多少 token**"（`[AMD 自述]`，S01）——**响应性变成一等指标，TPOT（time per output token）才是约束**。在 batch=1 场景下，这个约束的物理来源很清楚：每层每个算子都是一个独立 kernel、一个 token 要穿过几百个 kernel，每个 kernel 都有启动与同步开销，而**单个请求无法把它们藏起来**。
- **f**：AMD 的回答是四个杠杆叠加：**持久化 megakernel**（一个 workgroup 常驻每个 compute unit，workgroup 之间通过内存"手递手"传递数据，把 launch 与同步开销从热路径上拿掉）、**投机解码**（用小 drafter 猜若干 token、target 一次验证，接受几个就用几个）、**低精度数据类型**（MXFP4 权重，权重字节数约为 BF16 的 1/3.8）、以及**硬件感知的数据放置**（MI355X 双 die 上用 DPX+NPS2 让每个 die 读自己 die 的 HBM）。四者互相咬合：低精度降低每轮需读的权重字节，megakernel 把每轮 pass 逼近"读权重所需时间"这条下界，投机解码把一次 pass 分摊给多个 token，数据放置则减少跨 die 读取。
- **f(x)**：接受 f 之后，AMD 自测在**单张 MI355X、batch=1、GSM8K 128 条提示**上给出 **1.9×–3.3×** 的 decode 加速（Qwen3.8-27B ~1,100 tok/s、Qwen3.8-Flash-Next ~750 tok/s、GPT-OSS-120B 1,472 tok/s）。**但这条结论的边界必须和数字一起读**：所有比较都是"各侧最快配置"对"各侧最快配置"，GPT-OSS-120B 一侧**分区模式、精度与 drafter 都不同**；**GPT-OSS-120B 的投机解码版本在 5-shot 原始文本 GSM8K 上从 42.8% 掉到 35.5%–39.3%，AMD 自述"正在排查"**（§5.4、§9）；相关代码分散在临时个人仓库，其中两个仓库创建于 2026-10，Fleet 临时仓库创建于 2026-07，AMD 自己写明部分代码会在未来几周迁到长期归属地（§6、§9）。**可迁移的不是这些倍数，而是"在低并发下，launch 与同步会进入关键路径"这一判断，以及"权重读取时间构成 decode 硬下界"的度量纪律。**

---

## 一、来源清单与读法

| 编号 | 来源 | 类型 | 本报告用途 |
|---|---|---|---|
| S01 | AMD ROCm Blogs《Bringing Ultra-Fast, Interactive LLM Inference to AMD Instinct™ MI355X GPUs》（2026-10-20） | 官方博客 | 问题定义、四个技术杠杆、三模型结果、测试配置与版本、质量数据、路线图、仓库链接 |
| S02 | arXiv:2604.15379《Fleet: Hierarchical Task-based Abstraction for Megakernels on Multi-Die GPUs》（Sangeeta Chowdhary 等 10 人，2026-04-15 提交，cs.AR） | 一手论文 | 持久化内核的学术谱系、chiplet 调度抽象、与 vLLM 的对比口径 |
| S03 | arXiv:2512.22219《MPK: A Compiler and Runtime for Mega-Kernelizing Tensor Programs》（Xinhao Cheng 等 21 人，v2 2026-06-10，cs.DC/cs.LG/cs.PL） | 一手论文 | "megakernel" 的定义与自动化编译思路、相对 kernel-per-operator 的量级 |
| S04 | `proaditya/aiter`（AITER 临时镜像；分支 `main` / `aitermk-qwen38` / `aitermk-gpt-oss`；MIT；创建 2026-10-18） | 一手代码仓 | megakernel kernel 与引擎插件的落地位置、仓库成熟度与迁移风险 |
| S05 | `proaditya/ATOM`（ATOM 临时镜像；MIT；创建 2026-10-12） | 一手代码仓 | ATOM 引擎定位、模型覆盖、bench client 位置 |
| S06 | `sangeeta0201/fleet-chiplet-megakernel`（Apache-2.0；默认分支 `amd_mi350`；创建 2026-07-29） | 一手代码仓 | Fleet 复现步骤、MI350 硬件参数、与 Mirage MPK 的对照数字、长期归属地指引 |
| S07 | `ROCm/FlyDSL`（302 stars / 131 forks；创建 2025-11-23；GitHub 许可字段为 NOASSERTION） | 一手代码仓 | megakernel 所用 DSL 的上游地位与许可元数据边界 |

**读法说明**：S01 是**完整的口径披露**（这一点值得肯定），S02/S03 是**学术坐标**（megakernel 不是凭空冒出的概念），S04–S07 是**落地形态与成熟度的证据**。本报告把"数字读法"与"可复现性读法"分开：前者看基线与条件，后者看仓库、版本与脚本。

---

## 二、原文问题重构：交互式推理是延迟问题，不是吞吐问题

### 2.1 问题定义

`[AMD 自述]` S01 开篇："AI inference is no longer just a throughput problem. As reasoning models, AI agents and interactive applications become mainstream, **responsiveness has become a first-class metric. Users notice seconds, not tokens per second.** Lowering time per output token (TPOT) is now critical for AI systems that feel conversational, responsive and useful."

`[AMD 自述]` 同文对"megakernel 存在理由"的解释是本报告认为整篇文章最重要的一句：**"Normally each operator of each layer is its own GPU kernel, and one token passes through hundreds of them, each with launch and synchronization overhead that a lone request cannot hide."**（S01）

`[分析者推断]` 这句话把问题的结构说透了：**launch 与同步开销是"单请求"的函数，不是"总吞吐"的函数**。在 batch=64 时，GPU 被充分喂饱，launch 开销被摊薄；batch=1 时，每个 kernel 的启动延迟、每条依赖边的同步延迟都**直接串在关键路径上**。因此"megakernel 更快"这个命题**只在低并发下成立**，把它当成吞吐方案是范畴错误。

### 2.2 四个技术杠杆的分工（AMD 自述）

| 杠杆 | AMD 的说法 | 本报告的归类 |
|---|---|---|
| **1. Megakernels** | "**Fewer Launches, Synchronize Only Where Needed**"：持久化 kernel，一个 workgroup 常驻每个 compute unit，workgroup 通过内存互相传数据 | **消除调度开销**（把 launch 与大部分同步从关键路径移除） |
| **2. Speculative Decoding** | "**More Tokens per Pass**"：drafter 猜几个 token，target 一次验证 | **摊薄固定成本**（把"读一遍全部权重"的成本分摊给多个 token） |
| **3. Low-Precision Data Types** | MXFP4 权重 + MXFP8 激活，比 BF16 少约 3.8× 权重字节 | **降低硬下界**（decode 每轮都要读全部权重，权重字节数直接决定下界） |
| **4. Data Locality** | DPX+NPS2 把每 die 的权重、KV cache 与同步标志留在自己 die 的 HBM | **降低下界本身**（跨 die 读权重要多付 28%） |

`[AMD 自述]` AMD 自己把第 3 条讲成了度量纪律：**"Low-precision weights set the speed limit: decode reads every weight on every pass, so the time to read them is a floor on each pass... Low precision alone does not reach that floor: the Qwen baselines run the same MXFP4 weights and stay well above it. The megakernels bring each pass closer to it, and speculative decoding spreads each pass over several tokens."**（S01）

`[分析者推断]` 这段是整篇文章的方法论核心：**它把"加速"翻译成一个可判定的命题——每轮耗时离"读权重的时间"还有多远**。任何后续复现或对比，都应该先算这条下界，再谈倍数。

### 2.3 AMD 自己的限定（很少被引用，但必须引用）

`[AMD 自述]` S01 有多处自我限定，本报告认为它们是这篇官方博客可信度的一部分：

- "**These are early results.** We expect both the engines' regular paths and our kernels to improve over the coming weeks, and the READMEs will track the latest numbers."
- "**These comparisons reflect each model's complete optimized setup**, including the precision, drafter and GPU partitioning differences detailed in the test configuration section."
- "**Decode rates are not whole-task speedups**: prompt processing and tool calls add to an agent's task time."
- "**some of the code lives in interim repositories today and will move to its long-term home over the coming weeks**, and the links will follow it."

---

## 三、MegaKernel 机制详解

### 3.1 从 kernel-per-operator 到持久化内核

`[AMD 自述]` S01："A megakernel is a **persistent kernel**: one workgroup stays resident on each compute unit, and the workgroups hand data to one another through memory."（S01）

`[AMD 自述]` 三个模型采用不同的融合粒度：**Qwen3.8-27B 与 GPT-OSS-120B 把整个 forward pass 跑成一个 kernel；Qwen3.8-Flash-Next 每个 decoder layer 一个 kernel，层间 ~1.7 µs 的边界是它唯一的 grid-wide 同步**（S01）。

`[论文事实]` S03（MPK）给这一类方法的学术定义与自动化路径：MPK "introduces an **SM-level graph representation** that captures data dependencies at the granularity of individual streaming multiprocessors (SMs), enabling **cross-operator software pipelining**, fine-grained overlap of computation and communication"；编译器把 tensor program 降级成 SM 级任务图并为每个任务生成实现，MPK 的 in-kernel 并行运行时"executes these tasks within a single persistent mega-kernel using **decentralized scheduling across SMs**"；其评测给出相对 kernel-per-operator LLM 服务的**最多 1.7× 更低端到端推理延迟**（S03）。

`[分析者推断]` 因此"megakernel"在这条技术线上不是一个单点 kernel，而是**一套编程范式**：控制流被显式表达成"哪个 SM 上的哪个 worker 在等什么"，从而让编译器和运行时能做跨算子软件流水。AMD 这条路线的特殊之处是**没有走通用编译器**（MPK 那条路），而是**手写 + DSL 辅助**：这换来了对具体模型的具体优化，也换来了 §9 要讲的维护成本。

### 3.2 手递手同步：把同步点压到最少

`[AMD 自述]` S01 描述了 megakernel 内部的同步纪律：

- 绝大多数阶段边界是**producer-to-consumer 交接**："a value and its sequence tag arrive in **one 64-bit store**, so a consumer **polls exactly the data it needs**"；
- **per-chiplet release words** 让大多数轮询落在本地缓存；
- **空闲 compute unit 预取下一阶段的权重**（weight prefetch），等输入到达时数据已在；
- "**synchronization only where data is actually shared**"。

`[分析者推断]` "value + sequence tag 打包进一个 64-bit store"是一个典型的**把同步语义编码进数据本身**的做法：消费者轮询一个 64-bit 字，既读到数据又读到"这是第几个"，从而避免了独立的 tag 数组与额外的内存序屏障。**它的代价是隐式的**——正确性依赖内存序与 release/acquire 语义，跨 vendor 复现与调试难度显著高于显式 barrier。

### 3.3 稀疏注意力的块选择并行化（一个可量化的小切口）

`[AMD 自述]` S01 给出 Qwen3.8-Flash-Next 的一个具体优化与其效果："Qwen3.8-Flash-Next's sparse attention **scores every block of the context and selects the top 512**; **splitting that selection into parallel chunks and merging their winners cut a sparse-attention layer at 250K tokens from 262 to 126 µs**; with further tuning, **a token at 250K now takes 3.0 ms, against 10.2 ms on ATOM's regular path**."（S01）

`[分析者推断]` 这条例子的价值在于**它展示了 megakernel 内部仍存在"非 kernel 化"的部分**：top-512 的选择是一个需要全局归约的步骤，如果写成独立 kernel，就会重新引入 launch 与 grid 同步。把它切成并行块再合并 winners，是把"全局归约"改写成"局部归约 + 一次合并"——**这是持久化 kernel 内部必须自己解决的一类问题**，也是"megakernel 比传统 kernel-per-operator 难写得多"的具体体现。

### 3.4 实现语言：FlyDSL 与手写 HIP

`[AMD 自述]` S01："The Qwen kernels are written in **FlyDSL, a Python DSL that compiles to AMD GPU code while keeping control of matrix instructions, memory transfers and ordering**; they **began as HIP C++**, as the GPT-OSS kernel still is."（S01）

`[代码证据]` S07：`ROCm/FlyDSL` 仓库描述为 "FlyDSL is the Python front‑end of the project: a Flexible Layout Pyth…"；创建于 2025-11-23，302 stars / 131 forks，最近推送 2026-10-24，GitHub API 的 **`license.spdx_id` 为 `NOASSERTION`**。这表示 API 没有给出可断言的 SPDX 许可结论，**不等于仓库没有许可**；本报告未进一步核对许可文件。

`[分析者推断]` 这三句话拼起来是一条有意思的技术路径史：**先用 HIP C++ 手写拿到性能，再用 DSL 重写以获得可维护性与迭代速度**。`[推测]` 这正是"用 AI 编码 agent 加速 kernel 迭代"能成立的前提——**DSL 化之后，agent 才能在类型化、可检查的接口上做批量修改**，而裸 HIP C++ 上做同样的事风险高得多。S01 明说这些路径是"Developed through **hundreds of optimization experiments by AMD engineers and AI coding agents**"（S01）——**AI agent 参与 kernel 优化本身，是这篇博文的一个被低估的元信息**。

### 3.5 学术谱系：MPK → Fleet → AMD 的产品化

`[论文事实]` S02（Fleet）：现代 GPU 采用 chiplet 设计、拥有多级私有缓存层次，但 CUDA/HIP 暴露的是**扁平**的执行层次，"cannot express chiplet-level locality or synchronization"，导致冗余内存流量与缓存利用不足；Fleet 引入 **Chiplet-tasks** 这一新抽象，把工作与数据绑定到某个 chiplet，并通过其共享 L2 协作；实现为带 per-chiplet 调度的持久化 kernel 运行时。

`[论文事实]` S02 的量化结果（MI350、Qwen3-8B）：**在 batch size 1–8 上比 vLLM 的 decode 延迟低 1.3–1.5×**；在更大 batch 上，协作式权重分块把 **L2 命中率从 12% 提到 54%（batch 32）、从 39% 提到 61%（batch 64）**，HBM 流量最多降 **37%**，相对"chiplet-unaware 的 megakernel 基线"再快 **1.27–1.30×**（S02）。

`[代码证据]` S06（Fleet 仓库 README）的对照表（Qwen3-8B、bf16、MI350）：

| Batch | Mirage (ms) | Fleet M-tile (ms) | Fleet M-split (ms) | 加速 |
|---:|---:|---:|---:|---:|
| 1 | 7.993 | 7.076 | 7.012 | 1.13× |
| 32 | 15.186 | 12.357 | 12.923 | 1.23× |
| 64 | 23.343 | 18.176 | 21.923 | 1.28× |

`[代码证据]` S06 记录的硬件参数：**AMD Instinct MI350（gfx950）**，**248 个 CU 组织成 8 个 XCD**，**每个 XCD 4 MB L2**、**256 MB MALL**、**HBM3 5.3 TB/s**；要求 **ROCm 7.0+**；复现需 `MIRAGE_HOME`、Qwen3-8B 权重与 CMake 3.24+。

`[分析者推断]` 把三份材料放在一起可以看出**一条清晰的谱系与一个清晰的分工**：MPK 提供"自动把多算子推理降成单个 mega-kernel"的编译器路线；Fleet 提供"在多 die GPU 上按 chiplet 组织任务"的任务模型；AMD 这次做的是**把这些思想手工落到具体模型的具体 kernel 上**，用 FlyDSL 与手写 HIP 换取极致性能。**Fleet 论文里"比 vLLM 低 1.3–1.5× 延迟"与本博客"1.9×–3.3×"不是同一件事**：前者是 Fleet 调度层相对 vLLM 的比较（Qwen3-8B、MI350），后者是**四个杠杆叠加**相对"各引擎常规路径最快配置"的比较（Qwen3.8-27B / Flash-Next / GPT-OSS-120B、MI355X）。把两组数字并排引用是常见误读。

### 3.6 机制示意

```
       传统 kernel-per-operator（batch=1 时无法隐藏开销）
   layer0: k1 k2 k3 ... k40   layer1: k1 k2 k3 ... k40   ...
            ↑ launch ↑ sync      ↑ launch ↑ sync
   关键路径 = Σ(launch + sync + compute)

       持久化 megakernel（AMD 路线）
   ┌──────────────── 一个常驻 mega-kernel ─────────────────┐
   │  CU0      CU1      CU2      ...      CU63            │
   │  wg0      wg1      wg2      ...      wg63             │
   │   │         │         │                  │            │
   │   │ 64-bit store: value + sequence tag                │
   │   └────────►│────────►│─────► … （消费者轮询它需要的那一个数据）│
   │                                                       │
   │  per-chiplet release words（轮询落在本地缓存）          │
   │  空闲 CU 预取下一阶段权重                                │
   │  同步点：只在数据真正共享处（如 Flash-Next 的层边界 ~1.7 µs）│
   └───────────────────────────────────────────────────────┘
            │                    │
            ▼                    ▼
   ① 消除 launch/sync     ② 每轮更接近"读权重时间"这条下界
                                   │
                                   ▼
                    ③ 投机解码把一次 pass 分摊给多个 token
                                   │
                                   ▼
                    ④ MXFP4（权重字节 ~1/3.8）与 DPX+NPS2（跨 die 读 +28%）
                                   ▼
                    每轮耗时 × 每轮接受 token 数 → decode tok/s
```

---

## 四、交互式 vs 吞吐：四种技术的权衡细节

### 4.1 权重读取是 decode 的硬下界

`[AMD 自述]` S01：MXFP4 权重（4-bit 值、每 32 个共享一个 scale）喂给 MI355X 原生低精度矩阵指令，配 MXFP8 激活，比 BF16 少约 **3.8×** 权重字节；"in MXFP4, Qwen3.8-Flash-Next **and its full 262K-token cache fit on one GPU**"（S01）。

`[分析者推断]` "权重 + 262K KV cache 塞进一张卡"这一事实，把 megakernel 路线的适用边界划得很清楚：**它服务的是"单请求 + 长上下文 + 模型刚好放得下"这个特定区间**。若模型放不下、或上下文再长一个量级，就回到多卡、TP 或分页的路线——这与 AMD 自己列的路线图一致（"**Tensor parallelism**, to split one request across GPUs for larger models and lower latency"，S01）。

### 4.2 drafter 的选择：看 tokens/ms，不看 acceptance

`[AMD 自述]` S01 给了一条很有价值的工程规则："**When choosing a drafter, measure tokens per millisecond, not acceptance alone.** Every extra position checked costs time, and in mixture-of-experts models it can also pull in more experts."（S01）

`[AMD 自述]` 具体案例（GPT-OSS-120B）：**DFlash 的 8-position block 每 pass 接受的 token 比 EAGLE3 更多，但一个 confidence-gated 的 EAGLE3 在"不确定时停止猜测"，其 pass 比 DFlash 短约 30%，因此整体更快**；并且"**The best draft length also depends on the workload**: predictable text such as step-by-step math rewards longer drafts, while dense conversational text accepts so few extra guesses that **one draft is best**."（S01）

`[分析者推断]` "tokens/ms"这条规则把 drafter 选择从**模型质量指标**变成了**系统指标**——它依赖 MoE 的专家数、batch、上下文长度与文本可预测性，因此**同一模型在不同工作负载下的最优 drafter 不同**。这与本仓库此前记录的 MiniMax M3.1 Flash 案例相互印证：那篇 vLLM 博文同样强调"接受长度是动态的、必须实测标定"（`[推测]` 两条独立材料指向同一结论）。

### 4.3 线性注意力的状态：重放而非复制

`[AMD 自述]` S01："**Linear-attention layers carry a running state instead of a KV cache. They undo rejected guesses by replaying compact per-token records, instead of saving a copy of the state for every position.**"（S01）

`[分析者推断]` 这个设计避免为每个 draft 位置保存完整的线性注意力状态副本：它只保留紧凑的 per-token 记录，并在拒绝时重放。公开材料没有给出状态大小、重放复杂度或显存节省量，因此不能把收益写成严格的渐进复杂度结论；能确定的是，它在投机回滚与长上下文状态之间减少了直接复制的压力。

### 4.4 数据放置：一个漂亮的反事实实验

`[AMD 自述]` S01 的 locality 部分给了一个**受控反事实实验**，方法论价值很高："with the same binary and output, **storing each half of the GPU's weights in the other half's HBM**, so every weight read crosses the die-to-die link, **makes each decoded token take about 28% longer**"（S01）。

`[AMD 自述]` 分层归因：沿关键路径**每层在默认模式下多花 1.4 µs**，其中 **86% 是搬数据、14% 是阶段间等待**；逐步测量中，最大收益出现在"等另一 die 数据"的步骤：**Q/K/V 交接快 25%、top-k 专家路由快 17%、输出投影合并与注意力释放快 11%**，而"已受 HBM 带宽限制的专家权重流只快 4%"（S01）。

`[AMD 自述]` 复合效应："a wider verification pass reads the union of the experts its tokens route to (**about 11.7 per layer for 4 tokens against 7 for 2**), so it leans harder on memory bandwidth"；在 GSM8K 上，**placement (1.08×) 与 speculation (1.27×) 合计约 1.36×** 相对默认单流路径（可验证：1.08 × 1.27 ≈ 1.37）。

`[分析者推断]` 这个 28% 的反事实实验是全文**最硬的一个数字**，因为它把"多 die 设计"这个硬件事实转换成了可比的系统代价：**跨 die 读权重 = +28%**。因此 DPX+NPS2 的"7.5–8%（仅放置）"与"16–20%（放置+投机）"这两个数字在物理上是自洽的——**后者更大是因为投机的验证 pass 需要更多专家、因此更吃带宽**。

### 4.5 一个容易被忽略的硬件细节：硬件队列数

`[AMD 自述]` S01 在测试配置里写道：Qwen3.8-27B 在 ROCm 10.0 下需要 **`GPU_MAX_HW_QUEUES=1`**；"with HIP's default of four, **the optimized path runs 10-25% slower**, and one queue also speeds up ATOM's regular path, **so we quote the tuned pair**"（S01）。

`[分析者推断]` 这处披露值得点赞：**AMD 没有只调优自己那一侧**，而是明确说明"把常规路径也调到同样条件后再比"。但它同时暴露了一件事：**这条路线在默认硬件队列配置下会损失 10–25%**，也就是说它对**运行时系统级配置**有依赖，不是"装上就能快"。

---

## 五、关键数字与口径核对

### 5.1 主结果表（全部为 AMD 自测，单张 MI355X，gfx950）

| 模型 | 优化路径配置 | 吞吐 | 对照配置 | 对照吞吐 | 倍数 | 条件 |
|---|---|---:|---|---:|---:|---|
| **Qwen3.8-27B** | MXFP4 权重；MXFP8 DFlash2 drafter，7 drafts/轮；greedy；batch=1 | **1,091** tok/s（ROCm 10.0）／**1,105**（ROCm 7.2.4） | ATOM 常规路径，**相同 MXFP4 权重、相同 drafter**，但 LM head 与 drafter 保持 BF16 | **535**（ROCm 10.0）／**481**（ROCm 7.2.4） | **2.0×**（ROCm 10.0）／**2.3×**（ROCm 7.2.4） | GSM8K 128 条提示；reasoning effort xhigh；输出上限 2,048 token |
| Qwen3.8-27B | 同上 | **913**／**924** tok/s | 同上 | 443／406 | 同上 | HumanEval 128 条 |
| Qwen3.8-27B | 同上 | **824**／**846** tok/s | 同上 | 412／368 | 同上 | MT-Bench 80 条首轮 |
| **Qwen3.8-Flash-Next** | MXFP4 权重；MTP 3 drafts/轮 | **~750** tok/s（MI355X）／**689**（MI350X） | ATOM 常规路径（同分支、同 MXFP4 权重、启用 MXFP4 kernel） | 227（MI350X） | **3.3×**（MTP）／**3.4–3.5×**（无投机） | 同上提示集；另有随机提示 1K/8K/128K/250K 上下文、1,024 输出 token |
| **GPT-OSS-120B** | vLLM 0.31.0 + megakernel 插件，**DPX+NPS2**，EAGLE3 | **1,472** tok/s | stock vLLM 0.31.0（DFlash，默认 SPX+NPS1） | **784** tok/s | **1.9×** | GSM8K 128 条、greedy、输出上限 256 token、忽略 EOS；**仅 decode** |

`[分析者推断]` 这张表里最容易被误读的是 **Qwen3.8-27B 的 "2.0× vs 2.3×"**：**同一模型、同一 drafter、同一权重，仅仅因为 ROCm 版本不同（10.0 vs 7.2.4），声明的加速倍数就从 2.3× 变成 2.0×**。原因是 AMD 明确说明"ROCm 10 需要的硬件队列设置也加速了 ATOM 的常规路径，**所以我们引用调优后的一对**"——**基线也变强了**。这提醒我们：**跨软件版本引用倍数必须带上版本号**，否则一个 15% 的漂移会被误读成方法本身的差异。

### 5.2 逐轮度量模型（AMD 给出的换算公式）

`[AMD 自述]` S01："**speed ≈ tokens accepted per round × 1,000 / ms per round**; each model's figures below let you rescale to other acceptance rates."（S01）

| 模型 | 每轮接受 token | 每轮耗时 | 常规路径每轮耗时 |
|---|---:|---:|---:|
| Qwen3.8-27B（DFlash2，7 drafts） | 5.6（GSM8K 平均） | 5.11 ms | — |
| Qwen3.8-Flash-Next（MTP，3 drafts） | 3.04 | 4.27 ms | 14.10 ms |
| GPT-OSS-120B（DFlash，两侧同 drafter） | 4.25 | 3.52 ms | 5.65 ms（stock vLLM：4.43 token / 5.65 ms） |
| GPT-OSS-120B（EAGLE3） | 3.53 | 2.46 ms | — |

`[分析者推断]` 这个公式**是本报告认为最值得单独抄走的东西**：它把 tok/s 拆成两个可独立测量的量（接受数、每轮耗时），从而**任何人都能在自己的负载上重算**，而不必相信 AMD 的绝对值。反过来也说明：**如果接受长度变了（不同 prompt 分布、不同 thinking 档位），tok/s 就会变**，因此所有 tok/s 数字都必须绑定 prompt 集合。

### 5.3 硬件与软件版本（复现所需）

| 项 | 内容 |
|---|---|
| 硬件 | **1× AMD Instinct MI355X（gfx950）**；Fleet 仓库另给 MI350 参数：248 CU / 8 XCD / 每 XCD 4 MB L2 / 256 MB MALL / HBM3 5.3 TB/s |
| 范围 | **仅 decode**；Qwen3.8-Flash-Next 另测 4 请求批量；**GPT-OSS-120B 插件尚不支持批量 prompt 处理** |
| ROCm 10.0 | 容器 `rocm/pytorch:rocm10.0_ubuntu24.04_py3.12_pytorch_release_2.13.0`，ATOM release 分支；需 `GPU_MAX_HW_QUEUES=1` |
| ROCm 7.2.4 | 容器 `rocm/pytorch:rocm7.2.4_ubuntu24.04_py3.12_pytorch_release_2.10.0`，ATOM main `2479251d3`；HIP 默认队列 |
| SGLang | main `f825d72936` 于 `rocm/sgl-dev:v0.5.16-rocm720-mi35x-20260807`（ROCm 7.2.0）；另 SGLang 0.5.22（`34c4ba14c8`）于 `lmsysorg/sglang-rocm:v0.5.22-rocm10-mi35x-20261016`；**FlyDSL `19418894`** |
| vLLM | `49cb2bbf7` 于 `vllm/vllm-openai-rocm:nightly-rocm100-49cb2bbf7…`；另 vLLM main `3f1bcfd82`（ROCm 7.2） |
| GPT-OSS-120B | stock vLLM **0.31.0**（0.27.1 亦可），容器 `vllm/vllm-openai-rocm:v0.31.0`（ROCm **7.2.3**）；provider build 以 **ROCm 7.0** 编译；DPX+NPS2；**≤32K token（prompt+output）** |
| 提示集 | DFlash benchmark 选集：GSM8K 128 + HumanEval 128 + MT-Bench 80 首轮；reasoning effort **xhigh**；输出上限 2,048 token |
| 上下文长度测试 | **随机提示** 1K/8K/128K/250K，1,024 输出 token，忽略 EOS；1K/8K 为 10 条 ×2–4 次，128K/250K 为 **3 条**；4 请求为 20 条 ×3 次 |
| 度量 | 单请求：每请求的 decode 速率（首 token 之后的 token ÷ 首 token 之后的时间），按请求平均；上下文/批量测试：每输出 token 时间 |
| 基准客户端 | `atom/benchmarks/single_request_bench.py`，**可对任意 OpenAI 兼容服务**（ATOM / SGLang / vLLM）使用 |

`[分析者推断]` 这份版本表本身是一份**相当完整的复现清单**，但也暴露了两点：**(1)** ROCm 版本横跨 10.0 / 7.2.4 / 7.2.3 / 7.2.0 / 7.0，同一模型在不同版本上的加速倍数不同；**(2)** 上下文长度测试的样本极小（128K/250K 各 **3 条**随机提示），因此那些"1K 到 250K 保持 3.4–3.6×"的说法**统计强度很弱**。

### 5.4 质量数据与一处必须标出的异常

| 模型 | 评测 | 结果 | 备注 |
|---|---|---|---|
| Qwen3.8-27B（MXFP4） | GSM8K / HumanEval / MMLU-Pro | 与 BF16 相差**约 1 分**以内 | 三个引擎均如此 |
| Qwen3.8-27B（MXFP4） | GPQA-Diamond | **低 3–5 分** | AMD 明说 |
| Qwen3.8-Flash-Next（MXFP4） | GSM8K / HumanEval / GPQA-Diamond / MMLU-Pro | **与 ATOM 常规路径持平**（同 MXFP4 权重） | — |
| GPT-OSS-120B | GSM8K（**chat 格式**，0-shot，reasoning effort low，≤4,096 token） | **94.8%–95.4%**（有无投机均同） | 与 stock vLLM 持平 |
| GPT-OSS-120B | MMLU-Pro（1,400 题，chat 格式） | **74.4% vs 73.2%** | megakernel 略高 |
| GPT-OSS-120B | GSM8K（**5-shot 原始文本**，≤256 token） | **42.8%（无投机） vs 35.5%–39.3%（有投机）** | ⚠️ 见下 |
| GPT-OSS-120B | 同上，对照 | vLLM + AMD MXFP4×FP8 checkpoint：**43.8%**；BF16 attention 权重：**49%–56%** | 差距明显 |

`[AMD 自述]` AMD 对上述异常的原文说明是："**speculation itself is exact**: the score follows **how the attention kernel splits the context, which we are investigating**"（S01）。

`[分析者推断]` **这是全文最重要的一处事实**：投机解码在定义上是**无损**的（target 验证保证输出分布不变），但这里"无投机 42.8% → 有投机 35.5–39.3%"的落差**说明 megakernel 的注意力上下文切分方式影响了结果**。AMD 把它归因于"注意力 kernel 切分上下文的方式"并声明正在排查——**这是正确的处理方式（公开 + 承认在查），但它同时意味着这条路线目前不能被当作"已验证无损"**。而且"BF16 attention 权重 49–56%"与 megakernel 的 42.8% 之间的差距（6–13 分）**远大于**"MXFP4 checkpoint 43.8%"与 BF16 的差距，指向**注意力路径本身**而非权重量化是主要来源。`[待验证]` AMD 未给出该差距的归因细节。

### 5.5 口径缺口清单

| 缺口 | 说明与影响 |
|---|---|
| **GPT-OSS-120B 的基线不是同配置** | 分区模式（DPX+NPS2 vs SPX+NPS1）、精度（LM head 与 attention 投影 MXFP4 vs BF16）、drafter（EAGLE3/LMSYS 头 vs NVIDIA 头）三项都不同；AMD 明说"这些比较的是**完整 decode 配置**而不是 kernel 本身"。AMD 给了两个"更接近精度"的对照（1.55–3.3× / 1.85–3.5×），但倍数区间很宽。 |
| **两侧计时方式不同** | "The megakernel is timed by the client through `vllm serve`; **stock vLLM by its measured decode steps, offline, without serving overhead, which favors stock vLLM**."——AMD 明说该口径**偏向对照组**，即真实差距可能比 1.9× 更大。这是罕见的诚实，但**两个口径仍不可直接相减**。 |
| **只比较 decode，不比较 prompt processing** | "the plugin **does not yet batch prompt processing**"；AMD 也明说 "Decode rates are not whole-task speedups"。对长提示的 Agent 负载，**prefill 未被优化，TPOT 收益会被摊薄**。 |
| **缺少 prefill / 端到端 / 任务级指标** | 无 TTFT、无总任务时长、无 tool-call 场景数字。 |
| **批量只覆盖 1 个模型 × 4 请求** | "3.1× per user with four requests batched together"（仅 Qwen3.8-Flash-Next），且"**Larger batches**"仍在路线图上。 |
| **上下文长度的样本量极小** | 128K/250K 各 3 条随机提示；提示是随机 token 而非真实文档。 |
| **长上下文测试不含投机** | "3.4–3.6x from 1K to 250K tokens of context" 是在**无投机**条件下给出的。 |
| **单卡结论** | 全部在 1 张 MI355X 上；AMD 路线图里"**Tensor parallelism**"尚未实现，因此**无法回答"更大模型 / 多卡"场景**。 |
| **无第三方复现** | 全部数字由 AMD 自测；`[待验证]` 社区是否已复现，本报告未检索到。 |
| **无版本对齐的"旧 vs 新"内核对比** | 加速是相对"引擎常规路径"，**不是相对"同一引擎的上一版内核"**，因此无法分离"megakernel 贡献"与"同期其它优化贡献"。 |

---

## 六、代码与复现材料证据

`[代码证据]` 本节汇总可逐条复核的实现与仓库事实：

| 事实 | 出处 |
|---|---|
| 三个模型 × 三个引擎的可用性：Qwen3.8-27B 三者皆可用；Flash-Next 仅 ATOM 可用（SGLang/vLLM 计划中）；GPT-OSS-120B 仅 vLLM **preview** | S01 Get Started 表 |
| Qwen3.8-27B 三条复现脚本：`blog_benchmark/build_and_repro.sh`（ATOM）、`aitermk/engine_adapters/sglang/scripts/build_and_repro.sh`（SGLang）、`aitermk/engine_adapters/vllm/scripts/build_and_repro.sh`（vLLM）、`aitermk/engine_adapters/qwen38_flash_mono/build_and_repro.sh`（Flash-Next） | S01 |
| 基准客户端 `atom/benchmarks/single_request_bench.py` 可对任意 OpenAI 兼容服务运行 | S01 |
| megakernel kernel 与引擎插件位于 **`proaditya/aiter`（AITER 临时镜像，MIT，创建 2026-10-18）**，分支为 `main` / `aitermk-qwen38` / `aitermk-gpt-oss` | S04 |
| ATOM 位于 **`proaditya/ATOM`（临时镜像，MIT，创建 2026-10-12）**；其 README 内容与上游 `ROCm/ATOM` 一致，ATOM 定义为 "a lightweight vLLM-like implementation"，基于 AITER；上游还支持 Qwen3.8（`Qwen3_5MoeForCausalLM`，MoE，MXFP4 权重，单机 8 卡 MI355）、DeepSeek-V4-Pro **DSpark** 投机解码、GLM-5.2、Qwen3.5 多模态等 | S05 |
| GPT-OSS-120B 的 megakernel 源码与 exporter 在 **`sangeeta0201/fleet-chiplet-megakernel`（Apache-2.0，创建 2026-07-29，默认分支 `amd_mi350`）**；其 README 指向长期归属地 **`git@github.com:AMD-RAD/fleet.git` 并 `git checkout amd_mi350`** | S06 |
| Fleet 复现步骤完整给出：环境变量组合（`USE_GANG` / `USE_CK_FMHA` / `USE_FUSED_SILU` / `GANG_M_TILES_GATEUP` / `USE_GANG_M_SPLIT`）、模型下载、demo 命令与 batch size 设置 | S06 |
| `ROCm/FlyDSL` 是该 DSL 的上游 Python 前端（302 stars / 131 forks，创建 2025-11-23，最近推送 2026-10-24）；GitHub API 的 `license.spdx_id` 为 **NOASSERTION**，本报告未核对实际许可文件 | S07 |
| 上述三个中间仓库均**为 0 stars、0 forks**，创建于 2026-07 至 2026-10 之间 | S04/S05/S06 的 GitHub API 元数据 |
| Fleet 论文作者 Sangeeta Chowdhary 同时是本篇 AMD 博客作者之一 | S02 与 S01 的作者列表 |

`[分析者推断]` 这张表暴露了两类事实，一类是好事，一类是风险。**好事是**：AMD 把复现脚本、容器 tag、commit hash、基准客户端（且该客户端对任何 OpenAI 兼容服务可用）都公开了，复现入口较完整。**风险是**：承载相关实现的三个个人仓库在读取时均为 0 star；其中 `proaditya/aiter` 与 `proaditya/ATOM` 创建于 2026-10，Fleet 临时仓库创建于 2026-07。前两者的 README 仍指向上游 ROCm/aiter 与 ROCm/ATOM，表现为上游镜像加实验分支。这与 AMD 所说的"部分代码目前位于临时仓库，未来几周迁移"一致。对生产部署而言，当前地址和分支都应视为待迁移依赖，而不是稳定发布渠道。

---

## 七、与替代路线的有边界比较

`[分析者推断]` 本章明确：**本报告没有做同条件的多框架实测**，比较基于 AMD 自己的声明、学术论文的对比与各路线公开的能力边界，因此结论是"边界比较"而非"性能排名"。

| 路线 | 优势 | 劣势 | 有边界的适用区间 |
|---|---|---|---|
| **A. AMD megakernel 路线**（本报告对象） | 单请求低延迟极致（自测 1.9–3.3×）；长上下文 + 投机解码可共存（线性注意力状态重放）；数据放置可利用多 die 局部性；已可在 ATOM/SGLang/vLLM 三个引擎使用 | **仅 decode、仅单卡、仅低并发被验证**；GPT-OSS-120B 仍为 preview（≤32K token、一次一个贪心请求）；注意力路径存在未解释的精度落差；代码在临时仓库；依赖 `GPU_MAX_HW_QUEUES=1` 等非默认配置 | **单用户交互、模型放得下单卡、上下文长但 ≤ 数百 K、对话/编码/推理类任务** |
| **B. 传统 multi-kernel + graph capture**（CUDA/HIP Graph；vLLM/SGLang 常规路径） | 通用、成熟、生态广；已支持批处理、TP、PD 分离；精度路径被更广泛使用 | batch=1 时仍可能保留多 kernel 依赖与同步；权重字节数与跨 die 读取成本不因 graph capture 自动消失 | 吞吐优先、多并发、需要批处理与弹性扩缩的线上服务 |
| **C. 模型专用融合路径**（各家 monokernel / fused path） | 可减少 launch 并围绕单一模型做深度优化 | 融合粒度与数据流因实现而异，不能一概视为完整持久化执行模型；平台和模型绑定强 | 单一模型、单卡、愿意承担专用维护成本时 |
| **D. 通用 mega-kernel 编译器**（MPK 路线，S03） | **自动**把多算子推理降成单个 mega-kernel，SM 级图表示、跨算子软件流水，宣称最多 1.7× 更低端到端延迟；保留既有编程模型的灵活性 | 需改造为可编译的 tensor program；对特定模型的极致优化不如手写 | 多个模型共享一套推理栈、希望**一次投入多处受益**的团队 |
| **E. Chiplet-aware 持久化调度**（Fleet 路线，S02/S06） | 显式建模 chiplet 级局部性与同步；协作式权重分块把 L2 命中率 12%→54%（BS32）、39%→61%（BS64），HBM 流量最多 −37%；MI350 上 BS1–8 比 vLLM decode 延迟低 1.3–1.5× | 需要理解 XCD 拓扑与调度语义；收益集中在较大 batch 的 L2 复用上 | 多 die GPU 上的**大 batch 吞吐**（BS32–64）比单请求延迟更有价值 |
| **F. TensorRT-LLM 等 NVIDIA 专用栈** | NVIDIA 生态内的极致优化与广泛验证 | **硬件绑定**，在 AMD MI355X 上不可用；本文所有数字都不适用于它 | NVIDIA 硬件上的同类问题 |

`[分析者推断]` 最有价值的比较其实是 **A 与 D/E 的关系**：本次产品路径是**手工、模型专用**的；MPK 是**自动化编译与运行时**路线；Fleet 是**拓扑感知的任务与调度**路线。三者共享持久化执行、细粒度任务和调度局部性的技术主题，但公开材料不足以证明本次实现直接复用了 MPK 或 Fleet。Fleet README 指向 `AMD-RAD/fleet`，说明其自身正迁往更稳定的项目归属；是否会进入这些模型专用路径仍待验证。

### 7.1 与多 Agent 负载的关系（必须单独说）

`[AMD 自述]` S01 明确："**Decode rates are not whole-task speedups: prompt processing and tool calls add to an agent's task time.**"（S01）

`[分析者推断]` 对多 Agent 负载，这条路线只在**每个 Agent 回合的"生成阶段"**有效；**工具调用往返、环境执行、上下文重新组装**都不在优化范围内。更关键的是：**Agent 场景常见的是"多会话并发"而非"单会话高吞吐"**，而 megakernel 的收益恰恰在低并发时最大——这看起来是匹配，但**多会话并发会把 GPU 重新填满，从而重新进入"launch 开销被摊薄"的 regime**，此时 megakernel 相对常规路径的增益会缩小（AMD 只测了 4 请求，且只在 Flash-Next 上，且是"per user"口径）。`[推测]` **在多 Agent 高并发场景下，这条路线的净收益很可能显著小于单请求数字**，这是本报告认为最需要实测的一点。

---

## 八、部署风险与最小验证方案

### 8.1 部署风险清单

| 风险 | 证据 | 影响 |
|---|---|---|
| **代码位于临时个人仓库** | `proaditya/aiter`、`proaditya/ATOM`（MIT，创建 2026-10-12/18）、`sangeeta0201/fleet-chiplet-megakernel`（Apache-2.0，创建 2026-07-29），均 **0 stars**；README 仍指向上游 ROCm/aiter、ROCm/ATOM；AMD 明说未来几周会迁到长期归属地 | **依赖地址不稳定**；升级路径未知；CI/发布流程未验证 |
| **依赖非默认系统配置** | 需 `GPU_MAX_HW_QUEUES=1`；HIP 默认 4 时优化路径慢 10–25% | 与既有服务的默认配置冲突，需专门调优 |
| **ROCm 版本敏感** | 同一模型加速倍数在 ROCm 10.0（2.0×）与 7.2.4（2.3×）间不同；GPT-OSS-120B 容器为 ROCm 7.2.3 而 provider build 以 ROCm 7.0 编译 | 升级 ROCm 需重新测量；**不能假设倍数可迁移** |
| **引擎插件与主线不同步** | SGLang 0.5.22 / vLLM nightly commit / ATOM release 分支，均为特定快照；"Also supported: SGLang main … vLLM main …" | 主线演进可能破坏插件；需锁定版本 |
| **FlyDSL 许可元数据** | GitHub API 的 `license.spdx_id` 为 **NOASSERTION**；本报告未核对仓库内许可文本 | 合规使用前需读取实际许可文件，不能只依赖 API 字段 |
| **精度落差未解释** | GPT-OSS-120B 5-shot 原始文本 GSM8K：megakernel 42.8%（无投机）/ 35.5–39.3%（有投机）vs BF16 attention 49–56% | **不能默认"无损"**；在精度敏感的评测/生产任务上需自行验证 |
| **功能覆盖窄** | GPT-OSS-120B 仅 preview：一次一个贪心请求、≤32K token、仅 GSM8K 与 MMLU-Pro 做过精度检查；插件不支持批量 prompt 处理；TP 未实现 | 真实 Agent 负载（多并发、长上下文、批量 prefill）**尚未被支持** |
| **生态成熟度** | 缺少第三方复现与生产案例；AMD 自称 "early results" | 故障时缺少社区经验与现成 workaround |

### 8.2 最小验证方案（本报告建议，读者可自行执行）

`[分析者推断]` 在投入生产之前，一个成本可控、结论可判定的验证应当包含：

1. **先建立基线，而不是先看倍数。** 用 AMD 公开的 `single_request_bench.py` 对**自己真实的 prompt 集**测三条路径：① 目标引擎的常规路径；② 优化路径；③ 优化路径但用 BF16 attention/LM head（若可用）。第 ③ 条用来把"megakernel 收益"与"精度收益"分开。
2. **用 AMD 的换算公式重建期望值。** 实测你负载上的"每轮接受 token 数"与"每轮耗时"，代入 `speed ≈ accepted × 1000 / ms_per_round`，看能否复现 AMD 的 tok/s。**这一步是最快的证伪手段**：若差距很大，先怀疑接受长度与工作负载相关，而不是怀疑 kernel。
3. **必须包含精度对照与"开/关投机"两档。** 针对 GPT-OSS-120B 的已知异常，**在你自己关心的评测口径上同时跑无投机与有投机两档**，并至少包含一个"原始文本 few-shot"式评测（该异常正是在 5-shot 原始文本口径上暴露的，chat 格式口径下没有暴露）。
4. **量化 prefill 的占比。** 记录你的负载里 TTFT 与 TPOT 的比例；若 prefill 占比高，**decode 加速 3× 可能只换来端到端 1.3×**。
5. **验证多并发的净收益。** 在 1 / 4 / 8 / 16 并发下分别测 per-user tok/s 与 aggregate tok/s。**这是本报告认为 AMD 尚未证明、而对 Agent 部署最关键的一条。**
6. **锁定版本并留存可复现材料。** 记录容器 tag、commit、ROCm 版本、`GPU_MAX_HW_QUEUES`、提示集与每轮接受长度；这些是 §5.3 那份清单的最小子集，也是判断未来升级是否安全的基础。

---

## 九、反方解释与 Limitations

### 9.1 反方解释（本报告认为最强的三种替代解读）

`[分析者推断]` **对"1.9–3.3×"最保守的解读**是：这不是"megakernel 快了 3 倍"，而是**"把三个各自为政的优化（持久化 kernel、投机解码、低精度）叠在一起，并且基线也用了同样的低精度权重"之后的复合效应**。拆解来看：

- **投机会改变相对倍数，但不能据此分解贡献**：GPT-OSS-120B 的 "**3.6× stock vLLM 0.31.0 without speculation**, 2.3× with EAGLE3 and 1.6× with the same DFlash drafter"表明，当两侧加入投机后，相对差距缩小。无投机的 3.6× 是**两侧都未启用投机**的对照，不能归因于"只有常规路径没开投机"；更谨慎的解释是，投机加速了两条路径且与每轮耗时、drafter 精度和接受长度耦合，现有数字无法干净分解 megakernel 与投机各自贡献。
- **低精度也贡献很大**：AMD 明说基线用的是同样的 MXFP4 权重，因此倍数已经是"同精度"对比——**这一点是加分项**，但也意味着**相对 BF16 基线的绝对收益比这些倍数更大**，读者容易把"1.9–3.3×"误当成"相对原版模型的收益"。
- **数据放置贡献 7.5–8%**（仅放置）到 16–20%（配合投机）——**占比不大**，但它是四项里唯一有干净反事实实验支撑的。

`[分析者推断]` **对"megakernel 更快"最保守的解读**是：单请求 decode 的瓶颈在 **launch 与同步**，而这恰恰是**多 kernel 架构下最容易被摊薄**的开销。当 batch 从 1 升到 4（Flash-Next 的唯一批量数据点）时倍数已降到 3.1× per user；AMD 自己的路线图把 "**Larger batches**" 列为待做。`[推测]` **因此这条路线在"低并发"上的优势，会随着并发上升而收敛**；它解决的是"没人跟你抢 GPU"的问题，而不是"GPU 不够用"的问题。

`[分析者推断]` **对"这是重大突破"的反方解读**是：Fleet 在 MI350 + Qwen3-8B 上报告相对 vLLM 的 **1.3–1.5×** decode 延迟改善，MPK 报告最多 **1.7×** 端到端延迟改善，而本博客给出 1.9–3.3×。三组结果的模型、硬件、指标、基线和优化组合都不同，**既不能直接相减，也不能用前两组数字估算本博客中 megakernel 单项的贡献**。它们只能说明：持久化执行在不同系统里都能产生可观收益；本博客的复合倍数仍需同精度、同 drafter、同分区模式的消融才能拆解。

### 9.2 Limitations（本研究自身的边界）

1. **未运行任何 kernel、未在任何 MI355X/MI350 上测量、未复现任何数字。** 全部结论为来源转述 + 文档/仓库阅读。
2. **S01 博客全文已读至结尾**（含 What's Next、Summary、Additional Resources 与 Disclaimers），但**五张图（Figure 1–5）内部的坐标与数值未取到**，因此本报告引用的是**正文与图注中可核对的数字**，图内更细的分解未覆盖。
3. **未读** megakernel 的**源码**（`proaditya/aiter` 的 `aitermk-*` 分支内容、`fleet-chiplet-megakernel` 的 `src/`、`python/`、`include/`），因此本报告的"机制"描述**全部来自博客与 README 的文字**，未做实现级验证。
4. **未读** ATOM 与 AITER 的**复现 README 与 `build_and_repro.sh` 脚本内容**，故"复现门槛低"是基于脚本与容器 tag 的存在性与博客说明的推断，未实测步骤数与耗时。
5. **Fleet 论文只读了摘要**（arXiv:2604.15379），其方法细节、评测设置与"1.3–1.5×"的完整口径未核实；**MPK 论文同样只读摘要**。
6. **未做跨框架同条件实测**，第 7 章的比较基于各来源自述与公开能力边界，**不构成性能排名**。
7. **未检索社区复现与生产案例**；本报告未发现任何第三方复现，但也未系统检索。
8. **未核对 AMD 与 OpenAI 等其他厂商在同期是否给出同类数字**，因此无法判断 1.9–3.3× 在行业中的相对水位。
9. **未评估"用 AI coding agent 做 kernel 优化"这一方法本身的有效性**：S01 只说"hundreds of optimization experiments by AMD engineers and AI coding agents"，没有给出 agent 的贡献比例、成功率或失败模式。
10. **资料时点**：网络读取发生于 2026-10-25（UTC 17:51–18:20 左右）；博客发布于 2026-10-20，临时仓库在读取时仍为 0 star 状态；AMD 明说数字会随周更新。

---

## 十、对 Agent harness 的可迁移启示

`[分析者推断]` 本节面向 EverAgent 与同类 agent harness，不把 AMD 的倍数搬过来，只搬可迁移的判断与度量纪律。

1. **低并发是 agent 的常态，而 agent 的瓶颈常常不在模型上。** 一个"用户等回答"的 agent 回合里，模型 decode 只占一部分；**launch/同步/串行等待这类"调度开销"在低并发下占比更高**。`[推测]` 因此评估"换模型能快多少"时，应同时问"我们的 harness 自己加了多少串行等待"。
2. **把"每轮固定成本"与"每 token 边际成本"分开度量。** AMD 的 `speed ≈ accepted × 1000 / ms_per_round` 是一把很好的尺子；对应到 agent：**每个回合的固定成本（首 token 延迟、工具往返、上下文重建）与每 token 边际成本（decode）要分开报告**，否则"tok/s 提升 3×"会被误读成"任务快 3×"——AMD 自己就提醒了这一点。
3. **投机解码的收益必须按"接受长度 × 每轮耗时"重算，并随负载重新标定。** AMD 明说最优 drafter 与 draft 长度**依赖工作负载**（可预测的数学文本适合长 draft，密集对话文本一次最好）。agent 任务的输出结构差异极大，**照抄别人的 drafter 配置很可能适得其反**。
4. **上下文读取是硬下界，减字节数比减算力更值钱。** MXFP4 让"权重 + 262K KV cache"塞进一张卡——**这提示 agent harness：给模型塞更多上下文之前，先算清楚每 token 的存储与带宽成本**。
5. **"看起来能工作"与"结果正确"要分开验证。** GPT-OSS-120B 的"chat 格式 GSM8K 94.8–95.4% 持平"与"5-shot 原始文本 42.8% vs 35.5–39.3%"**指向两个不同的世界**。对 agent harness 的含义很直接：**同一个模型在不同提示格式与评测口径下可能表现迥异**，因此"我们的 eval 口径"必须显式声明格式与 few-shot 设置。
6. **把上游依赖的位置与稳定性当作选型的一部分。** "megakernel 代码住在 0 star 的临时仓库、未来几周会迁移"是一种**常态但少被讨论的风险**。对 harness 而言：**优先选有稳定归属地、可锁定版本、有上游 CI 的实现**；若必须用早期路径，至少把版本锁定与迁移检查写进运维清单。
7. **可迁移的最抽象一条**：**"把固定的每轮成本摊到多个有效输出上"**——这既是投机解码的原理，也是 agent harness 里"一次调用做更多事"的设计原则。

---

## 十一、思考与追问

### 11.1 我真正理解了什么

- **megakernel 不是"更快的 kernel"，而是"换掉执行模型"**：传统路径的 launch 与同步被摊进吞吐里，持久化路径把它们从关键路径上拿掉，剩下的下界就是"读一遍权重要多久"。AMD 的度量纪律（每轮 accepted token × 每轮 ms）是这条路线**最可迁移的遗产**。
- **四个杠杆的贡献是复合的、且彼此依赖**：投机解码之所以能省时间，是因为 megakernel 把每轮压得足够短；而投机解码的验证 pass 需要读更多专家（4 token 时约 11.7 个专家 vs 2 token 时 7 个），所以它更吃带宽——**于是数据放置的价值随投机一起上升**（1.08× × 1.27× ≈ 1.36×）。**单独优化任何一个杠杆都会错过这个耦合。**
- **这篇官方博客的可信度来自它的自我限定**，而不是来自它的数字：它明确说基线配置不同、计时方式偏向对照组、只比较 decode、"early results"、代码在临时仓库、精度异常正在排查。**一份把不利事实写进正文的厂商材料，比一份只有优点的材料更值得引用。**
- **"交互式"这个叙事正在把推理优化的目标从吞吐改成延迟**，而这直接改变了工程取舍：单请求下"少启动、少同步、单 die 读权重"比"多卡并行、多批处理"更重要——**这与过去五年"堆并发"的直觉相反**。

### 11.2 我还没搞懂什么

- **注意力路径的精度落差到底来自哪里？** megakernel 在 5-shot 原始文本 GSM8K 上 42.8%，而 BF16 attention 权重是 49–56%——**6–13 分的差距没有被归因**。是注意力 kernel 的上下文切分、MXFP4 注意力投影、还是别的？AMD 只说"正在排查"。
- **并发上升时倍数如何收敛？** 只有 Flash-Next 的 4 请求数据点（3.1× per user），且没有 8/16/32 的曲线。**这恰恰是 agent 部署最需要的形状。**
- **megakernel 与投机解码的耦合有多紧？** GPT-OSS-120B 三个数（3.6× 无投机 / 2.3× EAGLE3 / 1.6× 同 DFlash）说明在两边都用投机时 kernel 优势缩小——**那么"megakernel + 投机"这个组合的**真实**增益是多少？需要同 drafter、同精度的三方对照。
- **prefill 侧怎么办？** megakernel 路线只做 decode；长提示的 agent 负载里 prefill 占比可能很高，**端到端收益需要实测**。
- **"用 AI coding agent 做 kernel 优化"的可复制性**：AMD 说"hundreds of optimization experiments by AMD engineers and AI coding agents"。**agent 在其中扮演什么角色、成功率如何、失败模式是什么**，公开材料未涉及——**而这恰恰是本仓库最关心的元问题**。
- **Fleet 的 chiplet 调度何时能进入 megakernel 产品路径？** Fleet 是自动、拓扑感知的通用层；AMD 的 megakernel 是手写、模型专用的。**两者的合流点**（例如用 Fleet 的 chiplet 调度重写 Qwen megakernel）也许才是这条路线规模化的关键。

### 11.3 下一步读什么或做什么

1. 读 `proaditya/aiter` 的 `aitermk-qwen38` 分支源码与 `build_and_repro.sh`，核对本报告对"手递手 64-bit store / per-chiplet release words / 稀疏注意力块选择并行化"的转述是否与实现一致——**这是把"厂商叙述"升级为"代码事实"的唯一途径**。
2. 读 Fleet 论文全文（arXiv:2604.15379）与其 `docs/`、`src/` 中的调度实现，补上"chiplet-task 抽象如何映射到 AMD 的 megakernel"这一环；并核对 "1.3–1.5× vs vLLM（BS 1–8）"的完整评测设置。
3. 找 GPT-OSS-120B 精度异常的公开跟踪：AMD 是否已给出根因？若已修复，本报告 §9 的反方解读需要相应更新。
4. 在自己**真实的长上下文 + 多并发** agent 负载上做 §8.2 的最小验证，重点是第 5 条（并发曲线）与第 4 条（prefill 占比）——**这两个数字决定这条路线的净收益**。
5. 面向本仓库自身：把"每轮固定成本 vs 每 token 边际成本"的度量方式引入 agent harness 的 trace 记录，**先在自己的系统里把口径建起来**，再谈选型。

---

## 附：来源清单（可复核）

- S01 https://rocm.blogs.amd.com/software-tools-optimization/megakernel-intro/README.html （AMD ROCm Blogs，2026-10-20）
- S02 https://arxiv.org/abs/2604.15379 （Fleet: Hierarchical Task-based Abstraction for Megakernels on Multi-Die GPUs，2026-04-15）
- S03 https://arxiv.org/abs/2512.22219 （MPK: A Compiler and Runtime for Mega-Kernelizing Tensor Programs，v2 2026-06-10）
- S04 https://github.com/proaditya/aiter （AITER 临时镜像；分支 `aitermk-qwen38` / `aitermk-gpt-oss`；读取于 2026-10-25）
- S05 https://github.com/proaditya/ATOM （ATOM 临时镜像；读取于 2026-10-25）
- S06 https://github.com/sangeeta0201/fleet-chiplet-megakernel （Fleet 临时仓库，分支 `amd_mi350`；读取于 2026-10-25）
- S07 https://github.com/ROCm/FlyDSL （FlyDSL 上游；读取于 2026-10-25）
