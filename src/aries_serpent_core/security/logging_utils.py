"""
Security utilities for safe logging and sensitive data redaction.

This module provides utilities to prevent information disclosure vulnerabilities
by automatically redacting sensitive data patterns before logging or displaying them.

Security: Addresses CodeQL py/clear-text-logging-sensitive-data and
py/clear-text-storage-sensitive-data findings.

Usage:
    from codex.security.logging_utils import redact_sensitive_data, safe_log

    # Redact a message
    safe_msg = redact_sensitive_data("Authorization: ******")
    logger.info(safe_msg)

    # Use safe_log wrapper
    safe_log(logger, "info", f"Token: {token}")
"""

import logging
import re
from typing import Any, Optional

# Patterns for common sensitive data types
SENSITIVE_PATTERNS = [
    # GitHub tokens
    (r"ghp_[A-Za-z0-9]{36,}", "[REDACTED_GITHUB_TOKEN]"),
    (r"github_pat_[A-Za-z0-9_]{82}", "[REDACTED_GITHUB_PAT]"),
    (r"ghu_[A-Za-z0-9]{76}", "[REDACTED_GITHUB_USER_TOKEN]"),
    (r"ghs_[A-Za-z0-9]{68}", "[REDACTED_GITHUB_OAUTH]"),
    # Generic secrets and credentials
    (r'(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', r"\1: [REDACTED_API_KEY]"),
    (r'(?:token|bearer)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)', r"\1: [REDACTED_TOKEN]"),
    (
        r'(?:secret|password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
        r"\1: [REDACTED_SECRET]",
    ),
    (
        r'(?:private[_-]?key|privatekey)["\']?\s*[:=]\s*["\']?([^"\'\s,}]+)',
        r"\1: [REDACTED_PRIVATE_KEY]",
    ),
    # OAuth and authentication
    (r"authorization:\s*bearer\s+[^\s]+", "authorization: bearer [REDACTED]"),
    (r"x-api-key:\s*[^\s]+", "x-api-key: [REDACTED]"),
    # AWS credentials
    (r"(?:AKIA|ASIA)[0-9A-Z]{16}", "[REDACTED_AWS_ACCESS_KEY]"),
    (r'aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*[^\s,}]+', "[REDACTED_AWS_SECRET]"),
    # Generic database URIs with credentials
    (
        r"(?:mysql|postgres|mongodb|redis)[+\w]*://[^@]+@[^\s,}]+",
        "database://[REDACTED_CREDENTIALS]@[REDACTED_HOST]",
    ),
]


def redact_sensitive_data(text: Any, max_preview: int = 8) -> str:
    """
    Redact common secret patterns before logging.

    Args:
        text: The text to redact (will be converted to string if not already)
        max_preview: Maximum characters to show for partial redaction

    Returns:
        String with sensitive patterns replaced with redaction markers

    Example:
        >>> redact_sensitive_data("token: ghp_abc123...")
        'token: [REDACTED_GITHUB_TOKEN]'
    """
    if not isinstance(text, str):
        text = str(text)

    if not text:
        return text

    result = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def safe_log(logger: logging.Logger, level: str, message: str, *args, **kwargs) -> None:
    """
    Log a message with automatic secret redaction.

    Args:
        logger: The logger instance
        level: Log level ('debug', 'info', 'warning', 'error', 'critical')
        message: The message to log
        *args: Positional arguments for message formatting
        **kwargs: Keyword arguments (redacted before logging)

    Example:
        >>> safe_log(logger, 'info', f'Token: {secret_token}')
    """
    # Redact the message
    safe_message = redact_sensitive_data(message)

    # Redact any keyword arguments
    safe_kwargs = {k: redact_sensitive_data(str(v)) for k, v in kwargs.items()}

    # Redact positional arguments
    safe_args = tuple(redact_sensitive_data(str(arg)) for arg in args)

    # Call the logger with the appropriate level
    log_func = getattr(logger, level, logger.info)
    log_func(safe_message, *safe_args, **safe_kwargs)  # type: ignore[arg-type]


def redact_dict(data: dict[str, Any], exclude_keys: Optional[list[Any]] = None) -> dict[str, Any]:
    """
    Redact all values in a dictionary that might be sensitive.

    Args:
        data: The dictionary to redact
        exclude_keys: List of keys whose values should NOT be redacted

    Returns:
        Dictionary with sensitive values redacted
    """
    if not isinstance(data, dict):
        return data

    exclude_keys = exclude_keys or []
    result = {}

    for key, value in data.items():
        if key in exclude_keys:
            result[key] = value
        elif isinstance(value, str):
            result[key] = redact_sensitive_data(value)
        elif isinstance(value, dict):
            result[key] = redact_dict(value, exclude_keys)
        elif isinstance(value, list):
            result[key] = [redact_sensitive_data(v) if isinstance(v, str) else v for v in value]
        else:
            result[key] = value

    return result


def mask_secret(secret: str, visible_chars: int = 4) -> str:
    """
    Mask a secret by showing only the last N characters.

    Args:
        secret: The secret to mask
        visible_chars: Number of characters to show at the end

    Returns:
        Masked string in format: ***REDACTED***[last_N_chars]

    Example:
        >>> mask_secret("my_super_secret_key", 4)
        '***REDACTED***_key'
    """
    if not secret or len(secret) <= visible_chars:
        return "***REDACTED***"

    return f"***REDACTED***{secret[-visible_chars:]}"


__all__ = [
    "redact_sensitive_data",
    "safe_log",
    "redact_dict",
    "mask_secret",
    "SENSITIVE_PATTERNS",
]
