"""Small reader configuration: repair locations/signatures, never supply evidence."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re

_CONFIG_FILE = Path(__file__).with_name("readers.json")
OWNER = "packages/everagent-core/src/everagent_core/identity/readers.json"


def load(*, override: bool = True) -> dict:
    value = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    explicit = os.environ.get("EVERAGENT_IDENTITY_CONFIG") if override else None
    if explicit:
        path = Path(explicit).expanduser()
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
            raise ValueError("identity-config-unavailable")
        patch = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(patch, dict) or set(patch) - {"schema_version", "harnesses"} or patch.get("schema_version") != 1:
            raise ValueError("identity-config-schema-invalid")
        changes = patch.get("harnesses")
        if not isinstance(changes, dict) or len(changes) > 64:
            raise ValueError("identity-config-harnesses-invalid")
        for key, fields in changes.items():
            if not isinstance(fields, dict):
                raise ValueError("identity-config-rule-invalid")
            value["harnesses"][key] = {**value["harnesses"].get(key, {}), **fields}
    for key, fields in value["harnesses"].items():
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", key) or set(fields) - {"process_names", "session_keys", "root", "model_key", "form"}:
            raise ValueError("identity-config-rule-invalid")
        for field in ("process_names", "session_keys"):
            items = fields.get(field, [])
            if not isinstance(items, list) or len(items) > 16 or any(not isinstance(x, str) or not x or len(x) > 128 for x in items):
                raise ValueError("identity-config-signature-invalid")
            if field == "process_names" and any(x.casefold() in {"node", "python", "python3", "bash", "zsh", "sh", "pwsh", "cmd.exe"} or any(c in x for c in "/\\*?\n\r") for x in items):
                raise ValueError("identity-config-generic-process-refused")
            if field == "session_keys" and any(not re.fullmatch(r"[A-Z][A-Z0-9_]{1,127}", x) or re.search(r"TOKEN|PASSWORD|SECRET|COOKIE|AUTH|API_KEY", x) for x in items):
                raise ValueError("identity-config-session-key-invalid")
        if fields.get("form") not in {"cli", "desktop", "web"}:
            raise ValueError("identity-config-form-invalid")
        if "root" in fields:
            root = fields["root"]
            if not isinstance(root, str) or len(root) > 1024 or any(c in root for c in "\n\r\x00*?$") or not (root.startswith("~/") or Path(root).is_absolute()):
                raise ValueError("identity-config-root-invalid")
        if "model_key" in fields and (not isinstance(fields["model_key"], str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", fields["model_key"])):
            raise ValueError("identity-config-model-key-invalid")
    return value["harnesses"]


def rule(harness: str) -> dict:
    return load().get(harness, {})


def root(harness: str, home: Path | None, *, override: str | None = None) -> Path | None:
    value = override or rule(harness).get("root")
    if not value:
        return None
    if value.startswith("~/"):
        return (home / value[2:]).resolve() if home else None
    path = Path(value)
    return path.resolve() if path.is_absolute() else None
