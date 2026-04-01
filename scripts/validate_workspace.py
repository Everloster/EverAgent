#!/usr/bin/env python3
"""Validate cross-workspace documentation and metadata conventions."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {
    "ai-learning": ROOT / "ai-learning",
    "biology-learning": ROOT / "biology-learning",
    "cs-learning": ROOT / "cs-learning",
    "philosophy-learning": ROOT / "philosophy-learning",
    "psychology-learning": ROOT / "psychology-learning",
    "github-trending-analyzer": ROOT / "github-trending-analyzer",
}
LEARNING_PROJECTS = {
    name: path for name, path in PROJECTS.items() if name != "github-trending-analyzer"
}
REQUIRED_FRONTMATTER_KEYS = {"title", "domain", "report_type", "status", "updated_on"}
REPORT_GLOBS = [
    "ai-learning/reports/**/*.md",
    "biology-learning/reports/**/*.md",
    "cs-learning/reports/**/*.md",
    "philosophy-learning/reports/**/*.md",
    "psychology-learning/reports/**/*.md",
]
SKILL_TEMPLATE_HINT = "docs/SKILL_TEMPLATES.md"
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
MARKDOWN_LINK_PATTERN = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")


@dataclass
class ValidationIssue:
    severity: str
    path: Path
    message: str


def parse_frontmatter(text: str) -> dict[str, str] | None:
    match = FRONTMATTER_PATTERN.match(text)
    if not match:
        return None

    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def iter_report_files() -> list[Path]:
    files: set[Path] = set()
    for pattern in REPORT_GLOBS:
        files.update(ROOT.glob(pattern))
    return sorted(path for path in files if path.is_file())


def validate_frontmatter() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in iter_report_files():
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            issues.append(
                ValidationIssue("WARN", relative, "missing YAML frontmatter")
            )
            continue

        missing_keys = REQUIRED_FRONTMATTER_KEYS - set(frontmatter)
        if missing_keys:
            issues.append(
                ValidationIssue(
                    "WARN",
                    relative,
                    "frontmatter missing keys: " + ", ".join(sorted(missing_keys)),
                )
            )

        domain = frontmatter.get("domain")
        expected_domain = relative.parts[0]
        if domain and domain != expected_domain:
            issues.append(
                ValidationIssue(
                    "WARN",
                    relative,
                    f"frontmatter domain '{domain}' does not match '{expected_domain}'",
                )
            )
    return issues


def validate_skill_template_links() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for project_name, project_dir in LEARNING_PROJECTS.items():
        for skill_path in sorted(project_dir.glob("skills/**/SKILL.md")):
            relative = skill_path.relative_to(ROOT)
            text = skill_path.read_text(encoding="utf-8")
            if SKILL_TEMPLATE_HINT not in text:
                issues.append(
                    ValidationIssue(
                        "WARN",
                        relative,
                        f"missing reference to {SKILL_TEMPLATE_HINT}",
                    )
                )
    return issues


def validate_readme_links() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for project_dir in PROJECTS.values():
        for doc_name in ("README.md", "CONTEXT.md"):
            path = project_dir / doc_name
            if not path.exists():
                issues.append(
                    ValidationIssue("ERROR", path.relative_to(ROOT), "required file is missing")
                )
                continue

            text = path.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK_PATTERN.findall(text):
                clean_target = target.split("#", 1)[0]
                if not clean_target:
                    continue
                resolved = (path.parent / clean_target).resolve()
                if not resolved.exists():
                    issues.append(
                        ValidationIssue(
                            "WARN",
                            path.relative_to(ROOT),
                            f"broken relative link target: {target}",
                        )
                    )
    return issues


def validate_repository_hygiene() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in sorted(ROOT.rglob(".DS_Store")):
        issues.append(
            ValidationIssue("WARN", path.relative_to(ROOT), "tracked junk file should be removed")
        )
    return issues


# Report naming convention: {number}_{name}_{year}.md (no Chinese suffixes)
REPORT_NAME_BAD_SUFFIXES = re.compile(r"_[\u4e00-\u9fff]+\.md$")


ANALYSIS_DIRS = {"paper_analyses", "text_analyses"}


def validate_report_naming() -> list[ValidationIssue]:
    """Check report filenames follow convention and detect duplicates."""
    issues: list[ValidationIssue] = []
    # Group by (project, report_dir, normalized_stem) to detect duplicates
    seen: dict[str, list[Path]] = {}

    for path in iter_report_files():
        relative = path.relative_to(ROOT)
        name = path.name

        # Only enforce naming convention on paper/text analyses (not knowledge/concept reports)
        if any(d in relative.parts for d in ANALYSIS_DIRS):
            if REPORT_NAME_BAD_SUFFIXES.search(name):
                issues.append(
                    ValidationIssue(
                        "WARN",
                        relative,
                        f"filename contains Chinese suffix; expected {{number}}_{{name}}_{{year}}.md",
                    )
                )

        # Build dedup key: strip known suffixes to find the canonical stem
        stem = path.stem
        for suffix in ("_分析报告", "_后训练分析报告", "_精读报告"):
            stem = stem.replace(suffix, "")
        dedup_key = f"{path.parent}:{stem}"
        seen.setdefault(dedup_key, []).append(relative)

    for key, paths in seen.items():
        if len(paths) > 1:
            names = ", ".join(str(p) for p in paths)
            issues.append(
                ValidationIssue(
                    "WARN",
                    paths[0],
                    f"possible duplicate reports: {names}",
                )
            )

    return issues


# LFS budget: GitHub free tier = 1 GB storage, 1 GB bandwidth/month
LFS_STORAGE_WARN_MB = 700
LFS_STORAGE_ERROR_MB = 950


def validate_lfs_budget() -> list[ValidationIssue]:
    """Check total size of LFS-tracked files against GitHub free tier budget."""
    issues: list[ValidationIssue] = []
    gitattributes = ROOT / ".gitattributes"
    if not gitattributes.exists():
        return issues

    text = gitattributes.read_text(encoding="utf-8")
    lfs_patterns: list[str] = []
    for line in text.splitlines():
        if "filter=lfs" in line:
            pattern = line.split()[0]
            lfs_patterns.append(pattern)

    if not lfs_patterns:
        return issues

    total_bytes = 0
    for pattern in lfs_patterns:
        for path in sorted(ROOT.rglob(pattern)):
            if path.is_file():
                total_bytes += path.stat().st_size

    total_mb = total_bytes / (1024 * 1024)

    if total_mb >= LFS_STORAGE_ERROR_MB:
        issues.append(
            ValidationIssue(
                "ERROR",
                Path(".gitattributes"),
                f"LFS tracked files total {total_mb:.0f} MB, exceeding {LFS_STORAGE_ERROR_MB} MB safety limit (GitHub free = 1 GB)",
            )
        )
    elif total_mb >= LFS_STORAGE_WARN_MB:
        issues.append(
            ValidationIssue(
                "WARN",
                Path(".gitattributes"),
                f"LFS tracked files total {total_mb:.0f} MB, approaching {LFS_STORAGE_ERROR_MB} MB limit (GitHub free = 1 GB)",
            )
        )

    return issues


def main() -> int:
    issues = []
    issues.extend(validate_frontmatter())
    issues.extend(validate_skill_template_links())
    issues.extend(validate_readme_links())
    issues.extend(validate_repository_hygiene())
    issues.extend(validate_report_naming())
    issues.extend(validate_lfs_budget())

    if not issues:
        print("Workspace validation passed.")
        return 0

    for issue in issues:
        print(f"[{issue.severity}] {issue.path}: {issue.message}")

    severities = {issue.severity for issue in issues}
    return 1 if "ERROR" in severities else 0


if __name__ == "__main__":
    sys.exit(main())
