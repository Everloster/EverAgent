#!/usr/bin/env python3
"""EverAgent shared common utilities — Phase 0 modularization.

This module extracts shared helpers used across multiple scripts to eliminate
code duplication and provide a single source of truth for common operations.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


ISO8601_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\+\d{2}:\d{2}|Z)?)?$")


def parse_iso8601(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO8601 string to timezone-aware datetime."""
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


def format_iso8601(dt: Optional[datetime] = None) -> str:
    """Format datetime as ISO8601 string. Uses current time if dt is None."""
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.astimezone().isoformat(timespec="seconds")


def now_iso() -> str:
    """Return current time as ISO8601 string."""
    return format_iso8601()


def normalize_value(raw: str) -> Optional[str]:
    """Normalize a YAML-like string value, returning None for empty/null."""
    value = raw.strip().strip('"').strip("'")
    if value in {"", "null", "None"}:
        return None
    return value


def read_yamlish_file(path: Path) -> list[dict[str, Optional[str]]]:
    """Read a YAML-like file containing a list of items (e.g., task state, registry).

    Returns a list of dicts, each representing one item.
    """
    if not path.exists():
        return []

    items: list[dict[str, Optional[str]]] = []
    current: dict[str, Optional[str]] = {}

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current:
                items.append(current)
            current = {}
            stripped = stripped[2:]

        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        current[key.strip()] = normalize_value(value)

    if current:
        items.append(current)

    return items


def write_yamlish_file(path: Path, items: list[dict[str, Optional[str]]]) -> None:
    """Write a list of dicts to a YAML-like file."""
    lines: list[str] = []
    for index, item in enumerate(items):
        if index > 0:
            lines.append("")
        first = True
        for key, value in item.items():
            prefix = "- " if first else "  "
            first = False
            if value is None:
                lines.append(f"{prefix}{key}: null")
            else:
                lines.append(f'{prefix}{key}: "{value}"')
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
DOCS_DIR = ROOT / "docs"
EVENTS_DIR = ROOT / "events"
STATE_FILE_NAME = ".project-task-state"
AGENTS_REGISTRY_PATH = DOCS_DIR / "agents_registry.yaml"
