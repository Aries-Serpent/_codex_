import pytest

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def test_hf_tokenizer_encode_roundtrip():
    from codex_ml.interfaces.tokenizer import HFTokenizer

    tk = HFTokenizer("gpt2", padding=False, truncation=True, max_length=32)
    ids = tk.encode("hello world")
