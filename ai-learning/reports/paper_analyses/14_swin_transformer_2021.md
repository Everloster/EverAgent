---
title: "Swin Transformer — Hierarchical Vision Transformer (2021) 深度分析"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-03-26"
---

# 13 | Swin Transformer: Hierarchical Vision Transformer using Shifted Windows (2021) 分析报告

**作者**：Ze Liu, Yutong Lin, Yue Cao, Han Hu, Yixuan Wei, Zheng Zhang, Stephen Lin, Baining Guo（微软亚洲研究院）
**年份**：2021
**发表**：ICCV 2021 Best Paper（Marr Prize）
**分析日期**：2026-03-26
**阅读难度**：⭐⭐⭐⭐

---

## TL;DR（一段话总结）

Swin Transformer 是微软亚研院对 ViT 的关键改进，通过引入**层次化特征图**和**滑动窗口注意力（Shifted Window Attention）**，将 Transformer 的计算复杂度从图像像素数的平方降为线性，同时恢复了 CNN 的多尺度特征层次结构。它在图像分类、目标检测、语义分割三大视觉任务上全面超越 ViT 和 ResNet，成为 2021 年最具影响力的通用视觉骨干网络，并拿下 ICCV 2021 最佳论文。

---

## Step 1 | 背景与问题

### 历史节点

ViT（2020）证明了纯 Transformer 可以做图像分类，但它存在两个根本性的工程缺陷：

1. **计算复杂度随图像尺寸平方增长**：ViT 在所有 patch 之间计算全局 Self-Attention，196 个 patch（224×224 图像）已经勉强可行，但分辨率翻倍就会爆炸（784²次注意力计算）。
2. **单一尺度，无层次结构**：ViT 始终保持 14×14 的 patch 分辨率，缺乏 CNN 的从低级纹理到高级语义的多尺度特征金字塔。目标检测、分割等密集预测任务严重依赖多尺度特征（FPN），ViT 天然不支持。

**一句话问题**：如何让 Transformer 既保持全局建模能力，又能高效处理大分辨率图像并支持多尺度密集预测任务？

### 前人方案的局限

| 方案 | 局限 |
|------|------|
| ViT（原版） | O(N²) 全局注意力，无多尺度，分辨率受限 |
| DeiT（2021） | 改进 ViT 训练策略，但架构缺陷未解决 |
| ResNet（CNN） | 有多尺度，但全局感受野弱，需深堆叠 |
| Non-local Networks | CNN + 全局 Attention，计算仍昂贵 |

### 论文核心主张

> 通过**局部窗口注意力** + **跨窗口移位机制（Shifted Window）** + **Patch Merging**，构建一个**线性复杂度、层次化**的通用视觉 Transformer 骨干，在分类、检测、分割三大任务上统一超越 CNN。

---

## Step 2 | 技术方案

### 2.1 层次化架构（Hierarchical Feature Maps）

Swin Transformer 将网络分为 4 个 Stage，每个 Stage 经过一次 **Patch Merging**（类似池化），分辨率逐步减半，通道数翻倍：

```
输入 224×224
Stage 1: 56×56 × 96C   → Patch Partition（4×4 patch）+ 2 Swin Blocks
Stage 2: 28×28 × 192C  → Patch Merging + 2 Swin Blocks
Stage 3: 14×14 × 384C  → Patch Merging + 6 Swin Blocks（最多计算在此）
Stage 4:  7×7  × 768C  → Patch Merging + 2 Swin Blocks
```

这与 ResNet 的 {C2, C3, C4, C5} 特征图完全对齐，可以直接接 FPN 做目标检测/分割，是 Swin 能做"通用骨干"的关键。

### 2.2 窗口内 Self-Attention（W-MSA）

将 H×W 的特征图划分为 M×M 大小的**非重叠局部窗口**（M=7 为默认），每个窗口内部独立计算 Multi-Head Self-Attention：

```
全局注意力复杂度: O(N²·d) = O((HW)²·d)  → ViT
窗口注意力复杂度: O(M²·M²·d · HW/M²) = O(M²·HW·d)  → Swin（线性！）
```

当图像分辨率翻倍（H,W→2H,2W），计算量仅翻 4 倍，而 ViT 翻 16 倍。

**代价**：窗口之间没有信息交换——局部窗口是孤立的，失去了 Transformer 的全局建模能力。

### 2.3 核心创新：移位窗口（Shifted Window，SW-MSA）

Swin 交替使用两种 Block：

- **偶数层**：标准窗口划分（W-MSA）
- **奇数层**：将窗口整体移位（⌊M/2⌋, ⌊M/2⌋），即 SW-MSA

```
原始窗口划分（W-MSA）:
[A|B]    窗口 A 和 B 之间无交互
[C|D]    窗口 C 和 D 之间无交互

移位后（SW-MSA）:
A 的右边 ↔ B 的左边 现在在同一窗口中
C 的下面 ↔ A 的上面 现在在同一窗口中
```

通过移位，相邻窗口的边界 patch 在下一层就能建立连接，形成跨窗口的全局感受野，但**每层仍保持 O(HW) 线性复杂度**。

**循环移位 + Masking 优化**：直接移位会产生大小不均的窗口，论文用循环移位将图像卷绕，使所有窗口保持 M×M，然后用 Attention Mask 遮蔽不相邻区域的注意力，等价于非均匀窗口但更高效。

### 2.4 相对位置偏置（Relative Position Bias）

不同于 ViT 的绝对位置嵌入，Swin 在 Attention 计算中加入可学习的**相对位置偏置矩阵 B**：

```
Attention(Q, K, V) = SoftMax(QKᵀ/√d + B) · V
```

其中 B 是形状为 (2M-1)×(2M-1) 的可学习矩阵，表达两个 patch 的相对位移。实验表明，相对位置偏置比绝对位置嵌入提升约 +1.2% 精度，且在不同分辨率间迁移性更好。

---

## Step 3 | 关键实验与结论

### ImageNet-1K 图像分类

| 模型 | 参数量 | Top-1 Acc |
|------|--------|-----------|
| ResNet-50 | 25M | 76.2% |
| DeiT-B/16 | 86M | 81.8% |
| **Swin-T** | **28M** | **81.3%** |
| **Swin-B** | **88M** | **83.5%** |
| **Swin-L（ImageNet-22K预训练）** | **197M** | **87.3%** |

Swin-T 以接近 ResNet-50 的参数量超越 DeiT-B，说明架构效率极高。

### COCO 目标检测（Cascade Mask R-CNN）

| Backbone | box AP | mask AP |
|----------|--------|---------|
| ResNet-50 | 46.3 | 40.1 |
| ResNet-101 | 48.1 | 41.5 |
| **Swin-T** | **50.5** | **43.7** |
| **Swin-B** | **51.9** | **45.0** |

Swin 作为检测骨干比 ResNet-101 高出约 +4 box AP，充分发挥多尺度层次结构优势。

### ADE20K 语义分割

| Backbone | mIoU |
|----------|------|
| ResNet-101 | 44.9 |
| **Swin-T** | **44.5** |
| **Swin-B** | **48.1** |
| **Swin-L（22K预训练）** | **53.5** |

在语义分割任务中，大型 Swin 模型远超 ResNet，验证了多尺度特征的价值。

---

## Step 4 | 核心洞察与历史意义

### 4.1 为什么 Shifted Window 有效？

从感受野理论看：
- 每层 W-MSA：每个 patch 感知 M×M=49 个 patch（7×7 窗口）
- 每层 SW-MSA：增加跨窗口连接，实际感受野扩大到约 (2M-1)×(2M-1)≈169
- 堆叠 L 层后：感受野呈指数增长，L 层后理论全局感受野 ≈ M^L 个 patch

**关键洞察**：SW-MSA 用一次移位操作，以 O(HW) 代价获得了跨窗口信息流动，是优雅的工程权衡。

### 4.2 Swin 与 ViT 的设计哲学对比

| 维度 | ViT | Swin Transformer |
|------|-----|-----------------|
| 复杂度 | O(N²)，全局 | O(N)，局部+移位 |
| 特征尺度 | 单尺度 | 多尺度（层次化） |
| 归纳偏置 | 无（需大数据） | 轻微局部性 |
| 适用任务 | 分类为主 | 分类+检测+分割 |
| 设计思路 | "NLP Transformer → 图像" | "CNN 层次结构 + Transformer 注意力" |

### 4.3 历史地位

Swin Transformer 拿下 ICCV 2021 最佳论文（Marr Prize），是计算机视觉领域年度最高荣誉。它标志着：

1. **Transformer 统一视觉任务的里程碑**：分类、检测、分割都用同一骨干网络，不再需要专门为不同任务设计 CNN 变体。
2. **CNN 时代的终结起点**：2022 年起，SOTA 目标检测（DINO、GLIP）、语义分割（SegFormer、Mask2Former）几乎全部采用 Swin 或类似的层次化 Transformer 骨干。
3. **工程范式的确立**：Patch Merging + 窗口注意力的设计被 ConvNeXt（2022）所借鉴，引发 CNN 与 Transformer 的新一轮比较研究。

---

## Step 5 | 与已有报告的关联

```
AlexNet (2012)
    ↓ 深度CNN兴起
ResNet (2015)          ← 残差连接·多尺度特征图思想
    ↓ CNN称霸视觉
ViT (2020)             ← Swin 的直接前驱：证明纯Transformer可用于图像
    ↓ 单尺度、O(N²)复杂度
Swin Transformer (2021) ← 本报告：层次化 + 线性复杂度，Transformer统治视觉
    ↓
MAE (2022)、DINO v2 (2023)、Segment Anything (2023)
```

**与 CLIP 的关系**：CLIP 用 ViT 作图像编码器，后续版本（如 OpenCLIP、EVA-CLIP）已将部分实现迁移到 Swin 类架构以提升大分辨率性能。

---

## Step 6 | 局限与后续发展

| 局限 | 后续解决方案 |
|------|-------------|
| 移位窗口实现复杂（循环移位+masking） | Focal Attention（2021）：非均匀窗口 |
| M×M 窗口大小固定，感受野受限 | MaxViT（2022）：网格注意力 + 窗口注意力 |
| 预训练依赖 ImageNet 有监督标签 | MAE（2022）：自监督预训练视觉模型 |
| 在极大分辨率（4K+）仍存在内存压力 | Swin V2（2022）：支持更高分辨率迁移 |

---

## Step 7 | 总结

**一句话**：Swin Transformer 用"分而治之"的窗口注意力 + 移位跨窗通信，将 Transformer 的全局建模能力移植到多尺度视觉骨干中，以线性复杂度统一了分类、检测、分割三大任务，是深度学习视觉时代从"CNN 统治"到"Transformer 统治"的关键转折点。

**核心贡献**：
- **Shifted Window Attention**：O(HW) 线性复杂度 + 跨窗口信息流动
- **层次化特征图**：与 FPN/密集预测任务无缝对接
- **通用视觉骨干**：单一架构三大视觉任务全面超越 CNN
