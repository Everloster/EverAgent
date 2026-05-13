---
title: "SkillOS Curator Simulation"
type: concept
status: active
updated_on: 2026-05-13
related: [long_context_simulation, mixture_of_experts, grpo]
---

# SkillOS Curator Simulation

SkillOS Curator Simulation 是 `exp_007` 的缩尺实践概念：用纯 Python 模拟 SkillOS 中的 grouped task streams、SkillRepo、技能检索和 insert/update/delete 策展操作。

它不是论文训练系统的完整复现，而是为了帮助理解 SkillOS 的工程骨架。

## 对应论文机制

| 论文机制 | 实验缩尺实现 |
|----------|--------------|
| grouped task streams | 5 个任务组，每组 8 个相关任务 |
| Agent Executor | `execute()` 概率执行器 |
| SkillRepo | `SkillRepo` dataclass |
| BM25 skill retrieval | tag/pitfall 重叠度排序 |
| Skill Curator | `run_policy()` 中的启发式 insert/update/delete |
| compression reward | `skill_tokens` 和 repo size 对照 |

## 关键观察

默认 grouped 设置下：

- `no_memory` 成功率为 0.500，平均步数 8.88。
- `raw_memory` 成功率为 0.875，平均步数 7.00，但保留 40 条技能。
- `skillos_heuristic` 成功率同为 0.875，平均步数降到 6.45，只保留 4 条技能。

这展示了 SkillOS 的核心直觉：经验的价值不在于原样保存，而在于压缩、更新和复用。

## 运行方式

```bash
python3 ai-practice/src/skillos_curator_simulation.py --groups 5 --tasks-per-group 8 --top-k 2 --seed 13 --order grouped
```

对照随机顺序：

```bash
python3 ai-practice/src/skillos_curator_simulation.py --groups 5 --tasks-per-group 8 --top-k 2 --seed 13 --order shuffled
```

## 学习价值

这个实验适合作为真实 SkillOS 复现前的低成本 sanity check。

它能帮助你先回答：

- grouped task stream 为什么重要？
- raw memory 为什么容易膨胀？
- update 为什么比单纯 insert 更像长期技能治理？
- delete 为什么是 SkillRepo 健康度的一部分？

## 延伸方向

下一步可以把 `Skill` 从 tag 集合改成真实 Markdown 文件，并让本地 LLM 根据失败轨迹生成 skill patch。

更进一步，可以把任务成功率、步数、repo token 成本组合成一个简化 reward，训练一个小 policy 来选择 insert/update/delete。
