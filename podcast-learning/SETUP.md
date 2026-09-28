# podcast-learning 环境配置

> 本地转写依赖，一次性安装。转写全程本地运行（whisper.cpp），音频下载走 yt-dlp。
> 详见 https://github.com/ggml-org/whisper.cpp

## 安装

```bash
# 系统依赖：ffmpeg（音频抽取/转码）+ yt-dlp（音频下载）
brew install ffmpeg yt-dlp

# whisper.cpp：从源码编译
git clone https://github.com/ggml-org/whisper.cpp.git ~/workspace/whisper.cpp
cd ~/workspace/whisper.cpp
cmake -B build
cmake --build build --config Release -j

# 把可执行软链到 brew bin（已加入 PATH）
ln -sf ~/workspace/whisper.cpp/build/bin/whisper-cli /opt/homebrew/bin/whisper-cli
ln -sf ~/workspace/whisper.cpp/build/bin/whisper-server /opt/homebrew/bin/whisper-server
ln -sf ~/workspace/whisper.cpp/build/bin/whisper-bench /opt/homebrew/bin/whisper-bench

# 下载模型（默认 large-v3；中文播客推荐）
cd models
./download-ggml-model.sh large-v3
curl --fail --location --output ggml-silero-v6.2.0.bin \
  https://huggingface.co/ggml-org/whisper-vad/resolve/main/ggml-silero-v6.2.0.bin
echo 'b65ad872758ea4ac85ec18aa132b384d91804f52799c70edc80f8fdb0420e1a5  ggml-silero-v6.2.0.bin' | shasum -a 256 -c -
```

> **Apple Silicon**：Metal 加速默认开（`libggml-metal.dylib` 自动链接），无需额外配置。
> **NVIDIA GPU**：用 `-DGGML_CUDA=ON` 重新编译可获更佳性能（本机无独立 GPU，跳过）。

## 快速使用

```bash
cd podcast-learning/scripts

# URL 的常规入口：Razer 静默 worker（先 plan，再按返回值确认）
eacli podcast status
eacli podcast plan --source "https://www.xiaoyuzhoufm.com/episode/xxxx"

# 本地文件或隔离排障 fallback
python3 transcribe.py /path/to/audio.mp3 --out out.transcript.txt

# 只下载音频不转写（无 UI；留档/换机器转写）
python3 transcribe.py "URL" --download-only --audio-out ep.mp3

# 显式指定模型目录（默认 ~/workspace/whisper.cpp/models/）
WHISPER_CPP_MODELS=/path/to/models python3 transcribe.py "URL" --out out.txt
```

## 模型大小选择

| 模型 | 大小 | 适用 |
|------|------|------|
| `tiny` | ~75 MB | 极快草稿 |
| `base` | ~141 MB | 快速草稿 |
| `small` | ~465 MB | 平衡 |
| `medium` | ~1.5 GB | CPU 仍可用 |
| `large-v3` | ~2.9 GB | 最佳质量（中文播客推荐） |

下载脚本：`./models/download-ggml-model.sh <model>`。

- Apple Silicon 走 Metal 加速，**`large-v3` 处理 1 小时音频约 3-5 分钟**（实测墙钟约 实时 ×0.05）。
- 中文播客默认 `--lang zh`；混合语种用 `--lang auto`。

## 支持的链接来源

yt-dlp 支持小宇宙、B站、YouTube、Apple Podcasts、直链音频等。URL 常规任务必须走
Razer `eacli podcast`；无法解析时只允许无 UI API/adapter 或用户提供本地音频。禁止用
`opencli browser`、Chrome 登录态、系统 URL opener 或播放器兜底。

## 故障排查

- `whisper-cli: command not found` → 软链未生效，跑 `which whisper-cli` 确认；重连终端或 `hash -r`。
- 模型文件不存在 → 检查 `WHISPER_CPP_MODELS` 环境变量或 `--model-dir` 参数是否指向正确目录。
- Metal 加速未启用 → 看 whisper 启动时打印的 `system_info`，应有 `MTL : EMBED_LIBRARY = 1`。
