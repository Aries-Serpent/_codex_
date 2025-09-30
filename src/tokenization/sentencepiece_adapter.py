from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    import sentencepiece as spm
except Exception as exc:  # pragma: no cover
    spm = None
    _SPM_ERROR = exc
else:  # pragma: no cover - import succeeded
    _SPM_ERROR = None


class SentencePieceAdapter:
    """Minimal SentencePiece wrapper with convenience helpers."""

    def __init__(self, model_path: str | Path, special_tokens: Optional[List[str]] = None) -> None:
        self.model_path = Path(model_path)
        if spm is None:
            raise ImportError("sentencepiece is not installed") from _SPM_ERROR
        self.special_tokens = list(special_tokens or [])
        self.sp = None
        if self.model_path.exists():
            self.load()

    # ------------------------------------------------------------------
    # Loading & training helpers
    # ------------------------------------------------------------------
    def load(self) -> "SentencePieceAdapter":
        """Load the sentencepiece model from disk."""

        if not self.model_path.exists():
            raise FileNotFoundError(f"SentencePiece model missing: {self.model_path}")

        processor_cls = getattr(spm, "SentencePieceProcessor", None)
        if processor_cls is None:  # pragma: no cover - defensive
            raise AttributeError("sentencepiece missing SentencePieceProcessor")

        try:
            processor = processor_cls(model_file=str(self.model_path))
        except TypeError:
            processor = processor_cls()
            loader = getattr(processor, "Load", None) or getattr(processor, "load", None)
            if loader is None:  # pragma: no cover - defensive
                raise AttributeError("SentencePieceProcessor missing Load/load method")
            loader(str(self.model_path))

        self.sp = processor
        return self

    def train_or_load(
        self,
        corpus_path: str | Path,
        *,
        vocab_size: int = 32000,
        character_coverage: float = 0.9995,
        model_type: str = "bpe",
        trainer_kwargs: Optional[dict[str, Any]] = None,
    ) -> "SentencePieceAdapter":
        """Train the model if required and load it."""

        if self.model_path.exists():
            return self.load()

        trainer = getattr(spm, "SentencePieceTrainer", None)
        if trainer is None:  # pragma: no cover - optional dependency guard
            raise AttributeError("sentencepiece missing SentencePieceTrainer")

        train_fn = getattr(trainer, "Train", None) or getattr(trainer, "train", None)
        if train_fn is None:  # pragma: no cover - defensive
            raise AttributeError("SentencePieceTrainer missing Train/train method")

        prefix = self.model_path.with_suffix("")
        prefix.parent.mkdir(parents=True, exist_ok=True)
        params: dict[str, Any] = {
            "input": str(corpus_path),
            "model_prefix": str(prefix),
            "vocab_size": vocab_size,
            "character_coverage": character_coverage,
            "model_type": model_type,
        }
        if trainer_kwargs:
            params.update(trainer_kwargs)

        train_fn(**params)
        return self.load()

    def _ensure_processor(self):
        if self.sp is None:
            return self.load().sp
        return self.sp

    def encode(
        self,
        text: str,
        *,
        padding: Optional[str] = None,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> List[int]:
        ids = list(self._encode_ids(text))

        if truncation in ("only_first", "longest_first") and max_length:
            if len(ids) > max_length:
                # NOTE: this preserves the leading tokens for single sequence inputs.
                # Pair-handling logic should be added alongside two-sequence support.
                ids = ids[:max_length]
        elif truncation == "only_second" and max_length:
            if len(ids) > max_length:
                ids = ids[-max_length:]
        if padding in (True, "longest", "max_length") and max_length:
            ids = ids[:max_length] + [self._pad_id()] * max(0, max_length - len(ids))
        return ids

    def batch_encode(
        self,
        texts: Iterable[str],
        *,
        padding: Optional[str] = None,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> List[List[int]]:
        return [
            self.encode(
                text,
                padding=padding,
                truncation=truncation,
                max_length=max_length,
            )
            for text in texts
        ]

    def decode(self, ids: Iterable[int]) -> str:
        return self._decode_ids(list(ids))

    def _encode_ids(self, text: str) -> List[int]:
        processor = self._ensure_processor()
        if processor is None:  # pragma: no cover - defensive
            raise RuntimeError("SentencePieceProcessor failed to load")

        encode = getattr(processor, "encode", None)
        if callable(encode):
            try:
                return list(encode(text, out_type=int))
            except TypeError:
                return list(encode(text))
        fallback = getattr(processor, "EncodeAsIds", None)
        if fallback is None:  # pragma: no cover - defensive
            raise AttributeError("SentencePieceProcessor missing encode/EncodeAsIds")
        return list(fallback(text))

    def _decode_ids(self, ids: List[int]) -> str:
        processor = self._ensure_processor()
        if processor is None:  # pragma: no cover - defensive
            raise RuntimeError("SentencePieceProcessor failed to load")

        decode = getattr(processor, "decode", None)
        if callable(decode):
            return decode(ids)
        fallback = getattr(processor, "DecodeIds", None)
        if fallback is None:  # pragma: no cover - defensive
            raise AttributeError("SentencePieceProcessor missing decode/DecodeIds")
        return fallback(ids)

    def _pad_id(self) -> int:
        processor = self._ensure_processor()
        if processor is None:  # pragma: no cover - defensive
            raise RuntimeError("SentencePieceProcessor failed to load")

        pad_method = getattr(processor, "pad_id", None)
        if callable(pad_method):
            try:
                value = pad_method()
            except TypeError:  # pragma: no cover - defensive
                value = None
            if isinstance(value, int) and value >= 0:
                return value
        return 0


__all__ = ["SentencePieceAdapter"]
