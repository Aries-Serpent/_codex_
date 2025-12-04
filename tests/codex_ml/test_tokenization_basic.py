from codex_ml.tokenization import base


def test_tokenize_example_is_deterministic():
    text = "codex"
    assert base.tokenize_example(text) == base.tokenize_example(text)
