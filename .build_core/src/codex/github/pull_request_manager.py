"""Pull request operations for GitHub API.

Encapsulates PR creation, commenting, and management.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from codex.github.api_client import _GITHUB_API, APIClient

logger = logging.getLogger(__name__)


class PullRequestManager:
    """GitHub pull request operations.

    Handles:
    - Posting comments on PRs
    - Creating pull requests
    - Listing pull requests
    """

    def __init__(self, api_client: APIClient) -> None:
        """Initialize with an APIClient for making requests."""
        self._api = api_client

    def post_pr_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Post *body* as a comment on PR *pr_number* in *repo*.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format, e.g. ``"Aries-Serpent/_codex_"``.
        pr_number:
            PR number (int).
        body:
            Comment markdown body. Must start with ``@copilot`` for
            autonomous session triggering.

        Returns
        -------
        dict
            GitHub API response payload (includes ``html_url`` of comment).

        Raises
        ------
        RuntimeError
            If no token is available.
        urllib.error.HTTPError
            If GitHub returns a non-2xx status.
        """
        self._api._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
        return self._api._request("POST", url, {"body": body})

    def post_pr_comment_from_file(
        self,
        repo: str,
        pr_number: int,
        body_file: str | Path,
    ) -> dict[str, Any]:
        """Read *body_file* and post its contents as a PR comment."""
        body = Path(body_file).read_text()
        return self.post_pr_comment(repo, pr_number, body)

    def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = False,
    ) -> dict[str, Any]:
        """Open a pull request on GitHub.

        Requires the token to have ``pull-requests: write`` scope.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        title:
            PR title.
        body:
            PR description (markdown).
        head:
            Head (source) branch name, e.g. ``"0D_base_"``.
        base:
            Base (target) branch name, e.g. ``"main"``.
        draft:
            If ``True``, open the PR as a draft.

        Returns
        -------
        dict
            GitHub API response with ``number``, ``html_url``, etc.

        Raises
        ------
        urllib.error.HTTPError
            If the PR cannot be created (e.g. 422 on merge conflict).
        """
        self._api._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/pulls"
        payload = {
            "title": title,
            "body": body,
            "head": head,
            "base": base,
            "draft": draft,
        }
        result = self._api._request("POST", url, payload)
        # Record to cognitive brain
        self._api._record_cb_pattern(
            "CB-pr-create",
            f"create_pull_request: {title[:50]}",
            {"repo": repo, "head": head, "base": base, "title": title},
        )
        return result

    def list_pull_requests(
        self,
        repo: str,
        state: str = "open",
        head: str | None = None,
        base: str | None = None,
        per_page: int = 30,
    ) -> list[dict[str, Any]]:
        """List pull requests in a repository.

        Parameters
        ----------
        repo:
            ``"owner/repo"`` format.
        state:
            Filter by state: ``"open"``, ``"closed"``, or ``"all"``.
        head:
            Filter by head branch (format: ``"owner:branch"``).
        base:
            Filter by base branch name (e.g. ``"main"``).
        per_page:
            Number of results per page (max 100, default 30).

        Returns
        -------
        list[dict]
            List of PR objects with ``number``, ``title``, ``state``, etc.
        """
        self._api._require_token()
        url = f"{_GITHUB_API}/repos/{repo}/pulls"
        params = {"state": state, "per_page": min(per_page, 100)}
        if head:
            params["head"] = head
        if base:
            params["base"] = base

        # Build URL with query params
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        full_url = f"{url}?{param_str}"

        return self._api._get(full_url)
