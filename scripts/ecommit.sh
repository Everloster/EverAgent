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

# Committer：自动识别当前 agent 身份（whoami_agent.py，跨平台 mac/linux/win）。
# 铁律（2026-07-28 用户定）：识别不出身份 = 禁止提交，绝不静默兜底。
_NAME="$(python3 "$_D/whoami_agent.py" --name 2>/dev/null || true)"
_EMAIL="$(python3 "$_D/whoami_agent.py" --email 2>/dev/null || true)"
if [ -z "${_NAME:-}" ] || [ -z "${_EMAIL:-}" ] || [[ "$_NAME" == *-unknown ]]; then
  echo "[ecommit] BLOCKED: 无法识别当前 agent 身份（name=${_NAME:-空}, email=${_EMAIL:-空}），已阻止提交。" >&2
  echo "  ① 优先：修 scripts/whoami_agent.py，让它覆盖当前 CLI/模型（加检测规则+厂商邮箱）。" >&2
  echo "  ② 应急：与用户确认身份后显式指定，例如：" >&2
  echo "     AGENT_ID=<cli>-<model> AGENT_EMAIL=<厂商noreply> scripts/ecommit.sh -m \"...\"" >&2
  exit 1
fi
export GIT_COMMITTER_NAME="$_NAME"
export GIT_COMMITTER_EMAIL="$_EMAIL"
# 同步 git config，使 pre-commit hook（读 user.name/email）与实际 committer 一致
git config user.name "$_NAME"
git config user.email "$_EMAIL"

exec git commit "$@"
