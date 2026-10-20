#!/usr/bin/env python3
"""经 eacli 从 Razer 拉回播客转写，并对大文件自动分片、重组和验 hash。

常规用法：
  python3 podcast_artifact_pull.py pull \
    --remote-path /srv/everagent/artifacts/podcast/pod_x.transcript.txt \
    --sha256 <artifact_sha256> --size <bytes> \
    --output ../reports/transcripts/<slug>.transcript.txt \
    --request-id req_<stable-id>

脚本只编排 `eacli invoke` 与 `eacli pull`，不绕过 coordinator。`split` 子命令由
`eacli invoke` 在 Razer 执行，不作为日常人工入口。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

REMOTE_ROOT = pathlib.PurePosixPath("/srv/everagent/artifacts/podcast")
DEFAULT_CHUNK_SIZE = 180_000


class PullError(RuntimeError):
    pass


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_remote_artifact(path: str) -> pathlib.PurePosixPath:
    value = pathlib.PurePosixPath(path)
    if not value.is_absolute() or value.parent != REMOTE_ROOT:
        raise PullError(f"remote path must be a direct child of {REMOTE_ROOT}")
    return value


def run_json(argv: list[str]) -> dict:
    proc = subprocess.run(argv, text=True, capture_output=True, check=False)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise PullError(
            f"command returned non-JSON output ({proc.returncode}): {' '.join(argv[:3])}; "
            f"stderr={proc.stderr.strip()[:300]}"
        ) from exc
    if proc.returncode != 0 or payload.get("ok") is not True:
        raise PullError(
            f"command failed ({proc.returncode}): {' '.join(argv[:3])}; "
            f"error={payload.get('error') or proc.stderr.strip()[:300]}"
        )
    return payload


def remote_split(source_raw: str, prefix_raw: str, chunk_size: int) -> int:
    source = require_remote_artifact(source_raw)
    prefix = require_remote_artifact(prefix_raw)
    if not 1 <= chunk_size <= DEFAULT_CHUNK_SIZE:
        raise PullError(f"chunk size must be 1..{DEFAULT_CHUNK_SIZE}")
    source_path = pathlib.Path(str(source))
    if not source_path.is_file():
        raise PullError(f"source missing: {source}")
    data = source_path.read_bytes()
    parts = []
    for index, start in enumerate(range(0, len(data), chunk_size)):
        payload = data[start : start + chunk_size]
        destination = pathlib.Path(f"{prefix}.{index:03d}")
        temporary = destination.with_name(destination.name + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(destination)
        parts.append(
            {
                "path": str(destination),
                "size": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    print(
        json.dumps(
            {
                "source": str(source),
                "source_size": len(data),
                "source_sha256": hashlib.sha256(data).hexdigest(),
                "chunk_size": chunk_size,
                "parts": parts,
            },
            ensure_ascii=False,
        )
    )
    return 0


def verify_existing(output: pathlib.Path, expected_sha256: str, expected_size: int) -> bool:
    if not output.exists():
        return False
    actual_size = output.stat().st_size
    actual_sha256 = sha256_file(output)
    if actual_size == expected_size and actual_sha256 == expected_sha256:
        return True
    raise PullError(
        f"output already exists with different content: {output} "
        f"size={actual_size} sha256={actual_sha256}"
    )


def pull_one(
    *,
    eacli: str,
    device: str,
    remote_path: str,
    local_path: pathlib.Path,
    request_id: str,
) -> dict:
    return run_json(
        [
            eacli,
            "pull",
            f"{device}:{remote_path}",
            str(local_path),
            "--request-id",
            request_id,
            "--json",
        ]
    )


def pull_artifact(args: argparse.Namespace) -> int:
    remote = require_remote_artifact(args.remote_path)
    if len(args.sha256) != 64 or any(char not in "0123456789abcdef" for char in args.sha256.lower()):
        raise PullError("sha256 must contain 64 hexadecimal characters")
    if args.size <= 0:
        raise PullError("size must be positive")
    if not args.request_id.strip():
        raise PullError("request-id must be non-empty")

    output = pathlib.Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if verify_existing(output, args.sha256.lower(), args.size):
        print(
            json.dumps(
                {
                    "ok": True,
                    "duplicate": True,
                    "output": str(output),
                    "size": args.size,
                    "sha256": args.sha256.lower(),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    eacli = shutil.which("eacli")
    if not eacli:
        raise PullError("eacli is not installed or not on PATH")

    if args.size <= args.chunk_size:
        pull_one(
            eacli=eacli,
            device=args.device,
            remote_path=str(remote),
            local_path=output,
            request_id=args.request_id,
        )
        mode = "direct"
        part_count = 1
    else:
        script = pathlib.Path(__file__).resolve()
        prefix = pathlib.PurePosixPath(f"{remote}.{args.sha256[:12]}.part")
        plan = run_json(
            [
                eacli,
                "invoke",
                "plan",
                "--device",
                args.device,
                "--file",
                str(script),
                "--engine",
                "python",
                "--arg",
                "split",
                "--arg",
                str(remote),
                "--arg",
                str(prefix),
                "--arg=--chunk-size",
                "--arg",
                str(args.chunk_size),
                "--timeout",
                "60",
                "--output",
                "json",
                "--json",
            ]
        )
        confirm = plan["result"]["confirm"]
        split_receipt = run_json(
            [
                eacli,
                "invoke",
                "run",
                "--device",
                args.device,
                "--file",
                str(script),
                "--engine",
                "python",
                "--arg",
                "split",
                "--arg",
                str(remote),
                "--arg",
                str(prefix),
                "--arg=--chunk-size",
                "--arg",
                str(args.chunk_size),
                "--timeout",
                "60",
                "--output",
                "json",
                "--request-id",
                f"{args.request_id}-split",
                "--confirm",
                confirm,
                "--wait",
                "--wait-timeout",
                "60",
                "--json",
            ]
        )
        manifest = split_receipt["result"]["result"]
        if manifest.get("source_sha256") != args.sha256.lower() or manifest.get("source_size") != args.size:
            raise PullError("remote split manifest does not match the podcast artifact receipt")

        local_parts = []
        try:
            for index, part in enumerate(manifest["parts"]):
                destination = output.with_name(f".{output.name}.part-{index:03d}")
                if destination.exists():
                    if destination.stat().st_size != part["size"] or sha256_file(destination) != part["sha256"]:
                        raise PullError(f"stale local part differs: {destination}")
                else:
                    pull_one(
                        eacli=eacli,
                        device=args.device,
                        remote_path=part["path"],
                        local_path=destination,
                        request_id=f"{args.request_id}-part-{index:03d}",
                    )
                local_parts.append(destination)

            temporary = output.with_name(f".{output.name}.tmp")
            with temporary.open("wb") as merged:
                for part in local_parts:
                    with part.open("rb") as source_handle:
                        shutil.copyfileobj(source_handle, merged)
            if temporary.stat().st_size != args.size or sha256_file(temporary) != args.sha256.lower():
                raise PullError("reassembled artifact failed size or SHA-256 verification")
            os.replace(temporary, output)
        finally:
            for part in local_parts:
                part.unlink(missing_ok=True)
        mode = "chunked"
        part_count = len(manifest["parts"])

    actual_size = output.stat().st_size
    actual_sha256 = sha256_file(output)
    if actual_size != args.size or actual_sha256 != args.sha256.lower():
        raise PullError("final artifact failed size or SHA-256 verification")
    print(
        json.dumps(
            {
                "ok": True,
                "duplicate": False,
                "mode": mode,
                "parts": part_count,
                "output": str(output),
                "size": actual_size,
                "sha256": actual_sha256,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    subparsers = parser.add_subparsers(dest="command", required=True)

    pull = subparsers.add_parser("pull", help="拉回并校验一个 podcast artifact")
    pull.add_argument("--remote-path", required=True)
    pull.add_argument("--sha256", required=True)
    pull.add_argument("--size", type=int, required=True)
    pull.add_argument("--output", required=True)
    pull.add_argument("--request-id", required=True)
    pull.add_argument("--device", default="razer")
    pull.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)

    split = subparsers.add_parser("split", help=argparse.SUPPRESS)
    split.add_argument("source")
    split.add_argument("prefix")
    split.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "split":
            return remote_split(args.source, args.prefix, args.chunk_size)
        return pull_artifact(args)
    except (PullError, KeyError, OSError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
