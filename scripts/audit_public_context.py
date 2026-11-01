#!/usr/bin/env python3
"""Preflight selected public text files; no network, writes or matched values.

Paths are relative to this repository. This is a small heuristic scanner, not
an anonymity guarantee or a sandbox for hostile filesystem changes.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import ipaddress
import json
import re
import subprocess
from bisect import bisect_right
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2 * 1024 * 1024
PUBLICATION_SUFFIX = ".publication.json"


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


def reference_value(node: ast.expr) -> bool:
    """Recognize references, never quoted values or credential defaults."""
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Attribute):
        return reference_value(node.value)
    if isinstance(node, ast.Subscript):
        return reference_value(node.value) and isinstance(node.slice, (ast.Constant, ast.Name))
    if isinstance(node, ast.Call) and ast.unparse(node.func) in {"os.getenv", "os.environ.get"}:
        return (not node.keywords and 1 <= len(node.args) <= 2
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
                and (len(node.args) == 1 or (isinstance(node.args[1], ast.Constant)
                                           and node.args[1].value in (None, ""))))
    return False


def reference_spans(text: str, display: str) -> list[tuple[int, int]]:
    """Only Python syntax can exempt an assignment to a reference.

    JSON/YAML strings, comments, docstrings, and other token rules remain scanned.
    Parse failures grant no exemption; fenced Python examples use the same rules.
    """
    chunks = []
    if Path(display).suffix.lower() == ".py":
        chunks.append((0, text))
    elif Path(display).suffix.lower() == ".md":
        for match in re.finditer(r"(?m)^(`{3,}|~{3,})(?:python|python3|py)[ \t]*\n([\s\S]*?)^\1[ \t]*$", text):
            chunks.append((match.start(2), match.group(2)))
    spans = []
    for offset, code in chunks:
        try:
            tree = ast.parse(code)
        except (SyntaxError, ValueError, RecursionError):
            continue
        lines = code.splitlines(keepends=True)
        starts = [0]
        for line in lines:
            starts.append(starts[-1] + len(line))

        def position(line: int, column: int) -> int:
            # AST columns are UTF-8 bytes, regex offsets are Unicode characters.
            return offset + starts[line - 1] + len(lines[line - 1].encode()[:column].decode())

        for node in ast.walk(tree):
            values = []
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr, ast.keyword)):
                values = [node.value]
            elif isinstance(node, ast.Dict):
                values = node.values
            for value in values:
                if value is not None and reference_value(value):
                    spans.append((position(value.lineno, value.col_offset),
                                  position(value.end_lineno, value.end_col_offset)))
    return spans


def text_hits(text: str, display: str, *, decoded: bool = False):
    """Keep value-specific fingerprints in memory only, never in audit output."""
    newlines = [match.start() for match in re.finditer("\n", text)]
    references = [] if decoded else reference_spans(text, display)
    for severity, code, pattern, message in RULES:
        for match in re.finditer(pattern, text):
            if code == "CREDENTIAL_VALUE" and any(
                match.start() <= start < match.end() <= end for start, end in references
            ):
                continue
            if code == "IP_ADDRESS":
                try:
                    ipaddress.ip_address(match.group().rstrip("."))
                except ValueError:
                    continue
            line = 0 if decoded else bisect_right(newlines, match.start()) + 1
            fingerprint = hashlib.sha256(match.group().encode("utf-8")).digest()
            # Headers and heuristic assignments may match only a credential's
            # prefix; a changed body/suffix must never inherit that exemption.
            key = None if code in {"PRIVATE_KEY", "CREDENTIAL_VALUE"} else (code, decoded, fingerprint)
            yield Finding(display, line, severity, code, message), key


def scan_text(text: str, display: str, *, decoded: bool = False) -> set[Finding]:
    return {finding for finding, _ in text_hits(text, display, decoded=decoded)}


def content_hits(text: str, display: str):
    yield from text_hits(text, display)
    if Path(display).suffix.lower() == ".json":
        try:
            for string in json_strings(json.loads(text)):
                yield from text_hits(string, display, decoded=True)
        except (ValueError, RecursionError):
            yield Finding(display, 0, "error", "INVALID_JSON", "JSON 无法完整解析。"), None


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

    findings = {finding for finding, _ in content_hits(text, display)}
    return sorted(findings, key=lambda item: (item.line, item.code)), True


class AuditError(Exception):
    """A deliberately value-free Git/read failure."""


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=False)
    if result.returncode:
        raise AuditError("无法读取 Git 快照；增量检查未完成。")
    return result.stdout


def tree_entries(root: Path, revision: str | None) -> dict[str, tuple[str, str]]:
    if revision is None:
        return {}
    entries = {}
    for record in git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if record:
            metadata, name = record.split(b"\t", 1)
            mode, _, oid = metadata.decode("ascii").split()
            entries[name.decode("utf-8", "surrogateescape")] = (mode, oid)
    return entries


def index_entries(root: Path) -> dict[str, tuple[str, str]]:
    entries = {}
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if record:
            metadata, name = record.split(b"\t", 1)
            mode, oid, stage = metadata.decode("ascii").split()
            if stage != "0":
                raise AuditError("Git index 有未解决的冲突；增量检查未完成。")
            entries[name.decode("utf-8", "surrogateescape")] = (mode, oid)
    return entries


def resolve_tree(root: Path, revision: str) -> str:
    return git(root, "rev-parse", "--verify", "--end-of-options", revision + "^{tree}").decode().strip()


def known_binary(data: bytes, path: str) -> bool:
    """Only recognize public document/image formats, not arbitrary binary files.

    This is a text scanner: recognized binaries are counted as skipped, not safe.
    Text disguised with an asset suffix still goes through the text rules.
    """
    suffix = Path(path).suffix.lower()
    public_media = path.startswith("docs/assets/public/") and (
        (suffix == ".mp4" and data[4:8] == b"ftyp")
        or (suffix == ".webm" and data.startswith(b"\x1aE\xdf\xa3"))
        or (suffix == ".ogg" and data.startswith(b"OggS"))
        or (suffix == ".mp3" and (data.startswith(b"ID3") or
                                 (len(data) > 1 and data[0] == 255 and data[1] & 224 == 224)))
    )
    return public_media or (
        (suffix == ".pdf" and data.startswith(b"%PDF-"))
        or (suffix == ".png" and data.startswith(b"\x89PNG\r\n\x1a\n"))
        or (suffix in {".jpg", ".jpeg"} and data.startswith(b"\xff\xd8\xff"))
        or (suffix == ".gif" and data.startswith((b"GIF87a", b"GIF89a")))
        or (suffix == ".webp" and data.startswith(b"RIFF") and data[8:12] == b"WEBP")
        or (suffix == ".ico" and data.startswith(b"\x00\x00\x01\x00"))
    )


def protected_path(path: str) -> bool:
    name = Path(path).name.lower()
    return (name == ".env" or name.startswith(".env.")
            or name in {"id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"}
            or Path(name).suffix in {".key", ".pem", ".p12", ".pfx"})


def full_transcript_path(path: str) -> bool:
    candidate = Path(path.lower())
    return (path.lower().endswith((".transcript.txt", ".polished.txt", ".transcript.md", ".polished.md", ".srt", ".vtt"))
            or ("transcripts" in candidate.parts and candidate.suffix in {".txt", ".md"}
                and candidate.name not in {"readme.md", "index.md"}))


def publication_errors(data: bytes, permission: bytes) -> list[str]:
    """Check an explicit, content-bound exception; this cannot prove legal rights."""
    if len(permission) > MAX_BYTES:
        return ["全文公开说明超过文本检查上限。"]
    try:
        record = json.loads(permission)
    except (ValueError, UnicodeError):
        return ["全文公开说明不是有效 JSON。"]
    fields = {"schema_version", "sha256", "source_url", "permission_url", "permission_note", "maintainer_confirmed"}
    if not isinstance(record, dict) or set(record) != fields:
        return ["全文公开说明需要版本、SHA-256、来源、授权链接、允许范围和维护者确认。"]
    errors = []
    if type(record["schema_version"]) is not int or record["schema_version"] != 1:
        errors.append("全文公开说明版本无效。")
    if record["sha256"] != hashlib.sha256(data).hexdigest():
        errors.append("全文已变化；公开说明的 SHA-256 与当前文件不符。")
    if record["maintainer_confirmed"] is not True:
        errors.append("全文公开例外尚未记录维护者确认。")
    if not isinstance(record["permission_note"], str) or not record["permission_note"].strip():
        errors.append("全文公开说明缺少允许范围。")
    for field in ("source_url", "permission_url"):
        try:
            url = urlsplit(record[field])
            if (url.scheme not in {"http", "https"} or not url.hostname
                    or url.username or url.password):
                raise ValueError
        except (ValueError, TypeError, AttributeError):
            errors.append("全文公开说明需要可审阅的公开来源与授权链接。")
    return errors


def decode_text(data: bytes, path: str) -> str | None:
    if known_binary(data, path):
        return None
    if len(data) > MAX_BYTES:
        raise AuditError("文本超过 2 MiB；增量检查未完成。")
    try:
        text = data.decode("utf-8-sig")
        if "\x00" in text:
            raise ValueError
        return text
    except (UnicodeError, ValueError):
        raise AuditError("无法识别的二进制或非 UTF-8 内容；增量检查未完成。") from None


def audit_git(root: Path, *, staged: bool = False, base: str = "HEAD",
              head: str | None = None) -> dict:
    """Compare exact occurrences against one immutable base, scoped per path.

    Staged mode reads blobs, never worktree contents. Changed mode includes
    tracked worktree changes and untracked non-ignored files, unless --head
    selects a committed tree (CI). Deletions have no content to publish. Renames
    are deliberately additions, so moving an old secret cannot exempt it.
    """
    try:
        baseline = resolve_tree(root, base)
    except AuditError:
        # The first commit has no HEAD; a misspelled explicit base fails closed.
        if base != "HEAD" or subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"], cwd=root,
            capture_output=True, check=False,
        ).returncode == 0:
            raise
        baseline = None
    before = tree_entries(root, baseline)
    after = tree_entries(root, resolve_tree(root, head)) if head else index_entries(root)
    args = ["diff", "--no-ext-diff", "--no-renames", "--name-only", "-z", "--diff-filter=ACDMRTUXB"]
    if staged:
        args.append("--cached")
    if baseline:
        args.append(baseline)
        if head:
            args.append(resolve_tree(root, head))
        names = {name.decode("utf-8", "surrogateescape") for name in git(root, *args, "--").split(b"\0") if name}
    else:
        names = set(after)
    if not staged and not head:
        names.update(name.decode("utf-8", "surrogateescape") for name in
                     git(root, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0") if name)

    def exists(name: str) -> bool:
        return name in after if staged or head else (root / name).exists() or (root / name).is_symlink()

    def read(name: str) -> bytes:
        if staged or head:
            mode, oid = after[name]
            if mode not in {"100644", "100755"}:
                raise AuditError("不检查符号链接或子模块；请使用公开普通文件。")
            return git(root, "cat-file", "blob", oid)
        path = root / name
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root):
            raise AuditError("不读取符号链接或经符号链接目录访问的文件。")
        return path.read_bytes()

    # Permission edits/deletions must recheck an unchanged source too.
    names.update(name.removesuffix(PUBLICATION_SUFFIX) for name in list(names)
                 if name.endswith(PUBLICATION_SUFFIX) and full_transcript_path(name.removesuffix(PUBLICATION_SUFFIX)))
    names = {name for name in names if exists(name)}

    findings = []
    scanned = skipped = existing = 0
    for name in sorted(names):
        try:
            if protected_path(name):
                findings.append(Finding(name, 0, "error", "PROTECTED_FILE", "凭据文件不得进入公开仓库。"))
                continue
            data = read(name)
            permission_name = name + PUBLICATION_SUFFIX
            if full_transcript_path(name) and (
                name not in before or permission_name in before or exists(permission_name)
            ):
                if exists(permission_name):
                    errors = publication_errors(data, read(permission_name))
                else:
                    errors = ["新增转写/润色全文默认私有；公开例外需附同名 .publication.json，记录内容哈希、授权依据与维护者确认。"]
                findings.extend(Finding(name, 0, "error", "FULL_TRANSCRIPT_PUBLICATION", message) for message in errors)
            text = decode_text(data, name)
            if text is None:
                skipped += 1
                continue
            old_counts = Counter()
            if name in before and before[name][0] in {"100644", "100755"}:
                try:
                    old_text = decode_text(git(root, "cat-file", "blob", before[name][1]), name)
                    if old_text is not None:
                        old_counts.update(key for _, key in content_hits(old_text, name) if key is not None)
                except AuditError:
                    pass  # Unscannable old content can never exempt new hits.
            scanned += 1
            for finding, key in content_hits(text, name):
                if key is not None and old_counts[key]:
                    old_counts[key] -= 1
                    existing += 1
                else:
                    findings.append(finding)
        except (AuditError, OSError, KeyError):
            findings.append(Finding(name, 0, "error", "INCOMPLETE_SCAN", "无法完整检查该路径；拒绝发布。"))
    result = make_result(findings, selected=len(names), scanned=scanned)
    result.update(files_skipped_binary=skipped, existing_occurrences=existing,
                  mode="staged" if staged else "changed", base_tree=baseline)
    return result


def make_result(findings: list[Finding], *, selected: int, scanned: int, strict: bool = False) -> dict:
    items = sorted(set(findings), key=lambda item: (item.file, item.line, item.code))
    errors = sum(item.severity == "error" for item in items)
    warnings = sum(item.severity == "warning" for item in items)
    return {
        "schema_version": 1, "files_selected": selected, "files_scanned": scanned,
        "strict": strict, "ok": not (errors or (strict and warnings)),
        "errors": errors, "warnings": warnings, "findings": [asdict(item) for item in items],
        "limitations": [
            "仅检查文本；已识别的 PDF/图片及 docs/assets/public 媒体跳过，不代表内容可安全公开。",
            "增量仅豁免同路径相对基线未增加的完整命中；私钥头及可能截断的凭据赋值不豁免，不豁免整个文件或测试目录。",
            "规则不能穷尽凭据和个人标识；无命中不代表匿名或可安全发布。",
            "JSON 解码命中行号为 0；不检查 Git 历史、链接目标或二进制内部内容。",
            "新增转写全文按文件名/目录识别；公开说明只验证结构、哈希和确认记录，不代替授权核实，也不能识别所有改名伪装。",
        ],
    }


def emit(result: dict, *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(f"public-context audit: files={result['files_scanned']}/{result['files_selected']} "
              f"errors={result['errors']} warnings={result['warnings']} "
              f"binary_skipped={result.get('files_skipped_binary', 0)} "
              f"existing_occurrences={result.get('existing_occurrences', 0)}")
        for item in result["findings"]:
            location = json.dumps(item['file'], ensure_ascii=False)
            print(f"{item['severity'].upper()} {item['code']} {location}:{item['line']} {item['message']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Files relative to this repository (full scan).")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="Check index versus HEAD, not worktree bytes.")
    mode.add_argument("--changed", action="store_true", help="Check worktree or --head against --base.")
    parser.add_argument("--base", default="HEAD", help="Immutable comparison revision; default HEAD.")
    parser.add_argument("--head", help="Committed target revision for CI; requires --changed.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Fail on warnings as well as errors.")
    args = parser.parse_args()
    if (args.paths and (args.staged or args.changed)) or (args.head and not args.changed):
        parser.error("显式路径不能与增量模式混用；--head 仅用于 --changed。")
    if args.staged and args.base != "HEAD":
        parser.error("--staged 固定与 HEAD 比较。")
    if not (args.paths or args.staged or args.changed):
        parser.error("请选择显式路径、--staged 或 --changed。")

    if args.staged or args.changed:
        try:
            result = audit_git(ROOT, staged=args.staged, base=args.base, head=args.head)
        except (AuditError, OSError):
            result = make_result([Finding("<git>", 0, "error", "GIT_ERROR", "无法读取 Git 基线或快照；检查未完成。")],
                                 selected=0, scanned=0)
        result["strict"] = args.strict
        result["ok"] = not (result["errors"] or (args.strict and result["warnings"]))
    else:
        selected = dict.fromkeys(ROOT / Path(raw) for raw in args.paths)
        findings = []
        scanned = 0
        for path in selected:
            items, was_scanned = scan_file(path)
            findings.extend(items)
            scanned += was_scanned
        result = make_result(findings, selected=len(selected), scanned=scanned, strict=args.strict)
    emit(result, as_json=args.json)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
