#!/usr/bin/env python
"""Build a tiny SentencePiece model fixture for offline tests."""

from __future__ import annotations

import pathlib
import random
import tempfile
import textwrap
from typing import Final


def main() -> int:
    try:
        import sentencepiece as spm  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - optional dependency
        print(f"[skip] sentencepiece unavailable: {exc}")
        return 0

    root = pathlib.Path(__file__).resolve().parents[1]
    out_dir = root / "tests" / "fixtures"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_prefix = out_dir / "spm_toy"

    corpus: Final[str] = textwrap.dedent(
        """
        hello world
        hello codex
        sentencepiece tiny model
        tokenization invariants padding truncation
        reproducibility offline local file store
        """
    ).strip()

    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as fh:
        fh.write(corpus)
        corpus_path = fh.name

    random.seed(0)
    spm.SentencePieceTrainer.Train(
        input=corpus_path,
        model_prefix=str(model_prefix),
        vocab_size=64,
        character_coverage=1.0,
        model_type="unigram",
        input_sentence_size=1000,
        shuffle_input_sentence=False,
        train_extremely_large_corpus=False,
    )
    print(f"[ok] wrote {model_prefix}.model and {model_prefix}.vocab")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
