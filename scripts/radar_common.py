"""Shared local registry helpers for the blog and podcast radars."""

from __future__ import annotations

import json
import pathlib
import tempfile
from typing import Any


class RadarError(RuntimeError):
    pass


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = pathlib.Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_set_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def set_dotted(target: dict[str, Any], assignment: str) -> None:
    if "=" not in assignment:
        raise RadarError(f"--set 需要 key=value：{assignment}")
    path, raw = assignment.split("=", 1)
    keys = [key for key in path.split(".") if key]
    if not keys:
        raise RadarError("--set key 不能为空")
    cursor = target
    for key in keys[:-1]:
        child = cursor.get(key)
        if child is None:
            child = {}
            cursor[key] = child
        if not isinstance(child, dict):
            raise RadarError(f"无法进入非 object 字段：{key}")
        cursor = child
    cursor[keys[-1]] = parse_set_value(raw)
