---
title: "FlyDSL × PyTorch：把 GPU kernel 写进 Python 的 CuTe 式布局路线深度解析"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["FlyDSL", "PyTorch", "AMD", "ROCm", "MI355X", "kernel", "DSL", "MLIR", "Triton"]
related_concepts: ["GPU算子开发", "DSL与中间表示", "布局代数", "Inductor后端选择", "低精度GEMM"]
---

# FlyDSL × PyTorch：把 GPU kernel 写进 Python 的 CuTe 式布局路线深度解析

**研究对象**：PyTorch 官方博客《Accelerating PyTorch on AMD GPUs with FlyDSL》（2026-10-21，作者 Ebba Simpson），并交叉核对 AMD ROCm 官方博客《FlyDSL: Expert GPU Kernel Development with the Ease of Python》（2026-03-30）、`ROCm/FlyDSL` 开源仓库（README、架构指南、kernel authoring 指南、目录结构）、`ROCm/aotriton` 仓库元数据，以及 PyTorch/ROCm 的后端选择与编译接口材料。

> **标注约定**（全文通用）
> - `[官方自述]`：PyTorch / AMD 官方材料中可直接核对的陈述与数字，**均为厂商自测**。
> - `[代码证据]`：来自开源仓库文档与目录结构的事实（注明文件）。
> - `[分析者推断]` / `[推测]` / `[待验证]`：本报告作者的推理与未决疑点。
>
> **本报告最重要的一条结论先行**：FlyDSL 的技术命题不是"又一个 Python kernel DSL"，而是**"把 CUTLASS/CuTe 那套布局代数搬进 Python，并让它通过 PyTorch 现有的算子 API 自动生效"**。它带来的收益在算子级相当可观（BF16 dense GEMM 1.10×、MXFP8 1.58×、MXFP4 1.68×、grouped GEMM 对 Triton 1.20×、小 K TopK 4.82×），但**端到端只兑现了 1.13×（BF16）到 3.01×（MXFP4）**——**这个落差本身就是本报告最值得读的数字**。

---

## 开头三行：x → f → f(x)

- **x**：写 GPU kernel 的门槛一直由**编程模型**而非硬件决定。CUTLASS / CuTe DSL 给出了能逼近 roofline 的抽象，但它们是 **C++ 模板世界**：编译慢、迭代笨重、与编译器脆弱耦合、上手陡。Triton 用 Python 换来了生产力，但它的抽象层是**块级（block-level）**的——线程、wave、指令映射交给编译器，于是**某些架构专属的数据搬运与指令占有关键路径时，Triton 的抽象就挡路了**。AMD 明确把 FlyDSL 定位成**"Triton 的补充而非替代"**：**Triton 面向主流开发者的块级编程，FlyDSL 面向追求 roofline 性能或做编译器基础设施的专家的线程级与 IR 级控制**（`[官方自述]`，S02）。
- **f**：FlyDSL 的答案是**三层结构 + 一套数学**。三层是：**Python DSL 前端**（用 Python 写 kernel，控制流经 AST 变换转成 MLIR）→ **Fly dialect：一种一等公民的布局 IR**（`!fly.int_tuple` / `!fly.layout` / `!fly.coord_tensor` / `!fly.memref`，带组合/乘/除/分块代数与坐标映射算子）→ **FlyROCDL 与 MLIR→ROCDL→HSACO 的下降管线**。数学底座是 **CuTe 布局代数**（AMD 称其"形式化验证过的"）。落到 PyTorch 侧，它被包装成**可加的、可测量的后端**：eager 下 RMSNorm/TopK 自动分派，`torch.compile` 下 Inductor 把 FlyDSL 加入 GEMM 候选并**实测后选最快的**，注意力则经 **AOTriton** 在 FlyDSL / Triton / AITER ASM 之间按调优数据库派发。
- **f(x)**：接受 f 之后，得到的是一条**"专家写 kernel、普通人用算子"**的分工：FlyDSL 在多数已报告的算子用例中占优，但并非全面获胜（15 个 BF16 dense GEMM 形状为 **10 胜 / 3 平 / 2 负**，对"每个形状中更快的 ATen/Triton"取得 **1.10× 几何均值**；MXFP8 **1.58×**、MXFP4 **1.68×**；24 个 grouped GEMM 用例对 Triton **1.20×**、对 ATen **1.95×**；22 个 RMSNorm 用例 **1.17×–3.66×**；小 K TopK **4.82×**）；但端到端 vLLM 只兑现 **BF16 峰值 1.13×**（Llama-3.3-70B 多数测点处于 **1.79% 的实测噪声地板内**）、**MXFP8 1.04×–2.04×**、**MXFP4 1.25×–3.01×**。**算子级 1.6× 到端到端 1.13× 的落差，说明 kernel 优化的收益会被"算子在模型里占多少时间"这个比例摊薄**——这也正是官方自己写下的限制："These gains are most relevant when the supported operations account for a significant share of model runtime."（`[官方自述]`，S01）

---

## 一、一手来源清单与读法

| 编号 | 来源 | 类型 | 本报告用途 |
|---|---|---|---|
| S01 | PyTorch 官方博客《Accelerating PyTorch on AMD GPUs with FlyDSL》（2026-10-21） | 官方博客（主对象） | 集成方式、支持矩阵、全部性能数字与测量协议、What's Next |
| S02 | AMD ROCm 官方博客《FlyDSL: Expert GPU Kernel Development with the Ease of Python》（2026-03-30） | 官方博客 | FlyDSL 的设计动机、与 Triton/CK 的定位、CuTe 布局代数、构建方式、生产采用自述、路线图 |
| S03 | `ROCm/FlyDSL` 仓库 `README.md` | 一手代码仓文档 | 项目定位与分层、核心 IR 类型、仓库结构、示例、安装与构建前提 |
| S04 | `ROCm/FlyDSL` 仓库 `docs/architecture_guide.md` | 一手代码仓文档 | 编译器组件与阶段、Fly / FlyROCDL 方言结构、JIT 与 AOT 导出 |
| S05 | `ROCm/FlyDSL` 仓库 `docs/kernel_authoring_guide.md` | 一手代码仓文档 | kernel authoring 模型（`@flyc.kernel` / `@flyc.jit` / launch / 同步原语） |
| S06 | `ROCm/FlyDSL` 仓库目录树（`kernels/`、`docs/`、`python/flydsl/`） | 一手代码证据 | kernel 家族清单、文档谱系、仓库规模与维护信号 |
| S07 | `ROCm/aotriton` 仓库元数据 | 一手代码证据 | AOTriton 的定位与成熟度信号 |

**读法说明**：S01 是"**怎么接进 PyTorch**"，S02 是"**为什么这么设计**"，S03–S07 是"**到底长什么样**"。本报告把三者交叉使用：S01 的每个性能数字都回到 S02/S03–S07 的机制描述里找解释（例如"为什么 TopK 小 K 优势这么大"要回到 S01 的寄存器路径与 radix 路径设计）。

---

## 二、原文论证的重构

### 2.1 PyTorch 那篇在回答什么

`[官方自述]` S01 的定位句：**"PyTorch users on AMD MI350-series GPUs can now use FlyDSL through existing operator APIs … without requiring applications to call custom kernels."** 核心是三句话：

1. **不改变用户代码**——用户仍然调用 `torch.mm` / `F.scaled_mm` / `F.grouped_mm` / `F.rms_norm` / `torch.topk` / `F.scaled_dot_product_attention`；
2. **FlyDSL 是"可加的"（additive）后端**——"Unsupported workloads retain existing implementations"；
3. **性能由 PyTorch 自己来选**——不是让用户手选后端，而是**让 Inductor 与 AOTriton 各自做实测与调度**。

`[分析者推断]` 第三点是整篇文章的**架构要点**：它把"要不要用 FlyDSL"这个决定从用户手里拿走，交给框架。**这既降低了使用门槛，也把 FlyDSL 的收益变成了"框架能自动发现的那部分"**——因此**只有当 FlyDSL 覆盖的算子在该模型运行时间里占比足够高时，收益才会显现**（S01 自己写明这一点）。这也解释了后文端到端收益远小于算子级收益的现象。

### 2.2 AMD 那篇在回答什么（设计动机）

`[官方自述]` S02 列出 FlyDSL 要解决的三类长期需求：

1. **给 CUTLASS / CuTe DSL 用户一条迁移路径**：FlyDSL 保留 tile-based 与布局代数的设计模式，"migrate existing kernels with minimal redesign"。
2. **给模板密集的 HIP C++ 一个现代替代**：S02 直指 CK（Composable Kernel）的痛点——"long build times, slow iteration cycles, brittle compiler interactions, and steep onboarding requirements"，并给出对策：原生 Python DSL、**AST 变换把 Pythonic 控制流转成 MLIR**、JIT 友好的编译、清晰的 **MLIR → Fly → ROCDL → HSACO** 管线。
3. **用 CuTe 布局代数做统一数学基础**：S02 称 FlyDSL 引入了"**formally validated CuTe layout algebra**"，带来"跨 kernel 家族的一致表示、可预测的优化行为、跨 GPU 架构的可移植性"。

`[官方自述]` S02 同时给出定位边界："**Triton: block-level programming for mainstream developers; FlyDSL: thread-level and IR-level control for expert developers seeking roofline performance or working on compiler infrastructure**"，并强调"AMD and OpenAI actively collaborate on Triton"——**FlyDSL 是 AMD 自己生态里的补充层，不是对 Triton 的替代**。

### 2.3 两篇的分歧点

`[分析者推断]` S01 与 S02 的**措辞差异值得记录**：S02（2026-03）说 FlyDSL "already supports several essential AI operators … Softmax, LayerNorm/RMSNorm, Quantization, GEMM, MoE kernels"，并称"FlyDSL-based high-performance operators have entered early production adoption for **large-scale** inference workloads … operating at production hyperscale across MI GPU clusters"；而 S01（2026-10）给出的 PyTorch 侧支持矩阵要**窄得多**（Dense/MXFP/Grouped GEMM、RMSNorm、TopK、Attention），且**不包含 Softmax、Quantization、Conv**，也**不提供任何生产采用证据**。S02 还自称部分 FlyDSL 实现可达到与 CK 相当或更快的性能，但没有给出可独立复核的同条件对照。`[推测]` 这些差异可能来自"DSL 能力"与"PyTorch 集成面"的边界，而非能力倒退；`[待验证]`。

---

## 三、FlyDSL 是什么：用白话解释

### 3.1 三层结构

`[代码证据]` S03（README）："FlyDSL is the **Python front-end** of the project: a *Flexible Layout Python DSL* for expressing **tiling, partitioning, data movement, and kernel structure** at a high level."

`[代码证据]` S04（架构指南）给出组件表：

| 组件 | 作用 | 关键文件 |
|---|---|---|
| FlyDSL | Python DSL 前端，编写 GPU kernel | `python/flydsl/` |
| FlyDSL Compiler | **基于 trace 的 JIT 编译、specialization 与 C object 导出** | `python/flydsl/compiler/` |
| FlyDSL Expr | DSL 表达式算子（arith / vector / gpu / buffer / rocdl） | `python/flydsl/expr/` |
| **Fly Dialect** | **Flexible Layout IR**——带布局代数的 MLIR 方言 | `include/flydsl/Dialect/Fly/` |
| MlirCompiler | 端到端 MLIR pass 管线（DSL → 二进制） | `python/flydsl/compiler/jit_function.py` |
| CompiledArtifact | 可序列化的已编译 MLIR + 惰性 ExecutionEngine 状态 | `python/flydsl/compiler/jit_executor.py` |
| CompiledFunction | 可调用 specialization，支持 `export_to_c()` | `python/flydsl/compiler/jit_function.py` |

`[代码证据]` S03 列出核心 IR 类型：**`!fly.int_tuple`、`!fly.layout`、`!fly.coord_tensor`、`!fly.memref`**，以及代数算子"**composition / product / divide / partition** + coordinate mapping 算子"；另有 **FlyROCDL** 方言提供 **copy atom 与 MMA atom**。`[代码证据]` S03 还说明"**Embedded MLIR Python runtime (`_mlir`)：无需外部 `mlir` Python wheel**"。

`[分析者推断]` **白话解释这套结构**：传统写法里，"这个张量在内存里怎么排、哪根线程读第几行"是散落在代码里的临时变量；FlyDSL 把它提升为**一种可以被组合、被代数运算、被编译器推理的一等对象**。于是"把 A 按 M 切、按 N 切、按线程切"变成了对 layout 的**除法与组合运算**——**这正是 CuTe 布局代数的核心思想，只是现在写在 Python 里、并且有编译器在后面接着。**

### 3.2 编译与代码生成

`[官方自述]` S02："FlyDSL is powered by the Fly dialect: an end-to-end, **MLIR-native compiler stack** for GPU kernels. Its core is the `fly` dialect—a first-class layout IR with explicit algebra and coordinate mapping, plus a **composable lowering pipeline to GPU/ROCDL**."

`[官方自述]` S02 的编译流：**Python 源码 → AST 变换（把 Pythonic 控制流转成 MLIR）→ Fly 方言 → ROCDL → HSACO**。

`[代码证据]` S04 显示 Fly 方言在 TableGen 层的结构：`FlyOps.td`（`make_shape`、`crd2idx`、`composition` 等布局算子）、`FlyTypeDefs.td`（自定义类型）、`FlyInterfaces.td`（算子接口）、`Transforms/Passes.td` 与 `LayoutLowering.td`（布局下降 pass）；`FlyROCDL/IR/` 下有 `CopyAtom.td` 与 `MmaAtom.td`。

`[代码证据]` S03 的 Python 包结构显示 JIT 管线由 AST 重写器（`ast_rewriter.py`）、kernel 函数（`kernel_function.py`）、JIT 函数（`jit_function.py`）、后端目录（`backends/`）组成，并有 **`autotune.py`：Triton-style autotune 模块**。

`[分析者推断]` "**AST 重写 + 布局 IR + 可组合下降**"这套组合的代价是明确的：**它把编译错误的发现时机推后了**（Python 语义先被转成 MLIR，再由方言做类型推断与合法性检查），并且**要求用户理解 layout 概念才能写出好 kernel**。相比之下，Triton 的编程模型更"像 Python"，但抽象更低。

### 3.3 kernel authoring 模型（白话）

`[代码证据]` S05（kernel authoring 指南）给出两个装饰器与一套原语：

| 概念 | API | 说明 |
|---|---|---|
| JIT host 函数 | `@flyc.jit` | 发出宿主侧 launcher，JIT 编译 |
| GPU kernel | `@flyc.kernel` | 定义 GPU kernel 函数 |
| 发射 | `kernel(...).launch(grid=, block=)` | 配置并发出 GPU launch |
| 线程/块索引 | `fx.gpu.thread_idx.x` / `fx.gpu.block_idx.x` / `fx.gpu.block_dim.x` | 硬件级索引 |
| 编译期常量 | `fx.Constexpr[int]` | 参与特化与缓存键 |
| 张量参数 | `fx.Tensor` | 经 DLPack 传入 |
| Stream 参数 | `fx.Stream` | CUDA/HIP stream |
| 同步 | `fx.gpu.barrier()` | workgroup 同步 |
| 类型化常量 | `fx.Int32` / `fx.Int64` / `fx.Float32` | DSL 常量 |
| 编译期展开循环 | `range_constexpr(n)` | 静态展开 |
| Buffer 载入 | `buffer_ops.buffer_load(rsrc, off)` / `fx.rocdl.s_buffer_load(...)` | AMD buffer 载入原语 |

`[代码证据]` S02 给出的 vectorAdd 示例展示了完整的"布局代数 + copy atom + 寄存器运算"写法：`fx.logical_divide(A, fx.make_layout(block_dim, 1))` 把张量按 block 切分、`fx.slice` 取出某个 block、`fx.make_copy_atom(fx.UniversalCopy32b(), fx.Float32)` 构造 copy atom、`fx.memref_alloca` 在寄存器空间分配、`fx.copy_atom_call` 执行拷贝、`fx.arith.addf` 做寄存器向量运算。

`[分析者推断]` **这段示例本身就是"FlyDSL 学习曲线的真实写照"**：相比 Triton 的 `tl.load` / `tl.store`，这里的每一次数据移动都要显式选择 atom、显式决定 layout、显式管理寄存器生命周期。**"性能上限更高"与"上手更陡"是同一件事的两面。**

### 3.4 机制示意

```
  kernel 作者（Python）
  ┌───────────────────────────────────────────────────────────────┐
  │ @flyc.kernel  def kern(A,B,C, N: fx.Constexpr[int]):          │
  │   tA = fx.logical_divide(A, fx.make_layout(block_dim,1))        │
  │   tA = fx.slice(tA,(None,bid));  tA = fx.logical_divide(tA,…)   │
  │   rA = fx.memref_alloca(RegMemRef, fx.make_layout(1,1))          │
  │   fx.copy_atom_call(copyAtomBuffer, fx.slice(tA,(None,tid)), rA)  │
  │   vC = fx.arith.addf(fx.memref_load_vec(rA), fx.memref_load_vec(rB))│
  │ @flyc.jit    def host(...): kern(...).launch(grid=,block=,stream=)│
  └───────────────────────────┬───────────────────────────────────┘
                              │  AST 变换（Python 控制流 → MLIR）
                              ▼
  ┌───────────────────────────────────────────────────────────────┐
  │ Fly 方言（一等布局 IR）                                          │
  │  !fly.int_tuple / !fly.layout / !fly.coord_tensor / !fly.memref │
  │  代数：composition / product / divide / partition               │
  │  坐标映射：crd2idx 等                                          │
  │  FlyROCDL：copy atom / MMA atom                                │
  └───────────────────────────┬───────────────────────────────────┘
                              │  可组合下降：MLIR → ROCDL → HSACO
                              ▼
        可执行 kernel（可 export_to_c() 导出为可链接 C 对象）
        ├─ JIT 路径：特殊化 + 缓存（CompiledArtifact 可序列化）
        └─ AOT 路径：导出 C 对象供外部工程链接
```

---

## 四、PyTorch 集成：三条通路

`[官方自述]` S01 的 Figure 1 概括了三通路：

| 通路 | 机制 | 覆盖算子 |
|---|---|---|
| **Eager 自动分派** | "eligible RMSNorm and TopK calls dispatch to FlyDSL when the optional runtime is installed and enabled; **other calls retain ATen**" | RMSNorm、TopK |
| **`torch.compile`** | "TorchInductor **filters eligible Dense, Grouped, and MXFP GEMM candidates, benchmarks FlyDSL beside ATen and Triton where supported, caches the winner for each workload, and runs the fastest measured kernel**" | Dense GEMM、Grouped GEMM、MXFP scaled GEMM |
| **Attention（AOTriton）** | "`F.scaled_dot_product_attention` calls AOTriton, which now picks among **FlyDSL, Triton, and AITER ASM** kernels for each workload using its **offline operator-tuning database**" | SDPA（forward + backward） |

`[代码证据]` S07：`ROCm/aotriton` 描述为 "Ahead of Time (AOT) Triton Math Library"，MIT 许可，102 stars / 47 forks / **41 open issues**，创建 2023-10-17，最近推送 2026-10-22。

### 4.1 支持矩阵（`[官方自述]` S01 逐字）

| 操作 | 模式 | PyTorch API | 输入 dtype | 布局/形状 | 输出/选项 |
|---|---|---|---|---|---|
| Dense GEMM | Compile | `torch.mm` | FP16, BF16 | 静态 2D；NN/NT/TN/TT | 同 dtype |
| MXFP scaled GEMM | Compile | `F.scaled_mm` | MXFP8, MXFP4 | 静态 2D；A 行主序、B 列主序 | FP16/BF16；block scales |
| Grouped GEMM | Compile | `F.grouped_mm` | FP16, BF16 |  ragged 2D A；grouped 3D B | 不均匀/空 group |
| RMSNorm | Eager | `F.rms_norm` | FP16, BF16, FP32 | 连续；1-D norm 维度 | 仅前向 |
| TopK | Eager | `torch.topk` | FP32 | 连续；最后一维 | 最大值、已排序；functional / `out=` |
| Attention（经 AOTriton） | Eager, compile | `F.scaled_dot_product_attention` | FP16, BF16 | D 最内维；head dim 32–512 | 前向与反向 |

`[官方自述]` S01 补充的关键约束：
- **RMSNorm 的 backward 仍走 PyTorch 既有实现**（"continues through PyTorch's existing implementation"）；
- **MXFP** 要求 **K 为 128 的倍数**；**不支持 fast accumulation**；可选一维 bias（长度 N、dtype 与输出一致）；两种格式都用 FP32 累加、输出 FP16/BF16；缩放规格为 **每 32 个值共享一个 E8M0 scale（BlockWise1x32）**；
- **Inductor 的布局约束先于后端选择生效**：要求 A、B 沿 K 为 unit stride（行主序 A、列主序 B），不兼容时 Inductor 会插入一次 layout copy；
- **Attention 不支持 FP32**；FP32 输入与被调优库分配到别处的工作负载，仍走 AOTriton 的 Triton 或 AITER ASM；
- **`torch.nn.attention.flex_attention` 是另一条路**：Inductor 把它编译成自己的 Triton kernel，**不走 AOTriton**。

`[分析者推断]` 两条约束对使用者影响最大：**MXFP 的"插入 layout copy"**意味着一次"量化 GEMM"可能悄悄多出一次内存拷贝——**这会让 MXFP 的实际收益低于 kernel 级数字**；而 **flex_attention 走 Triton** 意味着 FlyDSL 目前**没有覆盖 FlexAttention 这条 increasingly 重要的路径**（S01 的 What's Next 也把"FlexAttention with FlyDSL"列为待做）。

### 4.2 为什么快：六类 kernel 分别在省什么（`[官方自述]` S01）

这些机制不是独立性能归因实验，而是 PyTorch 官方对实现的解释。它们共同回答一个问题：**FlyDSL 的线程级控制具体怎样把数据搬运、同步与矩阵计算叠在一起。**

| Kernel | 调度机制 | 白话解释 |
|---|---|---|
| **Dense GEMM** | full-tile 与 half-tile interleaved（HTI）两条路径；多级 K-tile 环形 LDS；两个四 wave 组用错相 barrier 交替做 MFMA 与异步预取 | 不等整块算完才换数据；一组 wave 计算时，另一组搬下一批数据，并以半块为单位复用 LDS |
| **MXFP GEMM** | A/B 按 K tile 推进，scale 放在跨多个 K tile 的独立 slot；chunk 边界预取下一组 scale；full-tile 路径则让 scale 与对应 K tile 共用 stage index | 让量化值与 E8M0 scale 的生命周期精确对齐，避免每个 tile 都重新装载整组缩放信息 |
| **Grouped GEMM** | persistent grid 沿所有 expert 的累计 tile offset 走 strided 序列，自动跳过空 expert；XCD-aware swizzle 分摊到 8 个 XCD，N-major fallback 复用 B tile | 不为每个 expert 单独 launch；同一批常驻 workgroup 跨 expert 接活，减少不均匀 token 分配造成的空转 |
| **RMSNorm** | 每行一个 CTA；128-bit 向量加载后把输入留在寄存器；先做 Wave64 shuffle 归约，再用小 LDS 合并各 wave partial；原值复用来写输出与 backward 所需 `rstd` | 一次把整行读进来，归约完成后直接复用，不再重复读显存 |
| **TopK** | 小 K 用寄存器内 bitonic + butterfly merge；大 K 用四轮 8-bit radix 找阈值，只收集幸存候选，再排序到下一 2 的幂 | K 很小时不把整行搬去全量排序；K 变大时先筛掉大多数元素，只排序可能入选的部分 |
| **Attention** | head dim ≤256 用 dual-wave 软件流水，把一个 KV tile 的 softmax VALU 与另一个 tile 的 QK/PV MFMA 重叠；head dim 512 在时间上经 LDS 分片、在 wave 间拆输出 accumulator；backward 复用 forward 的 lane map 与数据通路 | 同时占用标量/向量与矩阵单元；超宽 head 则分时分 wave，避免 272 KB 双 tile 需求撞上 160 KB LDS 上限 |

`[分析者推断]` 这张表也解释了 FlyDSL 与 Triton 的边界：收益不是来自“Python 比 Triton 快”，而是来自**作者能把 wave、LDS、寄存器、scale 与 MFMA 的所有权写进 kernel 本身**。能否兑现，仍取决于 shape、dtype、布局和该算子在端到端运行时中的占比。

---

## 五、性能数字逐口径核对

### 5.1 测量协议（官方明写）

`[官方自述]` S01 的测量协议是本报告认为**必须逐条引用**的部分：

- **硬件**：AMD Instinct MI355X（`gfx950`）；
- **三套不同的计时方式**：dense GEMM 用 **GPU-event 计时 graph replay**；grouped GEMM 报 **steady-state 吞吐**；RMSNorm 与 TopK 用 **GPU-event 计时重复算子调用**；
- **只测稳态算子执行，排除编译与初次 autotune**；
- **"they do not represent end-to-end model latency"**；
- **MXFP 测量从已量化操作数开始，输入量化不在计时区间内**；
- **>1.0 表示 FlyDSL 快于所指基线**；**几何均值对每个采样用例等权**；
- "Each figure and caption specifies its baseline and aggregation scope."

### 5.2 算子级数字

| 算子 | 套件 | 基线 | 结果 | 范围/细节 |
|---|---|---|---|---|
| Dense GEMM（BF16 NT） | **15 个形状** | 每个形状中**更快的** ATen/Triton | **1.10× 几何均值** | 10 胜 / 3 平 / 2 负（±1% 平局带）；`64×4096×4096` 提升 **1.33×**；两个最大方阵略偏 ATen |
| Dense GEMM（后续回归） | 同 15 形状 | 同上 | **1.12× 聚合** | 官方注明这是"later regression check of the current all-layout kernel"，且只发布了聚合结果，故 Figure 3 仍保留早期逐形状数据 |
| MXFP8 scaled GEMM（NT） | **17 个形状** | ATen | **1.58× 几何均值** | 范围 **1.31×–2.23×**，最大在 `32×4096×4096`；**所有报告用例均快于 ATen** |
| MXFP4 scaled GEMM（NT） | **17 个形状** | ATen | **1.68× 几何均值** | 范围 **1.31×–2.96×**，峰值在 `32×14336×4096` |
| Grouped GEMM（BF16） | **24 个用例** | Triton / ATen | **1.20× / 1.95× 几何均值** | 均匀组 14 例：**1.21× / 2.12×**，FlyDSL 在 14 例中 11 例最快；原文明写投影维度 **5 例**：**1.23× / 1.73×**；**ragged 5 例：1.15× / 1.73×，FlyDSL 全胜** |
| RMSNorm | **22 个用例** | ATen | **1.17×–3.66×** | 对齐维度约 **1.2×–1.5×**；**差一位**的维度（如 4097）可达 **3.66×**（某个 FP16 用例） |
| TopK（FP32） | 小 K={2,4,8,16} 的 **10 个用例** | ATen | **4.82×**（关闭确定性算法）/ **4.02×**（开启） | 更大 K 段 **1.40×–1.97×**；图注聚合**全部 33 个报告用例** |

`[分析者推断]` 三处必须点明的口径问题：
1. **Dense GEMM 的基线是"逐形状取更快者"**——这是一个**保守基线**，让 1.10× 更有说服力；但同时也意味着**"FlyDSL 比 ATen 快多少"这个问题在此套件上没有答案**。
2. **MXFP 的 1.58×/1.68× 是对 ATen（hipBLASLt）**，而 ATen 在低精度上的实现是否已是该格式的最优实现，原文未讨论。
3. **RMSNorm 的 3.66× 出现在"差一位"的形状上**，官方自己提醒"3.66x applies to a particular FP16 case"。**把它当作 RMSNorm 的典型加速是误读。**

### 5.3 Attention 的数字是"版本对比"，不是"FlyDSL 对 Triton"

`[官方自述]` S01：**AOTriton 0.14.2b 相对 0.13b** 在 `gfx950` 上，**forward 0.92×–2.34×、backward 0.93×–2.47×**（跨 head dim 与 causal 模式）。官方明确加注："**This release-to-release comparison also includes updated Triton, AITER, and tuning databases, so it is not an isolated FlyDSL-versus-Triton measurement.**"

`[分析者推断]` **这是全文最容易被误读的一处**：读者极易把 "2.34×" 读成"FlyDSL 比 Triton 快 2.34×"。实际上它衡量的是**两个 AOTriton 版本的整体差异**，其中混入了 Triton 更新、AITER ASM 更新与调优数据库更新。**要回答"FlyDSL 的 attention kernel 到底比 Triton 快多少"，这篇官方文没有给数据。**

### 5.4 端到端 vLLM（A/B）

`[官方自述]` S01 的端到端协议：

- **工具**：`vllm bench serve`；**硬件**：1 张 MI355X（**TP=1**）；**模型**：Llama-3.1-8B-Instruct、Qwen3-32B、Llama-3.3-70B-Instruct；
- **请求**：256 token 输入、固定 512 token 输出；**并发 8–256**；
- **基线与处理组使用相同的 serving 配置与 per-model KV cache**，**只有 Inductor 的 GEMM 候选列表不同**；指标是 **whole-request speedup**。

| 精度 | 基线 | 结果 | 测量强度 |
|---|---|---|---|
| **BF16** | ATen + Triton | Llama-3.1-8B 峰值 **1.13×**；Qwen3-32B 峰值 **1.06×**；**Llama-3.3-70B 多数测点处于 1.79% 的实测噪声地板内** | 报告"至少两次 ABBA 交错重复的中位数" |
| **MXFP8 (A8W8)** | **ATen (hipBLASLt)** | 18 个"模型×并发"组合**全部改善**：Qwen3-32B **1.40×–2.03×**、Llama-3.1-8B **1.04×–1.92×**、Llama-3.3-70B **1.38×–2.04×** | **每格仅 1 次测量** |
| **MXFP4 (A4W4)** | ATen (hipBLASLt)，**`lm_head` 保持未量化** | 18 个组合**全部改善**：Qwen3-32B **1.53×–3.01×**、Llama-3.1-8B **1.25×–1.85×**、Llama-3.3-70B **1.50×–2.82×** | **每格仅 1 次测量**，官方明说"small differences should not be treated as variance-qualified results" |

`[分析者推断]` **BF16 的端到端结果最诚实也最说明问题**：8B 模型峰值 1.13×、32B 峰值 1.06×、**70B 多数测点处于噪声地板内**。这与"算子级 1.10×"是一致的——**GEMM 在整模型时间里占比有限**，所以算子级优势几乎原样折算成端到端优势。**真正的量级差异出现在低精度路径（MXFP8/MXFP4），但那里的对照基线只有 ATen（hipBLASLt），而且每格只测一次。**

### 5.5 口径缺口清单

| 缺口 | 影响 |
|---|---|
| **Attention 没有 FlyDSL-vs-Triton 的隔离对比** | 无法回答 FlyDSL attention kernel 的真实优势 |
| **MXFP 端到端每格仅 1 次测量** | 官方自陈"不应视为方差合格的结果" |
| **BF16 端到端仅 2 次 ABBA 交错重复取中位数** | 统计强度有限；70B 已落到噪声地板 |
| **端到端只覆盖 3 个模型、单卡 TP=1、256 输入 / 512 输出** | 与真实 agent 负载（长输入、变长、多并发）差距大 |
| **无训练侧数字** | 完全没有训练吞吐/步时间；AMD 博客的"production adoption"是自述 |
| **无 MFU、无显存占用数据** | 无法判断 kernel 优化是否以显存为代价 |
| **无跨硬件数据** | 全部在 gfx950（MI350 系列）；RDNA4 只有 attention kernel |
| **无与 CK/AITER 的直接对比** | 只有 "ATen (hipBLASLt)" 与 Triton |
| **GEMM epilogue fusion 与更广的 backward 覆盖尚未支持** | 官方列为待做，直接限制了可优化算子的范围 |
| **Dense GEMM 的"更快原始基线"不明确是 ATen 还是 Triton** | 1.10× 的分母只能理解为逐形状取快者 |

### 5.6 官方自述 vs 可核对

| 主张 | 类型 | 核对结论 |
|---|---|---|
| "FlyDSL 已接入 PyTorch，可通过现有算子 API 使用" | 官方 + 代码 | **可核对**：仓库 `kernels/` 目录含 `attention`、`comm`、`conv`、`gemm`、`mega_moe`、`mega_moe_tp`、`moe`、`monokernel`、`norm`（S06） |
| "FlyDSL 是 Python 前端 + Fly 布局 IR + MLIR→ROCDL 管线" | 官方 + 代码 | **可核对**：S03/S04 的组件表与方言结构 |
| "Inductor 会实测并缓存每个负载的胜者" | 官方 | **机制陈述**，未读到实现代码 |
| "AOTriton 用离线算子调优数据库在 FlyDSL/Triton/AITER ASM 间派发" | 官方 | **机制陈述**；`ROCm/aotriton` 仓库存在且 MIT（102 stars / 41 open issues） |
| "1.10×–4.82× 算子级加速" | 官方自测 | **口径清楚**（GPU 型号、shape 数、基线、几何均值、测量方式）；**但未独立复现**，且 attention 项为版本对比 |
| "端到端 1.13× / 2.04× / 3.01×" | 官方自测 | **协议清楚**（模型、并发、输入输出长度、候选列表差异）；**MXFP 路径每格仅 1 次测量** |
| "FlyDSL operators 已进入大规模推理生产采用" | **AMD 自述** | **无证据**：无客户名、无部署规模、无数字；S01 未复述 |
| "Triton 与 FlyDSL 互补而非替代" | AMD 自述 | 与 PyTorch 官方文"多后端可选"的机制一致 |
| "MI450 Series 的支持在路线图上" | 官方 | 路线图陈述 |

---

## 六、与替代路线的有边界比较

`[分析者推断]` 本章不含同条件实测，比较基于各方案公开的抽象层、官方定位与本报告读到的材料。

| 路线 | 抽象层 | 优势 | 劣势 | 有边界的适用区间 |
|---|---|---|---|---|
| **A. FlyDSL** | **线程级 + IR 级 + 显式布局代数** | 布局代数带来可推理的 tile/分区表达；CuTe 生态迁移路径；MLIR 原生管线可组合下降；能显式表达 copy atom / MMA atom / LDS swizzle / 同步边界 | 学习曲线陡（需懂 layout）；构建需从源码编译 LLVM/MLIR；**许可字段为 NOASSERTION**；**140 个 open issue**；目前仅 gfx950 | 需要逼近 roofline 的少数关键算子、架构专属数据搬运、编译器基础设施工作 |
| **B. Triton** | 块级（编译器管线程/wave/指令映射） | 生产力高、生态广、**Inductor 原生后端**、社区熟悉 | 抽象边界挡路（AMD 明说 FlyDSL 的价值在"Triton's abstraction boundary 之外"） | 绝大多数算子开发 |
| **C. Composable Kernel (CK)** | C++ 模板 | 极致性能、AMD 生态原生 | 编译慢、迭代笨重、模板脆弱、陡峭上手（AMD 自述） | 已有 CK 资产的团队、可接受长编译周期 |
| **D. HIP / CUDA C++** | 完全手写 | 完全控制、无抽象税 | 全部成本自己承担 | 极特殊算子、需要非标准指令序列 |
| **E. CUTLASS / CuTe DSL** | C++ 模板 + 布局代数 | 数学基础成熟、AMD 与 NVIDIA 双生态、FlashInfer/FlashAttention 等大量项目已用它 | C++ 模板的构建与迭代成本 | 有既有 CuTe 资产、且愿意留在 C++ 模板世界 |
| **F. TileLang / MLIR 系其它 DSL** | 声明式 tile + MLIR | 介于 Triton 与 FlyDSL 之间 | 各家生态与成熟度不一；AMD 博客把 TileLang 列为 FlyDSL 的"受益方"之一（其 CuTe DSL 后端） | 需要 tile 级抽象但不想碰 Triton 限制时 |

`[分析者推断]` **FlyDSL 在这张表里的独特位置**：它是**唯一一个把"布局代数"和"Python 生产力"这两件事同时做到位、并且已经接入 PyTorch 主流算子路径**的方案。B 更易用但抽象更低；C/E 性能等价但开发成本高；F 生态尚在形成。**代价是它目前只服务 AMD 一家的硬件抽象，且成熟度指标（140 open issue、NOASSERTION 许可、需自建 LLVM）都指向"早期但真实"的状态。**

---

## 七、可移植性、维护成本与成熟度

### 7.1 可移植性

`[官方自述]` S01：支持目标为 **AMD MI350-series（`gfx950`）**；"AOTriton also ships FlyDSL attention kernels for **RDNA4 (`gfx1201`)**"；What's Next 提到扩展到 **AMD Instinct MI450 Series**。

`[官方自述]` S02 声称 CuTe 布局代数带来"**Portability across GPU architectures**"。

`[分析者推断]` **"可移植性"需要拆成两层**：**(1) DSL 层的可移植性**——同一份 kernel 源码能否换架构重编译？S01 给出的答案是"目前只有 gfx950 目标 + RDNA4 的 attention kernel + MI450 在路线图上"，**因此今天的实际可移植性接近于零**；**(2) 抽象层的可移植性**——布局代数是一种**架构中立的表达方式**，这为未来的多架构支持留下了接口。**S02 的"portability"更接近后者，是设计主张而非当前能力。**

### 7.2 维护成本

`[代码证据]` S03（README）：从源码构建需要 **cmake ≥3.20、C++17 编译器、nanobind/numpy/pybind11**，且要先跑 `scripts/build_llvm.sh` **从源码构建 LLVM/MLIR**（含 `thirdparty/llvm-extensions`），再 `scripts/build.sh` 构建 FlyDSL。`[代码证据]` S03 还说明 Python 包**自带 MLIR Python 绑定**，用户无需外部 `mlir` wheel；文档站提供 `.readthedocs.yaml` 与 Sphinx 配置。

`[代码证据]` S06：仓库 `ROCm/FlyDSL` **302 stars / 131 forks / 140 open issues**，创建 2025-11-23，最近推送 2026-10-24，**许可字段为 NOASSERTION**（非标准 SPDX 标识）。

`[分析者推断]` **"140 个 open issue"需要两面看**：对一个月活跃、公开开发的项目是**健康的社区信号**；对一个要进生产的关键路径依赖，则是**响应能力的风险**。**"许可字段 NOASSERTION"更值得注意**——它意味着仓库使用自定义或复合许可，**合规团队必须单独确认条款**。相比之下 `ROCm/aotriton` 是标准 MIT。

### 7.3 成熟度

`[官方自述]` S01 的 What's Next 明确列出了**尚未完成**的部分，构成本报告判断成熟度的最佳依据：

- 扩展到 **MI450 Series**；
- 增加 **MXFP8 grouped GEMM** 与更多 attention 工作负载；
- **把 AOTriton 的 attention kernel 移入 FlyDSL 的 `kernels/attention/`**（当前是 vendored 副本，"让 AOTriton 从上游构建而不是用 vendored 副本"）；
- **FlexAttention 的 FlyDSL 后端**（当前 Inductor 编译成自己的 Triton kernel）；
- **GEMM epilogue fusion 与更广的 backward 覆盖**；
- **AOTInductor 支持**与更多端到端模型 benchmark。

`[分析者推断]` **这六项里有四项直接限制了当前可用范围**（FlexAttention、epilogue fusion、backward 覆盖、AOTInductor），**一项是代码重复的技术债**（attention kernel 的 vendored 副本）。**因此"FlyDSL 已经进入生产"（S02 的措辞）与"PyTorch 集成仍在补齐"（S01 的措辞）是可以同时为真的**——前者指 AMD 内部直接用 FlyDSL 写算子，后者指 PyTorch 侧的通用集成。

### 7.4 TopK 的确定性：一个可复现性的真实缺口

`[官方自述]` S01 的 TopK 段落给出了一个容易被跳过的细节："determinism on"指 `torch.use_deterministic_algorithms(True)`；radix 路径此时用 **prefix-sum slots** 保留有限值的 tie 顺序，关闭时用 **atomic slot allocation**，**因此相等值的索引可能变化**；寄存器 kernel 本身在两种模式下都可复现，**但其 tie 顺序可能与 ATen 不同**；**NaN 被规范化到同一个 ordinal，因此即使在确定性模式下，精确的 NaN payload 与索引选择也可能与 ATen 不同**。

`[分析者推断]` **这是本报告找到的唯一一处"语义级不一致"**（其余是性能差异）。它意味着：**不能假设"切到 FlyDSL 后 TopK 的输出与 ATen 逐位一致"**，即便是 deterministic 模式；对依赖精确索引的确定性测试、缓存键或差分测试，这是一个真实的破口。

---

## 八、对推理/训练 kernel 开发的现实意义

`[分析者推断]` 本节面向真正要写 kernel 或选型的人。

1. **先问"这个算子在我的模型里占多少时间"。** `[锚点 S01]` 官方自陈"这些收益在**被支持的操作占据模型运行时间的显著份额**时才最相关"；端到端数据也印证了这一点（BF16 70B 落在噪声地板内）。**FlyDSL 不是"让模型变快"的开关，而是"让你能把优化精力放在少数关键算子上"的工具。**
2. **低精度是 FlyDSL 当前最确定的价值区间。** `[锚点 §5.4]` MXFP8/MXFP4 端到端 1.04×–3.01×，而 BF16 只有 1.06×–1.13×。**若你的服务已经在 MXFP8/MXFP4 路径上，FlyDSL 的接入几乎是白捡的；若还在 BF16，先算清楚 GEMM 占比再决定。**
3. **低精度路径要额外算一次 layout copy 的成本。** `[锚点 S01]` MXFP 受 Inductor 的 K 方向 unit-stride 约束，不兼容时插入 layout copy。**"kernel 快 1.68×"与"端到端快多少"之间，差的可能就是这一次拷贝。**
4. **FlyDSL 的学习投入应按"关键算子数量"摊销。** 若你只需要 1–2 个算子达到 roofline，**用 C++/CK 手写可能更划算**（编译慢但一次到位，且无学习成本）；若你要维护一个算子库、或要给多个模型提供同一批优化算子，**FlyDSL 的 JIT 迭代速度与 Python 生产力才开始摊销**。
5. **attention 路径要特别小心。** `[锚点 §5.3]` 官方的 2.34×/2.47× 是版本对比而非 FlyDSL-vs-Triton 隔离对比；且 **FlexAttention 走 Triton、attention kernel 当前是 vendored 副本**。**把 attention 的期望建立在官方数字上是不安全的。**
6. **TopK 之类的选择类算子要单独做数值回归。** `[锚点 §7.4]` tie 顺序与 NaN 选择可能与 ATen 不同。**若你的模型或 eval 依赖精确索引，这是要先验证的点。**
7. **如果你在做的是"给 Agent 写推理栈"，FlyDSL 提示了一条更通用的路线**：**不要自己维护一份推理实现，而是想办法让优化过的 kernel 落进框架已有的分派路径**（Inductor 候选列表、AOTriton 调优库），让收益自动覆盖所有走该 API 的模型。**这是本文档里最可迁移的一条工程判断。**

---

## 九、Limitations（本研究自身的边界）

1. **未编写、未编译、未运行任何 FlyDSL kernel，未在 MI355X 上测量，未复现任何官方 benchmark。** 全部结论为来源转述与文档/仓库阅读所得。
2. **两篇官方文均已读至结尾**（S01 的 What's Next 与 Conclusion、S02 的 Summary 与路线图），但**正文中的多张图（编译流示意、HTI wave 视图、HTI 缓冲、各算子加速条形图、AOTriton 吞吐、vLLM 端到端曲线）的图内数值未取到**，因此本报告只引用正文与图注中可核对的数字。
3. **未读 FlyDSL 源码实现**（`python/flydsl/`、`lib/`、`include/` 的具体算子与 pass），只读了 README、架构指南、kernel authoring 指南与目录树；**对布局代数如何具体落到 MFMA/Copy atom 的理解是从文档与示例推断的**。
4. **未读** `docs/` 中的 `layout_system_guide.md`、`cute_layout_algebra_guide.md`、`autotune_guide.md`、`kernel_tuning_guide.md`、`ktrace_guide.md`、`prebuilt_kernels_guide.md`、`testing_benchmarking_guide.md`、`api_stability.md`、`extern_integration_guide.md`、`extension/`、`tutorials/`、`language/`，也未读 `examples/`、`tests/`、`tools/`；**因此对 autotune 空间、API 稳定性承诺与扩展机制的判断不完整**。
5. **未验证** S02 的"生产采用"自述、"formally validated CuTe layout algebra"的说法、以及 AMD 博客引用的文献 [1]；**未核实 `torch.compile` 的候选列表与 AOTriton 调优库的实现**。
6. **未做与 CK / AITER / Triton 的同条件实测**，第六章是有边界的定性比较，**不构成性能排名**；且本次报告的所有性能数字均为 PyTorch 官方自测。§4.2 的 kernel 调度解释同样来自官方实现说明，没有硬件计数器或消融证明某一项机制独立贡献了多少加速。
7. **未检索社区复现、issue 讨论或第三方 benchmark**；仅读取了仓库 issue 计数（140）与 `ROCm/aotriton` 的计数（41），**未读取 issue 内容**。
8. **未核实许可**：仓库许可字段为 NOASSERTION，本报告**未读取 LICENSE 原文**，因此不对其具体条款作判断。
9. **未核对 "AMD and OpenAI actively collaborate on Triton" 这一关系的当前状态**，也未评估若 Triton 上游吸收类似能力会如何影响 FlyDSL 的定位。
10. **资料时点**：网络读取发生于 2026-10-25（UTC 18:39–19:05 左右）；PyTorch 官方文 publishedTime 为 2026-10-21T17:45:40Z，AMD 官方文为 2026-03-30，`ROCm/FlyDSL` 最近推送 2026-10-24。

---

## 十、思考与追问

### 10.1 我真正理解了什么

- **FlyDSL 的真正命题不是"Python 写 kernel"，而是"把布局代数变成编译器可推理的一等公民"。** 传统 C++ 模板世界里的 layout 是编译器内部的东西；FlyDSL 把它提升成 `!fly.layout` 这种**可以被组合、可以被除法、可以被坐标映射**的显式对象，于是"怎么切 tile"从**手写索引算术**变成**对布局做代数**。**这才是它能同时给出高精度与高可读性的原因。**
- **"多后端可选 + 框架自动实测选择"比"更快的一个后端"更有价值。** `[锚点 S01]` Inductor 会把 FlyDSL 与 ATen、Triton 放在一起实测并缓存胜者，AOTriton 会按调优库在三种实现间派发。**这意味着 FlyDSL 的失败模式是"不被选中"，而不是"让用户跑不起来"**——**这是一条极其安全的接入路径，也是它在两次官方发布之间能快速铺开的原因。**
- **算子级 1.6× 与端到端 1.13× 的落差不是失败，而是正确预期。** `[锚点 §5.2/§5.4]` GEMM 在端到端里的占比有限；而真正量级差异出现在 MXFP8/MXFP4 路径。**"换后端能快多少"这个问题，必须先问"这个算子占多少时间"。**
- **AMD 与 PyTorch 的两份材料共同拼出了一条路线图**：**AMD 说"专家用 FlyDSL 写专家算子"，PyTorch 说"普通用户走现有 API 就用上了"**。**这是一条分工清晰、风险极低的异构生态路径**——比"让用户改代码换硬件"务实得多。

### 10.2 我还没搞懂什么

- **Attention 上 FlyDSL 到底比 Triton 快多少？** 官方只给了版本间对比（0.92×–2.47×）。**这是最大的数据空白。**
- **MXFP 端到端每格只测一次**，1.04×–3.01× 的分布里有多少是噪声？**官方自己提示不要当方差合格的结果。**
- **"backward 覆盖尚未广泛支持"对训练意味着什么？** 若 RMSNorm backward 仍走 ATen、其余 backward 未覆盖，**训练侧的收益可能远小于推理侧**——而官方完全没给训练数字。
- **autotune 空间有多大、成本多高？** S03 提到"Triton-style autotune module"，但 `[待验证]` 其搜索空间、缓存策略与首次调优耗时都未读到。**这直接决定了"第一次调用要等多久"。**
- **140 个 open issue 里有多少是阻塞性的？** 未读内容，无法判断响应能力。
- **许可证 NOASSERTION 的具体条款**：对商业使用的影响未评估。
- **如果 Triton 上游吸收了更细的抽象（AMD 博客已提到 Triton Linear layouts 与 FlyDSL 互补），FlyDSL 的定位会不会被挤压？**

### 10.3 下一步读什么或做什么

1. 读 `docs/layout_system_guide.md` 与 `docs/cute_layout_algebra_guide.md`，把"布局代数"从概念变成可复述的数学；再读 `docs/autotune_guide.md` 与 `docs/kernel_tuning_guide.md`，弄清调优空间与首次成本。
2. 读 `docs/api_stability.md` 与 `docs/prebuilt_kernels_guide.md`，判断这套 API 对生产依赖的承诺程度；读 `docs/testing_benchmarking_guide.md` 看**官方自己如何定义 benchmark 口径**——这是可直接借鉴到本仓库 eval 规范的部分。
3. 读 `ROCm/aotriton` 的调优数据库格式与 SDPA 派发逻辑，**回答"FlyDSL attention 相对 Triton 到底快多少"**这个官方没答的问题。
4. 读 `ROCm/FlyDSL` 的 LICENSE 原文，确认 NOASSERTION 对应的实际许可条款。
5. 在自有 MI300/MI350 机器上做一次最小实验：选一个自己模型里占比最高的算子（GEMM 或 norm），用 PyTorch 的 `torch.compile` 打开 FlyDSL 候选，**同时记录 kernel 级与端到端两组数字**——**用自己负载的"算子占比 × 加速"去预测端到端收益**，这是本文档最缺的一次自测。

---

## 附：来源清单（可复核）

- S01 https://pytorch.org/blog/accelerating-pytorch-on-amd-gpus-with-flydsl （PyTorch 官方博客，2026-10-21，Ebba Simpson）
- S02 https://rocm.blogs.amd.com/software-tools-optimization/flydsl-python-native/README.html （AMD ROCm 官方博客，2026-03-30）
- S03 https://github.com/ROCm/FlyDSL/blob/main/README.md （仓库 README：分层、IR 类型、仓库结构、构建）
- S04 https://github.com/ROCm/FlyDSL/blob/main/docs/architecture_guide.md （架构与编译管线指南）
- S05 https://github.com/ROCm/FlyDSL/blob/main/docs/kernel_authoring_guide.md （kernel authoring 指南）
- S06 https://github.com/ROCm/FlyDSL （仓库元数据与目录树，GitHub API 读取于 2026-10-25）
- S07 https://github.com/ROCm/aotriton （AOTriton 仓库元数据，GitHub API 读取于 2026-10-25）
