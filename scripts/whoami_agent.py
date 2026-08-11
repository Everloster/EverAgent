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


_WIN_SCAN: tuple[list[str], list[str], bool] | None = None


def _win_scan() -> tuple[list[str], list[str], bool]:
    """Windows 进程扫描：ctypes Toolhelp32 快照（纯 stdlib、毫秒级、无 PowerShell 冷启动抖动）。
    返回 (祖先链小写, 全快照进程名原始大小写, 祖先链是否正常走到根)。
    实测坑（2026-08-09 ecommit 场景）：MSYS2 的 bash 脚本 exec 会弄死中间进程，
    祖先链在两个 bash.exe 后即断（父 PID 已不在快照），此时须回落全快照匹配。"""
    global _WIN_SCAN
    if _WIN_SCAN is not None:
        return _WIN_SCAN
    ancestors: list[str] = []
    all_raw: list[str] = []
    reached_root = False
    try:
        import ctypes

        TH32CS_SNAPPROCESS = 0x00000002
        INVALID_HANDLE = ctypes.c_void_p(-1).value

        class PROCESSENTRY32W(ctypes.Structure):
            _fields_ = [
                ("dwSize", ctypes.c_ulong),
                ("cntUsage", ctypes.c_ulong),
                ("th32ProcessID", ctypes.c_ulong),
                ("th32DefaultHeapID", ctypes.c_size_t),
                ("th32ModuleID", ctypes.c_ulong),
                ("cntThreads", ctypes.c_ulong),
                ("th32ParentProcessID", ctypes.c_ulong),
                ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.c_ulong),
                ("szExeFile", ctypes.c_wchar * 260),
            ]

        k32 = ctypes.windll.kernel32
        snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if snap == INVALID_HANDLE:
            raise OSError("CreateToolhelp32Snapshot failed")
        try:
            entry = PROCESSENTRY32W()
            entry.dwSize = ctypes.sizeof(PROCESSENTRY32W)
            procs: dict[int, tuple[int, str]] = {}
            ok = k32.Process32FirstW(snap, ctypes.byref(entry))
            while ok:
                procs[entry.th32ProcessID] = (entry.th32ParentProcessID, entry.szExeFile)
                ok = k32.Process32NextW(snap, ctypes.byref(entry))
        finally:
            k32.CloseHandle(snap)
        all_raw = [exe for _, exe in procs.values()]
        pid = os.getpid()
        for _ in range(16):
            info = procs.get(pid)
            if not info:
                break  # 父进程已死（MSYS2 exec 截断）→ 链断
            ppid, exe = info
            ancestors.append(exe.lower())
            if ppid <= 0 or ppid == pid or exe.lower() in ("explorer.exe", "services.exe", "sshd.exe", "system"):
                reached_root = True
                break
            pid = ppid
    except Exception as e:
        if os.environ.get("WHOAMI_DEBUG"):
            print(f"[whoami] _win_scan 异常: {e!r}", file=sys.stderr)
    _WIN_SCAN = (ancestors, all_raw, reached_root)
    return _WIN_SCAN


def _proc_has(*names) -> bool:
    """进程链兜底：类 Unix 用 ps 向上爬；Windows 用 Toolhelp32 快照（2026-08-09 补）。
    祖先链被 MSYS2 exec 截断时回落全快照精确匹配 `{name}.exe`（大小写敏感——
    kimi.exe 是 CLI、Kimi.exe 是桌面 App，二者必须区分）。局限：多个 agent CLI
    并存时全快照匹配可能误中，优先靠各 CLI 专有 env / AGENT_ID 显式指定。"""
    if os.name == "nt":
        ancestors, all_raw, reached_root = _win_scan()
        low = [n.lower() for n in names]
        if any(n in a for a in ancestors for n in low):
            return True
        if reached_root:
            return False
        if os.environ.get("WHOAMI_DEBUG"):
            print(f"[whoami] 祖先链截断 {ancestors}，回落全快照匹配 {names}", file=sys.stderr)
        return any(raw == f"{n}.exe" for raw in all_raw for n in names)
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


def _trae_session_model() -> str | None:
    """从当前 TRAE thread 的运行日志读取真实会话模型。

    `~/.trae/traecli.toml` 记录的是静态/下次启动配置，模型在会话内切换后可能仍是旧值。
    TRAE 运行日志则按 thread_id 记录每次请求的 config_name，是当前会话事实源。
    """
    thread_id = (
        os.environ.get("TRAE_THREAD_ID")
        or os.environ.get("TRAECLI_THREAD_ID")
        or os.environ.get("CODEX_THREAD_ID")
    )
    if not thread_id:
        return None

    log_dir = HOME / ".trae" / "cli" / "log"
    try:
        logs = sorted(
            log_dir.glob("traecli*.log"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return None

    for log_path in logs:
        try:
            with log_path.open("rb") as handle:
                handle.seek(0, os.SEEK_END)
                size = handle.tell()
                handle.seek(max(0, size - 8 * 1024 * 1024))
                text = handle.read().decode("utf-8", errors="ignore")
        except OSError:
            continue

        for line in reversed(text.splitlines()):
            if f"thread_id={thread_id}" not in line:
                continue
            match = re.search(r"\bconfig_name=([^\s]+)", line)
            if match:
                return match.group(1)
            match = re.search(r"server reported model ([^\s]+)", line)
            if match:
                return match.group(1)
    return None


def detect_model(cli: str) -> str:
    """按 CLI 读其配置拿模型名。"""
    if cli == "trae":
        session_model = _trae_session_model()
        if session_model:
            return session_model
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
