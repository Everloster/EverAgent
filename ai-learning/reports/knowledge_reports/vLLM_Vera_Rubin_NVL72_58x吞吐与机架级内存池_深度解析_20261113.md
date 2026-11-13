---
title: "vLLM 在 Vera Rubin NVL72 上服务 DeepSeek-V4.1-Flash：SM107 内核重写、TP8 低延迟与机架级内存池（系列第三篇）"
domain: "ai-learning"
report_type: "concept_report"
source: "vLLM 官方博客"
source_url: https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin
status: "completed"
created: "2026-11-13"
updated_on: "2026-11-13"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["vllm", "deepseek-v4.1-flash", "vera-rubin", "nvl72", "sm107", "fp4", "dep", "wide-ep", "tp8", "mooncake", "engram", "dynamo", "agentx", "inferact", "kv-cache"]
---

# vLLM 在 Vera Rubin NVL72 上服务 DeepSeek-V4.1-Flash：SM107 内核重写、TP8 低延迟与机架级内存池（系列第三篇）

> **一句话结论**：vLLM 团队（**Inferact 主导**，NVIDIA 早期硬件合作）2026-11-12 发布系列第三篇：把第二篇的 GB300 NVL72 栈（P/D 分离 + Wide-EP，[本库前作解析](../knowledge_reports/vLLM_DeepSeek-V4.1-Flash_PD分离与Wide-EP机架级服务_深度解析_20261025.md)）搬到 **Vera Rubin NVL72**，在 SemiAnalysis AgentX 上达到【vLLM 自报】**单机架 all-token 吞吐 1.7M tokens/s/GPU（峰值 2.52M）**，同时每用户 **P90 387 tokens/s**；单用户专用路径 **P50 1,844 tokens/s**。收益来自三件事：为 Rubin 的**双内存域 + SM107 宽块缩放 MMA** 重写内核（DEP prefill 每步 -28%、decode -25%）；跨两 tray 的 **TP8 低延迟路径**；以及**机架级共享内存池**（Mooncake KV 池 DRAM→空闲 HBM、Engram 表 HBM 分片 + Dynamo 按负载路由，prefix 命中率 96.5–97%，并发 4,800 时请求数 +68%、TTFT P50 29.8s→4.2s）。标题的 **"58× GB300"** 自带交互水平限定（"…at 387 tokens/s"），即 Rubin 侧工作点固定在 387 tok/s/user 的对比口径，未说明 GB300 侧对比配置【本报告推断，见 §6】；与前作同栈 GB300 头条数字直接相除是 1.78×。全部数字为项目方自报，本文未复现。

> **来源分级（贯穿全文）**：**【vLLM 自报】**来自官方博客正文与图注；**【DeepSeek 自报】**来自模型卡/前作引述；**【第三方】**来自 SemiAnalysis AgentX 方法学；**【本报告推断】**为本文分析，逐处标注。本文未在任何目标硬件上复现。

---

## 目录

1. [系列位置与前作基线](#1-系列位置与前作基线)
2. [Rubin 硬件三事实（一切优化的出发点）](#2-rubin-硬件三事实一切优化的出发点)
3. [内核重写：prefill -28% / decode -25% 从哪来](#3-内核重写prefill--28--decode--25-从哪来)
4. [低延迟专用路径：TP8 跨 tray](#4-低延迟专用路径tp8-跨-tray)
5. [机架级内存池与 Dynamo 路由](#5-机架级内存池与-dynamo-路由)
6. [关键数字与口径逐项核对](#6-关键数字与口径逐项核对)
7. [迁移要点与本库连线](#7-迁移要点与本库连线)
8. [厂商自报边界清单](#8-厂商自报边界清单)

## 1. 系列位置与前作基线

这是 DeepSeek-V4.1-Flash 服务系列的第三篇：第一篇做 day-0 bring-up 与 kernel fusion；第二篇（GB300 NVL72，P/D 分离 + Wide-EP + EPLB）的头条数字是【vLLM 自报】64 GPU、AgentX 并发 10,888、**954,146 all-token/s/GPU、P90 196.46 tok/s/user、TTFT P90 7.974s**（前作口径见[本库 2026-10-25 解析](../knowledge_reports/vLLM_DeepSeek-V4.1-Flash_PD分离与Wide-EP机架级服务_深度解析_20261025.md)）。第三篇保持同一负载（AgentX）与同一方法学（`vllm bench forward` 走真实 `execute_model` 路径、真实权重与真实 AgentX token），把栈整体搬到 Vera Rubin NVL72——"我们介绍过 Rubin（上月）"，本篇是同栈新硬件的横向纵深。

模型侧前提沿用前作：DeepSeek-V4.1-Flash 是小 KV、384 选 6 的 MoE，配 DSpark 投机解码（本篇固定接受率 3.51 token/步）与 Engram 2×94.4 GiB n-gram 表【vLLM/DeepSeek 自报】。

## 2. Rubin 硬件三事实（一切优化的出发点）

【vLLM 自报】三条硬件性质决定了全部优化方向：

1. **每 GPU 两个内存域**：SM 读本域远快于交错内存，更慢于跨域。受带宽约束的数据（MoE 权重、LM head、MegaMoE combine buffer、mHC residual stream）必须 die-local 化——**NUMA 语义回到了 GPU 内部**。
2. **SM107 加宽块缩放 MMA**：新的 K64 混合精度（FP8×FP4）MMA 每指令做两倍工作（MegaMoE 8K+ token/rank 时 +8–11% 吞吐；低批量 routed GEMM +12%）；indexer 用新 K128 FP4 MMA + 六 token query tile，decode MQA-logits 内核快 15–22%。
3. **72 GPU 共享一个 NVLink 域**：TP8 可以几乎零成本跨两个 compute tray（跨 tray all-reduce 只贵 0.3 µs）；prefill 实例可以直接读彼此 HBM——**大表不再需要每实例复制一份**。

## 3. 内核重写：prefill -28% / decode -25% 从哪来

保留 GB300 的三种引擎形态（DEP2 prefill、Wide-EP decode（DEP16/32）、TP 低延迟路径）与 DeepSeek 内核集（MegaMoE/MegaAttn/Mega-mHC/MegaGate/DeepSelect），为 SM107 大量重建【vLLM 自报】。DEP2/16/32 = data-parallel attention + expert parallelism over 2/16/32 GPU。

**DEP prefill（32K token/rank 每步 -28%）**，按收益：

- **MegaMoE 按"最忙 rank"定 tile**：eager prefill 不做 DP batch padding，86% 的真实 DEP2 prefill 步里空闲 rank 按自己的小 token 数定 tile、专家却服务忙 rank 的 token——tile 改为取本地与 DP 均值的较大者后，40 步回放中 MegaMoE 时间 **-55%**，相邻空闲 rank 的单请求 TTFT 8K→32K 降 13–39%。
- **Mega-mHC residual 驻留 die-local 池**：prefill 尺寸下该内核 HBM-bound（每 token 约 100KB 四路 residual），residual 改为跨两域条带化、每域一个 task counter、SM 先排干本域；354→317 µs/调用。
- **Query 上投影换 SM107 K64 MMA**（cuDNN SM100 → FlashInfer CuTe DSL）：4K–32K 行快 13–18%。
- **MegaAttn 喂饱 tensor core**：空闲 warp 先发 SV、KV producer 预取下一 block 的 top-k 索引、cluster-launch-control 预取下个 job、softmax 不再经 shared memory 交换部分和——16K–32K 快 15%、4K 快 23%。
- 另有两条次级优化未单列：Mega-mHC ticketed task ring（prefill，-18% @32K、13–22%/调用）与 MegaAttn decode 更深流水线（7–10% @6–424 行）。
- **MegaGate 只给"还有机会进 top-6"的专家算分**：对第六大分数设界 + sqrt-softplus 斜率给阈值，384 个专家约 7 个通过精确评估；32K 时 77→68 µs。

**DEP decode（DEP32 目标 forward -25%，对照"已做 die-local 权重"的首版 Rubin 构建）**：

- **die-local 专家权重**：按输出列跨域切分，每域 SM 只拿本地 tile——batch 32 时 decode forward -10.1%。
- **Wide-EP dispatch 每 token 一次 NVLink 往返**：DEP8 时 NVLink 只跑出峰值 39%，改为全部远程读先发、单 fence 发布、计数用不返回的 `red` 原子——MegaMoE 192→160 µs（-17%）。
- **combine 等 data 不等 barrier**：sentinel 预填 combine buffer，CTA 完成自己的 GEMM 即合并；跨 rank 尾 barrier 在一次 launch 结束发信号、下次 launch 开始等待。
- **split-K GEMM 跨 SM107 cluster**：每 rank 只有几十行时投影 GEMM CTA 太少吃不满带宽，K 拆到 cluster 上经分布式 shared memory 归约——GEMM -10–38%。
- **split Mega-mHC**：下一层只需要 Post/路由折叠/RMSNorm，mixes 移到 side stream 下一边界汇合——decode forward -2.0–4.8%。
- **MQA logits 六 token tile + K128 MMA**：DSpark 每请求 5–6 行 query 打包成单个 192 宽 tile——快 15–22%。

## 4. 低延迟专用路径：TP8 跨 tray

单用户场景（AgentX 并发 1）走从 GB300 移植、为 Rubin 重建的专用 decode 路径，**P50 1,117→1,844 tokens/s**（固定 DSpark 接受率 3.51）【vLLM 自报】。机制清单（每项都是 µs 级抠法）：

- **TP8 铺满两 tray**：每 rank 持每专家 288 列切片 + 8 个 attention 头，跨 tray all-reduce 仅 +0.3 µs——TP8 几乎免费地把每 GPU 权重读减半，一步快 35%。
- **packed FP4 权重 staging**：SM100 单字节 FP4 布局在 256KB UMMA 寻址上限下只放 7 级流水，SM107 K64 读 packed FP4 后同空间放 11 级——每步省 57 µs。
- **die-local LM head**；**all-reduce 与 mHC 单程完成**（GEMM epilogue 直写 Lamport mailbox、NVLink multicast，接收内核顺带做 mHC Post/RMSNorm/router GEMM，约 -30 µs/步）；**sparse MLA**（上一内核仍在跑时就 gather 除新 token 外的全部 KV 行，-16–21 µs）；**shared expert 并入 routed GEMM**（<16 行时省 220 µs/步——MoE 子层尾延迟的 80% 层命中）；**提前发射**（all-reduce finalizer 在自己的 grid wait 后立刻发射依赖方 -16 µs；indexer 预载 KV -24 µs；Engram all-gather 移到本层 stream 省 ~40 µs）。

## 5. 机架级内存池与 Dynamo 路由

Rubin 算得快 → 机架能撑的并发远高于 GB300 → 所有 agentic 会话的活跃 prefix 超出任何 per-rank 缓存。第二篇的答案是 per-rank CPU tier + 会话钉在 rank 上；本篇改为**把内存池化到机架级**【vLLM 自报】：

- **Mooncake KV 池**：全部 prefill/decode tray 的 DRAM 组成一个 store，任意 rank 可经 RDMA 载入任意 prefix——迁移请求的代价从"重算"变成"一次 KV 载入"。prefill 调度器异步等待池（查找出进程异步、本地 HBM 命中跳过查找但续租、KV 载入随查找返回即启动）：被查找拖空的 prefill 步从 6–14% 降到 <0.5%，被 KV 载入拖住的从 13.5% 降到 1%。
- **HBM 池（实验性）**：模型小、每 token KV 小，服务一个请求只用 prefill/decode GPU HBM 的一小部分；每 prefill rank 只留一个最大长度请求的 KV，其余 KV 预算自动作为 HBM 段捐给 Mooncake（同样 RDMA 路径读）。
- **Engram 池**：两张 94.4 GiB hashed n-gram 表移入 HBM——decode 早已按 DP rank 分片（vllm#54371），本篇让 18 个 prefill GPU 组成 peer group 各持 10.5 GiB、其余经 **NVLink**（非 RDMA）读 peers 的 HBM（vllm#66552）；查找比 host memory 更快，省出的 host 内存多放约 1,500 个会话的活跃 prefix。
- **Dynamo workload-aware routing**：prefix 全入共享池后，会话不再需要钉 rank——DP 不平衡的根源消失；Dynamo 把每个请求发给"未缓存工作量最小"的 (worker, DP rank)，纯配置变更。三个 DEP2 实例并发 4,800：请求数 +68%、TTFT P50 29.8s→4.2s、命中率 91.8%→96.1%；12×DEP2 模拟中"一 rank 排队另一 rank 空闲"的时间从 10.3%→1.3%、TTFT P90 0.98s→0.38s。

即便极高并发下 prefix 命中率保持 **96.5–97%**（接近理论命中上限）——这是整个池化方案成立的前提数字。

## 6. 关键数字与口径逐项核对

| 数字 | 原文语境 | 口径核对本报告判定 |
|---|---|---|
| 1.7M tokens/s/GPU；峰值 2.52M | AgentX 单机架 all-token 吞吐（含 cached input、uncached input、output） | 【vLLM 自报】all-token 口径与前作一致（图 1 注明 GB300 source 同口径）。未复现 |
| 387 tokens/s（P90，per user） | 每 token 交互速度 | 【vLLM 自报】前作 GB300 同指标为 196.46——交互性翻倍 |
| **58× GB300 NVL72** | 标题与 TL;DR（含 "at 387 tokens/s" 限定） | 【本报告推断】标题限定的是 Rubin 侧工作点（387 tok/s/user）、未说明 GB300 侧对比配置；与前作 954K all-token/s/GPU 直接相除仅 1.78×，故 58× 应理解为**把 GB300 压到同等交互水平低并发时**的吞吐对比（等交互性比较）。引用时写"厂商称"并注明口径 |
| 1,810 / 1,844 tokens/s 单用户 | TP8 专用路径（P90 1,810；正文并发 1 P50 1,117→1,844） | 【vLLM 自报】P90 与 P50 两个口径并存，引用需注明分位 |
| prefill -28% / decode -25% | 内核组每步时间 | 【vLLM 自报】decode -25% 基线是"首版 Rubin 构建（已含 die-local 权重）"且**在单 4-GPU 节点模拟**（原文口径），不是 GB300 实测；基线与模拟口径均已注明 |
| 96.5–97% prefix hit | 机架池化后的命中率 | 【vLLM 自报】"接近理论命中上限"；AgentX 是高复用 agentic 负载，迁移到低复用负载不可外推 |
| +68% 请求 / TTFT P50 29.8→4.2s / 0.98→0.38s | 3×DEP2 并发 4,800 / 12×DEP2 模拟 | 【vLLM 自报】后者是模拟（simulation）非实测，引用需注明 |
| DSpark 接受率 3.51 | 低延迟路径固定值 | 【vLLM 自报】固定值而非实测分布 |
| 220 µs / 57 µs / 0.3 µs 等微秒级数字 | 各内核收益 | 【vLLM 自报】`vllm bench forward` 真实路径 A/B 回放；方法学与前作一致 |

## 7. 迁移要点与本库连线

1. **内存域感知成为内核的新设计维度**。从"SM 数、HBM 带宽"到"哪个域、谁预取、发射依赖"——NUMA 的教训在 GPU 内部重演。对一般工程师的可迁移判断：在 Rubin 类双域硬件上，**数据驻留位置**比指令选择更先决定带宽bound内核的上限。
2. **机架级池化是并发上来后的第二增长曲线**。第二篇的极限在 per-rank 缓存 + 会话钉死；本篇 +68% 请求的收益主要不是算得更快，而是**内存组织方式**变了（KV 走 RDMA 池、表走 NVLink 分片、路由去亲和）。这与数据库领域 shared-nothing→shared-storage 的老剧本同构【本报告推断】。
3. **µs 级抠法的清单化**。-16/-24/-30/-40 µs 逐项列出的收益表说明：头部推理栈的优化已经进入"每步数百 µs 预算内逐项记账"的阶段，与[游凯超访谈](../../../podcast-learning/reports/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.md)中"模型×Infra×硬件 co-design"的判断完全互文——本篇由 **Inferact 主导**、NVIDIA 早期硬件合作、DeepSeek 开源模型与内核，正是该访谈所述协作结构的又一实例。
4. **对 CAPEX 大辩论的输入**：同栈一年内 GB300→Rubin 的 all-token/GPU 再乘 1.78×（同口径），是[美第奇的账本](../../../podcast-learning/wiki/concepts/ai-capex-bubble-debate.md)两侧都要认账的供给侧事实——单位算力产出仍在快速改善，但每代机架的获取成本与电力同样在上行（本篇给出 power-normalized 吞吐图但正文未引用具体瓦数）【本报告推断】。

## 8. 厂商自报边界清单

- 全部性能数字为 vLLM/Inferact 自报，未独立复现；NVIDIA 提供早期硬件访问并深度参与优化（致谢名单 7 人）——**硬件商、框架方、模型方三方利益一致**的发布结构。
- AgentX 为 SemiAnalysis 基准（第三方），但负载特性（agentic 高缓存复用）与 vLLM 优化方向高度匹配；96.5–97% 命中率前提在低复用负载不成立。
- "58×"为标题口径，直接引用需加"厂商称"与交互水平限定（§6）。
- HBM 池标注 experimental；12×DEP2 的路由收益为模拟值。
- 本报告作者未接触 Vera Rubin 硬件；对"58×"的解释为基于两篇博客公开数字的推断，若 vLLM 后续给出精确对比配置应以其为准。

---

来源：[vLLM 官方博客：DeepSeek-V4.1-Flash on Vera Rubin NVL72（2026-11-12）](https://vllm.ai/blog/2026-11-12-deepseek-v41-flash-vera-rubin)，经 eacli Token Plan（web.read）全文获取。前作：[GB300 NVL72 P/D 分离篇](https://vllm.ai/blog/2026-10-23-deepseek-v41-flash-gb300-nvl72)（本库解析 2026-10-25）。资料核验日期：2026-11-13。
