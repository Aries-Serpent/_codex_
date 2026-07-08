"""
Test Train Tokenizer Smoke

Test module for train tokenizer smoke.
"""

import json

import pytest

pytest.importorskip("sentencepiece")
pytest.importorskip("sentencepiece")
from src.tokenization.train_tokenizer import TrainTokenizerConfig, train


def test_train_tokenizer_smoke(tmp_path):
    pytest.importorskip("sentencepiece")
    from tokenizers import Tokenizer

    corpus = tmp_path / "corpus.txt"
    corpus.write_text("hello world\n" * 5)
    cfg = TrainTokenizerConfig(
        corpus_glob=str(corpus),
        vocab_size=30,
        out_dir=str(tmp_path / "artifacts"),
        name="tok",
        seed=0,
        workers=1,
    )
    out = train(cfg)
    assert (out / "tokenizer.json").exists(), "Condition must be true"
    assert (out / "manifest.json").exists(), "Condition must be true"
    assert (out / "spm.model").exists(), "Condition must be true"
    assert (out / "spm.vocab").exists(), "Condition must be true"
    tok = Tokenizer.from_file(str(out / "tokenizer.json"))
    assert tok.get_vocab_size() <= cfg.vocab_size + 4, "Condition must be true"
    manifest = json.loads((out / "manifest.json").read_text())
    assert manifest.get("hash"), "Condition must be true"
