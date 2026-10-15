# ai-learning — 领域协议

> 领域：AI/ML 论文精读与技术深度报告 **+ AI 行业与商业观察**（行业访谈/商业案例/公司与人才信号——2026-07-29 用户拍板扩边界，旧"纯技术"边界作废）。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。
> 联网与个人上下文遵守根 `AGENTS.md` 的托管策略，本文件不重复工具细节。

---

## 工作模式：对话即学习

- 用户明确要求学习、精读、深挖或出报告时，使用根 skill [`everagent-report`](../.agents/skills/everagent-report/SKILL.md) 与 [REPORT_WORKFLOW](../docs/REPORT_WORKFLOW.md)。
- 通过 eacli 从 `knowledge.ai` 获取最小 context，只读取命中的报告或 wiki；需要调节讲法时读 PROFILE，需要更新覆盖时读 MAP，需要续接问题时读 open-questions。命令格式见 REPORT_WORKFLOW。
- 建直觉时读 [科普讲解](./skills/科普讲解/SKILL.md)；需要公式、消融、工程参数或落地时读 [concept_deep_dive](./skills/concept_deep_dive/SKILL.md) 或 [paper_analysis](./skills/paper_analysis/SKILL.md)。用户已经明确要求“深度”时直接采用深度专业体。
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
status: "in_progress"
updated_on: "YYYY-MM-DD"
quality_schema: "report-v2"
quality_tier: "important"
semantic_tags: ["tag"]
---
```

文件命名：论文 `{序号}_{简称}_{年份}.md`；概念科普 `{主题}_科普讲解_{日期}.md`；深度专业 `{主题}_深度解析_{日期}.md`。

---

## 完成后

> 用户原话（2026-07-17）：**"只是跑代码脚本的检查是自嗨，应该关注我的学习情况的反馈。"**
> 排序照此：**学习反馈 > 配方自检 > 脚本自检**。

1. **收学习反馈（第一位）** — 交付后主动问一句"懂了 / 卡在哪 / 没读下去 / 深度不够"，落进
   [skills/科普讲解/FEEDBACK_LOG.md](./skills/科普讲解/FEEDBACK_LOG.md)。反馈是迭代技能的唯一燃料。
2. **配方自检** — 只对照本次体裁对应的一个 skill。
3. **确定性检查**：
   ```bash
   python3 scripts/reindex.py
   python3 scripts/audit_reports.py --changed
   python3 scripts/reindex.py --check
   ```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
