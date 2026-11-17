---
title: "GPU 发起 SDMA：把搬数据交给复制引擎，为什么还要核对阈值、完成语义和版本"
domain: "ai-learning"
report_type: "knowledge_report"
status: "completed"
report_depth: "deep"
source_url: "https://rocm.blogs.amd.com/software-tools-optimization/gpu-initiated-sdma/README.html"
source_published_on: "2026-11-13"
updated_on: "2026-11-17"
semantic_tags: ["sdma", "rccl", "rocshmem", "gpu-communication", "memory-ordering", "inference", "benchmark"]
---

# GPU 发起 SDMA：把搬数据交给复制引擎

一块 GPU 正在计算，另一块 GPU 等它传来数据。如果复制也由计算单元执行，两件事就会争用部分执行资源。AMD 这篇文章介绍的变化，是让正在运行的 GPU kernel 自己下发复制请求，由专门的 SDMA 引擎搬运数据。[原文](https://rocm.blogs.amd.com/software-tools-optimization/gpu-initiated-sdma/README.html)给出的亮点是：在八卡 MI350X 的指定大消息测试中，GPU 发起 SDMA 用一个 CU，就能取得接近或略高于默认 RCCL 使用 64 个 CU 时的带宽。

这个结果首先说明**通信可以少占计算资源**。它没有给出推理服务快 64 倍、能耗降低多少，或所有消息尺寸都会受益的证据。实际接入还要解决三个问题：消息何时值得交给 SDMA，复制何时真正完成，所用软件是否与实验版本相符。

本次核对还发现两项具体的复现差异：文章中 rocSHMEM 的 128 KiB 路径说明与其配置、固定源码不能完全对齐；AllGather 示例里的 `-D 3` 也不属于本次读取的公开 rccl-tests 默认分支参数。下面分别解释机制、结果和这些差异。

## 谁发起复制，与谁搬运数据，是两件事

CU 是 GPU 的计算单元，执行程序中的计算及 load/store 指令；SDMA 是独立的复制引擎。GPU 发起通信并不新，新增能力是在节点内通信时，让 GPU 下令、SDMA 搬运，而不是让 CU 执行整段复制。

| 方式 | 谁提交请求 | 谁搬运数据 | CU 主要承担什么 |
|---|---|---|---|
| GPU load/store | GPU kernel | CU | 逐段执行读取和写入 |
| Host-SDMA | CPU | SDMA 引擎 | 不执行这次复制的主体工作 |
| GPU-initiated SDMA | GPU kernel | SDMA 引擎 | 组织命令、提交和协调完成 |

这一区分也解释了为什么只说“异步复制”不够。CPU 发起的 `hipMemcpyAsync` 已经可以调用复制引擎；GPU 发起的接口则允许 kernel 根据自己刚算出的状态提交下一次传输，减少细粒度通信对主机调度的依赖。[AMD 原文的架构说明](https://rocm.blogs.amd.com/software-tools-optimization/gpu-initiated-sdma/README.html#architectural-perspective)

RCCL 提供集合通信，如 AllGather 将各参与者的数据收集到每个参与者，AlltoAll 则让每个参与者给其他参与者发送相应分片。rocSHMEM 提供 GPU 侧的远程内存操作及集合操作，`putnbi` 表示非阻塞、隐式完成的 put：提交数据传送后，还需按接口语义确认完成。

文章讨论的是 **scale-up 范围的节点内传输**。GIN 名称里有 Networking，不代表这项 SDMA 结果已经证明跨节点 RDMA 性能；同一通信库可以提供多个后端，选择哪个后端和数据实际经过哪条通路，要另外确认。

## 命令进入队列以后，还要处理可见性与完成

原文用环形队列和 doorbell 解释底层：软件把复制命令写入队列，再通知引擎消费。对普通使用者，RCCL-GIN 或 rocSHMEM 包装了描述符格式及队列操作。

在文章指定的 rocSHMEM 提交 `1b28700e0c9d6ce2e7e5917bb555181859e5f9da` 中，可以沿着实际代码看到这条路径：[GDA 的设备侧入口](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/gda/context_gda_device.cpp)先检查目标是否可走本地 IPC 路径，再进入 [IPC 复制策略](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/ipc_policy.hpp)，由尺寸阈值决定 SDMA 或 load/store。

```text
kernel 生成数据
      ↓
通信库检查目标和尺寸，选择复制路径
      ↓
SDMA 路径：发布数据 → 写命令队列 → 通知 doorbell
      ↓
引擎复制；CU 可在依赖允许时做别的工作
      ↓
确认完成及可见性 → 使用结果或复用缓冲区
```

这里不能省掉“发布数据”和“确认完成”。[sdma_policy.hpp](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/sdma_policy.hpp)在提交前使用 device scope 的 release fence；非阻塞操作还记录哪些通道有待完成工作。[anvil_device.hpp](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/sdma/anvil_device.hpp)处理队列写入、doorbell 和读指针轮询。它们说明数据与命令的内存顺序是实现的一部分，不能把“GPU 线程走到下一行”当作远端数据已经就绪。

对使用接口的人，更重要的是守住公开语义：[rocSHMEM 头文件](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/include/rocshmem/rocshmem.hpp)把 `fence` 定义为相关消息的顺序保证，把 `quiet` 定义为完成该 context 先前提交的操作。某个后端可能用等待完成来实现更强的顺序，但不能反过来依赖这种内部实现，把所有 fence 都当作 quiet。

一个常见错误是提交非阻塞复制后立刻改写源缓冲区，或让接收方看到一个无序的“完成”标记后立即读取。具体代码应使用库所要求的完成、通知和同步方式；普通 workgroup barrier 不能代替跨引擎、跨 GPU 的全部同步。本文没有提供绕过库接口的裸队列操作配方。

## 四张性能图回答的，其实是不同问题

以下结果均来自 [AMD 原文的性能部分](https://rocm.blogs.amd.com/software-tools-optimization/gpu-initiated-sdma/README.html#performance-evaluation)，是厂商测量，本文没有运行 MI350X 性能复现。

| 实验 | 原文比较条件 | 能从中读出什么 |
|---|---|---|
| RCCL AlltoAll，八卡 | 默认 load/store、Host-SDMA、GIN-SDMA；后两者使用对称内存注册 | 指定大消息下，SDMA 带宽接近或略高；GIN-SDMA 用一个 CU，默认算法用 64 个 CU |
| RCCL AllGather，八卡 | 同样三条路径 | 原文称从 512 KiB 起使用 GIN-SDMA，大消息显示资源占用优势 |
| rocSHMEM AlltoAll，八卡 | 都只用一个 CU；SDMA ON 为一个 wavefront，OFF 为 16 个 | 在 CU 预算被限制为一时，复制引擎能更充分使用通信带宽；不能据此说所有优化后的 OFF 配置都慢 |
| rocSHMEM putnbi，两卡 | 比较多种 CU / wavefront 配置 | 128 KiB 时一个 CU 的 ON/OFF 带宽相近，更多 CU 的 OFF 可以更高；从 512 KiB 起，ON 在所测配置中最高 |

RCCL AlltoAll 还有一个容易漏掉的条件：原文说 **消息大于 32 MiB** 时使用 GIN-SDMA，更小尺寸走向量 load/store。因此，图中名为 GIN-SDMA 的整条曲线，并不表示每个点都用了复制引擎。边界值 32 MiB 本身也不应擅自改写成“大于等于”。

这几组实验用了不同通信操作、参与 GPU 数量和资源配置。尤其是两卡 putnbi 的带宽，不能直接与八卡集合通信的 bus bandwidth 相除，得出库之间的优劣。Host-SDMA 和 GIN-SDMA 额外依赖对称内存注册，默认实现不依赖；它们比较的是整套实现配置，而不是只替换一个完全孤立的变量。

文章说重复了 5—7 次，因结果稳定而选取一组展示，没有给出所有运行值或波动区间。报告据此保留趋势和明确阈值，不从曲线估读小数带宽，也不制造均值、置信区间或端到端加速比。

## bus bandwidth 的分母和修正系数要看源码

本次读取了 `ROCm/rccl-tests` 的固定提交 `40b1b17901370a7880d4a56854b5361c89f8d324`。其中 [AlltoAllGetBw](https://github.com/ROCm/rccl-tests/blob/40b1b17901370a7880d4a56854b5361c89f8d324/src/alltoall.cu)与 [AllGatherGetBw](https://github.com/ROCm/rccl-tests/blob/40b1b17901370a7880d4a56854b5361c89f8d324/src/all_gather.cu)采用：

\[
B_{\mathrm{alg}}=\frac{\mathrm{count}\times\mathrm{typesize}\times P}{10^9\times t},\qquad
B_{\mathrm{bus}}=B_{\mathrm{alg}}\frac{P-1}{P}.
\]

这里 `count` 是传给操作的元素数，`typesize` 是每元素字节数，\(P\) 是参与 rank 数，\(t\) 是测得的秒数；带宽单位为十进制 GB/s。AllGather 中 `count` 对应每个参与者贡献的数据，AlltoAll 中对应发给每个参与者的数据分片。乘以 \(P\) 后是相应操作的逻辑数据量，再用 \((P-1)/P\) 修正本地份额。

八个 rank 时该系数为 **7/8**。例如算法带宽为 800 GB/s，按这段公式得到的 bus bandwidth 是 700 GB/s；这只是**自拟算例**，不是原文测量点。它说明 bus bandwidth 是根据操作语义计算的指标，不能直接当作机器所有物理链路吞吐之和。

文章没有给出 rccl-tests 的确切提交。上述源码用于解释已核实版本的计量口径，不能冒充已经找回原作者作图所用测试程序。

## 阈值核对：1024 不一定代表 1 KiB 消息

把小消息也交给 SDMA，可能花更多时间准备和协调队列，得不偿失。可以用一个简化模型理解这一点：复制时间约为固定启动成本 \(\alpha\) 加上数据量 \(S\) 除以有效带宽 \(B\)，即 \(T\approx\alpha+S/B\)。小消息中固定成本更显眼；大消息更容易摊薄它。这个关系用于解释阈值，不能不经测量就给出某台机器的最佳切换点。

rocSHMEM 的配置还多了一层单位转换。固定提交中的 [envvar.cpp](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/envvar.cpp)将 `ROCSHMEM_SDMA_THRESHOLD` 定义为字节阈值，并注明 wave/workgroup 操作会按 `WF_SIZE` 放大；[constmem.cpp](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/constmem.cpp)在启用 SDMA 时将环境变量值写入设备常量。实际 [IPC 策略](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/ipc_policy.hpp)比较的是：

- 单线程复制：`size >= threshold`。
- wave / workgroup 复制：`size >= threshold * WF_SIZE`。

按本文 MI350X 场景的 64 线程 wave 来算，workgroup 路径下 `threshold=1024` 对应 **64 KiB**，`threshold=2048` 对应 **128 KiB**。这些是源码条件的静态计算，前提是 SDMA 已启用、目标可走相应 IPC 路径。

原文 putnbi 命令采用 `-a wgputnbi` 和 `ROCSHMEM_SDMA_THRESHOLD=1024`，正文却说小于 128 KiB 的消息不使用 SDMA。沿已读取的 [GDA putmem_nbi_wg 路径](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/gda/context_gda_device.cpp)，满足 IPC 条件后会进入上述 workgroup 判断；**64 KiB 点究竟用了哪条路径，仅凭文章不能完全复原**。这可能涉及实际作图配置或版本差异，不能在没有运行记录时替作者确定原因。

此外，不能看到 `alltoall_wg` 后缀就给全部内部传输套同一个倍率。固定源码中的 [IPC AlltoAll 实现](https://github.com/ROCm/rocm-systems/blob/1b28700e0c9d6ce2e7e5917bb555181859e5f9da/projects/rocshmem/src/ipc/context_ipc_tmpl_device.hpp)，启用 SDMA 时会选择由线程分别执行 put 的分支。集合操作的整体消息量、内部每次 put 的尺寸、参与线程范围，必须逐层区分。

这不是说图中的大消息带宽结果必然错误，而是说“阈值是多少”“某一点为什么更快”需要比性能曲线更完整的配置证据。

## 版本与命令：公开资料还缺什么

原文把功能可用性放在 ROCm 10.1，并要求从源码构建。它同时列出了两套不同的测量环境：

| 项目 | 文中记录 |
|---|---|
| RCCL | `2.32.3-develop:d20dae4`，HIP `7.0.51831-b20d3d7ac`，ROCm `7.0.2.2.0-16-9428210`，Open MPI 4.1.8 |
| rocSHMEM | `v3.8.0` 的 GDA/RO/IPC/SDMA 组合，提交 `1b28700e0c9d6ce2e7e5917bb555181859e5f9da`，ROCm 10.1.0 |

两组都使用单机八张 MI350X，但服务器、CPU 和操作系统也不同。RCCL 的短提交已解析为 [d20dae4a07c1c2dc43fff47bfbe13e86386c9051](https://github.com/ROCm/rocm-systems/tree/d20dae4a07c1c2dc43fff47bfbe13e86386c9051/projects/rccl)。文章没有解释功能发布版本与这套 RCCL 测量软件栈之间的关系，因此不能把两栏合并成“统一在 ROCm 10.1 上测试”。

配置层面，原文要求 RCCL 使用对称内存注册与 `NCCL_CUMEM_ENABLE=1`，以 `NCCL_GIN_TYPE=7` 选择 SDMA；rocSHMEM 则同时涉及构建时 `-DUSE_SDMA=ON`、运行时 `ROCSHMEM_SDMA_ENABLED=1` 和消息阈值。只打开一个变量，不足以证明实际数据走了预期后端。

更具体的命令差异在 rccl-tests。文章的 AllGather 示例包含 `-D 3`；本次固定读取的默认分支 [common.cu 参数解析](https://github.com/ROCm/rccl-tests/blob/40b1b17901370a7880d4a56854b5361c89f8d324/src/common.cu)中，`getopt_long` 的短参数、长参数和分支都没有 `D`，虽然已有 `-R 2` 对称注册选项。没有作者实际使用的测试提交，就不能保证 clone 默认分支后原样运行该命令。删掉 `-D 3` 也可能改变所测实现，不能把“命令不报错”当成复现成功。

真正着手复现时，应先固定库和测试程序提交，确认二进制支持文章参数、实际选择的后端及消息路径，再比较带宽。现阶段公开材料足以研究机制和设计后续测试，还不足以让本文提供“已经验证、一键重现原图”的脚本。

## 留出 CU 之后，推理为什么仍可能没有变快

数据移动交给独立引擎，减少的是 CU 执行复制指令的负担。数据仍然经过显存及互连，队列、完成检查和消费者等待也仍有成本。因此，原文“减少资源竞争”的结论适合限定到所观察的执行资源，不能扩展成所有共享资源竞争都消失。

对推理应用，最关键的条件是：传输期间是否有独立计算可做。例如一个分片正在发送时，kernel 能否继续处理另一个不依赖传输结果的分片？如果下一步必须等全部数据到齐，节省 CU 不会自动缩短这段依赖。若本来就受显存带宽限制，计算与 SDMA 并行甚至可能继续争用同一数据通路。这些是根据资源与依赖关系作出的工程推断，原文没有用完整模型服务验证。

后续测试可以从实际工作负载切出一个生产者—传输—消费者片段，在同一任务上记录：

1. 结果是否正确，非阻塞传输后的读取、复用和通知是否符合语义。
2. 独立通信时的耗时、带宽，以及尺寸改变时实际经过的路径。
3. 与计算同时运行时，两者耗时和总完成时间如何变化。
4. 回到推理服务后，吞吐与尾延迟是否改善，注册及初始化成本如何摊销。

这比只比较一条“峰值带宽”曲线更接近应用问题。若带宽相近、通信占用的 CU 减少，而并行计算与服务时间也改善，才能把资源优势转为应用收益。

## 本次核验与来源范围

完整读取了 AMD 2026-11-13 原文，查阅了 ROCm 10.1 发布说明中与 SDMA 有关的条目，并读取上述固定提交的相关源码。原始 HTML 为 68,532 字节，SHA-256：`77a7f13010837bf3f4b497e83c348b9eecad17e64118c3cbf3197f8edc4607ea`。所有原文副本、源码快照与核对记录保存在仓外。

本次实际完成的是源码路径、阈值单位、参数存在性和带宽公式核对；静态算例确认 `1024×64=65536` 字节、`2048×64=131072` 字节，以及八 rank 的 `7/8` 修正。没有编译运行 RCCL/rocSHMEM，没有 MI350X 测量，也没有推理吞吐、延迟或能耗结果。文章四张性能图的趋势归作者测量，本文新增的价值是明确资源含义、同步条件及尚未对齐的复现信息。
