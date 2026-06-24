"""
Adapter Module

This module provides functionality for adapter.

Usage:
    from tokenization.adapter import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import abc  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import shutil  # noqa: E402
import warnings  # noqa: E402
from collections.abc import Iterable, Mapping, Sequence  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import (  # noqa: E402
    TYPE_CHECKING,
    Any,
    Optional,
)

from codex_ml.utils.hf_pinning import load_from_pretrained  # noqa: E402
from codex_ml.utils.hf_revision import get_hf_revision  # noqa: E402

spm = None
_SPM_IMPORT_ERROR: Exception | None = None


def _ensure_sentencepiece() -> bool:
    """Attempt to import ``sentencepiece`` lazily."""

    global spm, _SPM_IMPORT_ERROR
    if spm is not None:
        return True
    try:  # pragma: no cover - optional dependency
        import sentencepiece as _spm
    except (ImportError, AttributeError) as exc:  # pragma: no cover - dependency missing
        _SPM_IMPORT_ERROR = exc
        spm = None
        return False
    spm = _spm
    _SPM_IMPORT_ERROR = None
    return True


if TYPE_CHECKING:  # pragma: no cover - type checking only
    import sentencepiece as spm

    from .sentencepiece_adapter import SentencePieceAdapter as _SentencePieceAdapter


class TokenizerAdapter(abc.ABC):
    """Abstract base class for tokenizers used in training/eval."""

    @abc.abstractmethod
    def encode(self, text: str, **kwargs: Any) -> list[int]:
        """Encode ``text`` into token ids."""

    @abc.abstractmethod
    def decode(self, tokens: Iterable[int], **kwargs: Any) -> str:
        """Decode token ids back to string."""

    @abc.abstractmethod
    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> list[list[int]]:
        """Vectorised encoding for multiple strings."""

    @abc.abstractmethod
    def save_pretrained(self, output_dir: str) -> None:
        """Persist tokenizer to ``output_dir``."""

    @staticmethod
    def from_config(cfg: dict[str, Any]) -> TokenizerAdapter:
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
    special_tokens: Optional[dict[str, str]] = None

    def __post_init__(self) -> None:  # pragma: no cover - simple delegation
        try:
            from transformers import AutoTokenizer
        except (ImportError, AttributeError) as exc:  # pragma: no cover - transformers optional
            warnings.warn(
                f"transformers unavailable for HFTokenizerAdapter; falling back to WhitespaceTokenizer ({exc})",  # noqa: E501
                RuntimeWarning,
            )
            self.tokenizer = WhitespaceTokenizer()
            return

        params = {"use_fast": True}
        self.tokenizer = load_from_pretrained(
            AutoTokenizer,
            self.name_or_path,
            revision=get_hf_revision(),
            **params,
        )
        special = self.special_tokens or {}
        if special:
            self.tokenizer.add_special_tokens({"additional_special_tokens": list(special.values())})  # type: ignore[arg-type]
        if self.tokenizer.pad_token_id is None:  # type: ignore[attr-defined]
            self.tokenizer.add_special_tokens({"pad_token": "<pad>"})  # type: ignore[arg-type]  # nosec B105

    def encode(self, text: str, **kwargs: Any) -> list[int]:
        return self.tokenizer.encode(text, **kwargs)

    def decode(self, tokens: Iterable[int], **kwargs: Any) -> str:
        return self.tokenizer.decode(tokens, **kwargs)

    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> list[list[int]]:
        return self.tokenizer.batch_encode_plus(list(texts), **kwargs)["input_ids"]  # type: ignore[attr-defined]

    def save_pretrained(self, output_dir: str) -> None:
        self.tokenizer.save_pretrained(output_dir)

    def add_special_tokens(
        self, tokens: Sequence[str]
    ) -> dict[str, int]:  # pragma: no cover - thin wrapper
        added = self.tokenizer.add_special_tokens({"additional_special_tokens": list(tokens)})  # type: ignore[arg-type]
        mapping: dict[str, int] = {}
        if hasattr(self.tokenizer, "get_vocab"):
            vocab = self.tokenizer.get_vocab()
            for tok in tokens:
                if tok in vocab:
                    mapping[str(tok)] = int(vocab[tok])
        if not mapping and added:
            start = int(self.tokenizer.vocab_size) - added  # type: ignore[operator]
            mapping = {str(tok): start + idx for idx, tok in enumerate(tokens)}
        return mapping

    def save(self, path: Path) -> None:  # pragma: no cover - delegation
        self.save_pretrained(str(path))

    @property
    def vocab_size(self) -> int:
        return int(getattr(self.tokenizer, "vocab_size", 0))


class WhitespaceTokenizer(TokenizerAdapter):
    """Simple whitespace tokenizer primarily used for tests."""

    def __init__(self) -> None:
        self._special_tokens: list[str] = []
        self._dynamic_vocab: set[str] = set()

    def encode(self, text: str, **kwargs: Any) -> list[int]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        tokens = text.split()
        stable_ids: list[int] = []
        for tok in tokens:
            digest = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
            stable_ids.append(int.from_bytes(digest, "big") % (2**31))
            self._dynamic_vocab.add(tok)
        return stable_ids

    def decode(
        self, tokens: Iterable[int], **kwargs: Any
    ) -> str:  # pragma: no cover - lossy decode
        for tok in tokens:
            if not isinstance(tok, int):
                raise ValueError("tokens must be integers")
        return " ".join(str(t) for t in tokens)

    def batch_encode(self, texts: Iterable[str], **kwargs: Any) -> list[list[int]]:
        encoded: list[list[int]] = []
        for text in texts:
            if not isinstance(text, str):
                raise TypeError("batch_encode expects an iterable of strings")
            encoded.append(self.encode(text, **kwargs))
        return encoded

    def add_special_tokens(
        self, tokens: Sequence[str]
    ) -> dict[str, int]:  # pragma: no cover - simple mapping
        mapping: dict[str, int] = {}
        start = self.vocab_size
        for offset, tok in enumerate(tokens):
            mapping[str(tok)] = start + offset
        self._special_tokens.extend([str(tok) for tok in tokens])
        return mapping

    def save_pretrained(self, output_dir: str) -> None:  # pragma: no cover - trivial
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        (Path(output_dir) / "tokenizer.txt").write_text("whitespace", encoding="utf-8")

    def save(self, path: Path) -> None:  # pragma: no cover - trivial
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("whitespace", encoding="utf-8")
        else:
            self.save_pretrained(str(path))

    @property
    def vocab_size(self) -> int:
        return len(self._dynamic_vocab) + len(self._special_tokens)

    @property
    def name_or_path(self) -> str:
        return "whitespace-tokenizer"


class SentencePieceTokenizer(TokenizerAdapter):
    """Tokenizer adapter that wraps ``sentencepiece`` models."""

    def __init__(
        self,
        model_or_processor: str | Path | spm.SentencePieceProcessor,  # type: ignore[name-defined]
        *,
        special_tokens: Optional[Sequence[str] | Mapping[str, int]] = None,
    ) -> None:
        if not _ensure_sentencepiece():  # pragma: no cover - import guard
            raise ImportError(
                "Install optional dependency `sentencepiece` to use SentencePieceTokenizer"
            ) from _SPM_IMPORT_ERROR

        from .sentencepiece_adapter import SentencePieceAdapter

        tokens_to_add, provided_map = self._normalise_special_tokens(special_tokens)

        self.special_tokens: list[str] = []
        self.special_tokens_map: dict[str, int] = {}
        self._adapter: Optional[SentencePieceAdapter] = None
        self._processor: spm.SentencePieceProcessor  # type: ignore[name-defined]
        self.model_path: Optional[Path] = None
        self._special_tokens_path: Optional[Path] = None

        if isinstance(model_or_processor, (str, Path)):
            model_path = self._resolve_model_path(Path(model_or_processor))
            self._adapter = SentencePieceAdapter(model_path)
            self._adapter.load()
            if self._adapter.sp is None:  # pragma: no cover - defensive
                raise RuntimeError("SentencePieceAdapter failed to load the processor")
            self._processor = self._adapter.sp
            self.model_path = self._adapter.model_path
            (
                existing_map,
                legacy_tokens,
                special_tokens_path,
            ) = self._prepare_special_tokens_state(self._adapter)
            combined_existing = dict(existing_map)
            if provided_map:
                combined_existing.update(provided_map)
            schedule = self._combine_schedules(legacy_tokens, tokens_to_add)
            mapping = self._adapter.add_special_tokens(
                schedule,
                existing=combined_existing or None,
            )
            self.special_tokens_map = mapping
            self.special_tokens = self._ordered_special_tokens(mapping)
            self._special_tokens_path = getattr(
                self._adapter, "special_tokens_path", special_tokens_path
            )
        elif isinstance(model_or_processor, spm.SentencePieceProcessor):  # type: ignore[union-attr]
            self._init_from_processor(model_or_processor, tokens_to_add, provided_map)
        else:  # pragma: no cover - defensive
            raise TypeError(
                "model_or_processor must be a path, directory, or a SentencePieceProcessor"
            )

    @classmethod
    def from_pretrained(cls, path_or_folder: str | Path) -> SentencePieceTokenizer:
        path = Path(path_or_folder)
        model_file = cls._resolve_model_path(path)
        special_tokens = cls._discover_special_tokens(model_file)
        return cls(model_file, special_tokens=special_tokens)

    @staticmethod
    def _resolve_model_path(path: Path) -> Path:
        if path.is_dir():
            candidates = sorted(path.glob("*.model"))
            if not candidates:
                raise FileNotFoundError(f"No SentencePiece .model file found in {path}")
            return candidates[0]
        return path

    @staticmethod
    def _normalise_special_tokens(
        special_tokens: Optional[Sequence[str] | Mapping[str, int]],
    ) -> tuple[list[str], Optional[dict[str, int]]]:
        tokens: list[str] = []
        provided: Optional[dict[str, int]] = None
        if special_tokens is None:
            return tokens, provided
        if isinstance(special_tokens, Mapping):
            provided = {str(k): int(v) for k, v in special_tokens.items()}
            tokens = list(provided.keys())
            return tokens, provided
        if isinstance(special_tokens, (str, bytes)):
            raise TypeError(
                "SentencePieceTokenizer special_tokens must be a sequence of strings or a mapping"
            )
        tokens = [str(token) for token in special_tokens]
        return tokens, provided

    @staticmethod
    def _combine_schedules(*sequences: Sequence[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for seq in sequences:
            for token in seq:
                if token in seen:
                    continue
                seen.add(token)
                ordered.append(token)
        return ordered

    def _prepare_special_tokens_state(
        self, adapter: _SentencePieceAdapter
    ) -> tuple[dict[str, int], list[str], Path]:
        default_path = adapter.model_prefix.with_suffix(".special_tokens.json")
        existing_map: dict[str, int] = {}
        legacy_tokens: list[str] = []

        chosen_path = default_path
        if default_path.exists():
            mapping, legacy = self._read_special_tokens_file(default_path)
            existing_map.update(mapping)
            legacy_tokens.extend(legacy)

        alt_path = adapter.model_path.with_name("special_tokens.json")
        if alt_path.exists() and alt_path != default_path:
            mapping, legacy = self._read_special_tokens_file(alt_path)
            if mapping and not default_path.exists():
                chosen_path = alt_path
            for key, value in mapping.items():
                existing_map.setdefault(key, value)
            for token in legacy:
                if token not in existing_map and token not in legacy_tokens:
                    legacy_tokens.append(token)

        adapter.special_tokens_path = chosen_path  # type: ignore[has-type]
        self._special_tokens_path = chosen_path
        return existing_map, legacy_tokens, chosen_path

    @staticmethod
    def _read_special_tokens_file(path: Path) -> tuple[dict[str, int], list[str]]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid JSON in {path}") from exc

        if isinstance(data, dict):
            mapping: dict[str, int] = {}
            for key, value in data.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if isinstance(value, bool):
                    raise ValueError("special token ids must be integers")
                if not isinstance(value, int):
                    try:
                        value = int(value)
                    except (
                        TypeError,
                        ValueError,
                    ) as exc:  # pragma: no cover - defensive
                        raise ValueError("special token ids must be integers") from exc
                mapping[key] = int(value)
            return mapping, []
        if isinstance(data, list):
            tokens: list[str] = []
            for item in data:
                if not isinstance(item, str):
                    raise ValueError("special tokens must be strings")
                tokens.append(item)
            return {}, tokens
        raise ValueError("special tokens file must contain a mapping or list of strings")

    def _init_from_processor(
        self,
        processor: spm.SentencePieceProcessor,  # type: ignore[name-defined]
        tokens_to_add: Sequence[str],
        provided_map: Optional[dict[str, int]],
    ) -> None:
        self._processor = processor
        self._adapter = None
        self.model_path = None
        self._special_tokens_path = None
        mapping: dict[str, int] = dict(provided_map or {})
        next_id = self._processor_vocab_size(processor)
        used_ids = set(mapping.values())
        for token in tokens_to_add:
            if token in mapping:
                continue
            while next_id in used_ids:
                next_id += 1
            mapping[token] = next_id
            used_ids.add(next_id)
            next_id += 1
        self.special_tokens_map = mapping
        if mapping:
            self.special_tokens = self._ordered_special_tokens(mapping)
        else:
            self.special_tokens = list(tokens_to_add)

    @staticmethod
    def _ordered_special_tokens(mapping: dict[str, int]) -> list[str]:
        return [token for token, _ in sorted(mapping.items(), key=lambda item: item[1])]

    @staticmethod
    def _processor_vocab_size(processor: spm.SentencePieceProcessor) -> int:  # type: ignore[name-defined]
        for attr in ("get_piece_size", "piece_size", "vocab_size"):
            getter = getattr(processor, attr, None)
            if callable(getter):
                try:
                    value = getter()
                except TypeError:  # pragma: no cover - defensive
                    continue
                try:
                    return int(value)
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    continue
        return 0

    @staticmethod
    def _discover_special_tokens(
        model_file: Path,
    ) -> Optional[Sequence[str] | Mapping[str, int]]:
        default_path = model_file.with_suffix(".special_tokens.json")
        alt_path = model_file.with_name("special_tokens.json")
        for candidate in (default_path, alt_path):
            if not candidate.exists():
                continue
            mapping, legacy = SentencePieceTokenizer._read_special_tokens_file(candidate)
            if mapping:
                return mapping
            if legacy:
                return legacy
        return None

    def encode(  # type: ignore[override]
        self,
        text: str,
        *,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
        padding: Optional[str] = None,
    ) -> list[int]:
        encode_fn = getattr(self._processor, "encode", None)
        if callable(encode_fn):
            ids = list(encode_fn(text, out_type=int))
        else:  # pragma: no cover - compatibility fallback
            ids = list(self._processor.EncodeAsIds(text))
        if truncation in ("only_first", "longest_first") and max_length:
            if len(ids) > max_length:
                ids = ids[:max_length]
        elif truncation == "only_second" and max_length and len(ids) > max_length:
            ids = ids[-max_length:]

        if padding in (True, "longest", "max_length") and max_length:
            pad_id = self._infer_pad_id()
            ids = ids[:max_length] + [pad_id] * max(0, max_length - len(ids))
        return ids

    def _infer_pad_id(self) -> int:
        pad_getters = ("pad_id",)
        for attr in pad_getters:
            getter = getattr(self._processor, attr, None)
            if callable(getter):
                try:
                    value = getter()
                except TypeError:  # pragma: no cover - defensive
                    continue
                if isinstance(value, int) and value >= 0:
                    return value
        return 0

    def decode(self, tokens: Iterable[int], **_: Any) -> str:
        decode_fn = getattr(self._processor, "decode", None)
        if callable(decode_fn):
            return decode_fn(list(tokens))
        return self._processor.DecodeIds(list(tokens))

    def batch_encode(  # type: ignore[override]
        self,
        texts: Iterable[str],
        *,
        truncation: Optional[str] = None,
        max_length: Optional[int] = None,
        padding: Optional[str] = None,
    ) -> list[list[int]]:
        return [
            self.encode(text, truncation=truncation, max_length=max_length, padding=padding)
            for text in texts
        ]

    def save_pretrained(self, output_dir: str) -> None:
        if not _ensure_sentencepiece():  # pragma: no cover - safety guard
            raise ImportError(
                "Install optional dependency `sentencepiece` to use SentencePieceTokenizer"
            ) from _SPM_IMPORT_ERROR

        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)

        if self.model_path and self.model_path.exists():
            artifacts = [self.model_path]
            vocab_candidate = self.model_path.with_suffix(".vocab")
            if vocab_candidate.exists():
                artifacts.append(vocab_candidate)
            for artifact in artifacts:
                shutil.copy2(artifact, target / artifact.name)
            specials = self._special_tokens_path
            if specials and specials.exists():
                shutil.copy2(specials, target / specials.name)
            elif self.special_tokens_map:
                dest = target / (self.model_path.with_suffix(".special_tokens.json").name)
                dest.write_text(
                    json.dumps(self.special_tokens_map, indent=2, sort_keys=True),
                    encoding="utf-8",
                )
        else:
            dest = target / "sentencepiece.model"
            serialized = self._processor.serialized_model_proto()
            dest.write_bytes(serialized)
            if self.special_tokens_map:
                specials_path = dest.with_suffix(".special_tokens.json")
                specials_path.write_text(
                    json.dumps(self.special_tokens_map, indent=2, sort_keys=True),
                    encoding="utf-8",
                )
            elif self.special_tokens:
                fallback = target / "special_tokens.json"
                fallback.write_text(json.dumps(self.special_tokens, indent=2), encoding="utf-8")

    def save(self, path: Path) -> None:  # pragma: no cover - compatibility wrapper
        self.save_pretrained(str(path))

    @property
    def vocab_size(self) -> int:
        return self._processor_vocab_size(self._processor)

    @property
    def name_or_path(self) -> str:
        return str(self.model_path or "sentencepiece-tokenizer")
