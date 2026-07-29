# 章：Kimi Delta Attention（KDA）+ 混合注意力

> 源：技术报告 §2.1 / §2.1.1 / §2.1.2。⚠️ **公式保真警告**：docling 抽取时编号公式(Eq.1–6)显示为 `<!-- formula-not-decoded -->`（未解码），本章的公式**基于原始 PDF 人工补全**，非纯自动蒸馏所得——这是 book-to-skill 在公式密集论文上的已知局限（见本 demo 评估笔记）。

## 心智模型：会聪明遗忘的传令兵

KDA 是**线性注意力**——不让每个 token 与所有 token 两两对视（那是标准 attention 的 O(n²) 堵点），而是一个"传令兵"带着状态矩阵 S 从头扫到尾，边扫边"选择性遗忘旧信息、写入新信息"，一趟 O(n) 完成。

## 核心机制（逐点）

- **delta-rule 递归 + 通道级遗忘门**：状态更新 `S_t = (I − β_t k_t k_t^T) Diag(α_t) S_{t−1} + β_t k_t v_t^T`，输出 `õ_t = S_t^T q_t`。
  - `α_t ∈ (0,1)^{d_k}`：**通道级**单步保留因子（每类信息分别决定忘多少）
  - `β_t ∈ (0,1)`：delta-rule 写入强度
- **参数化**（每 head）：q/k/v 投影经 ShortConv + Swish；q、k 再过 L2Norm；低秩投影 + head 专属 bias 产生细粒度 decay logit `z_t^h`。
- **分块并行（chunkwise）**：跨块递归、块内并行。块大小 C，`Γ` 为通道累积衰减，UT 变换产出伪值项 `Ṽ`。输出 O 拆两项：跨块（inter-chunk）+ 块内（intra-chunk，Tril 因果掩码）。

## K3 相对 Kimi Linear 的两个关键改进（重点）

1. **有下界的 log-decay**（消除性能瓶颈）
   - 问题：Eq.4 用 `1/Γ` 重缩放 key，而 Γ 是 (0,1) 内因子连乘 → 倒数可无限增大 → 低精度溢出。Kimi Linear 靠 log 空间 + 16-token 子 tile 控制，但**对角 tile 仍需慢速逐位置计算**（intra-chunk 主瓶颈）。
   - K3 解法：把 decay logit→log-decay 的映射从无界 `−e^A·Softplus(z)` 换成**有下界 scaled-sigmoid** `g = gmin·Sigmoid(e^A·z)`，`gmin=−5` 固定。→ 保留因子 `α > e^−5 ≈ 6.7e−3`，16-token tile 累积 log-decay 落在 (−80,0)，倒数在 BF16 范围内。
   - **收益**：对角 + 非对角 tile **全部用 Tensor Core 稠密矩阵乘**，慢速位置对通道消失。典型"算法-系统协同设计"。
2. **全秩输出门**：从 Kimi Linear 的低秩门改为输入相关的全秩投影：`y_t = W_o[Sigmoid(W_g x_t) ⊙ RMSNorm(õ_t)]`。

## Gated MLA（§2.1.2）——全局注意力兜底

- 每块 3 个 KDA + 1 个 Gated MLA（3:1），backbone 末尾额外加 1 个 MLA 保证最后一层做全局注意力。
- MLA（源自 DeepSeek-V2）把 KV 压成低维潜向量 `c_t=W_c x_t`，缓存 c 而非完整 KV，省显存又保全局注意力。
- **K3 关键改动：所有 MLA 层用 NoPE（无位置编码）** → 位置感全交给 KDA。好处：扩上下文不用 retune RoPE / YaRN。
- MLA 也加输入相关全秩输出门；训练时注意力输出保 FP32 纠正 flash-attention 舍入偏差。

## 一句话

KDA 用"聪明遗忘的传令兵"把长序列注意力降到线性；K3 的有下界 decay 让它在 Tensor Core 上全速跑；配 3:1 的 NoPE Gated MLA 兜住全局交互——高效与全局兼得。
