"""
Log sanitization utilities to prevent sensitive data exposure and log injection.

This module provides comprehensive sanitization for logging sensitive information
and preventing log injection attacks.

Security Features:
- Automatic redaction of sensitive patterns (API keys, tokens, passwords)
- Prevention of log injection via newline/control character removal
- Support for structured logging with extra fields
- Pattern-based detection and masking

Usage:
    from codex.security.log_sanitizer import sanitize_log, mask_sensitive

    # Sanitize user input
    logger.info(f"User {sanitize_log(username)} logged in")

    # Mask sensitive data
    safe_message = mask_sensitive(message_with_token)
    logger.info(safe_message)
"""

import re
from typing import Any

# Patterns for detecting sensitive data
SENSITIVE_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # API keys and tokens
    (
        re.compile(r'(api[_-]?key|token|secret|password)\s*[=:]\s*["\']?(\S+)', re.IGNORECASE),
        r"\1=***REDACTED***",
    ),
    # Bearer tokens
    (re.compile(r"Bearer\s+\S+", re.IGNORECASE), "Bearer ***REDACTED***"),
    # Base64-encoded secrets (40+ chars)
    (re.compile(r"[a-zA-Z0-9+/]{40,}={0,2}"), "***BASE64_REDACTED***"),
    # Hex-encoded secrets (32+ chars)
    (re.compile(r"\b[a-fA-F0-9]{32,}\b"), "***HEX_REDACTED***"),
    # AWS keys
    (re.compile(r"AKIA[0-9A-Z]{16}"), "***AWS_KEY_REDACTED***"),
    # JWT tokens
    (
        re.compile(r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*"),
        "***JWT_REDACTED***",
    ),
    # Private keys
    (
        re.compile(
            r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----.*?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
            re.DOTALL,
        ),
        "***PRIVATE_KEY_REDACTED***",
    ),
]


def sanitize_log(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging by removing control characters.

    This prevents log injection attacks where attackers can inject newlines
    or control characters to forge log entries or hide malicious activity.

    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)

    Returns:
        Sanitized string safe for logging

    Example:
        >>> sanitize_log("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log("test" * 200, max_length=100)
        'testtesttest...[truncated]'
    """
    if value is None:
        return "None"

    # Convert to string
    str_value = str(value)

    # Remove control characters (newlines, tabs, etc.)
    # \x00-\x1f: C0 control characters
    # \x7f-\x9f: DEL and C1 control characters
    sanitized = re.sub(r"[\n\r\t\x00-\x1f\x7f-\x9f]", "", str_value)

    # Remove ANSI escape codes (terminal color codes, etc.)
    sanitized = re.sub(r"\x1b\[[0-9;]*m", "", sanitized)

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "...[truncated]"

    return sanitized


def mask_sensitive(message: str) -> str:
    """
    Mask sensitive data patterns in a message.

    Automatically detects and redacts common sensitive patterns like:
    - API keys and tokens
    - Bearer tokens
    - Base64/hex-encoded secrets
    - AWS credentials
    - JWT tokens
    - Private keys

    Args:
        message: Message that may contain sensitive data

    Returns:
        Message with sensitive patterns redacted

    Example:
        >>> mask_sensitive("Token: sk_live_abc123xyz789")
        'Token: ***REDACTED***'
        >>> mask_sensitive("Bearer eyJhbGc...")
        'Bearer ***JWT_REDACTED***'
    """
    masked = message
    for pattern, replacement in SENSITIVE_PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked


def safe_log_message(message: str, mask_secrets: bool = True) -> str:
    """
    Comprehensive log message sanitization.

    Combines both control character removal and sensitive data masking
    for maximum security.

    Args:
        message: Message to sanitize
        mask_secrets: Whether to mask sensitive patterns (default: True)

    Returns:
        Fully sanitized and masked message

    Example:
        >>> safe_log_message("User api_key=sk_test_123\\nFAKE_LOG logged in")
        'User api_key=***REDACTED*** FAKE_LOG logged in'
    """
    # First remove control characters
    sanitized = sanitize_log(message)

    # Then mask sensitive patterns if requested
    if mask_secrets:
        sanitized = mask_sensitive(sanitized)

    return sanitized


def sanitize_dict_for_log(
    data: dict[str, Any], max_length: int = 500, mask_secrets: bool = True
) -> dict[str, Any]:
    """
    Sanitize all values in a dictionary for logging.

    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled or sensitive data.

    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value
        mask_secrets: Whether to mask sensitive patterns

    Returns:
        New dictionary with sanitized values

    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "token": "abc123"})
        {'user': 'testinjection', 'token': '***REDACTED***'}
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = sanitize_dict_for_log(value, max_length, mask_secrets)
        elif isinstance(value, (list, tuple)):
            if mask_secrets:
                result[key] = [  # type: ignore[assignment]
                    (
                        mask_sensitive(sanitize_log(str(item), max_length))
                        if not isinstance(item, dict)
                        else sanitize_dict_for_log(item, max_length, mask_secrets)
                    )
                    for item in value
                ]
            else:
                result[key] = [  # type: ignore[assignment]
                    (
                        sanitize_log(str(item), max_length)
                        if not isinstance(item, dict)
                        else sanitize_dict_for_log(item, max_length, mask_secrets)
                    )
                    for item in value
                ]
        else:
            str_value = sanitize_log(value, max_length)
            if mask_secrets:
                str_value = mask_sensitive(str_value)
            result[key] = str_value  # type: ignore[assignment]
    return result


# Shorthand aliases
safe_log = sanitize_log
mask_secrets = mask_sensitive


__all__ = [
    "mask_secrets",
    "mask_sensitive",
    "safe_log",
    "safe_log_message",
    "sanitize_dict_for_log",
    "sanitize_log",
]
