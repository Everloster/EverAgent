# Skill: episode_analysis — 播客总结/报告模板

> 通用研究方法论与「思考与追问」要求见根 [METHODOLOGY.md](../../../METHODOLOGY.md)；按当前任务读取相关章节。本文件只保留领域差异。
> 前置：已取得完整原文与润色稿，默认存放在仓库外私有目录。节目观点以原始材料为据；转写疑点需核验，外部事实另附来源。

---

## 三种报告类型（同存 `reports/`，用 frontmatter `report_type` 区分）

| report_type | 场景 | 侧重 |
|-------------|------|------|
| `episode_summary` | 单期消化 | 核心观点 + 金句 + 概念/人物 |
| `cross_episode` | 跨期专题 | 多期同主题的横向梳理与对比 |
| `concept_tracking` | 概念/人物追踪 | 某概念或某人观点在多期中的演变 |

文件命名：`{YYYY-MM-DD}_{show}_{ep}_{slug}.md`。

---

## 输出结构参考（episode_summary，标题与节数按内容调整）

```markdown
---
title: "..."
domain: "podcast-learning"
report_type: episode_summary
source: 小宇宙播客
source_url: https://...
show: "节目名"
guest: "嘉宾"
transcript_visibility: private
transcript_path: null
polished_transcript_path: null
status: in_progress
updated_on: YYYY-MM-DD
quality_schema: "report-v2"
quality_tier: "important"
report_depth: "standard"
reader_contract: "standalone"
semantic_tags: ["podcast"]
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
- 数字：标明来源和统计口径，区分节目中的说法与独立核实的结果

## 金句
> 原文引用（保留措辞）。

## 分析与延伸
- 与相关知识的联系、推论及适用边界

## Limitations
- 转写质量、缺失片段、未辨识处（如有）

## 思考与追问
1. 我真正理解了什么？
2. 我还没搞懂什么？（汇入 wiki/open-questions.md）
3. 下一步听什么 / 查什么？
```

`cross_episode` / `concept_tracking` 复用上面骨架，把「核心观点」换成跨期对比表或演变时间线。

`standard/deep` 报告需完整展开来源主线，不以固定标题或小节数量判断深度。按原始来源建立 evidence 的 `source_coverage`，由独立 Reviewer 留下 `source_content_map`；覆盖表留在质量文件，正文选择方便读者的导航与讲解结构。详细合同见 [report-guide §三](../report-writing/references/report-guide.md#三报告写作规范模板-v2)。

> 观点成体系、摘要装不下推理路径时，改用 [qa_chain](../qa_chain/SKILL.md) 的问答链格式（`format: qa_chain`）。

---

## 规则

1. **忠实记录与事实核验分开**：不把转写误识别或嘉宾口误固化成事实。补充引用、数据和背景须实际查证、标明来源，不冒充节目原话。
2. **客观背景信息**（嘉宾履历、节目定位等）若非转写内容，须通过 eacli 查证并标来源，不编造。
3. **沉淀**：只为可复用的新知识或值得续接的问题做必要的 wiki 更新，不为每篇报告自动新建页面。
4. **继续讨论**：用户追问时围绕转写原文 + 已查证事实展开，不引入编造内容。
