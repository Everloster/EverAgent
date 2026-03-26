# EverAgent — AI Agent 协作协议 v2.0

> 唯一全局入口。README.md 供人类阅读，AI 忽略。

---

## §0 初始化约束（每次新对话必须执行）

### 身份自检 → 权限分级

```
Q1: 在线大模型 or 离线模型？
  └─ 离线 → 【只读模式】(§0.2)
Q2: 能否执行 git commit/push？
  └─ 不能 → 【只读模式】(§0.2)
Q3: Claude 系列？
  ├─ 是 → 【全权限】任务 1/2/3 均可
  └─ 否 → 【执行模式】仅任务 3
```

### Git 初始化（全权限/执行模式 必须执行）

```bash
# 1. 读 token
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d'"' -f2)
# 2. 配远程
git remote set-url origin https://${GITHUB_TOKEN}@github.com/Everloster/EverAgent.git
# 3. 验权限（失败则降级只读）
git ls-remote origin HEAD
# 4. 设提交者
git config user.name "Claude Opus 4.6"   # 按实际模型替换
git config user.email "noreply@anthropic.com"
```

### §0.2 只读模式

✅ 读取任意文件 / 提供分析问答　　❌ 创建·修改·删除文件　　❌ git 操作　　❌ 任务 1/2

---

## §1 权限矩阵

| 能力 | Claude 系（全权限） | 其他在线模型（执行） | 离线模型（只读） |
|------|:---:|:---:|:---:|
| 读取任意文件 | ✅ | ✅ | ✅ |
| 跨项目并发操作 | ✅ | ❌ | ❌ |
| 任务1 项目优化 | ✅ | ❌ | ❌ |
| 任务2 创建新项目 | ✅ | ❌ | ❌ |
| 任务3 执行任务 | ✅ | ✅ | ❌ |
| git commit & push | ✅ | ✅ | ❌ |
| 修改全局配置 | ✅ | ❌ | ❌ |

> **Claude 系 Agent = 项目主负责人**，拥有最终决策权。

---

## §2 项目索引

| 项目 | CONTEXT 入口 | 领域 | 状态 |
|------|-------------|------|:---:|
| ai-learning | `./ai-learning/CONTEXT.md` | AI/ML 论文精读·技术报告 | 🟢 |
| cs-learning | `./cs-learning/CONTEXT.md` | 计算机科学·系统·算法 | 🟡 |
| philosophy-learning | `./philosophy-learning/CONTEXT.md` | 西方哲学史·文本分析 | 🟡 |
| psychology-learning | `./psychology-learning/CONTEXT.md` | 心理学·经典实验 | 🟡 |
| biology-learning | `./biology-learning/CONTEXT.md` | 时间生物学·睡眠·运动生理 | 🔵 |
| github-trending-analyzer | `./github-trending-analyzer/CONTEXT.md` | 开源热点·Repo 知识库 | 🟢 |

---

## §3 四类任务

### 任务1【项目优化】— 仅 Claude

对整个项目/子项目进行重构、规划、TODO 分配。可跨项目加载 CONTEXT.md。
产出：结构调整 + 元文件更新 + 各子项目 TODO 排期。
并发：允许同时分析多子项目，写操作串行。

### 任务2【创建新项目】— 仅 Claude

用户提出主题 → 按现有规范创建完整子项目结构：

```
{name}-learning/
├── CONTEXT.md / README.md
├── papers/PAPERS_INDEX.md · books/BOOKS_INDEX.md
├── reports/{paper_analyses,knowledge_reports,concept_reports}/
├── knowledge/INDEX.md
├── roadmap/{Learning_Roadmap,Development_Timeline}.md
└── skills/{paper_analysis,concept_deep_dive}/SKILL.md
```

创建后更新本文件 §2 索引表 → 提交推送。

### 任务3【执行任务】— Claude + 其他在线模型

选取 2-3 个子项目的待办任务并发推进（学习/研究/分析）。
规范：产出符合 `docs/REPORT_METADATA.md` frontmatter + `docs/SKILL_TEMPLATES.md` 方法论。
完成后更新对应 CONTEXT.md → 立即提交推送（§4）。

**并发约束**：不同子项目可并行，同一子项目禁止多 Agent 同时写入。

### 任务4【初始化约束】— 自动执行

非独立任务，为上述三类的前置条件层（即 §0），每个 Agent 进入时自动触发。

---

## §4 提交规范

### Commit Message 格式

```
[{task-type}] {scope}: {描述}

Agent: {模型全称}
Task-Type: {project-optimization | new-project | task-execution}
```

task-type 取值：`project-optimization` / `new-project` / `task-execution`
scope 取值：`global` 或具体子项目名（如 `ai-learning`）

### 提交流程

```bash
git add -A
git commit -m "[task-execution] ai-learning: XXX报告

Agent: Claude Opus 4.6
Task-Type: task-execution"
git pull --rebase origin main   # 冲突无法自动解决则暂停通知用户
git push origin main
```

---

## §5 并发规则

- **项目锁**：同一子项目同一时间仅一个 Agent 可写
- **先提交优先**：先完成的先 push，后续 Agent 需 rebase
- **全局优先**：Claude 执行任务1 时，其他 Agent 暂停写操作
- **异步通信**：Agent 间通过 commit message 声明操作范围，后续 Agent 通过 `git log` 获取状态
- **冲突仲裁**：以 Claude Agent 决策为准

---

## §6 铁律

1. **防幻觉**：未加载的文件内容禁止推测；CONTEXT.md 未列出的报告须告知用户"尚未研究"
2. **身份诚实**：不得伪装身份或权限；无法 git 的 Agent 不得声称已提交
3. **唯一入口**：本文件是 AI 唯一全局入口
4. **Token 安全**：`.env` 绝不可提交到 Git，commit 中不得暴露 token
5. **Claude 终裁**：多 Agent 意见冲突时以 Claude 判断为准
