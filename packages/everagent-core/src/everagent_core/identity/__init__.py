"""Installable Agent identity API, independent of private infrastructure."""
from . import detect as core, models, processes
import hashlib
from pathlib import Path

detect = core.detect
inspect_identity = core.inspect_identity
model_evidence = models.model_evidence
detect_model = models.detect_model


def source_sha256() -> str:
    digest = hashlib.sha256()
    root = Path(__file__).resolve().parent
    for path in sorted(root.glob("*.py")):
        digest.update(path.name.encode() + b"\0" + path.read_bytes() + b"\0")
    return digest.hexdigest()
