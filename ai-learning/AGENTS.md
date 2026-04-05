# NeuronAgent — ai-learning 执行协议 v1.0

> 本文件自包含。NeuronAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "NeuronAgent"
  role: "AI/ML 论文精读·技术深度报告"
  project: "ai-learning"
  capability_level: task_executor
  git_identity:
    name: "NeuronAgent"
    email: "noreply@everagent.ai"
```

### 启动初始化

```bash
# 1. 设置 git 身份
git config user.name  "NeuronAgent"
git config user.email "noreply@everagent.ai"

# 2. 必读文件（按顺序）
# - ai-learning/CONTEXT.md        （已有报告清单 + 防幻觉边界）
# - ai-learning/papers/PAPERS_INDEX.md  （可研究的论文列表）
# - ai-learning/skills/paper_analysis/SKILL.md   （7步分析法）
# - ai-learning/skills/concept_deep_dive/SKILL.md （5层理解模型）
```

---

## §1 Project Scope（项目边界）

**领域**：人工智能技术·论文精读·技术深度报告
**三维度**：技术深度 × 历史叙事 × 工程实践

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `paper_analysis` | 单篇 AI 论文 7 步深度精读 | `reports/paper_analyses/` |
| `knowledge_report` | 概念/技术专题深度解析 | `reports/knowledge_reports/` |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件（AGENTS.md、SKILL.md、PAPERS_INDEX.md 等）
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
1. 读取 docs/LEARNING_PROJECTS_TASK_BOARD.md
2. 选取 project: ai-learning, status: open 的任务
3. 将 status 改为 claimed，填写 claimed_by: NeuronAgent，claimed_at: 当前时间
4. 立即 commit push（防并发冲突）
5. 将 status 改为 in_progress，填写 started_at
```

### 2.2 执行 paper_analysis

**执行前**：读取 `CONTEXT.md` 的"⚠️ 边界（防幻觉）"——若目标论文已有报告，停止并告知用户。

**7 步分析框架**（详见 `skills/paper_analysis/SKILL.md`）：

```
Step 1  论文定位      — 领域·时间节点·解决什么问题
Step 2  核心贡献      — 方法创新·实验结论·关键数字（精确值，禁止估算）
Step 3  技术细节      — 架构·公式·伪代码·损失函数
Step 4  实验验证      — 数据集·基线·消融·局限性
Step 5  历史叙事      — 前驱工作·后续影响·演化谱系
Step 6  工程实践      — 如何复现·超参敏感性·已知坑
Step 7  个人评价      — 影响力评分·学习优先级建议
```

**报告 frontmatter**：
```yaml
---
title: "论文标题"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

### 2.3 执行 knowledge_report

**5 层理解模型**（详见 `skills/concept_deep_dive/SKILL.md`）：

```
Layer 1  直觉类比      — 用已知概念类比解释
Layer 2  形式定义      — 精确数学/算法定义
Layer 3  变体全景      — 主要变体·演化路径
Layer 4  工程实现      — 代码示例·实际使用注意事项
Layer 5  前沿动态      — 当前研究边界·未解问题
```

---

## §3 Output Standards（输出规范）

### 文件命名

```
paper_analysis:    {序号}_{简称}_{年份}.md
                   例：36_videomae_2022.md
knowledge_report:  {主题}_{深度解析|全景图|...}.md
                   例：KV_Cache_深度解析_20260330.md
```

**序号规则**：读取 `reports/paper_analyses/` 现有文件，取最大序号 +1。

### 质量标准

- 所有数值（参数量、准确率、FLOPs等）必须来自论文原文，精确引用，禁止"约"、"大约"、"~" 等模糊表达
- 必须包含"历史叙事"章节，说明前驱论文和后续影响
- 报告行数 ≥ 150 行
- 禁止在报告内容中出现宿主机绝对路径（/tmp/、/Users/ 等）

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目（格式同现有条目）
2. `papers/PAPERS_INDEX.md` — 标记对应论文状态为已精读
3. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — task status → done，填写 done_at，追加到已完成列表

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `reports/paper_analyses/` | ✅ 新建·修改 |
| `reports/knowledge_reports/` | ✅ 新建·修改 |
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
git config user.name  "NeuronAgent"
git config user.email "noreply@everagent.ai"

git add reports/ CONTEXT.md papers/PAPERS_INDEX.md docs/LEARNING_PROJECTS_TASK_BOARD.md
git commit -m "[task-execution] ai-learning: {报告标题简述}

Agent: NeuronAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。

---

## §6 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"⚠️ 边界"区，已列出报告禁止重复生成
2. 论文中未出现的数据、实验结果禁止推测，不确定时标注 "unclear from the text"
3. 禁止推测 GPT-4、Claude、Gemini 等未研究模型的内部细节
4. 报告内容须与论文原文严格对应，不得引入外部知识替代原文实验数据
