# 播客学习 — 本地转写驱动

> 发一个播客/视频链接 → 本地转写出原文 → 润色 → 总结/讨论 → 产出报告。
> 转写全程本地运行（faster-whisper），不上传云端。

> **AI 使用本项目？** → 先读 [AGENTS.md](./AGENTS.md) 与根 [METHODOLOGY.md](../METHODOLOGY.md)。

---

## 工作流

```
我：发链接（小宇宙/B站/YouTube/本地音频）
  ↓
AI：1. 本地转写   scripts/transcribe.py → reports/transcripts/*.transcript.txt
    2. 润色       忠实去口水/断句/纠错 → *.polished.txt
    3. 总结       提取观点/概念/人物/金句 → reports/*.md
    4. 沉淀       更新 wiki + open-questions
  ↓
我：读转写/报告 → 继续讨论 → 循环
```

---

## 目录结构

```
podcast-learning/
├── AGENTS.md              # 执行协议
├── SETUP.md               # 转写依赖安装（yt-dlp + faster-whisper + ffmpeg）
├── scripts/
│   └── transcribe.py      # 本地转写脚本
├── reports/
│   ├── transcripts/       # 转写原文(.transcript.txt) + 润色稿(.polished.txt)
│   └── *.md               # 单期总结 / 跨期专题 / 概念追踪
├── wiki/                  # concepts / entities / syntheses / open-questions.md
└── skills/
    ├── transcription/     # 转写 + 润色规范
    └── episode_analysis/  # 总结/报告模板
```

---

## 快速开始

```bash
# 1. 装依赖（首次）
cat SETUP.md

# 2. 转写一期
cd scripts
python3 transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxx" \
    --out ../reports/transcripts/2026-07-06_xiaoyuzhou_epXX.transcript.txt
```

执行协议见 [AGENTS.md](./AGENTS.md)。
