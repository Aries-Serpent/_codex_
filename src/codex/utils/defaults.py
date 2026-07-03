"""
P018: Default Argument Utilities

Consolidates 1,448 occurrences of default argument patterns.

Example:
    # Instead of: def func(data=None):
    @with_defaults(data=lambda: {})
    def func(data):
        ...
"""

from typing import Any, Callable, TypeVar

__all__ = [
    "default_factory",
    "with_defaults",
]

T = TypeVar("T")


def default_factory(factory: Callable[[], T]) -> T:
    """
    Call a factory function to get default value.

    This prevents mutable default argument issues.

    Args:
        factory: Function to call for default value

    Returns:
        Result of calling factory

    Example:
        >>> def func(items=None):
        ...     if items is None:
        ...         items = default_factory(list)
    """
    return factory()


def with_defaults(**defaults: Any) -> Callable:
    """
    Decorator to safely provide default argument values.

    Args:
        **defaults: Default values as keyword arguments

    Returns:
        Decorator function

    Example:
        >>> @with_defaults(items=list, config=dict)
        ... def func(items, config):
        ...     return items, config
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            for key, factory in defaults.items():
                if key not in kwargs:
                    kwargs[key] = factory() if callable(factory) else factory
            return func(*args, **kwargs)

        return wrapper

    return decorator
