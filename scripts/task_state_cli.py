#!/usr/bin/env python3
"""CLI for safe task-state transitions."""

from __future__ import annotations

import argparse
import sys

from task_state import (
    TaskEntry,
    find_task,
    load_tasks_for_project,
    now_iso,
    replace_task,
    update_task,
)


VALID_TRANSITIONS = {
    "claim": {"open"},
    "start": {"claimed"},
    "done": {"claimed", "in_progress"},
    "fail": {"claimed", "in_progress"},
    "abandon": {"claimed", "in_progress"},
}


def require_task(task_id: str) -> TaskEntry:
    task = find_task(task_id)
    if task is None:
        raise KeyError(f"Task {task_id} not found")
    return task


def ensure_transition(task: TaskEntry, command: str) -> None:
    allowed = VALID_TRANSITIONS[command]
    if task.status not in allowed:
        raise ValueError(f"Task {task.id} status '{task.status}' cannot transition via '{command}'")


def command_list(args: argparse.Namespace) -> int:
    tasks = load_tasks_for_project(args.project)
    if args.status:
        tasks = [task for task in tasks if task.status == args.status]
    for task in tasks:
        print(f"{task.id}\t{task.status}\t{task.type}\t{task.target}")
    return 0


def command_show(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    for line in task.to_lines():
        print(line)
    return 0


def command_claim(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "claim")
    updated = update_task(
        task,
        status="claimed",
        claimed_by=args.agent,
        claimed_at=now_iso(),
        failed_reason=None,
    )
    replace_task(task.project, task.id, updated)
    print(f"[PASS] Claimed {task.id} for {args.agent}")
    return 0


def command_start(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "start")
    updated = update_task(task, status="in_progress", started_at=now_iso())
    replace_task(task.project, task.id, updated)
    print(f"[PASS] Started {task.id}")
    return 0


def command_done(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "done")
    updated = update_task(task, status="done", done_at=now_iso(), failed_reason=None)
    replace_task(task.project, task.id, updated)
    print(f"[PASS] Marked {task.id} done")
    return 0


def command_fail(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "fail")
    updated = update_task(task, status="failed", failed_reason=args.reason, done_at=None)
    replace_task(task.project, task.id, updated)
    print(f"[PASS] Marked {task.id} failed")
    return 0


def command_abandon(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "abandon")
    updated = update_task(task, status="abandoned", failed_reason=args.reason or "abandoned")
    replace_task(task.project, task.id, updated)
    print(f"[PASS] Marked {task.id} abandoned")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage task-state transitions")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--project", required=True)
    list_parser.add_argument("--status")
    list_parser.set_defaults(func=command_list)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("--task-id", required=True)
    show_parser.set_defaults(func=command_show)

    claim_parser = subparsers.add_parser("claim")
    claim_parser.add_argument("--task-id", required=True)
    claim_parser.add_argument("--agent", required=True)
    claim_parser.set_defaults(func=command_claim)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--task-id", required=True)
    start_parser.set_defaults(func=command_start)

    done_parser = subparsers.add_parser("done")
    done_parser.add_argument("--task-id", required=True)
    done_parser.set_defaults(func=command_done)

    fail_parser = subparsers.add_parser("fail")
    fail_parser.add_argument("--task-id", required=True)
    fail_parser.add_argument("--reason", required=True)
    fail_parser.set_defaults(func=command_fail)

    abandon_parser = subparsers.add_parser("abandon")
    abandon_parser.add_argument("--task-id", required=True)
    abandon_parser.add_argument("--reason")
    abandon_parser.set_defaults(func=command_abandon)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except (KeyError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
