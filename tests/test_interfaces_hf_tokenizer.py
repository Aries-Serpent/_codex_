from codex_ml.interfaces.tokenizer import HFTokenizer


def test_round_trip():
    tok = HFTokenizer(
        "distilbert-base-uncased",
        padding=True,
        truncation=True,
        max_length=16,
    )
    text = "hello world"
    ids = tok.encode(text)
    decoded = tok.decode(ids)
    assert "hello" in decoded.lower()
    assert tok.pad_id >= 0 and tok.eos_id >= 0
