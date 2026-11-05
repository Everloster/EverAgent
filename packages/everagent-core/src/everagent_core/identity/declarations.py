"""Explicit user facts, scoped to the caller; legacy model receipts remain readable."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import time
from . import config

MODEL_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9:./_-]{0,127}")
SESSION_KEYS = {key: tuple(value.get("session_keys", ()))
                for key, value in config.load(override=False).items()}


def session_keys(harness: str):
    return tuple(config.rule(harness).get("session_keys", ()))


def safe_home() -> Path | None:
    try:
        return Path.home()
    except (OSError, RuntimeError):
        return None


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def caller_scope(harness: str) -> dict | None:
    from . import processes
    anchor = processes.caller_anchor(harness)
    if anchor is None:
        return None
    native = next((os.environ[k] for k in session_keys(harness)
                   if os.environ.get(k) and re.fullmatch(r"[A-Za-z0-9:._/-]{1,256}", os.environ[k])), None)
    # PID + creation time prevents reuse after restarts; a nested harness has its own anchor.
    scope = {"harness": harness, "process_ref": anchor}
    if native:
        scope["session_ref"] = digest([harness, native])[:24]
    terminal = os.environ.get("ORCA_TERMINAL_HANDLE") or os.environ.get("HERDR_PANE_ID")
    if terminal and re.fullmatch(r"[A-Za-z0-9:._/-]{1,256}", terminal):
        scope["terminal_ref"] = digest(terminal)[:24]
    if "session_ref" not in scope and (config.rule(harness).get("form") in {"desktop", "web"}
                                      or "terminal_ref" not in scope):
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


def read_declaration(harness: str, *, hint: str, now: float | None = None,
                     include_expired: bool = False) -> dict | None:
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
                or value["declared_at"] > current
                or (not include_expired and current >= value["expires_at"])
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


def fact_scope(*, expected_harness: str | None = None) -> dict | None:
    """Bind fallback facts even when no known harness can be identified.

    An unknown caller is limited to its exact execution shell. A terminal env
    value alone never extends that lifetime to other conversations.
    """
    import platform
    from . import models, processes
    from .detect import _detect_cli
    try:
        harness, _ = _detect_cli()
        if expected_harness and harness and harness != expected_harness:
            return None
        scope = caller_scope(harness) if harness else None
        if scope is None:
            shells = {"bash", "zsh", "sh", "fish", "cmd.exe", "powershell.exe", "pwsh.exe", "pwsh"}
            shell = next((row for row in processes.process_chain()
                          if row.get("name", "").casefold() in shells and row.get("started")), None)
            if shell is None:
                return None
            scope = {"execution_ref": digest([shell["pid"], shell["started"]])[:24]}
        return {**scope, "automatic_harness": harness,
                "machine_ref": digest([platform.system(), platform.node()])[:24],
                "hint_sha256": models.hint_fingerprint(harness or "")}
    except (OSError, ValueError, TypeError):
        return None


def facts_path(scope: dict) -> Path | None:
    explicit = os.environ.get("EVERAGENT_SESSION_DECLARATION")
    if explicit:
        return Path(explicit).expanduser()
    home = safe_home()
    # One local declaration mechanism, not a second identity registry.
    return home / ".local/share/everagent/session-models" / ("facts-" + digest(scope) + ".json") if home else None


def _valid_facts(fields) -> bool:
    return (isinstance(fields, dict) and bool(fields) and not set(fields) - {"device", "harness", "form", "model"}
            and all(isinstance(v, str) and MODEL_RE.fullmatch(v) and v.lower() != "unknown" for v in fields.values())
            and ("harness" not in fields or re.fullmatch(r"[a-z][a-z0-9-]{0,63}", fields["harness"]))
            and ("form" not in fields or fields["form"] in {"cli", "desktop", "web"}))


def read_facts(*, harness: str | None = None, now: float | None = None,
               include_expired: bool = False) -> dict | None:
    scope = fact_scope(expected_harness=harness)
    path = facts_path(scope) if scope else None
    if path is None:
        return None
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 8192:
            return None
        if os.name != "nt" and (path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077):
            return None
        value = json.loads(path.read_text(encoding="utf-8"))
        current = time.time() if now is None else now
        if (not isinstance(value, dict) or value.get("schema_version") != 2 or value.get("scope") != scope
                or value.get("source") != "user" or value.get("confirmation") != "explicit"
                or not _valid_facts(value.get("fields"))
                or type(value.get("declared_at")) not in (int, float)
                or type(value.get("expires_at")) not in (int, float)
                or value["declared_at"] > current
                or (not include_expired and current >= value["expires_at"])
                or not 300 <= value["expires_at"] - value["declared_at"] <= 43200
                or value.get("id") != digest({k: v for k, v in value.items() if k != "id"})):
            return None
        times = value.get("field_times")
        if not isinstance(times, dict) or set(times) != set(value["fields"]):
            return None
        for timing in times.values():
            if (not isinstance(timing, dict) or set(timing) != {"declared_at", "expires_at"}
                    or any(type(timing[k]) not in (int, float) for k in timing)
                    or not 300 <= timing["expires_at"] - timing["declared_at"] <= 43200
                    or not timing["declared_at"] <= value["declared_at"] <= current
                    or timing["expires_at"] > value["expires_at"]):
                return None
        discarded_at = value.get("model_discarded_at", 0)
        if type(discarded_at) not in (int, float) or not 0 <= discarded_at <= value["declared_at"]:
            return None
        # When only the user can identify a harness, still bind its particular
        # model hint. The automatic scope stays unknown; it is never forged.
        declared_harness = value["fields"].get("harness")
        if not scope.get("automatic_harness") and declared_harness:
            from .models import hint_fingerprint
            if value.get("harness_hint_sha256") != hint_fingerprint(declared_harness):
                return None
        fields = {k: v for k, v in value["fields"].items()
                  if include_expired or current < times[k]["expires_at"]}
        return {**value, "fields": fields, "field_times": {k: times[k] for k in fields}} if fields else None
    except (OSError, ValueError, TypeError):
        return None


def declare_facts(fields: dict, *, user_confirmed: bool, ttl_seconds: int = 14400,
                  observed: dict | None = None) -> dict:
    """Record explicit user facts; automatic facts take precedence and cannot be overwritten."""
    if not user_confirmed:
        raise ValueError("需要用户明确指定缺失事实；不得从配置猜测后代为确认")
    if not _valid_facts(fields):
        raise ValueError("只接受明确的 device/harness/form/model；form 为 cli/desktop/web")
    if type(ttl_seconds) is not int or not 300 <= ttl_seconds <= 43200:
        raise ValueError("声明有效期必须为 300–43200 秒")
    if observed and any(observed.get(k) not in (None, "unknown", v) for k, v in fields.items()):
        raise ValueError("声明与当前自动证据冲突；先诊断读取路径，不覆盖自动证据")
    scope = fact_scope()
    path = facts_path(scope) if scope else None
    if path is None or path.is_symlink():
        raise ValueError("无法绑定当前执行上下文；不得借其他会话声明")
    current = time.time()
    # Keep expired entries as supersession evidence, not as usable facts. An
    # unrelated update must not erase a newer expired model and revive legacy.
    previous = read_facts(include_expired=True)
    retained = {k: v for k, v in (previous["fields"] if previous else {}).items()
                if k not in fields and (not observed or observed.get(k) in (None, "unknown", v))}
    if fields.get("harness") and previous and fields["harness"] != previous["fields"].get("harness"):
        # A model/form stated for the previous harness cannot follow its replacement.
        retained.pop("model", None)
        retained.pop("form", None)
    discarded_at = previous.get("model_discarded_at", 0) if previous else 0
    if previous and "model" in previous["fields"] and "model" not in retained and "model" not in fields:
        # Discarding a contradicted fact must also suppress older legacy model
        # receipts. This is a revocation boundary, never a renewed model fact.
        discarded_at = current
    times = {k: previous["field_times"][k] for k in retained}
    times.update({k: {"declared_at": current, "expires_at": current + ttl_seconds} for k in fields})
    fields = {**retained, **fields}
    value = {"schema_version": 2, "source": "user", "confirmation": "explicit", "scope": scope,
             "fields": fields, "field_times": times, "declared_at": current,
             "expires_at": max(t["expires_at"] for t in times.values())}
    if discarded_at:
        value["model_discarded_at"] = discarded_at
    if not scope.get("automatic_harness") and fields.get("harness"):
        from .models import hint_fingerprint
        value["harness_hint_sha256"] = hint_fingerprint(fields["harness"])
    value["id"] = digest(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".declaration-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    active = {k: v for k, v in fields.items() if current < times[k]["expires_at"]}
    return {"id": value["id"], "fields": active, "field_times": {k: times[k] for k in active}, "source": "user-declared", "scope": scope,
            "expires_at": value["expires_at"], "automatically_verified": False,
            "grants_permissions": False}
