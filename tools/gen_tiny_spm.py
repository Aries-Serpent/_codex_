#!/usr/bin/env python3
"""Generate a tiny deterministic SentencePiece model."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import sentencepiece as spm

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "tests" / "assets"


def sha256(p: Path) -> str:
    """Return SHA256 hash of a file."""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    """Train model and write checksum."""
    inp = ASSETS / "corpus_tiny.txt"
    prefix = ASSETS / "spm_tiny"
    spm.SentencePieceTrainer.Train(
        input=str(inp),
        model_prefix=str(prefix),
        vocab_size=128,
        model_type="unigram",
        character_coverage=1.0,
        pad_id=0,
        bos_id=1,
        eos_id=2,
        unk_id=3,
        shuffle_input_sentence=False,
        input_sentence_size=0,
        hard_vocab_limit=False,
    )
    m = ASSETS / "spm_tiny.model"
    v = ASSETS / "spm_tiny.vocab"
    s = ASSETS / "spm_tiny.sha256"
    s.write_text(sha256(m) + "\n", encoding="utf-8")
    sys.stdout.write(f"wrote: {m} {v} {s}\n")


if __name__ == "__main__":
    main()
