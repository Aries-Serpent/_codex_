"""
Test Tokenization Deprecation

Test module for tokenization deprecation.
"""

import warnings


def test_tokenization_deprecation_attr():
    import codex_ml.tokenization as tk

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)
        _ = tk.get_tokenizer
        assert any(isinstance(x.message, DeprecationWarning) for x in w)
