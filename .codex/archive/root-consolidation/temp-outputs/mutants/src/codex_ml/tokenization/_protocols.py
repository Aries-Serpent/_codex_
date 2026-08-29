"""Shared tokenization protocols.

Extracted from api.py to break the api→hf_tokenizer→api circular import.
Downstream modules (hf_tokenizer, hf_adapter, sp_trainer) should import
TokenizerAdapter from here, never from api.  api.py re-exports it for
backward compatibility.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class TokenizerAdapter(Protocol):
    """Minimal tokenizer interface for the symbolic pipeline.

    All tokenizer implementations (HFTokenizerAdapter, SPTokenizer,
    WhitespaceTokenizer, etc.) must satisfy this protocol.
    """

    def encode(self, text: str) -> list[int]:
        """Return token ids for text without adding special tokens."""

    def decode(self, ids: Sequence[int]) -> str:
        """Convert token ids back to a string."""

    def add_special_tokens(self, tokens: Sequence[str]) -> dict[str, int]:
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


__all__ = ["TokenizerAdapter"]
