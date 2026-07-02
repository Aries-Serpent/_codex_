"""Compatibility wrappers for the tokenizer training utilities.

The :mod:`codex_ml` package historically exposed a lightweight
``TrainTokenizerConfig`` based on SentencePiece. The authoritative
implementation lives in :mod:`src.tokenization.train_tokenizer`, which now
supports streaming ingestion, manifest generation, and additional
hyperparameters.  To avoid duplicating that logic we re-export the public
API here so existing imports keep working while the CLI can rely on the
fully featured trainer.
"""

from __future__ import annotations

from pathlib import Path

from tokenization import train_tokenizer as _legacy_train_tokenizer
from tokenization.train_tokenizer import (
    TrainTokenizerConfig,  # explicit re-export for type checkers
)


def train(cfg: TrainTokenizerConfig) -> Path:
    """Train a tokenizer and return the output directory."""

    return _legacy_train_tokenizer.train(cfg)


def run(cfg: TrainTokenizerConfig) -> Path:
    """Backward compatible alias for :func:`train`."""

    return train(cfg)


# ``main`` is provided for ``python -m codex_ml.tokenization.train_tokenizer``
# entry points and Hydra integration.  The legacy module handles both cases,
# so we simply re-export the callable.
main = _legacy_train_tokenizer.main


__all__ = ["TrainTokenizerConfig", "main", "run", "train"]


def train(cfg: TrainTokenizerConfig) -> Path:  # type: ignore[no-redef]
    """Train a tokenizer and return the output directory."""

    return _legacy_train_tokenizer.train(cfg)


def run(cfg: TrainTokenizerConfig) -> Path:  # type: ignore[no-redef]
    """Backward compatible alias for :func:`train`."""

    return train(cfg)


# ``main`` is provided for ``python -m codex_ml.tokenization.train_tokenizer``
# entry points and Hydra integration.  The legacy module handles both cases,
# so we simply re-export the callable.
main = _legacy_train_tokenizer.main


__all__ = ["TrainTokenizerConfig", "main", "run", "train"]
