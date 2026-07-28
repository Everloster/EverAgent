#!/usr/bin/env bash
# whoami-agent —— 自动识别"当前正在运行的 agent 身份"（CLI + 模型），用作 git Committer。
# 输出一行：<cli>-<model>（如 trae-openrouter-3o / codex-gpt-5.5 / claude-code-<model>）。
# 设计：Author 永远是仓库主人 Everloster（固定，由 ecommit 注入）；Committer 是"谁在跑"，本脚本自动定。
# 谁跑就填谁：换 CLI/模型无需改配置。判据是"真实进程链"（最可靠），不是环境变量是否存在
# （如 CODEX_HOME 可能被编排层全局设置，存在≠正跑在 codex 里）。探测不到给安全兜底，绝不中断提交。
set -uo pipefail

slug() { echo "$1" | tr '[:upper:] ' '[:lower:]-' | tr -cd 'a-z0-9._-'; }

# 从 toml 取某 key 的值（去引号）
toml_get() { grep -m1 "^$2[[:space:]]*=" "$1" 2>/dev/null | sed -E "s/^$2[[:space:]]*=[[:space:]]*//; s/^\"//; s/\"$//; s/[[:space:]]*#.*//"; }

# 返回进程链里第一个匹配到的已知 CLI 名（trae/codex/claude/...）
detect_cli() {
  local pid=$$ comm
  for _ in $(seq 1 8); do
    comm=$(ps -o comm= -p "$pid" 2>/dev/null | xargs basename 2>/dev/null)
    case "$comm" in
      coco|traecli|trae) echo trae; return;;
      codex) echo codex; return;;
      claude) echo claude; return;;
    esac
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' '); { [ -z "$pid" ] || [ "$pid" = 0 ]; } && break
  done
  echo ""
}

detect() {
  local cli; cli=$(detect_cli)
  case "$cli" in
    trae)
      local toml="$HOME/.trae/traecli.toml" prov model
      prov=$(toml_get "$toml" model_provider); model=$(toml_get "$toml" model)
      echo "${prov:-trae}-${model:-unknown}"; return;;
    codex)
      local m; m=$(toml_get "${CODEX_HOME:-$HOME/.codex}/config.toml" model)
      echo "codex-${m:-unknown}"; return;;
    claude)
      echo "claude-code-${CLAUDE_MODEL:-unknown}"; return;;
  esac
  # 通用 env 兜底：任意 CLI 可显式声明 AGENT_ID
  [ -n "${AGENT_ID:-}" ] && { echo "$AGENT_ID"; return; }
  # 最终兜底：进程名（保证提交不中断）
  echo "$(ps -o comm= -p "${PPID:-$$}" 2>/dev/null | xargs basename 2>/dev/null || echo agent)-unknown"
}

slug "$(detect)"
