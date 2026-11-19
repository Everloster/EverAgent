#!/usr/bin/env bash
# Thin-entry plumbing only: repository location and installed CLI selection.
# Source this helper; it never parses business arguments or runs Git itself.
EA_REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"

_ea_entry_error() {
  printf 'EverAgent: %s\n' "$*" >&2
  return 2
}

_ea_require_eacli() {
  local version major minor
  if [[ ${EACLI_BIN+x} ]]; then
    [[ -n "$EACLI_BIN" ]] || { _ea_entry_error 'EACLI_BIN is empty; provide an installed eacli >=10.1.0.'; return 2; }
    if [[ "$EACLI_BIN" == */* ]]; then
      EA_EACLI="$EACLI_BIN"
    else
      EA_EACLI="$(type -P -- "$EACLI_BIN" || true)"
    fi
  elif [[ -n ${HOME:-} && ( -e "$HOME/.local/bin/eacli" || -L "$HOME/.local/bin/eacli" ) ]]; then
    EA_EACLI="$HOME/.local/bin/eacli"
  else
    EA_EACLI="$(type -P -- eacli || true)"
  fi
  [[ -n "$EA_EACLI" && -f "$EA_EACLI" && -x "$EA_EACLI" ]] || {
    _ea_entry_error 'Installed eacli not found or not executable; set EACLI_BIN or install eacli >=10.1.0 separately (no fallback/build/install).'
    return 2
  }
  if ! version="$("$EA_EACLI" --version)"; then
    _ea_entry_error 'eacli --version failed; an installed eacli >=10.1.0 is required.'
    return 2
  fi
  # Require the plain stable release version, without prefixes or extra fields.
  [[ "$version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || {
    _ea_entry_error 'Invalid eacli --version output; expected a plain release version such as 10.1.0.'
    return 2
  }
  major="${BASH_REMATCH[1]}"; minor="${BASH_REMATCH[2]}"
  # String comparison avoids overflow for otherwise valid large version numbers.
  if [[ ${#major} -lt 2 || ( ${#major} -eq 2 && "$major" < 10 ) || ( "$major" == 10 && "$minor" == 0 ) ]]; then
    _ea_entry_error "eacli $version is too old; eacli >=10.1.0 is required (no fallback/build/install)."
    return 2
  fi
}
