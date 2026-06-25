# cs-learning — 领域协议

> 领域：计算机科学（系统·算法·分布式·数据库·网络）经典论文精读与概念深挖。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。

---

## 工作模式：对话即学习

用户说"帮我学 X / 深入 Y / 上次那个继续"，按以下循环：

1. **读画像与地图** — [PROFILE.md](./PROFILE.md)、[MAP.md](./MAP.md)、[wiki/open-questions.md](./wiki/open-questions.md)
2. **查已有积累** — 翻 `wiki/concepts/` 与 `reports/`，已有则深化而非重复
3. **做研究** — 按 METHODOLOGY 真读原文、查证、标注证据；框架见 `skills/`
4. **写报告** — 存 `reports/`，带 frontmatter，结尾必带「思考与追问」三问
5. **沉淀** — 更新 wiki、未解问题汇入 open-questions、必要时写 syntheses
6. **更新画像** — 把新兴趣/水平/偏好写回 PROFILE（仅凭用户真实表达，禁止臆测）

> 追问已有主题时：在原报告追加 `## 追问深入 [日期]` 小节并刷新 `updated_on`，不另开新文件。

---

## 领域特化

- **报告类型**：`reports/paper_analyses/`（论文精读）、`reports/knowledge_reports/`（概念深挖）
- **特化要求**：正确性证明重构关键步骤；复杂度精确到 big-O（注明 worst/amortized/expected）；伪代码可复现；trade-off 给具体数值
- **特化模板**：[skills/paper_analysis/SKILL.md](./skills/paper_analysis/SKILL.md)、[skills/concept_deep_dive/SKILL.md](./skills/concept_deep_dive/SKILL.md)

---

## 报告 frontmatter

```yaml
---
title: "标题"
domain: "cs-learning"
report_type: "paper_analysis"   # 或 knowledge_report
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

---

## 完成后自检

```bash
python3 scripts/lint_evidence.py <报告路径>
python3 scripts/reindex.py
```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
