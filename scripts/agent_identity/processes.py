"""Bounded process ancestry probes; only the caller chain is identity evidence."""
from __future__ import annotations
import os
import sys

_ANCESTORS: list[str] | None = None
_WIN_SCAN: tuple[list[str], list[str], bool] | None = None

def _win_scan() -> tuple[list[str], list[str], bool]:
    """Windows 进程扫描：ctypes Toolhelp32 快照（纯 stdlib、毫秒级、无 PowerShell 冷启动抖动）。
    返回 (祖先链原始名称, 空的兼容字段, 祖先链是否正常走到根)。
    MSYS2 exec 可能使祖先链截断；此时不把其他进程当成当前 Agent。"""
    global _WIN_SCAN
    if _WIN_SCAN is not None:
        return _WIN_SCAN
    ancestors: list[str] = []
    all_raw: list[str] = []
    reached_root = False
    try:
        import ctypes

        TH32CS_SNAPPROCESS = 0x00000002
        INVALID_HANDLE = ctypes.c_void_p(-1).value

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_ulong),
                ("cntUsage", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", ctypes.c_ulong),
                ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_wchar * 260),
            ]

        k32 = ctypes.windll.kernel32
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == INVALID_HANDLE:
            raise OSError("CreateToolhelp32Snapshot failed")
        try:
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            procs: dict[int, tuple[int, str]] = {}
            ok = k32.Process32FirstW(snap, ctypes.byref(entry))
            while ok:
                procs[entry.th32ProcessID] = (entry.th32ParentProcessID, entry.szExeFile)
                ok = k32.Process32NextW(snap, ctypes.byref(entry))
        finally:
            k32.CloseHandle(snap)
        pid = os.getpid()
        for _ in range(16):
            info = procs.get(pid)
            if not info:
                break  # 父进程已死（MSYS2 exec 截断）→ 链断
            ppid, exe = info
            ancestors.append(exe)
            if ppid <= 0 or ppid == pid or exe.lower() in ("explorer.exe", "services.exe", "sshd.exe", "system"):
                reached_root = True
                break
            pid = ppid
    except Exception as e:
        if os.environ.get("WHOAMI_DEBUG"):
            print(f"[whoami] _win_scan 异常: {e!r}", file=sys.stderr)
    _WIN_SCAN = (ancestors, all_raw, reached_root)
    return _WIN_SCAN


def _process_ancestors() -> list[str]:
    """单次、有界的祖先链；Windows 断链时保持未知，不匹配全机其他进程。"""
    global _ANCESTORS
    if _ANCESTORS is not None:
        return _ANCESTORS
    if os.name == "nt":
        _ANCESTORS = _win_scan()[0]
        return _ANCESTORS
    ancestors = []
    try:
        import subprocess
        pid = os.getpid()
        seen = set()
        for _ in range(16):
            if pid in seen:
                break
            seen.add(pid)
            out = subprocess.run(["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=1).stdout.strip()
            if not out:
                break
            parts = out.split(None, 1)
            if len(parts) < 2:
                break
            ppid, comm = parts[0], parts[1]
            ancestors.append(os.path.basename(comm))
            pid = int(ppid) if ppid.isdigit() else 0
            if pid <= 1:
                break
    except Exception:
        pass
    _ANCESTORS = ancestors
    return ancestors


def _matches_process(base: str, names: tuple[str, ...]) -> bool:
    if os.name == "nt":
        if base.lower().endswith(".exe"):
            base = base[:-4]
        return any(base == name if name == "kimi" else base.lower() == name.lower() for name in names)
    return any(base == name or
               (name == "zcode-host" and base.startswith("zcode-host-")) or
               (name == "MiniMax Code" and base.startswith("MiniMax Code Helper"))
               for name in names)


def _proc_has(*names) -> bool:
    return any(_matches_process(base, names) for base in _process_ancestors())
