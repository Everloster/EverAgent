---
title: "MiniMax M3.1 Flash：Agent 模型与 vLLM Day-0 支持深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["MiniMax", "M3.1-Flash", "MSA", "MoE", "投机解码", "vLLM", "Agent", "推理优化"]
---

# MiniMax M3.1 Flash：Agent 模型与 vLLM Day-0 支持深度解析

**研究对象**：MiniMax 官方发布文《MiniMax M3.1 Flash: Redefining Agent Performance and Cost》（中英文双版，发布于 2026-10-19）与 vLLM 官方博客《vLLM Delivers Day-0 Support for MiniMax-M3.1-Flash》（2026-10-23），以及两文直接链接的技术材料：HuggingFace 模型卡、arXiv:2606.13392（MiniMax Sparse Attention, MSA）与 arXiv:2607.05147（DSpark）、vLLM Recipes 部署文档、vLLM 仓库 PR 与 MSA kernel 仓库。

> **标注约定**（全文通用）
> - `[原文事实]`：可在引用来源中逐字或逐表核对到的内容，括注来源与定位。
> - `[厂商主张]`：MiniMax 或 vLLM 自报、未经独立复现的数据与结论。
> - `[代码证据]`：来自代码、配置、PR、kernel 仓库的可核对事实。
> - `[独立评估]`：第三方评测机构或媒体的测评结果（其中再标注是否为二手转述）。
> - `[推测]` / `[待验证]`：本报告作者的推断或尚未解决的疑点。
>
> **本报告未运行任何模型或 benchmark**，所有性能与能力数字均为转述来源自报；`[厂商主张]` 与 `[独立评估]` 不可混为一谈。

---

## 开头三行：x → f → f(x)

- **x**：Agent 负载的形状是"读极长的仓库/日志，写相对短的动作与结论"。厂商要在同一款模型上同时压住**单位任务成本**、**长上下文并发数**和**交互式体感速度**——三者在传统 dense attention + 全精度 KV 的推理栈里互相打架。MiniMax 在 2026-10-19 把 M3.1 Flash 定义为"Agent 任务代际跃迁 + 线上推理近 3 倍提速 + Agent 任务综合使用成本降 70%"，两天后 vLLM 在 2026-10-23 宣布 Day-0 支持。三件事必须合起来看才成立。
- **f**：MiniMax 的回答分三层叠在**同一份模型**上：(1) **MSA 稀疏注意力铺满全模型**——轻量 Index Branch 仍线性扫描全上下文，为每个 query 按 GQA 组选 top-16 个 128-token 块；Main Branch 只在选中块上做**精确** softmax，使主注意力的 K/V 读取与计算从 O(N) 压到 O(k·B_k)，但整层仍保留一个系数较小的 O(N) 索引项；(2) **量化感知训练（QAT）**——NVFP4 的 KV cache（indexer 与主注意力两条路径都量化）与 NVFP4 的 routed MoE 专家权重是**训练出来的**，不是事后压的；(3) **DSpark 投机解码**——用半自回归 drafter + confidence head 做"按置信度调度验证"，替代 M3 时代的 EAGLE-like MTP。三者互相咬合：稀疏注意力降低长上下文的主 K/V 读取，NVFP4 继续压低 KV 与权重带宽，投机解码再减少 decode 所需的 target steps。
- **f(x)**：接受 f 之后，长上下文 Agent 服务有了**可核对的容量账本**：4×B300 + DEP4 + 256K 序列下，M3.1 装得下 76 条并发、M3（FP8 KV）只装得下 28 条，约 2.7×（vLLM 自报）；NVFP4 checkpoint 250.1 GB vs M3 MXFP8 451.5 GB；NVFP4 KV 34,560 B/token vs FP8 61,440 B/token。它说明 256K 场景的显存压力显著下降，**不能单凭这组数据推断 1M 场景的并发数**。所有数字都是 vLLM 在 day-0 镜像上的项目自报，AgentX 还使用"合成接受长度 3.16–3.26"，且**上游 PR 当时仍未合并**（#63232 仍带 `needs-rebase`）。能力侧同样有边界：本次纳入的 Artificial Analysis 独立评测及其转述显示，它在"答错时不拒答"方向上有明显风险信号（见 §5.4）——**这正是 Agent harness 最该盯的指标，而厂商榜单不体现它**。

---

## 一、一手来源清单与读法

| 编号 | 来源 | 类型 | 本报告用途 | 定位 |
|---|---|---|---|---|
| S01 | MiniMax《MiniMax M3.1 Flash: Redefining Agent Performance and Cost》（英文） | 官方发布文 | 厂商叙事、定价、速度与能力口径 | https://www.minimax.io/blog/minimax-m31f （2026-10-19） |
| S02 | MiniMax 同题中文版 | 官方发布文 | 核对人民币定价与中文措辞 | https://www.minimax.cn/blog/minimax-m31f （2026-10-19） |
| S03 | HuggingFace `MiniMaxAI/MiniMax-M3.1-Flash` 模型卡 | 官方模型卡 | 参数、上下文、完整 benchmark 表与评测脚手架口径 | https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash |
| S04 | vLLM《vLLM Delivers Day-0 Support for MiniMax-M3.1-Flash》 | 官方工程博客 | MSA 机制 primer、kernel 设计、AgentX 与 RL 数据 | https://vllm.ai/blog/2026-10-23-minimax-m31-flash （2026-10-23） |
| S05 | vLLM Recipes `MiniMaxAI/MiniMax-M3.1-Flash` | 官方部署文档 | 硬件矩阵、启动参数、踩坑点 | https://recipes.vllm.ai/MiniMaxAI/MiniMax-M3.1-Flash |
| S06 | arXiv:2606.13392《MiniMax Sparse Attention》v2 | 一手论文 | MSA 机制与训练目标的精确描述 | https://arxiv.org/abs/2606.13392 （v1 2026-06-11，v2 2026-06-12） |
| S07 | arXiv:2607.05147《DSpark: Confidence-Scheduled Speculative Decoding with Semi-Autoregressive Generation》 | 一手论文 | DSpark 机制与生产侧收益 | https://arxiv.org/abs/2607.05147 （2026-07-06） |
| S08 | MSA kernel 仓库（vLLM 项目镜像 / MiniMax 上游） | 代码 | kernel 家族、依赖与用法 | https://github.com/vllm-project/MSA ，上游 https://github.com/MiniMax-AI/MSA |
| S09 | vLLM PR 集合 | 代码/PR | Day-0 支持的工程落点与成熟度 | 见 §4.7 表格 |
| S10 | VentureBeat 对 M3.1 Flash 的报道（转述 Artificial Analysis） | 二手报道（引用第三方评测） | 独立评估与反例 | https://venturebeat.com/technology/minimaxs-new-m3-1-flash-beats-deepseek-and-opus-5-on-a-key-business-benchmark-at-lower-cost-but-with-a-high-hallucination-rate |
| S11 | Artificial Analysis 的 M3.1 Flash 模型页 | 独立评测机构一手页面 | 核对当前 Intelligence Index 与 AA-Omniscience 指标定义 | https://artificialanalysis.ai/models/minimax-m3-1-flash |

**读法说明**：S01/S02 是"公司说了什么"，S03 是"公司承诺了什么口径"，S04 是"工程侧把这些承诺变成了什么"，S06/S07 是"底层机制的可核对描述"，S08/S09 是"代码里真的长什么样"。S10 是本次纳入的独立测评转述，S11 用于核对评测机构当前页面与指标定义；它们同时提供了一条对厂商叙事不利的风险信号。

---

## 二、厂商叙事的重构（x → f → f(x)）

### 2.1 MiniMax 到底在回答什么问题

`[原文事实]` S01 全文的骨架很短，核心只有五句话：

1. "Space Bunny 🐰, which processed more than 200 trillion tokens while operating anonymously, was an early version of MiniMax M3.1 Flash."（S01）——一个匿名运行的内部 Agent 消耗了 200 万亿 token，它是 M3.1 Flash 的早期版本。
2. "M3.1 Flash delivers a generational leap in agentic tasks, coding, Computer Use and cybersecurity, while making online inference nearly three times faster and reducing usage costs by 70%."（S01）
3. 四类能力的具体分数：AutomationBench-AA "ranks among the top performers"（**未给数值**）、BankerToolBench 76.2、DeepSWE v1.1 73.7%、OSWorld V2 61.7、ALE 29.6、CyberGym 82%（S01）。
4. "We have further optimized M3.1 Flash's inference efficiency through more aggressive sparsity. In everyday use, output speeds can reach 200+ TPS, with median (P50) speeds consistently reaching 170+ TPS."（S01）
5. 定价：$0.15 / $0.60 / $0.015 每百万 token（输入 / 输出 / 缓存输入）；S02 的中文版给出人民币 1 元 / 4 元 / 0.1 元每百万 token。`[原文事实]` 两版一致（1 元 ≈ $0.15）。

`[评]` 这篇文章**没有出现任何一个架构名词**——没有 MSA、没有 MoE、没有 NVFP4、没有投机解码。厂商把全部技术内容折叠进了一句"more aggressive sparsity"，把全部工程内容折叠进"3 倍速度 + 70% 降本"。因此这篇文章本身**不足以支撑架构判断**；真正的技术内容在模型卡（S03）与 vLLM 的工程复现（S04）里。这是本次研究最重要的一条阅读方法论：**读厂商发布文只能拿到"意图与口径"，拿到机制必须追模型卡与代码**。

`[厂商主张]` "近 3 倍线上推理提速"和"Agent 任务综合成本降 70%"**都没有给出基线定义**：3 倍是相对 M3 的哪一项（首 token 延迟？输出 TPS？吞吐？）、什么上下文长度、什么并发？70% 是相对 M3 的什么任务组合、什么 thinking 档位、什么缓存命中率？S01 均未说明。`[待验证]`。

### 2.2 vLLM 在回答什么不同的问题

`[原文事实]` S04 开篇的技术定位句与 MiniMax 完全不同口径："It is also built for inference efficiency, with a native NVFP4 KV cache, NVFP4-quantized MoE weights, and a DSpark draft model for speculative decoding."（S04）

`[评]` 两篇文章其实在回答**两个不同问题**，这也解释了为什么它们的数字无法直接对齐：

- MiniMax 回答"**在托管 API 上，一个 Agent 任务要花多少钱、跑多快**"（端到端任务经济学）。
- vLLM 回答"**在自建集群上，这个模型能压到多少并发、每 GPU 多少 token、每美元多少 token**"（推理栈经济学）。

把两者的 TPS、tok/s、$/task 混在一张表里比较是**口径错误**——一个是托管 API 的单请求输出速度（含排队与批处理策略），一个是自建集群的 Pareto 前沿指标（每用户 / 每 GPU / 每美元三种坐标）。本报告因此把两组数字分开列（§5.2、§5.3）。

---

## 三、训练与推理设计的三层重构

### 3.1 MSA：把主注意力压成常数窗口，把索引扫描留在线性项

#### 3.1.1 机制（依据 S06 论文正文 + S04 primer）

`[原文事实]` S06 §2.2 把稀疏注意力形式化为两阶段：

```
I_i = Index_φ(q_i, K_{≤i})          # 选哪些 key
o_i = Attn(q_i, K[I_i], V[I_i])      # 在选中的 key 上算标准 softmax
```

`[原文事实]` MSA 的 Index Branch（论文 Eq. 5–7）只加了两个投影矩阵：

- 每个 GQA 组一个 index query head（`Q_idx ∈ ℝ^{N×H_kv×d_idx}`），**全模型共用一个 index key head**（`K_idx ∈ ℝ^{N×1×d_idx}`）；
- 打分后按块做 **max-pooling**：`M_idx(i,b) = max_{j∈B_b, j≤i} S_idx(i,j)`，即一个块只保留它最强的那个 token 的分数；
- 再取 **top-k 块**；**包含当前 query 所在局部块的块永远入选**（forced local block）。

`[原文事实]` Main Branch（Eq. 8）是**精确**注意力，不是近似：`O_i^(h) = softmax(Q_i^(h) K^(r)[I_i^(r)]^T / √d_h) V^(r)[I_i^(r)]`。块集合 `I_i^(r)` 在组内 G 个 query head 间共享，但每个 head 保留自己的 query 投影。

`[原文事实]` 因为选中块的 token 数上界是 `k·B_k`，Main Branch 每 query 的 K/V 读取与精确注意力计算从 O(N) 降为 O(k·B_k)。但 Index Branch 仍要给全上下文的 key 打分，因此整层并非严格的常数复杂度：它保留一个维度更小、字节数更低的 O(N) 索引扫描项。vLLM 的工程账也明确写着「每步仍扫描全上下文 index keys」，只是每 token/layer 为 128 B，而 dense K/V 为 1,024 B（S04）。

`[原文事实]` S04 的 primer 给出 M3.1 的具体取值：**块大小 128 token，每 query 选 top-16 块，最新块始终保留 → 每个 query 最多看 2,048 个 key**（S04）。

#### 3.1.2 训练目标：为什么它不能直接用 LM loss 训

`[原文事实]` S06 §3.2：top-k 选择不可导，所以 LM loss 无法直接训练 index 的 `W_q_idx / W_k_idx`。MSA 用 **KL 对齐损失**给 Index Branch 直接的学习信号（让 index 分布在选中的块上对齐"组内平均的 Main Branch 分布"），并用三个机制稳定训练：

1. **Gradient Detach**——Index Branch 的梯度与 Main Branch 解耦（论文 Figure 1 图注原文："the Index Branch gradient is detached from the Main Branch"）；
2. **Indexer Warmup**；
3. **forced Local Block**（S06 §3.2 首段与 Figure 1 图注）。

`[原文事实]` kernel 侧的配套设计（S06 §1、§3.2 末段）：为 small-k 定制的 **exp-free Top-k kernel**（利用块级 indexer 在选择前跳过不必要的 softmax 计算）、**KV-outer** 稀疏注意力排布（被选中的 KV 块反向收集其关联 query，拼满 tensor core MMA，用预调度分块 + 两阶段 combine 处理块热度极不均衡，避免 atomic）、把稀疏 KL loss 需要的 LSE 计算**融进 forward**、backward 用 persistent load balancing。

`[原文事实]` S06 摘要给出的量化结果：在**109B 参数、3T token 预算、从零训练、原生多模态**的 MoE 模型上，MSA 与 GQA 在下游 benchmark 上**持平（on par）**，同时在 1M 上下文把每 token 注意力计算量降低 **28.4×**，配合其 kernel 在 **H800** 上取得 **prefill 14.2× / decode 7.6×** 的 wall-clock 加速。

`[推测]` 这是本报告认为最被低估的一点：**MSA 的卖点不是"稀疏所以便宜"，而是"稀疏所以便宜，且质量不掉"**——后者由"精确注意力 + KL 对齐训练"这两个设计共同保证。绝大多数只强调 top-k 稀疏的方案，其质量折损才是拦路虎。MiniMax 的答案是把稀疏选择做成一个**可训练的近似**，并用 Main Branch 的分布给它打靶。

#### 3.1.3 机制示意

```
                    ┌──────────── 每个 query token i，每个 GQA 组 r ────────────┐
                    │                                                          │
  X (hidden)        │                                                          │
    │               │                                                          │
    ├── W_q_idx ──► Q_idx: N×H_kv×d_idx   (每组一个 index query head)        │
    └── W_k_idx ──► K_idx: N×1×d_idx      (全局共用一个 index key head)       │
                                    │                                          │
                    S_idx(i,j) = <Q_idx(i,r), K_idx(j)> / √d_idx             │
                                    │                                          │
                    ┌───────────────┴───────────────┐                          │
                    │  max-pool 到块级（块=128 tok） │                          │
                    │  M_idx(i,b) = max_{j∈B_b} S   │                          │
                    └───────────────┬───────────────┘                          │
                                    │                                          │
                    Top-k (k=16)  +  forced local block（最近块恒入选）        │
                                    │                                          │
                    I_i^(r) = {16 个块}  ← 同一 GQA 组内 G 个 query head 共享    │
                                    │                                          │
                    ┌───────────────┴───────────────┐                          │
                    │  Main Branch：精确 softmax 注意力                          │
                    │  只在选中块的 ≤2048 个 key 上计算                            │
                    │  O_i^(h) = softmax(Q K[r][I]^T/√d_h) V[r][I]                │
                    └───────────────┬───────────────┘                          │
                                    ▼                                          │
                            层输出（Main Branch: O(N) → O(k·B_k)）              │
                            Index Branch 仍扫描 N 个轻量 index keys             │
                    └──────────────────────────────────────────────────────────┘

训练回路（S06 §3.2）：
  LM loss ──► Main Branch（参数正常更新）
  KL 对齐 loss ──► Index Branch（梯度 detach，不回传到 Main Branch）
  稳定器：Indexer Warmup + forced Local Block
```

#### 3.1.4 稀疏注意力到底省了多少带宽

`[厂商主张]` S04 给了一个很干净的账（MiniMax 官方博客没有这个层面的数字）：

- decode 每步仍要扫全上下文的 **index key**：**128 B/token/layer**；
- 对比 dense attention 要读的 K/V：**1,024 B**（FP8，4 个 KV head × 128 维）；
- 选中块的完整 K/V 只读那 2,048 个 token；
- **长上下文 decode 的每步 HBM 流量降到 dense 的约 12.5%**（S04）。

`[评]` 注意这个 12.5% 是**decode 侧**的数字，且它成立的前提是"indexer 也要被扫全"。`[待验证]` S04 在给出 128 B/token/layer 这个数时**没有写明它对应的量化格式**，而 S04 的 Figure 2 图注又说明 M3.1 的 indexer cache 本身是 NVFP4——因此"128 B"究竟对应 FP8 的 128 维 index key，还是 NVFP4 下更宽的 index 维度，原文未交代，12.5% 这一比例随 index head 维度与 KV head 数变化的幅度也未给出。`[评]` 可以确定的是 S06 Eq. 5 中"**全局共用一个 index key head**"的设计正是这个数字成立的经济学理由：**indexer 的带宽成本与 GQA 组数无关，只与 token 数线性相关**，这与"每组一个 index query head"形成对照——如果 index key 也按组复制，indexer 的读取量会随组数线性膨胀。

### 3.2 量化感知训练（QAT）：让 NVFP4 成为"原生格式"而非"事后压缩"

`[原文事实]` S03《What's New in M3.1-Flash》列出三条变化，第二条即："**Quantization-aware training:** the routed MoE experts and the attention paths are quantized during training, reducing memory footprint and improving serving efficiency."（S03）

`[原文事实]` S04 进一步给出 QAT 的**两个具体产物与两个可核对数字**：

| 对象 | 数字 | 口径 |
|---|---|---|
| checkpoint 体积 | M3 MXFP8 **451.5 GB** → M3.1 NVFP4 **250.1 GB** | 专家权重 NVFP4、其余 dense 层 MXFP8；**小 44.6%**（S04） |
| KV cache | FP8 **61,440 B/token** → NVFP4 **34,560 B/token** | **每 token 省 43.75%**（S04） |
| 并发能力 | 4×B300、DEP4、256K 序列：M3.1 **76** 条并发 vs M3（FP8 KV）**28** 条 | 同硬件约 **2.7×**（S04） |

`[评]` 这三个数字必须连着读：250.1 GB 是**整个 checkpoint 的落盘体积**，显著低于 4×B300 的总 HBM，但它本身不能说明运行时如何放置权重、工作区与 KV；真正直接证明容量收益的是同硬件、同 256K 序列下的 76 vs 28 并发。**QAT 是这里的关键**：`[推测]` NVFP4 若只做事后量化，indexer 与 Main Branch 两条路径的量化误差可能改变块排序，稀疏选择会比普通权重量化更敏感。M3.1 把"前三层原本是 full attention 的层也换成稀疏"（S03 原文）是否为了统一全模型 KV 格式，官方没有解释；这只能保留为待验证的工程动机，不能当成设计事实。

### 3.3 DSpark：把投机解码从"固定长度"改成"按置信度调度"

`[原文事实]` S03："**DSpark speculative decoding:** DSpark replaces the earlier EAGLE-like MTP approach. The release includes the draft head for use with compatible serving implementations."（S03）

`[原文事实]` S05（Recipes）：checkpoint 内置 **`dspark/` 目录的 draft head**，`--speculative-config` **不需要额外的 draft model 路径**（S05）——即"draft 模型随主模型一起发布"，这是把投机解码变成产品默认项而不是用户自选项的关键工程动作。

`[原文事实]` S07（DSpark 论文摘要）给出的机制三点：

1. **半自回归 drafter**：并行 backbone + 轻量顺序模块，补回块内 token 间依赖，缓解"接受长度快速衰减"；
2. **confidence head**：估计每个 draft token 在"此前 token 全部通过验证"条件下的存活概率；
3. **confidence-scheduled verification**：按估计的前缀存活概率 + 引擎吞吐画像，**为每个请求动态决定验证长度**——避免在高并发下把宝贵的 batch 容量浪费在高拒绝风险的 token 上。

`[原文事实]` S07 报告的生产侧收益：在 **DeepSeek-V4** 的线上服务中，相比既有生产基线 **MTP-1**，在同等吞吐下**每用户生成速度提升 60–85%**，并因避免严格交互性约束下的吞吐崩塌而"移了 Pareto 前沿"。

`[代码证据]` vLLM 侧的配置印证了这套语义：S04/S05 的启动参数包含 `"draft_sample_method":"probabilistic"`、`"num_speculative_tokens":7`（NVIDIA/FlashInfer 路线）或 `3`（AMD/Triton 路线）、`"rejection_sample_method":"block"`（NVIDIA 路线）。

`[原文事实]` S07 的 arXiv HTML 明确列出作者机构为 **Peking University 与 DeepSeek-AI**，通讯邮箱为 `@deepseek.com`，并公开 DeepSeek-V4 的 DSpark checkpoint 与 DeepSpec 仓库。因此 DSpark 是 DeepSeek 主导的工作，MiniMax M3.1 是**采用方**；"M3.1 用 DSpark"属于跨厂商复用，而不是 MiniMax 自研算法。

`[评]` 对 Agent harness 而言，DSpark 的意义不在"更快"，而在**接受长度（acceptance length）是动态的**：vLLM 的 AgentX 数据用的是"合成接受长度 3.16–3.26"（S04），说明在给定并发与请求分布下，真实接受长度需要实测标定，而**接受长度直接决定单位任务的 token 成本**。任何按"标称 TPS"做的成本预算，对投机解码模型都是不可靠的。

### 3.4 多硬件支持：同一份权重，三条不同的"降级路径"

`[代码证据]` S05 给出的硬件矩阵（本报告认为这是两篇文章之外最有实用价值的材料）：

| 硬件 | TP | KV / indexer cache | MoE 权重 | DSpark | 备注 |
|---|---|---|---|---|---|
| NVIDIA Blackwell（GB200/GB300/B200/B300） | 4 | NVFP4 | NVFP4 原生 | ✅ 7 tok，`FLASHINFER_TS` | NVFP4 走原生 FP4 tensor core；`use_prefill_query_quantization`（Q8KV4）可选 |
| NVIDIA Hopper（H100/H200） | 8（整机） | **FP8** | NVFP4 走 **Marlin** kernel | ❌ 不启用 | Hopper 无 FP4 tensor core；`--limit-mm-per-prompt '{"video": 0}'` 关闭视频 |
| AMD MI355X（gfx950，ROCm 7.2+） | 4 | NVFP4 | 加载时重量化为 **MXFP8** | ✅ 3 tok，`TRITON_ATTN` | AITER MoE；`indexer_decode_cp: true` |

`[原文事实]` 两条硬性约束值得单独记住：S05 明确 "**`--block-size 128` is mandatory**"（MSA 的稀疏块大小是 128，vLLM 的 KV cache block size 必须匹配，否则报错 `No common block size for 16`）；以及推理与工具解析都用同一个 parser 名 `minimax_m3`（`--reasoning-parser minimax_m3`、`--tool-call-parser minimax_m3`）。

`[评]` 这张表本身就是一个重要结论：**"Day-0 支持"在这类超大 MoE 上从来不是"一个模型跑遍所有硬件"，而是"一份权重 + 每种硬件一条降级路径"**。Hopper 路径同时降了两件事（KV 从 NVFP4 降到 FP8、关掉投机解码），AMD 路径降的是 MoE 权重精度并用查找表模拟 NVFP4 反量化。这意味着**同一模型在不同硬件上的单位 token 成本与速度不可比**，跨硬件比较时必须带上这张表。

---

## 四、vLLM Day-0 支持的工程重构

### 4.1 MSA kernel 家族（Blackwell）

`[原文事实]` S04：NVFP4 的 KV 存在、query 留在 FP8，因此**不能直接用 NVFP4 tensor core 指令做矩阵乘**，kernel 必须在内部把 NVFP4 反量化为 FP8 再跑 FP8 MMA。为压低反量化成本，vLLM 使用 CUDA 13.4 新增的 Blackwell 专用 PTX 指令 `mul.e4m3x4.e2m1x4.e4m3x4`（SASS `QMUL4`）——**一条指令把 4 个 NVFP4 值按其 scale 缩放并产出 4 个 FP8 值**，比原先走 FP16 往返的路径省下大量 CUDA core 指令。结果：**indexer QK decode kernel 最高 1.7×、稀疏注意力 decode kernel 1.3×**（S04）。

`[代码证据]` S08（MSA kernel 仓库）显示这是一套**独立开源的 kernel 家族**，MIT 许可，两套 JIT 栈共用一个 Python 包：`csrc JIT`（Jinja 模板运行时编译，产出 dense FMHA `fmha_sm100` / `fmha_sm100_plan` 与 `sparse_topk_select` indexer）与 `CuTe-DSL`（运行时 `cute.compile`，提供完整稀疏注意力 forward + paged FP8 decode，支持 BF16 / FP8 / NVFP4 / FP4）。仓库 README 的最小可用示例里 `page_size, topk = 128, 16`——**与 S04 描述的块大小与 top-k 完全对上**。目标硬件标注为 **NVIDIA SM100**（Blackwell），S08 同时声明 SGLang 与 vLLM 均可使用。

### 4.2 NVFP4 MegaMoE：_dtype 换了，流水线必须重排

`[原文事实]` S04：vLLM 把 DeepGEMM 的 **MegaMoE** 扩展到 NVFP4 精度，并融合 MXFP8 shared experts，代码开在 fork `vllm-project/DeepGEMM`。"Adding NVFP4 support to MegaMoE is more than a dtype swap."——因为 NVFP4 每元素字节数减半、tensor core 吞吐翻倍，**kernel 其余部分不改就会让流水线失衡**。

`[原文事实]` 具体的重排点：**在 FC1 epilogue 提前释放 TMEM stage**。原先 TMEM stage 要等 epilogue 结束才释放，但 epilogue 全程在寄存器里跑，所以**累加器一装载进寄存器就可以释放 TMEM**，不必等任何算术完成。总效果：**prefill kernel latency −20%，整体 prefill 吞吐 +7%**（S04）。

`[评]` 这一条是整篇 vLLM 博客里工程含量最高的一句：**它揭示了量化不是"换个 dtype"，而是"重新安排流水线的资源生命周期"**。任何自己实现 NVFP4 MoE 的团队都会踩到同一类问题——把 TMEM 占着不放，表面上"精度更高"，实际上让 tensor core 空转。

### 4.3 Indexer DCP：把"每个 GPU 扫全上下文"改成分片 + 归并

`[原文事实]` 问题（S04）：低延迟服务里，**每个 GPU 只算自己那个 index head，但要对全上下文打分**。TP4 下 4 张 GPU 各自把整个 index cache 读 4 遍。

`[原文事实]` 解法：Indexer decode context parallelism（DCP）**按上下文切分而非按 head 切分**——每张 GPU 对**全部 4 个 head** 打分，但只负责**四分之一的 page**；然后通过 NVLink 把本地每个 head 的 top-16 候选发给"拥有该 head 的 GPU"，后者合并出最终 top-16。**选择结果保持精确（exact）**，indexer 在 4×GB300、512K 上下文下**每个稀疏层最高快 3.3×**（S04）。

`[原文事实]` AMD 侧同机制（CDNA4）还额外解决了矩阵核闲置问题：一个 DSpark-3 decode step 每请求只有 4 行 query，只填满 16×16×128 FP8 MFMA 的 16 列中的 4 列；**DCP 下每 GPU 算 4 个 head × 4 行 = 16 列全满**。实现上用单个 kernel 通过 Infinity Fabric 交换 index query 并把各 head 分数直接写进属主 GPU 的显存，**device-side handshake 保证它在 HIP graph 内也能工作**；因为分数与单 GPU 版本**逐位相同**，选择仍然精确。4×MI355X 上，45 个 30K–210K token 的请求中，indexer 每个稀疏层最高快 **2.8×**（S04）。

`[评]` DCP 是本报告认为**最容易被误解为"作弊"但其实完全正当**的一项优化：它不改变选择的语义（逐位相同的分数、精确的 top-16），只是把"读 4 遍"变成"读 1 遍 + 交换 16 个候选"。**它的前提是 NVLink / Infinity Fabric 的带宽远高于 index cache 的重复读取**——在 PCIe 拓扑或更弱的互联上，这个前提可能不成立。`[推测]` 该结论未被 S04 覆盖。

### 4.4 QKV GEMM + norm + RoPE + KV insert 融合

`[原文事实]` S04：M3.1 的 QKV 与 indexer 投影原本要把**完整 QKV 张量写进 HBM**，再由第二个 kernel 读回来做 norm、RoPE 和 KV cache 插入。vLLM 把它**融进单个 GEMM kernel**，epilogue 逐 head 处理 FP32 累加器：对 query 与 index query 做 norm 与 RoPE，**把 K、V 和 index key 量化成 NVFP4 并直接写入各自的 cache**——**QKV 张量从不落到 HBM**。效果（GB300）：**prefill batch ≥ 512 token 快 1.1–1.6×，TP4 下 P50 TTFT 降低约 19%**（S04）。

`[代码证据]` 同一融合在 vLLM 仓库里落成一个独立的 CUDA 文件：`csrc/fused_minimax_m3_qknorm_rope_kv_insert_kernel.cu`（PR #63232 的变更文件列表，见 §4.7）。

### 4.5 FlashInfer PrimiTS：给 drafter 换后端

`[原文事实]` S04：M3.1 的 DSpark drafter 跑**非因果 GQA + 4096 token 滑动窗口**；vLLM 原先用 FlashAttention 4 跑它，而 FA4 并未针对 decode 形状优化。换成 **FlashInfer 的 PrimiTS 后端**后：**比 FlashAttention 4 快 1.3–2×，总 forward 时间降低 5%**（S04）。

`[评]` "5%" 这个数字很小，但它的意义不在幅度：**它揭示了 drafter 本身也是 decode 形状的 workload**，在 Agent 场景里 drafter 跑得与 target 同频，所以 drafter 的 kernel 效率直接进端到端延迟。S04 提到 PrimiTS 是"FlashInfer PrimiTS"，而 S05 的 NVIDIA 路线配置里用的是 `"attention_backend":"FLASHINFER_TS"`——两处命名一致。

### 4.6 Rubin（SM107）与 AMD：两条为"缺指令"而生的路径

`[原文事实]` Rubin 路线（S04）：因为 NVFP4→FP8 转换有开销，**Rubin 上改为直接转成 FP16 并用 FP16 跑 indexer 的 score MMA**——反量化指令减少约 1/3，且**分数变成精确值，不再带 E4M3 的二次舍入**。当 query ≤ 4 条时，单 head 的 indexer decode kernel 用 SM107 的 packed `fma.rn.f32x2.f16x2` **每个 MMA 结果施加一次块 scale**（而不是每个 K 值一次），并借此做到**每 SM 3 个 CTA**。Rubin 的 shared memory 328 KB（Blackwell 228 KB）、TMEM 列数 576（Blackwell 512）支撑了这一布局；且因为 Rubin 的 SM 更多（**212 个**），work planner 按 SM 数切 tile。prefill 稀疏注意力另用 **CUDA virtual memory API 做 locality domain 优化**：2 MB page 在两个 domain 之间交替分配，融合 kernel 把每个 tile 交给持有该 tile 数据的 SM 所在 domain 的 CTA；Rubin 上 prefill & decode 注意力 kernel 使用 **K=64 的 dense FP8 MMA**，MMA 指令数减半、跑出 Blackwell 两倍的 FP8 速率（S04）。

`[原文事实]` AMD 路线（S04）：CDNA4 **没有原生 NVFP4 反量化指令**，vLLM 把反量化变成**查表**——256 种可能的 E4M3 scale × 8 种 E2M1 幅值，全部预先算好并**以已舍入到 FP8 的形式存进 LDS 的 2 KB 表**，一次 `v_perm_b32` 字节置换 + 一次符号位 XOR 就把 4 个 FP4 转成 FP8；且**共享前缀页只反量化一次，最多服务 64 个共享该页的请求**。结果：**稀疏 decode 注意力最高比"把选中块转成 FP8 再跑 FP8 注意力 kernel"快 2.5×**（S04）。

`[原文事实]` AMD 的 prefill 侧用 **SP（sequence parallel）+ DBO（dual-batch overlap）**：DBO 把张量并行 collective 藏在另一个 microbatch 的计算后面；SP 让每 GPU 只保留四分之一 token，注意力输出以 MXFP8 做 all-to-all 交换使每 GPU 都能对自己那部分 token 跑完整 `o_proj`，MoE 输出做 reduce-scatter。效果：**每 GPU 通信量从约 36 KB 降到 20 KB / token / layer**，norm、量化与 router 只在四分之一 token 上跑。配合 KV 布局改动（从"每层切成 125 个小 page、每 page 一次 NIXL RDMA 读"改成**每个 block 存成一条连续 1.82 MB 的行**，一次读走）：**4×MI355X 上 16K+ token 的 prefill batch 快 1.8–2.1×**（S04）。

`[原文事实]` AMD 的低延迟杀手锏是 **mono kernel**：低并发时 decode 是 launch-bound 的——kernel launch 开销比数学计算还贵。Mono decode 把**每个稀疏 MoE decoder 层压成单次 FlyDSL kernel launch**，覆盖从 QKV 投影、稀疏注意力到张量并行 all-reduce 与 MXFP4 MoE 的全过程，**替换掉约 1,170 次 kernel launch**。MI350X TP4 上 decode step **最高快 2.3×**，低并发下 8K-in/1K-out 吞吐翻倍；在 **agentic coding 轨迹上交互性提升 50–65%**（S04）。

`[评]` "1,170 → 1" 是整篇博客里最戏剧性的一个数字，而它揭示的问题与模型无关：**在低并发、单请求的 Agent 场景（正是绝大多数企业 PoC 的形态）里，GPU 的 launch 开销而不是算力是瓶颈**。绝大多数团队以为"小 batch 下大模型推理慢"是显存带宽问题，其实是 CPU 侧调度问题。这也解释了为什么 §4.6 的 mono kernel 收益（交互性 +50–65%）远大于其理论吞吐收益。

### 4.7 Day-0 支持的成熟度：镜像已发，上游未合

`[代码证据]` S04 明确："the model will only be available in the nightly PyPI wheel after the code is reviewed and merged upstream, which usually takes about a week." 提供的入口是**预构建镜像** `vllm/vllm-openai:minimax-m31-flash` 与 `vllm/vllm-openai-rocm:minimax-m31-flash`（S04）。

`[代码证据]` vLLM 仓库 PR（截至 2026-10-25 抓取，GitHub API）：

| PR | 标题 | 状态 | 创建 / 合并时间 |
|---|---|---|---|
| #63232 | `[New Model] Support Minimax-M3.1-Flash` | **open**（带 `needs-rebase`、`performance`、`rocm`、`speculative-decoding`、`multi-modality` 标签） | 创建 2026-10-23T00:37:40Z |
| #63428 | `[Doc][Recipe] MiniMax-M3.1-Flash: DEP2 + DEP4 PD on GB200/GB300, 7-token FLASHINFER_TS DSpark on NVIDIA` | closed / **merged** | 合并 2026-10-24T03:43:49Z |
| #63257 | `[ROCm][Recipe] MiniMax-M3.1-Flash: MI355X PD, DBO / SP prefill, Quark MXFP4, mono decode` | closed / **merged** | 合并 2026-10-23T06:31:12Z |
| #63244 | `[Doc][Recipe] MiniMax-M3.1-Flash: add Hopper FP8 variant, Docker-only install` | closed / **merged** | 合并 2026-10-23T02:06:57Z |
| #63236 | `[Doc][Recipe] Add MiniMax-M3.1-Flash recipe` | closed / **merged** | 合并 2026-10-23T01:29:22Z |
| #63380 | `[CI] Label MiniMax M3 and M3.1 PRs and issues` | open | 创建 2026-10-23T17:37:15Z |
| #63490 | `[ROCm][MiniMax-M3.1] Move DBO under pure TP and SP prefill to their own PRs` | open | 创建 2026-10-23T15:53:39Z |
| #63491 | `[ROCm][MiniMax-M3.1] Sequence-parallel pure TP (split PR of M3.1)` | open，+64 / −106，14 个文件 | 创建 2026-10-24T15:53:53Z |

`[代码证据]` #63232 的变更文件包含 `cmake/external_projects/fmha_sm100.cmake`、`csrc/fused_minimax_m3_qknorm_rope_kv_insert_kernel.cu`、`benchmarks/kernels/benchmark_mxfp8_tp4.py`、`.buildkite/test_areas/spec_decode.yaml`、`.buildkite/test_areas/kernels.yaml`。

`[评]` 这张表给出了**一个必须写进选型报告的事实：截至 2026-10-25，"Day-0 支持"= 预构建镜像 + 预构建 kernel 已就绪，但核心模型 PR #63232 仍未合并且带 `needs-rebase` 标签**。文档与 Recipe 类 PR 已经合并，模型实现本身还在流动中。对 harness 团队而言，这意味着**现在绑定该模型 = 绑定 nightly 镜像**，升级路径与回滚路径都要自己设计。

### 4.8 Day-0 RL：训练侧与推理侧的"精度必须对齐"

`[原文事实]` S04：RL 从 **NVFP4 checkpoint** 出发，**只训练 rank-32 的 LoRA adapter**；veRL trainer 按引擎服务的方式量化基座（routed experts 用 NVFP4、其余投影用 MXFP8），**每步只把 adapter 同步给引擎**；引擎侧 expert LoRA 跑在 FlashInfer 的 TRTLLM NVFP4 MoE kernel 内，基座专家仍走常规服务 kernel。

`[原文事实]` 训练前的**一致性三查**：引擎收到的权重与 trainer 发送的完全一致；两者把每个 token 路由到**相同的专家**（routing replay）；两者对同一 token 给出接近的 logprob。

`[原文事实]` 剩余偏差用 **token-level importance sampling（TIS）** 修正，**importance ratio 上限截断为 2**；由于每个 batch 只做一次 optimizer step，trainer 直接用 rollout logprob 作为 old logprob，跳过重算所需的额外 forward。

`[原文事实]` 实验结果：**DAPO-Math-17K、16×GB300、200 步 GRPO**，AIME-2024 准确率 **36.3% → 67.5%**；训练 reward **−0.06 → 0.67**；train/rollout KL 从 **0.040 降到 0.024**（S04）。

`[评]` 这段最值得学的不是 AIME 的绝对数字，而是**"QAT 模型也能做 RL"这件事的工程前提**：一旦基座是 NVFP4，trainer 与 engine 之间的任何精度/路由差异都会变成 RL 的系统性偏差，所以必须先做**三查 + TIS 兜底**才敢开跑。`[推测]` 对想自己微调的团队，"用官方 NVFP4 checkpoint 而不是自己重量化"几乎肯定是更优路径——MiniMax 已经把路由专家的量化形态训练进了权重里。

---

## 五、关键数字与逐项口径核对

### 5.1 能力与 Agent 任务（厂商自报，S03 模型卡；括号内为评测脚手架口径）

| Benchmark | M3.1 Flash | DeepSeek V4.1 Flash-1017 | DeepSeek V4.1 Flash | Kimi K3 | GLM-5.3 | GPT-5.6 Sol | Opus 5 | 口径（S03 Evaluation Notes） |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Automation-Bench v1.0.6 | **62.8** | 60.5 | 54.8 | 46.7 | 48.8 | 45.8 | 50.3 | 600 个公开发布任务 |
| BankerToolBench | **76.2** | — | 73.7 | 69.1 | 74.5 | 74.6 | **76.2** | OpenCode 1.17.18；judge 用 MiniMax-M2.7 |
| GDP.pdf AA | 20.8 | — | 12.8 | 22.0 | 11.2 | **27.2** | 21.6 | 直接取自 Artificial Analysis |
| Terminal Bench 4.0 | 38.1 | 42.3 | 31.2 | 12.6 | 37.9 | 39.9 | **51.8** | Codex 0.149.1 |
| LOCA-Bench 256K | **60.3** | — | — | 49.7 | 50.3 | 60.0 | 53.7 | 官方实现，256K |
| Agents' Last Exam | 29.6 | — | — | 28.3 | — | 30.6 | **32.2** | 官方 Overall 设置；只取官方 leaderboard 全量结果；空白 = 官方无结果（CLI-only 不计），**不等于 0** |
| OSWorld 2.0 | 61.7 | — | 54.3 | 58.3 | — | 65.7 | **70.6** | 0808 全量发布；各模型取发布时最高报告值，DeepSeek V4.1 为**内部复现** |
| PostTrain Bench v1.1 | 39.3 | — | 30.5 | 36.6 | 37.5 | 36.2 | **40.4** | Claude Code 2.1.251，512K 上下文 |
| DeepSWE v1.1 | 73.7 | **77.0** | 74.2 | 67.5 | 66.9 | 73.0 | 74.0 | mini-SWE-agent 2.4.5，512K 上下文 |
| NL2Repo-Bench | 61.2 | 68.2 | 65.4 | 58.0 | 58.0 | 56.8 | **75.3** | Claude Code 2.1.233，512K；reward hacking = 0；两个不一致任务已修正（分数用修正集） |
| SWE Refactor Bench | 23.0 | — | 11.8 | 19.5 | 10.4 | 28.5 | **31.0** | Claude Code 2.1.220，200K 上下文 |
| CyberGym | 82.2 | — | — | 80.0 | **84.5** | 83.6 | — | Claude Code 2.1.263，1M 上下文 |
| BabyVision（带工具） | 91.0 | 92.5 | 89.6 | 85.7 | — | 88.9 | **94.1** | Claude Code 2.1.285；图像最短边 1,500 px |
| HLE（不带工具） | 43.4 | 42.6 | 39.2 | 43.5 | 42.3 | 49.5 | **55.6** | **纯文本子集，2,158 题** |
| CharXiv RQ | 82.5 | — | 69.0 | 84.8 | — | **85.2** | 83.7 | GPT-5.5 作 judge |

`[原文事实]` S03 末尾还写了一句容易被忽略但很关键的话："**Results are for the official weights; third-party quantizations may differ.**"（S03）——**即所有 benchmark 数字对应官方权重，第三方量化版本的结果会不同**。

`[评]` 这张表的读法有三条纪律：

1. **空白 ≠ 0**（ALE、OSWorld、PostTrain、BabyVision 的 GLM-5.3 列），厂商自己标注了这一点；任何"全面领先"的结论都建立在选择性读取之上。
2. **同列不同模型可能用了不同复现条件**：OSWorld 一列里 DeepSeek V4.1 明确是"内部复现"，其余是"发布时最高报告值"——**这不是同口径横比**。
3. **judge 模型会污染分数**：BankerToolBench 用 MiniMax-M2.7 当 judge、CharXiv 用 GPT-5.5 当 judge。`[推测]` 自家模型被自家模型评判，是一个需要额外证据才能排除的循环风险；S03 未披露 judge 的一致性或人工校验比例。

### 5.2 推理效率（托管 API 口径，厂商自报）

| 指标 | 数值 | 口径 | 来源 |
|---|---:|---|---|
| 输出速度（日常使用） | 200+ TPS | 未定义上下文长度、并发、thinking 档位 | S01 |
| 输出速度 P50 | 170+ TPS | 同上 | S01 |
| 线上推理速度提升 | 近 3× | **基线未定义**（相对 M3 的哪一项？） | S01 |
| Agent 任务综合成本 | −70% | **相对 M3，任务组合未定义** | S01/S02 |
| 定价（输入/输出/缓存输入） | $0.15 / $0.60 / $0.015 每 1M token | 人民币 1 / 4 / 0.1 元 | S01/S02 |

### 5.3 推理效率（自建集群口径，vLLM 自报）

| 平台 | 指标 | 数值 | 口径 |
|---|---|---:|---|
| 4×B300（DEP4） | 每 token KV 占用 | 34,560 B（NVFP4） vs 61,440 B（FP8） | −43.75% |
| 4×B300（DEP4, 256K 序列） | 可并发序列 | 76 vs 28（M3，FP8 KV） | ≈2.7× |
| 4×GB300 | indexer DCP | ≤3.3×（512K 上下文，每稀疏层） | 4×GB300 |
| 4×GB300 | QKV 融合 | prefill ≥512 token 快 1.1–1.6×；P50 TTFT −19%（TP4） | GB300 |
| 4×GB300 | AgentX 延迟端 | 418.9 tok/s per user | 7 spec tokens，**合成接受长度 3.16–3.26** |
| 4×GB300 | AgentX 中段 | 每用户 >200 tok/s，同时 38.6K tok/s per GPU | 同上 |
| 4×GB300 | AgentX 吞吐端 | 153.8K tok/s per GPU（≈24× 最交互点），每用户 ≈127 tok/s | 同上 |
| Rubin | AgentX 延迟端 | 724.9 tok/s per user | 同上 |
| Rubin | AgentX 吞吐端 | 191.5K tok/s per GPU，每用户 ≈134 tok/s（≈1.5× GB300） | 同上 |
| 4×MI355X | indexer DCP | ≤2.8×（45 请求，30K–210K token，每稀疏层） | CDNA4 |
| 4×MI355X | SP + DBO + KV 单读 | prefill 16K+ token 快 1.8–2.1× | MI355X |
| MI350X TP4 | mono kernel | decode step ≤2.3×；低并发 8K-in/1K-out 吞吐翻倍；**agentic coding 轨迹交互性 +50–65%** | MI350X |
| MI355X | AgentX | 331.0 tok/s per user（延迟端）；34.6M tok/$（中段，每用户 >170 tok/s）；133.3M tok/$（成本端，每用户 ≈79 tok/s） | InferenceX AgentX；c1/c4 用 7 spec + 3.2 接受长度，其余 3 spec + 2.45 |
| 16×GB300 | RL | AIME-2024 36.3% → 67.5%（200 步 GRPO，DAPO-Math-17K） | veRL + FSDP2 + rank-32 LoRA |

### 5.4 独立评估与反例（S10 转述 + S11 原始指标页）

`[独立评估]` VentureBeat 引述 Artificial Analysis 对 M3.1 Flash 发布时的评测；独立复核又读取了 AA 当前模型页，确认 Intelligence Index 已显示为 43，说明榜单会随版本或重跑变化。下表的发布时数值仍按 S10 转述列出：

| 项 | M3.1 Flash | 对照 | 备注 |
|---|---:|---|---|
| Intelligence Index（最大 reasoning effort） | **42** | M3 = 29 | 比前代 +13 分 |
| Intelligence Index 每任务成本 | **≈$0.22** | M3 ≈$0.51 | −57% |
| 同档竞品 | GLM-5.3 Flash 42 @ $0.28；DeepSeek V4.1 Flash-1017 45 @ $0.26；Gemini 3.8 Flash 41 @ $1.24 | | |
| Humanity's Last Exam | 48% | M3 39%；GLM-5.3 Flash 40%；DeepSeek V4.1 Flash-1017 43% | 与 S03 的 43.4 **口径不同** |
| CritPt（物理推理） | 22% | M3 4%；GLM-5.3 Flash 15%；Gemini 3.8 Flash 18%；DeepSeek 24% | |
| Intelligence Index 输出 token 消耗 | ≈189M | GLM-5.3 Flash ≈324M；Gemini 3.8 Flash ≈334M | 少输出 token 本身就是成本优势来源 |
| AA-Omniscience 答对率 | 56% | DeepSeek V4.1 Flash-1017 43%；GLM-5.3 28% | |
| AA-Omniscience **幻觉率** | **93%** | — | 定义：在**非正确**回答中，"错答"相对于"部分回答/拒答"的比例；**不是**"93% 的答案是错的" |
| AA-Omniscience 总分 | 16 | — | |

`[评]` 这条"幻觉率"是本报告认为**对 Agent 选型最关键、却完全不在厂商榜单上的事实**。厂商的七个 benchmark 全是"任务完成度"，而 Agent harness 的真实失败模式是**"自信地做错"**：当模型答错时，它选择编一个答案而不是说"不知道"。在一个允许写文件、调用工具、改数据库的 Agent 里，这种行为模式的代价远高于普通问答——它把一次错误变成一次不可逆的副作用。S03 明确标注 ALE "Blank = no official result (CLI-only excluded), **not zero**"，可见厂商对数字的诚实度并不低；**但厂商没有发布任何"知道自己不知道"维度的指标**。

### 5.5 厂商自身数字之间的不一致（未解决）

| 数字 | 出现处 A | 出现处 B | 状态 |
|---|---|---|---|
| Automation-Bench v1.0.6 | 模型卡 **62.8**（S03） | VentureBeat 转述 MiniMax **62.2**（S10） | `[待验证]` 同一厂商同一 benchmark 出现两个值，差异 0.6；可能是不同版本、不同跑次或转述误差。本报告以模型卡 62.8 为准并保留此疑点。 |
| Intelligence Index | VentureBeat **42**（S10，注明 max reasoning effort） | Artificial Analysis 模型页搜索摘要显示 **43**（S10 同源机构） | `[待验证]` 可能是索引版本不同（搜索结果提到 v4.3.2）或重跑所致。 |
| HLE | 模型卡 **43.4**（无工具、纯文本 2,158 题） | Artificial Analysis **48%** | `[评]` 口径不同（是否带工具、题目子集），**不是矛盾**；但两者被并列引用时会造成误导。 |
| CyberGym | 博客 **82%**（S01/S02） | 模型卡 **82.2**（S03） | `[评]` 取整，非矛盾。 |
| "近 3 倍推理提速" | 博客（S01） | 无第三方复现 | `[待验证]` 基线未定义。 |
| "成本降 70%" | 博客（S01/S02） | AA 实测每任务成本 −57%（S10） | `[评]` 口径不同：厂商说的是"Agentic 任务综合使用成本"，AA 说的是"Intelligence Index 单任务成本"。两个数字都不能直接互证。 |

`[评]` 这一节的结论不是"厂商在造假"，而是**"厂商发布文、模型卡、第三方评测构成三个不同的口径体系"**。任何把三者放在一张图里比较"谁更强"的结论，都是在比较口径而不是模型。

---

## 六、与替代方案的有边界比较

### 6.1 同代模型：有边界比较，不是全面对比

`[原文事实]` S03 的横向表里，M3.1 Flash 的位置呈现清晰的**能力形状**（而不是全面领先）：

- **企业自动化最强**：Automation-Bench 62.8 高于 DeepSeek V4.1 Flash-1017（60.5）、GLM-5.3（48.8）、GPT-5.6 Sol（45.8）、Opus 5（50.3）；BankerToolBench 76.2 与 Opus 5 并列第一。
- **代码类落后一档**：DeepSWE v1.1 73.7 低于 DeepSeek V4.1 Flash-1017 的 77.0；NL2Repo-Bench 61.2 低于 68.2 与 Opus 5 的 75.3；SWE Refactor Bench 23.0 低于 GPT-5.6 Sol 的 28.5 与 Opus 5 的 31.0；Terminal Bench 4.0 38.1 低于 DeepSeek V4.1 Flash-1017 的 42.3 与 Opus 5 的 51.8。
- **长上下文**：LOCA-Bench 256K 60.3 与 GPT-5.6 Sol 的 60.0 基本持平，高于 Kimi K3（49.7）、GLM-5.3（50.3）、Opus 5（53.7）。
- **安全**：CyberGym 82.2 低于 GLM-5.3（84.5）与 GPT-5.6 Sol（83.6）。

`[评]` **形状比排名更有信息**：M3.1 Flash 的画像是"**企业流程自动化 + 长上下文 + 低成本**强，**纯代码工程**中等"。对一个要在真实 SaaS/内部系统上跑长链路流程的 Agent harness，这是比"总榜第一"更实用的画像；但对一个以写代码为主任务的 coding harness，SWE 类三项（DeepSWE / NL2Repo / SWE Refactor）全部落后一档，意味着**不能默认用它替换主力 coding 模型**。

### 6.2 稀疏注意力路线：MSA 的取舍位置

| 方案 | 粒度 | 选择器 | 相对 GQA 的能力代价 | 部署复杂度 |
|---|---|---|---|---|
| **MSA（S06）** | 128-token 块，top-16（≈2048 token 上界） | 可训练 Index Branch + KL 对齐训练 | 论文称**持平**（109B MoE、3T token） | 中（需专用 kernel，跨 Blackwell/Rubin/AMD 三套实现） |
| 纯线性 / 滑窗注意力（混合式） | token 或固定窗口 | 无（规则式） | 通常有可测退化 | 低 |
| DeepSeek NSA 一类"token 级 + 压缩块" | 更细 | 专用打分 + 压缩 | 各家口径不同 | 高 |

`[评]` MSA 的关键设计选择是**故意做粗**："We adopt blockwise token selection with a smaller top-k, enabling efficient execution across a wider range of GPU architectures while relaxing the head-dimension constraints imposed by prior designs"（S06 §1）。块粒度换来了**跨 GPU 家族的通用性**——这与 §3.4 的硬件矩阵互相印证：一个能在 SM100 / SM107 / CDNA4 上用同一套"128 块 + top-16"逻辑跑起来的注意力，比一个在单一硬件上快 20% 但换卡就失效的注意力更适合生产。`[推测]` 代价是**精细 token 级检索能力**：当答案的关键信息落在某个块的非最强 token 上时，块级 max-pooling 会系统性偏好"该块中最像 query 的那个 token"，这在"针藏在长上下文里"的任务上可能表现为召回下降。S06 声称下游 benchmark 持平，但**未覆盖 NIAH 类极端检索探针**，本报告因此把这视为一个未被排除的边界。

### 6.3 投机解码路线：DSpark vs MTP vs EAGLE

`[原文事实]` S03 明说 M3.1 用 DSpark **替换**了 M3 时代的 "EAGLE-like MTP approach"；S07 的生产数据是相对 **MTP-1** 基线的 60–85% 每用户提速。

`[评]` 三者区别在**"谁决定验证多长"**：MTP/EAGLE 类是固定长度验证；DSpark 用 confidence head 估计前缀存活概率并**按请求动态定长**。在高并发 serving 里，固定长度验证会把 batch 容量浪费在高拒绝风险 token 上——这正是 §3.3 论文摘要点名的机制。`[推测]` 对 Agent 场景（输出结构化、长度分布方差大、工具调用序列长），动态验证长度应当优于固定长度；但 DSpark 的收益数据来自 **DeepSeek-V4 的生产流量**，把它外推到 MiniMax-M3.1 的流量分布上属于未验证的迁移。

### 6.4 量化路线：NVFP4 vs FP8 vs MXFP8 的分工

`[代码证据]` 从 S04/S05 可以拼出一张**各硬件上谁承担什么**的表：

| 组件 | Blackwell | Rubin | Hopper | AMD MI350 |
|---|---|---|---|---|
| KV cache | NVFP4（QAT） | NVFP4（QAT） | **FP8**（降级） | NVFP4（QAT） |
| indexer cache | NVFP4 | NVFP4（转 FP16 算分） | **FP8**（降级） | NVFP4（查表反量化） |
| routed experts | NVFP4 原生 | NVFP4 原生 | NVFP4 on **Marlin** | 加载时重量化为 **MXFP8** |
| 其他 dense 投影 | MXFP8 | MXFP8 | MXFP8 | MXFP8 |
| 投机解码 | ✅ 7 tok | ✅ | ❌ | ✅ 3 tok |

`[评]` 这张表把硬件差异讲透了：Hopper 路径失去原生 FP4 tensor-core 加速，KV 降为 FP8 且不启用 DSpark，因此长上下文容量与 decode 收益显著缩水；但 routed-expert 权重仍以 NVFP4 存储并通过 Marlin 运行，**权重压缩收益并未归零**。所以更准确的结论是：NVFP4 + QAT 的完整收益主要在 Blackwell/Rubin/AMD 路径兑现，Hopper 只保留其中一部分；用 Hopper 结果外推其他平台会失真。

---

## 七、对 Agent harness 选型的可迁移启示与限制

### 7.1 可迁移的启示

1. **上下文经济学要按"并发 × 长度"算，不按单价算。** `[代码证据]` S04 的 76 vs 28 并发对比说明：同一模型、同样的 KV 字节数下，**NVFP4 KV 换来的是并发而非延迟**。对 harness 而言，"每百万 token 多少钱"是第二顺位指标，第一顺位是"在我真实的并发剖面下能同时服务多少条会话"。`[推测]` 凡是任务上下文在 100K–500K 区间的 harness（仓库级分析、长文档审计、日志取证），量化格式对总拥有成本的影响会大于模型单价差异。
2. **把 `reasoning_effort` 当成 harness 的一等公民参数。** `[原文事实]` S03 写明 M3.1 的 reasoning 强度为 `low / medium / high / xhigh / max` 五档，S05 给出调用方式 `chat_template_kwargs: {"reasoning_effort": "<level>"}`。（`[待验证]` "默认 max 且不可关闭"仅见于搜索结果中的二手中文转述，**未在 S01–S05 的一手材料中核实`——若属实，则未显式指定档位的调用会默认落在最贵档位。）`[评]` 这意味着：(a) 不同任务应当能各自选档，否则所有任务都在付最贵的档位；(b) **任何跨模型的能力/成本对比如果不记录 thinking 档位就是无效的**——S04 自己就靠"最大 reasoning effort"才拿到 AA 的 42 分。harness 应当把档位写进每条 trace。
3. **投机解码模型的成本必须用"接受长度"标定，不能用标称 TPS。** `[厂商主张]` vLLM 的 AgentX 用的是**合成接受长度 3.16–3.26**（S04）——这意味着厂商的 tok/s 数字里已经隐含了一个未必适用于你的接受长度假设。harness 应实测自己流量下的接受长度，再重算单位任务成本。
4. **"不知道"必须是 agent 契约的一部分，而不是模型的自然行为。** `[独立评估｜二手]` AA-Omniscience 的 93% 幻觉率（S10）意味着：**必须用工具化手段把不确定性外化**——强制引用来源、要求"证据不足时显式声明"、对高风险动作加人工确认闸门。这条启示**与模型选择无关**，是所有 Agent harness 都该做的，但廉价模型把这块风险放大了。
5. **Day-0 支持要按"上游合并进度"评估，而不是按"镜像可拉取"评估。** `[代码证据]` §4.7 的 PR 表显示：文档类 PR 已合并，**核心模型 PR #63232 仍 open 且带 `needs-rebase`**。harness 团队的落地清单应包含：镜像 tag 固定策略、上游合并后的 diff 审查、kernel 版本与 CUDA 13.4 `QMUL4` 指令的最低驱动要求。
6. **跨硬件比较必须带降级路径表。** `[代码证据]` §6.4 那张表说明同一个模型在 Hopper 上的实际形态与 Blackwell 差好几档。任何"这个模型在我们机器上更快"的结论，若不说明硬件路径，就不可比。

### 7.2 限制：这些启示不能迁移到哪里

- **不能把 vLLM 的 kernel 数字当成模型能力数字。** §4 的全部数字都是 **vLLM 在自己 day-0 镜像、特定硬件、特定并发剖面下**的结果；换 SGLang / TokenSpeed / TensorRT-LLM（`[原文事实]` S03 列出这三者为推荐框架）实现路径不同，数字不可比。
- **不能把托管 API 的 TPS 当作自建集群的容量指标**，反之亦然（§2.2）。
- **MSA 的"质量持平"结论来自 109B MoE / 3T token 的对照实验（S06），不是 M3.1-Flash 本身**。`[推测]` 把论文结论外推到 428B / 23B 激活的 M3.1 是合理但**未经直接验证**的推断；M3.1 相对 M3 还叠加了"前三层也换成稀疏"这一改动（`[原文事实]` S03），其质量影响在两篇官方材料中**均无单独评测**。
- **93% 幻觉率的精确值主要来自 VentureBeat 对 Artificial Analysis 的转述与 AA 官方公开摘要**；独立复核已访问 AA 模型页，确认其当前 Intelligence Index 为 43、AA-Omniscience 的计分定义会奖励正确、惩罚幻觉且不惩罚拒答，但页面未公开完整逐题记录。它是**强烈的反向信号**，不应脱离版本和评测设置当成恒定模型属性。

---

## 八、Limitations（本研究自身的边界）

1. **未运行任何模型、kernel 或 benchmark。** 全部数字为来源转述；`[厂商主张]` 与 `[独立评估]` 已在正文逐条标注，但**没有任何一条被本报告独立复现**。
2. **未逐表审计 MSA 论文全文。** 已核对摘要与机制/训练目标相关章节，但未系统复核全部消融、训练稳定性数据、更多模态结果与局限讨论；§3.1 中关于"块级 max-pooling 可能损失精细检索能力"只是 `[推测]`，论文的 NIAH 类实验未核实。
3. **DSpark 论文只核对了摘要、机构与生产部署相关章节**，没有逐表复核全部离线实验；其 DeepSeek-AI / Peking University 归属已确认。
4. **未读 MiniMax 官方 API 文档、模型权重与 config.json**，因此报告中的"428B 总参 / 23B 激活 / 1M 上下文"只依据模型卡自述，未与权重文件核对；`[原文事实]` 该模型卡还写明 "the checkpoint is at MiniMaxAI/MiniMax-M3.1-Flash"，**权重目录结构未验证**。
5. **未验证 vLLM PR 的具体代码内容**，只读了 GitHub API 返回的标题、状态、时间与文件名清单；**未 diff 具体实现**，也未核实 `fmha_sm100.cmake` 等文件在 PR 中的实际改动。
6. **AgentX 基准的复现条件不完整**：S04 说明其基准细节"详见我们上一篇博文"，本报告**未读那篇**（MiniMax M3 的 Day-0 博文），因此 AgentX 的请求分布、并发阶梯定义、是否含工具调用**均未知**。
7. **Automation-Bench 62.8 vs 62.2 与 AA 42 vs 43 两处不一致未解决**（§5.5）。
8. **S04 未说明 12.5% 带宽数字对应的 indexer 量化格式**（128 B/token/layer 未标 dtype，而 M3.1 的 indexer cache 本身是 NVFP4），因此该比例的可迁移性未被验证（§3.1.4）。
9. **未核实**一条搜索结果中出现的第三方线索（称 DSpark / DFlash 在量化目标下存在未关闭的确定性 bug）；该线索来自 `duanyytop/agents-radar` 的 issue 摘要，本报告**未读其原文**，故不作为结论使用，仅在此登记为待核。
10. **资料时点**：全部网络读取发生于 2026-10-25（UTC 16:00–16:40 左右）；模型、镜像、PR、榜单与定价都可能在此后变化。`[原文事实]` S01 的 `publishedTime` 为 2026-10-19T00:00:00Z，S04 正文标注 2026-10-23。
11. **本报告未评估 MiniMax 的服务稳定性、SLA、数据处理条款与合规属性**，这些是 Agent harness 落地的必要条件，但不在两篇原文的讨论范围内。

---

## 九、思考与追问

### 9.1 我真正理解了什么

- **"稀疏 + 量化 + 投机解码"不是三件独立的事，而是一条从"训练"到"服务"的完整链条**：MSA 决定了哪些 token 值得读（块级、每组独立、精确注意力保质量）；QAT 决定了这些 token 的 KV 与专家权重能以多低的比特存（NVFP4 必须是训练出来的，否则稀疏选择本身就被量化误差污染）；DSpark 决定了在剩下的带宽里一次能多吐几个 token（接受长度动态、按置信度调度）。任何一环单独做都能拿到局部收益，但**三环的收益只有在 Blackwell/Rubin/AMD 这类有 FP4 路径或强互联的硬件上才同时兑现**——Hopper 路径上 NVFP4 与投机解码双双缺席。
- **本代模型最值得注意的不是分数，是"厂商发布文与技术材料的信息密度差"**：MiniMax 发布文通篇没有一个架构名词，而真正的机制分布在模型卡、arXiv 论文、vLLM 博客、部署 recipe、kernel 仓库和 PR 列表这**六个层次**里，且彼此口径不同。对 harness 选型者而言，**"读发布文"远远不够**。
- **Agent 场景里最该被量化的指标厂商没有发布**：七个官方 benchmark 全是任务完成度，而 AA 测出的 93% "幻觉率"（答错时选择错答而非拒答的比例）完全不在厂商叙事里。这提示了一件事：**能力榜与可靠性榜必须分开读**，而后者对 Agent 比前者更要命。

### 9.2 我还没搞懂什么

- MSA 的**块级 max-pooling 在真实 needle-in-a-haystack 任务上的召回损失**到底有多大？论文称"on par"，但我没读到它的 NIAH 类消融。
- **"近 3 倍推理提速"**中的基线是什么？是同一 API 的 M3 在同等并发下的输出 TPS，还是同等硬件自建集群的端到端延迟？两者的工程含义完全不同。
- **DSpark 接受长度在 MiniMax-M3.1 自己的流量分布上落在什么区间**？vLLM 用的是合成值 3.16–3.26，真实值可能显著不同，而它直接决定单位任务成本。
- **QAT 的 NVFP4 是否让"第三方量化版本"（S03 自己警告"结果会不同"）在能力上有可见损失**？这对"能否用别人量化过的权重"影响很大。
- **NVFP4 KV 在 1M 上下文下的精度表现**如何？S04 只给了字节数，没有给长上下文检索精度随长度衰减的曲线。

### 9.3 下一步读什么或做什么

1. 读 arXiv:2606.13392 的完整消融（NIAH / 长上下文召回 / 训练稳定性），补上 §9.2 的第一问。
2. 读 arXiv:2607.05147 全文确认机构归属与 DeepSeek-V4 生产数据的设置，判断能否外推到 MiniMax 流量。
3. 读 vLLM 上一篇 AgentX 博文（MiniMax M3 Day-0），补齐 AgentX 基准的请求分布与并发阶梯定义（§8-6）。
4. 抓取 Artificial Analysis 的 M3.1-Flash 原始模型页，核对 42 vs 43 与"93% 幻觉率"的原始定义与评测设置（§5.4、§5.5）。
5. 若要落地：在**自己真实的 Agent 任务集**上做 A/B——M3.1-Flash 跑 `reasoning_effort=max` 与 `medium` 两档，配合 §9.2-3 实测接受长度，用实测数据重算单位任务成本，并与 GLM-5.3 Flash / DeepSeek V4.1 Flash-1017 做**同脚手架**对比（而不是引用 §5.1 的厂商横表）。

---

## 附：来源清单（可复核）

- S01 https://www.minimax.io/blog/minimax-m31f （2026-10-19，官方发布文，英文）
- S02 https://www.minimax.cn/blog/minimax-m31f （2026-10-19，官方发布文，中文）
- S03 https://huggingface.co/MiniMaxAI/MiniMax-M3.1-Flash （官方模型卡）
- S04 https://vllm.ai/blog/2026-10-23-minimax-m31-flash （2026-10-23，vLLM 官方博客）
- S05 https://recipes.vllm.ai/MiniMaxAI/MiniMax-M3.1-Flash （vLLM Recipes）
- S06 https://arxiv.org/abs/2606.13392 （MiniMax Sparse Attention，v2 2026-06-12）
- S07 https://arxiv.org/abs/2607.05147 （DSpark，2026-07-06）
- S08 https://github.com/vllm-project/MSA ；上游 https://github.com/MiniMax-AI/MSA （MSA kernel 仓库，MIT）
- S09 vLLM PR：#63232 / #63428 / #63257 / #63244 / #63236 / #63380 / #63490 / #63491（GitHub API，读取于 2026-10-25）
- S10 https://venturebeat.com/technology/minimaxs-new-m3-1-flash-beats-deepseek-and-opus-5-on-a-key-business-benchmark-at-lower-cost-but-with-a-high-hallucination-rate （二手报道，转述 Artificial Analysis）
- S11 https://artificialanalysis.ai/models/minimax-m3-1-flash （独立评测机构模型页；用于核对当前 Index 与 AA-Omniscience 定义）
