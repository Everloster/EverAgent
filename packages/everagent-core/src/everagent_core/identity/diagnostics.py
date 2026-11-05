"""Explain identity failures using current-caller metadata and public owner paths."""
from __future__ import annotations

from . import config, declarations, observations, processes
from .detect import _detect_cli, inspect_identity


def diagnose() -> dict:
    processes.reset_cache()
    config_error = None
    try:
        config.load()
        harness, _ = _detect_cli()
    except (OSError, ValueError, TypeError) as exc:
        harness, config_error = None, type(exc).__name__
    probe = {}
    scope = None
    if harness:
        scope = declarations.caller_scope(harness)
        observation = observations.collect(harness, scope, diagnostics=probe)
    else:
        observation = None
        probe = {"harness": None, "readers": [], "status": "unavailable",
                 "reason_code": "reader-config-invalid" if config_error else "current-harness-unresolved"}
    # An empty observation suppresses a second read and cannot authorize a model.
    value = inspect_identity(observation=observation or {})
    ready = value.get("commit_ready") is True
    owner = "packages/everagent-core/src/everagent_core/identity/"
    return {
        "schema_version": 1,
        "status": "ready" if ready else "repair-needed",
        "identity": value,
        "automatic_probe": probe,
        "reader_config": {"owner": config.OWNER, "override_environment": "EVERAGENT_IDENTITY_CONFIG",
                          "status": "invalid" if config_error else "valid", "error_type": config_error},
        "repair": {
            "owner_repository": "EverAgent",
            "owners": [owner + file for file in (
                "readers.json", "config.py", "detect.py", "processes.py", "observations.py", "models.py", "declarations.py")],
            "order": ["inspect-current-caller-binding", "repair-supported-reader-or-adapter",
                      "verify-current-session-and-regressions", "request-explicit-user-facts-if-unverifiable"],
            "validation": ["eacli session current --json",
                           "python3 scripts/agent_identity.py diagnose --json"],
            "source_validation_repository": "EverAgent",
            "boundary": "Only current-caller metadata; preserve privacy, process/session binding, freshness and unknown states.",
        },
        "user_fallback": {
            "role": "last-resort", "available": declarations.fact_scope() is not None,
            "fields": ["device", "harness", "form", "model"],
            "requires_explicit_user_confirmation": True,
            "condition": "Current-session evidence remains unavailable after scoped diagnosis and feasible source repair.",
        },
        "authorized_source_repair_allowed": True,
        "authorized_read_only_allowed": True,
        "commit_allowed": ready,
        "diagnostics_are_model_evidence": False,
    }
