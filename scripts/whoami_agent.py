#!/usr/bin/env python3
"""Compatibility identity CLI/API. Owner: packages/everagent-core."""
from pathlib import Path
import sys

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import core_bootstrap  # noqa: E402,F401
from everagent_core import identity as _identity  # noqa: E402
from everagent_core.identity.cli import main  # noqa: E402

model_evidence = _identity.model_evidence
detect_model = _identity.detect_model


def inspect_identity() -> dict:
    return {**_identity.inspect_identity(), "source_sha256": _identity.source_sha256()}


def detect() -> tuple[str, str]:
    value = inspect_identity()
    return value["name"], value["email"]


if __name__ == "__main__":
    raise SystemExit(main())
