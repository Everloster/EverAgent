# everloster-star-analysis

> 对 GitHub 用户 `Everloster` 的 starred 仓库做时间窗汇总分析的知识库。

## 目录结构

```
everloster-star-analysis/
├── README.md         # 本文件
├── scripts/          # 数据拉取与分析脚本
│   ├── fetch_stars.py
│   └── analyze.py
├── raw/              # 全量 starred raw JSON(按 page 切分,断点续传)
├── data/             # 处理后中间数据(过滤 / 补字段 / 分类)
└── reports/          # 分析报告
```

## 数据来源

- GitHub REST API `/user/starred`,通过本地 `gh` CLI 鉴权(token 存于 keyring)
- 用户 ID: `2820419`(账号 `Everloster`)

## 命名规范

### 报告文件

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 时间窗汇总 | `everloster-star-{period}-summary-{YYYY-MM-DD}.md` | `everloster-star-3y-summary-2026-06-03.md` |
| 单 repo 深度(预留) | `research_{owner}_{repo}.md` | `research_foo_bar.md` |

- `period` ∈ `{1y, 2y, 3y, 5y, all}`
- `date` = 数据截止 UTC 日期(ISO 8601)
- 文件名小写、连字符、无空格

### 数据文件

| 类型 | 命名格式 | 说明 |
|------|---------|------|
| Raw 单页 | `raw/page_{NNN}.json` | 全量 starred 按 100/页 切分,`NNN` 三位补零 |
| 过滤子集 | `data/starred_{period}.json` | 按时间窗过滤后的子集 |
| 补字段子集 | `data/starred_{period}_detailed.json` | 补 topics / created_at / license 后 |
| 分类结果 | `data/categories_{period}.json` | 主题分类 + 频次 |

## 报告章节模板

汇总报告统一按以下 8 章(中文):

1. 报告概览
2. 总量与时间分布
3. 编程语言分布
4. 主题分类与代表项目
5. 高 Star 项目 Top N
6. 趋势观察
7. 总结
8. 附录(数据来源 · 方法 · 限制)

## 重新生成

```bash
# 1. 拉取(后台,带断点续传)
python3 scripts/fetch_stars.py

# 2. 过滤 + 补字段 + 分类
python3 scripts/analyze.py --period 3y

# 3. 报告自动写入 reports/
```

## 边界(防幻觉)

- 数值(Stars / Forks / 频次)必须来自 API 返回值,禁止估算
- 主题分类基于 GitHub repo `topics` 字段,无法归类时归入「其他」并显式标注
- 报告内容生成后须人工 review 关键数据点
