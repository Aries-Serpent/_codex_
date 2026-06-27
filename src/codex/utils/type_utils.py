"""
Type Utilities

Utilities for working with Python typing constructs at runtime.
"""

from typing import Any, Union, get_args, get_origin


def safe_isinstance(obj: Any, typ: Any) -> bool:
    """
    isinstance() that handles typing constructs safely.

    Standard isinstance() doesn't work with typing constructs like Optional, Union, etc.
    This function handles those cases gracefully.

    Args:
        obj: Object to check
        typ: Type or typing construct to check against

    Returns:
        True if obj is an instance of typ, False otherwise

    Examples:
        >>> from typing import Optional
        >>> safe_isinstance(5, int)
        True
        >>> safe_isinstance(5, Optional[int])
        True
        >>> safe_isinstance(None, Optional[int])
        True
        >>> safe_isinstance([1, 2, 3], list[int])
        True
        >>> safe_isinstance(['a', 'b'], list[int])
        False
    """
    # Get the origin of the type (e.g., list from list[int])
    origin = get_origin(typ)

    # If no origin, it's a regular type
    if origin is None:
        try:
            return isinstance(obj, typ)
        except TypeError:
            # typ might be a typing construct we don't handle
            return False

    # Handle list and tuple with type parameters
    if origin in (list, tuple):
        args = get_args(typ)
        if not isinstance(obj, (list, tuple)):
            return False
        if not args:
            # No type parameter, just check if it's a list/tuple
            return True
        # Check all elements match the type parameter
        return all(safe_isinstance(item, args[0]) for item in obj)

    # Handle Union (including Optional which is Union[T, None])
    if origin is Union:
        # Check if obj matches any of the union members
        return any(safe_isinstance(obj, t) for t in get_args(typ))

    # Handle dict with type parameters
    if origin is dict:
        if not isinstance(obj, dict):
            return False
        args = get_args(typ)
        if not args:
            return True
        key_type, value_type = args
        return all(
            safe_isinstance(k, key_type) and safe_isinstance(v, value_type) for k, v in obj.items()
        )

    # For other generic types, try to check against the origin
    args = get_args(typ)
    if args:
        try:
            # Try checking against all args
            return isinstance(obj, args if len(args) > 1 else args[0])
        except TypeError:
            # Fallback: just check against origin
            try:
                return isinstance(obj, origin)
            except TypeError:
                return False

    # Fallback: try checking against the origin
    try:
        return isinstance(obj, origin)
    except TypeError:
        return False
