#!/usr/bin/env python3
"""Validate configured git identity for agent commits.

Checks both halves of the dual identity (docs/PROTOCOL_COMMON.md §C):
- Committer = current agent (git config user.name/email, noreply required)
- Author    = repo owner Everloster (GIT_AUTHOR_* env, e.g. via scripts/ecommit.sh)
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path


# Defaults are intentionally loose:
# - Name is agent-defined per runtime (do NOT hardcode a single model name).
# - Email must be a vendor noreply address; exact domain can be overridden by env/CLI.
DEFAULT_EMAIL = "noreply@openai.com"
ENV_NAME_KEYS = ("EVERAGENT_GIT_NAME", "AGENT_GIT_NAME")
ENV_EMAIL_KEYS = ("EVERAGENT_GIT_EMAIL", "AGENT_GIT_EMAIL")

# Dual identity: every commit's Author must be the repo owner (PROTOCOL_COMMON §C).
EXPECTED_AUTHOR_NAME = "Everloster"
EXPECTED_AUTHOR_EMAIL = "2820419+Everloster@users.noreply.github.com"
ENV_AUTHOR_NAME_KEYS = ("EVERAGENT_GIT_AUTHOR_NAME",)
ENV_AUTHOR_EMAIL_KEYS = ("EVERAGENT_GIT_AUTHOR_EMAIL",)


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
    # Treat placeholders like "<CURRENT_AGENT_NAME>" as "unspecified".
    if name and name.startswith("<") and name.endswith(">"):
        name = None
    if email and email.startswith("<") and email.endswith(">"):
        email = None
    return name, email


def read_git_config(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def expected_author() -> tuple[str, str]:
    name, email = EXPECTED_AUTHOR_NAME, EXPECTED_AUTHOR_EMAIL
    for key in ENV_AUTHOR_NAME_KEYS:
        if os.getenv(key):
            name = os.environ[key]
    for key in ENV_AUTHOR_EMAIL_KEYS:
        if os.getenv(key):
            email = os.environ[key]
    return name, email


def read_author_ident() -> tuple[str, str]:
    """Author of the would-be commit (honors GIT_AUTHOR_* env vars)."""
    result = subprocess.run(
        ["git", "var", "GIT_AUTHOR_IDENT"],
        check=False,
        capture_output=True,
        text=True,
    )
    m = re.match(r"^(.*?) <(.*?)>", result.stdout.strip())
    if not m:
        return "", ""
    return m.group(1), m.group(2)


def expected_name(cli_value: str | None) -> str | None:
    if cli_value:
        return cli_value
    for key in ENV_NAME_KEYS:
        if os.getenv(key):
            return os.environ[key]
    name, _ = _read_expected_from_agents_md()
    if name:
        return name
    return None


def expected_email(cli_value: str | None) -> str | None:
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
    print(f"expected_name={expected_name(args.name) or '<dynamic>'}")
    print(f"expected_email={expected_email(args.email) or '<dynamic>'}")
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
    elif act_name.endswith("-unknown"):
        errors.append(
            f"committer identity unresolved: '{act_name}' — fix scripts/whoami_agent.py to cover this CLI, "
            "or set AGENT_ID/AGENT_EMAIL explicitly after confirming with the user"
        )
    elif exp_name and act_name != exp_name:
        errors.append(f"git user.name mismatch: expected '{exp_name}', got '{act_name}'")

    if not act_email:
        errors.append("git user.email is unset")
    else:
        if "noreply@" not in act_email:
            errors.append(f"git user.email must be a noreply address, got '{act_email}'")
        elif exp_email and act_email != exp_email:
            print(f"[WARN] git user.email differs from expected '{exp_email}': got '{act_email}'", file=sys.stderr)

    exp_author = expected_author()
    author = read_author_ident()
    if author != exp_author:
        errors.append(
            f"dual-identity violated: commit Author must be repo owner "
            f"'{exp_author[0]} <{exp_author[1]}>', got '{author[0]} <{author[1]}>'"
        )

    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        hint_name = exp_name or "<agent-defined name>"
        hint_email = exp_email or "<vendor noreply email>"
        print(f"[HINT] Configure git with: git config user.name \"{hint_name}\" && git config user.email \"{hint_email}\"", file=sys.stderr)
        print("[HINT] Commit via scripts/ecommit.sh (auto-sets Author=Everloster), see docs/PROTOCOL_COMMON.md §C", file=sys.stderr)
        return 1

    print(f"[PASS] Git identity OK: committer {act_name} <{act_email}>, author {author[0]} <{author[1]}>")
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
