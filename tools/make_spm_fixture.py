#!/usr/bin/env python
"""
Deterministically build a tiny SentencePiece model offline for tests.
Writes: tests/fixtures/spm_toy.model and spm_toy.vocab
Skips gracefully if sentencepiece is not installed.
"""
from __future__ import annotations

import pathlib
import random
import tempfile
import textwrap


def main():
    try:
        import sentencepiece as spm  # optional
    except Exception as exc:  # pragma: no cover
        print(f"[skip] sentencepiece unavailable: {exc}")
        return 0

    root = pathlib.Path(__file__).resolve().parents[1]
    out_dir = root / "tests" / "fixtures"
    out_dir.mkdir(parents=True, exist_ok=True)
    model_prefix = out_dir / "spm_toy"

    # Small synthetic corpus; deterministic content
    corpus = textwrap.dedent(
        """
        hello world
        hello codex
        sentencepiece tiny model
        tokenization invariants padding truncation
        reproducibility offline local file store
        """
    ).strip()
    with tempfile.NamedTemporaryFile("w", delete=False) as fh:
        fh.write(corpus)
        corpus_path = fh.name

    # Deterministic flags
    random.seed(0)
    # Train a tiny model (e.g., vocab_size=64) suitable for tests
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
    print(f"[ok] wrote {model_prefix}.model and .vocab")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


# WHY: Provide a tiny, offline SP model so tests are hermetic.
# RISK: None (tiny artifacts).
# ROLLBACK: delete this file and the generated fixtures.
# TESTS: 'python tools/make_spm_fixture.py' then run SP tests.
