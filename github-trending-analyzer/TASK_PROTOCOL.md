---
version: "1.1"
updated: "2026-04-05"
---

# github-trending-analyzer — 任务协议

> AI Agent 唯一执行规范。定义全部任务类型的触发条件、执行步骤、命名规则和验收标准。
> 执行前必须已完成 [AGENTS.md §0](../AGENTS.md) 初始化。

---

## 任务类型总览

| 类型 | 触发场景 | 核心技能 | 输出 |
|------|---------|---------|------|
| [TT-1 trending_report](#tt-1-trending_report) | 生成日/周/月 trending 报告 | github-trending-analyzer + github-deep-research | 汇总报告 + N 份 repo 报告 |
| [TT-2 repo_research](#tt-2-repo_research) | 对单个 repo 深度研究 | github-deep-research | 1 份 repo 报告 |
| [TT-3 index_sync](#tt-3-index_sync) | 批量操作后同步知识索引 | 无（纯文件维护） | 更新 3 处索引文件 |
| [TT-4 validate_all](#tt-4-validate_all) | 验证全部报告质量 + 索引一致性 | scripts/validate_reports.py | 验证报告（stdout） |

---

## TT-1: trending_report

### 触发
用户请求"分析 GitHub 热点项目" / "生成 trending 报告" / 指定日期的 daily/weekly/monthly 报告。

### 参数
| 参数 | 取值 | 说明 |
|------|------|------|
| `period` | `daily` \| `weekly` \| `monthly` | 必填 |
| `date` | `YYYY-MM-DD` | 默认今日 |
| `language` | 编程语言字符串 | 可选，空=全语言 |

### 执行步骤（严格顺序，不可跳过）

**Step 1 — 获取榜单**
```bash
python3 github-trending-analyzer/trending_fetcher.py fetch {period} [{language}]
```
输出 JSON 数组，保存到临时变量 `REPOS`。若返回空数组则停止并告知用户。

**Step 2 — 逐 repo 检查缓存**

对 `REPOS` 中每个 `{owner}/{repo}`：
```bash
python3 github-trending-analyzer/trending_fetcher.py check {owner}/{repo}
```
- `needs_update: false` → 缓存有效（7天内），**跳过深度研究**，记入"缓存复用"列表
- `needs_update: true`  → 需要新研究，进入 Step 3
- `name_mismatch: true` → 警告：文件存在但命名不规范，记录后按缓存处理，不重新生成

**Step 3 — 逐 repo 深度研究**（仅 needs_update=true 的 repo）

调用 `github-deep-research` 技能，**4 轮研究**：
```bash
# Round 1: GitHub API 基础数据
python3 github-deep-research/scripts/github_api.py {owner} {repo} summary
python3 github-deep-research/scripts/github_api.py {owner} {repo} readme
python3 github-deep-research/scripts/github_api.py {owner} {repo} contributors
python3 github-deep-research/scripts/github_api.py {owner} {repo} releases
python3 github-deep-research/scripts/github_api.py {owner} {repo} issues

# Round 2-4: web_search + web_fetch（见 github-deep-research/SKILL.md）
```

研究完成后，将结果转换为 **7 章中文格式**，直接写入：
```
github-trending-reports/research_{owner}_{repo}.md
```

> ⚠️ **禁止**直接存储 github-deep-research 的英文模板结构（Executive Summary / Confidence Assessment 等）。

**Step 4 — 验证每份报告**（汇总前必须完成）

对每个新生成的报告运行验证器：
```bash
python3 scripts/validate_reports.py {owner}/{repo}
```

验证器执行以下 8 项检查，全部通过（exit 0）才算合格：

| 检查 ID | 规则 |
|---------|------|
| V-NAME   | 文件名 `research_{owner}_{repo}.md`，禁止日期后缀 |
| V-STRUCT | 7 个中文章节均存在（项目概述/基本信息/技术分析/社区活跃度/发展趋势/竞品对比/总结评价） |
| V-LEN    | 总行数 ≥ 150 |
| V-PREC   | 无模糊数值（禁止"17,000+"等大数字后跟"+"的写法） |
| V-COMP   | 竞品对比表格数据行 ≥ 2 |
| V-FOOTER | 页脚含 `*报告生成时间: YYYY-MM-DD*` 和 `*研究方法: github-deep-research 多轮深度研究*` |
| V-PATH   | 无宿主机路径（/tmp/、/sessions/、/mnt/、/Users/、/home/） |
| V-LANG   | 无英文模板标记（Executive Summary、Confidence Assessment 等） |

未通过验证 → 修复后重新验证，不得跳过。记入 `MISSING_REPOS` 列表（将在汇总中标记 ⚠️）。

**Step 5 — 生成汇总报告**
```bash
python3 github-trending-analyzer/report_generator.py summary \
  {period} \
  '{REPOS_JSON}' \
  github-trending-reports/all-{period}-summary-{date}.md \
  '{MISSING_REPOS_JSON}' \
  'github-deep-research 多轮深度研究'
```

汇总报告须包含：
```
✅ 概览表（分析项目数/总Stars/周期增长）
✅ 语言分布
✅ 项目列表（含今日增长精确值）
✅ 趋势分析（🔥热门趋势 / 🏢大厂动态 / 🔬技术创新 / 📊语言趋势，4 个子章节均不可缺）
✅ 详细报告链接（相对路径 ./research_{owner}_{repo}.md）
✅ 报告状态说明（如实区分新生成和缓存复用，禁止虚报"全部新生成"）
```

**Step 6 — 同步索引**（完成 TT-3）

### 输出命名
| 产物 | 路径 | 规则 |
|------|------|------|
| 汇总报告 | `github-trending-reports/all-{period}-summary-{date}.md` | period 小写；date = YYYY-MM-DD |
| 单项目报告 | `github-trending-reports/research_{owner}_{repo}.md` | **owner/repo 保留 GitHub 原始大小写**，连字符保留，无日期后缀 |

**命名示例：**
```
✅ research_hsliuping_TradingAgents-CN.md
✅ research_666ghj_BettaFish.md
❌ research_hsliuping_tradingagents_cn.md   ← 大小写/连字符丢失
❌ research_browser-use_browser-use_20260405.md  ← 多余日期后缀
```

### 临时文件
使用 `/tmp/github-trending-{date}/` 存放中间数据，**任务完成后清理**：
```python
import shutil; shutil.rmtree(f"/tmp/github-trending-{date}", ignore_errors=True)
```

---

## TT-2: repo_research

### 触发
用户指定某个具体 GitHub repo 进行深度研究（独立请求，不依附于 trending 榜单）。

### 执行步骤

**Step 1 — 检查缓存**
```bash
python3 github-trending-analyzer/trending_fetcher.py check {owner}/{repo}
```
- `needs_update: false` → 告知用户缓存有效，询问是否强制重新研究
- `needs_update: true`  → 继续 Step 2

**Step 2 — 深度研究**

调用 `github-deep-research` 技能，4 轮研究（同 TT-1 Step 3）。

**Step 3 — 写入报告**

路径：`github-trending-reports/research_{owner}_{repo}.md`

写入后立即运行验证器，exit 非 0 则修复：
```bash
python3 scripts/validate_reports.py {owner}/{repo}
```

验证标准同 TT-1 Step 4（8 项检查）。

**Step 4 — 同步索引**（完成 TT-3）

---

## TT-3: index_sync

### 触发
- TT-1 或 TT-2 完成后自动执行
- 手动维护/发现索引与文件不一致时执行

### 执行步骤

**Step 1 — 统计实际文件数**

统计 `github-trending-reports/research_*.md` 文件总数（记为 `ACTUAL_COUNT`）。

**Step 2 — 比对 reports_index.md**

读取 `knowledge/reports_index.md`，找出实际有文件但索引中缺少的 repo。

**Step 3 — 追加缺失条目**

将缺失 repo 按**字母序**追加到 `knowledge/reports_index.md` 的 `## Repository Deep Reports` 列表中。
格式：`- {owner}/{repo}`（保留 GitHub 原始大小写）。

**Step 4 — 更新 INDEX.md**

更新 `knowledge/INDEX.md` 中的统计数字：
```
全部 {ACTUAL_COUNT} 篇 Repo 报告 + {SUMMARY_COUNT} 篇汇总报告索引
```

**Step 5 — 更新 CONTEXT.md**

更新 `CONTEXT.md` 中"知识库现状"的数字：
```
**Repo 深度报告**：{ACTUAL_COUNT} 篇
**汇总报告**：daily ×N、weekly ×N、monthly ×N（共 {SUMMARY_COUNT} 篇）
```

**禁止删除** `reports_index.md` 中已有的条目。

---

---

## TT-4: validate_all

### 触发
- 手动检查全部报告质量
- 发现疑似不合规报告时
- 批量修复后的回归验证

### 执行步骤

**Step 1 — 验证全部报告**
```bash
python3 scripts/validate_reports.py --fail-only --index
```

**Step 2 — 查看 JSON 详情**（可选，用于批量修复）
```bash
python3 scripts/validate_reports.py --json --index > /tmp/validation_results.json
```

**Step 3 — 针对失败报告修复并复验**
```bash
# 修复单个报告后
python3 scripts/validate_reports.py {owner}/{repo}
```

### 退出码
| 退出码 | 含义 |
|--------|------|
| 0 | 所有检查通过 |
| 1 | 存在失败检查（详见输出） |
| 2 | 使用错误（文件不存在等） |

---

## 通用约束

### 写入限制
| 路径 | 权限 |
|------|------|
| `github-trending-reports/` | ✅ 可写（仅 `research_*.md` 和 `all-*.md`） |
| `knowledge/reports_index.md` | ✅ 仅追加 |
| `knowledge/INDEX.md` | ✅ 仅更新数字 |
| `CONTEXT.md` | ✅ 仅更新数字 |
| `github-trending-analyzer/` | ❌ 只读 |
| `github-deep-research/` | ❌ 只读 |
| `scripts/validate_reports.py` | ❌ 只读 |
| `SKILL.md` / `TASK_PROTOCOL.md` | ❌ 只读 |

### 数据精度
- Stars、Forks 等数值必须使用 GitHub API 精确返回值
- 禁止使用"17,000+"、"约 1 万"等模糊表达

### Mermaid 图表
仅允许：`flowchart` / `sequenceDiagram` / `gantt` / `pie`
禁止：`mindmap`、`timeline` 及其他未经验证的类型

### 路径安全
报告内容禁止出现宿主机路径（`/tmp/`、`/sessions/`、`/mnt/` 等绝对路径）

---

## 常见失误速查

| # | 错误行为 | 正确做法 |
|---|---------|---------|
| 1 | 汇总报告写"✅ 所有 N 份完整生成"，实际有缓存复用 | 报告状态说明如实区分新生成和缓存复用 |
| 2 | 直接存储 github-deep-research 英文模板（Executive Summary 等章节） | 必须转换为 7 章中文结构后存档 |
| 3 | 页脚出现"Github Deep Research by DeerFlow"等品牌 | 统一使用 `*报告生成时间:...` / `*研究方法:...` |
| 4 | Stars 写"17,000+"等模糊值 | 使用 API 精确整数 |
| 5 | 趋势分析只写 2-3 行 | 必须包含 🔥/🏢/🔬/📊 四个子章节 |
| 6 | 报告命名用小写或下划线替换连字符 | 保留 GitHub 原始大小写和连字符 |
| 7 | 完成 TT-1/TT-2 后未执行 TT-3 | 每次产出新报告后必须同步索引 |
