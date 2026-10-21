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
- `Agent:` 填运行时已核实或用户明确指定的当前模型；默认配置、环境提示与历史对话不能授权署名。无法核实时先请用户明确指定。
- 严禁 commit message 包含 token / API key / 私人凭据

---

## §C Push Flow（推送流程 · 全局统一）

> **双身份**：Author 由 [`config/git-policy.json`](../config/git-policy.json) 拥有，Committer 是当前 harness 与模型。
> `scripts/ecommit.sh` 是稳定入口；[`git_commit.py`](../scripts/git_commit.py) 绑定公开仓质量门禁，公共
> [`everagent-core`](../packages/everagent-core/README.md) 拥有 Git 参数、身份注入、消息与 index 不变规则。
> 私仓 eacli 随包携带同源 core，绑定私仓门禁；安装态身份与会话无需相邻 checkout。

**提交前必须有模型依据**：先自动读取运行时的精确会话证据；只有读取不到时才由用户明确指定。
Codex 当前 thread、Pi 当前 shell context 与 TRAE thread 读取路径见 [身份契约](./AGENT_SESSION.md#模型证据与声明)。
配置默认值、一般环境提示、全局最近日志、历史对话和 `AGENT_ID` 都不能自动放行。
自动核实仍失败时，请用户给出当前模型 ID，再运行：

```bash
python3 scripts/agent_model_declare.py --model <用户明确指定的ID> --user-confirmed
```

声明绑定 harness 进程创建身份和当前 session/terminal，默认 4 小时，最长 12 小时；重启、嵌套 harness、
切换会话、模型提示变化或过期后失效。`user-declared` 与 `current_model_confirmed=true` 分开，声明不冒充实测。
身份缺失只阻断提交，已获授权的只读和源码工作可以继续。当前证据与字段定义见
[身份与会话契约](./AGENT_SESSION.md)。

`agent_identity.py` 是 canonical 入口，`whoami_agent.py` 和旧 Python import 路径保持兼容。
Git validator 消费同一公共 core；上一会话的 Git 配置不构成本会话证据。

提交只消费显式暂存的 tree，拒绝 pathspec、`--all/--include/--only/--patch/--fixup` 等改变内容的参数。
质量门禁前后核验 index，并重新读取当前身份。`-m/-F`、复用消息、amend 与原生编辑器的最终消息都规范化，
保留其他 trailer，`Co-Authored-By: Aiden` 在最终 trailer block 恰好一次。内部 amend 作者重置仍绑定仓库 owner，
不接受用户用 `--reset-author` 绕过双身份。

项目提交器保留已有 `core.hooksPath`；外部 hook 正常执行。Git 返回后再次校验 commit tree、Author、Committer
与 trailer；失败时保留现场并禁止继续推送，不自动回退或改史。CI 复跑同一行为测试。

```bash
git add <本次修改的文件>
scripts/ecommit.sh -m "[architecture-redesign] global: 身份与会话契约收敛"
git fetch origin main
git merge --ff-only FETCH_HEAD
git push origin main
```

安装态可在批准的双仓内使用 `eacli git commit`，它读取 checkout 自带的质量门禁；缺门禁硬失败。
`eacli git push` 会 fetch、核验远端祖先关系并普通推送，分叉时要求先检查集成方案，禁止 force。
提交和推送授权仍来自本会话的用户指令；上述例子不授予额外权限。

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
