#!/usr/bin/env bash
# 双身份提交包装（docs/PROTOCOL_COMMON.md §C）：
#   Author    = Everloster（仓库主人，GitHub 显示其头像）
#   Committer = 当前 Agent（git config user.name/email，pre-commit hook 校验）
# 用法与 git commit 完全相同：
#   scripts/ecommit.sh -m "[{task-type}] {scope}: {描述}"
set -euo pipefail

export GIT_AUTHOR_NAME="Everloster"
export GIT_AUTHOR_EMAIL="2820419+Everloster@users.noreply.github.com"

exec git commit "$@"
