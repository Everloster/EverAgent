# philosophy-learning — 领域协议

> 领域：世界哲学（含中国哲学）文本分析与概念深挖。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。
> 联网与个人上下文遵守根 `AGENTS.md` 的托管策略，本文件不重复工具细节。

---

## 工作模式：对话即学习

用户明确要求学习、精读、深挖或出报告时，使用根 skill [`everagent-report`](../.agents/skills/everagent-report/SKILL.md) 与 [REPORT_WORKFLOW](../docs/REPORT_WORKFLOW.md)。通过 eacli 从 `knowledge.philosophy` 获取最小 context，再按需读取 PROFILE、MAP、open-questions 和一个体裁 skill。哲学文本采用 METHODOLOGY 的三遍阅读法。

> 追问已有主题时：在原报告追加 `## 追问深入 [日期]` 小节并刷新 `updated_on`，不另开新文件。

---

## 领域特化

- **报告类型**：`reports/text_analyses/`（文本分析）、`reports/concept_reports/`（概念深挖）
- **特化要求**：论证重构忠实原文（不加作者没有的前提，隐含前提标注）；关键概念回到原文界定技术含义；原文引用标准页码（Stephanus/Academy/节号）；呈现最强反驳
- **特化模板**：[skills/text_analysis/SKILL.md](./skills/text_analysis/SKILL.md)、[skills/concept_deep_dive/SKILL.md](./skills/concept_deep_dive/SKILL.md)

---

## 报告 frontmatter

```yaml
---
title: "标题"
domain: "philosophy-learning"
report_type: "text_analysis"   # 或 concept_report
status: "completed"
updated_on: "YYYY-MM-DD"
quality_schema: "report-v1"
---
```

---

## 完成后自检

```bash
python3 scripts/reindex.py
python3 scripts/audit_reports.py --changed
python3 scripts/reindex.py --check
```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
