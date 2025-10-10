"""Core security helpers used across API and data ingestion layers."""

from __future__ import annotations

import asyncio
import functools
import html
import logging
import re
import time
from collections import defaultdict, deque
from collections.abc import Callable, Iterable, MutableMapping
from typing import Any


class SecurityError(ValueError):
    """Raised when security validation fails."""


_SQLI_PATTERN = re.compile(r"('.*--|;\s*(drop|alter|delete)\b|\b(or|and)\b\s+\d=\d)", re.I)
_XSS_PATTERN = re.compile(r"<\s*(script|iframe|object|embed)[^>]*>", re.I)
_PATH_TRAVERSAL_PATTERN = re.compile(r"(?:\.\./|\.\\|\0)")
_JSON_INJECTION_PATTERN = re.compile(r"__proto__|constructor|prototype", re.I)


def _ensure_str(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if not isinstance(value, str):
        return str(value)
    return value


def sanitize_user_content(value: Any) -> str:
    """Return content safe for rendering by stripping dangerous markup."""

    text = _ensure_str(value)
    # Escape HTML entities then perform lightweight profanity/PII scrubbing.
    escaped = html.escape(text)
    from .content_filters import sanitize_text  # Local import to avoid cycle

    return sanitize_text(escaped)


def validate_input(value: Any, *, input_type: str = "text") -> str:
    """Validate user supplied input according to the provided type."""

    text = _ensure_str(value)
    candidate = text.strip()
    lowered = candidate.lower()

    if input_type == "sql":
        if _SQLI_PATTERN.search(candidate):
            raise SecurityError("SQL injection attempt detected")
        return candidate

    if input_type == "html":
        if _XSS_PATTERN.search(candidate):
            # Rather than rejecting outright, sanitize the content.
            return sanitize_user_content(candidate)
        return sanitize_user_content(candidate)

    if input_type == "path":
        if _PATH_TRAVERSAL_PATTERN.search(candidate):
            raise SecurityError("Path traversal attempt detected")
        if candidate.startswith("/"):
            raise SecurityError("Absolute paths are not permitted")
        return candidate

    if input_type == "json":
        if _JSON_INJECTION_PATTERN.search(lowered):
            raise SecurityError("Prototype pollution patterns detected")
        return candidate

    # Default behaviour: return sanitized text.
    return sanitize_user_content(candidate)


def rate_limiter(
    *,
    calls: int = 60,
    period: float = 60.0,
    key_func: Callable[..., str] | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator implementing a simple token bucket rate limiter."""

    if calls <= 0:
        raise ValueError("calls must be positive")
    if period <= 0:
        raise ValueError("period must be positive")

    windows: dict[str, deque[float]] = defaultdict(deque)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        if asyncio.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                key = key_func(*args, **kwargs) if key_func else "global"
                timestamps = windows[key]
                now = clock()

                while timestamps and now - timestamps[0] > period:
                    timestamps.popleft()

                if len(timestamps) >= calls:
                    raise SecurityError("Rate limit exceeded")

                timestamps.append(now)
                return await func(*args, **kwargs)

            return async_wrapper

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = key_func(*args, **kwargs) if key_func else "global"
            timestamps = windows[key]
            now = clock()

            while timestamps and now - timestamps[0] > period:
                timestamps.popleft()

            if len(timestamps) >= calls:
                raise SecurityError("Rate limit exceeded")

            timestamps.append(now)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def verify_csrf_token(provided_token: str | None, session_token: str | None) -> None:
    """Ensure a CSRF token matches the server-side value."""

    if not provided_token or not session_token:
        raise SecurityError("Missing CSRF token")
    if not hmac_compare(provided_token, session_token):
        raise SecurityError("CSRF token mismatch")


def verify_session_integrity(
    session_id: str,
    metadata: MutableMapping[str, Any],
    active_sessions: Iterable[MutableMapping[str, Any]],
) -> None:
    """Basic checks to mitigate session hijacking attempts."""

    fingerprint = metadata.get("fingerprint")
    ip_address = metadata.get("ip")
    user_agent = metadata.get("user_agent")
    if not all([session_id, fingerprint, ip_address, user_agent]):
        raise SecurityError("Incomplete session metadata")

    for session in active_sessions:
        if session.get("id") == session_id:
            if session.get("fingerprint") != fingerprint:
                raise SecurityError("Session fingerprint mismatch")
            if session.get("ip") != ip_address:
                raise SecurityError("Session IP mismatch")
            if session.get("user_agent") != user_agent:
                raise SecurityError("Session user agent mismatch")
            break


def log_security_event(event: str, *, logger: logging.Logger | None = None) -> None:
    """Emit an audit log entry for a security-relevant event."""

    log = logger or logging.getLogger("codex.security")
    from .content_filters import sanitize_text  # Local import to avoid cycle

    log.info("security_event", extra={"event": sanitize_text(event)})


def hmac_compare(expected: str, actual: str) -> bool:
    """Constant-time comparison helper to avoid timing attacks."""

    if len(expected) != len(actual):
        return False
    result = 0
    for x, y in zip(expected.encode("utf-8"), actual.encode("utf-8"), strict=True):
        result |= x ^ y
    return result == 0
