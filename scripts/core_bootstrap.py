"""Load the public source package from this checkout, including linked worktrees."""
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / "packages/everagent-core/src"
if not (SOURCE / "everagent_core/__init__.py").is_file():
    raise ImportError("EverAgent core source is unavailable")
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))
