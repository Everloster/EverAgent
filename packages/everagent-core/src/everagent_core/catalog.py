"""Describe scripts and validate their ownership, aliases and contracts."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re

KINDS = {"canonical", "compatibility", "internal"}
PLATFORMS = {"macos", "linux", "windows"}
FIELDS = {"id", "description", "entrypoint", "owner", "kind", "aliases", "platforms",
          "requirements", "input", "output", "side_effects", "authorization", "scope"}


def relative_path(value: object) -> bool:
    return (isinstance(value, str) and bool(value) and "\\" not in value
            and not value.startswith("/") and ":" not in value
            and all(part not in ("", ".", "..") for part in value.split("/")))


def load_catalog(path: Path) -> dict:
    if path.stat().st_size > 262144:
        raise ValueError("script catalog exceeds 256 KiB")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("script catalog must be an object")
    return value


def validate_catalog(value: dict, *, roots: dict[str, Path] | None = None) -> list[str]:
    errors, ids, entrypoints = [], set(), set()
    if value.get("schema_version") != 1 or not isinstance(value.get("scripts"), list):
        return ["unsupported script catalog"]
    repository = value.get("repository")
    for row in value["scripts"]:
        if not isinstance(row, dict) or set(row) != FIELDS:
            errors.append("script descriptor fields differ from schema")
            continue
        label = row["id"]
        if not isinstance(label, str) or not re.fullmatch(r"[a-z][a-z0-9.-]{1,79}", label) or label in ids:
            errors.append("invalid/duplicate script id")
        ids.add(str(label))
        if not isinstance(row["description"], str) or not 8 <= len(row["description"]) <= 240:
            errors.append(f"{label}: description must explain its purpose")
        if (not isinstance(row["kind"], str) or row["kind"] not in KINDS
                or not isinstance(row["platforms"], list) or not row["platforms"]
                or not all(isinstance(p, str) for p in row["platforms"])
                or not set(row["platforms"]) <= PLATFORMS):
            errors.append(f"{label}: invalid kind/platforms")
        for key in ("requirements", "side_effects"):
            if not isinstance(row[key], list) or any(not isinstance(x, str) for x in row[key]):
                errors.append(f"{label}: invalid {key}")
        if not all(isinstance(row[k], str) and row[k] for k in ("input", "output", "scope")):
            errors.append(f"{label}: missing contract/scope")
        if not isinstance(row["aliases"], list):
            errors.append(f"{label}: invalid aliases")
            continue
        paths = [row["entrypoint"], *[a.get("path") for a in row["aliases"] if isinstance(a, dict)]]
        if len(paths) != 1 + len(row["aliases"]):
            errors.append(f"{label}: invalid alias descriptor")
        for path in paths:
            if not relative_path(path) or path in entrypoints:
                errors.append(f"{label}: unsafe/duplicate entrypoint")
                continue
            entrypoints.add(path)
            if roots and repository in roots and not (roots[repository] / path).is_file():
                errors.append(f"{label}: missing entrypoint {path}")
        for key in ("owner", "authorization"):
            target = row[key]
            if (not isinstance(target, dict) or not isinstance(target.get("repository"), str)
                    or not relative_path(target.get("path"))):
                errors.append(f"{label}: invalid {key} reference")
                continue
            if key == "authorization" and not target.get("section"):
                errors.append(f"{label}: authorization needs a section/operation reference")
            if roots and target["repository"] in roots and not (roots[target["repository"]] / target["path"]).is_file():
                errors.append(f"{label}: missing {key} {target['path']}")
        if any(not isinstance(a.get("description"), str) or not a["description"] for a in row["aliases"] if isinstance(a, dict)):
            errors.append(f"{label}: alias needs a description")
    return errors


def render_index(value: dict, *, source_sha256: str) -> str:
    lines = ["# 脚本目录", "", "> Generated from script-catalog.json; do not edit by hand.",
             f"> source-sha256: `{source_sha256}`",
             f"> generator-sha256: `{hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}`", "",
             "| ID | 入口 | 描述 | 范围 |", "|---|---|---|---|"]
    for row in value["scripts"]:
        description = row["description"].replace("|", "\\|")
        lines.append(f"| `{row['id']}` | `{row['entrypoint']}` | {description} | {row['scope']} |")
        for alias in row["aliases"]:
            lines.append(f"| ↳ compatibility | `{alias['path']}` | {alias['description']} | 同 canonical |")
    return "\n".join([*lines, ""])


def catalog_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
