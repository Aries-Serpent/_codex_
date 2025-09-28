import pathlib

import pytest

pytestmark = pytest.mark.requires_sentencepiece

sp = pytest.importorskip("sentencepiece")


def test_sp_fixture_roundtrip_if_present():
    """
    Use the tiny SentencePiece fixture for a strict encode/decode round-trip.
    If the fixture doesn't exist locally, skip with guidance.
    """

    root = pathlib.Path(__file__).resolve().parents[1]
    model = root / "fixtures" / "spm_toy.model"
    if not model.exists():
        pytest.skip("missing tests/fixtures/spm_toy.model; run: tools/make_spm_fixture.py")
    proc = sp.SentencePieceProcessor(model_file=str(model))
    text = "hello codex"
    ids = proc.encode(text, out_type=int)
    assert isinstance(ids, list) and ids, "encoding failed"
    dec = proc.decode(ids)
    assert isinstance(dec, str) and dec, "decoding failed"


# WHY: Round-trip check using the hermetic SP model.
# RISK: None; skip-safe if sentencepiece not installed.
# ROLLBACK: delete this file.
# TESTS: 'pytest -q tests/tokenization/test_sp_fixture_roundtrip.py'
