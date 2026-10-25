#!/usr/bin/env python3
"""Preflight selected public text files; no network, writes or matched values.

Paths are relative to this repository. This is a small heuristic scanner, not
an anonymity guarantee or a sandbox for hostile filesystem changes.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
from bisect import bisect_right
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    severity: str
    code: str
    message: str


# Severity, code, pattern, explanation. Keep findings free of matched values.
RULES = [
    ("error", "PRIVATE_KEY",
     r"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----|"
     r"-----BEGIN PGP PRIVATE KEY" r" BLOCK-----",
     "发现私钥头；公开文件不得包含私钥正文。"),
    ("error", "ABSOLUTE_HOME_PATH",
     r"(?i)(?<!\w)(?:/(?:Users|home)/[^/\\\s\"'<>\x60]+|/root)"
     r"(?=[/\\\s\"'<>\x60]|$)|"
     r"\b[A-Za-z]:[\\/]+Users[\\/]+[^\\/:\s\"'<>\x60]+(?=[/\\\s\"'<>\x60]|$)",
     "发现个人主目录绝对路径；改成相对路径或抽象描述。"),
    ("error", "URL_CREDENTIAL",
     r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/@?#]+@[^\s/?#]+",
     "URL 中包含用户信息；确认是否暴露账号或凭据。"),
    ("error", "CREDENTIAL_VALUE",
     r"(?i)(?<![\w-])[\"']?(?:api[_-]?key|access[_-]?token|auth[_-]?token|"
     r"password|passwd|secret)[\"']?\s*[:=]\s*[\"']?(?![<{$])[A-Za-z0-9_./+=-]{8,}",
     "发现疑似凭据赋值；公开文档应使用占位符。"),
    ("error", "BEARER_TOKEN",
     r"(?i)[\"']?authorization[\"']?\s*[:=]\s*[\"']?bearer\s+[A-Za-z0-9._~+/=-]{8,}",
     "发现疑似 Bearer Token。"),
    ("error", "KNOWN_TOKEN_PREFIX",
     r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})\b",
     "发现具有常见前缀的疑似访问 Token。"),
    ("warning", "IP_ADDRESS",
     r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?!\w|\.\d)|"
     r"(?<![\w:])(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f:.]*(?:%[A-Za-z0-9_.-]+)?(?![\w:])",
     "发现 IP 地址；确认是否适合公开。"),
    ("warning", "EMAIL_ADDRESS",
     r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
     "发现邮箱地址；确认已获公开授权。"),
    ("warning", "SSH_ENDPOINT",
     r"(?i)\bssh\s+(?:-[^\s]+\s+)*[^\s@]+@[^\s]+|"
     r"\bssh://[^\s]+|\b(?:scp|sftp)\s+[^\s@]+@[^\s:]+:",
     "发现 SSH 入口；公开案例应移除用户、主机与端口。"),
]


def scan_text(text: str, display: str, *, decoded: bool = False) -> set[Finding]:
    newlines = [match.start() for match in re.finditer("\n", text)]
    findings = set()
    for severity, code, pattern, message in RULES:
        for match in re.finditer(pattern, text):
            if code == "IP_ADDRESS":
                try:
                    ipaddress.ip_address(match.group().rstrip("."))
                except ValueError:
                    continue
            line = 0 if decoded else bisect_right(newlines, match.start()) + 1
            findings.add(Finding(display, line, severity, code, message))
    return findings


def json_strings(value: object):
    """Include decoded keys and assignments, not just string values."""
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            if isinstance(item, str):
                yield key + "=" + item
            yield from json_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from json_strings(item)


def scan_file(path: Path) -> tuple[list[Finding], bool]:
    path = ROOT / path
    display = "<outside-repository>"

    def reject(code: str, message: str):
        return [Finding(display, 0, "error", code, message)], False

    try:
        relative = path.relative_to(ROOT)
        if ".." in relative.parts:
            raise ValueError
    except ValueError:
        return reject("OUTSIDE_REPOSITORY", "请使用仓内路径，不接受父目录跳转。")

    display = relative.as_posix()
    try:
        current = ROOT
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                return reject("SYMLINK_FILE", "不读取符号链接或经符号链接目录访问的文件。")
        if not path.is_file():
            return reject("INVALID_FILE", "指定文件不存在或不是普通文件；目录不会展开。")
        if not path.resolve().is_relative_to(ROOT):
            return reject("OUTSIDE_REPOSITORY", "解析后的文件不在本仓库内。")
        with path.open("rb") as stream:
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            return reject("FILE_TOO_LARGE", "文件超过 2 MiB；请缩小发布物后再检查。")
        text = data.decode("utf-8-sig")
        if "\x00" in text:
            raise ValueError
    except (OSError, UnicodeError, ValueError, RuntimeError):
        return reject("READ_ERROR", "需要可读取的 UTF-8 文本文件；未完成检查。")

    findings = scan_text(text, display)
    if path.suffix.lower() == ".json":
        try:
            for string in json_strings(json.loads(text)):
                findings.update(scan_text(string, display, decoded=True))
        except (ValueError, RecursionError):
            findings.add(Finding(display, 0, "error", "INVALID_JSON", "JSON 无法完整解析。"))
    return sorted(findings, key=lambda item: (item.line, item.code)), True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Files relative to this repository.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors.")
    args = parser.parse_args()

    selected = dict.fromkeys(ROOT / Path(raw) for raw in args.paths)
    findings = []
    scanned = 0
    for path in selected:
        items, was_scanned = scan_file(path)
        findings.extend(items)
        scanned += was_scanned
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    ok = not (errors or (args.strict and warnings))
    result = {
        "schema_version": 1,
        "files_selected": len(selected),
        "files_scanned": scanned,
        "strict": args.strict,
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "findings": [asdict(item) for item in findings],
        "limitations": [
            "只检查显式选择的仓内 UTF-8 文本，不检查 Git 历史或链接目标。",
            "规则不能穷尽凭据和个人标识；无命中不代表匿名或可安全发布。",
            "JSON 使用标准库解码，不替代 schema 校验；发布前仍需人工审阅。",
        ],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"public-context audit: files={scanned}/{len(selected)} errors={errors} warnings={warnings}")
        for item in findings:
            print(f"{item.severity.upper()} {item.code} {item.file}:{item.line} {item.message}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
