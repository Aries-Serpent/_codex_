from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest


@pytest.fixture(autouse=True)
def _stub_tokenizers(monkeypatch):
    """Provide a lightweight tokenizers stub so imports succeed without deps."""

    if "tokenizers" in sys.modules:
        return

    stub = SimpleNamespace(
        SentencePieceUnigramTokenizer=lambda *args, **kwargs: None,
        Tokenizer=lambda *args, **kwargs: None,
        models=SimpleNamespace(BPE=lambda *args, **kwargs: None),
        normalizers=SimpleNamespace(NFKC=lambda: None),
        pre_tokenizers=SimpleNamespace(ByteLevel=lambda: None),
        trainers=SimpleNamespace(BpeTrainer=lambda **kwargs: None),
    )
    monkeypatch.setitem(sys.modules, "tokenizers", stub)


def test_train_tokenizer_no_corpus_raises(tmp_path):
    from tokenization.train_tokenizer import TrainTokenizerConfig, train

    cfg = TrainTokenizerConfig(
        corpus_glob=str(tmp_path / "missing" / "*.txt"),
        out_dir=str(tmp_path / "artifacts"),
        name="no-files",
    )
    with pytest.raises(FileNotFoundError, match="No training files found"):
        train(cfg)
