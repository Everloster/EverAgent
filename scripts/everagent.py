#!/usr/bin/env python3
"""One-stop CLI entry for common EverAgent maintenance operations.

This script intentionally avoids third-party dependencies.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(cmd: list[str]) -> int:
    print(f"[RUN] {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        return exc.returncode
    return 0


def command_doctor(_: argparse.Namespace) -> int:
    steps = [
        ["python3", "scripts/validate_workspace.py"],
        ["python3", "scripts/execution_validator.py", "--mode=self-check"],
        ["python3", "scripts/task_board_aggregator.py", "--dry-run"],
    ]
    for step in steps:
        code = run_step(step)
        if code != 0:
            print(f"[FAIL] Step failed: {' '.join(step)}", file=sys.stderr)
            return code
    print("[PASS] Doctor checks passed.")
    return 0


def command_sync(args: argparse.Namespace) -> int:
    cmd = ["python3", "scripts/task_board_aggregator.py"]
    if args.sync_readme:
        cmd.append("--sync-readme")
    return run_step(cmd)


def _install_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    # Ensure executable.
    mode = os.stat(dst).st_mode
    os.chmod(dst, mode | 0o111)


def command_hooks_install(_: argparse.Namespace) -> int:
    git_dir = ROOT / ".git"
    if not git_dir.exists():
        print("[FAIL] .git directory not found; are you in a git checkout?", file=sys.stderr)
        return 2

    src = ROOT / "scripts" / "hooks" / "pre-commit"
    if not src.exists():
        print(f"[FAIL] Hook template not found: {src}", file=sys.stderr)
        return 2

    dst = git_dir / "hooks" / "pre-commit"
    _install_file(src, dst)
    print(f"[PASS] Installed pre-commit hook to {dst}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="EverAgent maintenance CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    doctor = sub.add_parser("doctor", help="Run workspace self-checks")
    doctor.set_defaults(func=command_doctor)

    sync = sub.add_parser("sync", help="Regenerate Task Board view (and optionally README overview)")
    sync.add_argument("--sync-readme", action="store_true", help="Also refresh root README overview table")
    sync.set_defaults(func=command_sync)

    hooks = sub.add_parser("hooks", help="Manage local git hooks")
    hooks_sub = hooks.add_subparsers(dest="hooks_command", required=True)
    hooks_install = hooks_sub.add_parser("install", help="Install repo pre-commit hook into .git/hooks")
    hooks_install.set_defaults(func=command_hooks_install)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

