"""Minimal Hydra stub used in tests when the real dependency is absent."""

from __future__ import annotations

from typing import Any, Callable


def main(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return func

    return decorator


__all__ = ["main"]
