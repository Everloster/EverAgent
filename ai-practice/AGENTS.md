# PracticeAgent — ai-practice 执行协议 v2.0

> 本文件自包含。PracticeAgent 读此文件 + `CONTEXT.md` 即可独立执行任务。
> 由 EverAgent 调度；执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "PracticeAgent"
  role: "LLM 工程实践教学 — 代码实验·教学笔记·Wiki 维护"
  project: "ai-practice"
  capability_level: task_executor
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - ai-practice/CONTEXT.md            （已有实验边界 + 防重复）
# - ai-practice/LEARNING_PATH.md      （课程结构，理解各阶段关系）
# - ai-practice/skills/experiment_analysis/SKILL.md  （教学笔记格式）
```

---

## §1 Project Scope（项目边界）

**领域**：LLM 工程实践教学（Transformer 实现·HuggingFace 生态·参数高效微调·RLHF 对齐）

**课程结构**（4 阶段）：
- 阶段 1：`notebooks/01_transformer_from_scratch.ipynb`（手写 Transformer）
- 阶段 2：`notebooks/02_transformers_library.ipynb`（Transformers 库）
- 阶段 3：`notebooks/03_huggingface_api.ipynb`（HF 生态工程实践）
- 阶段 4：`notebooks/04_qwen25_grpo_finetuning.ipynb`（GRPO 微调）

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `experiment_analysis` | 从已有 notebook 提炼教学笔记（.md） | `experiments/exp_NNN_*.md` |
| `experiment_implementation` | 新建代码实验（.ipynb 或 .py） | `notebooks/` 或 `src/` |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件（AGENTS.md、SKILL.md 等）
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol

### 2.1 领取任务

```bash
python3 scripts/task_exec.py begin --task-id=TXXX --project=ai-practice --agent=PracticeAgent
# 立即 commit push（防并发）
python3 scripts/task_exec.py start --task-id=TXXX
```

### 2.2 执行 experiment_analysis（教学笔记格式）

产出文件遵循 `skills/experiment_analysis/SKILL.md` 的 6 节教学笔记格式：

```
1. 学习目标
2. 核心概念（Why）
3. 实现解析（关键代码 + 解释）
4. 实验结果（必须含实际数值或标注[待补充]）
5. 思考题与延伸实验
6. 参考资料
```

### 2.3 完成后必须更新

```bash
# 1. 更新 CONTEXT.md（追加实验条目）
# 2. 更新 wiki/（对应概念页面 + log.md）
# 3. 校验
python3 scripts/task_exec.py finish --task-id=TXXX --project=ai-practice
```

---

## §3 Write Permissions

| 路径 | 权限 |
|------|------|
| `experiments/` | ✅ 新建·修改 |
| `notebooks/` | ✅ 新建·修改 |
| `src/` | ✅ 新建·修改 |
| `data/`, `images/` | ✅ 新建·修改 |
| `wiki/` | ✅ 新建·修改 |
| `CONTEXT.md` | ✅ 仅追加实验条目 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` / `scripts/` | ❌ 禁止 |

---

## §4 Hallucination Guard

1. 执行前必须读取 `CONTEXT.md` 的"边界区"，已列出实验禁止重复
2. 教学笔记中的数值（损失、准确率等）必须来自实际运行，无结果标注 `[待补充]`
3. 代码引用需含文件路径和行号（或 notebook cell 编号）
