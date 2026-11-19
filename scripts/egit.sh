#!/usr/bin/env bash
# Repository-bound adapter to installed eacli; no Git implementation or fallback.
set -euo pipefail
_SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
source "$_SCRIPT_DIR/eacli-entry.sh"

case "${1:-}" in
  identity|commit|merge|push|hooks) _ACTION="$1"; shift ;;
  validate) _ACTION=identity; shift; set -- validate "$@" ;;
  -h|--help) printf 'Usage: egit.sh identity|validate|commit|merge|push|hooks <args>\n'; exit 0 ;;
  *) printf 'Usage: egit.sh identity|validate|commit|merge|push|hooks <args>\n' >&2; exit 2 ;;
esac
_ea_require_eacli
exec "$EA_EACLI" git "$_ACTION" --repo-root "$EA_REPO_ROOT" "$@"
