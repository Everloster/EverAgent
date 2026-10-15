---
id: concept-muon_hyperball
title: "Muon 系优化器与 Hyperball 包装"
type: concept/optimization
domain: [ai-learning]
created: 2026-10-15
updated: 2026-10-15
sources: [PuRo-2B_开放低成本预训练配方_MuonHyperball与RTX5090_深度解析_20261015]
---

# Muon 系优化器与 Hyperball 包装

## 定义
**Muon**：对二维权重矩阵的动量更新做 Newton-Schulz 正交化（近似极正交化）的优化器——更新只保留方向、舍弃幅度。**MuonHyperball（MuonH）**：Wen et al. 提出的包装，把每个被包裹矩阵钉在初始化半径 R=‖W₀‖_F 的 Frobenius 球面上。

## 核心机制：有效学习率（ELR）的显式化

尺度不变性（norm 层使 L(cW)≈L(W)）意味着更新幅度应相对权重尺度解释。矩阵级有效学习率：

> ρ_t(W) = η_t·‖u_t‖_F / ‖W_t‖_F

- **普通 Muon**：ρ_t 由演化的权重范数与更新范数**间接涌现**，scalar LR 控制不了它；其诱导 ELR 早期快速衰减、收尾趋零。
- **MuonH**：更新归一化后位移长度恰为 η_t·R，权重范数恒为 R → **ρ_t = η_t**，数值上等于学习率超参本身；每步投影回球面。

**归因证据**（PuRo 170M 三角，BF16）：MuonH 3.029 ≈ ELR 对齐的普通 Muon 3.030 << 普通 LR Muon 3.073——MuonH 相对 Muon 的收益主要来自 ELR schedule 可控，而非球面投影本身。

## 参数路由（PuRo 生产配置）
- 进 MuonH：二维 attention/MLP 矩阵（近似尺度不变）；fused QKV/SwiGLU 按**逻辑子矩阵**分别归一化与 Newton-Schulz
- 留 AdamW：embedding、LM head、bias、norm 权重；MuonH 组 LR = m × base（m=10），fixed-radius 矩阵**禁用 weight decay**（投影已承担半径控制）

## 关联
- PuRo-2B 用 MuonH 训练 1.4T tokens（κ=1.19× 质量等效率力乘子）；工业侧 Moonlight/Kimi 亦用 Muon 变体
- LR schedule 设计在 ELR 视角下统一：WSD sweep 两观察（大 peak→长 decay；长 horizon→长 decay）→ power(p=0.5) 开放式 + 长线性衰减两阶段
- 诊断工具：Multi-Power Law（MPL）从 LR schedule 预测 loss 曲线；用 ELR 而非 raw LR 拟合更准（RMSE 0.0265→0.0210）

## 来源与边界
PuRo-2B 论文（arXiv 2608.27370v2）§3.3 + 附录 F；ELR 对齐实验在 170M/BF16 做，2B/FP8 尺度未单独验证；参数路由无逐类消融（详见来源报告 §5/§11）。
