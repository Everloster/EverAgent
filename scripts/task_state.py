#!/usr/bin/env python3
"""Shared helpers for versioned task-state files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
STATE_FILE_NAME = ".project-task-state"
GLOBAL_PROJECT = "global"

PROJECTS = {
    "ai-learning": ROOT / "ai-learning",
    "cs-learning": ROOT / "cs-learning",
    "philosophy-learning": ROOT / "philosophy-learning",
    "psychology-learning": ROOT / "psychology-learning",
    "biology-learning": ROOT / "biology-learning",
    "github-trending-analyzer": ROOT / "github-trending-analyzer",
    GLOBAL_PROJECT: ROOT,
}

LEARNING_PROJECTS = {
    name: path
    for name, path in PROJECTS.items()
    if name not in {GLOBAL_PROJECT, "github-trending-analyzer"}
}


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
