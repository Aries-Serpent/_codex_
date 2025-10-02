from __future__ import annotations

import json
import numbers
import os
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Optional, Sequence

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
        self.special_tokens_map: dict[str, int] = {}
        if self.model_path.exists():
            self.load()
        else:
            self._load_special_tokens()

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
        self._load_special_tokens()
        if self.special_tokens:
            missing = [tok for tok in self.special_tokens if tok not in self.special_tokens_map]
            if missing:
                self.add_special_tokens(missing)
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
        ids = self._encode_ids(text)

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

    def add_special_tokens(
        self,
        tokens: Sequence[str],
        *,
        existing: Optional[Mapping[str, int | str]] = None,
    ) -> dict[str, int]:
        if isinstance(tokens, (str, bytes)):
            raise ValueError("tokens must be a sequence of strings")

        normalised: list[str] = []
        for token in tokens:
            if not isinstance(token, str):
                raise ValueError("special tokens must be strings")
            if not token:
                raise ValueError("special tokens must be non-empty strings")
            normalised.append(token)

        processor = self._ensure_processor()
        if processor is None:  # pragma: no cover - defensive
            raise RuntimeError("SentencePieceProcessor failed to load")

        mapping = dict(self.special_tokens_map)
        scheduled: list[str] = []
        scheduled_set: set[str] = set()

        def _schedule(token: str) -> None:
            if token in mapping or token in scheduled_set:
                return
            if not isinstance(token, str):
                raise ValueError("special tokens must be strings")
            if not token:
                raise ValueError("special tokens must be non-empty strings")
            scheduled.append(token)
            scheduled_set.add(token)

        for token in normalised:
            _schedule(token)

        if existing:
            for key, value in existing.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if isinstance(value, numbers.Integral):
                    mapping[key] = int(value)
                elif isinstance(value, str):
                    _schedule(value)
                else:
                    raise ValueError("special token ids must be integers or strings")

        for token in self.special_tokens:
            _schedule(token)

        special_path = self._special_tokens_path()
        on_disk = self._load_special_tokens()
        if on_disk:
            mapping.update(on_disk)

        used_ids = set(mapping.values())
        next_id = max(self._vocab_size(processor), (max(used_ids) + 1) if used_ids else 0)

        for token in scheduled:
            while next_id in used_ids:
                next_id += 1
            mapping[token] = next_id
            used_ids.add(next_id)
            next_id += 1

        serialised = json.dumps(mapping, indent=2, sort_keys=True)
        special_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = special_path.with_suffix(special_path.suffix + ".tmp")
        tmp_path.write_text(serialised, encoding="utf-8")
        os.replace(tmp_path, special_path)

        self.special_tokens_map = dict(mapping)
        return dict(mapping)

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

    def _special_tokens_path(self) -> Path:
        return self.model_path.with_suffix(".special_tokens.json")

    def _load_special_tokens(self) -> dict[str, int]:
        mapping: dict[str, int] = {}
        path = self._special_tokens_path()
        if path.exists():
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("special tokens file must contain a mapping")
            for key, value in raw.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if not isinstance(value, numbers.Integral):
                    raise ValueError("special token ids must be integers")
                mapping[key] = int(value)
        self.special_tokens_map = mapping
        return dict(mapping)

    def _vocab_size(self, processor: Any) -> int:
        getters = (
            "vocab_size",
            "get_piece_size",
            "piece_size",
            "GetPieceSize",
        )
        for attr in getters:
            getter = getattr(processor, attr, None)
            if callable(getter):
                size = getter()
                if isinstance(size, numbers.Integral):
                    return int(size)
                try:
                    return int(size)
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    continue
        return 0


__all__ = ["SentencePieceAdapter"]
