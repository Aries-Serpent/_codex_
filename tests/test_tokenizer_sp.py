"""
Test Tokenizer Sp

Test module for tokenizer sp.
"""

import pathlib

import pytest

spm = pytest.importorskip("sentencepiece")

from codex_ml.tokenization.sp_trainer import SPTokenizer

_SYLLABLES = ("ka", "lo", "mi", "nu", "pe", "ra", "si", "to", "vu", "ze")


def _corpus_text(*seed_lines: str) -> str:
    """Return ``seed_lines`` plus deterministic filler words.

    Real sentencepiece BPE refuses a ``vocab_size`` larger than the corpus can
    support ("Vocabulary size too high"), so a 1-2 line corpus cannot produce a
    64/128 piece model. 1000 synthetic three-syllable words give ample merges.
    """
    words = [a + b + c for a in _SYLLABLES for b in _SYLLABLES for c in _SYLLABLES]
    filler = [" ".join(words[i : i + 10]) for i in range(0, len(words), 10)]
    # Repeat the seed lines so their characters stay above the default
    # character_coverage cut-off (otherwise e.g. "h" would decode as <unk>).
    return "\n".join([*(list(seed_lines) * 50), *filler]) + "\n"


def test_sentencepiece_trainer_roundtrip(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(_corpus_text("hello world", "hello codex"), encoding="utf-8")

    tokenizer = SPTokenizer.train(
        input_files=[str(corpus)],
        vocab_size=128,
        output_dir=str(tmp_path / "tok"),
        seed=13,
    )

    pointer = tmp_path / "tok" / "tokenizer.pointer"
    assert pointer.exists(), "Condition must be true"

    export_pointer = tmp_path / "export.pointer"
    tokenizer.save(str(export_pointer))
    assert export_pointer.exists(), "exp is not valid"

    loaded = SPTokenizer.load(str(pointer))
    ids = loaded.encode("hello world", max_length=6, padding=True, truncation=True)
    assert isinstance(ids, list)
    assert len(ids) == 6, "Ids must not be empty"

    decoded = loaded.decode(ids)
    assert isinstance(decoded, str)
    assert "hello" in decoded, "Condition must be true"


def test_sentencepiece_trainer_reproducible(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text(_corpus_text("determinism test"), encoding="utf-8")

    tok_a = SPTokenizer.train(
        input_files=[str(corpus)],
        vocab_size=64,
        output_dir=str(tmp_path / "tok_a"),
        seed=7,
    )
    tok_b = SPTokenizer.train(
        input_files=[str(corpus)],
        vocab_size=64,
        output_dir=str(tmp_path / "tok_b"),
        seed=7,
    )

    model_a = (tmp_path / "tok_a" / "spm.model").read_bytes()
    model_b = (tmp_path / "tok_b" / "spm.model").read_bytes()
    assert model_a == model_b, "model_a is not valid"
    assert tok_a.decode(tok_a.encode("determinism")) == tok_b.decode(tok_b.encode("determinism"))
