"""
Test Encode Decode Roundtrip

Test module for encode decode roundtrip.
"""

import pytest

pytest.importorskip("sentencepiece")

from codex_ml.interfaces.tokenizer import HFTokenizer
from src.tokenization.train_tokenizer import TrainTokenizerConfig, train


def test_encode_decode_roundtrip(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\n" * 3)
    cfg = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=20,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        seed=123,
        workers=1,
    )
    out = train(cfg)
    tk = HFTokenizer(
        name_or_path=None,
        artifacts_dir=str(out),
        padding="max_length",
        truncation=True,
        max_length=5,
    )
    ids1 = tk.encode("hello world")
    ids2 = tk.encode("hello world")
    assert ids1 == ids2, "ids1 is not valid"
    assert len(ids1) == 5, "Ids1 must not be empty"
    text = tk.decode(ids1, skip_special_tokens=False)
    assert "hello" in text, "Condition must be true"
