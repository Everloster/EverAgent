"""Bounded caller ancestry. Other terminals never supply identity evidence."""
from __future__ import annotations

import hashlib
import os
import subprocess

_ANCESTORS: list[str] | None = None
_WIN_SCAN: tuple[list[str], list[str], bool] | None = None
_CHAIN: list[dict] | None = None


def reset_cache() -> None:
    global _ANCESTORS, _WIN_SCAN, _CHAIN
    _ANCESTORS = None
    _WIN_SCAN = None
    _CHAIN = None


def _windows_chain() -> tuple[list[dict], bool]:
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    class Entry(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("usage", wintypes.DWORD),
                    ("pid", wintypes.DWORD), ("heap", ctypes.c_size_t),
                    ("module", wintypes.DWORD), ("threads", wintypes.DWORD),
                    ("parent", wintypes.DWORD), ("priority", wintypes.LONG),
                    ("flags", wintypes.DWORD), ("name", wintypes.WCHAR * 260)]
    kernel.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(Entry)]
    kernel.Process32FirstW.restype = wintypes.BOOL
    kernel.Process32NextW.argtypes = kernel.Process32FirstW.argtypes
    kernel.Process32NextW.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
    kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
    kernel.GetProcessTimes.argtypes = [wintypes.HANDLE, *([ctypes.POINTER(wintypes.FILETIME)] * 4)]
    kernel.GetProcessTimes.restype = wintypes.BOOL
    snapshot = kernel.CreateToolhelp32Snapshot(2, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise OSError("process snapshot unavailable")
    entry = Entry()
    entry.size = ctypes.sizeof(Entry)
    parents = {}
    try:
        more = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while more:
            parents[entry.pid] = (entry.parent, entry.name)
            more = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    chain, seen, pid, reached = [], set(), os.getpid(), False
    for _ in range(16):
        if pid in seen or pid not in parents:
            break
        seen.add(pid)
        parent, name = parents[pid]
        row = {"pid": pid, "parent": parent, "name": name, "started": None, "image": ""}
        handle = kernel.OpenProcess(0x1000, False, pid)
        if handle:
            try:
                buffer = ctypes.create_unicode_buffer(32768)
                size = wintypes.DWORD(len(buffer))
                if kernel.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
                    row["image"] = buffer.value
                times = [wintypes.FILETIME() for _ in range(4)]
                if kernel.GetProcessTimes(handle, *[ctypes.byref(x) for x in times]):
                    row["started"] = str((times[0].dwHighDateTime << 32) | times[0].dwLowDateTime)
            finally:
                kernel.CloseHandle(handle)
        chain.append(row)
        if parent <= 0 or parent == pid or name.casefold() in ("explorer.exe", "services.exe", "sshd.exe", "system"):
            reached = True
            break
        pid = parent
    return chain, reached


def process_chain() -> list[dict]:
    global _CHAIN
    if _CHAIN is not None:
        return _CHAIN
    chain = []
    try:
        if os.name == "nt":
            chain, _ = _windows_chain()
        else:
            pid, seen = os.getpid(), set()
            for _ in range(16):
                if pid in seen or pid <= 1:
                    break
                seen.add(pid)
                result = subprocess.run(["ps", "-o", "ppid=,lstart=,comm=", "-p", str(pid)],
                                        capture_output=True, text=True, encoding="utf-8",
                                        errors="replace", timeout=1, env={**os.environ, "LC_ALL": "C"})
                parts = result.stdout.strip().split(None, 6)
                if len(parts) != 7 or not parts[0].isdigit():
                    break
                parent = int(parts[0])
                chain.append({"pid": pid, "parent": parent, "name": os.path.basename(parts[6]),
                              "started": " ".join(parts[1:6]), "image": parts[6]})
                pid = parent
    except (OSError, ValueError, subprocess.SubprocessError, AttributeError):
        pass
    _CHAIN = chain
    return chain


def _win_scan() -> tuple[list[str], list[str], bool]:
    global _WIN_SCAN
    if _WIN_SCAN is None:
        try:
            chain, reached = _windows_chain()
            _WIN_SCAN = ([row["name"] for row in chain], [], reached)
        except (OSError, AttributeError, ImportError):
            _WIN_SCAN = ([], [], False)
    return _WIN_SCAN


def _process_ancestors() -> list[str]:
    global _ANCESTORS
    if _ANCESTORS is None:
        _ANCESTORS = _win_scan()[0] if os.name == "nt" else [row["name"] for row in process_chain()]
    return _ANCESTORS


def _matches_process(base: str, names: tuple[str, ...]) -> bool:
    if os.name == "nt":
        if base.casefold().endswith(".exe"):
            base = base[:-4]
        # The Desktop's Kimi and the CLI's kimi must not silently alias.
        return any(base == name if name in ("kimi", "Kimi") else base.casefold() == name.casefold()
                   for name in names)
    return any(base == name or (name == "zcode-host" and base.startswith("zcode-host-"))
               or (name == "MiniMax Code" and base.startswith("MiniMax Code Helper")) for name in names)


def _proc_has(*names) -> bool:
    return any(_matches_process(base, names) for base in _process_ancestors())


def matches_row(row: dict, names: tuple[str, ...]) -> bool:
    if os.name == "nt" and any(name in names for name in ("kimi", "Kimi", "MiniMax Code", "ZCode")):
        from ..apps import app_for_process
        app_id = app_for_process(row, windows=True)
        desktop = {"kimi-desktop": "Kimi", "minimax-code": "MiniMax Code", "zcode": "ZCode"}
        if app_id:
            return desktop[app_id] in names
        if row.get("name", "").casefold().removesuffix(".exe") == "kimi":
            path = row.get("image", "").replace("\\", "/").casefold()
            cli_path = any(part in path for part in ("/.local/bin/", "/scripts/", "/kimi-cli/", "/.kimi/bin/"))
            return "kimi" in names and cli_path
        if any(name in names for name in ("Kimi", "MiniMax Code", "ZCode")):
            return False
    return _matches_process(row.get("name", ""), names)


def caller_process(harness: str) -> dict | None:
    from .detect import PROCESS_RULES
    harness = "claude-code" if harness == "cowork" else harness
    names = next((names for key, names in PROCESS_RULES if key == harness), ())
    for row in process_chain():
        if matches_row(row, names):
            return row
    return None


def caller_anchor(harness: str) -> str | None:
    row = caller_process(harness)
    if row is None or not row.get("started"):
        return None
    raw = f'{harness}:{row["pid"]}:{row["started"]}'.encode()
    return hashlib.sha256(raw).hexdigest()[:24]
