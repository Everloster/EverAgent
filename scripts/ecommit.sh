#!/usr/bin/env bash
# 双身份提交包装（docs/PROTOCOL_COMMON.md §C）：
#   Author    = Everloster（仓库主人，固定，GitHub 显示其头像）
#   Committer = 当前运行的 agent（自动识别 CLI+模型，谁跑就填谁；换 agent/模型无需改配置）
# 用法与 git commit 完全相同：
#   scripts/ecommit.sh -m "[{task-type}] {scope}: {描述}"
set -euo pipefail

_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Author：固定仓库主人（可被已存在的 GIT_AUTHOR_* 覆盖，便于特殊场景）
export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-Everloster}"
export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-2820419+Everloster@users.noreply.github.com}"

# Committer：自动识别当前 agent 身份（whoami-agent.sh）。失败则回退到 git config，绝不中断提交。
_AGENT="$("$_D/whoami-agent.sh" 2>/dev/null || true)"
if [ -n "${_AGENT:-}" ]; then
  export GIT_COMMITTER_NAME="$_AGENT"
  export GIT_COMMITTER_EMAIL="noreply@trae.com"
  # 同步 git config，使 pre-commit hook（读 user.name/email）与实际 committer 一致
  git config user.name "$_AGENT"
  git config user.email "noreply@trae.com"
fi

exec git commit "$@"
