from __future__ import annotations

from codex_ml.interfaces.tokenizer import HFTokenizer


def test_round_trip():
    tok = HFTokenizer(
        "hf-internal-testing/tiny-random-bert",
        padding=True,
        truncation=True,
        max_length=16,
    )
    text = "hello world"
    ids = tok.encode(text)
    decoded = tok.decode(ids)
    assert "hello" in decoded.lower()

    # Backward compatibility: both legacy and new properties are validated.
    # - pad_id/eos_id are integer aliases (legacy)
    # - pad_token_id may be None depending on tokenizer (newer property)
    assert tok.pad_id >= 0 and tok.eos_id >= 0
    assert tok.pad_token_id is None or tok.pad_token_id >= 0
