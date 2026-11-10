#!/usr/bin/env bash
# Commit compatibility entry; Author, Committer and content checks share egit.
set -euo pipefail
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$_SCRIPT_DIR/egit.sh" commit "$@"
