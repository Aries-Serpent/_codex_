"""Tokenizer utilities for building and validating Codex vocabularies."""

import warnings as _warnings

_warnings.warn(
    "src.tokenizer is deprecated and will be removed in version 2.0. "
    "Use src.codex_ml.tokenization instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__: list[str] = []
