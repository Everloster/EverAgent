#!/usr/bin/env python3
"""Bind EverAgent repository policy and quality to the reusable core Git primitives."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import core_bootstrap  # noqa: E402,F401
from everagent_core import git as _core  # noqa: E402

CommitError = _core.CommitError
TRAILER = _core.TRAILER
option_parts = _core.option_parts
normalize_message = _core.normalize_message
message_arguments = _core.message_arguments
git_value = _core.git_value


def owned_module(name: str):
    if name not in {"whoami_agent", "git_identity"}:
        raise CommitError("unsupported public repository policy", 1)
    path = _SCRIPTS / (name + ".py")
    spec = importlib.util.spec_from_file_location("_everagent_commit_" + name, path)
    if spec is None or spec.loader is None:
        raise CommitError("public repository policy is unavailable", 1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity_environment(identity: dict, base: dict[str, str]) -> dict[str, str]:
    return _core.identity_environment(identity, base, author=owned_module("git_identity").expected_author())


def commit(arguments, *, gate, identity_reader) -> int:
    return _core.commit(arguments, gate=gate, identity_reader=identity_reader,
                        author_reader=owned_module("git_identity").expected_author)


def main() -> int:
    root = _SCRIPTS.parent
    def gate(target: Path, env: dict[str, str]) -> int:
        if target != root:
            raise CommitError("公开仓提交入口必须在其所属 checkout 内执行", 1)
        proc = subprocess.run([sys.executable, str(root / "scripts/precommit_quality.py")],
                              cwd=root, env=env, check=False)
        if proc.returncode == 0:
            env["EVERAGENT_QUALITY_GATE_DONE"] = "1"
        return proc.returncode
    return commit(sys.argv[1:], gate=gate,
                  identity_reader=lambda: owned_module("whoami_agent").inspect_identity())


if __name__ == "__main__":
    raise SystemExit(main())
