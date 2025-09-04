import os

import pytest

from src.tokenization.sentencepiece_adapter import SentencePieceAdapter

spm = pytest.importorskip("sentencepiece")


def test_padding_truncation_roundtrip(tmp_path):
    # tiny toy model (shipped via test assets or generated ahead of time)
    model = os.environ.get("SPM_TINY_MODEL")
    if not model or not os.path.exists(model):
        pytest.skip("SPM_TINY_MODEL not provided")
    tok = SentencePieceAdapter(model_path=model)
    ids = tok.encode("hello world", padding="max_length", truncation="only_first", max_length=8)
    assert len(ids) == 8
    text = tok.decode(ids)
    assert isinstance(text, str)
