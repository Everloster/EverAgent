#!/usr/bin/env python3
"""
GitHub Trending Reports Validator
Validates reports in github-trending-reports/ against TASK_PROTOCOL.md standards.

Checks:
  V-NAME    Naming: research_{owner}_{repo}.md — no date suffix, underscores only as separator
  V-STRUCT  All 7 required Chinese chapters present
  V-LEN     Total lines >= 150
  V-PREC    No fuzzy numbers (e.g., "17,000+", "1.2万+")
  V-COMP    >= 2 competitors in 竞品对比 section
  V-FOOTER  Standard footer: *报告生成时间* + *研究方法*
  V-PATH    No host machine paths (/tmp/, /sessions/, /mnt/, /Users/, /home/)
  V-LANG    No English template markers (Executive Summary, Confidence Assessment, etc.)
  V-INDEX   File vs knowledge/reports_index.md consistency (only with --index flag)

Usage:
  python3 scripts/validate_reports.py                  # Validate all research_*.md
  python3 scripts/validate_reports.py owner/repo       # Validate one report
  python3 scripts/validate_reports.py --json           # JSON output
  python3 scripts/validate_reports.py --index          # Include index consistency check
  python3 scripts/validate_reports.py --fail-only      # Show only failed reports

Exit codes:
  0  All checks passed
  1  One or more checks failed
  2  Usage/setup error
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


# ── Project paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
REPORTS_DIR = PROJECT_ROOT / "github-trending-reports"
INDEX_FILE = PROJECT_ROOT / "knowledge" / "reports_index.md"


# ── Check constants ────────────────────────────────────────────────────────────
REQUIRED_CHAPTERS = [
    "## 项目概述",
    "## 基本信息",
    "## 技术分析",
    "## 社区活跃度",
    "## 发展趋势",
    "## 竞品对比",
    "## 总结评价",
]

MIN_LINES = 150
MIN_COMPETITORS = 2

ENGLISH_MARKERS = [
    "Executive Summary",
    "Confidence Level",
    "Confidence Assessment",
    "Chronological Timeline",
    "Key Stakeholders",
    "Research Methodology",
    "## Overview",
    "## Background",
]

HOST_PATH_RE = re.compile(r"(?:/tmp/|/sessions/|/mnt/)[^\s\"'`]")
# Match large numbers with + suffix: "17,000+" "1,200+" but not "C++" or "v1.0+"
FUZZY_NUMBER_RE = re.compile(r"\b\d[\d,]{2,}\+")
FOOTER_TIME_RE = re.compile(r"\*报告生成时间:\s*\d{4}-\d{2}-\d{2}")
FOOTER_METHOD_RE = re.compile(r"\*研究方法:\s*github-deep-research 多轮深度研究\*")
DATE_SUFFIX_RE = re.compile(r"research_.+_\d{4}[-_]\d{2}[-_]\d{2}\.md$")
VALID_NAME_RE = re.compile(r"^research_[^_].+_.+\.md$")

# Competitor table data row: starts with |, has content, not a header/separator row
COMP_TABLE_ROW_RE = re.compile(r"^\|[^|]+\|")
COMP_SEPARATOR_RE = re.compile(r"^\|[\s\-|:]+\|$")


class CheckResult:
    def __init__(
        self,
        check_id: str,
        passed: bool,
        message: str,
        details: Optional[List[str]] = None,
    ):
        self.check_id = check_id
        self.passed = passed
        self.message = message
        self.details = details or []

    def to_dict(self) -> dict:
        d = {"check": self.check_id, "passed": self.passed, "message": self.message}
        if self.details:
            d["details"] = self.details
        return d


class ReportValidator:
    def __init__(self, report_path: Path):
        self.path = report_path
        self.name = report_path.name
        self.content = report_path.read_text(encoding="utf-8")
        self.lines = self.content.splitlines()

    # ── V-NAME ─────────────────────────────────────────────────────────────────
    def check_naming(self) -> CheckResult:
        """Naming: research_{owner}_{repo}.md — no date suffix."""
        name = self.name

        if not name.startswith("research_"):
            return CheckResult("V-NAME", False, f"Must start with 'research_': {name}")

        if DATE_SUFFIX_RE.search(name):
            return CheckResult("V-NAME", False, f"Date suffix not allowed: {name}")

        if not VALID_NAME_RE.match(name):
            return CheckResult("V-NAME", False, f"Cannot parse owner/repo from: {name}")

        return CheckResult("V-NAME", True, "Naming OK")

    # ── V-STRUCT ───────────────────────────────────────────────────────────────
    def check_structure(self) -> CheckResult:
        """All 7 required Chinese chapters must be present."""
        missing = [ch for ch in REQUIRED_CHAPTERS if ch not in self.content]
        if missing:
            return CheckResult(
                "V-STRUCT", False, f"Missing {len(missing)} chapter(s)", missing
            )
        return CheckResult("V-STRUCT", True, "All 7 chapters present")

    # ── V-LEN ──────────────────────────────────────────────────────────────────
    def check_length(self) -> CheckResult:
        """Total lines >= 150."""
        n = len(self.lines)
        if n < MIN_LINES:
            return CheckResult(
                "V-LEN", False, f"Too short: {n} lines (min {MIN_LINES})"
            )
        return CheckResult("V-LEN", True, f"Length OK: {n} lines")

    # ── V-PREC ─────────────────────────────────────────────────────────────────
    def check_precision(self) -> CheckResult:
        """No fuzzy large numbers like '17,000+'."""
        issues = []
        for i, line in enumerate(self.lines, 1):
            if FUZZY_NUMBER_RE.search(line):
                issues.append(f"Line {i}: {line.strip()[:100]}")
        if issues:
            return CheckResult(
                "V-PREC", False, f"Fuzzy numbers in {len(issues)} line(s)", issues[:5]
            )
        return CheckResult("V-PREC", True, "No fuzzy numbers")

    # ── V-COMP ─────────────────────────────────────────────────────────────────
    def check_competitors(self) -> CheckResult:
        """竞品对比 section must have >= 2 data rows."""
        in_section = False
        data_rows = 0

        for line in self.lines:
            if "## 竞品对比" in line:
                in_section = True
                continue
            if in_section and line.startswith("## "):
                break
            if not in_section:
                continue
            stripped = line.strip()
            if not stripped or not stripped.startswith("|"):
                continue
            # Skip separator rows like |---|---|
            if COMP_SEPARATOR_RE.match(stripped):
                continue
            # Skip header rows that contain column names (heuristic: 竞品/项目/名称/对比)
            header_keywords = {"竞品", "项目名", "名称", "对比项", "工具", "方案"}
            if any(kw in stripped for kw in header_keywords):
                continue
            if COMP_TABLE_ROW_RE.match(stripped):
                data_rows += 1

        if data_rows < MIN_COMPETITORS:
            return CheckResult(
                "V-COMP",
                False,
                f"Too few competitors: {data_rows} data row(s) (min {MIN_COMPETITORS})",
            )
        return CheckResult("V-COMP", True, f"Competitors OK: {data_rows} found")

    # ── V-FOOTER ───────────────────────────────────────────────────────────────
    def check_footer(self) -> CheckResult:
        """Standard footer: *报告生成时间* and *研究方法: github-deep-research 多轮深度研究*."""
        issues = []
        if not FOOTER_TIME_RE.search(self.content):
            issues.append("Missing: *报告生成时间: YYYY-MM-DD*")
        if not FOOTER_METHOD_RE.search(self.content):
            issues.append("Missing/wrong: *研究方法: github-deep-research 多轮深度研究*")
        if issues:
            return CheckResult("V-FOOTER", False, "Footer format incorrect", issues)
        return CheckResult("V-FOOTER", True, "Footer OK")

    # ── V-PATH ─────────────────────────────────────────────────────────────────
    def check_paths(self) -> CheckResult:
        """No host machine absolute paths in report content."""
        # Also check /Users/ and /home/ with word chars after slash
        extended_re = re.compile(
            r"(?:/tmp/|/sessions/|/mnt/|/Users/\w|/home/\w)[^\s\"'`]*"
        )
        issues = []
        for i, line in enumerate(self.lines, 1):
            if extended_re.search(line):
                issues.append(f"Line {i}: {line.strip()[:100]}")
        if issues:
            return CheckResult(
                "V-PATH", False, f"Host paths in {len(issues)} line(s)", issues[:3]
            )
        return CheckResult("V-PATH", True, "No host paths")

    # ── V-LANG ─────────────────────────────────────────────────────────────────
    def check_language(self) -> CheckResult:
        """No English template markers from github-deep-research raw output."""
        found = [m for m in ENGLISH_MARKERS if m in self.content]
        if found:
            return CheckResult(
                "V-LANG",
                False,
                "English template markers found",
                found,
            )
        return CheckResult("V-LANG", True, "No English template markers")

    # ── Run all ────────────────────────────────────────────────────────────────
    def run_all(self) -> List[CheckResult]:
        return [
            self.check_naming(),
            self.check_structure(),
            self.check_length(),
            self.check_precision(),
            self.check_competitors(),
            self.check_footer(),
            self.check_paths(),
            self.check_language(),
        ]


# ── V-INDEX ────────────────────────────────────────────────────────────────────
def check_index_consistency() -> List[CheckResult]:
    """Validate file vs knowledge/reports_index.md consistency."""
    if not INDEX_FILE.exists():
        return [CheckResult("V-INDEX", False, f"Index file not found: {INDEX_FILE}")]

    # Collect actual repo identifiers from filenames
    actual: Dict[str, str] = {}  # "owner/repo" -> filename
    for f in REPORTS_DIR.glob("research_*.md"):
        stem = f.name[len("research_") : -len(".md")]
        # Split on first underscore to get owner, rest is repo
        parts = stem.split("_", 1)
        if len(parts) == 2:
            key = f"{parts[0]}/{parts[1]}"
            actual[key] = f.name

    # Parse index entries
    index_content = INDEX_FILE.read_text(encoding="utf-8")
    index_repos: set = set()
    in_repo_section = False
    for line in index_content.splitlines():
        if "## Repository Deep Reports" in line:
            in_repo_section = True
            continue
        if in_repo_section and line.startswith("## "):
            break
        if in_repo_section and line.startswith("- ") and "/" in line:
            repo = line[2:].strip()
            index_repos.add(repo)

    actual_set = set(actual.keys())
    missing_from_index = actual_set - index_repos
    orphaned_in_index = index_repos - actual_set

    results = []
    if missing_from_index:
        results.append(
            CheckResult(
                "V-INDEX",
                False,
                f"{len(missing_from_index)} file(s) not in index",
                sorted(missing_from_index),
            )
        )
    if orphaned_in_index:
        results.append(
            CheckResult(
                "V-INDEX",
                False,
                f"{len(orphaned_in_index)} index entry(ies) have no file",
                sorted(orphaned_in_index),
            )
        )
    if not missing_from_index and not orphaned_in_index:
        results.append(
            CheckResult(
                "V-INDEX",
                True,
                f"Index consistent: {len(actual_set)} files ↔ {len(index_repos)} entries",
            )
        )
    return results


# ── Formatting ─────────────────────────────────────────────────────────────────
def format_file_result(path: Path, results: List[CheckResult]) -> str:
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    status = "PASS" if passed == total else "FAIL"
    lines = [f"[{status}] {path.name}  ({passed}/{total})"]
    for r in results:
        icon = "✓" if r.passed else "✗"
        lines.append(f"  {icon} {r.check_id}: {r.message}")
        for d in r.details[:3]:
            lines.append(f"      → {d}")
    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    raw_args = sys.argv[1:]
    json_mode = "--json" in raw_args
    check_index = "--index" in raw_args
    fail_only = "--fail-only" in raw_args
    positional = [a for a in raw_args if not a.startswith("--")]

    # Resolve target files
    if positional:
        target = positional[0]
        if "/" not in target:
            print(f"ERROR: Expected owner/repo, got: {target}", file=sys.stderr)
            sys.exit(2)
        owner, repo = target.split("/", 1)
        report_path = REPORTS_DIR / f"research_{owner}_{repo}.md"
        if not report_path.exists():
            print(f"ERROR: Not found: {report_path}", file=sys.stderr)
            sys.exit(2)
        report_files = [report_path]
    else:
        report_files = sorted(REPORTS_DIR.glob("research_*.md"))

    if not report_files:
        print(f"ERROR: No research_*.md files in {REPORTS_DIR}", file=sys.stderr)
        sys.exit(2)

    # Run validators
    all_results: Dict[str, List[CheckResult]] = {}
    for path in report_files:
        validator = ReportValidator(path)
        all_results[path.name] = validator.run_all()

    # Index check
    index_results: List[CheckResult] = []
    if check_index:
        index_results = check_index_consistency()

    # Compute totals
    total_pass = sum(
        1 for results in all_results.values() for r in results if r.passed
    ) + sum(1 for r in index_results if r.passed)
    total_fail = sum(
        1 for results in all_results.values() for r in results if not r.passed
    ) + sum(1 for r in index_results if not r.passed)

    if json_mode:
        output = {
            "summary": {
                "files": len(report_files),
                "checks_passed": total_pass,
                "checks_failed": total_fail,
                "overall": "PASS" if total_fail == 0 else "FAIL",
            },
            "reports": {
                name: [r.to_dict() for r in results]
                for name, results in all_results.items()
            },
        }
        if check_index:
            output["index"] = [r.to_dict() for r in index_results]
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        failed_files = [
            (REPORTS_DIR / name, results)
            for name, results in all_results.items()
            if any(not r.passed for r in results)
        ]
        passed_files = [
            (REPORTS_DIR / name, results)
            for name, results in all_results.items()
            if all(r.passed for r in results)
        ]

        if failed_files:
            print(f"\n{'='*60}")
            print(f"FAILED ({len(failed_files)}/{len(report_files)} files):")
            print(f"{'='*60}")
            for path, results in failed_files:
                print(format_file_result(path, results))
                print()
        if not fail_only and passed_files:
            print(f"\n{'='*60}")
            print(f"PASSED ({len(passed_files)}/{len(report_files)} files):")
            print(f"{'='*60}")
            for path, results in passed_files:
                print(f"  ✓ {path.name}")

        if check_index:
            print(f"\n{'='*60}")
            print("INDEX CONSISTENCY:")
            print(f"{'='*60}")
            for r in index_results:
                icon = "✓" if r.passed else "✗"
                print(f"  {icon} {r.check_id}: {r.message}")
                for d in r.details[:10]:
                    print(f"      → {d}")

        print(
            f"\nSummary: {total_pass} passed, {total_fail} failed"
            f" across {len(report_files)} report file(s)"
        )

    sys.exit(0 if total_fail == 0 else 1)


if __name__ == "__main__":
    main()
