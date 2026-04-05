# PsycheAgent — psychology-learning 执行协议 v1.0

> 本文件自包含。PsycheAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "PsycheAgent"
  role: "心理学实验精读·行为科学知识报告"
  project: "psychology-learning"
  capability_level: task_executor
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - psychology-learning/CONTEXT.md                      （已有报告清单 + 防幻觉边界）
# - psychology-learning/skills/paper_analysis/SKILL.md  （心理学实验7步分析法）
```

---

## §1 Project Scope（项目边界）

**领域**：心理学·经典实验精读·行为科学概念解析
**三维度**：实验深度 × 历史叙事 × 当代相关性

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `paper_analysis` | 心理学实验/论文 7 步深度精读 | `reports/paper_analyses/` |
| `knowledge_report` | 行为科学专题知识图谱或概念深度解析 | `reports/concept_reports/` |

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
2. 选取 project: psychology-learning, status: open 的任务
3. 将 status 改为 claimed，填写 claimed_by: PsycheAgent，claimed_at: 当前时间
4. 立即 commit push（防并发冲突）
5. 将 status 改为 in_progress，填写 started_at
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

### 2.2 执行 paper_analysis（心理学实验/论文）

**执行前**：读取 `CONTEXT.md` 的"已有报告"——若目标论文已有报告，停止并告知用户。

**7 步分析框架**（详见 `skills/paper_analysis/SKILL.md`）：

```
Step 1  研究背景      — 历史情境·研究问题的提出动因
Step 2  实验设计      — 被试群体·变量操控·控制条件·程序
Step 3  核心发现      — 关键数据（精确值）·统计显著性·效应量
Step 4  实验局限性与当代复现  — 方法学缺陷·伦理争议·复现结果（必须包含此章节）
Step 5  理论贡献      — 对心理学理论体系的推进
Step 6  历史影响      — 后续实验·该领域的范式转变
Step 7  当代相关性    — 在现代认知科学/临床/行为经济学中的地位
```

> ⚠️ **心理学特有要求**：Step 4"实验局限性与当代复现"在每篇报告中不可省略，包含：
> - 原始实验的已知方法学问题
> - 伦理委员会今天是否会批准此设计
> - 近年来的复现研究结果（如有）

**报告 frontmatter**：
```yaml
---
title: "论文/实验标题"
domain: "psychology-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

### 2.3 执行 knowledge_report（行为科学专题）

**适用场景**：整合多篇精读归纳为专题（如"认知偏差全景图"整合 Kahneman/Tversky 系列）。

**报告结构**：

```
1. 专题定义与范围
2. 核心概念矩阵（概念 × 代表实验 × 效应量 × 复现状况）
3. 理论演化路径
4. 实践应用（行为经济学·临床·教育）
5. 局限性与争议（包含"复现危机"影响）
6. 延伸阅读建议
```

---

## §3 Output Standards（输出规范）

### 文件命名

```
paper_analysis:  {序号}_{作者}_{关键词}_{年份}.md
                 例：08_bandura_bobo_1961.md
knowledge_report: {主题}_{全景图|图谱|...}.md
                 例：认知偏差_全景图.md
```

**序号规则**：读取 `reports/paper_analyses/` 现有文件，取最大序号 +1。

### 质量标准

- 实验数据（样本量、p值、效应量等）必须来自原始论文，精确引用
- 必须包含"实验局限性与当代复现"章节
- 区分"已复现"、"部分复现"、"未能复现"三种状态
- 报告行数 ≥ 120 行

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目
2. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — task status → done，填写 done_at，追加到已完成列表

### 完成后必须校验

```
[commit 前必须运行]
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project=psychology-learning
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
| `docs/LEARNING_PROJECTS_TASK_BOARD.md` | ✅ 仅更新自身任务行 + 追加已完成条目 |
| `skills/` | ❌ 只读 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目任意路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` / `scripts/` | ❌ 禁止 |

---

## §5 Commit Protocol（提交规范）

```bash
# 提交前需先配置 git 身份（从全局 AGENTS.md 获取当前模型名称）
git add reports/ CONTEXT.md docs/LEARNING_PROJECTS_TASK_BOARD.md
git commit -m "[task-execution] psychology-learning: {报告标题简述}

Agent: PsycheAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。

---

## §6 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"已有报告"区，禁止重复生成
2. 实验数据（样本量、p值、结论）必须以原始论文为准，不得引用二手综述替代
3. 复现状况须基于已发表研究，不得推测
4. 争议性实验（如 Zimbardo 斯坦福监狱实验）须同时呈现支持与批评两方声音
5. 禁止将"历史影响"与"科学有效性"混为一谈
