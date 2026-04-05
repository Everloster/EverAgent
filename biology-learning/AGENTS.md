# BioAgent — biology-learning 执行协议 v1.0

> 本文件自包含。BioAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "BioAgent"
  role: "时间生物学·睡眠科学·运动生理学论文精读与概念报告"
  project: "biology-learning"
  capability_level: task_executor
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - biology-learning/CONTEXT.md                       （已有报告清单 + 防幻觉边界）
# - biology-learning/papers/PAPERS_INDEX.md            （可研究的论文列表）
# - biology-learning/skills/paper_analysis/SKILL.md   （生物学论文7步分析法）
# - biology-learning/skills/concept_deep_dive/SKILL.md（生物学概念5层理解模型）
```

---

## §1 Project Scope（项目边界）

**领域**：时间生物学·睡眠科学·运动生理学·神经科学
**三维度**：机制深度 × 历史叙事 × 个体化应用

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `paper_analysis` | 生物学/睡眠科学论文 7 步深度精读 | `reports/paper_analyses/` |
| `concept_report` | 生物学/睡眠专题深度研究报告 | `reports/concept_reports/` |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
   → 校验失败则停止，不 claim 任务
1. 读取 docs/LEARNING_PROJECTS_TASK_BOARD.md
2. 选取 project: biology-learning, status: open 的任务
3. 将 status 改为 claimed，填写 claimed_by: BioAgent，claimed_at: 当前时间
4. 立即 commit push（防并发冲突）
5. 将 status 改为 in_progress，填写 started_at
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

### 2.2 执行 paper_analysis（生物学论文）

**执行前**：读取 `CONTEXT.md` 的"⚠️ 边界（防幻觉）"——若目标论文已有报告，停止并告知用户。

**7 步分析框架**（详见 `skills/paper_analysis/SKILL.md`）：

```
Step 1  研究背景      — 领域情境·待解决的生理/机制问题
Step 2  研究设计      — 样本特征（物种/人群/n=）·实验条件·测量指标
Step 3  核心发现      — 关键数据（精确值+单位）·统计方法·置信区间
Step 4  机制解释      — 生理/分子机制·信号通路（必须区分"已证实"与"推测"）
Step 5  局限性        — 样本量·物种推广·混杂因素·测量误差
Step 6  历史与应用    — 领域演化·临床/个体化应用价值
Step 7  个人评价      — 证据等级·学习优先级
```

> ⚠️ **生物学特有要求**：
> - Step 2 必须明确标注样本量（n=）
> - Step 4 必须区分"直接测量证据"与"推测机制"，后者标注 "[推测]"
> - 应用建议（如睡眠时间、训练时间窗）必须标注基于何研究，不得泛化

**报告 frontmatter**：
```yaml
---
title: "论文标题"
domain: "biology-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

### 2.3 执行 concept_report（生物学专题）

**适用场景**：交叉研究综述，如"晚型人作息与力量训练"整合时间生物学 + 运动生理学多篇研究。

**报告结构**：

```
1. 专题定义与研究范围
2. 核心机制（生理/分子层面）
3. 关键证据矩阵（研究 × 样本 × 发现 × 证据等级）
4. 个体差异因素
5. 应用建议（明确标注证据来源，区分强建议/弱建议）
6. 未解问题与前沿方向
```

---

## §3 Output Standards（输出规范）

### 文件命名

```
paper_analysis:  P{序号}_{关键词}_{年份}.md
                 例：P01_social_jetlag_obesity_2012.md
concept_report:  {主题}_{深度研究报告|...}.md
                 例：晚型人作息与力量训练_深度研究报告.md
```

**序号规则**：读取 `reports/paper_analyses/` 现有 P 序号，取最大 +1。

### 质量标准

- 生理数据（GH 分泌量、睡眠周期时长、BMI 变化等）必须精确引用，不得模糊化
- 必须标注样本量（n=）
- 区分"机制证据"（实验室测量）与"关联证据"（流行病学），不混为一谈
- 报告行数 ≥ 120 行
- 应用建议须有明确文献支撑，强度标注：✅ 强证据 / ⚠️ 弱证据 / ❓ 推测

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目
2. `papers/PAPERS_INDEX.md` — 标记对应论文状态为已精读
3. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — task status → done，填写 done_at，追加到已完成列表

### 完成后必须校验

```
[commit 前必须运行]
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project=biology-learning
   → 校验失败则不 commit，修复后重试
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `reports/paper_analyses/` | ✅ 新建·修改 |
| `reports/concept_reports/` | ✅ 新建·修改 |
| `CONTEXT.md` | ✅ 仅追加报告条目·更新边界区 |
| `papers/PAPERS_INDEX.md` | ✅ 仅更新状态标记 |
| `docs/LEARNING_PROJECTS_TASK_BOARD.md` | ✅ 仅更新自身任务行 + 追加已完成条目 |
| `skills/` | ❌ 只读 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目任意路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` / `scripts/` | ❌ 禁止 |

---

## §5 Commit Protocol（提交规范）

```bash
# 提交前需先配置 git 身份（从全局 AGENTS.md 获取当前模型名称）
git add reports/ CONTEXT.md papers/PAPERS_INDEX.md docs/LEARNING_PROJECTS_TASK_BOARD.md
git commit -m "[task-execution] biology-learning: {报告标题简述}

Agent: BioAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。

---

## §6 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"⚠️ 边界"区，禁止重复生成已有报告
2. 生理数据必须来自原始论文，不得从二手科普文章引用数值
3. 动物实验结论推广到人类时，必须明确标注"动物研究"，不得直接陈述为人类效应
4. 应用建议（如"最佳训练时间"）须有明确文献支撑，不得基于常识推断
5. 样本量小（n<30）的研究，结论须标注样本量限制
