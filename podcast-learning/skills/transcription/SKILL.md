# Skill: transcription — 本地转写 + 润色规范

> 通用研究方法论见根 [METHODOLOGY.md](../../METHODOLOGY.md)（强制）。本文件为领域特化部分。
> 目标：把一个播客/视频链接（或本地音频）变成可读、忠实的原文，供后续总结与讨论。

---

## 一、转写（产出 `.transcript.txt`）

用本地脚本，全程离线（除下载音频），不走云端 API。

```bash
cd podcast-learning/scripts
python3 transcribe.py "<链接或本地音频路径>" \
    --out ../reports/transcripts/{YYYY-MM-DD}_{show}_{ep}.transcript.txt
# 中文播客默认 --lang zh；混合语种 --lang auto；纯 CPU 建议 --model medium
```

- 首次使用先按 [SETUP.md](../../SETUP.md) 安装 `yt-dlp faster-whisper` + `ffmpeg`。
- 链接无法被 yt-dlp 解析时：手动下载音频 → 用本地文件模式转写。
- 转写文件保留时间戳行 `[HH:MM:SS -> HH:MM:SS] 文本`，方便回溯定位。

## 二、润色（产出 `.polished.txt`）

基于转写原文做**忠实润色**，与转写并列存放，同名 `.polished.txt`。

**允许**：去口水词（嗯/那个/就是）、合理断句分段、纠正明显同音错字、补标点。
**禁止**：改变说话人原意、增删事实、脑补未说出口的内容、合并不同人观点。

- 听不清/转写明显出错且无法确定的词：保留原文并标 `[?]`，不猜。
- 可按话轮或话题分段，段前可留粗略时间戳锚点。
- 润色稿是"可读版原文"，不是总结——不做提炼、不加评论。

---

## 质量红线

- ❌ 转写里没有的引用、数据、人物言论，禁止在润色/报告中出现。
- ❌ 转写质量差时不强行"补全"，在报告 limitations 如实标注。
- ✅ 关键金句、数字、人名保留原文措辞（哪怕标点残缺）。
