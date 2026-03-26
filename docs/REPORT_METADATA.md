# Report Metadata

为保证跨子项目报告可追踪，建议所有 `reports/**/*.md` 使用如下 frontmatter：

```yaml
---
title: "报告标题"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-03-25"
---
```

字段说明：

- `title`: 报告标题
- `domain`: 所属子项目（`ai-learning` / `biology-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `github-trending-analyzer`）
- `report_type`: 报告类型（如 `paper_analysis`、`knowledge_report`、`concept_report`、`text_analysis`）
- `status`: 状态（建议值：`completed`、`in_progress`、`planned`）
- `updated_on`: 最近更新时间（`YYYY-MM-DD`）

补充约定：

- 学习型子项目下的 `reports/**/*.md` 默认应遵循此规范。
- `github-trending-analyzer/github-trending-reports/` 下的自动生成报告可暂缓补齐，但推荐逐步对齐，便于后续统一索引。
