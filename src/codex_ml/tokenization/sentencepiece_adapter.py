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

try:
    import sentencepiece as spm  # type: ignore
except Exception:
    spm = None  # type: ignore


class SentencePieceAdapter:
    """Lightweight adapter around a SentencePiece model."""

    def __init__(self, model_path: Path):
        self.model_path = Path(model_path)
        self.sp = None

    def train_or_load(
        self, input_path: Path, vocab_size: int = 32000, model_type: str = "bpe"
    ):
        if self.model_path.exists():
            return self.load()
        if spm is None:
            raise RuntimeError("sentencepiece not installed")
        spm.SentencePieceTrainer.Train(
            input=str(input_path),
            model_prefix=str(self.model_path.with_suffix("")),
            vocab_size=vocab_size,
            model_type=model_type,
            character_coverage=0.9995,
            pad_id=0,
            unk_id=1,
            bos_id=2,
            eos_id=3,
        )
        return self.load()

    def load(self):
        if spm is None:
            raise RuntimeError("sentencepiece not installed")
        self.sp = spm.SentencePieceProcessor(model_file=str(self.model_path))
        return self

    def add_special_tokens(self, tokens: list[str]) -> None:
        sidecar = self.model_path.with_suffix(".specials.json")
        sidecar.write_text(json.dumps(tokens, indent=2), encoding="utf-8")

    def assert_vocab_size(self, expected: int) -> None:
        if self.sp is None:
            raise RuntimeError("adapter not loaded")
        vs = int(self.sp.vocab_size())
        if vs != expected:
            raise AssertionError(f"vocab_size {vs} != expected {expected}")


# END: CODEX_SENTENCEPIECE_ADAPTER
