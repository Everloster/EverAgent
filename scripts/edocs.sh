#!/usr/bin/env bash
# Repository-bound document-tool adapter; all implementation lives in eacli.
set -euo pipefail
_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source "$_SCRIPT_DIR/eacli-entry.sh"
case "${1:-}" in
  ''|-) printf 'Usage: edocs.sh ACTION <args>\n' >&2; exit 2 ;;
  -h|--help) printf 'Usage: edocs.sh ACTION <args> (see eacli docs --help)\n'; exit 0 ;;
esac
_ACTION="$1"; shift
_ea_require_eacli
exec "$EA_EACLI" docs "$_ACTION" --repo-root "$EA_REPO_ROOT" "$@"
