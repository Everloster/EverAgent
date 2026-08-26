# Skill: episode_analysis — 播客总结/报告模板

> 通用研究方法论与「思考与追问」要求见根 [METHODOLOGY.md](../../../METHODOLOGY.md)（强制）。本文件为领域特化部分。
> 前置：已有 `reports/transcripts/{slug}.transcript.txt`（及润色稿）。报告一切事实以转写原文为准。

---

## 三种报告类型（同存 `reports/`，用 frontmatter `report_type` 区分）

| report_type | 场景 | 侧重 |
|-------------|------|------|
| `episode_summary` | 单期消化 | 核心观点 + 金句 + 概念/人物 |
| `cross_episode` | 跨期专题 | 多期同主题的横向梳理与对比 |
| `concept_tracking` | 概念/人物追踪 | 某概念或某人观点在多期中的演变 |

文件命名：`{YYYY-MM-DD}_{show}_{ep}_{slug}.md`。

---

## 输出结构（episode_summary）

```markdown
---
title: "..."
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://...
show: "节目名"
guest: "嘉宾"
transcript: reports/transcripts/{slug}.transcript.txt
status: archived
updated_on: YYYY-MM-DD
---

## 一句话总结
> 这期在讲什么，最值得记住的一点。

## 背景
- 节目/嘉宾是谁，为什么值得听（可查证的客观信息，来源标注）。

## 核心观点（3-6 条）
- 观点：……（如有原话，引用转写原文，标大致时间戳）

## 关键概念 / 人物 / 数字
- 概念：定义 + 嘉宾如何用它
- 人物/机构：转写中提到的、值得沉淀到 wiki 的
- 数字：**只用转写中明确出现的数字**，标注

## 金句
> 原文引用（保留措辞）。

## 我的思考与延伸
- 与我已知的哪些内容关联

## Limitations
- 转写质量、缺失片段、未辨识处（如有）

## 思考与追问
1. 我真正理解了什么？
2. 我还没搞懂什么？（汇入 wiki/open-questions.md）
3. 下一步听什么 / 查什么？
```

`cross_episode` / `concept_tracking` 复用上面骨架，把「核心观点」换成跨期对比表或演变时间线。

> 观点成体系、摘要装不下推理路径时，改用 [qa_chain](../qa_chain/SKILL.md) 的问答链格式（`format: qa_chain`）。

---

## 规则

1. **事实以转写为准**：转写外的引用/数据/言论禁止出现（见 transcription skill 红线）。
2. **客观背景信息**（嘉宾履历、节目定位等）若非转写内容，须 WebSearch 查证并标来源，不编造。
3. **沉淀**：报告完成后更新 `wiki/`（新人物/概念页）、未解问题汇入 `wiki/open-questions.md`。
4. **继续讨论**：用户追问时围绕转写原文 + 已查证事实展开，不引入编造内容。
