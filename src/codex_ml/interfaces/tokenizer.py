# BEGIN: CODEX_IFACE_TOKENIZER
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union

try:  # optional dependency
    from transformers import AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover
    AutoTokenizer = None  # type: ignore


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

    @property
    @abstractmethod
    def vocab_size(self) -> int:
        """Return size of vocabulary."""
        raise NotImplementedError

    @property
    @abstractmethod
    def pad_id(self) -> int:
        """Return padding token id."""
        raise NotImplementedError

    @property
    @abstractmethod
    def eos_id(self) -> int:
        """Return end-of-sequence token id."""
        raise NotImplementedError


# Concrete implementation ----------------------------------------------------
class HFTokenizer(TokenizerAdapter):
    """Lightweight wrapper around ``transformers.AutoTokenizer``.

    Provides a stable adapter interface while preserving compatibility with
    existing code that expects Hugging Face-style batch outputs.
    """

    def __init__(
        self,
        name_or_path: str,
        padding: Union[bool, str] = False,
        truncation: Union[bool, str] = True,
        max_length: Optional[int] = None,
        use_fast: bool = True,
        **kwargs: Any,
    ) -> None:
        if AutoTokenizer is None:  # pragma: no cover - transformers missing
            raise ImportError("transformers is required for HFTokenizer")
        self.tk = AutoTokenizer.from_pretrained(name_or_path, use_fast=use_fast, **kwargs)
        self.padding = padding
        self.truncation = truncation
        self.max_length = max_length

    def encode(self, text: str, *, add_special_tokens: bool = True) -> List[int]:
        """Encode a single string to a list of token ids."""
        return self.tk.encode(
            text,
            add_special_tokens=add_special_tokens,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
        )

    def batch_encode(
        self,
        texts: Iterable[str],
        *,
        add_special_tokens: bool = True,
        return_dict: bool = False,
    ) -> Union[List[List[int]], Dict[str, Any]]:
        """Batch encode texts.

        - By default returns List[List[int]] of input_ids for adapter consistency.
        - If return_dict=True, returns the raw Hugging Face-style dict, preserving
          backward compatibility with prior usages expecting a mapping.
        """
        enc = self.tk(
            list(texts),
            add_special_tokens=add_special_tokens,
            padding=self.padding,
            truncation=self.truncation,
            max_length=self.max_length,
            return_tensors=None,
        )
        if return_dict:
            return enc
        return [list(seq) for seq in enc.get("input_ids", [])]

    # Compatibility helper mirroring HF API
    def batch_encode_plus(
        self,
        texts: Iterable[str],
        *,
        add_special_tokens: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Return a Hugging Face-style encoding dict (compatibility alias)."""
        _ = kwargs  # ignored but accepted for compatibility
        out = self.batch_encode(texts, add_special_tokens=add_special_tokens, return_dict=True)
        return out  # type: ignore[return-value]

    def decode(self, ids: Iterable[int], *, skip_special_tokens: bool = True) -> str:
        """Decode a list of token ids back to a string."""
        return self.tk.decode(list(ids), skip_special_tokens=skip_special_tokens)

    @property
    def vocab_size(self) -> int:
        """Return tokenizer vocabulary size as int."""
        return int(getattr(self.tk, "vocab_size", 0) or 0)

    @property
    def pad_id(self) -> int:
        """Return padding token id, 0 if undefined."""
        return int(getattr(self.tk, "pad_token_id", None) or 0)

    @property
    def eos_id(self) -> int:
        """Return end-of-sequence token id, 0 if undefined."""
        return int(getattr(self.tk, "eos_token_id", None) or 0)

    # Convenience accessor
    @property
    def raw_tokenizer(self) -> Any:
        """Access the underlying Hugging Face tokenizer instance."""
        return self.tk


__all__ = ["TokenizerAdapter", "HFTokenizer"]


# END: CODEX_IFACE_TOKENIZER
