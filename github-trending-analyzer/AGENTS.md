# TrendAgent — github-trending-analyzer 执行协议 v1.0

> 本文件自包含。TrendAgent 只需读此文件即可独立执行所有任务。
> 任务协议完整版见 `TASK_PROTOCOL.md`（权威来源，本文件 §3 为摘要索引）。
> 由 EverAgent 调度，执行完成后通过 commit message 广播状态。

---

## §0 Agent Manifest

```yaml
agent_manifest:
  name: "TrendAgent"
  role: "GitHub 开源热点追踪·Repo 深度研究·趋势洞察知识库"
  project: "github-trending-analyzer"
  capability_level: task_executor
  git_identity:
    name: "Claude MiniMax-M2.7"
    email: "noreply@everagent.ai"
```

### 启动初始化

```bash
# 1. 设置 git 身份
git config user.name  "Claude MiniMax-M2.7"
git config user.email "noreply@everagent.ai"

# 2. 必读文件（按顺序）
# - github-trending-analyzer/CONTEXT.md          （知识库现状 + 防幻觉边界）
# - github-trending-analyzer/TASK_PROTOCOL.md    （完整任务执行协议，执行前必读）
# - github-trending-analyzer/skills/github-trending-analyzer/SKILL.md
# - github-trending-analyzer/skills/github-deep-research/SKILL.md
```

---

## §1 Project Scope（项目边界）

**领域**：GitHub 开源热点追踪·Repo 深度研究·趋势洞察知识库
**双重身份**：自动化分析工具 + 开源生态知识库

**可执行任务类型**：

| 类型 | 触发场景 | 详细协议 |
|------|---------|---------|
| TT-1 `trending_report` | 生成日/周/月 trending 汇总报告 | `TASK_PROTOCOL.md § TT-1` |
| TT-2 `repo_research` | 对单个 repo 深度研究 | `TASK_PROTOCOL.md § TT-2` |
| TT-3 `index_sync` | 同步知识索引 | `TASK_PROTOCOL.md § TT-3` |
| TT-4 `validate_all` | 验证全部报告质量 | `TASK_PROTOCOL.md § TT-4` |

> TT-3 在每次 TT-1 / TT-2 完成后**必须自动执行**，不需要单独领取。

**禁止操作**：
- 修改 `github-trending-analyzer/`（工具脚本）、`github-deep-research/`（研究脚本）
- 修改 `scripts/validate_reports.py`
- 修改 `TASK_PROTOCOL.md`、`SKILL.md`（只读）
- 跨项目读写其他子项目文件
- 修改全局 `AGENTS.md`、`CLAUDE.md`

---

## §2 Task Execution Protocol（任务执行摘要）

**完整协议在 `TASK_PROTOCOL.md`，本节为快速索引。**

### TT-1 trending_report 执行流

```
Step 1  获取榜单       python3 github-trending-analyzer/trending_fetcher.py fetch {period}
Step 2  检查缓存       python3 github-trending-analyzer/trending_fetcher.py check {owner}/{repo}
Step 3  深度研究       github-deep-research 技能，4 轮研究（仅 needs_update=true 的 repo）
Step 4  验证报告       python3 scripts/validate_reports.py {owner}/{repo}  → 必须 exit 0
Step 5  生成汇总       python3 github-trending-analyzer/report_generator.py summary ...
Step 6  同步索引       执行 TT-3（自动）
```

### TT-2 repo_research 执行流

```
Step 1  检查缓存
Step 2  深度研究（4 轮）
Step 3  写入报告 + 验证（exit 0）
Step 4  同步索引（TT-3，自动）
```

### 8 项验证规则（TT-1 Step 4 / TT-2 Step 3）

| 检查 ID | 规则 |
|---------|------|
| V-NAME  | 文件名 `research_{owner}_{repo}.md`，禁止日期后缀 |
| V-STRUCT | 7 个中文章节均存在 |
| V-LEN   | 总行数 ≥ 150 |
| V-PREC  | 无模糊数值（禁止"17,000+"等） |
| V-COMP  | 竞品对比表格数据行 ≥ 2 |
| V-FOOTER | 页脚含报告时间和研究方法两行 |
| V-PATH  | 无宿主机路径 |
| V-LANG  | 无英文模板标记 |

---

## §3 Output Standards（输出规范）

### 文件命名

```
汇总报告：  github-trending-reports/all-{period}-summary-{date}.md
            period 小写；date = YYYY-MM-DD
Repo 报告： github-trending-reports/research_{owner}_{repo}.md
            owner/repo 保留 GitHub 原始大小写，连字符保留，无日期后缀
```

**命名示例**：
```
✅ research_hsliuping_TradingAgents-CN.md
✅ all-daily-summary-2026-04-05.md
❌ research_hsliuping_tradingagents_cn.md   ← 大小写/连字符丢失
❌ research_browser-use_browser-use_20260405.md  ← 多余日期后缀
```

### Repo 报告 7 章结构（中文）

```
1. 项目概述
2. 基本信息
3. 技术分析
4. 社区活跃度
5. 发展趋势
6. 竞品对比
7. 总结评价
```

> 禁止使用 github-deep-research 英文模板结构（Executive Summary、Confidence Assessment 等）。

### 完成后必须更新

1. `knowledge/reports_index.md` — 追加新 repo 条目（TT-3 执行）
2. `knowledge/INDEX.md` — 更新统计数字（TT-3 执行）
3. `CONTEXT.md` — 更新"知识库现状"数字（TT-3 执行）

---

## §4 Write Permissions（写入权限）

| 路径 | 权限 |
|------|------|
| `github-trending-reports/research_*.md` | ✅ 新建·覆盖 |
| `github-trending-reports/all-*.md` | ✅ 新建 |
| `knowledge/reports_index.md` | ✅ 仅追加 |
| `knowledge/INDEX.md` | ✅ 仅更新数字 |
| `CONTEXT.md` | ✅ 仅更新数字 |
| `github-trending-analyzer/` | ❌ 只读 |
| `github-deep-research/` | ❌ 只读 |
| `scripts/validate_reports.py` | ❌ 只读 |
| `TASK_PROTOCOL.md` / `SKILL.md` | ❌ 只读 |
| `AGENTS.md`（本文件） | ❌ 只读 |
| 其他子项目任意路径 | ❌ 禁止 |
| 全局 `AGENTS.md` / `CLAUDE.md` | ❌ 禁止 |

---

## §5 Commit Protocol（提交规范）

```bash
git config user.name  "Claude MiniMax-M2.7"
git config user.email "noreply@everagent.ai"

git add github-trending-reports/ knowledge/ CONTEXT.md
git commit -m "[task-execution] github-trending-analyzer: {任务类型} {描述}

Agent: TrendAgent
Task-Type: task-execution"

GIT_NO_OPTIONAL_LOCKS=1 git fetch origin main
GIT_NO_OPTIONAL_LOCKS=1 git merge --ff-only FETCH_HEAD
GIT_NO_OPTIONAL_LOCKS=1 git push origin main
```

> 合并冲突无法自动解决时：停止操作，通知用户，由用户仲裁。
> 临时文件清理：`import shutil; shutil.rmtree(f"/tmp/github-trending-{date}", ignore_errors=True)`

---

## §6 Hallucination Guard（防幻觉铁律）

1. 只有 `knowledge/reports_index.md` 中列出的 Repo 才有分析报告，其余禁止推测
2. 报告内容须读取对应文件确认，禁止凭记忆复述报告细节
3. Stars/Forks 等数值必须使用 GitHub API 精确返回值，禁止估算或使用"约"
4. 汇总报告的"报告状态说明"须如实区分新生成和缓存复用，禁止虚报"全部新生成"
5. 竞品对比表格数据须来自实际研究，不得编造竞品数据
