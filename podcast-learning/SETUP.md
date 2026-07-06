# podcast-learning 环境配置

> 本地转写依赖，一次性安装。转写全程本地运行（faster-whisper），音频下载走 yt-dlp。

## 安装

```bash
# Python 依赖
pip install yt-dlp faster-whisper

# 系统依赖：ffmpeg（音频抽取/转码）
brew install ffmpeg          # macOS
# sudo apt install ffmpeg    # Ubuntu/Debian
```

## 快速使用

```bash
cd podcast-learning/scripts

# 从链接：下载音频 → 本地转写（默认 large-v3 / 中文）
python3 transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxx" \
    --out ../reports/transcripts/2026-07-06_xiaoyuzhou_epXX.transcript.txt

# 从本地音频文件
python3 transcribe.py /path/to/audio.mp3 --out out.transcript.txt

# 只下载音频不转写（留档/换机器转写）
python3 transcribe.py "URL" --download-only --audio-out ep.mp3
```

## 模型大小选择

| 模型 | 速度 | 质量 | 适用 |
|------|------|------|------|
| `small` | 快 | 一般 | 纯 CPU、快速草稿 |
| `medium` | 中 | 好 | 纯 CPU 推荐 |
| `large-v3` | 慢 | 最佳 | 有 GPU（`--device cuda --compute-type float16`）或愿意等 |

- Apple Silicon：走 CPU int8，`medium` 约实时 2-4×，`large-v3` 更慢但质量最好。
- 中文播客默认 `--lang zh`；混合语种用 `--lang auto`。

## 支持的链接来源

yt-dlp 支持小宇宙、B站、YouTube、Apple Podcasts、直链音频等。无法解析时，先手动下载音频再用本地文件模式转写。
