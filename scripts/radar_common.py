"""Shared transport and pure helpers for the blog and podcast radars."""

from __future__ import annotations

import datetime as dt
import email.utils
import gzip
import hashlib
import html
import io
import json
import pathlib
import re
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections.abc import Callable
from typing import Any


class RadarError(RuntimeError):
    pass


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            temporary = pathlib.Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_set_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def set_dotted(target: dict[str, Any], assignment: str) -> None:
    if "=" not in assignment:
        raise RadarError(f"--set 需要 key=value：{assignment}")
    path, raw = assignment.split("=", 1)
    keys = [key for key in path.split(".") if key]
    if not keys or len(keys) != len(path.split(".")):
        raise RadarError("--set key 不能为空")
    cursor = target
    for key in keys[:-1]:
        child = cursor.get(key)
        if child is None:
            child = {}
            cursor[key] = child
        if not isinstance(child, dict):
            raise RadarError(f"无法进入非 object 字段：{key}")
        cursor = child
    cursor[keys[-1]] = parse_set_value(raw)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def clean_text(value: str | None, *, preserve_breaks: bool = False) -> str:
    if not value:
        return ""
    value = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", value, flags=re.S)
    if preserve_breaks:
        value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(html.unescape(value))).strip()


def trim_text(value: str, size: int) -> str:
    return value if len(value) <= size else value[: size - 1].rstrip() + "…"


def normalize_url(url: str, denied_params: set[str]) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url.strip())
    query = []
    for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        lower = key.lower()
        if lower.startswith("utm_") or lower in denied_params:
            continue
        query.append((key, value))
    path = parsed.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, urllib.parse.urlencode(sorted(query)), "")
    )


def title_fingerprint(title: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", title.lower())


def parse_standard_date(text: str) -> dt.datetime | None:
    try:
        parsed = email.utils.parsedate_to_datetime(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except (TypeError, ValueError, OverflowError):
        pass
    for candidate in re.findall(r"\d{4}-\d{1,2}-\d{1,2}(?:[T ][0-9:.+-Z]+)?", text):
        try:
            parsed = dt.datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
        except ValueError:
            continue
    return None


def request_id(source_id: str, payload: str, *, now: dt.datetime | None = None) -> str:
    hour = (now or now_utc()).strftime("%Y%m%d%H")
    identity = json.dumps([source_id, hour, payload], ensure_ascii=False)
    digest = hashlib.sha256(identity.encode()).hexdigest()[:32]
    return f"req_{digest}"


def run_eacli(args: list[str], timeout: int = 60, error_limit: int = 600) -> str:
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        raise RadarError("找不到 eacli") from exc
    except subprocess.TimeoutExpired as exc:
        raise RadarError(f"eacli 超时（{timeout}s）") from exc
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise RadarError(message[:error_limit])
    return completed.stdout


def parse_inner_result(stdout: str) -> Any:
    payload = json.loads(stdout)
    if not payload.get("ok"):
        error = payload.get("error") or payload.get("result", {}).get("error") or "eacli 调用失败"
        raise RadarError(str(error))
    raw = payload.get("result", {}).get("result")
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw
    return raw


def http_get(
    url: str,
    *,
    timeout: int,
    user_agent: str,
    accept: str,
    max_bytes: int,
    max_decompressed_bytes: int,
    retry_on: Callable[[Exception], bool] | None = None,
) -> str:
    for attempt in range(2):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": user_agent,
                "Accept": accept,
                "Accept-Encoding": "identity",
                "Connection": "close",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read(max_bytes + 1)
            if len(payload) > max_bytes:
                raise RadarError(f"响应超过 {max_bytes} bytes 上限")
            if payload.startswith(b"\x1f\x8b"):
                with gzip.GzipFile(fileobj=io.BytesIO(payload)) as compressed:
                    payload = compressed.read(max_decompressed_bytes + 1)
                if len(payload) > max_decompressed_bytes:
                    raise RadarError(f"gzip 解压后超过 {max_decompressed_bytes} bytes 上限")
            return payload.decode("utf-8", errors="replace")
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if attempt or retry_on is None or not retry_on(exc):
                raise
    raise AssertionError("unreachable")


def xml_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1].lower()


def xml_elements(text: str, names: set[str]) -> list[ET.Element] | None:
    try:
        root = ET.fromstring(text)
    except (ET.ParseError, ValueError):
        return None
    return [element for element in root.iter() if xml_name(element) in names]


def xml_text(element: ET.Element, names: set[str]) -> str:
    for child in element.iter():
        if child is not element and xml_name(child) in names:
            return "".join(child.itertext())
    return ""


def xml_attribute(element: ET.Element, names: set[str], attribute: str) -> str:
    for child in element.iter():
        if child is not element and xml_name(child) in names:
            value = child.get(attribute)
            if value:
                return value
    return ""


def output(value: Any, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value, end="" if str(value).endswith("\n") else "\n")
