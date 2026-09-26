"""GitHub HTTP client - Extracted utility for managing API requests.

This module provides a reusable HTTP client for GitHub API interactions,
extracted from the GitHubMCPPoster God Class (mcp_poster.py).

By extracting HTTP handling into a separate module:
- Reduces mcp_poster.py from 2691 LOC to ~1700 LOC
- Consolidates 8+ duplicate urllib.request patterns
- Improves testability of HTTP layer
- Enables reuse across other GitHub API clients
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlsplit, urlunsplit

logger = logging.getLogger(__name__)

_GITHUB_API = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"
_API_VERSION = "2022-11-28"


def redact_url_for_log(url: str) -> str:
    """Return URL without credentials, query, or fragment for safe logging."""
    if not url:
        return ""
    parts = urlsplit(url)
    host = parts.hostname or ""
    if host and ":" in host and not host.startswith("["):
        host = f"[{host}]"
    try:
        port = parts.port
    except ValueError:
        port = None
    netloc = f"{host}:{port}" if port is not None else host
    return urlunsplit((parts.scheme, netloc, parts.path, "", ""))


def validated_github_api_url(url: str) -> str:
    """Allow only credential-free HTTPS calls to api.github.com."""
    if not url:
        raise ValueError("GitHub API URL cannot be empty")
    if any(ch in url for ch in ("\x00", "\n", "\r", "\t")):
        raise ValueError("GitHub API URL contains control characters")
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "api.github.com":
        raise ValueError(f"GitHub API URL must target https://api.github.com: {url!r}")
    if parts.username or parts.password:
        raise ValueError("GitHub API URL must not contain embedded credentials")
    return url


class GitHubHTTPClient:
    """Encapsulates GitHub API HTTP operations.

    Extracted from GitHubMCPPoster to reduce God Class complexity.
    Consolidates all urllib.request patterns and error handling.
    """

    def __init__(self, token: str | None = None) -> None:
        """Initialize HTTP client with authentication token.

        Args:
            token: GitHub API token. If None, operations will fail without token.
        """
        self._token = token

    def make_request(
        self,
        method: str,
        url: str,
        data: dict[str, Any] | None = None,
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Make a GitHub API request.

        Consolidates duplicate urllib patterns from mcp_poster.py.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE, etc.)
            url: API endpoint URL (auto-prefixed with GITHUB_API)
            data: Request body as dictionary (auto-JSON encoded)
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response

        Raises:
            RuntimeError: If no token is configured
            urllib.error.HTTPError: On API errors
            ValueError: If URL validation fails
        """
        if not self._token:
            raise RuntimeError("No GitHub token configured. Set CODEX_MASTER_KEY or GITHUB_TOKEN.")

        # Ensure full URL
        if not url.startswith("https://"):
            url = f"{_GITHUB_API}{url}"

        validated_url = validated_github_api_url(url)

        # Prepare headers
        headers = {
            "Authorization": "******",
            "Accept": _ACCEPT,
            "X-GitHub-Api-Version": _API_VERSION,
        }

        # Encode body
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        # Make request
        try:
            req = urllib.request.Request(
                validated_url,
                data=body,
                headers=headers,
                method=method,
            )

            with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310 - URL is validated to api.github.com with a https-only allowlist
                response_body = resp.read().decode("utf-8")
                if response_body:
                    return json.loads(response_body)
                return {}

        except urllib.error.HTTPError as e:
            # Log safe error details without exposing request or response secrets.
            logger.error("GitHub API error: %s %s at %s", e.code, e.reason, redact_url_for_log(url))
            try:
                json.loads(e.read().decode("utf-8"))
            except Exception:
                pass
            logger.debug("GitHub API error details: status=%s reason=%s", e.code, e.reason)
            raise
        except urllib.error.URLError as e:
            logger.error("Network error: %s at %s", e.reason, redact_url_for_log(url))
            raise

    def get(
        self,
        url: str,
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Make a GET request.

        Args:
            url: API endpoint URL
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response
        """
        return self.make_request("GET", url, timeout=timeout)

    def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Make a POST request.

        Args:
            url: API endpoint URL
            data: Request body
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response
        """
        return self.make_request("POST", url, data=data, timeout=timeout)

    def patch(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Make a PATCH request.

        Args:
            url: API endpoint URL
            data: Request body
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response
        """
        return self.make_request("PATCH", url, data=data, timeout=timeout)

    def delete(
        self,
        url: str,
        timeout: int = 10,
    ) -> dict[str, Any]:
        """Make a DELETE request.

        Args:
            url: API endpoint URL
            timeout: Request timeout in seconds

        Returns:
            Parsed JSON response (usually empty)
        """
        return self.make_request("DELETE", url, timeout=timeout)
