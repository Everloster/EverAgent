#!/usr/bin/env python3
"""SOTA AI 技术播客雷达：查询近期更新并维护渠道注册表。"""

from __future__ import annotations

import argparse
import concurrent.futures
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
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


PODCAST_ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = PODCAST_ROOT / "sources" / "ai-tech-podcasts.json"
REPORTS_DIR = PODCAST_ROOT / "reports"
UA = "Mozilla/5.0 (compatible; EverAgentAITechPodcastRadar/1.0)"

TIERS = {"core", "watch"}
LANGUAGES = {"zh", "en"}
SOURCE_CLASSES = {"independent", "community", "media", "lab", "vendor", "investor"}

TOPIC_LANES = {
    "model_research": {
        "ai model", "foundation model", "llm", "language model", "transformer", "reasoning",
        "pretraining", "pre-training", "post-training", "fine-tuning", "finetuning",
        "reinforcement learning", "scaling", "distillation", "multimodal", "world model",
        "模型", "大模型", "语言模型", "推理", "预训练", "后训练", "微调", "强化学习",
        "蒸馏", "多模态", "世界模型",
    },
    "agent_engineering": {
        "agent", "agents", "agentic", "harness", "tool use", "tool calling", "mcp",
        "coding agent", "claude code", "codex", "memory", "context engineering", "sandbox",
        "智能体", "工具调用", "上下文工程", "记忆", "沙箱", "编程智能体",
    },
    "systems_infra": {
        "inference", "serving", "distributed", "latency", "throughput", "kv cache",
        "vllm", "sglang", "compiler", "kernel", "cuda", "pytorch", "jax", "gpu cloud",
        "推理系统", "推理服务", "部署", "分布式", "延迟", "吞吐", "缓存", "编译器",
        "算子", "基础设施",
    },
    "hardware": {
        "gpu", "tpu", "npu", "chip", "semiconductor", "accelerator", "hbm", "sram",
        "cuda", "rocm", "trainium", "芯片", "半导体", "加速器", "显存", "算力",
    },
    "robotics": {
        "robot", "robotics", "embodied", "autonomous driving", "physical ai", "sim-to-real",
        "具身", "机器人", "自动驾驶", "物理 ai", "仿真到现实",
    },
    "evaluation_safety": {
        "eval", "evaluation", "benchmark", "safety", "security", "alignment", "red team",
        "interpretability", "verification", "hallucination", "评测", "基准", "安全", "对齐",
        "红队", "可解释", "验证", "幻觉",
    },
    "applied_ai": {
        "ai application", "ai product", "ai workflow", "enterprise ai", "ai developer tools",
        "ai deployment", "ai production", "ai应用", "人工智能应用", "ai产品", "ai工作流",
        "企业 ai", "企业ai", "ai开发者工具", "ai部署", "ai落地", "大模型落地",
    },
    "ai_industry": {
        "ai startup", "ai founder", "ai venture", "ai market", "ai economics",
        "ai business model", "ai strategy", "frontier lab", "ai lab", "ai创业", "人工智能创业",
        "ai创始人", "ai投资", "ai市场", "ai商业模式", "ai战略", "ai实验室", "大模型公司",
        "ai产业", "人工智能产业",
    },
    "science": {
        "science", "biology", "protein", "drug discovery", "medicine", "healthcare", "math",
        "physics", "chemistry", "weather", "科学", "生物", "蛋白质", "药物", "医学",
        "医疗", "数学", "物理", "化学", "气象",
    },
}

MECHANISM_TERMS = {
    "architecture", "mechanism", "algorithm", "method", "training", "post-training",
    "inference", "attention", "memory", "context", "agent", "harness", "reasoning",
    "scaling", "compiler", "kernel", "distributed", "架构", "机制", "算法", "训练",
    "推理", "注意力", "记忆", "上下文", "智能体", "编译器", "算子", "分布式",
}
EVIDENCE_TERMS = {
    "benchmark", "experiment", "dataset", "results", "ablation", "failure", "latency",
    "throughput", "accuracy", "performance", "study", "analysis", "evaluation", "trial",
    "基准", "实验", "数据集", "结果", "消融", "失败", "延迟", "吞吐", "准确率",
    "性能", "研究", "分析", "评测",
}
ARTIFACT_TERMS = {
    "paper", "open source", "open-source", "github", "code", "repository", "framework",
    "model card", "checkpoint", "technical report", "论文", "开源", "代码", "仓库",
    "框架", "模型卡", "权重", "技术报告",
}
NEWS_TERMS = {
    "weekly", "news", "roundup", "recap", "headlines", "this week", "周报", "新闻",
    "盘点", "速递", "快讯",
}


class RadarError(RuntimeError):
    pass


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def load_json(path: pathlib.Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
        temporary = pathlib.Path(handle.name)
    temporary.replace(path)


def validate_registry(registry: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["根节点必须是 object"]
    if registry.get("schema_version") != 1:
        errors.append("schema_version 必须为 1")
    sources = registry.get("sources")
    if not isinstance(sources, list):
        return errors + ["sources 必须为 array"]
    seen: set[str] = set()
    for index, source in enumerate(sources):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label} 必须为 object")
            continue
        source_id = source.get("id")
        if not isinstance(source_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", source_id):
            errors.append(f"{label}.id 必须是小写连字符 ID")
        elif source_id in seen:
            errors.append(f"重复 source id：{source_id}")
        else:
            seen.add(source_id)
        for key in ("name", "homepage", "feed_url", "apple_url", "why"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                errors.append(f"{label}.{key} 必须为非空字符串")
        for key in ("homepage", "feed_url", "apple_url"):
            value = source.get(key, "")
            if value and not re.match(r"^https?://", value):
                errors.append(f"{label}.{key} 必须是 http(s) URL")
        if source.get("tier") not in TIERS:
            errors.append(f"{label}.tier 必须是 core/watch")
        if source.get("language") not in LANGUAGES:
            errors.append(f"{label}.language 必须是 zh/en")
        if source.get("source_class") not in SOURCE_CLASSES:
            errors.append(f"{label}.source_class 无效")
        if not isinstance(source.get("enabled"), bool):
            errors.append(f"{label}.enabled 必须为 boolean")
        if not isinstance(source.get("require_topic"), bool):
            errors.append(f"{label}.require_topic 必须为 boolean")
        if source.get("topic_match", "full") not in {"full", "title"}:
            errors.append(f"{label}.topic_match 必须是 full/title")
        topics = source.get("topics")
        if not isinstance(topics, list) or not all(isinstance(value, str) for value in topics):
            errors.append(f"{label}.topics 必须为 string array")
        else:
            unknown = sorted(set(topics) - set(TOPIC_LANES))
            if unknown:
                errors.append(f"{label}.topics 含未知主题：{', '.join(unknown)}")
    defaults = registry.get("defaults")
    if not isinstance(defaults, dict):
        errors.append("defaults 必须为 object")
    return errors


def load_registry(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        raise RadarError(f"渠道注册表不存在：{path}")
    value = load_json(path)
    errors = validate_registry(value)
    if errors:
        raise RadarError("渠道注册表无效：" + "；".join(errors))
    return value


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", value, flags=re.S)
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(html.unescape(value))
    return re.sub(r"\s+", " ", value).strip()


def trim(value: str, size: int = 420) -> str:
    value = clean_text(value)
    return value if len(value) <= size else value[: size - 1].rstrip() + "…"


def parse_date(value: str | None, reference: dt.datetime | None = None) -> dt.datetime | None:
    if not value:
        return None
    reference = reference or now_utc()
    text = clean_text(value)
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
    relative = re.search(r"\b(\d+)\s*([hmwd])\s+ago\b", text, re.I)
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2).lower()
        delta = {
            "h": dt.timedelta(hours=amount),
            "d": dt.timedelta(days=amount),
            "w": dt.timedelta(weeks=amount),
            "m": dt.timedelta(minutes=amount),
        }[unit]
        return reference - delta
    if re.search(r"\btoday\b", text, re.I):
        return reference
    if re.search(r"\byesterday\b", text, re.I):
        return reference - dt.timedelta(days=1)
    month = re.search(
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2})(?:,\s*(\d{4}))?\b",
        text,
        re.I,
    )
    if month:
        year = int(month.group(3) or reference.year)
        try:
            parsed = dt.datetime.strptime(
                f"{month.group(1)[:3].title()} {month.group(2)} {year}", "%b %d %Y"
            ).replace(tzinfo=dt.timezone.utc)
            if not month.group(3) and parsed > reference + dt.timedelta(days=30):
                parsed = parsed.replace(year=year - 1)
            return parsed
        except ValueError:
            pass
    return None


def normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url.strip())
    query = []
    for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        lower = key.lower()
        if lower.startswith("utm_") or lower in {"source", "ref", "uo", "mt"}:
            continue
        query.append((key, value))
    path = parsed.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, urllib.parse.urlencode(sorted(query)), "")
    )


def title_fingerprint(title: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", title.lower())


def parse_duration_seconds(value: str | None) -> int | None:
    if not value:
        return None
    value = clean_text(value)
    try:
        if ":" not in value:
            return int(float(value))
        parts = [int(part) for part in value.split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        if len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except ValueError:
        return None
    return None


def format_duration(seconds: int | None) -> str:
    if seconds is None:
        return "时长未知"
    if seconds >= 3600:
        return f"{seconds // 3600}h{(seconds % 3600) // 60:02d}m"
    return f"{seconds // 60}m"


def xml_field(block: str, names: list[str]) -> str:
    for name in names:
        match = re.search(
            rf"<{re.escape(name)}\b[^>]*>(.*?)</{re.escape(name)}>",
            block,
            re.S | re.I,
        )
        if match:
            return clean_text(match.group(1))
    return ""


def parse_feed_text(text: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = re.findall(r"<item\b[^>]*>(.*?)</item>", text, re.S | re.I)
    atom = False
    if not blocks:
        blocks = re.findall(r"<entry\b[^>]*>(.*?)</entry>", text, re.S | re.I)
        atom = True
    episodes: list[dict[str, Any]] = []
    for block in blocks[:250]:
        title = xml_field(block, ["title"])
        if atom:
            link_match = re.search(r"<link\b[^>]*href=[\"']([^\"']+)", block, re.I)
            link = html.unescape(link_match.group(1)) if link_match else ""
            published_raw = xml_field(block, ["published", "updated"])
            summary = xml_field(block, ["summary", "content"])
            guid = xml_field(block, ["id"])
        else:
            link = xml_field(block, ["link"])
            guid = xml_field(block, ["guid"])
            if not link and guid.startswith("http"):
                link = guid
            published_raw = xml_field(block, ["pubDate", "dc:date", "date"])
            summary = xml_field(block, ["description", "content:encoded"])
        enclosure = re.search(r"<enclosure\b[^>]*url=[\"']([^\"']+)", block, re.I)
        audio_url = html.unescape(enclosure.group(1)) if enclosure else ""
        duration = parse_duration_seconds(xml_field(block, ["itunes:duration", "duration"]))
        author = xml_field(block, ["itunes:author", "dc:creator", "author"])
        if not title:
            continue
        episodes.append(
            {
                "title": title,
                "url": normalize_url(link or source["homepage"]),
                "audio_url": audio_url,
                "guid": guid,
                "published_at": parse_date(published_raw).isoformat() if parse_date(published_raw) else None,
                "duration_seconds": duration,
                "author": author,
                "summary": trim(summary),
                "discovered_via": "rss",
                "date_confidence": "feed" if published_raw else "unknown",
            }
        )
    return episodes


def first_relevant_paragraph(segment: str) -> str:
    for paragraph in re.split(r"\n\s*\n", segment):
        value = clean_text(paragraph)
        if len(value) < 80:
            continue
        if value.lower().startswith("xml version"):
            continue
        if "audio format of posts" in value.lower():
            continue
        return trim(value)
    return ""


def title_from_slug(url: str) -> str:
    slug = pathlib.PurePosixPath(urllib.parse.urlsplit(url).path.rstrip("/")).name
    value = re.sub(r"[-_]+", " ", urllib.parse.unquote(slug)).strip()
    return value[:1].upper() + value[1:] if value else url


def parse_substack_flattened(text: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    boundary = re.compile(
        r"\]\]>(?P<url>https?://[^\s]+?)substack:post:(?P<guid>\d+)"
        r"(?P<date>[A-Z][a-z]{2},\s+\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}\s+\d{2}:\d{2}"
        r"(?::\d{2})?(?:\s+[A-Z]{2,4})?)"
    )
    matches = list(boundary.finditer(text))
    episodes: list[dict[str, Any]] = []
    segment_start = 0
    for match in matches[:100]:
        link = match.group("url")
        published = parse_date(match.group("date"))
        episodes.append(
            {
                "title": title_from_slug(link),
                "url": normalize_url(link),
                "audio_url": "",
                "guid": "substack:" + match.group("guid"),
                "published_at": published.isoformat() if published else None,
                "duration_seconds": None,
                "author": "",
                "summary": first_relevant_paragraph(text[segment_start:match.start()]),
                "discovered_via": "eacli_flat_feed",
                "date_confidence": "feed_flattened",
                "metadata_lossy": True,
            }
        )
        segment_start = match.end()
    return episodes


def parse_blubrry_flattened(text: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    lines = [line.strip() for line in text.replace("\\n", "\n").splitlines()]
    episodes: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, title in enumerate(lines[:-1]):
        if not title or title.startswith(("http://", "https://")):
            continue
        link_index = index + 1
        while link_index < len(lines) and not lines[link_index]:
            link_index += 1
        if link_index >= len(lines) or not lines[link_index].startswith("http"):
            continue
        link = lines[link_index]
        if any(marker in link for marker in ("assets.blubrry.com", "feeds.blubrry.com", ".mp3")):
            continue
        date_index = None
        published = None
        for candidate in range(link_index + 1, min(len(lines), link_index + 10)):
            parsed = parse_date(lines[candidate])
            if parsed is not None:
                date_index = candidate
                published = parsed
                break
        if published is None or date_index is None:
            continue
        normalized = normalize_url(link)
        if normalized in seen:
            continue
        seen.add(normalized)
        summary = ""
        for candidate in range(date_index + 1, min(len(lines), date_index + 8)):
            value = clean_text(lines[candidate])
            if len(value) >= 40 and not value.startswith("http"):
                summary = trim(value)
                break
        duration = None
        for candidate in range(date_index + 1, min(len(lines), date_index + 18)):
            duration = parse_duration_seconds(lines[candidate])
            if duration is not None and ":" in lines[candidate]:
                break
            duration = None
        episodes.append(
            {
                "title": clean_text(title),
                "url": normalized,
                "audio_url": "",
                "guid": normalized,
                "published_at": published.isoformat(),
                "duration_seconds": duration,
                "author": "",
                "summary": summary,
                "discovered_via": "eacli_flat_feed",
                "date_confidence": "feed_flattened",
                "metadata_lossy": False,
            }
        )
    return episodes


def parse_flattened_feed(text: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    host = (urllib.parse.urlsplit(source["feed_url"]).hostname or "").lower()
    if host == "api.substack.com":
        return parse_substack_flattened(text, source)
    if host == "feeds.blubrry.com":
        return parse_blubrry_flattened(text, source)
    return []


def parse_inner_result(stdout: str) -> Any:
    payload = json.loads(stdout)
    if not payload.get("ok"):
        error = payload.get("error") or payload.get("result", {}).get("error") or "eacli 调用失败"
        raise RadarError(str(error))
    value = payload.get("result", {}).get("result")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def run_eacli(args: list[str], timeout: int = 75) -> str:
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RadarError("找不到 eacli") from exc
    except subprocess.TimeoutExpired as exc:
        raise RadarError(f"eacli 超时（{timeout}s）") from exc
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise RadarError(message[:600])
    return completed.stdout


def prepare_token_plan() -> dict[str, Any]:
    run_eacli(["eacli", "tokenplan", "catalog", "--json"], timeout=60)
    stdout = run_eacli(
        ["eacli", "tool", "select", "--capability", "web.read", "--device", "auto", "--json"],
        timeout=60,
    )
    payload = json.loads(stdout)
    selected = payload.get("result", {}).get("selected", {})
    return {
        "catalog": "ok",
        "web.read": {
            "provider": selected.get("provider"),
            "device": selected.get("device"),
            "backend": selected.get("backend"),
        },
    }


def request_id(source_id: str, url: str) -> str:
    digest = hashlib.sha256(url.encode()).hexdigest()[:10]
    hour = now_utc().strftime("%Y%m%d%H")
    return f"ai-podcast-radar-{source_id}-{hour}-{digest}"


def eacli_web_read(url: str, source_id: str, timeout: int = 35) -> Any:
    encoded = json.dumps({"url": url}, ensure_ascii=False, separators=(",", ":"))
    stdout = run_eacli(
        [
            "eacli", "tool", "invoke", "--capability", "web.read",
            "--input-json", encoded, "--device", "auto",
            "--request-id", request_id(source_id, url), "--json",
        ],
        timeout=timeout,
    )
    return parse_inner_result(stdout)


def extract_json_string_fragment(raw: str, key: str) -> str:
    marker = json.dumps(key) + ":"
    start = raw.find(marker)
    if start < 0:
        return ""
    index = start + len(marker)
    while index < len(raw) and raw[index].isspace():
        index += 1
    if index >= len(raw) or raw[index] != '"':
        return ""
    index += 1
    result: list[str] = []
    escapes = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
    while index < len(raw):
        char = raw[index]
        if char == '"':
            break
        if char != "\\":
            result.append(char)
            index += 1
            continue
        index += 1
        if index >= len(raw):
            break
        escaped = raw[index]
        if escaped == "u" and index + 4 < len(raw):
            code = raw[index + 1:index + 5]
            try:
                result.append(chr(int(code, 16)))
                index += 5
                continue
            except ValueError:
                pass
        result.append(escapes.get(escaped, escaped))
        index += 1
    return "".join(result)


def extract_read_content(value: Any) -> tuple[str, bool]:
    truncated = False
    candidates: list[str] = []

    def walk(node: Any) -> None:
        nonlocal truncated
        if isinstance(node, dict):
            truncated = truncated or bool(node.get("truncated"))
            for key in ("content", "text", "preview"):
                child = node.get(key)
                if isinstance(child, str):
                    candidates.append(child)
            for child in node.values():
                if isinstance(child, (dict, list)):
                    walk(child)
                elif isinstance(child, str) and child.lstrip().startswith("{"):
                    try:
                        walk(json.loads(child))
                    except json.JSONDecodeError:
                        pass
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, str):
            candidates.append(node)
            if node.lstrip().startswith("{"):
                fragment = extract_json_string_fragment(node, "content")
                if fragment:
                    candidates.append(fragment)
                try:
                    walk(json.loads(node))
                except json.JSONDecodeError:
                    pass

    walk(value)
    if not candidates:
        return "", truncated
    xml_candidates = [item for item in candidates if "<item" in item or "<entry" in item]
    decoded_candidates = [item for item in candidates if not item.lstrip().startswith(("{", "["))]
    return max(xml_candidates or decoded_candidates or candidates, key=len), truncated


def http_get(url: str, timeout: int = 10) -> str:
    last_error: Exception | None = None
    for attempt in range(2):
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": UA,
                "Accept": "application/rss+xml,application/atom+xml,application/xml,text/xml,*/*;q=0.5",
                "Accept-Encoding": "identity",
                "Connection": "close",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read(4_000_000)
                if payload.startswith(b"\x1f\x8b"):
                    with gzip.GzipFile(fileobj=io.BytesIO(payload)) as compressed:
                        payload = compressed.read(6_000_000)
                return payload.decode("utf-8", errors="replace")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt:
                break
    assert last_error is not None
    raise last_error


def parse_apple_date_token(value: str) -> dt.datetime | None:
    token = clean_text(value)
    if not token or token.startswith("![Image"):
        return None
    patterns = (
        r"\d+\s*[hmwd]\s+ago",
        r"today",
        r"yesterday",
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s*\d{4})?",
        r"\d{4}-\d{1,2}-\d{1,2}",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, token, re.I)
        if match:
            return parse_date(match.group(0))
    numeric = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", token)
    if numeric:
        try:
            return dt.datetime(
                int(numeric.group(3)), int(numeric.group(1)), int(numeric.group(2)),
                tzinfo=dt.timezone.utc,
            )
        except ValueError:
            return None
    return None


def parse_apple_duration(value: str) -> int | None:
    text = clean_text(value).lower()
    hour = re.fullmatch(r"(\d+)h(?:\s*(\d+)m)?", text)
    if hour:
        return int(hour.group(1)) * 3600 + int(hour.group(2) or 0) * 60
    minute = re.fullmatch(r"(\d+)\s*(?:m|min|mins|minutes)", text)
    if minute:
        return int(minute.group(1)) * 60
    return None


def parse_apple_page(text: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    lines = text.replace("\\n", "\n").splitlines()
    section_start = next(
        (index + 1 for index, line in enumerate(lines) if line.strip().lower() == "## episodes"),
        0,
    )
    section_end = next(
        (
            index for index in range(section_start, len(lines))
            if lines[index].strip().startswith("## ")
        ),
        len(lines),
    )
    marker_indexes = [
        index for index in range(section_start, section_end)
        if re.match(r"^\s*\d+\.\s+", lines[index])
    ]
    episodes: list[dict[str, Any]] = []
    for position, marker_index in enumerate(marker_indexes[:40]):
        end = marker_indexes[position + 1] if position + 1 < len(marker_indexes) else section_end
        marker = re.match(r"^\s*\d+\.\s+(.*?)\s*$", lines[marker_index])
        marker_value = marker.group(1) if marker else ""
        published = parse_apple_date_token(marker_value)
        heading_index = None
        title = ""
        for index in range(marker_index + 1, end):
            inline_heading = re.match(r"^\s*###\s+(.+?)\s*$", lines[index])
            if inline_heading:
                heading_index = index
                title = clean_text(inline_heading.group(1))
                break
            if lines[index].strip() == "###":
                heading_index = index
                title_index = index + 1
                while title_index < end and not lines[title_index].strip():
                    title_index += 1
                if title_index < end:
                    title = clean_text(lines[title_index])
                break
        if not title or heading_index is None:
            continue
        if published is None:
            for line in reversed(lines[marker_index + 1:heading_index]):
                published = parse_apple_date_token(line)
                if published is not None:
                    break
        body_lines: list[str] = []
        duration = None
        for line in lines[heading_index + 1:end]:
            stripped = line.strip()
            if stripped.startswith("![Image"):
                continue
            parsed_duration = parse_apple_duration(stripped)
            if parsed_duration is not None:
                duration = parsed_duration
                continue
            if stripped == title:
                continue
            body_lines.append(stripped)
        summary = trim(" ".join(body_lines))
        episodes.append(
            {
                "title": title,
                "url": normalize_url(source["apple_url"]),
                "audio_url": "",
                "guid": f"apple:{source['id']}:{title_fingerprint(title)}",
                "published_at": published.isoformat() if published else None,
                "duration_seconds": duration,
                "author": "",
                "summary": summary,
                "discovered_via": "apple_page",
                "date_confidence": "apple_listing" if published else "unknown",
            }
        )
    return episodes


def fetch_episodes(source: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], str, bool]:
    notes: list[str] = []
    errors: list[str] = []
    try:
        result = eacli_web_read(source["feed_url"], source["id"] + "-feed", timeout=20)
        content, truncated = extract_read_content(result)
        episodes = parse_feed_text(content, source)
        if episodes and not truncated:
            return episodes, notes, "eacli_feed", False
        flattened = parse_flattened_feed(content, source)
        if flattened:
            lossy = any(item.get("metadata_lossy") for item in flattened)
            if lossy:
                notes.append("eacli web.read 清洗了 Substack XML，按官方单集 URL、日期与 slug 恢复元数据")
            return flattened, notes, "eacli_flat_feed", lossy
        reason = "返回内容被截断" if truncated else "未保留可解析 RSS/Atom XML"
        notes.append(f"eacli web.read {reason}，使用只读 HTTP XML fallback")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"eacli feed：{exc}")
        notes.append(f"eacli web.read 读取 feed 失败，使用只读 HTTP XML fallback：{exc}")
    try:
        content = http_get(source["feed_url"])
        episodes = parse_feed_text(content, source)
        if episodes:
            return episodes, notes, "http_feed", False
        errors.append("HTTP feed 未识别到条目")
        notes.append("只读 HTTP feed 未识别到条目，使用 Apple Podcasts 备用入口")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"HTTP feed：{exc}")
        notes.append(f"只读 HTTP feed 失败，使用 Apple Podcasts 备用入口：{exc}")
    try:
        result = eacli_web_read(source["apple_url"], source["id"] + "-apple", timeout=35)
        content, _ = extract_read_content(result)
        episodes = parse_apple_page(content, source)
        if episodes:
            return episodes, notes, "apple_page", True
        errors.append("Apple 页面未识别到单集")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"Apple 页面：{exc}")
    raise RadarError("；".join(errors))


def normalized_search_text(value: str) -> str:
    return re.sub(r"[-_/]+", " ", value.lower())


def term_present(text: str, term: str) -> bool:
    needle = normalized_search_text(term)
    if needle.isascii() and len(needle) <= 3 and " " not in needle:
        return re.search(rf"\b{re.escape(needle)}\b", text) is not None
    return needle in text


def matched_terms(text: str, terms: set[str] | list[str]) -> list[str]:
    normalized = normalized_search_text(text)
    return sorted(term for term in terms if term_present(normalized, term))


def topic_lanes(text: str) -> list[str]:
    return sorted(lane for lane, terms in TOPIC_LANES.items() if matched_terms(text, terms))


def unquote_frontmatter_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        value = value[1:-1]
    return value.strip()


def load_studied_index() -> tuple[dict[str, str], dict[str, str]]:
    urls: dict[str, str] = {}
    titles: dict[str, str] = {}
    url_re = re.compile(r"https?://[^\s\"'<>)（）」』\u4e00-\u9fff]+")
    for path in sorted(REPORTS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter = re.match(r"^---\n(.*?)\n---", text, re.S)
        block = frontmatter.group(1) if frontmatter else ""
        relative = str(path.relative_to(PODCAST_ROOT.parent))
        for url in url_re.findall(block):
            urls[normalize_url(url)] = relative
        for key in ("episode", "title"):
            match = re.search(rf"(?m)^{key}:\s*(.+?)\s*$", block)
            if match:
                fingerprint = title_fingerprint(unquote_frontmatter_value(match.group(1)))
                if fingerprint:
                    titles[fingerprint] = relative
    return urls, titles


def match_studied_title(title: str, studied_titles: dict[str, str]) -> str | None:
    """匹配报告标题，兼容 Apple 给旧单集追加 emoji、嘉宾与职位的情况。"""
    fingerprint = title_fingerprint(title)
    exact = studied_titles.get(fingerprint)
    if exact:
        return exact
    matches: list[tuple[int, str]] = []
    for studied_fingerprint, report_path in studied_titles.items():
        shorter = min(len(fingerprint), len(studied_fingerprint))
        if shorter < 32:
            continue
        if studied_fingerprint in fingerprint or fingerprint in studied_fingerprint:
            matches.append((shorter, report_path))
    return max(matches, default=(0, ""))[1] or None


def canonicalize_apple_studied_date(
    episode: dict[str, Any], studied_titles: dict[str, str]
) -> dict[str, Any]:
    """Apple 会把重发/重编排日期显示成“刚更新”；已有报告日期优先代表首发日。"""
    if episode.get("discovered_via") != "apple_page":
        return episode
    report_path = match_studied_title(episode.get("title", ""), studied_titles)
    if not report_path:
        return episode
    match = re.search(r"(?:^|/)(\d{4}-\d{2}-\d{2})_", report_path)
    if not match:
        return episode
    canonical = parse_date(match.group(1))
    listing = parse_date(episode.get("published_at"))
    if canonical is None or listing is None or abs((listing - canonical).days) <= 1:
        return episode
    normalized = dict(episode)
    normalized["apple_listing_published_at"] = episode.get("published_at")
    normalized["published_at"] = canonical.isoformat()
    normalized["date_confidence"] = "studied_report_filename"
    normalized["date_note"] = "Apple 备用页显示重发/列表更新时间；首发日按已有报告文件名校正"
    normalized["studied_report_hint"] = report_path
    return normalized


def classify_episode(
    source: dict[str, Any], episode: dict[str, Any], global_excludes: list[str],
    studied_urls: dict[str, str], studied_titles: dict[str, str],
) -> dict[str, Any] | None:
    text = f"{episode['title']} {episode.get('summary', '')}"
    lower_title = normalized_search_text(episode["title"])
    if any(term_present(lower_title, term) for term in global_excludes):
        return None
    topic_text = episode["title"] if source.get("topic_match", "full") == "title" else text
    lanes = topic_lanes(topic_text)
    mechanism = matched_terms(text, MECHANISM_TERMS)
    evidence = matched_terms(text, EVIDENCE_TERMS)
    artifacts = matched_terms(text, ARTIFACT_TERMS)
    categories = sum(bool(values) for values in (mechanism, evidence, artifacts))
    if source.get("require_topic") and not lanes:
        return None
    if source["tier"] == "watch" and not lanes and categories == 0:
        return None
    published = parse_date(episode.get("published_at"))
    recency_bonus = 0
    if published:
        recency_bonus = max(0, 14 - max(0, (now_utc() - published).days))
    duration = episode.get("duration_seconds")
    duration_bonus = 3 if isinstance(duration, int) and duration >= 45 * 60 else 0
    source_bonus = 4 if source["source_class"] == "lab" else 0
    news_penalty = 5 if matched_terms(text, NEWS_TERMS) and categories < 2 else 0
    score = (
        (44 if source["tier"] == "core" else 24)
        + recency_bonus
        + categories * 8
        + min(12, len(lanes) * 3)
        + duration_bonus
        + source_bonus
        - news_penalty
    )
    if (
        categories >= 2
        or (duration_bonus and bool(mechanism or artifacts))
        or (source["source_class"] == "lab" and categories)
    ):
        kind = "deep_dive_candidate"
    elif lanes:
        kind = "frontier_signal"
    else:
        kind = "other_relevant"
    reasons: list[str] = []
    if mechanism:
        reasons.append("机制/架构")
    if evidence:
        reasons.append("实验/评测")
    if artifacts:
        reasons.append("论文/代码/开放产物")
    if duration_bonus:
        reasons.append("长访谈")
    if source["source_class"] == "lab":
        reasons.append("实验室一手")
    if not reasons and lanes:
        reasons.append("前沿主题")
    episode_url = normalize_url(episode.get("url", ""))
    report_path = (
        episode.get("studied_report_hint")
        or studied_urls.get(episode_url)
        or match_studied_title(episode["title"], studied_titles)
    )
    episode.pop("studied_report_hint", None)
    episode.update(
        {
            "source_id": source["id"],
            "source_name": source["name"],
            "source_class": source["source_class"],
            "language": source["language"],
            "tier": source["tier"],
            "kind": kind,
            "score": score,
            "reasons": reasons or ["高质量渠道更新"],
            "topic_lanes": lanes,
            "source_topics": source["topics"],
            "studied": report_path is not None,
            "report_path": report_path,
        }
    )
    return episode


def fetch_source(
    source: dict[str, Any], since: dt.datetime, global_excludes: list[str],
    studied_urls: dict[str, str], studied_titles: dict[str, str], include_undated: bool,
) -> dict[str, Any]:
    try:
        episodes, notes, discovery, degraded = fetch_episodes(source)
        episodes = [canonicalize_apple_studied_date(item, studied_titles) for item in episodes]
        latest = max(
            (parse_date(item.get("published_at")) for item in episodes if item.get("published_at")),
            default=None,
        )
        window: list[dict[str, Any]] = []
        for episode in episodes:
            published = parse_date(episode.get("published_at"))
            if published is None and not include_undated:
                continue
            if published is not None and published < since:
                continue
            window.append(episode)
        selected = []
        for episode in window:
            item = classify_episode(
                source, episode, global_excludes, studied_urls, studied_titles
            )
            if item:
                selected.append(item)
        selected.sort(
            key=lambda item: (item["score"], item.get("published_at") or ""), reverse=True
        )
        return {
            "source_id": source["id"],
            "source_name": source["name"],
            "ok": True,
            "items": selected,
            "raw_count": len(window),
            "selected_count": len(selected),
            "latest_published_at": latest.isoformat() if latest else None,
            "discovery_used": discovery,
            "degraded": degraded,
            "notes": notes,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "source_id": source["id"],
            "source_name": source["name"],
            "ok": False,
            "items": [],
            "raw_count": 0,
            "selected_count": 0,
            "latest_published_at": None,
            "discovery_used": None,
            "degraded": True,
            "notes": [],
            "error": str(exc),
        }


def select_sources(
    registry: dict[str, Any], ids: list[str], tier: str, language: str
) -> list[dict[str, Any]]:
    sources = [source for source in registry["sources"] if source.get("enabled")]
    if ids:
        wanted = set(ids)
        known = {source["id"] for source in registry["sources"]}
        missing = sorted(wanted - known)
        if missing:
            raise RadarError("未知渠道：" + ", ".join(missing))
        sources = [source for source in sources if source["id"] in wanted]
    if tier != "all":
        sources = [source for source in sources if source["tier"] == tier]
    if language != "all":
        sources = [source for source in sources if source["language"] == language]
    return sources


def collect_updates(
    registry: dict[str, Any], sources: list[dict[str, Any]], since: dt.datetime,
    limit: int, per_source: int, workers: int, include_studied: bool,
    include_undated: bool, topic_filters: set[str] | None = None,
) -> dict[str, Any]:
    token_plan = prepare_token_plan()
    studied_urls, studied_titles = load_studied_index()
    global_excludes = registry.get("global_exclude_any", [])
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [
            executor.submit(
                fetch_source, source, since, global_excludes, studied_urls, studied_titles,
                include_undated
            )
            for source in sources
        ]
        results = [future.result() for future in futures]
    source_by_id = {source["id"]: source for source in sources}
    items: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    transport_notes: list[dict[str, str]] = []
    source_stats: list[dict[str, Any]] = []
    studied_hidden = 0
    for result in results:
        source = source_by_id[result["source_id"]]
        if not result["ok"]:
            failures.append(
                {
                    "source_id": result["source_id"],
                    "source_name": result["source_name"],
                    "error": result["error"],
                }
            )
        else:
            source_items = result["items"]
            if topic_filters:
                source_items = [
                    item for item in source_items
                    if topic_filters.intersection(item.get("topic_lanes", []))
                ]
            if not include_studied:
                studied_hidden += sum(1 for item in source_items if item.get("studied"))
                source_items = [item for item in source_items if not item.get("studied")]
            items.extend(source_items[:per_source])
            for note in result.get("notes", []):
                transport_notes.append({"source_id": result["source_id"], "note": note})
        sample = [
            {
                "title": item["title"],
                "score": item["score"],
                "kind": item["kind"],
                "published_at": item.get("published_at"),
            }
            for item in result.get("items", [])[:3]
        ]
        source_stats.append(
            {
                "source_id": result["source_id"],
                "source_name": result["source_name"],
                "source_class": source["source_class"],
                "language": source["language"],
                "tier": source["tier"],
                "ok": result["ok"],
                "degraded": result.get("degraded", True),
                "discovery_used": result.get("discovery_used"),
                "raw_count": result.get("raw_count", 0),
                "selected_count": result.get("selected_count", 0),
                "latest_published_at": result.get("latest_published_at"),
                "sample": sample,
            }
        )
    deduped: dict[str, dict[str, Any]] = {}
    for item in items:
        source = source_by_id[item["source_id"]]
        normalized = normalize_url(item.get("url", ""))
        generic_urls = {
            normalize_url(source.get("homepage", "")),
            normalize_url(source.get("apple_url", "")),
        }
        guid = str(item.get("guid") or "").strip()
        if item.get("discovered_via") == "apple_page" or not normalized or normalized in generic_urls:
            key = (
                "guid:" + item["source_id"] + ":" + guid
                if guid
                else "title:" + title_fingerprint(item["title"])
            )
        else:
            key = "url:" + normalized
        previous = deduped.get(key)
        if previous is None or item["score"] > previous["score"]:
            deduped[key] = item
    title_deduped: dict[str, dict[str, Any]] = {}
    for item in deduped.values():
        key = title_fingerprint(item["title"])
        previous = title_deduped.get(key)
        if previous is None:
            title_deduped[key] = item
            continue
        winner, alternate = (item, previous) if item["score"] > previous["score"] else (previous, item)
        alternates = list(winner.get("alternate_sources", []))
        alternates.append(
            {"source_id": alternate["source_id"], "source_name": alternate["source_name"]}
        )
        winner["alternate_sources"] = alternates
        title_deduped[key] = winner
    items = list(title_deduped.values())
    items.sort(
        key=lambda item: (item["score"], item.get("published_at") or ""), reverse=True
    )
    return {
        "schema_version": 1,
        "generated_at": now_utc().isoformat(),
        "since": since.isoformat(),
        "sources_requested": len(sources),
        "sources_succeeded": len(sources) - len(failures),
        "sources_degraded": sum(1 for stat in source_stats if stat["ok"] and stat["degraded"]),
        "studied_hidden": studied_hidden,
        "items": items[:limit],
        "failures": failures,
        "transport_notes": transport_notes,
        "source_stats": source_stats,
        "topic_filters": sorted(topic_filters or []),
        "token_plan": token_plan,
    }


def markdown_updates(summary: dict[str, Any]) -> str:
    lines = [
        "# SOTA AI 技术播客更新",
        "",
        f"> 时间窗：{summary['since'][:10]} 至 {summary['generated_at'][:10]}｜"
        f"来源：{summary['sources_succeeded']}/{summary['sources_requested']} 成功｜"
        f"降级：{summary['sources_degraded']}｜已隐藏已学习：{summary['studied_hidden']}",
    ]
    groups = [
        ("deep_dive_candidate", "优先深挖"),
        ("frontier_signal", "前沿信号"),
        ("other_relevant", "其它相关更新"),
    ]
    for kind, title in groups:
        rows = [item for item in summary["items"] if item["kind"] == kind]
        if not rows:
            continue
        lines.extend(["", f"## {title}", ""])
        for item in rows:
            date = item.get("published_at", "")[:10] or "日期未解析"
            flags = "、".join(item["reasons"])
            if item.get("discovered_via") == "apple_page":
                route = (
                    " · Apple 备用，首发日已校正"
                    if item.get("date_confidence") == "studied_report_filename"
                    else " · Apple 备用，日期待核"
                )
            else:
                route = ""
            studied = " · 已学习" if item.get("studied") else ""
            lines.append(
                f"- **[{item['title']}]({item['url']})** · {item['source_name']} · "
                f"{date} · {format_duration(item.get('duration_seconds'))} · {flags}{route}{studied}"
            )
            if item.get("summary"):
                lines.append(f"  {trim(item['summary'], 220)}")
    if not summary["items"]:
        lines.extend(["", "本时间窗内没有筛选后的未学习技术播客更新。"])
    if summary["failures"]:
        lines.extend(["", "## 获取失败", ""])
        for failure in summary["failures"]:
            lines.append(f"- {failure['source_name']}：{failure['error']}")
    if summary["transport_notes"]:
        lines.extend(["", "## 采集降级记录", ""])
        for note in summary["transport_notes"]:
            lines.append(f"- {note['source_id']}：{note['note']}")
    return "\n".join(lines) + "\n"


def channels_markdown(sources: list[dict[str, Any]]) -> str:
    lines = [
        "| ID | 节目 | 语言 | 类型 | 档位 | 主题 | 状态 |",
        "|---|---|---|---|---|---|---|",
    ]
    for source in sources:
        topics = "、".join(source["topics"])
        lines.append(
            f"| `{source['id']}` | [{source['name']}]({source['homepage']}) | "
            f"{source['language']} | {source['source_class']} | {source['tier']} | "
            f"{topics} | {'启用' if source['enabled'] else '停用'} |"
        )
    return "\n".join(lines) + "\n"


def source_health(stat: dict[str, Any], reference: dt.datetime) -> str:
    if not stat["ok"]:
        return "失败"
    latest = parse_date(stat.get("latest_published_at"))
    if latest is None:
        return "日期未知（降级）" if stat.get("degraded") else "日期未知"
    age = (reference - latest).days
    if age > 180:
        status = "长期停更"
    elif age > 90:
        status = "低频观察"
    elif stat["raw_count"] and not stat["selected_count"]:
        status = "近期低相关"
    else:
        status = "正常"
    if stat.get("degraded"):
        status += "（降级）"
    return status


def scorecard_markdown(summary: dict[str, Any]) -> str:
    generated = parse_date(summary["generated_at"]) or now_utc()
    lines = [
        "# SOTA AI 技术播客渠道评分卡",
        "",
        f"> 时间窗：{summary['since'][:10]} 至 {summary['generated_at'][:10]}｜"
        f"来源：{summary['sources_succeeded']}/{summary['sources_requested']} 成功｜"
        f"降级：{summary['sources_degraded']}",
        "",
        "| 渠道 | 语言 | 档位 | 窗口单集 | 入选 | 相关率 | 最近更新 | 获取 | 健康度 | 代表单集 |",
        "|---|---|---|---:|---:|---:|---|---|---|---|",
    ]
    for stat in summary["source_stats"]:
        raw = stat["raw_count"]
        selected = stat["selected_count"]
        rate = f"{selected / raw:.0%}" if raw else "—"
        latest = (stat.get("latest_published_at") or "—")[:10]
        sample = "；".join(item["title"].replace("|", "\\|") for item in stat["sample"][:2]) or "—"
        lines.append(
            f"| `{stat['source_id']}` | {stat['language']} | {stat['tier']} | {raw} | {selected} | "
            f"{rate} | {latest} | {stat.get('discovery_used') or '失败'} | "
            f"{source_health(stat, generated)} | {sample} |"
        )
    if summary["failures"]:
        lines.extend(["", "## 获取失败", ""])
        for failure in summary["failures"]:
            lines.append(f"- {failure['source_name']}：{failure['error']}")
    return "\n".join(lines) + "\n"


def find_source(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    for source in registry["sources"]:
        if source["id"] == source_id:
            return source
    raise RadarError(f"未知渠道：{source_id}")


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
    if not keys:
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


def save_registry(path: pathlib.Path, registry: dict[str, Any]) -> None:
    registry["updated_on"] = dt.date.today().isoformat()
    errors = validate_registry(registry)
    if errors:
        raise RadarError("修改后注册表无效：" + "；".join(errors))
    write_json_atomic(path, registry)


def output(value: Any, fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value, end="" if str(value).endswith("\n") else "\n")


def cmd_updates(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    defaults = registry.get("defaults", {})
    if args.since:
        since_date = dt.date.fromisoformat(args.since)
        since = dt.datetime.combine(since_date, dt.time.min, tzinfo=dt.timezone.utc)
    else:
        days = args.days if args.days is not None else int(defaults.get("days", 7))
        since = now_utc() - dt.timedelta(days=days)
    sources = select_sources(registry, args.source, args.tier, args.language)
    summary = collect_updates(
        registry,
        sources,
        since,
        args.limit if args.limit is not None else int(defaults.get("limit", 20)),
        args.per_source if args.per_source is not None else int(defaults.get("per_source", 4)),
        args.workers if args.workers is not None else int(defaults.get("workers", 6)),
        args.include_studied,
        args.include_undated,
        set(args.topic),
    )
    output(summary if args.format == "json" else markdown_updates(summary), args.format)
    return 2 if sources and summary["sources_succeeded"] == 0 else 0


def cmd_channels_list(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    sources = select_sources(registry, [], args.tier, args.language)
    if args.include_disabled:
        sources = [
            source for source in registry["sources"]
            if (args.tier == "all" or source["tier"] == args.tier)
            and (args.language == "all" or source["language"] == args.language)
        ]
    value = {"schema_version": 1, "updated_on": registry["updated_on"], "sources": sources}
    output(value if args.format == "json" else channels_markdown(sources), args.format)
    return 0


def cmd_channels_get(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    source = find_source(registry, args.source_id)
    output(source if args.format == "json" else channels_markdown([source]), args.format)
    return 0


def cmd_channels_add(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    source = load_json(pathlib.Path(args.file))
    if not isinstance(source, dict):
        raise RadarError("新增渠道文件必须是单个 JSON object")
    if any(item["id"] == source.get("id") for item in registry["sources"]):
        raise RadarError(f"渠道已存在：{source.get('id')}")
    registry["sources"].append(source)
    save_registry(args.registry, registry)
    output({"status": "added", "source": source} if args.format == "json" else f"已新增：{source['id']}\n", args.format)
    return 0


def cmd_channels_update(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    source = find_source(registry, args.source_id)
    for assignment in args.set_values:
        set_dotted(source, assignment)
    save_registry(args.registry, registry)
    output({"status": "updated", "source": source} if args.format == "json" else f"已更新：{source['id']}\n", args.format)
    return 0


def cmd_channels_remove(args: argparse.Namespace) -> int:
    if not args.yes:
        raise RadarError("删除渠道必须显式传 --yes")
    registry = load_registry(args.registry)
    source = find_source(registry, args.source_id)
    registry["sources"] = [item for item in registry["sources"] if item["id"] != args.source_id]
    save_registry(args.registry, registry)
    output({"status": "removed", "source": source} if args.format == "json" else f"已删除：{source['id']}\n", args.format)
    return 0


def cmd_channels_validate(args: argparse.Namespace) -> int:
    raw = load_json(args.registry)
    errors = validate_registry(raw)
    result: dict[str, Any] = {
        "schema_version": 1,
        "registry": str(args.registry),
        "valid": not errors,
        "errors": errors,
        "source_count": len(raw.get("sources", [])) if isinstance(raw, dict) else 0,
    }
    if args.live and not errors:
        sources = select_sources(raw, args.source, args.tier, args.language)
        summary = collect_updates(
            raw,
            sources,
            now_utc() - dt.timedelta(days=3650),
            max(1, len(sources)),
            1,
            args.workers,
            True,
            True,
        )
        result["live"] = {
            "requested": summary["sources_requested"],
            "succeeded": summary["sources_succeeded"],
            "degraded": summary["sources_degraded"],
            "failures": summary["failures"],
            "source_stats": summary["source_stats"],
            "transport_notes": summary["transport_notes"],
            "token_plan": summary["token_plan"],
        }
        if summary["failures"]:
            result["valid"] = False
    if args.format == "json":
        output(result, "json")
    else:
        lines = [f"注册表：{'有效' if not errors else '无效'}（{result['source_count']} 个渠道）"]
        lines.extend(f"- {error}" for error in errors)
        if result.get("live"):
            live = result["live"]
            lines.append(f"联网检查：{live['succeeded']}/{live['requested']} 成功，{live['degraded']} 个降级")
            lines.extend(f"- {item['source_name']}：{item['error']}" for item in live["failures"])
        output("\n".join(lines) + "\n", "md")
    return 0 if result["valid"] else 1


def cmd_channels_evaluate(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    sources = select_sources(registry, args.source, args.tier, args.language)
    summary = collect_updates(
        registry,
        sources,
        now_utc() - dt.timedelta(days=args.days),
        max(1, len(sources) * args.per_source),
        args.per_source,
        args.workers,
        True,
        False,
    )
    value = {
        key: summary[key]
        for key in (
            "schema_version", "generated_at", "since", "sources_requested", "sources_succeeded",
            "sources_degraded", "source_stats", "failures", "transport_notes", "token_plan",
        )
    }
    output(value if args.format == "json" else scorecard_markdown(summary), args.format)
    return 2 if sources and summary["sources_succeeded"] == 0 else 0


def render_opml(sources: list[dict[str, Any]]) -> str:
    escaped = html.escape
    created = now_utc().isoformat()
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<opml version="2.0">',
        "  <head>",
        "    <title>SOTA AI Technical Podcasts</title>",
        f"    <dateCreated>{escaped(created)}</dateCreated>",
        "  </head>",
        "  <body>",
    ]
    for source in sources:
        lines.append(
            "    <outline "
            f'title="{escaped(source["name"], quote=True)}" '
            f'text="{escaped(source["why"], quote=True)}" '
            f'xmlUrl="{escaped(source["feed_url"], quote=True)}" '
            f'htmlUrl="{escaped(source["homepage"], quote=True)}" type="rss"/>'
        )
    lines.extend(["  </body>", "</opml>"])
    return "\n".join(lines) + "\n"


def cmd_channels_export_opml(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    sources = select_sources(registry, [], args.tier, args.language)
    text = render_opml(sources)
    if args.output == "-":
        print(text, end="")
        return 0
    destination = pathlib.Path(args.output).expanduser()
    if destination.exists() and not args.force:
        raise RadarError(f"目标已存在，若要覆盖请加 --force：{destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    print(f"已导出 {len(sources)} 个渠道：{destination}")
    return 0


def add_common_source_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--source", action="append", default=[], help="只查指定 source id，可重复")
    parser.add_argument("--tier", choices=["all", "core", "watch"], default="all")
    parser.add_argument("--language", choices=["all", "zh", "en"], default="all")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=pathlib.Path, default=DEFAULT_REGISTRY)
    sub = parser.add_subparsers(dest="command", required=True)

    updates = sub.add_parser("updates", help="获取最近技术播客更新")
    updates.add_argument("--days", type=int)
    updates.add_argument("--since", help="从 YYYY-MM-DD 起；优先于 --days")
    add_common_source_filters(updates)
    updates.add_argument("--limit", type=int)
    updates.add_argument("--per-source", type=int)
    updates.add_argument("--workers", type=int)
    updates.add_argument("--include-studied", action="store_true")
    updates.add_argument("--include-undated", action="store_true")
    updates.add_argument("--topic", action="append", default=[], choices=sorted(TOPIC_LANES))
    updates.add_argument("--format", choices=["json", "md"], default="md")
    updates.set_defaults(func=cmd_updates)

    channels = sub.add_parser("channels", help="渠道增删改查、评估与导出")
    channel_sub = channels.add_subparsers(dest="channel_command", required=True)

    channel_list = channel_sub.add_parser("list", help="列出渠道")
    channel_list.add_argument("--tier", choices=["all", "core", "watch"], default="all")
    channel_list.add_argument("--language", choices=["all", "zh", "en"], default="all")
    channel_list.add_argument("--include-disabled", action="store_true")
    channel_list.add_argument("--format", choices=["json", "md"], default="md")
    channel_list.set_defaults(func=cmd_channels_list)

    channel_get = channel_sub.add_parser("get", help="查看单个渠道")
    channel_get.add_argument("source_id")
    channel_get.add_argument("--format", choices=["json", "md"], default="json")
    channel_get.set_defaults(func=cmd_channels_get)

    channel_add = channel_sub.add_parser("add", help="从 JSON 文件新增渠道")
    channel_add.add_argument("--file", required=True)
    channel_add.add_argument("--format", choices=["json", "md"], default="json")
    channel_add.set_defaults(func=cmd_channels_add)

    channel_update = channel_sub.add_parser("update", help="用 dotted key=value 更新渠道")
    channel_update.add_argument("source_id")
    channel_update.add_argument("--set", dest="set_values", action="append", required=True)
    channel_update.add_argument("--format", choices=["json", "md"], default="json")
    channel_update.set_defaults(func=cmd_channels_update)

    channel_remove = channel_sub.add_parser("remove", help="删除渠道")
    channel_remove.add_argument("source_id")
    channel_remove.add_argument("--yes", action="store_true")
    channel_remove.add_argument("--format", choices=["json", "md"], default="json")
    channel_remove.set_defaults(func=cmd_channels_remove)

    channel_validate = channel_sub.add_parser("validate", help="校验注册表，可选联网检查")
    channel_validate.add_argument("--live", action="store_true")
    add_common_source_filters(channel_validate)
    channel_validate.add_argument("--workers", type=int, default=6)
    channel_validate.add_argument("--format", choices=["json", "md"], default="md")
    channel_validate.set_defaults(func=cmd_channels_validate)

    channel_evaluate = channel_sub.add_parser("evaluate", help="回测活跃度、相关率和代表单集")
    channel_evaluate.add_argument("--days", type=int, default=90)
    add_common_source_filters(channel_evaluate)
    channel_evaluate.add_argument("--per-source", type=int, default=20)
    channel_evaluate.add_argument("--workers", type=int, default=6)
    channel_evaluate.add_argument("--format", choices=["json", "md"], default="md")
    channel_evaluate.set_defaults(func=cmd_channels_evaluate)

    channel_opml = channel_sub.add_parser("export-opml", help="导出可导入播客客户端的 OPML")
    channel_opml.add_argument("--tier", choices=["all", "core", "watch"], default="all")
    channel_opml.add_argument("--language", choices=["all", "zh", "en"], default="all")
    channel_opml.add_argument("--output", default="-", help="输出路径；- 表示 stdout")
    channel_opml.add_argument("--force", action="store_true")
    channel_opml.set_defaults(func=cmd_channels_export_opml)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (RadarError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"[ai-tech-podcast-radar] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
