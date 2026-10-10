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

- **帆书讲《炎症》：身体出现这些信号，可能是炎症在提醒你！**（2026-08-21 发布，2026-08-25 归档）
  - 来源：B 站 · 帆书视频播客 · 第49期（BV1j18i6VEtn）
  - 形式：讲书/科普对谈（帆书主播[疑为樊登?] × 金博医生[三甲]）
  - 时长：17m50s（1070s）/ 字数：5,445 汉字（raw）/ 5,971 汉字（polished）/ 602 段 / 语速 305 字/min
  - 路径：`reports/2026-08-21_bilibili-fanshu_yanzheng.md`
  - 转录原文：`reports/transcripts/2026-08-21_bilibili-fanshu_yanzheng.transcript.txt`
  - 润色版：`reports/transcripts/2026-08-21_bilibili-fanshu_yanzheng.polished.txt`（按内容话题重组 8 节）
  - 状态：archived（**polished**，Kimi 通读自润 + 官方字幕交叉校验）
  - pipeline：opencli bilibili download → ffmpeg → whisper.cpp + VAD → 官方字幕交叉校验（首次完整走通「字幕亦错」标注流程）
  - 内容：慢性炎症/隐匿炎症/自查三法（C 反应蛋白·腰围·步速握力）/ 炎症×癌症×心血管 / 肥胖与巨噬细胞 / 炎性衰老与阿尔茨海默 / 餐桌抗炎四件套（脂肪·盐·糖·纤维）
  - 新增 concepts：慢性炎症与隐匿的炎症
  - 实体备注：金博医生与帆书主播身份信息不足，暂未建实体页

### 2026-10-09 六集批次（催更→全高优先集处理）

- **起朱楼 184：加息周期的重大投资决策——五步建立海外长债组合**（2026-10-08 发布）
  - 小宇宙单口（大卫翁）1h11m / 2,360 段 / 21,255→17,528 汉字；Razer eacli podcast 转写（173.7s）
  - 路径：`reports/2026-10-08_xiaoyuzhou-qizhulou_2026q3-investment-review.md`（+transcript/polished 三件套）
  - 内容：Q3 账本（+2.5%/YTD -0.5%）｜牛市后期三特征验证｜两轮加息四渠道对比（信用渠道=本轮要害）｜五步决策框架（目标→工具→风险后手→产品→建仓节奏）
  - 降级记录：智谱 web.reader 对该 URL 内容审查误判（1301）→ curl 直拉公开页面（shownotes）；同域名其他集正常
- **屠龙大实话：诺奖得主 Deisseroth 谈《照亮破碎之心》**（2026-10-06，28 期重发+视频）
  - 中英混合访谈 53m31s / 851 段（auto 版）——**英文回答被 whisper 强转破碎中文，两次尝试（zh/auto）均失败**；polished 为"转译大意"整理版
  - 路径：`reports/2026-10-06_xiaoyuzhou-tulong-dashihua_karl-deisseroth.md`
  - 诺奖已核实：Deisseroth+Hegemann+Nagel 共获 2026 诺贝尔生理学或医学奖（web.search nobelprize.org）
  - 新增 entities：[[deisseroth]]；新增 concepts：[[optogenetics]]（接脑科学线）
  - 转写失败经验：中英混合长音频是当前 pipeline 盲区，英文原声细节以视频字幕/原书为准
- **课代表立正 216：Codex 迭代十几轮的网站，Claude 一天作废**（2026-10-05）
  - transistor 短视频音频 14m17s / 610 段；本地 transcribe.py fallback（Razer 白名单不批 share.transistor.fm）
  - 路径：`reports/2026-10-05_rss-kedaibiao-lizheng_codex-claude.md`
  - 内容：Cowork→文档→Code 工作流（Document first）｜社区地图 n(n-1)/2 链接具象化｜"问问立正" Agentic RAG｜叙事主权/自留地｜摩托车垫片故事（高手不搞 fancy）
- **硅谷101 E255：榜单 99 分用户没感觉——张阔 107 任务评测**（2026-10-08）
  - fireside RSS 46m13s / 1,669 段；本地 transcribe.py fallback（白名单不批 aphid.fireside.fm）
  - 路径：`reports/2026-10-08_rss-guigu101_e255-zhangkuo.md`
  - 内容：Agent=Model×Harness×Context（乘法）｜107-task 开源 bench（最前沿模型无人干预 61%）｜帕累托路由 1/3 成本（3.69 vs 9+ 美元）｜商业 AGI 定义｜"不挂 means nothing"
- **十字路口：AI 无限，人生有限——山音与 KK**（2026-10-08）
  - 小宇宙对谈 1h05m / 2,805 段；Razer eacli podcast
  - 路径：`reports/2026-10-08_xiaoyuzhou-crossing_kk-shanyin.md`
  - 内容：不写剧本的电影（0.5→1）｜"眉头一皱"判断力｜"在现场"不可替代｜做 AI 没有任何借口｜Seedance/Nano Banana 版本线｜游戏时刻前夜｜中国创作者定义电影语言的窗口
  - 修正量大：Seedance 有 8+ 种误写、CapCut 5+ 种；版本号（2.0/2.5）含推测
- **知行小酒馆 E253：会思考的沙子与杀人的沙子——李治霖**（2026-10-09）
  - 小宇宙对谈 1h18m / 3,153 段 / 27,215→6,388 汉字；Razer eacli podcast
  - 路径：`reports/2026-10-09_xiaoyuzhou-zhixing-xiaojiuguan_e253-ai-good.md`
  - 内容：83% 劳动人口未用 AI｜6500 亿 AI capex vs 3040 亿消除极端贫困｜有效公益账本（白内障 3-5 千/蚊帐 3-5 千美元/先心病 3.8 万）｜恩格斯停顿 AI 版｜村医 20%→80%｜Max Roser 三句话
  - 关键修正：李治霖（6 种同音误写）｜发蚊帐（原转写"发文章"）｜转经（"赚金"）｜占了一卦

**本批 pipeline 记录**：Razer eacli podcast 成功 4 集（小宇宙域名）；本地 transcribe.py fallback 2 集（transistor/fireside 域名不在 Razer 白名单）；一集瞬时失败重试成功；中英混合音频转写质量不可用（屠龙期）。索引状态已更新 5 档（qizhulou/tulong-dashihua/guigu101/crossing/zhixing-xiaojiuguan/kedaibiao-lizheng）。


### 2026-10-09（二）中优先批次：4 项全处理

- **课代表立正·职业方法论九讲（存量专题）**：立正说 217/218/221-225 + 对话 327/328/329（2022-03~2023-08，transistor feed 回灌的存量视频片段，10 集批量本地转写 1208 段）
  - 路径：`reports/2026-10-09_rss-kedaibiao-lizheng_career-methods-series.md`（cross_episode；transcripts 前缀 `lizheng-career-series_` 共 10 件）
  - 内容：7+1 职业选择框架/AlphaGo 决策法/认知余裕（90% 工作无意义）/失败的期权/L6→L7 的 2-3 年/Simple vs Easy 榨汁机/不当韭菜三原则/大学生三问/correlation→causality/网红经济学
  - 关键修正：阿富汗/After Goal→AlphaGo；学书界→学术界；企号→起号
- **听懂涨声：父子坦白局**（2026-10-09，冉总+17 岁 Warren，1h36m/3307 段）
  - 路径：`reports/2026-10-09_xiaoyuzhou-tingdong-zhangsheng_father-son-money.md`
  - 内容：5 万公里移动课堂/建筑师范本第一曲线/杀死昨天的自己/禁止即诱惑/礼物股/应试四反/十分之一幸存律/原生家庭论
  - 关键修正：阮总→冉总；适应率→市盈率；Wordnos→Ordinals；八字真言[?]未还原
- **说医解药 Vol.91：银鳕鱼汞争议**（2026-10-08，外博，53m/1468 段）
  - 路径：`reports/2026-10-08_xiaoyuzhou-shuoyi-jieyao_vol91-cod-mercury.md`
  - 内容：三种汞毒性阶梯/血汞阈值/FDA 0.15-0.46 分档数学/鳕鱼命名史/油鱼骗局/Omega-3 十倍差
  - 系统性误识别：汞→拱/肱/股/肿、鳕→血/雪（全文数百处）
- **大小马 V95：中美新拐点**（2026-10-08，+电丸 AK，1h53m/4023 段）
  - 路径：`reports/2026-10-08_xiaoyuzhou-daxiaoma-keji_v95-china-us.md`
  - 内容：失业率反常识/出海三不碰/聚合 vs 单点/AI 眼镜三数量级增量/苹果 Security Enclave 长期主义/Muse 与 APP 时代崩塌/World Labs 收购/判断力保值
  - **pipeline 事件**：transcript 202KB 超 eacli pull 上限 → invoke 远程 split 三片合并取回（已验证无损）


### 工具：sync_index_status.py（2026-10-09 新增）

- **用途**：把 `reports/*.md` frontmatter `source_url`（100% 覆盖）回填到 `wiki/show-indexes/*.md` 状态列，打通「已做过」记录。起因：催更推荐连续把 3 个已做过的集当新集推荐（乱翻书 275 / 42章经浩哲 / 张帆 FDE）——事实源一直在 reports 里，只是没与索引打通。
- **契约**：幂等；匹配到的行统一写「✅ 已处理（日期 slug）」；未匹配的行不动（保留人工状态）；stdout 附「报告 URL 不在精选索引」清单（bilibili 等源正常，域名变更如 sv101.net→fireside、latepost↔xiaoyuzhou 双域也会出现在此，人工核）。
- **接入点**：AGENTS.md 催更流程第 1 步 + 报告自检清单（fetch_show_indexes 刷新按 guid/链接双键保留状态列，✅ 不会丢）。

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
- 慢性炎症与隐匿的炎症概念（详见 2026-08-21 帆书视频播客 49 期报告 + concepts/chronic-inflammation.md）

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

*Last updated: 2026-08-25 (added 帆书视频播客 49《炎症》讲书期 + 1 concept；官方字幕交叉校验流程首次完整走通)*
