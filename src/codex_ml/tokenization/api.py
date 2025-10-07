"""Tokenization API exports with deprecation helpers."""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Protocol, Sequence, cast

from codex_ml.interfaces.tokenizer import HFTokenizer
from .adapter import WhitespaceTokenizer

BOS_TOKEN = "<BOS>"
EOS_TOKEN = "<EOS>"
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


class TokenizerAdapter(Protocol):
    """Minimal tokenizer interface for the symbolic pipeline."""

    def encode(self, text: str) -> List[int]:
        """Return token ids for text without adding special tokens."""

    def decode(self, ids: Sequence[int]) -> str:
        """Convert token ids back to a string."""

    def add_special_tokens(self, tokens: Sequence[str]) -> Dict[str, int]:
        """Register additional special tokens and return their id mapping."""

    def save(self, path: Path) -> None:
        """Persist tokenizer configuration to path.

        path may be a directory or a tokenizer.json file location.
        """

    @property
    def vocab_size(self) -> int:
        """Return size of the tokenizer vocabulary."""

    @property
    def name_or_path(self) -> str:
        """Return model identifier or local path backing the tokenizer."""


if TYPE_CHECKING:  # pragma: no cover - import only used for typing
    from .hf_tokenizer import HFTokenizerAdapter as _HFTokenizerAdapter  # noqa: F401
    from .sp_trainer import SPTokenizer as _SPTokenizer  # noqa: F401


def _load_hf_adapter():
    try:
        from .hf_tokenizer import HFTokenizerAdapter as adapter
    except ModuleNotFoundError as exc:  # pragma: no cover - surfaced to callers
        missing = (exc.name or "").split(".", 1)[0]
        if missing == "transformers":
            raise ModuleNotFoundError(
                "Tokenizer operations that rely on Hugging Face tokenizers require the optional "
                "'transformers' dependency.",
                name="transformers",
            ) from exc
        raise
    return adapter


def load_tokenizer(
    name: Optional[str] = None,
    path: Optional[str] = None,
    *,
    use_fast: bool = True,
) -> TokenizerAdapter:
    """Load a tokenizer by name or filesystem path."""

    target = path or name
    if target and str(target).endswith(".model"):
        from .sentencepiece_adapter import SentencePieceAdapter

        return cast(TokenizerAdapter, SentencePieceAdapter(Path(target)).load())
    adapter = _load_hf_adapter()
    return adapter.load(target, use_fast=use_fast)


def get_tokenizer(*args, **kwargs):
    """Alias maintained for compatibility."""

    return load_tokenizer(*args, **kwargs)


def _load_sp_tokenizer():
    try:
        from .sp_trainer import SPTokenizer as tokenizer
    except ModuleNotFoundError as exc:  # pragma: no cover - surfaced to callers
        missing = (exc.name or "").split(".", 1)[0]
        if missing == "sentencepiece":
            raise ModuleNotFoundError(
                "Tokenizer operations that rely on SentencePiece require the optional 'sentencepiece' dependency.",
                name="sentencepiece",
            ) from exc
        raise
    return tokenizer


def __getattr__(name: str):  # pragma: no cover - thin lazy import shim
    if name == "HFTokenizerAdapter":
        return _load_hf_adapter()
    if name == "SPTokenizer":
        return _load_sp_tokenizer()
    raise AttributeError(name)


def deprecated_legacy_access(name: str):
    """Emit deprecation warning and provide legacy attribute access when possible."""

    legacy_map = {
        "TokenizerAdapter": lambda: TokenizerAdapter,
        "load_tokenizer": lambda: get_tokenizer,
        "get_tokenizer": lambda: get_tokenizer,
        "BOS_TOKEN": lambda: BOS_TOKEN,
        "EOS_TOKEN": lambda: EOS_TOKEN,
        "PAD_TOKEN": lambda: PAD_TOKEN,
        "UNK_TOKEN": lambda: UNK_TOKEN,
        "WhitespaceTokenizer": lambda: WhitespaceTokenizer,
        "HFTokenizer": lambda: HFTokenizer,
        "HFTokenizerAdapter": _load_hf_adapter,
        "SPTokenizer": _load_sp_tokenizer,
    }
    provider = legacy_map.get(name)
    if provider is None:
        return None
    warnings.warn(
        "Accessing 'codex_ml.tokenization.%s' is deprecated; import from 'codex_ml.tokenization.api' instead."
        % name,
        DeprecationWarning,
        stacklevel=3,
    )
    try:
        value = provider()
    except ModuleNotFoundError:
        raise
    except Exception:
        if name == "SPTokenizer":  # pragma: no cover - optional dependency guard
            raise
        raise
    return value


__all__ = [
    "BOS_TOKEN",
    "EOS_TOKEN",
    "PAD_TOKEN",
    "UNK_TOKEN",
    "TokenizerAdapter",
    "WhitespaceTokenizer",
    "HFTokenizer",
    "HFTokenizerAdapter",  # noqa: F822 - provided via __getattr__
    "SPTokenizer",  # noqa: F822 - provided via __getattr__
    "load_tokenizer",
    "get_tokenizer",
    "deprecated_legacy_access",
]


def __getattr__(name: str):
    if name == "HFTokenizerAdapter":
        return _load_hf_adapter()
    raise AttributeError(name)
