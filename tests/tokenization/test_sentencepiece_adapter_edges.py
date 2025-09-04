from pathlib import Path
import shutil

import pytest

from src.tokenization.sentencepiece_adapter import SentencePieceAdapter

spm = pytest.importorskip("sentencepiece")


# ruff: noqa
def test_padding_truncation_roundtrip(tmp_path):
    model_src = Path(__file__).resolve().parents[1] / "assets" / "spm_tiny.model.temp"
    assert (
        model_src.exists()
    ), "Missing spm_tiny.model.temp; run tools/gen_tiny_spm.py and commit artifacts."
    model = tmp_path / "spm_tiny.model"
    shutil.copyfile(model_src, model)
    tok = SentencePieceAdapter(model_path=model)
    ids = tok.encode("hello world", padding="max_length", truncation="only_first", max_length=8)
    assert len(ids) == 8
    text = tok.decode(ids)
    assert isinstance(text, str)
