#!/usr/bin/env python3
"""whoami-agent —— 识别"当前运行的 agent 身份"，用作 git Committer（跨平台：mac/linux/windows）。

两个目标（用户 2026-07-28 定）：
  1) 身份名 = <cli/工具/ide>-<模型>，如 trae-openrouter-3o / codex-gpt-5.5 / claude-code-sonnet-4.6
  2) 邮箱   = 厂商官方 noreply（claude→anthropic、codex/chatgpt→openai、trae→trae.com …），识别不出兜底 noreply@everloster.com

检测策略：已知 CLI 的最近祖先优先，再用运行时环境；只读该 CLI 的模型字段。
配置默认模型与未绑定当前会话的近期记录只作提示，不证明当前会话模型。

用法：
  whoami_agent.py            # 输出两行：name=<...> / email=<...>
  whoami_agent.py --name     # 只输出 name
  whoami_agent.py --email    # 只输出 email
  whoami_agent.py --json     # 身份、来源与可信度；配置默认模型不是会话证明
  whoami_agent.py --git-ident # 单次检测，输出 name<TAB>email，供提交包装消费
"""
from __future__ import annotations
import argparse, json, os, re, sys
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
    ("zcode", ("zcode-cli", "zcode-host")),
    ("kimi-cli", ("kimi",)),
    ("minimax-code", ("MiniMax Code",)),
    ("pi", ("pi", "pi-coding-agent")),
)
_ANCESTORS: list[str] | None = None


_WIN_SCAN: tuple[list[str], list[str], bool] | None = None


def _win_scan() -> tuple[list[str], list[str], bool]:
    """Windows 进程扫描：ctypes Toolhelp32 快照（纯 stdlib、毫秒级、无 PowerShell 冷启动抖动）。
    返回 (祖先链原始名称, 空的兼容字段, 祖先链是否正常走到根)。
    MSYS2 exec 可能使祖先链截断；此时不把其他进程当成当前 Agent。"""
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
        pid = os.getpid()
        for _ in range(16):
            info = procs.get(pid)
            if not info:
                break  # 父进程已死（MSYS2 exec 截断）→ 链断
            ppid, exe = info
            ancestors.append(exe)
            if ppid <= 0 or ppid == pid or exe.lower() in ("explorer.exe", "services.exe", "sshd.exe", "system"):
                reached_root = True
                break
            pid = ppid
    except Exception as e:
        if os.environ.get("WHOAMI_DEBUG"):
            print(f"[whoami] _win_scan 异常: {e!r}", file=sys.stderr)
    _WIN_SCAN = (ancestors, all_raw, reached_root)
    return _WIN_SCAN


def _process_ancestors() -> list[str]:
    """单次、有界的祖先链；Windows 断链时保持未知，不匹配全机其他进程。"""
    global _ANCESTORS
    if _ANCESTORS is not None:
        return _ANCESTORS
    if os.name == "nt":
        _ANCESTORS = _win_scan()[0]
        return _ANCESTORS
    ancestors = []
    try:
        import subprocess
        pid = os.getpid()
        seen = set()
        for _ in range(16):
            if pid in seen:
                break
            seen.add(pid)
            out = subprocess.run(["ps", "-o", "ppid=,comm=", "-p", str(pid)],
                                 capture_output=True, text=True, timeout=1).stdout.strip()
            if not out:
                break
            parts = out.split(None, 1)
            if len(parts) < 2:
                break
            ppid, comm = parts[0], parts[1]
            ancestors.append(os.path.basename(comm))
            pid = int(ppid) if ppid.isdigit() else 0
            if pid <= 1:
                break
    except Exception:
        pass
    _ANCESTORS = ancestors
    return ancestors


def _matches_process(base: str, names: tuple[str, ...]) -> bool:
    if os.name == "nt":
        if base.lower().endswith(".exe"):
            base = base[:-4]
        return any(base == name if name == "kimi" else base.lower() == name.lower() for name in names)
    return any(base == name or
               (name == "zcode-host" and base.startswith("zcode-host-")) or
               (name == "MiniMax Code" and base.startswith("MiniMax Code Helper"))
               for name in names)


def _proc_has(*names) -> bool:
    return any(_matches_process(base, names) for base in _process_ancestors())


def _detect_cli() -> tuple[str | None, str]:
    for base in _process_ancestors():
        for cli, names in PROCESS_RULES:
            if _matches_process(base, names):
                if cli == "claude-code" and _has("CLAUDE_CODE_IS_COWORK"):
                    cli = "cowork"
                return cli, "process-ancestry"
    for cli, rule in CLI_RULES:
        if rule():
            return cli, "runtime-environment"
    return None, "unresolved"


def _toml_get(path: Path, key: str) -> str | None:
    """极简 toml 取顶层 key（不引三方库，跨平台）。"""
    if not path.is_file() or path.stat().st_size > 1024 * 1024:
        return None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.lstrip().startswith("["):
            break
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

    for log_path in logs[:4]:
        try:
            with log_path.open("rb") as handle:
                handle.seek(0, os.SEEK_END)
                size = handle.tell()
                handle.seek(max(0, size - 1024 * 1024))
                text = handle.read(1024 * 1024).decode("utf-8", errors="ignore")
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


def _zcode_session_model() -> str | None:
    """从 ZCode CLI 运行日志读取真实会话模型。

    `~/.zcode/v2/setting.json` 只存套餐键（modelProviderFamilySelectedKeys，如
    coding-plan:builtin:bigmodel-start-plan），不含模型显示名；而
    `~/.zcode/cli/log/zcode-YYYY-MM-DD.jsonl` 按天记录请求，含
    `<plan>/<Model>`（如 bigmodel-start-plan/GLM-5.3），是当前会话事实源。
    取最新日志里最后一次出现的模型名。
    """
    log_dir = HOME / ".zcode" / "cli" / "log"
    try:
        logs = sorted(
            log_dir.glob("zcode-*.jsonl"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
    except OSError:
        return None

    for log_path in logs[:4]:
        try:
            with log_path.open("rb") as handle:
                handle.seek(0, os.SEEK_END)
                size = handle.tell()
                handle.seek(max(0, size - 1024 * 1024))
                text = handle.read(1024 * 1024).decode("utf-8", errors="ignore")
        except OSError:
            continue

        # 优先 <plan>/<Model> 组合（多套餐家族并存时最精确），再退裸模型名
        for pat in (r"[a-z0-9-]+-plan/(GLM[-.0-9]+)", r"\b(GLM[-.0-9]+)\b"):
            hits = re.findall(pat, text)
            if hits:
                return hits[-1]
    return None


def _opencode_session_model() -> str | None:
    """从 opencode 本地 SQLite（~/.local/share/opencode/opencode.db）读当前会话模型。

    opencode 不在配置文件里存全局模型（~/.config/opencode/opencode.json 无 model 键，
    模型是会话级选择），每条 assistant 消息把 providerID/modelID/path.cwd 存进 message
    表（JSON 文本列）。只取 cwd 与当前目录一致的模型提示，不读其他目录的消息。
    同目录可能有多个会话，因此它不是当前会话证明。只读模式打开，任何异常返回 None
    让上层落 unknown（ecommit 拦 *-unknown，绝不静默猜）。
    """
    db = HOME / ".local" / "share" / "opencode" / "opencode.db"
    if not db.is_file():
        return None
    try:
        import json as _json
        import sqlite3
        cwd = os.getcwd()
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2)
        try:
            rows = con.execute(
                "SELECT json_extract(data,'$.modelID') FROM message "
                "WHERE json_extract(data,'$.role')='assistant' "
                "AND json_extract(data,'$.path.cwd')=? "
                "ORDER BY time_created DESC LIMIT 1", (cwd,)
            ).fetchall()
        finally:
            con.close()
        return rows[0][0] if rows and isinstance(rows[0][0], str) else None
    except Exception:
        return None


def model_evidence(cli: str) -> dict:
    """会话环境优先；静态配置与近期日志明确标为提示。只返回模型字段。"""
    def found(model, source, confidence):
        if (not isinstance(model, str) or model.lower() == "unknown"
                or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9:./_-]{0,127}", model)):
            model = None
        return {"model": model or "unknown", "source": source,
                "confidence": confidence if model else "unknown",
                "current_model_confirmed": bool(model) and confidence in {
                    "runtime-environment", "session-bound"}}
    env_keys = {
        "opencode": ("OPENCODE_MODEL",), "trae": ("TRAE_MODEL",),
        "codex": ("CODEX_MODEL",),
        "claude-code": ("ANTHROPIC_MODEL", "CLAUDE_MODEL"),
        "cowork": ("ANTHROPIC_MODEL", "CLAUDE_MODEL"),
        "gemini-cli": ("GEMINI_MODEL",), "cursor": ("CURSOR_MODEL",),
        "cursor-cli": ("CURSOR_MODEL",), "pi": ("PI_MODEL",),
        "zcode": ("ZCODE_MODEL",), "kimi-cli": ("KIMI_MODEL",),
        "minimax-code": ("MINIMAX_MODEL",), "qoderclicn": ("QODERCN_MODEL",),
    }
    for key in (*env_keys.get(cli, ()), "AGENT_MODEL"):
        if os.environ.get(key):
            return found(os.environ[key], "env:" + key, "runtime-environment")
    if cli == "opencode":
        return found(_opencode_session_model(), "workspace-message-model", "workspace-hint")
    if cli == "trae":
        session_model = _trae_session_model()
        if session_model:
            return found(session_model, "thread-matched-runtime-log", "session-bound")
        t = HOME / ".trae" / "traecli.toml"
        prov = _toml_get(t, "model_provider") or ""
        model = _toml_get(t, "model") or ""
        # trae 已单列厂商，model 里带 provider 前缀反而重复；只取 model
        return found(model, "config-default", "configured")
    if cli == "codex":
        home = Path(os.environ.get("CODEX_HOME", HOME / ".codex"))
        return found(_toml_get(home / "config.toml", "model"), "config-default", "configured")
    if cli in ("claude-code", "cowork"):
        return found(None, "runtime-environment", "unknown")
    if cli == "gemini-cli":
        return found(None, "runtime-environment", "unknown")
    if cli in ("cursor", "cursor-cli"):
        return found(None, "runtime-environment", "unknown")
    if cli == "pi":
        # pi 会话环境直接携带当前模型（PI_MODEL，如 glm-5.3），harness 暴露的会话事实源
        return found(None, "runtime-environment", "unknown")
    if cli == "zcode":
        # env 可显式覆盖；默认读当日会话日志的真实模型（如 GLM-5.3）
        return found(_zcode_session_model(), "recent-runtime-log", "recent-log-hint")
    if cli == "kimi-cli":
        # ~/.kimi-code/config.toml 的 default_model 形如 "kimi-code/k3"，取 / 后段
        raw = _toml_get(HOME / ".kimi-code" / "config.toml", "default_model") or ""
        return found(raw.split("/")[-1] if raw else None, "config-default", "configured")
    if cli == "minimax-code":
        # ~/.minimax/config.yaml 的 defaultModel 形如 "minimax/MiniMax-M3"，取 / 后段并去 MiniMax- 前缀
        raw = _yaml_get(HOME / ".minimax" / "config.yaml", "defaultModel") or ""
        m = re.sub(r"^minimax-", "", raw.split("/")[-1], flags=re.I)
        return found(m, "config-default", "configured")
    if cli == "qoderclicn":
        # ~/.qoder-cn/settings.json 的 model.name 形如 "qmodel_38max"（厂商内部模型键，非显示名）
        try:
            import json
            cfg = json.loads((HOME / ".qoder-cn" / "settings.json").read_text(encoding="utf-8"))
            name = cfg.get("model", {}).get("name") or ""
        except Exception:
            name = ""
        return found(name, "config-default", "configured")
    # 通用兜底
    return found(None, "unresolved", "unknown")


def detect_model(cli: str) -> str:
    return model_evidence(cli)["model"]


def inspect_identity() -> dict:
    # 显式覆盖：任意 CLI 可设 AGENT_ID / AGENT_EMAIL 直接指定
    if os.environ.get("AGENT_ID"):
        name = os.environ["AGENT_ID"]
        email = os.environ.get("AGENT_EMAIL", FALLBACK_EMAIL)
        valid = bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,160}", name)
                     and re.fullmatch(r"[^\s<>@]+@[^\s<>@]+", email))
        return {"schema_version": 1, "name": name if valid else "agent-unknown",
                "email": email if valid else FALLBACK_EMAIL, "cli": None,
                "cli_source": "explicit-override", "model": "unknown",
                "model_source": "explicit-identity", "model_confidence": "declared",
                "current_model_confirmed": False,
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
        return {"schema_version": 1, "name": f"{base}-unknown", "email": FALLBACK_EMAIL,
                "cli": None, "cli_source": cli_source, "model": "unknown",
                "model_source": "unresolved", "model_confidence": "unknown",
                "current_model_confirmed": False, "resolved": False}

    evidence = model_evidence(cli)
    model = evidence["model"]
    name = f"{cli}-{model}"
    # 清洗成 git 身份安全字符
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-").lower()
    email = VENDOR_EMAIL.get(cli, FALLBACK_EMAIL)
    return {"schema_version": 1, "name": name, "email": email,
            "cli": cli, "cli_source": cli_source, "model": model,
            "model_source": evidence["source"], "model_confidence": evidence["confidence"],
            "current_model_confirmed": evidence["current_model_confirmed"],
            "resolved": not name.endswith("-unknown")}


def detect() -> tuple[str, str]:
    identity = inspect_identity()
    return identity["name"], identity["email"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--name", action="store_true")
    output.add_argument("--email", action="store_true")
    output.add_argument("--json", action="store_true")
    output.add_argument("--git-ident", action="store_true")
    args = parser.parse_args()
    identity = inspect_identity()
    name, email = identity["name"], identity["email"]
    if args.name:
        print(name)
    elif args.email:
        print(email)
    elif args.json:
        print(json.dumps(identity, ensure_ascii=False))
    elif args.git_ident:
        print(f"{name}\t{email}")
        return 0 if identity["resolved"] else 1
    else:
        print(f"name={name}")
        print(f"email={email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
