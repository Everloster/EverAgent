#!/usr/bin/env python3
"""
GitHub API client for deep research.
Uses the `gh` CLI (gh api) for all requests — authentication is handled by
the user's existing `gh auth login`, so no token management is needed.
"""

import json
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional


class GitHubAPIError(Exception):
    """Raised when GitHub API request fails."""


class GitHubAPI:
    """GitHub API client backed by the `gh` CLI."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub API client.

        Args:
            token: Ignored — kept for backward compatibility. `gh` uses its own
                   stored credentials (`gh auth login`).
        """
        if shutil.which("gh") is None:
            raise GitHubAPIError(
                "`gh` CLI not found. Install it and run `gh auth login`."
            )

    def _get(
        self, endpoint: str, params: Optional[Dict] = None, accept: Optional[str] = None
    ) -> Any:
        """Make a GET request via `gh api`."""
        cmd = ["gh", "api", endpoint.lstrip("/")]
        if accept:
            cmd += ["-H", f"Accept: {accept}"]
        if params:
            # `-X GET -f k=v` sends params as query string (plain `-f` would POST).
            cmd += ["-X", "GET"]
            for key, value in params.items():
                cmd += ["-f", f"{key}={value}"]

        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
        except (subprocess.SubprocessError, OSError) as e:
            raise GitHubAPIError(f"GitHub API request failed: GET {endpoint}: {e}") from e

        if proc.returncode != 0:
            message = f"GitHub API request failed: GET {endpoint}"
            if params:
                message += f" params={params}"
            raise GitHubAPIError(f"{message}: {proc.stderr.strip()}")

        if "application/vnd.github.raw" in (accept or ""):
            return proc.stdout
        try:
            return json.loads(proc.stdout)
        except (json.JSONDecodeError, ValueError) as e:
            raise GitHubAPIError(
                f"GitHub API returned non-JSON response for {endpoint}: {e}"
            ) from e

    def get_repo_info(self, owner: str, repo: str) -> Dict:
        """Get basic repository information."""
        return self._get(f"/repos/{owner}/{repo}")

    def get_readme(self, owner: str, repo: str) -> str:
        """Get repository README content as markdown."""
        try:
            return self._get(
                f"/repos/{owner}/{repo}/readme", accept="application/vnd.github.raw"
            )
        except Exception as e:
            return f"[README not found: {e}]"

    def get_tree(
        self, owner: str, repo: str, branch: str = "main", recursive: bool = True
    ) -> Dict:
        """Get repository directory tree."""
        params = {"recursive": "1"} if recursive else {}
        try:
            return self._get(f"/repos/{owner}/{repo}/git/trees/{branch}", params)
        except GitHubAPIError:
            # Try 'master' if 'main' fails
            if branch == "main":
                return self._get(f"/repos/{owner}/{repo}/git/trees/master", params)
            raise

    def get_file_content(self, owner: str, repo: str, path: str) -> str:
        """Get content of a specific file."""
        try:
            return self._get(
                f"/repos/{owner}/{repo}/contents/{path}",
                accept="application/vnd.github.raw",
            )
        except Exception as e:
            return f"[File not found: {e}]"

    def get_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Get repository languages and their bytes."""
        return self._get(f"/repos/{owner}/{repo}/languages")

    def get_contributors(self, owner: str, repo: str, limit: int = 30) -> List[Dict]:
        """Get repository contributors."""
        return self._get(
            f"/repos/{owner}/{repo}/contributors", params={"per_page": min(limit, 100)}
        )

    def get_recent_commits(
        self, owner: str, repo: str, limit: int = 50, since: Optional[str] = None
    ) -> List[Dict]:
        """
        Get recent commits.

        Args:
            owner: Repository owner
            repo: Repository name
            limit: Max commits to fetch
            since: ISO date string to fetch commits since
        """
        params = {"per_page": min(limit, 100)}
        if since:
            params["since"] = since
        return self._get(f"/repos/{owner}/{repo}/commits", params)

    def get_issues(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        limit: int = 30,
        labels: Optional[str] = None,
    ) -> List[Dict]:
        """
        Get repository issues.

        Args:
            state: 'open', 'closed', or 'all'
            labels: Comma-separated label names
        """
        params = {"state": state, "per_page": min(limit, 100)}
        if labels:
            params["labels"] = labels
        return self._get(f"/repos/{owner}/{repo}/issues", params)

    def get_pull_requests(
        self, owner: str, repo: str, state: str = "all", limit: int = 30
    ) -> List[Dict]:
        """Get repository pull requests."""
        return self._get(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": min(limit, 100)},
        )

    def get_releases(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """Get repository releases."""
        return self._get(
            f"/repos/{owner}/{repo}/releases", params={"per_page": min(limit, 100)}
        )

    def get_tags(self, owner: str, repo: str, limit: int = 20) -> List[Dict]:
        """Get repository tags."""
        return self._get(
            f"/repos/{owner}/{repo}/tags", params={"per_page": min(limit, 100)}
        )

    def search_issues(self, owner: str, repo: str, query: str, limit: int = 30) -> Dict:
        """Search issues and PRs in repository."""
        q = f"repo:{owner}/{repo} {query}"
        return self._get("/search/issues", params={"q": q, "per_page": min(limit, 100)})

    def get_commit_activity(self, owner: str, repo: str) -> List[Dict]:
        """Get weekly commit activity for the last year."""
        return self._get(f"/repos/{owner}/{repo}/stats/commit_activity")

    def get_code_frequency(self, owner: str, repo: str) -> List[List[int]]:
        """Get weekly additions/deletions."""
        return self._get(f"/repos/{owner}/{repo}/stats/code_frequency")

    def format_tree(self, tree_data: Dict, max_depth: int = 3) -> str:
        """
        Format tree data as text directory structure.

        Args:
            tree_data: Response from get_tree()
            max_depth: Maximum depth to display
        """
        if "tree" not in tree_data:
            return "[Unable to parse tree]"

        lines = []
        for item in tree_data["tree"]:
            path = item["path"]
            depth = path.count("/")
            if depth < max_depth:
                indent = "  " * depth
                name = path.split("/")[-1]
                if item["type"] == "tree":
                    lines.append(f"{indent}{name}/")
                else:
                    lines.append(f"{indent}{name}")

        return "\n".join(lines[:100])  # Limit output

    def summarize_repo(self, owner: str, repo: str) -> Dict:
        """
        Get comprehensive repository summary.

        Returns dict with: info, languages, contributor_count,
        recent_activity, top_issues, latest_release
        """
        info = self.get_repo_info(owner, repo)

        summary = {
            "name": info.get("full_name"),
            "description": info.get("description"),
            "url": info.get("html_url"),
            "stars": info.get("stargazers_count"),
            "forks": info.get("forks_count"),
            "open_issues": info.get("open_issues_count"),
            "language": info.get("language"),
            "license": info.get("license", {}).get("spdx_id")
            if info.get("license")
            else None,
            "created_at": info.get("created_at"),
            "updated_at": info.get("updated_at"),
            "pushed_at": info.get("pushed_at"),
            "default_branch": info.get("default_branch"),
            "topics": info.get("topics", []),
        }

        # Add languages
        try:
            summary["languages"] = self.get_languages(owner, repo)
        except (GitHubAPIError, Exception) as e:
            print(f"Warning: failed to fetch languages for {owner}/{repo}: {e}", file=sys.stderr)
            summary["languages"] = {}

        # Add contributor count
        try:
            # Approximate with first 100 contributors to avoid extra API calls.
            summary["contributor_count"] = len(self.get_contributors(owner, repo, limit=100))
        except (GitHubAPIError, Exception) as e:
            print(f"Warning: failed to fetch contributors for {owner}/{repo}: {e}", file=sys.stderr)
            summary["contributor_count"] = "N/A"

        # Latest release
        try:
            releases = self.get_releases(owner, repo, limit=1)
            if releases:
                summary["latest_release"] = {
                    "tag": releases[0].get("tag_name"),
                    "name": releases[0].get("name"),
                    "date": releases[0].get("published_at"),
                }
        except (GitHubAPIError, Exception) as e:
            print(f"Warning: failed to fetch releases for {owner}/{repo}: {e}", file=sys.stderr)
            summary["latest_release"] = None

        return summary


def main():
    """CLI interface for testing."""
    if len(sys.argv) < 3:
        print("Usage: python github_api.py <owner> <repo> [command]")
        print("Commands: info, readme, tree, file <path>, languages,")
        print("          contributors, commits, commit_activity, issues,")
        print("          prs, releases, tags, summary")
        sys.exit(1)

    owner, repo = sys.argv[1], sys.argv[2]
    command = sys.argv[3] if len(sys.argv) > 3 else "summary"

    api = GitHubAPI()

    commands = {
        "info": lambda: api.get_repo_info(owner, repo),
        "readme": lambda: api.get_readme(owner, repo),
        "tree": lambda: api.format_tree(api.get_tree(owner, repo)),
        # `file <path>`: read one source file (lever 1, code-grounded analysis).
        "file": lambda: api.get_file_content(owner, repo, sys.argv[4]),
        "languages": lambda: api.get_languages(owner, repo),
        "contributors": lambda: api.get_contributors(owner, repo),
        "commits": lambda: api.get_recent_commits(owner, repo),
        # `commit_activity`: weekly commit counts for the last 52 weeks (lever 3).
        "commit_activity": lambda: api.get_commit_activity(owner, repo),
        "issues": lambda: api.get_issues(owner, repo),
        "prs": lambda: api.get_pull_requests(owner, repo),
        "releases": lambda: api.get_releases(owner, repo),
        "tags": lambda: api.get_tags(owner, repo),
        "summary": lambda: api.summarize_repo(owner, repo),
    }

    if command == "file" and len(sys.argv) < 5:
        print("Usage: python github_api.py <owner> <repo> file <path>")
        sys.exit(1)

    if command not in commands:
        print(f"Unknown command: {command}")
        sys.exit(1)

    try:
        result = commands[command]()
        if isinstance(result, str):
            print(result)
        else:
            print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
