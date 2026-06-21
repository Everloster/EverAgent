#!/usr/bin/env python3
"""Archive state-only done tasks to per-project state-history/ files.

After 2026-06-21 audit, 38 done entries in {project}/.project-task-state have
NO matching spec YAML (active or archived). They are historical April-May
deliverables: state file was the only record at the time. We now consider them
"history" and move them out of the live state file to:

  {project}/state-history/state-only-done-{year}.yaml

Live .project-task-state keeps only:
  - entries with an active spec YAML (T058-T070 today)
  - entries with an archived spec YAML (T030-T042 today)
  - open tasks (T012 today)

check_task_state_consistency.py is updated to also consult state-history/ so
the migration is invisible to that script (warnings → 0).

Idempotent: running twice is a no-op.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"


def collect_state_files() -> list[Path]:
    out = []
    if (ROOT / ".project-task-state").exists():
        out.append(ROOT / ".project-task-state")
    for sub in sorted(ROOT.iterdir()):
        if sub.is_dir() and (sub / ".project-task-state").exists():
            out.append(sub / ".project-task-state")
    return out


def load_all_spec_ids() -> set[str]:
    ids: set[str] = set()
    for path in list(TASKS_DIR.glob("T*.yaml")) + list((TASKS_DIR / "archive").rglob("T*.yaml")):
        m = re.search(r"(T\d{3})", path.name)
        if m:
            ids.add(m.group(1))
    return ids


def project_from_state_path(state_path: Path) -> str:
    if state_path.parent == ROOT:
        return "global"
    return state_path.parent.name


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    spec_ids = load_all_spec_ids()
    state_files = collect_state_files()
    if not state_files:
        print("no state files found")
        return 0

    move_count = 0
    for sf in state_files:
        project = project_from_state_path(sf)
        entries = yaml.safe_load(sf.read_text(encoding="utf-8")) or []
        keep: list[dict] = []
        archive: list[dict] = []
        for e in entries:
            tid = e.get("id")
            status = e.get("status")
            # Archive only: done + state-only + not in spec (active or archived)
            if status == "done" and tid and tid not in spec_ids:
                archive.append(e)
            else:
                keep.append(e)
        if not archive:
            continue
        print(f"── {sf.relative_to(ROOT)} ({project}): {len(archive)} → archive, {len(keep)} → keep")
        # Group by year (from done_at if present, else current year)
        by_year: dict[str, list[dict]] = {}
        for e in archive:
            done_at = str(e.get("done_at", ""))
            year = done_at[:4] if done_at[:4].isdigit() else str(datetime.now().year)
            by_year.setdefault(year, []).append(e)
        for year, group in by_year.items():
            history_dir = sf.parent / "state-history"
            history_file = history_dir / f"state-only-done-{year}.yaml"
            print(f"     → {history_file.relative_to(ROOT)} ({len(group)} entries)")
            if args.apply:
                history_dir.mkdir(exist_ok=True)
                existing = []
                if history_file.exists():
                    existing = yaml.safe_load(history_file.read_text(encoding="utf-8")) or []
                # Dedupe by id
                seen = {e.get("id") for e in existing}
                merged = list(existing)
                for e in group:
                    if e.get("id") not in seen:
                        merged.append(e)
                        seen.add(e.get("id"))
                history_file.write_text(
                    yaml.safe_dump(merged, allow_unicode=True, sort_keys=False, default_flow_style=False),
                    encoding="utf-8",
                )
                move_count += len(group)
        if args.apply:
            # Rewrite live state file with only `keep`
            sf.write_text(
                yaml.safe_dump(keep, allow_unicode=True, sort_keys=False, default_flow_style=False),
                encoding="utf-8",
            )

    print(f"\nmoved: {move_count} entries" if args.apply else "\n(dry-run; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())