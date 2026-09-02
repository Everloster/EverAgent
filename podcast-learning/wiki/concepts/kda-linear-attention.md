# KDA（Kimi Delta Attention）与混合注意力

> 概念 · 首次出现：2026-08-04（晚点聊177）/ 2026-08-26（张小珺152）

## 定义

Kimi 的线性注意力：用**固定大小循环状态**压缩历史信息（复杂度线性），chunk 内并行、chunk 间串行递推。K3 主干：69 层 KDA + 24 层 Gated MLA（≈3:1，末层必为 MLA）。

## 谱系（孙宇涛领读版：每一步解决什么）

1. **线性注意力原型**：K、V 外积求和——无衰减，记忆互相干扰
2. **RetNet**：引入位置衰减（语言 recency 特性）+ **chunk recurrent 计算形式**（chunk 内打满 Tensor Core、chunk 间递归）——此后所有高效线性注意力的计算范式
3. **Mamba**：位置无关→位置有关衰减
4. **DeltaNet**：delta rule"精确覆写"，相同 KV cache 下提高上下文容量
5. **Gated DeltaNet**（NVIDIA，杨松林）：合并门控衰减与 delta rule，解决 GPU chunkwise 并行
6. **KDA**：衰减从 head 内标量细化为 **channel-wise**（逐通道，严格更强），代价是 kernel 更难写

## co-design 精髓

**decay 下界是从 kernelize 效率反推的**：仿 RoPE"绝对位置表示相对位置"，对 Q、K 做衰减倒数变换；须保证 16-token tile 内衰减不超 **BF16 动态范围**——由此反解衰减系数上限。算法参数由硬件约束决定。

## 推理系统工程连锁（赵晨阳第一手）

- 前缀缓存从 **Append-Only"只往后写的笔记本"变成"反复擦写的白板"**：每 token 驻留固定大小缓存反复覆写；SGLang 借 copy-on-write/snapshot/donate OS 原语跨请求安全共享（防边写边读前对后错）
- 投机采样：不存状态、只存每步约 **1KB 投影**，回退从 checkpoint 重放（象棋记谱而非每步快照）
- 1M 上下文：69 层 KDA 仅 54MB 固定状态；6.3 倍解码加速（**出自 Kimi Linear 论文，非 K3 报告**）
- Flash KDA：基于 CUTLASS 重叠 chunk 内计算与跨 chunk 状态传输；kernel 需管理状态全生命周期，模糊 kernel 与缓存管理界限
- 遗忘问题：固定 recurrent state 容量瓶颈，Delta Rule/Channel-wise Forget Gate 只是更聪明地管理有限记忆；真正缓解靠 MLA 层保留全局交互

## 关键论断

- "混合注意力在工程上是 trade-off，在模型表现上**不是** trade-off"（孙宇涛）
- 加速比与混合比成正比：3:1 → 上限约 4 倍（常数级）
- 3:1 来自 Kim Linear（约 48B/16 层）empirical ablation，直接放大 60 倍到 3T——"不一定是 3T 上的最优解"（晚点聊）

## 引用本概念的报告

- [[2026-08-26_xiaoyuzhou-zhangxiaojun_kimi-k3-report]]、[[2026-08-04_rss-wandian-latetalk_kimi-k3]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]
