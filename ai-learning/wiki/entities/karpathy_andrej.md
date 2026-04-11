# Andrej Karpathy

> Deep Video 第一作者，Stanford → Tesla → AI 教育者，CS231n 联合讲师

## 基本信息

| 项目 | 内容 |
|------|------|
| 全名 | Andrej Karpathy |
| 机构 | Stanford University → Tesla (Autopilot) → AI 教育者 |
| 核心贡献 | Deep Video (2014)，CS231n 深度学习计算机视觉课程 |
| 代表作 | "Large-scale Video Classification with CNNs" (CVPR 2014) |

## 学术脉络

```
Stanford PhD（师从 Fei-Fei Li）
    └── Deep Video (2014)
         ├── Sports-1M 数据集（100 万视频，487 类）
         ├── 四种时序融合策略系统比较
         └── 验证 CNN 用于视频分类的可行性

    └── CS231n（深度学习计算机视觉课程）
         ├── 成为全球最受欢迎的 AI 课程之一
         └── 培养了数代深度学习研究者

Tesla Autopilot（2017-2022）：
    └── 负责 Tesla 视觉感知系统
         → 端到端自动驾驶视觉方案

回归教育（2022+）：
    └── 创立 zero-to-mastery / AI 课程
         → 让 AI 教育民主化
```

## 核心贡献：Deep Video

### 主要技术成就

```
1. Sports-1M 数据集：
   - 100 万 YouTube 视频，487 运动类
   - 当时最大规模的视频分类数据集
   - 验证了大规模视频数据的价值

2. 时序融合策略系统比较：
   - Single-frame / Early / Late / Slow Fusion
   - Slow Fusion = 最佳策略
   → 预见了 3D CNN 和时序 Transformer 的设计

3. 多分辨率架构：
   - Fovea（高分辨率中心） + Context（低分辨率周围）
   - 同时捕获运动细节和场景信息
```

## 在本项目中的关联

- 直接关联报告：`40_deepvideo_2014.md`
- 关联论文：AlexNet (#06) — CNN 图像分类基础
- 概念关联：`video_cnn.md`、`temporal_fusion.md`

## 影响力特点

```
Karpathy 的独特风格：
  1. 大规模实验优先："没有大规模数据，就没有大规模深度学习"
  2. 系统性消融：不是调最优模型，而是系统比较所有方案
  3. 实践导向：追求"什么在实践中有效"
  4. 教育热情：CS231n 是 AI 教育的里程碑

Karpathy 的名言：
  "The graveyard of successful autonomous vehicle companies is filled with companies that tried to hand-design their way to solving perception."
  → 体现了 Bitter Lesson 的精神
```
