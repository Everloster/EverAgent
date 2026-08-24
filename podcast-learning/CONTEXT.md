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
  - 路径：`reports/2026-06-18_xiaoyuzhou-mingjing-diandian_wangxiaochuan.md`
  - 转录原文：`reports/transcripts/2026-06-18_xiaoyuzhou-mingjing-diandian_wangxiaochuan.transcript.txt`
  - 状态：archived（**polish 失败**，标点稀疏）

- **三年行业吃肉榜/爆亏榜大合集（2023-2025）**（2026-06-20）
  - 来源：B 站 · CLS同学 · BV1NHJF6oE8m
  - 嘉宾：—（UP 主单口深度分析）
  - 时长：1h2m53s / 字数：21,953
  - 路径：`reports/2026-06-20_bilibili-cls-tongxue_hangye-bangdan.md`
  - 转录原文：`reports/transcripts/2026-06-20_bilibili-cls-tongxue_hangye-bangdan.transcript.txt`
  - 润色版：`reports/transcripts/2026-06-20_bilibili-cls-tongxue_hangye-bangdan.polished.txt`（Claude 自润，50+ 处 Whisper 误识别修正）
  - 状态：archived（**polished**，Claude (MiniMax-M3) 自润）
  - 内容：覆盖 30 个一级/二级行业、3 年 60 个 TOP5 排名 + 大量上市公司具体数据点

- **Vol.30-32 三期高质播客综合收听笔记**（2026-06-21，report_type: cross_episode）
  - 来源：小宇宙 3 期节目（综合精读）
  - 3 期组合：
    - **Vol.30**：What's Next 科技早知道 · Sahil Lavingia · 一人公司 · 2026-06-09
    - **Vol.31**：声东击西 #378 · 塔利班关闭学校后阿富汗女孩的四年 · 2026-01-29
    - **Vol.32**：后互联网时代的乱弹 · 第 166 期 · 香会 + X 新生态 + 教育 · 2026-06-06
  - 路径：`reports/2026-06-21_xiaoyuzhou-multi_notes.md`
  - 转录：`reports/transcripts/2026-06-21_xiaoyuzhou-multi_notes.transcript.txt`（**占位**）
  - 状态：archived（**transcript 未取得**，报告基于小宇宙 show notes + Apple Podcasts 节目描述 + 多源 web_search 合成）
  - 新增 entities：Sahil Lavingia、Gumroad、Patreon、丁教 Diane、Lina（化名）、Sophia（化名）、徐涛、庄表伟、声动活泼、声湃 WavPub
  - 新增 concepts：一人公司、vibe coding、小而美、创作者经济工具型vs平台型、阿富汗女性教育禁令、化名报道、后互联网时代、平台算法治理、香格里拉对话、AI 时代的教育挑战

- **读书：4种配速，取景框，人是滤器，冲刷神经网络 —— 明镜与李继刚关于读书方法论的深度对话**（2026-07-09）
  - 来源：小宇宙 · 明镜与点点（面基）· 单期
  - 嘉宾：李继刚（43 AI · 即刻）—— 主持人明镜 + 嘉宾李继刚 **对谈节目**（非单口独白）
  - 时长：1h54min（6815s）/ 字数：35,430 汉字（raw）/ 35,897 汉字（polished）/ 5372 段 / 语速 312 字/min
  - 路径：`reports/2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang.md`
  - 转录原文：`reports/transcripts/2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang.transcript.txt`（5372 段，237 KB）
  - 润色版：`reports/transcripts/2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang.polished.txt`（按 shownotes 36 章节重组，无时间戳，43 KB）
  - 状态：archived（**polished**，Claude (MiniMax-M3) 自润 + 按章节重构）
  - pipeline：yt-dlp → ffmpeg mp3 → whisper.cpp / ggml-large-v3 / Metal 加速 / 7m30s 墙钟 → WebFetch 拉小宇宙 shownotes（修正嘉宾 + 36 章节时间戳 + 17 本书单）→ Claude 按章节重组成 polished
  - 内容：F × X = Fx 公式 / 读书的四种配速 / 找好书的四种方法 / 影子之书 / AI 时代读书方法论 / 43talks 闭门会 / "人是过滤器" / 预制菜同构讨论 / AI 魔法对魔法 / 17 本引用书 / 守 破 离 / 分辨率 / 一念境转
  - 新增 entities：李继刚（明镜已有）
  - 新增 concepts：F × X = Fx 公式、读书的四种配速
  - 重要修正：whisper 把"李继刚"听成"李金刚/李吉刚"、把对谈误判为单口独白；依 shownotes 修正

- **重估一切，文艺复兴——2026H1 AI行业观察**（2026-07-17）
  - 来源：小宇宙 · 屠龙之术 · 单期
  - 嘉宾：—（庄明浩单口；CSDN 大会 45min 演讲重录版，PPT 76 页）
  - 时长：54m37s（3277s）/ 字数：14,591 汉字（raw）/ 13,996 汉字（polished）/ 1,973 段 / 语速 267 字/min
  - 路径：`reports/2026-07-17_xiaoyuzhou-tulong-zhishu_2026h1-ai-review.md`
  - 转录原文：`reports/transcripts/2026-07-17_xiaoyuzhou-tulong-zhishu_2026h1-ai-review.transcript.txt`（1,973 段，93 KB）
  - 润色版：`reports/transcripts/2026-07-17_xiaoyuzhou-tulong-zhishu_2026h1-ai-review.polished.txt`（shownotes 69 时间戳归并 12 节 56 小节，无时间戳）
  - 状态：archived（**polished**，Kimi 自润 + 按章节重构）
  - pipeline：yt-dlp → whisper.cpp / ggml-large-v3 / Metal → curl 抓 episode 页 JSON-LD/__NEXT_DATA__ 解析 shownotes → Kimi 通读 + 按章节重组
  - 内容：文艺复兴映射框架 / 美第奇的账本（CAPEX 三年低估 vs 收入只够折旧）/ Anthropic 反超 OpenAI / 中美壁画-版画双路线 / 世界模型三分类 / Agent 元年（Codex=新 ChatGPT、Claude Code 时刻）/ 治理三对博弈 / token maxxing 证伪 / 第四支柱
  - 新增 entities：庄明浩
  - 新增 concepts：文艺复兴映射框架、美第奇的账本、Agent 元年、世界模型三分类、第四支柱
  - 重要修正：whisper 系统性误识别 40+ 处（KPS/CBS→CAPEX、视野模型→世界模型、美利奇→美第奇、Cloud Code→Claude Code 等）；30+ 处不确定项标 [?]

- **人到中年仨账户：现金流、肌肉、睡眠**（2026-07-13）
  - 来源：小宇宙 · 面基 · 单期
  - 嘉宾：—（老钱单口；35 岁，预习自己与 60 岁母亲的中年）
  - 时长：72m06s（4326s）/ 字数：19,509 汉字（raw）/ 19,166 汉字（polished）/ 2,414 段 / 语速 271 字/min
  - 路径：`reports/2026-07-13_xiaoyuzhou-mingjing-diandian_midlife-accounts.md`
  - 转录原文：`reports/transcripts/2026-07-13_xiaoyuzhou-mingjing-diandian_midlife-accounts.transcript.txt`（2,414 段，114 KB）
  - 润色版：`reports/transcripts/2026-07-13_xiaoyuzhou-mingjing-diandian_midlife-accounts.polished.txt`（shownotes ~40 时间戳归并 9 节 31 小节，无时间戳）
  - 状态：archived（**polished**，Kimi 自润 + 按章节重构）
  - pipeline：transcribe.py（yt-dlp + whisper.cpp）→ curl 抓 episode 页确认节目身份 → FetchURL 拉 shownotes → Kimi 通读 + 按章节重组
  - 内容：中年三本账框架 / 蓄水池模型与人力资本久期 / 订阅制支出与社会 SaaS 化 / 力量训练=退休储蓄（《超越百岁》）/ 蛋白质账 / 控制论看睡眠 / 睡眠三状态与温度曲线 / Eat, Sleep, Gym, Invest.
  - 新增 entities：老钱
  - 新增 concepts：中年三本账、订阅制支出、力量训练=退休储蓄、控制论看睡眠
  - 重要修正：**节目官方名确认为「面基」**（episode 页 podcast.title），即本库此前所称"明镜与点点"；老钱与"明镜"关系待确认；whisper 系统性误识别 40+ 处（面积→面基、生物中→生物钟、Aidsleep→Eight Sleep 等）

- **对游凯超3小时访谈：开源Infra、和模型Co-design、"如果vLLM失败，我们会后悔一辈子"**（2026-07-28 发布，2026-08-22 归档）
  - 来源：小宇宙 · 张小珺Jùn｜商业访谈录（语言即世界工作室）· Vol.148 —— **新节目 slug：zhangxiaojun**
  - 嘉宾：游凯超（Inferact 联创兼首席科学家、vLLM 核心维护者，清华本博）—— 主持张小珺 × 嘉宾**对谈**
  - 时长：3h00m26s（10826s）/ 字数：53,373 汉字（raw）/ 49,568 汉字（polished）/ 6,120 段 / 语速 296 字/min
  - 路径：`reports/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.md`
  - 转录原文：`reports/transcripts/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.transcript.txt`（6,120 段）
  - 润色版：`reports/transcripts/2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao.polished.txt`（按 shownotes 8 章节重组，无时间戳）
  - 状态：archived（**polished**，Kimi 8 章并行分章润色 + 组装）
  - pipeline：transcribe.py（yt-dlp + whisper.cpp，约 16min 墙钟）→ episode 页 JSON-LD + FetchURL shownotes（8 章节）→ 8 章并行 agent 润色 → 组装
  - 内容：vLLM 三年三级跳（SOSP 低分过线 → 开源 → PyTorch 基金会 → Inferact 1.5 亿美元种子轮）/ 仁慈的独裁者分级治理 / AI slop 与善意假设崩塌 / 模型-Infra-硬件 co-design / hardware lottery / DeepSeek 双料模式 / 投机解码谱系（EAGLE/MTP/DFlash/DSpark）/ Token vs 电力 / 开源模型会赢 / 上下文百万级 hot take
  - 新增 entities：游凯超、Inferact
  - 新增 concepts：模型×Infra×硬件 co-design、hardware lottery（系统彩票）
  - 重要修正：whisper 系统性误识别约 300 处（VLM/VM/为我们→vLLM 70+、杨斯多伊克→Ion Stoica 20+、归机→硅基、推力引擎→推理引擎、语言集世界→语言即世界 等）；约 40 处 [?]；嘉宾口述两处事实存疑（OpenSSH 段实为 OpenSSL Heartbleed；ALiBi 表述）
  - **跨项目联动**：与 ai-learning 的 vLLM 源码级学习线互为表里（概念页 `ai-learning/wiki/concepts/vllm_v1_architecture.md`）

- **对话盛颖：xAI，Infra的浪漫，SGLang，开源，平权与「甄嬛传」**（2026-08-04 发布，2026-08-23 归档）
  - 来源：硅谷101 · E247（Fireside RSS 音频直链，sv101.net/260）—— **首个 RSS 直链来源**（platform=rss）
  - 嘉宾：盛颖（RadixArk 联创&CEO、SGLang 发起人、xAI 前推理团队负责人；上海交大 ACM→哥大→斯坦福 PhD）—— 陈茜采访
  - 时长：1h46m26s（6387s）/ 字数：34,164 汉字（raw）/ 33,726 汉字（polished）/ 5,578 段 / 语速 321 字/min
  - 路径：`reports/2026-08-04_rss-guigu101_shengying.md`
  - 转录原文：`reports/transcripts/2026-08-04_rss-guigu101_shengying.transcript.txt`
  - 润色版：`reports/transcripts/2026-08-04_rss-guigu101_shengying.polished.txt`（按 shownotes 12 章节重组，无时间戳）
  - 状态：archived（**polished**，Kimi 12 章并行分章润色 + 组装）
  - pipeline：RSS 拿直链 → yt-dlp → whisper.cpp + **--vad** → Fireside shownotes → 12 章并行润色
  - **重大踩坑**：首跑无 VAD 时 whisper 循环幻觉报废约 1/3 内容，VAD 重跑恢复；教训入 AGENTS.md 已知局限 #5
  - 内容：SGLang 发起史 / RadixAttention / 与 vLLM 的时间轴分野 / day zero 兼容 / infra 即产品 / xAI v1.0 / Ion Stoica / RadixArk 1 亿美元种子（Accel）/ 开源是空气 / 平权
  - 新增 entities：盛颖、RadixArk、SGLang
  - 新增 concepts：RadixAttention
  - 重要修正：「Axial/Excel 领投」→ Accel（依官方新闻稿）；简介误写清华 → 实为上海交大 ACM 班（以转写为准）；约 200 处误识别修正 + 60 处 [?]
  - **跨项目联动**：与游凯超期构成开源推理引擎双子星对照；链接 ai-learning vLLM 概念页

- **刘方奇教授：肠癌越来越年轻，确诊后先别急着手术！**（2026-08-24 发布并归档）
  - 来源：小宇宙 · 菠萝健康派 · vol.122（周更扫描 cron 捕获的新集）
  - 嘉宾：刘方奇（复旦大学附属肿瘤医院大肠外科副主任医师，师从蔡三军，从业 16 年）—— 主播李治中（菠萝）对谈
  - 时长：1h21m34s（4894s）/ 字数：26,467 汉字（raw）/ 26,512 汉字（polished）/ 3,358 段 / 语速 324 字/min
  - 路径：`reports/2026-08-24_xiaoyuzhou-boluo-jiankang_liufangqi.md`
  - 转录原文：`reports/transcripts/2026-08-24_xiaoyuzhou-boluo-jiankang_liufangqi.transcript.txt`
  - 润色版：`reports/transcripts/2026-08-24_xiaoyuzhou-boluo-jiankang_liufangqi.polished.txt`（按 shownotes 10 章节重组）
  - 状态：archived（**polished**，Kimi 10 章并行分章润色；VAD 转写一次通过）
  - 内容：遗传性肠癌（Lynch/FAP/PJS、胚系检测、三代试管生殖阻断）/ 肠癌年轻化与 45 岁筛查线 / 保肛与造口去污名化 / 新辅助治疗与观察等待（dMMR 三年 DFS 100% 自述）/ 肛指检查 1/3 可摸到 / 外科医生的温度
  - 新增 entities：刘方奇、李治中（菠萝）
  - 新增 concepts：遗传性肠癌、新辅助治疗与观察等待
  - 重要修正：医学术语系统性误识别约 200 处（邻居综合症→Lynch、DMMA→dMMR、心腹中→新辅助、细肉→息肉、灶口→造口、宝刚→保肛 等）；约 40 处 [?]；证据纪律：医学数字为嘉宾自述口径，报告含「不构成医疗建议」声明

## ⚠️ 边界（防幻觉）

以下主题已有报告，禁止重复生成：

- 中年三本账（现金账/肉身账/睡眠账）/ 订阅制支出 / 力量训练=退休储蓄 / 控制论看睡眠（详见 2026-07-13 面基报告 + concepts/midlife-three-accounts.md 等 4 页）
- 老钱 / 面基 实体（详见 entities/lao-qian.md；节目官方名「面基」= 本库此前所称"明镜与点点"，老钱与"明镜"关系待确认）

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
- 屠龙之术 2026H1 行业观察：文艺复兴映射框架 / 美第奇的账本（CAPEX 泡沫之辩）/ Agent 元年 / 世界模型三分类 / 第四支柱（详见 2026-07-17 报告 + concepts/renaissance-revaluation.md 等 5 页）
- 庄明浩 / 屠龙之术 实体（详见 entities/zhuang-minghao.md；注意与 B 站屠龙博士 tulong-boshi 区分）
- vLLM 项目口述史 / 仁慈的独裁者治理 / Inferact 创业 / 模型-Infra co-design / hardware lottery（详见 2026-07-28 游凯超期 + entities/you-kaichao.md、entities/inferact.md + concepts/model-infra-codesign.md、hardware-lottery.md）
- 游凯超 / Inferact 实体（详见 entities/）
- 盛颖 / RadixArk / SGLang 实体、RadixAttention 概念（详见 2026-08-04 硅谷101 E247 报告 + entities/sheng-ying.md、radixark.md、sglang.md + concepts/radix-attention.md）
- 刘方奇 / 李治中（菠萝）实体、遗传性肠癌 / 新辅助治疗与观察等待概念（详见 2026-08-24 菠萝健康派 vol.122 报告 + entities/liu-fangqi.md、li-zhizhong.md + concepts/hereditary-colorectal-cancer.md、neoadjuvant-watch-and-wait.md）

---

## 学习路线

（待规划）

---

## 参考资源

- 转录工具：本地 `scripts/transcribe.py`（whisper.cpp / ggml-large-v3）
- 报告索引：reports/
- 知识图谱：wiki/index.md
- 选题库：[[wiki/curated-podcasts.md]]（51 档精选播客）+ `wiki/show-indexes/`（全量单集索引，周更 cron 刷新；脚本 `scripts/fetch_show_indexes.py`）
- 研究方法论：../METHODOLOGY.md

---

*Last updated: 2026-08-24 (added 菠萝健康派 vol.122 刘方奇期 + 2 entities + 2 concepts；本期由周更 cron 捕获)*
