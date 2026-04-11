# Bitter Lesson（苦涩教训）

> AI 研究方法论的元认知原则：通用计算方法长期总是赢

## 一句话定义

Rich Sutton 在 2019 年总结的 AI 70 年核心教训：利用算力的通用方法（搜索与学习）最终总是击败编码人类知识的专用方法，因为算力持续指数增长而手工知识不会自动改善。

## 核心论断

```
短期：编码人类知识 → 快速见效 → 研究者满意
长期：通用计算方法 → 持续扩展 → 最终碾压

根本原因：摩尔定律（广义）
  → 算力成本持续指数下降
  → 今天"太贵"的通用方法，明天就变得可行
  → 手工编码的知识不会随算力增长而改善
```

## 两类可无限扩展的方法

1. **搜索 (Search)**：深度搜索 → MCTS → AlphaGo Zero 的规划 → o1/o3 的 test-time compute
2. **学习 (Learning)**：统计学习 → 深度学习 → 自监督预训练 → LLM scaling

共同特征：给更多算力，效果就更好，且没有可见上限。

## 四个历史验证案例

| 领域 | 知识编码路线 | 通用方法胜出 | 间隔 |
|------|------------|------------|------|
| 国际象棋 | 编码棋理、开局库 | Deep Blue 大规模搜索 (1997) | ~30年 |
| 围棋 | 人类棋感、定式 | AlphaGo Zero 自我对弈 (2017) | ~20年 |
| 语音识别 | 音素规则、声道模型 | HMM → 深度学习 (2010s) | ~40年 |
| 计算机视觉 | SIFT、手工特征 | AlexNet 端到端学习 (2012) | ~50年 |

## 最深刻的哲学论断

> "We want AI agents that can discover like we can, not which contain what we have discovered."

不要编码"人类的发现"，要构建"发现的方法"（meta-methods）。

## 与其他概念的关系

```
Bitter Lesson (哲学纲领)
    ├── Scaling Laws (数学化表达) → 幂律证明"更多计算 = 更好效果"
    ├── Test-time Compute (搜索分支) → o1/o3 推理时扩展
    ├── Self-supervised Learning (学习分支) → 通用预训练
    └── Pretraining & Fine-tuning → 从特化走向通用
```

## 局限与补充

- **时间尺度问题**：工程师不能等 10 年让算力赶上来，短期内领域知识仍有价值
- **通用方法本身需人类设计**：Transformer 架构本身就是人类智慧的产物
- **Hardware Lottery** (Hooker 2021)：硬件形态会影响哪些"通用方法"能被探索
- **安全与对齐**：通用方法产生的能力可能不受控

## 在本项目四条时间线中的位置

Bitter Lesson 是四条时间线的**哲学总纲**：
- 模型范式线：AlexNet(CNN>手工特征) → Transformer(通用注意力>专用架构) → CoT/ReAct(推理时搜索)
- Infra 与数据线：Scaling Law 是 Bitter Lesson 的数学表达
- 语言模型线：Word2Vec → GPT-1 → GPT-3，每一步都是"更少人类知识，更多计算"
- 多模态线：SIFT → CNN → ViT → CLIP，手工特征被完全淘汰

## 来源

- Rich Sutton, "The Bitter Lesson", incompleteideas.net, 2019.03.13
- 项目报告：`reports/paper_analyses/22_bitter_lesson_2019.md`
