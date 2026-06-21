#!/usr/bin/env python3
"""Backfill context_links for done tasks that lack them.

Triggered after 2026-06-21 audit found 11 done tasks (T058-T069 etc.) whose
state.context_links is empty. This blocks quality_gates.py from validating
the right report file (it falls back to most-recent heuristics).

Algorithm: for each done task with empty context_links:
  1. Read state.target
  2. Scan subproject report directories (same mapping as quality_gates)
  3. Pick the .md whose frontmatter.title best token-matches state.target
  4. Set state.context_links = [relative path to that report]

Idempotent: only modifies entries with empty context_links. Exits 0 always
(dry-run by default; pass --apply to mutate).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from task_state import find_task, replace_task, load_tasks_for_project  # noqa: E402


SUBPROJECT_REPORT_DIRS = {
    "ai-learning": ["reports", "papers"],
    "cs-learning": ["reports", "papers"],
    "philosophy-learning": ["reports", "papers"],
    "psychology-learning": ["reports", "papers"],
    "biology-learning": ["reports", "papers"],
    "podcast-learning": ["reports", "papers"],
    "ai-practice": ["experiments", "src"],
    "github-trending-analyzer": [
        "github-trending-reports",
        "everloster-star-analysis/reports",
        "reports",
    ],
}


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError:
        return {}


def score_match(md_path: Path, target: str) -> int:
    if not target:
        return 0
    target_tokens = {t for t in re.split(r"[\s/:×x_，,。、]+", target) if len(t) >= 2}
    fname_tokens = {t for t in re.split(r"[_]+", md_path.stem) if len(t) >= 2}
    score = len(target_tokens & fname_tokens) * 2
    fm = load_frontmatter(md_path)
    title = str(fm.get("title", ""))
    title_tokens = {t for t in re.split(r"[\s/:×x_，,。、()]+", title) if len(t) >= 2}
    score += len(target_tokens & title_tokens) * 3
    return score


def find_best_report(project: str, target: str) -> Path | None:
    proj_dir = ROOT / project
    if not proj_dir.exists():
        return None
    candidates: list[Path] = []
    for subdir in SUBPROJECT_REPORT_DIRS.get(project, ["reports"]):
        d = proj_dir / subdir
        if d.exists():
            candidates.extend(d.rglob("*.md"))
    if not candidates:
        return None
    if target:
        scored = sorted(candidates, key=lambda c: (-score_match(c, target), -c.stat().st_mtime))
        if score_match(scored[0], target) > 0:
            return scored[0]
    return max(candidates, key=lambda p: p.stat().st_mtime)


def collect_done_with_empty_links() -> list[tuple[str, str, str]]:
    """Returns list of (task_id, project, target)."""
    out: list[tuple[str, str, str]] = []
    candidates = [ROOT / ".project-task-state"]
    for sub in ROOT.iterdir():
        if sub.is_dir() and (sub / ".project-task-state").exists():
            candidates.append(sub / ".project-task-state")
    for sf in candidates:
        data = yaml.safe_load(sf.read_text(encoding="utf-8")) or []
        for entry in data:
            if entry.get("status") != "done":
                continue
            if entry.get("context_links"):
                continue
            tid = entry.get("id")
            project = entry.get("project", "")
            target = entry.get("target", "")
            if tid and project:
                out.append((tid, project, target))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="actually mutate state files")
    args = parser.parse_args()

    pending = collect_done_with_empty_links()
    if not pending:
        print("✓ no done tasks with empty context_links")
        return 0

    print(f"{'BACKFILL PLAN' if not args.apply else 'APPLYING'}: {len(pending)} task(s)\n")
    applied = skipped = 0
    for tid, project, target in pending:
        report = find_best_report(project, target)
        if not report:
            print(f"  ⚠ {tid} [{project}]: no report candidate found, skip")
            skipped += 1
            continue
        rel = str(report.relative_to(ROOT))
        print(f"  {tid} [{project}]: {rel}")
        if args.apply:
            task = find_task(tid)
            if task is None:
                print(f"     ✗ task not found in any state file (state-only entry)")
                skipped += 1
                continue
            updated = task.__class__(
                **{**task.__dict__, "context_links": (rel,)}
            )
            replace_task(task.project, task.id, updated)
            applied += 1
    print(f"\napplied: {applied}, skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())