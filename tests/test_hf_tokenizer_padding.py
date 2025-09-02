from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter


def test_encode_with_padding_and_truncation():
    tok = HFTokenizerAdapter.load()
    ids = tok.encode("hello world", pad_to_max=True, max_length=8)
    assert len(ids) == 8
    # ensure pad tokens appended
    assert ids[-1] == tok.pad_id
