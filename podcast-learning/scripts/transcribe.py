#!/usr/bin/env python3
"""Podcast 本地转写脚本.

用 yt-dlp 下载音频（小宇宙 / B站 / YouTube / 直链 / 本地文件），
再用 faster-whisper 本地转写为纯文本。全程离线（除下载音频外），不上传云端。

依赖见 podcast-learning/SETUP.md：
    pip install yt-dlp faster-whisper
    # 系统需 ffmpeg（brew install ffmpeg）

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

模型大小与显存/内存权衡（faster-whisper）：
    tiny / base / small / medium / large-v3
    CPU 可跑 small/medium；有 GPU（--device cuda）建议 large-v3。
    Apple Silicon 走 CPU int8，medium 约实时 2-4x。
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def check_dep(name: str, hint: str) -> None:
    if shutil.which(name) is None:
        sys.exit(f"[transcribe] 缺少依赖 `{name}`。{hint}")


def download_audio(url: str, audio_out: Path) -> Path:
    """用 yt-dlp 下载最佳音频，转成 mp3。返回实际输出路径。"""
    check_dep("yt-dlp", "安装：pip install yt-dlp")
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
    model_size: str,
    lang: str | None,
    device: str,
    compute_type: str,
) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("[transcribe] 缺少 faster-whisper。安装：pip install faster-whisper")

    print(f"[transcribe] 加载模型 {model_size}（device={device}, compute={compute_type}）…")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)

    print(f"[transcribe] 开始转写：{audio}")
    segments, info = model.transcribe(
        str(audio),
        language=lang,
        vad_filter=True,
        beam_size=5,
    )
    detected = getattr(info, "language", lang)
    print(f"[transcribe] 检测语言：{detected}（概率 {getattr(info, 'language_probability', 0):.2f}）")

    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as f:
        for seg in segments:
            ts = f"[{fmt_ts(seg.start)} -> {fmt_ts(seg.end)}]"
            line = f"{ts} {seg.text.strip()}"
            f.write(line + "\n")
            n += 1
            if n % 50 == 0:
                print(f"[transcribe]   已写 {n} 段…")
    print(f"[transcribe] 完成：{out}（共 {n} 段）")


def fmt_ts(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def main() -> int:
    p = argparse.ArgumentParser(description="Podcast 本地转写（yt-dlp + faster-whisper）")
    p.add_argument("source", help="播客/视频链接，或本地音频文件路径")
    p.add_argument("--out", help="转写文本输出路径（.transcript.txt）")
    p.add_argument("--audio-out", help="下载音频的保存路径（默认临时目录）")
    p.add_argument("--download-only", action="store_true", help="只下载音频，不转写")
    p.add_argument("--model", default="large-v3", help="faster-whisper 模型大小（默认 large-v3）")
    p.add_argument("--lang", default="zh", help="语言代码，默认 zh；设为 auto 让模型自动检测")
    p.add_argument("--device", default="cpu", help="cpu / cuda（默认 cpu）")
    p.add_argument("--compute-type", default="int8", help="int8 / float16 / float32（默认 int8）")
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
            print("[transcribe] 警告：--download-only 且未指定 --audio-out，音频在临时目录，退出后会丢失。")
        return 0

    # 2) 转写
    if not args.out:
        sys.exit("[transcribe] 转写需指定 --out 输出路径。")
    transcribe(
        audio=audio,
        out=Path(args.out),
        model_size=args.model,
        lang=lang,
        device=args.device,
        compute_type=args.compute_type,
    )

    if tmpdir is not None:
        tmpdir.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
