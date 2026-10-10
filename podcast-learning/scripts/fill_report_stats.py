#!/usr/bin/env python3
"""报告 frontmatter 统计校验：从三件套实际文件统计字数/段数，核对并写回。

消灭手填数字（2026-10-09 实证：两篇报告的 polished 字数靠目测写错）。
事实源是 transcript/polished 文件本身；frontmatter 与实际不一致时以实际为准改写。

- transcript_path / polished_transcript_path 支持：单路径、多路径（、/，分隔）、
  glob 前缀（含 *）、路径后带中文注释（取括号前）
- 校验项：hanzi_chars / total_chars / transcript_segments / speech_rate_cjk
- 幂等；--dry-run 只报差异不写

用法：python3 scripts/fill_report_stats.py [报告文件...] [--dry-run]
不传参数则校验 reports/ 全部（含历史报告，可顺手清理存量错误）。
"""

import argparse
import glob
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"


def parse_paths(raw: str) -> list[pathlib.Path]:
    """'a.txt（注释）、b*.txt' → 实际文件列表；支持「前缀 xxx」注释语义。"""
    if not raw:
        return []
    # 「前缀 xxx」注释：按前缀 glob（cross_episode 多文件场景）
    m = re.search(r"前缀\s*[\w./-]+", raw)
    if m:
        prefix = m.group(0)[2:].strip()
        hits = sorted(glob.glob(str(ROOT / "reports" / "transcripts" / f"{prefix}*")))
        if hits:
            return [pathlib.Path(h) for h in hits]
    raw = re.split(r"[（(]", raw)[0].strip()  # 去尾部中文注释
    paths: list[pathlib.Path] = []
    for part in re.split(r"[、,，]", raw):
        part = part.strip()
        if not part:
            continue
        base = ROOT.parent / part if not (ROOT / part).exists() else ROOT / part
        hits = sorted(glob.glob(str(base)))
        if hits:
            paths.extend(pathlib.Path(h) for h in hits)
    return [p for p in paths if p.exists()]


def stats(paths: list[pathlib.Path]) -> dict:
    hanzi = total = segs = 0
    for p in paths:
        t = p.read_text(encoding="utf-8", errors="replace")
        hanzi += len(re.findall(r"[一-鿿]", t))
        total += len(t)
        segs += len(re.findall(r"\[\d+:\d+:\d+ -> ", t))
    return {"hanzi": hanzi, "total": total, "segs": segs}


def check(report: pathlib.Path, dry: bool) -> list[str]:
    text = report.read_text(encoding="utf-8")
    fm = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not fm:
        return [f"{report.name}: 无 frontmatter，跳过"]
    block, rest = fm.group(1), text[fm.end():]
    fixes, diffs = [], []

    tr = stats(parse_paths(re.search(r"^transcript_path:\s*(.+)$", block, re.M).group(1) if re.search(r"^transcript_path:\s*(.+)$", block, re.M) else ""))
    po = stats(parse_paths(re.search(r"^polished_transcript_path:\s*(.+)$", block, re.M).group(1) if re.search(r"^polished_transcript_path:\s*(.+)$", block, re.M) else ""))

    pairs = [
        (r"hanzi_chars_raw", tr["hanzi"]), (r"total_chars_raw", tr["total"]),
        (r"transcript_segments", tr["segs"]),
        (r"hanzi_chars_polished", po["hanzi"]), (r"total_chars_polished", po["total"]),
    ]
    for key, actual in pairs:
        if not tr["segs"] and key.endswith(("_raw", "_segments")):
            continue
        if not po["hanzi"] and "polished" in key:
            continue
        m = re.search(rf"^{key}:\s*(\d+)", block, re.M)
        old = int(m.group(1)) if m else None
        if old != actual:
            diffs.append(f"{key}: {old} → {actual}")
            if m:
                block = re.sub(rf"^{key}:\s*\d+", f"{key}: {actual}", block, flags=re.M)
            else:
                block += f"\n{key}: {actual}"
    # 语速（需 duration_seconds）
    m = re.search(r"^duration_seconds:\s*(\d+)", block, re.M)
    if m and tr["hanzi"] and int(m.group(1)) > 0:
        rate = round(tr["hanzi"] / (int(m.group(1)) / 60))
        m2 = re.search(r'^speech_rate_cjk:\s*"?(\d+)', block, re.M)
        if m2 and abs(int(m2.group(1)) - rate) > 2:
            diffs.append(f"speech_rate_cjk: {m2.group(1)} → {rate}")
            block = re.sub(r'^speech_rate_cjk:\s*".*?"', f'speech_rate_cjk: "{rate} 字/min"', block, flags=re.M)

    if diffs and not dry:
        report.write_text("---\n" + block + "\n---\n" + rest, encoding="utf-8")
    tag = "[dry] " if dry else ""
    print(f"{tag}{report.name}: " + ("；".join(diffs) if diffs else "✓ 一致"))
    return diffs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*", help="报告文件名（reports/ 下）；缺省全量")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    targets = [REPORTS / f for f in args.files] if args.files else sorted(REPORTS.glob("*.md"))
    bad = sum(1 for r in targets if check(r, args.dry_run))
    print(f"\n共 {len(targets)} 篇，{bad if args.dry_run else '已修正 ' + str(bad)} 篇存在差异")
    return 0


if __name__ == "__main__":
    sys.exit(main())
