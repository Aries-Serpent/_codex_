"""Tokenization utilities and adapter interfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Protocol, Sequence

BOS_TOKEN = "<BOS>"
EOS_TOKEN = "<EOS>"
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


class TokenizerAdapter(Protocol):
    """Minimal tokenizer interface for the symbolic pipeline."""

    def encode(self, text: str) -> List[int]:
        """Return token ids for *text* without adding special tokens."""

    def decode(self, ids: Sequence[int]) -> str:
        """Convert token ids back to a string."""

    def add_special_tokens(self, tokens: Sequence[str]) -> Dict[str, int]:
        """Register additional special tokens and return their id mapping."""

    def save(self, path: Path) -> None:
        """Persist tokenizer configuration to *path*.

        ``path`` may be a directory or a ``tokenizer.json`` file location.
        """

    @property
    def vocab_size(self) -> int:
        """Return size of the tokenizer vocabulary."""

    @property
    def name_or_path(self) -> str:
        """Return model identifier or local path backing the tokenizer."""


from .hf_tokenizer import HFTokenizerAdapter  # noqa: E402  (import after Protocol)


def load_tokenizer(
    name: Optional[str] = None, path: Optional[str] = None
) -> TokenizerAdapter:
    """Load a tokenizer by name or filesystem path.

    If both ``name`` and ``path`` are ``None``, the pretrained GPT-2
    tokenizer is used.
    """

    target = path or name
    return HFTokenizerAdapter.load(target)


__all__ = [
    "TokenizerAdapter",
    "HFTokenizerAdapter",
    "load_tokenizer",
    "BOS_TOKEN",
    "EOS_TOKEN",
    "PAD_TOKEN",
    "UNK_TOKEN",
]
