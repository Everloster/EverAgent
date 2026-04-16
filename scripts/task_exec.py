#!/usr/bin/env python3
"""Thin wrapper for common task execution flows."""

from __future__ import annotations

import argparse
import subprocess
import sys

from task_state import find_task


def run_step(command: list[str]) -> None:
    print(f"[RUN] {' '.join(command)}")
    subprocess.run(command, check=True)


def require_task(task_id: str):
    task = find_task(task_id)
    if task is None:
        raise KeyError(f"Task {task_id} not found")
    return task


def command_begin(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    if task.project != args.project:
        raise ValueError(f"Task {task.id} belongs to {task.project}, not {args.project}")

    run_step(
        [
            "python3",
            "scripts/execution_validator.py",
            "--mode=input",
            "--task-id",
            args.task_id,
            "--project",
            args.project,
        ]
    )
    if args.project != "global":
        run_step(
            [
                "python3",
                "scripts/project_lock.py",
                "acquire",
                "--project",
                args.project,
                "--task-id",
                args.task_id,
                "--agent",
                args.agent,
            ]
        )
    run_step(
        [
            "python3",
            "scripts/task_state_cli.py",
            "claim",
            "--task-id",
            args.task_id,
            "--agent",
            args.agent,
        ]
    )
    print("[PASS] Begin flow completed. Commit/push the claim, then run task_exec.py start.")
    return 0


def command_start(args: argparse.Namespace) -> int:
    require_task(args.task_id)
    run_step(["python3", "scripts/task_state_cli.py", "start", "--task-id", args.task_id])
    print("[PASS] Task is now in_progress.")
    return 0


def command_finish(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    project = args.project or task.project
    if project != task.project:
        raise ValueError(f"Task {task.id} belongs to {task.project}, not {project}")

    run_step(
        [
            "python3",
            "scripts/execution_validator.py",
            "--mode=output",
            "--task-id",
            args.task_id,
            "--project",
            project,
        ]
    )
    run_step(["python3", "scripts/task_state_cli.py", "done", "--task-id", args.task_id])
    print("[PASS] Finish flow completed. Commit/push the done status, then release the lock.")
    return 0


def command_fail(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    project = args.project or task.project
    if project != task.project:
        raise ValueError(f"Task {task.id} belongs to {task.project}, not {project}")

    run_step(
        [
            "python3",
            "scripts/task_state_cli.py",
            "fail",
            "--task-id",
            args.task_id,
            "--reason",
            args.reason,
        ]
    )
    print("[PASS] Failure status recorded. Commit/push the failed state, then release the lock.")
    return 0


def command_release(args: argparse.Namespace) -> int:
    task = require_task(args.task_id)
    project = args.project or task.project
    if project != task.project:
        raise ValueError(f"Task {task.id} belongs to {task.project}, not {project}")
    if project == "global":
        print("[PASS] Global tasks do not use project locks.")
        return 0

    run_step(
        [
            "python3",
            "scripts/project_lock.py",
            "release",
            "--project",
            project,
            "--task-id",
            args.task_id,
            "--agent",
            args.agent,
        ]
    )
    print("[PASS] Lock released.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Thin wrapper for task execution flows")
    subparsers = parser.add_subparsers(dest="command", required=True)

    begin_parser = subparsers.add_parser("begin")
    begin_parser.add_argument("--task-id", required=True)
    begin_parser.add_argument("--project", required=True)
    begin_parser.add_argument("--agent", required=True)
    begin_parser.set_defaults(func=command_begin)

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("--task-id", required=True)
    start_parser.set_defaults(func=command_start)

    finish_parser = subparsers.add_parser("finish")
    finish_parser.add_argument("--task-id", required=True)
    finish_parser.add_argument("--project")
    finish_parser.set_defaults(func=command_finish)

    fail_parser = subparsers.add_parser("fail")
    fail_parser.add_argument("--task-id", required=True)
    fail_parser.add_argument("--project")
    fail_parser.add_argument("--reason", required=True)
    fail_parser.set_defaults(func=command_fail)

    release_parser = subparsers.add_parser("release")
    release_parser.add_argument("--task-id", required=True)
    release_parser.add_argument("--project")
    release_parser.add_argument("--agent", required=True)
    release_parser.set_defaults(func=command_release)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except (KeyError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
