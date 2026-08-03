#!/usr/bin/env python3
"""whoami-agent —— 识别"当前运行的 agent 身份"，用作 git Committer（跨平台：mac/linux/windows）。

两个目标（用户 2026-07-28 定）：
  1) 身份名 = <cli/工具/ide>-<模型>，如 trae-openrouter-3o / codex-gpt-5.5 / claude-code-sonnet-4.6
  2) 邮箱   = 厂商官方 noreply（claude→anthropic、codex/chatgpt→openai、trae→trae.com …），识别不出兜底 noreply@everloster.com

检测策略：优先环境变量（社区最佳实践，见 github.com/cli/cli internal/agents/detect.go
与 crates.io/detect-coding-agent），跨平台且无需 ps；再读该 CLI 配置补模型名。

用法：
  whoami_agent.py            # 输出两行：name=<...> / email=<...>
  whoami_agent.py --name     # 只输出 name
  whoami_agent.py --email    # 只输出 email
"""
from __future__ import annotations
import os, re, sys, configparser
from pathlib import Path

HOME = Path.home()

# ── CLI 检测表：环境变量信号（借鉴 gh cli / detect-coding-agent，社区权威）──
# 每项：(cli_id, 厂商邮箱, 判定函数)。顺序=优先级（具体的在前）。
def _has(*keys):  return any(os.environ.get(k) for k in keys)
def _eq(key, val): return os.environ.get(key) == val

# CLI → 厂商官方 noreply 邮箱
VENDOR_EMAIL = {
    "claude-code": "noreply@anthropic.com",
    "cowork":      "noreply@anthropic.com",
    "codex":       "noreply@openai.com",
    "chatgpt":     "noreply@openai.com",
    "copilot-cli": "noreply@github.com",
    "copilot":     "noreply@github.com",
    "gemini-cli":  "noreply@google.com",
    "cursor":      "noreply@cursor.com",
    "cursor-cli":  "noreply@cursor.com",
    "trae":        "noreply@trae.com",
    "goose":       "noreply@block.xyz",
    "aider":       "noreply@aider.chat",
    "opencode":    "noreply@opencode.ai",
    "windsurf":    "noreply@codeium.com",
    "qwen-code":   "noreply@alibabacloud.com",
    "amp":         "noreply@sourcegraph.com",
    "kimi-cli":    "noreply@moonshot.ai",
    "minimax-code": "noreply@minimaxi.com",
    "qoderclicn":  "noreply@qoder.com.cn",
}
FALLBACK_EMAIL = "noreply@everloster.com"

# 检测规则（顺序即优先级）
CLI_RULES = [
    ("cowork",      lambda: _has("CLAUDE_CODE_IS_COWORK")),
    ("amp",         lambda: _has("AMP_CURRENT_THREAD_ID") or _eq("AGENT", "amp")),
    # TRAE / coco：先于 codex 判——本机 CODEX_HOME 是 Orca 编排层全局设的干扰项，
    # 若 TRAE 会话信号在场则必是 trae（社区教训：勿用会被别的工具设置的变量判 CLI）。
    ("trae",        lambda: _has("TRAECLI_SESSION_INBOX") or _proc_has("coco", "traecli")),
    # codex：只认 codex 运行时专有变量，不含 CODEX_HOME（它可能被编排层全局设置）。
    ("codex",       lambda: _has("CODEX_THREAD_ID", "CODEX_SANDBOX", "CODEX_CI")),
    ("gemini-cli",  lambda: _has("GEMINI_CLI")),
    ("copilot-cli", lambda: _has("COPILOT_AGENT_SESSION_ID", "GH_COPILOT_CLI")),
    ("cursor-cli",  lambda: _has("CURSOR_AGENT") or _eq("CURSOR_EXTENSION_HOST_ROLE", "agent-exec")),
    ("cursor",      lambda: _has("CURSOR_TRACE_ID")),
    ("opencode",    lambda: _has("OPENCODE")),
    ("windsurf",    lambda: _has("CODEIUM_EDITOR_APP_ROOT")),
    ("qwen-code",   lambda: _has("QWEN_CODE")),
    ("aider",       lambda: _has("AIDER_API_KEY")),
    ("claude-code", lambda: _has("CLAUDECODE", "CLAUDE_CODE")),
    ("goose",       lambda: _has("GOOSE_PROVIDER")),
    # qoderclicn（QoderCN CLI，CN 渠道）：专有环境变量 QODERCN_CLI，进程链 comm=qoderclicn 兜底。
    ("qoderclicn",  lambda: _has("QODERCN_CLI") or _proc_has("qoderclicn")),
    # kimi-cli（Kimi Code CLI）：无专有环境变量，靠进程链判（comm=kimi）。放最后——
    # 进程链判定优先级最低，嵌套场景下让 env 型 CLI 先匹配。
    # 注意命名：kimi = 桌面 App，kimi-cli = 命令行工具，二者身份须区分（2026-07-28 用户订正）。
    ("kimi-cli",    lambda: _has("KIMI_CLI", "KIMI_CODE_CLI") or _proc_has("kimi")),
    # minimax-code（MiniMax Code 桌面 App，Electron）：进程链 comm=MiniMax Code Helper。
    ("minimax-code", lambda: _has("MINIMAX_CODE") or _proc_has("MiniMax Code")),
]


def _proc_has(*names) -> bool:
    """进程链兜底（仅类 Unix 有 ps；Windows 上直接返回 False，靠 env 判定）。"""
    if os.name == "nt":
        return False
    try:
        import subprocess
        pid = os.getpid()
        for _ in range(8):
            out = subprocess.run(["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=3).stdout.strip()
            if not out:
                break
            parts = out.split(None, 1)
            if len(parts) < 2:
                break
            ppid, comm = parts[0], parts[1]
            base = os.path.basename(comm)
            if any(n in base for n in names):
                return True
            pid = int(ppid) if ppid.isdigit() else 0
            if pid <= 1:
                break
    except Exception:
        pass
    return False


def _toml_get(path: Path, key: str) -> str | None:
    """极简 toml 取顶层 key（不引三方库，跨平台）。"""
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(rf'^\s*{re.escape(key)}\s*=\s*"?([^"#\n]+)"?', line)
        if m:
            return m.group(1).strip()
    return None


def _yaml_get(path: Path, key: str) -> str | None:
    """极简 yaml 取顶层 key（`key: value` 形式，不引三方库）。"""
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(rf'^\s*{re.escape(key)}\s*:\s*"?([^"#\n]+)"?', line)
        if m:
            return m.group(1).strip()
    return None


def detect_model(cli: str) -> str:
    """按 CLI 读其配置拿模型名。"""
    if cli == "trae":
        t = HOME / ".trae" / "traecli.toml"
        prov = _toml_get(t, "model_provider") or ""
        model = _toml_get(t, "model") or ""
        # trae 已单列厂商，model 里带 provider 前缀反而重复；只取 model
        return model or "unknown"
    if cli == "codex":
        home = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))
        return _toml_get(home / "config.toml", "model") or os.environ.get("CODEX_MODEL", "unknown")
    if cli in ("claude-code", "cowork"):
        return os.environ.get("ANTHROPIC_MODEL") or os.environ.get("CLAUDE_MODEL", "unknown")
    if cli == "gemini-cli":
        return os.environ.get("GEMINI_MODEL", "unknown")
    if cli in ("cursor", "cursor-cli"):
        return os.environ.get("CURSOR_MODEL", "unknown")
    if cli == "kimi-cli":
        # ~/.kimi-code/config.toml 的 default_model 形如 "kimi-code/k3"，取 / 后段
        raw = _toml_get(HOME / ".kimi-code" / "config.toml", "default_model") or ""
        return raw.split("/")[-1] if raw else os.environ.get("KIMI_MODEL", "unknown")
    if cli == "minimax-code":
        # ~/.minimax/config.yaml 的 defaultModel 形如 "minimax/MiniMax-M3"，取 / 后段并去 MiniMax- 前缀
        raw = _yaml_get(HOME / ".minimax" / "config.yaml", "defaultModel") or ""
        m = re.sub(r"^minimax-", "", raw.split("/")[-1], flags=re.I)
        return m or os.environ.get("MINIMAX_MODEL", "unknown")
    if cli == "qoderclicn":
        # ~/.qoder-cn/settings.json 的 model.name 形如 "qmodel_38max"（厂商内部模型键，非显示名）
        try:
            import json
            cfg = json.loads((HOME / ".qoder-cn" / "settings.json").read_text(encoding="utf-8"))
            name = cfg.get("model", {}).get("name") or ""
        except Exception:
            name = ""
        return name or os.environ.get("QODERCN_MODEL", "unknown")
    # 通用兜底
    return os.environ.get("AGENT_MODEL", "unknown")


def detect() -> tuple[str, str]:
    # 显式覆盖：任意 CLI 可设 AGENT_ID / AGENT_EMAIL 直接指定
    if os.environ.get("AGENT_ID"):
        return os.environ["AGENT_ID"], os.environ.get("AGENT_EMAIL", FALLBACK_EMAIL)

    cli = None
    for cid, rule in CLI_RULES:
        try:
            if rule():
                cli = cid
                break
        except Exception:
            continue

    if not cli:
        # 完全识别不出：进程名 + 兜底邮箱（ecommit 会拦 *-unknown，绝不静默提交）
        base = "agent"
        if os.name != "nt":
            try:
                import subprocess
                base = os.path.basename(subprocess.run(
                    ["ps", "-o", "comm=", "-p", str(os.getppid())],
                    capture_output=True, text=True, timeout=3).stdout.strip()) or "agent"
            except Exception:
                pass
        base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-").lower()
        return f"{base}-unknown", FALLBACK_EMAIL

    model = detect_model(cli)
    name = f"{cli}-{model}"
    # 清洗成 git 身份安全字符
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-").lower()
    email = VENDOR_EMAIL.get(cli, FALLBACK_EMAIL)
    return name, email


def main() -> int:
    name, email = detect()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--name":
        print(name)
    elif arg == "--email":
        print(email)
    else:
        print(f"name={name}")
        print(f"email={email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
