# podcast-learning — 领域协议

> 领域：播客内容学习与知识提取（跨领域：AI/科技/商业/医疗/哲学/心理学等）。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。

---

## 工作模式：对话即学习

用户说"帮我消化这期播客 / 整理某访谈 / 上次那个继续"，按以下循环：

1. **读画像与地图** — [PROFILE.md](./PROFILE.md)、[MAP.md](./MAP.md)、[wiki/open-questions.md](./wiki/open-questions.md)
2. **获取转录** — 通过 `agent-reach xiaoyuzhou` skill 拉取转录（Groq Whisper）；转录存 `/tmp`，重启清空，须在同会话归档
3. **提取** — 通读转录，提取核心观点/关键人物/新概念/关键数字/金句
4. **写报告** — 存 `reports/text_analyses/`，带 frontmatter，结尾必带「思考与追问」三问
5. **沉淀** — 更新 wiki（人物/概念页）、未解问题汇入 open-questions
6. **更新画像** — 把新关注的节目/人物/主题写回 PROFILE（仅凭用户真实表达，禁止臆测）

---

## 领域特化

- **报告类型**：`reports/text_analyses/`（单期精读）、`reports/knowledge_reports/`（跨期专题）、`reports/concept_reports/`（概念/人物追踪）
- **特化要求（关键）**：**转录中未出现的引用、数据、人物言论禁止推测**；关键引用保留原文（哪怕标点残缺）；转录质量差时在 limitations 标注，不强行总结
- **特化模板**：[skills/paper_analysis/SKILL.md](./skills/paper_analysis/SKILL.md)、[skills/concept_deep_dive/SKILL.md](./skills/concept_deep_dive/SKILL.md)

---

## 报告 frontmatter

```yaml
---
title: "标题"
domain: "podcast-learning"
report_type: text_analysis   # 或 knowledge_report / concept_report
source: 小宇宙播客
source_url: https://www.xiaoyuzhoufm.com/episode/...
show: "节目名"
guest: "嘉宾"
status: archived
updated_on: YYYY-MM-DD
---
```

文件命名：`{YYYY-MM-DD}_{show}_{ep}_{slug}.md`。

---

## 完成后自检

```bash
python3 scripts/reindex.py
```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
