"""Top-level data package exports with lazy loader bindings."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

_MODULE_EXPORTS = {
    "collect_stats": ".loaders",
    "iter_jsonl": ".loaders",
    "iter_txt": ".loaders",
    "stream_paths": ".loaders",
    "StreamingDataModule": ".datamodule",
    "default_example_validator": ".datamodule",
    "iter_jsonl_chunks": ".streaming",
}

__all__ = list(_MODULE_EXPORTS)


def __getattr__(name: str) -> Any:
    try:
        module_name = _MODULE_EXPORTS[name]
    except KeyError as exc:  # pragma: no cover - attribute errors handled below
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc
    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


if TYPE_CHECKING:  # pragma: no cover - import for type checkers only
    from .datamodule import StreamingDataModule, default_example_validator
    from .loaders import collect_stats, iter_jsonl, iter_txt, stream_paths
    from .streaming import iter_jsonl_chunks
