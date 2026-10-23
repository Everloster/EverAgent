"""Generic Git submission. Repository authors and quality gates are injected."""
from __future__ import annotations

import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
from typing import Callable
from .identity.declarations import MODEL_RE

VALUE_OPTIONS = {
    "-m", "-F", "-C", "-c", "--message", "--file", "--reuse-message",
    "--reedit-message", "--author", "--date", "--cleanup", "--squash", "--trailer",
}
FLAGS = {
    "-q", "--quiet", "-v", "--verbose", "-s", "--signoff", "--no-signoff", "-S",
    "--gpg-sign", "--no-gpg-sign", "--no-verify", "--verify", "--allow-empty",
    "--allow-empty-message", "--amend", "--no-post-rewrite", "--no-edit", "-e", "--edit", "--dry-run",
    "--short", "--branch", "--porcelain", "--long", "-z", "--null", "--ahead-behind",
    "--no-ahead-behind", "--renames", "--no-renames", "--find-renames",
}


class CommitError(RuntimeError):
    def __init__(self, message: str, code: int = 2):
        super().__init__(message)
        self.code = code


def emit_error(message: str) -> None:
    encoded = message + "\n"
    buffer = getattr(sys.stderr, "buffer", None)
    if buffer is not None:
        buffer.write(encoded.encode("utf-8"))
        buffer.flush()
    else:
        sys.stderr.write(encoded)


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
            raise CommitError(f"不接受会改变待提交内容的模式、未审计选项或 pathspec {argument!r}；请先显式 git add")
        position += 1
    return result


def require_model(identity: dict) -> None:
    model = identity.get("model")
    observed = (identity.get("current_model_confirmed") is True
                and identity.get("model_confidence") == "session-bound")
    declared = (identity.get("user_model_declared") is True
                and identity.get("model_confidence") == "declared"
                and identity.get("model_source") == "user-declared"
                and isinstance(identity.get("declaration"), dict))
    if (not isinstance(model, str) or not MODEL_RE.fullmatch(model)
            or model.lower() == "unknown" or not (observed or declared)):
        raise CommitError("当前模型未核实；先运行 eacli session diagnose --json 或 "
                          "python3 scripts/agent_identity.py diagnose --json，按诊断修复自动识别并复验；"
                          "确实无法取得当前会话证据时，才请用户明确指定。已授权的源码修复和只读工作可继续", 1)


def validate_identity(identity: dict | None, *, committer: tuple[str, str],
                      author: tuple[str, str], expected_author: tuple[str, str]) -> list[str]:
    errors = []
    if not identity or identity.get("resolved") is not True:
        errors.append("current agent identity is unresolved")
    else:
        try:
            require_model(identity)
        except CommitError as exc:
            errors.append(str(exc))
        if committer != (identity.get("name"), identity.get("email")):
            errors.append("Git Committer does not match the current Agent/model")
    if not committer[0] or committer[0].endswith("-unknown") or not re.fullmatch(r"noreply@[^\s<>@]+", committer[1]):
        errors.append("Git Committer is unset or not a vendor noreply identity")
    if author != expected_author:
        errors.append("Git Author does not match the repository owner")
    return errors


def identity_environment(identity: dict, base: dict[str, str], *, author: tuple[str, str]) -> dict[str, str]:
    name, email = identity.get("name"), identity.get("email")
    if (identity.get("resolved") is not True or not isinstance(name, str)
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,160}", name)
            or name.endswith("-unknown") or not isinstance(email, str)
            or not re.fullmatch(r"noreply@[^\s<>@]+", email)):
        raise CommitError("当前 Agent 身份未识别；先运行 eacli session diagnose --json 或 "
                          "python3 scripts/agent_identity.py diagnose --json，修复诊断指向的公共 core owner 后重试；"
                          "已授权的源码修复和只读工作可继续", 1)
    require_model(identity)
    env = dict(base)
    author_name, author_email = author
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
    """Preserve the caller's message and explicit trailers; add only a final newline."""
    return message if not message or message.endswith("\n") else message + "\n"


def message_arguments(parts: list[tuple[str, str | None]], *, cwd: Path,
                      directory: Path) -> list[str]:
    messages = [value for key, value in parts if key in {"-m", "--message"}]
    files = [value for key, value in parts if key in {"-F", "--file"}]
    reused = [(key, value) for key, value in parts
              if key in {"-C", "-c", "--reuse-message", "--reedit-message"}]
    if sum(bool(group) for group in (messages, files, reused)) > 1 or len(files) > 1 or len(reused) > 1:
        raise CommitError("commit message 来源冲突")
    message = None
    if messages:
        message = "\n\n".join(messages)
    elif files:
        try:
            message = sys.stdin.read() if files[0] == "-" else (cwd / files[0]).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise CommitError("无法读取 commit message 文件") from exc
    elif reused or (any(key == "--amend" for key, _ in parts)
                    and any(key == "--no-edit" for key, _ in parts)):
        revision = reused[0][1] if reused else "HEAD"
        proc = subprocess.run(["git", "rev-parse", "--verify", "--end-of-options", revision + "^{commit}"],
                              cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False)
        if proc.returncode:
            raise CommitError("无法读取复用的 commit message")
        proc = subprocess.run(["git", "show", "-s", "--format=%B", proc.stdout.strip()],
                              cwd=cwd, capture_output=True, text=True, encoding="utf-8", check=False)
        if proc.returncode:
            raise CommitError("无法读取复用的 commit message")
        message = proc.stdout
    forwarded = []
    for key, value in parts:
        if message is not None and key in {"-m", "--message", "-F", "--file", "-C", "-c", "--reuse-message", "--reedit-message"}:
            continue
        forwarded.append(key)
        if value is not None:
            forwarded.append(value)
    if message is not None:
        path = directory / "message.txt"
        path.write_text(normalize_message(message, cwd=cwd), encoding="utf-8")
        path.chmod(0o600)
        forwarded.extend(["-F", str(path)])
    if reused:
        forwarded.append("--edit" if reused[0][0] in {"-c", "--reedit-message"} else "--no-edit")
    # Git otherwise inherits a historical Author from --amend/-C/-c.
    if any(key == "--amend" for key, _ in parts):
        forwarded.append("--reset-author")
    return forwarded


def editor_environment(env: dict[str, str], *, cwd: Path, directory: Path) -> dict[str, str]:
    """Keep the configured editor and normalize its final message before Git commits."""
    proc = subprocess.run(["git", "var", "GIT_EDITOR"], cwd=cwd, env=env,
                          capture_output=True, text=True, encoding="utf-8", check=False)
    if proc.returncode:
        # Explicit -m/-F/no-edit paths do not need an editor.
        return env
    wrapper = directory / "editor.py"
    wrapper.write_text(
        "import os, pathlib, shlex, subprocess, sys\n"
        "sys.path.insert(0, os.environ['EVERAGENT_COMMIT_CORE_PARENT'])\n"
        "from " + __package__ + ".git import normalize_message\n"
        "path = pathlib.Path(sys.argv[1])\n"
        "argument = subprocess.list2cmdline([str(path)]) if os.name == 'nt' else shlex.quote(str(path))\n"
        "code = subprocess.run(os.environ['EVERAGENT_COMMIT_EDITOR'] + ' ' + argument, shell=True).returncode\n"
        "if code: raise SystemExit(code)\n"
        "path.write_text(normalize_message(path.read_text(encoding='utf-8'), cwd=pathlib.Path.cwd()), encoding='utf-8')\n",
        encoding="utf-8")
    result = dict(env)
    parent = Path(__file__).resolve()
    for _ in __package__.split("."):
        parent = parent.parent
    result["EVERAGENT_COMMIT_CORE_PARENT"] = str(parent.parent)
    result["EVERAGENT_COMMIT_EDITOR"] = proc.stdout.strip()
    result["GIT_EDITOR"] = shlex.join([str(Path(sys.executable)).replace("\\", "/"), str(wrapper).replace("\\", "/")])
    return result


def git_value(arguments: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    proc = subprocess.run(["git", *arguments], cwd=cwd, env=env, text=True,
                          encoding="utf-8", errors="replace", capture_output=True, check=False)
    if proc.returncode:
        raise CommitError("无法读取待提交仓库或 Git index", 1)
    return proc.stdout.strip()


def signing_evidence(identity: dict) -> tuple:
    declaration = identity.get("declaration") or {}
    source = identity.get("model_source")
    if identity.get("current_model_confirmed") is True and identity.get("observation_ref"):
        source = "session-observation"
    return (*(identity.get(key) for key in ("name", "email", "cli", "model")), source,
            *(identity.get(key) for key in ("model_confidence", "current_model_confirmed", "user_model_declared")),
            declaration.get("id"), declaration.get("scope_ref"), identity.get("scope_ref"), identity.get("observation_ref"))


def commit(arguments: list[str], *, gate: Callable[[Path, dict[str, str]], int],
           identity_reader: Callable[[], dict], author_reader: Callable[[], tuple[str, str]],
           preflight: Callable[[Path, dict], None] | None = None) -> int:
    try:
        parts = option_parts(arguments)
        identity = identity_reader()
        env = identity_environment(identity, os.environ, author=author_reader())
        cwd = Path.cwd()
        target = Path(git_value(["rev-parse", "--show-toplevel"], cwd=cwd, env=env)).resolve()
        if preflight:
            preflight(target, identity)
        expected_author = f"{env['GIT_AUTHOR_NAME']} <{env['GIT_AUTHOR_EMAIL']}>"
        if any(key == "--author" and value != expected_author for key, value in parts):
            raise CommitError("--author 必须与已确认的仓库主人身份一致")
        with tempfile.TemporaryDirectory(prefix="everagent-commit-") as temporary:
            forwarded = message_arguments(parts, cwd=cwd, directory=Path(temporary))
            env = editor_environment(env, cwd=cwd, directory=Path(temporary))
            before = git_value(["write-tree"], cwd=cwd, env=env)
            result = gate(target, env)
            if result:
                return result
            if git_value(["write-tree"], cwd=cwd, env=env) != before:
                raise CommitError("quality gate 运行期间 Git index 已变化，请重新检查并重试", 3)
            fresh = identity_reader()
            fresh_env = identity_environment(fresh, os.environ, author=author_reader())
            if signing_evidence(fresh) != signing_evidence(identity):
                raise CommitError("quality gate 期间 Agent/模型身份已变化，请重新核实", 3)
            if (fresh_env["GIT_AUTHOR_NAME"], fresh_env["GIT_AUTHOR_EMAIL"]) != (env["GIT_AUTHOR_NAME"], env["GIT_AUTHOR_EMAIL"]):
                raise CommitError("quality gate 期间仓库 Author 策略已变化，请重新核实", 3)
            if preflight:
                preflight(target, fresh)
            command = ["git", "commit", *forwarded]
            code = subprocess.run(command, cwd=cwd, env=env, check=False).returncode
            if code or any(key == "--dry-run" for key, _ in parts):
                return code
            # Hooks may change an index or message after our gate. Report a failed
            # postcondition; never reset or rewrite the resulting commit silently.
            actual_tree = git_value(["rev-parse", "HEAD^{tree}"], cwd=cwd, env=env)
            actual_author = git_value(["show", "-s", "--format=%an <%ae>", "HEAD"], cwd=cwd, env=env)
            actual_committer = git_value(["show", "-s", "--format=%cn <%ce>", "HEAD"], cwd=cwd, env=env)
            if (actual_tree != before or actual_author != expected_author
                    or actual_committer != f"{identity['name']} <{identity['email']}>"):
                raise CommitError("commit 已生成，但 tree/身份后置校验失败；保留现场，先 review，禁止推送", 3)
            return 0
    except CommitError as exc:
        emit_error(f"[ecommit] BLOCKED: {exc}")
        return exc.code
    except (OSError, ValueError, AttributeError, ImportError) as exc:
        emit_error(f"[ecommit] BLOCKED: 提交 owner 或执行环境不可用（{type(exc).__name__}）")
        return 1


def push(*, cwd: Path, remote: str = "origin", branch: str = "main") -> dict:
    """Fetch, prove ancestry and push the current branch without force."""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", remote):
        raise CommitError("invalid Git remote")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]{0,160}", branch) or ".." in branch:
        raise CommitError("invalid Git branch")
    env = dict(os.environ)
    actual = git_value(["branch", "--show-current"], cwd=cwd, env=env)
    if actual != branch:
        raise CommitError("push 必须明确对应当前 checkout 的分支")
    fetched = subprocess.run(["git", "fetch", "--no-tags", remote, branch], cwd=cwd,
                             env=env, capture_output=True, text=True, encoding="utf-8", check=False)
    if fetched.returncode:
        raise CommitError("无法读取远端分支；未推送", 1)
    head = git_value(["rev-parse", "HEAD"], cwd=cwd, env=env)
    base = git_value(["rev-parse", "FETCH_HEAD"], cwd=cwd, env=env)
    proof = subprocess.run(["git", "merge-base", "--is-ancestor", base, head], cwd=cwd,
                           env=env, capture_output=True, check=False)
    if proof.returncode:
        raise CommitError("远端分支不是当前 HEAD 的祖先；检查并集成后再推送", 3)
    result = subprocess.run(["git", "push", "--porcelain", remote, f"HEAD:refs/heads/{branch}"],
                            cwd=cwd, env=env, capture_output=True, text=True, encoding="utf-8", check=False)
    if result.returncode:
        raise CommitError("Git 推送失败；先读取远端状态，禁止 force", 1)
    return {"status": "pushed", "remote": remote, "branch": branch, "head": head,
            "base": base, "fast_forward": True}
