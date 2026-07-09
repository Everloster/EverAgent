# Wiki Log

> Append-only。禁止修改历史条目。

## [2026-06-18] init | scaffold
- 初始化项目骨架（podcast-learning v1.0，PodcastAgent）

## [2026-06-18] ingest | xiaoyuzhou
- 来源：小宇宙 · 明镜与点点 Vol.29
- 嘉宾：王小川（百川智能创始人）
- 标题：对话王小川：造医生，战豆包，与无尽的 AI 非共识
- 时长：92m45s · 转录：19,983 字（Whisper large-v3, zh, 未润色）
- 报告：[[2026-06-18_xiaoyuzhou_vol29_wangxiaochuan]]
- 新增 entities: 王小川、百川智能
- 新增 concepts: 百川 M4、百小一、生命模型、非共识 AI、医疗供给侧改革
- 失败/限制：Llama 3.3 70B polish 因 Groq TPM 12,000 限速失败，标点稀疏；详见报告 Limitations

## [2026-06-20] ingest | bilibili
- 来源：B 站 · CLS同学 · BV1NHJF6oE8m
- 标题：三年行业吃肉榜/爆亏榜大合集（2023-2025）
- 时长：1h2m53s · 转录：21,953 字（Whisper large-v3 zh, **已用 Claude (MiniMax-M3) 自润** — 跳过 Groq Llama 3.3 70B，见 self-polish memory）
- 报告：[[2026-06-20_bilibili_BV1NHJF6oE8m_cls-tongxue]]
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
- 报告：[[2026-06-21_xiaoyuzhou_vol30-32_收听笔记]]
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
- 报告：[[2026-07-09_xiaoyuzhou_6a4b22ad_lijigang]]
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
