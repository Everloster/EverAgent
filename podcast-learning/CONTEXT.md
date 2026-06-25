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

- **三年行业吃肉榜/爆亏榜大合集（2023-2025）**（2026-06-20）
  - 来源：B 站 · CLS同学 · BV1NHJF6oE8m
  - 嘉宾：—（UP 主单口深度分析）
  - 时长：1h2m53s
  - 字数：21,953
  - 路径：`reports/text_analyses/2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue.md`
  - 转录原文：`reports/transcripts/2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue.transcript.txt`
  - 润色版：`reports/transcripts/2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue.polished.txt`（Claude 自润，50+ 处 Whisper 误识别修正）
  - 状态：archived（**polished**，Claude (MiniMax-M3) 自润；跳过 Groq Llama 3.3 70B）
  - 内容：覆盖 30 个一级/二级行业、3 年 60 个 TOP5 排名 + 大量上市公司具体数据点
  - 适用研究：行业轮动 / 出海制造业 / AI 算力链 / 政策红利捕获 / 周期反转案例

- **Vol.30-32 三期高质播客综合收听笔记**（2026-06-21）
  - 来源：小宇宙 3 期节目（综合精读）
  - 3 期组合：
    - **Vol.30**：What's Next 科技早知道 · Sahil Lavingia · 一人公司 · 2026-06-09
    - **Vol.31**：声东击西 #378 · 塔利班关闭学校后阿富汗女孩的四年 · 2026-01-29
    - **Vol.32**：后互联网时代的乱弹 · 第 166 期 · 香会 + X 新生态 + 教育 · 2026-06-06
  - 路径：`reports/text_analyses/2026-06-21_xiaoyuzhou_vol30-32_收听笔记.md`
  - 转录：`reports/transcripts/2026-06-21_xiaoyuzhou_vol30-32.transcript.txt`（**占位**）
  - 状态：archived（**transcript 未取得**，本 session Bash 工具被拒，无法调用 `agent-reach xiaoyuzhou transcribe.sh`；报告基于小宇宙 show notes + Apple Podcasts 节目描述 + 声动活泼官方宣传 + 多源 web_search 合成）
  - 主题覆盖：学术/科技 + 商业（Vol.30）/ 心理学+人文+国际（Vol.31）/ 工程+开发者文化（Vol.32）
  - 新增 entities：Sahil Lavingia、Gumroad、Patreon、丁教 Diane、Lina（化名）、Sophia（化名）、徐涛、庄表伟、声动活泼、声湃 WavPub
  - 新增 concepts：一人公司、vibe coding、小而美、创作者经济工具型vs平台型、阿富汗女性教育禁令、化名报道、后互联网时代、平台算法治理、香格里拉对话、AI 时代的教育挑战

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
- 三年中国行业吃肉榜/衰落榜（详见 BV1NHJF6oE8m 报告 + entities/cls-tongxue.md）
- 一人公司 / vibe coding / 小而美 / Gumroad vs Patreon（详见 Vol.30-32 报告 + concepts/one-person-company.md 等）
- 阿富汗女性教育禁令 / 化名报道（详见 Vol.30-32 报告 + concepts/afghan-women-education-ban.md 等）
- 后互联网时代 / 平台算法治理 / 香格里拉对话（详见 Vol.30-32 报告 + concepts/post-internet-era.md 等）

---

## 学习路线

（待规划）

---

## 参考资源

- 转录工具：agent-reach xiaoyuzhou
- 报告索引：reports/text_analyses/
- 知识图谱：wiki/index.md
- 研究方法论：../METHODOLOGY.md

---

*Last updated: 2026-06-21 (added Vol.30-32 三期综合收听笔记 + 10 concepts + 10 entities；transcript 占位待补)*
