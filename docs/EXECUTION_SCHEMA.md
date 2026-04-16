# Execution Schema — 任务执行输入/输出标准化

> 版本：v1.0 | 日期：2026-04-05
> 适用范围：所有学习型子Agent（ai-learning / cs-learning / philosophy-learning / psychology-learning / biology-learning）
> 参考：docs/SKILL_TEMPLATES.md | scripts/execution_validator.py

---

## §1 任务输入 Schema（Task Input）

任务领取时必须校验的标准化结构。任务源为各项目的 `.project-task-state`；Task Board 只是聚合视图。

```yaml
task_input:
  task_id: string          # 非空，匹配 .project-task-state 中的 id（如 T001）
  project: string          # 必须与 agent 项目路径匹配（如 ai-learning）
  type: enum               # paper_analysis | knowledge_report | text_analysis | concept_report
  target: string           # 非空，具体论文/文本/主题（如 VideoMAE (2022)）
  claimed_by: string       # 必须为当前 Agent 名称（如 NeuronAgent）
  claimed_at: ISO8601      # 当前时间（如 2026-04-05T10:30:00+08:00）
  git_commit_sha: string   # 领取时的 commit SHA，用于幂等校验
```

### §1.1 输入校验规则

| 字段 | 规则 |
|------|------|
| `task_id` | 非空，必须存在于 `.project-task-state` |
| `project` | 必须与当前 Agent 项目路径一致 |
| `type` | 必须在枚举值范围内 |
| `target` | 非空，长度 > 0 |
| `claimed_by` | 必须与当前 Agent 名称完全一致 |
| `claimed_at` | 必须是有效 ISO8601 格式 |
| `git_commit_sha` | 必须是 40 字符 SHA1 |

### §1.2 校验时机

```
0. 读取对应项目的 `.project-task-state`，选取 `status: open` 的任务
1. 优先运行 `python3 scripts/task_exec.py begin --task-id=TXXX --project=<project> --agent=<AgentName>`
   → 内部依次执行 input 校验、项目锁获取、状态迁移为 claimed
2. 立即 commit push（防并发冲突）
3. 运行 `python3 scripts/task_exec.py start --task-id=TXXX`
```

---

## §2 任务输出 Schema（Task Output）

任务完成时必须满足的标准化结构。

```yaml
task_output:
  task_id: string
  status: done | failed
  done_at: ISO8601 | null      # status=done 时非空
  failed_reason: string | null  # status=failed 时非空
  files_created: string[]       # 绝对路径列表
  files_modified: string[]      # 绝对路径列表（含更新后的索引文件）
  frontmatter_validated: boolean
  report_quality_checks:
    - check_name: string
      passed: boolean
      message: string
  validated_by: string          # 执行校验的脚本名称（如 execution_validator.py）
```

### §2.1 输出校验规则

| 字段 | 规则 |
|------|------|
| `task_id` | 必须与输入 task_id 一致 |
| `status` | 必须是 done 或 failed |
| `done_at` | status=done 时必须是非空 ISO8601 |
| `failed_reason` | status=failed 时必须是非空字符串 |
| `files_created` | 可空数组，但不能是 null |
| `files_modified` | 至少包含 CONTEXT.md（如果存在） |
| `frontmatter_validated` | 必须为 true（由校验脚本设置） |
| `report_quality_checks` | 至少包含 3 项检查 |

### §2.2 校验时机

```
[任务执行完成后，commit 前]
1. 优先运行 `python3 scripts/task_exec.py finish --task-id=TXXX --project=<project>`
   → 内部依次执行 output 校验、状态迁移为 done
2. commit push
3. 运行 `python3 scripts/task_exec.py release --task-id=TXXX --project=<project> --agent=<AgentName>`
```

---

## §3 失败恢复协议（Failure Recovery）

任务执行失败时的标准化处理。

```yaml
failure_report:
  task_id: string
  failed_reason: string         # 失败原因描述（非空）
  failed_at: ISO8601
  partial_files_created: string[]  # 失败前已创建的文件（可能为空）
  checkpoint: string             # 失败发生的阶段（见下）
```

### §3.1 失败阶段（Checkpoint）

| checkpoint | 含义 |
|------------|------|
| `input_validation` | 输入校验阶段失败 |
| `task_execution` | 任务执行阶段失败 |
| `output_validation` | 输出校验阶段失败 |
| `git_commit` | Git 提交阶段失败 |

### §3.2 失败处理流程

```
1. 填写 failure_report
2. 不删除 partial_files_created（保留中间产物）
3. 运行 `python3 scripts/task_exec.py fail --task-id=TXXX --project=<project> --reason="{failed_reason}"`
4. commit push（message 包含 failed_reason）
5. 运行 `python3 scripts/task_exec.py release --task-id=TXXX --project=<project> --agent=<AgentName>`
6. 不更新 CONTEXT.md（由 EverAgent 后续处理）
```

---

## §4 校验脚本调用规范

### §4.1 命令行接口

```bash
# 输入校验（领取任务前）
python3 scripts/task_exec.py begin --task-id=T001 --project=ai-learning --agent=NeuronAgent
python3 scripts/task_exec.py start --task-id=T001

# 输出校验（完成任务后）
python3 scripts/task_exec.py finish --task-id=T001 --project=ai-learning

# 释放项目锁（push 后）
python3 scripts/task_exec.py release --task-id=T001 --project=ai-learning --agent=NeuronAgent

# 自检模式（验证脚本自身）
python3 scripts/execution_validator.py --mode=self-check

# 帮助
python3 scripts/execution_validator.py --help
```

### §4.2 返回码

| 返回码 | 含义 |
|--------|------|
| 0 | 校验通过 |
| 1 | 校验失败（输出有问题） |
| 2 | 脚本错误（文件不存在、参数错误等） |

---

## §5 与现有验证框架的关系

- **validate_workspace.py**：全局 pre-commit 校验（文件存在性、frontmatter、链接等）
- **validate_reports.py**：TrendAgent 专用报告校验（V-NAME ~ V-LANG 8项检查）
- **execution_validator.py**：任务执行输入/输出标准化校验（本文档定义）
- **project_lock.py**：项目级写锁管理（防并发写入）
- **task_state_cli.py**：任务状态机原子操作（claim/start/done/fail 等）
- **task_exec.py**：任务执行薄封装（begin/start/finish/fail/release）

三者是互补关系：
```
execution_validator.py (任务边界)
    ↓ 调用
validate_workspace.py (文件级校验)
    + validate_reports.py (TrendAgent 专用)
```

---

## §6 Schema 版本管理

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-04-05 | 初始版本 |
