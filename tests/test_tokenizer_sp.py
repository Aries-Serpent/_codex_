import pathlib

import pytest

spm = pytest.importorskip("sentencepiece")  # noqa: F401

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
    assert pointer.exists()

    export_pointer = tmp_path / "export.pointer"
    tokenizer.save(str(export_pointer))
    assert export_pointer.exists()

    loaded = SPTokenizer.load(str(pointer))
    ids = loaded.encode("hello world", max_length=6, padding=True, truncation=True)
    assert isinstance(ids, list)
    assert len(ids) == 6

    decoded = loaded.decode(ids)
    assert isinstance(decoded, str)
    assert "hello" in decoded
