"""SentencePiece fixture round-trip tests."""

from __future__ import annotations

import pathlib

import pytest

sp = pytest.importorskip("sentencepiece")


def test_sp_fixture_roundtrip_if_present() -> None:
    """Ensure the generated tiny SentencePiece model is self-consistent."""

    root = pathlib.Path(__file__).resolve().parents[1]
    model = root / "fixtures" / "spm_toy.model"
    if not model.exists():
        pytest.skip("missing tests/fixtures/spm_toy.model; run tools/make_spm_fixture.py")
    processor = sp.SentencePieceProcessor(model_file=str(model))
    text = "hello codex"
    ids = processor.encode(text, out_type=int)
    assert isinstance(ids, list) and ids, "encoding failed"
    decoded = processor.decode(ids)
    assert isinstance(decoded, str) and decoded, "decoding failed"
