---
title: "SkillOS 技能库策展小型实验复现"
type: experiment_analysis
status: done
experiment_id: exp_007
script: src/skillos_curator_simulation.py
updated_on: 2026-05-13
---

# exp_007：SkillOS 技能库策展小型实验复现

## 实验摘要

> 一句话：用一个确定性小型任务流复刻 SkillOS 的核心接口，观察 grouped task stream、SkillRepo 检索、insert/update/delete 策展操作如何让后续相关任务更快、更稳地复用经验。

本实验不是论文的完整复现。

论文中的 SkillOS 使用 Qwen3-8B 作为训练中的 skill curator 和 executor，使用 GRPO 在 ALFWorld、WebShop、DeepMath-103k 构造的推理任务上训练；完整训练需要 16 张 H100，耗时约 2.5 到 5 天。

本实验把它缩尺为 CPU 可运行的教学模拟：

- 任务从多个相关 group 中顺序到达。
- executor 在每个任务前从 SkillRepo 检索技能。
- curator 在每个任务后根据结果插入、更新或删除技能。
- 后续同组任务检验早期技能是否真的可复用。

## Step 1 实验目标

### 1.1 验证的问题

本实验验证三个工程问题。

第一，为什么 SkillOS 要把训练实例构造成 grouped task streams，而不是随机任务序列。

第二，为什么直接保存所有轨迹的 raw memory 虽然可能提升成功率，却会造成 SkillRepo 膨胀。

第三，为什么技能策展的核心不是“记更多”，而是“把经验压缩成可检索、可更新、可复用的程序性知识”。

### 1.2 与论文的对应关系

论文的关键接口是：

```text
Task stream -> Agent Executor -> trajectory -> Skill Curator -> SkillRepo
```

本实验保留同样的逻辑：

- `Task` 对应论文中的任务 `x_i`。
- `SkillRepo` 对应论文中的外部技能库 `S_t`。
- `Skill` 对应 Markdown skill 文件的缩尺表示。
- `execute()` 对应冻结 executor 使用检索到的技能执行任务。
- `run_policy()` 对应按任务流逐步执行、策展、再执行的闭环。

### 1.3 为什么不用 LLM

这里不用真实 LLM，是为了把变量固定住。

如果直接调用模型，结果会同时受到 prompt、模型能力、采样温度、上下文窗口和 judge 偏差影响。教学实验的目标是先看清 SkillOS 的结构性因果链：

```text
相关任务成组 -> 早期经验生成技能 -> 后续任务复用技能 -> 成功率和步数改变
```

## Step 2 实现方法

### 2.1 框架与库

实验脚本：

```text
src/skillos_curator_simulation.py
```

依赖：

```text
Python 标准库：argparse, random, collections, dataclasses
外部依赖：无
```

因此它可以在没有 GPU、没有 PyTorch、没有网络的环境里运行。

### 2.2 任务数据

默认配置生成 5 个任务组，每组 8 个任务，共 40 个任务。

任务组包括：

| group | 代表含义 |
|------|----------|
| `alfworld_heat` | 类 ALFWorld 的加热/容器/状态变化任务 |
| `alfworld_clean` | 类 ALFWorld 的清洁/水槽/验证任务 |
| `webshop_filter` | 类 WebShop 的筛选/价格/属性匹配任务 |
| `reasoning_verify` | 推理任务中的分解、方程、答案验证 |
| `reasoning_count` | 推理任务中的计数、分类讨论、off-by-one |

每个任务包含：

- `tags`：可复用的任务属性。
- `pitfalls`：容易出错的关键点。
- `difficulty`：执行难度。

### 2.3 三种策略

实验比较三种策略。

| policy | 含义 |
|--------|------|
| `no_memory` | 没有 SkillRepo，每个任务从零执行 |
| `raw_memory` | 每个任务后都保存一条 trace 风格技能，不压缩、不合并 |
| `skillos_heuristic` | 使用 SkillRepo，按相似度检索，按结果 insert/update/delete |

### 2.4 执行模型

`execute()` 根据技能覆盖度决定成功概率和执行步数。

核心直觉是：

- 检索技能越匹配，任务成功概率越高。
- 匹配技能能减少探索步数。
- 技能太多会带来上下文负担，所以有 overload penalty。

这对应论文中的效率指标：ALFWorld 和 WebShop 不只看成功率，也看 steps。

### 2.5 策展逻辑

`skillos_heuristic` 使用三类操作。

`insert`：

当没有相关技能时，为当前 group 建立一个技能。

`update`：

当已有相关技能且任务成功时，把新任务里的 tag 和 pitfall 合并进旧技能。

`delete`：

当某个技能使用次数足够多但成功率低于阈值时删除，模拟 SkillOS 的压缩与低效技能清理。

这不是 GRPO 学出来的策略，而是一个可解释启发式，用来复刻 SkillOS 的操作空间。

## Step 3 关键发现

### 3.1 grouped 顺序运行结果

运行命令：

```bash
python3 ai-practice/src/skillos_curator_simulation.py --groups 5 --tasks-per-group 8 --top-k 2 --seed 13 --order grouped
```

实际结果：

| policy | success_rate | avg_steps | repo_size | skill_tokens | insert | update | delete |
|--------|--------------|-----------|-----------|--------------|--------|--------|--------|
| `no_memory` | 0.500 | 8.88 | 0 | 0 | 0 | 0 | 0 |
| `raw_memory` | 0.875 | 7.00 | 40 | 2160 | 40 | 0 | 0 |
| `skillos_heuristic` | 0.875 | 6.45 | 4 | 380 | 4 | 11 | 0 |

核心观察：

- `raw_memory` 和 `skillos_heuristic` 都把成功率从 0.500 提升到 0.875。
- `skillos_heuristic` 的平均步数更低：6.45 vs 7.00。
- `raw_memory` 保存了 40 条技能，SkillRepo token 成本 2160。
- `skillos_heuristic` 只保留 4 条技能，SkillRepo token 成本 380。

这说明同等成功率下，技能策展比原始轨迹记忆更紧凑、更便于检索。

### 3.2 grouped 顺序中的组内表现

`skillos_heuristic` 的分组表现：

| group | success | rate |
|-------|---------|------|
| `alfworld_clean` | 7/8 | 0.875 |
| `alfworld_heat` | 7/8 | 0.875 |
| `reasoning_count` | 7/8 | 0.875 |
| `reasoning_verify` | 6/8 | 0.750 |
| `webshop_filter` | 8/8 | 1.000 |

同组任务连续出现时，早期任务生成的技能能很快作用于后续任务。这正是论文选择 grouped task streams 的原因：让延迟反馈变得更密集。

### 3.3 shuffled 顺序运行结果

运行命令：

```bash
python3 ai-practice/src/skillos_curator_simulation.py --groups 5 --tasks-per-group 8 --top-k 2 --seed 13 --order shuffled
```

实际结果：

| policy | success_rate | avg_steps | repo_size | skill_tokens | insert | update | delete |
|--------|--------------|-----------|-----------|--------------|--------|--------|--------|
| `no_memory` | 0.500 | 8.88 | 0 | 0 | 0 | 0 | 0 |
| `raw_memory` | 0.800 | 7.10 | 40 | 2160 | 40 | 0 | 0 |
| `skillos_heuristic` | 0.800 | 7.08 | 4 | 376 | 5 | 16 | 1 |

随机顺序下，两个记忆策略的成功率都降到 0.800。

这和论文的 ablation 方向一致：没有 task grouping 时，早期技能未必马上遇到相关后续任务，策展操作的下游反馈更稀疏。

### 3.4 与论文数字的关系

论文在 ALFWorld ablation 中报告：

- SkillOS-GRPO：Avg. SR 61.2，Steps 18.9。
- w/o content-quality reward：Avg. SR 58.6，Steps 20.1。
- w/o compression reward：Avg. SR 60.0，Steps 19.3。
- w/o grouping：Avg. SR 57.3，Steps 20.6。

本实验的数字不能和论文横向比较，因为任务、模型和环境都不同。

但趋势是一致的：

- grouped 比 shuffled 更容易暴露复用收益。
- 压缩后的技能库可以维持较高成功率，同时降低检索和上下文成本。
- 原始记忆能有帮助，但容易用更大的 repo 换结果。

## Step 4 代码参考

### 4.1 任务与技能表示

核心位置：

```text
src/skillos_curator_simulation.py:22
src/skillos_curator_simulation.py:31
src/skillos_curator_simulation.py:50
```

`Task` 保存任务属性，`Skill` 保存可复用 tag/pitfall，`SkillRepo` 管理检索和操作计数。

### 4.2 检索和压缩

核心位置：

```text
src/skillos_curator_simulation.py:55
src/skillos_curator_simulation.py:79
src/skillos_curator_simulation.py:89
```

`retrieve()` 用 tag/pitfall 重叠度做简化版 BM25。

`delete_low_utility()` 对低效技能做删除。

`token_cost()` 用固定公式估算 SkillRepo 的上下文成本。

### 4.3 grouped task stream

核心位置：

```text
src/skillos_curator_simulation.py:113
src/skillos_curator_simulation.py:145
```

`build_grouped_tasks()` 构造同组相关任务。

`shuffled_tasks()` 用于对照随机任务顺序。

### 4.4 执行与策展闭环

核心位置：

```text
src/skillos_curator_simulation.py:152
src/skillos_curator_simulation.py:164
```

`execute()` 模拟冻结 executor。

`run_policy()` 模拟每个任务之后更新 SkillRepo 的闭环。

## Step 5 局限性与下一步

### 5.1 当前实验局限

第一，成功概率是手写函数，不是真实 LLM executor。

第二，技能内容只是 tag/pitfall 集合，不是 Markdown skill 文件。

第三，策展策略是启发式，不是 GRPO 训练得到的 policy。

第四，content-quality reward 没有真实 judge，只用 repo token 成本和成功率间接观察。

第五，任务环境不是 ALFWorld/WebShop，也没有真实 ReAct 轨迹。

### 5.2 可扩展方向

下一步可以把技能表示改成真实 Markdown 文件：

```text
---
name: verify_state_after_action
description: Use when a task requires checking object state after an operation.
---

## Workflow
1. Perform the state-changing action.
2. Inspect the object.
3. If state mismatches, run fallback search.
```

再进一步，可以接入一个小模型或本地 LLM，让 curator 从失败轨迹中写技能。

### 5.3 与 ai-learning 报告的配合

建议先读 `ai-learning/reports/paper_analyses/44_skillos_2026.md` 理解论文完整训练配方，再运行本实验看结构性机制。

报告偏理论与论文精读。

本实验偏工程直觉与可运行缩尺模拟。

二者合起来，能把 SkillOS 从“又一个 Agent 论文”变成一个可迁移的设计模式：

```text
经验不是资产。
被压缩、被检索、被复用、被更新的经验才是资产。
```

## 参考资料

- Siru Ouyang et al., `SkillOS: Learning Skill Curation for Self-Evolving Agents`, arXiv:2605.06614, 2026.
- ReAct: Synergizing Reasoning and Acting in Language Models.
- GRPO / Grouped Reward Policy Optimization 相关后训练方法。
- Anthropic Agent Skills / SKILL.md 风格技能组织。
