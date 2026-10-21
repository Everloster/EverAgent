#!/usr/bin/env python3
"""Validate configured git identity for agent commits.

Checks both halves of the dual identity (docs/PROTOCOL_COMMON.md §C):
- Committer = current agent (git config user.name/email, noreply required)
- Author    = repo owner Everloster (GIT_AUTHOR_* env, e.g. via scripts/ecommit.sh)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

_SCRIPT_ROOT = Path(__file__).resolve().parent
if str(_SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_ROOT))
import core_bootstrap  # noqa: E402,F401
from everagent_core.git import CommitError, require_model  # noqa: E402


# Defaults are intentionally loose:
# - Name is agent-defined per runtime (do NOT hardcode a single model name).
# - Email must be a vendor noreply address; the exact domain is resolved
#   dynamically from scripts/whoami_agent.py (the current-agent single source of
#   truth), never hardcoded here — a fixed vendor domain drifts every time the
#   active CLI/model changes (e.g. openai -> trae).
ENV_NAME_KEYS = ("EVERAGENT_GIT_NAME", "AGENT_GIT_NAME")
ENV_EMAIL_KEYS = ("EVERAGENT_GIT_EMAIL", "AGENT_GIT_EMAIL")

# Dual identity: every commit's Author must be the repo owner (PROTOCOL_COMMON §C).
_POLICY = json.loads((_SCRIPT_ROOT.parent / "config/git-policy.json").read_text(encoding="utf-8"))
EXPECTED_AUTHOR_NAME = _POLICY["author"]["name"]
EXPECTED_AUTHOR_EMAIL = _POLICY["author"]["email"]
ENV_AUTHOR_NAME_KEYS = ("EVERAGENT_GIT_AUTHOR_NAME",)
ENV_AUTHOR_EMAIL_KEYS = ("EVERAGENT_GIT_AUTHOR_EMAIL",)


def read_git_config(key: str) -> str:
    result = subprocess.run(
        ["git", "config", "--get", key],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _whoami_identity() -> dict | None:
    """Read the public owner's structured evidence once per validation."""
    script = Path(__file__).resolve().parent / "whoami_agent.py"
    if not script.exists():
        return None
    try:
        result = subprocess.run(
            [sys.executable, str(script), "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    try:
        identity = json.loads(result.stdout)
    except (ValueError, TypeError):
        return None
    if result.returncode or not isinstance(identity, dict):
        return None
    return identity


def _whoami_email() -> str | None:
    identity = _whoami_identity()
    if not identity or identity.get("resolved") is not True:
        return None
    email = identity.get("email")
    return email if isinstance(email, str) and "noreply@" in email else None


def expected_author() -> tuple[str, str]:
    return EXPECTED_AUTHOR_NAME, EXPECTED_AUTHOR_EMAIL


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
    return None


def expected_email(cli_value: str | None) -> str | None:
    if cli_value:
        return cli_value
    for key in ENV_EMAIL_KEYS:
        if os.getenv(key):
            return os.environ[key]
    return _whoami_email()


def command_show(args: argparse.Namespace) -> int:
    print(f"expected_name={expected_name(args.name) or '<dynamic>'}")
    print(f"expected_email={expected_email(args.email) or '<dynamic>'}")
    print(f"git_name={read_git_config('user.name') or '<unset>'}")
    print(f"git_email={read_git_config('user.email') or '<unset>'}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    from everagent_core.git import validate_identity
    identity = _whoami_identity()
    actual = (read_git_config("user.name"), read_git_config("user.email"))
    errors = validate_identity(identity, committer=actual, author=read_author_ident(),
                               expected_author=expected_author())
    if args.name and actual[0] != args.name:
        errors.append("explicit committer name assertion failed")
    if args.email and actual[1] != args.email:
        errors.append("explicit committer email assertion failed")
    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        print("[HINT] 核实/声明当前模型，然后使用 scripts/ecommit.sh", file=sys.stderr)
        return 1
    print(f"[PASS] Git identity OK: committer {actual[0]} <{actual[1]}>")
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

