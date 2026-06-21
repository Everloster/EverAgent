#!/usr/bin/env python3
"""Strip runtime-state fields from active task YAML files.

`tasks/T*.yaml` is the task *specification* (what to do, how to verify).
`{project}/.project-task-state` is the task *runtime state* (who claimed,
when started/done). State fields in YAML cause double-bookkeeping drift.

This script removes the following fields from `metadata:` of active tasks:
    status, claimed_by, claimed_at, started_at, done_at, completed_by

It preserves field order, comments, and empty lines via ruamel.yaml when
available, falling back to PyYAML (which may reorder keys).
"""

from __future__ import annotations

import sys
from pathlib import Path

TASKS_DIR = Path(__file__).resolve().parent.parent / "tasks"
STRIP_KEYS = {
    "status",
    "claimed_by",
    "claimed_at",
    "started_at",
    "done_at",
    "completed_by",
}


def try_ruamel(paths: list[Path]) -> bool:
    """Round-trip with ruamel.yaml to preserve comments + key order."""
    try:
        from ruamel.yaml import YAML  # type: ignore
    except ImportError:
        return False

    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.preserve_quotes = True

    for p in paths:
        text = p.read_text(encoding="utf-8")
        data = yaml.load(text)
        if not isinstance(data, dict):
            continue
        meta = data.get("metadata")
        if not isinstance(meta, dict):
            continue
        removed = [k for k in meta if k in STRIP_KEYS]
        for k in removed:
            del meta[k]
        if removed:
            out = StringIO()
            yaml.dump(data, out)
            p.write_text(out.getvalue(), encoding="utf-8")
            print(f"  {p.name}: stripped {removed}")
    return True


def try_pyyaml(paths: list[Path]) -> None:
    """Fallback: PyYAML (reorders keys but is always available)."""
    import yaml  # type: ignore

    for p in paths:
        with p.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            continue
        meta = data.get("metadata")
        if not isinstance(meta, dict):
            continue
        removed = [k for k in list(meta.keys()) if k in STRIP_KEYS]
        for k in removed:
            del meta[k]
        if removed:
            with p.open("w", encoding="utf-8") as f:
                yaml.safe_dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            print(f"  {p.name}: stripped {removed}")


def main() -> int:
    active = sorted(TASKS_DIR.glob("T*.yaml"))
    if not active:
        print("no active task YAMLs found", file=sys.stderr)
        return 1
    print(f"processing {len(active)} active task YAMLs in {TASKS_DIR}")
    if not try_ruamel(active):
        try_pyyaml(active)
    return 0


if __name__ == "__main__":
    from io import StringIO

    sys.exit(main())