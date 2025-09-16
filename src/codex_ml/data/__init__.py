"""Top-level data package exports with lazy loader bindings."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = ["collect_stats", "iter_jsonl", "iter_txt", "stream_paths"]


def __getattr__(name: str) -> Any:
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(".loaders", __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


if TYPE_CHECKING:  # pragma: no cover - import for type checkers only
    from .loaders import collect_stats, iter_jsonl, iter_txt, stream_paths
