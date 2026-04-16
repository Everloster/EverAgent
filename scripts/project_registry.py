#!/usr/bin/env python3
"""Discover EverAgent subprojects and load machine-readable project registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_PROJECT = "global"
NON_LEARNING_PROJECTS = {"github-trending-analyzer"}
STATE_FILE_NAME = ".project-task-state"
AGENTS_REGISTRY = ROOT / "docs" / "agents_registry.yaml"


@dataclass(frozen=True)
class AgentRegistryEntry:
    agent: str
    project: str
    protocol: str
    domain: str
    status: str
    title: str


def discover_projects(root: Path = ROOT) -> dict[str, Path]:
    projects: dict[str, Path] = {}
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if (child / "AGENTS.md").exists() and (child / STATE_FILE_NAME).exists():
            projects[child.name] = child
    return projects


def discover_learning_projects(root: Path = ROOT) -> dict[str, Path]:
    return {
        name: path
        for name, path in discover_projects(root).items()
        if name not in NON_LEARNING_PROJECTS
    }


def load_agents_registry(path: Path = AGENTS_REGISTRY) -> list[AgentRegistryEntry]:
    if not path.exists():
        return []

    entries: list[AgentRegistryEntry] = []
    current: dict[str, str] = {}

    def normalize_value(raw: str) -> str:
        return raw.strip().strip('"').strip("'")

    def flush() -> None:
        if not current:
            return
        entries.append(
            AgentRegistryEntry(
                agent=current.get("agent", ""),
                project=current.get("project", ""),
                protocol=current.get("protocol", ""),
                domain=current.get("domain", ""),
                status=current.get("status", ""),
                title=current.get("title", ""),
            )
        )

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- "):
            flush()
            current = {}
            stripped = stripped[2:]
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = normalize_value(value)

    flush()
    return entries
