"""HuggingFace dataset loaders with streaming support."""

from __future__ import annotations

from typing import Any

from .registry import register_dataset

try:  # optional dependency
    from datasets import load_dataset  # type: ignore

    _HAS_DATASETS = True
except Exception:  # pragma: no cover - optional
    load_dataset = None  # type: ignore
    _HAS_DATASETS = False


@register_dataset("hf")
def load_hf_dataset(name: str, split: str = "train", fallback_path: str | None = None) -> Any:
    """Load a dataset via ``datasets.load_dataset`` with streaming.

    If the `datasets` library is unavailable or loading fails, falls back to a
    line-based dataset when ``fallback_path`` is provided.
    """
    if not _HAS_DATASETS:
        if fallback_path:
            from .registry import get_dataset

            return get_dataset("lines", path=fallback_path)
        raise ImportError("datasets library not available")
    try:
        return load_dataset(name, split=split, streaming=True)
    except Exception:
        if fallback_path:
            from .registry import get_dataset

            return get_dataset("lines", path=fallback_path)
        return load_dataset(name, split=split)
