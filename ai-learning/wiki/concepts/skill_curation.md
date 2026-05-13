---
title: "Skill Curation"
type: concept
status: active
updated_on: 2026-05-13
related: [agent_systems, agent_orchestration, rlhf]
---

# Skill Curation

Skill curation 指 Agent 从过去执行轨迹中抽取、压缩、更新、删除可复用技能的过程。

它和普通 memory 的区别在于：memory 关注“保存过去发生了什么”，skill curation 关注“整理出未来该怎么做”。

## 核心问题

一个长期运行的 Agent 会不断产生经验。

如果完全不保存，Agent 每次都从零开始。

如果原样保存所有轨迹，SkillRepo 会迅速膨胀，检索和上下文成本上升，甚至产生互相冲突的建议。

Skill curation 要回答：

- 哪些经验应该变成技能？
- 哪些旧技能应该更新？
- 哪些技能低效、过时或有害，应该删除？
- 技能应该写成什么结构，executor 才能稳定使用？

## SkillOS 的定义

SkillOS 把技能策展拆成两个角色：

- frozen Agent Executor：使用检索到的技能解决任务。
- trainable Skill Curator：根据执行轨迹更新外部 SkillRepo。

SkillRepo 中的技能是 Markdown 文件，包含适用场景、工作流、约束、失败处理和可复用启发式。

curator 通过三类操作维护仓库：

```text
insert_skill
update_skill
delete_skill
```

## 训练信号

SkillOS 的关键是 grouped task streams。

同组任务存在共享技能依赖，因此前面任务生成的技能会在后面相关任务中被检验。

复合奖励包含：

- `r_task`：后续任务成功率。
- `r_fc`：函数调用是否有效。
- `r_cnt`：技能内容质量。
- `r_comp`：技能库相对输入上下文的压缩程度。

这使 curator 学到的不是“多记”，而是“保留对 executor 有用的程序性知识”。

## 工程启发

在真实 Agent 系统中，skill curation 可以对应这些维护动作：

- 从成功任务中抽取 workflow。
- 从失败任务中补充 failure handling。
- 合并重复技能。
- 给技能增加适用条件和禁用条件。
- 删除长期未使用或使用后失败率高的技能。

对于 EverAgent，这个概念可映射到：

- `AGENTS.md` 协议更新。
- `skills/` 技能文件维护。
- `wiki/` 概念页摄入。
- `CONTEXT.md` 防重复边界更新。
- 任务事件日志里的成功/失败反馈。

## 与相关概念的区别

| 概念 | 关注点 |
|------|--------|
| RAG | 检索外部知识进入上下文 |
| Agent Memory | 保存历史经验或偏好 |
| Skill Curation | 把经验治理成可复用技能 |
| RLHF / GRPO | 用奖励训练策略 |
| Agent Orchestration | 管理多模型、多工具、多状态的执行系统 |

## 参考

- `reports/paper_analyses/44_skillos_2026.md`
- `ai-practice/experiments/exp_007_skillos_curator_simulation.md`
