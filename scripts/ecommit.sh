#!/usr/bin/env bash
# 双身份提交包装（docs/PROTOCOL_COMMON.md §C）：
#   Author    = Everloster（仓库主人，固定，GitHub 显示其头像）
#   Committer = 当前运行的 agent（自动识别 CLI+模型，谁跑就填谁；换 agent/模型无需改配置）
#   Gate      = 提交前验证已暂存报告、索引与 context
# 用法与 git commit 完全相同：
#   scripts/ecommit.sh -m "[{task-type}] {scope}: {描述}"
set -euo pipefail

_D="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 门禁验证的是当前 Git index。-a/--all、--include/--only/--patch 和
# pathspec 会在门禁后让 git commit 构造另一棵树，因此这里只接受元数据选项。
_EXPECT_VALUE=""
for _ARG in "$@"; do
  if [ -n "$_EXPECT_VALUE" ]; then
    _EXPECT_VALUE=""
    continue
  fi
  case "$_ARG" in
    -m|-F|-C|-c|--message|--file|--reuse-message|--reedit-message|--author|--date|--cleanup|--squash|--trailer)
      _EXPECT_VALUE="$_ARG"
      ;;
    -m?*|-F?*|-C?*|-c?*|--message=*|--file=*|--reuse-message=*|--reedit-message=*|--author=*|--date=*|--cleanup=*|--squash=*|--trailer=*)
      ;;
    -q|--quiet|-v|--verbose|-s|--signoff|--no-signoff|-S|--gpg-sign|--gpg-sign=*|--no-gpg-sign|--no-verify|--verify|--allow-empty|--allow-empty-message|--amend|--no-post-rewrite|--no-edit|--reset-author|--dry-run|--short|--branch|--porcelain|--long|-z|--null|--ahead-behind|--no-ahead-behind|--renames|--no-renames|--find-renames|--find-renames=*)
      ;;
    -a|--all|-i|--include|-o|--only|-p|--patch|--interactive|--fixup|--fixup=*|--pathspec-from-file|--pathspec-from-file=*|--pathspec-file-nul|--)
      echo "[ecommit] BLOCKED: $_ARG 会在质量门后改变待提交内容；请先显式 git add。" >&2
      exit 2
      ;;
    -*)
      echo "[ecommit] BLOCKED: 未审计的 git commit 选项 $_ARG。" >&2
      exit 2
      ;;
    *)
      echo "[ecommit] BLOCKED: 不接受 pathspec '$_ARG'；请先显式 git add。" >&2
      exit 2
      ;;
  esac
done
if [ -n "$_EXPECT_VALUE" ]; then
  echo "[ecommit] BLOCKED: $_EXPECT_VALUE 缺少参数值。" >&2
  exit 2
fi

# Author：固定仓库主人（可被已存在的 GIT_AUTHOR_* 覆盖，便于特殊场景）
export GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-Everloster}"
export GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-2820419+Everloster@users.noreply.github.com}"

# Committer：自动识别当前 agent 身份（whoami_agent.py，跨平台 mac/linux/win）。
# 铁律（2026-07-28 用户定）：识别不出身份 = 禁止提交，绝不静默兜底。
_IDENTITY="$(python3 "$_D/whoami_agent.py" --git-ident 2>/dev/null || true)"
IFS=$'\t' read -r _NAME _EMAIL <<< "$_IDENTITY"
if [ -z "${_NAME:-}" ] || [ -z "${_EMAIL:-}" ] || [[ "$_NAME" == *-unknown ]]; then
  echo "[ecommit] BLOCKED: 无法识别当前 agent 身份（name=${_NAME:-空}, email=${_EMAIL:-空}），已阻止提交。" >&2
  echo "  ① 优先：修 scripts/whoami_agent.py，让它覆盖当前 CLI/模型（加检测规则+厂商邮箱）。" >&2
  echo "  ② 应急：与用户确认身份后显式指定，例如：" >&2
  echo "     AGENT_ID=<cli>-<model> AGENT_EMAIL=<厂商noreply> scripts/ecommit.sh -m \"...\"" >&2
  exit 1
fi
export GIT_COMMITTER_NAME="$_NAME"
export GIT_COMMITTER_EMAIL="$_EMAIL"
# 只对本次进程覆盖 git config，使外部 hook 看到同一身份；不修改仓库配置。
_CONFIG_COUNT="${GIT_CONFIG_COUNT:-0}"
export "GIT_CONFIG_KEY_${_CONFIG_COUNT}=user.name"
export "GIT_CONFIG_VALUE_${_CONFIG_COUNT}=$_NAME"
_CONFIG_COUNT=$((_CONFIG_COUNT + 1))
export "GIT_CONFIG_KEY_${_CONFIG_COUNT}=user.email"
export "GIT_CONFIG_VALUE_${_CONFIG_COUNT}=$_EMAIL"
export GIT_CONFIG_COUNT=$((_CONFIG_COUNT + 1))

# 所有 Harness 共用同一份确定性质量门。hook 可能由外部环境管理，故 ecommit 主动执行。
_INDEX_BEFORE="$(git write-tree)"
python3 "$_D/precommit_quality.py"
_INDEX_AFTER="$(git write-tree)"
if [ "$_INDEX_BEFORE" != "$_INDEX_AFTER" ]; then
  echo "[ecommit] BLOCKED: 质量门运行期间 Git index 已变化，请重新检查并重试。" >&2
  exit 3
fi
export EVERAGENT_QUALITY_GATE_DONE=1

exec git commit "$@"
