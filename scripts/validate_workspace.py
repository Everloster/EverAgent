#!/usr/bin/env python3
"""Validate workspace documentation, metadata, and task-state conventions."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

from task_state import PROJECTS as TASK_STATE_PROJECTS, state_file_for_project


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
REPORT_NAME_BAD_SUFFIXES = re.compile(r"_[\u4e00-\u9fff]+\.md$")
REPLACEMENT_CHAR = "\ufffd"
ANALYSIS_DIRS = {"paper_analyses", "text_analyses"}


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
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter is None:
            issues.append(ValidationIssue("WARN", relative, "missing YAML frontmatter"))
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
    for project_dir in LEARNING_PROJECTS.values():
        for skill_path in sorted(project_dir.glob("skills/**/SKILL.md")):
            if SKILL_TEMPLATE_HINT not in skill_path.read_text(encoding="utf-8"):
                issues.append(
                    ValidationIssue(
                        "WARN",
                        skill_path.relative_to(ROOT),
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
                issues.append(ValidationIssue("ERROR", path.relative_to(ROOT), "required file is missing"))
                continue
            text = path.read_text(encoding="utf-8")
            for target in MARKDOWN_LINK_PATTERN.findall(text):
                clean_target = target.split("#", 1)[0]
                if not clean_target:
                    continue
                if not (path.parent / clean_target).resolve().exists():
                    issues.append(
                        ValidationIssue(
                            "WARN",
                            path.relative_to(ROOT),
                            f"broken relative link target: {target}",
                        )
                    )
    return issues


def validate_repository_hygiene() -> list[ValidationIssue]:
    return [
        ValidationIssue("WARN", path.relative_to(ROOT), "tracked junk file should be removed")
        for path in sorted(ROOT.rglob(".DS_Store"))
    ]


def validate_text_encoding() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in sorted(ROOT.rglob("*.md")):
        relative = path.relative_to(ROOT)
        if ".git" in relative.parts:
            continue
        if REPLACEMENT_CHAR in path.read_text(encoding="utf-8"):
            issues.append(
                ValidationIssue(
                    "WARN",
                    relative,
                    "contains Unicode replacement character (possible encoding corruption)",
                )
            )
    return issues


def validate_git_locks() -> list[ValidationIssue]:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        return []
    return [
        ValidationIssue("WARN", path.relative_to(ROOT), "git lock file is present and may block git operations")
        for path in sorted(git_dir.rglob("*.lock"))
    ]


def validate_task_state_files() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for project_name in TASK_STATE_PROJECTS:
        state_path = state_file_for_project(project_name)
        if not state_path.exists():
            issues.append(
                ValidationIssue(
                    "ERROR",
                    state_path.relative_to(ROOT),
                    "missing versioned .project-task-state file",
                )
            )
    return issues


def validate_report_naming() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: dict[str, list[Path]] = {}
    for path in iter_report_files():
        relative = path.relative_to(ROOT)
        if any(directory in relative.parts for directory in ANALYSIS_DIRS):
            if REPORT_NAME_BAD_SUFFIXES.search(path.name):
                issues.append(
                    ValidationIssue(
                        "WARN",
                        relative,
                        "filename contains Chinese suffix; expected {number}_{name}_{year}.md",
                    )
                )
        stem = path.stem
        for suffix in ("_分析报告", "_后训练分析报告", "_精读报告"):
            stem = stem.replace(suffix, "")
        seen.setdefault(f"{path.parent}:{stem}", []).append(relative)
    for paths in seen.values():
        if len(paths) > 1:
            names = ", ".join(str(path) for path in paths)
            issues.append(ValidationIssue("WARN", paths[0], f"possible duplicate reports: {names}"))
    return issues


def main() -> int:
    validators = [
        validate_frontmatter,
        validate_skill_template_links,
        validate_readme_links,
        validate_repository_hygiene,
        validate_text_encoding,
        validate_git_locks,
        validate_task_state_files,
        validate_report_naming,
    ]

    issues: list[ValidationIssue] = []
    for validator in validators:
        issues.extend(validator())

    if not issues:
        print("Workspace validation passed.")
        return 0

    has_error = False
    for issue in issues:
        if issue.severity == "ERROR":
            has_error = True
        print(f"[{issue.severity}] {issue.path}: {issue.message}")
    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
