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
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from .lint_evidence import lint_file as lint_evidence_file
    from .report_catalog import ROOT, collection_for_path, iter_reports, metadata_alias_issues, parse_frontmatter
    from .report_quality import (
        CURRENT_REPORT_SCHEMA,
        SUPPORTED_REPORT_SCHEMAS,
        evaluate_report as evaluate_report_quality,
        report_for_quality_artifact,
    )
except ImportError:  # Direct script execution.
    from lint_evidence import lint_file as lint_evidence_file
    from report_catalog import ROOT, collection_for_path, iter_reports, metadata_alias_issues, parse_frontmatter
    from report_quality import (
        CURRENT_REPORT_SCHEMA,
        SUPPORTED_REPORT_SCHEMAS,
        evaluate_report as evaluate_report_quality,
        report_for_quality_artifact,
    )


# 领域目录带连字符，按固定仓内模块路径加载；不改变 sys.path 或执行外部生产器。
_podcast_spec = importlib.util.spec_from_file_location(
    "everagent_podcast_audit", Path(__file__).resolve().parents[1] / "podcast-learning/scripts/audit_transcript.py"
)
assert _podcast_spec and _podcast_spec.loader
podcast_audit = importlib.util.module_from_spec(_podcast_spec)
_podcast_spec.loader.exec_module(podcast_audit)

QUALITY_SCHEMA = CURRENT_REPORT_SCHEMA
REQUIRED_FIELDS = ("title", "domain", "report_type", "status", "updated_on")
PODCAST_DEPTH_SINCE = "2026-10-20"
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


def _git_ref(ref: str) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", ref],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _git_is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT,
        capture_output=True,
        check=False,
    ).returncode == 0


def _podcast_dependencies(path: Path) -> set[Path]:
    text = path.read_text(encoding="utf-8", errors="replace")
    dependencies = podcast_audit.report_sources(ROOT, parse_frontmatter(text))
    for target in RELATIVE_LINK_RE.findall(text):
        candidate = (path.parent / target.split("#", 1)[0]).resolve()
        if candidate.is_relative_to(ROOT / "podcast-learning/reports/transcripts"):
            dependencies.add(candidate)
    # evidence 中的 local 来源也能触发反向审计；不读取任何仓外来源。
    evidence = path.parent / ".quality" / f"{path.stem}.evidence.json"
    if evidence.is_file():
        dependencies.add(evidence)
        try:
            manifest = json.loads(evidence.read_text(encoding="utf-8"))
            for source in manifest.get("sources", []):
                if isinstance(source, dict) and source.get("kind") == "local":
                    candidate = (ROOT / str(source.get("locator") or "")).resolve()
                    if candidate.is_relative_to(ROOT / "podcast-learning/reports/transcripts"):
                        dependencies.add(candidate)
        except (OSError, ValueError, AttributeError, TypeError):
            pass  # report-v2 的质量门负责报告损坏的 evidence。
    return dependencies


def _reports_from_paths(paths: set[Path]) -> list[Path]:
    reports: set[Path] = set()
    for path in paths:
        if collection_for_path(path):
            reports.add(path)
            continue
        report = report_for_quality_artifact(path)
        if report is not None and collection_for_path(report):
            reports.add(report)
    # 转写、润色稿、收据变化（含删除）不能绕过只看 .md 的入口。
    for report in (ROOT / "podcast-learning/reports").glob("*.md"):
        if _podcast_dependencies(report) & paths:
            reports.add(report)
    return sorted(reports)


def changed_reports() -> tuple[list[Path], set[Path]]:
    tracked = _git_paths(["git", "diff", "HEAD", "--name-only", "--diff-filter=ACDMRTUXB", "-z"])
    added = _git_paths(["git", "diff", "HEAD", "--name-only", "--diff-filter=A", "-z"])
    untracked = _git_paths(["git", "ls-files", "-z", "--others", "--exclude-standard"])
    candidates = tracked | untracked
    reports = _reports_from_paths(candidates)
    return reports, {path.resolve() for path in added | untracked}


def staged_reports() -> tuple[list[Path], set[Path]]:
    staged = _git_paths(["git", "diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB", "-z"])
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


def _date_on_or_after(value: object, threshold: str) -> bool:
    text = str(value or "")
    return bool(_valid_date(text) and text >= threshold)


def _prose_for_placeholder_scan(text: str) -> str:
    """Ignore code examples when looking for unfinished template markers."""
    without_fences = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]+`", "", without_fences)


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


def _wikilink_exists(path: Path, target: str, index: dict[str, list[Path]]) -> bool:
    target = target.strip()
    name = re.sub(r"\.(?:md|txt)$", "", target)
    if "/" not in name:
        return bool(index.get(name))
    # 限定路径必须真正命中，不允许以别处同 basename 页面蒙混通过。
    collection = collection_for_path(path)
    bases = [ROOT, path.parent]
    if collection:
        bases.extend((ROOT / collection.id, ROOT / collection.id / "wiki"))
    candidates = index.get(Path(name).name, [])
    for base in bases:
        for suffix in ("", ".md", ".txt"):
            expected = (base / (name + suffix)).resolve()
            if expected.is_relative_to(ROOT) and any(candidate.resolve() == expected for candidate in candidates):
                return True
    return False


def audit_file(
    path: Path, *, enforce: bool, wikilinks: dict[str, list[Path]], source_enforce: bool | None = None
) -> list[Issue]:
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
    source_enforce = strict_selection if source_enforce is None else source_enforce
    enforce = strict_selection or versioned_schema

    if enforce and schema_value == QUALITY_SCHEMA:
        for message in metadata_alias_issues(metadata):
            issues.append(_issue(_severity(strict_selection or source_enforce), "META010", path, message))

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
    if completed and PLACEHOLDER_RE.search(_prose_for_placeholder_scan(text)):
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
        report_depth = str(metadata.get("report_depth") or "")
        depth_contract_required = strict_selection and _date_on_or_after(
            metadata.get("updated_on"), PODCAST_DEPTH_SINCE
        )
        if depth_contract_required and not report_depth:
            issues.append(_issue("error", "POD002", path, "新增播客报告缺少 report_depth"))
        if report_depth and report_depth not in {"brief", "standard", "deep"}:
            issues.append(_issue("error", "POD002", path, f"未知 report_depth：{report_depth}"))
        if (depth_contract_required or report_depth) and metadata.get("reader_contract") != "standalone":
            issues.append(_issue("error", "POD003", path, "播客报告需声明 reader_contract: standalone"))
        if report_depth in {"standard", "deep"}:
            if "## 内容地图" not in text:
                issues.append(_issue("error", "POD004", path, "standard/deep 播客缺少内容地图"))
            subsection_count = len(re.findall(r"^###\s+\S", text, re.MULTILINE))
            mainline_h2_count = len(
                re.findall(r"^##\s+主线(?:[一二三四五六七八九十]+|\d+)(?:[:：]|\s)", text, re.MULTILINE)
            )
            if subsection_count + mainline_h2_count < 3:
                issues.append(_issue("error", "POD005", path, "standard/deep 播客至少展开 3 个主线小节"))
            duration = metadata.get("duration_seconds")
            try:
                duration_seconds = int(str(duration))
            except (TypeError, ValueError):
                duration_seconds = 0
            body = text.split("\n---\n", 1)[-1]
            body_hanzi = len(re.findall(r"[\u3400-\u9fff]", body))
            if duration_seconds >= 3600 and body_hanzi < 3500:
                issues.append(
                    _issue(
                        "warning",
                        "POD006",
                        path,
                        f"60 分钟以上 standard/deep 报告仅 {body_hanzi} 汉字，需人工检查内容召回",
                    )
                )

    if collection.id == "podcast-learning":
        for code, message, advisory in podcast_audit.audit_report(ROOT, metadata, text):
            severity = "warning" if advisory else _severity(source_enforce)
            issues.append(_issue(severity, code, path, message))

    issues.extend(_local_link_issues(path, text, enforce or source_enforce))
    for target in WIKILINK_RE.findall(_prose_for_placeholder_scan(text)):
        stem = Path(target.strip()).stem
        if stem in {"...", "…"} or "{" in target:
            continue
        if stem and not _wikilink_exists(path, target, wikilinks):
            # Qualified-path validation is new: keep old basename matches as
            # warnings until changed, without weakening existing missing targets.
            link_enforce = strict_selection or source_enforce or (enforce and not wikilinks.get(stem))
            issues.append(_issue(_severity(link_enforce), "LINK002", path, f"wikilink 无目标：[[{target}]]"))

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


def audit(
    paths: list[Path], *, strict_all: bool, new_paths: set[Path],
    changed_paths: set[Path] | None = None, source_paths: set[Path] | None = None,
) -> dict[str, object]:
    changed_paths = (changed_paths or set()) | new_paths
    source_paths = set(source_paths or ())
    enforced_sources = set(changed_paths)
    covered_sources: set[Path] = set()
    referenced_sources: set[Path] = set()
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
        dependencies = _podcast_dependencies(path) if collection.id == "podcast-learning" else set()
        # 只有声明的 raw 已在 audit_report 内审计；仅 Markdown/evidence 引用仍需直接检查。
        try:
            raw = podcast_audit.source_path(ROOT, metadata.get("transcript_path")) if collection.id == "podcast-learning" else None
        except ValueError:
            raw = None
        if raw:
            covered_sources.add(raw)
        referenced_sources.update(item for item in dependencies if item.name.endswith(".transcript.txt"))
        source_paths |= referenced_sources
        affected = path.resolve() in changed_paths or bool(dependencies & changed_paths)
        if affected:
            enforced_sources.update(dependencies)
        all_issues.extend(
            audit_file(
                path,
                enforce=strict_all or path.resolve() in new_paths,
                wikilinks=wikilinks,
                source_enforce=strict_all or affected,
            )
        )

    for source in sorted(source_paths - covered_sources):
        if not source.name.endswith(".transcript.txt"):
            continue
        if not source.is_file():
            if source in referenced_sources:
                all_issues.append(_issue(_severity(strict_all or source in enforced_sources), "POD101", source, "报告引用的转写来源不存在"))
            continue
        # 来源是仓内普通文件才读取；杜绝符号链接跟随到私人目录。
        try:
            podcast_audit.source_path(ROOT, str(source.relative_to(ROOT)))
        except ValueError:
            all_issues.append(_issue(_severity(strict_all or source in enforced_sources), "POD101", source, "来源不是安全仓内路径"))
            continue
        result = podcast_audit.audit(source)
        for error in result["errors"]:
            all_issues.append(_issue(_severity(strict_all or source in enforced_sources), "POD102", source, error))
        for warning in result["warnings"]:
            all_issues.append(_issue("warning", "POD103", source, warning))

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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Audit EverAgent reports")
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", action="store_true", help="audit every registered report")
    scope.add_argument("--changed", action="store_true", help="audit changed and untracked reports")
    scope.add_argument("--staged", action="store_true", help="audit reports staged for commit")
    parser.add_argument("--strict", action="store_true", help="apply current contract to every selected report")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--summary-only", action="store_true", help="print totals without individual warnings")
    parser.add_argument("--changed-path", action="append", default=[], metavar="REPO_PATH",
                        help="explicit changed path for a Git-free staged snapshot; repeat as needed")
    parser.add_argument("paths", nargs="*", help="explicit report paths")
    args = parser.parse_args(argv)

    if args.all:
        head = _git_ref("HEAD")
        remote = _git_ref("origin/main")
        if head and remote and not _git_is_ancestor(remote, head):
            message = (
                "current HEAD does not contain origin/main; full audit would miss remote reports. "
                f"HEAD={head[:8]} origin/main={remote[:8]}. Audit the target ref in an isolated worktree."
            )
            if args.json:
                print(
                    json.dumps(
                        {
                            "reports_scanned": 0,
                            "errors": 1,
                            "warnings": 0,
                            "metadata_missing": 0,
                            "issues": [
                                {
                                    "severity": "error",
                                    "code": "SCOPE001",
                                    "path": ".",
                                    "message": message,
                                }
                            ],
                        },
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                print("审计 0 篇：ERROR 1｜WARN 0｜缺 frontmatter 0")
                print(f"  ✗ SCOPE001 .: {message}")
            return 1

    new_paths: set[Path] = set()
    if args.staged:
        changed_paths = _git_paths(["git", "diff", "--cached", "--name-only", "--diff-filter=ACDMRTUXB", "-z"])
    else:
        changed_paths = _git_paths(["git", "diff", "HEAD", "--name-only", "--diff-filter=ACDMRTUXB", "-z"])
        changed_paths |= _git_paths(["git", "ls-files", "-z", "--others", "--exclude-standard"])
    for item in args.changed_path:
        candidate = Path(item)
        if candidate.is_absolute() or ".." in candidate.parts:
            parser.error("--changed-path requires a repository-relative path without '..'")
        changed_paths.add(ROOT / candidate)
    source_paths = {path for path in changed_paths if path.name.endswith(".transcript.txt")}
    if args.paths:
        selected = {Path(item) if Path(item).is_absolute() else ROOT / item for item in args.paths}
        paths = _reports_from_paths(selected)
        source_paths = {path for path in selected if path.name.endswith(".transcript.txt")}
        new_paths = {
            path.resolve()
            for path in paths
            if not _git_paths(
                ["git", "ls-files", "-z", "--error-unmatch", str(path.relative_to(ROOT))]
            )
        }
    elif args.all:
        paths = [path for _collection, path in iter_reports()]
        source_paths |= set((ROOT / "podcast-learning/reports/transcripts").glob("*.transcript.txt"))
    elif args.staged:
        paths, new_paths = staged_reports()
    else:
        paths, new_paths = changed_reports()
    if args.changed_path and not args.all and not args.paths:
        paths = sorted(set(paths) | set(_reports_from_paths(changed_paths)))

    result = audit(paths, strict_all=args.strict, new_paths=new_paths,
                   changed_paths=changed_paths, source_paths=source_paths)
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
