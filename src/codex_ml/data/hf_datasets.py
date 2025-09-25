"""HuggingFace dataset loaders with streaming support."""

from __future__ import annotations

from typing import Any

from codex_ml.utils.hf_pinning import ensure_pinned_kwargs

from .registry import register_dataset

try:  # optional dependency
    from datasets import load_dataset as _load_dataset  # type: ignore

    _HAS_DATASETS = True
except Exception:  # pragma: no cover - optional
    _load_dataset = None  # type: ignore
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
        revision, extra = ensure_pinned_kwargs(name)
        if revision is None:
            return _load_dataset(
                name, split=split, streaming=True, **extra
            )  # nosec B615: local path
        return _load_dataset(
            name,
            split=split,
            streaming=True,
            revision=revision,
            **extra,
        )  # nosec B615: revision pinned via ensure_pinned_kwargs
    except Exception:
        if fallback_path:
            from .registry import get_dataset

            return get_dataset("lines", path=fallback_path)
        revision, extra = ensure_pinned_kwargs(name)
        if revision is None:
            return _load_dataset(name, split=split, **extra)  # nosec B615: local path fallback
        return _load_dataset(
            name,
            split=split,
            revision=revision,
            **extra,
        )  # nosec B615: revision pinned via ensure_pinned_kwargs
