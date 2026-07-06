# podcast-learning — 领域协议

> 领域：播客/访谈内容学习。**本地转写驱动**：我发链接 → 本地转写出原文 → 润色 → 总结/讨论 → 报告。
> 通用研究方法论见根 [METHODOLOGY.md](../METHODOLOGY.md)（强制）。本文件只写本领域的边界与特化。

---

## 工作模式：链接 → 本地转写 → 报告

用户发一个播客/视频链接（或本地音频文件），或说"上次那期继续"，按以下循环：

1. **读画像与地图** — [PROFILE.md](./PROFILE.md)、[MAP.md](./MAP.md)、[wiki/open-questions.md](./wiki/open-questions.md)
2. **本地转写** — 用 `scripts/transcribe.py` 本地转写（yt-dlp 下载音频 + faster-whisper），产出 `reports/transcripts/{slug}.transcript.txt`。首次用需按 [SETUP.md](./SETUP.md) 装依赖。
3. **润色** — 基于原始转写去口水词、断句、纠正明显错字，产出 `.polished.txt`（与转写并列存放）。**只修表达，不改事实**；无法辨识处保留原文并标 `[?]`。
4. **提取/总结** — 通读润色稿，提取核心观点/关键人物/新概念/关键数字/金句。
5. **写报告** — 存 `reports/`，带 frontmatter，结尾必带「思考与追问」三问。
6. **沉淀** — 更新 wiki（人物/概念页）、未解问题汇入 open-questions。
7. **更新画像** — 把新关注的节目/人物/主题写回 PROFILE（仅凭用户真实表达，禁止臆测）。

> "继续讨论"场景：用户读完转写/报告后追问，围绕转写原文与已查证事实展开，不引入转写外的编造内容。

---

## 领域特化

- **转写脚本**：`scripts/transcribe.py`（本地 faster-whisper，全程离线）；模型/依赖见 [SETUP.md](./SETUP.md)。
- **报告类型**：`reports/`（单期总结/跨期专题/概念追踪，同目录按 frontmatter `report_type` 区分，不再按子目录拆分）。
- **特化要求（关键）**：**转录中未出现的引用、数据、人物言论禁止推测**；关键引用保留原文（哪怕标点残缺）；转录质量差时在 limitations 标注，不强行总结；润色只改表达不改事实。
- **特化模板**：[skills/transcription/SKILL.md](./skills/transcription/SKILL.md)（转写+润色规范）、[skills/episode_analysis/SKILL.md](./skills/episode_analysis/SKILL.md)（总结/报告模板）。

---

## 文件约定

```
reports/
├── transcripts/                       # 转写原文 + 润色稿
│   ├── {YYYY-MM-DD}_{show}_{ep}.transcript.txt
│   └── {YYYY-MM-DD}_{show}_{ep}.polished.txt
└── {YYYY-MM-DD}_{show}_{ep}_{slug}.md # 总结/专题报告
```

报告 frontmatter：

```yaml
---
title: "标题"
domain: "podcast-learning"
report_type: episode_summary   # 或 cross_episode / concept_tracking
source: 小宇宙播客              # 或 bilibili / youtube / 本地音频
source_url: https://...
show: "节目名"
guest: "嘉宾"
transcript: reports/transcripts/{slug}.transcript.txt
status: archived
updated_on: YYYY-MM-DD
---
```

---

## 完成后自检

```bash
python3 ../scripts/reindex.py
```

提交规范见根 [AGENTS.md](../AGENTS.md) 与 [docs/PROTOCOL_COMMON.md](../docs/PROTOCOL_COMMON.md)。
