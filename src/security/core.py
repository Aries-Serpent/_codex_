"""Core security helpers used across API and data ingestion layers."""

from __future__ import annotations

import asyncio
import functools
import html
import inspect
import logging
import os
import re
import time
from collections import defaultdict, deque
from collections.abc import Callable, Iterable, MutableMapping
from pathlib import Path
from typing import Any, Literal

from ._types import SecurityError, sanitize_text  # noqa: F401 – re-exported for callers

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


def sanitize_for_logging(value: Any, max_length: int = 200) -> str:
    """Sanitize user input for safe logging (prevents log injection).

    Removes newlines, control characters, and truncates to prevent log poisoning.

    Args:
        value: Input value to sanitize
        max_length: Maximum length of output (default: 200)

    Returns:
        Sanitized string safe for logging
    """
    text = _ensure_str(value)
    # Remove newlines and control characters that could be used for log injection
    sanitized = re.sub(r"[\r\n\t\x00-\x1f\x7f]", " ", text)
    # Keep the final string within the requested maximum length.
    if max_length <= 0:
        return ""
    if len(sanitized) > max_length:
        suffix = "...[truncated]"
        keep = max(0, max_length - len(suffix))
        sanitized = sanitized[:keep] + suffix
    return sanitized


def _ensure_str(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if not isinstance(value, str):
        return str(value)
    return value


def sanitize_user_content(value: Any, content_type: Literal["html", "markdown"] = "html") -> str:
    """Sanitize user generated content for safe rendering.

    Security: Uses proper HTML parsing instead of regex to prevent XSS and ReDoS attacks.
    """
    text = _ensure_str(value)

    # Remove dangerous URL protocols (javascript:, data:, vbscript:) before HTML escaping
    # This prevents XSS attacks via URL schemes that bypass HTML entity escaping
    for pattern in XSS_PATTERNS:
        text = pattern.sub("", text)

    if content_type == "html":
        # Use html.escape for HTML content (safe and efficient)
        sanitized = html.escape(text)
    elif content_type == "markdown":
        # For markdown, escape HTML entities (markdown parsers handle the rest)
        # DO NOT use regex for HTML filtering - it's inherently flawed
        sanitized = html.escape(text)
    else:
        sanitized = text

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
        return sanitize_user_content(value, content_type="html")

    if input_type == "path":
        _validate_path_input(value)
        return value

    if input_type == "text":
        if "\0" in value or any(ord(char) < 32 and char not in "\t\n\r" for char in value):
            raise SecurityError("Invalid control characters in text")
        return sanitize_text(value)

    if input_type == "json":
        if _JSON_INJECTION_PATTERN.search(value):
            raise SecurityError("Prototype pollution patterns detected")
        return value

    raise SecurityError(f"Unsupported input_type: {input_type}")


def _validate_path_input(value: str) -> None:
    """Validate filesystem paths for traversal or injection attempts.

    Uses pathlib.Path.resolve() with parent directory containment checks
    to prevent directory traversal attacks (CWE-22).

    Args:
        value: Path string to validate

    Raises:
        SecurityError: If path contains traversal attempts or invalid characters
    """
    # Check for null bytes and control characters
    if any(char in value for char in ["\0", "\n", "\r"]):
        raise SecurityError("Invalid characters in path")

    # Reject absolute paths
    if os.path.isabs(value):
        raise SecurityError(f"Path traversal attempt detected: {value}")

    # Reject home directory expansion attempts
    if value.startswith("~"):
        raise SecurityError(f"Path traversal attempt detected: {value}")

    # Use pathlib.Path.resolve() to resolve symlinks and normalize the path
    # This prevents bypassing security checks via symlink escape attacks
    try:
        current_dir = Path.cwd().resolve()
        input_path = Path(value)

        # Reject paths with ".." components before resolution
        # This catches explicit traversal attempts
        if ".." in input_path.parts:
            raise SecurityError(f"Path traversal attempt detected: {value}")

        # Resolve the path relative to current directory
        resolved_path = (current_dir / input_path).resolve()

        # Verify that the resolved path is within or a child of current directory
        # This prevents symlink escape attacks and ensures containment
        try:
            resolved_path.relative_to(current_dir)
        except ValueError as err:
            raise SecurityError(f"Path '{value}' attempts to escape current directory") from err

    except (RuntimeError, OSError) as err:
        raise SecurityError(f"Invalid path: {value}") from err


def enforce_absolute_path(path: str) -> Path:
    """Validate and enforce absolute path requirements.

    Uses pathlib.Path.resolve() to properly handle symlinks and validate
    path containment (CWE-22 mitigation).

    Args:
        path: Path string to validate

    Returns:
        Validated absolute Path object

    Raises:
        SecurityError: If path contains relative components or traversal
    """
    # Reject relative path traversal patterns
    if ".." in path:
        raise SecurityError(f"Path traversal not allowed: {path}")

    p = Path(path)

    # Reject non-absolute paths
    if not p.is_absolute():
        raise SecurityError(f"Only absolute paths allowed: {path}")

    # Resolve the path to handle symlinks and validate it's still absolute
    # This prevents symlink escape attacks
    try:
        resolved = p.resolve()
        if not resolved.is_absolute():
            raise SecurityError(f"Failed to resolve to absolute path: {path}")
        return resolved
    except (RuntimeError, OSError) as err:
        raise SecurityError(f"Failed to resolve path: {path}") from err


def sanitize_path(path: str | Path, base_dir: str | Path | None = None) -> str:
    """Sanitize and normalize a filesystem path.

    This is intentionally permissive when no base_dir is supplied so callers can
    safely normalize user-controlled strings without crashing. When base_dir is
    provided, the resolved path is constrained to remain beneath that directory.
    """
    if path is None:
        return ""

    raw = str(path)
    if raw == "":
        return ""

    sanitized = raw.replace("\\", "/")
    sanitized = sanitized.replace("//", "/")
    sanitized = sanitized.replace("\x00", "")
    sanitized = "".join(ch for ch in sanitized if ch.isprintable() or ch in {"\n", "\r", "\t"})
    sanitized = re.sub(r"[\r\n\t]", " ", sanitized)

    if base_dir is None:
        return sanitized

    base = Path(base_dir).expanduser().resolve(strict=False)
    candidate = Path(sanitized)
    resolved = (base / candidate) if not candidate.is_absolute() else candidate

    try:
        resolved = resolved.expanduser().resolve(strict=False)
        resolved.relative_to(base)
    except ValueError as err:
        raise ValueError(f"Path {path} is outside base directory {base_dir}") from err
    except (RuntimeError, OSError) as err:
        raise ValueError(f"Failed to resolve path {path} within base directory {base_dir}") from err

    return str(resolved)


def check_permissions(path: Path, mode: str) -> bool:
    """Check if a path has the specified permissions.

    Args:
        path: Path to check
        mode: Permission mode ('read', 'write', 'execute')

    Returns:
        True if path has the specified permission
    """
    if not path.exists():
        return False

    if mode == "read":
        return os.access(path, os.R_OK)
    if mode == "write":
        return os.access(path, os.W_OK)
    if mode == "execute":
        return os.access(path, os.X_OK)

    return False


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

            setattr(async_wrapper, "__signature__", inspect.signature(func))
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

        setattr(wrapper, "__signature__", inspect.signature(func))
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
    log.info("security_event", extra={"event": sanitize_text(event)})


def hmac_compare(expected: str, actual: str) -> bool:
    """Constant-time comparison helper to avoid timing attacks."""

    if len(expected) != len(actual):
        return False
    result = 0
    for x, y in zip(expected.encode("utf-8"), actual.encode("utf-8"), strict=True):
        result |= x ^ y
    return result == 0
