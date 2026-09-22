#!/usr/bin/env python3
"""Build a bounded manifest of curated Xiaoyuzhou learning episodes.

Reads generated show indexes under podcast-learning/wiki/show-indexes and
existing report frontmatter under podcast-learning/reports. The output is a
public, bounded JSON manifest consumed by EverAgent Android. No transcript or
private note content is included.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
INDEX_DIR = ROOT / "podcast-learning" / "wiki" / "show-indexes"
REPORT_DIR = ROOT / "podcast-learning" / "reports"
OUTPUT = ROOT / "docs" / "PODCAST_MANIFEST.json"
MAX_ITEMS = 200

SHOW_TITLES = {
    "ai-lianjinshu": "AI炼金术",
    "zhangxiaojun": "张小珺商业访谈录",
    "luanfanshu": "乱翻书",
    "guigu101": "硅谷101",
    "wandian-latetalk": "晚点聊 LateTalk",
    "crossing": "十字路口Crossing",
    "shengdong-jixi": "声东击西",
    "tulong-zhishu": "屠龙之术",
    "42zhangjing": "42章经",
    "daxiaoma-keji": "大小马聊科技",
    "mingjing-diandian": "明镜与点点",
}

ROW = re.compile(
    r"^\|\s*(\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*([^|]+)\s*\|"
    r"\s*\[([^]]+)]\(([^)]+)\)[^|]*\|\s*([^|]*)\s*\|\s*$"
)


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_url(value: str) -> str:
    return value.strip().split("?", 1)[0].rstrip("/")


def safe_https(value: str) -> str:
    parsed = urlsplit(value.strip())
    return value.strip() if parsed.scheme == "https" and parsed.netloc else ""


def compact(value: str, limit: int) -> str:
    return re.sub(r"\s+", " ", value).strip()[:limit]


def parse_frontmatter(path: pathlib.Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace")[:8192].splitlines()
    except OSError:
        return {}
    if not lines or lines[0].strip() != "---":
        return {}
    result: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip().lower()] = value.strip().strip("\"'")
    return result


def load_reports() -> dict[str, dict]:
    by_audio: dict[str, dict] = {}
    for path in REPORT_DIR.rglob("*.md"):
        if not path.is_file() or "/transcripts/" in path.as_posix():
            continue
        fm = parse_frontmatter(path)
        audio = safe_https(fm.get("source_url", ""))
        if not audio or "xiaoyuzhoufm.com/episode/" not in audio:
            continue
        key = normalize_url(audio)
        candidate = {
            "path": path.relative_to(ROOT).as_posix(),
            "title": compact(fm.get("title") or path.stem, 240),
            "updated_on": fm.get("updated_on", ""),
            "source": fm.get("source", "小宇宙"),
            "status": fm.get("status", "completed"),
            "show": fm.get("show", ""),
            "episode": fm.get("episode", ""),
            "duration": fm.get("duration", ""),
        }
        old = by_audio.get(key)
        if old is None or candidate["updated_on"] >= old["updated_on"]:
            by_audio[key] = candidate
    return by_audio


def parse_show_index(path: pathlib.Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = ROW.match(line)
        if not match:
            continue
        episode_no, date, duration, title, audio, status = match.groups()
        audio = safe_https(audio.strip())
        guid = re.search(r"<!--g:([^>]+)-->", line)
        if not audio or "xiaoyuzhoufm.com/episode/" not in audio:
            continue
        rows.append({
            "episode_no": int(episode_no) if episode_no.isdigit() else None,
            "date": date,
            "duration": duration.strip()[:32],
            "title": compact(title.strip(), 240),
            "audio_url": audio,
            "guid": guid.group(1)[:128] if guid else sha256(normalize_url(audio))[:24],
            "index_status": compact(status.strip(), 80),
        })
    return rows


def build() -> dict:
    reports = load_reports()
    items: list[dict] = []
    seen: set[str] = set()

    for index_path in sorted(INDEX_DIR.glob("*.md")):
        slug = index_path.stem
        if slug not in SHOW_TITLES:
            continue
        show = SHOW_TITLES[slug]
        for row in parse_show_index(index_path):
            key = normalize_url(row["audio_url"])
            if key in seen:
                continue
            seen.add(key)
            report = reports.get(key)
            reported = report is not None
            canonical_path = report["path"] if report else ""
            report_id = sha256("everagent-report:" + canonical_path) if canonical_path else \
                sha256("everagent-podcast:" + row["guid"])
            items.append({
                "id": report_id,
                "guid": row["guid"],
                "study_state": "reported" if reported else "pending",
                "kind": "podcast_episode",
                "platform": "xiaoyuzhou",
                "show_slug": slug,
                "show": show,
                "episode_no": row["episode_no"],
                "date": row["date"],
                "duration": row["duration"],
                "title": row["title"],
                "audio_url": row["audio_url"],
                "index_status": row["index_status"],
                "report": {
                    "path": canonical_path,
                    "url": f"https://github.com/Everloster/EverAgent/blob/main/{canonical_path}" if canonical_path else "",
                    "raw_url": f"https://raw.githubusercontent.com/Everloster/EverAgent/main/{canonical_path}" if canonical_path else "",
                    "title": report["title"] if report else "",
                    "updated_on": report["updated_on"] if report else "",
                },
                "task": {
                    "target_worker": "razer",
                    "kind": "podcast_learning",
                    "ready": not reported,
                    "suggested_report_path": (
                        f"podcast-learning/reports/{row['date']}_xiaoyuzhou-{slug}_episode-{row['episode_no'] or 'x'}.md"
                    ),
                    "prompt": (
                        f"请按 podcast-learning 协议学习小宇宙节目《{row['title']}》。"
                        f"来源：{row['audio_url']}。"
                        "输出结构化学习报告：概览、关键论点、证据、疑问、行动项。"
                    ),
                },
            })

    items.sort(key=lambda item: (item["date"], item["episode_no"] or 0), reverse=True)
    return {
        "schema_version": 1,
        "source": "curated-xiaoyuzhou",
        "platform": "xiaoyuzhou",
        "items": items[:MAX_ITEMS],
    }


def main() -> int:
    manifest = build()
    OUTPUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reported = sum(1 for item in manifest["items"] if item["study_state"] == "reported")
    print(f"[podcast-manifest] {len(manifest['items'])} items; {reported} reported")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
