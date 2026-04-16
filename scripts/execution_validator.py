#!/usr/bin/env python3
"""Validate task execution against versioned task-state files."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from project_lock import is_expired, lock_path_for_project, parse_lock
from task_state import GLOBAL_PROJECT, PROJECTS, TaskEntry, find_task, state_file_for_project


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_SCHEMA = ROOT / "docs" / "EXECUTION_SCHEMA.md"

ISO8601_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)?)?$")
REQUIRED_FRONTMATTER_KEYS = {"title", "domain", "report_type", "status", "updated_on"}
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
VALID_TASK_TYPES = {
    "paper_analysis",
    "knowledge_report",
    "text_analysis",
    "concept_report",
    "project_optimization",
    "new_project",
    "maintenance",
}

def build_project_rules() -> dict[str, dict[str, bool | set[str]]]:
    rules: dict[str, dict[str, bool | set[str]]] = {}
    for project_name, project_path in PROJECTS.items():
        if project_name in {GLOBAL_PROJECT, "github-trending-analyzer"}:
            rules[project_name] = {
                "requires_papers_index": False,
                "requires_wiki": False,
                "report_task_types": set(),
            }
            continue

        reports_dir = project_path / "reports"
        report_task_types: set[str] = set()
        if (reports_dir / "paper_analyses").exists():
            report_task_types.add("paper_analysis")
        if (reports_dir / "knowledge_reports").exists():
            report_task_types.add("knowledge_report")
        if (reports_dir / "text_analyses").exists():
            report_task_types.add("text_analysis")
        if (reports_dir / "concept_reports").exists():
            report_task_types.add("concept_report")

        rules[project_name] = {
            "requires_papers_index": (project_path / "papers" / "PAPERS_INDEX.md").exists(),
            "requires_wiki": (project_path / "wiki").exists(),
            "report_task_types": report_task_types,
        }
    return rules


PROJECT_RULES = build_project_rules()


@dataclass
class ValidationIssue:
    severity: str
    field: str
    message: str


@dataclass
class ValidationResult:
    passed: bool
    task_id: str
    issues: list[ValidationIssue] = field(default_factory=list)

    def add_error(self, field: str, message: str) -> None:
        self.issues.append(ValidationIssue("ERROR", field, message))
        self.passed = False

    def add_warning(self, field: str, message: str) -> None:
        self.issues.append(ValidationIssue("WARN", field, message))


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


def _parse_iso8601(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _extract_task_keywords(target: str) -> list[str]:
    normalized = re.sub(r"[()/:,+]", " ", target)
    raw_keywords = [token.strip() for token in re.split(r"\s+|或|->", normalized) if token.strip()]
    keywords: list[str] = []
    for token in raw_keywords:
        if len(token) < 2:
            continue
        if token.isdigit():
            continue
        lowered = token.lower()
        if lowered not in keywords:
            keywords.append(lowered)
    return keywords


def _discover_recent_reports(project_path: Path, task: TaskEntry, claimed_at: Optional[datetime]) -> list[Path]:
    reports_dir = project_path / "reports"
    if not reports_dir.exists():
        return []

    candidates = [path for path in reports_dir.rglob("*.md") if path.is_file()]
    keywords = _extract_task_keywords(task.target)

    def matches(path: Path) -> bool:
        haystack = f"{path.name}\n{path.read_text(encoding='utf-8')[:2000]}".lower()
        return any(keyword in haystack for keyword in keywords)

    matched = [path for path in candidates if matches(path)]
    if not matched:
        matched = sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)

    if claimed_at is None:
        return matched[:3]

    recent: list[Path] = []
    for path in matched:
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if modified >= claimed_at.astimezone(timezone.utc):
            recent.append(path)
    return (recent or matched)[:5]


def _validate_frontmatter(project: str, report_paths: list[Path]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for report_path in report_paths:
        frontmatter = parse_frontmatter(report_path.read_text(encoding="utf-8"))
        if frontmatter is None:
            issues.append(ValidationIssue("ERROR", str(report_path.relative_to(ROOT)), "missing YAML frontmatter"))
            continue
        missing_keys = REQUIRED_FRONTMATTER_KEYS - set(frontmatter)
        if missing_keys:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    str(report_path.relative_to(ROOT)),
                    "frontmatter missing keys: " + ", ".join(sorted(missing_keys)),
                )
            )
        domain = frontmatter.get("domain")
        if domain and domain != project:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    str(report_path.relative_to(ROOT)),
                    f"frontmatter domain '{domain}' does not match '{project}'",
                )
            )
    return issues


def _validate_expected_updates(task: TaskEntry, project_path: Path, result: ValidationResult) -> None:
    rules = PROJECT_RULES[task.project]
    claimed_at = _parse_iso8601(task.claimed_at)

    context_path = project_path / "CONTEXT.md"
    if not context_path.exists():
        result.add_error("context", f"CONTEXT.md not found: {context_path}")
    elif claimed_at:
        modified = datetime.fromtimestamp(context_path.stat().st_mtime, tz=timezone.utc)
        if modified < claimed_at.astimezone(timezone.utc):
            result.add_error("context", "CONTEXT.md was not updated after task claim")

    report_paths = _discover_recent_reports(project_path, task, claimed_at)
    if task.type in rules["report_task_types"] and not report_paths:
        result.add_error("reports", "No recently updated report was found for this task")
    for issue in _validate_frontmatter(task.project, report_paths):
        if issue.severity == "ERROR":
            result.add_error(issue.field, issue.message)
        else:
            result.add_warning(issue.field, issue.message)

    if rules["requires_papers_index"] and task.type == "paper_analysis":
        papers_index = project_path / "papers" / "PAPERS_INDEX.md"
        if not papers_index.exists():
            result.add_error("papers_index", f"PAPERS_INDEX.md not found: {papers_index}")
        elif claimed_at:
            modified = datetime.fromtimestamp(papers_index.stat().st_mtime, tz=timezone.utc)
            if modified < claimed_at.astimezone(timezone.utc):
                result.add_error("papers_index", "PAPERS_INDEX.md was not updated after task claim")

    if rules["requires_wiki"] and task.type in rules["report_task_types"]:
        wiki_index = project_path / "wiki" / "index.md"
        wiki_log = project_path / "wiki" / "log.md"
        for label, path in {"wiki_index": wiki_index, "wiki_log": wiki_log}.items():
            if not path.exists():
                result.add_error(label, f"Required wiki file not found: {path}")
                continue
            if claimed_at:
                modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                if modified < claimed_at.astimezone(timezone.utc):
                    result.add_error(label, f"{path.name} was not updated after task claim")


def _validate_lock_for_input(task: TaskEntry, result: ValidationResult) -> None:
    if task.project == GLOBAL_PROJECT:
        return
    try:
        lock = parse_lock(lock_path_for_project(task.project))
    except (KeyError, ValueError) as exc:
        result.add_error("lock", str(exc))
        return

    if lock is None:
        return
    if is_expired(lock):
        result.add_warning("lock", f"Expired lock exists for {task.project}; safe to replace")
        return
    result.add_error("lock", f"Active project lock exists: task={lock.task_id} agent={lock.agent}")


def _validate_lock_for_output(task: TaskEntry, result: ValidationResult) -> None:
    if task.project == GLOBAL_PROJECT:
        return
    lock = parse_lock(lock_path_for_project(task.project))
    if lock is None:
        result.add_warning("lock", "No project lock found; release step may have been skipped")
        return
    if is_expired(lock):
        result.add_error("lock", f"Project lock expired before completion: task={lock.task_id} agent={lock.agent}")
        return
    if lock.task_id != task.id:
        result.add_error("lock", f"Project lock task mismatch: expected {task.id}, found {lock.task_id}")


def _require_task(task_id: str, result: ValidationResult) -> Optional[TaskEntry]:
    task = find_task(task_id)
    if task is None:
        result.add_error("task_id", f"Task {task_id} not found in any .project-task-state file")
    return task


def validate_input_schema(task_id: str, project: Optional[str] = None) -> ValidationResult:
    result = ValidationResult(passed=True, task_id=task_id)
    task = _require_task(task_id, result)
    if task is None:
        return result

    if project and task.project != project:
        result.add_error("project", f"Project mismatch: expected {task.project}, got {project}")
    if task.type not in VALID_TASK_TYPES:
        result.add_error("type", f"Unknown task type: {task.type}")
    if task.status != "open":
        result.add_error("status", f"Task status is '{task.status}', expected 'open'")
    if task.claimed_by is not None:
        result.add_error("claimed_by", f"Task already claimed by {task.claimed_by}")
    if task.project not in PROJECTS:
        result.add_error("project", f"Unknown project for task: {task.project}")
        return result
    state_file = state_file_for_project(task.project)
    if not state_file.exists():
        result.add_error("state_file", f"Task state file missing: {state_file}")
    if task.project != GLOBAL_PROJECT:
        context_path = PROJECTS[task.project] / "CONTEXT.md"
        if not context_path.exists():
            result.add_error("context", f"CONTEXT.md not found: {context_path}")
    if not EXECUTION_SCHEMA.exists():
        result.add_warning("schema", f"EXECUTION_SCHEMA.md not found: {EXECUTION_SCHEMA}")
    _validate_lock_for_input(task, result)
    return result


def validate_output_schema(task_id: str, project: Optional[str] = None) -> ValidationResult:
    result = ValidationResult(passed=True, task_id=task_id)
    task = _require_task(task_id, result)
    if task is None:
        return result

    if project and task.project != project:
        result.add_error("project", f"Project mismatch: expected {task.project}, got {project}")
    if task.status not in {"done", "failed"}:
        result.add_error("status", f"Task status is '{task.status}', expected 'done' or 'failed'")
    if task.status == "done":
        if not task.done_at:
            result.add_error("done_at", "status=done but done_at is null")
        elif not ISO8601_RE.match(task.done_at):
            result.add_error("done_at", f"done_at is not ISO8601: {task.done_at}")
    if task.status == "failed" and not task.failed_reason:
        result.add_error("failed_reason", "status=failed but failed_reason is null")
    if task.claimed_by is None:
        result.add_error("claimed_by", "claimed_by is null")
    if task.project not in PROJECTS:
        result.add_error("project", f"Unknown project for task: {task.project}")
        return result

    _validate_lock_for_output(task, result)

    if task.project != GLOBAL_PROJECT:
        _validate_expected_updates(task, PROJECTS[task.project], result)
    return result


def validate_self_check() -> ValidationResult:
    result = ValidationResult(passed=True, task_id="self-check")
    if not EXECUTION_SCHEMA.exists():
        result.add_error("schema", f"EXECUTION_SCHEMA.md not found: {EXECUTION_SCHEMA}")
    for project, project_path in PROJECTS.items():
        if project == GLOBAL_PROJECT:
            state_path = state_file_for_project(project)
            if not state_path.exists():
                result.add_error("state_file", f"Global task-state file missing: {state_path}")
            continue
        if not project_path.exists():
            result.add_error("project", f"Project directory missing: {project_path}")
            continue
        state_path = state_file_for_project(project)
        if not state_path.exists():
            result.add_error("state_file", f"Task-state file missing: {state_path}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Execution Validator")
    parser.add_argument("--mode", required=True, choices=["input", "output", "self-check"])
    parser.add_argument("--task-id", help="Task ID such as T001")
    parser.add_argument("--project", help="Project name such as ai-learning")
    return parser


def print_result(result: ValidationResult) -> None:
    print(f"[{'PASS' if result.passed else 'FAIL'}] Task {result.task_id}")
    for issue in result.issues:
        prefix = "ERROR" if issue.severity == "ERROR" else "WARN "
        print(f"  [{prefix}] {issue.field}: {issue.message}")


def main() -> int:
    args = build_parser().parse_args()

    if args.mode in {"input", "output"} and not args.task_id:
        print(f"[ERROR] --task-id is required for --mode={args.mode}", file=sys.stderr)
        return 2

    if args.mode == "input":
        result = validate_input_schema(args.task_id, args.project)
    elif args.mode == "output":
        result = validate_output_schema(args.task_id, args.project)
    else:
        result = validate_self_check()

    print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
