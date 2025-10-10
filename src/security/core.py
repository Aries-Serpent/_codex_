"""Core security helpers used across API and data ingestion layers."""

from __future__ import annotations

import asyncio
import functools
import html
import logging
import os
import re
import time
from collections import defaultdict, deque
from collections.abc import Callable, Iterable, MutableMapping
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Literal


class SecurityError(ValueError):
    """Raised when security validation fails."""


SQL_INJECTION_PATTERNS = [
    re.compile(r";\s*(DROP|DELETE|UPDATE|INSERT|ALTER)\s+", re.IGNORECASE),
    re.compile(r"'\s*OR\s+'", re.IGNORECASE),
    re.compile(r"--", re.IGNORECASE),
    re.compile(r"/\*.*?\*/", re.IGNORECASE | re.DOTALL),
]

XSS_PATTERNS = [
    re.compile(r"<script[^>]*>", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"on\w+\s*=", re.IGNORECASE),
]

_JSON_INJECTION_PATTERN = re.compile(r"__proto__|constructor|prototype", re.IGNORECASE)


def _ensure_str(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if not isinstance(value, str):
        return str(value)
    return value


def sanitize_user_content(
    value: Any, content_type: Literal["html", "markdown"] = "html"
) -> str:
    """Sanitize user generated content for safe rendering."""

    text = _ensure_str(value)

    if content_type == "html":
        sanitized = html.escape(text)
    elif content_type == "markdown":
        sanitized = re.sub(
            r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL
        )
        sanitized = html.escape(sanitized)
    else:
        sanitized = text

    from .content_filters import sanitize_text  # Local import to avoid cycle

    return sanitize_text(sanitized)


def validate_input(
    value: str,
    *,
    input_type: Literal["sql", "html", "path", "text", "json"] = "text",
    max_length: int = 10_000,
) -> str:
    """Validate user supplied input according to the provided type."""

    if not isinstance(value, str):
        raise SecurityError(f"Expected string, got {type(value)}")

    if len(value) > max_length:
        raise SecurityError(f"Input exceeds max length {max_length}")

    if input_type == "sql":
        for pattern in SQL_INJECTION_PATTERNS:
            if pattern.search(value):
                raise SecurityError("SQL injection pattern detected")
        return value

    if input_type == "html":
        for pattern in XSS_PATTERNS:
            if pattern.search(value):
                raise SecurityError("XSS pattern detected in HTML input")
        return value

    if input_type == "path":
        _validate_path_input(value)
        return value

    if input_type == "text":
        if "\0" in value or any(
            ord(char) < 32 and char not in "\t\n\r" for char in value
        ):
            raise SecurityError("Invalid control characters in text")
        return value

    if input_type == "json":
        if _JSON_INJECTION_PATTERN.search(value):
            raise SecurityError("Prototype pollution patterns detected")
        return value

    raise SecurityError(f"Unsupported input_type: {input_type}")


def _validate_path_input(value: str) -> None:
    """Validate filesystem paths for traversal or injection attempts."""

    if any(char in value for char in ["\0", "\n", "\r"]):
        raise SecurityError("Invalid characters in path")

    normalized = os.path.normpath(value)
    if normalized.startswith("..") or os.path.isabs(normalized):
        raise SecurityError(f"Path traversal attempt detected: {value}")

    if value.startswith("~"):
        raise SecurityError(f"Path traversal attempt detected: {value}")

    posix_path = PurePosixPath(value)
    if any(part == ".." for part in posix_path.parts):
        raise SecurityError(f"Path traversal attempt detected: {value}")

    windows_path = PureWindowsPath(value)
    if windows_path.is_absolute() or windows_path.drive:
        raise SecurityError(f"Path traversal attempt detected: {value}")

    if any(part == ".." for part in windows_path.parts):
        raise SecurityError(f"Path traversal attempt detected: {value}")


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
