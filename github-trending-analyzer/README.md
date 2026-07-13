# github-trending-analyzer

> GitHub 开源热点追踪 · Repo 深度研究 · 趋势洞察知识库。
> **双重身份**：自动化分析工具 + 离线知识库。执行协议见 [`AGENTS.md`](./AGENTS.md)。

## 只做三件事

| # | 事 | 触发 | 产出 |
|---|----|------|------|
| ① | 单 repo 深度研究 | 对话贴 repo 链接 | `reports/research_{owner}_{repo}.md` |
| ② | trending 汇总 | "出日/周/月 trending 报告" | `reports/all-{period}-summary-{date}.md` + 榜上各 repo 报告 |
| ③ | 深度研究方法论 | 研究单个 repo 时遵循，持续迭代 | 4 轮研究规范（`skills/deep-research/`） |

与三件事无关的需求不在本项目处理。

## Quick Start

```bash
# 1. 依赖（Python 3.9+；gh CLI 已 gh auth login）
pip install -e ".[dev]"

# 2. 抓榜单
python3 scripts/trending_fetcher.py fetch daily          # daily/weekly/monthly
python3 scripts/trending_fetcher.py fetch daily python   # 按语言过滤

# 3. 检查某 repo 报告是否需更新（7 天缓存）
python3 scripts/trending_fetcher.py check owner/repo

# 4. GitHub API 取数
python3 scripts/github_api.py <owner> <repo> summary

# 5. 报告质量校验（8 项，commit 前必过）
python3 scripts/validate_reports.py owner/repo           # 单篇
python3 scripts/validate_reports.py --fail-only --index  # 全量 + 索引一致性
```

## 目录

```
scripts/     全部脚本（只读）：trending_fetcher / report_generator / github_api / validate_reports
skills/      三件事各一 skill：repo-research / trending-analyzer / deep-research
assets/      report_template.md
reports/     【唯一输出目录】research_*.md + all-*-summary-*.md
knowledge/   reports_index.md（报告索引）
tests/       单元测试
```

## 知识库现状（`reports/`）

- **Repo 深度报告**：106 篇（AI/ML、DevTools、Infra、Agent 等）
- **汇总报告**：daily ×7、weekly ×2、monthly ×4（共 13 篇）
- 完整索引 → [`knowledge/reports_index.md`](./knowledge/reports_index.md)

## 质量校验

```bash
ruff check scripts tests
pytest -q
```

CI：`.github/workflows/trending-analyzer-ci.yml`（push/PR 自动跑 ruff + pytest）。
