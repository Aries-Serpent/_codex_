"""Helpers for working with pinned HuggingFace identifiers."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Tuple

__all__ = ["ensure_pinned_kwargs", "load_from_pretrained"]


def ensure_pinned_kwargs(
    identifier: str,
    overrides: Mapping[str, Any] | None = None,
) -> Tuple[str | None, Dict[str, Any]]:
    """Return a ``revision`` value and merged kwargs for HF loaders.

    The shim keeps behaviour intentionally simple: a ``revision`` supplied via
    ``overrides`` wins, otherwise ``None`` is returned so callers can decide how
    to proceed.
    """

    kwargs = dict(overrides or {})
    revision = kwargs.get("revision")
    if revision is None and identifier.startswith("./"):
        return None, kwargs
    return revision, kwargs


def load_from_pretrained(factory: Any, identifier: str, /, **kwargs: Any) -> Any:
    """Instantiate ``factory`` using ``identifier`` with best-effort fallbacks."""

    if hasattr(factory, "from_pretrained"):
        return factory.from_pretrained(identifier, **kwargs)
    if callable(factory):
        return factory(identifier, **kwargs)
    raise TypeError(f"Unsupported factory type: {type(factory)!r}")
