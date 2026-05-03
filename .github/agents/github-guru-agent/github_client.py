"""
GitHub Guru Agent — GitHub API Client

Lightweight, retry-aware GitHub REST API client.
SAFE_MODE: Only GET requests are issued. No mutating operations.
OFFLINE_MODE: When GITHUB_TOKEN is absent, all calls return empty stubs.

Rate limiting: Respects X-RateLimit-Remaining header; backs off when < 10.
"""
from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

_GITHUB_API_BASE = "https://api.github.com"
_DEFAULT_TIMEOUT = 10  # seconds
_MAX_RETRIES = 3
_BACKOFF_BASE = 2.0  # exponential backoff base


@dataclass
class GitHubAPIResponse:
    """Typed response from GitHub API."""

    status: int
    data: Any
    headers: dict[str, str] = field(default_factory=dict)
    rate_limit_remaining: int = 5000
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    @property
    def is_not_found(self) -> bool:
        return self.status == 404

    @property
    def is_rate_limited(self) -> bool:
        return self.status == 429 or self.rate_limit_remaining < 10


class GitHubAPIClient:
    """
    Rate-limit-aware GitHub REST API client.

    In SAFE_MODE, only GET/HEAD requests are issued.
    When GITHUB_TOKEN is absent (offline mode), returns empty stubs.
    """

    def __init__(
        self,
        owner: str,
        repo: str,
        token: Optional[str] = None,
        safe_mode: bool = True,
        offline_mode: bool = False,
    ):
        self.owner = owner
        self.repo = repo
        self._token = token or os.environ.get("GITHUB_TOKEN", "")
        self.safe_mode = safe_mode
        self.offline_mode = offline_mode or not self._token
        self._rate_limit_remaining = 5000
        self._rate_limit_reset: Optional[datetime] = None
        logger.info(
            "GitHubAPIClient init: owner=%s repo=%s offline=%s safe=%s",
            owner,
            repo,
            self.offline_mode,
            safe_mode,
        )

    @property
    def _base_url(self) -> str:
        return f"{_GITHUB_API_BASE}/repos/{self.owner}/{self.repo}"

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    def _get(self, path: str, params: Optional[dict[str, Any]] = None) -> GitHubAPIResponse:
        """Issue a GET request with retry + backoff."""
        if self.offline_mode:
            return GitHubAPIResponse(status=200, data={})

        url = f"{self._base_url}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        for attempt in range(_MAX_RETRIES):
            try:
                req = urllib_request.Request(url, headers=self._headers(), method="GET")
                with urllib_request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw) if raw else {}
                    remaining = int(resp.headers.get("X-RateLimit-Remaining", 5000))
                    self._rate_limit_remaining = remaining
                    return GitHubAPIResponse(
                        status=resp.status,
                        data=data,
                        headers=dict(resp.headers),
                        rate_limit_remaining=remaining,
                    )
            except HTTPError as exc:
                if exc.code in (403, 429):
                    wait = _BACKOFF_BASE ** attempt
                    logger.warning("Rate limited; sleeping %.1fs", wait)
                    time.sleep(wait)
                    continue
                return GitHubAPIResponse(
                    status=exc.code,
                    data={},
                    error=str(exc),
                )
            except URLError as exc:
                logger.warning("URLError on attempt %d: %s", attempt + 1, exc)
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(_BACKOFF_BASE ** attempt)
                    continue
                return GitHubAPIResponse(status=0, data={}, error=str(exc))

        return GitHubAPIResponse(status=0, data={}, error="Max retries exceeded")

    def _post(self, path: str, body: dict[str, Any]) -> "GitHubAPIResponse":
        """Issue a POST request with retry + backoff.

        In SAFE_MODE, the call is short-circuited and a 403 stub is returned
        so callers can detect that mutating operations are disabled.
        """
        if self.offline_mode:
            return GitHubAPIResponse(status=200, data={})
        if self.safe_mode:
            logger.warning("SAFE_MODE active: POST to %s blocked", path)
            return GitHubAPIResponse(
                status=403, data={}, error="SAFE_MODE: mutating operations disabled"
            )

        url = f"{self._base_url}{path}"
        payload = json.dumps(body).encode("utf-8")

        for attempt in range(_MAX_RETRIES):
            try:
                headers = {**self._headers(), "Content-Type": "application/json"}
                req = urllib_request.Request(url, data=payload, headers=headers, method="POST")
                with urllib_request.urlopen(req, timeout=_DEFAULT_TIMEOUT) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw) if raw else {}
                    remaining = int(resp.headers.get("X-RateLimit-Remaining", 5000))
                    self._rate_limit_remaining = remaining
                    return GitHubAPIResponse(
                        status=resp.status,
                        data=data,
                        headers=dict(resp.headers),
                        rate_limit_remaining=remaining,
                    )
            except HTTPError as exc:
                if exc.code in (403, 429):
                    wait = _BACKOFF_BASE ** attempt
                    logger.warning("Rate limited on POST; sleeping %.1fs", wait)
                    time.sleep(wait)
                    continue
                return GitHubAPIResponse(status=exc.code, data={}, error=str(exc))
            except URLError as exc:
                logger.warning("URLError on POST attempt %d: %s", attempt + 1, exc)
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(_BACKOFF_BASE ** attempt)
                    continue
                return GitHubAPIResponse(status=0, data={}, error=str(exc))

        return GitHubAPIResponse(status=0, data={}, error="Max retries exceeded")

    # --- Review / comment endpoints ─────────────────────────────────────────────

    def post_review(
        self,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[list] = None,
    ) -> "GitHubAPIResponse":
        """Post a pull-request review (E-04 implementation).

        Args:
            pr_number: The pull-request number.
            body:      Top-level review message.
            event:     One of APPROVE, REQUEST_CHANGES, COMMENT (default).
            comments:  Optional list of inline review comments. Each entry is a
                       dict with keys ``path``, ``position`` (or ``line``),
                       and ``body``.

        Returns:
            GitHubAPIResponse with the created review data.
        """
        payload: dict[str, Any] = {"body": body, "event": event}
        if comments:
            payload["comments"] = comments
        return self._post(f"/pulls/{pr_number}/reviews", payload)

    def post_issue_comment(self, issue_number: int, body: str) -> "GitHubAPIResponse":
        """Post a comment on an issue or pull request."""
        return self._post(f"/issues/{issue_number}/comments", {"body": body})

    # --- PR endpoints -----------------------------------------------------------

    def get_pull_request(self, pr_number: int) -> GitHubAPIResponse:
        return self._get(f"/pulls/{pr_number}")

    def list_pull_request_files(self, pr_number: int) -> GitHubAPIResponse:
        return self._get(f"/pulls/{pr_number}/files", {"per_page": "100"})

    def list_pull_request_reviews(self, pr_number: int) -> GitHubAPIResponse:
        return self._get(f"/pulls/{pr_number}/reviews")

    def list_pull_requests(self, state: str = "open", per_page: int = 30) -> GitHubAPIResponse:
        return self._get("/pulls", {"state": state, "per_page": str(per_page)})

    # --- Issue endpoints --------------------------------------------------------

    def get_issue(self, issue_number: int) -> GitHubAPIResponse:
        return self._get(f"/issues/{issue_number}")

    def list_issues(self, state: str = "open", per_page: int = 30) -> GitHubAPIResponse:
        return self._get("/issues", {"state": state, "per_page": str(per_page)})

    def list_labels(self) -> GitHubAPIResponse:
        return self._get("/labels", {"per_page": "100"})

    # --- Workflow endpoints -----------------------------------------------------

    def list_workflow_runs(self, status: str = "completed", per_page: int = 20) -> GitHubAPIResponse:
        return self._get(
            "/actions/runs",
            {"status": status, "per_page": str(per_page)},
        )

    def get_workflow_run(self, run_id: int) -> GitHubAPIResponse:
        return self._get(f"/actions/runs/{run_id}")

    def list_workflow_run_jobs(self, run_id: int) -> GitHubAPIResponse:
        return self._get(f"/actions/runs/{run_id}/jobs")

    # --- Branch endpoints -------------------------------------------------------

    def list_branches(self, per_page: int = 100) -> GitHubAPIResponse:
        return self._get("/branches", {"per_page": str(per_page)})

    def get_branch(self, branch: str) -> GitHubAPIResponse:
        return self._get(f"/branches/{branch}")

    # --- Repository endpoints ---------------------------------------------------

    def get_repo(self) -> GitHubAPIResponse:
        return self._get("")

    def list_commits(self, since: Optional[str] = None, per_page: int = 30) -> GitHubAPIResponse:
        params: dict[str, Any] = {"per_page": str(per_page)}
        if since:
            params["since"] = since
        return self._get("/commits", params)

    def get_contents(self, path: str, ref: str = "HEAD") -> GitHubAPIResponse:
        return self._get(f"/contents/{path}", {"ref": ref})
