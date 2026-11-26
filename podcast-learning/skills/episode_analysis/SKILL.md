# Skill: episode_analysis — 播客论证分析

> 通用研究方法论与「思考与追问」要求见根 [METHODOLOGY.md](../../../METHODOLOGY.md)；按当前任务读取相关章节。本文件只保留领域差异。
> 完整节目分析须以足够的原始材料为据，转写与润色稿默认留在仓外私有目录。来源不足时可先保存明确标注范围的草稿，不冒充完整学习；转写疑点需核验，外部事实另附来源。

---

## 三种报告类型（同存 `reports/`，用 frontmatter `report_type` 区分）

| report_type | 场景 | 侧重 |
|-------------|------|------|
| `episode_summary` | 单期消化 | 主问题、关键论证、例子与分歧 |
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
report_depth: "standard"
reader_contract: "standalone"
semantic_tags: ["podcast"]
---

# 报告标题

## 概述

总结主线与主要发现，提炼值得记住的见解；原话引用要有来源和时间。

**提炼句：** 本报告的凝练表达，不冒充嘉宾原话。

## 取景框 f(x)

**x｜问题：** 本期真正处理的具体问题。

**f｜取景框：** 嘉宾的核心区分与观察视角。

**f(x)｜判断变化：** 用该视角重看问题，判断或行动怎样改变，何时适用。

## 背景
- 节目/嘉宾是谁，为什么值得听（可查证的客观信息，来源标注）。

## 核心观点与论证
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

`cross_episode` / `concept_tracking` 也先呈现概述与取景框，正文按跨期比较或概念演变组织。两部分之后的章节只是可选分析维度，不要求完整目录或固定三问；无可靠引文时使用作者提炼，转写过程与无关项目联想不进入正文。

`standard/deep`报告需完整展开来源主线，不以固定标题、小节数量或分数判断深度。先对照原始内容核对覆盖，正文选择方便读者的结构；只有用户明确采用独立复核或旧严格合同，才另建覆盖表和质量附件。写作细节见[report-guide §三](../report-writing/references/report-guide.md#三报告写作规范模板-v2)，默认流程以根写作指南为准。

> 观点成体系、摘要装不下推理路径时，改用 [qa_chain](../qa_chain/SKILL.md) 的问答链格式（`format: qa_chain`）。

---

## 规则

1. **忠实记录与事实核验分开**：不把转写误识别或嘉宾口误固化成事实。补充引用、数据和背景须实际查证、标明来源，不冒充节目原话。
2. **客观背景信息**（嘉宾履历、节目定位等）若非转写内容，须通过 eacli 查证并标来源，不编造。
3. **沉淀**：只为可复用的新知识或值得续接的问题做必要的 wiki 更新，不为每篇报告自动新建页面。
4. **继续讨论**：用户追问时围绕转写原文 + 已查证事实展开，不引入编造内容。
