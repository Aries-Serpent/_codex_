import pytest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


@pytest.mark.skip(reason="requires transformers")
def test_hf_tokenizer_encode_roundtrip():
    from codex_ml.interfaces.tokenizer import HFTokenizer

    tk = HFTokenizer("gpt2", padding=False, truncation=True, max_length=32)
    ids = tk.encode("hello world")
    assert isinstance(ids, list) and len(ids) >= 2
    text = tk.decode(ids)
    assert "hello" in text
