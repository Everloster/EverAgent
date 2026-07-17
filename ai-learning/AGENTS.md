# ai-learning — 领域协议

> 领域：AI/ML 论文精读与技术深度报告。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。

---

## 工作模式：对话即学习

用户说"帮我学 X / 深入 Y / 上次那个继续"，按以下循环：

1. **读画像与地图** — [PROFILE.md](./PROFILE.md)（兴趣/水平/偏好）、[MAP.md](./MAP.md)（覆盖与缺口）、[wiki/open-questions.md](./wiki/open-questions.md)（未解问题）
2. **查已有积累** — 翻 `wiki/concepts/` 与 `reports/`，已有则深化而非重复
3. **做研究** — 按 METHODOLOGY 真读原文、查证、标注证据；框架见 `skills/`
4. **写报告** — 存 `reports/`，带 frontmatter，结尾必带「思考与追问」三问。
   **先判场景选体裁**（见 [科普讲解 §0 场景表](./skills/科普讲解/SKILL.md)）：建直觉/想通原理 → [科普讲解](./skills/科普讲解/SKILL.md)；要公式/消融数字/工程参数/落地 → 深度专业（[concept_deep_dive](./skills/concept_deep_dive/SKILL.md) / [paper_analysis](./skills/paper_analysis/SKILL.md)）。**场景不明就先问用户要哪种**。
5. **收学习反馈** — 交付后主动收一次反馈（懂了 / 卡在X / 没读下去 / 深度不够），落进 [skills/科普讲解/FEEDBACK_LOG.md](./skills/科普讲解/FEEDBACK_LOG.md)。
6. **沉淀** — 更新 wiki（概念/实体页追加链接）、未解问题汇入 open-questions、必要时写 syntheses
7. **更新画像** — 把新兴趣/水平/偏好写回 PROFILE（仅凭用户真实表达，禁止臆测）

> 追问已有主题时：在原报告追加 `## 追问深入 [日期]` 小节并刷新 `updated_on`，不另开新文件。

---

## 领域特化

- **报告类型**：`reports/paper_analyses/`（论文精读）、`reports/knowledge_reports/`（概念专题）
- **体裁按场景选**：建直觉/想通原理 → [科普讲解](./skills/科普讲解/SKILL.md)（钩子标题·贯穿类比·渐进式暴露·一页纸）；要精确公式/消融数字/工程参数/落地 → 深度专业。二者平级，判断依据见 [科普讲解 §0 场景表](./skills/科普讲解/SKILL.md)。
- **特化要求**：核心公式逐符号解释；消融实验数字精确引用；含"历史叙事"（前驱+后续影响）
- **特化模板**：[科普讲解](./skills/科普讲解/SKILL.md)（建直觉体裁）、[concept_deep_dive](./skills/concept_deep_dive/SKILL.md)（概念五层次深度专业）、[paper_analysis](./skills/paper_analysis/SKILL.md)（逐篇精读）

---

## 报告 frontmatter

```yaml
---
title: "标题"
domain: "ai-learning"
report_type: "paper_analysis"   # 或 knowledge_report
status: "completed"
updated_on: "YYYY-MM-DD"
---
```

文件命名：论文 `{序号}_{简称}_{年份}.md`；概念科普 `{主题}_科普讲解_{日期}.md`；深度专业 `{主题}_深度解析_{日期}.md`。

---

## 完成后：先看学习反馈，脚本只是兜底

> 用户原话（2026-07-17）：**"只是跑代码脚本的检查是自嗨，应该关注我的学习情况的反馈。"**
> 排序照此：**学习反馈 > 配方自检 > 脚本自检**。

1. **收学习反馈（第一位）** — 交付后主动问一句"懂了 / 卡在哪 / 没读下去 / 深度不够"，落进
   [skills/科普讲解/FEEDBACK_LOG.md](./skills/科普讲解/FEEDBACK_LOG.md)。反馈是迭代技能的唯一燃料。
2. **配方自检（第二位，按体裁）** — 科普体对照 [科普讲解 §4 自检表](./skills/科普讲解/SKILL.md)（钩子标题·贯穿类比·渐进式暴露·一页纸）；深度专业体对照 [concept_deep_dive](./skills/concept_deep_dive/SKILL.md) / [paper_analysis](./skills/paper_analysis/SKILL.md) 的证据标准（公式逐符号、消融数字精确）。
3. **脚本自检（兜底，非阻塞）** — 仅验证证据密度，**不代表"讲得好"**：
   ```bash
   python3 scripts/lint_evidence.py <报告路径>   # 证据兜底
   python3 scripts/reindex.py                     # 刷新 README 计数
   ```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
