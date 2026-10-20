"""Model-only evidence readers, with session proof separated from configuration hints."""
from __future__ import annotations
import json
import os
import re
from pathlib import Path

HOME = Path.home()

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
