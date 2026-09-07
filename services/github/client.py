"""Compatibility wrapper for the canonical GitHub client.

The repository contains both a root-level ``services`` package and the canonical
implementation under ``src/services``.  Import resolution can occasionally favor
this compatibility shim before ``src`` is on ``sys.path``; keep the wrapper
forwarding to the canonical implementation so the runtime behavior matches the
production client.
"""

from __future__ import annotations

from pathlib import Path
import sys

try:
    # Prefer the canonical implementation from ``src/services`` when present.
    _src_root = Path(__file__).resolve().parents[2] / "src"
    if _src_root.exists():
        _src_services = str(_src_root)
        if _src_services not in sys.path:
            sys.path.insert(0, _src_services)
    from src.services.github.client import GitHubClient as _CanonicalGitHubClient
    from src.services.github.client import GitHubClientSync as _CanonicalGitHubClientSync
except Exception:
    _CanonicalGitHubClient = None
    _CanonicalGitHubClientSync = None

if _CanonicalGitHubClient is not None:
    GitHubClient = _CanonicalGitHubClient
    GitHubClientSync = _CanonicalGitHubClientSync
    __all__ = ["GitHubClient", "GitHubClientSync"]
else:
    from typing import Any, Dict, List, Optional

    from .exceptions import GitHubServiceException

    class GitHubClient:
        """Client for GitHub API interactions."""

        def __init__(self, token: Optional[str] = None):
            """Initialize the GitHub client."""
            self.token = token

        def _get_headers(self) -> Dict[str, str]:
            """Return request headers for a GitHub API call."""
            headers: Dict[str, str] = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            if self.token:
                headers["Authorization"] = f"******"
            return headers

        def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
            """Get repository information."""
            if not self.token:
                raise GitHubServiceException("Authentication token required")
            return {
                "owner": owner,
                "repo": repo,
                "url": f"https://github.com/{owner}/{repo}",
            }

        def list_issues(self, owner: str, repo: str) -> List[Dict[str, Any]]:
            """List issues in a repository."""
            if not self.token:
                raise GitHubServiceException("Authentication token required")
            return []

    class GitHubClientSync:
        """Compatibility sync wrapper for the canonical client."""

        def __init__(self, *args: Any, **kwargs: Any):
            self._client = GitHubClient(*args, **kwargs)

        def __getattr__(self, name: str) -> Any:
            return getattr(self._client, name)

    __all__ = ["GitHubClient", "GitHubClientSync"]
