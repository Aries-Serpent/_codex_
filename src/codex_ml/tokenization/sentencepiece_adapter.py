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
from pathlib import Path

try:  # pragma: no cover - exercised in tests
    import sentencepiece as spm  # type: ignore
except Exception:  # pragma: no cover
    spm = None


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
        if spm is None:
            raise ImportError("sentencepiece not installed")
        if self.model_path.exists():
            return self.load()
        spm.SentencePieceTrainer.train(
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
        if spm is None:
            raise ImportError("sentencepiece not installed")
        cls = spm.SentencePieceProcessor
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

    def add_special_tokens(self, tokens: dict[str, str]) -> None:
        sidecar = self.model_prefix.with_suffix(".special_tokens.json")
        sidecar.write_text(json.dumps(tokens, indent=2), encoding="utf-8")

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
