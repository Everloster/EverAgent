# Wiki Log

> Append-only。禁止修改历史条目。

## [2026-06-18] init | scaffold
- 初始化项目骨架（podcast-learning v1.0，PodcastAgent）

## [2026-06-18] ingest | xiaoyuzhou
- 来源：小宇宙 · 明镜与点点 Vol.29
- 嘉宾：王小川（百川智能创始人）
- 标题：对话王小川：造医生，战豆包，与无尽的 AI 非共识
- 时长：92m45s · 转录：19,983 字（Whisper large-v3, zh, 未润色）
- 报告：[[2026-06-18_xiaoyuzhou-mingjing-diandian_wangxiaochuan]]
- 新增 entities: 王小川、百川智能
- 新增 concepts: 百川 M4、百小一、生命模型、非共识 AI、医疗供给侧改革
- 失败/限制：Llama 3.3 70B polish 因 Groq TPM 12,000 限速失败，标点稀疏；详见报告 Limitations

## [2026-06-20] ingest | bilibili
- 来源：B 站 · CLS同学 · BV1NHJF6oE8m
- 标题：三年行业吃肉榜/爆亏榜大合集（2023-2025）
- 时长：1h2m53s · 转录：21,953 字（Whisper large-v3 zh, **已用 Claude (MiniMax-M3) 自润** — 跳过 Groq Llama 3.3 70B，见 self-polish memory）
- 报告：[[2026-06-20_bilibili-cls-tongxue_hangye-bangdan]]
- 新增 entities: CLS 同学
- 新增 concepts：（未单独建页，详见报告"关键观点"7 节）
- pipeline: opencli bilibili summary → yt-dlp mp4 → ffmpeg mp3 → Groq Whisper large-v3 → Claude (MiniMax-M3) 自润（分段 + 标点 + 50+ 处误识别修正）
- 特殊处理：bili-cli audio download 内部失败（NoneType.value bug），绕道 opencli bilibili download 成功；非小宇宙来源，AGENTS.md 协议为 podcast-first 故标注为"适配执行"
- 自润修正样本：吸音→SHEIN / 陈明纸业→晨鸣纸业 / 携行通用→钱江通用 / 一春理矿→宜春锂矿 / 耳濒资博→尔滨/淄博 / 中东收入陷阱→中等收入陷阱 等 50+ 条，详见 polished.txt 末尾清单

## [2026-06-21] ingest | xiaoyuzhou
- 来源：小宇宙 3 期节目（综合精读）
- 3 期组合：
  - **Vol.30**：What's Next 科技早知道 · Sahil Lavingia · 一人公司 · 2026-06-09
  - **Vol.31**：声东击西 #378 · 塔利班关闭学校后阿富汗女孩的四年 · 2026-01-29
  - **Vol.32**：后互联网时代的乱弹 · 第 166 期 · 香会 + X 新生态 + 教育 · 2026-06-06
- 报告：[[2026-06-21_xiaoyuzhou-multi_notes]]
- 状态：archived（**transcript 未取得**，transcript_chars: 0；本 session Bash 工具被持续拒绝，无法调用 `agent-reach xiaoyuzhou transcribe.sh` 拉取音频）
- 报告合成源：小宇宙 show notes + Apple Podcasts 节目描述 + 声动活泼官方宣传 + 豆瓣播客元数据 + 多源 web_search 交叉印证
- 新增 entities（10 个）：Sahil Lavingia、Gumroad、Patreon、丁教 Diane、Lina（化名）、Sophia（化名）、徐涛、庄表伟、声动活泼、声湃 WavPub
- 新增 concepts（10 个）：一人公司、vibe coding、小而美、创作者经济工具型vs平台型、阿富汗女性教育禁令、化名报道、后互联网时代、平台算法治理、香格里拉对话、AI 时代的教育挑战
- 任务 ID：T069
- 失败/限制：
  - Bash 工具在多个调用中返回 "Permission to use Bash has been denied"，包括 `ls /Users/jabe/.agent-reach/tools/xiaoyuzhou/`、`bash /Users/jabe/.agent-reach/tools/xiaoyuzhou/transcribe.sh ...` 等关键命令
  - WebFetch 工具同样被拒（permssion denied）
  - 因此 transcript 完全未取得；报告基于公开信息源合成
  - 后续 session 拿到 Bash 权限后建议补跑：
    ```bash
    bash /Users/jabe/.agent-reach/tools/xiaoyuzhou/transcribe.sh https://www.xiaoyuzhoufm.com/episode/697b3b35875712791583c0f8 /tmp/vol31.txt
    # Vol.30 / Vol.32 单期 episode ID 需补充
    ```
## 2026-06-21 ingest
- T069 完结：3 期播客综合笔记 + 3 个新概念页 + 4 个新实体页；transcript 缺失由 WebSearch 公开资料合成补全

## [2026-07-09] ingest | xiaoyuzhou
- 来源：小宇宙 · 明镜与点点（面基）· 单期
- 形式：**对谈节目**（明镜主持 + 李继刚作客），非单口独白
- 嘉宾：**李继刚**（43 AI · 即刻 [@752D3103](https://web.okjike.com/u/752D3103-1107-43A0-BA49-20EC29D09E36)）—— 箴言式写作者，聊天过程是"将高度压缩的只言片语进行解压缩"
- 标题：读书：4种配速，取景框，人是滤器，冲刷神经网络
- 时长：1h54min（6815s）· 转录：5,372 段 / **35,430 汉字**（whisper.cpp / ggml-large-v3 / Metal 加速 / zh）/ 语速 312 字/min
- 报告：[[2026-07-09_xiaoyuzhou-mingjing-diandian_lijigang]]
- pipeline: yt-dlp 拉小宇宙 mp3（105MB m4a → 128MB mp3）→ whisper.cpp / ggml-large-v3 / Metal 加速 / 7m30s 墙钟 → Claude (MiniMax-M3) 自润 → WebFetch 拉小宇宙 shownotes（修正嘉宾 + 36 章节时间戳 + 17 本书单）→ Claude 按章节重组成 polished
- 自润：删 4 段小宇宙片尾广告 + 修 1 处明确同音误识别（黑心流→黑天鹅）+ 标 2 处不确定项（携带码 [?]）+ polished 头部 metadata
- polished 重构：按 shownotes 36 章节（无时间戳，每节一段连续文本）—— 43 KB，35,897 汉字
- 关键洞察：F × X = Fx 公式（shownotes 星标）/ 读书的四种配速（主题阅读 + 周维度的书 + 每天一本书 + 每天一个章节）/ 影子之书 / 43talks 闭门会 / "人是过滤器" / 预制菜同构讨论 / AI 魔法对魔法 / 守 破 离 / 分辨率 / 一念境转
- 引用 17 本书：《如何阅读一本书》《控制论与科学方法论》《智慧学九论》《鱼不存在》《无穷的开始》《随机漫步的傻瓜》《思考的真相》《GEB——一条永恒的金带》《我是个怪圈》《千脑智能》《存在与投资》《柏基之道》《我们赖以生存的隐喻》《金刚经》《道德经》《剑来》（+ 隐含引用）
- 新增 entities: 李继刚（明镜已有，2026-07-09 当期新加）
- 新增 concepts: F × X = Fx 公式、读书的四种配速
- 特别：whisper.cpp 后端（架构 redesign 后的新栈）首次在 podcast-learning 实战通过，实测 113 min 音频 7m30s 处理完（约 15× 实时，比 faster-whisper CPU int8 估算快 25-50 倍）
- 重要修正：whisper 把"李继刚"听成"李金刚/李吉刚"（多发）、把对谈误判为单口独白、没识别 shownotes 提供的 36 章节；本日志依 WebFetch 拉取的小宇宙页面修正
- Limitations: 标点稀疏 / "861 个神经元"应为"860 亿" / 难书名"GB"应指《GEB》/ 说话人区分缺失（明镜 vs 李继刚）/ 关键数字"86 1 亿"为已知吞字错误未在 polished 中修改

## [2026-07-19] ingest | xiaoyuzhou
- 来源：小宇宙 · 屠龙之术 · 单期《重估一切，文艺复兴——2026H1 AI行业观察》
- 形式：**单口**（主播庄明浩；CSDN 大会 45min 演讲的重新录制版，素材=ima 知识库 5-6 月约 200 张图 + 50 份 PDF，PPT 76 页）
- 时长：54m37s（3277s）· 转录：1,973 段 / **14,591 汉字**（whisper.cpp / ggml-large-v3 / Metal / zh）/ 语速 267 字/min
- 报告：[[2026-07-17_xiaoyuzhou-tulong-zhishu_2026h1-ai-review]]
- pipeline: yt-dlp 拉小宇宙音频 → whisper.cpp 本地转写（7/19 完成，卡在 shownotes 未拉取）→ curl 抓 episode 页（JSON-LD + __NEXT_DATA__）解析 shownotes（69 时间戳 + 节目简介）→ Kimi 通读全文 → 按章节重组成 polished（12 节 56 小节，无时间戳）
- 润色：删末尾 whisper 幻觉行（MING PAO...）+ 修正 40+ 处系统性同音误识别（KPS/CBS→CAPEX、视野模型→世界模型、美利奇→美第奇、Cloud Code→Claude Code、Isofix/ASOPEC/阿萨佩→Anthropic、openseo→OpenAI、Covid→CoreWeave、候选人→后训练、OpenSource→OpenRouter 等）+ 30+ 处不确定项标 [?]（Fable 5、马语、小龙虾、国产产品名等）
- 核心框架：文艺复兴映射（印刷术=推理成本坍塌 / 美第奇=CAPEX / 南北文艺复兴=中美双极 / 透视法=世界模型 / 工坊=Agent / 虚荣的篝火=治理反弹 / 人的画像=第四支柱）
- 关键判断：CAPEX 三年连续低估 vs 收入只够折旧；Anthropic 26Q2 反超 OpenAI（to B 订阅 + 估值）；Agent 元年 Chatbot 翻篇（Codex=新 ChatGPT，日增百万用户）；token maxxing 一季内证伪；"刚刚开始"
- 新增 entities：庄明浩（注意与 B 站屠龙博士区分，仅昵称同含"屠龙"）
- 新增 concepts：文艺复兴映射框架 / 美第奇的账本（CAPEX 泡沫之辩）/ Agent 元年 / 世界模型三分类 / 第四支柱
- 顺手补齐：wiki/index.md 漏登的 2026-07-07 屠龙博士、2026-07-14 鹿哥早餐两期报告与对应实体/概念条目
- Limitations：音频未保留（大小按 128kbps×时长估算 52MB）；CAPEX/估值/股价均为主播转述未经独立核实；30+ 处 [?] 详见报告 Limitations

## [2026-07-20] ingest | xiaoyuzhou
- 来源：小宇宙 · 面基 · 单期《人到中年仨账户：现金流、肌肉、睡眠》
- 形式：**单口**（主播老钱 / 老钱日日谈；35 岁，预习自己与母亲的中年）
- 时长：72m06s（4326s）· 转录：2,414 段 / **19,509 汉字**（whisper.cpp / ggml-large-v3 / Metal / zh，transcribe.py）/ 语速 271 字/min
- 报告：[[2026-07-13_xiaoyuzhou-mingjing-diandian_midlife-accounts]]
- pipeline: yt-dlp → whisper.cpp 本地转写 → curl 抓 episode 页 JSON-LD/__NEXT_DATA__（确认节目身份 + 时长）→ FetchURL 拉 shownotes（~40 时间戳 + 书单 + 概念解释）→ Kimi 通读 → 按章节重组成 polished（9 节 31 小节，无时间戳）
- **节目身份确认**：episode 页 podcast.title=面基 → 本库此前所称"明镜与点点"官方名即「面基」（2026-07-09 李继刚期同一节目）；老钱与"明镜"关系待确认（实体页交叉标注 [?]）
- 润色：删末尾 whisper 幻觉行（优优独播剧场...）+ 修正 40+ 处系统性误识别（面积→面基、生物中→生物钟、腺肝→腺苷、缺窍→缺觉、潜睡眠→浅睡眠、Aidsleep→Eight Sleep、烙蛋白→酪蛋白、金关涛→金观涛 等）+ 10+ 处 [?]
- 核心框架：中年三本账（现金账/肉身账/睡眠账）——地基性 + 可量化 + 慢反馈；订阅制支出（SEI 12 年 6 倍，社会 SaaS 化）；力量训练=退休储蓄（《超越百岁》）；控制论看睡眠（输入可控输出不可控）；Eat, Sleep, Gym, Invest.
- 赞助提示：59:23 起为 Eight Sleep 赞助段（已在报告标注，内容与广告区分阅读）
- 新增 entities：老钱
- 新增 concepts：中年三本账 / 订阅制支出 / 力量训练=退休储蓄 / 控制论看睡眠
- Limitations：音频未保留（69MB 为估算）；shownotes 自带科学注记（2A 类=夜班工作而非睡眠不足本身；β-淀粉样蛋白非唯一元凶）已在报告保留

## [2026-08-22] ingest | xiaoyuzhou
- 来源：小宇宙 · 张小珺Jùn｜商业访谈录 · Vol.148《对游凯超3小时访谈：开源Infra、和模型Co-design、"如果vLLM失败，我们会后悔一辈子"》（2026-07-28 发布）
- 形式：**对谈**（主持张小珺 × 嘉宾游凯超：Inferact 联创兼首席科学家、vLLM 核心维护者，清华本博）
- 时长：3h00m26s（10826s）· 转录：6,120 段 / **53,373 汉字**（whisper.cpp / ggml-large-v3 / Metal，transcribe.py，约 16min 墙钟）/ 语速 296 字/min
- 报告：[[2026-07-28_xiaoyuzhou-zhangxiaojun_youkaichao]]
- pipeline：yt-dlp → whisper.cpp → episode 页 JSON-LD/__NEXT_DATA__（时长/发布日）+ FetchURL shownotes（8 章节时间戳）→ **8 章并行分章润色**（agent swarm）→ 组装 polished（49,568 汉字）
- 润色：修正约 300 处系统性误识别（VLM/VM/为我们→vLLM 70+、杨斯多伊克→Ion Stoica 20+、归机→硅基、推力引擎→推理引擎、语言集世界→语言即世界 等）；约 40 处 [?]（翁嘉义[?]疑为翁家翌 Jiayi Weng、Johan[?]疑为 Zhuohan 音误、ch6 海外大咖人名被吞 等）
- 核心框架：vLLM 三年三级跳（SOSP 低分过线→开源→PyTorch 基金会→Inferact）/ 仁慈的独裁者分级治理 / AI slop 与善意假设崩塌 / 模型-Infra-硬件 co-design / hardware lottery / Token vs 电力 / 开源模型会赢
- 新增 entities：游凯超、Inferact；新节目 slug：zhangxiaojun（张小珺Jùn｜商业访谈录）
- 新增 concepts：模型×Infra×硬件 co-design、hardware lottery（系统彩票）
- Limitations：音频未保留（173MB 为 128kbps 估算）；嘉宾口述两处事实存疑已在报告标注（OpenSSH 段实为 OpenSSL Heartbleed；ALiBi 表述）；融资细节（1.5 亿美元种子/8 亿估值/a16z+Lightspeed 领投）经公开报道交叉验证；**与 ai-learning vLLM 源码级学习线互为表里**（代码在 ai-learning，人在本线）

## [2026-08-23] index | xiaoyuzhou
- 归档「张小珺Jùn｜商业访谈录」全量 154 集选题索引：[[show-indexes/zhangxiaojun]]（官方 RSS `feed.xyzfm.space/dk4yh3pkpjp3` 免登录全量拉取，2022-04 至今）
- 设周更扫描 cron：每周一 09:47 扫 RSS 对比索引首行，发现新集 → 提醒用户（不落文件、不自动转写）
- 方法备忘：小宇宙节目主页 SSR JSON 仅含最新 15 集；官方「加载更多」API 需登录 token（401）；**全量清单走 Apple Podcasts lookup 反查 feedUrl → RSS**，通用可复用
- 同日扩面：小宇宙 app 内导出 OPML（官方功能）→ 归档为 [[curated-podcasts|精选播客清单]]（51 档节目，含公开 RSS；对外表述为精选清单）→ `scripts/fetch_show_indexes.py` 拉全部 51 档节目的全量单集索引入 `wiki/show-indexes/`（共 7,839 集，零失败；含喜马拉雅/fireside/transistor 等非小宇宙源）
- 周更 cron 升级：由单节目（张小珺）改为全量刷新（`fetch_show_indexes.py`，每周一 09:47，cron id 01M0PF17S1J77J21T69Z7WZQJP），新集自动插入索引并提醒；「状态」列人工标记经链接 diff 保留（修过一次 [[wikilink|别名]] 竖线干扰状态列解析的 bug）

## [2026-08-23] ingest | rss（Fireside）
- 来源：硅谷101 · E247《对话盛颖：xAI，Infra的浪漫，SGLang，开源，平权与"甄嬛传"》（2026-08-04 发布）
- 形式：**对谈**（采访陈茜 × 嘉宾盛颖：RadixArk 联创&CEO、SGLang 发起人、xAI 前推理团队负责人；上海交大 ACM→哥大→斯坦福 PhD）
- 时长：1h46m26s（6387s）· 转录：5,578 段 / **34,164 汉字**（whisper.cpp / ggml-large-v3 / Metal / **--vad silero**）/ 语速 321 字/min · 音频 147MB（实测）
- 报告：[[2026-08-04_rss-guigu101_shengying]]
- pipeline：RSS 拿到频直链 → yt-dlp → whisper.cpp → Fireside shownotes（12 章节）→ 12 章并行润色 → 组装 polished（33,726 汉字）
- **重大踩坑**：首跑无 VAD，whisper 在音乐/过场段陷入循环幻觉（约 00:39 起循环输出无关广告词，整段报废；音频本身完好）→ `--vad` 重跑恢复；教训已写入 AGENTS.md 已知局限 #5，`transcribe.py` 新增 `--whisper-args` 透传
- 润色：修正约 200 处系统性误识别（SG Lane→SGLang、ReddixArc/Radi Shark→RadixArk、施琳/摄影→盛颖、一浪→Elon、Young Stoica→Ion Stoica、PSC→PhD 等）；约 60 处 [?]
- 外部核验：RadixArk 1 亿美元种子/4 亿估值/Accel 领投（BusinessWire 官方稿，2026-05-05）；转写中「Axial/Excel 领投」系误识别
- 核心框架：infra 即产品 / impact not making / RadixAttention / SGLang vs vLLM 时间轴分野 / day zero / 开源是空气 / 平权「赢不需要被解释」/ 世间的美好是存在的
- 新增 entities：盛颖、RadixArk、SGLang；新增 concepts：RadixAttention
- 与 [2026-07-28] 游凯超期构成双子星对照（vLLM/Inferact vs SGLang/RadixArk，同一伯克利圈子）；已交叉链接 ai-learning vLLM 概念页

## [2026-08-24] ingest | xiaoyuzhou
- 来源：小宇宙 · 菠萝健康派 · vol.122《刘方奇教授：肠癌越来越年轻，确诊后先别急着手术！》（2026-08-24 发布，周更扫描 cron 捕获）
- 形式：**对谈**（主播李治中/菠萝 × 嘉宾刘方奇：复旦大学附属肿瘤医院大肠外科副主任医师，师从蔡三军，从业 16 年）
- 时长：1h21m34s（4894s）· 转录：3,358 段 / **26,467 汉字**（whisper.cpp / ggml-large-v3 / Metal / --vad silero）/ 语速 324 字/min
- 报告：[[2026-08-24_xiaoyuzhou-boluo-jiankang_liufangqi]]
- pipeline：transcribe.py（yt-dlp + whisper.cpp + VAD）→ 小宇宙 shownotes（10 章节）→ 10 章并行润色 → 组装 polished（26,512 汉字）
- 内容：遗传性肠癌（Lynch/FAP/PJS、胚系检测、三代试管生殖阻断）/ 肠癌年轻化与筛查年龄 / 保肛与造口去污名化 / 新辅助治疗与观察等待 / 肛指检查价值 / 外科医生的温度
- 医学术语误识别密集修正约 200 处（邻居综合症→Lynch、迭面骂/DMMA→dMMR、心腹中→新辅助、细肉→息肉、灶口→造口、宝刚→保肛、聚钢门→距肛门 等）；约 40 处 [?]
- 新增 entities：刘方奇、李治中（菠萝）
- 新增 concepts：遗传性肠癌（Lynch/FAP/PJS）、新辅助治疗与观察等待
- 证据纪律：医学数字绝大部分为嘉宾个人临床口径自述，报告已做证据等级声明 + 不构成医疗建议；「dMMR 新辅助免疫三年 DFS 100%」等待一手文献追踪（open-questions 问 2）

## [2026-08-25] ingest | bilibili
- 来源：B 站 · 帆书视频播客 · 第49期《身体出现这些信号，可能是炎症在提醒你！三甲医生教你3个自查方法》（2026-08-21 发布，BV1j18i6VEtn）
- 形式：**讲书/科普对谈**（帆书主播[疑为樊登?] + 助讲嘉宾金博医生[三甲]）讲书《炎症》
- 时长：17m50s（1070s）· 转录：602 段 / **5,445 汉字**（whisper.cpp / ggml-large-v3 / Metal / --vad silero）/ 语速 305 字/min · 视频 30.8MB
- 报告：[[2026-08-21_bilibili-fanshu_yanzheng]]
- pipeline：opencli bilibili download（绕 412）→ ffmpeg → whisper.cpp + VAD → opencli 官方字幕交叉校验 → Kimi 通读自润（短集不走分章 swarm）
- 字幕校验亮点：烤箱糖→口香糖、一道素→胰岛素、消盐→消炎 等约 40 处修正；**字幕亦错两处**（套蛋白→Tau 蛋白、醋盐→促炎）依医学常识修正并单独标注——官方字幕校验源的角色首次完整走通
- 内容：慢性炎症=无声小火 / 炎症×癌症（1/4）×心血管（C 反应蛋白、卡纳单抗 -15%）/ 肥胖=巨噬细胞包围脂肪细胞 / 炎性衰老与阿尔茨海默 / 餐桌抗炎（Omega-3 vs 6、深色蔬菜、盐 6g、高果糖玉米糖浆、纤维益生元）
- 新增 concepts：慢性炎症与隐匿的炎症（chronic-inflammation）
- 实体备注：金博医生（三甲，单位未报出）与帆书主播（疑为樊登[?]）均未建实体页——身份信息不足以成页，待后续期数补全

## [2026-08-31] index | 人工催更（cron 退役）
- 用户催更补刷本周索引：51 档全量刷新，真实新增 31 集；同日修复两类机制缺陷并迭代脚本：
- **事故 1｜RSS 链接变更假阳性**：硅谷101 Fireside 单集域名 `www.sv101.net` → `sv101.fireside.fm`，link 单键 diff 全量失配 → 29 条 2020 年老集误报 NEW，且人工状态列面临清零（本次实损为零）。**修复**：diff 改 **guid+链接双键**——guid 写入标题单元格 HTML 注释 `<!--g:...-->`（渲染不可见）；另加护栏：单节目新增占比 >30% 自动降级 `SUSPECT`，不计入 NEW
- **事故 2｜解析正则回归**：改键时新正则用 `[^|]*` 取状态列，遇 `✅ 已处理（[[报告|别名]]）` 内嵌竖线整行失配（张小珺 148 状态一度被重置，已手工恢复）。状态列必须保持贪婪 `(.*)` 到行尾竖线的旧结构——与 2026-08-24 修过的 wikilink 竖线坑同源，回归了一次，已在代码注释里立牌
- 三遍全量跑收敛验证：第三遍「无新增单集」+ 148 ✅ 状态完整保留 + 51 档零失败
- **机制变更**：周更 cron（id 01M0PF17S1J77J21T69Z7WZQJP）退役——它挂在当时会话里从未持久化（本机 crontab/launchd/openclaw 均查无此任务）。2026-08-31 起**改用户主动催更**，工作流写入 AGENTS.md（跑脚本 → NEW 按 PROFILE 兴趣排序汇总 → 问是否转写）
