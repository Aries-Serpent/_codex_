"""GitHub URL utilities for validation and safe logging.

This module provides utilities for:
- Redacting sensitive information from URLs for safe logging
- Validating GitHub API URLs
- Formatting URLs for display
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def redact_url_for_log(url: str) -> str:
    """Return URL without credentials, query, or fragment for safe logging.

    Strips usernames, passwords, query parameters, and fragments from URLs
    while preserving the scheme, host, port, and path for safe logging output.

    Parameters
    ----------
    url : str
        URL to redact

    Returns
    -------
    str
        Redacted URL safe for logging
    """
    parts = urlsplit(url)
    host = parts.hostname or ""
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    netloc = f"{host}:{parts.port}" if parts.port else host
    return urlunsplit((parts.scheme, netloc, parts.path, "", ""))


def validate_github_api_url(url: str) -> str:
    """Validate that a URL is safe for GitHub API communication.

    Ensures the URL:
    - Uses HTTPS (no HTTP)
    - Targets api.github.com (no other hosts)
    - Contains no embedded credentials

    Parameters
    ----------
    url : str
        URL to validate

    Returns
    -------
    str
        The validated URL if all checks pass

    Raises
    ------
    ValueError
        If the URL doesn't meet any validation requirement
    """
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname != "api.github.com":
        raise ValueError(f"GitHub API URL must target https://api.github.com: {url!r}")
    if parts.username or parts.password:
        raise ValueError("GitHub API URL must not contain embedded credentials")
    return url


def get_url_for_display(url: str, max_length: int = 100) -> str:
    """Format a URL for display/logging with optional truncation.

    Redacts sensitive information and optionally truncates if too long.

    Parameters
    ----------
    url : str
        URL to format
    max_length : int, optional
        Maximum length for the display string (default: 100)

    Returns
    -------
    str
        Formatted URL safe for display
    """
    redacted = redact_url_for_log(url)
    if len(redacted) > max_length:
        return redacted[: max_length - 3] + "..."
    return redacted
