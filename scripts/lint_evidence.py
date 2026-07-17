#!/usr/bin/env python3
"""Evidence-density linter for EverAgent reports.

A self-check tool, not a gate. Flags reports that "look like" deep analysis
but lack precise evidence: missing numbers in paper analyses, missing
verifiable citations (URL / arXiv / DOI / RFC) for post-cutoff claims in
knowledge reports, missing citations in text analyses.

Usage:
    python3 scripts/lint_evidence.py path/to/report.md [more.md ...]
    python3 scripts/lint_evidence.py --domain ai-learning
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FUZZY = [
    "显著提升", "显著提高", "显著改善", "大幅提升", "大幅提高", "大幅改善",
    "研究表明", "实验证明", "结果显示", "多家博客", "有报告称", "显著差异",
]
SPEC_MARKERS = ["[推测]", "[待验证]", "[未验证]", "[动物实验]", "[体外实验]", "[初步"]
# 可核实引用 = URL 或稳定标识符（arXiv / DOI / RFC）。这些都能让读者事后独立复核，
# 因此在证据密度检查里等价于 URL；只认 http(s) 会对引 arXiv 的报告产生假阳性。
URL_RE = re.compile(r"https?://\S+")
ARXIV_RE = re.compile(r"arxiv[:/]\s*\d{4}\.\d{4,5}|arxiv\.org/abs/", re.I)
DOI_RE = re.compile(r"doi[:\s]\s*10\.\d{4,9}/|doi\.org/10\.", re.I)
RFC_RE = re.compile(r"\bRFC\s?\d{3,5}\b", re.I)
NUM_RE = re.compile(
    r"\d+\.\d+|%|n\s*=\s*\d+|N\s*=\s*\d+|Table\s+\d|Figure\s+\d|Fig\.\s*\d|p\s*[<=>]\s*0?\.\d+"
)
RECENT_RE = re.compile(r"202[4-9]")
CITE_RE = re.compile(r"[a-z]+\d+[a-e]?|Ch\.\s*\d+|§\s*\d+|p\.\s*\d+|》|“|\"")


def infer_type(path: Path) -> str:
    p = str(path).lower()
    if "paper_analyses" in p:
        return "paper_analysis"
    if "text_analyses" in p:
        return "text_analysis"
    if "knowledge_reports" in p or "concept_reports" in p:
        return "knowledge_report"
    return "other"


def lint_file(path: Path) -> list[str]:
    warns: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [f"cannot read {path}"]

    rtype = infer_type(path)
    fuzzy = sum(text.count(f) for f in FUZZY)
    nums = len(NUM_RE.findall(text))
    urls = len(URL_RE.findall(text))
    # 可核实引用总数：URL + arXiv + DOI + RFC。任一形式都足以让读者复核来源。
    cites = urls + len(ARXIV_RE.findall(text)) + len(DOI_RE.findall(text)) + len(RFC_RE.findall(text))
    has_marker = any(m in text for m in SPEC_MARKERS)

    if rtype == "paper_analysis":
        if nums < 2:
            warns.append(f"only {nums} precise numbers (expect ≥2: %, decimals, n=, Table/Fig, p)")
        if fuzzy > 3 and nums < 5:
            warns.append(f"{fuzzy} fuzzy phrases with only {nums} precise numbers")
    elif rtype == "knowledge_report":
        if RECENT_RE.search(text) and cites == 0:
            warns.append("mentions 2024+ events but 0 verifiable citations (URL/arXiv/DOI/RFC — verify via WebSearch)")
        if fuzzy > 5 and cites == 0 and not has_marker:
            warns.append(f"{fuzzy} source-free fuzzy phrases, 0 verifiable citations, no speculation markers")
    elif rtype == "text_analysis":
        if len(CITE_RE.findall(text)) < 4:
            warns.append("few citation markers (page/section numbers or direct quotations)")

    return warns


def collect(args: argparse.Namespace) -> list[Path]:
    if args.domain:
        base = ROOT / args.domain / "reports"
        return sorted(p for p in base.rglob("*.md") if p.is_file())
    return [Path(p) for p in args.paths]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evidence-density linter")
    parser.add_argument("paths", nargs="*", help="report .md files")
    parser.add_argument("--domain", help="lint all reports under a domain")
    args = parser.parse_args()

    files = collect(args)
    if not files:
        print("no files to lint")
        return 0

    flagged = 0
    for f in files:
        warns = lint_file(f)
        if warns:
            flagged += 1
            rel = f.relative_to(ROOT) if f.is_absolute() and str(f).startswith(str(ROOT)) else f
            print(f"[WARN] {rel}")
            for w in warns:
                print(f"   - {w}")
    print(f"\nlinted {len(files)} files, {flagged} flagged (warnings only, non-blocking)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
