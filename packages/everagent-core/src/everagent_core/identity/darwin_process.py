"""Read one known Darwin PID when a sandbox refuses to execute set-id ps.

Uses libproc and KERN_PROCARGS2, not a process scan. Callers supply only their
own ancestor PIDs. Process arguments are returned; environment entries are not.
"""
from __future__ import annotations

import ctypes
import os
import struct
import time


class _BSDInfo(ctypes.Structure):
    # Darwin SDK sys/proc_info.h: struct proc_bsdinfo, PROC_PIDTBSDINFO=3.
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "flags", "status", "xstatus", "pid", "ppid", "uid", "gid", "ruid", "rgid",
        "svuid", "svgid", "reserved")] + [
        ("comm", ctypes.c_char * 16), ("name", ctypes.c_char * 32),
        *[(name, ctypes.c_uint32) for name in ("nfiles", "pgid", "jobc", "tdev", "tpgid")],
        ("nice", ctypes.c_int32), ("start_sec", ctypes.c_uint64), ("start_usec", ctypes.c_uint64)]


def process_row(pid: int) -> dict:
    library = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
    library.proc_pidinfo.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_uint64,
                                    ctypes.c_void_p, ctypes.c_int]
    library.proc_pidinfo.restype = ctypes.c_int
    info = _BSDInfo()
    if library.proc_pidinfo(pid, 3, 0, ctypes.byref(info), ctypes.sizeof(info)) != ctypes.sizeof(info):
        raise OSError(ctypes.get_errno(), 'ancestor process info unavailable')
    if info.pid != pid or info.start_sec <= 0:
        raise ValueError('invalid ancestor process info')
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    path = ctypes.create_string_buffer(4096)
    if library.proc_pidpath(pid, path, len(path)) <= 0:
        raise OSError(ctypes.get_errno(), 'ancestor process path unavailable')
    image = os.fsdecode(path.value)
    return {'pid': pid, 'parent': info.ppid, 'name': os.path.basename(image), 'image': image,
            'started': ' '.join(time.asctime(time.localtime(info.start_sec)).split())}


def _argv(data: bytes) -> list[str]:
    if len(data) < 5:
        raise ValueError('short process arguments')
    count = struct.unpack_from('=i', data)[0]
    if not 1 <= count <= 4096:
        raise ValueError('invalid argument count')
    end = data.find(b'\0', 4)  # executable path precedes argv, with NUL padding.
    if end < 0:
        raise ValueError('missing executable terminator')
    start = end + 1
    while start < len(data) and data[start] == 0:
        start += 1
    args = []
    for _ in range(count):
        end = data.find(b'\0', start)
        if end < 0:
            raise ValueError('truncated process arguments')
        args.append(os.fsdecode(data[start:end]))
        start = end + 1
    return args


def process_args(pid: int) -> list[str]:
    library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    library.sysctl.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_uint,
                              ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t),
                              ctypes.c_void_p, ctypes.c_size_t]
    library.sysctl.restype = ctypes.c_int
    mib = (ctypes.c_int * 3)(1, 49, pid)  # CTL_KERN, KERN_PROCARGS2, exact ancestor.
    size = ctypes.c_size_t()
    if library.sysctl(mib, 3, None, ctypes.byref(size), None, 0) or not 4 < size.value <= 1024 * 1024:
        raise OSError(ctypes.get_errno(), 'ancestor arguments unavailable')
    data = ctypes.create_string_buffer(size.value)
    if library.sysctl(mib, 3, data, ctypes.byref(size), None, 0):
        raise OSError(ctypes.get_errno(), 'ancestor arguments unavailable')
    return _argv(data.raw[:size.value])
