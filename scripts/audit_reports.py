#!/usr/bin/env python3
"""Audit EverAgent report artifacts with legacy-aware, changed-file gating.

The repository contains several generations of reports. Full-library audits surface
legacy debt without blocking work; newly added reports must use ``report-v2``.
Versioned reports are checked against their declared contract.

Usage:
    python3 scripts/audit_reports.py --all
    python3 scripts/audit_reports.py --all --json
    python3 scripts/audit_reports.py --changed
    python3 scripts/audit_reports.py --staged
    python3 scripts/audit_reports.py path/to/report.md
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .lint_evidence import lint_file as lint_evidence_file
    from .report_catalog import ROOT, collection_for_path, iter_reports, parse_frontmatter
    from .report_quality import (
        CURRENT_REPORT_SCHEMA,
        SUPPORTED_REPORT_SCHEMAS,
        evaluate_report as evaluate_report_quality,
        report_for_quality_artifact,
    )
except ImportError:  # Direct script execution.
    from lint_evidence import lint_file as lint_evidence_file
    from report_catalog import ROOT, collection_for_path, iter_reports, parse_frontmatter
    from report_quality import (
        CURRENT_REPORT_SCHEMA,
        SUPPORTED_REPORT_SCHEMAS,
        evaluate_report as evaluate_report_quality,
        report_for_quality_artifact,
    )


QUALITY_SCHEMA = CURRENT_REPORT_SCHEMA
REQUIRED_FIELDS = ("title", "domain", "report_type", "status", "updated_on")
CANONICAL_STATUSES = {
    "completed",
    "in_progress",
    "planned",
    "archived",
    "cached",
    "superseded",
    "degraded_shownotes_only",
}
LEARNING_DOMAINS = {
    "ai-learning",
    "cs-learning",
    "philosophy-learning",
    "psychology-learning",
    "biology-learning",
}
EVIDENCE_RE = re.compile(
    r"https?://|arxiv[:/. ]\s*\d{4}\.\d{4,5}|doi[:/. ]\s*10\.|\bRFC\s*\d+|"
    r"\[(?:代码|API|README|Web|原始材料|一手|二手|推测|待验证)\]|"
    r"(?:Table|Figure|Fig\.|§|p\.)\s*\d+",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(
    r"(?i:\bTODO\b|\bTBD\b|PLACEHOLDER)|待填写|待补充内容|\{[A-Z][A-Z0-9_]{2,}\}",
)
RELATIVE_LINK_RE = re.compile(r"\[[^\]]*\]\((\.\.?/[^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


def _git_paths(command: list[str]) -> set[Path]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        return set()
    return {ROOT / item for item in proc.stdout.split("\0") if item}


def _reports_from_paths(paths: set[Path]) -> list[Path]:
    reports: set[Path] = set()
    for path in paths:
        if collection_for_path(path):
            reports.add(path)
            continue
        report = report_for_quality_artifact(path)
        if report is not None and collection_for_path(report):
            reports.add(report)
    return sorted(reports)


def changed_reports() -> tuple[list[Path], set[Path]]:
    tracked = _git_paths(["git", "diff", "HEAD", "--name-only", "--diff-filter=ACMRTUXB", "-z"])
    added = _git_paths(["git", "diff", "HEAD", "--name-only", "--diff-filter=A", "-z"])
    untracked = _git_paths(["git", "ls-files", "-z", "--others", "--exclude-standard"])
    candidates = tracked | untracked
    reports = _reports_from_paths(candidates)
    return reports, {path.resolve() for path in added | untracked}


def staged_reports() -> tuple[list[Path], set[Path]]:
    staged = _git_paths(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTUXB", "-z"])
    added = _git_paths(["git", "diff", "--cached", "--name-only", "--diff-filter=A", "-z"])
    reports = _reports_from_paths(staged)
    return reports, {path.resolve() for path in added}


def _issue(severity: str, code: str, path: Path, message: str) -> Issue:
    try:
        display = str(path.resolve().relative_to(ROOT))
    except ValueError:
        display = str(path)
    return Issue(severity, code, display, message)


def _severity(enforce: bool, *, hard: bool = False) -> str:
    return "error" if enforce or hard else "warning"


def _has_frontmatter_close(text: str) -> bool:
    return text.startswith("---\n") and text.find("\n---", 4) >= 0


def _valid_date(value: object) -> bool:
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value or "")))


def _local_link_issues(path: Path, text: str, enforce: bool) -> list[Issue]:
    issues: list[Issue] = []
    for raw_target in RELATIVE_LINK_RE.findall(text):
        target = raw_target.strip().strip("<>").split("#", 1)[0]
        if not target or not re.search(r"\.(?:md|txt|json|csv|py|sh)$", target, re.I):
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            issues.append(
                _issue(_severity(enforce), "LINK001", path, f"相对链接目标不存在：{raw_target}")
            )
    return issues


def _wikilink_index() -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt"} and ".git" not in path.parts:
            index[path.stem].append(path)
    return index


def audit_file(path: Path, *, enforce: bool, wikilinks: dict[str, list[Path]]) -> list[Issue]:
    issues: list[Issue] = []
    collection = collection_for_path(path)
    if collection is None:
        return [_issue("error", "PATH001", path, "不属于已登记的报告目录")]

    text = path.read_text(encoding="utf-8", errors="replace")
    metadata = parse_frontmatter(text)
    status_value = str(metadata.get("status") or "").lower()
    completed = status_value not in {"in_progress", "planned"}
    schema_value = str(metadata.get("quality_schema") or "")
    versioned_schema = schema_value in SUPPORTED_REPORT_SCHEMAS
    strict_selection = enforce
    enforce = strict_selection or versioned_schema

    if not _has_frontmatter_close(text):
        issues.append(_issue(_severity(enforce), "META001", path, "缺少有效 frontmatter"))
    else:
        for field in REQUIRED_FIELDS:
            if not metadata.get(field):
                issues.append(_issue(_severity(enforce), "META002", path, f"缺少字段 {field}"))
        if metadata.get("domain") and metadata.get("domain") != collection.id:
            issues.append(
                _issue(
                    _severity(enforce),
                    "META003",
                    path,
                    f"domain={metadata.get('domain')} 与目录 {collection.id} 不一致",
                )
            )
        if metadata.get("updated_on") and not _valid_date(metadata.get("updated_on")):
            issues.append(_issue(_severity(enforce), "META004", path, "updated_on 不是 YYYY-MM-DD"))
        status = str(metadata.get("status") or "")
        if status and status not in CANONICAL_STATUSES:
            issues.append(_issue(_severity(enforce), "META005", path, f"非规范 status：{status}"))
        if schema_value and not versioned_schema:
            issues.append(_issue(_severity(enforce), "META006", path, f"未知 quality_schema：{schema_value}"))
        elif strict_selection and schema_value != QUALITY_SCHEMA:
            issues.append(
                _issue("error", "META006", path, f"新增报告需声明 quality_schema: {QUALITY_SCHEMA}")
            )
        if "semantic_tags" not in metadata:
            issues.append(_issue(_severity(enforce), "META007", path, "缺少 semantic_tags"))
        if strict_selection and schema_value == QUALITY_SCHEMA and not completed:
            issues.append(
                _issue("error", "META009", path, "新增 report-v2 报告必须完成复核并 finalize 后才能提交")
            )

    if not re.search(r"^#\s+\S", text, re.MULTILINE):
        issues.append(_issue(_severity(enforce), "STRUCT001", path, "缺少 H1 标题"))
    if len(text.encode("utf-8")) < 2000:
        issues.append(_issue("warning", "STRUCT002", path, "正文短于 2,000 bytes，需确认不是未完成草稿"))
    if completed and PLACEHOLDER_RE.search(text):
        issues.append(_issue(_severity(enforce), "STRUCT003", path, "completed 报告仍含模板占位符"))

    if collection.id in LEARNING_DOMAINS and "思考与追问" not in text:
        issues.append(_issue(_severity(enforce and completed), "LEARN001", path, "学习报告缺少“思考与追问”"))

    evidence_count = len(EVIDENCE_RE.findall(text))
    if completed and evidence_count == 0:
        issues.append(_issue(_severity(enforce), "EVID001", path, "completed 报告没有可识别证据锚点"))
    if enforce and collection.id == "github-trending-analyzer" and path.name.startswith("research_"):
        for marker in ("[API]", "[代码]"):
            if marker not in text:
                issues.append(_issue("error", "REPO001", path, f"深研报告缺少 {marker} 证据"))
    if enforce and collection.id == "podcast-learning":
        for section in ("## Limitations", "思考与追问"):
            if section not in text:
                issues.append(_issue("error", "POD001", path, f"播客报告缺少 {section}"))

    issues.extend(_local_link_issues(path, text, enforce))
    for target in WIKILINK_RE.findall(text):
        stem = Path(target.strip()).stem
        if stem in {"...", "…"} or "{" in target:
            continue
        if stem and stem not in wikilinks:
            issues.append(_issue(_severity(enforce), "LINK002", path, f"wikilink 无目标：[[{target}]]"))

    for warning in lint_evidence_file(path):
        issues.append(_issue("warning", "EVID900", path, warning))

    if schema_value == CURRENT_REPORT_SCHEMA and completed:
        quality_result = evaluate_report_quality(path)
        for finding in quality_result["errors"]:
            issues.append(_issue("error", finding["code"], path, finding["message"]))
        for finding in quality_result["warnings"]:
            issues.append(_issue("warning", finding["code"], path, finding["message"]))
    elif schema_value == CURRENT_REPORT_SCHEMA and not metadata.get("quality_tier"):
        issues.append(_issue(_severity(enforce), "QG002", path, "report-v2 草稿缺少 quality_tier"))
    return issues


def audit(paths: list[Path], *, strict_all: bool, new_paths: set[Path]) -> dict[str, object]:
    wikilinks = _wikilink_index()
    all_issues: list[Issue] = []
    domains: Counter[str] = Counter()
    titles: dict[str, list[Path]] = defaultdict(list)
    metadata_missing = 0
    current_schema_reports = 0
    versioned_reports = 0
    schema_counts: Counter[str] = Counter()

    for path in paths:
        collection = collection_for_path(path)
        if collection is None or not path.exists():
            continue
        domains[collection.id] += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        metadata = parse_frontmatter(text)
        if not metadata:
            metadata_missing += 1
        schema_value = str(metadata.get("quality_schema") or "")
        if schema_value:
            schema_counts[schema_value] += 1
        if schema_value in SUPPORTED_REPORT_SCHEMAS:
            versioned_reports += 1
        if schema_value == QUALITY_SCHEMA:
            current_schema_reports += 1
        title = str(metadata.get("title") or "")
        if not title:
            match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
            title = match.group(1).strip() if match else path.stem
        titles[title].append(path)
        all_issues.extend(
            audit_file(
                path,
                enforce=strict_all or path.resolve() in new_paths,
                wikilinks=wikilinks,
            )
        )

    for title, title_paths in titles.items():
        if len(title_paths) > 1:
            for path in title_paths:
                all_issues.append(_issue("warning", "CAT001", path, f"标题重复：{title}"))

    counts = Counter(issue.severity for issue in all_issues)
    codes = Counter(issue.code for issue in all_issues)
    issue_domains: dict[str, Counter[str]] = defaultdict(Counter)
    for issue in all_issues:
        collection = collection_for_path(ROOT / issue.path)
        issue_domains[collection.id if collection else "unknown"][issue.code] += 1
    return {
        "schema_version": 1,
        "quality_schema": QUALITY_SCHEMA,
        "reports_scanned": sum(domains.values()),
        "domains": dict(sorted(domains.items())),
        "metadata_missing": metadata_missing,
        "current_schema_reports": current_schema_reports,
        "versioned_reports": versioned_reports,
        "legacy_reports": sum(domains.values()) - versioned_reports,
        "quality_schema_counts": dict(sorted(schema_counts.items())),
        "errors": counts["error"],
        "warnings": counts["warning"],
        "issue_codes": dict(sorted(codes.items())),
        "issue_codes_by_domain": {
            domain: dict(sorted(domain_counts.items()))
            for domain, domain_counts in sorted(issue_domains.items())
        },
        "issues": [asdict(issue) for issue in all_issues],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit EverAgent reports")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", action="store_true", help="audit every registered report")
    scope.add_argument("--changed", action="store_true", help="audit changed and untracked reports")
    scope.add_argument("--staged", action="store_true", help="audit reports staged for commit")
    parser.add_argument("--strict", action="store_true", help="apply current contract to every selected report")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--summary-only", action="store_true", help="print totals without individual warnings")
    parser.add_argument("paths", nargs="*", help="explicit report paths")
    args = parser.parse_args()

    new_paths: set[Path] = set()
    if args.paths:
        paths = [Path(item) if Path(item).is_absolute() else ROOT / item for item in args.paths]
        new_paths = {
            path.resolve()
            for path in paths
            if not _git_paths(
                ["git", "ls-files", "-z", "--error-unmatch", str(path.relative_to(ROOT))]
            )
        }
    elif args.all:
        paths = [path for _collection, path in iter_reports()]
    elif args.staged:
        paths, new_paths = staged_reports()
    else:
        paths, new_paths = changed_reports()

    result = audit(paths, strict_all=args.strict, new_paths=new_paths)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(
            f"审计 {result['reports_scanned']} 篇：ERROR {result['errors']}｜"
            f"WARN {result['warnings']}｜缺 frontmatter {result['metadata_missing']}"
        )
        if not args.summary_only:
            for issue in result["issues"]:
                symbol = "✗" if issue["severity"] == "error" else "⚠"
                print(f"  {symbol} {issue['code']} {issue['path']}: {issue['message']}")

    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
