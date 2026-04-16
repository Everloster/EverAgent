#!/usr/bin/env python3
"""Shared helpers for versioned task-state files."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from project_registry import GLOBAL_PROJECT, ROOT, discover_learning_projects, discover_projects

STATE_FILE_NAME = ".project-task-state"
PROJECTS = {**discover_projects(), GLOBAL_PROJECT: ROOT}
LEARNING_PROJECTS = discover_learning_projects()


@dataclass
class TaskEntry:
    id: str
    project: str
    type: str
    target: str
    value: str = ""
    priority: str = "P2"
    required_capability: str = "task_executor"
    status: str = "open"
    claimed_by: Optional[str] = None
    claimed_at: Optional[str] = None
    started_at: Optional[str] = None
    done_at: Optional[str] = None
    failed_reason: Optional[str] = None

    @property
    def is_open(self) -> bool:
        return self.status == "open"

    @property
    def is_active(self) -> bool:
        return self.status in {"claimed", "in_progress"}

    @property
    def is_done(self) -> bool:
        return self.status == "done"

    def to_lines(self) -> list[str]:
        lines = [f"- id: {self.id}"]
        lines.append(f"  project: {self.project}")
        lines.append(f"  type: {self.type}")
        lines.append(f'  target: "{self.target}"')
        if self.value:
            lines.append(f'  value: "{self.value}"')
        lines.append(f"  priority: {self.priority}")
        lines.append(f"  required_capability: {self.required_capability}")
        lines.append(f"  status: {self.status}")
        lines.append(f"  claimed_by: {self.claimed_by or 'null'}")
        lines.append(f"  claimed_at: {self.claimed_at or 'null'}")
        if self.started_at is not None:
            lines.append(f"  started_at: {self.started_at}")
        if self.done_at is not None:
            lines.append(f"  done_at: {self.done_at}")
        if self.failed_reason is not None:
            lines.append(f'  failed_reason: "{self.failed_reason}"')
        return lines


def state_file_for_project(project: str) -> Path:
    if project not in PROJECTS:
        raise KeyError(f"Unknown project: {project}")
    return PROJECTS[project] / STATE_FILE_NAME


def list_state_files() -> dict[str, Path]:
    return {project: state_file_for_project(project) for project in PROJECTS}


def _normalize_value(raw: str) -> Optional[str]:
    value = raw.strip().strip('"').strip("'")
    if value in {"", "null", "None"}:
        return None
    return value


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_iso8601(value: Optional[str]) -> Optional[datetime]:
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


def parse_task_state_file(path: Path, default_project: Optional[str] = None) -> list[TaskEntry]:
    if not path.exists():
        return []

    tasks: list[TaskEntry] = []
    current: dict[str, Optional[str]] = {}

    def flush() -> None:
        if not current.get("id"):
            return
        tasks.append(
            TaskEntry(
                id=current.get("id") or "",
                project=current.get("project") or (default_project or ""),
                type=current.get("type") or "",
                target=current.get("target") or "",
                value=current.get("value") or "",
                priority=current.get("priority") or "P2",
                required_capability=current.get("required_capability") or "task_executor",
                status=current.get("status") or "open",
                claimed_by=current.get("claimed_by"),
                claimed_at=current.get("claimed_at"),
                started_at=current.get("started_at"),
                done_at=current.get("done_at"),
                failed_reason=current.get("failed_reason"),
            )
        )

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- id:"):
            flush()
            current = {"id": _normalize_value(stripped.split(":", 1)[1])}
            continue
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = _normalize_value(value)

    flush()
    return tasks


def load_tasks_for_project(project: str) -> list[TaskEntry]:
    return parse_task_state_file(state_file_for_project(project), default_project=project)


def load_all_tasks(include_global: bool = True) -> list[TaskEntry]:
    projects = list(PROJECTS)
    if not include_global:
        projects = [project for project in projects if project != GLOBAL_PROJECT]
    tasks: list[TaskEntry] = []
    for project in projects:
        tasks.extend(load_tasks_for_project(project))
    return tasks


def find_task(task_id: str) -> Optional[TaskEntry]:
    for task in load_all_tasks(include_global=True):
        if task.id == task_id:
            return task
    return None


def find_stale_tasks(include_global: bool = False, ttl_hours: int = 72) -> list[TaskEntry]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=ttl_hours)
    stale: list[TaskEntry] = []
    for task in load_all_tasks(include_global=include_global):
        if not task.is_active:
            continue
        reference = parse_iso8601(task.started_at or task.claimed_at)
        if reference is None:
            continue
        if reference.astimezone(timezone.utc) < cutoff:
            stale.append(task)
    return stale


def replace_task(project: str, task_id: str, updated_task: TaskEntry) -> None:
    path = state_file_for_project(project)
    tasks = load_tasks_for_project(project)
    replaced = False
    updated_tasks: list[TaskEntry] = []
    for task in tasks:
        if task.id == task_id:
            updated_tasks.append(updated_task)
            replaced = True
        else:
            updated_tasks.append(task)
    if not replaced:
        raise KeyError(f"Task {task_id} not found in {path}")
    write_task_state_file(path, updated_tasks)


def write_task_state_file(path: Path, tasks: list[TaskEntry]) -> None:
    content_lines: list[str] = []
    for index, task in enumerate(tasks):
        if index > 0:
            content_lines.append("")
        content_lines.extend(task.to_lines())
    path.write_text("\n".join(content_lines).rstrip() + "\n", encoding="utf-8")


def update_task(task: TaskEntry, **changes: Optional[str]) -> TaskEntry:
    return replace(task, **changes)
