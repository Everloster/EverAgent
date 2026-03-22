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
    if not html:
        return []
    
    repos = parse_trending_repos(html)
    
    for repo in repos:
        repo["period"] = since
        repo["fetched_at"] = datetime.now().isoformat()
    
    return repos


def check_report_exists(base_dir: Path, owner: str, repo: str) -> Optional[Dict]:
    """
    Check if a report exists and when it was last updated.
    
    Returns None if doesn't exist, or dict with 'path' and 'age_days'.
    """
    report_path = base_dir / f"research_{owner}_{repo}.md"
    
    if not report_path.exists():
        return None
    
    mtime = report_path.stat().st_mtime
    age_seconds = time.time() - mtime
    age_days = age_seconds / (24 * 60 * 60)
    
    return {
        "path": str(report_path),
        "age_days": age_days,
        "needs_update": age_days > 7
    }


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
                "needs_update": result["needs_update"]
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
