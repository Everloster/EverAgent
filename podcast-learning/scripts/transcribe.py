#!/usr/bin/env python3
"""Podcast 本地转写脚本.

用 yt-dlp 下载音频（小宇宙 / B站 / YouTube / 直链 / 本地文件），
再用 whisper.cpp（whisper-cli）本地转写为带时间戳的纯文本。
全程离线（除下载音频外），不上传云端。

依赖见 podcast-learning/SETUP.md：
    # 系统需：whisper.cpp（https://github.com/ggml-org/whisper.cpp）
    #         ffmpeg（brew install ffmpeg）
    #         yt-dlp（brew install yt-dlp）
    # whisper.cpp 编译后把 build/bin/whisper-cli 软链到 /opt/homebrew/bin/。

用法：
    # 从链接转写（自动下载音频 → 转写）
    python3 transcribe.py "https://www.xiaoyuzhoufm.com/episode/xxxx" \
        --out ../reports/transcripts/2026-07-06_xiaoyuzhou_epXX.transcript.txt

    # 从本地音频文件转写
    python3 transcribe.py /path/to/audio.mp3 --out out.transcript.txt

    # 只下载音频不转写
    python3 transcribe.py "URL" --download-only --audio-out ep.mp3

    # 指定模型大小与语言（默认 large-v3 / zh）
    python3 transcribe.py "URL" --model medium --lang zh --out out.txt

模型大小权衡（whisper.cpp ggml 格式）：
    tiny / base / small / medium / large-v3
    Apple Silicon 走 Metal 加速，large-v3 仍可对 1h 音频在数分钟内处理完。

环境变量：
    WHISPER_CPP_MODELS   whisper.cpp 模型目录（默认：~/workspace/whisper.cpp/models/）
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_WHISPER_CPP_MODELS = "/Users/jabe/workspace/whisper.cpp/models"

# 模型名（tiny / base / small / medium / large-v3）→ ggml 文件名
MODEL_FILES = {
    "tiny": "ggml-tiny.bin",
    "tiny.en": "ggml-tiny.en.bin",
    "base": "ggml-base.bin",
    "base.en": "ggml-base.en.bin",
    "small": "ggml-small.bin",
    "small.en": "ggml-small.en.bin",
    "medium": "ggml-medium.bin",
    "medium.en": "ggml-medium.en.bin",
    "large": "ggml-large-v3.bin",
    "large-v1": "ggml-large-v1.bin",
    "large-v2": "ggml-large-v2.bin",
    "large-v3": "ggml-large-v3.bin",
}


def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def check_dep(name: str, hint: str) -> None:
    if shutil.which(name) is None:
        sys.exit(f"[transcribe] 缺少依赖 `{name}`。{hint}")


def resolve_model_path(model: str, model_dir: str | None) -> Path:
    """把模型名（如 'large-v3'）解析为 .bin 绝对路径."""
    model_dir = model_dir or os.environ.get("WHISPER_CPP_MODELS", DEFAULT_WHISPER_CPP_MODELS)
    filename = MODEL_FILES.get(model)
    if filename is None:
        sys.exit(
            f"[transcribe] 未知模型 `{model}`。可选: {', '.join(MODEL_FILES)}"
        )
    path = Path(model_dir) / filename
    if not path.exists():
        sys.exit(
            f"[transcribe] 模型文件不存在: {path}\n"
            f"  · 装模型: cd {model_dir} && ./download-ggml-model.sh {model}\n"
            f"  · 或设置环境变量 WHISPER_CPP_MODELS 指向你的模型目录"
        )
    return path


def download_audio(url: str, audio_out: Path) -> Path:
    """用 yt-dlp 下载最佳音频，转成 mp3。返回实际输出路径."""
    check_dep("yt-dlp", "安装：brew install yt-dlp")
    check_dep("ffmpeg", "安装：brew install ffmpeg")

    # yt-dlp 用 %(ext)s 决定后缀，这里固定抽取为 mp3
    out_template = str(audio_out.with_suffix(".%(ext)s"))
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", out_template,
        url,
    ]
    print(f"[transcribe] 下载音频：{url}")
    subprocess.run(cmd, check=True)

    mp3 = audio_out.with_suffix(".mp3")
    if not mp3.exists():
        sys.exit(f"[transcribe] 下载完成但未找到 {mp3}，请检查 yt-dlp 输出。")
    print(f"[transcribe] 音频已保存：{mp3}")
    return mp3


def transcribe(
    audio: Path,
    out: Path,
    model: str,
    lang: str | None,
    model_dir: str | None,
    whisper_args: list[str] | None = None,
) -> None:
    check_dep(
        "whisper-cli",
        "安装：编译 https://github.com/ggml-org/whisper.cpp 后把 build/bin/whisper-cli 软链到 PATH",
    )

    model_path = resolve_model_path(model, model_dir)
    print(f"[transcribe] 模型: {model_path}")
    print(f"[transcribe] 语言: {lang or 'auto-detect'}")

    with tempfile.TemporaryDirectory(prefix="whisper-out-") as tmp:
        prefix = Path(tmp) / "out"
        cmd = [
            "whisper-cli",
            "-m", str(model_path),
            "-l", lang or "auto",
            "-f", str(audio),
            "-oj",                # JSON 输出（带时间戳、文本）
            "-of", str(prefix),   # 输出文件前缀
            "-np",                # 抑制 whisper 自带的进度/计时打印
        ]
        if whisper_args:
            cmd += whisper_args   # 透传 whisper-cli 额外参数（如 --vad / -mc 0 防循环幻觉）
        print(f"[transcribe] 调用 whisper-cli…")
        subprocess.run(cmd, check=True)

        json_path = Path(tmp) / "out.json"
        if not json_path.exists():
            sys.exit(f"[transcribe] 期望 JSON 产物 {json_path} 不存在")
        with json_path.open(encoding="utf-8") as f:
            data = json.load(f)

    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for seg in data.get("transcription", []):
            ts_from = seg["timestamps"]["from"].split(",")[0]  # HH:MM:SS,mmm → HH:MM:SS
            ts_to = seg["timestamps"]["to"].split(",")[0]
            text = seg["text"].strip()
            f.write(f"[{ts_from} -> {ts_to}] {text}\n")
            n += 1
            if n % 50 == 0:
                print(f"[transcribe]   已写 {n} 段…")

    detected = data.get("result", {}).get("language", lang)
    print(f"[transcribe] 完成：{out}（{n} 段，检测语种={detected}）")


def main() -> int:
    p = argparse.ArgumentParser(description="Podcast 本地转写（yt-dlp + whisper.cpp）")
    p.add_argument("source", help="播客/视频链接，或本地音频文件路径")
    p.add_argument("--out", help="转写文本输出路径（.transcript.txt）")
    p.add_argument("--audio-out", help="下载音频的保存路径（默认临时目录）")
    p.add_argument(
        "--download-only", action="store_true", help="只下载音频，不转写"
    )
    p.add_argument(
        "--model",
        default="large-v3",
        help="whisper.cpp 模型大小（默认 large-v3）: "
        + ", ".join(MODEL_FILES),
    )
    p.add_argument(
        "--lang", default="zh", help="语言代码，默认 zh；设为 auto 让模型自动检测"
    )
    p.add_argument(
        "--model-dir",
        help="whisper.cpp 模型目录（默认读环境变量 WHISPER_CPP_MODELS，或 ~/workspace/whisper.cpp/models/）",
    )
    p.add_argument(
        "--whisper-args",
        help='透传给 whisper-cli 的额外参数，如 "--vad -vm <silero模型> -mc 0"（长音频防循环幻觉）',
    )
    args = p.parse_args()

    lang = None if args.lang == "auto" else args.lang

    # 1) 拿到音频路径
    tmpdir: tempfile.TemporaryDirectory | None = None
    if is_url(args.source):
        if args.audio_out:
            audio_base = Path(args.audio_out)
        else:
            tmpdir = tempfile.TemporaryDirectory(prefix="podcast-audio-")
            audio_base = Path(tmpdir.name) / "episode"
        audio = download_audio(args.source, audio_base)
    else:
        audio = Path(args.source)
        if not audio.exists():
            sys.exit(f"[transcribe] 本地文件不存在：{audio}")

    if args.download_only:
        if tmpdir is not None:
            print(
                "[transcribe] 警告：--download-only 且未指定 --audio-out，音频在临时目录，退出后会丢失。"
            )
        return 0

    # 2) 转写
    if not args.out:
        sys.exit("[transcribe] 转写需指定 --out 输出路径。")
    transcribe(
        audio=audio,
        out=Path(args.out),
        model=args.model,
        lang=lang,
        model_dir=args.model_dir,
        whisper_args=shlex.split(args.whisper_args) if args.whisper_args else None,
    )

    if tmpdir is not None:
        tmpdir.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
