#!/usr/bin/env python3
"""
GitHub Trending Fetcher
Fetches trending repositories from GitHub and outputs structured data.

Cross-platform compatible - works on macOS, Linux, and Windows.
"""

import json
import os
import platform
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def get_skill_dir() -> Path:
    """
    Get the directory where this skill is located.
    Works regardless of current working directory.
    """
    return Path(__file__).parent.resolve()


def get_default_reports_dir() -> Path:
    """
    Get default reports directory.
    Priority:
    1. TRENDING_REPORTS_DIR environment variable
    2. github-trending-reports in current working directory
    """
    env_dir = os.environ.get("TRENDING_REPORTS_DIR")
    if env_dir:
        return Path(env_dir)
    return Path.cwd() / "github-trending-reports"


def get_user_agent() -> str:
    """
    Generate a platform-appropriate User-Agent string.
    Uses the actual platform instead of hardcoding macOS.
    """
    system = platform.system()
    if system == "Darwin":
        return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    elif system == "Windows":
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    elif system == "Linux":
        return "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
    else:
        return "Mozilla/5.0 (compatible; GitHub-Trending-Analyzer/1.0)"


def fetch_trending_page(since: str = "daily", language: str = "") -> str:
    """
    Fetch GitHub trending page HTML.
    
    Args:
        since: Time period - 'daily', 'weekly', or 'monthly'
        language: Programming language filter (optional)
    """
    url = "https://github.com/trending"
    if language:
        url += f"/{language}"
    url += f"?since={since}"
    
    headers = {
        "User-Agent": get_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }
    
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.environ.get('GITHUB_TOKEN')}"
    
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            return response.read().decode("utf-8")
    except (HTTPError, URLError) as e:
        print(f"Error fetching trending page: {e}", file=sys.stderr)
        return ""


def parse_trending_repos(html: str) -> List[Dict]:
    """
    Parse trending repositories from HTML.
    
    Returns list of dicts with: owner, repo, url, description, language, stars, forks, today_stars
    """
    repos = []
    
    repo_pattern = r'<article[^>]*class="[^"]*Box-row[^"]*"[^>]*>(.*?)</article>'
    repo_matches = re.findall(repo_pattern, html, re.DOTALL)
    
    for match in repo_matches:
        repo = {}
        
        owner_repo_match = re.search(r'<h2[^>]*>.*?href="/([^"]+)"', match, re.DOTALL)
        if owner_repo_match:
            path = owner_repo_match.group(1).strip()
            parts = path.split("/")
            if len(parts) >= 2:
                repo["owner"] = parts[0]
                repo["repo"] = parts[1]
                repo["url"] = f"https://github.com/{parts[0]}/{parts[1]}"
        
        desc_match = re.search(r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>', match, re.DOTALL)
        if desc_match:
            desc = re.sub(r'<[^>]+>', '', desc_match.group(1))
            repo["description"] = desc.strip()
        else:
            repo["description"] = ""
        
        lang_match = re.search(r'<span[^>]*itemprop="programmingLanguage"[^>]*>([^<]+)</span>', match)
        if lang_match:
            repo["language"] = lang_match.group(1).strip()
        else:
            repo["language"] = "Unknown"
        
        stars_match = re.search(r'href="/[^"]+/stargazers"[^>]*>.*?</svg>\s*([\d,]+)\s*</a>', match, re.DOTALL)
        if stars_match:
            repo["stars"] = int(stars_match.group(1).replace(",", ""))
        else:
            repo["stars"] = 0
        
        forks_match = re.search(r'href="/[^"]+/forks"[^>]*>.*?</svg>\s*([\d,]+)\s*</a>', match, re.DOTALL)
        if forks_match:
            repo["forks"] = int(forks_match.group(1).replace(",", ""))
        else:
            repo["forks"] = 0
        
        today_match = re.search(r'([\d,]+)\s*stars?\s*today', match)
        if today_match:
            repo["today_stars"] = int(today_match.group(1).replace(",", ""))
        else:
            repo["today_stars"] = 0
        
        if "owner" in repo and "repo" in repo:
            repos.append(repo)
    
    return repos


def fetch_trending_via_api(since: str = "daily", language: str = "") -> List[Dict]:
    """
    Fetch trending repositories via GitHub Search API (fallback).

    Args:
        since: Time period - 'daily', 'weekly', or 'monthly'
        language: Programming language filter (optional)

    Returns:
        List of repository dictionaries, or empty list on failure
    """
    days_map = {"daily": 1, "weekly": 7, "monthly": 30}
    days = days_map.get(since, 1)

    from datetime import timedelta
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    q = f"created:>{cutoff}"
    if language:
        q += f" language:{language}"

    url = (
        f"https://api.github.com/search/repositories"
        f"?q={q}&sort=stars&order=desc&per_page=25"
    )

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": get_user_agent(),
    }
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"token {os.environ.get('GITHUB_TOKEN')}"

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError) as e:
        print(f"Error fetching from GitHub Search API: {e}", file=sys.stderr)
        return []

    repos = []
    fetched_at = datetime.now().isoformat()
    for item in data.get("items", []):
        owner = item.get("owner", {}).get("login", "")
        repo_name = item.get("name", "")
        if not owner or not repo_name:
            continue
        repos.append({
            "owner": owner,
            "repo": repo_name,
            "url": item.get("html_url", f"https://github.com/{owner}/{repo_name}"),
            "description": item.get("description") or "",
            "language": item.get("language") or "Unknown",
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "today_stars": 0,
            "period": since,
            "fetched_at": fetched_at,
            "source": "github_api",
        })
    return repos


def get_trending(since: str = "daily", language: str = "") -> List[Dict]:
    """
    Get trending repositories.
    
    Args:
        since: 'daily', 'weekly', or 'monthly'
        language: Optional language filter
    
    Returns:
        List of repository dictionaries
    """
    html = fetch_trending_page(since, language)
    repos = parse_trending_repos(html) if html else []

    if not repos:
        print(
            "HTML scraping returned no results, falling back to GitHub Search API...",
            file=sys.stderr,
        )
        return fetch_trending_via_api(since, language)

    fetched_at = datetime.now().isoformat()
    for repo in repos:
        repo["period"] = since
        repo["fetched_at"] = fetched_at
        repo["source"] = "html_scrape"

    return repos


def normalize_repo_name(name: str) -> str:
    """
    Normalize a repo/owner name for fuzzy matching.
    Converts to lowercase and replaces hyphens with underscores.
    Used only for comparison — never for generating actual file names.
    """
    return name.lower().replace("-", "_")


def check_report_exists(base_dir: Path, owner: str, repo: str) -> Optional[Dict]:
    """
    Check if a report exists and when it was last updated.

    First tries an exact match (preserving original case and hyphens).
    If not found, falls back to a case/hyphen-insensitive scan of the directory
    so that previously mis-named variants are detected and flagged rather than
    silently spawning a duplicate with a different name.

    Returns None if no match found, or a dict with:
      - 'path'         : str path to the found file
      - 'age_days'     : float days since last modification
      - 'needs_update' : bool (True if older than 7 days)
      - 'name_mismatch': bool (True when the found file name differs from the
                         canonical name — signals a pre-existing naming error)
    """
    canonical_name = f"research_{owner}_{repo}.md"
    canonical_path = base_dir / canonical_name

    # --- exact match (happy path) ---
    if canonical_path.exists():
        mtime = canonical_path.stat().st_mtime
        age_days = (time.time() - mtime) / 86400
        return {
            "path": str(canonical_path),
            "age_days": age_days,
            "needs_update": age_days > 7,
            "name_mismatch": False,
        }

    # --- fuzzy fallback: scan for case/hyphen variants ---
    canonical_norm = normalize_repo_name(f"research_{owner}_{repo}")
    if base_dir.exists():
        for f in base_dir.iterdir():
            if f.suffix != ".md":
                continue
            stem_norm = normalize_repo_name(f.stem)
            if stem_norm == canonical_norm:
                mtime = f.stat().st_mtime
                age_days = (time.time() - mtime) / 86400
                print(
                    f"Warning: found '{f.name}' but canonical name should be "
                    f"'{canonical_name}'. Consider renaming.",
                    file=sys.stderr,
                )
                return {
                    "path": str(f),
                    "age_days": age_days,
                    "needs_update": age_days > 7,
                    "name_mismatch": True,
                }

    return None


def main():
    """CLI interface."""
    if len(sys.argv) < 2:
        print("Usage: python trending_fetcher.py <command> [args]")
        print("Commands:")
        print("  fetch [daily|weekly|monthly] [language]  - Fetch trending repos")
        print("  check <owner/repo>                       - Check if report needs update")
        print("  info                                     - Show skill directory info")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "fetch":
        since = sys.argv[2] if len(sys.argv) > 2 else "daily"
        language = sys.argv[3] if len(sys.argv) > 3 else ""
        
        repos = get_trending(since, language)
        print(json.dumps(repos, indent=2, ensure_ascii=False))
    
    elif command == "check":
        if len(sys.argv) < 3:
            print("Usage: python trending_fetcher.py check <owner/repo>")
            sys.exit(1)
        
        repo_path = sys.argv[2]
        
        if "/" in repo_path:
            owner, repo = repo_path.split("/", 1)
        else:
            print("Invalid repo format. Use owner/repo")
            sys.exit(1)
        
        base_dir = get_default_reports_dir()
        result = check_report_exists(base_dir, owner, repo)
        
        if result:
            print(json.dumps({
                "exists": True,
                "path": result["path"],
                "age_days": round(result["age_days"], 1),
                "needs_update": result["needs_update"],
                "name_mismatch": result.get("name_mismatch", False),
            }))
        else:
            print(json.dumps({"exists": False, "needs_update": True}))
    
    elif command == "info":
        skill_dir = get_skill_dir()
        reports_dir = get_default_reports_dir()
        print(json.dumps({
            "skill_directory": str(skill_dir),
            "default_reports_directory": str(reports_dir),
            "platform": platform.system(),
            "python_version": platform.python_version()
        }, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
