"""
P015: Validation Guards Utilities

Consolidates 1,307 occurrences of input validation guard patterns.

Example:
    # Instead of: if not value: raise ValueError(...)
    require_not_empty(value, "username")

    # Instead of: if value is None: return
    require_truthy(value, "config")
"""

from typing import Any, Optional

__all__ = [
    "require_not_empty",
    "require_truthy",
    "require_in",
    "GuardError",
]


class GuardError(ValueError):
    """Raised when a guard check fails."""

    pass


def require_not_empty(
    value: Any,
    name: str = "value",
    error_msg: Optional[str] = None,
) -> Any:
    """
    Require a value to be non-empty.

    Args:
        value: Value to check
        name: Name of the value (for error messages)
        error_msg: Custom error message

    Returns:
        The value if not empty

    Raises:
        GuardError: If value is empty

    Example:
        >>> require_not_empty("hello", "message")
        'hello'
        >>> require_not_empty("", "message")
        Traceback: GuardError
    """
    if not value:
        msg = error_msg or f"'{name}' must not be empty"
        raise GuardError(msg)
    return value


def require_truthy(
    value: Any,
    name: str = "value",
    error_msg: Optional[str] = None,
) -> Any:
    """
    Require a value to be truthy.

    Args:
        value: Value to check
        name: Name of the value (for error messages)
        error_msg: Custom error message

    Returns:
        The value if truthy

    Raises:
        GuardError: If value is falsy

    Example:
        >>> require_truthy(True, "enabled")
        True
    """
    if not value:
        msg = error_msg or f"'{name}' must be truthy"
        raise GuardError(msg)
    return value


def require_in(
    value: Any,
    valid_values: Any,
    name: str = "value",
) -> Any:
    """
    Require a value to be in a set of valid values.

    Args:
        value: Value to check
        valid_values: Collection of valid values
        name: Name of the value (for error messages)

    Returns:
        The value if in valid values

    Raises:
        GuardError: If value not in valid values

    Example:
        >>> require_in("admin", ["admin", "user", "guest"], "role")
        'admin'
    """
    if value not in valid_values:
        raise GuardError(f"'{name}' must be one of {valid_values}, got {value!r}")
    return value
