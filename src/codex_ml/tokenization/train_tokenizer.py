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

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from tokenization import train_tokenizer as _legacy_train_tokenizer_module
from tokenization.train_tokenizer import (
    TrainTokenizerConfig,  # explicit re-export for type checkers
)

# Legacy streaming tests and internal callers use the implementation module's
# ingest/SPM symbols directly. Keep compatibility without duplicating logic.
ingest = getattr(_legacy_train_tokenizer_module, "ingest", None)
spm = getattr(_legacy_train_tokenizer_module, "spm", None)
_SPM_ERROR = getattr(_legacy_train_tokenizer_module, "_SPM_ERROR", None)
SentencePieceUnigramTokenizer = getattr(
    _legacy_train_tokenizer_module,
    "SentencePieceUnigramTokenizer",
    None,
)


def _iter_text(files: Sequence[str], cfg: TrainTokenizerConfig) -> Iterable[str]:
    """Compatibility iterator used by legacy streaming tests and callers."""
    chunk_size = getattr(cfg, "stream_chunk_size", None) or 1024 * 1024
    for path in files:
        if ingest is not None:
            yield from ingest(path, encoding="auto", chunk_size=chunk_size)
        else:
            for line in Path(path).read_text(encoding="utf-8").splitlines(True):
                yield line


def train(cfg: TrainTokenizerConfig) -> Path:
    """Train a tokenizer and return the output directory."""
    _legacy_train_tokenizer_module.ingest = ingest
    _legacy_train_tokenizer_module.spm = spm
    _legacy_train_tokenizer_module._SPM_ERROR = _SPM_ERROR
    _legacy_train_tokenizer_module.SentencePieceUnigramTokenizer = SentencePieceUnigramTokenizer
    return _legacy_train_tokenizer_module.train(cfg)  # type: ignore[attr-defined]


def run(cfg: TrainTokenizerConfig) -> Path:
    """Backward compatible alias for :func:`train`."""
    return train(cfg)


# ``main`` is provided for ``python -m codex_ml.tokenization.train_tokenizer``
# entry points and Hydra integration.  The legacy module handles both cases,
# so we simply re-export the callable.
main: Any = _legacy_train_tokenizer_module.main  # type: ignore[attr-defined]


__all__ = [
    "SentencePieceUnigramTokenizer",
    "TrainTokenizerConfig",
    "_iter_text",
    "_SPM_ERROR",
    "ingest",
    "main",
    "run",
    "spm",
    "train",
]
