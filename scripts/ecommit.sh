#!/usr/bin/env bash
# Stable ecommit entry; shared identity, argument, trailer and index rules live in git_commit.py.
set -euo pipefail
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for _COMMAND in python3 python; do
  if [ "$("$_COMMAND" -c 'print("everagent-python-ok")' 2>/dev/null || true)" = "everagent-python-ok" ]; then
    exec "$_COMMAND" "$_SCRIPT_DIR/git_commit.py" "$@"
  fi
done
if [ "$(py -3 -c 'print("everagent-python-ok")' 2>/dev/null || true)" = "everagent-python-ok" ]; then
  exec py -3 "$_SCRIPT_DIR/git_commit.py" "$@"
fi
echo "[ecommit] BLOCKED: 找不到可执行的 Python 解释器" >&2
exit 1
