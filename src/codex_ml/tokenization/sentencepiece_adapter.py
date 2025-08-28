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
except Exception as exc:  # pragma: no cover
    raise ImportError("sentencepiece not installed") from exc


class SentencePieceAdapter:
    """Lightweight adapter around a SentencePiece model."""

    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.sp = None

    def train_or_load(
        self,
        input_path: str | Path,
        vocab_size: int = 32000,
        character_coverage: float = 0.9995,
        model_type: str = "bpe",
    ) -> "SentencePieceAdapter":
        """Train a new model or load an existing one."""
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
        return self.load()

    def load(self) -> "SentencePieceAdapter":
        self.sp = spm.SentencePieceProcessor(model_file=str(self.model_path))
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
        vs = int(self.sp.vocab_size())
        if vs < min_size:
            raise AssertionError(f"vocab_size {vs} < min_size {min_size}")


# END: CODEX_SENTENCEPIECE_ADAPTER

