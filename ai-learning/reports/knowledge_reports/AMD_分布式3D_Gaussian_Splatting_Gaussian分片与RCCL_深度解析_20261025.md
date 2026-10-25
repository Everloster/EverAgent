---
title: "AMD 分布式 3D Gaussian Splatting：Gaussian 分片、RCCL 通信与扩展口径"
domain: "ai-learning"
report_type: "概念深度解析"
status: "completed"
updated_on: "2026-10-25"
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "deep"
reader_contract: "standalone"
semantic_tags: ["3d-gaussian-splatting", "distributed-training", "gsplat", "RCCL", "MI300X", "all-to-all", "Grendel"]
---

# AMD 分布式 3D Gaussian Splatting：Gaussian 分片、RCCL 通信与扩展口径

## 一句话结论

gsplat 通过“Gaussian 分片持有、投影后按相机路由、再反向回传梯度”的方式，把普通数据并行无法提供的容量扩展能力引入 3DGS：主通信是方向性 `all_to_all`，Gaussian 梯度不执行 `all_reduce`；但默认稠密交换仍可能成为通信瓶颈，理论显存上限也不等于实际可训练规模。

## 来源与证据等级

- [AMD ROCm 官方技术博客](https://rocm.blogs.amd.com/software-tools-optimization/scaling-gsplat/README.html)
- [ROCm/gsplat 公开仓库](https://github.com/ROCm/gsplat)
- [Grendel：On Scaling Up 3D Gaussian Splatting Training](https://arxiv.org/abs/2406.18533)

- **代码事实（直接证据）**：原文引用了 `gsplat/rendering.py`、`gsplat/distributed.py` 和 `examples/simple_trainer.py`。分片使用 `points[world_rank::world_size]`，发生在参数与 Adam 状态创建之前；通信由可微 `all_to_all`、相机 `all_gather` 及可选辅助模块 DDP 实现。
- **解析推导（可复算）**：按 `float32` 计算，SH degree 3 时每个 Gaussian 有 59 个可学习参数；加上 Adam 一、二阶矩共 118 个状态量，合计 708 字节。MI300X 的 271M 和八卡 2.17B 均由此推导。
- **厂商材料与自测（有限证据）**：原文属于 gsplat/AMD 技术文章，并称使用 `rocprofv3` 检查过真实四卡运行；所给片段没有完整 trace 原始数据或独立复现实验，因此四卡观察不能直接外推至八卡或真实生产负载。
- **论文证据边界**：Grendel 论文提供了另一套分布式 3DGS 结果，但不是 AMD gsplat 四卡实现的同硬件复现。L1 与 D-SSIM 损失、Adam 和动态致密化机制有代码与公式支持；AMD 性能结论仍应视为实现方材料。

## 一、3DGS为什么先撞内存墙

3DGS 没有一个固定规模、可跨数据集泛化的网络；场景本身就是一组各向异性 Gaussian。每个 primitive 包含三维中心 \(\mu\)、由 scale 与 quaternion 表示的协方差 \(\Sigma\)、球谐颜色 \(c\) 和不透明度 \(\alpha\)。在 SH degree 2 下共有 38 个参数、152 字节；加 Adam 的一阶、二阶矩后为 114 个数、456 字节。gsplat 默认 SH degree 3，颜色变为每通道 16 个系数，因此达到 59 个参数、236 字节；再加 Adam 状态为 708 字节。

这解释了理论上限：MI300X 的 192 GB HBM3 在默认 SH degree 3 下只能容纳约 **271M** 个 Gaussian；八张 MI300X 的聚合显存对应约 **2.17B**；SH degree 2 的单卡上限则约为 421M。必须强调，271M 与 2.17B **仅是参数和 Adam 状态的理论线，明确排除了梯度缓冲区以及按 tile 排序的 Gaussian—pixel intersection buffer**，实际 OOM 会更早发生。

完整训练步还需要参数、梯度、Adam 状态和前向激活。3DGS 的激活不是固定网络中间层，而是随分辨率和场景密度增长的相交列表；4K 下它往往比参数更早触发 OOM。致密化又使参数规模持续变化：每约一百步依据累计二维位置梯度 clone、split、prune Gaussian。因而单纯增加显存只能延后容量上限，不能解决吞吐、单总线渲染延迟，也不能避免为了装入显存而降低致密化强度造成的细节损失。

## 二、为什么普通DDP解决不了

标准 DDP 每卡保存完整参数和 Adam 状态，处理不同输入，局部反向得到不同梯度，再对梯度执行 `all_reduce`，最后各卡执行相同优化器更新。它提高吞吐量，却不提高单模型容量；每个 rank 仍需容纳整个场景。FSDP、ZeRO 虽能分片参数和优化器状态，但 gsplat 还需要利用“Gaussian 只影响能看见它的相机”这一稀疏、视角相关关系进行定向路由。

gsplat 虽有 L1 加 D-SSIM 损失，梯度也会传回 \(\mu,\Sigma,c,\alpha\)，但 Gaussian 梯度**不做平均**：每个 Gaussian 只存在于一个 owner rank，没有可供全场景平均的同构副本。其参数还会在训练中增删，普通 DDP 所依赖的静态参数集合不再成立；各相机可见 Gaussian 数量高度不均，也使负载随视角和致密化过程变化。

因此每卡只持有互不相交的 Gaussian 分片，Adam 和 densification 均在本分片执行。DDP 仅用于体量较小且各卡需要副本的可选相机位姿优化器、扰动模块和外观 embedding；若关闭默认的 `pose_opt`、`app_opt`，训练循环中不存在任何可学习参数的 `all_reduce`。

## 三、Gaussian分片到camera并行的一次完整迭代

初始化时，各 rank 以跨步轮转方式切分点云、颜色和 scale。切分发生在参数及优化器构造之前，因此每卡只分配约 \(N/\text{world\_size}\) 个 Gaussian 的参数和 Adam 状态；它不是空间分片，相邻点也可能位于不同卡。相机则由各 rank 使用不同随机种子的 DataLoader 独立抽取。

一次多卡迭代按以下路径推进：

1. **Gaussian-parallel**：先用小型 `all_gather` 交换各卡 Gaussian 数量，建立本地与全局索引偏移；再 `all_gather` 全部相机的 view matrix 和内参。随后每卡仅以本地 Gaussian 分片对全局相机执行投影，生成二维均值、深度、conic、半径和可见性掩码。SH 也先在 owner 卡上求值：SH degree 3 的 48 个系数不跨网传输，真正交换的仅是三个颜色通道。
2. **all_to_all**：每卡按“目标相机由谁负责”计算发送量，把可见的 Gaussian 投影记录定向送往对应 rank。`packed=True` 只交换真实相交的 `(camera, Gaussian)` 记录；默认 `packed=False` 则发送稠密 `[C,N]` 数据，包括不可见项。稠密路径每 rank 每次约发送 \(48N_rC_{\text{local}}(W-1)\) 字节：四卡、每卡 2M Gaussian 且每卡一相机时，每方向可达数百 MB。`packed` 将发送量替换为实际可见数量，通常显著更省，但会增加索引重映射步骤。
3. **camera-parallel**：接收后，每卡持有渲染本地相机所需的全部记录，独立完成 rasterization，再计算本地 L1、D-SSIM 及可选深度或正则损失。相机侧不保存持久状态；参数、Adam 和 densification 始终留在 Gaussian 侧。
4. **梯度返回**：可微 `all_to_all` 在反向时执行反向交换，将每个 Gaussian 的梯度贡献送回其唯一 owner，而不是在所有卡之间求平均。相机 `all_gather` 的反向对应 `reduce-scatter`，用于汇总相机位姿梯度；只有启用的辅助模块才由 DDP 再做 `all_reduce`。
5. **本地更新**：各卡对自己的 Gaussian 分片执行 Adam，再依据二维梯度进行 clone、split 和 prune，不跨卡同步。由此形成完整闭环：**Gaussian-parallel → all_to_all → camera-parallel → 梯度反向返回 → 本地 Adam 与 densification**。

## 四、4 GPU trace：五次 collective 与零训练期 all-reduce

这组数字只覆盖原文的单节点四 GPU 轨迹：一张卡一个 rank，默认 dense 路径、`packed=False`，每个 rank 每步处理一台相机；前 60 步尚未触发 densification，四个分片稳定在 13569、13569、13569 和 13568 个 Gaussian。

| 次序 | collective | 阶段 | 代表迭代 GPU 时间 |
|---:|---|---|---:|
| 1 | `all_gather` Gaussian 分片大小 | rasterize | 0.51 ms |
| 2 | `all_gather` 相机 view matrix 与 intrinsics | rasterize | 0.12 ms |
| 3 | `all_to_all` radii | rasterize | 0.43 ms |
| 4 | `all_to_all` projected records | rasterize | 0.34 ms |
| 5 | `all_to_all` Gaussian gradients | backward | 0.46 ms |

“投影记录”虽然包含 `means2d`、`depths`、`conics`、`opacities` 和 `colors` 五类张量，helper 会先拼成一个 buffer，因此在 trace 中仍是一组 grouped `all_to_all`，不是五次独立通信。Radii 不需要梯度，只有可微的 projected records 在反向中产生转置 `all_to_all`。表中逐项数值来自一个代表迭代；原文另给出的 1.64 ms 是稳态跨 rank 平均的 collective 总时长，两种统计口径不能直接混算。

“零训练期 all-reduce”也有严格边界：34.7 秒 capture 中，每个 rank 只出现一次 `ncclAllReduce`，耗时 66 微秒，位置在最后一个训练步之后的 evaluation/shutdown；60 个训练迭代里没有场景参数 all-reduce。若启用由 DDP 包装的位姿或外观辅助模块，仍可能产生小规模 all-reduce，因此这不是“所有配置永远没有 all-reduce”。

## 五、17.70 毫秒真正花在哪里

原文对四个 rank 的第 11 至 60 步取平均，稳态每步 17.70 ms：

| 组成 | 时间 | 占比 |
|---|---:|---:|
| SSIM loss 的 MIOpen 卷积 | 5.88 ms | 33% |
| gsplat 投影、SH、相交与 rasterize kernel | 2.23 ms | 13% |
| RCCL collective | 1.64 ms | 9% |
| 其它 PyTorch elementwise/reduction/copy | 1.68 ms | 9% |
| Adam | 0.83 ms | 5% |
| tile-Gaussian key 的 radix sort/scan | 0.25 ms | 1% |
| GPU 无任务排队 | 5.19 ms | 29% |

四卡合计吞吐为 226 images/s，中位迭代 17.4 ms，90% 的迭代不超过 18.7 ms。最显眼的瓶颈不是 RCCL：SSIM 使用两次约 2.9 ms 的 MIOpen Winograd convolution，耗时超过 renderer 两倍；GPU 另有 29% 时间无任务排队，说明单 rank 单相机时 Python 与 kernel launch 间隙没有被更大工作覆盖。RCCL 在这个小场景只占 9%，但交换仍位于关键路径且没有和计算重叠。

步时相近也不代表负载相同：四个 rank 的平均步时只差 0.8%，tile-Gaussian intersection 数却相差 4.3 倍，通信时间相差 2.1 倍；同步会把不平衡隐藏成等待。上述比例只适用于这次小场景、四卡、dense exchange 的厂商 trace，不能当作大规模生产场景的固定预算。

## 六、1到8 GPU扩展数字该怎样读

读扩展数字时，必须分开“单步耗时、总墙钟时间、总算力吞吐、训练样本量”。MI300X 上，单卡每个 rank 占用 12.5 GB，8 卡时降至 4.2 GB。原因是参数和 Adam 状态按 rank 分片，每 rank 显存约等于总显存除以 world size；这是近似关系，4.2 GB 并不是严格的 12.5/8。相应地，每 rank 的 Gaussian 数下降，而作业可容纳的 Gaussian 总数随 GPU 数大致线性增加。这首先是容量收益，而不是墙钟加速。

1 卡 20 分钟、8 卡 16 分钟若直接相除，只得到 1.25 倍的“相同步数时间比”；但这些运行沿用默认 `max_steps`，没有使用 `--steps_scaler`。每步每个 rank 都读取自己的视图，因此 8 卡处理了单卡 8 倍的图像。按吞吐计算为：

`8 ÷ (16/20) ≈ 10`

所以提升约为 10 倍，而不是 1.25 倍。2 卡反而比单卡慢，是因为它完整支付了进程组建立、逐步 `all_gather`、`all_to_all` 和索引重基等固定成本，却只取得了约 2 倍图像消费增量。

RCCL/xGMI 利用也不能按卡数简单线性外推。2 卡只激活节点 xGMI 链路的一小部分；原文未给出 2、4 卡各自的精确链路占比，不能杜撰。4 卡 trace 中通信仅占迭代时间的 9%，loss 占 33%，另有 29% 时间 GPU 空闲；默认 dense exchange 还会把每个 local Gaussian 发给每个 peer，无论是否可见，`--packed` 可修正这一点。因此应先 profile，不能仅因通信“看起来昂贵”就归咎互联链路。全 8 卡参与时，RCCL collective 的效率最好，8 卡不仅通信更多，链路利用也更充分。

短基准还受启动成本主导：首迭代平均 8.14 秒、最慢 rank 为 9.50 秒，其中 3.42 秒在 RCCL device kernel 内建立连接、channel 和 buffer；`ncclCommInitRankConfig` 每 rank 耗时 2.6 秒，销毁再用 220 毫秒。迭代 1—10 共耗时 8.31 秒，而迭代 11—60 仅 0.88 秒。因此比较 world size 应至少丢弃前十步，测量不足几百步基本是在测 RCCL bootstrap。

## 七、batch、steps_scaler与超参数缩放

gsplat 默认 `batch_size=1`，即每个 rank 每步读取一个相机视图。设局部 batch 为 \(b\)、world size 为 \(N\)，则全局 batch 为 \(BS=bN\)。增大 \(b\) 可让每个 rank 完成更多有用的 rasterization 工作，从而摊薄固定 exchange 成本。

源码自动将学习率缩放为原值的 \(\sqrt{BS}\)，即 \(lr\sqrt{bN}\)；因此局部 batch 不变时，\(N\) 卡对应约 \(\sqrt N\) 倍学习率，而全局口径始终是 \(\sqrt{bN}\)，不是 \(\sqrt{b/N}\)。这不是 SGD 常用的线性规则，因为 Adam 已通过二阶矩估计的平方根吸收了部分 batch 效应。

同一机制令 Adam 的 `eps=1e-15/√BS`，并把动量系数改为 `(1−0.1BS, 1−0.001BS)`，使 batch 越大时优化器越少依赖历史。注意 \(BS=10\) 时 `beta1` 会降为零，这是源码标明的退化限制，大有效 batch 需谨慎使用。

学习率计划、评估与保存及 PLY 间隔、SH degree 间隔，以及 densification 的起止、reset 和 refine 周期均以 step 表示。增加 GPU 而保持 `max_steps`，会让作业消费 \(N\) 倍图像；`--steps_scaler` 以同一个 factor 同步修改这些 step 参数。要让 \(N\) 卡与单卡消费相同图像数，应设 factor 为 \(1/N\)，例如 4 卡使用 `0.25`。若保持固定 steps，则目标应是提升容量和吞吐、训练更多图像，而不是宣称得到同一结果。

## 八、与Grendel论文的关系

AMD 的 gsplat 分布式实现与 Grendel 论文存在技术谱系关系，但不是同一方案。AMD 版本采用混合并行：高斯参数以步长轮转方式分片且不复制，投影阶段覆盖全部相机，随后通过 `all_to_all` 将投影记录送往拥有目标相机的 rank；光栅化和损失按相机并行，梯度沿同一交换的转置返回。场景参数不做 all-reduce，DDP 仅覆盖较小的位姿和外观模块，通信由 RCCL 经 xGMI 承载。

Grendel 论文明确采用稀疏 all-to-all，只把高斯送往与其实际相交的像素分区，并实施动态负载均衡；它还支持多视图 batch，并发现按 `sqrt(batch size)` 缩放超参数较为有效。因此，AMD 实现中“按相机归属交换”不能等同于 Grendel 的“按像素稀疏交换加动态均衡”。AMD 多 GPU 策略引用该论文，只能说明渊源，不代表实现或性能相同。

评测口径同样必须分开。Grendel 在 Rubble 数据集报告：将 **40.4M** 高斯分布到 **16 张 GPU**，测试 PSNR 为 **27.28**；单卡使用 **11.2M** 高斯时为 **26.28**。这是论文结果，并非 AMD 四卡案例的复现。AMD 博客的四卡轨迹以及 README 所称“最高 4× 更少显存、最高快 15%”均属厂商材料，**不是第三方 benchmark**，不能与上述 PSNR 结果拼接为同口径比较。

## 九、已知限制与适用场景

AMD 当前分布式模式存在明确边界：

- `absgrad=True` 会触发断言，不支持分布式 AbsGrad；AbsGS 致密化仅限单 GPU。
- 分布式仅允许逐高斯颜色；逐相机颜色张量及新版 `batch_dims` 接口均会被拒绝。
- 分片从不重平衡。致密化完全在本地执行，场景密集区域所在 rank 会积累更多高斯与计算量，最慢 rank 决定每一步速度。
- 没有像素级负载均衡，工作按 camera 粒度划分。细节密集视图与天空视图负载差异明显；厂商轨迹中 tile-Gaussian 交点数相差 **4.3 倍**，各 rank 通信时间相差 **2.1 倍**，只能由多步平均缓解。
- 通信完全暴露在高斯交换的关键路径上，不能像 DDP 梯度 all-reduce 那样与计算重叠；轨迹中没有 kernel 并发。
- 交互式 viewer 不可用。

其适合场景包括城市、工业园区和遗产等超单卡容量的大型数字孪生，不能接受裁剪的 VR/AR 细节流媒体、全分辨率影视特效，以及需要缩短大路测语料迭代周期的自动驾驶训练。但采用前必须确认不依赖 AbsGrad、逐相机颜色、`batch_dims` 和 viewer。

## 十、对EverAgent与分布式评测的启示

EverAgent 的分布式评测应把**容量、渲染质量、吞吐、实际墙钟时间和使用能力**分开报告，而不能以“已支持多 GPU”替代性能结论。基准应固定数据集、相机 batch、训练步数、硬件和质量指标，分别比较单卡、AMD gsplat 与 Grendel；同时记录高斯数量、峰值显存、PSNR/SSIM/LPIPS、每步耗时、通信占比、最大/平均 rank 负载及冷启动开销。

AMD 四卡厂商轨迹还显示，每次迭代有五次 collective，包括两次 metadata all-gather 和三次 grouped all-to-all；通信占迭代时间 **9%**，但仍位于关键路径且无 kernel 并发，GPU 另有 **29%** 时间无任务排队。六十步中 **90%** 的墙钟时间用于前十步的 RCCL 初始化。因此评测应分别报告冷启动与稳态，并明确“容量扩展”不等于“单步加速”。README 的显存和速度宣称也应标为厂商自测，而非第三方结论。

## 反方解释

AMD gsplat 未体现 Grendel 的同等质量或扩展效率，不能直接证明 Grendel 在所有硬件和实现上更优；两者的工作负载、相机划分和调度机制并不相同。反过来，Grendel 的 **27.28 对 26.28** 同时伴随 **40.4M/16 GPU 对 11.2M/单卡** 的模型规模变化，故这 **1.00 dB** 增益不能全部归因于分布式通信或调度算法。AMD 实现即使墙钟收益有限，仍可能通过分片降低参数与优化器显存占用，从而获得单卡无法容纳的训练容量。

## Limitations

现有材料只能支持有限比较：Grendel 片段给出论文摘要级结果，未提供足以复现实验的完整设置、硬件明细和消融；AMD 博客与 README 均为厂商自测，不是独立 benchmark。两者尚无同硬件、同数据、同相机 batch、同高斯预算和同训练步数的受控对照。因而不能据此宣称 AMD gsplat 达到或超过 Grendel，也不能把 AMD 的四卡通信占比直接外推到 Grendel 的像素分区实现。

## 思考与追问

EverAgent 的目标工作负载是否必须使用 AbsGrad、逐相机颜色或多视图 `batch_dims`？若必须，AMD 分布式路径是否应被排除，还是需要先补齐功能？评测能否在高斯数量固定时比较质量，从而分离模型容量与调度收益？此外，是否值得为像素级动态均衡增加通信复杂度？通信与投影或光栅化能否实现真实重叠，而非仅报告 collective 的时间占比？

## 最终结论

AMD 厂商材料展示了 gsplat 可在 ROCm/MI300X 上以混合并行扩展高斯容量，但其实现是 camera 粒度、无分片重平衡、通信暴露且功能受限，不能与 Grendel 的稀疏 all-to-all 和动态负载均衡混称。Grendel 论文的明确结果是 **40.4M、16 GPU、PSNR 27.28** 优于 **11.2M、单卡、26.28**；AMD 厂商博客和 README 则不能充当第三方 benchmark。对 EverAgent 最有价值的结论不是立即宣称某方案胜出，而是建立功能矩阵、质量控制实验、稳态与冷启动分离、逐 rank 负载分析和端到端墙钟评测。
