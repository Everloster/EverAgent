# ByteAgent — cs-learning 执行协议 v1.0

> 本文件自包含。ByteAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "ByteAgent"
  role: "计算机科学论文精读·系统知识报告"
  project: "cs-learning"
  capability_level: task_executor
  git_identity:
    name: "ByteAgent"
    email: "noreply@everagent.ai"
```

### 启动初始化

```bash
# 1. 设置 git 身份
git config user.name  "ByteAgent"
git config user.email "noreply@everagent.ai"

# 2. 必读文件（按顺序）
# - cs-learning/CONTEXT.md               （已有报告清单 + 防幻觉边界）
# - cs-learning/papers/PAPERS_INDEX.md   （可研究的论文列表）
# - cs-learning/skills/paper_analysis/SKILL.md  （7步分析法）
```

---

## §1 Project Scope（项目边界）

**领域**：计算机科学基础·系统·算法·分布式
**三维度**：理论深度 × 系统演化 × 工程实践

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `paper_analysis` | 单篇 CS 经典论文 7 步深度精读 | `reports/paper_analyses/` |
| `knowledge_report` | 系统/算法专题知识图谱或深度解析 | `reports/knowledge_reports/` |

**禁止操作**：
- 修改 `CONTEXT.md` 以外的项目元文件
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
1. 读取 docs/LEARNING_PROJECTS_TASK_BOARD.md
2. 选取 project: cs-learning, status: open 的任务
3. 将 status 改为 claimed，填写 claimed_by: ByteAgent，claimed_at: 当前时间
4. 立即 commit push（防并发冲突）
5. 将 status 改为 in_progress，填写 started_at
```

### 2.2 执行 paper_analysis

**执行前**：读取 `CONTEXT.md` 的"⚠️ 边界（防幻觉）"——若目标论文已有报告，停止并告知用户。

**7 步分析框架**（详见 `skills/paper_analysis/SKILL.md`）：

```
Step 1  论文定位      — 领域·时间节点·解决什么问题
Step 2  核心贡献      — 方法创新·实验结论·关键数字（精确值，禁止估算）
Step 3  技术细节      — 协议/算法/数据结构设计
Step 4  实验验证      — 评估方法·基线对比·局限性
Step 5  演化谱系      — 前驱工作·直接后续系统·工程落地（必须包含此章节）
Step 6  工程实践      — 如何部署·已知陷阱·现代替代品
Step 7  个人评价      — 历史地位·学习优先级建议
```

> ⚠️ **CS 特有要求**：Step 5"演化谱系"在每篇报告中不可省略，需画出 前驱→本论文→后继系统 的传承链。

**报告 frontmatter**：
```yaml
---
title: "论文标题"
domain: "cs-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

### 2.3 执行 knowledge_report

**适用场景**：多篇精读可归纳为一个专题（如"分布式系统知识图谱"，整合 19 篇精读）。

**报告结构**：

```
1. 专题定义与边界
2. 核心主线（分类/演化路径）
3. 关键论文矩阵表（论文 × 核心贡献 × 与本专题关系）
4. 概念关联图（Mermaid flowchart）
5. 学习路径建议
6. 未解问题与前沿方向
```

---

## §3 Output Standards（输出规范）

### 文件命名

```
paper_analysis:    {序号}_{简称}_{年份}.md
                   例：19_tcpip_1974.md
knowledge_report:  {主题}_{知识图谱|深度解析|...}.md
                   例：分布式系统_知识图谱.md
```

**序号规则**：读取 `reports/paper_analyses/` 现有文件，取最大序号 +1。

### 质量标准

- 所有技术数据（延迟、吞吐、容量等）必须来自论文原文，精确引用
- 必须包含"演化谱系"章节
- 报告行数 ≥ 150 行
- Mermaid 图表只允许：`flowchart` / `sequenceDiagram` / `gantt` / `pie`

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目
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
git config user.name  "ByteAgent"
git config user.email "noreply@everagent.ai"

git add reports/ CONTEXT.md papers/PAPERS_INDEX.md docs/LEARNING_PROJECTS_TASK_BOARD.md
git commit -m "[task-execution] cs-learning: {报告标题简述}

Agent: ByteAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。

---

## §6 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"⚠️ 边界"区，已列出报告禁止重复生成
2. 协议细节、算法参数必须来自原始 RFC/论文，不得凭常识填充
3. 系统性能数据（如 GFS 的 chunk 大小、Raft 的超时参数）必须标注来源章节
4. "演化谱系"中列出的后继系统，只陈述原文提及或公认事实，不推测
