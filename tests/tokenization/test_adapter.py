"""
Test Adapter

Test module for adapter.
"""
from codex_ml.tokenization.adapter import HFTokenizerAdapter, WhitespaceTokenizer
    from codex_ml.utils.hf_pinning import HFModelUnavailableError




def test_whitespace_roundtrip():
    tok = WhitespaceTokenizer()
    text = "hello world"
    ids = tok.encode(text)
    assert isinstance(ids, list)
    decoded = tok.decode(ids)
    assert isinstance(decoded, str)


def test_hf_tokenizer_roundtrip():

    try:
        tok = HFTokenizerAdapter("gpt2")
    except HFModelUnavailableError:
        pytest.skip("HF model unavailable in CI (no network access)")
    else:
        text = "hello world"
        ids = tok.encode(text)
        assert isinstance(ids, list)
        decoded = tok.decode(ids)
        assert isinstance(decoded, str)
