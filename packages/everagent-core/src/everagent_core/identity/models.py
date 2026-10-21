"""Model observations, user declarations and configuration hints stay distinct."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import time
from . import declarations, observations

# Compatibility field: a missing Windows home is a real unknown, not an import failure.
HOME = declarations.safe_home()
ENV_KEYS = {
    "opencode": ("OPENCODE_MODEL",), "trae": ("TRAE_MODEL",), "codex": ("CODEX_MODEL",),
    "claude-code": ("ANTHROPIC_MODEL", "CLAUDE_MODEL"), "cowork": ("ANTHROPIC_MODEL", "CLAUDE_MODEL"),
    "gemini-cli": ("GEMINI_MODEL",), "cursor": ("CURSOR_MODEL",), "cursor-cli": ("CURSOR_MODEL",),
    "pi": ("PI_MODEL",), "zcode": ("ZCODE_MODEL",), "kimi-cli": ("KIMI_MODEL",),
    "minimax-code": ("MINIMAX_MODEL",), "qoderclicn": ("QODERCN_MODEL",),
}
OBSERVATION_SOURCES = {
    "codex-turn-context", "codex-thread-state", "pi-session-runtime", "trae-thread-runtime",
    "orca-agent-session", "herdr-agent-session", "desktop-session-api",
}


def _valid(model) -> str | None:
    return model if isinstance(model, str) and declarations.MODEL_RE.fullmatch(model) and model.lower() != "unknown" else None


def _read_text(path: Path) -> str:
    try:
        if not path.is_file() or path.stat().st_size > 1024 * 1024:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except (OSError, RuntimeError):
        return ""


def _toml_get(path: Path, key: str) -> str | None:
    for line in _read_text(path).splitlines():
        if line.lstrip().startswith("["):
            break
        match = re.match(rf'^\s*{re.escape(key)}\s*=\s*"([^"\n]+)"\s*(?:#.*)?$', line)
        if match:
            return match.group(1).strip()
    return None


def _yaml_get(path: Path, key: str) -> str | None:
    for line in _read_text(path).splitlines():
        match = re.match(rf'^\s*{re.escape(key)}\s*:\s*["\']?([^"\'\n#]+)["\']?\s*(?:#.*)?$', line)
        if match:
            return match.group(1).strip()
    return None


def configuration_hint(harness: str) -> dict:
    for key in (*ENV_KEYS.get(harness, ()), "AGENT_MODEL"):
        if _valid(os.environ.get(key)):
            return {"model": os.environ[key], "source": "env:" + key, "confidence": "environment-hint"}
    home = HOME
    raw = None
    if harness == "codex":
        codex_home = os.environ.get("CODEX_HOME")
        root = Path(codex_home) if codex_home else home / ".codex" if home else None
        raw = _toml_get(root / "config.toml", "model") if root else None
    elif home and harness == "trae":
        raw = _toml_get(home / ".trae/traecli.toml", "model")
    elif home and harness == "kimi-cli":
        raw = _toml_get(home / ".kimi-code/config.toml", "default_model")
        raw = raw.split("/")[-1] if raw else None
    elif home and harness == "minimax-code":
        raw = _yaml_get(home / ".minimax/config.yaml", "defaultModel")
        raw = re.sub(r"^minimax-", "", raw.split("/")[-1], flags=re.I) if raw else None
    elif home and harness == "qoderclicn":
        try:
            raw = json.loads(_read_text(home / ".qoder-cn/settings.json")).get("model", {}).get("name")
        except (ValueError, TypeError, AttributeError):
            pass
    # Desktop clients do not borrow a similarly named CLI's config or a global recent log.
    return {"model": _valid(raw) or "unknown", "source": "config-default" if _valid(raw) else "unresolved",
            "confidence": "configured" if _valid(raw) else "unknown"}


def hint_fingerprint(harness: str) -> str:
    return declarations.digest(configuration_hint(harness))


def model_evidence(harness: str, *, observation: dict | None = None) -> dict:
    """Automatically inspect the current runtime before falling back to a user declaration."""
    hint = configuration_hint(harness)
    scope = declarations.caller_scope(harness)
    if observation is None:
        observation = observations.collect(harness, scope)
    evidence = {"requested_model": None,
                "configured_model": hint["model"] if hint["model"] != "unknown" else None,
                "observed_model": None, "user_declared_model": None}
    if (isinstance(observation, dict) and scope is not None
            and observation.get("scope") == scope and observation.get("harness") == harness
            and observation.get("source") in OBSERVATION_SOURCES
            and type(observation.get("observed_at")) in (int, float)
            and 0 <= time.time() - observation["observed_at"] <= 300
            and _valid(observation.get("model"))):
        return {**evidence, "observed_model": observation["model"],
                "model": observation["model"], "source": observation["source"], "confidence": "session-bound",
                "current_model_confirmed": True, "user_model_declared": False,
                "scope_ref": declarations.digest(scope)[:24], "observed_at": observation["observed_at"],
                **({"observation_ref": observation["observation_ref"]} if observation.get("observation_ref") else {})}
    declared = declarations.read_declaration(harness, hint=declarations.digest(hint))
    if declared:
        return {**evidence, "user_declared_model": declared["model"],
                "model": declared["model"], "source": "user-declared", "confidence": "declared",
                "current_model_confirmed": False, "user_model_declared": True,
                "declaration": {"id": declared["id"], "scope_ref": declarations.digest(declared["scope"])[:24],
                                "expires_at": declared["expires_at"]}}
    return {**evidence, **hint, "current_model_confirmed": False, "user_model_declared": False}


def detect_model(harness: str) -> str:
    return model_evidence(harness)["model"]
