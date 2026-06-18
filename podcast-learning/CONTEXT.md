# podcast-learning Context

> 项目：播客内容学习与知识提取
> Agent：PodcastAgent
> 创建时间：2026-06-18

---

## 项目概述

跨领域播客内容学习库。聚焦三个维度：内容价值 × 关键人物 × 概念图谱。

支持格式：
- text_analysis（单期精读）
- knowledge_report（跨期共性 / 系列专题）
- concept_report（单一概念 / 人物纵向追踪）

转录上游：agent-reach xiaoyuzhou（Groq Whisper large-v3，zh prompt 加标点）

---

## 已有报告

### text_analyses/

- **Vol.29 对话王小川：造医生，战豆包，与无尽的 AI 非共识**（2026-06-18）
  - 来源：小宇宙 · 明镜与点点 · Vol.29
  - 嘉宾：王小川（百川智能创始人）
  - 时长：92m45s
  - 字数：19,983
  - 路径：`reports/text_analyses/2026-06-18_xiaoyuzhou_vol29_wangxiaochuan.md`
  - 状态：archived（**polish 失败**，标点稀疏）

### knowledge_reports/

（暂无）

### concept_reports/

（暂无）

---

## ⚠️ 边界（防幻觉）

以下主题已有报告，禁止重复生成：

- 百川 M4 模型（详见 Vol.29 报告 + concepts/baichuan-m4.md）
- 百小一 AI 家庭医生（详见 Vol.29 报告 + concepts/baixiao-yi-ai-doctor.md）
- 生命模型（详见 Vol.29 报告 + concepts/life-model.md）
- 非共识 AI 路线（详见 Vol.29 报告 + concepts/non-consensus-ai.md）
- 医疗供给侧改革（详见 Vol.29 报告 + concepts/medical-supply-side-reform.md）
- 王小川 / 百川智能 实体（详见 entities/）

---

## 学习路线

（待规划）

---

## 参考资源

- 转录工具：agent-reach xiaoyuzhou
- 报告索引：reports/text_analyses/
- 知识图谱：wiki/index.md
- 技能模板：docs/SKILL_TEMPLATES.md

---

*Last updated: 2026-06-18*
