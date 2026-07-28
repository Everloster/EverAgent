# EverAgent — 共享执行协议

> **本文档由根 `AGENTS.md` 与各领域 `AGENTS.md` 共同引用**，提取共享规则避免协议漂移。

---

## §A Safety Rules（安全铁律 · 全局适用）

1. **防幻觉**：未加载的文件内容禁止推测；报告须读取文件确认，禁止凭记忆复述
2. **身份诚实**：不得伪装身份；无法 git push 时不得声称已提交
3. **Token 安全**：`.env` 绝不可提交；commit message 中不得暴露 token
4. **冲突上报**：无法自动解决的冲突，停止操作，通知用户仲裁
5. **领域隔离**：修改某领域时不越界改其他领域或全局配置（除非用户明确要求）

---

## §B Commit Message 格式（全局统一）

```
[{task-type}] {scope}: {描述}

Agent: {模型名}
Task-Type: {project-optimization | new-project | task-execution}
```

- `{task-type}` = `conversational-learning`（对话学习，默认）/ `project-optimization`（项目优化）/ `architecture-redesign`（架构）/ `maintenance`（维护）/ `chore`（杂务）
- `{scope}` = `global` 或具体领域名（`ai-learning` / `cs-learning` / ...）
- `{描述}` ≤ 72 字符，使用中文，简明扼要
- `Agent:` 必须填当前运行模型名。Pre-commit hook 会校验 git 身份。
- 严禁 commit message 包含 token / API key / 私人凭据

---

## §C Push Flow（推送流程 · 全局统一）

> **双身份**：每个 commit 的 **Author = 仓库主人 Everloster**（固定，显示其 GitHub 头像），**Committer = 当前运行的 Agent**（自动识别，谁跑就填谁）。
> `scripts/ecommit.sh` 自动完成两件事：注入 Author=Everloster；调用 `scripts/whoami-agent.sh` 识别当前 agent 身份（进程链判 CLI + 读其配置拿模型，如 `trae-openrouter-3o`/`codex-gpt-5.5`）设为 Committer。**换任何 CLI/模型都无需改配置。**
> pre-commit hook 强制校验：Committer 邮箱须含 `noreply@`；Author 须为 Everloster（绕过 ecommit 且未设 `GIT_AUTHOR_*` 的裸 `git commit` 会被拦截）。

```bash
git add -A
scripts/ecommit.sh -m "[{task-type}] {scope}: {描述}

Agent: {模型名}
Task-Type: {task-type}"
GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

- `2820419+Everloster@users.noreply.github.com` 是 Everloster 账号的 GitHub noreply 邮箱（`{id}+{login}@users.noreply.github.com`），绑定后 GitHub 显示其头像并链接 profile。
- Committer 邮箱必须含 `noreply@`，否则 pre-commit hook（`git_identity.py`）拦截。
- GitHub 提交页会显示为 "Everloster authored and {Agent} committed"，两个头像并排。

### 常见错误处理

| 错误 | 修复 |
|------|------|
| `fatal: Unable to create '.git/index.lock': File exists` | `find .git -name "*.lock" -delete && git pull` |
| `Updates were rejected because the tip of your current branch is behind` | 先 `git fetch && git pull --rebase origin main`，解决冲突后再 push |
| `pre-commit hook denied` | 检查 git identity（运行 `python3 scripts/git_identity.py validate`） |
| 网络超时 / 502 | 重试 3 次，每次间隔 ≥ 30s；3 次失败则上报用户 |

---

## §D 报告自检（非阻塞）

完成报告后建议运行：

```bash
python3 scripts/lint_evidence.py <报告路径>   # 证据密度自检（WARN，不阻塞）
python3 scripts/reindex.py                     # 刷新 README 报告/wiki 计数
```

---

## 引用方清单

| 文件 | 引用章节 |
|------|---------|
| `AGENTS.md` | §A 安全 · §B/§C 提交 |
| `{domain}/AGENTS.md` ×8 | §A 安全 · §B/§C 提交 |

---

*EverAgent 2.0（知识优先架构）。旧多 Agent 协议见 `legacy-v1-multiagent` 分支。*
