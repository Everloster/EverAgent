#!/usr/bin/env python3
"""Verify that each subproject's reports/ layer and wiki/ layer remain in sync.

Design goals
------------
The Karpathy-style wiki (see CLAUDE.md "Wiki Operations") states that every new
report should trigger an update of wiki/entities, wiki/concepts, wiki/log.md and
wiki/index.md. This is documented but, until now, unenforced. This checker
turns those rules into mechanical checks so that drift becomes visible.

Checks performed per learning subproject (those with a ``wiki/`` directory):

1. Frontmatter of every wiki page under ``wiki/entities/``, ``wiki/concepts/``,
   ``wiki/syntheses/`` has the minimum required keys (``id``, ``title``,
   ``type``, ``domain``, ``sources``).
2. ``wiki/index.md`` links to every wiki page that exists on disk.
3. Every link in ``wiki/index.md`` points to a wiki page that actually exists.
4. Every ``sources:`` entry in a wiki page corresponds to a real report
   filename stem (e.g. ``21_moe_2017`` matches
   ``ai-learning/reports/paper_analyses/21_moe_2017.md``) OR to the title of a
   concept/knowledge report that lives under ``reports/concept_reports/`` or
   ``reports/knowledge_reports/``. Unknown sources are reported as warnings so
   the check never blocks on cross-project references that happen to live
   elsewhere.
5. WARN when a ``paper_analysis`` report is not mentioned in any wiki page's
   ``sources`` — that usually means a new paper was ingested without a
   follow-up wiki update.
6. ``wiki/log.md`` exists (non-empty append-only log is a soft requirement).

Subprojects without a ``wiki/`` directory produce a single INFO line and are
otherwise skipped so the script never fails just because a project hasn't
adopted the wiki layer yet.

Exit codes
----------
``0`` clean; ``1`` at least one ERROR; ``2`` only WARNs in ``--strict``.

This script uses standard library only — no PyYAML — to match the rest of
``scripts/`` (see validate_workspace.py, project_registry.py).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from project_registry import discover_learning_projects


ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

WIKI_PAGE_KEYS = {"id", "title", "type", "domain", "sources"}
REPORT_KEYS = {"title", "domain", "report_type", "status", "updated_on"}
WIKI_SUBDIRS = ("entities", "concepts", "syntheses")
REPORT_SUBDIRS = ("paper_analyses", "concept_reports", "knowledge_reports", "text_analyses")


@dataclass
class SyncIssue:
    severity: str  # ERROR | WARN | INFO
    project: str
    path: Path
    message: str


@dataclass
class ReportIndex:
    """Index of a project's report files: filename stems and titles."""

    stems: set[str] = field(default_factory=set)
    titles: set[str] = field(default_factory=set)
    paper_analysis_stems: set[str] = field(default_factory=set)
    # stem -> frontmatter dict
    by_stem: dict[str, dict[str, str]] = field(default_factory=dict)


# ---------- Frontmatter helpers ----------

def parse_frontmatter(text: str) -> dict[str, object] | None:
    """Very small YAML subset parser.

    Supports scalar ``key: value`` pairs and ``sources: [a, b, c]`` inline
    lists. Matches the style used by validate_workspace.py.
    """
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return None

    fields: dict[str, object] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        # Inline list: [a, b, c] or [a]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                fields[key] = []
            else:
                items = [
                    item.strip().strip('"').strip("'")
                    for item in inner.split(",")
                    if item.strip()
                ]
                fields[key] = items
        else:
            fields[key] = value.strip('"').strip("'")
    return fields


# ---------- Report index ----------

def build_report_index(project_path: Path) -> ReportIndex:
    index = ReportIndex()
    reports_dir = project_path / "reports"
    if not reports_dir.exists():
        return index

    for sub in REPORT_SUBDIRS:
        sub_dir = reports_dir / sub
        if not sub_dir.exists():
            continue
        for report in sorted(sub_dir.glob("*.md")):
            stem = report.stem
            index.stems.add(stem)
            text = report.read_text(encoding="utf-8", errors="replace")
            fm = parse_frontmatter(text) or {}
            title = str(fm.get("title", "")).strip()
            if title:
                index.titles.add(title)
            index.by_stem[stem] = {k: str(v) for k, v in fm.items() if not isinstance(v, list)}
            if str(fm.get("report_type", "")).strip() == "paper_analysis":
                index.paper_analysis_stems.add(stem)

    # Also pick up reports directly under reports/ (rare, but ai-learning has one)
    for report in sorted(reports_dir.glob("*.md")):
        stem = report.stem
        index.stems.add(stem)
        fm = parse_frontmatter(report.read_text(encoding="utf-8", errors="replace")) or {}
        title = str(fm.get("title", "")).strip()
        if title:
            index.titles.add(title)

    return index


# ---------- Wiki scanning ----------

def iter_wiki_pages(wiki_dir: Path) -> list[Path]:
    pages: list[Path] = []
    for sub in WIKI_SUBDIRS:
        sub_dir = wiki_dir / sub
        if not sub_dir.exists():
            continue
        pages.extend(sorted(p for p in sub_dir.glob("*.md")))
    return pages


def collect_index_links(index_md: Path) -> set[str]:
    """Return all relative wiki links listed in wiki/index.md (hrefs only)."""
    if not index_md.exists():
        return set()
    text = index_md.read_text(encoding="utf-8", errors="replace")
    hrefs: set[str] = set()
    for m in MARKDOWN_LINK_PATTERN.finditer(text):
        href = m.group(1).strip()
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        hrefs.add(href.split("#", 1)[0])  # strip anchor
    return hrefs


def _normalise_href(href: str) -> str:
    """Drop leading './' so that './entities/foo.md' == 'entities/foo.md'."""
    return href.lstrip("./")


# ---------- Core check ----------

def check_project(project: str, project_path: Path) -> list[SyncIssue]:
    issues: list[SyncIssue] = []
    wiki_dir = project_path / "wiki"
    if not wiki_dir.exists():
        issues.append(
            SyncIssue(
                severity="INFO",
                project=project,
                path=project_path,
                message="no wiki/ directory (subproject has not adopted the wiki layer yet)",
            )
        )
        return issues

    index_md = wiki_dir / "index.md"
    if not index_md.exists():
        issues.append(
            SyncIssue("ERROR", project, wiki_dir, "wiki/index.md is missing")
        )
        return issues

    log_md = wiki_dir / "log.md"
    if not log_md.exists():
        issues.append(
            SyncIssue("WARN", project, wiki_dir, "wiki/log.md is missing (append-only log required)")
        )

    report_index = build_report_index(project_path)

    # --- scan wiki pages & build map of referenced sources ---
    referenced_sources: set[str] = set()
    wiki_pages = iter_wiki_pages(wiki_dir)
    wiki_rel_paths: set[str] = set()

    for page in wiki_pages:
        rel = page.relative_to(wiki_dir).as_posix()
        wiki_rel_paths.add(rel)
        text = page.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        if fm is None:
            issues.append(
                SyncIssue("ERROR", project, page, "wiki page missing YAML frontmatter")
            )
            continue
        missing = WIKI_PAGE_KEYS - set(fm.keys())
        if missing:
            issues.append(
                SyncIssue(
                    "ERROR",
                    project,
                    page,
                    f"wiki page frontmatter missing keys: {sorted(missing)}",
                )
            )
        sources = fm.get("sources")
        # Tolerate scalar-string sources (single value instead of list)
        if isinstance(sources, str) and sources:
            sources = [sources]
        if isinstance(sources, list):
            for src in sources:
                if not src:
                    continue
                src_str = str(src).strip()
                referenced_sources.add(src_str)
                # Cross-references to non-report files (knowledge/*, ../something) are legitimate
                if "/" in src_str or src_str.endswith(".md"):
                    continue
                if (
                    src_str not in report_index.stems
                    and src_str not in report_index.titles
                ):
                    issues.append(
                        SyncIssue(
                            "WARN",
                            project,
                            page,
                            f"source '{src_str}' does not match any report stem or title in this project",
                        )
                    )
        elif sources is None:
            issues.append(
                SyncIssue(
                    "ERROR",
                    project,
                    page,
                    "wiki page frontmatter missing 'sources' list",
                )
            )

    # --- compare wiki/index.md against on-disk wiki pages ---
    index_hrefs = {_normalise_href(h) for h in collect_index_links(index_md)}
    # filter index hrefs to those pointing into WIKI_SUBDIRS (ignore external refs like ../reports/)
    index_wiki_hrefs = {h for h in index_hrefs if h.split("/", 1)[0] in WIKI_SUBDIRS}

    # Pages on disk but not listed in index.md
    missing_from_index = wiki_rel_paths - index_wiki_hrefs
    for rel in sorted(missing_from_index):
        issues.append(
            SyncIssue(
                "ERROR",
                project,
                wiki_dir / rel,
                "wiki page exists on disk but is not linked from wiki/index.md",
            )
        )

    # Pages listed in index.md but missing from disk
    missing_on_disk = index_wiki_hrefs - wiki_rel_paths
    for rel in sorted(missing_on_disk):
        issues.append(
            SyncIssue(
                "ERROR",
                project,
                index_md,
                f"wiki/index.md links to '{rel}' but that file does not exist",
            )
        )

    # --- WARN: paper_analysis reports with no wiki reference ---
    orphan_papers = report_index.paper_analysis_stems - referenced_sources
    # Allow a match if any source string contains the stem (fuzzy)
    sources_as_text = " ".join(referenced_sources)
    orphan_papers = {s for s in orphan_papers if s not in sources_as_text}
    for stem in sorted(orphan_papers):
        issues.append(
            SyncIssue(
                "WARN",
                project,
                project_path / "reports" / f"{stem}.md",
                f"paper_analysis '{stem}' is not referenced by any wiki page (possible drift)",
            )
        )

    return issues


# ---------- Report formatting ----------

SEVERITY_ORDER = {"ERROR": 0, "WARN": 1, "INFO": 2}


def format_issues(issues: list[SyncIssue]) -> str:
    if not issues:
        return "wiki_sync_check: clean"
    lines: list[str] = []
    for issue in sorted(issues, key=lambda i: (SEVERITY_ORDER[i.severity], i.project, str(i.path))):
        try:
            rel = issue.path.relative_to(ROOT)
        except ValueError:
            rel = issue.path
        lines.append(f"[{issue.severity}] {issue.project} :: {rel} — {issue.message}")
    return "\n".join(lines)


# ---------- CLI ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project",
        help="Only check the given subproject name (default: all learning subprojects).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat WARN as a non-zero exit (useful in CI).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress INFO lines (e.g. subprojects without a wiki/ dir).",
    )
    args = parser.parse_args(argv)

    projects = discover_learning_projects()
    if args.project:
        if args.project not in projects:
            print(f"unknown project: {args.project}", file=sys.stderr)
            return 1
        projects = {args.project: projects[args.project]}

    all_issues: list[SyncIssue] = []
    for name, path in projects.items():
        all_issues.extend(check_project(name, path))

    if args.quiet:
        all_issues = [i for i in all_issues if i.severity != "INFO"]

    print(format_issues(all_issues))

    has_error = any(i.severity == "ERROR" for i in all_issues)
    has_warn = any(i.severity == "WARN" for i in all_issues)

    if has_error:
        return 1
    if args.strict and has_warn:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
