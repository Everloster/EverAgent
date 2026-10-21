---
title: "NVIDIA CUDA Tile 加速 Mamba-2：从 SSD 分块到三内核融合"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-21"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["mamba_2", "structured_state_space_duality", "cuda_tile", "cutile", "gpu_kernel", "triton", "tensor_cores", "state_space_model"]
related_concepts: ["llm_inference_engines", "flash_attention"]
---

# NVIDIA CUDA Tile 加速 Mamba-2：从 SSD 分块到三内核融合

> 研究时点：2026-10-21  
> 核心材料：NVIDIA 2026-10-19 技术博客、Mamba-2 原论文与作者系列文章、`state-spaces/mamba` 实现、cuTile 官方文档，以及 NVIDIA TileGym 公开主分支快照。  
> 验证边界：本文没有在 NVIDIA B300 上编译或复现 kernel；性能结论均属于 NVIDIA/Jane Street 官方自报。本文核验了公开公式、代码路径、软件与硬件口径，并明确区分源码事实、厂商结果和分析推断。

## 一、结论先行

这篇 NVIDIA 博客真正重要的地方，不只是“cuTile 比 Triton 快 1.14–1.82 倍”，而是展示了一个完整的算子工程闭环：**先从 Mamba-2 的 Structured State Space Duality（SSD）分块算法中识别可融合的数据流，再用 tile 级编程模型把矩阵乘、递推、衰减、因果掩码和 skip connection 压进三个 forward kernels。**

我的核心判断有七条：

1. **性能来源首先是算法分解与 fusion，其次才是 DSL。** 上游 Mamba-2 的典型 Triton forward 路径可拆成 cumulative sum、chunk state、state passing、`C @ Bᵀ`、chunk scan 五个阶段；博客中的 cuTile 路径将后两对阶段分别融合，最终只保留 `chunk_cumsum`、`fwd_pass_state`、`compute_out` 三个 kernel。
2. **最关键的内存优化是避免把完整的 chunk 内交互矩阵写回显存。** `compute_out` 在 tile 内构造 `C @ Bᵀ`，随即施加衰减和因果掩码，再与 `dt·X` 相乘；博客称该矩阵保留在寄存器 tile 中，而非物化成全局内存里的 `[batch, chunks, chunk_size, chunk_size]` 张量。
3. **cuTile 抽象了 thread/warp 映射，但没有抽象掉 kernel 设计。** 程序员仍需决定 chunk、fusion 边界、数据布局、MMA 操作数方向、精度和 autotune 搜索空间。编译器负责把 tile 操作映射到 Tensor Core、Tensor Memory、Shared Memory 与 TMA。
4. **官方 benchmark 很强，但适用范围窄。** 单张 B300 SXM6 上，cuTile forward 相对特定 Triton reference 的官方自报加速为 **1.14×–1.82×**；测试覆盖 1K–256K tokens 与 state size 64–512。它不是端到端模型吞吐或训练结果。TileGym 已公开 backward 实现与 perf harness，但博客没有发布 backward 加速、每个点的绝对延迟或原始结果。
5. **这更像 prefill / training-forward kernel，而非逐 token decode kernel。** Mamba-2 decode 本来就适合直接递推固定大小状态；长序列 prefill 才需要 chunked SSD 把主要工作转成 Tensor Core 友好的矩阵乘。
6. **原博客至少有两处符号表述需要按源码校正。** `dt` 在官方 Mamba-2 代码中经过 `softplus` 后为正，负的是 `A`，所以 `a_t=A·dt_t≤0`；博客简化公式又把输出从 `C_tᵀh_t` 写成了 `C_tᵀh_{t-1}`，与前文和原论文的索引不一致。
7. **TileGym 已把复现所需的代码骨架公开出来。** 固定快照 `NVIDIA/TileGym@3a871364` 包含 `mamba2_chunk_forward`、`mamba2_chunk_backward`、`Mamba2ProblemSpec`、正确性容差和 forward/backward perf harness。真正缺失的是博客图对应的 raw benchmark 结果、B300 独立复现、误差分布与端到端训练数据。

---

## 二、先把数学对象摆正：Mamba-2 在算什么

### 2.1 符号与 shape

以下采用更贴近 kernel 存储的约定，把单个 head 的状态写成 `H × S`；原论文也常写成转置的 `S × H`，两者只差内存与公式方向，不改变计算。

| 符号 | shape | 含义 |
|---|---:|---|
| $t$ | 标量 | token 位置 |
| $H$ | 标量 | head dimension；博客样例为 64 |
| $S$ | 标量 | state size / state dimension；benchmark 扫描 64、128、256、512 |
| $Q$ | 标量 | chunk size；博客样例为 128 |
| $x_t$ | $H$ | 当前 token 的 value-like 输入 |
| $B_t$ | $S$ | 写入状态的 key-like 向量 |
| $C_t$ | $S$ | 从状态读出的 query-like 向量 |
| $dt_t$ | 标量/每 head | 正的选择性步长，源码通过 `softplus` 得到 |
| $A$ | 标量/每 head | 负的学习参数，源码使用 `-exp(A_log)` |
| $a_t=A\cdot dt_t$ | 标量 | 对数域衰减，满足 $a_t\le 0$ |
| $b_t=dt_t B_t$ | $S$ | 已乘步长的写入向量 |
| $h_t$ | $H\times S$ | 固定大小 recurrent state |
| $D$ | 标量或 $H$ | 输入到输出的 skip 参数 |
| $y_t$ | $H$ | 当前 token 输出 |

按这个方向，单步递推可以写成：

$$
h_t = e^{a_t}h_{t-1}+x_t b_t^{\mathsf T},
\qquad
y_t=h_t C_t+D\odot x_t.
$$

逐符号解释：

- $e^{a_t}h_{t-1}$：把旧状态整体衰减；因为 $a_t\le0$，系数位于 $(0,1]$。
- $x_t b_t^{\mathsf T}$：$H\times S$ 的外积，把当前输入写进二维状态。
- $h_t C_t$：用 $C_t$ 沿 state 维读出 $H$ 维输出。
- $D\odot x_t$：绕过 recurrent state 的直接通路。

源码证据很明确：`Mamba2.forward()` 令 `A = -torch.exp(A_log)`，而 step path 令 `dt = softplus(dt + dt_bias)`，再计算 `exp(dt * A)`。[A 的构造](https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/modules/mamba2.py#L182-L194)；[step 中的 dt](https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/modules/mamba2.py#L307-L318)

### 2.2 为什么不能直接沿 token for-loop

逐 token 递推很适合 decode：每次只更新一个固定大小状态，内存不随历史长度增长。但 training 或 prefill 已经拥有整段序列，串行 for-loop 无法充分利用 GPU。

另一条路是把每个 token 的完整 $h_t$ 都物化出来并做 parallel scan。这保持 $O(T)$ 序列复杂度，却会生成庞大的中间状态张量，并且主要由逐元素运算构成，难以喂满 Tensor Core。

SSD 的关键发现是：对 Mamba-2 使用的 scalar-times-identity 状态转移，递推形式与一种带结构 mask 的线性 attention 完全等价。于是可以让：

- chunk **内部**走 attention-like 的矩阵乘；
- chunk **之间**只传固定大小状态。

这就是“线性复杂度 + 矩阵乘友好”的来源，而非简单地把 RNN 换一种语法。[Mamba-2 论文，第 6 节](https://arxiv.org/pdf/2405.21060)；[作者算法讲解](https://tridao.me/blog/2024/mamba2-part3-algorithm)

### 2.3 一个 chunk 的闭式计算

考虑长度为 $Q$ 的 chunk，令：

$$
g_i=\sum_{r=1}^{i}a_r,
\qquad
E_{ij}=
\begin{cases}
e^{g_i-g_j}, & i\ge j,\\
0, & i<j.
\end{cases}
$$

其中：

- $g_i$ 是 chunk 内到位置 $i$ 的累计对数衰减；
- $E\in\mathbb R^{Q\times Q}$ 同时编码衰减与因果关系；
- $i<j$ 的未来 token 被置零。

把每个 $x_i,B_i,C_i$ 堆成 $X\in\mathbb R^{Q\times H}$、$B,C\in\mathbb R^{Q\times S}$，chunk 末状态为：

$$
h_Q=e^{g_Q}h_0+
X^{\mathsf T}
\left[\operatorname{diag}\!\left(dt\odot e^{g_Q\mathbf 1-g}\right)B\right].
$$

式中：

- 第一项是 chunk 初始状态一路衰减到末尾；
- 方括号把每个 $B_i$ 乘上步长 $dt_i$ 和从位置 $i$ 到 chunk 末尾的衰减；
- $X^{\mathsf T}(\cdot)$ 是 Tensor Core 友好的 $H\times Q$ 乘 $Q\times S$。

chunk 内全部输出可以写成：

$$
Y=
\operatorname{diag}(e^g)C h_0^{\mathsf T}
+\left[E\odot(CB^{\mathsf T})\right]
\operatorname{diag}(dt)X
+D\odot X.
$$

三项分别对应：

1. chunk 之前的历史状态对当前输出的贡献；
2. chunk 内 token 两两交互的贡献；
3. skip connection。

这个式子已经直接暴露了实现机会：`C @ B.T`、状态投影和最后的 score-value 乘法都是 MMA；`E` 不必单独存储，只需由 $g_i-g_j$ 和下三角条件即时构造。

---

## 三、从 SSD 四步算法到三个 cuTile kernels

### 3.1 原始 SSD 四步

Mamba-2 论文把半可分矩阵按 $Q\times Q$ 分块后，得到四步：

1. **Intra-chunk output**：每个对角块用 quadratic form 计算本 chunk 内输出。
2. **Chunk state**：假设初始状态为零，计算每个 chunk 自己产生的末状态。
3. **State passing**：在 chunk 边界状态之间做更短的递推。
4. **State-to-output**：把每个 chunk 的真实初始状态投影回 token 输出。

只有第 3 步保留递推；它的序列长度从 $T$ 缩短到 $T/Q$。其余主要工作都可以转成 matmul。[原论文 Listing 1](https://arxiv.org/pdf/2405.21060)；[官方最小实现](https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/modules/ssd_minimal.py)

### 3.2 Triton reference 的典型数据流

`state-spaces/mamba` 的 combined forward 按以下顺序调用：

```text
_chunk_cumsum_fwd
  → _chunk_state_fwd
  → _state_passing_fwd
  → _bmm_chunk_fwd          # C @ B.T，生成 CB
  → _chunk_scan_fwd         # 衰减、mask、CB @ X、状态输出、D
```

[源码：combined forward](https://github.com/state-spaces/mamba/blob/e9594ce1c732d97440f0332fdc43170a2294dbfa/mamba_ssm/ops/triton/ssd_combined.py#L343-L386)

这段上游代码用于解释标准分解，不等价于证明 NVIDIA benchmark 中 `mamba_ssm 2.3.2.post1 (NVIDIA Dynamo-Triton reference)` 的每一行完全相同；博客没有给出该 baseline 的固定 commit。

### 3.3 cuTile 的三内核重组

| cuTile kernel | 做什么 | 相对标准分解的 fusion | 主要并行轴 |
|---|---|---|---|
| `chunk_cumsum` | 计算 chunk 内 $G=\operatorname{cumsum}(A\cdot dt)$ | 融合逐元素乘与 scan；结果供后两核复用 | chunk × head tile × batch |
| `fwd_pass_state` | 计算每个 chunk 的初始状态和全序列最终状态 | 融合 chunk-state 形成与跨 chunk state passing | batch × head × head tile × state tile；每个 program 内顺序遍历 chunk |
| `compute_out` | 计算历史状态贡献、chunk 内交互与 skip | 融合 `C@Bᵀ`、衰减、causal mask、score×value、`D·X` | batch × chunk × head × head tile |

#### Kernel 1：`chunk_cumsum`

输入 `a[num_heads]` 与 `dt[batch,tokens,heads]` 先转 FP32，广播相乘后沿 chunk token 轴 `ct.cumsum`。实现把自然对数域结果乘以 `log2(e)`，后续统一用更便宜的 `exp2`：

```python
d_tile = ct.cumsum(a_tile * dt_tile, axis=1) * LOG2E
```

它只做 **chunk 内** cumulative sum，不跨 chunk。把 $G$ 单独存回显存看似多一次流量，却避免在 state 和 output kernel 中各算一遍，属于有意保留的共享中间量。

#### Kernel 2：`fwd_pass_state`

每个 program instance 负责一个 `(batch, head, head_tile, state_tile)` 状态切片，并在内部顺序遍历全部 chunks：

```text
读取本切片初始状态
for each chunk:
    保存该 chunk 的初始状态
    读取 X、B、dt、G
    衰减旧状态
    MMA: X.T @ weighted_B
保存最终状态
```

它把“每个 chunk 独自产生状态”和“chunk 间传递状态”合并到同一个 kernel。序列方向仍有依赖，但大量 `(batch, head, H-tile, S-tile)` 切片可以并行；而且不再需要把局部末状态写出后再启动独立 state-passing kernel。

代价也很明确：当 `num_chunks` 很大而 batch/head/tile 并行度不足时，单个 program 的循环会变长。博客的最大序列为 256K、样例 chunk 为 128；若沿用该 chunk，单 program 最多要经历 2,048 次循环。官方没有发布不同 batch/head 并行度下的 occupancy 或 tail effect 数据。

#### Kernel 3：`compute_out`

每个 program 负责一个 `(batch, chunk, head, head_tile)` 输出 tile，分两段工作：

1. 沿 state tiles 累积 `cb_tile = C @ B.T`，同时计算 `C @ H.T`；
2. 即时构造 pairwise decay 与 causal mask，再做 `cb_tile @ (dt·X)`，最后加 `D·X`。

关键点是：

```text
CB 不落全局内存
pairwise decay 不落全局内存
causal mask 不落全局内存
FP32 accumulator 跨 state tiles 累积
最终一次 store 写出 output
```

这减少了中间张量流量与 kernel launch，也把更多工作变成连续的 MMA。另一方面，`cb_tile` 的面积是 $Q^2$：`Q=128` 时有 16,384 个 FP32 元素，逻辑数据量为 64 KiB。cuTile 的 tile 不保证对应某一种物理存储，编译器可能把相关数据映射到寄存器、Tensor Memory 或 Shared Memory；因此这里只能推断它会影响资源规划与 occupancy，不能把 64 KiB 直接等同于某类硬件占用。[分析]

---

## 四、cuTile 到底替开发者做了什么

### 4.1 编程对象：array、tile、block

cuTile 不暴露单个 GPU thread。开发者表达的是：

- **global array**：带 shape、stride、dtype 的显存数组；PyTorch tensor 与 CuPy array 可通过 DLPack / CUDA Array Interface 传入；
- **tile**：kernel 内不可变的多维值；shape 必须编译期已知，各维必须是 2 的幂；
- **block**：grid 中的逻辑执行单元，负责对一个或多个 tiles 做集体并行运算。

标量操作在一个 thread 上串行执行，array/tile 操作由 block 内资源协同完成。tile 是数据单位，block 是执行单位，两者不能混为一谈。[cuTile 数据模型](https://docs.nvidia.com/cuda/cutile-python/data.html)；[执行模型](https://docs.nvidia.com/cuda/cutile-python/execution.html)

常用原语与这三个 kernels 的关系如下：

| 原语 | 作用 | Mamba-2 中的用途 |
|---|---|---|
| `ct.bid(axis)` | 当前逻辑 block 坐标 | 映射 chunk、head tile、batch |
| `ct.load/store` | global array 与 tile 间搬运 | 载入 X/B/C/G/state，写出 G/state/output |
| `ct.cumsum` | tile 内 scan | 生成 chunk 内累计衰减 |
| `ct.mma` | matrix multiply-accumulate | state jump、`C@Bᵀ`、state projection、score×value |
| `ct.arange/where` | 即时索引与选择 | 生成 causal lower triangle，不存 mask |
| `ct.extract` | 取 tile 中局部值 | 读取 chunk 最后一个累计衰减 |

### 4.2 编译器抽象不等于“零调优”

cuTile 的承诺是让同一套 tile 语义跨 NVIDIA GPU 架构编译，并自动使用 Tensor Core、Shared Memory、Tensor Memory Accelerator 等硬件。博客仍然列出四类人工优化：

1. **Latency hint**：给 load/store 标注预期延迟，帮助编译器安排指令与 pipeline buffer 深度。
2. **Swap A/B**：Blackwell 第五代 Tensor Core 的 MMA 两个输入不对称；operand A 可位于 Tensor Memory，operand B 必须位于 Shared Memory。利用 $(AB)^{\mathsf T}=B^{\mathsf T}A^{\mathsf T}$ 改写乘法，把融合后的 `b_dt_d` 放到 A 侧，缓解 Shared Memory 压力。
3. **GMEM layout**：把 `dt` 和 `decay_cumsum` 从不利于连续访问的布局转成 `[batch, head, token]`，使 load 可降到 TMA，而非 cache-unfriendly LDG。
4. **Autotune**：把 block size、occupancy、上述策略放进 `ct.tune.exhaustive_search` 搜索。cuTile 1.5.0 还加入单次配置超时和对慢配置的提前停止。

因此 cuTile 更准确的定位是：**把 thread/warp 级实现细节交给编译器，同时保留算法、tile、布局和资源提示层的控制。**

### 4.3 需要知道的硬约束

官方文档还给出几项会直接影响框架集成的限制：

- tile 各维必须是 2 的幂且编译期已知，shape specialization 会产生独立 JIT cache；
- kernel 内没有 pointer，只能操作有界 array view；
- 多个 array 参数若底层存储重叠，行为未定义；
- block 内不允许显式 synchronization / communication，必须依赖 tile 语义和编译器；
- global array 的普通 shape 查询使用 int32，当前单维可表示元素数上限为 2,147,483,647；
- target-specific compiler hints 会让“同源代码可移植”与“完全相同配置可移植”成为两回事。

这解释了为何高性能框架仍需要 shape bucketing、编译缓存与每代 GPU 的调优记录。

---

## 五、内存、并行与数值设计

### 5.1 为什么 log-space + `exp2`

跨 token 的衰减本质是许多小于等于 1 的数连乘。直接 cumprod 会快速下溢。把它写成：

$$
\prod_{r=j+1}^{i}e^{a_r}
=e^{\sum_{r=j+1}^{i}a_r}
=2^{\log_2(e)\sum_{r=j+1}^{i}a_r}
$$

就能用 cumsum 代替 cumprod，并用硬件更友好的 `exp2` 恢复衰减。

因 $a_t\le0$，对因果区域 $i\ge j$ 有 $g_i-g_j\le0$，指数不会大于 1。上三角可能出现正差并溢出，但随后由 `ct.where(i>=j, ..., 0)` 丢弃。博客声称这些被 mask 的值不会污染输出。

### 5.2 精度路径

博客代码显示：

- `A`、`dt` 在 `chunk_cumsum` 内转 FP32 累积；
- `cb_tile` 与 `out_tile` 以 FP32 初始化并累积；
- 最后一次 `cb_tile @ dt_x` 显式转为 `tfloat32`，使用 Tensor Core，以接近 FP32 的动态范围和 10-bit mantissa 计算；
- 最终输出再转成目标 dtype；benchmark 样例输入为 BF16，state dtype 为 FP32。

这不是“全程 FP32”。TF32、BF16 输入、衰减 buffer 的实际存储 dtype 和长链 cumulative error 都可能影响误差。

### 5.3 一个尚未闭合的数值问题

Mamba-2 作者在算法讲解中明确警告：用“两个 cumulative sums 相减”构造 segment sum 可能发生 catastrophic cancellation，甚至让训练立即出现 NaN；其稳定参考实现改用只做加法的 `segsum`。[作者的 Stability 小节](https://tridao.me/blog/2024/mamba2-part3-algorithm#stability)

**[待验证]** 新 cuTile forward 使用 chunk 内 `g_i-g_j`。这不必然说明实现错误，因为：

- 只在有限 chunk 内相减，而非全序列；
- cumsum 和 accumulator 使用 FP32；
- TileGym 已提供 forward/backward reference 与正确性测试：forward 输出容差 `2e-2`、final state `1e-2`，backward 不同梯度的容差约 `1e-2–8e-2`；
- 这些测试至少说明作者针对公开 shape 做了数值门禁，但不能替代长序列误差分布和训练稳定性实验。

TileGym 的测试补上了“有没有 reference/tolerance”这一层证据；尚未公开的是博客 benchmark 对应的 max/mean error、极端衰减压力测试、不同长度的误差曲线和端到端训练稳定性。因此在把它纳入训练栈前，仍应独立复现数值边界，不能只看速度图。还要注意，作者警告的主要对象是全序列 cumulative-difference 构造；cuTile 在有限 chunk 内做差，风险机制相关，但不能直接等同。

### 5.4 原文两处校勘

| 原文表述 | 交叉核验 | 结论 |
|---|---|---|
| “All values in `dt` are negative” | 官方代码对 `dt+dt_bias` 做 `softplus`；`A=-exp(A_log)` | 应理解为 $A<0,dt>0,a=A\cdot dt<0$ |
| 简化式写 $y_t=C_t^{\mathsf T}h_{t-1}+Dx_t$ | 前一行、原论文与状态更新语义使用 $h_t$ | 属于索引表述不一致；实现应以原论文和代码为准 |

另外，博客先把状态描述成 `S,H`，kernel 则用 `[BLOCK_HEAD,BLOCK_STATE]`。这是转置存储约定，不是数学冲突。

---

## 六、benchmark：哪些数字能信到什么程度

### 6.1 官方公开的完整环境

| 维度 | 官方配置 |
|---|---|
| 候选实现 | `cuda-tile` 1.5.0；TileIR assembler 13.4 |
| baseline | `mamba_ssm` 2.3.2.post1，NVIDIA Dynamo-Triton reference；Triton 3.7.1 |
| PyTorch / CUDA | PyTorch 2.13.0；CUDA 13.3；NVCC 13.3.33 |
| Driver | 595.58.03 |
| Python / OS | Python 3.12.3；Ubuntu 24.04.4 LTS；Linux 6.8.0-107 |
| GPU | 单张 NVIDIA B300 SXM6，compute capability 10.3 |
| GPU 运行上限 | 1920 MHz max SM clock；1100 W power limit；268 GiB HBM |
| 测量对象 | Mamba-2 **forward pass kernels** |
| 图中变量 | tokens：1K、2K、4K、8K、16K、32K、64K、128K、256K；state size：64、128、256、512 |

[官方 benchmark 章节](https://developer.nvidia.com/blog/accelerating-mamba-2-with-high-performance-forward-pass-kernels-in-nvidia-cuda-tile/#mamba-2-forward-pass-performance-benchmarks)

博客还给了一个具体调用样例：

```text
batch_size = 4
num_tokens = 16,384
num_groups = 1
num_heads = 8
state_size = 128
head_size = 64
chunk_size = 128
dtype = bfloat16
state_dtype = float32
measurement = common.benchmark(..., use_cupti=True)["forward"]["median"]
```

但文章没有明确说性能图的所有点都继承了样例中的 batch、heads、head size、groups、chunk size 和 dtype。因此这些字段只能称为“公开样例 shape”，不能无条件当成整张图的固定控制变量。

### 6.2 图中结果

官方正文给出的结论是 **1.14×–1.82×**。图没有打印每个 bar 的数值，以下是对官方图的视觉读取，仅用于理解趋势，误差约 ±0.02–0.03：

| tokens | state 64 | state 128 | state 256 | state 512 |
|---:|---:|---:|---:|---:|
| 1K | ≈1.15× | ≈1.25× | ≈1.33× | ≈1.52× |
| 4K | ≈1.27× | ≈1.42× | ≈1.45× | ≈1.70× |
| 16K | ≈1.39× | ≈1.59× | ≈1.62× | ≈1.82× |
| 256K | ≈1.42× | ≈1.54× | ≈1.59× | ≈1.82× |

能确定的趋势：

- 所有展示配置都高于 1.0×；
- state 越大，加速通常越高；
- 从短序列到约 16K 加速上升，之后大体进入平台区；
- 最高区域是 state 512、tokens ≥16K，约 1.82×。

**[分析]** 这个趋势符合 fusion 的预期：较大 state 增加 `C@Bᵀ`、state projection 和 boundary-state MMA 的占比，cuTile 的 operand placement、TMA 与融合更有发挥空间；较长序列摊薄固定启动和编译后执行开销。但官方没有提供 profiler breakdown，不能把这项解释写成已证实因果。

### 6.3 这些结果不能证明什么

1. **不能证明端到端训练加速 1.14–1.82×。** 博客曲线只测 forward；TileGym 虽已公开 backward 与 perf harness，却没有发布 backward speedup 或端到端训练结果。
2. **不能证明端到端推理吞吐同倍数提升。** 模型还包含投影、卷积、归一化、通信、sampling 和调度。
3. **不能证明 cuTile 普遍优于 Triton。** 对照是特定 Mamba-2 reference、特定版本和 B300。
4. **不能计算绝对收益。** 图只画 speedup，没有公开每个点的 cuTile/Triton latency、tokens/s、warmup、repeat、方差或置信区间。
5. **不能证明跨 GPU 保持同一加速。** 没有 H100、A100、消费卡或不同 clock/power 的数据。
6. **不能证明完整数值等价范围。** TileGym 给出了固定测试容差，但文章未发布 benchmark 对应的误差分布、长度缩放曲线或训练质量变化。

原论文中“SSD 比 Mamba scan 快 2–8×、2K 后快于 FlashAttention-2”来自 2024 年 A100 80GB PCIe 上的另一套实验，不应与本次 B300 上“cuTile 相对 Triton 1.14–1.82×”混成同一数字。前者比较算法与旧 scan，后者比较同一 Mamba-2 forward 的两种 kernel 实现。

---

## 七、可移植性与当前公开状态

### 7.1 源码可移植与性能可移植是两回事

cuTile 官方定位是跨 NVIDIA GPU 架构的 tile IR：同一 source kernel 可以由编译器映射到不同硬件，无需为 Tensor Core 或 TMA 重写 thread-level 代码。[官方介绍](https://developer.nvidia.com/blog/simplify-gpu-programming-with-nvidia-cuda-tile-in-python)

但这篇 Mamba-2 实现包含 Blackwell 专属判断：

- operand A/B 的 Tensor Memory / Shared Memory 不对称；
- B300 的 Tensor Core、TMA 与寄存器资源；
- shape-specific exhaustive search；
- target-specific occupancy / block hints。

因此可以期待**功能可移植**，不能由单卡 benchmark 推出**性能可移植**。在 Hopper、Ampere 或未来架构上，最佳 operand 方向、tile shape 与 occupancy 可能变化。

### 7.2 版本与平台矩阵仍在快速变化

官方 Quickstart 当前要求 Linux x86_64/aarch64 或 Windows x86_64、Driver R580+、CUDA Toolkit 13.1+、Python 3.10–3.13，并列出 compute capability 8.x、10.x、11.x、12.x。与此同时，1.4.0 release notes 又明确写了 Hopper `sm_90` 支持。两处公开文档的架构列表并不完全一致，部署应按具体 `cuda-tile`、Toolkit 与 Driver 组合做编译/运行探针，而不是只读一张静态支持表。[Quickstart](https://docs.nvidia.com/cuda/cutile-python/quickstart.html)；[Release Notes](https://docs.nvidia.com/cuda/cutile-python/generated/release_notes.html)

### 7.3 TileGym 公开实现与剩余复现缺口

NVIDIA 博客写道实现“available through TileGym”，并给出：

```python
tilegym.ops.mamba2_chunk_forward(...)
from tests.ops.test_mamba2 import Mamba2ProblemSpec
```

在 2026-10-21 核验的 [`NVIDIA/TileGym@3a871364`](https://github.com/NVIDIA/TileGym/tree/3a871364f1fbd59ef30b1afcc5a79fc3634888ce) 中，上述入口已经存在：

- `src/tilegym/ops/cutile/mamba2.py` 注册 `mamba2_chunk_forward` 与 `mamba2_chunk_backward`；
- forward 由 `_chunk_cumsum`、`_fwd_pass_state`、`_compute_out` 组成，backward 另含 state 反传与梯度 kernels；
- `tests/ops/test_mamba2.py` 定义 `Mamba2ProblemSpec`、reference、shape matrix 与正确性容差；
- forward perf harness 扫描 `T=2^10…2^18`、`S=64/128/256/512`，使用 batch 4、8 heads、head size 64、chunk 128；backward 也有相应 perf harness。

因此，公开代码与测试入口已经闭合，报告可以审计算法结构和测试标准。仍未闭合的是**结果复现**：仓库没有随代码提交博客图的逐点 raw latency、重复次数、方差、完整 profiler 与误差分布；本报告也没有 B300 环境运行这些 tests。代码可读不等于厂商性能数字已被独立复现。

还存在一处版本漂移：博客示例使用 `common.benchmark(..., use_cupti=True)`，固定快照的测试则调用 `common.benchmark_framework(...)`，当前 harness 走 CUDA Graph 计时路径。读者应以固定提交的 API 为准，不能假设博客片段可以逐字复制到当前 `main`。

---

## 八、对推理框架的实际意义

### 8.1 应按 phase 路由，而不是“一把替换”

**[推测]** 按算法边界，Mamba-2 推理框架至少需要两条 execution path：

```text
长序列 training / prefill
    → chunked SSD forward
    → 大量 Tensor Core MMA

逐 token decode
    → recurrent state update
    → 固定 H×S 状态，不重跑 chunk 矩阵
```

如果推理框架把 decode 也强行塞进 chunk kernel，会引入无意义的 $Q\times Q$ 交互与启动开销。反过来，prefill 若逐 token 递推，又会浪费 GPU 矩阵乘能力。

### 8.2 一个可落地的 operator contract

适合框架集成的接口应显式携带：

```text
inputs:
  X, dt, A, B, C, D
  initial_state?        # 流式 prefill / prefix continuation
  sequence_boundaries? # packed variable-length batch
  shape metadata       # heads, groups, H, S, Q

outputs:
  Y
  final_state          # 交给后续 decode 或下一段 prefill
```

框架还要维护：

- `dtype × shape × GPU arch × compiler version` 的 autotune cache key；
- cuTile 编译失败或 shape 不支持时的 Triton/reference fallback；
- packed sequences 的 boundary reset，防止状态跨样本泄漏；
- CUDA Graph / stream 兼容性；
- initial/final state 的布局与生命周期。

### 8.3 上线前的最小验证矩阵

| 维度 | 至少要测什么 |
|---|---|
| 正确性 | 对照 PyTorch/Triton；max abs/rel error；不同 seed |
| 衰减极端 | 很小/很大 `dt`，接近 0 的 A，长 chunk，256K tokens |
| shape | 非整 chunk 尾部、不同 batch/head/group/H/S/Q、initial state |
| dtype | BF16、FP16、FP32 state、TF32 开关 |
| phase | prefill、流式多段 prefill、decode 接续 |
| 性能 | 冷/热 JIT、warmup、P50/P95、绝对延迟、tokens/s、HBM、功耗 |
| 端到端 | kernel 占比、projection/conv/norm、调度、通信、模型吞吐 |
| 架构 | B300、H100/A100 或实际部署 GPU，各自重新 autotune |

### 8.4 对 kernel DSL 与推理系统的更一般启示

这项工作说明，下一代推理框架的关键抽象可能不是“统一所有模型为 attention”，而是：

1. 用代数结构识别可块化、低秩或可递推的 operator；
2. 在 prefill 与 decode 之间切换等价算法；
3. 把中间张量的存储边界当作一等设计对象；
4. 让 DSL/compiler 负责硬件映射，让框架负责 phase、shape、cache 与 fallback。

**[分析]** cuTile 对框架最大的价值不是替代全部 CUDA/Triton 代码，而是缩短“新算法 → 可读高性能 kernel → 多代 NVIDIA GPU”的路径。它仍需要真实 benchmark、数值门禁和 fallback，无法单凭“编译器自动优化”保证生产效果。

---

## 九、局限、思考与追问

1. 本报告没有 B300 环境，无法复现 1.14–1.82×。
2. 官方没有公开 raw benchmark、绝对延迟、重复次数、方差和 profiler breakdown。
3. 博客性能图只有 forward；TileGym 已有 backward 实现和 perf harness，但没有公开 backward speedup、完整 autograd 集成或端到端 training 结果。
4. TileGym 已公开实现、测试容差和 benchmark harness，但没有随仓库提供博客图对应的 raw result、方差、profiler 或独立复现收据。
5. 原博客的 `dt` 符号和 $h_t/h_{t-1}$ 索引存在文字不一致，本文按原论文与官方代码校正。
6. chunk 内 cumulative-difference 的数值稳定性与 Mamba-2 作者早期警告之间尚缺公开解释。
7. 只有 B300 数据，不能外推到 Hopper、Ampere、消费卡、多 GPU 或其他厂商硬件。
8. benchmark 对照是特定 Triton reference；不能外推为 cuTile 与 Triton 的通用胜负。

后续最值得追踪的三个问题：

- TileGym 何时公开 forward/backward 的 raw benchmark、误差分布与 profiler breakdown？
- 已公开 backward 在端到端训练中能否保持稳定，并把 kernel 级收益转成真实 step-time 收益？
- 同一 kernel 在 H100/A100 上能否保持优势，autotune 最优点是否发生结构性变化？

---

## 十、自测题

1. 为什么 SSD 可以同时保留线性序列复杂度和 Tensor Core 友好的矩阵乘？
2. `fwd_pass_state` 为什么仍有顺序循环，却不等于退回逐 token RNN？
3. `compute_out` 不把 `C@Bᵀ` 写回显存，会节省什么，又增加什么资源压力？
4. 为什么 $A<0,dt>0$ 比“dt 为负”更符合官方实现？
5. 1.82× kernel speedup 为什么不能直接解释成 1.82× 训练吞吐？
6. 如果要把该实现接入推理框架，prefill 与 decode 应如何路由？

---

## 参考资料

### 核心一手来源

1. NVIDIA Technical Blog, [Accelerating Mamba-2 with High-Performance Forward Pass Kernels in NVIDIA CUDA Tile](https://developer.nvidia.com/blog/accelerating-mamba-2-with-high-performance-forward-pass-kernels-in-nvidia-cuda-tile), 2026-10-19。
2. Tri Dao, Albert Gu, [Transformers are SSMs: Generalized Models and Efficient Algorithms Through Structured State Space Duality](https://arxiv.org/abs/2405.21060), ICML 2024。
3. `state-spaces/mamba`, [Mamba-2 implementation](https://github.com/state-spaces/mamba/tree/e9594ce1c732d97440f0332fdc43170a2294dbfa), 代码快照核验于 2026-10-21。
4. Tri Dao, [State Space Duality (Mamba-2) Part III — The Algorithm](https://tridao.me/blog/2024/mamba2-part3-algorithm), 2024-05-31。
5. Tri Dao, [State Space Duality (Mamba-2) Part IV — The Systems](https://tridao.me/blog/2024/mamba2-part4-systems), 2024-05-31。

### CUDA Tile / cuTile 官方资料

6. NVIDIA, [cuTile Python documentation](https://docs.nvidia.com/cuda/cutile-python/index.html)。
7. NVIDIA, [cuTile Execution Model](https://docs.nvidia.com/cuda/cutile-python/execution.html)。
8. NVIDIA, [cuTile Data Model](https://docs.nvidia.com/cuda/cutile-python/data.html)。
9. NVIDIA, [cuTile Quickstart](https://docs.nvidia.com/cuda/cutile-python/quickstart.html)。
10. NVIDIA, [cuTile Release Notes](https://docs.nvidia.com/cuda/cutile-python/generated/release_notes.html)。
11. NVIDIA Technical Blog, [Simplify GPU Programming with NVIDIA CUDA Tile in Python](https://developer.nvidia.com/blog/simplify-gpu-programming-with-nvidia-cuda-tile-in-python), 2025-12-04。
12. NVIDIA, [`TileGym@3a871364`](https://github.com/NVIDIA/TileGym/tree/3a871364f1fbd59ef30b1afcc5a79fc3634888ce), 公开主分支快照核验于 2026-10-21。
