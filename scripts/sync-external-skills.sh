#!/usr/bin/env bash
# 同步两个 vendor 技能；只有显式 --install 才写用户级技能目录。
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd -P)"
REPO_URL="${EVERAGENT_SKILLS_UPSTREAM:-https://github.com/K-Dense-AI/scientific-agent-skills}"
SKILLS=(hypothesis-generation scientific-writing)
DEST_ROOT="$REPO_ROOT/docs/external-skills/scientific-agent-skills"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP" "$DEST_ROOT"/.*.new.$$' EXIT

echo "[sync] sparse-clone 上游 $REPO_URL ..."
git clone --quiet --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TMP/upstream"
git -C "$TMP/upstream" sparse-checkout set skills >/dev/null 2>&1

UPSTREAM_COMMIT=$(git -C "$TMP/upstream" rev-parse HEAD)
UPSTREAM_DATE=$(git -C "$TMP/upstream" log -1 --format=%cd --date=short)
echo "[sync] 上游 HEAD: $UPSTREAM_COMMIT ($UPSTREAM_DATE)"

mkdir -p "$TMP/staged"
for s in "${SKILLS[@]}"; do
  src="$TMP/upstream/skills/$s"
  if [ ! -d "$src" ]; then
    echo "[sync] 上游缺少 ${s}；未修改任何本地技能，请人工核对目录迁移。" >&2
    exit 1
  fi
  cp -R "$src" "$TMP/staged/$s"
done

CHANGED=()
for s in "${SKILLS[@]}"; do
  dst="$DEST_ROOT/$s"
  if [ ! -d "$dst" ] || ! diff -qr "$TMP/staged/$s" "$dst" >/dev/null 2>&1; then
    CHANGED+=("$s")
  fi
done

if [ "${#CHANGED[@]}" = 0 ]; then
  echo "[sync] 与上游一致，无需提交。"
else
  for s in "${CHANGED[@]}"; do
    new="$DEST_ROOT/.$s.new.$$"
    cp -R "$TMP/staged/$s" "$new"
  done
  for s in "${CHANGED[@]}"; do
    dst="$DEST_ROOT/$s"
    new="$DEST_ROOT/.$s.new.$$"
    backup="$DEST_ROOT/.$s.backup.$$"
    if [ -d "$dst" ]; then
      mv "$dst" "$backup"
    fi
    if ! mv "$new" "$dst"; then
      if [ -d "$backup" ]; then mv "$backup" "$dst"; fi
      exit 1
    fi
    if [ -d "$backup" ]; then rm -rf "$backup"; fi
    echo "[sync] 已更新 $s"
  done
  echo "[sync] 变更如下（请记录完整上游 commit ${UPSTREAM_COMMIT}，审阅后再提交）:"
  git -C "$REPO_ROOT" --no-pager diff --stat -- docs/external-skills/scientific-agent-skills || true
fi

if [ "${1:-}" = "--install" ]; then
  for s in "${SKILLS[@]}"; do
    mkdir -p "$HOME/.agents/skills"
    rm -rf "$HOME/.agents/skills/$s"
    cp -R "$DEST_ROOT/$s" "$HOME/.agents/skills/$s"
    echo "[install] $s → ~/.agents/skills/$s"
  done
fi
