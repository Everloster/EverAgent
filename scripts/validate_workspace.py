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
REPLACEMENT_CHAR = "\ufffd"


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


def validate_text_encoding() -> list[ValidationIssue]:
    """Flag files that contain Unicode replacement characters."""
    issues: list[ValidationIssue] = []
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        # Skip git internals even if a future path pattern matches there.
        if ".git" in relative.parts:
            continue

        text = path.read_text(encoding="utf-8")
        if REPLACEMENT_CHAR in text:
            issues.append(
                ValidationIssue(
                    "WARN",
                    relative,
                    "contains Unicode replacement character (possible encoding corruption)",
                )
            )
    return issues


def validate_git_locks() -> list[ValidationIssue]:
    """Warn when git lock files are present, since they can block future writes."""
    issues: list[ValidationIssue] = []
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        return issues

    for path in sorted(git_dir.rglob("*.lock")):
        issues.append(
            ValidationIssue(
                "WARN",
                path.relative_to(ROOT),
                "git lock file is present and may block git operations",
            )
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


def validate_report_structure() -> list[ValidationIssue]:
    """Check that reports contain sufficient structural depth (headings count)."""
    issues: list[ValidationIssue] = []
    heading_pattern = re.compile(r"^#{2,3}\s+\S", re.MULTILINE)

    for path in iter_report_files():
        relative = path.relative_to(ROOT)
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if fm is None:
            continue

        report_type = fm.get("report_type", "")
        headings = heading_pattern.findall(text)

        if report_type in ("paper_analysis", "text_analysis"):
            if len(headings) < 4:
                issues.append(
                    ValidationIssue(
                        "WARN",
                        relative,
                        f"paper_analysis has only {len(headings)} sections (expected ≥ 4); "
                        "may be missing required 7-step structure",
                    )
                )
        elif report_type in ("knowledge_report", "concept_report"):
            # 人物图谱、比较研究、深度研究报告等使用自定义结构，不要求5层
            _SKIP_LAYER_CHECK = ("图谱", "比较", "研究报告", "timeline", "roadmap")
            if any(kw in path.stem for kw in _SKIP_LAYER_CHECK):
                continue
            layer_count = len(re.findall(r"层次[一二三四五]", text))
            if layer_count < 3:
                issues.append(
                    ValidationIssue(
                        "WARN",
                        relative,
                        f"{report_type} has {layer_count} 层次 sections (expected ≥ 3); "
                        "may be missing required 5-layer structure",
                    )
                )

    return issues


# Pattern: backtick-wrapped stems that look like report identifiers
# Matches things like `01_transformer_2017`, `31_megascale_2024`, `self_attention_深度解析`
_CONTEXT_REF_PATTERN = re.compile(r"`([a-zA-Z0-9_\-\u4e00-\u9fff]{4,})`")


def validate_context_consistency() -> list[ValidationIssue]:
    """Cross-check CONTEXT.md report listings against actual files on disk."""
    issues: list[ValidationIssue] = []

    for project_name, project_dir in LEARNING_PROJECTS.items():
        context_path = project_dir / "CONTEXT.md"
        reports_dir = project_dir / "reports"
        if not context_path.exists() or not reports_dir.exists():
            continue

        context_text = context_path.read_text(encoding="utf-8")
        relative_context = context_path.relative_to(ROOT)

        # Collect all report file stems on disk
        actual_stems: set[str] = {
            p.stem for p in reports_dir.rglob("*.md") if p.is_file()
        }

        # Extract candidate references from CONTEXT.md (backtick-wrapped tokens)
        raw_refs = _CONTEXT_REF_PATTERN.findall(context_text)
        # Keep only refs that look like report stems (contain underscore)
        referenced_stems: set[str] = {r for r in raw_refs if "_" in r}

        # Referenced in CONTEXT.md but missing on disk
        for stem in sorted(referenced_stems):
            if stem not in actual_stems:
                issues.append(
                    ValidationIssue(
                        "WARN",
                        relative_context,
                        f"CONTEXT.md references `{stem}` but no matching report file found on disk",
                    )
                )

        # On disk but not mentioned in CONTEXT.md
        for stem in sorted(actual_stems):
            if stem not in referenced_stems:
                # Only warn for numbered reports (e.g. 01_xxx); skip index/template files
                if re.match(r"^\d{2}_", stem):
                    issues.append(
                        ValidationIssue(
                            "WARN",
                            relative_context,
                            f"report `{stem}` exists on disk but is not listed in CONTEXT.md",
                        )
                    )

    return issues


def validate_task_board() -> list[ValidationIssue]:
    """Check Task Board task entries for required field consistency."""
    issues: list[ValidationIssue] = []
    task_board = ROOT / "docs" / "LEARNING_PROJECTS_TASK_BOARD.md"
    if not task_board.exists():
        return issues

    text = task_board.read_text(encoding="utf-8")
    relative = task_board.relative_to(ROOT)

    # Extract YAML code blocks
    yaml_blocks = re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)

    for block in yaml_blocks:
        # Split on task boundaries (lines starting with '- id:')
        chunks = re.split(r"\n(?=- id:)", block.strip())
        for chunk in chunks:
            if not chunk.strip():
                continue

            task: dict[str, str] = {}
            for line in chunk.splitlines():
                line = line.strip().lstrip("- ")
                if ":" in line:
                    key, _, value = line.partition(":")
                    task[key.strip()] = value.strip().strip('"')

            if "id" not in task:
                continue

            task_id = task.get("id", "?")
            status = task.get("status", "")

            if status == "claimed":
                for field in ("claimed_by", "claimed_at"):
                    if not task.get(field) or task[field] in ("null", ""):
                        issues.append(
                            ValidationIssue(
                                "WARN",
                                relative,
                                f"task {task_id}: status=claimed but `{field}` is null",
                            )
                        )
            elif status == "in_progress":
                if not task.get("started_at") or task["started_at"] in ("null", ""):
                    issues.append(
                        ValidationIssue(
                            "WARN",
                            relative,
                            f"task {task_id}: status=in_progress but `started_at` is null",
                        )
                    )
            elif status == "done":
                if not task.get("done_at") or task["done_at"] in ("null", ""):
                    issues.append(
                        ValidationIssue(
                            "WARN",
                            relative,
                            f"task {task_id}: status=done but `done_at` is null",
                        )
                    )
            elif status == "failed":
                if not task.get("failed_reason") or task["failed_reason"] in ("null", ""):
                    issues.append(
                        ValidationIssue(
                            "WARN",
                            relative,
                            f"task {task_id}: status=failed but `failed_reason` is null",
                        )
                    )

    return issues


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
    issues.extend(validate_text_encoding())
    issues.extend(validate_report_naming())
    issues.extend(validate_report_structure())
    issues.extend(validate_context_consistency())
    issues.extend(validate_task_board())
    issues.extend(validate_lfs_budget())
    issues.extend(validate_git_locks())

    if not issues:
        print("Workspace validation passed.")
        return 0

    for issue in issues:
        print(f"[{issue.severity}] {issue.path}: {issue.message}")

    severities = {issue.severity for issue in issues}
    return 1 if "ERROR" in severities else 0


if __name__ == "__main__":
    sys.exit(main())
