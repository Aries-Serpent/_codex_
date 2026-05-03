"""
Log sanitization utilities to prevent log injection attacks.

This module provides functions to sanitize user-controlled input before
including it in log statements, preventing log forging and injection attacks.

Security Rationale:
-------------------
User-controlled data in logs can allow attackers to:
- Inject fake log entries by including newline characters
- Hide malicious activity by injecting ANSI escape codes
- Corrupt log parsers with control characters

Always use sanitize_log_input() for any user-provided data in logs.

Example:
    >>> from src.utils.log_sanitizer import sanitize_log_input
    >>> logger.info(f"User {sanitize_log_input(user_input)} logged in")
"""

import re
from typing import Any


def sanitize_log_input(value: Any, max_length: int = 500) -> str:
    """
    Sanitize user input for safe logging.

    Removes control characters and truncates to prevent log injection attacks.

    Removes:
    - Newline characters (\\n, \\r)
    - Tab characters (\\t)
    - Control characters (0x00-0x1F, 0x7F-0x9F)
    - ANSI escape codes

    Args:
        value: Input value to sanitize (will be converted to string)
        max_length: Maximum length of output string (default: 500)

    Returns:
        Sanitized string safe for logging

    Example:
        >>> sanitize_log_input("user\\nfake_log_entry")
        'userfake_log_entry'
        >>> sanitize_log_input("a" * 600, max_length=100)
        'aaaa...[truncated]'
    """
    if value is None:
        return "None"

    # Convert to string
    str_value = str(value)

    # Remove ANSI escape codes (terminal color codes, etc.) before stripping control chars
    sanitized = re.sub(r"\x1b\[[0-9;]*m", "", str_value)
    sanitized = re.sub(r"\[[0-9;]*m", "", sanitized)

    # Remove control characters (newlines, tabs, etc.)
    # \\x00-\\x1f: C0 control characters
    # \\x7f-\\x9f: DEL and C1 control characters
    sanitized = re.sub(r"[\n\r\t\x00-\x1f\x7f-\x9f]", "", sanitized)

    # Truncate to max length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "...[truncated]"

    return sanitized


def sanitize_dict_for_log(data: dict, max_length: int = 500) -> dict:
    """
    Sanitize all values in a dictionary for logging.

    Recursively sanitizes nested dictionaries.
    Useful for logging request/response bodies or configuration objects
    that may contain user-controlled data.

    Args:
        data: Dictionary to sanitize
        max_length: Maximum length per value

    Returns:
        New dictionary with sanitized values

    Example:
        >>> sanitize_dict_for_log({"user": "test\\ninjection", "id": 123})
        {'user': 'testinjection', 'id': '123'}
    """

    def _sanitize_value(value: Any) -> Any:
        """Recursively sanitize a value."""
        if isinstance(value, dict):
            return {k: _sanitize_value(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return type(value)(_sanitize_value(item) for item in value)
        return sanitize_log_input(value, max_length)

    return _sanitize_value(data)


# Shorthand alias for convenience
safe_log = sanitize_log_input

# Export alias for backward compatibility
sanitize_log = sanitize_log_input

# Ensure it's in __all__ if defined
__all__ = ["safe_log", "sanitize_dict_for_log", "sanitize_log", "sanitize_log_input"]
