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
- `Agent:` 填运行时已核实或用户明确指定的当前模型；默认配置、环境提示与历史对话不能授权署名。核实失败先诊断并修复可行的自动路径，确实无法取证才由用户指定。
- `Co-Authored-By` 按实际共同参与者显式填写；项目提交器不自动添加或强制指定姓名，已有 trailer 与显式 `--trailer` 沿用 Git 原生语义。
- 严禁 commit message 包含 token / API key / 私人凭据

---

## §C Push Flow（推送流程 · 全局统一）

常规报告和维护默认直接在 `main` 完成并交付。确需临时分支时，任务收尾要把成果合入 `main`；确认已推送、没有独有未合入提交或在用工作树后，清理对应本地和远端分支。用户只需在主分支查阅报告。

> **双身份**：Author 由 [`config/git-policy.json`](../config/git-policy.json) 拥有，Committer 是当前 harness 与模型。
> `scripts/ecommit.sh` 是稳定入口；[`git_commit.py`](../scripts/git_commit.py) 绑定公开仓质量门禁，公共
> [`everagent-core`](../packages/everagent-core/README.md) 拥有 Git 参数、身份注入、消息与 index 不变规则。
> 私仓 eacli 随包携带同源 core，绑定私仓门禁；安装态身份与会话无需相邻 checkout。

**提交前必须有模型依据**：先自动读取运行时的精确会话证据；失败时 Agent 先诊断并修复可行的识别路径，确实无法取证才由用户明确指定。
Codex 当前 thread、Pi 当前 shell context、TRAE thread 与 Claude Code UUID session 读取路径见 [身份契约](./AGENT_SESSION.md#模型证据与声明)。
配置默认值、一般环境提示、全局最近日志、历史对话和 `AGENT_ID` 都不能自动放行。
OpenCode V2原生会话的请求Model.Ref也不是provider返回型号；requested-only记录不能自动授权署名。
诊断入口是 `eacli session diagnose --json`；源码兜底为
`python3 scripts/agent_identity.py diagnose --json`。按诊断核对当前调用方绑定，回公共 core owner 修复
读取器或 adapter、补针对性回归，再复验当前会话。已授权的源码修复与只读工作可继续；仅配置值不能提交。
确实无法取得当前会话证据时，请用户给出当前模型 ID，再运行：

```bash
python3 scripts/agent_model_declare.py --model <用户明确指定的ID> --user-confirmed
```

新源码入口为`eacli session declare`，可只补用户明确指定的device/harness/form/model；`declare-model`继续兼容模型。
声明绑定harness进程创建身份和当前session/terminal；Desktop/Web无native session及未知harness限当前执行shell。
默认4小时、最长12小时，字段独立TTL；重启、嵌套、会话/模型hint变化或到期失效。无关字段更新不续期模型，
更晚的过期/撤销模型证据不能让旧模型复活，撤销时刻相等也不构成新的确认。`user-declared`与自动confirmed分开，声明不授予权限或冒充实测。
身份缺失只阻断提交，已获授权的只读和源码工作可以继续。当前证据与字段定义见
[身份与会话契约](./AGENT_SESSION.md)。

`agent_identity.py` 是 canonical 入口，`whoami_agent.py` 和旧 Python import 路径保持兼容。
Git validator 消费同一公共 core；上一会话的 Git 配置不构成本会话证据。

提交只消费显式暂存的 tree，拒绝 pathspec、`--all/--include/--only/--patch/--fixup` 等改变内容的参数。
质量门禁前后核验 index，并重新读取当前身份。`-m/-F`、复用消息、amend 与原生编辑器保留调用方消息及
显式 trailer，只补必要的末尾换行。内部 amend 作者重置仍绑定仓库 owner，
不接受用户用 `--reset-author` 绕过双身份。

项目提交器保留已有 `core.hooksPath`；外部 hook 正常执行。Git 返回后再次校验 commit tree、Author、Committer；
失败时保留现场并禁止继续推送，不自动回退或改史。CI 复跑同一行为测试。

```bash
git add <本次修改的文件>
scripts/ecommit.sh -m "[architecture-redesign] global: 身份与会话契约收敛"
git fetch origin main
git merge --ff-only FETCH_HEAD
git push origin main
```

安装态可在批准的双仓内使用 `eacli git commit`，它读取 checkout 自带的质量门禁；缺门禁硬失败。
`eacli git identity`默认校验`git var`返回的实际Author/Committer，失败非零；旧`identity show`保持诊断零退出，但有显式validation_exit_code，不得拿它当校验通过。
`eacli git push`绑定捕获的HEAD SHA与唯一实际push目的地，先读回/获取该目的分支并核验祖先关系，再推送捕获SHA，
不因并发HEAD变化改推新提交。命名remote的pushurl与fetch URL可不同；会拒绝目的URL再次匹配insteadOf/pushInsteadOf
或remote别名造成的歧义，不修改用户Git配置。普通推送后再次读回同一目的ref，仅remote_sha==head才返回verified=true；
传输确认丢失但SHA一致仍可核实，读回失败/不一致返回pushed-unverified及非零退出，不能报已核实交付或自动重推。
分叉时先检查集成，禁止force；多pushurl拒绝在写前，不做部分推送。上述为已修源码契约，旧安装态须另行核验。
提交和推送授权仍来自本会话的用户指令；上述例子不授予额外权限。

### 常见错误处理

| 错误 | 修复 |
|------|------|
| `fatal: Unable to create '.git/index.lock': File exists` | 用 `git rev-parse --git-path index.lock` 定位真实锁，检查相关 Git 进程；现有操作结束后重试。锁文件清理按用户授权处理。 |
| `Updates were rejected because the tip of your current branch is behind` | 先 `git fetch origin main` 并检查差异；只做可证明的 fast-forward，分叉时先处理集成方案。 |
| `pre-commit hook denied` | 检查 git identity（运行 `python3 scripts/git_identity.py validate`） |
| 网络超时 / 502 | 只读请求可有界重试；commit/push等写入结果未知先查原提交/目的ref，不自动重放；读回仍失败则明确未核实并上报 |

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
- 同一领域内正文完全不变的报告改名沿用原合同；复制、新建、跨领域移动或从其他目录迁入仍按新报告检查。提交前与 CI 共用该判定，原有版本合同和来源检查继续执行。
- 播客、代码实验等领域若有额外审计或真实运行要求，按领域 `AGENTS.md` 追加执行。
- `lint_evidence.py` 保留为单文件快速诊断，由统一审计器复用。

---

## 引用方清单

| 文件 | 引用章节 |
|------|---------|
| `AGENTS.md` | §A 安全 · §B/§C 提交 |
| `{domain}/AGENTS.md` ×8 | §A 安全 · §B/§C 提交 |

---

*EverAgent 2.0（知识优先架构）。*
