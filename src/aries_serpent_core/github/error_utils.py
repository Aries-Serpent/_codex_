"""GitHub API error handling utilities.

This module provides utilities for:
- Handling GitHub API errors (rate limiting, auth, etc.)
- Error message formatting
- Retry logic with exponential backoff
- Rate-limit tracking
"""

from __future__ import annotations

import logging
import time
import urllib.error
from typing import Any

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""

    pass


class RateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(self, message: str, reset_at: int | None = None) -> None:
        """Initialize RateLimitError.

        Parameters
        ----------
        message : str
            Error message
        reset_at : int, optional
            Unix timestamp when the rate limit resets
        """
        super().__init__(message)
        self.reset_at = reset_at

    def wait_until_reset(self) -> None:
        """Sleep until rate limit resets."""
        if self.reset_at:
            wait_seconds = max(0, self.reset_at - int(time.time()))
            if wait_seconds > 0:
                logger.warning(f"Rate limited. Waiting {wait_seconds} seconds...")
                time.sleep(wait_seconds)


class AuthenticationError(GitHubAPIError):
    """Raised when authentication fails."""

    pass


class NotFoundError(GitHubAPIError):
    """Raised when a resource is not found."""

    pass


def handle_http_error(
    exc: urllib.error.HTTPError,
    operation: str = "GitHub API",
    url: str = "",
) -> tuple[int, str]:
    """Extract HTTP status code and error message from HTTPError.

    Parameters
    ----------
    exc : urllib.error.HTTPError
        HTTP error exception
    operation : str, optional
        Operation name for error messages (default: "GitHub API")
    url : str, optional
        URL that caused the error

    Returns
    -------
    tuple[int, str]
        (status_code, error_message)
    """
    status = exc.code
    try:
        body = exc.read().decode("utf-8")
    except Exception:
        body = str(exc.reason)

    message = f"{operation} error ({status}): {body}"
    if url:
        message += f" (URL: {url})"

    return status, message


def is_rate_limited(response_headers: dict[str, str]) -> bool:
    """Check if response indicates rate limiting.

    Parameters
    ----------
    response_headers : dict[str, str]
        HTTP response headers

    Returns
    -------
    bool
        True if rate limited
    """
    remaining = response_headers.get("x-ratelimit-remaining", "1")
    retry_after = response_headers.get("retry-after")

    try:
        return int(remaining) == 0 or bool(retry_after)
    except (ValueError, TypeError):
        return bool(retry_after)


def get_rate_limit_reset_time(response_headers: dict[str, str]) -> int | None:
    """Extract rate limit reset time from response headers.

    Parameters
    ----------
    response_headers : dict[str, str]
        HTTP response headers

    Returns
    -------
    int | None
        Unix timestamp when rate limit resets, or None if not found
    """
    reset_header = response_headers.get("x-ratelimit-reset")
    if reset_header:
        try:
            return int(reset_header)
        except (ValueError, TypeError):
            pass
    return None


def format_error_message(
    error_type: str,
    error_msg: str,
    operation: str = "",
    context: dict[str, Any] | None = None,
) -> str:
    """Format an error message for logging or display.

    Parameters
    ----------
    error_type : str
        Type of error (e.g., "ParseError", "ConnectionError")
    error_msg : str
        Error message text
    operation : str, optional
        Operation being performed
    context : dict, optional
        Additional context information

    Returns
    -------
    str
        Formatted error message
    """
    parts = [f"{error_type}: {error_msg}"]

    if operation:
        parts.insert(0, f"[{operation}]")

    if context:
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        parts.append(f"({context_str})")

    return " ".join(parts)


def should_retry(
    status: int,
    attempt: int,
    max_retries: int = 5,
) -> bool:
    """Determine if an HTTP request should be retried.

    Retryable status codes: 408, 429, 500, 502, 503, 504
    (408 Request Timeout, 429 Too Many Requests, 5xx Server Errors)

    Parameters
    ----------
    status : int
        HTTP status code
    attempt : int
        Current attempt number (0-indexed)
    max_retries : int, optional
        Maximum number of retries (default: 5)

    Returns
    -------
    bool
        True if the request should be retried
    """
    if attempt >= max_retries:
        return False

    retryable_statuses = {408, 429, 500, 502, 503, 504}
    return status in retryable_statuses


def get_backoff_delay(attempt: int, base: float = 1.0, max_delay: float = 60.0) -> float:
    """Calculate exponential backoff delay.

    Uses exponential backoff: delay = base * (2 ^ attempt)
    Capped at max_delay.

    Parameters
    ----------
    attempt : int
        Current attempt number (0-indexed)
    base : float, optional
        Base delay in seconds (default: 1.0)
    max_delay : float, optional
        Maximum delay in seconds (default: 60.0)

    Returns
    -------
    float
        Delay in seconds before retrying
    """
    delay = base * (2**attempt)
    return min(delay, max_delay)
