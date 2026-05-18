"""
  Init   Module

This module provides functionality for   init  .

Usage:
    from data.__init__ import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


from importlib import import_module
from typing import TYPE_CHECKING, Any

_MODULE_EXPORTS = {
    "collect_stats": ".loaders",
    "iter_jsonl": ".loaders",
    "iter_txt": ".loaders",
    "stream_paths": ".loaders",
    "load_dataset": ".loaders",
    "load_jsonl": ".loaders",
    "load_csv": ".loaders",
    "split_indices": ".loaders",
    "compute_file_checksum": ".loaders",
    "Sample": ".loaders",
    "StreamingDataModule": ".datamodule",
    "default_example_validator": ".datamodule",
    "iter_jsonl_chunks": ".streaming",
    "list_reasoning_corpora": ".reasoning_manifest",
    "get_reasoning_corpus": ".reasoning_manifest",
    "build_corpus_selection": ".reasoning_manifest",
    "iter_corpus_manifests": ".reasoning_manifest",
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
    from .loaders import (
        Sample,
        collect_stats,
        compute_file_checksum,
        iter_jsonl,
        iter_txt,
        load_csv,
        load_dataset,
        load_jsonl,
        split_indices,
        stream_paths,
    )
    from .streaming import iter_jsonl_chunks
