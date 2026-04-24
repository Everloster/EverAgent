#!/usr/bin/env python3
"""CLI for safe task-state transitions.

Phase 1: All state transitions now emit events to the event log.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone

from ea_events import emit_event
from task_state import (
    TaskEntry,
    append_task,
    find_task,
    load_tasks_for_project,
    now_iso,
    parse_iso8601,
    replace_task,
    update_task,
)


VALID_TRANSITIONS = {
    "claim": {"open"},
    "start": {"claimed", "help_needed"},
    "done": {"claimed", "in_progress", "help_needed"},
    "fail": {"claimed", "in_progress", "help_needed"},
    "help": {"claimed", "in_progress"},
    "cancel": {"open", "claimed", "in_progress", "help_needed"},
    "expire": {"open", "claimed", "in_progress", "help_needed"},
    "abandon": {"claimed", "in_progress", "help_needed"},
    "reopen": {"failed", "abandoned", "cancelled", "expired", "help_needed"},
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


def command_dispatch(args: argparse.Namespace) -> int:
    if find_task(args.task_id) is not None:
        raise ValueError(f"Task {args.task_id} already exists")

    task = TaskEntry(
        id=args.task_id,
        project=args.project,
        type=args.type,
        target=args.target,
        value=args.value or "",
        priority=args.priority,
        required_capability=args.required_capability,
        status="open",
        parent_task_id=args.parent_task_id,
        expires_at=args.expires_at,
        context_links=tuple(args.context_links or ()),
    )
    append_task(args.project, task)
    emit_event(
        event_type="task_dispatched",
        actor=args.actor,
        project=args.project,
        task_id=args.task_id,
        payload={
            "target": args.target,
            "type": args.type,
            "priority": args.priority,
            "parent_task_id": args.parent_task_id,
            "expires_at": args.expires_at,
            "context_links": args.context_links or [],
        },
        dedupe_key=f"{args.task_id}:task.dispatch:{args.actor}",
    )
    print(f"[PASS] Dispatched {args.task_id} to {args.project}")
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
    emit_event(
        event_type="task_claimed",
        actor=args.agent,
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "type": task.type},
    )
    print(f"[PASS] Claimed {task.id} for {args.agent}")
    return 0


def command_start(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "start")
    updated = update_task(task, status="in_progress", started_at=task.started_at or now_iso(), help_reason=None)
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_started",
        actor=task.claimed_by or "unknown",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target},
    )
    print(f"[PASS] Started {task.id}")
    return 0


def command_done(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "done")
    updated = update_task(task, status="done", done_at=now_iso(), failed_reason=None)
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_done",
        actor=task.claimed_by or "unknown",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "duration_hint": "completed"},
    )
    print(f"[PASS] Marked {task.id} done")
    return 0


def command_fail(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "fail")
    updated = update_task(task, status="failed", failed_reason=args.reason, done_at=None)
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_failed",
        actor=task.claimed_by or "unknown",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "reason": args.reason},
    )
    print(f"[PASS] Marked {task.id} failed")
    return 0


def command_help(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "help")
    updated = update_task(task, status="help_needed", help_reason=args.reason)
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_help_needed",
        actor=task.claimed_by or "unknown",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "reason": args.reason, "suggested_options": args.suggested_options or []},
    )
    print(f"[PASS] Marked {task.id} help_needed")
    return 0


def command_cancel(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "cancel")
    updated = update_task(
        task,
        status="cancelled",
        cancelled_at=now_iso(),
        failed_reason=args.reason or "cancelled",
    )
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_cancelled",
        actor=args.actor or task.claimed_by or "system",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "reason": args.reason or "cancelled"},
    )
    print(f"[PASS] Cancelled {task.id}")
    return 0


def command_expire(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "expire")
    expires_at = parse_iso8601(task.expires_at)
    if not args.force:
        if expires_at is None:
            raise ValueError(f"Task {task.id} has no valid expires_at")
        if expires_at.astimezone(timezone.utc) > datetime.now(timezone.utc):
            raise ValueError(f"Task {task.id} has not expired yet: {task.expires_at}")

    updated = update_task(
        task,
        status="expired",
        failed_reason=args.reason or "expired",
    )
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_expired",
        actor=args.actor or "system",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "reason": args.reason or "expired", "expires_at": task.expires_at},
    )
    print(f"[PASS] Expired {task.id}")
    return 0


def command_abandon(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "abandon")
    updated = update_task(task, status="abandoned", failed_reason=args.reason or "abandoned")
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_abandoned",
        actor=task.claimed_by or "unknown",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target, "reason": args.reason or "abandoned"},
    )
    print(f"[PASS] Marked {task.id} abandoned")
    return 0


def command_reopen(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    ensure_transition(task, "reopen")
    updated = update_task(
        task,
        status="open",
        claimed_by=None,
        claimed_at=None,
        started_at=None,
        done_at=None,
        failed_reason=None,
        help_reason=None,
        cancelled_at=None,
    )
    replace_task(task.project, task.id, updated)
    emit_event(
        event_type="task_reopened",
        actor="system",
        project=task.project,
        task_id=task.id,
        payload={"target": task.target},
    )
    print(f"[PASS] Reopened {task.id}")
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

    dispatch_parser = subparsers.add_parser("dispatch")
    dispatch_parser.add_argument("--task-id", required=True)
    dispatch_parser.add_argument("--project", required=True)
    dispatch_parser.add_argument("--type", required=True)
    dispatch_parser.add_argument("--target", required=True)
    dispatch_parser.add_argument("--value")
    dispatch_parser.add_argument("--priority", default="P2", choices=["P1", "P2", "P3"])
    dispatch_parser.add_argument("--required-capability", default="task_executor")
    dispatch_parser.add_argument("--parent-task-id")
    dispatch_parser.add_argument("--expires-at")
    dispatch_parser.add_argument("--context-links", nargs="*")
    dispatch_parser.add_argument("--actor", default="EverAgent")
    dispatch_parser.set_defaults(func=command_dispatch)

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

    help_parser = subparsers.add_parser("help")
    help_parser.add_argument("--task-id", required=True)
    help_parser.add_argument("--reason", required=True)
    help_parser.add_argument("--suggested-options", nargs="*", help="Optional suggested next actions")
    help_parser.set_defaults(func=command_help)

    cancel_parser = subparsers.add_parser("cancel")
    cancel_parser.add_argument("--task-id", required=True)
    cancel_parser.add_argument("--reason")
    cancel_parser.add_argument("--actor")
    cancel_parser.set_defaults(func=command_cancel)

    expire_parser = subparsers.add_parser("expire")
    expire_parser.add_argument("--task-id", required=True)
    expire_parser.add_argument("--reason")
    expire_parser.add_argument("--actor")
    expire_parser.add_argument("--force", action="store_true")
    expire_parser.set_defaults(func=command_expire)

    abandon_parser = subparsers.add_parser("abandon")
    abandon_parser.add_argument("--task-id", required=True)
    abandon_parser.add_argument("--reason")
    abandon_parser.set_defaults(func=command_abandon)

    reopen_parser = subparsers.add_parser("reopen")
    reopen_parser.add_argument("--task-id", required=True)
    reopen_parser.set_defaults(func=command_reopen)
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
