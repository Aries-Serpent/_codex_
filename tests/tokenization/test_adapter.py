from codex_ml.tokenization.adapter import HFTokenizerAdapter, WhitespaceTokenizer


def test_whitespace_roundtrip():
    tok = WhitespaceTokenizer()
    text = "hello world"
    ids = tok.encode(text)
    assert isinstance(ids, list)
    decoded = tok.decode(ids)
    assert isinstance(decoded, str)


def test_hf_tokenizer_roundtrip():
    tok = HFTokenizerAdapter("gpt2")
    text = "hello world"
    ids = tok.encode(text)
    assert isinstance(ids, list)
    decoded = tok.decode(ids)
    assert isinstance(decoded, str)
