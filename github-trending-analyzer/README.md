# GitHub Trending Analyzer

用于抓取 GitHub Trending、生成项目报告和汇总报告的脚本集合。

## Quick Start

### 1. 准备 Python 环境

要求：Python 3.9+

可选方案：

- 系统 Python（`python` / `py -3`）
- `uv`（推荐，速度更快）

### 2. 安装依赖

```bash
pip install -e ".[dev]"
```

### 3. 运行示例

```bash
# 获取日榜
python github-trending-analyzer/trending_fetcher.py fetch daily

# 检查某个仓库报告是否需要更新
python github-trending-analyzer/trending_fetcher.py check owner/repo
```

### 4. 质量检查

```bash
ruff check github-trending-analyzer github-deep-research/scripts tests
pytest -q
```

## 目录说明

- `github-trending-analyzer/SKILL.md`: 热点趋势分析主技能（抓取榜单、生成汇总）
- `github-deep-research/SKILL.md`: 单仓库深度研究技能（深入分析具体项目）
- `github-trending-analyzer/trending_fetcher.py`: Trending 数据抓取与报告缓存检查
- `github-trending-analyzer/report_generator.py`: 单项目和汇总报告生成
- `github-deep-research/scripts/github_api.py`: GitHub API 封装
- `tests/`: 单元测试

## CI

仓库使用 GitHub Actions 自动执行 `ruff + pytest`：

- `.github/workflows/trending-analyzer-ci.yml`
