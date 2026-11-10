#!/usr/bin/env bash
# Public entry: verified Committer plus changed-content disclosure; no quality pipeline.
set -euo pipefail
_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_BUILD_DIR="$(mktemp -d "${TMPDIR:-/tmp}/everagent-git.XXXXXXXX")"
trap 'rm -rf -- "$_BUILD_DIR"' EXIT
go -C "$_SCRIPT_DIR/../packages/everagent-core" build -mod=readonly -trimpath -buildvcs=false \
  -o "$_BUILD_DIR/ea-git" ./cmd/ea-git
# go run collapses every nonzero child status to 1; preserve the CLI contract.
"$_BUILD_DIR/ea-git" --repo-root "$_SCRIPT_DIR/.." commit "$@"
