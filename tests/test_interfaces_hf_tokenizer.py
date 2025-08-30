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
    assert tok.pad_token_id is None or tok.pad_token_id >= 0
