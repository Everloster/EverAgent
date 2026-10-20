#!/usr/bin/env python3
"""Shared ecommit rules; each caller binds its own repository quality gate."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Callable

TRAILER = "Co-Authored-By: Aiden"
VALUE_OPTIONS = {
    "-m", "-F", "-C", "-c", "--message", "--file", "--reuse-message",
    "--reedit-message", "--author", "--date", "--cleanup", "--squash", "--trailer",
}
FLAGS = {
    "-q", "--quiet", "-v", "--verbose", "-s", "--signoff", "--no-signoff", "-S",
    "--gpg-sign", "--no-gpg-sign", "--no-verify", "--verify", "--allow-empty",
    "--allow-empty-message", "--amend", "--no-post-rewrite", "--no-edit", "--dry-run",
    "--short", "--branch", "--porcelain", "--long", "-z", "--null", "--ahead-behind",
    "--no-ahead-behind", "--renames", "--no-renames", "--find-renames",
}


class CommitError(RuntimeError):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def option_parts(arguments: list[str]) -> list[tuple[str, str | None]]:
    """The quality gate proves the already staged tree; accept metadata only."""
    result = []
    position = 0
    while position < len(arguments):
        argument = arguments[position]
        if argument in VALUE_OPTIONS:
            position += 1
            if position >= len(arguments):
                raise CommitError(f"{argument} 缺少参数值")
            result.append((argument, arguments[position]))
        elif any(argument.startswith(flag) and len(argument) > 2 for flag in ("-m", "-F", "-C", "-c")):
            result.append((argument[:2], argument[2:]))
        elif "=" in argument and argument.split("=", 1)[0] in VALUE_OPTIONS | {"--gpg-sign", "--find-renames"}:
            result.append(tuple(argument.split("=", 1)))
        elif argument in FLAGS:
            result.append((argument, None))
        else:
            raise CommitError(f"不接受未审计选项或 pathspec {argument!r}；请先显式 git add")
        position += 1
    return result


def owned_module(name: str):
    path = Path(__file__).resolve().with_name(name + ".py")
    spec = importlib.util.spec_from_file_location("_everagent_commit_" + name, path)
    if spec is None or spec.loader is None:
        raise CommitError("公共提交 owner 不可用", 1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def identity_environment(identity: dict, base: dict[str, str]) -> dict[str, str]:
    name, email = identity.get("name"), identity.get("email")
    if (identity.get("resolved") is not True or not isinstance(name, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,160}", name)
            or name.endswith("-unknown") or not isinstance(email, str)
            or not re.fullmatch(r"noreply@[^\s<>@]+", email)):
        raise CommitError("当前 Agent 身份未识别；请修复 whoami_agent.py owner 后重试", 1)
    env = dict(base)
    author_name, author_email = owned_module("git_identity").expected_author()
    env.update(GIT_AUTHOR_NAME=author_name, GIT_AUTHOR_EMAIL=author_email,
               GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=email)
    try:
        count = int(env.get("GIT_CONFIG_COUNT", "0"))
        if count < 0:
            raise ValueError
    except ValueError as exc:
        raise CommitError("GIT_CONFIG_COUNT 无效") from exc
    for key, value in (("user.name", name), ("user.email", email)):
        env[f"GIT_CONFIG_KEY_{count}"] = key
        env[f"GIT_CONFIG_VALUE_{count}"] = value
        count += 1
    env["GIT_CONFIG_COUNT"] = str(count)
    return env


def normalize_message(message: str, *, cwd: Path) -> str:
    """Use Git's trailer parser, retaining other authors and one Aiden entry."""
    proc = subprocess.run(
        ["git", "interpret-trailers", "--if-exists", "addIfDifferent", "--trailer", TRAILER],
        input=message, cwd=cwd, text=True, capture_output=True, check=False)
    if proc.returncode:
        raise CommitError("无法规范化 commit trailer")
    lines = proc.stdout.rstrip().splitlines()
    start = len(lines)
    while start and lines[start - 1].strip():
        start -= 1
    final = [line for line in lines[start:]
             if not re.fullmatch(r"Co-Authored-By\s*:\s*Aiden\s*", line, re.IGNORECASE)]
    return "\n".join([*lines[:start], *final, TRAILER]) + "\n"


def message_arguments(parts: list[tuple[str, str | None]], *, cwd: Path,
                      directory: Path) -> list[str]:
    messages = [value for key, value in parts if key in {"-m", "--message"}]
    files = [value for key, value in parts if key in {"-F", "--file"}]
    if (messages and files) or len(files) > 1:
        raise CommitError("commit message 来源冲突")
    message = None
    if messages:
        message = "\n\n".join(messages)
    elif files:
        try:
            message = sys.stdin.read() if files[0] == "-" else (cwd / files[0]).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise CommitError("无法读取 commit message 文件") from exc
    forwarded = []
    for key, value in parts:
        if message is not None and key in {"-m", "--message", "-F", "--file"}:
            continue
        if key == "--trailer" and re.fullmatch(
                r"(?:Co-Authored-By|aiden)\s*[:=]\s*Aiden\s*", value or "", re.IGNORECASE):
            continue
        forwarded.append(key)
        if value is not None:
            forwarded.append(value)
    if message is not None:
        path = directory / "message.txt"
        path.write_text(normalize_message(message, cwd=cwd), encoding="utf-8")
        path.chmod(0o600)
        forwarded.extend(["-F", str(path)])
    return forwarded


def git_value(arguments: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    proc = subprocess.run(["git", *arguments], cwd=cwd, env=env, text=True,
                          capture_output=True, check=False)
    if proc.returncode:
        raise CommitError("无法读取待提交仓库或 Git index", 1)
    return proc.stdout.strip()


def commit(arguments: list[str], *, gate: Callable[[Path, dict[str, str]], int],
           identity_reader: Callable[[], dict]) -> int:
    try:
        parts = option_parts(arguments)
        identity = identity_reader()
        env = identity_environment(identity, os.environ)
        cwd = Path.cwd()
        target = Path(git_value(["rev-parse", "--show-toplevel"], cwd=cwd, env=env)).resolve()
        expected_author = f"{env['GIT_AUTHOR_NAME']} <{env['GIT_AUTHOR_EMAIL']}>"
        if any(key == "--author" and value != expected_author for key, value in parts):
            raise CommitError("--author 必须与已确认的仓库主人身份一致")
        with tempfile.TemporaryDirectory(prefix="everagent-commit-") as temporary:
            forwarded = message_arguments(parts, cwd=cwd, directory=Path(temporary))
            before = git_value(["write-tree"], cwd=cwd, env=env)
            result = gate(target, env)
            if result:
                return result
            if git_value(["write-tree"], cwd=cwd, env=env) != before:
                raise CommitError("quality gate 运行期间 Git index 已变化，请重新检查并重试", 3)
            command = ["git", "-c", "trailer.aiden.key=Co-Authored-By",
                       "-c", "trailer.aiden.ifexists=addIfDifferent",
                       "-c", "trailer.co-authored-by.ifexists=addIfDifferent",
                       "commit", *forwarded, "--trailer", "aiden: Aiden"]
            return subprocess.run(command, cwd=cwd, env=env, check=False).returncode
    except CommitError as exc:
        print(f"[ecommit] BLOCKED: {exc}", file=sys.stderr)
        return exc.code
    except (OSError, ValueError, AttributeError, ImportError) as exc:
        print(f"[ecommit] BLOCKED: 提交 owner 或执行环境不可用（{type(exc).__name__}）", file=sys.stderr)
        return 1


def main() -> int:
    root = Path(__file__).resolve().parents[1]

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
