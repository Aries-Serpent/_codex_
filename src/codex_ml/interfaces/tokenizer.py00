# BEGIN: CODEX_IFACE_TOKENIZER
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Optional, Union

from transformers import AutoTokenizer


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


# ---------------------------------------------------------------------------
# Concrete implementations
# ---------------------------------------------------------------------------


class HFTokenizer(TokenizerAdapter):
    """Thin wrapper around ``transformers.AutoTokenizer``.

    Parameters
    ----------
    name_or_path:
        Model identifier or local path resolved by ``AutoTokenizer``.
    padding, truncation, max_length:
        Forwarded to ``tokenizer.encode`` for deterministic batching per the
        Transformers padding and truncation guide.
    """

    def __init__(
        self,
        name_or_path: str,
        *,
        padding: Union[bool, str] = False,
        truncation: Union[bool, str] = False,
        max_length: Optional[int] = None,
    ) -> None:
        self._tok = AutoTokenizer.from_pretrained(name_or_path, use_fast=True)
        if self._tok.pad_token is None:
            self._tok.pad_token = self._tok.eos_token
        self.padding = padding
        self.truncation = truncation
        self.max_length = max_length

    def encode(self, text: str, *, add_special_tokens: bool = True) -> List[int]:
        return self._tok.encode(
            text,
            add_special_tokens=add_special_tokens,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
        )

    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        return self._tok.decode(list(ids), skip_special_tokens=skip_special_tokens)

    def vocab_size(self) -> int:
        return int(self._tok.vocab_size)

    def pad_id(self) -> int:
        return int(self._tok.pad_token_id or 0)

    def eos_id(self) -> int:
        return int(self._tok.eos_token_id or 0)

# END: CODEX_IFACE_TOKENIZER
