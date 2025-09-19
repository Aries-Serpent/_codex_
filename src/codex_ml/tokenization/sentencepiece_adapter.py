# BEGIN: CODEX_SENTENCEPIECE_ADAPTER
"""Thin wrapper around `sentencepiece` with minimal conveniences.

The adapter can train a tiny model or load an existing one and stores
additional special tokens in a ``.specials.json`` sidecar.  It purposefully
avoids heavy dependencies and therefore expects the caller to have the
``sentencepiece`` package installed.  A small example::

    adapter = SentencePieceAdapter(Path("toy.model"))
    adapter.train_or_load(Path("corpus.txt"), vocab_size=100)
    adapter.add_special_tokens(["<pad>", "<bos>"])

"""
from __future__ import annotations

import json
import numbers
import os
from pathlib import Path
from typing import Dict, Optional, Sequence

spm = None  # type: ignore[assignment]


def _get_sentencepiece():
    """Return the ``sentencepiece`` module or raise ``ImportError``."""

    global spm
    if spm is not None:
        return spm
    try:  # pragma: no cover - optional dependency
        import sentencepiece as sentencepiece_module  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency missing
        spm = None
        raise ImportError("sentencepiece not installed") from exc
    spm = sentencepiece_module
    return sentencepiece_module


class SentencePieceAdapter:
    """Lightweight adapter around a SentencePiece model."""

    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.sp = None

    @property
    def model_prefix(self) -> Path:
        """Return the model prefix without the ``.model`` suffix."""
        return self.model_path.with_suffix("")

    @model_prefix.setter
    def model_prefix(self, value: str | Path) -> None:
        """Set the model prefix, updating ``model_path`` accordingly."""
        self.model_path = Path(value).with_suffix(".model")

    def train_or_load(
        self,
        input_path: str | Path,
        vocab_size: int = 32000,
        character_coverage: float = 0.9995,
        model_type: str = "bpe",
    ) -> "SentencePieceAdapter":
        """Train a new model or load an existing one."""
        module = _get_sentencepiece()
        if self.model_path.exists():
            return self.load()
        module.SentencePieceTrainer.train(
            input=str(input_path),
            model_prefix=str(self.model_prefix),
            vocab_size=vocab_size,
            character_coverage=character_coverage,
            model_type=model_type,
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
        )
        self._trained_vocab_size = vocab_size
        return self.load()

    def load(self) -> "SentencePieceAdapter":
        module = _get_sentencepiece()
        cls = module.SentencePieceProcessor
        try:
            proc = cls(model_file=str(self.model_path))
        except TypeError:
            proc = cls()
            loader = getattr(proc, "Load", None) or getattr(proc, "load", None)
            if loader is None:  # pragma: no cover - defensive
                raise AttributeError("SentencePieceProcessor missing Load/load")
            loader(str(self.model_path))
        self.sp = proc
        return self

    def encode(self, text: str) -> list[int]:
        if self.sp is None:
            raise RuntimeError("adapter not loaded")
        return list(self.sp.encode(text, out_type=int))

    def decode(self, ids: list[int] | tuple[int, ...]) -> str:
        if self.sp is None:
            raise RuntimeError("adapter not loaded")
        return self.sp.decode(ids)

    def add_special_tokens(
        self, tokens: Sequence[str], existing: Optional[Dict[str, int]] = None
    ) -> Dict[str, int]:
        if isinstance(tokens, (str, bytes)):
            raise ValueError("tokens must be a sequence of strings")

        normalised_tokens: list[str] = []
        for tok in tokens:
            if not isinstance(tok, str):
                raise ValueError("special tokens must be strings")
            if not tok:
                raise ValueError("special tokens must be non-empty strings")
            normalised_tokens.append(tok)

        if getattr(self, "sp", None) is None:
            self.load()
        if self.sp is None:  # pragma: no cover - defensive
            raise RuntimeError("adapter not loaded")

        size_getters = (
            "get_piece_size",
            "GetPieceSize",
            "piece_size",
            "vocab_size",
        )
        piece_size: Optional[int] = None
        for attr in size_getters:
            getter = getattr(self.sp, attr, None)
            if callable(getter):
                piece_size = int(getter())
                break
        if piece_size is None:
            raise AttributeError("SentencePieceProcessor missing piece size accessor")

        special_path = Path(
            getattr(
                self,
                "special_tokens_path",
                self.model_prefix.with_suffix(".special_tokens.json"),
            )
        )
        special_path.parent.mkdir(parents=True, exist_ok=True)

        legacy_tokens: list[str] = []
        legacy_seen: set[str] = set()

        def _record_legacy(token: str) -> None:
            if not isinstance(token, str):
                raise ValueError("special tokens must be strings")
            if not token:
                raise ValueError("special tokens must be non-empty strings")
            if token not in legacy_seen:
                legacy_seen.add(token)
                legacy_tokens.append(token)

        on_disk: Dict[str, int] = {}
        if special_path.exists():
            try:
                raw = json.loads(special_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive
                raise ValueError(f"Invalid JSON in special tokens file: {special_path}") from exc
            if not isinstance(raw, dict):
                raise ValueError("special tokens file must contain a mapping")
            for key, value in raw.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if isinstance(value, numbers.Integral):
                    on_disk[key] = int(value)
                    continue
                if isinstance(value, str):
                    _record_legacy(value)
                    continue
                raise ValueError("special token ids must be integers")

        provided: Dict[str, int] = {}
        if existing:
            for key, value in existing.items():
                if not isinstance(key, str):
                    raise ValueError("special token keys must be strings")
                if isinstance(value, numbers.Integral):
                    provided[key] = int(value)
                    continue
                if isinstance(value, str):
                    _record_legacy(value)
                    continue
                raise ValueError("special token ids must be integers")

        merged: Dict[str, int] = dict(on_disk)
        merged.update(provided)

        id_to_token: Dict[int, str] = {}
        for token, idx in merged.items():
            if idx in id_to_token and id_to_token[idx] != token:
                raise ValueError(
                    f"special token id collision for {token!r} and {id_to_token[idx]!r}"
                )
            id_to_token[idx] = token

        used_ids = set(merged.values())
        if used_ids:
            next_id = max(piece_size, max(used_ids) + 1)
        else:
            next_id = piece_size

        scheduled: list[str] = []
        scheduled_set: set[str] = set()

        for token in legacy_tokens:
            if token in merged or token in scheduled_set:
                continue
            scheduled.append(token)
            scheduled_set.add(token)

        for token in normalised_tokens:
            if token in merged or token in scheduled_set:
                continue
            scheduled.append(token)
            scheduled_set.add(token)

        for token in scheduled:
            while next_id in used_ids:
                next_id += 1
            merged[token] = next_id
            used_ids.add(next_id)
            next_id += 1

        serialised = json.dumps(merged, indent=2, sort_keys=True)
        tmp_path = special_path.with_suffix(special_path.suffix + ".tmp")
        tmp_path.write_text(serialised, encoding="utf-8")
        os.replace(tmp_path, special_path)

        self.special_tokens_map = dict(merged)
        self.special_tokens_path = special_path
        return dict(merged)

    def assert_vocab_size(self, min_size: int) -> None:
        if self.sp is None:
            raise RuntimeError("adapter not loaded")
        if hasattr(self.sp, "vocab_size"):
            vs = int(self.sp.vocab_size())
        elif hasattr(self, "_trained_vocab_size"):
            vs = int(self._trained_vocab_size)
        else:  # pragma: no cover - defensive
            raise AttributeError("vocab_size unavailable")
        if vs < min_size:
            raise AssertionError(f"vocab_size {vs} < min_size {min_size}")


# END: CODEX_SENTENCEPIECE_ADAPTER
