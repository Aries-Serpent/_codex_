"""
Test Tokenization Deprecation

Test module for tokenization deprecation.
"""
import pytest
import warnings
    import codex_ml.tokenization as tk



def test_tokenization_deprecation_attr():

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", DeprecationWarning)
        _ = tk.get_tokenizer
        assert any(isinstance(x.message, DeprecationWarning) for x in w)
