#!/usr/bin/env python3
"""Read-only Bilibili following and learning inbox via OpenCLI browser sessions."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import secrets
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BILIBILI_HOME = "https://t.bilibili.com/"


class InboxError(RuntimeError):
    pass


def _run_opencli(args: list[str], timeout: int = 120) -> str:
    result = subprocess.run(
        ["opencli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise InboxError(f"opencli failed: {detail}")
    return result.stdout.strip()


def _parse_json(raw: str, label: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InboxError(
            f"{label} returned invalid JSON: {exc}; bytes={len(raw)}"
        ) from exc


class BrowserSession:
    def __init__(self) -> None:
        self.name = f"bili-inbox-{os.getpid()}-{secrets.token_hex(3)}"
        self.opened = False

    def __enter__(self) -> "BrowserSession":
        if not shutil.which("opencli"):
            raise InboxError("opencli is not installed or not on PATH")
        _run_opencli(["browser", self.name, "open", BILIBILI_HOME, "--window", "background"])
        self.opened = True
        return self

    def eval(self, expression: str, timeout: int = 120, attempts: int = 3) -> Any:
        last_error: InboxError | None = None
        for attempt in range(attempts):
            raw = _run_opencli(["browser", self.name, "eval", expression], timeout=timeout)
            try:
                return _parse_json(raw, "browser eval")
            except InboxError as exc:
                last_error = exc
                if attempt + 1 < attempts:
                    time.sleep(0.5 * (attempt + 1))
        assert last_error is not None
        raise last_error

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        if self.opened:
            subprocess.run(
                ["opencli", "browser", self.name, "close"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )


def _js_string(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def fetch_account(session: BrowserSession) -> dict[str, Any]:
    result = session.eval(
        """(async()=>{
          const j=await (await fetch('https://api.bilibili.com/x/web-interface/nav',
            {credentials:'include'})).json();
          if(j.code!==0||!j.data?.isLogin) throw new Error(`Bilibili login required: ${j.message}`);
          return {mid:String(j.data.mid),name:j.data.uname||''};
        })()"""
    )
    if not result.get("mid"):
        raise InboxError("Bilibili account id is missing")
    return result


def fetch_followings(
    session: BrowserSession,
    account_mid: str,
    max_pages: int,
    delay_ms: int,
) -> dict[str, Any]:
    all_items: list[dict[str, Any]] = []
    total = 0
    complete = False
    # Keep each browser bridge response small. Some profiles intermittently
    # truncate large eval payloads even though the underlying API succeeded.
    batch_size = 1
    for start_page in range(1, max_pages + 1, batch_size):
        end_page = min(start_page + batch_size - 1, max_pages)
        expression = f"""(async()=>{{
          const all=[];
          let total=0;
          let complete=false;
          for(let pn={start_page};pn<={end_page};pn++){{
            const q=new URLSearchParams({{vmid:{_js_string(account_mid)},pn:String(pn),ps:'50',order:'desc'}});
            const j=await (await fetch('https://api.bilibili.com/x/relation/followings?'+q,
              {{credentials:'include'}})).json();
            if(j.code!==0) throw new Error(`followings failed: ${{j.message}} (${{j.code}})`);
            const list=j.data?.list||[];
            total=Number(j.data?.total||total||0);
            for(const u of list) all.push({{
              mid:String(u.mid),name:u.uname||'',sign:u.sign||'',face:u.face||'',
              followed_at:Number(u.mtime||0),special:Boolean(u.special),
              official:u.official_verify?.desc||''
            }});
            if(list.length<50){{complete=true;break;}}
            if({delay_ms}>0) await new Promise(r=>setTimeout(r,{delay_ms}));
          }}
          return {{total,complete,items:all}};
        }})()"""
        try:
            batch = session.eval(expression, timeout=max(120, batch_size * 4))
        except InboxError as exc:
            raise InboxError(f"followings page {start_page}: {exc}") from exc
        total = int(batch.get("total") or total)
        all_items.extend(batch.get("items") or [])
        if batch.get("complete"):
            complete = True
            break
    return {"total": total, "complete": complete, "items": all_items}


def fetch_recommended_ups(
    session: BrowserSession,
    max_pages: int = 10,
    delay_ms: int = 300,
) -> list[dict[str, Any]]:
    expression = f"""(async()=>{{
      const seen=new Map();
      const first=await (await fetch(
        'https://api.bilibili.com/x/polymer/web-dynamic/v1/portal?up_list_more=1',
        {{credentials:'include'}})).json();
      if(first.code!==0) throw new Error(`portal failed: ${{first.message}} (${{first.code}})`);
      let data=first.data?.up_list||{{}};
      let items=Array.isArray(data)?data:(data.items||[]);
      for(const u of items) seen.set(String(u.mid),{{
        mid:String(u.mid),name:u.uname||'',has_update:Boolean(u.has_update)
      }});
      let offset=Array.isArray(data)?'':(data.offset||'');
      let hasMore=Array.isArray(data)?false:Boolean(data.has_more);
      for(let page=1;page<{max_pages}&&hasMore&&offset;page++){{
        if({delay_ms}>0) await new Promise(r=>setTimeout(r,{delay_ms}));
        const q=new URLSearchParams({{offset,platform:'web'}});
        const j=await (await fetch(
          'https://api.bilibili.com/x/polymer/web-dynamic/v1/uplist?'+q,
          {{credentials:'include'}})).json();
        if(j.code!==0) throw new Error(`uplist failed: ${{j.message}} (${{j.code}})`);
        data=j.data||{{}};
        items=data.items||[];
        for(const u of items) seen.set(String(u.mid),{{
          mid:String(u.mid),name:u.uname||'',has_update:Boolean(u.has_update)
        }});
        const next=data.offset||'';
        hasMore=Boolean(data.has_more)&&next&&next!==offset;
        offset=next;
      }}
      return Array.from(seen.values());
    }})()"""
    return session.eval(expression)


def fetch_video_feed(
    session: BrowserSession,
    pages: int,
    delay_ms: int,
) -> dict[str, Any]:
    expression = f"""(async()=>{{
      const items=[];
      let offset='';
      let latest='';
      let complete=false;
      for(let page=1;page<={pages};page++){{
        const q=new URLSearchParams({{
          timezone_offset:'-480',type:'video',platform:'web',page:String(page)
        }});
        if(offset) q.set('offset',offset);
        const j=await (await fetch(
          'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/all?'+q,
          {{credentials:'include'}})).json();
        if(j.code!==0) throw new Error(`feed failed: ${{j.message}} (${{j.code}})`);
        const d=j.data||{{}};
        if(!latest) latest=String(d.update_baseline||d.items?.[0]?.id_str||'');
        const rows=d.items||[];
        for(const item of rows){{
          const archive=item.modules?.module_dynamic?.major?.archive;
          const author=item.modules?.module_author;
          if(!archive?.bvid||!author?.mid) continue;
          items.push({{
            dynamic_id:String(item.id_str||''),bvid:String(archive.bvid),
            title:archive.title||'',creator_mid:String(author.mid),
            creator_name:author.name||'',published_at:Number(author.pub_ts||0),
            published_text:author.pub_time||'',duration_text:archive.duration_text||'',
            url:`https://www.bilibili.com/video/${{archive.bvid}}`
          }});
        }}
        const next=String(d.offset||rows.at(-1)?.id_str||'');
        if(!d.has_more||!rows.length||!next||next===offset){{complete=true;break;}}
        offset=next;
        if({delay_ms}>0) await new Promise(r=>setTimeout(r,{delay_ms}));
      }}
      return {{latest_dynamic_id:latest,complete,items}};
    }})()"""
    return session.eval(expression, timeout=max(120, pages * 4))


def fetch_history(
    session: BrowserSession,
    pages: int,
    cutoff_ts: int,
    delay_ms: int,
) -> list[dict[str, Any]]:
    expression = f"""(async()=>{{
      const items=[];
      let cursor={{max:'0',view_at:'0',business:''}};
      let previous='';
      for(let page=0;page<{pages};page++){{
        const q=new URLSearchParams({{ps:'30',type:'archive'}});
        if(page>0){{
          q.set('max',String(cursor.max||0));
          q.set('view_at',String(cursor.view_at||0));
          q.set('business',String(cursor.business||''));
        }}
        const j=await (await fetch(
          'https://api.bilibili.com/x/web-interface/history/cursor?'+q,
          {{credentials:'include'}})).json();
        if(j.code!==0) throw new Error(`history failed: ${{j.message}} (${{j.code}})`);
        const rows=j.data?.list||[];
        for(const item of rows){{
          const bvid=item.history?.bvid;
          if(!bvid) continue;
          items.push({{
            bvid:String(bvid),view_at:Number(item.view_at||0),
            progress:Number(item.progress||0),duration:Number(item.duration||0)
          }});
        }}
        cursor=j.data?.cursor||{{}};
        const marker=`${{cursor.max||0}}:${{cursor.view_at||0}}:${{cursor.business||''}}`;
        const oldest=rows.at(-1)?.view_at||0;
        if(rows.length<30||marker===previous||({cutoff_ts}>0&&oldest<{cutoff_ts})) break;
        previous=marker;
        if({delay_ms}>0) await new Promise(r=>setTimeout(r,{delay_ms}));
      }}
      return items;
    }})()"""
    return session.eval(expression, timeout=max(120, pages * 4))


def parse_duration(value: str) -> int:
    parts = value.strip().split(":") if value else []
    if not parts or any(not part.isdigit() for part in parts) or len(parts) > 3:
        return 0
    total = 0
    for part in parts:
        total = total * 60 + int(part)
    return total


def classify_watch(record: dict[str, Any] | None) -> tuple[str, int, int]:
    if record is None:
        return "unwatched", 0, 0
    progress = int(record.get("progress") or 0)
    duration = int(record.get("duration") or 0)
    if progress < 0 or (duration > 0 and progress >= duration):
        return "finished", max(progress, duration), duration
    if progress == 0:
        return "opened", 0, duration
    return "partial", progress, duration


def build_inbox(
    videos: list[dict[str, Any]],
    history: list[dict[str, Any]],
    recommended_ups: list[dict[str, Any]],
    *,
    since_hours: int,
    min_duration_minutes: int,
    unwatched_only: bool,
    recommended_only: bool,
    limit: int,
    now_ts: int | None = None,
) -> list[dict[str, Any]]:
    now_ts = now_ts or int(time.time())
    cutoff = now_ts - max(since_hours, 0) * 3600 if since_hours else 0
    history_by_bvid: dict[str, dict[str, Any]] = {}
    for item in history:
        history_by_bvid.setdefault(str(item.get("bvid") or ""), item)
    recommended = {
        str(item.get("mid")) for item in recommended_ups if item.get("has_update")
    }

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for video in sorted(videos, key=lambda item: int(item.get("published_at") or 0), reverse=True):
        bvid = str(video.get("bvid") or "")
        if not bvid or bvid in seen:
            continue
        seen.add(bvid)
        published_at = int(video.get("published_at") or 0)
        if cutoff and published_at < cutoff:
            continue
        duration = parse_duration(str(video.get("duration_text") or ""))
        if duration < max(min_duration_minutes, 0) * 60:
            continue
        creator_mid = str(video.get("creator_mid") or "")
        is_recommended = creator_mid in recommended
        if recommended_only and not is_recommended:
            continue
        watch_state, progress, history_duration = classify_watch(history_by_bvid.get(bvid))
        if unwatched_only and watch_state != "unwatched":
            continue
        rows.append(
            {
                **video,
                "duration_seconds": duration or history_duration,
                "official_update": is_recommended,
                "watch_state": watch_state,
                "progress_seconds": progress,
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _escape_md(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: dict[str, Any]) -> str:
    rows = payload.get("items", [])
    lines = [
        f"# {payload.get('title', 'Bilibili 数据')}",
        "",
        f"生成时间：{payload.get('generated_at', '')}",
        "",
    ]
    if payload.get("kind") == "followings":
        lines.extend(["| UID | UP 主 | 简介 | 特别关注 |", "|---|---|---|---|"])
        for row in rows:
            lines.append(
                f"| {_escape_md(row.get('mid'))} | {_escape_md(row.get('name'))} | "
                f"{_escape_md(row.get('sign'))} | {'是' if row.get('special') else '否'} |"
            )
    elif payload.get("kind") == "recommended-ups":
        lines.extend(["| UID | UP 主 | 有更新 |", "|---|---|---|"])
        for row in rows:
            lines.append(
                f"| {_escape_md(row.get('mid'))} | {_escape_md(row.get('name'))} | "
                f"{'是' if row.get('has_update') else '否'} |"
            )
    else:
        lines.extend(
            [
                "| 时间 | UP 主 | 视频 | 时长 | 观看状态 | 官方更新 |",
                "|---|---|---|---:|---|---|",
            ]
        )
        for row in rows:
            title = f"[{_escape_md(row.get('title'))}]({_escape_md(row.get('url'))})"
            lines.append(
                f"| {_escape_md(row.get('published_text'))} | {_escape_md(row.get('creator_name'))} | "
                f"{title} | {_escape_md(row.get('duration_text'))} | "
                f"{_escape_md(row.get('watch_state'))} | {'是' if row.get('official_update') else '否'} |"
            )
    lines.append("")
    return "\n".join(lines)


def render_csv(payload: dict[str, Any]) -> str:
    rows = payload.get("items", [])
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def serialize(payload: dict[str, Any], output_format: str) -> str:
    if output_format == "json":
        return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if output_format == "md":
        return render_markdown(payload)
    if output_format == "csv":
        return render_csv(payload)
    raise InboxError(f"unsupported output format: {output_format}")


def write_output(content: str, out: str | None, force: bool) -> None:
    if not out:
        sys.stdout.write(content)
        return
    path = Path(out).expanduser().resolve()
    if path.exists() and not force:
        raise InboxError(f"output already exists: {path}; pass --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(path)


def payload(kind: str, title: str, items: list[dict[str, Any]], **summary: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": kind,
        "title": title,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "items": items,
    }


def add_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=["json", "md", "csv"], default="json")
    parser.add_argument("--out", help="Optional output file; stdout when omitted")
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    followings = sub.add_parser("followings", help="Export the complete following list")
    followings.add_argument("--max-pages", type=int, default=100)
    followings.add_argument("--delay-ms", type=int, default=500)
    add_output_args(followings)

    recommended = sub.add_parser(
        "recommended-ups", help="List UPs displayed by the official dynamic portal"
    )
    recommended.add_argument("--include-no-update", action="store_true")
    add_output_args(recommended)

    inbox = sub.add_parser("inbox", help="Build a recent followed-video learning inbox")
    inbox.add_argument("--feed-pages", type=int, default=5)
    inbox.add_argument("--history-pages", type=int, default=10)
    inbox.add_argument("--delay-ms", type=int, default=300)
    inbox.add_argument("--since-hours", type=int, default=168)
    inbox.add_argument("--min-duration-minutes", type=int, default=10)
    inbox.add_argument("--limit", type=int, default=50)
    inbox.add_argument("--unwatched-only", action=argparse.BooleanOptionalAction, default=True)
    inbox.add_argument("--recommended-only", action="store_true")
    add_output_args(inbox)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        with BrowserSession() as session:
            account = fetch_account(session)
            if args.command == "followings":
                result = fetch_followings(
                    session, account["mid"], max(args.max_pages, 1), max(args.delay_ms, 0)
                )
                items = result.get("items", [])
                data = payload(
                    "followings",
                    "Bilibili 关注列表",
                    items,
                    total=result.get("total", len(items)),
                    exported=len(items),
                    complete=bool(result.get("complete")),
                )
            elif args.command == "recommended-ups":
                items = fetch_recommended_ups(session)
                if not args.include_no_update:
                    items = [item for item in items if item.get("has_update")]
                data = payload(
                    "recommended-ups",
                    "Bilibili 官方动态页更新 UP",
                    items,
                    count=len(items),
                )
            else:
                feed = fetch_video_feed(
                    session, max(args.feed_pages, 1), max(args.delay_ms, 0)
                )
                videos = feed.get("items", [])
                earliest = min(
                    (int(item.get("published_at") or 0) for item in videos), default=0
                )
                history = fetch_history(
                    session,
                    max(args.history_pages, 1),
                    earliest,
                    max(args.delay_ms, 0),
                )
                recommended = fetch_recommended_ups(session)
                items = build_inbox(
                    videos,
                    history,
                    recommended,
                    since_hours=max(args.since_hours, 0),
                    min_duration_minutes=max(args.min_duration_minutes, 0),
                    unwatched_only=args.unwatched_only,
                    recommended_only=args.recommended_only,
                    limit=max(args.limit, 1),
                )
                data = payload(
                    "inbox",
                    "Bilibili 最近未看学习候选",
                    items,
                    candidate_videos=len(videos),
                    history_records=len(history),
                    official_updated_ups=sum(1 for item in recommended if item.get("has_update")),
                    feed_complete=bool(feed.get("complete")),
                )
        write_output(serialize(data, args.format), args.out, args.force)
        return 0
    except (InboxError, subprocess.TimeoutExpired) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
