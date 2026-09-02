# Kernel Development Agent（KDA 同名梗）

> 概念 · 首次出现：2026-08-04（晚点聊177；张小珺152 未涉及——两期互补盲区的典型）

## 定义

用（早期）**checkpoint 编写、测试和优化 GPU kernel 的智能体**——与 Kimi Delta Attention 缩写撞名，晚点聊的"双 KDA 之问"："我很难说哪一个更伟大"。

## K3 报告中的设计（赵晨阳转述）

- **任务**：单算子优化、巨型算子融合；语言覆盖 CUDA/Triton/Thunder/TileLang 等；精度覆盖 BF16/FP8/FP4
- **两层 reward**：① PyTorch vanilla 版本既是性能底线又是**正确性基准**（数值超误差直接零分）② 与专家 kernel 对比分数——越接近硬件物理上限 reward 越高
- **作弊检测**：惩罚恶意 CUDA Graph 重放、"打表"式输入输出缓存投机
- K3 **早期 checkpoint**（未训完版本）已大规模承担 kernel 优化，甚至可能反哺后续训练速度

## 为什么 kernel 是 RSI 的先行领域

RSI 三条件：**便宜、可验证、难作弊**——kernel 全满足（跑一次硬件即验证、性能/正确性好验证、作弊方式有限且可检测）。赵晨阳："在有验证器的领域，RSI loop 已经在高速运作——这不是自我进化，是在清晰边界下不断自我提升，这正在发生。"RadixArk 团队自己也在用 AI 放大顶尖 kernel 工程师的理解（"某种程度上是 kernel 领域的 RSI"）。

## 产业含义

- AMD 朋友高强度依赖 kernel agent 写 kernel；英伟达内部 next-gen DSL 也大量依赖；摩尔线程极短时间 support K3——**两个 KDA 可能都在改变芯片生态**
- 与之对照：RSI 整体瓶颈在 **evaluation/harness**（曾致远）——不好评估的领域（写作、研究本身）还没有验证器
- 延伸：Muon 诞生于 Keller Jordan 的 nanoGPT Speedrun；RSI 公司（Tim Shi/田渊栋）系统化自动跑 Speedrun——优化器研究天然适合 auto research

## 引用本概念的报告

- [[2026-08-04_rss-wandian-latetalk_kimi-k3]]、[[2026-09-02_multi_kimi-k3-dueling-reads]]
