# BEGIN: CODEX_IFACE_TOKENIZER
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List


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


# END: CODEX_IFACE_TOKENIZER
