# EverAgent — 共享执行协议

> **本文档由根 `AGENTS.md` 与 8 个子项目 `AGENTS.md` 共同引用**。
> 提取共享规则，避免 9 份 AGENTS.md 各自维护导致协议漂移。
> 修改本文件前请同步通知所有引用方（直接 grep `PROTOCOL_COMMON.md` 即可）。

---

## §A Safety Rules（安全铁律 · 全局适用）

适用于所有 Agent：EverAgent + 8 Subagents + 临时手动执行。

1. **防幻觉**：未加载的文件内容禁止推测；子项目报告须读取文件确认，禁止凭记忆复述
2. **身份诚实**：不得伪装身份；无法 git push 时不得声称已提交
3. **Token 安全**：`.env` 绝不可提交；commit message 中不得暴露 token
4. **冲突上报**：多 Agent 意见冲突或无法自动解决时，停止操作，通知用户仲裁
5. **子项目隔离**：Subagent 不得修改其他子项目文件，不得修改全局配置文件

---

## §B Commit Message 格式（全局统一）

```
[{task-type}] {scope}: {描述}

Agent: {模型名}
Task-Type: {project-optimization | new-project | task-execution}
```

- `{task-type}` = `task-execution`（默认）/ `project-optimization`（项目优化）/ `new-project`（新建项目）/ `maintenance`（维护）/ `chore`（杂务）
- `{scope}` = `global` 或具体子项目名（`ai-learning` / `cs-learning` / ...）
- `{描述}` ≤ 72 字符，使用中文，简明扼要
- `Agent:` 必须填当前运行模型名（不是 agent role 名）。Pre-commit hook 会校验。
- `Task-Type:` 行必须出现在 body 中（hook 校验）
- 严禁 commit message 包含 token / API key / 私人凭据

详细示例参见根 `AGENTS.md` §7 与各子项目 `AGENTS.md` §5。

---

## §C Push Flow（推送流程 · 全局统一）

```bash
git add -A
git commit -m "[{task-type}] {scope}: {描述}

Agent: {模型名}
Task-Type: {task-type}"
GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

### 常见错误处理

| 错误 | 修复 |
|------|------|
| `fatal: Unable to create '.git/index.lock': File exists` | `find .git -name "*.lock" -delete && git pull` |
| `Updates were rejected because the tip of your current branch is behind` | 先 `git fetch && git pull --rebase origin main`，解决冲突后再 push |
| `pre-commit hook denied` | 检查 git identity（运行 `python3 scripts/git_identity.py validate`） |
| 网络超时 / 502 | 重试 3 次，每次间隔 ≥ 30s；3 次失败则上报用户 |

---

## §D 任务状态机与文件分工

详见根 `AGENTS.md` §3。本节仅重申关键点：

- **Spec**（任务定义）= `tasks/T*.yaml`，**禁止**包含 status 字段
- **State**（运行时状态）= `{project}/.project-task-state`，**唯一来源**
- 历史 state-only 任务归档到 `{project}/state-history/state-only-done-{year}.yaml`
- 校验：`python3 scripts/check_task_state_consistency.py`

---

## §E 质量门自动校验（强制）

完成任务的 finish 路径强制三道关：

1. `execution_validator.py --mode=output` — 任务字段格式校验
2. `check_quality_gates.py --task-id=TXXX` — 报告内容质量校验
3. `task_state_cli.py done` — 标记完成

任何 required check FAIL → finish 拒绝。覆盖：仅 `task_exec.py finish --skip-quality-gate`（CI / 紧急场景）。

校验脚本：

```bash
python3 scripts/check_task_state_consistency.py   # 任务文件一致性
python3 scripts/check_quality_gates.py            # 24 check 类型
python3 scripts/backfill_context_links.py         # 回填 context_links
python3 scripts/archive_state_only_tasks.py       # 归档历史 state
```

---

## 引用方清单（修改本文件时同步更新）

| 文件 | 引用章节 | 替换内容 |
|------|---------|---------|
| `AGENTS.md` | §5, §7, §8 | 根级说明保留，本文件作 source of truth |
| `ai-learning/AGENTS.md` | §5, §6 | 提交规范与防幻觉指向本文档 |
| `cs-learning/AGENTS.md` | §5, §6 | 同上 |
| `philosophy-learning/AGENTS.md` | §5, §6 | 同上 |
| `psychology-learning/AGENTS.md` | §5, §6 | 同上 |
| `biology-learning/AGENTS.md` | §5, §6 | 同上 |
| `podcast-learning/AGENTS.md` | §5 | 同上 |
| `ai-practice/AGENTS.md` | §4 | 同上 |
| `github-trending-analyzer/AGENTS.md` | §5, §6 | 同上 |

---

*协议抽取时间：2026-06-21*
*触发原因：根 AGENTS.md (289 行) + 8 子项目 AGENTS.md (~1600 行) 章节重叠 ~80%*