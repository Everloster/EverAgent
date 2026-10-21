"""Common session evidence for interactive clients and supervised workers."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess


def checkout_context(cwd: Path | None = None) -> tuple[dict, Path | None]:
    cwd = cwd or Path.cwd()
    try:
        proc = subprocess.run(["git", "rev-parse", "--show-toplevel", "HEAD", "--git-common-dir"],
                              cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=3)
        lines = proc.stdout.splitlines()
        if proc.returncode or len(lines) != 3:
            return {"status": "outside-git"}, None
        root = Path(lines[0]).resolve()
        common = Path(lines[2])
        if not common.is_absolute():
            common = cwd / common
        common = common.resolve()
        main = common.parent if common.name == ".git" else root
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=root,
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace", timeout=3)
        if branch.returncode:
            return {"status": "unavailable"}, root
        return {"status": "ok", "repository": main.name, "branch": branch.stdout.strip() or None,
                "head": lines[1], "linked_worktree": root != main,
                "checkout_ref": hashlib.sha256(str(root).encode()).hexdigest()[:24]}, root
    except (OSError, ValueError, subprocess.SubprocessError):
        return {"status": "unavailable"}, None


def readiness(device: dict, agent: dict, checkout: dict, host: dict) -> dict:
    reasons = []
    if not device.get("known"):
        reasons.append("unknown-device")
    if not agent.get("harness_resolved", agent.get("resolved", False)):
        reasons.append("agent-unresolved")
    from .git import CommitError, require_model
    try:
        require_model(agent)
    except CommitError:
        reasons.append("model-needs-user")
    if checkout.get("status") != "ok":
        reasons.append("checkout-unavailable")
    if host.get("status") in {"ambiguous-runtime", "unavailable", "disconnected-or-orphaned", "no-caller-handle"}:
        reasons.append("runtime-" + host["status"])
    if host.get("kind") in {"orca", "herdr"} and host.get("verified") is not True:
        reasons.append("caller-unverified")
    if host.get("workspace_matches_runtime") is False:
        reasons.append("checkout-differs-from-host")
    return {"read_only": device.get("known") is True, "commit": not reasons,
            "reasons": list(dict.fromkeys(reasons))}


def normalize(*, device: dict, agent: dict, checkout: dict, runtime: dict,
              caller: dict, host_app: dict | None = None, task: dict | None = None,
              core: dict | None = None) -> dict:
    ready = readiness(device, agent, checkout, runtime)
    worker = task is not None and task.get("owner") is not None and task.get("verified") is True
    harness = agent.get("cli")
    actor_kind = ("agent" if agent.get("harness_resolved", agent.get("resolved"))
                  else "executor-service" if worker and task.get("verified") and task.get("kind") == "executor"
                  else "unresolved")
    model = {"id": agent.get("model", "unknown"), "source": agent.get("model_source", "unresolved"),
             "confidence": agent.get("model_confidence", "unknown"),
             "confirmed": agent.get("current_model_confirmed") is True,
             "user_declared": agent.get("user_model_declared") is True}
    for field in ("requested_model", "configured_model", "observed_model", "user_declared_model"):
        if agent.get(field):
            model[field.removesuffix("_model")] = agent[field]
    if agent.get("declaration"):
        model["declaration_id"] = agent["declaration"]["id"][:24]
    host = {key: runtime[key] for key in ("kind", "status", "verified", "source", "terminal_handle",
            "pane_id", "tab_id", "workspace_id", "worktree_ref", "workspace_matches_runtime", "error", "candidates")
            if key in runtime}
    if not host.get("kind") and host_app and host_app.get("id"):
        host = dict(host_app)
    return {"schema_version": 2, "observed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "unknown-device" if not device.get("known") else "ok" if ready["commit"] else "partial",
            "usage": "worker" if worker and actor_kind == "agent" else "executor" if actor_kind == "executor-service" else "interactive",
            "actor": {"kind": actor_kind, "harness": harness, "name": agent.get("name"), "model": model},
            "execution": {key: device.get(key) for key in
                          ("device", "asset_id", "platform", "redline", "archive", "known")},
            "caller": caller, "host": host, "checkout": checkout,
            "task": task or {"owner": None, "status": "unbound", "verified": False},
            "readiness": ready, **({"core": core} if core else {})}
