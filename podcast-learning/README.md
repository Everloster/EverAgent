# 播客学习 — Razer 静默转写驱动

> 发一个播客/视频链接 → Razer 静默转写出原文 → 润色 → 总结/讨论 → 产出报告。
> 转写全程在个人设备本地运行（whisper.cpp / CUDA），不上传云端、不打开浏览器、不播放媒体。

> **AI 使用本项目？** → 先读 [AGENTS.md](./AGENTS.md) 与根 [METHODOLOGY.md](../METHODOLOGY.md)。

---

## 工作流

```
我：发链接（小宇宙/B站/YouTube/本地音频）
  ↓
AI：1. 静默转写   eacli podcast（Razer）→ reports/transcripts/*.transcript.txt
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
├── SETUP.md               # Razer 主路径与本地 fallback 依赖
├── scripts/
│   └── transcribe.py      # 本地文件/隔离排障 fallback
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
# URL：先检查 Razer worker，再 plan/run/result
eacli podcast status
eacli podcast plan --source "https://www.xiaoyuzhoufm.com/episode/xxxx"
```

执行协议见 [AGENTS.md](./AGENTS.md)。
