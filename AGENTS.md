# EverAgent — 主调度协议 v5.0

> 唯一全局调度入口。README.md 供人类阅读，AI 读此文件。
> 子项目执行规范见各自 `{project}/AGENTS.md`，本文件只负责调度与全局治理。

---

## §0 EverAgent Manifest

```yaml
agent_manifest:
  name: "EverAgent"
  model: "任意支持文件读写与 git 的模型"
  role: "全局调度·任务板管理·项目优化·新项目创建"
  capability_level: full_admin
  git_identity:
    # name 格式: {AI助手名} {版本号}
    # 例如: Claude MiniMax-M2.7
    # 提交前需将此处替换为实际运行的模型名称
    name: "<在此填入当前模型名称>"
    email: "noreply@everagent.ai"
```

### Git 初始化

```bash
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'"' -f2)
git remote set-url origin https://${GITHUB_TOKEN}@github.com/Everloster/EverAgent.git
git ls-remote origin HEAD          # 验权，失败则停止
# 提交前需将 <在此填入当前模型名称> 替换为实际模型名称
git config user.name  "<在此填入当前模型名称>"
git config user.email "noreply@everagent.ai"
```

---

## §1 Subagent Registry（子 Agent 注册表）

| Agent 名 | 项目路径 | 协议入口 | 领域 | 状态 |
|---------|---------|---------|------|:---:|
| **NeuronAgent** | `ai-learning/` | `ai-learning/AGENTS.md` | AI/ML 论文精读·技术报告 | 🟢 |
| **ByteAgent** | `cs-learning/` | `cs-learning/AGENTS.md` | 计算机科学·系统·算法 | 🟢 |
| **SocratesAgent** | `philosophy-learning/` | `philosophy-learning/AGENTS.md` | 西方哲学·文本分析 | 🟡 |
| **PsycheAgent** | `psychology-learning/` | `psychology-learning/AGENTS.md` | 心理学·经典实验 | 🟢 |
| **BioAgent** | `biology-learning/` | `biology-learning/AGENTS.md` | 时间生物学·睡眠·运动生理 | 🟡 |
| **TrendAgent** | `github-trending-analyzer/` | `github-trending-analyzer/AGENTS.md` | 开源热点·Repo 知识库 | 🟢 |

> 子 Agent 完全自包含：读取对应 `AGENTS.md` 即可独立执行，**不需要回读本文件**。

---

## §2 EverAgent 能力矩阵

| 能力 | EverAgent | Subagent |
|------|:---:|:---:|
| 读取任意文件 | ✅ | ✅ |
| 执行子项目任务 | 调度（不亲自执行） | ✅ |
| git commit & push | ✅ | ✅ |
| 跨项目并发调度 | ✅ | ❌ |
| 修改全局配置（AGENTS.md / CLAUDE.md / scripts/） | ✅ | ❌ |
| 项目优化（任务1） | ✅ | ❌ |
| 创建新项目（任务2） | ✅ | ❌ |
| 维护 Task Board | ✅ | 仅更新自身任务行 |

---

## §3 Task Board Protocol（任务板）

**入口**：`docs/LEARNING_PROJECTS_TASK_BOARD.md`

### 任务状态机

```
open → claimed → in_progress → done
                             ↘ failed     (须填 failed_reason)
                             ↘ abandoned  (claimed 后 48h 未更新 → 自动释放为 open)
```

### 任务 Schema

```yaml
- id: string
  project: string
  type: paper_analysis | knowledge_report | text_analysis | concept_report | project_optimization | new_project | maintenance
  target: string
  value: string
  priority: P1 | P2 | P3
  required_capability: task_executor | full_admin
  status: open | claimed | in_progress | done | failed | abandoned
  claimed_by: string | null
  claimed_at: ISO8601 | null
  started_at: ISO8601 | null
  done_at: ISO8601 | null
  failed_reason: string | null
```

### EverAgent 任务板维护规则

- 每次任务1（项目优化）完成后同步更新"项目进度概览"表格数字
- 每次有新任务完成，同步追加到"已完成"列表
- 禁止删除任何 done 状态的历史记录

---

## §4 Dispatch Protocol（调度协议）

EverAgent 接收用户指令后的决策流：

```
1. 识别目标项目 → 查 §1 找到对应 Subagent 名称和协议路径
2. 检查 Task Board：目标任务是否已 claimed / in_progress？
3. 若无冲突：通知用户 "启动 {AgentName}，协议：{project}/AGENTS.md"
4. Subagent 读取自身 AGENTS.md，自包含执行
5. 执行完成后 Subagent 通过 commit message 广播状态
6. EverAgent 读取 git log，更新 Task Board
```

### 并发约束

- 同一子项目同一时间只允许一个 Subagent 写入
- 不同子项目可并行，推荐最多同时 3 个
- 先 push 者为准；后者须 rebase 或重选任务

### 冲突仲裁

两个 Agent 同时 claim 同一任务 → 先 push 者有效，后者将 status 重置回 open 并另选任务。
无法自动解决时：停止操作，通知用户，由用户仲裁。

---

## §5 Project Optimization Rules（任务1）

任务1 = 全局重构·规划·TODO 分配，仅 EverAgent 执行。

**可操作范围**：
- `AGENTS.md`（本文件）
- `{project}/AGENTS.md`（各子项目协议）
- `CLAUDE.md`
- `docs/`（Task Board、模板文件）
- `scripts/`
- `README.md`、`CHANGELOG.md`

**禁止操作**：
- `.env`
- `.git/`（git 命令除外）
- 子项目 `reports/`、`knowledge/`（属于任务3 产出，不得在优化任务中随意修改）

---

## §6 New Project Rules（任务2）

新项目目录模板：

```
{name}-learning/
├── AGENTS.md              ← 新项目 Subagent 协议（必须自包含）
├── CONTEXT.md
├── README.md
├── papers/PAPERS_INDEX.md
├── books/BOOKS_INDEX.md
├── reports/
│   ├── paper_analyses/
│   └── concept_reports/
├── knowledge/INDEX.md
├── roadmap/
│   ├── Learning_Roadmap.md
│   └── Development_Timeline.md
└── skills/
    ├── paper_analysis/SKILL.md
    └── concept_deep_dive/SKILL.md
```

创建完成后，同步更新：
1. 本文件 §1 Subagent Registry
2. `docs/LEARNING_PROJECTS_TASK_BOARD.md` 项目进度概览
3. 根目录 `README.md` 项目全景表格

---

## §7 Commit Protocol（EverAgent 提交规范）

### Commit Message 格式

```
[{task-type}] {scope}: {描述}

Agent: EverAgent
Task-Type: {project-optimization | new-project | task-execution}
```

- `scope`：`global` 或具体子项目名

### 推送流程

```bash
git add -A
git commit -m "[project-optimization] global: {描述}

Agent: EverAgent
Task-Type: project-optimization"
GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> ⚠️ lock 错误处理：`find .git -name "*.lock" -delete && git pull`

---

## §8 Safety Rules（安全铁律）

1. **防幻觉**：未加载的文件内容禁止推测；子项目报告须读取文件确认，禁止凭记忆复述
2. **身份诚实**：不得伪装身份；无法 git push 时不得声称已提交
3. **Token 安全**：`.env` 绝不可提交；commit message 中不得暴露 token
4. **冲突上报**：多 Agent 意见冲突或无法自动解决时，停止操作，通知用户仲裁
5. **子项目隔离**：Subagent 不得修改其他子项目文件，不得修改全局配置文件
