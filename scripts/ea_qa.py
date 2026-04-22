#!/usr/bin/env python3
"""EverAgent v3.0 Automated QA System — Report quality scoring and validation.

This module provides automated quality assurance for reports:
- Frontmatter completeness scoring
- Content quality metrics (word count, section coverage)
- Semantic tag validation
- Cross-reference checking
- Quality trend tracking over time

Usage:
    python3 scripts/ea_qa.py scan --project ai-learning
    python3 scripts/ea_qa.py score --report path/to/report.md
    python3 scripts/ea_qa.py trends --project ai-learning
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from ea_common import ROOT
from ea_database import get_db, record_metric


# ---------------------------------------------------------------------------
# Quality scoring models
# ---------------------------------------------------------------------------

@dataclass
class QualityScore:
    report_path: str
    overall_score: float  # 0-100
    frontmatter_score: float
    content_score: float
    structure_score: float
    cross_ref_score: float
    issues: list[str]


# ---------------------------------------------------------------------------
# Frontmatter validation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = {"title", "domain", "report_type", "status", "updated_on"}
OPTIONAL_SEMANTIC_FIELDS = {"semantic_tags", "related_concepts", "related_entities"}


def parse_frontmatter(text: str) -> Optional[dict[str, str]]:
    """Extract YAML frontmatter from markdown text."""
    match = re.search(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None

    frontmatter: dict[str, str] = {}
    for line in match.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"').strip("'")
    return frontmatter


def score_frontmatter(frontmatter: Optional[dict[str, str]]) -> tuple[float, list[str]]:
    """Score frontmatter completeness. Returns (score, issues)."""
    if frontmatter is None:
        return 0.0, ["Missing frontmatter entirely"]

    score = 100.0
    issues: list[str] = []

    # Check required fields
    missing = REQUIRED_FIELDS - set(frontmatter.keys())
    if missing:
        score -= len(missing) * 15
        issues.append(f"Missing required fields: {', '.join(missing)}")

    # Check semantic fields (bonus)
    semantic_present = OPTIONAL_SEMANTIC_FIELDS & set(frontmatter.keys())
    if not semantic_present:
        score -= 5
        issues.append("No semantic metadata (semantic_tags, related_concepts, related_entities)")

    # Validate status
    valid_statuses = {"completed", "in_progress", "planned"}
    status = frontmatter.get("status", "")
    if status and status not in valid_statuses:
        score -= 10
        issues.append(f"Invalid status: {status}")

    # Validate report_type
    valid_types = {"paper_analysis", "knowledge_report", "concept_report", "text_analysis"}
    report_type = frontmatter.get("report_type", "")
    if report_type and report_type not in valid_types:
        score -= 10
        issues.append(f"Invalid report_type: {report_type}")

    return max(0.0, score), issues


# ---------------------------------------------------------------------------
# Content quality scoring
# ---------------------------------------------------------------------------

SECTION_PATTERNS = {
    "introduction": re.compile(r"(?i)^#{1,3}\s*(?:introduction|简介|概述|背景)"),
    "methodology": re.compile(r"(?i)^#{1,3}\s*(?:methodology|方法|方法论|approach)"),
    "results": re.compile(r"(?i)^#{1,3}\s*(?:results?|结果|findings|发现)"),
    "discussion": re.compile(r"(?i)^#{1,3}\s*(?:discussion|讨论|分析)"),
    "conclusion": re.compile(r"(?i)^#{1,3}\s*(?:conclusion|结论|summary|总结)"),
    "references": re.compile(r"(?i)^#{1,3}\s*(?:references?|参考|引用|bibliography)"),
}


def score_content(text: str) -> tuple[float, list[str]]:
    """Score content quality. Returns (score, issues)."""
    score = 100.0
    issues: list[str] = []

    # Word count
    words = len(text.split())
    if words < 500:
        score -= 20
        issues.append(f"Content too short: {words} words (minimum 500)")
    elif words < 1000:
        score -= 10
        issues.append(f"Content short: {words} words (recommended 1000+)")

    # Section coverage
    sections_found = set()
    for line in text.splitlines():
        for section, pattern in SECTION_PATTERNS.items():
            if pattern.match(line.strip()):
                sections_found.add(section)

    expected_sections = {"introduction", "conclusion"}
    missing_sections = expected_sections - sections_found
    if missing_sections:
        score -= len(missing_sections) * 10
        issues.append(f"Missing sections: {', '.join(missing_sections)}")

    # Check for code blocks (indicates technical depth)
    code_blocks = text.count("```")
    if code_blocks == 0:
        score -= 5
        issues.append("No code blocks found (technical reports should include examples)")

    # Check for tables
    tables = len(re.findall(r"\|.*\|.*\|", text))
    if tables == 0:
        score -= 3
        issues.append("No tables found (structured data improves readability)")

    return max(0.0, score), issues


# ---------------------------------------------------------------------------
# Structure scoring
# ---------------------------------------------------------------------------

def score_structure(text: str) -> tuple[float, list[str]]:
    """Score document structure. Returns (score, issues)."""
    score = 100.0
    issues: list[str] = []

    # Heading hierarchy
    headings = re.findall(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE)
    if not headings:
        score -= 30
        issues.append("No headings found")
    else:
        # Check for h1
        h1_count = sum(1 for h, _ in headings if h == "#")
        if h1_count == 0:
            score -= 10
            issues.append("No H1 heading")
        elif h1_count > 1:
            score -= 5
            issues.append("Multiple H1 headings")

        # Check heading depth jumps
        prev_level = 1
        for h, _ in headings:
            level = len(h)
            if level > prev_level + 1:
                score -= 3
                issues.append(f"Heading level jump: H{prev_level} → H{level}")
            prev_level = level

    # Check for images
    images = re.findall(r"!\[.*?\]\(.*?\)", text)
    if len(images) == 0:
        score -= 5
        issues.append("No images found (visual aids improve comprehension)")

    # Check for links
    links = re.findall(r"\[.*?\]\(.*?\)", text)
    if len(links) < 3:
        score -= 5
        issues.append("Few internal/external links (cross-referencing is important)")

    return max(0.0, score), issues


# ---------------------------------------------------------------------------
# Cross-reference scoring
# ---------------------------------------------------------------------------

def score_cross_references(text: str, project: str) -> tuple[float, list[str]]:
    """Score cross-references to wiki and other reports."""
    score = 100.0
    issues: list[str] = []

    # Check for wiki links
    wiki_links = re.findall(r"\[.*?\]\(\.\./\.\./wiki/(.*?)\.md\)", text)
    if len(wiki_links) < 2:
        score -= 15
        issues.append("Few wiki cross-references (link to entities/concepts)")

    # Check for report links
    report_links = re.findall(r"\[.*?\]\((?:\.\./)*reports/(.*?)\.md\)", text)
    if len(report_links) < 1:
        score -= 10
        issues.append("No links to other reports")

    # Check for external references
    external_links = re.findall(r"\[.*?\]\(https?://.*?\)", text)
    if len(external_links) < 3:
        score -= 10
        issues.append("Few external references (papers, documentation)")

    return max(0.0, score), issues


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------

def score_report(path: Path) -> QualityScore:
    """Compute full quality score for a report."""
    text = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(text)

    fm_score, fm_issues = score_frontmatter(frontmatter)
    content_score, content_issues = score_content(text)
    structure_score, structure_issues = score_structure(text)

    # Determine project from path
    project = path.parts[0] if len(path.parts) > 1 else "unknown"
    cross_score, cross_issues = score_cross_references(text, project)

    # Weighted overall score
    overall = (
        fm_score * 0.25 +
        content_score * 0.35 +
        structure_score * 0.25 +
        cross_score * 0.15
    )

    all_issues = fm_issues + content_issues + structure_issues + cross_issues

    return QualityScore(
        report_path=str(path),
        overall_score=round(overall, 1),
        frontmatter_score=round(fm_score, 1),
        content_score=round(content_score, 1),
        structure_score=round(structure_score, 1),
        cross_ref_score=round(cross_score, 1),
        issues=all_issues,
    )


def scan_project(project: str) -> list[QualityScore]:
    """Scan all reports in a project and score them."""
    project_dir = ROOT / project / "reports"
    if not project_dir.exists():
        return []

    scores: list[QualityScore] = []
    for pattern in ["**/*.md"]:
        for path in project_dir.glob(pattern):
            try:
                score = score_report(path)
                scores.append(score)
            except Exception as exc:
                print(f"[WARN] Failed to score {path}: {exc}")

    return scores


def store_scores(scores: list[QualityScore], project: str) -> None:
    """Store quality scores in database."""
    with get_db() as conn:
        for s in scores:
            conn.execute(
                """
                INSERT INTO reports (path, project, quality_score, frontmatter_valid)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(path) DO UPDATE SET
                    quality_score=excluded.quality_score,
                    frontmatter_valid=excluded.frontmatter_valid
                """,
                (s.report_path, project, s.overall_score, 1 if s.frontmatter_score >= 70 else 0),
            )
        conn.commit()

    # Record aggregate metric
    if scores:
        avg_score = sum(s.overall_score for s in scores) / len(scores)
        record_metric("report_quality_avg", avg_score, {"project": project})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="EverAgent v3.0 Automated QA")
    sub = parser.add_subparsers(dest="command")

    score_p = sub.add_parser("score", help="Score a single report")
    score_p.add_argument("--report", required=True, help="Path to report markdown file")
    score_p.set_defaults(func=command_score)

    scan_p = sub.add_parser("scan", help="Scan all reports in a project")
    scan_p.add_argument("--project", required=True, help="Project name")
    scan_p.set_defaults(func=command_scan)

    trends_p = sub.add_parser("trends", help="Show quality trends")
    trends_p.add_argument("--project", help="Project name (optional)")
    trends_p.set_defaults(func=command_trends)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


def command_score(args: argparse.Namespace) -> int:
    path = Path(args.report)
    if not path.exists():
        print(f"[ERROR] Report not found: {path}")
        return 1

    score = score_report(path)
    print(f"Report: {score.report_path}")
    print(f"Overall Score: {score.overall_score}/100")
    print(f"  Frontmatter: {score.frontmatter_score}/100")
    print(f"  Content:     {score.content_score}/100")
    print(f"  Structure:   {score.structure_score}/100")
    print(f"  Cross-refs:  {score.cross_ref_score}/100")
    if score.issues:
        print("\nIssues:")
        for issue in score.issues:
            print(f"  - {issue}")
    return 0


def command_scan(args: argparse.Namespace) -> int:
    print(f"[INFO] Scanning project: {args.project}")
    scores = scan_project(args.project)
    store_scores(scores, args.project)

    print(f"\nScanned {len(scores)} reports")
    if scores:
        avg = sum(s.overall_score for s in scores) / len(scores)
        print(f"Average score: {avg:.1f}/100")
        print("\nTop 3:")
        for s in sorted(scores, key=lambda x: x.overall_score, reverse=True)[:3]:
            print(f"  {s.overall_score:5.1f} {s.report_path}")
        print("\nBottom 3:")
        for s in sorted(scores, key=lambda x: x.overall_score)[:3]:
            print(f"  {s.overall_score:5.1f} {s.report_path}")
    return 0


def command_trends(args: argparse.Namespace) -> int:
    from ea_database import get_metrics

    project_filter = args.project
    metrics = get_metrics("report_quality_avg")

    print("Quality Trends:")
    for m in metrics[:20]:
        labels = m.get("labels", "")
        if project_filter and project_filter not in labels:
            continue
        print(f"  {m['timestamp']}: {m['metric_value']:.1f} {labels}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
