# Report Metadata

为保证跨子项目报告可追踪，新增报告与实质重写的报告使用如下 frontmatter；历史报告按需迁移：

```yaml
---
title: "报告标题"
domain: "ai-learning"
report_type: "paper_analysis"
status: "in_progress"
updated_on: "2026-03-25"
quality_schema: "report-v2"
quality_tier: "important"
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
| `domain` | 所属子项目，允许值见下方补充约定 |
| `report_type` | 报告类型（`paper_analysis`、`knowledge_report`、`concept_report`、`text_analysis`） |
| `status` | 状态（`completed`、`in_progress`、`planned`） |
| `updated_on` | 最近更新时间（`YYYY-MM-DD`） |
| `quality_schema` | 新报告使用 `report-v2`，启用证据账本与独立复核；`report-v1` 为过渡格式 |
| `quality_tier` | `standard`、`important` 或 `flagship`，决定来源、Reviewer 和评分门槛 |

### 语义字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `semantic_tags` | `report-v2` 必填；技术标签/关键词列表，用于跨报告检索和关联 | `["transformer", "attention", "moe"]` |
| `related_concepts` | 关联的 wiki/concepts/ 页面名（不含 .md 后缀） | `["self_attention", "moe_architecture"]` |
| `related_entities` | 关联的 wiki/entities/ 页面名（不含 .md 后缀） | `["vaswani_ashish", "openai"]` |

## 补充约定

- 新增报告与实质重写的报告遵循此规范；历史报告不因缺字段而批量重写。
- `domain` 可取：`ai-learning`、`cs-learning`、`philosophy-learning`、`psychology-learning`、`biology-learning`、`ai-practice`、`podcast-learning`、`github-trending-analyzer`、`web-surfing`。
- `report_type` 按领域取值，例如 `paper_analysis`、`knowledge_report`、`concept_report`、`text_analysis`、`experiment_analysis`、`episode_summary`、`cross_episode`、`repo_deep_research`、`daily_summary`、`weekly_summary`、`monthly_summary`、`web_report`。
- `status` 规范值为 `completed`、`in_progress`、`planned`、`archived`、`cached`、`superseded`、`degraded_shownotes_only`。
- **新增报告**必须填写 `semantic_tags`；`related_concepts` 和 `related_entities` 在有明确关联时填写。
- `semantic_tags` 使用小写英文，多个单词用下划线连接（如 `test_time_compute`）。
- 以上字段由 `scripts/reindex.py` 消费，自动生成阅读索引 [REPORT_INDEX.md](./REPORT_INDEX.md)（按更新时间列出全部报告）。缺少日期元数据的历史报告沿用索引中已有日期，避免 Git 快照不保留文件 mtime 导致索引漂移。
- `reports/transcripts/` 下的 shownotes、转写与润色稿属于来源产物，不计入报告数量和阅读索引。
- `report-v2` 的证据与复核文件放在报告同级 `.quality/` 目录；`in_progress` 可在本地暂缺，新增报告提交前必须通过质量门并 finalize。详细格式见 [REPORT_QUALITY_GATE.md](./REPORT_QUALITY_GATE.md)。
- 当前质量门：`python3 scripts/audit_reports.py --changed`；全库盘点：`python3 scripts/audit_reports.py --all --json`。
