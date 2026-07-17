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

### B站链接：音频获取走 opencli（2026-07-18 实测定规）

B站风控已全面 412 拦截 yt-dlp（直连/代理/Cookie 均无效），`bili-cli audio` 接口也故障（`internal_error: 获取音频流`）。**优先用 opencli 复用浏览器登录态下载**：

```bash
# 1. 下载视频（opencli 走浏览器会话，绕过 412）
opencli bilibili download <BVID> --output /tmp/bv_xxx --quality 480p

# 2. 提取音频
ffmpeg -y -i /tmp/bv_xxx/*.mp4 -vn -ac 1 -ar 16000 -b:a 128k /tmp/bv_xxx/audio.mp3

# 3. 本地 whisper.cpp 转写
whisper-cli -m ~/workspace/whisper.cpp/models/ggml-large-v3.bin \
    -l zh -f /tmp/bv_xxx/audio.mp3 -oj -of /tmp/bv_xxx/out -np
```

**官方字幕 = 修正源**（替代小宇宙 shownotes 的角色）：

```bash
opencli bilibili subtitle <BVID> -f yaml > /tmp/subtitles.yaml
```

- 用字幕逐处校验 whisper 误识别（人名/术语/数字），修正写入 polished 头部清单。
- ⚠️ 官方字幕自身也是 ASR 产物，**可能有错**（实测："夜里面"→"叶里面"、"清晨"→"清纯"）——字幕与 whisper 一致但上下文明显不通时，依上下文修正并单独标注「字幕亦错」。
- 视频发布日期用 API 拿（命名需要）：`curl -s "https://api.bilibili.com/x/web-interface/view?bvid=<BVID>"` 取 `pubdate`。

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
