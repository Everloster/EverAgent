"""Explicit user model declarations, bound to the caller rather than inherited env."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time

MODEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9:./_-]{0,127}")
SESSION_KEYS = {
    "codex": ("CODEX_THREAD_ID", "CODEX_SESSION_ID"),
    "pi": ("PI_SESSION_ID",),
    "trae": ("TRAECLI_THREAD_ID", "TRAE_THREAD_ID", "CODEX_THREAD_ID"),
    "claude-code": ("CLAUDE_CODE_SESSION_ID",),
    "kimi-cli": ("KIMI_CLI_SESSION_ID",),
}


def safe_home() -> Path | None:
    try:
        return Path.home()
    except (OSError, RuntimeError):
        return None


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def caller_scope(harness: str) -> dict | None:
    from . import processes
    from ..apps import DESKTOP_APPS
    anchor = processes.caller_anchor(harness)
    if anchor is None:
        return None
    native = next((os.environ[k] for k in SESSION_KEYS.get(harness, ())
                   if os.environ.get(k) and re.fullmatch(r"[A-Za-z0-9:._/-]{1,256}", os.environ[k])), None)
    # PID + creation time prevents reuse after restarts; a nested harness has its own anchor.
    scope = {"harness": harness, "process_ref": anchor}
    if native:
        scope["session_ref"] = digest([harness, native])[:24]
    terminal = os.environ.get("ORCA_TERMINAL_HANDLE") or os.environ.get("HERDR_PANE_ID")
    if terminal and re.fullmatch(r"[A-Za-z0-9:._/-]{1,256}", terminal):
        scope["terminal_ref"] = digest(terminal)[:24]
    if "session_ref" not in scope and (harness in DESKTOP_APPS or "terminal_ref" not in scope):
        # A persistent Desktop process can contain multiple conversations. With
        # no native conversation ID, limit reuse to the current execution shell.
        shells = {"bash", "zsh", "sh", "fish", "cmd.exe", "powershell.exe", "pwsh.exe", "pwsh"}
        owner = processes.caller_process(harness)
        shell = None
        for row in processes.process_chain():
            if row == owner:
                break
            if row.get("name", "").casefold() in shells and row.get("started"):
                shell = row
                break
        if shell is None:
            return None
        scope["execution_ref"] = digest([shell["pid"], shell["started"]])[:24]
    return scope


def declaration_path(scope: dict) -> Path | None:
    explicit = os.environ.get("EVERAGENT_MODEL_DECLARATION")
    if explicit:
        return Path(explicit).expanduser()
    home = safe_home()
    return home / ".local/share/everagent/session-models" / (digest(scope) + ".json") if home else None


def read_declaration(harness: str, *, hint: str, now: float | None = None) -> dict | None:
    scope = caller_scope(harness)
    path = declaration_path(scope) if scope else None
    if path is None:
        return None
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 8192:
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        current = time.time() if now is None else now
        if (not isinstance(value, dict) or value.get("schema_version") != 1
                or value.get("source") != "user" or value.get("confirmation") != "explicit"
                or value.get("scope") != scope or value.get("hint_sha256") != hint
                or not isinstance(value.get("model"), str)
                or not MODEL_RE.fullmatch(value["model"]) or value["model"].lower() == "unknown"
                or type(value.get("declared_at")) not in (int, float)
                or type(value.get("expires_at")) not in (int, float)
                or not value["declared_at"] <= current < value["expires_at"]
                or not 0 < value["expires_at"] - value["declared_at"] <= 43200):
            return None
        expected = digest({k: v for k, v in value.items() if k != "id"})
        if value.get("id") != expected:
            return None
        return value
    except (OSError, ValueError, TypeError):
        return None


def declare_model(harness: str, model: str, *, user_confirmed: bool,
                  hint: str, ttl_seconds: int = 14400) -> dict:
    """The caller must have the user's explicit instruction. This is an audit, not authentication."""
    if not user_confirmed:
        raise ValueError("需要用户明确指定当前模型；Agent 不得从配置猜测后代为确认")
    if not MODEL_RE.fullmatch(model or "") or model.lower() == "unknown":
        raise ValueError("model 必须是明确的当前模型 ID")
    if type(ttl_seconds) is not int or not 300 <= ttl_seconds <= 43200:
        raise ValueError("声明有效期必须为 300–43200 秒")
    scope = caller_scope(harness)
    if scope is None:
        raise ValueError("无法绑定当前 harness 进程；先修身份，不得借其他会话声明")
    path = declaration_path(scope)
    if path is None or path.is_symlink():
        raise ValueError("模型声明位置不可用")
    current = time.time()
    value = {"schema_version": 1, "source": "user", "confirmation": "explicit",
             "scope": scope, "model": model, "hint_sha256": hint,
             "declared_at": current, "expires_at": current + ttl_seconds}
    value["id"] = digest(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    # Atomic local receipt, never an argv credential or repository fact.
    fd, temporary = tempfile.mkstemp(prefix=".declaration-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return {"id": value["id"], "model": model, "source": "user-declared",
            "current_model_confirmed": False, "scope": scope,
            "expires_at": value["expires_at"]}
