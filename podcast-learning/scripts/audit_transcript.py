#!/usr/bin/env python3
"""审计播客 transcript：哈希、段数、时间戳单调性、连续重复与头尾边界。"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

STAMP_RE = re.compile(
    r"^\[(\d+):(\d+):(\d+) -> (\d+):(\d+):(\d+)\]\s*(.*)$"
)


def seconds(hours: str, minutes: str, secs: str) -> int:
    return int(hours) * 3600 + int(minutes) * 60 + int(secs)


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit(path: pathlib.Path, max_consecutive: int) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    lines = raw.splitlines()
    errors: list[str] = []
    warnings: list[str] = []
    segments = []
    malformed = []
    previous_start = -1
    previous_text = None
    current_run = 0
    longest_run = 0
    longest_text = ""

    for line_number, line in enumerate(lines, 1):
        match = STAMP_RE.match(line)
        if not match:
            if line.strip():
                malformed.append(line_number)
            continue
        start = seconds(*match.groups()[:3])
        end = seconds(*match.groups()[3:6])
        text = re.sub(r"\s+", " ", match.group(7)).strip()
        if end < start:
            errors.append(f"line {line_number}: end timestamp precedes start")
        if start < previous_start:
            errors.append(f"line {line_number}: start timestamp is not monotonic")
        previous_start = start
        if text and text == previous_text:
            current_run += 1
        else:
            current_run = 1 if text else 0
            previous_text = text or None
        if current_run > longest_run:
            longest_run = current_run
            longest_text = text
        segments.append({"start": start, "end": end, "text": text})

    if not segments:
        errors.append("no timestamped segments")
    if malformed:
        warnings.append(f"{len(malformed)} non-empty lines lack transcript timestamps")
    if longest_run > max_consecutive:
        errors.append(
            f"max consecutive identical text is {longest_run} (> {max_consecutive}): "
            f"{longest_text[:80]}"
        )
    if segments and len(segments) >= 2:
        tail_gap = segments[-1]["start"] - segments[-2]["end"]
        if tail_gap > 30:
            warnings.append(f"last segment starts after a {tail_gap}s gap; inspect possible outro")

    return {
        "path": str(path),
        "ok": not errors,
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
        "lines": len(lines),
        "segments": len(segments),
        "duration_seconds": segments[-1]["end"] if segments else None,
        "max_consecutive_identical": longest_run,
        "head": lines[:3],
        "tail": lines[-3:],
        "warnings": warnings,
        "errors": errors,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=pathlib.Path)
    parser.add_argument("--max-consecutive", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    results = [audit(path.resolve(), args.max_consecutive) for path in args.files]
    if args.json:
        print(json.dumps({"schema_version": 1, "results": results}, ensure_ascii=False, indent=2))
    else:
        for item in results:
            status = "PASS" if item["ok"] else "FAIL"
            print(
                f"{status} {item['path']}｜segments={item['segments']}｜"
                f"duration={item['duration_seconds']}s｜max_repeat={item['max_consecutive_identical']}"
            )
            for warning in item["warnings"]:
                print(f"  WARN {warning}")
            for error in item["errors"]:
                print(f"  ERROR {error}")
    return 0 if all(item["ok"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
