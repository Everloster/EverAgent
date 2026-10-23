"""Read current harness model metadata without loading conversation bodies."""
from __future__ import annotations

from datetime import datetime
from contextlib import closing
import heapq
import itertools
import json
import os
from pathlib import Path
import re
import sqlite3
import stat
import time

from . import declarations, processes

MODEL_RE = declarations.MODEL_RE
MAX_TAIL_BYTES = 4 * 1024 * 1024
MAX_RECORD_BYTES = 128 * 1024
MAX_AGE_SECONDS = 300
_CODEX_ENVELOPE = re.compile(
    rb'^\s*\{\s*"timestamp"\s*:\s*"[^"\n]+"'
    rb'(?:\s*,\s*"ordinal"\s*:\s*\d+)?\s*,\s*"type"\s*:\s*"([^"]+)"\s*,\s*"payload"\s*:'
)
# ZCode appends one record per completed model request; request metadata precedes
# the conversation body, so only the prefix is ever inspected.
_ZCODE_ENVELOPE = re.compile(
    rb'^\s*\{\s*"completedAt"\s*:\s*"([^"\n]+)"\s*,\s*"durationMs"\s*:\s*\d+\s*,'
    rb'\s*"requestId"\s*:\s*"([^"\n]{1,128})"\s*,\s*"attempt"\s*:\s*\d+\s*,'
    rb'\s*"model"\s*:\s*\{\s*"modelId"\s*:\s*"([^"\n]+)"'
)
_ZCODE_STARTUP = re.compile(r"/\.zcode/cli/exec/bash-startup/([A-Za-z0-9][A-Za-z0-9._-]{0,127})/")
_SHELLS = {"bash", "zsh", "sh", "fish", "cmd.exe", "powershell.exe", "pwsh.exe", "pwsh"}
# The MiniMax Code runtime leases a conversation to the process that executes
# its turn, so the lease owner carries the pid of that process.
_MINIMAX_LEASE = re.compile(r"^turn-lease:(\d+):")


def _model(value) -> str | None:
    return value if isinstance(value, str) and MODEL_RE.fullmatch(value) and value.lower() != "unknown" else None


def _timestamp(value) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except (ValueError, OverflowError, OSError):
        return None


def _started_at(row: dict) -> float | None:
    try:
        if os.name == "nt":
            return int(row["started"]) / 10_000_000 - 11_644_473_600
        return datetime.strptime(row["started"], "%a %b %d %H:%M:%S %Y").timestamp()
    except (KeyError, TypeError, ValueError, OverflowError, OSError):
        return None


def _regular(path: Path) -> bool:
    try:
        info = path.lstat()
        return (stat.S_ISREG(info.st_mode) and not path.is_symlink()
                and (os.name == "nt" or info.st_uid == os.getuid()))
    except OSError:
        return False


def _tail(path: Path, budget: int = MAX_TAIL_BYTES) -> list[bytes]:
    if not _regular(path):
        return []
    with path.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        offset = max(0, handle.tell() - budget)
        handle.seek(offset)
        lines = handle.read(budget).splitlines()
    return lines[1:] if offset else lines


def _native_id(harness: str) -> str | None:
    keys = declarations.SESSION_KEYS.get(harness, ())
    if harness == "trae":
        specific = keys[:2]
        keys = specific if any(os.environ.get(k) for k in specific) else keys[2:]
        if keys and keys[0] == "CODEX_THREAD_ID" and any(
                processes.matches_row(row, ("codex",)) for row in processes.process_chain()):
            return None
    values = {os.environ[k] for k in keys if os.environ.get(k)}
    if len(values) != 1:
        return None
    value = values.pop()
    return value if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}", value) else None


def _codex_index(root: Path, native: str) -> dict | None:
    for db in sorted(root.glob("state*.sqlite"), reverse=True)[:4]:
        if not _regular(db):
            continue
        try:
            with closing(sqlite3.connect(db.as_uri() + "?mode=ro", uri=True, timeout=0.25)) as connection:
                deadline = time.monotonic() + 0.25
                connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
                columns = {row[1] for row in connection.execute("PRAGMA table_info(threads)")}
                if not {"id", "rollout_path"} <= columns:
                    continue
                selected = [key for key in ("rollout_path", "model", "archived", "updated_at", "updated_at_ms") if key in columns]
                row = connection.execute("SELECT " + ",".join(selected) + " FROM threads WHERE id=? LIMIT 1", (native,)).fetchone()
                if row:
                    return dict(zip(selected, row))
        except (OSError, sqlite3.Error):
            continue
    return None


def _codex(native: str, owner: dict, now: float) -> dict | None:
    home = declarations.safe_home()
    explicit = os.environ.get("CODEX_HOME")
    if not explicit and home is None:
        return None
    root = (Path(explicit) if explicit else home / ".codex").resolve()
    index = _codex_index(root, native)
    if index:
        if index.get("archived"):
            return None
        path = Path(index["rollout_path"])
    else:
        matches = list(itertools.islice((root / "sessions").glob("*/*/*/rollout-*-" + native + ".jsonl"), 2))
        if len(matches) != 1:
            return None
        path = matches[0]
    if (not path.is_absolute() or not _regular(path)
            or not path.resolve().is_relative_to(root / "sessions")
            or not 0 <= now - path.stat().st_mtime <= MAX_AGE_SECONDS):
        return None
    started = _started_at(owner)
    if started is None:
        return None
    with path.open("rb") as handle:
        header = json.loads(handle.readline(MAX_RECORD_BYTES))
    if header.get("type") != "session_meta" or header.get("payload", {}).get("id") != native:
        return None
    context, usage, active, ended = None, None, None, False
    for line in _tail(path):
        match = _CODEX_ENVELOPE.match(line[:512])
        if not match or len(line) > MAX_RECORD_BYTES:
            continue
        kind = match[1]
        if kind in (b"turn_context", b"token_usage_record"):
            row = json.loads(line)
            payload = row.get("payload", {})
            if kind == b"turn_context":
                context = {"model": _model(payload.get("model")), "turn": payload.get("turn_id"),
                           "at": _timestamp(row.get("timestamp"))}
            elif payload.get("thread_id") == native:
                usage = {"turn": payload.get("turn_id"), "at": _timestamp(row.get("timestamp"))}
        elif kind == b"event_msg":
            # Lifecycle fields precede any message body. Never decode the body.
            prefix = line[match.end():match.end() + 2048]
            event = re.match(rb'\s*\{\s*"type"\s*:\s*"([^"]+)"', prefix)
            if event and event[1] in (b"task_started", b"task_complete", b"turn_aborted", b"shutdown_complete"):
                ended = event[1] != b"task_started"
                turn = re.search(rb'"turn_id"\s*:\s*"([^"\n]+)"', prefix)
                active = turn[1].decode("ascii") if turn and not ended else None
    if ended:
        return None
    indexed = _model(index.get("model")) if index else None
    if (context and context["model"] and context["at"] is not None
            and context["at"] >= started - 2 and active and context["turn"] == active):
        if indexed and indexed != context["model"]:
            return None
        return {"model": context["model"], "source": "codex-turn-context", "turn": active}
    # The native index avoids rereading a long turn's transcript. Require a
    # fresh response from this exact thread and current process incarnation.
    updated = 0
    if index:
        updated = index["updated_at_ms"] / 1000 if "updated_at_ms" in index else index.get("updated_at", 0)
    if (indexed and usage and usage["turn"] and usage["at"] is not None
            and usage["at"] >= started - 2 and 0 <= now - usage["at"] <= MAX_AGE_SECONDS
            and updated >= started - 2 and 0 <= now - updated <= MAX_AGE_SECONDS
            and (active is None or usage["turn"] == active)
            and (context is None or context["turn"] != usage["turn"] or context["model"] == indexed)):
        return {"model": indexed, "source": "codex-thread-state", "turn": usage["turn"]}
    return None


def _pi(native: str) -> dict | None:
    # Pi clears inherited PI_* values and injects ctx.model on each shell-tool
    # spawn (resolveSpawnContext in the official Pi runtime).
    model = _model(os.environ.get("PI_MODEL"))
    if model and os.environ.get("PI_CODING_AGENT") == "true" and os.environ.get("PI_SESSION_ID") == native:
        return {"model": model, "source": "pi-session-runtime"}
    return None


def _trae(native: str, owner: dict, now: float) -> dict | None:
    home = declarations.safe_home()
    if home is None:
        return None
    logs = heapq.nlargest(4, (home / ".trae/cli/log").glob("traecli*.log"), key=lambda path: path.stat().st_mtime)
    thread = re.compile(rb'(?<![A-Za-z0-9_])thread_id=' + re.escape(native.encode()) + rb'(?![A-Za-z0-9._:-])')
    started = _started_at(owner)
    latest = None
    for path in logs:
        for line in reversed(_tail(path, 1024 * 1024)):
            if len(line) > MAX_RECORD_BYTES or not thread.search(line):
                continue
            match = re.search(rb'\bconfig_name=([^\s]+)|\bserver reported model ([^\s]+)', line)
            stamp = re.search(rb'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?', line[:256])
            at = _timestamp(stamp[0].decode()) if stamp else None
            model = _model((match[1] or match[2]).decode()) if match else None
            if match and at is not None and (latest is None or at > latest[0]):
                latest = (at, model)
    if (latest and latest[1] and started is not None and latest[0] >= started - 2
            and 0 <= now - latest[0] <= MAX_AGE_SECONDS):
        return {"model": latest[1], "source": "trae-thread-runtime"}
    return None


def _json_value_end(text: str, start: int, limit: int) -> int:
    """Skip one JSON value without materializing strings or nested bodies."""
    stack, quoted, position = [], False, start
    while position < limit:
        char = text[position]
        if quoted:
            if char == "\\":
                position += 2
                continue
            if char == '"':
                quoted = False
                if not stack:
                    return position + 1
        elif char == '"':
            quoted = True
        elif char in "{[":
            stack.append("}" if char == "{" else "]")
            if len(stack) > 32:
                raise ValueError("metadata-nesting-limit")
        elif char in "}]":
            if not stack:
                return position
            if stack.pop() != char:
                raise ValueError("metadata-invalid-delimiter")
            if not stack:
                return position + 1
        elif not stack and (char in "," or char.isspace()):
            return position
        position += 1
    if quoted or stack:
        raise ValueError("metadata-incomplete-value")
    return position


def _json_object_spans(text: str, start: int = 0, limit: int | None = None) -> dict:
    """Return top-level value spans; do not decode unselected values."""
    limit = len(text) if limit is None else limit
    position = start
    while position < limit and text[position].isspace():
        position += 1
    if position >= limit or text[position] != "{":
        raise ValueError("metadata-not-object")
    position += 1
    spans = {}
    while position < limit:
        while position < limit and text[position].isspace():
            position += 1
        if position < limit and text[position] == "}":
            if text[position + 1:limit].strip():
                raise ValueError("metadata-trailing-data")
            return spans
        if position >= limit or text[position] != '"':
            raise ValueError("metadata-invalid-key")
        key, position = json.decoder.scanstring(text, position + 1)
        if key in spans:
            raise ValueError("metadata-duplicate-key")
        while position < limit and text[position].isspace():
            position += 1
        if position >= limit or text[position] != ":":
            raise ValueError("metadata-missing-colon")
        position += 1
        while position < limit and text[position].isspace():
            position += 1
        end = _json_value_end(text, position, limit)
        if end <= position:
            raise ValueError("metadata-empty-value")
        spans[key] = (position, end)
        position = end
        while position < limit and text[position].isspace():
            position += 1
        if position < limit and text[position] == ",":
            position += 1
            if text[position:limit].lstrip().startswith("}"):
                raise ValueError("metadata-trailing-comma")
        elif position >= limit or text[position] != "}":
            raise ValueError("metadata-missing-delimiter")
    raise ValueError("metadata-incomplete-object")


def _claude_metadata(raw: bytes) -> dict:
    """Select native routing/model metadata while skipping conversation bodies."""
    text = raw.decode("utf-8")
    spans = _json_object_spans(text)
    row = {key: json.loads(text[start:end]) for key, (start, end) in spans.items()
           if key in {"type", "sessionId", "cwd", "timestamp", "uuid", "isSidechain"}}
    if row.get("type") == "assistant" and "message" in spans:
        message = _json_object_spans(text, *spans["message"])
        if "model" in message:
            start, end = message["model"]
            row["model"] = json.loads(text[start:end])
    return row


def _claude(native: str, owner: dict, now: float) -> dict | None:
    home, started = declarations.safe_home(), _started_at(owner)
    if home is None or started is None or not re.fullmatch(
            r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", native):
        return None
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude").expanduser()
    cwd = Path.cwd().resolve()
    project = re.sub(r"[^a-zA-Z0-9]", "-", str(cwd))
    path = root / "projects" / project / (native + ".jsonl")
    if (not _regular(path) or not path.resolve().is_relative_to(root.resolve())
            or not 0 <= now - path.stat().st_mtime <= MAX_AGE_SECONDS):
        return None
    for raw in reversed(_tail(path)):
        if len(raw) > MAX_RECORD_BYTES:
            return None
        try:
            row = _claude_metadata(raw)
        except (ValueError, UnicodeError):
            return None
        if row.get("type") != "assistant" or row.get("isSidechain") is True:
            continue
        # Never borrow another session, checkout, old process or older model
        # when the newest native assistant metadata is incomplete.
        at, model = _timestamp(row.get("timestamp")), _model(row.get("model"))
        if (row.get("isSidechain") is not False or row.get("sessionId") != native or row.get("cwd") != str(cwd)
                or not isinstance(row.get("uuid"), str) or not row["uuid"]
                or at is None or at < started - 2
                or not 0 <= now - at <= MAX_AGE_SECONDS or model is None):
            return None
        return {"model": model, "source": "claude-session-runtime", "turn": row["uuid"]}
    return None


def _zcode_session_token(owner: dict) -> str | None:
    """The conversation tag rides in an ancestor shell's bash-startup path.

    Hook wrappers (sh, git, ecommit) sit between the probe and the tagged
    execution shell, so every ancestor shell is probed, not just the nearest.
    """
    if os.name != "posix":
        return None
    import subprocess
    for row in processes.process_chain():
        if row is owner or row.get("pid") == owner.get("pid"):
            return None
        if row.get("name", "").casefold() in _SHELLS and isinstance(row.get("pid"), int):
            try:
                result = subprocess.run(["ps", "-o", "args=", "-p", str(row["pid"])],
                                        capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=1,
                                        env={**os.environ, "LC_ALL": "C"})
            except (OSError, ValueError, subprocess.SubprocessError):
                continue
            if result.returncode == 0:
                match = _ZCODE_STARTUP.search(result.stdout)
                if match:
                    return match.group(1)
    return None


def _zcode(native: str, owner: dict, now: float) -> dict | None:
    home = declarations.safe_home()
    if home is None:
        return None
    root = (home / ".zcode" / "cli" / "rollout").resolve()
    path = root / f"model-io-{native}.jsonl"
    if not _regular(path) or not path.resolve().is_relative_to(root):
        return None
    if not 0 <= now - path.stat().st_mtime <= MAX_AGE_SECONDS:
        return None
    started = _started_at(owner)
    if started is None:
        return None
    for raw in reversed(_tail(path)):
        match = _ZCODE_ENVELOPE.match(raw[:640])
        if not match:
            # Non-request records (tool schemas etc.) never carry request metadata.
            continue
        at = _timestamp(match[1].decode("ascii", "replace"))
        model = _model(match[3].decode("ascii", "replace"))
        # The newest completed request must belong to this CLI incarnation and stay fresh.
        if at is None or model is None or at < started - 2 or not 0 <= now - at <= MAX_AGE_SECONDS:
            return None
        return {"model": model, "source": "zcode-model-io", "turn": match[2].decode("ascii", "replace")}
    return None


def _minimax(owner: dict, now: float) -> dict | None:
    """MiniMax Code Desktop records the running conversation in its own store.

    The Desktop app exposes no conversation environment variable and its Bash
    tool spawns a plain shell, so the session is bound through the runtime's
    turn lease: the lease owner carries the pid that executes the turn, and
    that pid is an ancestor of the caller. Only runtime metadata is read; the
    conversation transcript is never opened.
    """
    home = declarations.safe_home()
    if home is None:
        return None
    root = (home / ".minimax" / "v2").resolve()
    database = root / "sqlite" / "runtime-state.sqlite"
    if not _regular(database) or not database.resolve().is_relative_to(root):
        return None
    started = _started_at(owner)
    if started is None:
        return None
    pids = {row["pid"] for row in processes.process_chain() if isinstance(row.get("pid"), int)}
    if not pids:
        return None
    now_ms = int(now * 1000)
    try:
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=0.25)) as connection:
            deadline = time.monotonic() + 0.25
            connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
            lock_columns = {row[1] for row in connection.execute(
                "PRAGMA table_info(local_runtime_session_locks)")}
            if not {"session_id", "owner_id", "owner_kind", "expires_at_ms"} <= lock_columns:
                return None
            usage_columns = {row[1] for row in connection.execute(
                "PRAGMA table_info(local_runtime_token_usage)")}
            if not {"session_id", "model", "ts", "turn_id"} <= usage_columns:
                return None
            held = []
            for session_id, owner_id, expires_at_ms in connection.execute(
                    "SELECT session_id, owner_id, expires_at_ms FROM local_runtime_session_locks"
                    " WHERE owner_kind = 'turn'"):
                match = _MINIMAX_LEASE.match(owner_id if isinstance(owner_id, str) else "")
                if not match or int(match[1]) not in pids:
                    continue
                if not isinstance(expires_at_ms, int) or expires_at_ms <= now_ms:
                    continue
                held.append(session_id)
            if len(held) != 1:
                # Two live conversations cannot be told apart from one runtime.
                return None
            session = held[0]
            usage = connection.execute(
                "SELECT model, ts, turn_id FROM local_runtime_token_usage"
                " WHERE session_id = ? ORDER BY ts DESC LIMIT 1", (session,)).fetchone()
    except (OSError, sqlite3.Error):
        return None
    if usage is None:
        return None
    model, ts, turn_id = usage
    at = ts / 1000 if isinstance(ts, (int, float)) and not isinstance(ts, bool) else None
    if at is None or at < started - 2 or not 0 <= now - at <= MAX_AGE_SECONDS:
        return None
    # The runtime records a provider-qualified id such as 'minimax/MiniMax-M3.1-Flash'.
    name = _model(model.rsplit("/", 1)[-1]) if isinstance(model, str) else None
    if name is None:
        return None
    return {"model": name, "source": "minimax-session-runtime",
            "turn": turn_id if isinstance(turn_id, str) else None, "session": session}


def collect(harness: str, scope: dict | None) -> dict | None:
    """Return only a model observation bound to the exact current caller."""
    if scope is None or harness not in {"codex", "pi", "trae", "claude-code", "zcode", "minimax-code"}:
        return None
    try:
        owner = processes.caller_process(harness)
        if owner is None or not owner.get("started"):
            return None
        from .detect import PROCESS_RULES
        names = next(names for cli, names in PROCESS_RULES if cli == harness)
        if harness == "zcode":
            # zcode-cli is per conversation; the resident zcode-host above it is
            # structural, so the nearest match must be the session CLI itself.
            if owner.get("name") != "zcode-cli" or "execution_ref" not in scope:
                return None
            native = _zcode_session_token(owner)
            if not native:
                return None
        elif harness == "minimax-code":
            # The Desktop app has no conversation environment variable; the
            # session is bound by the runtime turn lease instead of a native id.
            if "execution_ref" not in scope:
                return None
            native = None
        else:
            native = _native_id(harness)
            if not native or scope.get("session_ref") != declarations.digest([harness, native])[:24]:
                return None
            if sum(processes.matches_row(row, names) for row in processes.process_chain()) != 1:
                return None
        now = time.time()
        if harness == "minimax-code":
            found = _minimax(owner, now)
        else:
            readers = {"codex": _codex, "trae": _trae, "claude-code": _claude, "zcode": _zcode}
            found = readers[harness](native, owner, now) if harness in readers else _pi(native)
        if found:
            reference = found.get("session") or native
            return {"harness": harness, "scope": scope, "observed_at": now,
                    "model": found["model"], "source": found["source"],
                    "observation_ref": declarations.digest([harness, reference, found.get("turn"), found["model"]])[:24]}
    except (OSError, ValueError, TypeError, AttributeError, sqlite3.Error, StopIteration):
        pass
    return None
