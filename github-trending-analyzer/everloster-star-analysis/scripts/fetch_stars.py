#!/usr/bin/env python3
"""Fetch all starred repos for the authenticated user via `gh api`.

Output: raw/page_NNN.json (one per page, NNN = 3-digit zero-padded)
Manifest: raw/manifest.json with total_pages, total_repos, fetched_at
Resume: skip pages whose file already exists.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PER_PAGE = 100
RAW_DIR = Path(__file__).resolve().parent.parent / "raw"


STAR_HEADER = ["-H", "Accept: application/vnd.github.star+json"]


def normalize(item: dict) -> dict:
    """star+json 媒体类型下,响应是 {starred_at, repo: {...}} 嵌套结构。
    拍平:把 repo.* 提到顶层,starred_at 保留在顶层。
    """
    if "repo" in item and isinstance(item["repo"], dict):
        flat = dict(item["repo"])
        flat["starred_at"] = item.get("starred_at")
        return flat
    return item


def fetch_page(page: int) -> list[dict]:
    result = subprocess.run(
        ["gh", "api", *STAR_HEADER, f"/user/starred?per_page={PER_PAGE}&page={page}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [normalize(it) for it in json.loads(result.stdout)]


def get_total_pages() -> int | None:
    """Parse Link header for rel=last page count."""
    result = subprocess.run(
        ["gh", "api", "-i", *STAR_HEADER, f"/user/starred?per_page=1&page=1"],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in result.stdout.splitlines():
        if line.lower().startswith("link:"):
            for part in line.split(","):
                if 'rel="last"' in part:
                    if "page=" in part:
                        try:
                            return int(part.split("page=")[-1].split(">")[0])
                        except (ValueError, IndexError):
                            return None
    return None


def normalize_existing() -> int:
    """In-place flatten: rewrite all raw/page_*.json to flat shape."""
    files = sorted(RAW_DIR.glob("page_*.json"))
    for f in files:
        items = json.loads(f.read_text())
        new_items = []
        for it in items:
            if "repo" in it and isinstance(it.get("repo"), dict):
                flat = dict(it["repo"])
                flat["starred_at"] = it.get("starred_at")
                new_items.append(flat)
            else:
                new_items.append(it)
        f.write_text(json.dumps(new_items, ensure_ascii=False, indent=2))
    print(f"[NORM] rewrote {len(files)} files", file=sys.stderr)
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--normalize-only", action="store_true",
                    help="rewrite existing raw/page_*.json to flat shape (no API calls)")
    args = ap.parse_args()
    if args.normalize_only:
        return normalize_existing()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    total = get_total_pages()
    if total is None:
        print("[WARN] cannot derive total pages, will stop on empty page", file=sys.stderr)

    print(f"[INFO] total_pages={total} per_page={PER_PAGE}", file=sys.stderr)
    started = time.time()

    fetched = 0
    skipped = 0
    for page in range(1, (total or 10**6) + 1):
        out = RAW_DIR / f"page_{page:03d}.json"
        if out.exists():
            skipped += 1
            continue
        try:
            data = fetch_page(page)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] page {page}: {e.stderr.strip()}", file=sys.stderr)
            return 1
        if not data:
            print(f"[INFO] empty page {page}, stop", file=sys.stderr)
            break
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        fetched += 1
        if page % 10 == 0 or page == 1:
            elapsed = time.time() - started
            rate = fetched / max(elapsed, 0.001)
            print(
                f"[INFO] page {page}/{total or '?'} ok, fetched={fetched}, "
                f"skipped={skipped}, rate={rate:.1f} page/s",
                file=sys.stderr,
            )
        if total is None and len(data) < PER_PAGE:
            print(f"[INFO] short page, stop", file=sys.stderr)
            break

    # Re-count all repos across all pages (skip manifest skip)
    all_files = sorted(RAW_DIR.glob("page_*.json"))
    total_repos = 0
    earliest: str | None = None
    latest: str | None = None
    for f in all_files:
        items = json.loads(f.read_text())
        total_repos += len(items)
        for it in items:
            sa = it.get("starred_at")
            if not sa:
                continue
            if earliest is None or sa < earliest:
                earliest = sa
            if latest is None or sa > latest:
                latest = sa

    manifest = {
        "user": "Everloster",
        "user_id": "2820419",
        "total_pages_reported_by_api": total,
        "pages_on_disk": len(all_files),
        "total_repos": total_repos,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "earliest_starred_at": earliest,
        "latest_starred_at": latest,
        "per_page": PER_PAGE,
    }
    (RAW_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    print(f"[DONE] {manifest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
