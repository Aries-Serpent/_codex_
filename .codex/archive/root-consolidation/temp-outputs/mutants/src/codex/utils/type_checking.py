"""
P002: Runtime Type Validation Utilities

Consolidates 1,540 occurrences of isinstance() patterns and type
checking into consistent, well-tested utility functions.

Example:
    # Instead of: if not isinstance(value, str):
    value = require_type(value, str, "username")

    # Instead of: isinstance(x, (int, float))
    if is_type(x, int, float):
        ...
"""

from typing import Any, Callable, Dict, Optional, Type, TypeVar

__all__ = [
    "is_type",
    "require_type",
    "safe_cast",
    "type_dispatch",
    "TypeCheckError",
    "get_type_name",
]

T = TypeVar("T")


class TypeCheckError(TypeError):
    """Raised when a type check fails."""

    pass


def get_type_name(type_obj: Type) -> str:
    """
    Get a human-readable name for a type.

    Args:
        type_obj: The type to get a name for

    Returns:
        Human-readable type name

    Example:
        >>> get_type_name(str)
        'str'
        >>> get_type_name(list)
        'list'
    """
    if hasattr(type_obj, "__name__"):
        return type_obj.__name__
    return str(type_obj)


def is_type(value: Any, *types: Type) -> bool:
    """
    Check if a value is an instance of any of the given types.

    Args:
        value: The value to check
        *types: One or more types to check against

    Returns:
        True if value is an instance of any type, False otherwise

    Example:
        >>> is_type(42, int, float)
        True
        >>> is_type("hello", int, float)
        False
    """
    return isinstance(value, types if len(types) > 1 else types[0])


def require_type(
    value: Any,
    *types: Type,
    name: str = "value",
    error_msg: Optional[str] = None,
) -> Any:
    """
    Assert that a value is an instance of one of the given types.

    Args:
        value: The value to check
        *types: One or more required types
        name: Name of the value (for error messages)
        error_msg: Custom error message

    Returns:
        The value if type check passes

    Raises:
        TypeCheckError: If value is not an instance of any type

    Example:
        >>> val = require_type("hello", str, name="greeting")
        >>> val
        'hello'

        >>> require_type(42, str, name="username")
        Traceback (most recent call last):
            ...
        TypeCheckError: 'username' must be str, got int
    """
    if is_type(value, *types):
        return value

    type_names = ", ".join(get_type_name(t) for t in types)
    actual_type = get_type_name(type(value))

    if error_msg:
        raise TypeCheckError(error_msg)

    raise TypeCheckError(f"'{name}' must be {type_names}, got {actual_type}")


def safe_cast(
    value: Any,
    target_type: Type[T],
    fallback: Optional[T] = None,
    error_on_fail: bool = False,
) -> Optional[T]:
    """
    Safely cast a value to a target type with optional fallback.

    Args:
        value: The value to cast
        target_type: The target type to cast to
        fallback: Value to return if cast fails
        error_on_fail: If True, raise error on failed cast

    Returns:
        Cast value, fallback value, or None

    Raises:
        TypeCheckError: If error_on_fail=True and cast fails

    Example:
        >>> safe_cast("42", int)
        42

        >>> safe_cast("hello", int, fallback=0)
        0

        >>> safe_cast("hello", int, error_on_fail=True)
        Traceback (most recent call last):
            ...
        TypeCheckError: Could not cast 'hello' to int
    """
    try:
        if isinstance(value, target_type):
            return value
        return target_type(value)
    except (ValueError, TypeError) as e:
        if error_on_fail:
            raise TypeCheckError(f"Could not cast '{value}' to {get_type_name(target_type)}") from e
        return fallback


def type_dispatch(
    value: Any,
    handlers: Dict[Type, Callable[[Any], Any]],
    default_handler: Optional[Callable[[Any], Any]] = None,
) -> Any:
    """
    Dispatch to different handlers based on value type.

    Args:
        value: The value to dispatch on
        handlers: Dict mapping types to handler functions
        default_handler: Handler to use if no type matches

    Returns:
        Result of calling the appropriate handler

    Raises:
        TypeCheckError: If no handler found and no default_handler

    Example:
        >>> handlers = {
        ...     str: lambda x: x.upper(),
        ...     int: lambda x: x * 2,
        ... }
        >>> type_dispatch("hello", handlers)
        'HELLO'
        >>> type_dispatch(21, handlers)
        42
    """
    # Check exact type matches first
    value_type = type(value)
    if value_type in handlers:
        return handlers[value_type](value)

    # Check isinstance matches
    for handler_type, handler_fn in handlers.items():
        if isinstance(value, handler_type):
            return handler_fn(value)

    # Use default handler
    if default_handler is not None:
        return default_handler(value)

    # No handler found
    type_names = ", ".join(get_type_name(t) for t in handlers.keys())
    raise TypeCheckError(
        f"No handler found for type {get_type_name(type(value))}. " f"Supported types: {type_names}"
    )
