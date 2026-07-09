"""Compatibility shims for tokenization imports."""

from __future__ import annotations

import importlib
import warnings
from functools import lru_cache
from typing import Any

_ALIASES: dict[str, str] = {
    # "encode": "codex_ml.tokenization.api:encode",
    # "decode": "codex_ml.tokenization.api:decode",
}


def _get_api() -> object:
    return importlib.import_module("codex_ml.tokenization.api")


@lru_cache(maxsize=1)
def _warn_load_tokenizer_deprecated() -> None:
    warnings.warn(
        "codex_ml.tokenization.compat.load_tokenizer is deprecated; use codex_ml.tokenization.api.load_tokenizer",  # noqa: E501
        DeprecationWarning,
        stacklevel=2,
    )


def load_tokenizer(*args: Any, **kwargs: Any) -> Any:
    """Backwards-compatible load_tokenizer with deprecation warning."""
    _warn_load_tokenizer_deprecated()
    return _get_api().load_tokenizer(*args, **kwargs)  # type: ignore[attr-defined]


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
