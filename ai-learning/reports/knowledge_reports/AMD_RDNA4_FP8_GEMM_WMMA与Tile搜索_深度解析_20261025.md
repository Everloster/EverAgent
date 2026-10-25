---
title: "AMD RDNA 4 FP8 GEMM：WMMA、LDS 预算与 Tile 搜索"
domain: "ai-learning"
report_type: "概念深度解析"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["RDNA4", "FP8", "GEMM", "WMMA", "LDS", "hipBLASLt", "kernel-tuning"]
---

# AMD RDNA 4 FP8 GEMM：WMMA、LDS 预算与 Tile 搜索

## 一句话结论

在 AMD gfx1201 上，把 FP16 GEMM 直接改为 FP8 WMMA，只能获得数据宽度翻倍和 LDS 占用减半的起点；真正的收益来自同步重设输出 Tile、K 深度、Wave 划分与预取，使缩小的操作数能换来更大 Tile 或更深 K，同时控制累加器与寄存器压力。

## 来源与证据等级

- [AMD ROCm 官方技术博客](https://rocm.blogs.amd.com/software-tools-optimization/rdna-fp8-gemm/README.html)
- [官方示例代码目录](https://github.com/ROCm/rocm-blogs/tree/release/blogs/software-tools-optimization/rdna-fp8-gemm/src)
- [RDNA4 dense WMMA builtins 官方参考](https://rocm-handbook.amd.com/projects/amd-rocm-optimization-guide/en/latest/compiler-builtins/rdna/rdna4-dense-wmma-builtins.html)

- **A 级——官方文档与代码事实：**依据 RDNA 4 dense WMMA builtins reference 及示例代码，E4M3 每个元素占 1 字节；WMMA builtin 接收两个 packed 32-bit 操作数并输出 FP32 累加结果。代码还明确给出 `int [[clang::ext_vector_type(2)]]` 的 fragment 声明。
- **B 级——厂商/作者平台自测：**原文在 gfx1201、ROCm 10.0 环境下给出四种配置的 Tile、Wave、LDS、fold 步数及编译器资源报告。这些数字来自原作者环境，不等同于独立复现。
- **代码核查入口：**原文称配套仓库包含完整实现；本文仅依据所给节选确认上述 API、类型和资源配置。
- **论文证据：**节选没有引用相关论文，也没有第三方实验复现。因而结构与 API 结论可信度较高，而通用性、性能排序及最优性不能由本文外推。

## 一、从 FP16 直接换类型为什么不够

“直接换类型不够”指的是**没有充分释放资源潜力**，并非转换后无法正确执行。FP16 每个操作数元素占 2 字节，而 E4M3 FP8 只占 1 字节，因此一次 128-bit load 可搬运 16 个 FP8 值，而不是 8 个 FP16 值；`elems_per_b128` 从 8 增至 16，所有 LDS 尺寸和搬运次数都应随之重算。

但如果只把元素类型和 builtin 换掉，原来的 16×16 WMMA Tile、`block_k`、Wave 划分和调度仍保持不变，那么节省下来的 LDS 空间不会被主动用于扩大输出 Tile 或增加 K 深度。原文的 Config 1 正是这种“只换类型”的基线：其 FP8 操作数切片只需 17.5 KB，在 64 KB LDS 预算下仍留下 46.5 KB。因而，FP8 指令提供的是重新组织 Tile 的必要条件，而不是自动完成重新组织。

## 二、FP8 WMMA 到底改变了什么

在指令层面，核心调用为：

```cpp
__builtin_amdgcn_wmma_f32_16x16x16_fp8_fp8_w32_gfx12(a, b, acc);
```

其变化可明确拆成四点：

1. **操作数类型：**A、B 均为 E4M3 FP8，每元素 1 字节。
2. **Fragment 布局：**每个操作数 fragment 仍覆盖每 lane 的 8 个 K 值，但由 8×1 字节组成，即**每 lane 8 字节**；它使用**两个 packed 32-bit word**，每个 word 装 4 个 FP8 值，共占两个 32-bit 寄存器。builtin 接收的是两个 packed 32-bit 整数，而不是 FP8 vector。数据仍通过一次 8 字节 `__builtin_memcpy` 从 LDS 指针装入。
3. **累加类型：**累加器固定为 **FP32**，没有 FP16 accumulator 变体。每 lane 保存 8 个 FP32 值，即 32 字节；输出 `C` 为 `float`，采用与 hipBLASLt 一致的列主序和 leading dimension M。
4. **没有 scale factor：**内核直接处理原始 E4M3 值，WMMA 内部完成乘法并以 FP32 累加；操作前后均未应用 per-tensor 或 per-row scale。生产量化推理通常需要 scale，该内核只是后续带缩放内核的基础。

## 三、四种 Tile/K/Wave 配置

### Config 1：直接移植，128×96，K=64

输出 Tile 为 128×96，`block_k=64`，即一次 LDS 填充支持 4 个 K=16 的 WMMA 步骤；Wave 网格为 2×2，共 4 个 wave、128 线程，仅使用一个 LDS buffer。每 wave 负责 4×3 个 WMMA Tile，共 12 个 tile 级累加器。

计入 `block_k+lds_pad=64+16=80` 的行跨度后，FP8 的 A、B 切片分别为 `128×80×1 B` 和 `96×80×1 B`，原文合计 **17.5 KB**。
**算术疑点待核：**原表同时把 FP16 的两片尺寸列为 `128×80×2 B`、`96×80×2 B`，却将 LDS 写作 **63 KB**；按同表两片尺寸直接相加会得到 35,840 B，无法与 63 KB 对齐。原文未解释额外缓冲或统计口径，因此这里保留 63 KB 原值并明确标为待核，不自行修正；后续预算判断采用原文另列的 FP8 17.5 KB。

### Config 2：扩大 Tile，256×256，K=64

该配置仍保持 `block_k=64`，但把输出 Tile 扩为 256×256。Wave 网格变为 4×4，共 16 个 wave；每 wave 覆盖 64×64 象限，即 4×4 个 WMMA Tile，携带 16 个 tile 级累加器。FP8 操作数切片合计 **40 KB**，可放入 64 KB LDS。相比 Config 1，fold 从 48 步增至 64 步（4 个 K slice×每 wave 16 个 Tile），作者的判断是每次 LDS 填充可摊薄更多 WMMA 工作和 barrier。

### Config 3：加深 K，256×160，K=128

输出 Tile 为 256×160，`block_k=128`，一次容纳 8 个 K=16 的 WMMA 步骤。Wave 网格采用 4×2，共 8 个 wave、256 线程；每 wave 为 4×5 个 WMMA Tile，携带 20 个 tile 级累加器，fold 为 160 步。

A、B 切片分别为 `256×144×1 B` 和 `160×144×1 B`，即 36,864 B 与 23,040 B，合计 **58.5 KB**。预取需 8+5=13 个 chunk，每两步发出一个，到第 26 步全部发出，满足 `2×chunks≤steps`。未采用 4×4 Wave 网格，是因为 160 列除以 4 后每 wave 为 40 列，即 2.5 个 WMMA Tile，不能整除。

### Config 4：方形 Tile，192×192，K=128

Config 4 保持 K=128，采用 192×192 输出 Tile 和 2×4 Wave 网格，共 8 个 wave、256 线程。每 wave 覆盖 96×48，即 6×3 个 WMMA Tile，携带 18 个 tile 级累加器；fold 为 144 步，需 6+6=12 个预取 chunk，满足 `2×chunks≤steps`。

A、B 切片均为 `192×144×1 B`，合计 **54.0 KB**，比 Config 3 少 4.5 KB。作者的编译器资源报告给出 Config 4 为 210 VGPR、Config 3 为 235 VGPR。由此可区分两类权衡：Config 3 用更高 LDS 和更多 tile 级累加器换取更深 K、更多每-wave 工作；Config 4 则以较少 LDS 和 VGPR 换取略低的每-wave Tile 数。原文仅说明 Config 4 来自手工 Tile/Wave 搜索，不能据此认定它是所有形状的全局最优配置。

## 四、四组Transformer GEMM Benchmark

以下为原文作者在 AMD Radeon™ RX 9070 XT 上完成的厂商实测，并非第三方复现结果。四组 shape 均取 K=8192，对应 70B 级模型的隐藏维度：M=N=8192 模拟注意力输出投影；M=8192、N=28672 模拟 MLP up-projection；M=8192、N=10240 模拟 GQA QKV projection；M=3072、N=4096 为较小的非方形 GEMM。

**Table 1：M=N=K=8192**

| Kernel | Avg ms | TFLOP/s | LDS | vs hipBLASLt |
|---|---:|---:|---:|---:|
| hipBLASLt | `4.22` | `260.8` | — | — |
| Config 1 (128×96, K=64, 2×2) | `5.01` | `219.6` | `17.5 KB` | `−18.8%` |
| Config 2 (256×256, K=64, 4×4) | `4.78` | `230.1` | `40.0 KB` | `−13.3%` |
| Config 3 (256×160, K=128, 4×2) | `4.47` | `246.0` | `58.5 KB` | `−6.0%` |
| Config 4 (192×192, K=128, 2×4) | `4.39` | `250.5` | `54.0 KB` | `−4.1%` |

**Table 2：M=8192、N=28672、K=8192**

| Kernel | Avg ms | TFLOP/s | vs hipBLASLt |
|---|---:|---:|---:|
| hipBLASLt | `14.90` | `258.3` | — |
| Config 1 (128×96, K=64, 2×2) | `18.11` | `212.5` | `−21.6%` |
| Config 2 (256×256, K=64, 4×4) | `16.79` | `229.3` | `−12.7%` |
| Config 3 (256×160, K=128, 4×2) | `15.68` | `245.5` | `−5.2%` |
| Config 4 (192×192, K=128, 2×4) | `15.59` | `246.8` | `−4.7%` |

**Table 3：M=8192、N=10240、K=8192**

| Kernel | Avg ms | TFLOP/s | vs hipBLASLt |
|---|---:|---:|---:|
| hipBLASLt | `5.28` | `260.5` | — |
| Config 1 (128×96, K=64, 2×2) | `6.34` | `216.8` | `−20.2%` |
| Config 2 (256×256, K=64, 4×4) | `6.03` | `227.8` | `−14.4%` |
| Config 3 (256×160, K=128, 4×2) | `5.60` | `245.3` | `−6.2%` |
| Config 4 (192×192, K=128, 2×4) | `5.57` | `246.6` | `−5.7%` |

**Table 4：M=3072、N=4096、K=8192**

| Kernel | Avg ms | TFLOP/s | vs hipBLASLt |
|---|---:|---:|---:|
| hipBLASLt | `1.16` | `177.9` | — |
| Config 1 (128×96, K=64, 2×2) | `1.01` | `203.9` | `+12.8%` |
| Config 2 (256×256, K=64, 4×4) | `0.93` | `221.2` | `+19.6%` |
| Config 3 (256×160, K=128, 4×2) | `0.86` | `239.2` | `+25.7%` |
| Config 4 (192×192, K=128, 2×4) | `0.89` | `231.5` | `+23.2%` |

按原表 `vs hipBLASLt` 字段的口径，三组大 shape 上 Config 4 均落后 **4.1%至5.7%**；小 shape 上则是 **Config 3领先25.7%**。这些百分比沿用原文报告值，不由表中已经舍入的 TFLOP/s 重新计算。

## 五、Config 3与Config 4为什么各有胜场

**实测事实**是：Config 4 使用 192×192、K=128、2×4 wave grid，在三组大 shape 中均为四种自研配置里最快；Config 3 使用 256×160、K=128、4×2 wave grid，在 M=3072、N=4096 时以 `0.86 ms`、`239.2 TFLOP/s` 胜过 Config 4 的 `0.89 ms`、`231.5 TFLOP/s`。因此不存在一个在全部 shape 上都最优的固定 tile。

原文给出的工程解释是：FP8 元素为 1 字节，而 FP16 为 2 字节，同一 LDS 预算可容纳更大的 tile；例如 256×256、K=64 的 FP8 tile 占用 `40 KB`，若为 FP16 则需要 `80 KB` 而无法容纳。Config 2 通过增大 tile 缩小差距，Config 3 通过加深 K 继续缩小差距，Config 4 则由搜索得到，以 192×192 tile 和 2×4 wave grid 补足余下差距。

限制在于，原文没有针对小 shape 给出逐项消融数据，因此不能把 Config 3 的胜出唯一归因于某一项参数，也不能证明 Config 4 在所有大 shape 上都会最优；这里能确认的是配置与实测排序，而非完整因果。

## 六、正确性验证与实验口径

实验平台是 AMD Radeon RX 9070 XT（`gfx1201`）与 ROCm 10.0；工作负载为 FP8 E4M3 输入、FP32 输出的 TN GEMM，A 行主序、B 列主序。参考实现直接调用 hipBLASLt，使用 `HIPBLAS_COMPUTE_32F` 和 `hipblasLtMatmulAlgoGetHeuristic` 返回的算法。计时先做 10 次 warmup，再取 30 次运行均值；吞吐按 (2MNK/t) 计算。

正确性测试把 A、B 的元素都设为 -1 或 +1。乘积因此均为 ±1，部分和是 FP32 可精确表示的整数，正确 kernel 应与 hipBLASLt bit-for-bit 一致，不需要容差。这个设计能抓布局、索引和累加错误，却**不能代表一般 FP8 量化误差**：随机或真实 E4M3 输入还涉及舍入、饱和、尺度和非整数累加，而本示例又明确没有 scale factor。

## 七、手工搜索与 hipBLASLt 调优

手工搜索联合改变 tile 面积、K 深度和 wave grid。Config 1 是把 FP16 最终 kernel 直接换成 FP8；Config 2 扩大 tile；Config 3 把 `block_k` 加深到 128；Config 4 再通过 tile/wave sweep 选择 192×192 与 2×4。FP8 把操作数宽度减半，使过去受 LDS 容量排除的配置重新可行；与此同时，FP32 accumulator 的寄存器占用又更高，tile 继续增大时，约束会从 LDS 转向 VGPR 和 occupancy。

这四组配置只是手工探索的一小片搜索空间。hipBLASLt offline tuning 会在部署前为目标 shape、dtype 与架构搜索候选；online tuning 则可依据实际调用分布继续选择。两者与手工调优解决同一类问题，但搜索范围更大。正确评测应固定调优预算和候选空间，同时记录编译失败、资源超限和负收益配置，不能把一次配置扫描写成全局最优证明。

## 八、工程与产品适用边界

上述结果只覆盖单卡 RX 9070 XT、四个固定 shape、FP8 E4M3 输入与 FP32 输出。Config 4 在三个大 shape 上接近 hipBLASLt、Config 3 在最小 shape 上领先，最多证明“按 shape 调整 tile/K/wave 有价值”；它不能外推为所有模型、批量、精度或端到端推理都更快。GEMM 的几个百分点还可能被量化、内存搬运、调度和其它算子抵消。

## 九、对Kernel自动调优与EverAgent Eval的启示

原文事实表明，tile 面积、K 深度和 wave grid 不是三个彼此独立的旋钮，而是受数据类型、LDS、寄存器和代码可达性共同约束的联合搜索空间。数据类型必须进入搜索空间：同样受 LDS 预算限制，FP8 的 256×256、`block_k=64` 配置按原文计为 40 KB，而 FP8 路径在 FP16 下需 80 KB，故 FP16 下不可容纳的配置在 FP8 下可能成为候选。与此同时，FP8 路径使用每 lane 八个 FP32 累加值，共 32 字节寄存器，而 FP16 累加器为八个 `_Float16`，共 16 字节；因此随着 tile 面积增长，约束可能先从 LDS 转为寄存器压力。tile 形状和 K 深度还决定预取折叠能否满足 `2*chunks_a≤steps`、`2*chunks_b≤steps`。博客中的四次配置只是搜索空间的一个切片；hipBLASLt 离线与在线调优工具才是覆盖更多 shape、数据类型和架构的大规模搜索机制。

原文没有 EverAgent Eval 的实测结果，因此以下属于评测设计建议而非已有性能事实：EverAgent Eval 不应只奖励某个固定 kernel 的最高吞吐，而应评测自动调优器能否针对“shape＋数据类型＋目标硬件”选择或生成有效配置；基线应包含 hipBLASLt 启发式算法，并逐 shape 报告结果，同时记录无效配置、编译失败、资源约束、平均性能及负结果。离线调优适合在部署前扩大搜索，在线调优适合针对实际输入分布继续修正，二者不能由一次手工挑选的 192×192 配置取代。

## 反方解释

最宽泛的“优于 hipBLASLt”解释并不成立。Config 4 只是针对四个固定 shape 搜索后的结果；最小 shape 上 Config 3 反超，已经证明单个 tile 会过拟合。博客比较的是 hipBLASLt 启发式所选算法，并非穷尽其离线或在线调优空间，因而即使某一 shape 胜出，也不能证明库级方案已到上限。厂商博客还可能围绕既有实现选择代码路径、shape 与编译环境。若进一步混入模型调度、批量大小、量化误差、内存搬运和端到端时延，GEMM 层的几个百分点未必能转化为产品收益。因此“所有模型、批量及精度下均优于 hipBLASLt”属于不受原文支持的外推。

## Limitations

证据仅覆盖单卡 RX 9070 XT、单一代际、ROCm 10.0、单一编译选项、TN 布局及 FP8 E4M3 到 FP32 输出的四个固定 shape；未覆盖多 GPU、其他 RDNA/CDNA 架构、FP16/BF16/INT8、不同批量或模型端到端场景。测试只报告均值，原文片段未给出方差、置信区间和逐次原始数据，也未系统比较更多配置或调优预算。LDS、寄存器、occupancy、编译可行性和预取约束可能共同排除候选，故手工扫描不构成完备搜索。结果也不能回答配置在新 shape、冷启动和线上输入分布变化下是否稳定。

## 思考与追问

EverAgent Eval 是否会按 shape、dtype 和硬件分组，而非汇总成一个总分？候选生成器能否显式搜索 tile 面积、K 深度与 wave grid，并遵守 LDS、寄存器和折叠约束？失败或负收益配置是否被完整保留？离线调优预算、在线修正频率和部署时延成本如何共同计入？此外，在四个固定 shape 之外加入随机 shape、真实模型矩阵、批量扫描及多种精度后，启发式基线和生成式调优的排序是否仍成立？这些问题决定实验能否从代码示例走向可复现的工程结论。

## 最终结论

原文最有力地证明了两点：FP8 改变了 LDS 可容纳的 tile 边界，而 tile 面积、K 深度、wave grid 与数据类型必须联合调优；针对固定硬件和固定 shape 的手工配置，可以接近并在个别 shape 上超过 hipBLASLt 启发式基线。它没有证明单卡、四个 shape、厂商自测博客和代码示例中的结果可泛化到所有模型、批量与精度。Kernel 自动调优及 EverAgent Eval 应据此采用逐场景基线、完整约束建模和正负结果并报的方法，并让离线、在线调优承担更大规模搜索。
