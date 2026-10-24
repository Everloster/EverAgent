---
title: "vLLM 在 GB300 NVL72 上服务 DeepSeek-V4.1-Flash：P/D 分离 + Wide-EP 的机制拆解与口径核验"
domain: "ai-learning"
report_type: "概念深度解析"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["vllm", "deepseek-v4.1-flash", "P-D-disaggregation", "wide-EP", "EPLB", "DSpark", "GB300", "agentx", "moe"]
---

# vLLM 在 GB300 NVL72 上服务 DeepSeek-V4.1-Flash：P/D 分离 + Wide-EP 的机制拆解与口径核验

> **一句话结论**：vLLM 团队（Inferact 主导）在 2026-10-23 报告：用 **P/D 分离 + Wide-EP + EPLB** 在一台 **GB300 NVL72** 机架内服务 DeepSeek-V4.1-Flash。头条点实际使用 **64 GPU（16×DEP2 prefill + DEP32 decode）**、AgentX 并发 **10,888**，达到 **954,146 all-token/s/GPU、6,866 output-token/s/GPU、P90 196.46 token/s/user、P90 TTFT 7.974 秒**；相对第一篇在相近 interactivity 下的 DEP2 点（120,680 all-token/s/GPU、692.92 output-token/s/GPU、P90 171.53）分别是 **7.9×** 与 **9.9×**。`$38.96/GPU-hour` 是按 DeepSeek off-peak API 售价折算的 **token revenue per GPU-hour**，不是 GPU 租赁或 TCO 成本。上述结果仍是项目方提交与自报，本文未复现；更值得迁移的是 DEP2 prefill、Wide-EP/EPLB、以及机架尺度 CPU 开销的可核查机制与公开配置。

> **来源分级（贯穿全文）**：**【vLLM 自报】** 来自 vLLM 官方博客及其公开交互图；**【DeepSeek 自报】** 来自模型卡与 DeepInfer 仓库；**【第三方/基准方】** 来自 SemiAnalysis AgentX 方法学与指标定义；**【本报告推断】** 为我的分析并逐处标注。**本文未在 NVL72 或其它目标硬件上复现任何数字。**

---

## 目录

1. [问题定义：为什么要在 NVL72 上做 P/D + Wide-EP](#1-问题定义为什么要在-nvl72-上做-pd--wide-ep)
2. [模型侧前提：先把模型量清楚](#2-模型侧前提先把模型量清楚)
3. [部署形态与数据流](#3-部署形态与数据流)
4. [机制一：prefill 用小 DEP 实例](#4-机制一prefill-用小-dep-实例)
5. [机制二：Wide-EP 与 EPLB](#5-机制二wide-ep-与-eplb)
6. [机制三：CPU 开销在 NVL72 尺度上成为瓶颈](#6-机制三cpu-开销在-nvl72-尺度上成为瓶颈)
7. [机制四：专用 decode 路径与小批量低延迟](#7-机制四专用-decode-路径与小批量低延迟)
8. [关键数字与口径逐项核对](#8-关键数字与口径逐项核对)
9. [「vLLM matches DeepInfer」逐项判定](#9-vllm-matches-deepinfer-逐项判定)
10. [AgentX 口径与 954K 的含义](#10-agentx-口径与-954k-的含义)
11. [厂商自报边界清单](#11-厂商自报边界清单)
12. [硬件与网络前提](#12-硬件与网络前提)
13. [与其它路线的比较](#13-与其它路线的比较)
14. [对 EverAgent 双仓的现实价值](#14-对-everagent-双仓的现实价值)
15. [反方解释](#15-反方解释)
16. [Limitations](#16-limitations)
17. [思考与追问](#17-思考与追问)
18. [附录 A：来源清单](#附录-a来源清单)
19. [附录 B：数字速查](#附录-b数字速查)

---

## 1. 问题定义：为什么要在 NVL72 上做 P/D + Wide-EP

### 1.1 目标工作负载

DeepSeek-V4.1-Flash 是**为长程 agent 负载设计**的稀疏 MoE【DeepSeek 自报】：552B backbone、**prefill 每 token 激活 8B、decode 激活 16B**、原生 1M 上下文、原生多模态。vLLM 的目标因此不是「把一个模型跑快」，而是**在一台机架上同时服务大量长上下文 agent 会话**。

### 1.2 三个约束叠加

| 约束 | 内容 | 出处 |
|---|---|---|
| **KV 容量不再是瓶颈** | 全局 KV 仅 **890 bytes/token**（CSA2 跨层共享 + FP4 压缩），KV 能舒展地放进 HBM | 【DeepSeek 自报】模型卡；【vLLM 自报】博客复述 |
| **Decode 被 MoE 主导** | DEP4 decode、128K 上下文、每 rank 64 请求时，**MoE 占目标 step 的 62%**，attention 与 indexer 合计仅 13% | 【vLLM 自报】 |
| **上下文变长几乎不涨 decode 成本** | DEP32、每 rank 16 请求、每请求 6 token 时，128K→855K（6.7×）只让目标 forward 从 8.93ms 涨到 9.53ms（**+6.7%**） | 【vLLM 自报】 |

### 1.3 由此推出的策略

【vLLM 自报】的五条推论直接决定了后面的设计：

1. **prefill 应该跑在小 DEP**（DEP2）——小 world size 让 DP/EP 负载均衡变简单；
2. **KV 容量很少成为 batch 限制** → 可以把每个操作推到计算或带宽极限，而不必绕开 KV 容量；
3. **Wide-EP 对 decode 有效** —— decode 受权重读取（MoE）主导，Wide-EP 直接砍这块主导成本；
4. **decode 的 DP 负载均衡可以简化**为「按每 rank 请求数最小负载」，因为该模型的 decode step 时间随上下文变化很小；
5. **合成负载对 decode 仍有代表性**（用平均输入/输出长度即可估计性能，不必回放完整 agent 轨迹）——**这一点是后面所有数字口径的关键**。

---

## 2. 模型侧前提：先把模型量清楚

【DeepSeek 自报，来自模型卡与 vLLM 博客复述，二者一致】

| 项 | 事实 | 与本文的关系 |
|---|---|---|
| 架构 | **CED（因果编码器-解码器）**：40 层 = 20 层 causal encoder + 20 层 decoder；decoder 的全局 KV **由 encoder 末层 hidden states 投影而来**，而非各 decoder 层自身 | 解释了「decode 只处理最后 n_win 个 token」的可行性与 KV 共享结构 |
| 全局 KV | **890 bytes/token**（FP4 主 KV，E2M1 格式，每 16 通道一个 E4M3 scale），约为 V4-Flash 的 1/4 | 「KV 不成瓶颈」的来源 |
| CSA2 | 每层三种静态模式：**Full / Reindex / Reuse**，跨层共享主 KV 与 indexer K，并复用 Top-K 稀疏索引；decoder 侧用**层级稀疏 indexer**，把深层索引限制在第一层 Full 构造的候选池内 | 决定 indexer 成本不随上下文线性增长 |
| SWA Bounded Replay | 只重放最近 n_win 个 token 重建 SWA KV 状态，不必把 SWA KV 落 SSD → 持久 KV 约为 V4-Flash 的 **1/8** | vLLM 把 replay 延伸到第 20 层（+19.9%）的机制基础 |
| 稀疏注意力层 | **第 2、8、14 层使用 2× 压缩做全上下文索引**；第 20 层为所有 token 写全局 KV，但索引与 attention 只跑最后 128；第 21–39 层只处理这些 token | vLLM 的「layer 20 replay」改动正是把第 20 层也纳入只算 128 token |
| MoE | 每层 **1 个共享专家 + 384 个路由专家**，每 token 激活 **top-6** | 决定 Wide-EP 的形状与 EPLB 的粒度 |
| DSpark | 半自回归草稿生成 + 置信度调度验证；**草稿模型 128 个路由专家、top-3**（目标模型 384、top-6） | EPLB 必须分别跟踪两个模型的专家布局与负载 |
| Engram | 条件记忆，**196B 参数**，按 token 查表稀疏访问；其 host 表在 DP rank 间共享 | 解释了「2MB 大页」这条 CPU/TLB 优化为何必要 |
| 其它 | Single-Pass mHC + Mega-mHC kernel；DeepSeek-ViT 视觉编码器（2D-RoPE、3×3 pixel-unshuffle）；45T token 语料、64K 长度稀疏训练、34T token 处扩到 1M | — |

> 【本报告推断】**这一节是全文最「可核查」的部分**：模型卡的数字与 vLLM 博客的复述逐项一致（890 B/token、层 2/8/14、layer 20 replay 128、384+1 experts top-6、DSpark 128/top-3），说明**模型侧事实不是 vLLM 的自创叙事**；但**性能数字全部是 vLLM 自报**。

---

## 3. 部署形态与数据流

```
                   一台 NVIDIA GB300 NVL72 机架（72 GPU 可用，单一 scale-up 域）
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                                                                            │
 │  PREFILL 侧（头条点：16 个 DEP2 实例 = 32 GPU）                              │
 │   ┌──────────────┐   ┌──────────────┐                                    │
 │   │ DEP2 实例 A  │   │ DEP2 实例 B  │  … 每个实例 = 2 GPU                   │
 │   │ DP attention │   │              │  · 每 GPU 持有部分权重与专家           │
 │   │ + EP over 2  │   │              │  · 共享 KV（跨 head）→ DP 避免复制 KV   │
 │   └──────┬───────┘   └──────┬───────┘  · session affinity 保 prefix 局部性 │
 │          │ 共享前缀 / 亲和调度 │                                            │
 │          └────────┬─────────┘                                            │
 │                   │ 生成的 KV（按 token 分片）                              │
 │                   ▼                                                      │
 │   ┌───────────────────────────────────────────┐                           │
 │   │  KV 传输层（NIXL push + UCX scatter-gather）│  ← CPU 开销重灾区         │
 │   └───────────────────┬───────────────────────┘                           │
 │                       ▼                                                   │
 │  DECODE 侧（头条点：DEP32 = 32 GPU）                                        │
 │   ┌──────────────────────────────────────────────────────────────┐          │
 │   │ 32 GPU：DP attention + Expert Parallel over 32 ranks          │          │
 │   │ 每层跨 rank 同步 → 单 rank 慢即拖垮整个实例                    │          │
 │   │ EPLB：每 3000 步按前 1000 步负载重排专家（NVLink symm_mem 后端）│          │
 │   │ 目标模型 384 专家 top-6 ／ DSpark 草稿 128 专家 top-3（分别跟踪）│         │
 │   └──────────────────────────────────────────────────────────────┘          │
 │  头条配置合计 64 GPU；同一曲线其它点使用 34 / 40 / 44 GPU                    │
 └────────────────────────────────────────────────────────────────────────────┘
```

**术语**【vLLM 自报】：**DEP_n = data-parallel attention + expert parallelism over n GPUs**；**target forward** = 主模型在每个 decode step 的完整前向（验证草稿 token 并产出输出）；**draft forward** = DSpark 草稿模型的完整前向（提出下一步 token）。

---

## 4. 机制一：prefill 用小 DEP 实例

### 4.1 为什么小 DEP 更好【vLLM 自报】

AgentX prefill-only、并发 256 时：**DEP4 的每 GPU 吞吐只有 DEP2 的 83%**（53.3K vs **64.4K tokens/s**）。用「mirror（各 rank 同时收请求）vs lag（rank r 晚 r×5 秒收同样请求）」两种回放隔离 DP 不均衡：

| prefill 吞吐（tokens/s，每实例） | mirror（均衡） | lag（不均衡） | 损失 |
|---|---|---|---|
| **DEP2** | 138.7K | 130.5K | **5.9%** |
| **DEP4** | 267.6K | 231.1K | **13.6%** |

→ **DEP2 成为默认**。（脚注：该不均衡代价测于更早的构建，是 DEP 规模的性质而非 kernel 的性质。）

### 4.2 三个新优化（按收益排序）【vLLM 自报，均含 PR 号】

| 优化 | 机制 | 收益（32K 新 token） |
|---|---|---|
| **SWA bounded replay 延伸到第 20 层**（#59894） | 原先第 20 层仍对**全部新 token** 跑 indexer 计算；现在它仍为所有 token 写 KV，但**只对 128-token replay 批次跑其余计算** | **+19.9%**（4K 时 +10.1%，64K 时 +23.1%） |
| **共享 Engram host 表用 2MB 大页**（#62359） | 原先 `/dev/shm` 映射用 64KB GPU page → **频繁 GPU TLB miss**；改为 host-NUMA cuMem 分配以启用 2MB GPU page | **+2.8%** |
| **prefill indexer 用 DeepSelect top-k**（#62240） | indexer 改用 DeepSelect 对候选块排序，与 decode 路径一致；收益随被排序 key 数量增长 | **+15.6%**（64K 时 +15.2%） |

**合计**：在 128K 缓存前缀之上，**新 token prefill 吞吐提升 35.6%–43.9%**（4K–64K 范围）；**32K 处 +42.5%；64K 处从 71.2K 升到 102.5K tokens/s/GPU（+43.9%）**。

### 4.3 一个说明问题规模的数字【vLLM 自报】

两张 GB300 上：**8K token 的 prefill 在无既有上下文时 87.9ms，有 512K 缓存上下文时 189.4ms** —— 即**缓存上下文把「便宜的小 prefill」变成了「昂贵的 prefill」**。这正是 P/D 分离要解决的东西：把「读长上下文」与「算新 token」放到不同角色上。

---

## 5. 机制二：Wide-EP 与 EPLB

### 5.1 Wide-EP 的扩展性【vLLM 自报】

DEP4→DEP32、每 GPU 64 请求、128K 上下文、开启 EPLB：

- 目标模型的 **MegaMoE 时间从 13.4ms 降到 6.0ms**（每 rank 持有的专家更少）；
- **其余工作稳定在约 10ms**；
- 因此**每 GPU 吞吐增益逐级递减**；到 DEP32 时，**草稿侧的通信开销开始抵消更宽并行的收益**。

### 5.2 EPLB 做了什么【vLLM 自报】

- 每 **3000 步**重排一次专家，依据**前 1000 步**的负载；
- balancedness（每步 mean rank load / max rank load）从 **0.35 → 0.94**（目标模型）、**0.21 → 0.89**（草稿模型），**回收了到均匀路由差距的约 97% 与 93%**；
- 对照基准是「同一 decode batch 用均匀随机路由」的 balancedness：DEP32、每 GPU 72 请求时，目标模型（top-6）均匀路由约 **0.96**、草稿（top-3）约 **0.94** —— 该参考本身带采样噪声；
- 两项配套改动：**#62009** 引入基于 NVLink 的 `symm_mem` 后端，**不到一秒即可重平衡整个 DEP32 且不中断 decode**，并把 EPLB 的副本映射与负载记录**融合进 MegaMoE kernel**（每步省约 0.2ms），同时**移除 decode 循环中的 host 同步**；**#61395** 支持**异构目标/草稿模型**下的 EPLB（384/top-6 与 128/top-3 分别跟踪专家布局与负载）。

---

## 6. 机制三：CPU 开销在 NVL72 尺度上成为瓶颈

【vLLM 自报】Wide-EP decode **每层都要同步所有 rank**，所以一个慢 rank 会拖住整个实例；而 rank 越多，GPU step 越短、留给 CPU 的余量越少。实测：**未优化的 DEP32 比 DEP16 更慢（17.57 vs 13.84 ms/step），尽管其 GPU 执行快了 1.1ms** —— 典型的「GPU 更快、整体更慢」。

官方给出的四类原因与修复（**每行的效果来自不同设置，不能相加**）：

| 原因 | 修复 | PR | 效果 | 测量设置 |
|---|---|---|---|---|
| KV 读取在 decode worker 线程上**同步投递** | NIXL push + UCX scatter-gather；打包 KV 行作为单个 NIXL region | NIXL push connector、#61121 | **141K → 440K tokens/s per GPU；P90 ~40 → 159 tok/s/user** | GB300，8P1D，并发 3,072 |
| **Gloo all-reduce 延迟随 rank 数线性增长** | 递归倍增 CPU all-reduce | #61767（基于 #60267） | DP 同步 **10.8 → 1.5 ms/step**；step **16.10 → 13.15 ms** | DEP32 decode |
| **准入突发**：一步内最多 140 个请求被准入 | 可选「每步最多 4 次新 KV 加载」的限流 | #61725 | **460K → 516K tokens/s per GPU；P90 109 → 153 tok/s/user** | GB300，7P1D，并发 4,800（含另两项 CPU 修复） |
| **准入工作量随 prompt 长度增长** | prompt 作为一个 int32 buffer；跳过滑动窗口 block table 的空块；分块 prompt copy kernel | #59908、#62702、#61724、#62698 | 855K prompt：每次准入的 CPU 时间 **38.8 → 6.0 ms** | engine microbenchmark |

> 【本报告推断】这四条是全文**最有工程迁移价值**的部分：它们与「模型多稀疏」无关，是常见的分布式服务风险（同步投递、集合通信随规模劣化、准入突发、按输入规模线性增长的 CPU 工作），在本次 32-rank decode 与机架级编排下集中暴露。其它大规模 agent 服务是否出现同样排序，仍需用自身 trace 验证。

---

## 7. 机制四：专用 decode 路径与小批量低延迟

【vLLM 自报】延续上一篇文章的低延迟 kernel 支持（#61868、#61869）：在**真实 AgentX 会话**上，专用 decode 路径在**四张 B300**、并发 1 时达到 **P90 826 tokens/s（单用户）**，比标准 decode 路径（575）**高 44%**。

> **注意口径**：这 826 tok/s 是**四卡 TP4、并发 1、单用户**的场景，与第 8 节的机架级 954K tokens/s per GPU 属于**完全不同的配置**，两者不可互换引用。

---

## 8. 关键数字与口径逐项核对

| 数字 | 官方表述 | 口径与可核查性 | 判定 |
|---|---|---|---|
| **954K all-token/s/GPU** | 「On one NVIDIA GB300 NVL72 rack… 954K tokens/s per GPU」 | 交互图内嵌原始点为 **954,146.03**；配置 **16×DEP2 + DEP32，64 GPU，并发 10,888**；计入 cached input + uncached input + output；同点 output-only 为 **6,865.90 token/s/GPU**，P90 TTFT **7.974s** | **数据与配置可从公开交互图核对，真实性未独立复现**；all-token 口径不是纯计算吞吐 |
| **P90 196 tokens/s per user** | 同上 | 交互图原始值 **196.46**，定义为 P90 interactivity（1 / P90 inter-token latency）；不是单请求总吞吐 | 口径清楚；与 954K 属同一个并发 10,888 的运行点 |
| **7.9× all-token / 9.9× output-only** | 「a further 7.9×… over our aggregated single-node result」 | 交互图明确选取第一篇 DEP2、并发 32 的点：**120,679.53 all-token/s/GPU、692.92 output-token/s/GPU、P90 171.53**；新点为 954,146.03 / 6,865.90 / P90 196.46 | **同为 per-GPU 口径且分母公开可复算**；比较的是两个不同规模、不同并发的选定 operating point，不是同配置消融 |
| **$38.96 token revenue / GPU-hour** | 「at DeepSeek's off-peak prices」 | InferenceX 将 **Token Revenue per GPU Hour** 定义为按规范化或公开 token 售价折算的每 GPU 小时 token 销售价值；这里使用 DeepSeek off-peak API 价 | **不是硬件成本、租金或 TCO**，也不能直接推出利润；博客未展开各 token 类型的价格权重 |
| **826 tokens/s（单用户）** | 专用 decode 路径，**四张 B300、并发 1** | 与 954K 的机架级数字配置完全不同 | **不可与 954K 并列引用** |
| **vs DeepInfer decode「6% 以内」** | 「vLLM on GB200 achieves throughput within 6%… batch sizes 8–256」 | vLLM 交互图公开两组逐点数据：vLLM DEP32（32×GB200）与 DeepInfer EP64DP64（64×SM100）；两者都按 **batch × token/s/user = output token/s/GPU** 归一化。DeepInfer 数值仍是从其 README 图读取，而非同脚本复测 | **同模型、同 SM100 世代、同 nextn=3 的 per-GPU 曲线可比，但系统规模和实现不同，且 DeepInfer 点含读图误差** |
| **prefill「tracks DeepInfer」** | 「vLLM's DEP2 prefill tracks DeepSeek's own engine across the range they published」 | vLLM 自己明确：**「因为设置不同，我们不把两条曲线之间的差距读作引擎到引擎的加速比」** | **作者已自我设限**；这是全文最诚实的一句 |
| **+35.6%–43.9% prefill** | 三个优化叠加（layer 20 replay / 2MB page / DeepSelect top-k） | 基于 128K 缓存前缀、DEP2、32K–64K 新 token | **可对照代码复算的机制级结论**，但幅度仍为自报 |
| **balancedness 0.35→0.94** | EPLB 效果 | 与「均匀随机路由」参考比较；参考本身有噪声（0.96/0.94） | 口径较清楚，仍为自报 |
| **17.57 vs 13.84 ms/step** | 未优化 DEP32 慢于 DEP16，GPU 执行却快 1.1ms | 单点对比 | 机制级证据（说明 CPU 开销可反超 GPU 收益），数值未给多次重复 |
| **+19.9% / +2.8% / +15.6%** | 三个 prefill 优化的独立收益 | 各优化单独测量后叠加 | 属**可复现性较好**的一类（PR 号公开） |

---

## 9. 「vLLM matches DeepInfer」逐项判定

### 9.1 官方叙述与实际内容

> 「Under DeepSeek's decode configuration (131K context, nextn=3), vLLM on GB200 achieves throughput within 6% of DeepInfer's published results across batch sizes 8 to 256 (Figure 2).」
> 「…DeepInfer's published prefill curve uses EP4DP4 with 32 redundant experts and a 140-token bounded replay, on hardware the chart does not state, and we read its values off the chart. …Because the setups differ, we do not read the gap between the two curves as an engine-to-engine speedup.」

### 9.2 逐项判定

| 维度 | vLLM 侧 | DeepInfer 侧（README/图表） | 是否同口径 | 判定 |
|---|---|---|---|---|
| **模型与配置** | 131K 上下文、DSpark nextn=3、固定每 step 接受 3.25 token | vLLM 交互图按 DeepInfer 已发布的同一 decode 配置重建曲线 | 关键模型配置对齐 | **可比**；README 的默认 nextn=5 不代表该 benchmark 使用 5 |
| **硬件** | **32×GB200，DEP32** | README：decode 测于 **64×SM100，EP64DP64** | 同属 SM100 世代，但 GPU 数、整机与软件栈不同 | **适合 per-GPU 曲线比较，不是同机同跑的引擎消融** |
| **数据来源** | vLLM 自测 | **从 DeepInfer README 的图上读数** | **不是同一测量** | **不同口径** |
| **归一化** | 交互图用 `batch × token/s/user` 得到 output token/s/GPU | DeepInfer 原图给每用户速度与输出吞吐；vLLM 把读出的点转换为同一 per-GPU 口径 | 换算公式与逐点数组公开 | **可以复算**，主要不确定性来自对 DeepInfer 图片的读数 |
| **并发 / batch** | 8、16、32、64、128、256 requests per GPU | 同一组 requests per GPU 点 | 对齐 | **可直接逐点比较** |
| **Prefill** | DEP2、无冗余专家、128-token replay、GB300、**自有 prompts** | EP4DP4、32 个冗余专家、140-token replay、4×SM100 | **全部不同** | **明确不可比**（vLLM 自己这么说） |
| **结论强度** | 「matches」 | — | — | **作为“对 DeepInfer 已发布 decode 曲线的复现比较”，within 6% 成立**；它仍不是双方在同一机器、同一脚本下的独立复测，且两边共享代码血缘 |

### 9.3 双方的血缘关系（vLLM 官方陈述）

> 「两个引擎之所以接近，是因为它们在两个方向上共享血缘：**DeepInfer 最初构建于 vLLM 之上，而 vLLM 又持续集成 DeepSeek 库中的 kernel（MegaAttn、MegaMoE、Mega-mHC）**，并围绕它们优化了整个栈。」

【本报告推断】这句话对「6% 差距」是一个**很强的解释性变量**：两者共享同一批 DeepSeek kernel 与部分代码路径，因此「接近」**部分源于同源而非独立收敛**。这不否定工程成果，但意味着**「通用引擎匹配专用引擎」的证据强度需要打折**。

### 9.4 DeepInfer 自身仍缺的（README 明示）【DeepSeek 自报】

- VE / Prefill / Decode 分离（「most required engine functionality is already implemented」——即尚未提供）；
- 跨数据并行副本的负载均衡（prefill 与 decode 均缺）；
- 当前公开入口是 **offline engine**。

→ 【本报告推断】这恰好解释了两边能力的分野：**vLLM 强在「在线服务形态」（P/D、路由、调度、AgentX 在线回放），DeepInfer 强在「单模型离线内核」**。所谓「matches」正是在 DeepInfer 最强的那个维度（decode kernel 吞吐）上比较。

---

## 10. AgentX 口径与 954K 的含义

【第三方/基准方】SemiAnalysis InferenceX 的 AgentX 方法学要点：

| 项 | 事实 |
|---|---|
| 数据集 | 393 个 Claude Code 会话（opt-in 内部 trace 语料），**median 输入 142k token/请求、median 输出 444 token/请求**，44% 会话含 subagent |
| 回放 | **闭环（closed-loop）**回放；并发客户端数决定负载；合成 token 填充；seed 固定采样与起点。这里的 closed-loop 指请求到达受前序完成速度影响，**不是“闭源”** |
| 计量 | 每个配置 **1 小时 profiling 窗口**（warmup 不计入）；每个并发点重跑 |
| 投机解码 | AgentX **强制**使用 SPEED-Bench 测得的固定接受长度（按模型/投机器/草稿长度/思考模式组合） |
| DRAM | 无标准化 DRAM 的服务器上限 **3 TB**，每配置只能按 GPU 配额比例访问 |
| 边界声明 | 「AgentX 衡量的是**服务系统性能**；其合成载荷**不支持模型质量评估**」；闭环回放下**更快的配置会完成更多请求、遇到略有不同的负载混合**，低并发时最明显 |

### 10.1 因此「954K tokens/s per GPU」应当怎样读

1. **它是逻辑吞吐**：图注写明计入 cached input + uncached input + output；与本仓其它报告里 Cloudflare 的「logical tok/s」属**同一类口径**——缓存命中的输入被计入，因此**数值会显著高于纯计算吞吐**；
2. **它不是单请求速度**：同一部署的 P90 是 196 tok/s/user；
3. **闭环回放的负载漂移**：更快配置完成更多请求 → 负载混合变化；因此 954K 与任何其它系统的数字比较都需要同一 AgentX 版本与同一并发配置；
4. **已披露配置**：并发 10,888；16×DEP2 prefill + DEP32 decode；共 64 GPU；标准 AgentX profiling 窗口 1 小时；P90 TTFT 7.974 秒；
5. **仍未披露**：cached input 与 uncached input 的分别吞吐，以及 `$38.96` 折算中每类 token 的价格权重。

【本报告推断】**「954K」最容易被误读为「每 GPU 每秒新算 954K token」**。公开点显示 output-only 仅 6,866 token/s/GPU，即约 **99.3% 的 all-token 计数来自输入 token**；但 cached 与 uncached input 的拆分没有披露，不能再断言其中多少是缓存命中。这个数字更接近「长上下文、多轮前缀复用条件下的服务工作量」指标，而不是 GEMM 效率指标。

---

## 11. 厂商自报边界清单

| 结论 | 谁说的 | 可核查性 |
|---|---|---|
| 模型架构、KV 890 B/token、专家数/top-k、DSpark 草稿形状、1M 上下文 | **DeepSeek 自报**（模型卡） | 有官方文档，**但无第三方验证** |
| DeepInfer 的 prefill/decode 曲线 | **DeepSeek 自报**（仓库 README 与图） | 图可读，**数值未提供 raw 数据** |
| vLLM 的 954K / P90 196 / 7.9× / output-only 9.9× | **vLLM 自报** | 交互图内嵌逐点数组与配置，**数据可审计、测量未独立复现** |
| `$38.96 token revenue/GPU-hour` | **vLLM 自报 + InferenceX 指标定义** | 是按 token 售价折算的收入等价值，**不是 TCO 或利润** |
| vLLM「within 6% of DeepInfer」 | **vLLM 自报 + 对 DeepInfer 图读数** | vLLM 公开了转换后的逐点数组，DeepInfer 原始点仍来自图片 |
| 三个 prefill 优化的收益（19.9/2.8/15.6%） | **vLLM 自报** | 有 PR 号，**机制可核查、幅度不可** |
| CPU 开销四因与修复效果 | **vLLM 自报** | 有 PR 号与设置说明 |
| EPLB balancedness 0.35→0.94 | **vLLM 自报** | 有对照定义（均匀随机路由） |
| AgentX 方法学 | **基准方自述**（SemiAnalysis） | 方法学公开，**本文未独立运行** |
| 「DeepInfer 最初构建于 vLLM 之上」 | **vLLM 自报** | 与本仓既有 DeepInfer 报告的观察方向一致 |

---

## 12. 硬件与网络前提

| 项 | 前提 |
|---|---|
| **整机架** | **GB300 NVL72**（72 GPU 可用，单一 scale-up 域）；头条点使用 **64 GPU = 16×DEP2 prefill + DEP32 decode**，同图其它点使用 34/40/44 GPU |
| **对比机架** | DeepInfer decode 测于 **64 张 SM100**、prefill 测于 **4 张 SM100**；vLLM 的 decode 对比用 **GB200** |
| **小实例机架** | 专用 decode 路径实验用 **4×B300**（TP4、并发 1/8/16） |
| **通信** | EP 每层跨 rank 同步；**NIXL push + UCX scatter-gather** 传 KV（打包为单个 NIXL region）；**Gloo** CPU all-reduce 被换成递归倍增；**NVLink `symm_mem`** 用于 EPLB 重平衡（<1s、不中断 decode） |
| **主机内存** | Engram 的 host 表跨 DP rank 共享，需 **host-NUMA cuMem 分配**以启用 **2MB GPU page**（原 `/dev/shm` 64KB page → GPU TLB miss） |
| **显存与 KV** | FP8/NVFP4 KV 与 MegaAttention 组合；V4.1 在该 benchmark 中**不需要 KV offload** |
| **软件** | vLLM（主分支，多个 PR）；DeepSeek 开源的 MegaAttn / MegaMoE / Mega-mHC 等 kernel；AgentX 提交由 NVIDIA 协助 |
| **经济口径** | **DeepSeek 官方 off-peak token 售价**用于折算 `$38.96 token revenue/GPU-hour`；不代表 GPU 租金、TCO 或利润 |
| **人力** | 该工作由 **Inferact** 主导，NVIDIA 多位工程师协作，vLLM 社区贡献 prefill 优化 |

---

## 13. 与其它路线的比较

| 路线 | 形态 | 优势 | 局限 |
|---|---|---|---|
| **vLLM 通用引擎 + P/D + Wide-EP**（本文） | 在线服务，机架级 | 通用、在线、多模型、P/D 与路由齐备；**复用 DeepSeek kernel** | 依赖 NVL72 级 scale-up 域；头条配置使用 64 GPU；数字均为自报 |
| **DeepInfer 专用引擎**（DeepSeek 自有） | **offline** 引擎 | 单模型深度优化、batch-invariant、确定性采样；发布 prefill/decode 曲线 | **P/D 分离与跨 DP 副本负载均衡仍缺**；无在线服务形态 |
| **单节点聚合部署**（vLLM 第一篇） | 在线，单节点 | 简单、成本低；低并发延迟好（TP4 + FlashInfer） | 吞吐上限受节点内带宽与 GPU 数限制 |
| **专用小模型/蒸馏**（另一条降本路线） | 模型侧 | 单请求便宜 | 能力上限不同；与本文不是同一问题 |
| **KV 压缩 / 稀疏注意力**（模型侧，本文 §2） | 模型侧 | **让 KV 不成为瓶颈**，是「KV 容量很少限制 batch」的前提 | 需要模型与引擎协同（跨层共享、indexer 复用） |
| **自建小规模部署**（如单节点/少卡） | 本地 | 成本低、可控 | 无法复现 NVL72 级 scale-up 与本次 64-GPU 头条配置；本文的多数机架级结论与之无关 |

【本报告推断】**真正可迁移的不是「机架」，而是三条「规模无关」的结构性认识**：①**prefill 与 decode 是两种不同负载，应由不同实例承担**；②**decode 的主导成本会随模型结构变化**（这里是 MoE 权重读取，所以 Wide-EP 有效；换模型结论会变）；③**在足够大的规模上，CPU 开销会盖过 GPU 收益**。

---

## 14. 对 EverAgent 双仓的现实价值

> **定位说明**：EverAgent 是公开的「个人学习与研究工作台」，其工作负载是**报告生产、日报、播客与多 agent 协作**；另一仓承担私有基础设施。**本节只讨论结构性可迁移项，不涉及任何私有设备、网络或账号信息，也不建议在本工作台上复刻机架级部署。**

### 14.1 现实判断

| 判断 | 依据 |
|---|---|
| **机架级复刻不现实**：NVL72 级服务部署与个人知识工作台的报告、日报、播客等低吞吐任务没有对应形态 | 这里的瓶颈通常是证据读取、编排、复核与等待，而不是单机架 token 吞吐 |
| **但「结构性认识」高度可迁移**，尤其在多 agent 协作的**编排层** | 见 §14.2 |

### 14.2 四条可迁移项与落地方式

| # | 可迁移认识 | 在本工作台的落地形态 |
|---|---|---|
| 1 | **prefill 与 decode 分离**（prefill 吃长上下文、decode 吃生成） | 本仓的「**长文档预处理**（下载、抽取、精读）」与「**写作/复核**」天然是两类负载 → **在流程上把它们当成不同的成本中心**：预处理可批量、可缓存、可并行；写作阶段保持交互式。落地动作：报告生产的「资料抓取+精读」阶段与「成文+复核」阶段分别记录耗时与成本 |
| 2 | **小实例更简单**：DEP4 比 DEP2 差 13.6% 的根因是 **DP 不均衡** | 多 agent harness 里存在同构问题：**不同 worker 的负载天然不均**。落地动作：把「worker 负载均衡」当作一等公民（最少负载 vs 最少任务数），并在证据里记录**不均衡代价**；这也是 EPLB 思想的抽象版（按实测负载重排任务亲和） |
| 3 | **CPU/编排开销会盖过模型收益**（未优化 DEP32 比 DEP16 慢，尽管 GPU 更快） | 多 agent harness 的「**编排开销**」（派发、串行等待、重复读取同一文件、重复解析同一产物）常常大于模型推理成本。落地动作：把「每个 agent 回合的工具调用次数、重复读取量、串行等待」纳入观测指标——这与本仓其它报告（Cloudflare 成本报告里的「每轮一次工具调用」）指向同一结论 |
| 4 | **缓存与亲和性**：P/D 下的 KV 传输与 prefix 亲和、session affinity 保 prefix 局部性 | 本仓的上下文工程原则（稳定前缀、共享资料只读一次）已是同构实践；可加一条：**跨轮次复用同一份已解析材料，而不是每轮重新解析** |

### 14.3 建议的可执行 eval（低成本，不涉及硬件）

| eval | 指标 | 判据 |
|---|---|---|
| **E1 编排开销占比** | 每篇报告的「编排/重复读取/串行等待」耗时 ÷ 总耗时 | 若编排占比 > 模型耗时，则优先做工程优化而非换模型 |
| **E2 worker 不均衡代价** | 最慢 worker 用时 ÷ 平均 worker 用时 | 参照本文「DEP4 不均衡损失 13.6%」的量级设定本地阈值 |
| **E3 前缀复用率** | 稳定前缀在连续轮次中被复用的比例 | 直接对应「共享前缀」收益 |
| **E4 每报告工具调用数** | 工具调用次数与「被调用工具真的产生信息」的比例 | 对应本文「一次调用读一个文件」的反模式 |

> 【本报告推断】**这四条 eval 的共同点**：它们衡量的都是**编排与上下文**，而不是模型能力 —— 这与本工作台的定位（知识资产生产，而非训练前沿模型）一致。

---

## 15. 反方解释

对「通用引擎在机架级达到专用引擎水平」这一结论，至少有六种同样成立于原文事实的反方解释：

1. **血缘解释**：「6% 差距」部分源于 DeepInfer 本身构建于 vLLM 之上、且共享 DeepSeek kernel → **「接近」不是两个独立路线的收敛**；
2. **读图解释**：DeepInfer 的原始数值由 vLLM 从 README 图片读取；vLLM 已公开换算后的逐点数组和 per-GPU 公式，但小于 6% 的差异仍可能受图片读数精度影响；
3. **口径解释**：954K 计入缓存命中的输入 → **与「纯计算吞吐」不可比**，与其它系统的对比若未统一口径会失真；
4. **基线解释**：7.9× 比较的是新机架配置与第一篇中一个已经优化过的 DEP2 operating point；它说明 scale-out + P/D + Wide-EP 的综合变化，不是相对 day-0 的单项消融，也不应与第一篇的 5× 直接相乘后归因给某个机制；
5. **经济口径解释**：$38.96/GPU-hour 是按 DeepSeek off-peak token 售价折算的**收入等价值**，不是硬件成本或利润；换一个售价表会改变该数值，但不会改变实测吞吐；
6. **规模解释**：全部收益来自「足够大 + 足够快」的系统 → **对小规模部署，Wide-EP 的通信成本可能超过收益**（本文自己给出 DEP32 草稿侧通信开始抵消收益的证据）。

> **综合判断**【本报告推断】：**这篇博客最可靠的产出是「机制与代价清单」**（prefill 小实例 + 三项优化的量化、DP 不均衡的量化、EPLB 的 balancedness、CPU 四因与修复、专用 decode 路径），**而不是「954K / 7.9×」这些头条数字**。

---

## 16. Limitations

1. **全部性能数字为 vLLM/InferenceX 提交数据**，本文未在 GB300/GB200/B300 硬件上复现；交互图公开数据点不等于第三方复测。
2. **头条点的配置并非缺失**：公开交互图给出并发 10,888、16×DEP2 + DEP32、64 GPU、P90 TTFT 7.974 秒、all-token 与 output-only 吞吐，以及 7.9× 的精确分母。仍缺的是 cached/uncached input 拆分和 `$38.96` 的逐项价格权重。
3. **954K 是逻辑吞吐**（计入缓存命中的输入），不能读作纯计算效率。
4. **与 DeepInfer 的 decode 比较是“本次实测 vs 已发布曲线”**：同为 SM100 世代并已统一到 output token/s/GPU，但 GPU 数、系统软件和测量运行不同，DeepInfer 点还含图片读数误差；prefill 设置差异更大，vLLM 自己不把差距解释为引擎加速比。
5. **「硬件未披露」这一说法可以补强**：DeepInfer README 写明其 decode 测于 64×SM100、prefill 测于 4×SM100 —— **但那是 README 的口径，不是图表的**。
6. **模型侧事实同样来自 DeepSeek 自报**（模型卡），无第三方测量；本文仅核对 vLLM 博客与模型卡之间的一致性。
7. **AgentX 方法学为基准方自述**，本文未运行；其**闭环回放**会产生负载漂移。
8. **闭环回放的固有偏差**：更快配置完成更多请求 → 负载混合变化，低并发最明显。closed-loop 不是 closed-source。
9. **CPU 开销四因的行间效果来自不同设置**，官方明确不可相加。
10. **本文未涉及**：成本模型的完整假设（机架折旧、电费、运维）、长期稳定性、故障恢复、以及除 AgentX 之外的负载形态。
11. **与本仓既有 DeepInfer 报告的关系**：该报告覆盖 DeepInfer 仓库、DSpark、CED 等源码级细节；本报告只做「vLLM 机架级服务 vs DeepInfer offline 引擎」的对照，不重复其源码分析。
12. 本文标注为 **【本报告推断】** 的部分（口径影响、6% 结论强度、6 条反方解释、本工作台的四条 eval 设计）均为我的推断而非原文陈述。

---

## 17. 思考与追问

1. **「954K」这类数字该以什么形式发布？** 当前交互图已经能切换 all-token 与 output-only；若再把 cached input 与 uncached input 分开列，读者就能判断输入吞吐中有多少来自缓存命中。**AgentX 是否应提供这一级拆分？**
2. **与 DeepInfer 的比较能否变成可复现实验？** 条件其实已具备：同一模型、同一硬件世代、公开的 decode 配置（131K、nextn=3）。**缺的只是「双方用同一脚本跑」** —— 谁来做这件事，谁就能把「matches」从读图变成事实。
3. **「血缘」该如何在比较中处理？** 当两个引擎共享 kernel 与代码路径时，「6% 差距」是**工程结论**但不是**独立验证**。未来的评测是否应披露「实现血缘」这一维度？
4. **DP 不均衡的 5.9%/13.6% 能否成为通用指标？** 这两个数字来自一套特定的回放方法（mirror vs lag）。**在真实 agent 轨迹上（长度差异巨大、到达时间不均）不均衡代价是多少？** 本文的 lag 回放刻意让 rank 做同样的工作，**可能低估**了真实场景的失衡。
5. **CPU 开销的四个原因，在 agent harness 里对应什么？** 「同步投递」「集合通信随规模劣化」「准入突发」「按输入规模线性增长的 CPU 工作」—— 在多 agent 编排里分别是：**串行等待同一资源**、**worker 数增加导致协调变慢**、**批量派发造成突发**、**重复处理长输入**。**是否存在同一套「归因清单」方法论？**
6. **专用 decode 路径 826 tok/s（4×B300、并发 1）意味着什么？** 如果「为特定 batch 形态定制路径」能带来 44% 提升，那么**为 agent harness 的典型并发点各做一条路径**是否可行？还是必然走向维护爆炸？
7. **EPLB 的思想能否移植到「模型路由」？** EPLB 按实测负载重排专家亲和；对应的 agent 版是**按实测负载重排「模型 × 任务类型」的亲和**（例如某类任务长期偏向某个模型/某个 effort 档）。**在多模型 harness 里，是否有人测过这种亲和收益？**
8. **7.9× 的经济含义**：若把「机架吞吐」换成 TCO、单位成功会话成本或毛利，结论会怎样？`$38.96 token revenue/GPU-hour` 只是售价映射，**收入等价值不等于成本下降或利润**。
9. **对模型侧的反向问题**：KV 890 B/token 让「KV 不成瓶颈」，于是瓶颈转移到 **MoE 权重读取** → **Wide-EP**。**下一个模型如果让 attention 重新成为主导（更少专家、更长上下文），这套部署形态会怎样？** 说明「部署形态」与「模型结构」是耦合的，不能各自独立优化。
10. **最后**：**若把这些「口径纪律」搬回本工作台** —— 我们的报告成本、时长、缓存命中、工具调用数，是否也应当**只报告拆分后的口径**（例如「命中缓存的输入 token」与「新读入的 token」分列）？**否则本仓自己的数字也会在未来被误读。**

---

## 附录 A：来源清单

| ID | 来源 | 类型 | 用途 |
|---|---|---|---|
| S01 | vLLM 官方博客（2026-10-23）— *DeepSeek-V4.1-Flash 大规模服务：P/D + Wide-EP* `https://vllm.ai/blog/2026-10-23-deepseek-v41-flash-pd-wide-ep` | 一手（vLLM 自报） | 主线：954K/P90/7.9×/$38.96、模型侧测量、DEP2 prefill 与三项优化、Wide-EP 与 EPLB、CPU 四因、专用 decode 路径、与 DeepInfer 的对照 |
| S02 | vLLM 官方博客（2026-10-07）— *DeepSeek-V4.1-Flash on vLLM: 5x Agentic Throughput* `https://vllm.ai/blog/2026-10-07-deepseek-v41-flash` | 一手（vLLM 自报） | 「第一篇」基线口径：单节点聚合、相对 day-0 的 1.9×/5×、TP4+FlashInfer 与 DEP2 两条路径、MegaAttention/NVFP4 |
| S03 | DeepInfer 官方仓库 README（固定 commit `774ce244b87cc0eb8d4b94ab9f5de2ab22049f01`） | 一手（DeepSeek 自报） | DeepInfer 的定位、**benchmark 硬件说明（prefill 4×SM100、decode 64×SM100）**、图表坐标（prefill 非缓存输入吞吐 vs 延迟；decode 输出吞吐 vs 每用户速度）、DSpark/replay 默认值、仍缺的 P/D 与负载均衡 |
| S04 | DeepSeek-V4.1-Flash 官方模型卡（`deepseek-ai/DeepSeek-V4.1-Flash`） | 一手（DeepSeek 自报） | 552B/8B-16B 激活、CED 40 层、CSA2 三模式、层级稀疏 indexer、FP4 KV 890 B/token、384+1 专家 top-6、Engram 196B、DSpark、1M 上下文、45T token 训练 |
| S05 | SemiAnalysis InferenceX — *AgentX Methodology and Datasets* `https://inferencex.semianalysis.com/agentx` | 一手（基准方） | AgentX 口径：393 会话、median 142k/444、闭环回放、1 小时窗口、固定投机接受长度、DRAM 配额、只测服务性能与负载漂移声明 |
| S06 | SemiAnalysis InferenceX Glossary — *Tokens per dollar* `https://inferencex.semianalysis.com/glossary/tokens-per-dollar` | 一手（基准方） | 区分 TCO tokens/$ 与 **Token Revenue per GPU Hour**；后者使用规范化或公开 token 售价 |

**来源分级**：S01–S02 为 vLLM 自报（对「做了什么、机制为何、公开图内数据」是一手事实；对「测量是否可复现」仍是自报）；S03–S04 为 DeepSeek 自报（模型规格与官方曲线）；S05–S06 为基准方自述。**本文未复现任何性能数字。**

---

## 附录 B：数字速查

| 类别 | 数字 |
|---|---|
| 头条 | 头条点：**64 GPU = 16×DEP2 + DEP32**，并发 **10,888**；**954,146 all-token/s/GPU**、**6,865.90 output-token/s/GPU**、**P90 196.46 tok/s/user**、P90 TTFT **7.974s**；相对旧点 120,679.53 / 692.92 / P90 171.53 为 **7.9× all-token、9.9× output-only**；**$38.96 token revenue/GPU-hour**；专用 decode 路径 4×B300 并发 1 为 826 tok/s |
| 模型 | 552B backbone；prefill 激活 8B / decode 16B；40 层 CED（20+20）；全局 KV **890 B/token**（≈V4-Flash 的 1/4）；持久 KV ≈1/8；层 2/8/14 用 2× 压缩做全上下文索引；layer 20 只对最后 128 token 跑索引与 attention；1 共享 + 384 路由专家 top-6；DSpark 草稿 128 专家 top-3；Engram 196B；45T token 训练；1M 上下文 |
| Decode 结构 | 128K 上下文、64 请求/rank 时 **MoE 占目标 step 62%**，attention+indexer 合计 13%；DEP32、16 请求/rank、6 token/请求时 128K→855K 仅 **+6.7%**（8.93→9.53ms） |
| Prefill | AgentX prefill-only 并发 256：**DEP4 只有 DEP2 的 83%**（53.3K vs 64.4K tok/s per GPU）；mirror→lag 损失：**DEP2 5.9%、DEP4 13.6%**（138.7K→130.5K；267.6K→231.1K） |
| Prefill 优化 | layer 20 replay **+19.9%**（4K +10.1%、64K +23.1%）；Engram 2MB page **+2.8%**；DeepSelect top-k **+15.6%**（64K +15.2%）；合计 **35.6%–43.9%**，32K 处 +42.5%，64K 处 71.2K→102.5K tok/s/GPU（+43.9%）；8K prefill：无上下文 87.9ms vs 512K 缓存上下文 189.4ms |
| Wide-EP/EPLB | MegaMoE 时间 DEP4→DEP32：13.4→6.0ms，其余约 10ms；EPLB 每 3000 步按前 1000 步负载重排；balancedness **0.35→0.94**（target）、**0.21→0.89**（draft）；回收差距 ~97%/~93%；均匀随机参考 0.96/0.94；symm_mem 重平衡 **<1s** 不中断 decode；融合进 MegaMoE 每步省 ~0.2ms |
| CPU 开销 | DEP32 未优化 17.57ms/step vs DEP16 13.84ms/step（GPU 反而快 1.1ms）；NIXL push+UCX：**141K→440K tok/s per GPU**、P90 ~40→159；递归倍增 all-reduce：DP 同步 **10.8→1.5ms/step**、step 16.10→13.15ms；每步最多 4 次新 KV 加载：**460K→516K tok/s per GPU**、P90 109→153；855K prompt 每次准入 CPU **38.8→6.0ms** |
| DeepInfer 对照 | vLLM GB200 decode **「within 6%」**（batch 8–256，读图）；DeepInfer README：prefill 测于 **4×SM100**、decode 测于 **64×SM100**；DeepInfer prefill 配置 EP4DP4 + 32 冗余专家 + 140-token replay；vLLM 用 DEP2、无冗余专家、128-token replay、GB300、**自有 prompts** |
| AgentX | 393 会话；median 输入 **142k**、输出 **444**；闭环回放；1 小时窗口；固定接受长度；DRAM 上限 3 TB 按 GPU 配额分配；只测服务性能；更快配置会完成更多请求导致负载漂移 |
