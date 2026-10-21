"""Compatibility import. Implementation belongs to the installable public core."""
from pathlib import Path
import sys

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import core_bootstrap  # noqa: E402,F401
from everagent_core.identity import (  # noqa: E402,F401
    core, models, processes, detect, inspect_identity, model_evidence,
    detect_model, source_sha256,
)
for _name, _module in (("models", models), ("processes", processes), ("detect", core)):
    sys.modules[__name__ + "." + _name] = _module
