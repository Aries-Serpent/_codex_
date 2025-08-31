"""Tokenization interfaces and adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Protocol, Sequence


class TokenizerAdapter(Protocol):
    """Minimal tokenizer interface used across the project."""

    def encode(self, text: str) -> List[int]:
        """Encode a single string into token ids."""

    def decode(self, ids: Sequence[int]) -> str:
        """Decode a sequence of token ids into a string."""

    def batch_encode(self, texts: Sequence[str]) -> List[List[int]]:
        """Encode a batch of strings."""

    def batch_decode(self, batch_ids: Sequence[Sequence[int]]) -> List[str]:
        """Decode a batch of token id sequences."""

    @property
    def vocab_size(self) -> int:
        """Return tokenizer vocabulary size."""

    @property
    def pad_token_id(self) -> int | None:
        """Return the pad token id if defined."""


@dataclass
class HFTokenizer:
    """Wrapper around :func:`transformers.AutoTokenizer.from_pretrained`.

    Parameters mirror the common ``transformers`` call arguments for padding,
    truncation and maximum length. The underlying tokenizer instance is
    accessible via :attr:`tokenizer` when direct access is required.
    """

    name_or_path: str
    padding: bool | str = False
    truncation: bool | str = False
    max_length: int | None = None
    _tokenizer: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:  # pragma: no cover - exercised in tests
        from transformers import AutoTokenizer

        self._tokenizer = AutoTokenizer.from_pretrained(self.name_or_path)

    # encode/decode helpers -------------------------------------------------
    def _encode_args(self) -> dict[str, Any]:
        return {
            "padding": self.padding,
            "truncation": self.truncation,
            "max_length": self.max_length,
        }

    def encode(self, text: str) -> List[int]:
        return self._tokenizer.encode(text, **self._encode_args())

    def decode(self, ids: Sequence[int]) -> str:
        return self._tokenizer.decode(ids)

    def batch_encode(self, texts: Sequence[str]) -> List[List[int]]:
        return [self.encode(t) for t in texts]

    def batch_decode(self, batch_ids: Sequence[Sequence[int]]) -> List[str]:
        return [self.decode(ids) for ids in batch_ids]

    # metadata ---------------------------------------------------------------
    @property
    def vocab_size(self) -> int:
        return int(getattr(self._tokenizer, "vocab_size", 0))

    @property
    def pad_token_id(self) -> int | None:
        return getattr(self._tokenizer, "pad_token_id", None)

    @property
    def eos_token_id(self) -> int | None:  # pragma: no cover - simple proxy
        return getattr(self._tokenizer, "eos_token_id", None)

    @property
    def tokenizer(self) -> Any:
        """Return the underlying ``transformers`` tokenizer instance."""

        return self._tokenizer


__all__ = ["TokenizerAdapter", "HFTokenizer"]
