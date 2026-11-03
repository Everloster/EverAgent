#!/usr/bin/env python3
"""通过 eacli file pull 把回执绑定的完整转写拉到仓库外私有目录。

传输、断点续传和原子落盘由 eacli 拥有；本脚本检查公开仓边界，
并按转写回执再次核验大小与 SHA-256，不再分片或运行远端拆分脚本。
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

class PullError(RuntimeError):
    pass

def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def private_destination(raw: str) -> pathlib.Path:
    path = pathlib.Path(raw).expanduser().absolute()
    if path.is_symlink():
        raise PullError("destination must not be a symbolic link")
    resolved = path.resolve()
    if resolved.is_relative_to(REPO_ROOT):
        raise PullError("full transcripts must be stored outside the public repository")
    return resolved

def pull_artifact(args: argparse.Namespace) -> int:
    remote = pathlib.PurePosixPath(args.remote_path)
    if not remote.is_absolute() or ".." in remote.parts or any(c in args.remote_path for c in "\n\r\x00"):
        raise PullError("remote path must be the absolute path from the artifact receipt")
    expected_sha = args.sha256.lower()
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha) or args.size <= 0:
        raise PullError("a valid SHA-256 and positive size from the artifact receipt are required")
    if not re.fullmatch(r"req_[A-Za-z0-9_.-]{1,120}", args.request_id):
        raise PullError("a stable req_ request id is required")
    if not 1 <= args.timeout <= 86400:
        raise PullError("timeout must be within 1..86400 seconds")
    output = private_destination(args.output)
    if output.exists():
        if not output.is_file() or output.stat().st_nlink != 1:
            raise PullError("existing destination is not a private regular file")
        if output.stat().st_size != args.size or sha256_file(output) != expected_sha:
            raise PullError("existing destination differs from the artifact receipt")
        result = {"duplicate": True, "resumed_bytes": 0}
    else:
        eacli = shutil.which("eacli")
        if not eacli:
            raise PullError("eacli is not installed or not on PATH")
        proc = subprocess.run([
            eacli, "file", "pull", "--device", args.device,
            "--path", str(remote), "--destination", str(output),
            "--sha256", expected_sha, "--request-id", args.request_id,
            "--timeout", str(args.timeout), "--json",
        ], text=True, capture_output=True, check=False)
        try:
            receipt = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise PullError("file pull returned no complete JSON receipt; inspect the original request") from exc
        if not isinstance(receipt, dict):
            raise PullError("file pull receipt must be an object")
        result = receipt.get("result") or {}
        if not isinstance(result, dict) or proc.returncode != 0 or receipt.get("ok") is not True or result.get("status") != "verified":
            error = receipt.get("error") or {}
            reason = error.get("type", "transfer-unverified") if isinstance(error, dict) else "transfer-unverified"
            raise PullError(f"{reason}; partial data is retained by eacli; resume with the same command")
    if not output.is_file() or output.is_symlink() or output.stat().st_nlink != 1:
        raise PullError("verified destination is missing or not a private regular file")
    if output.stat().st_size != args.size or sha256_file(output) != expected_sha:
        raise PullError("download differs from the original artifact receipt; do not use it as source")
    print(json.dumps({"ok": True, "mode": "eacli-file", "output": str(output),
        "size": args.size, "sha256": expected_sha, "duplicate": result.get("duplicate", False),
        "resumed_bytes": result.get("resumed_bytes", 0)}, ensure_ascii=False, indent=2))
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    pull = commands.add_parser("pull", help="拉回并校验私有转写")
    for name in ("device", "remote-path", "sha256", "output", "request-id"):
        pull.add_argument("--" + name, required=True)
    pull.add_argument("--size", type=int, required=True)
    pull.add_argument("--timeout", type=int, default=1800)
    return parser

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return pull_artifact(args)
    except (PullError, OSError, ValueError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
