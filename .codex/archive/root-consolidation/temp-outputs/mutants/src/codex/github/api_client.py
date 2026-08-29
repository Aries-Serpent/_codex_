"""Low-level HTTP/GraphQL communication and token management for GitHub API.

This module encapsulates all REST API and GraphQL communication,
token validation, and rate-limit handling.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

from codex.logging.structured_logger import logger
from scripts.ci._token_resolver import get_token

from . import url_utils

_GITHUB_API = "https://api.github.com"
_ACCEPT = "application/vnd.github+json"
_API_VERSION = "2022-11-28"

# Re-export for backward compatibility
_redact_url_for_log = url_utils.redact_url_for_log
_validated_github_api_url = url_utils.validate_github_api_url


class APIClient:
    """Low-level GitHub REST and GraphQL API client with token management.

    Handles:
    - Token resolution and validation
    - HTTP requests with retry logic
    - GraphQL queries with exponential backoff
    - Rate-limit handling
    """

    def __init__(self, token: str | None = None) -> None:
        """Initialize API client with token from environment or explicit parameter.

        Parameters
        ----------
        token:
            Explicit token to use. If None, resolves from environment in priority order:
            1. CODEX_MASTER_KEY
            2. CODEX_BACKUP_KEY
            3. GITHUB_TOKEN
        """
        # Try to get elevated token, fall back to GITHUB_TOKEN
        elevated_token = None
        try:
            elevated_token, elevated_source = get_token(required_elevated=True)
        except Exception:
            pass  # Will fall back to GITHUB_TOKEN below

        self._token = token or elevated_token or os.environ.get("GITHUB_TOKEN")

        # Track which key is active for health-check reporting (GAP-033).
        if token:
            self._token_source = "explicit"  # nosec B105 — label string, not a credential
        elif elevated_token:
            # Determine if it's CODEX_MASTER_KEY or CODEX_BACKUP_KEY
            try:
                _, source = get_token(required_elevated=True)
                self._token_source = source  # nosec B105 — env-var name label
            except Exception:
                self._token_source = "none"  # nosec B105 — sentinel label
        elif os.environ.get("GITHUB_TOKEN"):
            self._token_source = "GITHUB_TOKEN"  # nosec B105 — env-var name label
        else:
            self._token_source = "none"  # nosec B105 — sentinel label, not a credential

        if not self._token:
            logger.warning(
                "No GitHub token found. Set CODEX_MASTER_KEY or CODEX_BACKUP_KEY. "
                "See .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3."
            )

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def check_token_health(self) -> dict[str, object]:
        """Verify the active GitHub token and report its scopes / expiry.

        GAP-033: when CODEX_MASTER_KEY expires or is rotated, the
        self-healing loop silently degrades because @copilot only responds to
        comments that appear to come from @mbaetiong (which requires the key).
        The fallback chain (CODEX_BACKUP_KEY → GITHUB_TOKEN) keeps basic API
        calls alive but lacks the ``repo + workflow`` scopes needed for rescue
        comments and workflow dispatches.

        Returns
        -------
        dict
            With keys: source, login, scopes, has_master_key_scopes,
            expiry_warning, healthy.

        Integration point: call this at session start and log the result to the
        PDA loop. CI can dispatch a CODEX_MASTER_KEY-rotation alert if
        healthy=False.
        """
        health: dict[str, object] = {
            "source": self._token_source,
            "login": None,
            "scopes": [],
            "has_master_key_scopes": False,
            "expiry_warning": None,
            "healthy": False,
        }
        if not self._token:
            health["expiry_warning"] = "No token configured — loop is broken."
            return health

        try:
            req = urllib.request.Request(
                _validated_github_api_url(f"{_GITHUB_API}/user"),
                headers={
                    "Authorization": "******",
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": _API_VERSION,
                },
            )
            with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated by _validated_github_api_url()
                req, timeout=10
            ) as resp:
                body = json.loads(resp.read().decode())
                raw_scopes = resp.headers.get("x-oauth-scopes", "")
                status = resp.status
        except urllib.error.HTTPError as exc:
            status = exc.code
            body = {}
            raw_scopes = ""
        except (ConnectionError, TimeoutError) as exc:
            health["expiry_warning"] = f"Request failed: {exc}"
            return health

        if status == 401:
            health["expiry_warning"] = (
                f"Token ({self._token_source}) is invalid or expired. "
                "Rotate CODEX_MASTER_KEY immediately to preserve the self-healing loop."
            )
            logger.error(health["expiry_warning"])  # codeql[py/clear-text-logging-sensitive-data]
            return health

        if status != 200:
            health["expiry_warning"] = f"Unexpected /user status {status}"
            return health

        health["login"] = body.get("login")

        # Parse OAuth scopes from response header
        scopes = [s.strip() for s in raw_scopes.split(",") if s.strip()]
        health["scopes"] = scopes

        required = {"repo", "workflow"}
        health["has_master_key_scopes"] = required.issubset(set(scopes))

        if not health["has_master_key_scopes"] and self._token_source in (
            "CODEX_MASTER_KEY",
            "CODEX_BACKUP_KEY",
        ):
            missing = required - set(scopes)
            health["expiry_warning"] = (
                f"Token ({self._token_source}) is missing required scopes: "
                f"{missing}.  Self-healing loop will silently degrade."
            )
            logger.warning(health["expiry_warning"])  # codeql[py/clear-text-logging-sensitive-data]

        health["healthy"] = bool(health["has_master_key_scopes"])
        return health

    def _require_token(self) -> None:
        """Raise RuntimeError if no token is available."""
        if not self._token:
            raise RuntimeError(
                "No GitHub token available. Set CODEX_MASTER_KEY. "
                "See .codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md § 3."
            )

    # ------------------------------------------------------------------
    # REST API methods
    # ------------------------------------------------------------------

    def _get(self, url: str) -> dict[str, Any]:
        """Execute a single GET request to the GitHub REST API (no retry).

        Use _request() with method="GET" when retry-on-rate-limit is
        needed. This lightweight helper is used by Git Data API helpers
        where a single attempt is sufficient.
        """
        url = _validated_github_api_url(url)
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": "******",
                "Accept": _ACCEPT,
                "X-GitHub-Api-Version": _API_VERSION,
            },
        )
        try:
            with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated by _validated_github_api_url()
                req, timeout=30
            ) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            logger.error(
                "GitHub API GET %s → %d (%s)",
                _redact_url_for_log(url),
                exc.code,
                type(exc).__name__,
            )
            raise

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any],
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Execute a GitHub REST API call with exponential back-off retry.

        Retries on HTTP 403 (secondary rate limit) and 429 (primary rate
        limit). Respects the ``Retry-After`` response header when present.
        Non-retryable errors (4xx other than 403/429, 5xx) are raised
        immediately after logging.

        Parameters
        ----------
        method:
            HTTP method string, e.g. "POST" or "PATCH".
        url:
            Fully-qualified HTTPS URL.
        payload:
            Request body as a JSON-serialisable dict.
        max_retries:
            Maximum number of retry attempts after the first failure
            (default 3, giving up to 4 total attempts).
        """
        url = _validated_github_api_url(url)
        data = json.dumps(payload).encode()
        last_exc: urllib.error.HTTPError | None = None
        for attempt in range(max_retries + 1):
            req = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers={
                    "Authorization": "******",
                    "Accept": _ACCEPT,
                    "X-GitHub-Api-Version": _API_VERSION,
                    "Content-Type": "application/json",
                },
            )
            try:
                with urllib.request.urlopen(  # nosec B310  # nosemgrep: semgrep.urllib-urlopen-dynamic -- URL is validated by _validated_github_api_url()
                    req, timeout=30
                ) as resp:
                    body = resp.read()
                    return json.loads(body) if body else {}
            except urllib.error.HTTPError as exc:
                last_exc = exc
                # Only retry on rate-limiting, not on real permission/auth errors.
                # 429 (primary rate limit) — always retryable.
                # 403 (secondary rate limit) — retryable only when GitHub signals
                #   throttling via a Retry-After header or x-ratelimit-remaining=0.
                is_rate_limited = False
                if exc.code == 429:
                    is_rate_limited = True
                elif exc.code == 403:
                    retry_after_hdr = exc.headers.get("Retry-After", "")
                    remaining = exc.headers.get("x-ratelimit-remaining", "")
                    is_rate_limited = bool(retry_after_hdr) or remaining == "0"

                if is_rate_limited and attempt < max_retries:
                    retry_after_hdr = exc.headers.get("Retry-After", "")
                    try:
                        wait = float(retry_after_hdr)
                    except (TypeError, ValueError):
                        wait = (2**attempt) * 1.0  # 1s, 2s, 4s …
                    logger.warning(
                        "GitHub API rate-limited (%d). Retrying in %.0fs (attempt %d/%d)…",
                        exc.code,
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(wait)
                else:
                    logger.error(
                        "GitHub API %s %s → %d (%s)",
                        method,
                        _redact_url_for_log(url),
                        exc.code,
                        type(exc).__name__,
                    )
                    raise
        # Should be unreachable, but satisfy type checker
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("Request failed after all retries but exception was not captured")

    # ------------------------------------------------------------------
    # GraphQL methods
    # ------------------------------------------------------------------

    def _graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        """Execute a simple GraphQL query/mutation."""
        url = f"{_GITHUB_API}/graphql"
        return self._request("POST", url, {"query": query, "variables": variables})

    def _graphql_with_retry(
        self,
        query: str,
        variables: dict[str, Any],
        *,
        max_retries: int = 3,
        operation_name: str = "GraphQL",
    ) -> dict[str, Any]:
        """Execute a GraphQL mutation/query with exponential back-off retry.

        Hardened posting pipeline (Phase 8 P6):
        - Detects GraphQL ``errors`` array in the response body and raises.
        - Recognises ``RATE_LIMITED`` errors from GitHub and waits/retries.
        - Retries on transient network errors (urllib.error.URLError,
          http.client.RemoteDisconnected, TimeoutError).
        - Non-retryable errors (FORBIDDEN, NOT_FOUND, auth failures)
          are raised immediately.
        - Returns result["data"] on success (unwraps the envelope).

        Returns:
            The full parsed JSON response dict (including data key) so
            callers can continue to use the same access pattern.
        """
        _NON_RETRYABLE_TYPES = frozenset({"FORBIDDEN", "NOT_FOUND", "UNPROCESSABLE", "BAD_REQUEST"})
        _RETRYABLE_TYPES = frozenset({"RATE_LIMITED", "SERVICE_UNAVAILABLE", "INTERNAL"})

        last_exc: Exception | None = None
        for attempt in range(max_retries + 1):
            try:
                url = f"{_GITHUB_API}/graphql"
                result = self._request("POST", url, {"query": query, "variables": variables})

                # Check for GraphQL-level errors (HTTP 200 but errors in body)
                gql_errors = result.get("errors")
                if gql_errors:
                    first = gql_errors[0]
                    err_type = first.get("type", "UNKNOWN")
                    err_msg = first.get("message", str(gql_errors))

                    if err_type in _NON_RETRYABLE_TYPES:
                        raise ValueError(f"{operation_name} GraphQL {err_type}: {err_msg}")

                    if err_type in _RETRYABLE_TYPES and attempt < max_retries:
                        wait = 2 ** (attempt + 1)
                        logger.error(
                            f"[mcp_poster] {operation_name} GraphQL {err_type} "
                            f"(attempt {attempt + 1}/{max_retries + 1}) — retry in {wait}s",
                        )
                        time.sleep(wait)
                        continue

                    # Unknown error type or retries exhausted
                    raise RuntimeError(f"{operation_name} GraphQL error ({err_type}): {err_msg}")

                return result

            except (urllib.error.URLError, TimeoutError, ConnectionResetError) as exc:
                last_exc = exc
                if attempt < max_retries:
                    wait = 2 ** (attempt + 1)
                    logger.error(
                        f"[mcp_poster] {operation_name} network error "
                        f"(attempt {attempt + 1}/{max_retries + 1}) — retry in {wait}s: {exc}",
                    )
                    time.sleep(wait)
                else:
                    raise

        # Should never reach here but satisfy type checker
        if last_exc is not None:
            raise last_exc
        raise RuntimeError(f"{operation_name}: max retries ({max_retries}) exceeded")
