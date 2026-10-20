#!/usr/bin/env python3
"""Recognize the current Agent, model and Git identity. Stable public CLI/API.

--json returns evidence; --git-ident emits name<TAB>email from one query.
Configuration defaults remain hints and do not confirm the active model.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

# Load by owned path so a private agent_identity.py bridge cannot shadow this package.
_PACKAGE = Path(__file__).resolve().parent / "agent_identity"
_PACKAGE_NAME = "_everagent_identity_" + hashlib.sha256(str(_PACKAGE).encode()).hexdigest()[:12]
if _PACKAGE_NAME not in sys.modules:
    _SPEC = importlib.util.spec_from_file_location(
        _PACKAGE_NAME, _PACKAGE / "__init__.py", submodule_search_locations=[str(_PACKAGE)])
    if _SPEC is None or _SPEC.loader is None:
        raise ImportError("public Agent identity package is unavailable")
    _identity = importlib.util.module_from_spec(_SPEC)
    sys.modules[_PACKAGE_NAME] = _identity
    _SPEC.loader.exec_module(_identity)
else:
    _identity = sys.modules[_PACKAGE_NAME]


def inspect_identity() -> dict:
    return {**_identity.inspect_identity(), "source_sha256": _identity.source_sha256()}


def detect() -> tuple[str, str]:
    value = inspect_identity()
    return value["name"], value["email"]


model_evidence = _identity.model_evidence
detect_model = _identity.detect_model

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--name", action="store_true")
    output.add_argument("--email", action="store_true")
    output.add_argument("--json", action="store_true")
    output.add_argument("--git-ident", action="store_true")
    args = parser.parse_args()
    identity = inspect_identity()
    name, email = identity["name"], identity["email"]
    if args.name:
        print(name)
    elif args.email:
        print(email)
    elif args.json:
        print(json.dumps(identity, ensure_ascii=False))
    elif args.git_ident:
        print(f"{name}\t{email}")
        return 0 if identity["resolved"] else 1
    else:
        print(f"name={name}")
        print(f"email={email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
