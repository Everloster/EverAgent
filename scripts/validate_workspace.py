#!/usr/bin/env python3
"""Validate workspace documentation, metadata, and task-state conventions.

Modes:
- full: scan the whole repo (warnings are non-blocking unless ERROR).
- changed: only validate staged changed files strictly (useful for pre-commit).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from project_registry import AGENTS_REGISTRY, discover_projects, load_agents_registry
from task_state import PROJECTS as TASK_STATE_PROJECTS, state_file_for_project


ROOT = Path(__file__).resolve().parents[1]
PROJECTS = {name: path for name, path in TASK_STATE_PROJECTS.items() if name != "global"}
LEARNING_PROJECTS = {
    name: path for name, path in PROJECTS.items() if name != "github-trending-analyzer"
}
REQUIRED_FRONTMATTER_KEYS = {"title", "domain", "report_type", "status", "updated_on"}
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


def _git_staged_paths() -> set[Path]:
    """Return staged paths (relative to repo root). Empty set if not in a git repo."""
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", "--cached"],
            cwd=ROOT,
            text=True,
        )
    except Exception:
        return set()
    paths: set[Path] = set()
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        paths.add(Path(line))
    return paths


def _is_learning_report(path: Path) -> bool:
    parts = path.parts
    if len(parts) < 3:
        return False
    if parts[0] not in LEARNING_PROJECTS:
        return False
    return parts[1] == "reports" and path.suffix == ".md"


def iter_report_files(only_paths: set[Path] | None = None) -> list[Path]:
    if only_paths is None:
        files: set[Path] = set()
        for project_path in LEARNING_PROJECTS.values():
            reports_dir = project_path / "reports"
            if reports_dir.exists():
                files.update(reports_dir.rglob("*.md"))
        return sorted(path for path in files if path.is_file())

    # only validate changed report files
    candidates = [ROOT / rel for rel in sorted(only_paths) if _is_learning_report(rel)]
    return [path for path in candidates if path.exists() and path.is_file()]


def validate_frontmatter(only_paths: set[Path] | None, strict: bool) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in iter_report_files(only_paths):
        relative = path.relative_to(ROOT)
        frontmatter = parse_frontmatter(path.read_text(encoding="utf-8"))
        if frontmatter is None:
            severity = "ERROR" if strict else "WARN"
            issues.append(ValidationIssue(severity, relative, "missing YAML frontmatter"))
            continue

        missing_keys = REQUIRED_FRONTMATTER_KEYS - set(frontmatter)
        if missing_keys:
            severity = "ERROR" if strict else "WARN"
            issues.append(
                ValidationIssue(
                    severity,
                    relative,
                    "frontmatter missing keys: " + ", ".join(sorted(missing_keys)),
                )
            )

        domain = frontmatter.get("domain")
        expected_domain = relative.parts[0]
        if domain and domain != expected_domain:
            severity = "ERROR" if strict else "WARN"
            issues.append(
                ValidationIssue(
                    severity,
                    relative,
                    f"frontmatter domain '{domain}' does not match '{expected_domain}'",
                )
            )
    return issues


def validate_skill_template_links(only_paths: set[Path] | None, strict: bool) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for project_dir in LEARNING_PROJECTS.values():
        for skill_path in sorted(project_dir.glob("skills/**/SKILL.md")):
            if only_paths is not None:
                rel = skill_path.relative_to(ROOT)
                if rel not in only_paths:
                    continue
            if SKILL_TEMPLATE_HINT not in skill_path.read_text(encoding="utf-8"):
                severity = "ERROR" if strict else "WARN"
                issues.append(
                    ValidationIssue(
                        severity,
                        skill_path.relative_to(ROOT),
                        f"missing reference to {SKILL_TEMPLATE_HINT}",
                    )
                )
    return issues


def validate_readme_links(only_paths: set[Path] | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for project_dir in PROJECTS.values():
        for doc_name in ("README.md", "CONTEXT.md"):
            path = project_dir / doc_name
            if only_paths is not None:
                rel = path.relative_to(ROOT)
                if rel not in only_paths:
                    continue
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


def validate_text_encoding(only_paths: set[Path] | None) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if only_paths is None:
        candidates = [path for path in sorted(ROOT.rglob("*.md")) if path.is_file()]
    else:
        candidates = [ROOT / rel for rel in sorted(only_paths) if rel.suffix == ".md"]
    for path in candidates:
        if not path.exists() or not path.is_file():
            continue
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


def validate_agents_registry(strict: bool) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    registry_path = AGENTS_REGISTRY
    severity = "ERROR" if strict else "WARN"

    if not registry_path.exists():
        issues.append(ValidationIssue("ERROR", registry_path.relative_to(ROOT), "agents registry file is missing"))
        return issues

    entries = load_agents_registry(registry_path)
    if not entries:
        issues.append(ValidationIssue("ERROR", registry_path.relative_to(ROOT), "agents registry is empty or unreadable"))
        return issues

    seen_agents: set[str] = set()
    seen_projects: set[str] = set()
    discovered_projects = discover_projects()

    for entry in entries:
        missing_fields = [
            field_name
            for field_name in ("agent", "project", "protocol", "domain", "status", "title")
            if not getattr(entry, field_name).strip()
        ]
        if missing_fields:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    registry_path.relative_to(ROOT),
                    f"registry entry for project '{entry.project or '?'}' missing fields: {', '.join(missing_fields)}",
                )
            )
            continue

        if entry.agent in seen_agents:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    registry_path.relative_to(ROOT),
                    f"duplicate agent in registry: {entry.agent}",
                )
            )
        seen_agents.add(entry.agent)

        if entry.project in seen_projects:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    registry_path.relative_to(ROOT),
                    f"duplicate project in registry: {entry.project}",
                )
            )
        seen_projects.add(entry.project)

        project_path = ROOT / entry.project
        protocol_path = ROOT / entry.protocol
        if not project_path.exists():
            issues.append(
                ValidationIssue(
                    "ERROR",
                    registry_path.relative_to(ROOT),
                    f"registry project does not exist on disk: {entry.project}",
                )
            )
        if not protocol_path.exists():
            issues.append(
                ValidationIssue(
                    "ERROR",
                    registry_path.relative_to(ROOT),
                    f"registry protocol does not exist on disk: {entry.protocol}",
                )
            )
        state_path = project_path / ".project-task-state"
        if not state_path.exists():
            issues.append(
                ValidationIssue(
                    "ERROR",
                    registry_path.relative_to(ROOT),
                    f"registry project missing state file: {state_path.relative_to(ROOT)}",
                )
            )

    missing_registry_projects = sorted(set(discovered_projects) - seen_projects)
    if missing_registry_projects:
        issues.append(
            ValidationIssue(
                severity,
                registry_path.relative_to(ROOT),
                "projects discovered on disk but missing from registry: " + ", ".join(missing_registry_projects),
            )
        )

    unknown_registry_projects = sorted(seen_projects - set(discovered_projects))
    if unknown_registry_projects:
        issues.append(
            ValidationIssue(
                "ERROR",
                registry_path.relative_to(ROOT),
                "registry contains unknown projects: " + ", ".join(unknown_registry_projects),
            )
        )

    return issues


def validate_report_naming(only_paths: set[Path] | None, strict: bool) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    severity = "ERROR" if strict else "WARN"
    seen: dict[str, list[Path]] = {}
    for path in iter_report_files():
        relative = path.relative_to(ROOT)
        if any(directory in relative.parts for directory in ANALYSIS_DIRS):
            if REPORT_NAME_BAD_SUFFIXES.search(path.name):
                issues.append(
                    ValidationIssue(
                        severity,
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
    parser = argparse.ArgumentParser(description="Validate EverAgent workspace")
    parser.add_argument(
        "--mode",
        choices=["full", "changed"],
        default="full",
        help="full scans the whole repo; changed strictly validates staged changes only",
    )
    args = parser.parse_args()

    only_paths: set[Path] | None = None
    strict = False
    if args.mode == "changed":
        only_paths = _git_staged_paths()
        strict = True
        if not only_paths:
            # If git is unavailable or nothing is staged, do not pretend things are clean.
            only_paths = None
            strict = False

    validators = [
        lambda: validate_frontmatter(only_paths, strict),
        lambda: validate_skill_template_links(only_paths, strict),
        lambda: validate_readme_links(only_paths),
        validate_repository_hygiene,
        lambda: validate_text_encoding(only_paths),
        validate_git_locks,
        validate_task_state_files,
        lambda: validate_agents_registry(strict),
        lambda: validate_report_naming(only_paths, strict),
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
