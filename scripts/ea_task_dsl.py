#!/usr/bin/env python3
"""EverAgent Declarative Task DSL — Phase 3 implementation.

New tasks can be defined as standalone YAML files under tasks/ directory.
This enables self-describing tasks with dependency graphs, resource declarations,
and quality gates.

Task DSL Schema (v1.0):
    apiVersion: everagent.io/v1
    kind: Task
    metadata:
      id: T030
      project: ai-learning
    spec:
      type: knowledge_report
      target: "报告标题"
      priority: P1
      dependencies:
        - task: T029
          condition: done
      resources:
        max_tokens: 50000
        expected_duration: 2h
      qualityGates:
        - check: frontmatter_complete
          required: true
      retryPolicy:
        maxRetries: 2
        backoff: exponential
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from ea_common import ROOT


TASKS_DIR = ROOT / "tasks"
VALID_TASK_TYPES = {
    "paper_analysis",
    "knowledge_report",
    "text_analysis",
    "concept_report",
    "project_optimization",
    "new_project",
    "maintenance",
}
VALID_PRIORITIES = {"P1", "P2", "P3"}
VALID_BACKOFFS = {"fixed", "linear", "exponential"}
TASK_ID_PATTERN = re.compile(r"^T\d{3,}$")


@dataclass
class TaskDependency:
    task_id: str
    condition: str = "done"


@dataclass
class TaskResource:
    max_tokens: Optional[int] = None
    expected_duration: Optional[str] = None


@dataclass
class QualityGate:
    check: str
    required: bool = True


@dataclass
class RetryPolicy:
    max_retries: int = 0
    backoff: str = "fixed"


@dataclass
class TaskSpec:
    type: str
    target: str
    priority: str = "P2"
    value: str = ""
    dependencies: list[TaskDependency] = field(default_factory=list)
    resources: TaskResource = field(default_factory=lambda: TaskResource())
    quality_gates: list[QualityGate] = field(default_factory=list)
    retry_policy: RetryPolicy = field(default_factory=lambda: RetryPolicy())


@dataclass
class TaskDSL:
    api_version: str
    kind: str
    task_id: str
    project: str
    spec: TaskSpec

    def to_task_state_dict(self) -> dict[str, Optional[str]]:
        """Convert DSL to flat task-state dict for backward compatibility."""
        return {
            "id": self.task_id,
            "project": self.project,
            "type": self.spec.type,
            "target": self.spec.target,
            "value": self.spec.value or "",
            "priority": self.spec.priority,
            "required_capability": "task_executor",
            "status": "open",
            "claimed_by": None,
            "claimed_at": None,
        }


def _parse_yaml_block(text: str) -> dict[str, Any]:
    """Parse a constrained YAML block into nested dicts.

    Supports:
    - Top-level keys (no indent)
    - Second-level keys (2-space indent)
    - List items (4-space indent + '- ')
    """
    data: dict[str, Any] = {}
    current_section: Optional[str] = None
    current_subsection: Optional[str] = None
    current_list: list[dict[str, str]] = []

    for line in text.splitlines():
        stripped = line.rstrip()

        if not stripped or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())

        # Top-level keys (indent == 0)
        if indent == 0 and ":" in stripped:
            # Flush pending list
            if current_subsection and current_list:
                if current_section not in data or isinstance(data[current_section], str):
                    data[current_section] = {}
                data[current_section][current_subsection] = current_list
                current_list = []

            key, value = stripped.split(":", 1)
            current_section = key.strip()
            current_subsection = None
            value = value.strip()
            data[current_section] = value if value else {}
            continue

        # Second-level keys (indent == 2)
        if indent == 2 and ":" in stripped:
            # Flush pending list
            if current_subsection and current_list:
                if current_section not in data or isinstance(data[current_section], str):
                    data[current_section] = {}
                data[current_section][current_subsection] = current_list
                current_list = []

            key, value = stripped[2:].split(":", 1)
            current_subsection = key.strip()
            if current_section not in data or isinstance(data[current_section], str):
                data[current_section] = {}

            value = value.strip()
            if value:
                data[current_section][current_subsection] = value.strip('"').strip("'")
            continue

        # List items (indent >= 4, starts with '- ')
        if indent >= 4 and stripped.startswith("- "):
            item_text = stripped[2:].strip()
            item_data: dict[str, str] = {}
            # Handle multi-field list items (key: value, key: value)
            if "," in item_text and ":" in item_text:
                for part in item_text.split(","):
                    if ":" not in part:
                        continue
                    k, v = part.split(":", 1)
                    item_data[k.strip()] = v.strip().strip('"').strip("'")
            elif ":" in item_text:
                k, v = item_text.split(":", 1)
                item_data[k.strip()] = v.strip().strip('"').strip("'")
            current_list.append(item_data)
            continue

    # Flush final list
    if current_subsection and current_list:
        if current_section not in data or isinstance(data[current_section], str):
            data[current_section] = {}
        data[current_section][current_subsection] = current_list

    return data


def parse_task_dsl(path: Path) -> TaskDSL:
    """Parse a task DSL YAML file into a TaskDSL object."""
    if not path.exists():
        raise FileNotFoundError(f"Task DSL file not found: {path}")

    text = path.read_text(encoding="utf-8")
    data = _parse_yaml_block(text)

    # Build TaskDSL
    api_version = data.get("apiVersion", "everagent.io/v1")
    kind = data.get("kind", "Task")

    metadata = data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}
    task_id = metadata.get("id", "")
    project = metadata.get("project", "")

    spec_data = data.get("spec", {}) if isinstance(data.get("spec"), dict) else {}
    task_type = spec_data.get("type", "")
    target = spec_data.get("target", "")
    priority = spec_data.get("priority", "P2")
    value = spec_data.get("value", "")

    # Parse dependencies
    dependencies: list[TaskDependency] = []
    for dep in spec_data.get("dependencies", []):
        if isinstance(dep, dict):
            dependencies.append(
                TaskDependency(
                    task_id=dep.get("task", ""),
                    condition=dep.get("condition", "done"),
                )
            )

    # Parse resources
    resources_data = spec_data.get("resources", {})
    if isinstance(resources_data, dict):
        max_tokens = None
        if "max_tokens" in resources_data:
            try:
                max_tokens = int(resources_data["max_tokens"])
            except (ValueError, TypeError):
                max_tokens = None
        resources = TaskResource(
            max_tokens=max_tokens,
            expected_duration=resources_data.get("expected_duration"),
        )
    else:
        resources = TaskResource()

    # Parse quality gates
    quality_gates: list[QualityGate] = []
    for gate in spec_data.get("qualityGates", []):
        if isinstance(gate, dict):
            required_val = gate.get("required", "true")
            if isinstance(required_val, bool):
                required = required_val
            else:
                required = str(required_val).lower() == "true"
            quality_gates.append(
                QualityGate(
                    check=gate.get("check", ""),
                    required=required,
                )
            )

    # Parse retry policy
    retry_data = spec_data.get("retryPolicy", {})
    if isinstance(retry_data, dict):
        max_retries = 0
        if "maxRetries" in retry_data:
            try:
                max_retries = int(retry_data["maxRetries"])
                if max_retries < 0:
                    max_retries = 0
                elif max_retries > 10:
                    max_retries = 10
            except (ValueError, TypeError):
                max_retries = 0
        backoff = retry_data.get("backoff", "fixed")
        if backoff not in VALID_BACKOFFS:
            backoff = "fixed"
        retry_policy = RetryPolicy(
            max_retries=max_retries,
            backoff=backoff,
        )
    else:
        retry_policy = RetryPolicy()

    spec = TaskSpec(
        type=task_type,
        target=target,
        priority=priority,
        value=value,
        dependencies=dependencies,
        resources=resources,
        quality_gates=quality_gates,
        retry_policy=retry_policy,
    )

    return TaskDSL(
        api_version=api_version,
        kind=kind,
        task_id=task_id,
        project=project,
        spec=spec,
    )


def validate_task_dsl(dsl: TaskDSL) -> list[str]:
    """Validate a TaskDSL object and return list of error messages."""
    errors: list[str] = []

    if not TASK_ID_PATTERN.match(dsl.task_id):
        errors.append(f"Invalid task ID: {dsl.task_id} (expected T###)")

    if dsl.spec.type not in VALID_TASK_TYPES:
        errors.append(f"Invalid task type: {dsl.spec.type}")

    if dsl.spec.priority not in VALID_PRIORITIES:
        errors.append(f"Invalid priority: {dsl.spec.priority}")

    if not dsl.spec.target:
        errors.append("Task target is required")

    if dsl.spec.retry_policy.backoff not in VALID_BACKOFFS:
        errors.append(f"Invalid backoff: {dsl.spec.retry_policy.backoff}")

    for dep in dsl.spec.dependencies:
        if not TASK_ID_PATTERN.match(dep.task_id):
            errors.append(f"Invalid dependency task ID: {dep.task_id}")

    return errors


def load_all_task_dsls() -> list[TaskDSL]:
    """Load all task DSL files from tasks/ directory."""
    tasks: list[TaskDSL] = []
    if not TASKS_DIR.exists():
        return tasks

    for path in sorted(TASKS_DIR.glob("T*.yaml")):
        try:
            dsl = parse_task_dsl(path)
            errors = validate_task_dsl(dsl)
            if errors:
                print(f"[WARN] {path.name}: {'; '.join(errors)}")
                continue
            tasks.append(dsl)
        except Exception as exc:
            print(f"[ERROR] Failed to parse {path}: {exc}")

    return tasks


def render_task_dsl_to_state(dsl: TaskDSL) -> str:
    """Render a TaskDSL to task-state YAML format."""
    d = dsl.to_task_state_dict()
    lines = [f"- id: {d['id']}"]
    lines.append(f"  project: {d['project']}")
    lines.append(f"  type: {d['type']}")
    lines.append(f'  target: "{d["target"]}"')
    if d.get("value"):
        lines.append(f'  value: "{d["value"]}"')
    lines.append(f"  priority: {d['priority']}")
    lines.append(f"  required_capability: {d['required_capability']}")
    lines.append(f"  status: {d['status']}")
    lines.append(f"  claimed_by: null")
    lines.append(f"  claimed_at: null")
    return "\n".join(lines)


def sync_task_dsls_to_project_states(dry_run: bool = False) -> list[str]:
    """Sync all task DSLs to their respective .project-task-state files.

    Returns list of actions performed.
    """
    from task_state import load_tasks_for_project, state_file_for_project, write_task_state_file, TaskEntry

    actions: list[str] = []
    dsls = load_all_task_dsls()

    # Group by project
    by_project: dict[str, list[TaskDSL]] = {}
    for dsl in dsls:
        by_project.setdefault(dsl.project, []).append(dsl)

    for project, project_dsls in by_project.items():
        try:
            state_path = state_file_for_project(project)
        except KeyError:
            actions.append(f"SKIP: Unknown project '{project}'")
            continue

        existing_tasks = load_tasks_for_project(project)
        existing_ids = {t.id for t in existing_tasks}

        new_tasks: list[TaskEntry] = []
        for dsl in project_dsls:
            if dsl.task_id in existing_ids:
                actions.append(f"SKIP: {dsl.task_id} already exists in {project}")
                continue

            new_tasks.append(
                TaskEntry(
                    id=dsl.task_id,
                    project=dsl.project,
                    type=dsl.spec.type,
                    target=dsl.spec.target,
                    value=dsl.spec.value,
                    priority=dsl.spec.priority,
                    status="open",
                )
            )
            actions.append(f"ADD: {dsl.task_id} -> {project}")

        if new_tasks and not dry_run:
            all_tasks = existing_tasks + new_tasks
            write_task_state_file(state_path, all_tasks)

    return actions
