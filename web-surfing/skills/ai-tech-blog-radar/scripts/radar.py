#!/usr/bin/env python3
"""顶尖 AI 技术博客雷达：查询近期更新并维护官方渠道注册表。

常用命令：
  python3 radar.py updates --days 7 --format json
  python3 radar.py channels list --format md
  python3 radar.py channels validate --live --format json
  python3 radar.py channels update deepseek --set tier=must
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from typing import Any


WEB_ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = WEB_ROOT / "sources" / "ai-tech-blogs.json"
UA = "Mozilla/5.0 (compatible; EverAgentAITechRadar/1.0)"

TIERS = {"must", "watch"}
DISCOVERY_KINDS = {"rss", "search", "sitemap"}

MECHANISM_TERMS = {
    "architecture", "mechanism", "algorithm", "method", "training", "post-training",
    "inference", "attention", "memory", "context", "agent", "harness", "eval",
    "evaluation", "reasoning", "scaling", "rl", "reinforcement learning", "kernel",
    "架构", "机制", "算法", "训练", "推理", "注意力", "记忆", "上下文", "智能体", "评测",
}
EVIDENCE_TERMS = {
    "benchmark", "experiment", "dataset", "results", "ablation", "failure", "latency",
    "throughput", "accuracy", "performance", "case study", "study", "analysis", "review",
    "trial", "sample",
    "基准", "实验", "数据集", "结果", "消融", "失败", "延迟", "吞吐", "准确率", "性能",
}
ARTIFACT_TERMS = {
    "open source", "open-source", "open weights", "open-weight", "github", "code",
    "paper", "technical", "technical report", "model card", "checkpoint", "repository", "framework",
    "开源", "代码", "论文", "技术报告", "模型卡", "权重", "框架",
}
RELEASE_TERMS = {
    "introducing", "release", "released", "launch", "new model", "preview", "update",
    "发布", "推出", "上线", "预览", "更新",
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
        tmp = pathlib.Path(handle.name)
    tmp.replace(path)


def load_registry(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists():
        raise RadarError(f"渠道注册表不存在：{path}")
    value = load_json(path)
    errors = validate_registry(value)
    if errors:
        raise RadarError("渠道注册表无效：" + "；".join(errors))
    return value


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
        for key in ("name", "vendor", "homepage", "why"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                errors.append(f"{label}.{key} 必须为非空字符串")
        if source.get("tier") not in TIERS:
            errors.append(f"{label}.tier 必须是 must/watch")
        if not isinstance(source.get("enabled"), bool):
            errors.append(f"{label}.enabled 必须是 boolean")
        discovery = source.get("discovery")
        if not isinstance(discovery, dict):
            errors.append(f"{label}.discovery 必须为 object")
        else:
            kind = discovery.get("kind")
            if kind not in DISCOVERY_KINDS:
                errors.append(f"{label}.discovery.kind 必须是 rss/search/sitemap")
            if kind in {"rss", "sitemap"} and not discovery.get("url"):
                errors.append(f"{label}.discovery.url 缺失")
            if kind == "search" and not discovery.get("query"):
                errors.append(f"{label}.discovery.query 缺失")
        for key in ("allow_domains", "path_prefixes", "include_any", "exclude_any"):
            if not isinstance(source.get(key), list) or not all(isinstance(x, str) for x in source[key]):
                errors.append(f"{label}.{key} 必须为 string array")
    defaults = registry.get("defaults", {})
    if not isinstance(defaults, dict):
        errors.append("defaults 必须为 object")
    return errors


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def trim(value: str, size: int = 260) -> str:
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
    month_pattern = (
        r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+(\d{1,2}),\s+(\d{4})"
    )
    match = re.search(month_pattern, text, re.I)
    if match:
        try:
            parsed = dt.datetime.strptime(
                f"{match.group(1)[:3].title()} {match.group(2)} {match.group(3)}", "%b %d %Y"
            )
            return parsed.replace(tzinfo=dt.timezone.utc)
        except ValueError:
            pass
    relative = re.search(r"\b(\d+)\s+(minute|hour|day|week)s?\s+ago\b", text, re.I)
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2).lower()
        delta = {
            "minute": dt.timedelta(minutes=amount),
            "hour": dt.timedelta(hours=amount),
            "day": dt.timedelta(days=amount),
            "week": dt.timedelta(weeks=amount),
        }[unit]
        return reference - delta
    return None


def normalize_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url.strip())
    query = []
    for key, value in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True):
        lower = key.lower()
        if lower.startswith("utm_") or lower in {"ref", "source", "from", "trk"}:
            continue
        query.append((key, value))
    path = parsed.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit(
        (parsed.scheme.lower(), parsed.netloc.lower(), path, urllib.parse.urlencode(sorted(query)), "")
    )


def source_accepts_url(source: dict[str, Any], url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    host = (parsed.hostname or "").lower()
    domains = [x.lower() for x in source.get("allow_domains", [])]
    if domains and not any(host == domain or host.endswith("." + domain) for domain in domains):
        return False
    prefixes = source.get("path_prefixes", [])
    if prefixes and not any(parsed.path.startswith(prefix) for prefix in prefixes):
        return False
    return True


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


def run_eacli(args: list[str], timeout: int = 45) -> str:
    try:
        completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RadarError("找不到 eacli") from exc
    except subprocess.TimeoutExpired as exc:
        raise RadarError(f"eacli 超时（{timeout}s）") from exc
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}"
        raise RadarError(message[:500])
    return completed.stdout


def prepare_token_plan(capabilities: set[str]) -> dict[str, Any]:
    evidence: dict[str, Any] = {"catalog": "ok", "selections": {}}
    run_eacli(["eacli", "tokenplan", "catalog", "--json"], timeout=30)
    for capability in sorted(capabilities):
        stdout = run_eacli(
            ["eacli", "tool", "select", "--capability", capability, "--device", "auto", "--json"],
            timeout=30,
        )
        payload = json.loads(stdout)
        selected = payload.get("result", {}).get("selected", {})
        evidence["selections"][capability] = {
            "provider": selected.get("provider"),
            "device": selected.get("device"),
            "backend": selected.get("backend"),
        }
    return evidence


def request_id(source_id: str, payload: str) -> str:
    digest = hashlib.sha256(payload.encode()).hexdigest()[:12]
    hour = now_utc().strftime("%Y%m%d%H")
    return f"ai-tech-radar-{source_id}-{hour}-{digest}"


def eacli_invoke(capability: str, arguments: dict[str, Any], source_id: str, timeout: int = 60) -> Any:
    encoded = json.dumps(arguments, ensure_ascii=False, separators=(",", ":"))
    stdout = run_eacli(
        [
            "eacli", "tool", "invoke", "--capability", capability,
            "--input-json", encoded, "--device", "auto",
            "--request-id", request_id(source_id, encoded), "--json",
        ],
        timeout=timeout,
    )
    return parse_inner_result(stdout)


def extract_web_read_content(result: Any) -> str:
    if isinstance(result, dict):
        content = result.get("content") or result.get("text") or ""
    else:
        content = str(result or "")
    content = content.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:xml)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
    return content


def http_get(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/rss+xml,application/atom+xml,application/xml,text/xml,text/html;q=0.8,*/*;q=0.5",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(1_500_000).decode("utf-8", errors="replace")


def xml_field(block: str, names: list[str]) -> str:
    for name in names:
        match = re.search(rf"<{re.escape(name)}\b[^>]*>(.*?)</{re.escape(name)}>", block, re.S | re.I)
        if match:
            return clean_text(match.group(1))
    return ""


def parse_feed_text(text: str, source: dict[str, Any], since: dt.datetime) -> list[dict[str, Any]]:
    blocks = re.findall(r"<item\b[^>]*>(.*?)</item>", text, re.S | re.I)
    atom = False
    if not blocks:
        blocks = re.findall(r"<entry\b[^>]*>(.*?)</entry>", text, re.S | re.I)
        atom = True
    entries: list[dict[str, Any]] = []
    for block in blocks:
        title = xml_field(block, ["title"])
        if atom:
            link_match = re.search(r"<link\b[^>]*href=[\"']([^\"']+)", block, re.I)
            link = html.unescape(link_match.group(1)) if link_match else ""
            published_raw = xml_field(block, ["published", "updated"])
            summary = xml_field(block, ["summary", "content"])
        else:
            link = xml_field(block, ["link", "guid"])
            published_raw = xml_field(block, ["pubDate", "dc:date", "date"])
            summary = xml_field(block, ["description", "content:encoded"])
        published = parse_date(published_raw)
        if published and published < since:
            continue
        if not title or not link or not source_accepts_url(source, link):
            continue
        entries.append(
            {
                "title": title,
                "url": normalize_url(link),
                "published_at": published.isoformat() if published else None,
                "summary": trim(summary),
                "discovered_via": "rss",
                "date_confidence": "feed" if published else "unknown",
            }
        )
    return entries


def fetch_rss(source: dict[str, Any], since: dt.datetime) -> tuple[list[dict[str, Any]], list[str]]:
    url = source["discovery"]["url"]
    notes: list[str] = []
    try:
        result = eacli_invoke("web.read", {"url": url}, source["id"] + "-rss")
        text = extract_web_read_content(result)
        entries = parse_feed_text(text, source, since)
        if entries:
            return entries, notes
        notes.append("eacli web.read 未保留可解析的完整 feed，使用只读 HTTP XML fallback")
    except Exception as exc:  # noqa: BLE001
        notes.append(f"eacli web.read 失败，使用只读 HTTP XML fallback：{exc}")
    text = http_get(url)
    entries = parse_feed_text(text, source, since)
    if not entries and "<item" not in text and "<entry" not in text:
        raise RadarError("未识别到 RSS/Atom 条目")
    return entries, notes


def search_rows(result: Any) -> list[dict[str, Any]]:
    if isinstance(result, list):
        return [row for row in result if isinstance(row, dict)]
    if isinstance(result, dict):
        for key in ("organic", "results", "data", "items"):
            value = result.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    return []


def fetch_search(
    source: dict[str, Any], since: dt.datetime, include_undated: bool
) -> tuple[list[dict[str, Any]], list[str]]:
    date_hint = since.date().isoformat()
    query = f"{source['discovery']['query']} after:{date_hint}"
    result = eacli_invoke("web.search", {"query": query}, source["id"] + "-search")
    entries: list[dict[str, Any]] = []
    for row in search_rows(result):
        title = clean_text(str(row.get("title") or row.get("name") or ""))
        url = str(row.get("link") or row.get("url") or "").strip()
        summary = clean_text(str(row.get("content") or row.get("snippet") or row.get("description") or ""))
        published = parse_date(str(row.get("date") or summary))
        if published and published < since:
            continue
        if not published and not include_undated:
            continue
        if not title or not url or not source_accepts_url(source, url):
            continue
        if normalize_url(url) == normalize_url(source["homepage"]):
            continue
        entries.append(
            {
                "title": title,
                "url": normalize_url(url),
                "published_at": published.isoformat() if published else None,
                "summary": trim(summary),
                "discovered_via": "search",
                "date_confidence": "result" if published else "search-window",
            }
        )
    return entries, []


def parse_sitemap_text(text: str) -> list[tuple[str, dt.datetime | None]]:
    rows: list[tuple[str, dt.datetime | None]] = []
    for block in re.findall(r"<url\b[^>]*>(.*?)</url>", text, re.S | re.I):
        loc = xml_field(block, ["loc"])
        if not loc:
            continue
        rows.append((loc, parse_date(xml_field(block, ["lastmod"]))))
    return rows


def title_from_url(url: str) -> str:
    slug = pathlib.PurePosixPath(urllib.parse.urlsplit(url).path.rstrip("/")).name
    words = re.sub(r"[-_]+", " ", slug).strip()
    return words[:1].upper() + words[1:] if words else url


def fetch_sitemap(source: dict[str, Any], since: dt.datetime) -> tuple[list[dict[str, Any]], list[str]]:
    url = source["discovery"]["url"]
    notes: list[str] = []
    try:
        result = eacli_invoke("web.read", {"url": url}, source["id"] + "-sitemap")
        text = extract_web_read_content(result)
        rows = parse_sitemap_text(text)
        if not rows:
            notes.append("eacli web.read 未保留可解析 sitemap，使用只读 HTTP XML fallback")
            text = http_get(url)
            rows = parse_sitemap_text(text)
    except Exception as exc:  # noqa: BLE001
        notes.append(f"eacli web.read 失败，使用只读 HTTP XML fallback：{exc}")
        rows = parse_sitemap_text(http_get(url))
    entries: list[dict[str, Any]] = []
    for link, published in rows:
        if published and published < since:
            continue
        if not source_accepts_url(source, link):
            continue
        entries.append(
            {
                "title": title_from_url(link),
                "url": normalize_url(link),
                "published_at": published.isoformat() if published else None,
                "summary": "",
                "discovered_via": "sitemap",
                "date_confidence": "lastmod" if published else "unknown",
            }
        )
    return entries, notes


def matched_terms(text: str, terms: set[str] | list[str]) -> list[str]:
    lower = re.sub(r"[-_/]+", " ", text.lower())
    return sorted(
        term for term in terms
        if re.sub(r"[-_/]+", " ", term.lower()) in lower
    )


def classify_entry(
    source: dict[str, Any], entry: dict[str, Any], global_excludes: list[str]
) -> dict[str, Any] | None:
    text = f"{entry['title']} {entry.get('summary', '')} {entry.get('url', '')}".lower()
    include_any = source.get("include_any", [])
    if include_any and not any(term.lower() in text for term in include_any):
        return None
    mechanism = matched_terms(text, MECHANISM_TERMS)
    evidence = matched_terms(text, EVIDENCE_TERMS)
    artifacts = matched_terms(text, ARTIFACT_TERMS)
    categories = sum(bool(items) for items in (mechanism, evidence, artifacts))
    source_noise = matched_terms(text, source.get("exclude_any", []))
    if source_noise:
        return None
    noise = matched_terms(text, global_excludes)
    if noise and categories < 2:
        return None
    release = matched_terms(text, RELEASE_TERMS)
    if categories >= 2:
        kind = "deep_read_candidate"
    elif release:
        kind = "release_signal"
    else:
        kind = "technical_update"
    published = parse_date(entry.get("published_at"))
    age_bonus = 0
    if published:
        age_bonus = max(0, 14 - max(0, (now_utc() - published).days))
    score = (30 if source["tier"] == "must" else 10) + categories * 8 + age_bonus
    reasons = []
    if mechanism:
        reasons.append("机制/架构")
    if evidence:
        reasons.append("实验/评测")
    if artifacts:
        reasons.append("代码/论文/开放产物")
    if kind == "release_signal" and not reasons:
        reasons.append("重要发布")
    entry.update(
        {
            "source_id": source["id"],
            "source_name": source["name"],
            "vendor": source["vendor"],
            "tier": source["tier"],
            "kind": kind,
            "score": score,
            "reasons": reasons or ["官方技术更新"],
        }
    )
    return entry


def fetch_source(
    source: dict[str, Any], since: dt.datetime, global_excludes: list[str], include_undated: bool
) -> dict[str, Any]:
    try:
        kind = source["discovery"]["kind"]
        if kind == "rss":
            entries, notes = fetch_rss(source, since)
        elif kind == "search":
            entries, notes = fetch_search(source, since, include_undated)
        else:
            entries, notes = fetch_sitemap(source, since)
        classified = []
        for entry in entries:
            item = classify_entry(source, entry, global_excludes)
            if item:
                classified.append(item)
        classified.sort(
            key=lambda item: (item["published_at"] or "", item["score"]), reverse=True
        )
        return {
            "source_id": source["id"],
            "source_name": source["name"],
            "ok": True,
            "items": classified,
            "notes": notes,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "source_id": source["id"],
            "source_name": source["name"],
            "ok": False,
            "items": [],
            "notes": [],
            "error": str(exc),
        }


def select_sources(
    registry: dict[str, Any], ids: list[str], tier: str
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
    return sources


def collect_updates(
    registry: dict[str, Any], sources: list[dict[str, Any]], since: dt.datetime,
    limit: int, per_source: int, workers: int, include_undated: bool = False,
) -> dict[str, Any]:
    capabilities = set()
    if any(source["discovery"]["kind"] == "search" for source in sources):
        capabilities.add("web.search")
    if any(source["discovery"]["kind"] in {"rss", "sitemap"} for source in sources):
        capabilities.add("web.read")
    token_plan = prepare_token_plan(capabilities) if capabilities else {}
    global_excludes = registry.get("global_exclude_any", [])
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
        futures = [
            executor.submit(fetch_source, source, since, global_excludes, include_undated)
            for source in sources
        ]
        results = [future.result() for future in futures]
    items: list[dict[str, Any]] = []
    failures = []
    notes = []
    for result in results:
        if not result["ok"]:
            failures.append(
                {"source_id": result["source_id"], "source_name": result["source_name"], "error": result["error"]}
            )
            continue
        items.extend(result["items"][:per_source])
        for note in result["notes"]:
            notes.append({"source_id": result["source_id"], "note": note})
    deduped: dict[str, dict[str, Any]] = {}
    for item in items:
        key = normalize_url(item["url"])
        previous = deduped.get(key)
        if previous is None or item["score"] > previous["score"]:
            deduped[key] = item
    items = list(deduped.values())
    items.sort(key=lambda item: (item["score"], item["published_at"] or ""), reverse=True)
    items = items[:limit]
    return {
        "schema_version": 1,
        "generated_at": now_utc().isoformat(),
        "since": since.isoformat(),
        "sources_requested": len(sources),
        "sources_succeeded": len(sources) - len(failures),
        "items": items,
        "failures": failures,
        "transport_notes": notes,
        "token_plan": token_plan,
    }


def markdown_updates(summary: dict[str, Any]) -> str:
    lines = [
        "# 顶尖 AI 技术博客更新",
        "",
        f"> 时间窗：{summary['since'][:10]} 至 {summary['generated_at'][:10]}｜"
        f"来源：{summary['sources_succeeded']}/{summary['sources_requested']} 成功",
    ]
    groups = [
        ("deep_read_candidate", "值得重点看"),
        ("release_signal", "重要发布"),
        ("technical_update", "其它技术更新"),
    ]
    for kind, title in groups:
        rows = [item for item in summary["items"] if item["kind"] == kind]
        if not rows:
            continue
        lines.extend(["", f"## {title}", ""])
        for item in rows:
            date = item["published_at"][:10] if item.get("published_at") else "日期未解析"
            reasons = "、".join(item["reasons"])
            lines.append(f"- **[{item['title']}]({item['url']})** · {item['source_name']} · {date} · {reasons}")
            if item.get("summary"):
                lines.append(f"  {item['summary']}")
    if not summary["items"]:
        lines.extend(["", "本时间窗内没有筛选后的技术更新。"])
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
        "| ID | 渠道 | 档位 | 状态 | 发现方式 | 入口 |",
        "|---|---|---|---|---|---|",
    ]
    for source in sources:
        discovery = source["discovery"]
        endpoint = discovery.get("url") or discovery.get("query") or ""
        lines.append(
            f"| `{source['id']}` | {source['name']} | {source['tier']} | "
            f"{'启用' if source['enabled'] else '停用'} | {discovery['kind']} | {endpoint} |"
        )
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
    cursor: dict[str, Any] = target
    for key in keys[:-1]:
        value = cursor.get(key)
        if value is None:
            value = {}
            cursor[key] = value
        if not isinstance(value, dict):
            raise RadarError(f"无法进入非 object 字段：{key}")
        cursor = value
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
    sources = select_sources(registry, args.source, args.tier)
    summary = collect_updates(
        registry,
        sources,
        since,
        args.limit if args.limit is not None else int(defaults.get("limit", 30)),
        args.per_source,
        args.workers if args.workers is not None else int(defaults.get("workers", 4)),
        args.include_undated,
    )
    output(summary if args.format == "json" else markdown_updates(summary), args.format)
    return 2 if sources and summary["sources_succeeded"] == 0 else 0


def cmd_channels_list(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    sources = registry["sources"]
    if args.tier != "all":
        sources = [source for source in sources if source["tier"] == args.tier]
    if args.format == "json":
        output({"schema_version": 1, "updated_on": registry["updated_on"], "sources": sources}, "json")
    else:
        output(channels_markdown(sources), "md")
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
    output({"status": "removed", "source": source} if args.format == "json" else f"已删除：{args.source_id}\n", args.format)
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
        registry = raw
        sources = select_sources(registry, args.source, args.tier)
        probe = collect_updates(
            registry,
            sources,
            now_utc() - dt.timedelta(days=3650),
            limit=max(1, len(sources)),
            per_source=1,
            workers=args.workers,
            include_undated=True,
        )
        result["live"] = {
            "requested": probe["sources_requested"],
            "succeeded": probe["sources_succeeded"],
            "failures": probe["failures"],
            "transport_notes": probe["transport_notes"],
        }
        if probe["failures"]:
            result["valid"] = False
    if args.format == "json":
        output(result, "json")
    else:
        lines = [f"注册表：{'有效' if not errors else '无效'}（{result['source_count']} 个渠道）"]
        lines.extend(f"- {error}" for error in errors)
        if result.get("live"):
            live = result["live"]
            lines.append(f"联网检查：{live['succeeded']}/{live['requested']} 成功")
            lines.extend(f"- {item['source_name']}：{item['error']}" for item in live["failures"])
        output("\n".join(lines) + "\n", "md")
    return 0 if result["valid"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", type=pathlib.Path, default=DEFAULT_REGISTRY, help="渠道注册表路径")
    sub = parser.add_subparsers(dest="command", required=True)

    updates = sub.add_parser("updates", help="获取最近技术博客更新")
    updates.add_argument("--days", type=int, help="最近多少天，默认读取 registry defaults")
    updates.add_argument("--since", help="从 YYYY-MM-DD 起；优先于 --days")
    updates.add_argument("--source", action="append", default=[], help="只查指定 source id，可重复")
    updates.add_argument("--tier", choices=["all", "must", "watch"], default="all")
    updates.add_argument("--limit", type=int, help="总条数上限")
    updates.add_argument("--per-source", type=int, default=5, help="每源条数上限")
    updates.add_argument("--workers", type=int, help="并发数")
    updates.add_argument("--include-undated", action="store_true", help="包含搜索结果中无法解析日期的条目")
    updates.add_argument("--format", choices=["json", "md"], default="md")
    updates.set_defaults(func=cmd_updates)

    channels = sub.add_parser("channels", help="渠道增删改查")
    channel_sub = channels.add_subparsers(dest="channel_command", required=True)

    channel_list = channel_sub.add_parser("list", help="列出渠道")
    channel_list.add_argument("--tier", choices=["all", "must", "watch"], default="all")
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
    channel_validate.add_argument("--source", action="append", default=[])
    channel_validate.add_argument("--tier", choices=["all", "must", "watch"], default="all")
    channel_validate.add_argument("--workers", type=int, default=4)
    channel_validate.add_argument("--format", choices=["json", "md"], default="md")
    channel_validate.set_defaults(func=cmd_channels_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (RadarError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"[ai-tech-blog-radar] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
