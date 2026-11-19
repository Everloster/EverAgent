#!/usr/bin/env bash
# Commit shorthand; forward every message, trailer and Git argument unchanged.
set -euo pipefail
_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
exec "$_SCRIPT_DIR/egit.sh" commit "$@"
