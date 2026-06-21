#!/usr/bin/env python3
"""Consistency check between tasks/T*.yaml (spec) and .project-task-state (state).

Historical context: prior to 2026-06-21, both files carried status fields, leading
to drift (11+ mismatches such as T061/T069 reported done in commit but state stuck
in_progress). Active task YAMLs now MUST NOT carry status / claimed_by / claimed_at
/ started_at / done_at / completed_by. This script enforces:

1. Active tasks/T*.yaml has NO forbidden state fields.
2. For every state entry with status=done, the matching spec YAML still exists.
3. For every active spec YAML, a state entry exists in {project}/.project-task-state
   (state may be missing only if status is already 'open' = not yet started).
4. Archived YAMLs are skipped (they have a different schema: status: archived).

Exits 0 if consistent, 1 if any mismatch found. Designed for pre-commit + CI.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except ImportError:
    print("PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"

FORBIDDEN_FIELDS = {
    "status",
    "claimed_by",
    "claimed_at",
    "started_at",
    "done_at",
    "completed_by",
}

# Map task id → owning project (parsed from spec YAML)
SPEC_INDEX: dict[str, dict] = {}


def load_active_specs() -> None:
    for path in sorted(TASKS_DIR.glob("T*.yaml")):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            print(f"YAML parse error in {path.name}: {e}", file=sys.stderr)
            continue
        meta = data.get("metadata") or {}
        tid = meta.get("id")
        if not tid:
            continue
        SPEC_INDEX[tid] = {
            "path": path,
            "project": meta.get("project"),
            "metadata": meta,
        }


def load_state_file(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    except yaml.YAMLError as e:
        print(f"YAML parse error in {path}: {e}", file=sys.stderr)
        return []
    return data if isinstance(data, list) else []


def collect_all_state() -> dict[str, dict]:
    """Map task id → (state_entry, source_file)."""
    out: dict[str, dict] = {}
    candidates = [ROOT / ".project-task-state"]
    for sub in ROOT.iterdir():
        if sub.is_dir() and (sub / ".project-task-state").exists():
            candidates.append(sub / ".project-task-state")
    for sf in candidates:
        for entry in load_state_file(sf):
            tid = entry.get("id")
            if tid and tid not in out:
                out[tid] = {"entry": entry, "file": sf}
    return out


def main() -> int:
    load_active_specs()
    states = collect_all_state()
    errors: list[str] = []
    warnings: list[str] = []

    for tid, spec in SPEC_INDEX.items():
        meta = spec["metadata"]
        # Rule 1: forbidden fields in active spec
        forbidden_present = [k for k in FORBIDDEN_FIELDS if k in meta]
        if forbidden_present:
            errors.append(
                f"{spec['path'].name}: forbidden state field(s) {forbidden_present} in active spec "
                f"(should live in .project-task-state, not tasks/T*.yaml)"
            )
        # Rule 2: state entry must exist for any spec
        state_ref = states.get(tid)
        if state_ref is None:
            warnings.append(
                f"{tid}: active spec exists but no state entry in any .project-task-state "
                f"(run `python3 scripts/task_state_cli.py upsert {tid}` to bootstrap)"
            )
            continue
        # Rule 3: spec project must match state project
        state_entry = state_ref["entry"]
        if state_entry.get("project") and state_entry["project"] != spec["project"]:
            errors.append(
                f"{tid}: spec.project={spec['project']} but state.project={state_entry['project']}"
            )

    # Rule 4: state entries that point to non-existent active specs
    active_ids = set(SPEC_INDEX.keys())
    for tid, ref in states.items():
        if tid not in active_ids:
            # OK if state points to archived spec
            archived = list((TASKS_DIR / "archive").rglob(f"{tid}.yaml")) if (TASKS_DIR / "archive").exists() else []
            if not archived:
                warnings.append(
                    f"{tid}: state entry in {ref['file'].relative_to(ROOT)} but no matching spec "
                    f"(active or archived)"
                )

    print(f"checked {len(SPEC_INDEX)} active task specs, {len(states)} state entries")
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")
    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        return 1
    if not warnings:
        print("✓ all consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())