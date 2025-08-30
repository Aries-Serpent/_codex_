# BEGIN: CODEX_IFACE_TOKENIZER
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Union, Dict, Any

try:
    from transformers import AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover - optional dep
    AutoTokenizer = None


class TokenizerAdapter(ABC):
    """Abstract adapter for tokenization backends.

    Implementations must provide deterministic encode/decode for reproducibility and
    expose key ids for padding and EOS handling.
    """

    @abstractmethod
    def encode(self, text: str, *, add_special_tokens: bool = True) -> List[int]:
        """Encode a single string into token ids."""
        raise NotImplementedError

    def batch_encode(
        self, texts: Iterable[str], *, add_special_tokens: bool = True
    ) -> List[List[int]]:
        """Optional batch encode; default maps to encode()."""
        return [self.encode(t, add_special_tokens=add_special_tokens) for t in texts]

    @abstractmethod
    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        """Decode token ids into a string."""
        raise NotImplementedError

    @abstractmethod
    def vocab_size(self) -> int:
        """Return size of vocabulary."""
        raise NotImplementedError

    @abstractmethod
    def pad_id(self) -> int:
        """Return padding token id."""
        raise NotImplementedError

    @abstractmethod
    def eos_id(self) -> int:
        """Return end-of-sequence token id."""
        raise NotImplementedError


class HFTokenizer:
    """Lightweight wrapper around ``transformers.AutoTokenizer``."""

    def __init__(
        self,
        name_or_path: str,
        *,
        padding: Union[bool, str] = False,
        truncation: Union[bool, str] = True,
        max_length: Optional[int] = None,
        use_fast: bool = True,
        **kwargs: Any,
    ) -> None:
        if AutoTokenizer is None:
            raise ImportError("transformers is required for HFTokenizer")
        self.tk = AutoTokenizer.from_pretrained(name_or_path, use_fast=use_fast, **kwargs)
        self.padding = padding
        self.truncation = truncation
        self.max_length = max_length

    def encode(self, text: str) -> List[int]:
        return self.tk.encode(
            text,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
        )

    def batch_encode(self, texts: List[str]) -> Dict[str, Any]:
        return self.tk(
            texts,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
            return_tensors=None,
        )


__all__ = ["TokenizerAdapter", "HFTokenizer"]


# END: CODEX_IFACE_TOKENIZER
