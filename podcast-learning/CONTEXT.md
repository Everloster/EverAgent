# podcast-learning Context

> 项目：播客内容学习与知识提取
> Agent：PodcastAgent
> 创建时间：2026-06-18

---

## 项目概述

跨领域播客内容学习库。聚焦三个维度：内容价值 × 关键人物 × 概念图谱。

报告类型（frontmatter `report_type`）：
- episode_summary（单期总结）
- cross_episode（跨期共性 / 系列专题）
- concept_tracking（单一概念 / 人物纵向追踪）

转录方式：**本地** `scripts/transcribe.py`（yt-dlp 下载 + whisper.cpp，Metal 加速，全程离线）。依赖见 SETUP.md。

---

## 已有报告

- **Vol.29 对话王小川：造医生，战豆包，与无尽的 AI 非共识**（2026-06-18）
  - 来源：小宇宙 · 明镜与点点 · Vol.29
  - 嘉宾：王小川（百川智能创始人）
  - 时长：92m45s / 字数：19,983
  - 路径：`reports/2026-06-18_xiaoyuzhou_vol29_wangxiaochuan.md`
  - 转录原文：`reports/transcripts/2026-06-18_xiaoyuzhou_vol29_wangxiaochuan.transcript.txt`
  - 状态：archived（**polish 失败**，标点稀疏）

- **三年行业吃肉榜/爆亏榜大合集（2023-2025）**（2026-06-20）
  - 来源：B 站 · CLS同学 · BV1NHJF6oE8m
  - 嘉宾：—（UP 主单口深度分析）
  - 时长：1h2m53s / 字数：21,953
  - 路径：`reports/2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue.md`
  - 转录原文：`reports/transcripts/2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue.transcript.txt`
  - 润色版：`reports/transcripts/2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue.polished.txt`（Claude 自润，50+ 处 Whisper 误识别修正）
  - 状态：archived（**polished**，Claude (MiniMax-M3) 自润）
  - 内容：覆盖 30 个一级/二级行业、3 年 60 个 TOP5 排名 + 大量上市公司具体数据点

- **Vol.30-32 三期高质播客综合收听笔记**（2026-06-21，report_type: cross_episode）
  - 来源：小宇宙 3 期节目（综合精读）
  - 3 期组合：
    - **Vol.30**：What's Next 科技早知道 · Sahil Lavingia · 一人公司 · 2026-06-09
    - **Vol.31**：声东击西 #378 · 塔利班关闭学校后阿富汗女孩的四年 · 2026-01-29
    - **Vol.32**：后互联网时代的乱弹 · 第 166 期 · 香会 + X 新生态 + 教育 · 2026-06-06
  - 路径：`reports/2026-06-21_xiaoyuzhou_vol30-32_收听笔记.md`
  - 转录：`reports/transcripts/2026-06-21_xiaoyuzhou_vol30-32.transcript.txt`（**占位**）
  - 状态：archived（**transcript 未取得**，报告基于小宇宙 show notes + Apple Podcasts 节目描述 + 多源 web_search 合成）
  - 新增 entities：Sahil Lavingia、Gumroad、Patreon、丁教 Diane、Lina（化名）、Sophia（化名）、徐涛、庄表伟、声动活泼、声湃 WavPub
  - 新增 concepts：一人公司、vibe coding、小而美、创作者经济工具型vs平台型、阿富汗女性教育禁令、化名报道、后互联网时代、平台算法治理、香格里拉对话、AI 时代的教育挑战

- **读书：4种配速，取景框，人是滤器，冲刷神经网络 —— 明镜与李继刚关于读书方法论的深度对话**（2026-07-09）
  - 来源：小宇宙 · 明镜与点点（面基）· 单期
  - 嘉宾：李继刚（43 AI · 即刻）—— 主持人明镜 + 嘉宾李继刚 **对谈节目**（非单口独白）
  - 时长：1h54min（6815s）/ 字数：35,430 汉字（raw）/ 35,897 汉字（polished）/ 5372 段 / 语速 312 字/min
  - 路径：`reports/2026-07-09_xiaoyuzhou_6a4b22ad_lijigang.md`
  - 转录原文：`reports/transcripts/2026-07-09_xiaoyuzhou_6a4b22ad_lijigang.transcript.txt`（5372 段，237 KB）
  - 润色版：`reports/transcripts/2026-07-09_xiaoyuzhou_6a4b22ad_lijigang.polished.txt`（按 shownotes 36 章节重组，无时间戳，43 KB）
  - 状态：archived（**polished**，Claude (MiniMax-M3) 自润 + 按章节重构）
  - pipeline：yt-dlp → ffmpeg mp3 → whisper.cpp / ggml-large-v3 / Metal 加速 / 7m30s 墙钟 → WebFetch 拉小宇宙 shownotes（修正嘉宾 + 36 章节时间戳 + 17 本书单）→ Claude 按章节重组成 polished
  - 内容：F × X = Fx 公式 / 读书的四种配速 / 找好书的四种方法 / 影子之书 / AI 时代读书方法论 / 43talks 闭门会 / "人是过滤器" / 预制菜同构讨论 / AI 魔法对魔法 / 17 本引用书 / 守 破 离 / 分辨率 / 一念境转
  - 新增 entities：李继刚（明镜已有）
  - 新增 concepts：F × X = Fx 公式、读书的四种配速
  - 重要修正：whisper 把"李继刚"听成"李金刚/李吉刚"、把对谈误判为单口独白；依 shownotes 修正

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
- F × X = Fx 公式 / 读书的四种配速 / 人是过滤器（详见 2026-07-09 明镜报告 + concepts/fx-formula.md + concepts/reading-four-paces.md）
- 明镜 / 43talks / 影子之书（详见 2026-07-09 明镜报告 + entities/mingjing.md）

---

## 学习路线

（待规划）

---

## 参考资源

- 转录工具：本地 `scripts/transcribe.py`（whisper.cpp / ggml-large-v3）
- 报告索引：reports/
- 知识图谱：wiki/index.md
- 研究方法论：../METHODOLOGY.md

---

*Last updated: 2026-07-09 (added 2026-07-09 明镜读书方法论长谈 + 2 concepts + 1 entity；whisper.cpp 后端首次实战通过 7m30s/113min=15× 实时)*
