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
