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
Co-Authored-By: Aiden
```

- `{task-type}` = `conversational-learning`（对话学习，默认）/ `project-optimization`（项目优化）/ `architecture-redesign`（架构）/ `maintenance`（维护）/ `chore`（杂务）
- `{scope}` = `global` 或具体领域名（`ai-learning` / `cs-learning` / ...）
- `{描述}` ≤ 72 字符，使用中文，简明扼要
- `Agent:` 填已经确认的当前模型；仅有默认配置时注明 `model-unverified` 与来源。Pre-commit hook 校验 Git 身份。
- 严禁 commit message 包含 token / API key / 私人凭据

---

## §C Push Flow（推送流程 · 全局统一）

> **双身份**：每个 commit 的 **Author = 仓库主人 Everloster**（固定，显示其 GitHub 头像），**Committer = 当前运行的 Agent**（自动识别，谁跑就填谁）。
> `scripts/ecommit.sh` 是解释器启动入口；公共 `scripts/git_commit.py` 拥有参数校验、双身份注入、trailer 和 index 不变检查。公开仓绑定 `precommit_quality.py`；私仓只桥接公共规则并绑定自己的质量门禁与站点导出校验。换 CLI/模型无需复制规则或修改 Git 配置。
> `scripts/ecommit.sh` 是项目质量门的强制入口：它验证精确 staged snapshot，并拒绝会在门禁后改变提交树的 commit 参数。版本化 pre-commit hook 是额外防线；若设备已有外部 `core.hooksPath`，不要覆盖它，外部 hook 会在 `git commit` 阶段继续执行。
> `.github/workflows/quality.yml` 在 push 与 PR 上复跑仓库级检查，避免本机 hook 配置差异成为唯一防线。
> **身份识别失败 = 禁止提交（2026-07-28 铁律）**：whoami 返回 `*-unknown` 时 ecommit 直接退出、hook 同样拦截，绝不允许静默兜底提交。处理：① 优先修 `scripts/whoami_agent.py` 覆盖当前 CLI（加检测规则 + 厂商 noreply 邮箱）；② 应急与用户确认身份后显式指定：`AGENT_ID=<cli>-<model> AGENT_EMAIL=<厂商noreply> scripts/ecommit.sh -m "..."`。

`whoami_agent.py --json` 给出 CLI、模型与各自来源；会话环境模型优先于配置默认值。
`model_confidence=configured` 只表示默认配置，`current_model_confirmed=false` 时不得把它当成当前模型证明。
提交包装单次调用同一结构化身份 API 获取 name/email；`--git-ident` 保留为兼容输出。
`whoami_agent.py` 是稳定入口，内部 `scripts/agent_identity/` 分别拥有祖先链、模型证据和身份裁定。
`source_sha256` 覆盖整组实现；既有配置提示仍可用于 Git 署名，未知身份继续拦截。
进程检测只认调用方祖先链；Windows 断链不会借其他终端的进程补身份。
Git validator 也消费同一 JSON owner；当前身份未知时，上一会话留下的 Git 配置不能放行提交。

显式 `-m` / `-F` 消息由公共提交器规范化最终 trailer block，保留已有 trailer 并去重
`Co-Authored-By: Aiden`。Git 原生编辑器与 reuse-message 模式继续使用其 trailer 机制；
提交完成后检查最终消息。`--author` 必须符合已确认的仓库主人；`--reset-author` 会破坏双身份，入口拒绝。

```bash
git add -A
scripts/ecommit.sh -m "[{task-type}] {scope}: {描述}

Agent: {模型名}
Task-Type: {task-type}
Co-Authored-By: Aiden"
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
| `fatal: Unable to create '.git/index.lock': File exists` | 用 `git rev-parse --git-path index.lock` 定位真实锁，检查相关 Git 进程；现有操作结束后重试。锁文件清理按用户授权处理。 |
| `Updates were rejected because the tip of your current branch is behind` | 先 `git fetch origin main` 并检查差异；只做可证明的 fast-forward，分叉时先处理集成方案。 |
| `pre-commit hook denied` | 检查 git identity（运行 `python3 scripts/git_identity.py validate`） |
| 网络超时 / 502 | 重试 3 次，每次间隔 ≥ 30s；3 次失败则上报用户 |

---

## §D 报告质量门

新增或实质修改报告后，从仓库根目录运行：

```bash
python3 scripts/reindex.py
python3 scripts/report_quality.py check <报告路径>  # report-v2
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

- 新报告使用 `quality_schema: report-v2`，并通过证据账本、独立复核和评分门；`report-v1` 保留为过渡格式。
- `scripts/ecommit.sh` 会对已暂存报告、索引和 context 自动运行确定性门禁，并校验门禁前后的 index tree 未变化。
- 历史报告只进入 WARN 清单，不因一次任务批量重写。
- 播客、代码实验等领域若有额外审计或真实运行要求，按领域 `AGENTS.md` 追加执行。
- `lint_evidence.py` 保留为单文件快速诊断，由统一审计器复用。

---

## 引用方清单

| 文件 | 引用章节 |
|------|---------|
| `AGENTS.md` | §A 安全 · §B/§C 提交 |
| `{domain}/AGENTS.md` ×8 | §A 安全 · §B/§C 提交 |

---

*EverAgent 2.0（知识优先架构）。旧多 Agent 协议见 `legacy-v1-multiagent` 分支。*
