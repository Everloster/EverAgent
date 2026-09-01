#!/usr/bin/env bash
# 同步 docs/external-skills/scientific-agent-skills 下的两个 vendor 技能
# 用法:
#   scripts/sync-external-skills.sh           拉上游 → 覆盖 → git diff 展示变化（不自动提交）
#   scripts/sync-external-skills.sh --install 追加: 把仓内副本投射到 ~/.agents/skills/（本机 Skill 工具可原生调用）
set -euo pipefail

REPO_URL="https://github.com/K-Dense-AI/scientific-agent-skills"
SKILLS=(hypothesis-generation scientific-writing)
DEST_ROOT="$(cd "$(dirname "$0")/.." && pwd)/docs/external-skills/scientific-agent-skills"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "[sync] sparse-clone 上游 $REPO_URL ..."
git clone --quiet --depth 1 --filter=blob:none --sparse "$REPO_URL" "$TMP" || { echo "[sync] clone 失败（网络?）"; exit 1; }
git -C "$TMP" sparse-checkout set skills >/dev/null 2>&1

UPSTREAM_COMMIT=$(git -C "$TMP" rev-parse --short HEAD)
echo "[sync] 上游 HEAD: $UPSTREAM_COMMIT ($(git -C "$TMP" log -1 --format=%cd --date=short))"

CHANGED=0
for s in "${SKILLS[@]}"; do
  src="$TMP/skills/$s"; dst="$DEST_ROOT/$s"
  if [ ! -d "$src" ]; then echo "[sync] ⚠️ 上游已无 $s（目录改名?）——跳过，请人工核对"; continue; fi
  if [ -d "$dst" ] && ! diff -qr "$src" "$dst" >/dev/null 2>&1; then
    rm -rf "$dst"; cp -R "$src" "$dst"; echo "[sync] ✅ $s 有更新，已覆盖"; CHANGED=1
  else
    echo "[sync] • $s 无变化"
  fi
done

if [ "$CHANGED" = 1 ]; then
  echo "[sync] 变更如下（确认后自行 ecommit，并更新 UPSTREAM.md 同步记录表）:"
  git -C "$(dirname "$DEST_ROOT")" --no-pager diff --stat -- docs/external-skills || true
else
  echo "[sync] 与上游一致，无需提交。"
fi

if [ "${1:-}" = "--install" ]; then
  for s in "${SKILLS[@]}"; do
    mkdir -p "$HOME/.agents/skills"
    rm -rf "$HOME/.agents/skills/$s"; cp -R "$DEST_ROOT/$s" "$HOME/.agents/skills/$s"
    echo "[install] ✅ $s → ~/.agents/skills/$s"
  done
fi
