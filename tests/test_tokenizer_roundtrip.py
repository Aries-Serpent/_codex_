from interfaces.tokenizer import HFTokenizer


def test_encode_decode_roundtrip():
    tk = HFTokenizer("distilbert-base-uncased", padding=False, truncation=False)
    text = "hello world"
    ids = tk.batch_encode([text])[0]
    decoded = tk.decode(ids)
    assert text == decoded.strip()
    assert isinstance(tk.pad_id, int) and isinstance(tk.eos_id, int)
    assert isinstance(tk.vocab_size, int) and tk.vocab_size > 0
