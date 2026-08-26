# Skill: experiment_analysis — 实验分析 5 步模板

> 用于从已有 Jupyter Notebook 或代码实验中提炼结构化 Markdown 报告。
> 产出路径：`experiments/exp_NNN_{短描述}.md`
> 通用研究方法论见根 [METHODOLOGY.md](../../../METHODOLOGY.md)（强制）。本文件为领域特化部分。

---

## 输出文件格式

```markdown
---
title: {实验名称（中文）}
type: experiment_analysis
status: done
experiment_id: exp_NNN
notebook: notebooks/{对应.ipynb}    # 若无对应 notebook 则省略此行
updated_on: YYYY-MM-DD
---

## 实验摘要
> 一句话：验证了什么，结论是什么。

## Step 1 实验目标
- 解决的工程问题或验证的假设
- 实验背景（与哪篇论文/概念关联，可交叉引用 ai-learning wiki）

## Step 2 实现方法
- 框架 & 库版本（PyTorch x.x / HuggingFace Transformers x.x / Unsloth x.x 等）
- 模型架构关键参数（必须列出具体数值，如 d_model=64, num_heads=4）
- 数据集（来源 + 规模）
- 训练配置（batch_size, lr, epochs 等关键超参数）

## Step 3 关键发现
- **必须包含具体数值**（损失、准确率、速度、内存占用等）
- 定性结论需有定量支撑
- 可用表格对比不同配置

## Step 4 代码参考
- 核心实现位置（文件路径 + 行号）
- 可复用的关键函数/类（含简短说明）

## Step 5 局限性与下一步
- 当前实验的已知局限（数据规模、硬件约束等）
- 建议的后续实验方向
```

---

## 使用规则

1. **数值必须来自实际运行**：若 notebook 未执行，标注 `[未运行]`，不得虚构结果
2. **experiment_id 序号**：查阅 `CONTEXT.md` 中最大 exp ID，顺序递增
3. **notebook 字段**：一篇报告对应一个 notebook，必须一一映射
4. **wiki 更新**：生成报告后必须更新 `wiki/concepts/` 和 `wiki/log.md`
5. **CONTEXT.md 追加**：报告完成后必须在 CONTEXT.md "已有实验"列表追加一行
