#!/usr/bin/env python3
"""Record the user's explicit current-model choice for this exact harness session."""
import sys
import core_bootstrap  # noqa: F401
from everagent_core.identity.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["declare-model", *sys.argv[1:]]))
