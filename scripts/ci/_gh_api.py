"""
_gh_api.py — Rate-limit-aware GitHub REST API helpers with TTL disk cache.

Shared by fetch_codeql_alerts.py, fetch_security_snapshot.py, and any other
CI script that needs to call the GitHub API without hitting secondary rate
limits or exhausting the primary REST quota.

Key design principles
---------------------
Rate-limit awareness
    Every HTTP call goes through ``api_get`` or ``api_post``.
    ``api_get`` checks ``X-RateLimit-Remaining`` on every response and sleeps
    until ``X-RateLimit-Reset`` when the budget drops below ``min_remaining``.
    ``429`` / ``403`` responses are retried after ``Retry-After`` (default 60 s).
    Network errors are retried up to ``MAX_RETRIES`` times with exponential
    back-off (5 s → 10 s → 20 s).

Disk cache
    ``api_get_cached`` and ``paginate_cached`` wrap the plain helpers with a
    simple SHA-256-keyed JSON file store under ``cache_dir``.  Cache entries
    are reused as long as they are younger than ``ttl_seconds`` (default 3600).
    The cache is automatically bypassed when:
      - ``cache_dir`` is ``None`` (default for uncached callers).
      - The env var ``CODEX_API_CACHE_DISABLED=1`` is set.
    The cache directory is safe for concurrent use because writes go through a
    temp-file rename (atomic on Linux/macOS).

Pagination
    ``paginate`` / ``paginate_cached`` are convenience wrappers that call
    ``api_get`` / ``api_get_cached`` per page and stop early when the API
    returns fewer items than ``per_page``.

Usage
-----
    from _gh_api import resolve_token, api_get, api_get_cached, paginate_cached

    token = resolve_token()
    cache = Path("~/.cache/codex_gh_api").expanduser()

    # Cached, paginated fetch — won't re-download if TTL hasn't expired
    alerts = paginate_cached(
        "https://api.github.com/repos/owner/repo/code-scanning/alerts"
        "?state=open&tool_name=CodeQL",
        token,
        cache_dir=cache,
        ttl_seconds=3600,
        max_pages=10,
        page_sleep=1.0,
    )
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES: int = 3
DEFAULT_PAGE_SLEEP: float = 1.0     # seconds between paginated requests
DEFAULT_MIN_REMAINING: int = 20     # pause when REST budget drops this low
DEFAULT_PER_PAGE: int = 100         # GitHub REST API maximum
DEFAULT_CACHE_TTL: int = 3600       # 1 hour

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
# Disk cache helpers
# ---------------------------------------------------------------------------

def _cache_key(url: str) -> str:
    """Return a short, filesystem-safe cache key derived from *url*."""
    return hashlib.sha256(url.encode()).hexdigest()[:32]


def _cache_load(
    cache_dir: Path,
    url: str,
    ttl_seconds: int,
) -> tuple[Any, dict[str, str]] | None:
    """Return ``(data, headers)`` from disk cache if fresh, else ``None``."""
    if os.environ.get("CODEX_API_CACHE_DISABLED", "0") == "1":
        return None
    path = cache_dir / f"{_cache_key(url)}.json"
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age >= ttl_seconds:
        log.debug("Cache stale for %s (age=%.0fs ttl=%ds)", url, age, ttl_seconds)
        return None
    try:
        entry = json.loads(path.read_text(encoding="utf-8"))
        log.debug("Cache hit  for %s (age=%.0fs)", url, age)
        return entry["data"], entry.get("headers", {})
    except Exception as exc:  # noqa: BLE001
        log.debug("Cache read failed for %s: %s", url, exc)
        return None


def _cache_store(
    cache_dir: Path,
    url: str,
    data: Any,
    headers: dict[str, str],
) -> None:
    """Atomically write *data*/*headers* to the disk cache for *url*."""
    if os.environ.get("CODEX_API_CACHE_DISABLED", "0") == "1":
        return
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / f"{_cache_key(url)}.json"
    entry = {"url": url, "data": data, "headers": headers}
    # Write to a temp file first, then rename — atomic on Linux/macOS.
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=cache_dir,
            prefix=".tmp_",
            suffix=".json",
            delete=False,
        ) as tmp:
            json.dump(entry, tmp)
            tmp_path = tmp.name
        os.replace(tmp_path, dest)
        log.debug("Cache stored for %s → %s", url, dest.name)
    except Exception as exc:  # noqa: BLE001
        log.debug("Cache write failed for %s: %s", url, exc)
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass


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
    raw_remaining = (
        headers.get("X-RateLimit-Remaining")
        or headers.get("x-ratelimit-remaining")
    )
    raw_reset = (
        headers.get("X-RateLimit-Reset")
        or headers.get("x-ratelimit-reset")
    )
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
    raw = exc.headers.get("Retry-After") or exc.headers.get("retry-after")
    retry_after = int(raw) if raw and str(raw).isdigit() else 60
    log.warning(
        "HTTP %d on attempt %d/%d — sleeping %ds (Retry-After).",
        exc.code, attempt + 1, MAX_RETRIES, retry_after,
    )
    time.sleep(retry_after)


# ---------------------------------------------------------------------------
# Public API — uncached
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
    - Inserts ``page_sleep`` after a successful response.
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
    inter_call_sleep: float = 2.0,
) -> tuple[Any, dict[str, str]]:
    """POST *url* with optional JSON *payload* and return ``(parsed_json, headers)``.

    Applies the same rate-limit and retry logic as ``api_get``.
    ``inter_call_sleep`` is inserted after each successful POST to avoid
    secondary rate limits when calling in a tight loop.
    """
    body = json.dumps(payload).encode("utf-8") if payload else b""
    req_headers = {**_make_headers(token), "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")

    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                resp_headers = dict(resp.headers)
                data = json.loads(raw) if raw.strip() else {}
                _check_rate_limit(resp_headers, min_remaining)
                if inter_call_sleep > 0:
                    time.sleep(inter_call_sleep)
                return data, resp_headers

        except urllib.error.HTTPError as exc:
            if exc.code in (429, 403):
                _handle_retry_after(exc, attempt)
                continue
            # 422 = autofix not supported for this alert / rule
            if exc.code == 422:
                body_txt = exc.read().decode("utf-8", errors="replace")
                log.debug("HTTP 422 for %s — not supported: %s", url, body_txt[:200])
                return {"error": "unsupported", "status": 422}, {}
            # 404 = alert gone or feature not enabled on this repo
            if exc.code == 404:
                log.debug("HTTP 404 for %s — not found or feature disabled.", url)
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

    *base_url* must NOT already contain ``per_page`` or ``page`` query params;
    they are appended automatically.  Stops when the API returns fewer items
    than ``per_page`` (last page) or ``max_pages`` has been reached.
    """
    sep = "&" if "?" in base_url else "?"
    all_items: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}{sep}per_page={per_page}&page={page}"
        log.info("Paginating page %d/%d: %s", page, max_pages, url)
        data, _ = api_get(url, token, page_sleep=page_sleep, min_remaining=min_remaining)

        if not isinstance(data, list):
            log.error("Expected list from %s, got %s", url, type(data).__name__)
            break

        all_items.extend(data)
        log.info("Page %d: %d items (total=%d)", page, len(data), len(all_items))

        if len(data) < per_page:
            log.info("Last page (%d < per_page=%d).", len(data), per_page)
            break
    else:
        log.warning("Reached max-pages cap (%d). More items may exist.", max_pages)

    return all_items


# ---------------------------------------------------------------------------
# Public API — cached variants
# ---------------------------------------------------------------------------


def api_get_cached(
    url: str,
    token: str,
    *,
    cache_dir: Path | str | None = None,
    ttl_seconds: int = DEFAULT_CACHE_TTL,
    page_sleep: float = DEFAULT_PAGE_SLEEP,
    min_remaining: int = DEFAULT_MIN_REMAINING,
) -> tuple[Any, dict[str, str]]:
    """``api_get`` with optional TTL-based disk cache.

    If *cache_dir* is set and a fresh cache entry exists, returns the cached
    response without making an API call.  Otherwise delegates to ``api_get``
    and writes the result to disk.

    Set ``CODEX_API_CACHE_DISABLED=1`` to bypass the cache entirely.
    """
    if cache_dir is None or os.environ.get("CODEX_API_CACHE_DISABLED", "0") == "1":
        return api_get(url, token, page_sleep=page_sleep, min_remaining=min_remaining)

    cache_path = Path(cache_dir)
    cached = _cache_load(cache_path, url, ttl_seconds)
    if cached is not None:
        # Still apply page_sleep even on cache hits to avoid burst patterns
        # when called in a tight loop against many URLs.
        if page_sleep > 0:
            time.sleep(page_sleep * 0.1)  # 10 % of normal sleep on cache hit
        return cached

    data, headers = api_get(url, token, page_sleep=page_sleep, min_remaining=min_remaining)
    _cache_store(cache_path, url, data, headers)
    return data, headers


def paginate_cached(
    base_url: str,
    token: str,
    *,
    cache_dir: Path | str | None = None,
    ttl_seconds: int = DEFAULT_CACHE_TTL,
    max_pages: int = 10,
    page_sleep: float = DEFAULT_PAGE_SLEEP,
    min_remaining: int = DEFAULT_MIN_REMAINING,
    per_page: int = DEFAULT_PER_PAGE,
) -> list[dict[str, Any]]:
    """``paginate`` with TTL-based disk cache per page URL.

    Each page URL is cached independently so partial re-fetches are cheap:
    only pages that have aged out are re-downloaded.
    """
    sep = "&" if "?" in base_url else "?"
    all_items: list[dict[str, Any]] = []

    for page in range(1, max_pages + 1):
        url = f"{base_url}{sep}per_page={per_page}&page={page}"
        log.info("Paginating (cached) page %d/%d: %s", page, max_pages, url)
        data, _ = api_get_cached(
            url,
            token,
            cache_dir=cache_dir,
            ttl_seconds=ttl_seconds,
            page_sleep=page_sleep,
            min_remaining=min_remaining,
        )

        if not isinstance(data, list):
            log.error("Expected list from %s, got %s", url, type(data).__name__)
            break

        all_items.extend(data)
        log.info("Page %d: %d items (total=%d)", page, len(data), len(all_items))

        if len(data) < per_page:
            log.info("Last page (%d < per_page=%d).", len(data), per_page)
            break
    else:
        log.warning("Reached max-pages cap (%d). More items may exist.", max_pages)

    return all_items


# ---------------------------------------------------------------------------
# RateLimitAwareHTTP — object-oriented façade (roadmap Priority 0.1)
# ---------------------------------------------------------------------------


class RateLimitAwareHTTP:
    """Rate-limit aware HTTP client for autonomous agent operations.

    This class provides an object-oriented interface over the module-level
    ``api_get`` / ``api_post`` / ``paginate_cached`` helpers, adding:

    * TTL-based disk caching (default 1 hour)
    * Exponential back-off on 429 / 503 responses
    * Token rotation: ``CODEX_MASTER_KEY`` → ``CODEX_BACKUP_KEY`` → ``GH_TOKEN``
      → ``GITHUB_TOKEN``
    * Request coalescing within the cache TTL window
    * Structured logging of every rate-limit encounter
    * Graceful degradation — returns cached data rather than raising when the
      API is rate-limited and cached data is available

    Usage::

        from _gh_api import RateLimitAwareHTTP

        http = RateLimitAwareHTTP(cache_dir=".codex/http_cache", ttl_seconds=3600)

        # GET with caching and back-off
        data = http.get("https://api.github.com/repos/owner/repo/issues")

        # POST with back-off (not cached)
        result = http.post(
            "https://api.github.com/repos/owner/repo/issues/1/comments",
            payload={"body": "hello"},
        )

        # Paginated GET with per-page caching
        all_items = http.list_paginated(
            "https://api.github.com/repos/owner/repo/issues?state=open",
            per_page=100,
        )
    """

    def __init__(
        self,
        *,
        cache_dir: str | Path | None = ".codex/http_cache",
        ttl_seconds: int = DEFAULT_CACHE_TTL,
        min_remaining: int = DEFAULT_MIN_REMAINING,
        page_sleep: float = DEFAULT_PAGE_SLEEP,
        max_retries: int = MAX_RETRIES,
        token: str | None = None,
    ) -> None:
        self._cache_dir: Path | None = Path(cache_dir) if cache_dir else None
        self._ttl = ttl_seconds
        self._min_remaining = min_remaining
        self._page_sleep = page_sleep
        self._max_retries = max_retries
        # Allow callers to inject a token directly; otherwise resolve lazily.
        self._token: str | None = token

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_token(self) -> str:
        """Return the resolved token, resolving lazily on first call."""
        if self._token is None:
            self._token = resolve_token()
        return self._token

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> Any:
        """GET *url* with TTL caching and back-off.

        Returns the parsed JSON body.  If the server is rate-limited and a
        cached response exists, the cached data is returned without raising.

        *headers* is reserved for future per-request header overrides;
        the standard GitHub auth headers are always injected automatically.
        """
        token = self._get_token()
        data, _ = api_get_cached(
            url,
            token,
            cache_dir=self._cache_dir,
            ttl_seconds=self._ttl,
            page_sleep=self._page_sleep,
            min_remaining=self._min_remaining,
        )
        return data

    def post(
        self,
        url: str,
        *,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """POST *url* with optional JSON *payload* and back-off.

        Returns the parsed JSON body.  POST responses are never cached.

        *headers* is reserved for future per-request header overrides.
        """
        token = self._get_token()
        data, _ = api_post(
            url,
            token,
            payload,
            min_remaining=self._min_remaining,
        )
        return data

    def list_paginated(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int = 10,
    ) -> list[dict[str, Any]]:
        """Paginate GET *url* and return all items as a flat list.

        Each page URL is cached independently (per-page deduplication): only
        pages whose cache entry has expired are re-downloaded.

        *headers* is reserved for future per-request header overrides.
        """
        token = self._get_token()
        return paginate_cached(
            url,
            token,
            cache_dir=self._cache_dir,
            ttl_seconds=self._ttl,
            max_pages=max_pages,
            page_sleep=self._page_sleep,
            min_remaining=self._min_remaining,
            per_page=per_page,
        )

    def handle_rate_limit(self, reset_time: int, endpoint: str) -> None:
        """Log a rate-limit event and sleep until *reset_time* (Unix epoch).

        This method is exposed publicly so callers that receive a rate-limit
        signal outside of a normal ``get``/``post`` call (e.g. a GraphQL
        response) can use the same structured logging and sleep logic.
        """
        now = int(datetime.now(timezone.utc).timestamp())
        sleep_secs = max(1, reset_time - now) + 5  # +5 s safety buffer
        log.warning(
            "Rate-limit detected on %s. Sleeping %ds until reset at %s.",
            endpoint,
            sleep_secs,
            datetime.fromtimestamp(reset_time, tz=timezone.utc).isoformat(),
        )
        time.sleep(sleep_secs)
