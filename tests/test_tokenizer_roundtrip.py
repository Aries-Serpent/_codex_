from codex_ml.interfaces.tokenizer import HFTokenizer


def test_encode_decode_roundtrip():
    tk = HFTokenizer("hf-internal-testing/tiny-random-bert", padding=False, truncation=False)
    text = "hello world"
    encoded = tk.encode(text)
    decoded = tk.decode(encoded)
    assert text == decoded.strip()
    assert tk.pad_token_id is None or isinstance(tk.pad_token_id, int)
    assert tk.vocab_size > 0
