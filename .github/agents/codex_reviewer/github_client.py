"""
GitHub API Client for Review Operations

Provides integration with GitHub REST API for posting reviews,
managing comments, and interacting with pull requests.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import urllib.parse
from dataclasses import dataclass
from typing import Any, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# ``requests`` is a hard runtime dependency (see pyproject.toml ``requests>=2.33.0``).
# It replaces the dynamic urllib fallback so no user-influenced URL is ever handed
# to ``urllib.request.urlopen`` (Semgrep dynamic-urllib-use-detected).
import json

import requests

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    token: Optional[str] = None
    base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3

    def __post_init__(self) -> None:
        """Reject unsafe API endpoints before any urllib fallback is used."""
        parsed = urllib.parse.urlsplit(self.base_url.rstrip("/"))
        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError("GitHub API base_url must be an https:// URL with a host")
        if parsed.username or parsed.password:
            raise ValueError("GitHub API base_url must not embed credentials")

    @classmethod
    def from_env(cls) -> "GitHubConfig":
        """Create configuration from environment variables."""
        return cls(
            token=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
            base_url=os.environ.get("GITHUB_API_URL", "https://api.github.com"),
        )


class GitHubAPIClient:
    """
    GitHub API client for PR review operations.

    Handles authentication, request formatting, error handling,
    and retry logic for GitHub API interactions.
    """

    def __init__(
        self,
        config: Optional[GitHubConfig] = None,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        """
        Initialize GitHub API client.

        Args:
            config: GitHub configuration (defaults to environment-based config)
            token: Optional token override for simple test/config usage.
            base_url: Optional base URL override.
        """
        if config is None:
            config = GitHubConfig(
                token=token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
                base_url=base_url or os.environ.get("GITHUB_API_URL", "https://api.github.com"),
                timeout=timeout or 30,
            )
        elif token is not None or base_url is not None:
            config = GitHubConfig(
                token=token if token is not None else config.token,
                base_url=base_url or config.base_url,
                timeout=timeout if timeout is not None else getattr(config, "timeout", 30),
                max_retries=getattr(config, "max_retries", 3),
            )

        self.config = config
        self.token = self.config.token
        self.base_url = self.config.base_url

        if not self.config.token:
            logger.warning("No GitHub token configured - API requests will fail")  # codeql[py/clear-text-logging-sensitive-data]

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CodexQuantumReviewer/1.0",
        }

        if self.config.token:
            headers["Authorization"] = f"token {self.config.token}"

        return headers

    @staticmethod
    def _normalize_repo_name(repo: str) -> str:
        """Normalize a repository identifier to owner/repo and reject malformed inputs."""
        if not isinstance(repo, str):
            raise ValueError("Repository must be a string in the format 'owner/repo'")

        candidate = repo.strip().strip("/")
        if not candidate:
            raise ValueError("Repository must not be empty")
        if "://" in candidate or candidate.startswith(("//", "http://", "https://")):
            raise ValueError("Repository must be 'owner/repo', not a URL")
        if any(part in ("", ".", "..") for part in candidate.split("/")):
            raise ValueError("Repository path contains empty or traversal segments")
        if candidate.startswith(".") or candidate.endswith("."):
            raise ValueError("Repository name must not start or end with a dot")
        if "?" in candidate or "#" in candidate or "\\" in candidate:
            raise ValueError("Repository name must not include query strings or path separators")

        if len(candidate.split("/")) != 2:
            raise ValueError("Repository must be in the format 'owner/repo'")

        owner, name = candidate.split("/", 1)
        if not re.fullmatch(r"[A-Za-z0-9._-]+", owner) or not re.fullmatch(r"[A-Za-z0-9._-]+", name):
            raise ValueError("Repository owner and name may only use GitHub-safe characters")
        return f"{owner}/{name}"

    @staticmethod
    def _has_unsafe_path_segments(path: str) -> bool:
        """Reject empty, dot, or traversal path segments after URL-decoding."""
        decoded = urllib.parse.unquote(path).replace("\\", "/").lstrip("/")
        if not decoded:
            return True
        segments = decoded.split("/")
        return any(segment in ("", ".", "..") for segment in segments)

    def _build_github_api_url(self, repo: str, api_path: str) -> str:
        """Build a GitHub API URL only from validated repo and API path segments."""
        repo_name = self._normalize_repo_name(repo)
        normalized_path = api_path.strip().lstrip("/")
        if not normalized_path:
            raise ValueError("GitHub API path must not be empty")
        if self._has_unsafe_path_segments(normalized_path):
            raise ValueError("GitHub API path contains empty or traversal segments")
        if "?" in normalized_path or "#" in normalized_path or "\\" in normalized_path:
            raise ValueError("GitHub API path must not include query strings or fragments")
        url = f"{self.config.base_url.rstrip('/')}/repos/{repo_name}/{normalized_path}"
        return self._validated_request_url(url)

    def _validated_request_url(self, url: str) -> str:
        """Enforce scheme/host parity with configured GitHub API base URL."""
        base = urllib.parse.urlsplit(self.config.base_url.rstrip("/"))
        target = urllib.parse.urlsplit(url)
        if target.scheme != "https" or not target.netloc:
            raise ValueError("GitHub request URL must be an absolute https URL")
        if target.username or target.password:
            raise ValueError("GitHub request URL must not include embedded credentials")
        if target.hostname != base.hostname:
            raise ValueError(
                f"GitHub request host mismatch: expected {base.hostname}, got {target.hostname}"
            )
        if target.query or target.fragment:
            raise ValueError("GitHub request URL must not include query parameters or fragments")

        base_path = (base.path or "").rstrip("/")
        expected_prefix = f"{base_path}/repos/" if base_path else "/repos/"
        if not target.path.startswith(expected_prefix):
            raise ValueError("GitHub request URL must target a GitHub repos API endpoint")
        if self._has_unsafe_path_segments(target.path):
            raise ValueError("GitHub request URL path contains traversal")
        return url

    async def post_review(
        self,
        repo: str,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Post a review to a pull request.

        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            body: Review body text (markdown)
            event: Review event type (APPROVE, REQUEST_CHANGES, COMMENT)
            comments: Optional inline comments

        Returns:
            GitHub API response

        Raises:
            Exception: If API request fails
        """
        url = self._build_github_api_url(repo, f"pulls/{pr_number}/reviews")

        payload = {
            "body": body,
            "event": event,
        }

        if comments:
            payload["comments"] = comments

        logger.info(f"Posting {event} review to {repo}#{pr_number}")  # codeql[py/clear-text-logging-sensitive-data]
        return await self._make_request(url, payload)

    async def _make_request(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Core request logic, exposed for tests and compatibility wrappers."""
        if HTTPX_AVAILABLE:
            return await self._post_with_httpx(url, payload)
        return await self._post_with_requests(url, payload)

    async def _post_with_httpx(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Post request using httpx library."""
        url = self._validated_request_url(url)
        async with httpx.AsyncClient() as client:
            for attempt in range(self.config.max_retries):
                try:
                    response = await client.post(
                        url,
                        json=payload,
                        headers=self._get_headers(),
                        timeout=self.config.timeout,
                    )

                    response.raise_for_status()
                    return response.json()

                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 422:
                        # Validation error - don't retry
                        logger.error(
                            "GitHub API validation error (status=%d).",
                            e.response.status_code,
                        )
                        raise

                    if attempt < self.config.max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Request failed, retrying in {wait_time}s...")  # codeql[py/clear-text-logging-sensitive-data]
                        await asyncio.sleep(wait_time)
                    else:
                        raise

                except Exception as e:
                    logger.error(f"Unexpected error posting review: {e}")  # codeql[py/clear-text-logging-sensitive-data]
                    raise

        return {}  # unreachable: loop always returns or raises

    async def _post_with_requests(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Fallback: POST via ``requests`` (no dynamic urllib use).

        The URL is still passed through ``_validated_request_url`` first, which
        enforces the configured ``GITHUB_API_URL`` scheme/host parity, preserves
        any configured base path, and rejects embedded credentials / traversal.
        The blocking ``requests`` call is dispatched to a thread-pool executor so
        the async event loop is never blocked.
        """
        url = self._validated_request_url(url)
        headers = self._get_headers()
        timeout = self.config.timeout

        def _do_post() -> dict[str, Any]:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()

        loop = asyncio.get_running_loop()
        for attempt in range(self.config.max_retries):
            try:
                return await loop.run_in_executor(None, _do_post)
            except requests.HTTPError as e:
                status = e.response.status_code if e.response is not None else 0
                if status == 422:
                    logger.error("GitHub API validation error (status=%d).", status)  # codeql[py/clear-text-logging-sensitive-data]
                    raise

                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Request failed, retrying in {wait_time}s...")  # codeql[py/clear-text-logging-sensitive-data]
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error posting review: {e}")  # codeql[py/clear-text-logging-sensitive-data]
                raise

        return {}  # unreachable: loop always returns or raises

    async def add_comment(
        self,
        repo: str,
        pr_number: int,
        body: str,
    ) -> dict[str, Any]:
        """
        Add a comment to a pull request.

        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            body: Comment body text (markdown)

        Returns:
            GitHub API response
        """
        url = self._build_github_api_url(repo, f"issues/{pr_number}/comments")

        payload = {"body": body}

        logger.info(f"Adding comment to {repo}#{pr_number}")  # codeql[py/clear-text-logging-sensitive-data]

        if HTTPX_AVAILABLE:
            return await self._post_with_httpx(url, payload)
        return await self._post_with_requests(url, payload)

    async def _get_json(self, url: str, headers: dict[str, str]) -> Any:
        """GET helper returning the decoded JSON body via ``requests``.

        No dynamic urllib use; the blocking call runs in a thread-pool executor.
        """
        loop = asyncio.get_running_loop()

        def _do_get() -> Any:
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            return response.json()

        return await loop.run_in_executor(None, _do_get)

    async def _get_text(self, url: str, headers: dict[str, str]) -> str:
        """GET helper returning the raw text body via ``requests``."""
        loop = asyncio.get_running_loop()

        def _do_get() -> str:
            response = requests.get(url, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()
            return response.text

        return await loop.run_in_executor(None, _do_get)

    async def get_pr_details(self, repo: str, pr_number: int) -> dict[str, Any]:
        """
        Get pull request details.

        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number

        Returns:
            PR details from GitHub API
        """
        url = self._build_github_api_url(repo, f"pulls/{pr_number}")

        headers = self._get_headers()

        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()
        else:
            return await self._get_json(url, headers)

    async def get_pr_files(self, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """
        Get list of files changed in a pull request.

        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number

        Returns:
            List of changed files from GitHub API
        """
        url = self._build_github_api_url(repo, f"pulls/{pr_number}/files")

        headers = self._get_headers()

        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.json()
        else:
            return await self._get_json(url, headers)

    async def get_pr_diff(self, repo: str, pr_number: int) -> str:
        """
        Get pull request diff.

        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number

        Returns:
            Unified diff string
        """
        url = self._build_github_api_url(repo, f"pulls/{pr_number}")

        headers = self._get_headers()
        headers["Accept"] = "application/vnd.github.v3.diff"

        if HTTPX_AVAILABLE:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, timeout=self.config.timeout)
                response.raise_for_status()
                return response.text
        else:
            return await self._get_text(url, headers)
