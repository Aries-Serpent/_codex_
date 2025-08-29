from interfaces.tokenizer import HFTokenizer


def test_encode_decode_roundtrip():
    tk = HFTokenizer("distilbert-base-uncased", padding=False, truncation=False)
    text = "hello world"
    encoded = tk.encode(text)["input_ids"][0].tolist()
    decoded = tk.decode(encoded)
    assert text == decoded.strip()
    assert isinstance(tk.pad_id, int) and isinstance(tk.eos_id, int)
    assert isinstance(tk.vocab_size, int) and tk.vocab_size > 0
