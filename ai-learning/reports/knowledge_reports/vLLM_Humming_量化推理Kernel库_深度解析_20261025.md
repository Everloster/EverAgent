---
title: "vLLM Humming：量化推理 GEMM Kernel 库的设计、支持矩阵与证据边界"
domain: "ai-learning"
report_type: "概念深度解析"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["vLLM", "Humming", "quantization", "GEMM", "kernel", "JIT", "MoE", "MXFP4"]
---

# vLLM Humming：量化推理 GEMM Kernel 库的设计、支持矩阵与证据边界

> **一句话结论**：Humming 是 vLLM 社区与蚂蚁集团在 2026-10 公开的一个 **JIT 编译的量化 GEMM kernel 库**，其真正贡献不是「某个新 kernel」，而是把 **量化描述（Layer/Compute/Tuning 三配置）** 与 **执行实现（共享 CUDA 组件 + 按架构启发式）** 解耦，从而用一套代码同时覆盖 dense/MoE、多种 weight×activation 组合、以及 Turing→Blackwell 的多代 NVIDIA GPU 与部分 CUDA 兼容设备；博客给出的性能数字（相对 Marlin / DeepGEMM / FlashInfer 最高约 2–5×，端到端 +14%～+43%）**全部是项目方与 vLLM 社区自报**，尚无独立复现，且缺少「同一 shape/批次/格式/测量口径」的完整对照表。

> **阅读边界**：本文以 vLLM 官方博客《Announcing Humming: Fast, Flexible Kernels for Quantized Inference》（2026-10-21）为主线，**实际读取了 Humming 官方仓库固定 commit `db930afa2256cba49b3e46c0589323c3e80b0bfb`（2026-10-22）** 的 README、`docs/config.md`、`humming/schema/humming.py`、`humming/jit/compiler.py`、`humming/testing/runner.py`、`humming/ops/gemm.py`、`humming/forward.py`、`humming/dtypes.py`、`humming/layer.py`、`benchmarks/bench_humming.py`，以及仓库目录树与测试目录清单；vLLM 侧读取了 `vllm/model_executor/layers/quantization/humming.py`、`vllm/utils/humming.py` 与 vLLM 官方 API 文档页。所有性能数字均标注为**自报**，不构成独立验证。

---

## 目录

1. [问题定义：三种碎片化同时发生](#1-问题定义三种碎片化同时发生)
2. [抽象：Humming 的四层结构与数据流](#2-抽象humming-的四层结构与数据流)
3. [支持矩阵：dtype × 激活 × 设备 × GEMM 类型](#3-支持矩阵dtype--激活--设备--gemm-类型)
4. [代码路径：仓库里各文件到底负责什么](#4-代码路径仓库里各文件到底负责什么)
5. [正确性门：Humming 怎么保证 kernel 算对](#5-正确性门humming-怎么保证-kernel-算对)
6. [benchmark 逐口径核对](#6-benchmark-逐口径核对)
7. [竞品比较：与 Marlin / FlashInfer / DeepGEMM / Triton 的有边界比较](#7-竞品比较与-marlin--flashinfer--deepgemm--triton-的有边界比较)
8. [vLLM 集成：哪些能力已合并、哪些仍是实验性](#8-vllm-集成哪些能力已合并哪些仍是实验性)
9. [对推理引擎插件化与跨硬件可维护性的启示](#9-对推理引擎插件化与跨硬件可维护性的启示)
10. [Limitations](#10-limitations)
11. [思考与追问](#11-思考与追问)
12. [附录 A：来源清单](#附录-a来源清单)
13. [附录 B：术语与安装/使用速查](#附录-b术语与安装使用速查)

---

## 1. 问题定义：三种碎片化同时发生

### 1.1 博客给出的问题陈述（一手）

博客《Background》一节把动机写成三层，互相叠加：

**（a）量化格式碎片化。** 常见组合是 WNA16 / W8A8 / W4A8 / W4A4（W=权重位宽，A=激活位宽，N=可变权重位宽）。但**同样位宽不等于同一种格式**：INT4 与 NVFP4 在数值格式和缩放上就不同；再加上缩放粒度（group/block/channel/tensor）、scale 的表示类型、group size、对称还是非对称，配置空间迅速膨胀。

**（b）硬件代际分裂。** 同一种量化格式在不同代 GPU 上的最优路径不同：Hopper 之前没有原生 MXFP4 Tensor Core；Blackwell 有原生 MXFP4/MXFP8；B300(SM103) 的 UMMA 甚至不再支持 INT8 计算，只能退回早期 MMA 指令；Rubin 又不支持某些 Blackwell 的「隐藏格式」。**一种格式要在多代硬件上跑得快，就需要为不同代写不同路径。**

**（c）kernel 维护成本。** 原文一句话点破：为「每种组合」都写一个专用 kernel，会导致「每个新组合都要自己的权重预处理、kernel 选择、框架适配与测试」，而且优化成果要在多份实现之间反复搬运。

### 1.2 我的补充判断：碎片化的真正来源是「三个正交维度」的笛卡尔积

把上面三点翻译成工程语言，量化 kernel 库的复杂度来自三个正交维度的乘积：

| 维度 | 取值空间（来自仓库实际实现） |
|---|---|
| **数值语义** | weight dtype × activation dtype × scale dtype × scale 粒度 × zero-point 表示 |
| **数据布局** | 权重打包方式、packed-K 布局、scale 的 M-major/row-major、输入量化模式 |
| **执行后端** | MMA / WGMMA / UMMA / MXMMA、pipeline 级数、TMA 与否、Stream-K、warp specialization |

仓库 `docs/config.md` 的三配置划分（`LayerConfig` / `ComputeConfig` / `TuningConfig`）正是**按这三个维度切开的**：

- `LayerConfig` = 数值语义 + 布局（在权重 transform 时确定，改动要重新 transform 权重）；
- `ComputeConfig` = GEMM 类型与计算行为（调用时可选，但必须与既有布局兼容）；
- `TuningConfig` = tiling / pipeline / 传输 / 调度（调用时可选）。

**这是 Humming 全部设计的关键**：它没有消除复杂度，而是**把复杂度从「kernel 数量」转移到「配置数量 + 组件数量」**。

---

## 2. 抽象：Humming 的四层结构与数据流

### 2.1 结构总览（读代码得到）

```
┌────────────────────────────────────────────────────────────────────────────┐
│ ① schema 层：统一量化表示（humming/schema/）                              │
│   BaseWeightSchema / BaseInputSchema                                       │
│   HummingWeightSchema（Humming 标准格式）+ HummingInputSchema              │
│   导出格式适配器：autoround / awq / bitnet / compressed_tensors / fp8 /   │
│                   gpt_oss_mxfp4 / gptq / modelopt / mxfp4 / quark         │
│   → 把不同量化工具的 checkpoint 归一到「同一套参数 + 同一种权重布局」      │
├────────────────────────────────────────────────────────────────────────────┤
│ ② config 层：三配置（humming/config/）                                    │
│   LayerConfig（形状/dtype/量化参数/目标 SM）                              │
│   ComputeConfig（gemm_type / use_f16_accum / use_batch_invariant / …）      │
│   TuningConfig（mma_type / block_shape / warp_shape / num_stages /        │
│                 TMA 开关 / use_stream_k / raster_group_m / multicast …）   │
├────────────────────────────────────────────────────────────────────────────┤
│ ③ JIT 层：按配置生成 kernel（humming/jit/、humming/utils/nvrtc.py）        │
│   签名 = 类名 + kernel 表达式 + 编译 flag + 生成的 CUDA 源码 + .cuh 文件时间│
│   → hash → 缓存目录（kernel.cubin / kernel.cu / stdout.log / stderr.log）  │
│   → FileLock + os.replace 原子替换；NVRTC 与 NVCC 两条编译路径             │
├────────────────────────────────────────────────────────────────────────────┤
│ ④ 执行层：调用与调度（humming/ops/、humming/forward.py、humming/tune/）    │
│   humming_gemm() → prepare_kernels（torch.ops.humming）→ launch_kernel     │
│   may_process_input（激活量化/分组 scale）→ may_quant_input                 │
│   tune/get_heuristics_config：按架构与 shape 区间给出候选配置               │
└────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 一次推理调用的数据流（结合 `humming/ops/gemm.py` 与 `humming/forward.py`）

```
模型加载期（一次性）：
  checkpoint ──► schema 适配器（export format → Humming 标准格式）
             ──► 权重打包 / 维度 padding（vLLM 侧 pad_n 到 256、pad_k 到 128）
             ──► LayerConfig 固化（形状、dtype、量化参数、目标 SM 版本）

预热期（每个 GEMM 形状一次）：
  (LayerConfig, ComputeConfig, TuningConfig) ──► JIT 编译 ──► cubin 缓存
  ──► prepare_kernels（humming::prepare_kernels，按 M 区间准备多份配置）

推理期（每次调用）：
  激活 ──► may_process_input（按 input_quant_mode 计算 dynamic token/group scale）
        ──► humming_gemm(layer_config, inputs, weight, scales, zero_point, bias,
                        compute_config, tuning_config, routing 信息)
        ──► launch_kernel（选 cubin、launch）
        ──► 输出（dense 直接写；indexed 按 sorted_ids/expert_ids 散写；
                  grouped_contiguous/masked 按专家分组布局）
```

### 2.3 「统一量化表示」在代码里长什么样

读 `humming/schema/humming.py` 得到的 `HummingWeightSchema` 关键字段：

- `b_dtype`（权重类型）、`bs_dtype`（scale 类型）、`weight_scale_group_size` / `_group_size_n`、`weight_scale_type`（group/block/channel/tensor）、`weight_scale_2_type`（次级 scale）、`has_zero_point` / `is_fp_zero_point`、`hadamard_block_size`。
- **别名机制**：`KWARGS_ALIAS` 把不同导出工具的字段名映射到统一名（`weight_dtype`/`dtype` → `b_dtype`，`group_size` → `weight_scale_group_size`，`scale_type` → `weight_scale_type`，`scale_dtype` → `bs_dtype` …）。这就是「不同量化工具的 checkpoint 归一」的落点。
- **权重物理存储**：低比特权重打包进 `int32`（`packed_factor = 32/num_bits`，沿 K 维打包）；group scale 形状 `(N, K/group)`；channel scale `(N,1)`；block scale `(N/group_n, K/group)`；tensor scale 为标量。
- **自动推导**：未显式给出 `weight_scale_type` 时，按 group_size_n>1 → block；group_size==0 → channel；否则 group。BLOCK 模式下 `bs_dtype` 强制为 float32。

`humming/schema/` 目录下的适配器清单（`autoround / awq / bitnet / compressed_tensors / fp8 / gpt_oss_mxfp4 / gptq / modelopt / mxfp4 / quark`）直接印证了博客「把支持的导出格式转成 Humming 标准格式」这句话。

### 2.4 JIT 编译与缓存（读 `humming/jit/compiler.py`）

- 编译签名：`f"{cls.__name__}$${cls.signature()}$${flags}$${kernel_expr}$${code}"`，再拼上 **所有 `.cuh` 头文件的最后修改时间**（`cuh_last_update_time`），以及可选的 cubin patcher 内容 hash。
- 缓存布局：`~/.cache/humming/<hash>/`（`kernel.cu` 源文件、`signature.txt`、`kernel_tmp.cubin` → `kernel.cubin`、`stdout.log`、`stderr.log`）。
- 并发安全：`FileLock` + `os.replace` 原子替换；命中缓存直接返回 cubin 路径。
- 两条编译后端：`NVRTCCompiler`（运行时 NVRTC，用 ctypes 加载 `nvrtcVersion`、注入标准头 shim、构造 `CUtensorMap` 结构）与 NVCC 路径；调试开关 `HUMMING_DEBUG_KERNEL` 会加 `-lineinfo` 与超时计数。

**这解释了博客里「编译 1.82s vs CUTLASS 23.35s」的来源**：Humming 的 kernel 是从 CUDA 组件拼装出来的短程序，不是模板实例化的大编译单元；同时 `.cuh` 时间戳进签名，保证改组件会自动失效缓存。

---

## 3. 支持矩阵：dtype × 激活 × 设备 × GEMM 类型

### 3.1 README 给出的激活 × 设备 × 权重类型表（一手，commit `db930af`）

| 激活类型 | 支持设备 | 支持的权重类型 |
|---|---|---|
| FP16 (e5m10) | SM75+ | 对称 INT1–8；带动态 zero point 的 INT1–8；任意有符号 FP（kBits ≤ 8, kExp ≤ 5） |
| BF16 (e8m7) | SM80+ | 对称 INT1–8；带动态 zero point 的 INT1–8；任意有符号 FP（kBits ≤ 8） |
| FP8 (e4m3) | SM89+ | 对称 INT1–5；带动态 zero point 的 INT1–4；任意有符号 FP（kExp ≤ 4, kMan ≤ 3） |
| FP8 (e5m2) | SM89+ | 对称 INT1–4；带动态 zero point 的 INT1–3；任意有符号 FP（kExp ≤ 5, kMan ≤ 2） |
| FP4 (e2m1) | SM120+ | 对称 INT1–3；带动态 zero point 的 INT1–2；任意有符号 FP（kExp ≤ 2, kMan ≤ 1） |
| INT8 | SM75+ | 对称 INT1–8；带动态 zero point 的 INT1–7 |
| INT4 | SM80+ | 对称 INT1–4；带动态 zero point 的 INT1–3 |

README 顶部还给出两条硬约束：包体「100+KB」，依赖仅 **PyTorch 与 NVCC**。

### 3.2 特殊数值格式（代码可验证）

- `humming/dtypes.py` 定义了 `float2e0m1 / float3e0m2 / float4e0m3 / float5e0m4 / float6e0m5 / float8e0m7` 等**零指数位**浮点格式，以及 `float4e2m1 / float8e3m4 / float8e4m3 / float8e5m2 / float8e5m3 / float8e8m0`；整数侧有 `uint1..uint8`、`int2/int3/int4/int6/int8`。
- 博客声称的两点与代码一致：①「零指数位格式的可表示值等价于同位宽对称整数」（如 INT8 去掉 −128 与 `float8e0m7` 都表示 −127…127），Humming 会把符合条件的对称整数权重**自动转换**成该格式以加速反量化；② `float4e0m3` 与 `float8e3m4` 是 Blackwell Tensor Core 的「隐藏能力」（不在 PTX 类型系统里暴露），`humming/config/mma.py` 里有 `supports_undocumented_fp_dtypes` / `uses_undocumented_fp_operand` 专门处理它们。
- 博客称 Rubin 不支持这两种隐藏格式 → 仓库 `humming/tune/` 里存在 `sm75 / sm8x / sm90 / sm90_h20 / sm100 / sm120 / sm121 / ppu_sm80`，**没有 Rubin 专用文件**，与「Rubin 需另做适配」的表述一致。

### 3.3 GEMM 类型（MoE 的四种输入组织方式）

来自 `docs/config.md` 的 `ComputeConfig.gemm_type`：

| 取值 | 语义 |
|---|---|
| `dense` | 普通矩阵乘，所有行共享同一份权重 |
| `indexed` | 按 routing 索引读输入，并写到对应位置（适合 MoE 的 token→expert 散写） |
| `grouped_contiguous` | 每个专家的输入沿行维连续存放，专家边界描述分组 |
| `grouped_masked` | 每专家固定容量存储区 + 实际有效行数 |

普通层可自动选 `dense`；MoE 必须显式指定并提供路由/专家布局数据。四者在 TMA 支持、tile 对齐、输出处理上不同。

### 3.4 设备覆盖与「已合并 / 仍实验性」

| 能力 | 状态 | 证据 |
|---|---|---|
| NVIDIA Turing(SM75)→Blackwell(SM120/SM121) | **已支持**（README + 逐架构 tune 文件） | README 支持矩阵；`humming/tune/sm75.py … sm121.py` |
| T-Head 玄武 810E（CUDA 兼容 PPU） | **已支持** | 博客声明；仓库存在 `humming/tune/ppu_sm80.py` |
| Zhenwu M890 等更多 PPU | **计划中** | 博客 Future Plans |
| Blackwell 隐藏格式（`float4e0m3`/`float8e3m4`） | 已支持（SM100/103、SM120/121），**Rubin 不支持** | 博客 + `dtypes.py` + 无 Rubin tune 文件 |
| Autotune（设备上实测候选配置） | **仍是计划**（`tune/candidate.py` 已有候选生成代码，但博客把它列为未来工作） | 博客 Future Plans「Adding Autotune」；仓库 `humming/tune/candidate.py` |
| 量化 All-to-All（EP 通信） | **仍是计划** | 博客 Future Plans「Deeper Integration with Inference Frameworks」 |
| Rubin Locality Domains 等新特性 | **仍是计划** | 博客 Future Plans |

---

## 4. 代码路径：仓库里各文件到底负责什么

以下均为**实际读过的文件**（commit `db930af`）：

| 文件 | 规模 | 职责（读码结论） |
|---|---|---|
| `humming/layer.py` | 28.5 KB | 用户侧主入口。`HummingLayer`（torch.nn.Module）：`load_from_unquantized` / `load_from_tensors` / `load_from_safetensors` / `from_safetensors` → `transform()`（把权重转成 Humming 布局并固化 LayerConfig）→ `forward()`。`HummingLayerMeta` 管理 weight/scale/zero-point/bias 的参数命名与 shape 覆盖；`HummingLayerMethod` 提供 `prepare_layer_meta`、`check_and_pad_tensors`、`may_process_int_weight_scale`、`may_process_fused_e8m0_scale`、`get_default_tuning_configs`、`transform_humming_layer`、`may_quant_input`、`may_process_input`、`forward_layer` 等钩子 |
| `humming/transform.py` | 28.4 KB | 权重转换与打包（打包因子、scale 布局重排、padding） |
| `humming/schema/humming.py` | 25.5 KB | **标准格式定义**：`HummingWeightSchema`（字段、别名、自动推导、`get_tensors_attrs` 决定物理 tensor 形状与 dtype）、`HummingInputSchema` |
| `humming/schema/*.py`（10 个适配器） | — | 各导出格式 → Humming 格式的转换（awq/gptq/autoround/quark/modelopt/compressed-tensors/fp8/mxfp4/bitnet/gpt_oss_mxfp4） |
| `humming/config/` | — | `LayerConfig` / `ComputeConfig` / `TuningConfig` 数据类与兼容性校验（`docs/config.md` 是其权威说明，26 KB） |
| `humming/jit/compiler.py` | 11.3 KB | 编译签名、缓存目录、FileLock、NVRTC/NVCC 后端 |
| `humming/jit/runtime.py` | 5.7 KB | 运行时加载 cubin |
| `humming/tune/`（13 个文件） | — | **按架构分文件的启发式**：`sm75 / sm8x / sm90 / sm90_h20 / sm90_policies / sm100 / sm120 / sm121 / ppu_sm80`，加 `candidate.py`（候选配置）、`base.py`、`process_input.py`、`raster.py` |
| `humming/ops/gemm.py` | 3.7 KB | 对外算子：`humming_gemm(...)`（参数即三配置 + 权重/尺度/zero-point/bias + routing 元数据），`_prepare_kernels_op` 注册为 `humming::prepare_kernels`（FakeTensor 分支也能返回配置数，保证 torch.compile 兼容） |
| `humming/ops/launcher.py` / `input.py` / `weight.py` / `utils.py` | — | kernel 启动、输入量化与权重准备、torch op 注册与设备守卫 |
| `humming/forward.py` | 7.7 KB | `may_process_input`（按 `input_quant_mode` 产出 group/token scale）、`may_quant_input`、`humming_forward`、`_resolve_use_pdl`（PDL = programmatic dependent launch） |
| `humming/dtypes.py` | 7.5 KB | `DataType` / `IntegerType` / `FloatingPointType` 与全部具体 dtype 常量、torch dtype 映射 |
| `humming/testing/runner.py` | 30.4 KB | **正确性测试框架**（见第 5 节） |
| `humming/testing/process_input.py` / `data.py` / `tuning.py` / `benchmark.py` | — | 输入处理参考实现、随机数据生成、调优配置测试、benchmark 落盘 |
| `benchmarks/bench_humming.py` | 9.9 KB | 微基准脚本（见第 6 节）；同目录另有 `bench_marlin.py`、`bench_cutlass_w8a8.py`、`bench_torch.py`、`bench_triton_moe.py` |
| `benchmarks/results/` | — | **已归档的结果产物目录**：`4090 / a800 / h20 / h200` 四个设备目录 |

`docs/config.md` 里最值得注意的**分层原则**（原文）：改变影响存储的选项需要重新 transform 权重；`ComputeConfig` 与 `TuningConfig` 可在调用时切换，但必须与既有布局兼容（例如换 `mma_type` 通常不需要重新 transform 权重）。**这条原则是「统一抽象」能成立的工程前提**。

---

## 5. 正确性门：Humming 怎么保证 kernel 算对

读 `humming/testing/runner.py` 得到的具体机制：

1. **参考实现**：把权重按 schema 反量化（`schema.dequant_tensors`），激活也走对应的反量化/量化参考路径（代码中逐 dtype 分支处理 INT3/INT4 打包、符号位等），然后用 **FP32 累加的 matmul** 作为参考输出（`_matmul_reference` / `make_reference`，MoE 路径按 topk 索引后逐专家计算）。
2. **比较门**：`torch.testing.assert_close(outputs, outputs_ref, rtol=rtol, atol=atol)`，默认 `rtol=0.01`、`atol=0.05`（`KernelTestCase` 的默认值）；对**非有限值**走更宽松分支（`atol=2*atol`），并统计 **outlier**（超出容差的元素比例）。
3. **形状覆盖门**：`assert_kernel_test_shape_coverage(...)` 强制测试覆盖声明的 shape 集合，防止「只测了顺手的形状」。
4. **测试资产**：`tests/` 下有 `test_jit_infrastructure.py`（25 KB）、`test_tuning_candidates.py`（27 KB）、`test_sm90_heuristics.py`（17.5 KB）、`test_sm90_h20_heuristics.py`、`test_sm8x_heuristics.py`，以及 `tests/kernels/humming/`（按架构/格式组织的 kernel 测试目录）、`tests/native/`。

**边界**：这套门是**库内自测**，它证明「实现与自己定义的参考语义一致」，不证明「端到端模型质量不变」。量化推理的质量评估（例如 W4A8 与 W4A16 的精度差）在本文所用材料中**没有数据**。

---

## 6. benchmark 逐口径核对

### 6.1 微基准的测量口径（博客明确写出 + 脚本可验证）

博客「Performance」一节写明：

- 由 **vLLM 社区**（不是蚂蚁自己）跑；
- **M 覆盖 1 到 8192 的每一个 2 的幂**；
- kernel **完全预热**，**冷 L2 cache** 下**独立计时**，样本之间**短暂暂停**；
- **MoE 的加速比 = Gateup 与 Down 两个 GEMM 延迟之和**；
- 每张图标注 **baseline、量化格式、矩阵维度、软件版本**。

脚本 `benchmarks/bench_humming.py` 印证并补充了口径：

- 默认 M 列表是 `[2**i for i in range(15)]`，即 **1…16384**（比博客所述区间多一个点；博客图表区间 1–8192 应是脚本传参后的子集）[分析者推导]；
- 每个 shape 都重新调用 `get_heuristics_config(...)` 取**按 M 区间分段的候选配置**，并把整份候选列表 `json.dumps` 后传入 kernel（因此「M 区间 → 配置」是运行时调度，不是单一 kernel）；
- 激活侧按 `may_process_input` 现场量化并生成 group/token scale；
- 结果通过 `humming.testing.save_benchmark_result` 落盘到 `benchmarks/results/<device>/`。

### 6.2 关键数字与其口径（全部为自报）

| 主题 | 数字 | baseline / 条件 |
|---|---|---|
| W4A16 dense | 小 batch 约 **3–4×**；大 batch H200 约 **2× Marlin**；部分 B300 **>3×** | baseline 为 cuBLAS（图注），对比对象为 vLLM Marlin |
| W4A16 MoE | H20/H200 上 MXFP4 约 **2× Marlin**；B300 上 Grouped 路径约 **5×** | 同上 |
| 其他 WnA16 | 低比特在 SM120 上 **>5× BF16 cuBLAS**；H20 大 batch 接近 BF16 cuBLAS | cuBLAS 基线 |
| W8A8 (Hopper) | H20 约 **2.6×**、H200 约 **2.5×** DeepGEMM Contiguous | DeepGEMM Contiguous 基线 |
| W4A8-MXFP4 (Hopper) | H20 约 **4.2×**、H200 约 **4.5×**（以 DeepGEMM W8A8 为基线） | 跨精度基线；并称优于 FlashInfer CUTLASS W4A8 |
| W8A8/W4A8/W4A4 (B300 SM103) | 约 **1.25× / 1.6× / 1.4×** | DeepGEMM Contiguous 同精度基线 |
| SM120/SM121 | SM121 小 batch W4A8 约 **+19%**、W4A4 约 **+9%** | FlashInfer CUTLASS 基线 |
| 编译时间 | H200 服务器、CUDA 13.4、**禁用缓存**：CUTLASS+NVCC **23.35 s** → Humming+NVCC **1.82 s** / Humming+NVRTC **1.88 s** | 单一 W4A16 kernel 编译 |
| 预热期批量编译 | 单层 GEMM 覆盖全部支持 M 的编译与加载约 **2–4 s** | 模型 warmup 期间并行编译 |

### 6.3 端到端 serving 数字（唯一一张完整表格，最可核验）

模型 **DeepSeek-V4.1-Flash**，**8×H20**，**TP=8**；保持模型 **MXFP4 权重不变**，只把 MoE 执行从 **vLLM Marlin W4A16（BF16 激活）** 换成 **Humming W4A8（tokenwise FP8 激活）**：

| 并发 | 输入吞吐 (tok/s) | 输出吞吐 (tok/s) | TTFT (ms) | TPOT (ms) |
|---|---|---|---|---|
| 1 | 2827.15 → 3226.23 (+14.1%) | 88.30 → 100.77 (+14.1%) | 543.13 → 383.80 (−29.3%) | 9.24 → 8.46 (−8.5%) |
| 2 | 4781.06 → 5646.98 (+18.1%) | 149.33 → 176.38 (+18.1%) | 794.31 → 555.66 (−30.0%) | 10.33 → 9.20 (−10.9%) |
| 4 | 7427.64 → 9160.81 (+23.3%) | 231.99 → 286.12 (+23.3%) | 1422.32 → 971.74 (−31.7%) | 11.72 → 10.22 (−12.9%) |
| 8 | 9190.03 → 12263.89 (+33.4%) | 287.04 → 383.04 (+33.4%) | 2049.81 → 1386.91 (−32.3%) | 19.90 → 15.49 (−22.2%) |
| 16 | 11124.67 → 15171.00 (+36.4%) | 348.96 → 475.89 (+36.4%) | 2463.69 → 1844.71 (−25.1%) | 36.28 → 26.44 (−27.1%) |
| 32 | 12669.43 → 17804.79 (+40.5%) | 398.83 → 560.49 (+40.5%) | 3546.74 → 2465.47 (−30.5%) | 66.44 → 47.48 (−28.5%) |
| 64 | 13937.42 → 19973.00 (+43.3%) | 442.37 → 633.94 (+43.3%) | 5467.35 → 3882.94 (−29.0%) | 123.25 → 85.70 (−30.5%) |

**口径核验（我的分析）**：

1. **博客的区间表述与表格一致**：吞吐 +14.1%…+43.3% ≈ 文中「14%–43%」；TTFT 降幅 −25.1%…−32.3% ≈ 文中「25%–32%」。
2. **输入吞吐与输出吞吐的百分比逐行完全相同，且二者绝对值之比始终约为 32:1**。这强烈说明 benchmark 使用了固定的输入/输出 token 配比，两列都由同一批完成请求数乘以固定 token 数得到，因而不是两份独立性能证据。[分析者推导] 更稳妥的读法是：该 workload 的**整体完成速率**提升 14.1%–43.3%；不能从两列相同百分比再额外推导一次收益。
3. **收益随并发单调上升**（14.1% → 43.3%），说明收益对 workload shape / 有效 batch 明显敏感；但表格无法区分这是更大的 GEMM `M` 带来的 kernel 利用率、权重流量下降、vLLM batching，还是排队/调度交互。并且并发 1 时 TTFT 已下降 29.3%、TPOT 下降 8.5%，所以不能说收益主要来自排队而非单请求执行。[分析者推导]
4. **对照是「同权重、换激活精度」**：Marlin W4A16 用 BF16 激活，Humming W4A8 用 tokenwise FP8 激活。这既是 kernel 差异，也是**数值路径差异**，收益里有多少来自「W4A8 本身更省带宽」、多少来自 Humming 的实现，**文章未做拆分**。
5. **口径缺失项**：未给请求长度分布、输出长度、是否开 prefix caching、MTP/speculative、采样参数、batch 调度策略，也未给多次重复与误差条；并发 1–64 的样本量与时长未写。

### 6.4 图中数字不可复述的部分

博客的六张性能图（W4A16 dense/MoE、WnA16 汇总、W8A8/W4A8 Hopper、MX MoE SM103、SM12x W4A8/W4A4）以 SVG 图片给出，**正文只给出「约几倍」的概括**。因此本报告只引用正文可唯一对应的数值，**不编造图内具体点值**；逐点数据需要看 `benchmarks/results/<device>/` 下的产物与原始脚本。

---

## 7. 竞品比较：与 Marlin / FlashInfer / DeepGEMM / Triton 的有边界比较

### 7.1 竞品各自解决什么

| 方案 | 定位 | 覆盖范围 | 局限（相对 Humming） |
|---|---|---|---|
| **vLLM Marlin** | vLLM 在本文对照中承担 W4A16 baseline | 本文比较的是 4-bit 权重 + 16-bit 激活路径 | 本文没有系统审计 Marlin 的全部格式覆盖；只能确认博客所测 shape 中 Humming 自报约 2–5× |
| **DeepGEMM** | 本文对照中承担 Hopper/Blackwell FP8 / MX 路径 baseline | 本文重点使用其 W8A8 与相应 MX precision 路径 | 本报告未审计 DeepGEMM 的完整类型矩阵；只能确认 Humming 自报的特定 shape / 格式结果，不能据此概括整个项目的覆盖能力 |
| **FlashInfer CUTLASS** | 基于 CUTLASS 的多后端实现（attention 生态强） | 覆盖多种量化 | 博客称 Humming 在 SM120/121 的 W4A8/W4A4 领先约 19%/9%；但也承认 **FlashInfer CUTLASS W4A8 本身就是「基于 Humming 的思路」的实现**，只是 Humming 当前实现更快 |
| **CUTLASS** | 通用模板 GEMM 库 | 广 | 编译慢（博客：23.35 s vs 1.82 s）、配置爆炸 |
| **Triton / torch.compile** | 可移植、开发门槛较低的生成式 kernel 路线 | 广 | 仓库保留 `bench_torch.py`、`bench_triton_moe.py` 作为对照脚本，但博客没有给统一 shape 下的完整结果；本文不能据此断言其普遍性能上限低于手写 CUDA |

### 7.2 比较的边界（必须一起读）

1. **基线是「各格式的强项」**：W4A16 对 Marlin、W8A8 对 DeepGEMM、SM12x 对 FlashInfer —— 每张图选的都是那个格式最强的对手，因此**不是单一统一 baseline 的横向排行**。
2. **跨精度基线**：Hopper 的 W4A8 面板用 **DeepGEMM W8A8** 作基线（Humming W4A8 高出 4.2–4.5×），这既包含 kernel 差异，也包含 **W4A8 比 W8A8 少搬一半权重** 的物理优势。把它读成「Humming 比 DeepGEMM 快 4.5×」是**错误口径**。
3. **未覆盖的对照**：博客没有给出与 TensorRT-LLM、SGLang 的对比，也没有在同一 shape 下把 Marlin/DeepGEMM/FlashInfer/Triton 全部放在一起。
4. **FlashInfer 的关系需要说清**：Humming 的思路已被 FlashInfer 采用（FlashInfer CUTLASS W4A8），Humming 的增量在于「统一 JIT 框架 + 跨架构 + 更多格式」。
5. **MoE 口径特殊**：博客定义 MoE 加速比 = Gateup + Down GEMM 延迟之和，**不含** router、dispatch/combine、all-to-all 通信。因此 **MoE 微基准的加速比不能直接换算成端到端 MoE 加速比**（端到端还要加上 EP 通信与调度开销）。
6. **Humming 自己也承认短板**：博客称「通过定向调优，Humming 在多数场景已能达到 SOTA」，但「模型形状、量化配置、设备资源差异巨大，启发式很难在每个 case 都选到最优配置」，**autotune 被列为未来计划**。

---

## 8. vLLM 集成：哪些能力已合并、哪些仍是实验性

### 8.1 vLLM 侧的实际集成（读 vLLM `main` 分支源码）

- **依赖已合并**：`vllm/utils/humming.py` 是一个**懒加载 facade**（注释写明：vLLM 代码应从这里导入 humming 符号，以推迟 `import humming` 的 import-time 副作用）。博客称 **vLLM 0.29.0 起 CUDA 安装已默认带 humming 依赖**。
- **后端选择**：`--linear-backend humming`（dense GEMM）与 `--moe-backend humming`（MoE GEMM）两个开关。
- **兼容路径**：`--quantization humming` 官方定位为「仅为 Humming 支持但 vLLM 不再支持或尚未原生支持的格式提供兼容路径，例如 GPTQ INT3」。vLLM 的 `HummingConfig.override_quantization_method` 甚至会对 `gpt_oss` + `mxfp4` 组合直接报错，提示改用 `--moe-backend humming`。
- **实现规模**：`vllm/model_executor/layers/quantization/humming.py` 定义了 `HummingConfig`（`QuantizationConfig` 子类）、`HummingLayerQuantizationConfig`、`HummingLinearMethod`、`HummingMoEMethod`；`get_min_capability()` 返回 **75**（SM75），支持激活 dtype 为 bf16/fp16。
- **工程细节**：权重加载器支持**在线量化**（`VLLM_HUMMING_ONLINE_QUANT_CONFIG`、`force_requant`）；对未量化的 FP16/BF16 权重会**回退**到 `UnquantizedLinearMethod`（并把该层标记为 fallback、释放量化参数）；支持 compressed-tensors / modelopt 的 config_groups 解析；权重 transform 时 `pad_n_to_multiple=256`、`pad_k_to_multiple=128`；为 Stream-K 预分配 `create_humming_locks`；MoE 侧按 schema 派生 QuantKey 并 `select_humming_moe_experts`。
- **激活类型可覆盖**：`--quantization-config.moe.activation mxfp8` 之类的方式指定激活类型；默认沿用 checkpoint 指定的激活类型，设备不支持时**自动回退到更高精度的可用路径**（例如无原生 MXFP4 的设备改走 FP8/BF16/FP16）。

### 8.2 「已合并」与「仍实验性」清单

| 项 | 状态 |
|---|---|
| vLLM 0.29.0+ CUDA 安装自带 humming | **已合并**（博客 + `vllm/utils/humming.py`） |
| `--linear-backend humming` / `--moe-backend humming` | **已合并**（vLLM 源码存在对应分支与 `HummingLinearMethod`/`HummingMoEMethod`） |
| `--quantization humming`（GPTQ INT3 等兼容路径） | **已合并但定位为兼容层**，不是主推路径 |
| 权重 schema 归一（awq/gptq/quark/modelopt/autoround/compressed-tensors/fp8/mxfp4/bitnet） | **已合并**（`humming/schema/` 与 vLLM 侧 `compressed_tensors_get_config`） |
| 在线量化 / force requant | **已合并**（环境变量 + 代码路径存在） |
| Blackwell 隐藏格式（float4e0m3 / float8e3m4） | **已实现**（dtypes + mma 配置），**Rubin 不支持** |
| Autotune | **仍实验性/计划中**（`tune/candidate.py` 有候选生成，但博客把它列为未来工作） |
| 量化 All-to-All（EP 通信） | **计划中** |
| T-Head 玄武 810E | **已支持**；M890 等 **计划中** |
| Rubin Locality Domains 等 | **计划中** |

---

## 9. 对推理引擎插件化与跨硬件可维护性的启示

### 9.1 「量化描述」与「执行选择」分离，是插件化的关键抽象

Humming 最可迁移的不是 kernel 本身，而是**它给引擎出的那份契约**：

- 引擎侧只需要说清「这一层的权重怎么量化、激活怎么量化、这次要什么 GEMM 形态」；
- kernel 侧只需要说清「在什么设备、什么 tile、什么 pipeline 下怎么算」；
- 中间由 **schema（数据语义）+ config（执行参数）** 连接，两侧各自演进。

放到 vLLM 这类引擎上，同构的做法是：**把「后端」抽象成 `(语义描述, 执行参数)` 而不是「一整套 kernel 文件」**。`--linear-backend / --moe-backend` 正是这种接口形态：新增一个后端不应改变上层模型代码。

### 9.2 JIT + 内容寻址缓存，是「多格式 × 多设备」可维护的前提

因为 kernel 是按配置动态生成的，**缓存键必须包含所有影响生成的输入**：仓库里签名包含 kernel 表达式、编译 flag、源码、**以及所有 `.cuh` 的修改时间**，并用 FileLock + 原子替换保证并发安全。这给出一条可复用的工程规则：

> 动态生成的东西，缓存键必须覆盖「一切会影响输出的输入」；否则一次组件修改就会被旧缓存悄悄吞掉。

同时，「1.8 s 编译 vs CUTLASS 23.35 s」说明**轻量 CUDA 组件拼装**比模板实例化更适合「配置很多、每个配置用得少」的量化场景 —— 这是跨代硬件维护成本的关键变量。

### 9.3 架构特化要「按文件隔离」，不要「按 if 分支」

仓库把启发式按架构拆成独立文件（`sm75 / sm8x / sm90 / sm90_h20 / sm100 / sm120 / sm121 / ppu_sm80`），并且 `sm90_h20.py`、`sm90_policies.py` 单独拆出 H200/H20 差异。**这比在同一个巨型 switch 里塞条件更可维护**：新增一代硬件 = 新增一个文件 + 少量共享策略，而不是修改所有既有路径。

### 9.4 「一份统一格式 + 多个适配器」是接入成本的关键

`humming/schema/` 里十个导出格式适配器（awq/gptq/autoround/quark/modelopt/compressed-tensors/fp8/mxfp4/bitnet/gpt_oss_mxfp4）+ `KWARGS_ALIAS` 别名表，使得「换一个量化工具导出的 checkpoint」不需要新增 kernel。**这是把「生态碎片化」收敛到「一处适配」的标准做法**，对任何要支持多家量化 checkpoint 的推理框架都适用。

### 9.5 质量与性能的分离需要显式管理

Humming 提供了 batch-invariant 选项（`use_batch_invariant`：约束 reduction 与调优选择，使不同 batch size 下结果一致，代价是需要关掉 Stream-K、且 `warp_shape_k == block_shape_k`）。这说明**「换 kernel 会改变数值」是量化推理的常态**，引擎必须显式决定：要不要 batch invariance、要不要量化 A2A、精度损失是否可接受。**任何把「换后端」当作纯性能开关的接入方式都是危险的。**

### 9.6 对 EverAgent 自身的意义

- EverAgent 走托管 API，短期内不会自建 kernel 栈；但「**后端作为可替换 provider**」这一层抽象可以迁移：把不同模型/不同推理服务当作「语义相同、性能与成本不同」的 provider，用真实任务的 TTFT、每用户速率与成功率评估，而不是只看 tok/s。
- 「统一格式 + 多适配器」也迁移到 harness 层：上下文、工具 schema、记忆条目应该有**统一表示**，而不是每个子系统各自一套格式 —— 这与仓库把十种 checkpoint 格式收敛到一种标准格式是同构的问题。

---

## 10. Limitations

1. **所有性能数字均为项目方/社区自报**（博客 + vLLM 社区微基准 + 端到端 serving 表），**无独立第三方复现**；本文也未在任何 GPU 上运行 Humming。
2. **微基准图表的具体点值不可从正文取得**，本文只引用正文可唯一对应的数值；逐点数据需查 `benchmarks/results/<device>/` 产物。
3. **端到端表的口径缺项**：请求长度分布、输出长度、prefix caching 是否开启、投机解码、采样参数、调度策略、重复次数与误差条均未披露；「输入吞吐」与「输出吞吐」的百分比逐行相同，说明二者不是独立指标。
4. **端到端对照同时改变了激活精度**（BF16 → tokenwise FP8），收益未在 kernel 实现与数值格式之间拆分。
5. **MoE 微基准口径不含 EP 通信与调度**（只算 Gateup+Down GEMM 延迟），不能直接换算为端到端 MoE 加速。
6. **跨精度 baseline**：Hopper W4A8 面板以 DeepGEMM W8A8 为基线，含「权重搬运量减半」的物理优势。
7. **编译时间对比依赖「禁用缓存」这一条件**，且只测了单一 W4A16 kernel；CUTLASS 的编译成本高度依赖模板参数，不能泛化。
8. **未与 TensorRT-LLM、SGLang 等引擎做同口径对比**；也未与 Marlin/DeepGEMM/FlashInfer/Triton 在同一 shape 下统一排行。
9. **质量未评估**：Humming 的正确性门验证的是「实现符合自己定义的参考语义」（rtol 0.01 / atol 0.05），**不是**「模型输出质量与未量化一致」；W4A8 与 W4A16 的端到端质量差异在所用材料中无数据。
10. **autotune 尚未落地**，启发式在部分 shape 上未必最优；博客自己承认这一点。
11. **版本锚点漂移**：本文读取的仓库 commit 为 `db930afa2256cba49b3e46c0589323c3e80b0bfb`（2026-10-22），博客发布于 2026-10-21，其后仓库仍在快速迭代（当日已有多次提交，如 `fix(dtypes): cache dtype strings for torch.compile (#160)`、`fix(process_input): zero the unused groups of packed 8-bit input scales (#157)`）——**博客数字不一定对应今天的主分支**。
12. **包体口径不一致**：博客称 wheel「约 500 KB」，README 称「100+KB」；二者可能分别指 wheel 大小与安装后体积，官方未说明，引用时不应混用。
13. **文档与实现的成熟度差**：`docs/config.md` 是完整权威说明，但 `LayerConfig`/`ComputeConfig`/`TuningConfig` 的部分选项（尤其 `use_packed_k_layout`、`use_fused_e8m0_scale`）会**改变权重存储**，README 里未提示「改动必须重新 transform 权重」，容易误用。
14. **PPU 支持的深度未知**：仓库存在 `tune/ppu_sm80.py`，但博客对玄武 810E 的性能数据只有「已完全支持」的定性表述，没有量化格式矩阵与性能表。
15. 本文所有标注为 **[分析者推导]** 的结论（微基准 M 区间差异、输入/输出吞吐同比例、收益随并发上升的来源、包体口径差异）均为我的推断而非官方陈述。

---

## 11. 思考与追问

1. **Humming 到底省了多少维护成本？** 仓库有 ~30 个 Python 文件 + 13 个 tune 文件 + CUDA 组件。它替代的是「每个组合一个专用 kernel」，但**组件数量本身**也可能爆炸。是否存在可度量的指标（如「新增一种量化格式需要改几处代码」）？
2. **autotune 落地后，启发式还有价值吗？** 如果每个部署都在启动时实测候选配置，跨代硬件的「通用启发式」就退化为「起始点」，Humming 的可移植性优势会缩水到什么程度？
3. **「统一格式」会不会反过来限制创新？** 标准格式把 weight dtype、scale 粒度、zero-point 表达都参数化，但像 `float4e0m3` 这种硬件隐藏格式、以及未来新硬件的独有格式，是否仍能被这套参数空间自然表达？
4. **端到端 +43% 里，有多少是「少搬权重」而非「kernel 更聪明」？** 用同一激活精度（如都 W4A16 或都 W4A8）对比 Marlin/DeepGEMM，才能把实现收益与物理收益分开。
5. **MoE 的真实收益应该怎么算？** 微基准只算 Gateup+Down GEMM。EP all-to-all 在 1M 上下文、多专家、高并发下占比多少？博客把「量化 A2A」列为计划，说明这一段是当前缺口。
6. **batch invariance 的代价有多大？** `use_batch_invariant` 要求关 Stream-K、`warp_shape_k == block_shape_k`，这会削掉多少性能？对一个「同一请求在不同并发下结果应一致」有要求的 serving 场景，这个 trade-off 是否值得？
7. **能否把 Humming 的三配置契约直接搬成 vLLM 的 backend 插件规范？** 具体到：引擎侧要实现哪些接口、schema 由谁拥有、如何避免「每家后端各写一套参数」重新碎片化？
8. **质量侧怎么办？** 量化推理的真实风险不是速度而是精度漂移。仓库的 `rtol=0.01/atol=0.05` 是**实现级**门；是否需要一个「端到端任务级质量回归」随 kernel 版本一起跑？
9. **对个人/小规模部署是否可用？** README 说「任何能跑 PyTorch 2.7 的环境原则上都能跑 Humming」，但 SM75+ 与 CUDA 编译器是硬门槛；单机 8 卡级别的问题不会出现在这里，但**单卡小模型的量化推理**才是多数人的场景，Humming 的启发式与收益在那种形状下是否成立？
10. **与「引擎自带 kernel」路线的关系？** vLLM 已有 Marlin，Humming 是「社区通用库 + 引擎适配」；这个分工能否推广到 attention、MoE dispatch、采样等其它 kernel 密集区？

---

## 附录 A：来源清单

| ID | 来源 | 类型 | 用途 |
|---|---|---|---|
| S01 | vLLM Blog — *Announcing Humming: Fast, Flexible Kernels for Quantized Inference*（2026-10-21）`https://vllm.ai/blog/2026-10-21-humming` | 一手（项目方） | 问题定义、三层架构叙述、支持矩阵、全部性能数字、vLLM 用法、未来计划 |
| S02 | Humming 仓库 README（固定 commit `db930afa2256cba49b3e46c0589323c3e80b0bfb`）`https://raw.githubusercontent.com/vllm-project/humming/db930afa2256cba49b3e46c0589323c3e80b0bfb/README.md` | 一手（代码） | 激活×设备×权重类型支持矩阵、依赖与包体、用法示例 |
| S03 | `docs/config.md`（同一 commit）`https://raw.githubusercontent.com/vllm-project/humming/db930afa2256cba49b3e46c0589323c3e80b0bfb/docs/config.md` | 一手（代码） | 三配置语义、LayerConfig/ComputeConfig/TuningConfig 全量选项与约束 |
| S04 | `humming/schema/humming.py`（同一 commit） | 一手（代码） | Humming 标准格式的字段、别名机制、权重/scale 的物理存储与自动推导 |
| S05 | `humming/jit/compiler.py`（同一 commit） | 一手（代码） | JIT 签名、缓存键、FileLock、NVRTC/NVCC 后端 |
| S06 | `humming/testing/runner.py`（同一 commit） | 一手（代码） | 正确性门：参考实现、rtol/atol、outlier 统计、shape 覆盖门 |
| S07 | `humming/ops/gemm.py` 与 `humming/forward.py`（同一 commit） | 一手（代码） | 对外算子签名、`humming::prepare_kernels`、输入量化与 scale 生成路径 |
| S08 | `benchmarks/bench_humming.py` 与 `benchmarks/` 目录（同一 commit） | 一手（代码） | 微基准脚本口径、M 列表、候选配置分段调度、竞品对照脚本清单 |
| S09 | vLLM `main`：`vllm/model_executor/layers/quantization/humming.py` `https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/model_executor/layers/quantization/humming.py` | 一手（代码） | vLLM 侧集成实现：HummingConfig/LinearMethod/MoEMethod、min capability 75、在线量化与回退、padding、locks |
| S10 | vLLM `main`：`vllm/utils/humming.py` | 一手（代码） | 懒加载 facade（推迟 import humming 副作用） |
| S11 | Humming 仓库目录树与提交记录（GitHub API，commit `db930af`） | 一手（代码） | 模块结构、`schema/` 适配器清单、`tune/` 逐架构文件、`tests/` 与 `benchmarks/results/` 资产、近期提交（版本漂移证据） |
| S12 | vLLM 官方 API 文档 `humming` 工具页 `https://docs.vllm.ai/en/stable/api/vllm/utils/humming` | 官方文档 | vLLM 侧 `humming` 工具模块的官方说明位置（本文仅用于确认集成入口存在） |

**证据分级**：S01 是项目方的**叙述与自报数据**；S02–S11 是**可复核的一手代码证据**（本文实际读取，非仅凭博客转述）；S12 为官方文档入口。性能数字全部只有 S01 一个来源，故一律标注为自报。

---

## 附录 B：术语与安装/使用速查

**术语**：GEMM（通用矩阵乘）/ WnA8（权重 n bit、激活 8 bit）/ MXFP4、NVFP4（微缩放与 NVFP4 块缩放格式）/ DSA-free 的 MLA 无关；这里只需知道：低比特权重 + 低比特激活要求**每组一个 scale**（group/block/channel/tensor 四种粒度）。TMA（Tensor Memory Accelerator）/ WGMMA / UMMA / MXMMA（不同代 Tensor Core 指令路径）/ Stream-K（沿 K 维切分工作以平衡波次）/ warp specialization（加载与计算分派给不同线程）/ `cp.async`（异步拷贝）/ `use_packed_k_layout`（为 WGMMA 打包 K 维布局）/ `use_fused_e8m0_scale`（把 E8M0 组 scale 融进 FP4→FP8/INT8 转换）/ `use_int_weight_scale`（组 scale 转整数表示以加速 INT8/INT4 激活路径）。

**安装**：`pip install humming-kernels`；若系统无 CUDA 编译器则用 `humming-kernels[cu12]` / `[cu13]` 附带对应 CUDA 主版本的编译依赖。

**vLLM 用法**：

```bash
vllm serve deepseek-ai/DeepSeek-V4.1-Flash-1017 \
    --tensor-parallel-size 8 \
    --linear-backend humming --moe-backend humming

# 仅兼容路径（如 GPTQ INT3）：
vllm serve hfl/Qwen2.5-VL-3B-Instruct-GPTQ-Int3 --quantization humming

# 覆盖 MoE 激活类型：
vllm serve openai/gpt-oss-20b --moe-backend humming --quantization-config.moe.activation mxfp8
```

**Humming 直用**（README 示例）：

```python
from humming.layer import HummingLayer
layer = HummingLayer(shape_n=8192, shape_k=8192,
                      weight_config={"dtype": "int6"},
                      torch_dtype=torch.float16).cuda()
layer.load_from_unquantized(weight)   # 载入未量化权重
layer.transform()                      # 转换权重并准备默认 kernel
output = layer(inputs)                 # 量化 GEMM
```

> 以上代码与命令均转录自官方来源，本文未在本机执行（本次研究不具备 CUDA 硬件条件）。
