"""Tests for tokenizer utilities."""

import pytest

from codex_ml.interfaces.tokenizer import HFTokenizer
from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter
from tokenization.train_tokenizer import TrainTokenizerConfig, train


@pytest.mark.tokenizer
def test_encode_decode_round_trip():
    tok = HFTokenizerAdapter("bert-base-uncased")
    text = "Hello world!"
    ids = tok.encode(text)
    assert isinstance(ids, list) and ids
    decoded = tok.decode(ids)
    assert "hello" in decoded.lower()


def test_tokenizer_basic(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("Run pre-commit --all-files now.\n")
    cfg = TrainTokenizerConfig(corpus_glob=str(corpus), vocab_size=20, out_dir=str(tmp_path))
    out = train(cfg)
    tk = HFTokenizer(name_or_path=None, artifacts_dir=str(out))
    toks = tk.encode("Run pre-commit --all-files now.")
    assert isinstance(toks, list)
    assert len(toks) > 0
