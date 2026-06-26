"""
Test Tokenizer Sp

Test module for tokenizer sp.
"""

import pathlib

import pytest

spm = pytest.importorskip("sentencepiece")

from codex_ml.tokenization.sp_trainer import SPTokenizer


def test_sentencepiece_trainer_roundtrip(tmp_path: pathlib.Path) -> None:
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\nhello codex\n", encoding="utf-8")

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
    corpus.write_text("determinism test", encoding="utf-8")

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
