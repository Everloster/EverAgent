#!/usr/bin/env python3
"""Validate configured git identity for agent commits."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_NAME = "Trae GPT-5.4"
DEFAULT_EMAIL = "noreply@openai.com"
ENV_NAME_KEYS = ("EVERAGENT_GIT_NAME", "AGENT_GIT_NAME")
ENV_EMAIL_KEYS = ("EVERAGENT_GIT_EMAIL", "AGENT_GIT_EMAIL")


def _read_expected_from_agents_md() -> tuple[str | None, str | None]:
    """Best-effort parse expected identity from the global AGENTS.md.

    This avoids drift between docs and pre-commit validation defaults.
    """

    agents_md = Path(__file__).resolve().parents[1] / "AGENTS.md"
    if not agents_md.exists():
        return None, None
    text = agents_md.read_text(encoding="utf-8")
    # Keep parsing intentionally lightweight (no YAML dependency).
    name = None
    email = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('name: "'):
            if "git_identity" in text[: text.find(line)]:
                name = stripped.split('"', 2)[1]
        if stripped.startswith('email: "'):
            if "git_identity" in text[: text.find(line)]:
                email = stripped.split('"', 2)[1]
        if name and email:
            break
    return name, email


def read_git_config(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def expected_name(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    for key in ENV_NAME_KEYS:
        if os.getenv(key):
            return os.environ[key]
    name, _ = _read_expected_from_agents_md()
    if name:
        return name
    return DEFAULT_NAME


def expected_email(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    for key in ENV_EMAIL_KEYS:
        if os.getenv(key):
            return os.environ[key]
    _, email = _read_expected_from_agents_md()
    if email:
        return email
    return DEFAULT_EMAIL


def command_show(args: argparse.Namespace) -> int:
    print(f"expected_name={expected_name(args.name)}")
    print(f"expected_email={expected_email(args.email)}")
    print(f"git_name={read_git_config('user.name') or '<unset>'}")
    print(f"git_email={read_git_config('user.email') or '<unset>'}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    exp_name = expected_name(args.name)
    exp_email = expected_email(args.email)
    act_name = read_git_config("user.name")
    act_email = read_git_config("user.email")

    errors: list[str] = []
    if not act_name:
        errors.append("git user.name is unset")
    elif act_name != exp_name:
        errors.append(f"git user.name mismatch: expected '{exp_name}', got '{act_name}'")

    if not act_email:
        errors.append("git user.email is unset")
    else:
        if act_email != exp_email:
            errors.append(f"git user.email mismatch: expected '{exp_email}', got '{act_email}'")
        if "noreply@" not in act_email:
            errors.append(f"git user.email must be a noreply address, got '{act_email}'")

    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        print(
            f"[HINT] Configure git with: git config user.name \"{exp_name}\" && git config user.email \"{exp_email}\"",
            file=sys.stderr,
        )
        return 1

    print(f"[PASS] Git identity matches {exp_name} <{exp_email}>")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate agent git identity")
    parser.add_argument("command", choices=["show", "validate"])
    parser.add_argument("--name", help="Expected git user.name override")
    parser.add_argument("--email", help="Expected git user.email override")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "show":
        return command_show(args)
    return command_validate(args)


if __name__ == "__main__":
    sys.exit(main())
