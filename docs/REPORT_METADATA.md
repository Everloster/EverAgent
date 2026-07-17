# Report Metadata

为保证跨子项目报告可追踪，建议所有 `reports/**/*.md` 使用如下 frontmatter：

```yaml
---
title: "报告标题"
domain: "ai-learning"
report_type: "paper_analysis"
status: "completed"
updated_on: "2026-03-25"
semantic_tags: ["transformer", "attention", "nlp"]
related_concepts: ["self_attention", "positional_encoding"]
related_entities: ["vaswani_ashish", "google_brain"]
---
```

## 字段说明

### 基础字段（必填）

| 字段 | 说明 |
|------|------|
| `title` | 报告标题 |
| `domain` | 所属子项目（`ai-learning` / `biology-learning` / `cs-learning` / `philosophy-learning` / `psychology-learning` / `github-trending-analyzer`） |
| `report_type` | 报告类型（`paper_analysis`、`knowledge_report`、`concept_report`、`text_analysis`） |
| `status` | 状态（`completed`、`in_progress`、`planned`） |
| `updated_on` | 最近更新时间（`YYYY-MM-DD`） |

### 语义字段（Phase 2 新增，可选但推荐）

| 字段 | 说明 | 示例 |
|------|------|------|
| `semantic_tags` | 技术标签/关键词列表，用于跨报告检索和关联 | `["transformer", "attention", "moe"]` |
| `related_concepts` | 关联的 wiki/concepts/ 页面名（不含 .md 后缀） | `["self_attention", "moe_architecture"]` |
| `related_entities` | 关联的 wiki/entities/ 页面名（不含 .md 后缀） | `["vaswani_ashish", "openai"]` |

## 补充约定

- 学习型子项目下的 `reports/**/*.md` 默认应遵循此规范。
- `github-trending-analyzer/github-trending-reports/` 下的自动生成报告可暂缓补齐，但推荐逐步对齐，便于后续统一索引。
- **新增报告**建议填写 `semantic_tags` 和 `related_concepts`，为后续知识图谱自动构建提供数据基础。
- `semantic_tags` 使用小写英文，多个单词用下划线连接（如 `test_time_compute`）。
- 以上字段由 `scripts/reindex.py` 消费，自动生成阅读索引 [REPORT_INDEX.md](./REPORT_INDEX.md)（按更新时间列出全部报告）。
