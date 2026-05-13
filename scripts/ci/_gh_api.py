"""
_gh_api.py — Rate-limit-aware GitHub REST API helpers.

Shared by fetch_codeql_alerts.py, fetch_security_snapshot.py, and any other
CI script that needs to call the GitHub API without hitting secondary rate
limits or exhausting the primary REST quota.

Key design principles
---------------------
- Every HTTP call goes through ``api_get`` or ``api_post``.
- ``api_get`` checks ``X-RateLimit-Remaining`` on every response and sleeps
  until ``X-RateLimit-Reset`` when the budget drops below ``min_remaining``.
- ``429`` / ``403`` responses are retried after ``Retry-After`` (default 60 s).
- Network errors are retried up to ``MAX_RETRIES`` times with exponential back-off.
- ``paginate`` is a convenience wrapper that calls ``api_get`` per page and
  stops early when the API returns fewer items than ``per_page``.
- ``api_post`` applies the same rate-limit guard before each attempt.

Usage
-----
    from _gh_api import resolve_token, api_get, api_post, paginate

    token = resolve_token()
    alerts = paginate(
        "https://api.github.com/repos/owner/repo/code-scanning/alerts"
        "?state=open&tool_name=CodeQL",
        token,
        max_pages=10,
        page_sleep=1.0,
    )
"""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES: int = 3
DEFAULT_PAGE_SLEEP: float = 1.0     # seconds between paginated requests
DEFAULT_MIN_REMAINING: int = 20     # pause when REST budget drops this low
DEFAULT_PER_PAGE: int = 100         # GitHub REST API maximum

API_VERSION = "2022-11-28"
ACCEPT = "application/vnd.github+json"
UA = "codex-gh-api-helper/1.0"

# ---------------------------------------------------------------------------
# Token resolution
# ---------------------------------------------------------------------------


def resolve_token() -> str:
    """Return the first non-empty token from the standard chain.

    Chain (highest to lowest privilege):
        CODEX_MASTER_KEY  — repo + workflow + security_events write
        CODEX_BACKUP_KEY  — same scopes, secondary secret
        GH_TOKEN          — set by ``gh`` CLI or workflow env
        GITHUB_TOKEN      — sandbox installation token (no security_events)
    """
    for envvar in ("CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "GH_TOKEN", "GITHUB_TOKEN"):
        tok = os.environ.get(envvar, "").strip()
        if tok:
            log.debug("Using token from %s", envvar)
            return tok
    log.error(
        "No GitHub token found. Set CODEX_MASTER_KEY (needs security_events scope)."
    )
    raise SystemExit(1)


# ---------------------------------------------------------------------------
# Core HTTP helpers
# ---------------------------------------------------------------------------


def _make_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": ACCEPT,
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": UA,
    }


def _check_rate_limit(headers: dict[str, str], min_remaining: int) -> None:
    """Sleep until the rate-limit window resets if budget is low."""
    raw_remaining = headers.get("X-RateLimit-Remaining") or headers.get(
        "x-ratelimit-remaining"
    )
    raw_reset = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    if raw_remaining is None:
        return
    remaining = int(raw_remaining)
    reset_at = int(raw_reset or "0")
    if remaining < min_remaining and reset_at > 0:
        now = int(datetime.now(timezone.utc).timestamp())
        sleep_secs = max(1, reset_at - now) + 5  # +5 s buffer
        log.warning(
            "Rate-limit low (%d remaining). Sleeping %ds until reset at %s.",
            remaining,
            sleep_secs,
            datetime.fromtimestamp(reset_at, tz=timezone.utc).isoformat(),
        )
        time.sleep(sleep_secs)


def _handle_retry_after(exc: urllib.error.HTTPError, attempt: int) -> None:
    """Read Retry-After from a 429/403 response and sleep accordingly."""
    retry_after_raw = exc.headers.get("Retry-After") or exc.headers.get("retry-after")
    retry_after = int(retry_after_raw) if retry_after_raw and retry_after_raw.isdigit() else 60
    log.warning(
        "HTTP %d on attempt %d/%d — sleeping %ds (Retry-After).",
        exc.code, attempt + 1, MAX_RETRIES, retry_after,
    )
    time.sleep(retry_after)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def api_get(
    url: str,
    token: str,
    *,
    page_sleep: float = DEFAULT_PAGE_SLEEP,
    min_remaining: int = DEFAULT_MIN_REMAINING,
) -> tuple[Any, dict[str, str]]:
    """GET *url* and return ``(parsed_json, response_headers)``.

    Automatically:
    - Sleeps when ``X-RateLimit-Remaining < min_remaining``.
    - Retries up to ``MAX_RETRIES`` times on 429/403 (Retry-After) and
      transient network errors (5-s exponential back-off).
    - Inserts ``page_sleep`` between calls when used in a loop.
    """
    req = urllib.request.Request(url, headers=_make_headers(token))

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                headers = dict(resp.headers)
                data = json.loads(raw)
                _check_rate_limit(headers, min_remaining)
                if page_sleep > 0:
                    time.sleep(page_sleep)
                return data, headers

        except urllib.error.HTTPError as exc:
            if exc.code in (429, 403):
                _handle_retry_after(exc, attempt)
                continue
            body = exc.read().decode("utf-8", errors="replace")
            log.error("HTTP %d fetching %s: %s", exc.code, url, body[:400])
            raise SystemExit(1)

        except OSError as exc:
            wait = 5 * (2 ** attempt)
            log.warning(
                "Network error on attempt %d/%d: %s — retrying in %ds.",
                attempt + 1, MAX_RETRIES, exc, wait,
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait)
                continue
            raise SystemExit(1)

    log.error("Exhausted %d retries for %s", MAX_RETRIES, url)
    raise SystemExit(1)


def api_post(
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
    *,
    min_remaining: int = DEFAULT_MIN_REMAINING,
) -> tuple[Any, dict[str, str]]:
    """POST *url* with optional JSON *payload* and return ``(parsed_json, headers)``.

    Applies the same rate-limit and retry logic as ``api_get``.
    """
    body = json.dumps(payload).encode("utf-8") if payload else b""
    headers = {**_make_headers(token), "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                resp_headers = dict(resp.headers)
                data = json.loads(raw) if raw.strip() else {}
                _check_rate_limit(resp_headers, min_remaining)
                return data, resp_headers

        except urllib.error.HTTPError as exc:
            if exc.code in (429, 403):
                _handle_retry_after(exc, attempt)
                continue
            # 422 = Unprocessable Entity (autofix not available for this alert)
            if exc.code == 422:
                body_txt = exc.read().decode("utf-8", errors="replace")
                log.debug("HTTP 422 for %s — autofix not available: %s", url, body_txt[:200])
                return {"error": "autofix_unavailable", "status": 422}, {}
            # 404 = alert doesn't exist or endpoint not enabled
            if exc.code == 404:
                log.debug("HTTP 404 for %s — endpoint not found or feature not enabled.", url)
                return {"error": "not_found", "status": 404}, {}
            body_txt = exc.read().decode("utf-8", errors="replace")
            log.error("HTTP %d POSTing %s: %s", exc.code, url, body_txt[:400])
            raise SystemExit(1)

        except OSError as exc:
            wait = 5 * (2 ** attempt)
            log.warning(
                "Network error on attempt %d/%d: %s — retrying in %ds.",
                attempt + 1, MAX_RETRIES, exc, wait,
            )
            if attempt < MAX_RETRIES - 1:
                time.sleep(wait)
                continue
            raise SystemExit(1)

    log.error("Exhausted %d retries for %s", MAX_RETRIES, url)
    raise SystemExit(1)


def paginate(
    base_url: str,
    token: str,
    *,
    max_pages: int = 10,
    page_sleep: float = DEFAULT_PAGE_SLEEP,
    min_remaining: int = DEFAULT_MIN_REMAINING,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[dict[str, Any]]:
    """Paginate GET *base_url* and return a flat list of all items.

    *base_url* must NOT already include ``per_page`` or ``page`` parameters;
    they are appended automatically.  Stops when:
    - The API returns fewer than ``per_page`` items (last page), or
    - ``max_pages`` pages have been fetched (hard cap).

    Emits a warning if the cap is hit (may be more items not fetched).
    """
    sep = "&" if "?" in base_url else "?"
    all_items: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}{sep}per_page={per_page}&page={page}"
        log.info("Paginating page %d: %s", page, url)
        data, _ = api_get(url, token, page_sleep=page_sleep, min_remaining=min_remaining)

        if not isinstance(data, list):
            log.error("Expected list from %s, got %s", url, type(data).__name__)
            break

        all_items.extend(data)
        log.info("Page %d: %d items (total so far: %d)", page, len(data), len(all_items))

        if len(data) < per_page:
            log.info("Last page reached (got %d < per_page=%d).", len(data), per_page)
            break
    else:
        log.warning(
            "Reached max-pages cap (%d). There may be more items not fetched.", max_pages
        )

    return all_items
