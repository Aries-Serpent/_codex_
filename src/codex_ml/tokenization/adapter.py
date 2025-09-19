"""Tokenizer adapter interfaces and implementations."""

from __future__ import annotations

import abc
import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

try:  # pragma: no cover - optional dependency
    import sentencepiece as spm  # type: ignore
except Exception as exc:  # pragma: no cover
    spm = None
    _SPM_IMPORT_ERROR = exc
else:  # pragma: no cover - import succeeded
    _SPM_IMPORT_ERROR = None


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
            model_path = (
                cfg.get("model_path")
                or cfg.get("model_file")
                or cfg.get("path")
                or cfg.get("model")
            )
            if not model_path:
                raise ValueError("SentencePieceTokenizer requires `model_path` in config")
            special_tokens = cfg.get("special_tokens")
            return SentencePieceTokenizer(model_path, special_tokens=special_tokens)
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
    """Tokenizer adapter that wraps ``sentencepiece`` models."""

    def __init__(
        self,
        model_or_processor: str | Path | "spm.SentencePieceProcessor",
        *,
        special_tokens: Optional[Sequence[str]] = None,
    ) -> None:
        if spm is None:  # pragma: no cover - import guard
            raise ImportError(
                "Install optional dependency `sentencepiece` to use SentencePieceTokenizer"
            ) from _SPM_IMPORT_ERROR

        from tokenization.sentencepiece_adapter import (
            SentencePieceAdapter as _LegacySentencePieceAdapter,
        )

        self.special_tokens: List[str] = list(special_tokens or [])
        self._adapter: Optional[_LegacySentencePieceAdapter]
        self._processor: "spm.SentencePieceProcessor"
        self.model_path: Optional[Path]

        if isinstance(model_or_processor, (str, Path)):
            self.model_path = Path(model_or_processor)
            self._adapter = _LegacySentencePieceAdapter(
                str(self.model_path), special_tokens=self.special_tokens or None
            )
            self._processor = self._adapter.sp
        elif spm is not None and isinstance(model_or_processor, spm.SentencePieceProcessor):
            self.model_path = None
            self._adapter = None
            self._processor = model_or_processor
        else:  # pragma: no cover - defensive
            raise TypeError(
                "model_or_processor must be a path to a .model file or a SentencePieceProcessor"
            )

    @classmethod
    def from_pretrained(cls, path_or_folder: str | Path) -> "SentencePieceTokenizer":
        path = Path(path_or_folder)
        special_tokens: Optional[Sequence[str]] = None
        if path.is_dir():
            specials_path = path / "special_tokens.json"
            if specials_path.exists():
                data = json.loads(specials_path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    special_tokens = [str(item) for item in data]
            model_candidates = sorted(path.glob("*.model"))
            if not model_candidates:
                raise FileNotFoundError(f"No SentencePiece .model file found in {path}")
            model_file = model_candidates[0]
        else:
            model_file = path
        return cls(model_file, special_tokens=special_tokens)

    def encode(
        self,
        text: str,
        *,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
        padding: Optional[str] = None,
    ) -> List[int]:
        ids = list(self._processor.EncodeAsIds(text))
        if truncation in ("only_first", "longest_first") and max_length:
            if len(ids) > max_length:
                ids = ids[:max_length]
        elif truncation == "only_second" and max_length:
            if len(ids) > max_length:
                ids = ids[-max_length:]

        if padding in (True, "longest", "max_length") and max_length:
            pad_id = (
                self._processor.pad_id()
                if hasattr(self._processor, "pad_id") and self._processor.pad_id() >= 0
                else 0
            )
            ids = ids[:max_length] + [pad_id] * max(0, max_length - len(ids))
        return ids

    def decode(self, tokens: Iterable[int], **_: Any) -> str:
        return self._processor.DecodeIds(list(tokens))

    def batch_encode(
        self,
        texts: Iterable[str],
        *,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
        padding: Optional[str] = None,
    ) -> List[List[int]]:
        return [
            self.encode(text, truncation=truncation, max_length=max_length, padding=padding)
            for text in texts
        ]

    def save_pretrained(self, output_dir: str) -> None:
        if spm is None:  # pragma: no cover - safety guard
            raise ImportError(
                "Install optional dependency `sentencepiece` to use SentencePieceTokenizer"
            ) from _SPM_IMPORT_ERROR

        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)

        if self.model_path and self.model_path.exists():
            dest = target / self.model_path.name
            shutil.copy2(self.model_path, dest)
            vocab_candidate = self.model_path.with_suffix(".vocab")
            if vocab_candidate.exists():
                shutil.copy2(vocab_candidate, target / vocab_candidate.name)
        else:
            dest = target / "sentencepiece.model"
            serialized = self._processor.serialized_model_proto()
            dest.write_bytes(serialized)

        if self.special_tokens:
            (target / "special_tokens.json").write_text(
                json.dumps(self.special_tokens, indent=2), encoding="utf-8"
            )
