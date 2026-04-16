#!/usr/bin/env python3
"""Discover EverAgent subprojects from the repository layout."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_PROJECT = "global"
NON_LEARNING_PROJECTS = {"github-trending-analyzer"}
STATE_FILE_NAME = ".project-task-state"


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

