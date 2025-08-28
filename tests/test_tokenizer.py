from codex_digest.tokenizer import DefaultTokenizer


def test_tokenizer_basic():
    tk = DefaultTokenizer()
    toks = tk.tokenize("Run pre-commit --all-files now.")
    assert any(t.text == "pre" for t in toks)
    assert any(t.text == "-" for t in toks if t.kind in {"punct", "symbol"})
