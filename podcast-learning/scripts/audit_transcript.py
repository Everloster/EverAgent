#!/usr/bin/env python3
"""只读转写审计与播客来源检查；可向 stdout 输出不含原文/本机路径的公开收据。"""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import pathlib
import re
from urllib.parse import parse_qsl, urlsplit

STAMP_RE = re.compile(r"^\[(\d+):(\d+):(\d+) -> (\d+):(\d+):(\d+)\]\s*(.*)$")
MAX_CONSECUTIVE = 3
COMPRESS_TOL_PP = 2.0
DURATION_TOL_S = 120
PATH_FIELDS = ("transcript_path", "polished_transcript_path", "transcript_audit_path")
NULL_VALUES = {"", "null", "none", "~"}
RECEIPT_METRICS = (
    "ok", "size", "sha256", "lines", "segments", "duration_seconds",
    "max_consecutive_identical", "timestamp_errors", "malformed_lines", "tail_gap_seconds",
)


def seconds(hours: str, minutes: str, secs: str) -> int:
    return int(hours) * 3600 + int(minutes) * 60 + int(secs)


def sha256_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(path: pathlib.Path, max_consecutive: int = MAX_CONSECUTIVE) -> dict:
    data = path.read_bytes()
    lines = data.decode("utf-8", errors="replace").splitlines()
    errors, warnings, segments = [], [], []
    malformed = timestamp_errors = longest_run = current_run = 0
    previous_start, previous_text = -1, None
    for line_number, line in enumerate(lines, 1):
        match = STAMP_RE.match(line)
        if not match:
            malformed += bool(line.strip())
            continue
        start = seconds(*match.groups()[:3])
        end = seconds(*match.groups()[3:6])
        text = re.sub(r"\s+", " ", match.group(7)).strip()
        if any(int(match.group(i)) >= 60 for i in (2, 3, 5, 6)):
            errors.append(f"line {line_number}: invalid timestamp component")
            timestamp_errors += 1
        if end < start:
            errors.append(f"line {line_number}: end timestamp precedes start")
            timestamp_errors += 1
        if start < previous_start:
            errors.append(f"line {line_number}: start timestamp is not monotonic")
            timestamp_errors += 1
        previous_start = start
        current_run = current_run + 1 if text and text == previous_text else int(bool(text))
        previous_text = text or None
        longest_run = max(longest_run, current_run)
        segments.append((start, end))
    if not segments:
        errors.append("no timestamped segments")
    if malformed:
        warnings.append(f"{malformed} non-empty lines lack transcript timestamps")
    if longest_run > max_consecutive:
        errors.append(f"max consecutive identical text is {longest_run} (> {max_consecutive})")
    tail_gap = segments[-1][0] - segments[-2][1] if len(segments) >= 2 else 0
    if tail_gap > 30:
        warnings.append(f"last segment starts after a {tail_gap}s gap; inspect possible outro")
    return {
        "path": str(path), "ok": not errors, "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(), "lines": len(lines),
        "segments": len(segments), "duration_seconds": segments[-1][1] if segments else None,
        "max_consecutive_identical": longest_run, "timestamp_errors": timestamp_errors,
        "malformed_lines": malformed, "tail_gap_seconds": tail_gap,
        "head": lines[:3], "tail": lines[-3:], "warnings": warnings, "errors": errors,
    }


def public_source_url(value: object) -> bool:
    """拒绝明显私有/含认证信息的 URL；是否适合公开仍需人工核对。"""
    try:
        url = urlsplit(str(value or ""))
        host = url.hostname or ""
        if url.scheme not in {"https", "http"} or not host or url.username or url.password or url.fragment:
            return False
        if "." not in host or host.endswith((".local", ".internal", ".localhost", ".ts.net")):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            pass
        return not any(re.search(r"token|secret|password|signature|api.?key|auth", key, re.I)
                       for key, _ in parse_qsl(url.query))
    except ValueError:
        return False


def public_receipt(result: dict, source_url: str) -> dict:
    if not public_source_url(source_url):
        raise ValueError("公开收据需要不含认证信息的公开 source_url")
    return {
        "schema_version": 2, "kind": "podcast-transcript-audit",
        "source_url": source_url, "source_ref": "sha256:" + result["sha256"],
        "max_consecutive_limit": MAX_CONSECUTIVE,
        "audit": {key: result[key] for key in RECEIPT_METRICS},
    }


def validate_receipt(receipt: object, *, source_ref: str, source_url: str) -> list[str]:
    """验证收据结构/绑定，不声称重读了私有源，也不把自报结果当签名证明。"""
    if not isinstance(receipt, dict):
        return ["收据必须是 JSON object"]
    expected = {"schema_version", "kind", "source_url", "source_ref", "max_consecutive_limit", "audit"}
    if set(receipt) != expected:
        return ["收据字段不符合公开白名单（不可含路径、样本或运行态标识）"]
    errors = []
    if receipt["schema_version"] != 2 or receipt["kind"] != "podcast-transcript-audit":
        errors.append("不支持的转写收据版本")
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", source_ref) or receipt["source_ref"] != source_ref:
        errors.append("transcript_source_ref 与收据不匹配")
    if not public_source_url(source_url) or receipt["source_url"] != source_url:
        errors.append("source_url 缺失、不适合公开或与收据不匹配")
    if receipt["max_consecutive_limit"] != MAX_CONSECUTIVE:
        errors.append("收据重复检查阈值不符合合同")
    metrics = receipt["audit"]
    if not isinstance(metrics, dict) or set(metrics) != set(RECEIPT_METRICS):
        return errors + ["收据缺少确定性审计指标或包含非公开字段"]
    for key in set(RECEIPT_METRICS) - {"ok", "sha256"}:
        value = metrics[key]
        if type(value) is not int or (key != "tail_gap_seconds" and value < 0):
            errors.append(f"收据指标 {key} 无效")
    if errors:
        return errors
    if metrics["sha256"] != source_ref.removeprefix("sha256:"):
        errors.append("收据 SHA-256 与 source_ref 不匹配")
    passed = (metrics["segments"] > 0 and metrics["timestamp_errors"] == 0
              and metrics["max_consecutive_identical"] <= MAX_CONSECUTIVE)
    if metrics["ok"] is not True or not passed:
        errors.append("收据记录了失败的转写审计")
    if (metrics["size"] <= 0 or metrics["lines"] < metrics["segments"]
            or metrics["segments"] < metrics["max_consecutive_identical"]
            or metrics["lines"] < metrics["segments"] + metrics["malformed_lines"]):
        errors.append("收据指标相互矛盾")
    return errors


def source_path(repo: pathlib.Path, value: object) -> pathlib.Path | None:
    """现有 transcript_path 是领域相对路径；亦接受显式仓库相对路径。"""
    raw = str(value or "")
    if raw.lower() in NULL_VALUES:
        return None
    path = pathlib.Path(raw)
    if not path.parts or path.is_absolute() or ".." in path.parts or "\\" in raw or ":" in raw:
        raise ValueError("来源路径必须是仓内相对路径，不可含私有绝对路径或越界段")
    candidate = repo / path if path.parts[0] == "podcast-learning" else repo / "podcast-learning" / path
    if not candidate.resolve().is_relative_to(repo.resolve()):
        raise ValueError("来源路径越出仓库")
    if any(part.is_symlink() for part in (candidate, *candidate.parents) if part.is_relative_to(repo)):
        raise ValueError("来源路径不能是符号链接")
    return candidate


def report_sources(repo: pathlib.Path, metadata: dict) -> set[pathlib.Path]:
    paths = set()
    for key in PATH_FIELDS:
        try:
            path = source_path(repo, metadata.get(key))
            if path:
                paths.add(path)
        except ValueError:
            pass
    return paths


def audit_report(repo: pathlib.Path, metadata: dict, text: str) -> list[tuple[str, str, bool]]:
    """返回 (code, message, advisory)；严重性由统一入口的变更范围决定。"""
    findings = []
    paths = {}
    for key in PATH_FIELDS:
        try:
            path = source_path(repo, metadata.get(key))
        except ValueError as exc:
            findings.append(("POD101", f"{key}: {exc}", False))
            continue
        if path and not path.is_file():
            findings.append(("POD101", f"{key} 文件不存在", False))
        elif path:
            paths[key] = path
    raw = paths.get("transcript_path")
    result = audit(raw) if raw else None
    if result:
        findings.extend(("POD102", message, False) for message in result["errors"])
        findings.extend(("POD103", message, True) for message in result["warnings"])
    ref = str(metadata.get("transcript_source_ref") or "")
    receipt_path = paths.get("transcript_audit_path")
    private = metadata.get("transcript_visibility") == "private"
    if private and (metadata.get("transcript_path") not in (None, "", "null", "~")
                    or metadata.get("polished_transcript_path") not in (None, "", "null", "~")):
        findings.append(("POD107", "private 转写不应声明公开全文路径", False))
    if ref or receipt_path or private:
        if not receipt_path:
            findings.append(("POD107", "私有来源/ref 缺少 transcript_audit_path 收据", False))
        else:
            try:
                receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
                errors = validate_receipt(receipt, source_ref=ref, source_url=str(metadata.get("source_url") or ""))
            except (OSError, ValueError) as exc:
                receipt, errors = None, [f"无法解析转写收据：{type(exc).__name__}"]
            findings.extend(("POD107", error, False) for error in errors)
            if not errors and result:
                if any(receipt["audit"][key] != result[key] for key in RECEIPT_METRICS):
                    findings.append(("POD108", "收据与当前源文件实测值不一致", False))
            elif not errors:
                result = receipt["audit"]
                findings.append(("POD109", "receipt_only：仅核对收据结构与来源绑定；私有源未在本机重验", True))
                if result["malformed_lines"] or result["tail_gap_seconds"] > 30:
                    findings.append(("POD103", "收据记录了非时间戳行或尾部异常间隔，需人工复核", True))
    if result:
        for field, measured, tolerance in (
            ("duration_seconds", result["duration_seconds"], DURATION_TOL_S),
            ("transcript_segments", result["segments"], 0),
        ):
            if metadata.get(field) is None:
                continue
            try:
                value = int(str(metadata[field]))
                if value < 0:
                    raise ValueError
            except ValueError:
                findings.append(("POD104", f"{field} 不是非负整数", False))
                continue
            if measured is not None and abs(value - measured) > tolerance:
                findings.append(("POD104", f"{field}={value} 与来源指标 {measured} 不一致（容差 {tolerance}）", False))
    polished = paths.get("polished_transcript_path")
    declaration = re.search(r"约 raw 的 ([\d.]+)%", text)
    if raw and polished:
        raw_hanzi = len(re.findall(r"[一-鿿]", raw.read_text(encoding="utf-8", errors="replace")))
        polished_hanzi = len(re.findall(r"[一-鿿]", polished.read_text(encoding="utf-8", errors="replace")))
        if raw_hanzi:
            ratio = polished_hanzi / raw_hanzi * 100
            if declaration:
                try:
                    declared = float(declaration.group(1))
                    if abs(declared - ratio) > COMPRESS_TOL_PP:
                        findings.append(("POD105", f"压缩比声明 {declared}% vs 文件实测 {ratio:.1f}%（容差 {COMPRESS_TOL_PP}pp）", False))
                except ValueError:
                    findings.append(("POD105", "压缩比声明不是有效数字", False))
            if ratio < 10 or ratio > 110:
                findings.append(("POD106", f"汉字压缩比 {ratio:.1f}%，需人工检查是否遗漏或扩写；不自动判定", True))
        elif declaration:
            findings.append(("POD106", "raw 无汉字，不能用汉字数核验压缩比声明", True))
    elif declaration:
        findings.append(("POD106", "缺少可读取的 raw/polished，压缩比声明未核验", True))
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=pathlib.Path)
    parser.add_argument("--max-consecutive", type=int, default=MAX_CONSECUTIVE)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--public-receipt", action="store_true", help="仅向 stdout 输出白名单收据，不含原文/路径")
    parser.add_argument("--source-url", help="公开收据绑定的公开节目 URL")
    args = parser.parse_args(argv)
    if args.max_consecutive < 1:
        parser.error("--max-consecutive 必须为正整数")
    if args.public_receipt and (len(args.files) != 1 or not args.source_url or args.max_consecutive != MAX_CONSECUTIVE):
        parser.error("公开收据要求一个源文件、--source-url，以及默认重复阈值")
    try:
        results = [audit(path.resolve(), args.max_consecutive) for path in args.files]
        if args.public_receipt:
            print(json.dumps(public_receipt(results[0], args.source_url), ensure_ascii=False, indent=2))
        elif args.json:
            print(json.dumps({"schema_version": 1, "results": results}, ensure_ascii=False, indent=2))
        else:
            for item in results:
                status = "PASS" if item["ok"] else "FAIL"
                print(f"{status} {item['path']}｜segments={item['segments']}｜duration={item['duration_seconds']}s｜max_repeat={item['max_consecutive_identical']}")
                for warning in item["warnings"]:
                    print(f"  WARN {warning}")
                for error in item["errors"]:
                    print(f"  ERROR {error}")
    except (OSError, ValueError) as exc:
        # 不把本机路径/原文带入准备公开的 stdout 收据。
        parser.exit(1, f"转写审计失败：{type(exc).__name__}\n")
    return 0 if all(item["ok"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
