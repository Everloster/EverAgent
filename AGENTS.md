# EverAgent — AI Agent 协作协议 v4.0

> 唯一全局入口。README.md 供人类阅读，AI 忽略。
> 兼容任何支持文件读取与 git 操作的 AI Agent 框架。

---

## §0 Agent Manifest（声明式身份）

每次新对话开始时，Agent **必须声明自身 manifest**，然后按 manifest 初始化环境。
无需运行时自检身份——能力由声明决定，不依赖模型品牌。

### Manifest 格式

```yaml
agent_manifest:
  name: "模型全称"          # 例：Claude Sonnet 4.6 / GPT-4o / Gemini 2.0
  framework: "框架名"       # 例：claude-code / openai-agents / langgraph / autogen
  capability_level: full_admin  # read_only | task_executor | full_admin（见 §1）
  git_identity:
    name: "提交者名称"       # 填入模型全称，例：Claude Sonnet 4.6
    email: "提交者邮箱"      # 例：noreply@anthropic.com
```

### Git 初始化（capability ≥ task_executor 时执行）

```bash
# 1. 读 token
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'"' -f2)
# 2. 配远程
git remote set-url origin https://${GITHUB_TOKEN}@github.com/Everloster/EverAgent.git
# 3. 验权限（失败则降级为 read_only）
git ls-remote origin HEAD
# 4. 设提交者（从 manifest.git_identity 读取）
git config user.name  "<manifest.git_identity.name>"
git config user.email "<manifest.git_identity.email>"
```

### read_only 模式

capability = read_only 时：

✅ 读取任意文件 / 提供分析问答　　❌ 创建·修改·删除文件　　❌ git 操作

---

## §1 Capability Matrix（能力矩阵）

权限由 **capability_level** 决定，与模型品牌无关。

| 能力 | read_only | task_executor | full_admin |
|------|:---:|:---:|:---:|
| 读取任意文件 | ✅ | ✅ | ✅ |
| 执行任务（任务3） | ❌ | ✅ | ✅ |
| git commit & push | ❌ | ✅ | ✅ |
| 跨项目并发操作 | ❌ | ❌ | ✅ |
| 项目优化（任务1） | ❌ | ❌ | ✅ |
| 创建新项目（任务2） | ❌ | ❌ | ✅ |
| 修改全局配置文件 | ❌ | ❌ | ✅ |

> **声明高于实际能力**：若 Agent 声明 full_admin 但实际无法 git push，应降级为 task_executor 并告知用户。

---

## §2 Project Registry（项目注册表）

| 项目 | CONTEXT 入口 | 领域 | 状态 |
|------|-------------|------|:---:|
| ai-learning | `./ai-learning/CONTEXT.md` | AI/ML 论文精读·技术报告 | 🟢 |
| cs-learning | `./cs-learning/CONTEXT.md` | 计算机科学·系统·算法 | 🟡 |
| philosophy-learning | `./philosophy-learning/CONTEXT.md` | 西方哲学史·文本分析 | 🟡 |
| psychology-learning | `./psychology-learning/CONTEXT.md` | 心理学·经典实验 | 🟡 |
| biology-learning | `./biology-learning/CONTEXT.md` | 时间生物学·睡眠·运动生理 | 🔵 |
| github-trending-analyzer | `./github-trending-analyzer/CONTEXT.md` | 开源热点·Repo 知识库 | 🟢 |

---

## §3 Task Protocol（任务协议）

### 3.1 任务类型

| 类型 | 说明 | 所需 capability |
|------|------|:---:|
| 任务1：项目优化 | 全局重构、规划、TODO 分配；可跨项目加载 CONTEXT.md | full_admin |
| 任务2：创建新项目 | 按规范创建完整子项目结构（见下方目录模板） | full_admin |
| 任务3：执行任务 | 从 Task Board 领取 open 任务，产出报告 | task_executor |

**新项目目录模板**（任务2 产出）：

```
{name}-learning/
├── CONTEXT.md / README.md
├── papers/PAPERS_INDEX.md · books/BOOKS_INDEX.md
├── reports/{paper_analyses,knowledge_reports,concept_reports}/
├── knowledge/INDEX.md
├── roadmap/{Learning_Roadmap,Development_Timeline}.md
└── skills/{paper_analysis,concept_deep_dive}/SKILL.md
```

### 3.2 任务状态机

```
open → claimed → in_progress → done
                             ↘ failed     (须填 failed_reason)
                             ↘ abandoned  (claimed 后 48h 未更新 → 自动释放为 open)
```

### 3.3 任务 Schema

Task Board（`docs/LEARNING_PROJECTS_TASK_BOARD.md`）中每条任务的字段定义：

```yaml
- id: string                   # 唯一标识，例 T001
  project: string              # 目标子项目名
  type: string                 # paper_analysis | knowledge_report | project_optimization | new_project
  target: string               # 执行对象描述
  value: string                # 价值说明
  priority: P1 | P2 | P3
  required_capability: task_executor | full_admin
  status: open | claimed | in_progress | done | failed | abandoned
  claimed_by: string | null
  claimed_at: ISO8601 | null
  started_at: ISO8601 | null
  done_at: ISO8601 | null
  failed_reason: string | null  # status=failed 时必填
```

### 3.4 领取流程

```
1. 读取 Task Board，选 status: open 且 required_capability ≤ 自身 capability 的任务
2. 将 status 改为 claimed，填写 claimed_by、claimed_at → 立即 commit push（防并发）
3. 开始执行前将 status 改为 in_progress，填写 started_at
4. 执行任务：产出符合 docs/REPORT_METADATA.md + docs/SKILL_TEMPLATES.md 的报告
5. 完成后将 status 改为 done，填写 done_at → 更新对应子项目 CONTEXT.md
6. 立即提交推送（§6）
```

**并发约束**：不同子项目可并行；同一子项目禁止多 Agent 同时写入。
**冲突处理**：两个 Agent 同时 claim 同一任务，以先 push 者为准，后者将 status 重置回 open 并另选任务。

---

## §4 Tool Registry（工具注册表）

Agent 可调用的工具及前提条件：

| 工具 | 类型 | 最低 capability |
|------|------|:---:|
| 文件读取（任意路径） | filesystem | read_only |
| 文件写入（reports/、knowledge/、roadmap/） | filesystem | task_executor |
| git commit + push | vcs | task_executor |
| GitHub REST API（降级推送） | http | task_executor |
| Web Search / Web Fetch | network | task_executor |
| 修改 AGENTS.md / CLAUDE.md / scripts/ | filesystem | full_admin |

**禁止写入路径**（任何 capability 均不得写入）：

- `.env`
- `.git/`（git 命令除外）
- `scripts/`（capability < full_admin 时）

---

## §5 Concurrency Rules（并发规则）

- **项目锁**：同一子项目同一时间仅一个 Agent 可写
- **先提交优先**：先完成 push 者有效，后续 Agent 需 rebase
- **锁超时**：`claimed` 状态超过 48h 未更新为 `in_progress` 或 `done`，视为 `abandoned`，释放为 `open`
- **full_admin 操作广播**：执行任务1 时通过 commit message 声明操作范围；其他 Agent 通过 `git log` 获知状态
- **冲突仲裁**：先 push 者为准；无法自动解决时停止操作并通知用户，由用户决定
- **异步通信**：Agent 间通过 commit message 传递状态，格式见 §6

---

## §6 Commit Protocol（提交规范）

### Commit Message 格式

```
[{task-type}] {scope}: {描述}

Agent: {manifest.name}
Task-Type: {project-optimization | new-project | task-execution}
```

- `task-type` 取值：`project-optimization` / `new-project` / `task-execution`
- `scope` 取值：`global` 或具体子项目名（如 `ai-learning`）

### 提交流程

```bash
git add -A
git commit -m "[task-execution] ai-learning: XXX报告

Agent: Claude Sonnet 4.6
Task-Type: task-execution"
GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD  # 冲突无法自动解决则停止并通知用户
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> ⚠️ **锁文件说明**：使用 `GIT_NO_OPTIONAL_LOCKS=1` 减少锁文件产生。若 git 报 lock 错误，用户在终端执行：
> `find .git -name "*.lock" -delete && git pull`

### 降级方案（本地 git 不可用时）

使用 GitHub REST API 直接推送：

```bash
# 1. 获取目标文件的当前 SHA
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/Everloster/EverAgent/contents/{path}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['sha'])"

# 2. PUT 更新文件（每个文件独立一次请求）
curl -s -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/Everloster/EverAgent/contents/{path}" \
  -d "{\"message\":\"{commit msg}\",\"content\":\"$(base64 -w0 {local_file})\",\"sha\":\"{sha}\"}"
```

注意：多文件降级推送会产生多个 commit，非原子操作，仅在本地 git 完全不可用时使用。
Token 从 `.env` 读取：`GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'"' -f2)`

---

## §7 Safety Rules（安全铁律）

1. **防幻觉**：未加载的文件内容禁止推测；CONTEXT.md 未列出的报告须告知用户"尚未研究"
2. **身份诚实**：不得伪装身份或 capability；无法 git 的 Agent 不得声称已提交
3. **唯一入口**：本文件是 AI 唯一全局入口
4. **Token 安全**：`.env` 绝不可提交到 Git；commit message 中不得暴露 token
5. **冲突上报**：多 Agent 意见冲突或无法自动解决时，停止操作，通知用户，由用户仲裁
