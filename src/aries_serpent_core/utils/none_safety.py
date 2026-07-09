"""
P001: None/Null Safety Validation Utilities

This module provides consistent patterns for None/null safety checks
across the codebase.

Consolidates 1,456 occurrences of None validation patterns into
reusable, well-tested utility functions.

Example:
    # Instead of: if value is None: ...
    value = ensure_not_none(value, "my_param")

    # Instead of: value = x if x is not None else y
    value = coalesce(x, y, z, "default")
"""

from typing import Any, Callable, Optional, TypeVar

__all__ = [
    "ensure_not_none",
    "is_none",
    "coalesce",
    "nullable",
    "NoneError",
]

T = TypeVar("T")


class NoneError(ValueError):
    """Raised when a value is None but shouldn't be."""

    pass


def ensure_not_none(
    value: Optional[T],
    name: str = "value",
    default: Optional[T] = None,
    error_msg: Optional[str] = None,
) -> T:
    """
    Ensure a value is not None, optionally using a default.

    Args:
        value: The value to check
        name: Name of the value (for error messages)
        default: Default value to use if value is None
        error_msg: Custom error message

    Returns:
        The value if not None, the default if provided, or raises error

    Raises:
        NoneError: If value is None and no default provided

    Example:
        >>> val = ensure_not_none(None, "config", default={})
        >>> val
        {}

        >>> val = ensure_not_none(42, "count")
        >>> val
        42
    """
    if value is not None:
        return value

    if default is not None:
        return default

    error_message = error_msg or f"'{name}' must not be None"
    raise NoneError(error_message)


def is_none(value: Any) -> bool:
    """
    Check if a value is None.

    This is a simple wrapper for consistency and potential future extensions.

    Args:
        value: The value to check

    Returns:
        True if value is None, False otherwise

    Example:
        >>> is_none(None)
        True
        >>> is_none(42)
        False
    """
    return value is None


def coalesce(*values: Optional[T], default: Optional[T] = None) -> T:
    """
    Return the first non-None value from a list of values.

    Args:
        *values: Variable arguments to check in order
        default: Default value if all are None

    Returns:
        First non-None value, or default if all are None

    Raises:
        NoneError: If all values are None and no default provided

    Example:
        >>> coalesce(None, None, 42, 99)
        42

        >>> coalesce(None, None, None, default=10)
        10
    """
    for value in values:
        if value is not None:
            return value

    if default is not None:
        return default

    raise NoneError("All values are None and no default provided")


def nullable(
    value: Optional[T],
    handler: Callable[[T], Any],
    default: Any = None,
) -> Any:
    """
    Apply a handler function only if value is not None.

    Args:
        value: The value to check
        handler: Function to apply if value is not None
        default: Value to return if value is None

    Returns:
        Result of handler(value) if value is not None, else default

    Example:
        >>> result = nullable(42, lambda x: x * 2)
        >>> result
        84

        >>> result = nullable(None, lambda x: x * 2, default=0)
        >>> result
        0
    """
    if value is not None:
        return handler(value)
    return default


def is_empty(value: Optional[Any]) -> bool:
    """
    Check if a value is None or empty.

    Handles None, empty strings, empty collections, etc.

    Args:
        value: The value to check

    Returns:
        True if value is None or empty, False otherwise

    Example:
        >>> is_empty(None)
        True
        >>> is_empty([])
        True
        >>> is_empty("")
        True
        >>> is_empty([1, 2, 3])
        False
    """
    if value is None:
        return True
    try:
        return len(value) == 0
    except TypeError:
        # value doesn't have len(), assume not empty
        return False
