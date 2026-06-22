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
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - ai-learning/CONTEXT.md        （已有报告清单 + 防幻觉边界）
# - ai-learning/papers/PAPERS_INDEX.md  （可研究的论文列表）
# - ai-learning/skills/paper_analysis/SKILL.md   （7步分析法）
# - ai-learning/skills/concept_deep_dive/SKILL.md （5层理解模型）

# 2. 进入「对话学习模式」（用户发起、非派发任务）时额外必读：
# - ai-learning/LEARNING_PROFILE.md         （学习者画像：兴趣/水平/偏好/追问队列）
# - ai-learning/roadmap/Learning_Roadmap.md （核心知识地图 + 新知识雷达）
```

> 本协议有两条并行车道：**§2 派发执行**（EverAgent 派发预定义任务）与 **§2B 对话学习**（用户当面发起、兴趣驱动）。二者共用同一套 SKILL / reports / wiki / CONTEXT，区别只在触发方式与状态管理。

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
- 修改项目元文件中本协议未授权的部分（AGENTS.md、SKILL.md、PAPERS_INDEX.md 结构等）；可写文件以 §4 写入权限表为准
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
   → 校验失败则停止，不 claim 任务
1. 读取 ai-learning/.project-task-state（Task Board 仅作只读视图）
2. 选取 project: ai-learning, status: open 的任务
3. 优先运行 python3 scripts/task_exec.py begin --task-id=TXXX --project=ai-learning --agent=NeuronAgent
4. 立即 commit push（防并发冲突）
5. 运行 python3 scripts/task_exec.py start --task-id=TXXX
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

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

## §2B 对话学习模式（用户发起）

> 触发：用户当面说"我想学 X / 帮我深入 Y / 上次那个继续"。这是**兴趣驱动**的学习循环，不是派发任务。
> 本模式不创建 `.project-task-state` 条目，不跑 `task_exec` / `execution_validator`；产出仍是带 frontmatter 的正式报告，靠 pre-commit 的 `validate_workspace.py --mode=changed` 兜底质量。

### 循环流程

```
1. 开场：读 LEARNING_PROFILE.md + roadmap「核心知识地图/新知识雷达」+ CONTEXT「⚠️边界」
2. 提问：基于画像兴趣点与「追问队列」，问用户"这次想学什么 / 上次那个要不要再深入"
3. 学：用既有 7 步法（paper）/ 5 层模型（concept）+ WebSearch 学"重点知识 + 新知识"
4. 落 md：写进 reports/knowledge_reports/（或 paper_analyses/），带标准 5 键 frontmatter
5. 用户读 md 自学
6. 用户追问：
   - 命中已有报告 → 在该文件追加 "## 追问深入 [日期]" 小节，刷新 frontmatter 的 updated_on
     （复用报告末「知识检验题」作追问钩子；绝不为追问另开新报告）
   - 是全新主题 → 回到第 3 步新建报告
7. 沉淀：按 §2.x 更新 wiki；按下方"完成后必须更新"刷新 CONTEXT 台账与 roadmap 状态
8. 更新画像：把新兴趣/水平变化/偏好/未解问题写入 LEARNING_PROFILE.md（禁止凭空臆测）
```

### 三个关键规则

1. **不走 task 状态机**：对话报告无需 `.project-task-state` 条目，不运行 begin/start/finish/execution_validator。
2. **仍过文件校验**：报告必须带 5 键 frontmatter（title/domain/report_type/status/updated_on），命名遵循 §3 规范，否则 pre-commit 拦截。
3. **追问 = 续写既有报告**：用 frontmatter 命中已存在报告并追加小节，不另开新文件——这样同一主题的理解持续加深而非散落。

### 完成后必须更新（与 §3 共用，去重分工）

- `CONTEXT.md「已有报告」` — 唯一成品台账，追加/更新报告条目（含摘要）
- `roadmap「核心知识地图」` — 把对应主题翻成 `[已学]`+链接（不抄摘要）
- `roadmap「新知识雷达」` — 若该主题原在雷达里，勾掉
- `LEARNING_PROFILE.md` — 更新兴趣/水平/追问队列/更新日志

---

## §2.x Wiki Integration（摄入后必须执行）

完成 paper_analysis 或 knowledge_report 后，执行 wiki 更新：

```
1. 识别报告中涉及的人物、机构
   → 更新或创建 wiki/entities/{name}.md

2. 识别核心概念（架构、方法、现象）
   → 更新或创建 wiki/concepts/{concept}.md

3. 追加 wiki/log.md 一行：
   ## [YYYY-MM-DD] ingest | {论文/报告标题}
   - 新建报告：reports/...
   - 更新 wiki 页面：{列出实际更新的文件}

4. 更新 wiki/index.md：在对应分类下追加条目
```

**页面格式参考**：`llm-wiki-plan.md` §四

**写入权限**：

| 路径 | 权限 |
|------|------|
| `wiki/entities/` | ✅ 新建·追加更新 |
| `wiki/concepts/` | ✅ 新建·追加更新 |
| `wiki/syntheses/` | ✅ 新建（归档有价值的问答） |
| `wiki/index.md` | ✅ 追加条目 |
| `wiki/log.md` | ✅ 仅 append |

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

- 所有关键数值（参数量、准确率、FLOPs等）必须注明来源；若来源原文本身为新闻、综述或访谈中的近似表达，可保留原文语气并标明出处
- 必须包含"历史叙事"章节，说明前驱论文和后续影响
- 报告行数 ≥ 150 行
- 禁止在报告内容中出现宿主机绝对路径（/tmp/、/Users/ 等）

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"列表追加新报告条目（格式同现有条目）
2. `papers/PAPERS_INDEX.md` — 标记对应论文状态为已精读
3. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — 通过聚合器重建只读视图

### 完成后必须校验

```
[commit 前必须运行]
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project=ai-learning
   → 校验失败则不 commit，修复后重试
python3 scripts/task_exec.py finish --task-id=TXXX --project=ai-learning
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `reports/paper_analyses/` | ✅ 新建·修改 |
| `reports/knowledge_reports/` | ✅ 新建·修改 |
| `CONTEXT.md` | ✅ 仅追加报告条目·更新边界区 |
| `LEARNING_PROFILE.md` | ✅ 对话学习模式下更新画像（兴趣/水平/偏好/追问队列/日志） |
| `roadmap/Learning_Roadmap.md` | ✅ 仅更新「核心知识地图」状态与「新知识雷达」条目 |
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
git commit -m "[task-execution] ai-learning: {报告标题简述}

Agent: NeuronAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
python3 scripts/task_exec.py release --task-id=TXXX --project=ai-learning --agent=NeuronAgent
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。

### 对话学习模式的提交（§2B）

对话学习产出用独立提交类型，不涉及 task 状态机与 lock：

```bash
git add reports/ CONTEXT.md roadmap/Learning_Roadmap.md LEARNING_PROFILE.md wiki/
git commit -m "[conversational-learning] ai-learning: {主题简述}

Agent: NeuronAgent
Task-Type: conversational-learning"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

---

## §6 Hallucination Guard（防幻觉铁律）

1. 执行前必须读取 `CONTEXT.md` 的"⚠️ 边界"区，已列出报告禁止重复生成
2. 论文中未出现的数据、实验结果禁止推测，不确定时标注 "unclear from the text"
3. 禁止推测 GPT-4、Claude、Gemini 等未研究模型的内部细节
4. 报告内容须与论文原文严格对应，不得引入外部知识替代原文实验数据
