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
CLAUDE_READ_ATTEMPTS = 3
CLAUDE_READ_SETTLE_SECONDS = 0.02
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
AUTOMATIC_READERS = {
    "codex": ("codex-turn-context", "codex-thread-state"),
    "pi": ("pi-session-runtime",), "trae": ("trae-thread-runtime",),
    "claude-code": ("claude-session-runtime",), "zcode": ("zcode-model-io",),
    "minimax-code": ("minimax-session-runtime",),
    "kimi-desktop": ("kimi-desktop-session-runtime",),
}


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
        if position >= limit:
            raise ValueError("metadata-incomplete-key")
        if text[position] != '"':
            raise ValueError("metadata-invalid-key")
        try:
            key, position = json.decoder.scanstring(text, position + 1)
        except json.JSONDecodeError as exc:
            if exc.msg.startswith("Unterminated string"):
                raise ValueError("metadata-incomplete-key") from exc
            raise
        if key in spans:
            raise ValueError("metadata-duplicate-key")
        while position < limit and text[position].isspace():
            position += 1
        if position >= limit:
            raise ValueError("metadata-incomplete-colon")
        if text[position] != ":":
            raise ValueError("metadata-missing-colon")
        position += 1
        while position < limit and text[position].isspace():
            position += 1
        end = _json_value_end(text, position, limit)
        if end <= position and end == limit:
            raise ValueError("metadata-incomplete-value")
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
        elif position >= limit:
            raise ValueError("metadata-incomplete-delimiter")
        elif text[position] != "}":
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


def _claude_tail(path: Path) -> tuple[list[bytes], bool, bool]:
    """Read one bounded snapshot, retaining EOF and concurrent-write evidence."""
    with path.open("rb") as handle:
        before = os.fstat(handle.fileno())
        offset = max(0, before.st_size - MAX_TAIL_BYTES)
        handle.seek(offset)
        data = handle.read(MAX_TAIL_BYTES)
        after = os.fstat(handle.fileno())
    lines = data.splitlines()
    stable = (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
    return (lines[1:] if offset else lines), data.endswith(b"\n"), stable


def _claude(native: str, owner: dict, now: float, *, diagnostics: dict | None = None) -> dict | None:
    def unavailable(reason):
        if diagnostics is not None:
            diagnostics["reason_code"] = reason
        return None

    home, started = declarations.safe_home(), _started_at(owner)
    if home is None or started is None or not re.fullmatch(
            r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", native):
        return unavailable("native-session-binding-unavailable")
    root = Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude").expanduser()
    cwd = Path.cwd().resolve()
    project = re.sub(r"[^a-zA-Z0-9]", "-", str(cwd))
    path = root / "projects" / project / (native + ".jsonl")
    # A tool shell may cd into another checkout while Claude keeps its session
    # in the harness process's project. Resolve only that exact current ancestor;
    # never scan projects or replace an existing invalid/stale session candidate.
    if not path.exists() and not path.is_symlink():
        harness_cwd = processes.current_directory(owner)
        if harness_cwd is not None and harness_cwd != cwd:
            cwd = harness_cwd
            project = re.sub(r"[^a-zA-Z0-9]", "-", str(cwd))
            path = root / "projects" / project / (native + ".jsonl")
    for attempt in range(CLAUDE_READ_ATTEMPTS):
        if diagnostics is not None:
            diagnostics["retry_count"] = attempt
        if not _regular(path) or not path.resolve().is_relative_to(root.resolve()):
            return unavailable("native-session-file-unavailable")
        age = now - path.stat().st_mtime
        if age > MAX_AGE_SECONDS:
            return unavailable("native-session-file-stale")
        transient = age < 0
        if not transient:
            lines, terminated, stable = _claude_tail(path)
            transient = not stable
            if stable:
                for index, raw in enumerate(reversed(lines)):
                    if len(raw) > MAX_RECORD_BYTES:
                        return unavailable("native-record-oversized")
                    try:
                        row = _claude_metadata(raw)
                    except (ValueError, UnicodeError) as exc:
                        # Retry only an unfinished final JSON object. Complete
                        # malformed records still fail; never skip to an older model.
                        incomplete = str(exc).startswith("metadata-incomplete") or (
                            isinstance(exc, UnicodeDecodeError) and exc.reason == "unexpected end of data")
                        if index == 0 and not terminated and incomplete:
                            transient = True
                            break
                        return unavailable("native-metadata-invalid")
                    if row.get("type") != "assistant" or row.get("isSidechain") is True:
                        continue
                    at, model = _timestamp(row.get("timestamp")), _model(row.get("model"))
                    if (row.get("isSidechain") is not False or row.get("sessionId") != native
                            or row.get("cwd") != str(cwd) or not isinstance(row.get("uuid"), str)
                            or not row["uuid"] or at is None or at < started - 2 or model is None):
                        return unavailable("native-assistant-binding-invalid")
                    if now - at > MAX_AGE_SECONDS:
                        return unavailable("native-assistant-stale")
                    if at > now:
                        transient = True
                        break
                    return {"model": model, "source": "claude-session-runtime", "turn": row["uuid"],
                            "observed_at": now}
                if not transient:
                    return unavailable("native-current-assistant-unavailable")
        if attempt + 1 < CLAUDE_READ_ATTEMPTS:
            time.sleep(CLAUDE_READ_SETTLE_SECONDS)
            now = time.time()
    return unavailable("native-observation-in-progress")


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


_KIMI_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,255}")
_KIMI_ENVELOPE = re.compile(rb'^\s*\{\s*"type"\s*:\s*"(usage\.record|llm\.request)"')
_KIMI_STATE_MAX_BYTES = 1024 * 1024
_KIMI_ACTIVE_TURN_LIMIT = 16
# The packaged Node runtime keeps the control token in its own process. Python
# supplies only public candidate metadata on stdin; no token enters argv/output.
_KIMI_TASK_QUERY = r"""
const fs = require('node:fs');
const fail = () => process.exit(1);
let state, candidates;
try {
  if (fs.statSync(process.argv[1]).size > 1048576) fail();
  state = JSON.parse(fs.readFileSync(process.argv[1], 'utf8'));
  candidates = JSON.parse(fs.readFileSync(0, 'utf8'));
} catch (_) { fail(); }
if (!Array.isArray(candidates) || candidates.length < 1 || candidates.length > 16) fail();
const endpoint = state?.control?.endpoint;
const url = endpoint?.url;
const token = endpoint?.auth?.token;
if (typeof url !== 'string' || typeof token !== 'string' || !token) fail();
function query(candidate, index) {
  return new Promise((resolve, reject) => {
    const id = 'everagent-identity-' + index;
    const socket = new WebSocket(url, { headers: { Authorization: 'Bearer ' + token } });
    let done = false;
    const finish = (callback, value) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      socket.close();
      callback(value);
    };
    const timer = setTimeout(() => finish(reject, new Error('timeout')), 2000);
    socket.addEventListener('open', () => {
      try {
        socket.send(JSON.stringify({ jsonrpc: '2.0', id, method: 'backgroundTasks.list',
          params: { agentId: candidate.agentId, kernelSessionId: candidate.kernelSessionId,
            activeOnly: true, limit: 100 } }));
      } catch (error) { finish(reject, error); }
    });
    socket.addEventListener('message', (event) => {
      let frame;
      try { frame = JSON.parse(String(event.data)); } catch (error) { finish(reject, error); return; }
      if (frame.id !== id) return;
      if (frame.error) { finish(reject, new Error('control query failed')); return; }
      const result = frame.result ?? {};
      if (result.kernelSessionId !== candidate.kernelSessionId || !Array.isArray(result.tasks)
          || result.tasks.length > 100) {
        finish(reject, new Error('invalid control response'));
        return;
      }
      finish(resolve, { kernelSessionId: result.kernelSessionId, tasks: result.tasks.map((task) => ({
        kind: task?.kind, status: task?.status, pid: task?.pid, startedAtMs: task?.startedAtMs,
      })) });
    });
    socket.addEventListener('error', () => finish(reject, new Error('control connection failed')));
  });
}
Promise.all(candidates.map(query)).then(
  (rows) => process.stdout.write(JSON.stringify(rows)),
  () => process.exit(1),
);
"""


def _kimi_root() -> Path | None:
    explicit = os.environ.get("KIMI_SHARE_DIR")
    home = declarations.safe_home()
    if explicit:
        root = Path(explicit).expanduser()
    elif home is not None and os.name == "nt":
        root = Path(os.environ.get("APPDATA") or home / "AppData/Roaming") / "kimi-desktop/daimon-share"
    elif home is not None:
        root = home / "Library/Application Support/kimi-desktop/daimon-share"
    else:
        return None
    return root.resolve() if root.is_absolute() else None


def _kimi_active_turns(state_path: Path, pids: set[int]) -> list[dict] | None:
    """Read bounded runtime state without exposing its control credential."""
    from urllib.parse import urlsplit
    if not _regular(state_path) or state_path.stat().st_size > _KIMI_STATE_MAX_BYTES:
        return None
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("schemaVersion") != 1 or state.get("lifecycleStatus") != "running":
        return None
    endpoint = state.get("control", {}).get("endpoint", {})
    daemon = state.get("daemonGeneration", {})
    pid = endpoint.get("pid")
    parsed = urlsplit(endpoint.get("url") if isinstance(endpoint.get("url"), str) else "")
    if (parsed.scheme != "ws" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username is not None or parsed.password is not None
            or not isinstance(parsed.port, int) or not 1 <= parsed.port <= 65535
            or type(pid) is not int or pid <= 1 or pid not in pids or daemon.get("pid") != pid
            or not isinstance(endpoint.get("auth", {}).get("token"), str)
            or not endpoint.get("auth", {}).get("token")):
        return None
    turns = state.get("activeKernelTurns")
    if not isinstance(turns, list) or not 1 <= len(turns) <= _KIMI_ACTIVE_TURN_LIMIT:
        return None
    candidates, sessions = [], set()
    for raw in turns:
        if not isinstance(raw, dict):
            continue
        session, agent = raw.get("kernelSessionId"), raw.get("ownerAgentId")
        conversation, turn = raw.get("conversationKey"), raw.get("turnId")
        turn = str(turn) if type(turn) is int else turn
        at = _timestamp(raw.get("startedAt"))
        if (not all(isinstance(value, str) and _KIMI_ID.fullmatch(value)
                    for value in (session, agent, conversation, turn)) or at is None):
            continue
        if session in sessions:
            # One session with two active turns has no unambiguous observation_ref.
            return None
        sessions.add(session)
        candidates.append({"agent": agent, "session": session, "conversation": conversation,
                           "turn": turn, "at": at})
    return candidates or None


def _kimi_background_tasks(state_path: Path, candidates: list[dict]) -> dict[str, list] | None:
    import subprocess
    node = os.environ.get("KIMI_DESKTOP_RUNTIME_NODE")
    executable = Path(node).expanduser() if node else None
    if executable is None or not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
        return None
    payload = json.dumps([{"agentId": row["agent"], "kernelSessionId": row["session"]} for row in candidates])
    env = {**os.environ, "ELECTRON_RUN_AS_NODE": "1"}
    env.pop("NODE_OPTIONS", None)
    try:
        result = subprocess.run([str(executable), "-e", _KIMI_TASK_QUERY, str(state_path)], input=payload,
                                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=4, env=env)
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    if result.returncode != 0 or len(result.stdout) > 1024 * 1024:
        return None
    rows = json.loads(result.stdout)
    expected = {row["session"] for row in candidates}
    if not isinstance(rows, list) or len(rows) != len(expected):
        return None
    found = {}
    for row in rows:
        if not isinstance(row, dict):
            return None
        session, tasks = row.get("kernelSessionId"), row.get("tasks")
        if session not in expected or session in found or not isinstance(tasks, list) or len(tasks) > 100:
            return None
        found[session] = tasks
    return found if set(found) == expected else None


def _kimi_model_record(raw: bytes) -> dict:
    """Decode only allowlisted scalar fields from a model metadata record."""
    text = raw.decode("utf-8")
    spans = _json_object_spans(text)
    fields = {"type", "model", "time", "usageScope", "kind", "provider", "modelAlias"}
    return {key: json.loads(text[start:end]) for key, (start, end) in spans.items() if key in fields}


def _kimi_wire_model(root: Path, turn: dict, owner: dict, now: float) -> str | None:
    database = root / "daimon/agents/main/sessions/hosted-logical/conversations.sqlite"
    wire_root = root / "daimon/runtime/kimi-code/home/sessions"
    if not _regular(database):
        return None
    try:
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=0.25)) as connection:
            deadline = time.monotonic() + 0.25
            connection.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
            columns = {row[1] for row in connection.execute("PRAGMA table_info(conversations)")}
            required = {"agent_id", "conversation_key", "kernel_session_id", "kernel_records_path", "workspace_path"}
            if not required <= columns:
                return None
            rows = connection.execute(
                "SELECT kernel_records_path, workspace_path FROM conversations"
                " WHERE kernel_session_id=? AND conversation_key=? AND agent_id=? LIMIT 2",
                (turn["session"], turn["conversation"], turn["agent"])).fetchall()
    except (OSError, sqlite3.Error):
        return None
    if len(rows) != 1 or not all(isinstance(value, str) for value in rows[0]):
        return None
    records, workspace = Path(rows[0][0]), Path(rows[0][1])
    if not records.is_absolute() or not workspace.is_absolute() or not _regular(records):
        return None
    records, workspace, cwd = records.resolve(), workspace.resolve(), Path.cwd().resolve()
    if not records.is_relative_to(wire_root) or not cwd.is_relative_to(workspace):
        return None
    relative = records.relative_to(wire_root)
    if (len(relative.parts) != 5 or relative.parts[1] != turn["session"]
            or relative.parts[2:] != ("agents", "main", "wire.jsonl")):
        return None
    if not -2 <= now - records.stat().st_mtime <= MAX_AGE_SECONDS:
        return None
    latest = {}
    for raw in reversed(_tail(records)):
        match = _KIMI_ENVELOPE.match(raw[:128])
        if match:
            kind = match[1].decode("ascii")
            if kind not in latest and len(raw) <= MAX_RECORD_BYTES:
                latest[kind] = raw
            elif kind not in latest:
                return None
        if len(latest) == 2:
            break
    if set(latest) != {"usage.record", "llm.request"}:
        return None
    try:
        usage = _kimi_model_record(latest["usage.record"])
        request = _kimi_model_record(latest["llm.request"])
    except (ValueError, UnicodeError):
        return None
    model = _model(usage.get("model"))
    usage_at = usage.get("time") / 1000 if type(usage.get("time")) in (int, float) else None
    request_at = request.get("time") / 1000 if type(request.get("time")) in (int, float) else None
    started = _started_at(owner)
    if (usage.get("type") != "usage.record" or request.get("type") != "llm.request"
            or usage.get("usageScope") != "turn" or request.get("kind") != "loop"
            or request.get("provider") != "kimi" or model is None or _model(request.get("model")) != model
            or ("modelAlias" in request and _model(request["modelAlias"]) is None)
            or usage_at is None or request_at is None or started is None
            or abs(usage_at - request_at) > 2 or not -2 <= now - usage_at <= MAX_AGE_SECONDS
            or usage_at < turn["at"] - 2 or request_at < turn["at"] - 2 or usage_at < started - 2):
        return None
    return model


def _kimi(owner: dict, now: float) -> dict | None:
    """Bind Kimi's running Bash task to one active turn and its exact wire."""
    root = _kimi_root()
    if root is None:
        return None
    state_path = root / "daimon/agents/main/runner.state.json"
    chain = processes.process_chain()
    pids = {row["pid"] for row in chain if type(row.get("pid")) is int}
    turns = _kimi_active_turns(state_path, pids)
    if not turns:
        return None
    queries = _kimi_background_tasks(state_path, turns)
    if queries is None:
        return None
    shells = []
    for row in chain:
        if row.get("pid") == owner.get("pid"):
            break
        if row.get("name", "").casefold() in _SHELLS and _started_at(row) is not None:
            shells.append(row)
    started = _started_at(owner)
    if started is None:
        return None
    bindings = []
    for turn in turns:
        if not started - 2 <= turn["at"] <= now + 2:
            continue
        for task in queries.get(turn["session"], []):
            if not isinstance(task, dict) or task.get("kind") != "bash" or task.get("status") != "running":
                continue
            pid, at_ms = task.get("pid"), task.get("startedAtMs")
            if type(pid) is not int or type(at_ms) not in (int, float):
                continue
            at = at_ms / 1000
            if not turn["at"] - 2 <= at <= now + 2:
                continue
            if any(row["pid"] == pid and abs(at - _started_at(row)) <= 2 for row in shells):
                bindings.append(turn)
    if len(bindings) != 1:
        # Parallel sessions and duplicate task bindings are not distinguishable.
        return None
    turn = bindings[0]
    current = _kimi_active_turns(state_path, pids)
    if current is None or turn not in current:
        return None
    model = _kimi_wire_model(root, turn, owner, now)
    if model is None:
        return None
    return {"model": model, "source": "kimi-desktop-session-runtime",
            "turn": turn["turn"], "session": turn["session"]}


def collect(harness: str, scope: dict | None, *, diagnostics: dict | None = None) -> dict | None:
    """Return only a model observation bound to the exact current caller."""
    if diagnostics is not None:
        diagnostics.update(harness=harness, readers=list(AUTOMATIC_READERS.get(harness, ())))

    def unavailable(reason: str, *, status: str = "unavailable"):
        if diagnostics is not None:
            diagnostics.update(status=status, reason_code=reason)
        return None

    if harness not in AUTOMATIC_READERS:
        return unavailable("automatic-reader-not-implemented", status="unsupported")
    if scope is None:
        return unavailable("current-caller-scope-unavailable")
    try:
        owner = processes.caller_process(harness)
        if owner is None or not owner.get("started"):
            return unavailable("current-caller-process-unavailable")
        from .detect import PROCESS_RULES
        names = next(names for cli, names in PROCESS_RULES if cli == harness)
        if harness == "zcode":
            # zcode-cli is per conversation; the resident zcode-host above it is
            # structural, so the nearest match must be the session CLI itself.
            if os.name != "posix":
                return unavailable("automatic-reader-platform-unsupported", status="unsupported")
            if owner.get("name") != "zcode-cli":
                return unavailable("current-caller-is-not-session-owner")
            if "execution_ref" not in scope:
                return unavailable("current-execution-scope-unavailable")
            native = _zcode_session_token(owner)
            if not native:
                return unavailable("native-session-binding-unavailable")
        elif harness in ("minimax-code", "kimi-desktop"):
            # These Desktop apps have no conversation environment variable;
            # their own runtime binds the current execution shell to a session.
            if "execution_ref" not in scope:
                return unavailable("current-execution-scope-unavailable")
            native = None
        else:
            native = _native_id(harness)
            if not native:
                return unavailable("native-session-binding-unavailable")
            if scope.get("session_ref") != declarations.digest([harness, native])[:24]:
                return unavailable("native-session-scope-mismatch")
            if sum(processes.matches_row(row, names) for row in processes.process_chain()) != 1:
                return unavailable("ambiguous-harness-ancestry")
        now = time.time()
        detail = {}
        if harness == "claude-code":
            found = _claude(native, owner, now, diagnostics=detail)
            if diagnostics is not None:
                diagnostics.update(detail)
        elif harness == "minimax-code":
            found = _minimax(owner, now)
        elif harness == "kimi-desktop":
            found = _kimi(owner, now)
        else:
            readers = {"codex": _codex, "trae": _trae, "claude-code": _claude, "zcode": _zcode}
            found = readers[harness](native, owner, now) if harness in readers else _pi(native)
        if found:
            reference = found.get("session") or native
            if diagnostics is not None:
                diagnostics.update(status="observed", reason_code=None, source=found["source"])
            return {"harness": harness, "scope": scope, "observed_at": found.get("observed_at", now),
                    "model": found["model"], "source": found["source"],
                    "observation_ref": declarations.digest([harness, reference, found.get("turn"), found["model"]])[:24]}
    except (OSError, ValueError, TypeError, AttributeError, sqlite3.Error, StopIteration) as exc:
        if diagnostics is not None:
            diagnostics["error_type"] = type(exc).__name__
        return unavailable("automatic-probe-error")
    return unavailable(detail.get("reason_code", "native-metadata-unavailable-or-invalid"))
