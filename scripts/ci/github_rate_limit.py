"""Shared GitHub REST transport with credential rotation and quota-aware retry."""

from __future__ import annotations

import hashlib
import json
import os
import random
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

API_BASE = "https://api.github.com"
DEFAULT_TOKEN_SOURCES = (
    "CODEX_MASTER_KEY",
    "CODEX_BACKUP_KEY",
    "CODEX_ADMIN_KEY",
    "AGENT_GITHUB_TOKEN",
    "GH_TOKEN",
    "GITHUB_TOKEN",
)
DEFAULT_ACCEPT = "application/vnd.github+json"
DEFAULT_MAX_RETRIES = 3
DEFAULT_MIN_REMAINING = 20
DEFAULT_MAX_WAIT_SECONDS = 120.0
DEFAULT_CACHE_TTL_SECONDS = 300
DEFAULT_MAX_RESPONSE_BYTES = 1024 * 1024


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        return None


def secure_open(request: urllib.request.Request, timeout: int) -> Any:
    """Open one request with proxies and HTTP redirects disabled."""
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect())
    return opener.open(request, timeout=timeout)


class GitHubInvalidResponseError(RuntimeError):
    """The GitHub response was malformed JSON or exceeded the bounded size."""


@dataclass(frozen=True, slots=True)
class Credential:
    """A non-rendering credential reference for one authenticated request."""

    source: str
    token: str

    def __repr__(self) -> str:
        return f"Credential(source={self.source!r}, token=<redacted>)"


@dataclass(frozen=True, slots=True)
class Quota:
    """Redacted rate-limit evidence for one credential bucket."""

    source: str
    remaining: int | None
    limit: int | None
    reset_epoch: int | None
    resource: str
    deferred_until: float | None = None


@dataclass(frozen=True, slots=True)
class GitHubResponse:
    """One normalized response from the shared GitHub transport."""

    status: int
    payload: Any
    headers: dict[str, str]
    source: str
    attempts: int
    cached: bool = False


class GitHubRateLimitError(RuntimeError):
    """All available credentials are deferred beyond the bounded wait window."""

    def __init__(self, quotas: Iterable[Quota]) -> None:
        self.quotas = tuple(quotas)
        super().__init__("GitHub API rate-limit budget is unavailable")


class _QuotaTracker:
    def __init__(self) -> None:
        self._deferred: dict[str, float] = {}
        self._last: dict[str, Quota] = {}

    @staticmethod
    def fingerprint(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()[:20]

    def observe(self, credential: Credential, headers: Mapping[str, str]) -> Quota:
        remaining = _header_int(headers, "x-ratelimit-remaining")
        limit = _header_int(headers, "x-ratelimit-limit")
        reset_epoch = _header_int(headers, "x-ratelimit-reset")
        resource = _header_value(headers, "x-ratelimit-resource") or "core"
        fingerprint = self.fingerprint(credential.token)
        deferred_until = self._deferred.get(fingerprint)
        quota = Quota(
            source=credential.source,
            remaining=remaining,
            limit=limit,
            reset_epoch=reset_epoch,
            resource=resource,
            deferred_until=deferred_until,
        )
        self._last[fingerprint] = quota
        return quota

    def defer(self, credential: Credential, until: float) -> None:
        self._deferred[self.fingerprint(credential.token)] = max(
            until, self._deferred.get(self.fingerprint(credential.token), 0.0)
        )

    def deferred_until(self, credential: Credential) -> float | None:
        return self._deferred.get(self.fingerprint(credential.token))

    def clear_expired(self, credential: Credential, now: float) -> None:
        fingerprint = self.fingerprint(credential.token)
        until = self._deferred.get(fingerprint)
        if until is not None and until <= now:
            self._deferred.pop(fingerprint, None)

    def release(self, credential: Credential) -> None:
        self._deferred.pop(self.fingerprint(credential.token), None)

    def snapshot(self, credentials: Iterable[Credential]) -> list[Quota]:
        result: list[Quota] = []
        for credential in credentials:
            fingerprint = self.fingerprint(credential.token)
            prior = self._last.get(fingerprint)
            deferred_until = self._deferred.get(fingerprint)
            if prior is not None:
                result.append(
                    Quota(
                        source=prior.source,
                        remaining=prior.remaining,
                        limit=prior.limit,
                        reset_epoch=prior.reset_epoch,
                        resource=prior.resource,
                        deferred_until=deferred_until,
                    )
                )
            else:
                result.append(
                    Quota(
                        source=credential.source,
                        remaining=None,
                        limit=None,
                        reset_epoch=None,
                        resource="unknown",
                        deferred_until=deferred_until,
                    )
                )
        return result


_TRACKER = _QuotaTracker()


def _header_value(headers: Mapping[str, str], name: str) -> str | None:
    lowered = name.lower()
    for key, value in headers.items():
        if key.lower() == lowered:
            return str(value)
    return None


def _header_int(headers: Mapping[str, str], name: str) -> int | None:
    value = _header_value(headers, name)
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def discover_credentials(
    *,
    token: str | None = None,
    source: str = "explicit",
    sources: Iterable[str] = DEFAULT_TOKEN_SOURCES,
) -> list[Credential]:
    """Return distinct, non-rendering credentials in priority order."""
    if token:
        candidates = [(source, token)]
    else:
        candidates = [(name, os.environ.get(name, "").strip()) for name in sources]
    seen: set[str] = set()
    credentials: list[Credential] = []
    for name, value in candidates:
        if not value or value in seen:
            continue
        seen.add(value)
        credentials.append(Credential(name, value))
    return credentials


def source_for_token(token: str, default: str = "explicit") -> str:
    """Return a safe environment source label without exposing the token."""
    for name in DEFAULT_TOKEN_SOURCES:
        if token == os.environ.get(name, "").strip():
            return name
    return default


def credentials_for_token(
    token: str,
    source: str = "explicit",
    *,
    sources: Iterable[str] = DEFAULT_TOKEN_SOURCES,
) -> list[Credential]:
    """Rotate matching environment credentials, but never escape an App token boundary."""
    environment = discover_credentials(sources=sources)
    if any(credential.token == token for credential in environment):
        return environment
    return [Credential(source=source_for_token(token, source), token=token)]


def quota_status(credentials: Iterable[Credential] | None = None) -> dict[str, Any]:
    """Return secret-free process-observed quota and deferral state."""
    selected = list(credentials or discover_credentials())
    now = time.time()
    return {
        "observed_at": int(now),
        "credentials": [
            {
                "source": quota.source,
                "remaining": quota.remaining,
                "limit": quota.limit,
                "reset_epoch": quota.reset_epoch,
                "resource": quota.resource,
                "deferred_seconds": (
                    max(0, int(quota.deferred_until - now))
                    if quota.deferred_until is not None
                    else 0
                ),
            }
            for quota in _TRACKER.snapshot(selected)
        ],
    }


def _is_rate_limited(status: int, payload: Any, headers: Mapping[str, str]) -> bool:
    if status == 429:
        return True
    if status != 403:
        return False
    if _header_int(headers, "x-ratelimit-remaining") == 0:
        return True
    body = json.dumps(payload, sort_keys=True).lower() if payload is not None else ""
    return any(
        phrase in body
        for phrase in (
            "rate limit",
            "secondary rate limit",
            "abuse detection",
            "temporarily blocked",
        )
    )


def _defer_until(
    status: int, payload: Any, headers: Mapping[str, str], now: float, attempt: int
) -> float:
    retry_after = _header_int(headers, "retry-after")
    if retry_after is not None:
        return now + max(1, retry_after) + 1.0
    reset_epoch = _header_int(headers, "x-ratelimit-reset")
    if reset_epoch is not None:
        return max(now, float(reset_epoch)) + 1.0
    reset = payload.get("rate", {}).get("reset") if isinstance(payload, dict) else None
    try:
        if reset is not None:
            return max(now, float(reset)) + 1.0
    except (TypeError, ValueError):
        # Malformed reset metadata is ignored in favor of bounded jitter.
        return now + min(60.0, (2.0**attempt) + random.random())
    return now + min(60.0, (2.0**attempt) + random.random())


def _parse_payload(raw: bytes, accept: str, *, strict_json: bool) -> Any:
    if not raw:
        return {}
    if "diff" in accept or accept.endswith("patch"):
        return raw.decode("utf-8", errors="replace")
    try:
        return json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        if strict_json:
            raise GitHubInvalidResponseError("GitHub API returned invalid JSON") from exc
        return raw.decode("utf-8", errors="replace")


def _cache_path(cache_dir: Path | str, url: str, accept: str, token: str) -> Path:
    key = hashlib.sha256(
        f"{url}\n{accept}\n{_TRACKER.fingerprint(token)}".encode("utf-8")
    ).hexdigest()
    return Path(cache_dir) / f"{key}.json"


def _cache_load(path: Path, ttl_seconds: int, now: float) -> tuple[Any, dict[str, str]] | None:
    if not path.is_file() or now - path.stat().st_mtime >= ttl_seconds:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload["payload"], payload.get("headers", {})
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return None


def _cache_store(path: Path, payload: Any, headers: Mapping[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".tmp-", delete=False
        ) as handle:
            json.dump({"payload": payload, "headers": dict(headers)}, handle)
            temporary = handle.name
        os.replace(temporary, path)
    except OSError:
        if temporary:
            Path(temporary).unlink(missing_ok=True)


def request(
    method: str,
    url: str,
    *,
    token: str | None = None,
    source: str = "explicit",
    credentials: Iterable[Credential] | None = None,
    body: Mapping[str, Any] | None = None,
    accept: str = DEFAULT_ACCEPT,
    user_agent: str = "codex-github-rate-limit/1.0",
    timeout: int = 30,
    max_retries: int = DEFAULT_MAX_RETRIES,
    min_remaining: int = DEFAULT_MIN_REMAINING,
    max_wait_seconds: float = DEFAULT_MAX_WAIT_SECONDS,
    cache_dir: Path | str | None = None,
    cache_ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
    sleep: Callable[[float], None] = time.sleep,
    now: Callable[[], float] = time.time,
    opener: Callable[..., Any] = secure_open,
    max_response_bytes: int = DEFAULT_MAX_RESPONSE_BYTES,
    strict_json: bool = True,
) -> GitHubResponse:
    """Perform a bounded request, rotating credentials before quota exhaustion."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "api.github.com":
        raise ValueError("GitHub requests must target the exact api.github.com HTTPS origin")
    selected = list(credentials or discover_credentials(token=token, source=source))
    if not selected:
        raise RuntimeError("No GitHub credential is available")

    method = method.upper()
    attempts = 0
    last_response: GitHubResponse | None = None
    for attempt in range(max_retries):
        checked_at = now()
        available: list[Credential] = []
        for credential in selected:
            _TRACKER.clear_expired(credential, checked_at)
            until = _TRACKER.deferred_until(credential)
            if until is None or until <= checked_at:
                available.append(credential)
        if not available:
            wait_candidates = [
                value
                for credential in selected
                if (value := _TRACKER.deferred_until(credential)) is not None
            ]
            wait_until = min(wait_candidates) if wait_candidates else checked_at
            wait = max(0.0, wait_until - checked_at)
            if wait > max_wait_seconds:
                raise GitHubRateLimitError(_TRACKER.snapshot(selected))
            sleep(min(max_wait_seconds, max(1.0, wait)))
            available = selected

        credential = available[attempt % len(available)]
        cache = (
            _cache_path(cache_dir, url, accept, credential.token)
            if cache_dir and method == "GET"
            else None
        )
        if cache is not None:
            cached = _cache_load(cache, cache_ttl_seconds, now())
            if cached is not None:
                payload, headers = cached
                return GitHubResponse(200, payload, headers, credential.source, 0, cached=True)
        encoded = json.dumps(dict(body)).encode("utf-8") if body is not None else None
        request_headers = {
            "Authorization": f"Bearer {credential.token}",
            "Accept": accept,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": user_agent,
        }
        if encoded is not None:
            request_headers["Content-Type"] = "application/json"
        outbound = urllib.request.Request(url, data=encoded, headers=request_headers, method=method)
        attempts += 1
        try:
            with opener(outbound, timeout=timeout) as response:
                response_headers = dict(getattr(response, "headers", {}))
                raw = response.read(max_response_bytes + 1)
                if len(raw) > max_response_bytes:
                    raise GitHubInvalidResponseError("GitHub API response exceeds size limit")
                payload = _parse_payload(raw, accept, strict_json=strict_json)
                status = int(response.status)
                _TRACKER.observe(credential, response_headers)
                remaining = _header_int(response_headers, "x-ratelimit-remaining")
                reset_epoch = _header_int(response_headers, "x-ratelimit-reset")
                if remaining is not None and remaining < min_remaining and reset_epoch:
                    _TRACKER.defer(credential, float(reset_epoch) + 1.0)
                normalized = GitHubResponse(
                    status, payload, response_headers, credential.source, attempts
                )
                if status < 400 and cache is not None and method == "GET":
                    _cache_store(cache, payload, response_headers)
                return normalized
        except urllib.error.HTTPError as exc:
            raw = exc.read(max_response_bytes + 1)
            if len(raw) > max_response_bytes:
                raise GitHubInvalidResponseError(
                    "GitHub API error response exceeds size limit"
                ) from exc
            response_headers = dict(exc.headers or {})
            payload = _parse_payload(raw, accept, strict_json=False)
            _TRACKER.observe(credential, response_headers)
            last_response = GitHubResponse(
                exc.code, payload, response_headers, credential.source, attempts
            )
            if not _is_rate_limited(exc.code, payload, response_headers):
                return last_response
            until = _defer_until(exc.code, payload, response_headers, now(), attempt)
            _TRACKER.defer(credential, until)
            if len({item.token for item in available}) > 1:
                continue
            wait = max(0.0, until - now())
            if attempt + 1 >= max_retries or wait > max_wait_seconds:
                raise GitHubRateLimitError(_TRACKER.snapshot(selected)) from exc
            sleep(max(1.0, wait))
            _TRACKER.release(credential)
        except (TimeoutError, OSError):
            if method == "POST" or attempt + 1 >= max_retries:
                raise
            sleep(min(max_wait_seconds, 2.0**attempt + random.random()))

    if last_response is not None:
        return last_response
    raise RuntimeError("GitHub request exhausted without a response")
