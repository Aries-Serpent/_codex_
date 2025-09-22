"""Hydra stub for offline execution."""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable

__all__ = ["main"]


def main(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*f_args: Any, **f_kwargs: Any) -> Any:
            return func(*f_args, **f_kwargs)

        return wrapper

    return decorator
