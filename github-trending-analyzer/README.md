# github-trending-analyzer

> GitHub 开源热点追踪 · Repo 深度研究 · 趋势洞察知识库。
> **双重身份**：自动化分析工具 + 离线知识库。执行协议见 [`AGENTS.md`](./AGENTS.md)。

## 只做三件事

| # | 事 | 触发 | 产出 |
|---|----|------|------|
| A | 单 repo 深度研究 | 对话贴 repo 链接 | `reports/research_{owner}_{repo}.md` |
| B | trending 汇总 | "出日/周/月 trending 报告" | `reports/all-{period}-summary-{date}.md` + 榜上各 repo 报告 |
| C | 迭代优化研究技能本身 | 每次做完 A/B 后 | 对 `skills/repo-research/SKILL.md` 的改进（元活动） |

**事A 就是深度研究方法论本身**（4 轮研究 + 7 章中文报告，见 `skills/repo-research/`）。事B 建立在事A 之上：抓榜单 → 对榜上每个 repo 做一次事A → 汇总。**事C 是元活动**：把每次研究踩到的坑与更优做法折回事A 的 skill，越用越强。

> 报告质量靠**遵循并持续迭代 skill 规范（事C）**保证，不靠脚本校验。发现更好的研究做法就直接改 `skills/repo-research/SKILL.md`。

## Quick Start

```bash
# 1. 依赖（Python 3.9+；gh CLI 已 gh auth login）
pip install -e ".[dev]"

# 2. 抓榜单
python3 scripts/trending_fetcher.py fetch daily          # daily/weekly/monthly
python3 scripts/trending_fetcher.py fetch daily python   # 按语言过滤

# 3. 检查某 repo 是否已有报告（7 天缓存判断）
python3 scripts/trending_fetcher.py check owner/repo

# 4. GitHub API 取数（4 轮研究的取数入口）
python3 scripts/github_api.py <owner> <repo> summary
```

## 目录

```
scripts/     辅助脚本（只读）：trending_fetcher / report_generator / github_api
skills/      两件事各一 skill：repo-research（含 4 轮方法论）/ trending-analyzer
assets/      report_template.md
reports/     【唯一输出目录】research_*.md + all-*-summary-*.md
knowledge/   reports_index.md（人类导航索引，可选维护）
tests/       脚本单元测试
```

## 知识库现状（`reports/`）

- **Repo 深度报告**：107 篇（AI/ML、DevTools、Infra、Agent 等）
- **汇总报告**：daily ×7、weekly ×2、monthly ×4（共 13 篇）
- 完整索引 → [`knowledge/reports_index.md`](./knowledge/reports_index.md)

## 脚本自检

```bash
ruff check scripts tests
pytest -q
```

CI：`.github/workflows/trending-analyzer-ci.yml`（push/PR 自动跑 ruff + pytest，仅护脚本，不校验报告内容）。
