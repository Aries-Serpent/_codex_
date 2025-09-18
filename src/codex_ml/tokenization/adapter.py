"""Tokenizer adapter interfaces and implementations."""

from __future__ import annotations

import abc
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class TokenizerAdapter(abc.ABC):
    """Abstract base class for tokenizers used in training/eval."""

    @abc.abstractmethod
    def encode(self, text: str, **kwargs: Any) -> List[int]:
        """Encode ``text`` into token ids."""

    @abc.abstractmethod
    def decode(self, tokens: Iterable[int], **kwargs: Any) -> str:
        """Decode token ids back to string."""

    @abc.abstractmethod
    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> List[List[int]]:
        """Vectorised encoding for multiple strings."""

    @abc.abstractmethod
    def save_pretrained(self, output_dir: str) -> None:
        """Persist tokenizer to ``output_dir``."""

    @staticmethod
    def from_config(cfg: Dict[str, Any]) -> "TokenizerAdapter":
        """Instantiate a tokenizer adapter from configuration mapping.

        Expected keys include ``type`` (``"hf"`` or ``"whitespace"``) and
        backend-specific parameters like ``pretrained_model_name_or_path`` for
        HuggingFace tokenizers.
        """

        ttype = cfg.get("type", "hf")
        if ttype == "hf":
            name = cfg.get("pretrained_model_name_or_path", "gpt2")
            special = cfg.get("special_tokens")
            return HFTokenizerAdapter(name, special)
        if ttype == "whitespace":
            return WhitespaceTokenizer()
        if ttype == "sentencepiece":
            raise NotImplementedError("SentencePieceTokenizer is not implemented yet")
        raise ValueError(f"Unknown tokenizer type: {ttype}")


@dataclass
class HFTokenizerAdapter(TokenizerAdapter):
    """Wrap a HuggingFace ``PreTrainedTokenizer`` object."""

    name_or_path: str
    special_tokens: Optional[Dict[str, str]] = None

    def __post_init__(self) -> None:  # pragma: no cover - simple delegation
        from transformers import AutoTokenizer  # type: ignore

        self.tokenizer = AutoTokenizer.from_pretrained(self.name_or_path, use_fast=True)
        special = self.special_tokens or {}
        if special:
            self.tokenizer.add_special_tokens({"additional_special_tokens": list(special.values())})
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.add_special_tokens({"pad_token": "<pad>"})

    def encode(self, text: str, **kwargs: Any) -> List[int]:
        return self.tokenizer.encode(text, **kwargs)

    def decode(self, tokens: Iterable[int], **kwargs: Any) -> str:
        return self.tokenizer.decode(tokens, **kwargs)

    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> List[List[int]]:
        return self.tokenizer.batch_encode_plus(list(texts), **kwargs)["input_ids"]

    def save_pretrained(self, output_dir: str) -> None:
        self.tokenizer.save_pretrained(output_dir)


class WhitespaceTokenizer(TokenizerAdapter):
    """Simple whitespace tokenizer primarily used for tests."""

    def encode(self, text: str, **kwargs: Any) -> List[int]:
        tokens = text.split()
        stable_ids: List[int] = []
        for tok in tokens:
            digest = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
            stable_ids.append(int.from_bytes(digest, "big") % (2**31))
        return stable_ids

    def decode(
        self, tokens: Iterable[int], **kwargs: Any
    ) -> str:  # pragma: no cover - lossy decode
        return " ".join(str(t) for t in tokens)

    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> List[List[int]]:
        return [self.encode(t) for t in texts]

    def save_pretrained(self, output_dir: str) -> None:  # pragma: no cover - trivial
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / "tokenizer.txt").write_text("whitespace", encoding="utf-8")


class SentencePieceTokenizer(TokenizerAdapter):
    """Placeholder for future SentencePiece support."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - stub
        raise NotImplementedError("SentencePieceTokenizer is not implemented yet")

    def encode(self, text: str, **kwargs: Any) -> List[int]:
        raise NotImplementedError

    def decode(self, tokens: Iterable[int], **kwargs: Any) -> str:
        raise NotImplementedError

    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> List[List[int]]:
        raise NotImplementedError

    def save_pretrained(self, output_dir: str) -> None:
        raise NotImplementedError
