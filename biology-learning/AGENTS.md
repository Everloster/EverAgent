# biology-learning — 领域协议

> 领域：时间生物学·睡眠科学·运动生理学·内分泌代谢的论文精读与概念深挖。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。
> 联网与个人上下文遵守根 `AGENTS.md` 的托管策略，本文件不重复工具细节。

---

## 工作模式：对话即学习

用户明确要求学习、精读、深挖或出报告时，使用根 skill [`everagent-report`](../.agents/skills/everagent-report/SKILL.md) 与 [REPORT_WORKFLOW](../docs/REPORT_WORKFLOW.md)。通过 eacli 从 `knowledge.biology` 获取最小 context，再按需读取 PROFILE、MAP、open-questions 和一个体裁 skill。

> 追问已有主题时：在原报告追加 `## 追问深入 [日期]` 小节并刷新 `updated_on`，不另开新文件。

---

## 领域特化

- **报告类型**：`reports/paper_analyses/`（论文精读）、`reports/concept_reports/`（概念深挖）
- **特化要求**：报告 n=、研究类型、人群；证据等级（RCT>队列>横断面>动物>细胞）；动物/体外实验须标注不可直接推广；机制追溯到分子通路；**禁止给无证据的健康/医疗建议**
- **特化模板**：[skills/paper_analysis/SKILL.md](./skills/paper_analysis/SKILL.md)、[skills/concept_deep_dive/SKILL.md](./skills/concept_deep_dive/SKILL.md)

---

## 报告 frontmatter

```yaml
---
title: "标题"
domain: "biology-learning"
report_type: "paper_analysis"   # 或 concept_report
status: "in_progress"
updated_on: "YYYY-MM-DD"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["tag"]
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
