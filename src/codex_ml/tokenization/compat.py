"""Compatibility shims for tokenization imports."""

from __future__ import annotations

import importlib
import warnings
from typing import Any

_ALIASES: dict[str, str] = {
    # "encode": "codex_ml.tokenization.api:encode",
    # "decode": "codex_ml.tokenization.api:decode",
}

_warned = False
_api = None


def _get_api():
    global _api
    if _api is None:
        _api = importlib.import_module("codex_ml.tokenization.api")
    return _api


def load_tokenizer(*args: Any, **kwargs: Any) -> Any:
    """Backwards-compatible load_tokenizer with deprecation warning."""
    global _warned
    if not _warned:
        warnings.warn(
            "codex_ml.tokenization.compat.load_tokenizer is deprecated; use codex_ml.tokenization.api.load_tokenizer",  # noqa: E501
            DeprecationWarning,
            stacklevel=2,
        )
        _warned = True  # noqa: F841
    return _get_api().load_tokenizer(*args, **kwargs)


def __getattr__(name: str) -> Any:
    if name in _ALIASES:
        modname, attr = _ALIASES[name].split(":")
        warnings.warn(
            f"codex_ml.tokenization.{name} is deprecated; use {_ALIASES[name]}",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(importlib.import_module(modname), attr)
    raise AttributeError(name)


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_ALIASES.keys()))
