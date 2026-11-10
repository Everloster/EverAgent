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
report_depth: "standard"
reader_contract: "standalone"
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
| `report_depth` | `brief`、`standard` 或 `deep`；控制内容深度，不等同于质量等级。播客学习任务默认 `standard` |
| `reader_contract` | `standalone` 表示报告是主要消费面，不能要求读者再打开 polished 才能理解核心内容 |

### 语义字段

| 字段 | 说明 | 示例 |
|------|------|------|
| `semantic_tags` | `report-v2` 必填；技术标签/关键词列表，用于跨报告检索和关联 | `["transformer", "attention", "moe"]` |
| `related_concepts` | 关联的 wiki/concepts/ 页面名（不含 .md 后缀） | `["self_attention", "moe_architecture"]` |
| `related_entities` | 关联的 wiki/entities/ 页面名（不含 .md 后缀） | `["vaswani_ashish", "openai"]` |

## 历史元数据兼容

`scripts/report_catalog.py` 维护唯一别名表，读取视图统一以下历史拼写：

| 字段 | 历史拼写 | 规范值 |
|---|---|---|
| `status` | `complete`、`done` | `completed` |
| `report_type` | `概念深度解析`、`concept_deep_dive` | `concept_report` |
| `report_type` | `ai_news_daily`、`daily_digest` | `daily_summary` |

`report_info()` 同时返回规范化的 `metadata` 与原始 `raw_metadata`；`parse_frontmatter()` 保留原始字段，质量审计与哈希校验继续读取原件。未知类型不猜测映射，缺失字段不自动编造。这是读取兼容，不批量重写历史报告，也不刷新原报告的日期或复核收据。新增或实质修改的 `report-v2` 报告应使用规范拼写。

## 补充约定

- 新增报告与实质重写的报告遵循此规范；历史报告不因缺字段而批量重写。
- `domain` 可取：`ai-learning`、`cs-learning`、`philosophy-learning`、`psychology-learning`、`biology-learning`、`ai-practice`、`podcast-learning`、`github-trending-analyzer`、`web-surfing`。
- `report_type` 按领域取值，例如 `paper_analysis`、`knowledge_report`、`concept_report`、`text_analysis`、`experiment_analysis`、`episode_summary`、`cross_episode`、`repo_deep_research`、`daily_summary`、`weekly_summary`、`monthly_summary`、`web_report`。
- `status` 规范值为 `completed`、`in_progress`、`planned`、`archived`、`cached`、`superseded`、`degraded_shownotes_only`。
- **新增报告**必须填写 `semantic_tags`；`related_concepts` 和 `related_entities` 在有明确关联时填写。
- 2026-10-20 起新增或实质重写的播客报告填写 `report_depth` 与 `reader_contract: standalone`；`brief` 只用于用户明确要求速览或摘要。此前已经成稿的报告不因字段新增被追溯阻断。
- `semantic_tags` 使用小写英文，多个单词用下划线连接（如 `test_time_compute`）。
- 以上字段由 Go `ea-quality index --write` 消费，自动生成阅读索引 [REPORT_INDEX.md](./REPORT_INDEX.md)（按更新时间列出全部报告）。缺少日期元数据的历史报告沿用索引中已有日期；仍未知就保持未知，不以文件 mtime 伪造更新日期。完整命令见[共享协议](./PROTOCOL_COMMON.md#d-报告质量门)。
- `reports/transcripts/` 下的 shownotes、转写与润色稿属于来源产物，不计入报告数量和阅读索引。
- `report-v2` 的证据与复核文件放在报告同级 `.quality/` 目录；`in_progress` 可在本地暂缺，新增报告提交前必须通过质量门并 finalize。详细格式见 [REPORT_QUALITY_GATE.md](./REPORT_QUALITY_GATE.md)。
- 当前质量门：`python3 scripts/audit_reports.py --changed`；全库盘点：`python3 scripts/audit_reports.py --all --json`。
