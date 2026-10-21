"""Agent harness selection; reusable core with no repository policy."""
from __future__ import annotations
import os
import re
from . import models, processes

# ── CLI 检测表：环境变量信号（借鉴 gh cli / detect-coding-agent，社区权威）──
# 每项：(cli_id, 厂商邮箱, 判定函数)。顺序=优先级（具体的在前）。
def _has(*keys):  return any(os.environ.get(k) for k in keys)
def _eq(key, val): return os.environ.get(key) == val

# CLI → 厂商命名空间署名地址（项目约定）
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
    "kimi-desktop": "noreply@moonshot.ai",
    "minimax-code": "noreply@minimaxi.com",
    "qoderclicn":  "noreply@qoder.com.cn",
    "zcode":       "noreply@z.ai",
    "pi":          "noreply@pi.dev",
}
FALLBACK_EMAIL = "noreply@everloster.com"

# 检测规则（顺序即优先级）
CLI_RULES = [
    ("cowork",      lambda: _has("CLAUDE_CODE_IS_COWORK")),
    ("amp",         lambda: _has("AMP_CURRENT_THREAD_ID") or _eq("AGENT", "amp")),
    # TRAE / coco：先于 codex 判——本机 CODEX_HOME 是 Orca 编排层全局设的干扰项，
    # 若 TRAE 会话信号在场则必是 trae（社区教训：勿用会被别的工具设置的变量判 CLI）。
    ("trae",        lambda: _has("TRAECLI_SESSION_INBOX")),
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
    # claude-code：CLAUDECODE/CLAUDE_CODE 为继承型 env（claude 的 shell 工具子进程均带），
    # 放中后段让位给可能嵌套运行的其他 CLI 专有信号（同 pi/kimi-cli 让位原则）。
    # 2026-08-24 修：5c4be6f 加 pi 时误删此行，致 cc-connect daemon 场景识别为 zsh-unknown。
    ("claude-code", lambda: _has("CLAUDECODE", "CLAUDE_CODE")),
    ("goose",       lambda: _has("GOOSE_PROVIDER")),
    # qoderclicn（QoderCN CLI，CN 渠道）：专有环境变量 QODERCN_CLI，进程链 comm=qoderclicn 兜底。
    ("qoderclicn",  lambda: _has("QODERCN_CLI")),
    # zcode（ZCode 桌面 App 内嵌 CLI，厂商 z.ai）：专有 ZCODE_* 环境变量为主，
    # 进程链 comm=zcode-cli / zcode-host-* 兜底（首字母大写的 ZCode 主进程不参与匹配）。
    ("zcode",       lambda: _has("ZCODE_APP_VERSION", "ZCODE_ENV", "ZCODE_PROCESS_LABEL")),
    # kimi-cli（Kimi Code CLI）：最近祖先的精确匹配见 PROCESS_RULES；环境仅作后续依据。
    # 注意命名：kimi = 桌面 App，kimi-cli = 命令行工具，二者身份须区分（2026-07-28 用户订正）。
    ("kimi-cli",    lambda: _has("KIMI_CLI", "KIMI_CODE_CLI")),
    # minimax-code（MiniMax Code 桌面 App，Electron）：进程链 comm=MiniMax Code Helper。
    ("minimax-code", lambda: _has("MINIMAX_CODE")),
    # pi（pi-coding-agent，OSS harness，官网 pi.dev）：会话环境自带 PI_CODING_AGENT=true
    # 和 PI_SESSION_ID/PI_MODEL；进程只精确匹配，避免 "pi" 误中 pip 等程序。
    # 放最后：PI_* 是环境继承型信号（pi 的 bash 工具会传给所有子进程），若别的
    # CLI 嵌套运行在 pi 内，应让它们自己的专有信号先命中（同 trae 嵌套让位原则）。
    ("pi",          lambda: _has("PI_CODING_AGENT", "PI_SESSION_ID")),
]

# 仅匹配调用方祖先链，最近的已知 CLI 优先；其他终端里运行的 Agent 不是身份依据。
PROCESS_RULES = (
    ("codex", ("codex",)),
    ("claude-code", ("claude", "claude-code")),
    ("trae", ("coco", "traecli")),
    ("qoderclicn", ("qoderclicn",)),
    ("zcode", ("zcode-cli", "zcode-host", "ZCode")),
    ("kimi-cli", ("kimi",)),
    ("kimi-desktop", ("Kimi",)),
    ("minimax-code", ("MiniMax Code",)),
    ("pi", ("pi", "pi-coding-agent")),
)

def _detect_cli() -> tuple[str | None, str]:
    for row in processes.process_chain():
        for cli, names in PROCESS_RULES:
            if processes.matches_row(row, names):
                if cli == "claude-code" and _has("CLAUDE_CODE_IS_COWORK"):
                    cli = "cowork"
                return cli, "process-ancestry"
    for cli, rule in CLI_RULES:
        if rule():
            return cli, "runtime-environment"
    return None, "unresolved"


def inspect_identity(*, observation: dict | None = None) -> dict:
    # Each inspection rechecks ancestry; a gate must not reuse a dead caller.
    processes.reset_cache()
    # Legacy identity overrides remain diagnostic; env is not proof of user confirmation.
    if os.environ.get("AGENT_ID"):
        name = os.environ["AGENT_ID"]
        email = os.environ.get("AGENT_EMAIL", FALLBACK_EMAIL)
        valid = bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,160}", name)
                     and re.fullmatch(r"[^\s<>@]+@[^\s<>@]+", email))
        return {"schema_version": 2, "name": name if valid else "agent-unknown",
                "email": email if valid else FALLBACK_EMAIL, "cli": None,
                "cli_source": "explicit-override", "model": "unknown",
                "model_source": "explicit-identity", "model_confidence": "declared",
                "current_model_confirmed": False,
                "harness_resolved": False, "user_model_declared": False, "commit_ready": False,
                "resolved": valid and not name.endswith("-unknown")}

    cli, cli_source = _detect_cli()

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
        return {"schema_version": 2, "name": f"{base}-unknown", "email": FALLBACK_EMAIL,
                "cli": None, "cli_source": cli_source, "model": "unknown",
                "model_source": "unresolved", "model_confidence": "unknown",
                "current_model_confirmed": False, "resolved": False, "harness_resolved": False,
                "user_model_declared": False, "commit_ready": False}

    evidence = models.model_evidence(cli, observation=observation)
    model = evidence["model"]
    name = f"{cli}-{model}"
    # 清洗成 git 身份安全字符
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-").lower()
    email = VENDOR_EMAIL.get(cli, FALLBACK_EMAIL)
    return {"schema_version": 2, "name": name, "email": email,
            "cli": cli, "cli_source": cli_source, "model": model,
            "model_source": evidence["source"], "model_confidence": evidence["confidence"],
            "current_model_confirmed": evidence["current_model_confirmed"],
            "user_model_declared": evidence["user_model_declared"],
            "harness_resolved": True, "resolved": not name.endswith("-unknown"),
            "commit_ready": evidence["current_model_confirmed"] or evidence["user_model_declared"],
            **{key: evidence[key] for key in ("declaration", "scope_ref", "observed_at", "requested_model",
                                           "configured_model", "observed_model", "user_declared_model", "observation_ref") if key in evidence}}


def detect() -> tuple[str, str]:
    identity = inspect_identity()
    return identity["name"], identity["email"]
