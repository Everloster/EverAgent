---
title: "PuRo-2B 开放低成本预训练配方深度解析：MuonHyperball、FP8 与 RTX 5090 的 $5090 实验"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-20"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["pretraining", "muon_optimizer", "fp8_training", "cost_scaling_law", "curriculum_learning", "model_averaging", "open_recipe", "consumer_gpu"]
related_concepts: ["mixed_precision_training", "learning_rate_schedule"]
related_entities: ["tsinghua_pacman", "nvidia"]
---

# PuRo-2B 开放低成本预训练配方深度解析：MuonHyperball、FP8 与 RTX 5090 的 $5090 实验

> 一句话：清华 thu-pacman 用 96 张消费级 RTX 5090、FP8 精度、MuonHyperball 优化器与课程模型平均，从零训练 1.4T tokens 的 2B 模型，把「达到 Qwen2-1.5B 水平」的复现成本压到 $4.4K——并给出成本-性能标度律。本报告精读论文（arXiv 2608.27370v2，63 页）与配套开源仓 thu-pacman/Puro-Megatron，逐层拆解其硬件 hack、系统设计、优化器理论与数据方法论。

## 0. 一页结论

1. **定位**：PuRo-2B（普罗-2B）补上了「开放配方」谱系的最后一环——**可复现 ≠ 可负担**。OLMo/SmolLM3 等开放了数据与代码，但 SmolLM3-3B 用了 384 张 H100、复现要 $700K+；PuRo 用三级开放度框架（closed → open-weight → open-recipe）定位自己，主张 open-recipe 还必须**成本可达**（S=p25-26, §5）。
2. **账本**（口径见 §1）：生产版 $6.9K 达到接近 Qwen2.5-1.5B；$4.4K 的 Uniform-Phase2-1of2 是真实中间 checkpoint，实测 55.54 已越过 Qwen2-1.5B 的 55.14，论文再用拟合曲线概括这一交点（15 benchmark 无权平均；PuRo 档位见 Table 19, S=p53，对比模型见 Table 7, S=p39）。
3. **四大杠杆**：① RTX 5090 的 FP8 成本效率是 H200 的 ~2.7×（$0.31/h 摊销价 vs $4.00/h，EFLOP/USD 口径）；② 改 NVIDIA 驱动解锁消费卡的 PCIe P2P 与 GPUDirect RDMA（软件禁制而非硬件限制）；③ blockwise FP8 全程训练（72% 计算走 FP8，吞吐 1.36×，质量净收益 1.34×）；④ MuonHyperball 使**有效学习率变成显式超参**——这是全文理论核心（S=p8-13）。
4. **理论灵魂**：MuonH 把每个权重矩阵钉在初始化半径的球面上，使有效学习率 ρ_t **数值上等于**学习率超参本身；论文用 170M 对照实验证明 MuonH 相对普通 Muon 的收益主要来自有效 LR schedule 的可控性，而非球面投影本身（普通 Muon 对齐有效 LR 后 3.030 ≈ MuonH 3.029 << 不对齐 3.073）（S=p12-14, Figure 5）。
5. **数据方法论**：不迷信单一样本级质量分，而是用「proxy benchmarking」——每个候选数据切片从同一 Qwen3-0.6B checkpoint 续训 2000 步、15 benchmark 出**能力向量**，用能力向量（含 PCA 投影）指导选源、源内分位过滤与两阶段配比（S=p17-19, §3.6）。
6. **诚实的边界**：作者明确声明成本口径是「重跑最终配方的边际加速器成本」（排除数据预处理、消融实验、后训练、人力），承认课程收益部分可能来自基准污染、驱动修改有 EULA 风险且他人难以原样复现（S=p8 §2.2, p16 §3.4, p9-10 §3.1.2）。

---

## 1. 问题定位与成本口径

### 1.1 「可复现」与「可负担」之间的鸿沟

论文把现有模型分为三级：closed（GPT/Claude/Gemini）、open-weight（Qwen/Gemma/Llama——有权重无数据与配方）、open-recipe（OLMo/OLMoE/SmolLM/YuLan/Marin/Instella——数据、代码、配置、checkpoint 全开）。但开放不等于负担得起：Llama-3.2-3B 训练成本超 $1.5M，复现 SmolLM3-3B 要 $700K+；open-recipe 阵营内部，Yulan-Mini-2.4B 用了 48 张 A800、SmolLM3 用了 384 张 H100、Instella-3B 第一阶段用 128 张 MI300X（S=p4 §1, p25-26 §5.1）。小型研究组即使拿到全部配方也跑不动。

PuRo 的主张：把训练负载（数据效率）、数值精度（FP8）、硬件可达性（消费卡）、显式成本核算四件事**一起**做，才能填平这道鸿沟（S=p26 §5.2）。

### 1.2 Reproduction-Cost Boundary：先说清楚什么不算钱

读这篇论文的一切成本数字前，必须先钉住它的口径（§2.2, S=p8）：

- **算什么**：从 phase-specific 数据 shard 物化完成后开始，仅 Phase 1 + Phase 2 生产 run 的算力时间，按 RTX 5090 租赁等效价折算（账本保留 CNY 原值便于追溯）。
- **不算什么**：数据获取与预处理（Kaiyuan-SpaRK 的 Spark 集群）、proxy 模型实验、scaling/消融研究、失败与探索 run、后训练、评测、checkpoint 平均、科研人力、CPU/存储/网络、税与折旧。

作者自己总结：这是「狭义边际加速器成本」，不是开发这个模型的总成本，也不是从零重建所有工件的成本。**$5090 是营销钩子（标题梗：预算 ≤ 卡价），$6.9K/$4.4K 才是正文口径**。这个诚实声明是开放配方工作中少见的规范做法，也是本报告后面所有批判的基线。

## 2. 硬件层：为什么是 RTX 5090，以及两个驱动 hack

### 2.1 性价比账

论文的 GPU 对比表（Table 2, S=p9，价格为 2026-08-16 采集）：

| GPU | BF16/FP8 峰值 (TFLOPS) | 显存 | 租价 ($/h) | 峰值算力/成本 (EFLOP/USD, BF16/FP8) |
|---|---|---|---|---|
| A100 SXM4 | 312 / – | 80 GB | 1.79 | 0.63 / – |
| H200 SXM5 | 989.5 / 1979 | 141 GB | 4.00 | 0.89 / 1.78 |
| RTX PRO 6000 | 503.8 / 1007.6 | 96 GB | 1.89 | 0.96 / 1.92 |
| **RTX 5090** | 209.5 / 419 | 32 GB | **0.31**（自摊销） | **2.43 / 4.87** |

RTX 5090 绝对吞吐远低于数据中心卡（FP32 累积下 Tensor Core 还被人为限半——消费卡惯例），但**单位美元算力**的 BF16/FP8 成本效率约是 H200 的 2.7×。注意两点口径细节：① RTX 5090 因 NVIDIA EULA 限制没有公开租赁渠道，$0.31/h 是作者把硬件+电费按 5 年摊销的估计（8 卡节点约 12,000 CNY/月）；② Blackwell 数据中心卡（GB200）因政策与成本不可得，5090 是**有 FP4 支持的最实际选项**（RTX PRO 6000 也有 FP4 但更贵，S=p9 §3.1.1）。

### 2.2 软件禁制的破解：P2P 与 GPUDirect RDMA

5090 的两大硬件短板：无 NVLink、32 GB 显存。论文发现这两条路上真正的限制是**驱动层的软件禁制**而非硬件（§3.1.2, S=p9-10）：

- **PCIe P2P**：NVIDIA 在非数据中心卡上禁用 PCIe P2P，迫使 GPU 间通信经主存中转（ping-pong）。作者用修改版开源 NVIDIA 驱动 + 平台配置（关 IOMMU 与 PCIe ACS、调 NPS/Sub-NUMA）启用 P2P：单向带宽 31.5 → 56 GB/s（逼近 PCIe 5.0 ×16 的 64 GB/s 物理极限），双向 32 → 111 GB/s，延迟 14.3 µs → 0.4 µs；8 卡 AllReduce busbw 从 14.75 → 27.34 GB/s，同 socket 4 卡从 16.33 → 46.31 GB/s（约 2.8×）。
- **GPUDirect RDMA（GDR）**：跨节点场景下消费卡同样被禁 GDR。作者对 CUDA 用户态驱动做最小二进制修改启用之（EULA 原因不能公开细节）：24 卡 AllReduce busbw 从 8.87 → 19.93 GB/s。拿不到改版驱动时可用原厂驱动跑同配方，只是跨节点带宽更低。
- 集群拓扑：x86 双路服务器、每台 8 张 5090（每 socket 4 张）、400 Gbps InfiniBand 互联（双口 ConnectX-7 接 200 Gbps HDR 交换机）。

作者加了三条 caveat：驱动修改无厂商支持、自担风险；不能突破物理 PCIe 带宽；P2P/GDR 不是无脑开（低端 CPU 的 root complex peer-switching 能力弱时，P2P 反而可能比 ping-pong 更堵（S=p10））。这段是全文最有黑客精神的工程叙事——它同时揭示了「消费卡训练」的真实门槛：**别人要复现同样的吞吐，也得过驱动修改这道墙**。

## 3. 系统层：Megatron 补丁面的设计逻辑

### 3.1 并行策略：为什么完全不用张量并行

通信带宽受限 → 只用通信需求温和的并行维度（§3.1.3, S=p10）：

- **DP**（主通信是优化器周边的 ReduceScatter/AllGather）+ **PP**（只在 stage 边界交换 hidden state），**不用 TP**（每层内部都有频繁集合通信）。
- 自定义 **pp-dp 排序**：把每个 PP 组放在节点内拓扑相近的 GPU 上，降低对通信延迟的敏感度——偏离 Megatron 默认 rank 排序。
- 生产配置：Phase 1 用 24 卡（3 节点）、PP=2 layout (18|10)、DP=12，中位吞吐 238 TFLOP/s/卡；Phase 2 用 96 卡、PP=4 layout (9|9|9|1)、DP=24，192 TFLOP/s/卡（Amdahl 定律使梯度同步占比上升）。加权 MFU 约 73%——注意口径：混合精度加权峰值 P_eff=(0.72/419+0.28/209.5)⁻¹≈327 TFLOP/s，不是 BF16-only 满血 MFU（S=p11）。

### 3.2 三个细颗粒度的工程决策

1. **MBS 用 roofline knee 选**：FP8 kernel 算得快但多出量化开销，比 BF16 更容易 memory-bound（小 hidden size 放大此效应）。作者扩展 Megatron 的解析 FLOP 估算器报告每个 GEMM/FlashAttention 的调用形状，逐形状 benchmark Transformer Engine kernel，选「FLOP/s 不再显著增长的最小 MBS」——结果是 MBS=2（S=p10-11）。
2. **PP 负载均衡**：大词表（151,936，沿用 Qwen tokenizer）使 embedding + LM head 的计算与内存占比不可忽略；FP8 又加速了内部层、拉大与 LM head 的差距（LM head 一项相当于数层 Transformer 的计算量）。按层/submodule/算子/精度归因的理论 FLOPs 报告指导 stage 分层：给含 LM head 的 stage 少分 Transformer 层——这就是 (18|10)（第一段 embedding+18 层，第二段 10 层+LM head）与 (9|9|9|1) 的由来（S=p10-11）。
3. **优化器状态的内存均衡**：替换 Megatron Core 分布式优化器在该版本对 embedding/LM head 张量的过度集中，改为内存感知分配——Muon 张量按显存足迹贪心装箱（bin-packing）分配给 DP owner，Adam 扁平张量尽量均匀填满剩余空间。这是把训练状态塞进 32 GB 的关键（S=p11）。

### 3.3 Puro-Megatron 仓库：可审计的补丁集

配套开源仓 [thu-pacman/Puro-Megatron](https://github.com/thu-pacman/Puro-Megatron) fork 自 Megatron-LM `core_v0.16.0`（commit `3bec9aa`），是**精选补丁系列**而非内部分支快照：`ORIGIN_COMMITS.md` 给出公开 commit ↔ 内部源 commit 的映射表（PROM 数据 11 个、MuonHyperball 4 个、内存均衡 4 个等），并明确列出**故意排除**的部分——两阶段 WD sweep、SFT/curriculum 代码、评测套件、长上下文实验、DCU 移植等（R=ORIGIN_COMMITS.md:43-53）。全量补丁可 `git diff core_v0.16.0..main` 审计。

`examples/puro/run_puro_2b.sh` 是三阶段配方的权威入口（R=run_puro_2b.sh:108-177），关键超参与论文正文逐一对应：

| 项 | Phase 1 (power) | Phase 2 (transition) | Phase 2 (constant-continuation) |
|---|---|---|---|
| train-samples | 107,271,866（×4096 ≈ 439B tokens） | 341,867,221（总预算） | 同左 |
| LR | 0.005 → min 0.0005，power 衰减，指数 0.5 | 0.00104 起，linear → 1e-5 | 常数 4.077e-5 |
| PP / layout | 2 / (18\|10) | 4 / (9\|9\|9\|1) | 4 / (9\|9\|9\|1) |
| 特殊 | warmup 1.536M samples | reset scheduler + dataloader 进度 | `--ckpt-step 218000`，非持久 ckpt 每 100 步、保留 4 |

（模型侧：28 层、hidden 2048、FFN 6144、GQA 16 头/8 KV 组、head_dim 128、seq 4096、RoPE base 10000、RMSNorm、QK-norm、untied embedding、SwiGLU、THD packed attention、NullTokenizer + Qwen 词表 151936。）

## 4. 精度层：blockwise FP8 从零起步

- **策略**：从随机初始化起全程 FP8 混合精度，无 BF16 预热、无中途切精度。训练状态与数值敏感操作保留 BF16/FP32 路径，Transformer 线性层（QKV/输出投影/MLP 投影）的 Fprop/Dgrad/Wgrad 走 E4M3；core attention（FlashAttention/SDPA）留 BF16；checkpoint 权重仍为 BF16，发布格式由单独的后训练转换产生（§3.2, S=p11）。
- **块缩放**：激活与激活梯度沿 GEMM 归约维按 128 连续值分组、权重按 128×128 二维块——**逻辑块大小跟随 DeepSeek-V3**；但在 RTX 5090（SM 120）上每个块缩放因子被约束为 2 的幂（E8M0 的纯指数表达），Transformer Engine 经 Blackwell 原生 **MXFP8 路径**执行。作者自己点出这个实现差异：「DeepSeek-V3 在 Hopper 上训练」可能是原因（S=p11）。
- **量化收益账**：FP8 加速的操作占总量 72% 计算。匹配 20 tokens/参数的 scaling ladder 中，blockwise FP8 相对 BF16 在五个测试尺寸上验证损失 +0.0031~0.0039；共享形状拟合把这映射为 **98.0% BF16 等效算力保留**；1.7B 规模中位吞吐 +1.36×，**质量调整后净收益 1.34×**（§3.2, S=p11; 细节 §4.3.1）。

## 5. 优化器层：MuonHyperball 与有效学习率（全文理论核心）

### 5.1 机制：把矩阵钉在固定半径的球面上

PuRo 采用 Muon 加 Hyperball 包装（MuonH，Wen et al. 引文 [99]）训练选定的权重矩阵（attention 与 MLP 矩阵）；embedding、norm 层、LM head 及其余参数走 AdamW（§3.3, S=p11-12）。

对每个被包裹的矩阵 $W_t$，MuonH 固定半径 $R=\lVert W_0\rVert_F$（初始化时的 Frobenius 范数），并把 Muon 更新 $u_t$ 归一化为 $\hat{u}_t = u_t/\lVert u_t\rVert_F$，然后（式 1, S=p12）：

$$\tilde{W}_{t+1} = W_t - \eta_t R\,\hat{u}_t, \qquad W_{t+1} = R\cdot\mathrm{Normalize}(\tilde{W}_{t+1})$$

- $\eta_t R \hat u_t$：规定**位移长度恰为 $\eta_t R$** 的方向性更新（$u_t$ 只提供方向）；
- 第二步把更新后的矩阵**投影回半径 $R$ 的球面**（$\mathrm{Normalize}(A)=A/\lVert A\rVert_F$）。

对照普通 Muon + decoupled weight decay（式 3, S=p12）：$W_{t+1}=(1-\lambda\eta_t)W_t-\eta_t u_t$——半径在 wd 与更新中**漂移**，位移长度 $\eta_t\lVert u_t\rVert_F$ 依赖优化器状态。

### 5.2 关键洞察：有效学习率从「涌现」变「处方」

尺度不变性是动机：norm 层使多数 attention/MLP 矩阵近似满足 $\mathcal{L}(cW)\approx\mathcal{L}(W)$，因此更新幅度应相对当前权重尺度解释。定义矩阵级**有效学习率**（ELR，式 4, S=p12）：

$$\rho_t(W) = \frac{\eta_t \lVert u_t\rVert_F}{\lVert W_t\rVert_F}$$

- 普通 Muon：$\rho_t$ 由演化的 $\lVert W_t\rVert$ 与 $\lVert u_t\rVert$ **间接涌现**，scalar LR 控制不了它；
- MuonH：位移范数 $\eta_t R$、权重范数 $R$，故 $\rho_t = \eta_t R / R = \eta_t$——**数值上等于学习率超参本身**，投影再把半径放回 $R$（S=p13, Figure 4 有清晰对照表）。

生产配置：AdamW 组用 base schedule $\eta_t^{base}$，MuonH 组 $\eta_t^H = m\cdot\eta_t^{base}$，$m=10$（对 `--muon-hyperball-lr-mult 10`，R=run_puro_2b.sh:52）。

### 5.3 归因实验：收益来自 ELR 可控，不是球面投影本身

170M BF16 三臂对照（同架构/批量/序列/种子/评测，§3.3.1, S=p13-14, Figure 5）：

| 臂 | 做法 | 最终验证损失 |
|---|---|---|
| MuonH | 预定线性衰减 ELR | **3.029** |
| Muon, ELR 对齐 | 普通 Muon，在线调 scalar LR 使 $\rho_t$ 跟随 MuonH 的曲线（式 5: $\eta_t=\rho_t^H\lVert W_t\rVert_F/\lVert u_t\rVert_F$） | 3.030 |
| Muon, 普通 LR | 直接用 MuonH 的 base LR schedule | 3.073 |

普通 LR 的 Muon 其诱导 ELR 早期快速衰减、收尾趋零——早期 loss 降得快、后劲不足；对齐 ELR 后基本复现 MuonH 曲线。**结论：MuonH 相对普通 Muon 的效率差距主要归因于有效 LR schedule，投影本身不是主角。** 附录 F.3 进一步给出反直觉控制：普通 Muon 用「山形」scalar LR 也能维持预定 ELR 轨迹收敛。

配套诊断：Multi-Power Law（MPL，引文 [57]）——从 LR schedule 预测 loss 曲线形状的标度律。用 ELR 而非 raw LR 做 MPL 拟合，held-out RMSE 从 0.0265 降到 0.0210（两 run 平均，主要由 base-Muon 臂贡献）（S=p13-14）。

### 5.4 参数路由与「逻辑矩阵」

- **路由**：二维 attention/MLP 矩阵 → MuonH；embedding、输出权重、bias、norm 权重及其余非矩阵参数 → AdamW（R=puro-megatron-ext.md:62-66）。理论直觉来自尺度不变性论证（norm 之后的位置）；论文未给出「逐类路由消融」，这是一处可追问的缺口。
- **fixed-radius 矩阵禁用 weight decay**（AdamW 路径保留 wd）——球面投影已承担半径控制，wd 会与投影打架（R=puro-megatron-ext.md:64-65）。
- **逻辑矩阵**（R=puro-megatron-ext.md:52-58）：fused QKV 与 SwiGLU FC1 物理上是拼接大矩阵，但语义上是若干独立矩阵。`--muon-qkv-norm-mode separate` 等让归一化与 Newton-Schulz 都按**逻辑子矩阵**分别进行（Q、K、V 各自正交化；SwiGLU 的门/值各自处理）——对拼接矩阵整体做 NS 会把不同语义块的更新混在一起。
- 可选 fixed-RMS：`--muon-hyperball-rms VALUE` 把每个逻辑矩阵的 Frobenius 半径定为 $VALUE\cdot\sqrt{global\_numel}$（含 TP 分片），与初始化时半径解耦。

## 6. LR Schedule：两阶段设计与其证据链

**动机**：实际项目总 token 预算常事先不定（continual pretraining 是常态）→ 需要 open-ended schedule + 受控终端衰减（§3.3.2, S=p14）。

**WSD sweep 证据**（0.6B、GBS 512、TPP 20 基准 + TPP 50/100 扩展；effective peak 0.008~0.024 × decay ratio 0.2~1.0，S=p14-15, Figure 6）：

- **观察 1**：更大 peak 需要更长 decay——peak 0.008/0.012/0.016/0.020/0.024 的最优点分别落在 decay ratio 0.4/1.0/0.8/0.8/1.0（以「距最优 0.01 loss 内的下边缘」看更稳：0.4/0.4/0.6/0.6/0.8 单调不降）。
- **观察 2**：更长 horizon 也要更长 decay——peak 0.012 下 TPP 20→50→100 的下边缘 0.4→0.6→0.6。
- **省算力的替代**：不全网格扫，只用 decay 0.2 与 1.0 两个端点拟合 MPL，估出最优 ratio 从 peak 0.008 的 0.33 升到 0.024 的 0.85——「信封背面」趋势诊断（S=p15, §F）。

**生产 schedule**（右面板 Figure 6 + R=run_puro_2b.sh）：

- **Phase 1（438.8B tokens）**：open-ended power 衰减 $\eta_t = min + (max-min)(1+t/\tau)^{-p}$，$p=0.5$、$\tau$=1.536M samples；base LR 从 5e-3 降到 1.04e-3，对应 MuonH 矩阵的 effective LR 从 ~5e-2 降到 1.04e-2。不设衰减地平线，尾巴保留续训路径（数据分布演化时可以直接接着跑）（S=p15; R=puro-megatron-ext.md:95-107）。
- **Phase 2（960.0B tokens）**：base LR 从 1.04e-3 接入**长线性衰减**（而非「稳定段+短尾降」）到 1e-5；按 m=10 换算，MuonH 矩阵的 ELR 是 1.04e-2→1e-4。这样才是同一口径下的“高初始 ELR + 长衰减”，让 loss 下降发生在训练全程。

## 7. 数据配方：proxy benchmarking 方法论

### 7.1 核心思想：用能力向量代替单一样本分

跨领域可比的单一样本级质量分难以设计，论文改为对候选**数据切片**做受控续训实验（§3.6, S=p17-18, Figure 9）：每个切片从同一 Qwen3-0.6B checkpoint 续训 2000 步（约 8.4B tokens，candidate 占比爬升到 80%、86B base replay 递减），在固定 15 benchmark 上评测得**能力向量**（GSM8K/MATH/MBPP/HumanEval/C-Eval/WinoGrande/...）。

这个 proxy 设计适合比较候选切片，却不能直接证明某个切片是性能变化的因果来源：HF 数据集卡明确提示实验没有额外的 base-only continuation 对照。因此能力向量应理解为同一配方下的筛选信号，而非脱离训练设置仍成立的因果质量分。

三条切片采样规则（S=p18）：

1. ≥50B tokens 且有可用样本分 → 按分数排序取 q00/q25/q50/q75 四个 4B 分位切片；
2. 5~50B 或无分数的大源 → 随机 4B 切片一片；
3. <5B 不评。

**源内分位的价值**：DCLM-Dedup 的 q00 切片平均 proxy 排第 3、q25 排第 11——同一源不同区域训练价值差异巨大，源级标签会掩盖这一点。据此 Phase 2 只保留 DCLM-Dedup top ~5%（34B tokens）（S=p18）。

### 7.2 能力平衡与两阶段组成

对能力向量做 PCA：PC1 ≈ General、Code 与 General 反向、Math 主要落在 PC2 且对 PC1 略正——**Code 与 General 的交换比 Math 与 General 更尖锐**，故 Phase 2 给 math 的份额（18.3%）略多于 code（11.5%）（S=p19, §I.0）。

| 域 | Phase 1 (438.84B) | Phase 2 (938.06B) |
|---|---|---|
| English | 73.2% | 59.4% |
| Math | 7.2% | 18.3% |
| Chinese | 11.7% | 9.4% |
| Code | 7.9% | 11.5% |
| SFT/instruction | – | 1.3% |

（S=p18, Table 3/Figure 8。Phase 1 重广覆盖，Phase 2 加数学与指令样数据。）

### 7.3 物化与复现：静态 shard + 课程桶

- 四阶段管线：源内去重（不跨源——分析发现跨源去重量收益小）→ proxy 评测 → 启发式过滤（能力剖面 × 域覆盖 × 语言平衡 × token 预算）→ **最终物化**：冻结源 revision、保留规则、混合权重与随机种子，合并为固定 shard 顺序读取，**无在线混合或采样**（S=p19）。
- 实现：Kaiyuan-SpaRK（Spark 框架，MinHash 等重计算操作经 Chukonu 用 C++ 内核，~2.5× 于 JVM）；支持课程桶物化——同一组件池换物化顺序即可产出 UD（均匀）或课程流（S=p19）。
- **Phase 1→2 过渡**：43.9B tokens 线性换血（21.9B Phase 1 replay + 21.9B Phase 2 头部），之后 916.1B 纯 Phase 2；总计 438.8+960.0 ≈ **1.4T tokens**（S=p19）。

## 8. 课程与 Curriculum Model Averaging

**冲突**：课程把好样本排后（提高好数据的数据效率），但常规终端 LR 衰减让后期样本在小更新下被看——好数据恰恰在被「冷处理」的时段出现（§3.4, S=p15, 引文 [56]）。

**CMA 四变体**（S=p15-16）：

| 变体 | 数据序 | LR | 终点 |
|---|---|---|---|
| UD | 均匀重排 | 衰减 | 末 checkpoint |
| CD | 课程 | 衰减 | 末 checkpoint |
| CDC | 课程 | 衰减→常数 LR 续训 | 续训末 checkpoint |
| **CMA（生产）** | 课程 | 衰减→常数 LR 续训 | 续训 6 checkpoint 等权平均 |

**课程构造**（组件内、保混合权重）：有分数组件按分数排序（分数只在源内解释，**不做全局排名**）、无分数组件随机序；按累计 token 质量算归一化 rank；切成 **376 个桶 × ~2.5B tokens**，每桶从每个组件抽 1/376——跨组件混合权重逐桶保持（S=p15-16, Figure 7）。

**生产 CMA run**：从 step 218k 恢复、base LR 固定 4.08e-5（Hyperball LR = 4.08e-4 = MuonH 矩阵的 ELR），训至 222,569 步，对 steps 222,100/222,200/222,300/222,400/222,500/222,569 **六个 checkpoint 等权平均**（只平均模型参数、不平均优化器状态；窗口 469 步 ≈ 2.95B tokens，相邻间距 100 步 ≈ 0.63B）得到发布模型（S=p16, p56 §H.3）。与 `run_puro_2b.sh` 的 `phase2-constant-continuation` 分支逐参数对上：脚本 `--lr 4.077248127291725e-05` 即论文 4.08e-5 的未舍入值；步数自洽（341,867,221 samples ÷ GBS 1536 ≈ 222,569.8，对应最后一个被平均的 222,569 checkpoint）（R=run_puro_2b.sh:150-171）。一个未解细节：脚本 `--non-persistent-ckpt-num-to-keep 4` 只保留 4 个非持久 checkpoint，六个平均输入如何凑齐（训练途中离线导出？）论文与 repo 均未说明。

这里还要保留两个方法边界：论文引用的参考 CMA 方法默认使用 EMA，而 PuRo 对最后六个 checkpoint 做简单等权平均；215k 与 218k 两个续训起点也不是严格匹配消融，结果只能说明本次实验选择 218k 更好，不能证明它是普适最优点（S=p56 §H.3）。

**消融**（15 benchmark 平均, S=p16, Figure 13b）：

- CD vs UD：57.17 vs 55.99（+1.18，不平均）；各自衰减轨迹平均后 57.18 vs 55.57（+1.61）；
- model averaging 单独并非普遍有益：UD 端点 −0.42、CD 端点 +0.01；
- CDC 215k/218k 不平均：55.64 / 57.12；**6-checkpoint 平均后：56.80 / 57.81** → 生产选 218k 平均分支。

**诚实声明**：CD 对 UD 的部分优势可能来自后期数据的基准污染（§A 讨论）；但 SFT 后优势保持（§4.4），污染难以完全解释持续改进（S=p16）。

## 9. 后训练 case study：预训练配方如何影响 SFT 后性能

研究问题：预训练配方（数据顺序与 checkpoint 构造）的影响在 SFT 后是否保持？——这个问题只有拿到完整预训练管线才能在最终模型尺度上回答（checkpoint 单独公开不够，小规模消融的 base 模型又太弱）（§3.5, S=p16-17）。对照的干净性由 UD Control 保证：UD 流与 CD 流来自**同一个物化组件池**（token 多重集在池级完全相同），唯一差别是呈现顺序（UD 用 seed 20260609 的确定性全局重排抹掉课程对齐）（§H.2, S=p55）。

设计：对 UD 与 CMA 两组 checkpoint 施加**完全相同**的 SFT（继续用 MuonH、cosine 1e-5→1e-7、m=10、GBS 160），三种数据设置：① GSM8K 系（GSM8K 训练拆分 + MetaMathQA/OpenMathInstruct-2 合成 + Tulu-3 数学与指令分量）；② Math&Code + replay（更大数学集 + OpenCodeInstruct/Magicoder 代码 + Phase 2 课程尾段高质量数据回放）；③ Tulu-3 英文混域。全部去重、13-gram 去污染（S=p17）。

**三设置结果**（UD 初始化 → CMA 初始化，成对设计、完全相同的 SFT 数据与优化，S=§4.4+附录 E）：

| SFT 设置 | UD | CMA | Δ | 备注 |
|---|---|---|---|---|
| GSM8K-based（最控制） | 66.89 | 68.66 | **+1.77pp** | 3/3 重复占优（范围 1.36–2.12）；19.2 万对话/41.4M assistant tokens |
| Math&Code + replay | 74.10 | 76.12 | **+2.02pp** | 范围 1.21–3.26；含 Phase 2 课程尾段高质量数据回放 |
| Tulu-3 混域（15-bench 宏平均） | 53.96 | 55.13 | **+1.17pp** | 15 基准 10 个占优（分布不均匀）；IFEval 41.71→43.07（+1.36pp） |

**核心发现**：预训练课程 + CMA 的优势**穿透了后训练**——三个设置全部保持、数学设置甚至略增（+1.77→+2.02pp）。这直接回应了「base 模型上的课程收益可能只是末段数据的临时效应」的质疑：同样的 SFT 过程冲不掉它（S=p24 §4.4; 附录 E）。这是「只有 open-recipe 才做得出来」的那类研究——需要把两个 1.4T tokens 的完整 Phase 2 各跑一遍才能对照。

## 10. 评测与 Puro Cost Scaling Law

### 10.1 评测口径

15 benchmarks 可按内容分成数学/代码与推理/知识两群，但评分方式另有一条边界：GSM8K、MATH、sanitized-MBPP、HumanEval、MMLU-Pro 与 BBH 共 6 项使用 GEN greedy 解码 + 确定性后处理，其余 9 项使用 PPL。OpenCompass 统一管线、固定 checkpoint/tokenizer revision 与数据快照；OLMES 惯例下 CF/MCF 双式**每模型独立取优**。总分 P = 15 项无权平均（§4.1, S=p20-21）。

Math/Code 群（Table 4, S=p21）：

| 模型 | GSM8K | MATH | MBPP | HumanEval | 四项均 |
|---|---|---|---|---|---|
| Qwen2-1.5B | 59.82 | 23.70 | 50.19 | 27.44 | 40.29 |
| Qwen2.5-1.5B | 67.70 | 32.28 | 58.37 | 31.71 | 47.52 |
| Qwen3-1.7B-Base | 76.04 | 42.44 | 64.20 | 51.22 | 58.48 |
| SmolLM3-3B-Base | 81.73 | 56.12 | 60.31 | 37.80 | 58.99 |
| **Puro-2B（$6.9K）** | 59.67 | 30.30 | 52.92 | 31.10 | **43.50** |
| Puro-2B（$4.4K 档） | 56.03 | 27.86 | 49.81 | 20.73 | 38.61 |

PuRo-2B 超 Qwen2-1.5B 3.21 分、距 Qwen2.5-1.5B 4.02 分；同代对标里 Qwen3-1.7B（58.48）显著更高——「接近 Qwen2.5」的表述需放在**代际语境**（Qwen2.5 是 2024 模型）里读。

推理/知识群（Table 5, S=p22）：PuRo-2B 11 项平均 63.02，vs Qwen2-1.5B 60.54、Qwen2.5-1.5B 65.53；最大单项赢面 BBH +10.32，唯一明显退步 CSQA −2.71。**15 项总分 P：PuRo-2B（CMA 生产版）57.81、$4.4K 档（UD-1/2）55.54、Qwen2-1.5B 55.14、Qwen2.5-1.5B 60.73、SmolLM3-3B 65.85**（PuRo 自身档位见 Table 19 S=p53；对比模型分见 Table 7 S=p39）——$4.4K 档实测已越过 Qwen2-1.5B 线。

### 10.2 Puro Cost Scaling Law

**数据点**（Table 18/19, S=p53）：五个 UD final checkpoint 档位——

| Phase 2 tokens | GPU-h | 成本 | Avg15 |
|---|---:|---:|---:|
| 60.00B | 7,041 | $2.16K | 51.98 |
| 120.00B | 8,073 | $2.47K | 53.24 |
| 240.00B | 10,136 | $3.10K | 54.01 |
| 480.00B | 14,262 | $4.37K | 55.54 |
| 959.99B | 22,514 | $6.89K | 56.00 |

精确成本账：Phase 1 实测 6,009.46 GPU-h（$1.84K）+ Phase 2 16,504.95 GPU-h = 22,514.41 h × 2.0833 RMB/h = 46,905 RMB ≈ **$6,891**（USD:CNY=6.8067，2026-07-01）；全程 1.40T tokens、17.6 天（Table 6/8, S=p38-40）。RTX 5090 费率 $0.31/GPU-h = 12,000 CNY/月 ÷ (8 卡×30 天×24 h) 的五年摊销。

**成本因子的阶梯证据**（附录 D, S=p42-44；0.17B~1.70B 五档、TPP=20）：MuonH 的质量等效率力乘子 **κ=1.19×**（leave-one-out 1.17–1.28，等效省 16.1% 算力）；blockwise FP8 的 BF16 等效算力保留 **ρ_C=98.0%**（LOO 97.6–98.1）× 吞吐 1.36× = 质量调整净收益 **1.34×**（省 25.2%）。产线等效：FP8 跑 22,654 h ≈ BF16 需 30,286 h。

**跨模型坐标**（§4.3.2, Table 7, S=p39-40；各模型复现算力按 H100 等效 989.5 TFLOP/s、η=0.70 折算）：Qwen2-1.5B ≈$84.3K（6ND 估算）、Qwen2.5-1.5B ≈$216.8K（family tokens 口径）、Llama-3.2-3B $1.495M（reported）、SmolLM3 ≈$718.8K、Yulan ≈$48.5K、Instella ≈$100.3K。注意两点口径：Qwen2.5 用家族级 token 记账会**高估**单模型复现成本；reported 与 estimated 两类证据在 Figure 1 中以颜色/填充区分。PuRo 的位置：约 **1/6 以下成本**达到可比 open-recipe 的水平（S=p8）。

**反演**：按标度律反推，CD 端点（57.18）等效 $11.36K、CMA 总分 57.81 等效 $16.55K 的 UD-型成本——即 CMA 相当于用 2.40× 的「等效训练预算」买到该分数（S=p24）；shifted RMSE 0.209（unshifted 0.452）。

**标度律的局限**：拟合形式为 P = a + b·log₂(C − C_P1)（P 为 15-bench 均值，C_P1=$1.84K 由 Phase 1 实测固定；shift 后 in-sample RMSE 0.452→0.209），但系数 a、b 的数值与置信区间未公布；5 个数据点无不确定性量化（LOO 只用于附录 D 的 κ/ρ_C 拟合）；「$4.4K 达 Qwen2-1.5B」实为「UD-1/2 档实测 55.54 > 55.14」加标度律内插，不是外推新 run（S=p24, p53, p26；HF 模型卡自己保留「The fit has no uncertainty interval」免责声明）。作者将其定位为 **fixed-2B、配方特定的 scale-down 关系**，不是普适定律——放大需新通信/显存设计，5090 的 32 GB HBM 是放大瓶颈（S=p38 附录 A）。

**成本因子的口径警示**（§4.3.1, S=p22-23）：论文自己强调四因子（硬件 2.77×、FP8 1.34×、MuonH 1.19×、CMA 2.40×）**参考系不同、不构成联合阶乘消融**，乘积只是 accounting estimates；且消融在 TPP=20 跑、生产是 TPP≈700 的过训练 regime（数据丰富、非 compute-optimal，附录 A 第三条）。

## 11. 批判性评估

1. **成本口径窄而自洽，但传播中必然失真**。$5090/$4.4K/$6.9K 都是「重跑最终配方的边际加速器成本」：Kaiyuan-SpaRK 数据预处理集群、proxy benchmarking 的 2000 步 × N 切片实验、WSD sweep、170M 诊断、Scaling ladder 的全部 run、后训练、评测、人力全部不计（S=p8 §2.2）。论文自己写得清楚，但标题的传播效应会按「训练一个 2B 模型只要 $5090」读——真实「从零到拥有」成本高一个量级以上。
2. **复现的软门槛被驱动修改卡住**。P2P/GDR 的带宽收益依赖修改版 NVIDIA 驱动（EULA 限制不可公开），他人复现只能用原厂驱动、跨节点带宽打折（S=p10）。加上 RTX 5090 无公开租赁渠道（$0.31/h 是 5 年摊销估计）——「可负担」的可达性对第三方要再打折扣。
3. **评测是自家协议**。15 benchmark 集合、OLMES 双式取优、确定性后处理都是自家口径；与各家官方数字不可直接比。好在对所有对比模型一视同仁，且公开了管线。
4. **代际选择**。「接近 Qwen2.5-1.5B」的对标是 2024 年模型；同代 Qwen3-1.7B-Base 在同一表里高 15 分。这不否定成本主张，但「性能对标」的表述要小心引用。
5. **基准污染承认**。CD/CMA 的课程优势部分可能来自后期数据污染基准（作者自己指出，S=p16），靠「SFT 后优势保持」辩护。发布表也没有把中文能力作为主要目标或单列中文 benchmark；虽然训练数据含中文，这份 15 项均分不能代表中文综合能力（S=p38 附录 A）。
6. **理论侧的可追问点**：MuonH vs Muon 的归因实验在 170M BF16 上做，2B FP8 生产配置上是否同构未单独验证；参数路由（哪些矩阵进 MuonH）凭尺度不变性直觉选择、未见逐类路由消融；「逻辑矩阵」分别 NS 的收益同样缺独立消融（仅作为生产配置出现）。
7. **开放度的裂缝比摘要说的更宽：四类资产四种 license**。论文摘要称「data, code, and model weights under Apache 2.0」（S=p1），实测：HF 模型卡 Apache 2.0（权重）✓；HF 数据集卡 license=other——混合上游条款，Apache 2.0 仅覆盖项目自产的文档/manifest/处理产物，**NVIDIA 控制的 Nemotron-CC-v2 与 Nemotron-Pretraining-Code-v1 Synthetic-Code 分区禁止原始再分发**；GitHub Puro-Megatron=Other/NOASSERTION；GitHub Kaiyuan-Spark=Apache-2.0。且 SFT/curriculum 代码、评测套件明确排除在公开仓外（R=ORIGIN_COMMITS.md:45-53）——「全流程开放」中后训练一段只有论文与 checkpoint，没有代码。
8. **$4.4K 的精确身份**：HF 模型卡口径比论文摘要严——$4.4K 对应 **Uniform-Phase2-1of2 中间 checkpoint**（非 canonical 终点）；「$5090」标题数字与账本无严格对应（最接近的是 CMA Phase 2 的 $5.05K），是 RTX 5090 谐音的品牌化选择 [推测]。
9. **元数据级瑕疵**：HF 模型卡与数据集卡的 bibtex 与 v2 PDF 题名页作者名单不一致（PDF 含 Chengxia Li、无 Kaiyue Wen；HF bibtex 反之——MuonH 原作者 Wen 在 PDF 中只出现在致谢与引文 [99]）。2026-10-15 的 arXiv API 元数据已经与 PDF 一致，无法复现早期“arXiv 也不一致”的说法；引用时以 PDF 题名页或当前 arXiv 元数据为准。
10. **HF 评论区独有事实**：pszemraj 质疑 419 TFLOPS 是 FP32-accumulate 口径（消费级 Blackwell sm120 上半速）、问是否试过 FP16 累积；作者答「明显伤害模型性能」但无论文数字——此问答只存在于 HF papers 页，正文无 FP16-acc 消融。
11. **算力赞助也是成本解释的一部分**。论文致谢与脚注说明 Yanfu Investments 提供了 GPU 资源；这不改变 rental-equivalent 成本账，但提醒读者，团队真实获得硬件、机房与运维条件的路径不等于第三方按 $0.31/GPU-h 即可复现。

### 11.1 外部反响速写

- **有实质内容的独立评论极少**（截至 2026-10-15）：kenashe.ai（2026-08-28）三点质疑——compute cost ≠ total cost、Qwen 对比只在自设 15 任务协议内成立、消费卡改变的是「谁能做实验」而非「谁自动赢」——并建议复用该配方做窄域课程实验而非再造通用弱模型（与本报告 §11 第 1、3 条的批判独立同构）。cctest.ai 强调 $4.4K 是本集合+本协议的拟合值。未发现 HN/Reddit 专题帖。
- **二次传播失真两例**：AlphaSignal 把「approaches Qwen2.5-1.5B」写成「matching」；hankli.space 用通用 TE per-tensor delayed scaling 讲 FP8（实际是 DeepSeek-V3 式细粒度 blockwise）。CSDN/ModelScope 长文转述与论文逐项吻合。引用二手材料时按此分层。
- **作者侧定位**：吕凯峰（@vfleaking，通讯作者）的 X 帖强调科学动机——「我们不仅缺理论，也正在失去在大规模上做受控训练实验的能力」；Puro 建立在两项前作上（CMA 入选 ICLR 2026 Oral；Hyperball/MuonH 即 Wen et al.）。一作罗开荣：清华计算机系三年级博士、姚班本科、陈文光组，曾主导开元-2B（鹏城脑海）；BAAI TALK 第 386 期（2026-09-17）有专题报告。

## 12. 与本库既有知识的缝合

- **Megatron 谱系**：本库《Megatron-LM 大规模训练系统深度解析》（20260416）覆盖了 TP/PP/DP 与混合精度训练的基础结构；PuRo 是那套基础设施在「通信受限 + 显存受限」极端约束下的**反常规用例**（弃 TP、PP layout 按理论 FLOPs 逐层配平、优化器状态 bin-packing）——可视为该报告「并行策略」一节的低配硬件极限延伸。
- **模型效率线的训练侧对称面**：本库 vLLM/投机解码/MoE 线都在推理侧做效率；PuRo 展示训练侧的效率杠杆（精度、数据效率、优化器效率、硬件成本）——两条线共享同一个底层问题：单位美元的智能。
- **优化器生态**：Muon 已从学术 curiosities 走到工业落地（Moonlight/Kimi 等用 Muon 变体训练大模型）；PuRo 的贡献是把「Muon 为什么好」的答案精化为「有效学习率可控」，并给出 ELR 对齐实验作为最干净的证据。**[推测]** ELR 视角可能成为今后 Muon 系工具链的标准诊断量（类似 MFU 之于系统）。
- **开放科学方法论**：三级开放度框架 + Reproduction-Cost Boundary 的口径声明，值得本库评估任何「开放 XX」项目时复用（先问：成本边界含不含数据/消融/后训练？）。

## 13. 思考与追问

1. **我真正理解了什么？** MuonHyperball 的本质不是「另一个优化器变体」，而是把有效学习率从涌现量变成处方量——一旦用 ρ_t=η_t 的等式看，MuonH 的 schedule 设计、与 AdamW 的 m=10 桥接、WSD sweep 的「大 peak 要长 decay」全部串成一条线。低成本开放的真正壁垒也不是算力单价，而是「数据预处理/消融/评测这些不计入 headline 的隐性算力」+ 驱动修改这类不可转移的工程知识。
2. **我还没搞懂什么？** ① ELR 对齐实验在 2B/FP8 尺度是否同构（170M/BF16 的结论外推风险）；② fixed-RMS 半径（--muon-hyperball-rms）与初始化半径的取舍依据论文正文着墨少；③ Power schedule 的 τ=1.536M samples 与 exponent 0.5 的联合选择在 sweep 里怎么定的（附录 F.2 细节待深挖）；④ Puro Cost Scaling Law 的拟合形式与置信区间（附录 D 待补）。
3. **下一步读什么？** ① Wen et al. 的 Hyperball 原文（MuonH 的完整理论）与 MPL 标度律原文 [57]；② Moonlight（Muon 工业落地）对照读；③ DeepSeek-V3 的 blockwise FP8 细节（PuRo 精度设计的上游）；④ 把本报告的 RTX 5090 驱动 hack 与 LLMQ（RTX 4090 FP8 训练）对照，看「消费卡训练」的系统方法谱系。

---

## 资料来源

- **S** = 论文：*PuRo-2B: Poor Lab's Qwen2-1.5B Trained on RTX 5090 within $5090*，arXiv 2608.27370v2，2026-09-03，清华 thu-pacman（Luo Kairong 等，通讯：吕凯峰、陈文光）。引用格式 S=p页码；本地提取件 `/tmp/puro-study/puro-paper.txt`（本次研究用，页码以 PDF 为准）。
- **R** = 仓库：[thu-pacman/Puro-Megatron](https://github.com/thu-pacman/Puro-Megatron)，fork 自 Megatron-LM `core_v0.16.0`。引用 R=文件:行号（`examples/puro/run_puro_2b.sh`、`docs/ORIGIN_COMMITS.md`、`docs/puro-megatron.md`，2026-10-15 快照）。
- HuggingFace 集合：[thu-pacman/puro-2b](https://huggingface.co/collections/thu-pacman/puro-2b)（Base/Phase1/Uniform-Phase2-1of2~1of16/Curriculum-DecayFinal/Curriculum-SMA6-Inputs 等 checkpoint 与数据集）。
- 关联本库报告：《Megatron_LM_大规模训练系统_深度解析_20260416》。
