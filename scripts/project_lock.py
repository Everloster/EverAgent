#!/usr/bin/env python3
"""Manage per-project agent locks."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from task_state import GLOBAL_PROJECT, PROJECTS


DEFAULT_TTL_HOURS = 72


@dataclass
class LockInfo:
    path: Path
    agent: Optional[str] = None
    task_id: Optional[str] = None
    claimed_at: Optional[str] = None
    git_commit_sha: Optional[str] = None


def lock_path_for_project(project: str) -> Path:
    if project == GLOBAL_PROJECT:
        raise ValueError("Global tasks do not use project locks")
    if project not in PROJECTS:
        raise KeyError(f"Unknown project: {project}")
    return PROJECTS[project] / ".agent-lock"


def parse_lock(path: Path) -> Optional[LockInfo]:
    if not path.exists():
        return None

    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip()

    return LockInfo(
        path=path,
        agent=data.get("agent"),
        task_id=data.get("task_id"),
        claimed_at=data.get("claimed_at"),
        git_commit_sha=data.get("git_commit_sha"),
    )


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def is_expired(lock: LockInfo, ttl_hours: int = DEFAULT_TTL_HOURS) -> bool:
    claimed_at = _parse_datetime(lock.claimed_at)
    if claimed_at is None:
        return False
    if claimed_at.tzinfo is None:
        claimed_at = claimed_at.replace(tzinfo=timezone.utc)
    return claimed_at + timedelta(hours=ttl_hours) < datetime.now(timezone.utc)


def write_lock(project: str, task_id: str, agent: str, git_commit_sha: str = "") -> Path:
    path = lock_path_for_project(project)
    claimed_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    payload = "\n".join(
        [
            f"agent: {agent}",
            f"task_id: {task_id}",
            f"claimed_at: {claimed_at}",
            f"git_commit_sha: {git_commit_sha}",
            "",
        ]
    )
    path.write_text(payload, encoding="utf-8")
    return path


def command_check(args: argparse.Namespace) -> int:
    lock = parse_lock(lock_path_for_project(args.project))
    if lock is None:
        print(f"[PASS] No active lock for {args.project}")
        return 0

    if is_expired(lock, args.ttl_hours):
        print(f"[WARN] Expired lock for {args.project}: task={lock.task_id} agent={lock.agent}")
        return 0

    print(f"[FAIL] Active lock for {args.project}: task={lock.task_id} agent={lock.agent}")
    return 1


def command_acquire(args: argparse.Namespace) -> int:
    path = lock_path_for_project(args.project)
    lock = parse_lock(path)

    if lock and not is_expired(lock, args.ttl_hours):
        if lock.task_id == args.task_id and lock.agent == args.agent:
            print(f"[PASS] Lock already held for {args.project}: task={lock.task_id} agent={lock.agent}")
            return 0
        print(f"[FAIL] Lock busy for {args.project}: task={lock.task_id} agent={lock.agent}")
        return 1

    write_lock(args.project, args.task_id, args.agent, args.git_commit_sha or "")
    print(f"[PASS] Lock acquired for {args.project}: task={args.task_id} agent={args.agent}")
    return 0


def command_release(args: argparse.Namespace) -> int:
    path = lock_path_for_project(args.project)
    lock = parse_lock(path)
    if lock is None:
        print(f"[PASS] No lock to release for {args.project}")
        return 0

    if not args.force:
        if args.task_id and lock.task_id != args.task_id:
            print(f"[FAIL] Lock task mismatch for {args.project}: expected {args.task_id}, found {lock.task_id}")
            return 1
        if args.agent and lock.agent != args.agent:
            print(f"[FAIL] Lock agent mismatch for {args.project}: expected {args.agent}, found {lock.agent}")
            return 1

    path.unlink()
    print(f"[PASS] Lock released for {args.project}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage EverAgent project locks")
    parser.add_argument("command", choices=["check", "acquire", "release"])
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--agent", help="Agent name")
    parser.add_argument("--git-commit-sha", help="Claim-time commit SHA")
    parser.add_argument("--ttl-hours", type=int, default=DEFAULT_TTL_HOURS, help="Lock expiration window")
    parser.add_argument("--force", action="store_true", help="Force release even if metadata mismatches")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.project == GLOBAL_PROJECT:
        print("[ERROR] Global tasks do not support project locks", file=sys.stderr)
        return 2

    if args.command == "check":
        return command_check(args)
    if args.command == "acquire":
        if not args.task_id or not args.agent:
            print("[ERROR] --task-id and --agent are required for acquire", file=sys.stderr)
            return 2
        return command_acquire(args)
    if args.command == "release":
        return command_release(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())
