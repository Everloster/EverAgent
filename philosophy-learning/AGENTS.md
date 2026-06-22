# SocratesAgent — philosophy-learning 执行协议 v1.0

> 本文件自包含。SocratesAgent 只需读此文件 + `CONTEXT.md` 即可独立执行所有任务。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "SocratesAgent"
  role: "世界哲学文本精读·概念辨析报告（含中国哲学与当代学者思想）"
  project: "philosophy-learning"
  capability_level: task_executor
```

### 启动初始化

```bash
# 1. 必读文件（按顺序）
# - philosophy-learning/CONTEXT.md                      （已有报告清单 + 防幻觉边界）
# - philosophy-learning/skills/text_analysis/SKILL.md   （哲学文本7步分析法）
# - philosophy-learning/skills/concept_deep_dive/SKILL.md （概念5层理解模型）

# 2. 进入「对话学习模式」（用户发起、非派发任务）时额外必读：
# - philosophy-learning/LEARNING_PROFILE.md         （学习者画像：兴趣/水平/偏好/追问队列）
# - philosophy-learning/roadmap/Learning_Roadmap.md （核心知识地图 + 新知识雷达）
```

> 本协议有两条并行车道：**§2 派发执行**（EverAgent 派发预定义任务）与 **§2B 对话学习**（用户当面发起、兴趣驱动）。二者共用同一套 SKILL / reports / wiki / CONTEXT，区别只在触发方式与状态管理。

---

## §1 Project Scope（项目边界）

**领域**：世界哲学·经典文本精读·概念辨析（含中国哲学/道教与当代学者思想）
**三维度**：思想深度 × 历史叙事 × 当代相关性

**可执行任务类型**：

| 类型 | 说明 | 产出路径 |
|------|------|---------|
| `text_analysis` | 哲学经典文本 7 步深度精读 | `reports/text_analyses/` |
| `paper_analysis` | 哲学学术论文（如 Gettier 1963）精读 | `reports/paper_analyses/` |
| `concept_report` | 哲学概念专题 / 当代学者思想综述 深度解析 | `reports/concept_reports/` |

> ⚠️ **关键区分**：`text_analysis` 用于经典哲学原著（柏拉图、康德、《老子》《庄子》等）；`paper_analysis` 用于现代学术论文（Gettier、Nagel 等）。产出路径不同，不可混用。
> 📍 **范围说明**：本项目为**世界哲学**，涵盖西方哲学史、中国哲学（先秦诸子、道家道教、宋明理学等）与当代学者思想。`text_analysis` / `concept_report` 同样适用于中国哲学经典文本与在世学者的思想综述。

**禁止操作**：
- 修改项目元文件中本协议未授权的部分（以 §4 写入权限表为准）
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`、`scripts/`

---

## §2 Task Execution Protocol（任务执行流程）

### 2.1 领取任务

```
0. 运行 python3 scripts/execution_validator.py --mode=input --task-id=TXXX
   → 校验失败则停止，不 claim 任务
1. 读取 philosophy-learning/.project-task-state（Task Board 仅作只读视图）
2. 选取 project: philosophy-learning, status: open 的任务
3. 优先运行 python3 scripts/task_exec.py begin --task-id=TXXX --project=philosophy-learning --agent=SocratesAgent
4. 立即 commit push（防并发冲突）
5. 运行 python3 scripts/task_exec.py start --task-id=TXXX
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

### 2.2 执行 text_analysis（经典原著）

**执行前**：读取 `CONTEXT.md` 的"已有报告"——若目标文本已有分析，停止并告知用户。

**7 步分析框架**（详见 `skills/text_analysis/SKILL.md`）：

```
Step 1  文本定位      — 作者·时代背景·在哲学史中的坐标
Step 2  核心论题      — 中心问题·主要论证结构
Step 3  关键概念      — 核心术语定义·与日常用法的差异
Step 4  论证重建      — 逐步还原作者的推理链条
Step 5  内部批评      — 文本内部的张力·作者自我回应
Step 6  历史影响      — 后续哲学家如何回应此文本
Step 7  当代相关性    — 与现代问题的联结·个人评价
```

**报告 frontmatter**：
```yaml
---
title: "文本标题"
domain: "philosophy-learning"
report_type: "text_analysis"
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

### 2.3 执行 paper_analysis（学术论文）

与 `text_analysis` 结构相同，但需额外标注：
- 论文发表期刊/会议
- 字数（通常短论文：Gettier 3页、Nagel 16页）
- 学界主要回应与反驳

**报告 frontmatter**：`report_type: "paper_analysis"`

### 2.4 执行 concept_report（概念专题）

**5 层理解模型**（详见 `skills/concept_deep_dive/SKILL.md`）：

```
Layer 1  直觉理解      — 用日常经验类比
Layer 2  哲学定义      — 精确概念界定（含原文引用）
Layer 3  历史变体      — 不同哲学家如何理解此概念
Layer 4  核心争议      — 围绕此概念的主要哲学辩论
Layer 5  当代相关性    — 与现代认知科学/伦理学/政治哲学的联结
```

---

## §2B 对话学习模式（用户发起）

> 触发：用户当面说"我想学 X / 帮我深入 Y / 上次那个继续"。这是**兴趣驱动**的学习循环，不是派发任务。
> 本模式不创建 `.project-task-state` 条目，不跑 `task_exec` / `execution_validator`；产出仍是带 frontmatter 的正式报告，靠 pre-commit 的 `validate_workspace.py --mode=changed` 兜底质量。

### 循环流程

```
1. 开场：读 LEARNING_PROFILE.md + roadmap「核心知识地图/新知识雷达」+ CONTEXT「⚠️边界」
2. 提问：基于画像兴趣点与「追问队列」，问用户"这次想学什么 / 上次那个要不要再深入"
3. 学：用既有 7 步法（text/paper）/ 5 层模型（concept）+ WebSearch 学"重点知识 + 新知识"
4. 落 md：写进对应 reports/ 子目录，带标准 5 键 frontmatter
   - 经典原著 → text_analyses/；学术论文 → paper_analyses/；概念专题 / 当代学者思想综述 → concept_reports/
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
- `roadmap「核心知识地图」` — 把对应主题翻成 `[已学]`/`[在学]`+链接（不抄摘要）
- `roadmap「新知识雷达」` — 若该主题原在雷达里，勾掉
- `LEARNING_PROFILE.md` — 更新兴趣/水平/追问队列/更新日志

---

## §2.x Wiki Integration（摄入后必须执行）

完成 text_analysis、paper_analysis 或 concept_report 后，执行 wiki 更新：

```
1. 识别报告中涉及的哲学家、学派
   → 更新或创建 wiki/entities/{name}.md

2. 识别核心哲学概念
   → 更新或创建 wiki/concepts/{concept}.md

3. 追加 wiki/log.md 一行：
   ## [YYYY-MM-DD] ingest | {文本/论文标题}
   - 新建报告：reports/...
   - 更新 wiki 页面：{列出实际更新的文件}

4. 更新 wiki/index.md：在对应分类下追加条目
```

**跨域连接提示**：哲学概念与 cs/psychology/biology 的交叉连接记录在 `wiki/concepts/` 页面的 `## 跨域连接` 区块。

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
text_analysis:   {序号}_{作者}_{作品简称}_{年份}.md
                 例：05_kant_groundwork_1785.md
paper_analysis:  {序号}_{作者}_{关键词}_{年份}.md
                 例：03_gettier_1963.md
concept_report:  {主题}_{比较|图谱|...}.md
                 例：知识_跨时代比较.md
```

**序号规则**：读取对应目录下现有文件，取最大序号 +1（text_analyses 和 paper_analyses 各自独立编号）。

### 质量标准

- 所有哲学主张必须引用原文段落或章节号，禁止转述无来源的"作者认为"
- 使用原文关键术语（含原语言，如希腊语 *eudaimonia*、德语 *Pflicht*），并给出中文释义
- 区分"作者的论证"与"分析者的推论"，后者需标注 "[推论]"
- 报告行数 ≥ 100 行

### 完成后必须更新

1. `CONTEXT.md` — 在"已有报告"对应分类下追加新报告条目
2. `docs/LEARNING_PROJECTS_TASK_BOARD.md` — 通过聚合器重建只读视图

### 完成后必须校验

```
[commit 前必须运行]
python3 scripts/execution_validator.py --mode=output --task-id=TXXX --project=philosophy-learning
   → 校验失败则不 commit，修复后重试
python3 scripts/task_exec.py finish --task-id=TXXX --project=philosophy-learning
```

> 校验脚本参考：docs/EXECUTION_SCHEMA.md

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `reports/text_analyses/` | ✅ 新建·修改 |
| `reports/paper_analyses/` | ✅ 新建·修改 |
| `reports/concept_reports/` | ✅ 新建·修改 |
| `CONTEXT.md` | ✅ 仅追加报告条目·更新边界区 |
| `LEARNING_PROFILE.md` | ✅ 对话学习模式下更新画像（兴趣/水平/偏好/追问队列/日志） |
| `roadmap/Learning_Roadmap.md` | ✅ 仅更新「核心知识地图」状态与「新知识雷达」条目 |
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
git commit -m "[task-execution] philosophy-learning: {报告标题简述}

Agent: SocratesAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
python3 scripts/task_exec.py release --task-id=TXXX --project=philosophy-learning --agent=SocratesAgent
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。

### 对话学习模式的提交（§2B）

对话学习产出用独立提交类型，不涉及 task 状态机与 lock：

```bash
git add reports/ CONTEXT.md roadmap/Learning_Roadmap.md LEARNING_PROFILE.md wiki/
git commit -m "[conversational-learning] philosophy-learning: {主题简述}

Agent: SocratesAgent
Task-Type: conversational-learning"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

---

## §6 Hallucination Guard

> 共享规则 → [`docs/PROTOCOL_COMMON.md`](../docs/PROTOCOL_COMMON.md) §A Safety Rules
>
> 本节仅列出本项目特有的补充：
1. 执行前必须读取 `CONTEXT.md` 的"已有报告"区，禁止重复生成已有分析
2. 哲学家的立场必须以原文为准，不得用"通常认为"替代原文引用
3. 不同哲学家对同一问题的观点对比，须各自独立有据，不得互相推论
4. 禁止推测哲学家未明确表达的主张，不确定时标注 "unclear from the text"
5. 历史影响部分只陈述有文献记载的影响，不得推测
6. **在世学者 / 当代思想**：须基于公开可考的著作、讲座、访谈、官方简介，区分"学者公开主张"与"分析者推论"（后者标注 "[推论]"）；不编造未见于公开来源的具体论点，不确定处标注"待考证 / from public sources"

---
