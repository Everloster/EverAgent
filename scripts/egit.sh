#!/usr/bin/env bash
# Repository-bound Git entry; preserves configured hooks and normal Git failures.
set -euo pipefail
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/everagent-git.XXXXXXXX")"
trap 'rm -rf -- "$_BUILD_DIR"' EXIT
go -C "$_SCRIPT_DIR/../packages/everagent-core" build -mod=readonly -trimpath -buildvcs=false \
  -o "$_BUILD_DIR/ea-git" ./cmd/ea-git
"$_BUILD_DIR/ea-git" --repo-root "$_SCRIPT_DIR/.." "$@"
