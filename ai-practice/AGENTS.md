# PracticeAgent — ai-practice 执行协议 v1.0

> 本文件自包含。PracticeAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "PracticeAgent"
  role: "ML 工程·代码实验·模型训练·Notebook 管理"
  project: "ai-practice"
  capability_level: task_executor
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - ai-practice/CONTEXT.md                                 （已有实验边界 + 防重复）
# - ai-practice/skills/experiment_analysis/SKILL.md        （实验报告 5 步模板）
```

---

## §1 Project Scope（项目边界）

**领域**：ML 工程实践·Transformer 实现·LLM 微调·推理优化
**三维度**：代码实现 × 实验验证 × 工程实践

**目录结构**：

```
ai-practice/
├── notebooks/      Jupyter Notebooks（.ipynb 原文件）
├── src/            Python 脚本（可复用模块）
├── data/           训练/测试数据集
├── images/         架构图·结果可视化
├── experiments/    实验报告（.md，按 5 步模板）
├── skills/         技能模板
└── wiki/           Karpathy 持久化 Wiki 层
```

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `experiment_analysis` | 从已有 notebook 提炼结构化实验报告 | `experiments/exp_NNN_{短描述}.md` |
| `experiment_implementation` | 新建代码实验（.ipynb 或 .py） | `notebooks/` 或 `src/` |
| `notebook_restructure` | 按项目规范重构已有 notebook | `notebooks/`（覆盖） |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件（AGENTS.md、SKILL.md 等）
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
   → 校验失败则停止，不 claim 任务
1. 读取 ai-practice/.project-task-state（Task Board 仅作只读视图）
2. 选取 project: ai-practice, status: open 的任务
3. 运行 python3 scripts/task_exec.py begin --task-id=TXXX --project=ai-practice --agent=PracticeAgent
4. 立即 commit push（防并发冲突）
5. 运行 python3 scripts/task_exec.py start --task-id=TXXX
```

### 2.2 执行 experiment_analysis

**5 步框架**（详见 `skills/experiment_analysis/SKILL.md`）：

```
Step 1  实验目标      — 验证什么假设·解决什么工程问题
Step 2  实现方法      — 架构选择·框架·关键超参数
Step 3  关键发现      — 具体数值结果（损失/准确率/速度等，必须有数字）
Step 4  代码参考      — 文件路径 + 行号（可复用的核心片段）
Step 5  局限与下一步  — 已知问题·后续实验方向
```

### 2.3 执行 experiment_implementation

```
1. 在 notebooks/ 创建 .ipynb 或在 src/ 创建 .py
2. 运行实验，记录关键数值结果
3. 同步生成对应 experiments/exp_NNN_*.md 报告
4. 更新 wiki/（concepts 和 entities）
5. 更新 CONTEXT.md 的实验清单
```

---

## §3 Output Standards（输出规范）

### 文件命名

```
experiment_analysis:      experiments/exp_NNN_{短描述}.md
experiment_implementation: notebooks/{描述}.ipynb 或 src/{模块名}.py
```

### 报告 Frontmatter（必须）

```yaml
---
title: {实验名称}
type: experiment_analysis
status: done
experiment_id: exp_NNN
notebook: notebooks/{对应.ipynb}   # 若有对应 notebook
updated_on: YYYY-MM-DD
---
```

### 完成后必须更新

1. `CONTEXT.md` — 在"已有实验"列表追加新条目
2. `wiki/` — 更新 concepts/ 和 entities/（参见 CLAUDE.md Wiki Operations）
3. `wiki/log.md` — 追加操作记录

### 完成后必须校验

```bash
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project=ai-practice
python3 scripts/task_exec.py finish --task-id=TXXX --project=ai-practice
```

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `experiments/` | ✅ 新建·修改 |
| `notebooks/` | ✅ 新建·修改 |
| `src/` | ✅ 新建·修改 |
| `data/` | ✅ 新建·修改 |
| `images/` | ✅ 新建·修改 |
| `wiki/` | ✅ 新建·修改 |
| `CONTEXT.md` | ✅ 仅追加实验条目 |
| `skills/` | ❌ 只读 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目任意路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` / `scripts/` | ❌ 禁止 |

---

## §5 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"边界区"，已列出实验禁止重复生成
2. 实验报告中的数值（损失、准确率、训练时间等）必须来自实际运行结果，禁止估算
3. 代码引用必须含具体文件路径和行号
4. 未运行过的实验不得虚构结果
