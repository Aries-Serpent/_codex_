from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = [pytest.mark.tokenizer, pytest.mark.requires_sentencepiece]

sp = pytest.importorskip("sentencepiece")


def test_sp_fixture_roundtrip_if_present():
    root = Path(__file__).resolve().parents[1]
    model = root / "fixtures" / "spm_toy.model"
    if not model.exists():
        pytest.skip("missing tests/fixtures/spm_toy.model; run: python tools/make_spm_fixture.py")
    proc = sp.SentencePieceProcessor(model_file=str(model))
    text = "hello codex"
    ids = proc.encode(text, out_type=int)
    assert isinstance(ids, list) and ids, "encoding failed"
    decoded = proc.decode(ids)
    assert isinstance(decoded, str) and decoded, "decoding failed"
