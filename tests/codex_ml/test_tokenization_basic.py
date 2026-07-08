"""
Test Tokenization Basic

Test module for tokenization basic.
"""

from codex_ml.tokenization import base


def test_tokenize_example_is_deterministic():
    text = "codex"
    result_a = base.tokenize_example(text)
    result_b = base.tokenize_example(text)
    assert result_a == result_b, "Result must not be empty"
